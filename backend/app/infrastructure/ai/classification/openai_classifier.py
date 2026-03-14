from __future__ import annotations
import json
import logging
import openai
from app.core.config import settings
from app.domain.enums.enums import SectionLabel
from app.infrastructure.ai.classification.base import (
    SectionClassifier,
    ClassificationWindow,
    ClassificationResult,
)

logger = logging.getLogger(__name__)

_LABELS = [label.value for label in SectionLabel]
_SYSTEM_PROMPT = (
    "You are an expert church service audio classifier. Your task is to analyze transcript windows from a church service recording "
    "and classify each into one of the following labels:\n\n"
    "- praise_worship: Music, singing, lyrics, and worship leaders leading the congregation in song. Look for repetitive lyrics, musical cues, and calls to worship.\n"
    "- prayer: Formal or informal communication with God. Often starts with 'Let us pray', 'Father', 'Lord', and ends with 'Amen'.\n"
    "- testimony: A person sharing their personal story, faith journey, or specific experiences of God's work in their life. This is personal storytelling and narrative-driven. If a segment contains significant personal narrative, even if it occurs during a teaching block, it should be classified as 'testimony'.\n"
    "- offering: Segments where the congregation is invited to give tithes, offerings, or financial gifts. Often includes mention of 'tithe', 'giving', 'blessing', or instructions on how to give.\n"
    "- announcements: Information about upcoming events, church business, community news, or giving instructions.\n"
    "- sermon: The main teaching or preaching segment. This is systematic biblical teaching, doctrinal exposition, or moral instruction. It is distinct from personal storytelling (testimony). Favor 'testimony' if the content is primarily a personal story about what God has done for an individual.\n"
    "- transition: Short segments between other sections, such as 'Thank you', 'Moving on to', or brief introductory/closing remarks. CRITICAL: Distinguish between internal transitions (e.g., 'Let's move to prayer') and service boundaries (e.g., 'Thanks for joining us for the first service, we'll be back in 30 minutes for our second service'). Use 'transition' for both, but look for explicit 'End of Service' or 'Start of Service' cues.\n"
    "- other: Anything else that doesn't fit, including background noise, technical talk, long pauses, or non-service content between multiple services in a single recording.\n\n"
    "CHURCH SERVICE SEQUENCE: Typical services follow a predictable sequence:\n"
    "1. praise_worship (Initial worship session)\n"
    "2. (prayer, testimony, offering, announcements) - These often occur in varying order between worship and the sermon.\n"
    "3. sermon (The main teaching)\n"
    "4. (transition/other) - Final closing, sometimes followed by more worship or a long gap before another service.\n\n"
    "Use this expected sequence to better classify ambiguous segments. For example, a praise_worship segment following a sermon is highly likely to be the start of a new service or a closing song.\n\n"
    "CRITICAL DISTINCTION: 'testimony' and 'sermon' are distinct. 'testimony' is personal narrative/storytelling. 'sermon' is systematic teaching. If you hear a personal story, label it 'testimony'.\n\n"
    "Respond ONLY with a JSON object containing a root key \"classifications\" which is an array of objects. "
    "Each object must have \"label\" (one of the strings above) and \"confidence\" (a float between 0.0 and 1.0). "
    "The number of classifications MUST match the number of input windows provided, in the exact same order.\n\n"
    "Few-Shot Examples:\n"
    "Input:\n"
    "[{\"index\": 0, \"text\": \"Lord we just thank you for this day, we ask for your presence here...\"}, {\"index\": 1, \"text\": \"Next week we have a bake sale in the parking lot...\"}]\n"
    "Output:\n"
    "{\n"
    "  \"classifications\": [\n"
    "    {\"label\": \"prayer\", \"confidence\": 0.95},\n"
    "    {\"label\": \"announcements\", \"confidence\": 0.90}\n"
    "  ]\n"
    "}\n\n"
    "Input:\n"
    "[{\"index\": 0, \"text\": \"(Singing) Hallelujah, praise the Lord, you are holy...\"}, {\"index\": 1, \"text\": \"Open your bibles to the book of John chapter 3...\"}]\n"
    "Output:\n"
    "{\n"
    "  \"classifications\": [\n"
    "    {\"label\": \"praise_worship\", \"confidence\": 0.98},\n"
    "    {\"label\": \"sermon\", \"confidence\": 0.95}\n"
    "  ]\n"
    "}\n\n"
    "Input:\n"
    "[{\"index\": 0, \"text\": \"...and that concludes our 9 AM service. We'll be back in 30 minutes for our next service.\"}, {\"index\": 1, \"text\": \"Welcome to our 11 AM service, please stand as we begin with praise and worship...\"}]\n"
    "Output:\n"
    "{\n"
    "  \"classifications\": [\n"
    "    {\"label\": \"transition\", \"confidence\": 0.99},\n"
    "    {\"label\": \"transition\", \"confidence\": 0.99}\n"
    "  ]\n"
    "}"
)

_BATCH_SIZE = 20


class OpenAISectionClassifier(SectionClassifier):
    def __init__(self) -> None:
        self._client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def classify(self, windows: list[ClassificationWindow]) -> list[ClassificationResult]:
        results: list[ClassificationResult] = []
        for batch_start in range(0, len(windows), _BATCH_SIZE):
            batch = windows[batch_start : batch_start + _BATCH_SIZE]
            batch_results = await self._classify_batch(batch)
            results.extend(batch_results)
        return results

    async def _classify_batch(self, windows: list[ClassificationWindow]) -> list[ClassificationResult]:
        user_content = json.dumps(
            [
                {
                    "index": i,
                    "start_seconds": w.start_seconds,
                    "end_seconds": w.end_seconds,
                    "text": w.text,
                }
                for i, w in enumerate(windows)
            ]
        )

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)

        # The model is instructed to return {"classifications": [...]}.
        # We also support fallback keys for robustness.
        if isinstance(parsed, dict):
            items = (
                parsed.get("classifications")
                or parsed.get("results")
                or parsed.get("windows")
                or next(iter(parsed.values()), [])
            )
        else:
            items = parsed

        results: list[ClassificationResult] = []
        for i, window in enumerate(windows):
            try:
                item = items[i]
                label_str = item.get("label", SectionLabel.other.value)
                try:
                    label = SectionLabel(label_str)
                except ValueError:
                    label = SectionLabel.other
                confidence = float(item.get("confidence", 0.5))
            except (IndexError, KeyError, TypeError):
                logger.warning("Missing classification for window index %d; defaulting to 'other'", i)
                label = SectionLabel.other
                confidence = 0.5

            results.append(ClassificationResult(
                start_seconds=window.start_seconds,
                end_seconds=window.end_seconds,
                label=label,
                confidence=confidence,
            ))
        return results

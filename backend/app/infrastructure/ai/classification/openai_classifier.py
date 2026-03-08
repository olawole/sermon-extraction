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
    "You are a church service audio classifier. "
    "You will receive a batch of transcript windows from a church service recording. "
    "For each window, classify it into exactly one of the following section labels: "
    + ", ".join(_LABELS)
    + ". "
    "Respond with a JSON array where each element has the fields "
    '"label" (string) and "confidence" (float between 0 and 1). '
    "Return one element per input window, in the same order."
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

        raw = response.choices[0].message.content or "[]"
        parsed = json.loads(raw)

        # The model may return {"results": [...]} or {"classifications": [...]} or a bare array.
        if isinstance(parsed, dict):
            items = (
                parsed.get("results")
                or parsed.get("classifications")
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

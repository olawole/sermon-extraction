from __future__ import annotations
import re
import json
import logging
from openai import AsyncOpenAI
from app.core.config import settings
from app.infrastructure.ai.scoring.base import HighlightScorer
from app.domain.services.highlight_generation import HighlightCandidate

logger = logging.getLogger(__name__)

_HOOK_PHRASES = [
    "god", "jesus", "spirit", "love", "grace", "mercy", "faith", "believe",
    "promise", "truth", "life", "eternal", "salvation", "blessing", "glory",
]


class RuleBasedHighlightScorer(HighlightScorer):
    IDEAL_DURATION_SECONDS = 45.0
    IDEAL_PHRASE_COUNT = 5.0
    IDEAL_TEXT_LENGTH = 200.0

    async def score(self, candidate: HighlightCandidate) -> float:
        scores: list[float] = []

        duration = candidate.end_seconds - candidate.start_seconds
        if duration <= 0:
            return 0.0
        duration_score = 1.0 - min(abs(duration - self.IDEAL_DURATION_SECONDS) / self.IDEAL_DURATION_SECONDS, 1.0)
        scores.append(duration_score)

        text = candidate.transcript.lower()

        phrase_hits = sum(1 for p in _HOOK_PHRASES if p in text)
        hook_score = min(phrase_hits / self.IDEAL_PHRASE_COUNT, 1.0)
        scores.append(hook_score)

        # Sentence completeness (ends with punctuation)
        stripped = text.strip()
        completeness = 1.0 if stripped and stripped[-1] in ".!?" else 0.4
        scores.append(completeness)

        length_score = min(len(text) / self.IDEAL_TEXT_LENGTH, 1.0)
        scores.append(length_score)

        return round(sum(scores) / len(scores), 4)


class OpenAIHighlightScorer(HighlightScorer):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def score(self, candidate: HighlightCandidate) -> float:
        prompt = (
            "Analyze the following sermon transcript segment for social media impact. "
            "Return a JSON object with: \"score\" (0.0-1.0), \"social_content\": {\"caption\": \"...\", \"hashtags\": \"...\"}, "
            "\"reasons\": [\"...\"], \"hook_text\": \"...\", \"title\": \"...\""
            f"\n\nTranscript: {candidate.transcript}"
        )
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            if not content:
                return 0.0
            
            data = json.loads(content)
            candidate.score = data.get("score", 0.0)
            candidate.title = data.get("title", candidate.title)
            candidate.hook_text = data.get("hook_text", candidate.hook_text)
            candidate.reasons = data.get("reasons", candidate.reasons)
            
            social = data.get("social_content", {})
            candidate.social_caption = social.get("caption", "")
            candidate.hashtags = social.get("hashtags", "")
            
            return candidate.score
        except Exception as exc:
            logger.error(f"OpenAI scoring failed: {exc}")
            return 0.0

from __future__ import annotations
import re
from app.infrastructure.ai.scoring.base import HighlightScorer
from app.domain.services.highlight_generation import HighlightCandidate

_HOOK_PHRASES = [
    "god", "jesus", "spirit", "love", "grace", "mercy", "faith", "believe",
    "promise", "truth", "life", "eternal", "salvation", "blessing", "glory",
]


class RuleBasedHighlightScorer(HighlightScorer):
    IDEAL_DURATION_SECONDS = 45.0
    IDEAL_PHRASE_COUNT = 5.0
    IDEAL_TEXT_LENGTH = 200.0

    def score(self, candidate: HighlightCandidate) -> float:
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

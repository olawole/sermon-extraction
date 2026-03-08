from __future__ import annotations
import re
from app.infrastructure.ai.scoring.base import HighlightScorer
from app.domain.services.highlight_generation import HighlightCandidate

_HOOK_PHRASES = [
    "god", "jesus", "spirit", "love", "grace", "mercy", "faith", "believe",
    "promise", "truth", "life", "eternal", "salvation", "blessing", "glory",
]


class RuleBasedHighlightScorer(HighlightScorer):
    def score(self, candidate: HighlightCandidate) -> float:
        scores: list[float] = []

        # Duration score (ideal ~45s)
        duration = candidate.end_seconds - candidate.start_seconds
        if duration <= 0:
            return 0.0
        ideal = 45.0
        duration_score = 1.0 - min(abs(duration - ideal) / ideal, 1.0)
        scores.append(duration_score)

        text = candidate.transcript.lower()

        # Hook phrase score
        phrase_hits = sum(1 for p in _HOOK_PHRASES if p in text)
        hook_score = min(phrase_hits / 5.0, 1.0)
        scores.append(hook_score)

        # Sentence completeness (ends with punctuation)
        stripped = text.strip()
        completeness = 1.0 if stripped and stripped[-1] in ".!?" else 0.4
        scores.append(completeness)

        # Text length (at least 50 chars is good)
        length_score = min(len(text) / 200.0, 1.0)
        scores.append(length_score)

        return round(sum(scores) / len(scores), 4)

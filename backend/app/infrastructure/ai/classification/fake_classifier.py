from __future__ import annotations
from app.infrastructure.ai.classification.base import SectionClassifier, ClassificationWindow, ClassificationResult
from app.domain.enums.enums import SectionLabel


_PATTERN = [
    (0, 600, SectionLabel.praise_worship, 0.9),
    (600, 900, SectionLabel.prayer, 0.85),
    (900, 1200, SectionLabel.praise_worship, 0.88),
    (1200, 1500, SectionLabel.announcements, 0.82),
    (1500, 1800, SectionLabel.transition, 0.9),
    (1800, 2100, SectionLabel.praise_worship, 0.87),
    (2100, 2400, SectionLabel.prayer, 0.84),
    (2400, 4800, SectionLabel.sermon, 0.92),
    (4800, 5400, SectionLabel.other, 0.75),
]


class FakeSectionClassifier(SectionClassifier):
    async def classify(self, windows: list[ClassificationWindow]) -> list[ClassificationResult]:
        results: list[ClassificationResult] = []
        for window in windows:
            mid = (window.start_seconds + window.end_seconds) / 2
            label = SectionLabel.other
            confidence = 0.7
            for start, end, lbl, conf in _PATTERN:
                if start <= mid < end:
                    label = lbl
                    confidence = conf
                    break
            results.append(ClassificationResult(
                start_seconds=window.start_seconds,
                end_seconds=window.end_seconds,
                label=label,
                confidence=confidence,
            ))
        return results

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from app.domain.enums.enums import SectionLabel


@dataclass
class SermonDetectionResult:
    service_number: int
    start_seconds: float
    end_seconds: float
    dominant_speaker: Optional[str]
    confidence: float


class SermonDetectionService:
    def detect(
        self,
        section_segments: list,
        service2_start: float,
        service2_end: float,
    ) -> Optional[SermonDetectionResult]:
        sermon_segments = [
            s for s in section_segments
            if (s.label == SectionLabel.sermon.value or s.label == "sermon")
            and s.end_seconds > service2_start
            and s.start_seconds < service2_end
        ]

        if not sermon_segments:
            return None

        sermon_segments.sort(key=lambda s: s.start_seconds)

        start = max(sermon_segments[0].start_seconds, service2_start)
        end = min(sermon_segments[-1].end_seconds, service2_end)

        avg_confidence = sum(
            getattr(s, "confidence", None) or 0.8 for s in sermon_segments
        ) / len(sermon_segments)

        return SermonDetectionResult(
            service_number=2,
            start_seconds=start,
            end_seconds=end,
            dominant_speaker=getattr(sermon_segments[0], "dominant_speaker", None),
            confidence=avg_confidence,
        )

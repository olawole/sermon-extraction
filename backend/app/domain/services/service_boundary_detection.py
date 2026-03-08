from __future__ import annotations
from dataclasses import dataclass
from app.domain.enums.enums import SectionLabel


@dataclass
class ServiceBoundaryResult:
    service_number: int
    start_seconds: float
    end_seconds: float
    confidence: float


class ServiceBoundaryDetectionService:
    def detect(
        self,
        section_segments: list,
        total_duration: float,
    ) -> list[ServiceBoundaryResult]:
        transition_segments = [
            s for s in section_segments
            if s.label == SectionLabel.transition.value or s.label == "transition"
        ]

        if transition_segments:
            transition = transition_segments[0]
            service1_end = transition.start_seconds
            service2_start = transition.end_seconds
        else:
            # Split at midpoint if no transition found
            service1_end = total_duration * 0.45
            service2_start = total_duration * 0.5

        return [
            ServiceBoundaryResult(
                service_number=1,
                start_seconds=0.0,
                end_seconds=service1_end,
                confidence=0.8,
            ),
            ServiceBoundaryResult(
                service_number=2,
                start_seconds=service2_start,
                end_seconds=total_duration,
                confidence=0.8,
            ),
        ]

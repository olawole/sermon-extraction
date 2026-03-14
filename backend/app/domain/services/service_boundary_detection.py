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
        # Identify all potential boundary segments (transitions or praise_worship)
        boundary_labels = {
            SectionLabel.transition.value,
            "transition",
            SectionLabel.praise_worship.value,
            "praise_worship",
        }

        boundaries = [
            s for s in section_segments
            if s.label in boundary_labels
        ]

        if not boundaries:
            return [
                ServiceBoundaryResult(
                    service_number=1,
                    start_seconds=0.0,
                    end_seconds=total_duration,
                    confidence=0.8,
                )
            ]

        # Sort boundaries by start time to handle them in order
        boundaries.sort(key=lambda s: s.start_seconds)

        results = []
        current_start = 0.0
        service_count = 1

        for b in boundaries:
            # If there's a gap between the current start and the next transition,
            # that gap constitutes a service.
            if b.start_seconds > current_start:
                results.append(ServiceBoundaryResult(
                    service_number=service_count,
                    start_seconds=current_start,
                    end_seconds=b.start_seconds,
                    confidence=0.8,
                ))
                service_count += 1
            # Move the current_start to the end of the transition segment
            current_start = max(current_start, b.end_seconds)

        # After all transitions, if there's time remaining, that's the final service
        if current_start < total_duration:
            results.append(ServiceBoundaryResult(
                service_number=service_count,
                start_seconds=current_start,
                end_seconds=total_duration,
                confidence=0.8,
            ))

        # Handle the case where the only segments were boundaries that covered everything
        if not results and boundaries:
            # This shouldn't really happen with typical church data, but for robustness:
            # If everything was a boundary, we might just return the whole thing or nothing.
            # Given the instruction "assume a single service", let's ensure we return something.
            # But the logic above already handles this if current_start < total_duration.
            pass

        return results

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
        """
        Detects church services from a list of classified section segments.
        A service boundary is detected if:
          - There is a 'transition' or 'other' segment longer than 5 minutes (300s).
          - A 'praise_worship' segment occurs after a 'sermon' has already been completed in the current service.
          - A 'praise_worship' segment occurs after the current service has been running for a long time (> 60 mins).
        """
        if not section_segments:
            return [
                ServiceBoundaryResult(
                    service_number=1,
                    start_seconds=0.0,
                    end_seconds=total_duration,
                    confidence=0.5,
                )
            ]

        services = []
        current_segments = []
        has_sermon_in_current_service = False
        service_start_time = section_segments[0].start_seconds

        for segment in section_segments:
            duration = segment.end_seconds - segment.start_seconds
            current_service_duration = segment.start_seconds - service_start_time
            
            is_long_gap = (
                segment.label in (SectionLabel.transition.value, SectionLabel.other.value)
                and duration > 300
            )
            
            # A new service cycle starts if we see praise_worship AND:
            # 1. We've already had a sermon in this service, OR
            # 2. This service has been running for a long time (> 60 mins)
            is_new_cycle = (
                segment.label == SectionLabel.praise_worship.value
                and (has_sermon_in_current_service or current_service_duration > 3600)
            )

            if is_long_gap or is_new_cycle:
                if current_segments:
                    # Finalize the current service
                    services.append(ServiceBoundaryResult(
                        service_number=len(services) + 1,
                        start_seconds=current_segments[0].start_seconds,
                        end_seconds=current_segments[-1].end_seconds,
                        confidence=0.9,
                    ))
                    current_segments = []
                    has_sermon_in_current_service = False
                
                if is_long_gap:
                    # Long gaps are not part of any service
                    # We'll update service_start_time when the next service segment starts
                    continue
                else:
                    # is_new_cycle: the current segment (praise_worship) is the start of the new service
                    service_start_time = segment.start_seconds

            if not current_segments:
                service_start_time = segment.start_seconds

            current_segments.append(segment)
            if segment.label == SectionLabel.sermon.value:
                has_sermon_in_current_service = True

        # Finalize the last service if it exists
        if current_segments:
            services.append(ServiceBoundaryResult(
                service_number=len(services) + 1,
                start_seconds=current_segments[0].start_seconds,
                end_seconds=current_segments[-1].end_seconds,
                confidence=0.9,
            ))

        # Fallback if no services were detected (e.g., all segments were long gaps)
        if not services:
            return [
                ServiceBoundaryResult(
                    service_number=1,
                    start_seconds=0.0,
                    end_seconds=total_duration,
                    confidence=0.5,
                )
            ]

        return services

from __future__ import annotations
from dataclasses import dataclass
from app.infrastructure.ai.classification.base import ClassificationResult
from app.domain.enums.enums import SectionLabel


@dataclass
class SmoothedSegment:
    label: str
    start_seconds: float
    end_seconds: float
    confidence: float


def smooth_and_merge(
    raw_results: list[ClassificationResult],
    min_duration_seconds: float = 60.0,
) -> list[SmoothedSegment]:
    if not raw_results:
        return []

    sorted_results = sorted(raw_results, key=lambda r: r.start_seconds)

    merged: list[SmoothedSegment] = []
    current = SmoothedSegment(
        label=sorted_results[0].label.value,
        start_seconds=sorted_results[0].start_seconds,
        end_seconds=sorted_results[0].end_seconds,
        confidence=sorted_results[0].confidence,
    )

    for result in sorted_results[1:]:
        if result.label.value == current.label:
            current.end_seconds = result.end_seconds
            current.confidence = (current.confidence + result.confidence) / 2
        else:
            if current.end_seconds - current.start_seconds >= min_duration_seconds:
                merged.append(current)
            current = SmoothedSegment(
                label=result.label.value,
                start_seconds=result.start_seconds,
                end_seconds=result.end_seconds,
                confidence=result.confidence,
            )

    if current.end_seconds - current.start_seconds >= min_duration_seconds:
        merged.append(current)

    return merged

import pytest
from dataclasses import dataclass
from app.domain.services.service_boundary_detection import ServiceBoundaryDetectionService
from app.domain.enums.enums import SectionLabel


@dataclass
class FakeSegment:
    label: str
    start_seconds: float
    end_seconds: float
    confidence: float = 0.9


def test_detects_two_services_with_transition():
    segments = [
        FakeSegment(label="praise_worship", start_seconds=0, end_seconds=600),
        FakeSegment(label="prayer", start_seconds=600, end_seconds=900),
        FakeSegment(label="transition", start_seconds=900, end_seconds=1200),
        FakeSegment(label="praise_worship", start_seconds=1200, end_seconds=1800),
        FakeSegment(label="sermon", start_seconds=1800, end_seconds=3600),
    ]
    service = ServiceBoundaryDetectionService()
    results = service.detect(segments, total_duration=3600.0)
    assert len(results) == 2
    assert results[0].service_number == 1
    assert results[1].service_number == 2


def test_fallback_split_at_midpoint():
    segments = [
        FakeSegment(label="sermon", start_seconds=0, end_seconds=3600),
    ]
    service = ServiceBoundaryDetectionService()
    results = service.detect(segments, total_duration=3600.0)
    assert len(results) == 2

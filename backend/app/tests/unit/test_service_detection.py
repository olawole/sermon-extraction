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
    # With the new logic:
    # Gap 1: [0, 600] (Praise)
    # Service 1: [600, 900] (Prayer)
    # Gap 2: [900, 1200] (Transition)
    # Gap 3: [1200, 1800] (Praise)
    # Service 2: [1800, 3600] (Sermon)
    assert len(results) == 2
    assert results[0].service_number == 1
    assert results[0].start_seconds == 600.0
    assert results[0].end_seconds == 900.0
    assert results[1].service_number == 2
    assert results[1].start_seconds == 1800.0
    assert results[1].end_seconds == 3600.0


def test_detects_single_service_when_no_transitions():
    segments = [
        FakeSegment(label="sermon", start_seconds=0, end_seconds=3600),
    ]
    service = ServiceBoundaryDetectionService()
    results = service.detect(segments, total_duration=3600.0)
    assert len(results) == 1
    assert results[0].start_seconds == 0.0
    assert results[0].end_seconds == 3600.0


def test_detects_multiple_services_with_multiple_transitions():
    segments = [
        FakeSegment(label="transition", start_seconds=1000, end_seconds=1100),
        FakeSegment(label="transition", start_seconds=2000, end_seconds=2100),
    ]
    service = ServiceBoundaryDetectionService()
    results = service.detect(segments, total_duration=3000.0)
    assert len(results) == 3
    assert results[0].start_seconds == 0.0
    assert results[0].end_seconds == 1000.0
    assert results[1].start_seconds == 1100.0
    assert results[1].end_seconds == 2000.0
    assert results[2].start_seconds == 2100.0
    assert results[2].end_seconds == 3000.0

def test_praise_worship_at_start_excluded_from_first_service():
    segments = [
        FakeSegment(label="praise_worship", start_seconds=0, end_seconds=600),
        FakeSegment(label="sermon", start_seconds=600, end_seconds=3000),
    ]
    service = ServiceBoundaryDetectionService()
    results = service.detect(segments, total_duration=3000.0)
    assert len(results) == 1
    assert results[0].start_seconds == 600.0
    assert results[0].end_seconds == 3000.0

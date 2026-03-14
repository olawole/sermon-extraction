import pytest
from dataclasses import dataclass
from app.domain.services.service_boundary_detection import ServiceBoundaryDetectionService, ServiceBoundaryResult
from app.domain.enums.enums import SectionLabel


@dataclass
class FakeSegment:
    label: str
    start_seconds: float
    end_seconds: float
    confidence: float = 0.9


def test_detects_single_service_with_short_transition():
    # Previous logic would split this, but new logic is less aggressive
    segments = [
        FakeSegment(label=SectionLabel.praise_worship.value, start_seconds=0, end_seconds=600),
        FakeSegment(label=SectionLabel.prayer.value, start_seconds=600, end_seconds=900),
        FakeSegment(label=SectionLabel.transition.value, start_seconds=900, end_seconds=1200), # 5 mins
        FakeSegment(label=SectionLabel.praise_worship.value, start_seconds=1200, end_seconds=1800),
        FakeSegment(label=SectionLabel.sermon.value, start_seconds=1800, end_seconds=3600),
    ]
    service = ServiceBoundaryDetectionService()
    results = service.detect(segments, total_duration=3600.0)
    
    # In new logic, 300s is not > 300s, so it's not a long gap.
    # And there was no sermon before the second praise, so no new cycle.
    assert len(results) == 1
    assert results[0].start_seconds == 0.0
    assert results[0].end_seconds == 3600.0


def test_detects_two_services_with_long_gap():
    segments = [
        FakeSegment(label=SectionLabel.praise_worship.value, start_seconds=0, end_seconds=600),
        FakeSegment(label=SectionLabel.sermon.value, start_seconds=600, end_seconds=2000),
        FakeSegment(label=SectionLabel.other.value, start_seconds=2000, end_seconds=2400), # 400s gap
        FakeSegment(label=SectionLabel.praise_worship.value, start_seconds=2400, end_seconds=3000),
        FakeSegment(label=SectionLabel.sermon.value, start_seconds=3000, end_seconds=5000),
    ]
    service = ServiceBoundaryDetectionService()
    results = service.detect(segments, total_duration=5000.0)
    
    assert len(results) == 2
    assert results[0].start_seconds == 0.0
    assert results[0].end_seconds == 2000.0
    assert results[1].start_seconds == 2400.0
    assert results[1].end_seconds == 5000.0


def test_detects_two_services_with_new_cycle():
    # Praise -> Sermon -> Praise (new service)
    segments = [
        FakeSegment(label=SectionLabel.praise_worship.value, start_seconds=0, end_seconds=600),
        FakeSegment(label=SectionLabel.sermon.value, start_seconds=600, end_seconds=2000),
        FakeSegment(label=SectionLabel.praise_worship.value, start_seconds=2000, end_seconds=2600),
        FakeSegment(label=SectionLabel.sermon.value, start_seconds=2600, end_seconds=4000),
    ]
    service = ServiceBoundaryDetectionService()
    results = service.detect(segments, total_duration=4000.0)
    
    assert len(results) == 2
    assert results[0].start_seconds == 0.0
    assert results[0].end_seconds == 2000.0
    assert results[1].start_seconds == 2000.0
    assert results[1].end_seconds == 4000.0


def test_simulate_four_hour_recording_two_services():
    # 4 hours = 14400 seconds
    # Service 1: 0 - 5400 (1.5 hours)
    # GAP: 5400 - 7200 (30 mins)
    # Service 2: 7200 - 12600 (1.5 hours)
    # GAP/END: 12600 - 14400 (30 mins)
    
    segments = [
        # Service 1
        FakeSegment(label=SectionLabel.praise_worship.value, start_seconds=0, end_seconds=1200),
        FakeSegment(label=SectionLabel.prayer.value, start_seconds=1200, end_seconds=1500),
        FakeSegment(label=SectionLabel.announcements.value, start_seconds=1500, end_seconds=1800),
        FakeSegment(label=SectionLabel.sermon.value, start_seconds=1800, end_seconds=5000),
        FakeSegment(label=SectionLabel.transition.value, start_seconds=5000, end_seconds=5300), # 300s

        # GAP
        FakeSegment(label=SectionLabel.other.value, start_seconds=5300, end_seconds=7200), # 1900s gap

        # Service 2
        FakeSegment(label=SectionLabel.praise_worship.value, start_seconds=7200, end_seconds=8400),
        FakeSegment(label=SectionLabel.prayer.value, start_seconds=8400, end_seconds=8700),
        FakeSegment(label=SectionLabel.sermon.value, start_seconds=8700, end_seconds=12000),
        FakeSegment(label=SectionLabel.transition.value, start_seconds=12000, end_seconds=12300), # 300s

        # GAP/END
        FakeSegment(label=SectionLabel.other.value, start_seconds=12300, end_seconds=14400), # 2100s gap
    ]
    
    service = ServiceBoundaryDetectionService()
    results = service.detect(segments, total_duration=14400.0)
    
    assert len(results) == 2
    assert results[0].service_number == 1
    assert results[0].start_seconds == 0.0
    assert results[0].end_seconds == 5300.0
    
    assert results[1].service_number == 2
    assert results[1].start_seconds == 7200.0
    assert results[1].end_seconds == 12300.0


def test_detects_single_service_when_no_transitions():
    segments = [
        FakeSegment(label=SectionLabel.sermon.value, start_seconds=0, end_seconds=3600),
    ]
    service = ServiceBoundaryDetectionService()
    results = service.detect(segments, total_duration=3600.0)
    assert len(results) == 1
    assert results[0].start_seconds == 0.0
    assert results[0].end_seconds == 3600.0


def test_praise_worship_at_start_included_in_service():
    # Previous logic excluded praise at start, new logic includes it
    segments = [
        FakeSegment(label=SectionLabel.praise_worship.value, start_seconds=0, end_seconds=600),
        FakeSegment(label=SectionLabel.sermon.value, start_seconds=600, end_seconds=3000),
    ]
    service = ServiceBoundaryDetectionService()
    results = service.detect(segments, total_duration=3000.0)
    assert len(results) == 1
    assert results[0].start_seconds == 0.0
    assert results[0].end_seconds == 3000.0


def test_complex_service_flow():
    # Praise -> Offering -> Testimony -> Sermon -> Praise (new service)
    segments = [
        FakeSegment(label=SectionLabel.praise_worship.value, start_seconds=0, end_seconds=600),
        FakeSegment(label=SectionLabel.offering.value, start_seconds=600, end_seconds=900),
        FakeSegment(label=SectionLabel.testimony.value, start_seconds=900, end_seconds=1200),
        FakeSegment(label=SectionLabel.sermon.value, start_seconds=1200, end_seconds=3000),
        FakeSegment(label=SectionLabel.praise_worship.value, start_seconds=3000, end_seconds=3600),
        FakeSegment(label=SectionLabel.sermon.value, start_seconds=3600, end_seconds=5000),
    ]
    service = ServiceBoundaryDetectionService()
    results = service.detect(segments, total_duration=5000.0)
    
    assert len(results) == 2
    assert results[0].start_seconds == 0.0
    assert results[0].end_seconds == 3000.0
    assert results[1].start_seconds == 3000.0
    assert results[1].end_seconds == 5000.0


def test_detects_new_service_after_long_duration_without_sermon():
    # Praise (70 mins) -> Praise (new service)
    segments = [
        FakeSegment(label=SectionLabel.praise_worship.value, start_seconds=0, end_seconds=4200), # 70 mins
        FakeSegment(label=SectionLabel.praise_worship.value, start_seconds=4200, end_seconds=4800),
        FakeSegment(label=SectionLabel.sermon.value, start_seconds=4800, end_seconds=6000),
    ]
    service = ServiceBoundaryDetectionService()
    results = service.detect(segments, total_duration=6000.0)
    
    assert len(results) == 2
    assert results[0].start_seconds == 0.0
    assert results[0].end_seconds == 4200.0
    assert results[1].start_seconds == 4200.0
    assert results[1].end_seconds == 6000.0

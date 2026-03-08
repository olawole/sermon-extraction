import pytest
from dataclasses import dataclass
from app.domain.services.sermon_detection import SermonDetectionService
from app.domain.enums.enums import SectionLabel


@dataclass
class FakeSegment:
    label: str
    start_seconds: float
    end_seconds: float
    confidence: float = 0.9
    dominant_speaker: str = None


def test_detects_sermon_in_service2():
    segments = [
        FakeSegment(label="praise_worship", start_seconds=1200, end_seconds=1800),
        FakeSegment(label="sermon", start_seconds=2400, end_seconds=4800),
        FakeSegment(label="other", start_seconds=4800, end_seconds=5400),
    ]
    service = SermonDetectionService()
    result = service.detect(segments, service2_start=1200.0, service2_end=5400.0)
    assert result is not None
    assert result.start_seconds == 2400.0
    assert result.end_seconds == 4800.0


def test_returns_none_when_no_sermon():
    segments = [
        FakeSegment(label="praise_worship", start_seconds=0, end_seconds=600),
    ]
    service = SermonDetectionService()
    result = service.detect(segments, service2_start=1800.0, service2_end=3600.0)
    assert result is None

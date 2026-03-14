import pytest
from dataclasses import dataclass
from typing import List, Optional
from app.domain.services.sermon_detection import SermonDetectionService
from app.domain.enums.enums import SectionLabel


@dataclass
class FakeSegment:
    label: str
    start_seconds: float
    end_seconds: float
    confidence: float = 0.9
    dominant_speaker: str = None


@dataclass
class FakeBoundary:
    service_number: int
    start_seconds: float
    end_seconds: float
    confidence: float = 0.8


def test_detects_sermon_in_service2():
    segments = [
        FakeSegment(label="praise_worship", start_seconds=1200, end_seconds=1800),
        FakeSegment(label="sermon", start_seconds=2400, end_seconds=4800), # 40 mins
        FakeSegment(label="other", start_seconds=4800, end_seconds=5400),
    ]
    boundaries = [
        FakeBoundary(service_number=1, start_seconds=0, end_seconds=2000),
        FakeBoundary(service_number=2, start_seconds=2100, end_seconds=6000),
    ]
    service = SermonDetectionService()
    result = service.detect(segments, boundaries)
    assert result is not None
    assert result.service_number == 2
    assert result.start_seconds == 2400.0
    assert result.end_seconds == 4800.0


def test_returns_none_when_no_sermon():
    segments = [
        FakeSegment(label="praise_worship", start_seconds=0, end_seconds=600),
    ]
    boundaries = [
        FakeBoundary(service_number=1, start_seconds=0, end_seconds=3600),
    ]
    service = SermonDetectionService()
    result = service.detect(segments, boundaries)
    assert result is None


def test_merges_adjacent_sermons():
    # Two sermon segments with 1 minute gap (60s)
    segments = [
        FakeSegment(label="sermon", start_seconds=2000, end_seconds=3000),
        FakeSegment(label="sermon", start_seconds=3060, end_seconds=4500),
    ]
    boundaries = [
        FakeBoundary(service_number=1, start_seconds=0, end_seconds=6000),
    ]
    service = SermonDetectionService()
    result = service.detect(segments, boundaries)
    
    assert result is not None
    assert result.start_seconds == 2000.0
    assert result.end_seconds == 4500.0
    # Duration = 2500s (~41 mins), which is valid


def test_does_not_merge_large_gaps():
    # Two sermon segments with 3 minute gap (180s)
    # First one is 20 mins, second is 25 mins.
    segments = [
        FakeSegment(label="sermon", start_seconds=1000, end_seconds=2200, confidence=0.7), # 20 mins
        FakeSegment(label="sermon", start_seconds=2380, end_seconds=3880, confidence=0.9), # 25 mins
    ]
    boundaries = [
        FakeBoundary(service_number=1, start_seconds=0, end_seconds=5000),
    ]
    service = SermonDetectionService()
    result = service.detect(segments, boundaries)
    
    # Should pick the one with highest confidence (0.9)
    assert result is not None
    assert result.start_seconds == 2380.0
    assert result.end_seconds == 3880.0


def test_filters_by_duration():
    segments = [
        FakeSegment(label="sermon", start_seconds=1000, end_seconds=1500), # 500s (< 900s)
        FakeSegment(label="sermon", start_seconds=2000, end_seconds=6500), # 4500s (> 4200s)
    ]
    boundaries = [
        FakeBoundary(service_number=1, start_seconds=0, end_seconds=10000),
    ]
    service = SermonDetectionService()
    result = service.detect(segments, boundaries)
    assert result is None


def test_multi_service_selection():
    segments = [
        FakeSegment(label="sermon", start_seconds=1000, end_seconds=3000, confidence=0.8), # Service 1, 2000s
        FakeSegment(label="sermon", start_seconds=6000, end_seconds=8500, confidence=0.9), # Service 2, 2500s
    ]
    boundaries = [
        FakeBoundary(service_number=1, start_seconds=0, end_seconds=5000),
        FakeBoundary(service_number=2, start_seconds=5500, end_seconds=10000),
    ]
    service = SermonDetectionService()
    result = service.detect(segments, boundaries)
    
    assert result is not None
    assert result.service_number == 2
    assert result.confidence == 0.9

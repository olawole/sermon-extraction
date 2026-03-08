import pytest
from app.domain.services.segment_smoothing import smooth_and_merge
from app.infrastructure.ai.classification.base import ClassificationResult
from app.domain.enums.enums import SectionLabel


def make_result(start, end, label, confidence=0.9):
    return ClassificationResult(start_seconds=start, end_seconds=end, label=label, confidence=confidence)


def test_merges_adjacent_same_label():
    results = [
        make_result(0, 300, SectionLabel.praise_worship),
        make_result(300, 600, SectionLabel.praise_worship),
        make_result(600, 900, SectionLabel.sermon),
    ]
    smoothed = smooth_and_merge(results, min_duration_seconds=60.0)
    praise = [s for s in smoothed if s.label == "praise_worship"]
    assert len(praise) == 1
    assert praise[0].start_seconds == 0
    assert praise[0].end_seconds == 600


def test_removes_tiny_fragments():
    results = [
        make_result(0, 600, SectionLabel.sermon),
        make_result(600, 610, SectionLabel.prayer),  # only 10s - should be removed
        make_result(610, 1200, SectionLabel.sermon),
    ]
    smoothed = smooth_and_merge(results, min_duration_seconds=60.0)
    prayer = [s for s in smoothed if s.label == "prayer"]
    assert len(prayer) == 0


def test_empty_returns_empty():
    assert smooth_and_merge([]) == []

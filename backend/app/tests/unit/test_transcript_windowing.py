import pytest
from dataclasses import dataclass
from app.domain.services.transcript_windowing import create_windows


@dataclass
class FakeChunk:
    chunk_index: int
    start_seconds: float
    end_seconds: float
    text: str


def make_chunks(n=20, total_duration=3600.0):
    interval = total_duration / n
    return [
        FakeChunk(
            chunk_index=i,
            start_seconds=i * interval,
            end_seconds=(i + 1) * interval,
            text=f"chunk {i} text here",
        )
        for i in range(n)
    ]


def test_create_windows_returns_windows():
    chunks = make_chunks()
    windows = create_windows(chunks, window_size_seconds=300.0, overlap_seconds=30.0)
    assert len(windows) > 0


def test_create_windows_overlap():
    chunks = make_chunks()
    windows = create_windows(chunks, window_size_seconds=300.0, overlap_seconds=30.0)
    # With overlap, adjacent windows should share some time
    for i in range(len(windows) - 1):
        assert windows[i].end_seconds > windows[i + 1].start_seconds


def test_create_windows_empty():
    assert create_windows([]) == []


def test_create_windows_cover_duration():
    chunks = make_chunks()
    windows = create_windows(chunks, window_size_seconds=300.0, overlap_seconds=30.0)
    assert windows[0].start_seconds == 0.0
    assert windows[-1].end_seconds <= 3600.0

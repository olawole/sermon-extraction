from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol


class ChunkLike(Protocol):
    chunk_index: int
    start_seconds: float
    end_seconds: float
    text: str


@dataclass
class ClassificationWindow:
    start_seconds: float
    end_seconds: float
    text: str
    chunk_indices: list[int] = field(default_factory=list)


def create_windows(
    chunks: list,
    window_size_seconds: float = 300.0,
    overlap_seconds: float = 30.0,
) -> list[ClassificationWindow]:
    if not chunks:
        return []

    windows: list[ClassificationWindow] = []
    step = window_size_seconds - overlap_seconds
    if step <= 0:
        step = window_size_seconds

    total_duration = max(c.end_seconds for c in chunks)
    start = 0.0
    while start < total_duration:
        end = start + window_size_seconds
        window_chunks = [c for c in chunks if c.start_seconds < end and c.end_seconds > start]
        if window_chunks:
            text = " ".join(c.text for c in window_chunks)
            indices = [c.chunk_index for c in window_chunks]
            windows.append(ClassificationWindow(
                start_seconds=start,
                end_seconds=min(end, total_duration),
                text=text,
                chunk_indices=indices,
            ))
        start += step

    return windows

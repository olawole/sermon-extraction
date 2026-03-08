from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HighlightCandidate:
    start_seconds: float
    end_seconds: float
    transcript: str
    chunk_indices: list[int] = field(default_factory=list)
    score: float = 0.0
    category: str = "sermon"
    title: str = ""
    hook_text: str = ""
    reasons: list[str] = field(default_factory=list)


class HighlightCandidateGenerator:
    TARGET_DURATIONS = [15.0, 30.0, 45.0, 60.0]
    MAX_HOOK_TEXT_LENGTH = 100

    def generate_candidates(
        self,
        chunks: list,
        sermon_start: float,
        sermon_end: float,
    ) -> list[HighlightCandidate]:
        sermon_chunks = [
            c for c in chunks
            if c.start_seconds >= sermon_start and c.end_seconds <= sermon_end
        ]
        if not sermon_chunks:
            return []

        candidates: list[HighlightCandidate] = []
        for i, chunk in enumerate(sermon_chunks):
            for target_duration in self.TARGET_DURATIONS:
                window_chunks = []
                duration = 0.0
                for j in range(i, len(sermon_chunks)):
                    window_chunks.append(sermon_chunks[j])
                    duration = sermon_chunks[j].end_seconds - chunk.start_seconds
                    if duration >= target_duration:
                        break

                if not window_chunks or duration < target_duration * 0.5:
                    continue

                text = " ".join(c.text for c in window_chunks)
                first_sentence = text.split(".")[0][:self.MAX_HOOK_TEXT_LENGTH] if "." in text else text[:self.MAX_HOOK_TEXT_LENGTH]

                candidates.append(HighlightCandidate(
                    start_seconds=chunk.start_seconds,
                    end_seconds=window_chunks[-1].end_seconds,
                    transcript=text,
                    chunk_indices=[c.chunk_index for c in window_chunks],
                    category="sermon",
                    title=f"Highlight at {int(chunk.start_seconds)}s",
                    hook_text=first_sentence,
                    reasons=["sermon content"],
                ))

        return candidates

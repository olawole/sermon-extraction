from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class TranscriptChunkData:
    chunk_index: int
    start_seconds: float
    end_seconds: float
    text: str
    speaker_id: Optional[str] = None
    confidence: Optional[float] = None


class TranscriptionProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: str) -> list[TranscriptChunkData]: ...

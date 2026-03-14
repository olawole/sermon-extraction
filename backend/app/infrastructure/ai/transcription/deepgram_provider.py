from __future__ import annotations
import logging
from app.infrastructure.ai.transcription.base import TranscriptionProvider, TranscriptChunkData

logger = logging.getLogger(__name__)


class DeepgramTranscriptionProvider(TranscriptionProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def transcribe(self, audio_path: str) -> list[TranscriptChunkData]:
        logger.info(f"DeepgramTranscriptionProvider: transcribing {audio_path} (STUB)")
        # This is a stub that currently returns nothing or could return fake data.
        return []

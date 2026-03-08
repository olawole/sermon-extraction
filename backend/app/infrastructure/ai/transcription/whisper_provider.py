from __future__ import annotations
import asyncio
import io
import openai
from app.core.config import settings
from app.infrastructure.ai.transcription.base import TranscriptionProvider, TranscriptChunkData


class WhisperTranscriptionProvider(TranscriptionProvider):
    def __init__(self) -> None:
        self._client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.whisper_model

    async def transcribe(self, audio_path: str, duration_seconds: float = 3600.0) -> list[TranscriptChunkData]:
        loop = asyncio.get_event_loop()
        audio_bytes = await loop.run_in_executor(None, lambda: open(audio_path, "rb").read())
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = audio_path
        response = await self._client.audio.transcriptions.create(
            model=self._model,
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )

        chunks: list[TranscriptChunkData] = []
        segments = getattr(response, "segments", None) or []
        for i, segment in enumerate(segments):
            chunks.append(TranscriptChunkData(
                chunk_index=i,
                start_seconds=float(segment.get("start", 0.0) if isinstance(segment, dict) else segment.start),
                end_seconds=float(segment.get("end", 0.0) if isinstance(segment, dict) else segment.end),
                text=(segment.get("text", "") if isinstance(segment, dict) else segment.text).strip(),
                speaker_id=None,
                confidence=None,
            ))
        return chunks

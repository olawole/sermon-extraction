from __future__ import annotations
import asyncio
import io
from pathlib import Path
import openai
from app.core.config import settings
from app.infrastructure.ai.transcription.base import TranscriptionProvider, TranscriptChunkData


class WhisperTranscriptionProvider(TranscriptionProvider):
    def __init__(self) -> None:
        self._client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.whisper_model

    async def transcribe(self, audio_path: str, duration_seconds: float = 3600.0) -> list[TranscriptChunkData]:
        normalized_path = str(Path(audio_path))
        audio_file_path = Path(audio_path)
        if not audio_file_path.exists():
            raise FileNotFoundError(
                f"Audio file not found at {normalized_path}; download or extraction may have failed"
            )
        if audio_file_path.stat().st_size == 0:
            raise ValueError(
                f"Audio file at {normalized_path} is empty (0 bytes); audio extraction may have failed"
            )
        loop = asyncio.get_running_loop()
        def _read_file() -> bytes:
            with open(normalized_path, "rb") as f:
                return f.read()
        audio_bytes = await loop.run_in_executor(None, _read_file)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = Path(normalized_path).name
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

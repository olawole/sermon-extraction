import asyncio
import io
import logging
import os
import tempfile
from pathlib import Path
import openai
from app.core.config import settings
from app.infrastructure.ai.transcription.base import TranscriptionProvider, TranscriptChunkData
from app.infrastructure.utils.subprocess_helper import run_subprocess

logger = logging.getLogger(__name__)


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
        
        # Whisper limit is 25MB, we use 24MB as a safe threshold
        max_size = 24 * 1024 * 1024
        current_size = audio_file_path.stat().st_size
        
        if current_size <= max_size:
            return await self._transcribe_single_file(audio_file_path)
        else:
            return await self._transcribe_chunks(audio_file_path)

    async def _transcribe_single_file(self, audio_file_path: Path, offset_seconds: float = 0.0) -> list[TranscriptChunkData]:
        normalized_path = str(audio_file_path)
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
            start = float(segment.get("start", 0.0) if isinstance(segment, dict) else segment.start)
            end = float(segment.get("end", 0.0) if isinstance(segment, dict) else segment.end)
            text = (segment.get("text", "") if isinstance(segment, dict) else segment.text).strip()
            
            chunks.append(TranscriptChunkData(
                chunk_index=i,
                start_seconds=start + offset_seconds,
                end_seconds=end + offset_seconds,
                text=text,
                speaker_id=None,
                confidence=None,
            ))
        return chunks

    async def _transcribe_chunks(self, audio_file_path: Path) -> list[TranscriptChunkData]:
        chunk_duration = 1200  # 20 minutes
        all_chunks: list[TranscriptChunkData] = []
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            segment_pattern = tmpdir_path / "segment%03d.mp3"
            
            cmd = [
                settings.ffmpeg_path, "-y",
                "-i", str(audio_file_path),
                "-f", "segment",
                "-segment_time", str(chunk_duration),
                "-c", "copy",
                str(segment_pattern)
            ]
            
            logger.info(f"Splitting large audio file {audio_file_path} into 20-minute chunks")
            _, stderr, returncode = await run_subprocess(cmd, timeout=300)
            if returncode != 0:
                raise RuntimeError(f"ffmpeg segmentation failed: {stderr.decode()[:500]}")
            
            segment_files = sorted(list(tmpdir_path.glob("segment*.mp3")))
            
            for i, segment_path in enumerate(segment_files):
                offset = i * chunk_duration
                logger.info(f"Transcribing segment {i} ({segment_path.name}) with offset {offset}s")
                segment_chunks = await self._transcribe_single_file(segment_path, offset_seconds=offset)
                all_chunks.extend(segment_chunks)
                
        # Re-index all chunks globally
        for i, chunk in enumerate(all_chunks):
            chunk.chunk_index = i
            
        return all_chunks

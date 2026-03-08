from __future__ import annotations
import asyncio
import logging
import os
from app.core.config import settings

logger = logging.getLogger(__name__)


class AudioExtractionService:
    async def extract_audio(self, video_path: str, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = [
            settings.ffmpeg_path, "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            output_path,
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                raise RuntimeError(f"ffmpeg audio extraction failed: {stderr.decode()[:500]}")
            return output_path
        except FileNotFoundError:
            raise RuntimeError(f"ffmpeg not found at {settings.ffmpeg_path}")

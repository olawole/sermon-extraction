from __future__ import annotations
import logging
import os
from app.core.config import settings
from app.infrastructure.utils.subprocess_helper import run_subprocess

logger = logging.getLogger(__name__)


class AudioExtractionService:
    async def extract_audio(self, video_path: str, output_path: str, log_path: str | os.PathLike | None = None) -> str:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = [
            settings.ffmpeg_path, "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "libmp3lame",
            "-b:a", "32k",
            "-ar", "16000",
            "-ac", "1",
            output_path,
        ]
        try:
            _, stderr, returncode = await run_subprocess(
                cmd,
                timeout=600,  # 10 minutes timeout for audio extraction
                log_path=log_path,
            )
            if returncode != 0:
                raise RuntimeError(f"ffmpeg audio extraction failed: {stderr.decode()[:500]}")
            return output_path
        except FileNotFoundError:
            raise RuntimeError(f"ffmpeg not found at {settings.ffmpeg_path}")

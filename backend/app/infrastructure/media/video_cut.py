from __future__ import annotations
import logging
import os
from typing import Optional
from app.core.config import settings
from app.infrastructure.utils.subprocess_helper import run_subprocess

logger = logging.getLogger(__name__)


class VideoCutService:
    async def cut_segment(self, source_path: str, start: float, end: float, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        duration = end - start
        cmd = [
            settings.ffmpeg_path, "-y",
            "-ss", str(start),
            "-i", source_path,
            "-t", str(duration),
            "-c", "copy",
            output_path,
        ]
        try:
            _, stderr, returncode = await run_subprocess(cmd)
            if returncode != 0:
                raise RuntimeError(f"ffmpeg cut failed: {stderr.decode()[:500]}")
            return output_path
        except FileNotFoundError:
            raise RuntimeError(f"ffmpeg not found at {settings.ffmpeg_path}")

    async def render_vertical(
        self,
        source_path: str,
        start: float,
        end: float,
        output_path: str,
        burn_subtitles_path: Optional[str] = None,
    ) -> str:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        duration = end - start
        vf = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
        if burn_subtitles_path:
            vf += f",subtitles={burn_subtitles_path}"
        cmd = [
            settings.ffmpeg_path, "-y",
            "-ss", str(start),
            "-i", source_path,
            "-t", str(duration),
            "-vf", vf,
            "-c:v", "libx264",
            "-c:a", "aac",
            output_path,
        ]
        try:
            _, stderr, returncode = await run_subprocess(cmd)
            if returncode != 0:
                raise RuntimeError(f"ffmpeg render failed: {stderr.decode()[:500]}")
            return output_path
        except FileNotFoundError:
            raise RuntimeError(f"ffmpeg not found at {settings.ffmpeg_path}")

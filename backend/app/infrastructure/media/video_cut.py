from __future__ import annotations
import logging
import os
from typing import Optional
from app.core.config import settings
from app.infrastructure.utils.subprocess_helper import run_subprocess

logger = logging.getLogger(__name__)


class VideoCutService:
    async def cut_segment(self, source_path: str, start: float, end: float, output_path: str, log_path: str | os.PathLike | None = None) -> str:
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
            _, stderr, returncode = await run_subprocess(
                cmd,
                timeout=300,  # 5 minutes timeout for fast copy-cuts
                log_path=log_path,
            )
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
        log_path: str | os.PathLike | None = None,
    ) -> str:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        duration = end - start
        
        # Advanced vertical rendering with blurred background
        filter_complex = (
            f"[0:v]split=2[bg][fg]; "
            f"[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:10[bg_blurred]; "
            f"[fg]scale=1080:-1[fg_scaled]; "
            f"[bg_blurred][fg_scaled]overlay=(W-w)/2:(H-h)/2"
        )
        
        if burn_subtitles_path:
            # Escape path for ffmpeg subtitles filter
            escaped_sub_path = burn_subtitles_path.replace("\\", "/").replace(":", "\\:")
            filter_complex += f",subtitles='{escaped_sub_path}'"

        cmd = [
            settings.ffmpeg_path, "-y",
            "-ss", str(start),
            "-i", source_path,
            "-t", str(duration),
            "-filter_complex", filter_complex,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-aspect", "9:16",
            output_path,
        ]
        try:
            _, stderr, returncode = await run_subprocess(
                cmd,
                timeout=900,  # 15 minutes timeout for full vertical re-encoding
                log_path=log_path,
            )
            if returncode != 0:
                raise RuntimeError(f"ffmpeg render failed: {stderr.decode()[:500]}")
            return output_path
        except FileNotFoundError:
            raise RuntimeError(f"ffmpeg not found at {settings.ffmpeg_path}")

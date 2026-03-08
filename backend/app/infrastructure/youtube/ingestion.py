from __future__ import annotations
import asyncio
import json
import logging
import os
import re
import subprocess
from typing import Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class VideoIngestionService:
    def validate_url(self, url: str) -> bool:
        patterns = [
            r"(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+",
            r"(https?://)?youtu\.be/[\w-]+",
        ]
        return any(re.search(p, url) for p in patterns)

    async def download(self, url: str, output_dir: str) -> dict[str, Any]:
        os.makedirs(output_dir, exist_ok=True)
        cmd = [
            settings.ytdlp_path,
            "--no-playlist",
            "--print-json",
            "--output", os.path.join(output_dir, "%(id)s.%(ext)s"),
            url,
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                raise RuntimeError(f"yt-dlp failed: {stderr.decode()[:500]}")
            info = json.loads(stdout.decode().strip().splitlines()[-1])
            # yt-dlp stores the actual saved path in _filename; fall back to
            # reconstructing it from the output template %(id)s.%(ext)s
            file_path = info.get("_filename") or os.path.join(
                output_dir,
                f"{info.get('id', '')}.{info.get('ext', 'mp4')}",
            )
            return {
                "title": info.get("title", ""),
                "duration": info.get("duration", 0),
                "file_path": file_path,
            }
        except FileNotFoundError:
            raise RuntimeError(f"yt-dlp not found at {settings.ytdlp_path}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse yt-dlp output: {e}")

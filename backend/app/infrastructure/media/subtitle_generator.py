from __future__ import annotations
import os
from app.infrastructure.ai.transcription.base import TranscriptChunkData


def _format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _format_vtt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


class SubtitleGenerator:
    def generate_srt(
        self,
        chunks: list[TranscriptChunkData],
        sermon_start: float,
        output_path: str,
    ) -> str:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        lines: list[str] = []
        for i, chunk in enumerate(chunks, 1):
            start = max(0.0, chunk.start_seconds - sermon_start)
            end = max(0.0, chunk.end_seconds - sermon_start)
            lines.append(str(i))
            lines.append(f"{_format_srt_time(start)} --> {_format_srt_time(end)}")
            lines.append(chunk.text)
            lines.append("")
        content = "\n".join(lines)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path

    def generate_vtt(
        self,
        chunks: list[TranscriptChunkData],
        sermon_start: float,
        output_path: str,
    ) -> str:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        lines: list[str] = ["WEBVTT", ""]
        for chunk in chunks:
            start = max(0.0, chunk.start_seconds - sermon_start)
            end = max(0.0, chunk.end_seconds - sermon_start)
            lines.append(f"{_format_vtt_time(start)} --> {_format_vtt_time(end)}")
            lines.append(chunk.text)
            lines.append("")
        content = "\n".join(lines)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path

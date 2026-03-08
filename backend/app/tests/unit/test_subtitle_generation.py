import pytest
import os
import tempfile
from app.infrastructure.media.subtitle_generator import SubtitleGenerator
from app.infrastructure.ai.transcription.base import TranscriptChunkData


def make_chunks():
    return [
        TranscriptChunkData(chunk_index=0, start_seconds=100.0, end_seconds=110.0, text="Hello world"),
        TranscriptChunkData(chunk_index=1, start_seconds=110.0, end_seconds=120.0, text="This is a test"),
    ]


def test_srt_generation():
    generator = SubtitleGenerator()
    chunks = make_chunks()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.srt")
        result = generator.generate_srt(chunks, sermon_start=100.0, output_path=path)
        assert os.path.exists(result)
        content = open(result).read()
        assert "00:00:00,000" in content  # first chunk relative to sermon_start
        assert "Hello world" in content


def test_vtt_generation():
    generator = SubtitleGenerator()
    chunks = make_chunks()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.vtt")
        result = generator.generate_vtt(chunks, sermon_start=100.0, output_path=path)
        assert os.path.exists(result)
        content = open(result).read()
        assert "WEBVTT" in content
        assert "00:00:00.000" in content
        assert "Hello world" in content


def test_srt_relative_timestamps():
    generator = SubtitleGenerator()
    chunks = [TranscriptChunkData(chunk_index=0, start_seconds=3600.0, end_seconds=3610.0, text="Late content")]
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.srt")
        generator.generate_srt(chunks, sermon_start=3600.0, output_path=path)
        content = open(path).read()
        # Timestamps should be relative (0s from sermon start)
        assert "00:00:00,000" in content

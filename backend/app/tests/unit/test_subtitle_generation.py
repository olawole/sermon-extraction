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
        with open(result) as f:
            content = f.read()
        assert "00:00:00,000" in content  # first chunk relative to sermon_start
        assert "Hello world" in content


def test_vtt_generation():
    generator = SubtitleGenerator()
    chunks = make_chunks()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.vtt")
        result = generator.generate_vtt(chunks, sermon_start=100.0, output_path=path)
        assert os.path.exists(result)
        with open(result) as f:
            content = f.read()
        assert "WEBVTT" in content
        assert "00:00:00.000" in content
        assert "Hello world" in content


def test_srt_with_sermon_end():
    generator = SubtitleGenerator()
    chunks = [
        TranscriptChunkData(chunk_index=0, start_seconds=100.0, end_seconds=110.0, text="Keep"),
        TranscriptChunkData(chunk_index=1, start_seconds=110.0, end_seconds=120.0, text="Keep also"),
        TranscriptChunkData(chunk_index=2, start_seconds=120.0, end_seconds=130.0, text="Discard"),
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.srt")
        # sermon_end is 120.0, so the third chunk (start=120, end=130) should be discarded 
        # because its end_seconds (130) > sermon_end (120).
        generator.generate_srt(chunks, sermon_start=100.0, output_path=path, sermon_end=120.0)
        with open(path) as f:
            content = f.read()
        assert "Keep" in content
        assert "Keep also" in content
        assert "Discard" not in content


def test_ass_generation():
    generator = SubtitleGenerator()
    chunks = make_chunks()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.ass")
        result = generator.generate_ass(chunks, sermon_start=100.0, output_path=path)
        assert os.path.exists(result)
        with open(result) as f:
            content = f.read()
        assert "[Script Info]" in content
        assert "[V4+ Styles]" in content
        assert "[Events]" in content
        assert "Style: Default,Arial,20,&H00FFFFFF" in content
        assert "Dialogue: 0,0:00:00.00,0:00:10.00,Default,,0,0,0,,Hello world" in content


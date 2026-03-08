from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.infrastructure.ai.transcription.whisper_provider import WhisperTranscriptionProvider


@pytest.mark.asyncio
async def test_transcribe_falls_back_to_sync_on_empty_buffer_assertion(tmp_path):
    audio_path = tmp_path / "sample.wav"
    audio_path.write_bytes(b"not-empty")

    with patch("app.infrastructure.ai.transcription.whisper_provider.openai.AsyncOpenAI", return_value=MagicMock()):
        with patch("app.infrastructure.ai.transcription.whisper_provider.openai.OpenAI", return_value=MagicMock()):
            provider = WhisperTranscriptionProvider()

    async def fail_async(_path: str):
        raise AssertionError("Data should not be empty")

    provider._transcribe_async = fail_async
    provider._transcribe_sync = MagicMock(return_value=SimpleNamespace(segments=[
        {"start": 1.0, "end": 2.0, "text": "hello world"}
    ]))

    chunks = await provider.transcribe(str(audio_path))

    provider._transcribe_sync.assert_called_once()
    assert len(chunks) == 1
    assert chunks[0].text == "hello world"


@pytest.mark.asyncio
async def test_transcribe_reraises_unrelated_assertion(tmp_path):
    audio_path = tmp_path / "sample.wav"
    audio_path.write_bytes(b"not-empty")

    with patch("app.infrastructure.ai.transcription.whisper_provider.openai.AsyncOpenAI", return_value=MagicMock()):
        with patch("app.infrastructure.ai.transcription.whisper_provider.openai.OpenAI", return_value=MagicMock()):
            provider = WhisperTranscriptionProvider()

    async def fail_async(_path: str):
        raise AssertionError("something else")

    provider._transcribe_async = fail_async

    with pytest.raises(AssertionError, match="something else"):
        await provider.transcribe(str(audio_path))

from __future__ import annotations
import pytest
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from app.infrastructure.ai.transcription.whisper_provider import WhisperTranscriptionProvider
from app.infrastructure.ai.transcription.base import TranscriptChunkData

@pytest.mark.asyncio
async def test_whisper_transcribe_file_not_found():
    provider = WhisperTranscriptionProvider()
    with pytest.raises(FileNotFoundError):
        await provider.transcribe("non_existent_file.wav")

@pytest.mark.asyncio
async def test_whisper_transcribe_empty_file(tmp_path):
    audio_path = tmp_path / "empty.wav"
    audio_path.touch()
    provider = WhisperTranscriptionProvider()
    with pytest.raises(ValueError, match="empty"):
        await provider.transcribe(str(audio_path))

@pytest.mark.asyncio
async def test_whisper_transcribe_success_object_response(tmp_path):
    audio_path = tmp_path / "test.wav"
    audio_path.write_bytes(b"fake audio data")
    
    provider = WhisperTranscriptionProvider()
    
    # Mock response from OpenAI with objects
    mock_segment = MagicMock()
    mock_segment.start = 0.0
    mock_segment.end = 5.0
    mock_segment.text = " Hello world "
    
    mock_response = MagicMock()
    mock_response.segments = [mock_segment]
    
    # Mock the client's transcribe method
    provider._client.audio.transcriptions.create = AsyncMock(return_value=mock_response)
    
    chunks = await provider.transcribe(str(audio_path))
    
    assert len(chunks) == 1
    assert chunks[0].start_seconds == 0.0
    assert chunks[0].end_seconds == 5.0
    assert chunks[0].text == "Hello world"
    provider._client.audio.transcriptions.create.assert_called_once()

@pytest.mark.asyncio
async def test_whisper_transcribe_success_dict_response(tmp_path):
    audio_path = tmp_path / "test_dict.wav"
    audio_path.write_bytes(b"fake audio data")
    
    provider = WhisperTranscriptionProvider()
    
    # Mock response from OpenAI with dicts
    mock_response = MagicMock()
    mock_response.segments = [
        {"start": 5.0, "end": 10.0, "text": " Secondary segment "}
    ]
    
    # Mock the client's transcribe method
    provider._client.audio.transcriptions.create = AsyncMock(return_value=mock_response)
    
    chunks = await provider.transcribe(str(audio_path))
    
    assert len(chunks) == 1
    assert chunks[0].start_seconds == 5.0
    assert chunks[0].end_seconds == 10.0
    assert chunks[0].text == "Secondary segment"
    provider._client.audio.transcriptions.create.assert_called_once()

@pytest.mark.asyncio
async def test_whisper_transcribe_chunking_logic(tmp_path):
    audio_path = tmp_path / "large.wav"
    # Create a file larger than 24MB to trigger chunking
    size = 25 * 1024 * 1024
    with open(audio_path, "wb") as f:
        f.seek(size - 1)
        f.write(b"0")
    
    provider = WhisperTranscriptionProvider()
    
    # Mock run_subprocess to avoid calling ffmpeg
    with patch("app.infrastructure.ai.transcription.whisper_provider.run_subprocess", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = (b"", b"", 0)
        
        # Mock segments in a temporary directory
        with patch("tempfile.TemporaryDirectory") as mock_tmpdir:
            tmp_dir_str = str(tmp_path / "fake_tmp")
            os.makedirs(tmp_dir_str, exist_ok=True)
            mock_tmpdir.return_value.__enter__.return_value = tmp_dir_str
            
            segment0 = Path(tmp_dir_str) / "segment000.mp3"
            segment1 = Path(tmp_dir_str) / "segment001.mp3"
            segment0.touch()
            segment1.touch()
            
            # Mock _transcribe_single_file to simulate offsetting
            with patch.object(WhisperTranscriptionProvider, "_transcribe_single_file", new_callable=AsyncMock) as mock_single:
                async def side_effect(path, offset_seconds=0.0):
                    if "segment000" in str(path):
                        return [TranscriptChunkData(chunk_index=0, start_seconds=10.0 + offset_seconds, end_seconds=20.0 + offset_seconds, text="First")]
                    else:
                        return [TranscriptChunkData(chunk_index=0, start_seconds=5.0 + offset_seconds, end_seconds=15.0 + offset_seconds, text="Second")]
                
                mock_single.side_effect = side_effect
                
                chunks = await provider.transcribe(str(audio_path))
                
                # Verify results
                assert len(chunks) == 2
                # Chunk 0 from segment 0 (offset 0)
                assert chunks[0].text == "First"
                assert chunks[0].start_seconds == 10.0
                assert chunks[0].chunk_index == 0
                
                # Chunk 1 from segment 1 (offset 1200)
                assert chunks[1].text == "Second"
                assert chunks[1].start_seconds == 1205.0  # 5 + 1200
                assert chunks[1].end_seconds == 1215.0    # 15 + 1200
                assert chunks[1].chunk_index == 1         # Re-indexed globally
                
                assert mock_single.call_count == 2
                # Verify offsets passed to calls
                assert mock_single.call_args_list[0].kwargs["offset_seconds"] == 0.0
                assert mock_single.call_args_list[1].kwargs["offset_seconds"] == 1200.0
                mock_run.assert_called_once()
                # Check ffmpeg command
                cmd = mock_run.call_args[0][0]
                assert "ffmpeg" in cmd[0]
                assert "-segment_time" in cmd
                assert "1200" in cmd

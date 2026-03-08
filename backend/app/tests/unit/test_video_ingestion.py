from __future__ import annotations
import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_download_uses_filename_field_when_present(tmp_path):
    """_filename in yt-dlp JSON output is used as the file_path."""
    from app.infrastructure.youtube.ingestion import VideoIngestionService

    info = {
        "id": "abc123",
        "ext": "mp4",
        "title": "Test Video",
        "duration": 120,
        "_filename": str(tmp_path / "abc123.mp4"),
    }
    stdout = json.dumps(info).encode()

    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(stdout, b""))

    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_proc)):
        service = VideoIngestionService()
        result = await service.download("https://youtube.com/watch?v=abc123", str(tmp_path))

    assert result["file_path"] == str(tmp_path / "abc123.mp4")
    assert result["title"] == "Test Video"
    assert result["duration"] == 120


@pytest.mark.asyncio
async def test_download_falls_back_to_reconstructed_path_when_filename_missing(tmp_path):
    """Without _filename, the path is reconstructed from id and ext."""
    from app.infrastructure.youtube.ingestion import VideoIngestionService

    info = {
        "id": "xyz789",
        "ext": "webm",
        "title": "Another Video",
        "duration": 60,
    }
    stdout = json.dumps(info).encode()

    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(stdout, b""))

    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_proc)):
        service = VideoIngestionService()
        result = await service.download("https://youtu.be/xyz789", str(tmp_path))

    expected_path = os.path.join(str(tmp_path), "xyz789.webm")
    assert result["file_path"] == expected_path


@pytest.mark.asyncio
async def test_download_raises_when_ytdlp_not_found(tmp_path):
    """FileNotFoundError from yt-dlp is wrapped in a RuntimeError."""
    from app.infrastructure.youtube.ingestion import VideoIngestionService

    with patch("asyncio.create_subprocess_exec", AsyncMock(side_effect=FileNotFoundError)):
        service = VideoIngestionService()
        with pytest.raises(RuntimeError, match="yt-dlp not found"):
            await service.download("https://youtube.com/watch?v=abc123", str(tmp_path))


@pytest.mark.asyncio
async def test_download_raises_when_ytdlp_fails(tmp_path):
    """Non-zero yt-dlp exit code raises RuntimeError."""
    from app.infrastructure.youtube.ingestion import VideoIngestionService

    mock_proc = MagicMock()
    mock_proc.returncode = 1
    mock_proc.communicate = AsyncMock(return_value=(b"", b"some error"))

    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_proc)):
        service = VideoIngestionService()
        with pytest.raises(RuntimeError, match="yt-dlp failed"):
            await service.download("https://youtube.com/watch?v=abc123", str(tmp_path))


@pytest.mark.asyncio
async def test_download_falls_back_when_create_subprocess_not_implemented(tmp_path):
    """Falls back to subprocess.run when asyncio.create_subprocess_exec raises NotImplementedError."""
    from app.infrastructure.youtube.ingestion import VideoIngestionService

    info = {
        "id": "abc123",
        "ext": "mp4",
        "title": "Fallback Video",
        "duration": 90,
        "_filename": str(tmp_path / "abc123.mp4"),
    }
    stdout = json.dumps(info).encode()

    mock_result = MagicMock()
    mock_result.stdout = stdout
    mock_result.stderr = b""
    mock_result.returncode = 0

    with patch("asyncio.create_subprocess_exec", AsyncMock(side_effect=NotImplementedError)):
        with patch("subprocess.run", return_value=mock_result):
            service = VideoIngestionService()
            result = await service.download("https://youtube.com/watch?v=abc123", str(tmp_path))

    assert result["file_path"] == str(tmp_path / "abc123.mp4")
    assert result["title"] == "Fallback Video"
    assert result["duration"] == 90

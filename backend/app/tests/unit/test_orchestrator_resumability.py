from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from app.workflows.orchestrators.job_orchestrator import JobOrchestrator
from app.domain.services.job_service import JobService
from app.domain.enums.enums import JobStage, SectionLabel
from app.infrastructure.ai.transcription.base import TranscriptChunkData
from app.infrastructure.ai.classification.base import ClassificationResult, ClassificationWindow

class MockTranscriptionProvider:
    async def transcribe(self, audio_path: str, duration_seconds: float = 3600.0) -> list[TranscriptChunkData]:
        return [
            TranscriptChunkData(
                chunk_index=0,
                start_seconds=0.0,
                end_seconds=10.0,
                text="Test transcription",
                speaker_id="speaker_1",
                confidence=0.9,
            )
        ]

class MockClassificationProvider:
    async def classify(self, windows: list[ClassificationWindow]) -> list[ClassificationResult]:
        return [
            ClassificationResult(
                start_seconds=0.0,
                end_seconds=2000.0,  # 33.3 minutes, should pass sermon duration filter
                label=SectionLabel.sermon,
                confidence=0.95,
            )
        ]

@pytest.mark.asyncio
async def test_orchestrator_resumability(db_session, tmp_path):
    session, _ = db_session
    orchestrator = JobOrchestrator(session)
    job_service = JobService(session)
    
    # Create a job
    job = await job_service.create_job("https://youtube.com/watch?v=test_resumability")
    job_id = job.id
    
    # Setup mocks
    mock_download = AsyncMock(return_value={
        "file_path": str(tmp_path / "original.mp4"),
        "title": "Test Resumability",
        "duration": 2500.0
    })
    
    async def mock_extract_audio_side_effect(video_path, audio_path):
        with open(audio_path, "wb") as f:
            f.write(b"fake audio data")
            
    mock_extract_audio = AsyncMock(side_effect=mock_extract_audio_side_effect)
    mock_transcribe = AsyncMock(side_effect=MockTranscriptionProvider().transcribe)
    mock_classify = AsyncMock(side_effect=MockClassificationProvider().classify)
    mock_cut_segment = AsyncMock()
    mock_subtitle = MagicMock()
    
    # Mock files
    (tmp_path / "original.mp4").touch()
    
    with patch.object(orchestrator.ingestion, "download", mock_download), \
         patch.object(orchestrator.audio_extractor, "extract_audio", mock_extract_audio), \
         patch.object(orchestrator.transcription_provider, "transcribe", mock_transcribe), \
         patch.object(orchestrator.classifier, "classify", mock_classify), \
         patch.object(orchestrator.video_cutter, "cut_segment", mock_cut_segment), \
         patch.object(orchestrator.subtitle_generator, "generate_srt", mock_subtitle), \
         patch.object(orchestrator.subtitle_generator, "generate_vtt", mock_subtitle), \
         patch.object(orchestrator.storage, "job_dir", return_value=str(tmp_path)):

        # First run
        await orchestrator._run(job_id)
        
        # Verify calls
        assert mock_download.call_count == 1
        assert mock_extract_audio.call_count == 1
        assert mock_transcribe.call_count == 1
        assert mock_classify.call_count == 1
        assert (tmp_path / "video.mp4").exists()
        assert (tmp_path / "audio.mp3").exists()
        
        # Verify job stage is completed
        await session.refresh(job)
        assert job.stage == JobStage.completed.value
        
        # Create sermon.mp4 to satisfy is_sermon_export_done
        (tmp_path / "sermon.mp4").touch()
        
        # Second run - should skip everything
        await orchestrator._run(job_id)
        
        # Call counts should remain 1
        assert mock_download.call_count == 1
        assert mock_extract_audio.call_count == 1
        assert mock_transcribe.call_count == 1
        assert mock_classify.call_count == 1

@pytest.mark.asyncio
async def test_orchestrator_partial_resumability(db_session, tmp_path):
    session, _ = db_session
    orchestrator = JobOrchestrator(session)
    job_service = JobService(session)
    
    # Create a job
    job = await job_service.create_job("https://youtube.com/watch?v=test_partial")
    job_id = job.id
    
    # Setup mocks
    mock_download = AsyncMock(return_value={
        "file_path": str(tmp_path / "video.mp4"),
        "title": "Test Partial",
        "duration": 2500.0
    })
    mock_extract_audio = AsyncMock()
    mock_transcribe = AsyncMock(side_effect=MockTranscriptionProvider().transcribe)
    mock_classify = AsyncMock(side_effect=MockClassificationProvider().classify)
    mock_cut_segment = AsyncMock()
    mock_subtitle = MagicMock()
    
    # Create video.mp4 and audio.mp3 manually to simulate partially completed stages
    (tmp_path / "video.mp4").touch()
    with open(tmp_path / "audio.mp3", "wb") as f:
        f.write(b"fake audio data")
    
    # Set duration in DB
    job.duration_seconds = 2500.0
    await session.commit()
    
    with patch.object(orchestrator.ingestion, "download", mock_download), \
         patch.object(orchestrator.audio_extractor, "extract_audio", mock_extract_audio), \
         patch.object(orchestrator.transcription_provider, "transcribe", mock_transcribe), \
         patch.object(orchestrator.classifier, "classify", mock_classify), \
         patch.object(orchestrator.video_cutter, "cut_segment", mock_cut_segment), \
         patch.object(orchestrator.subtitle_generator, "generate_srt", mock_subtitle), \
         patch.object(orchestrator.subtitle_generator, "generate_vtt", mock_subtitle), \
         patch.object(orchestrator.storage, "job_dir", return_value=str(tmp_path)):

        # Run pipeline
        await orchestrator._run(job_id)
        
        # Download and audio extraction should be skipped
        assert mock_download.call_count == 0
        assert mock_extract_audio.call_count == 0
        # Transcription should be called
        assert mock_transcribe.call_count == 1
        # Classification should be called
        assert mock_classify.call_count == 1

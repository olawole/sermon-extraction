from __future__ import annotations
import asyncio
import os
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from app.workers.background_worker import run_job_pipeline
from app.domain.enums.enums import JobStage, SectionLabel
from app.domain.services.job_service import JobService
from app.infrastructure.ai.transcription.base import TranscriptChunkData
from app.infrastructure.ai.classification.base import ClassificationResult, ClassificationWindow
from app.infrastructure.storage.local_storage import LocalStorageService

# Mock data for different scenarios
class MockProviders:
    def __init__(self, scenario_name: str, duration: float):
        self.scenario_name = scenario_name
        self.duration = duration

    async def transcribe(self, audio_path: str, duration_seconds: float = 3600.0) -> list[TranscriptChunkData]:
        # Generate some chunks based on duration
        chunks = []
        n_chunks = 20
        interval = duration_seconds / n_chunks
        for i in range(n_chunks):
            start = i * interval
            end = start + interval * 0.9
            chunks.append(TranscriptChunkData(
                chunk_index=i,
                start_seconds=round(start, 2),
                end_seconds=round(end, 2),
                text=f"This is chunk {i} of {self.scenario_name}",
                speaker_id="speaker_1",
                confidence=0.95,
            ))
        return chunks

    async def classify(self, windows: list[ClassificationWindow]) -> list[ClassificationResult]:
        results = []
        for w in windows:
            mid = (w.start_seconds + w.end_seconds) / 2
            label = SectionLabel.other
            
            if self.scenario_name == "Job A":
                # Job A (Single Service): ~60 minutes, no transition segments, one long sermon.
                if 0 <= mid < 900: label = SectionLabel.praise_worship
                elif 900 <= mid < 1200: label = SectionLabel.prayer
                elif 1200 <= mid < 3000: label = SectionLabel.sermon
                else: label = SectionLabel.other
            
            elif self.scenario_name == "Job B":
                # Job B (Two Services): ~120 minutes, with a transition segment at ~60 mins, sermon in the second service.
                # Service 1: 0 - 3600
                if 0 <= mid < 1200: label = SectionLabel.praise_worship
                elif 1200 <= mid < 3000: label = SectionLabel.sermon
                elif 3000 <= mid < 3600: label = SectionLabel.other
                # Transition: 3600 - 3900
                elif 3600 <= mid < 3900: label = SectionLabel.transition
                # Service 2: 3900 - 7200
                elif 3900 <= mid < 4500: label = SectionLabel.praise_worship
                elif 4500 <= mid < 6500: label = SectionLabel.sermon
                else: label = SectionLabel.other
                
            elif self.scenario_name == "Job C":
                # Job C (Multi-segment Sermon): ~90 minutes, sermon split by a 1-minute other segment to verify merging logic.
                if 0 <= mid < 1000: label = SectionLabel.praise_worship
                elif 1000 <= mid < 2000: label = SectionLabel.sermon
                elif 2000 <= mid < 2060: label = SectionLabel.other
                elif 2060 <= mid < 3500: label = SectionLabel.sermon
                else: label = SectionLabel.other
            
            results.append(ClassificationResult(
                start_seconds=w.start_seconds,
                end_seconds=w.end_seconds,
                label=label,
                confidence=0.9,
            ))
        return results

async def run_scenario(db_session_factory, scenario_name, duration, youtube_url, storage_path):
    # Mock implementations for external tools
    async def mock_download(url, job_dir):
        video_path = Path(job_dir) / "video.mp4"
        video_path.touch()
        return {"file_path": str(video_path), "title": f"Test {scenario_name}", "duration": duration}

    async def mock_extract_audio(video_path, audio_path):
        Path(audio_path).touch()
        # Need some size > 0 for orchestrator check
        with open(audio_path, "wb") as f:
            f.write(b"fake audio data")

    async def mock_cut_segment(source_path, start, end, output_path):
        Path(output_path).touch()

    def mock_generate_srt(transcript, start, srt_path, sermon_end=None):
        Path(srt_path).touch()

    def mock_generate_vtt(transcript, start, vtt_path, sermon_end=None):
        Path(vtt_path).touch()
    providers = MockProviders(scenario_name, duration)

    with patch("app.workflows.orchestrators.job_orchestrator.VideoIngestionService.download", side_effect=mock_download), \
         patch("app.workflows.orchestrators.job_orchestrator.AudioExtractionService.extract_audio", side_effect=mock_extract_audio), \
         patch("app.workflows.orchestrators.job_orchestrator.VideoCutService.cut_segment", side_effect=mock_cut_segment), \
         patch("app.workflows.orchestrators.job_orchestrator.SubtitleGenerator.generate_srt", side_effect=mock_generate_srt), \
         patch("app.workflows.orchestrators.job_orchestrator.SubtitleGenerator.generate_vtt", side_effect=mock_generate_vtt), \
         patch("app.workflows.orchestrators.job_orchestrator.get_transcription_provider", return_value=providers), \
         patch("app.workflows.orchestrators.job_orchestrator.get_classification_provider", return_value=providers), \
         patch("app.workflows.orchestrators.job_orchestrator.LocalStorageService.job_dir", return_value=storage_path), \
         patch("app.workers.background_worker.AsyncSessionLocal", side_effect=db_session_factory):

        # Create job
        async with db_session_factory() as db:
            job_service = JobService(db)
            job = await job_service.create_job(youtube_url)
            job_id = job.id
            await db.commit()

        # Run pipeline
        await run_job_pipeline(job_id)

        # Verify results
        async with db_session_factory() as db:
            job_service = JobService(db)
            job = await job_service.get_job(job_id)
            assert job.stage == JobStage.completed
            
            highlights = await job_service.get_highlights(job_id)
            assert len(highlights) > 0

        # Verify storage
        job_storage_path = Path(storage_path)
        assert (job_storage_path / "audio.mp3").exists()
        assert (job_storage_path / "sermon.mp4").exists()
        assert (job_storage_path / "sermon.srt").exists()

@pytest.mark.asyncio
async def test_full_pipeline_scenarios(db_session, tmp_path):
    _, session_factory = db_session
    
    # Scenarios
    scenarios = [
        ("Job A", 3600.0, "https://youtube.com/watch?v=jobA"),
        ("Job B", 7200.0, "https://youtube.com/watch?v=jobB"),
        ("Job C", 5400.0, "https://youtube.com/watch?v=jobC"),
    ]
    
    for name, duration, url in scenarios:
        storage_path = tmp_path / name.replace(" ", "_")
        storage_path.mkdir()
        await run_scenario(session_factory, name, duration, url, str(storage_path))

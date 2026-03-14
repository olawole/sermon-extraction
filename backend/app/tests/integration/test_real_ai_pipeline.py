from __future__ import annotations
import pytest
import os
from pathlib import Path
from app.core.config import settings
from app.domain.services.job_service import JobService
from app.domain.enums.enums import JobStage
from app.workers.background_worker import run_job_pipeline
from app.infrastructure.storage.local_storage import LocalStorageService

@pytest.mark.asyncio
async def test_real_ai_pipeline_flow(db_session, tmp_path):
    """
    Integration test that uses REAL AI providers if API keys are set.
    Otherwise, it might fail or skip depending on how providers handle missing keys.
    We check for settings.openai_api_key specifically.
    """
    if not settings.openai_api_key or settings.openai_api_key == "sk-...":
        pytest.skip("OpenAI API key not set, skipping real AI pipeline test")

    _, session_factory = db_session
    storage = LocalStorageService()
    
    # We'll use a very short, real video or a mock that still triggers real AI
    # For now, let's use a known short video URL if possible, 
    # or just rely on the orchestrator using real providers.
    youtube_url = "https://www.youtube.com/watch?v=rtfVv7ZpXIs" # Very short video (few seconds)

    async with session_factory() as db:
        job_service = JobService(db)
        job = await job_service.create_job(youtube_url)
        job_id = job.id
        await db.commit()

    # Override storage for test
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.infrastructure.storage.local_storage.LocalStorageService.base_dir", str(tmp_path))
        
        # Run pipeline
        # This will call real OpenAI/Whisper if configured in settings
        await run_job_pipeline(job_id)

    async with session_factory() as db:
        job_service = JobService(db)
        job = await job_service.get_job(job_id)
        
        # If it failed due to rate limits or other AI issues, we at least see it
        assert job.stage == JobStage.completed, f"Job failed with error: {job.error_message}"
        
        # Verify we have segments and highlights
        sections, services, sermon = await job_service.get_segments(job_id)
        assert len(sections) > 0
        assert sermon is not None
        
        highlights = await job_service.get_highlights(job_id)
        assert len(highlights) > 0

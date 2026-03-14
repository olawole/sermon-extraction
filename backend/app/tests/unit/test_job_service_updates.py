from __future__ import annotations
import pytest
from app.domain.services.job_service import JobService
from app.domain.models.models import VideoJob, SermonSegment, HighlightClip
from app.domain.enums.enums import JobStage, HighlightStatus


@pytest.mark.asyncio
async def test_update_sermon_segment(db_session):
    session, _ = db_session
    service = JobService(session)
    job = await service.create_job("https://youtube.com/watch?v=123")
    
    sermon = SermonSegment(
        job_id=job.id,
        service_number=1,
        start_seconds=10.0,
        end_seconds=100.0,
        confidence=0.9
    )
    session.add(sermon)
    await session.commit()
    
    updated_sermon = await service.update_sermon_segment(job.id, 20.0, 110.0)
    assert updated_sermon.start_seconds == 20.0
    assert updated_sermon.end_seconds == 110.0


@pytest.mark.asyncio
async def test_update_highlight_segment(db_session):
    session, _ = db_session
    service = JobService(session)
    job = await service.create_job("https://youtube.com/watch?v=123")
    
    highlight = HighlightClip(
        job_id=job.id,
        start_seconds=10.0,
        end_seconds=20.0,
        score=0.9,
        category="test",
        title="Test Highlight",
        hook_text="Test Hook",
        transcript="Test Transcript",
        status=HighlightStatus.pending.value
    )
    session.add(highlight)
    await session.commit()
    await session.refresh(highlight)
    
    updated_highlight = await service.update_highlight_segment(highlight.id, 15.0, 25.0)
    assert updated_highlight.start_seconds == 15.0
    assert updated_highlight.end_seconds == 25.0

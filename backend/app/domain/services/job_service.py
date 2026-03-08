from __future__ import annotations
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.models.models import (
    VideoJob, TranscriptChunk, SectionSegment, ServiceSegment,
    SermonSegment, HighlightClip, MediaAsset
)
from app.domain.enums.enums import JobStage, HighlightStatus
from datetime import datetime, timezone


class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(self, youtube_url: str) -> VideoJob:
        job = VideoJob(youtube_url=youtube_url, stage=JobStage.pending.value)
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_job(self, job_id: int) -> Optional[VideoJob]:
        result = await self.db.execute(select(VideoJob).where(VideoJob.id == job_id))
        return result.scalar_one_or_none()

    async def update_stage(self, job_id: int, stage: JobStage, error: Optional[str] = None) -> VideoJob:
        job = await self.get_job(job_id)
        if job is None:
            raise ValueError(f"Job {job_id} not found")
        job.stage = stage.value
        job.updated_at = datetime.now(timezone.utc)
        if error is not None:
            job.error_message = error
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def list_jobs(self) -> list[VideoJob]:
        result = await self.db.execute(select(VideoJob).order_by(VideoJob.created_at.desc()))
        return list(result.scalars().all())

    async def get_transcript(self, job_id: int) -> list[TranscriptChunk]:
        result = await self.db.execute(
            select(TranscriptChunk).where(TranscriptChunk.job_id == job_id).order_by(TranscriptChunk.chunk_index)
        )
        return list(result.scalars().all())

    async def get_segments(self, job_id: int) -> tuple[list[SectionSegment], list[ServiceSegment], Optional[SermonSegment]]:
        section_result = await self.db.execute(
            select(SectionSegment).where(SectionSegment.job_id == job_id).order_by(SectionSegment.start_seconds)
        )
        section_segments = list(section_result.scalars().all())

        service_result = await self.db.execute(
            select(ServiceSegment).where(ServiceSegment.job_id == job_id).order_by(ServiceSegment.service_number)
        )
        service_segments = list(service_result.scalars().all())

        sermon_result = await self.db.execute(
            select(SermonSegment).where(SermonSegment.job_id == job_id).order_by(SermonSegment.start_seconds).limit(1)
        )
        sermon_segment = sermon_result.scalar_one_or_none()

        return section_segments, service_segments, sermon_segment

    async def get_highlights(self, job_id: int) -> list[HighlightClip]:
        result = await self.db.execute(
            select(HighlightClip).where(HighlightClip.job_id == job_id).order_by(HighlightClip.score.desc())
        )
        return list(result.scalars().all())

    async def get_assets(self, job_id: int) -> list[MediaAsset]:
        result = await self.db.execute(
            select(MediaAsset).where(MediaAsset.job_id == job_id)
        )
        return list(result.scalars().all())

    async def update_highlight_status(self, highlight_id: int, status: HighlightStatus) -> HighlightClip:
        result = await self.db.execute(select(HighlightClip).where(HighlightClip.id == highlight_id))
        highlight = result.scalar_one_or_none()
        if highlight is None:
            raise ValueError(f"Highlight {highlight_id} not found")
        highlight.status = status.value
        await self.db.commit()
        await self.db.refresh(highlight)
        return highlight

    async def get_highlight(self, highlight_id: int) -> Optional[HighlightClip]:
        result = await self.db.execute(select(HighlightClip).where(HighlightClip.id == highlight_id))
        return result.scalar_one_or_none()

    async def get_approved_highlights(self, job_id: int) -> list[HighlightClip]:
        result = await self.db.execute(
            select(HighlightClip).where(
                HighlightClip.job_id == job_id,
                HighlightClip.status == HighlightStatus.approved.value,
            )
        )
        return list(result.scalars().all())

    async def attach_rendered_asset(self, highlight_id: int, asset: MediaAsset) -> HighlightClip:
        highlight = await self.get_highlight(highlight_id)
        if highlight is None:
            raise ValueError(f"Highlight {highlight_id} not found")
        self.db.add(asset)
        await self.db.flush()
        highlight.rendered_asset_id = asset.id
        highlight.status = HighlightStatus.rendered.value
        await self.db.commit()
        await self.db.refresh(highlight)
        return highlight

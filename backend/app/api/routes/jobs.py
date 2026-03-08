from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_db
from app.domain.services.job_service import JobService
from app.domain.enums.enums import HighlightStatus, JobStage
from app.api.schemas.jobs import (
    CreateJobRequest, JobResponse, JobDetailResponse, TranscriptResponse,
    SegmentsResponse, HighlightsResponse, AssetListResponse,
    TranscriptChunkSchema, SectionSegmentSchema, ServiceSegmentSchema,
    SermonSegmentSchema, HighlightClipSchema, MediaAssetSchema,
)
from app.workers.background_worker import run_job_pipeline, run_render_highlight

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(
    request: CreateJobRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    job = await service.create_job(str(request.youtube_url))
    background_tasks.add_task(run_job_pipeline, job.id)
    return job


@router.get("/", response_model=list[JobResponse])
async def list_jobs(db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    return await service.list_jobs()


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    job = await service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    assets = await service.get_assets(job_id)
    transcript = await service.get_transcript(job_id)
    section_segs, service_segs, sermon_seg = await service.get_segments(job_id)
    highlights = await service.get_highlights(job_id)

    return JobDetailResponse(
        id=job.id,
        youtube_url=job.youtube_url,
        title=job.title,
        duration_seconds=job.duration_seconds,
        stage=job.stage,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
        assets=[MediaAssetSchema.model_validate(a) for a in assets],
        transcript_chunks=[TranscriptChunkSchema.model_validate(c) for c in transcript],
        section_segments=[SectionSegmentSchema.model_validate(s) for s in section_segs],
        service_segments=[ServiceSegmentSchema.model_validate(s) for s in service_segs],
        sermon_segment=SermonSegmentSchema.model_validate(sermon_seg) if sermon_seg else None,
        highlights=[HighlightClipSchema.model_validate(h) for h in highlights],
    )


@router.get("/{job_id}/transcript", response_model=TranscriptResponse)
async def get_transcript(job_id: int, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    job = await service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    chunks = await service.get_transcript(job_id)
    return TranscriptResponse(
        job_id=job_id,
        chunks=[TranscriptChunkSchema.model_validate(c) for c in chunks],
    )


@router.get("/{job_id}/segments", response_model=SegmentsResponse)
async def get_segments(job_id: int, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    job = await service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    section_segs, service_segs, sermon_seg = await service.get_segments(job_id)
    return SegmentsResponse(
        job_id=job_id,
        section_segments=[SectionSegmentSchema.model_validate(s) for s in section_segs],
        service_segments=[ServiceSegmentSchema.model_validate(s) for s in service_segs],
        sermon_segment=SermonSegmentSchema.model_validate(sermon_seg) if sermon_seg else None,
    )


@router.get("/{job_id}/highlights", response_model=HighlightsResponse)
async def get_highlights(job_id: int, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    job = await service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    highlights = await service.get_highlights(job_id)
    return HighlightsResponse(
        job_id=job_id,
        highlights=[HighlightClipSchema.model_validate(h) for h in highlights],
    )


@router.get("/{job_id}/assets", response_model=AssetListResponse)
async def get_assets(job_id: int, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    job = await service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    assets = await service.get_assets(job_id)
    return AssetListResponse(
        job_id=job_id,
        assets=[MediaAssetSchema.model_validate(a) for a in assets],
    )


@router.post("/{job_id}/highlights/{highlight_id}/approve", response_model=HighlightClipSchema)
async def approve_highlight(job_id: int, highlight_id: int, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    try:
        highlight = await service.update_highlight_status(highlight_id, HighlightStatus.approved)
        return HighlightClipSchema.model_validate(highlight)
    except ValueError:
        raise HTTPException(status_code=404, detail="Highlight not found")


@router.post("/{job_id}/highlights/{highlight_id}/reject", response_model=HighlightClipSchema)
async def reject_highlight(job_id: int, highlight_id: int, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    try:
        highlight = await service.update_highlight_status(highlight_id, HighlightStatus.rejected)
        return HighlightClipSchema.model_validate(highlight)
    except ValueError:
        raise HTTPException(status_code=404, detail="Highlight not found")


@router.post("/{job_id}/reprocess", response_model=JobResponse)
async def reprocess_job(job_id: int, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    job = await service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    job = await service.update_stage(job_id, JobStage.pending)
    background_tasks.add_task(run_job_pipeline, job_id)
    return job


@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_job(job_id: int, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    try:
        job = await service.retry_job(job_id)
    except ValueError as exc:
        detail = str(exc)
        if "not found" in detail:
            raise HTTPException(status_code=404, detail="Job not found")
        raise HTTPException(status_code=400, detail=detail)
    background_tasks.add_task(run_job_pipeline, job_id)
    return job


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: int, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    try:
        await service.delete_job(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found")


@router.post("/{job_id}/highlights/{highlight_id}/render", response_model=HighlightClipSchema)
async def render_highlight(
    job_id: int,
    highlight_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    job = await service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    highlight = await service.get_highlight(highlight_id)
    if highlight is None or highlight.job_id != job_id:
        raise HTTPException(status_code=404, detail="Highlight not found")
    if highlight.status != HighlightStatus.approved.value:
        raise HTTPException(status_code=400, detail="Highlight must be approved to render")
    background_tasks.add_task(run_render_highlight, job_id, highlight_id)
    return HighlightClipSchema.model_validate(highlight)


@router.post("/{job_id}/render-all", response_model=list[HighlightClipSchema])
async def render_all_highlights(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    job = await service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    highlights = await service.get_approved_highlights(job_id)
    for h in highlights:
        background_tasks.add_task(run_render_highlight, job_id, h.id)
    return [HighlightClipSchema.model_validate(h) for h in highlights]

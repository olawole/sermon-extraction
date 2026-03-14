from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, HttpUrl, ConfigDict


class CreateJobRequest(BaseModel):
    youtube_url: HttpUrl


class UpdateSermonRequest(BaseModel):
    start_seconds: float
    end_seconds: float


class UpdateHighlightRequest(BaseModel):
    start_seconds: float
    end_seconds: float


class MediaAssetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    job_id: int
    asset_type: str
    file_path: str
    file_name: str
    format: Optional[str] = None
    size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None


class TranscriptChunkSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    chunk_index: int
    start_seconds: float
    end_seconds: float
    text: str
    speaker_id: Optional[str] = None
    confidence: Optional[float] = None


class SectionSegmentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    label: str
    start_seconds: float
    end_seconds: float
    confidence: Optional[float] = None
    dominant_speaker: Optional[str] = None


class ServiceSegmentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    service_number: int
    start_seconds: float
    end_seconds: float
    confidence: Optional[float] = None


class SermonSegmentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    service_number: int
    start_seconds: float
    end_seconds: float
    dominant_speaker: Optional[str] = None
    confidence: Optional[float] = None
    approved: bool = False


class HighlightClipSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    start_seconds: float
    end_seconds: float
    score: float
    category: str
    title: str
    hook_text: str
    transcript: str
    reasons: Optional[List[Any]] = None
    status: str


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    youtube_url: str
    title: Optional[str] = None
    duration_seconds: Optional[float] = None
    progress: Optional[float] = None
    stage: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class JobDetailResponse(JobResponse):
    assets: List[MediaAssetSchema] = []
    transcript_chunks: List[TranscriptChunkSchema] = []
    section_segments: List[SectionSegmentSchema] = []
    service_segments: List[ServiceSegmentSchema] = []
    sermon_segment: Optional[SermonSegmentSchema] = None
    highlights: List[HighlightClipSchema] = []


class TranscriptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    job_id: int
    chunks: List[TranscriptChunkSchema]


class SegmentsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    job_id: int
    section_segments: List[SectionSegmentSchema]
    service_segments: List[ServiceSegmentSchema]
    sermon_segment: Optional[SermonSegmentSchema] = None


class HighlightsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    job_id: int
    highlights: List[HighlightClipSchema]


class AssetListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    job_id: int
    assets: List[MediaAssetSchema]

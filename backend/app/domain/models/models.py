from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Integer, String, Float, Boolean, ForeignKey, DateTime, Text, JSON
)
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.infrastructure.db.base import Base
from app.domain.enums.enums import JobStage, AssetType, SectionLabel, HighlightStatus


def _now() -> datetime:
    return datetime.now(timezone.utc)


class VideoJob(Base):
    __tablename__ = "video_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    youtube_url: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    stage: Mapped[str] = mapped_column(String, default=JobStage.pending.value, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    assets: Mapped[List["MediaAsset"]] = relationship("MediaAsset", back_populates="job", cascade="all, delete-orphan")
    transcript_chunks: Mapped[List["TranscriptChunk"]] = relationship("TranscriptChunk", back_populates="job", cascade="all, delete-orphan")
    section_segments: Mapped[List["SectionSegment"]] = relationship("SectionSegment", back_populates="job", cascade="all, delete-orphan")
    service_segments: Mapped[List["ServiceSegment"]] = relationship("ServiceSegment", back_populates="job", cascade="all, delete-orphan")
    sermon_segments: Mapped[List["SermonSegment"]] = relationship("SermonSegment", back_populates="job", cascade="all, delete-orphan")
    highlights: Mapped[List["HighlightClip"]] = relationship("HighlightClip", back_populates="job", cascade="all, delete-orphan")


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("video_jobs.id"), nullable=False)
    asset_type: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    format: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    job: Mapped["VideoJob"] = relationship("VideoJob", back_populates="assets")
    highlight_clips: Mapped[List["HighlightClip"]] = relationship("HighlightClip", back_populates="rendered_asset", foreign_keys="HighlightClip.rendered_asset_id")


class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("video_jobs.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    end_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    speaker_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    job: Mapped["VideoJob"] = relationship("VideoJob", back_populates="transcript_chunks")


class SectionSegment(Base):
    __tablename__ = "section_segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("video_jobs.id"), nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    start_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    end_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dominant_speaker: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    job: Mapped["VideoJob"] = relationship("VideoJob", back_populates="section_segments")


class ServiceSegment(Base):
    __tablename__ = "service_segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("video_jobs.id"), nullable=False)
    service_number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    end_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    job: Mapped["VideoJob"] = relationship("VideoJob", back_populates="service_segments")


class SermonSegment(Base):
    __tablename__ = "sermon_segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("video_jobs.id"), nullable=False)
    service_number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    end_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    dominant_speaker: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    job: Mapped["VideoJob"] = relationship("VideoJob", back_populates="sermon_segments")


class HighlightClip(Base):
    __tablename__ = "highlight_clips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("video_jobs.id"), nullable=False)
    start_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    end_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    hook_text: Mapped[str] = mapped_column(Text, nullable=False)
    transcript: Mapped[str] = mapped_column(Text, nullable=False)
    reasons: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String, default=HighlightStatus.pending.value)
    rendered_asset_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("media_assets.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    job: Mapped["VideoJob"] = relationship("VideoJob", back_populates="highlights")
    rendered_asset: Mapped[Optional["MediaAsset"]] = relationship("MediaAsset", back_populates="highlight_clips", foreign_keys=[rendered_asset_id])

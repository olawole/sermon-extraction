from __future__ import annotations
import logging
import traceback
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.domain.enums.enums import JobStage, AssetType, HighlightStatus
from app.domain.models.models import (
    TranscriptChunk, SectionSegment, ServiceSegment, SermonSegment,
    HighlightClip, MediaAsset
)
from app.domain.services.job_service import JobService
from app.domain.services.transcript_windowing import create_windows
from app.domain.services.segment_smoothing import smooth_and_merge
from app.domain.services.service_boundary_detection import ServiceBoundaryDetectionService
from app.domain.services.sermon_detection import SermonDetectionService
from app.domain.services.highlight_generation import HighlightCandidateGenerator
from app.infrastructure.ai.provider_factory import get_transcription_provider, get_classification_provider
from app.infrastructure.ai.scoring.highlight_scorer import RuleBasedHighlightScorer
from app.infrastructure.youtube.ingestion import VideoIngestionService
from app.infrastructure.media.audio_extraction import AudioExtractionService
from app.infrastructure.media.video_cut import VideoCutService
from app.infrastructure.media.subtitle_generator import SubtitleGenerator
from app.infrastructure.storage.local_storage import LocalStorageService
from app.infrastructure.ai.classification.base import ClassificationWindow as CW

logger = logging.getLogger(__name__)

DEFAULT_VIDEO_DURATION_SECONDS = 3600.0


class JobOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_service = JobService(db)
        self.storage = LocalStorageService()
        self.ingestion = VideoIngestionService()
        self.audio_extractor = AudioExtractionService()
        self.transcription_provider = get_transcription_provider(settings.transcription_provider)
        self.classifier = get_classification_provider(settings.classification_provider)
        self.service_detector = ServiceBoundaryDetectionService()
        self.sermon_detector = SermonDetectionService()
        self.highlight_generator = HighlightCandidateGenerator()
        self.scorer = RuleBasedHighlightScorer()
        self.video_cutter = VideoCutService()
        self.subtitle_generator = SubtitleGenerator()

    async def is_download_done(self, job_id: int, video_path: str) -> bool:
        job = await self.job_service.get_job(job_id)
        return job is not None and Path(video_path).exists() and (job.duration_seconds or 0) > 0

    async def is_audio_extracted_done(self, audio_path: str) -> bool:
        return Path(audio_path).exists() and Path(audio_path).stat().st_size > 0

    async def is_transcription_done(self, job_id: int) -> bool:
        chunks = await self.job_service.get_transcript(job_id)
        return len(chunks) > 0

    async def is_classification_done(self, job_id: int) -> bool:
        sections, _, _ = await self.job_service.get_segments(job_id)
        return len(sections) > 0

    async def is_service_detection_done(self, job_id: int) -> bool:
        _, services, _ = await self.job_service.get_segments(job_id)
        return len(services) > 0

    async def is_sermon_detection_done(self, job_id: int) -> bool:
        _, _, sermon = await self.job_service.get_segments(job_id)
        return sermon is not None

    async def is_sermon_export_done(self, job_dir: str) -> bool:
        return Path(job_dir, "sermon.mp4").exists()

    async def is_highlights_generation_done(self, job_id: int) -> bool:
        highlights = await self.job_service.get_highlights(job_id)
        return len(highlights) > 0

    async def run_pipeline(self, job_id: int) -> None:
        try:
            await self._run(job_id)
        except Exception as exc:
            tb = traceback.format_exc()
            logger.exception(f"Pipeline failed for job {job_id}: {exc}")
            await self.job_service.update_stage(job_id, JobStage.failed, error=f"{exc}\n\n{tb}")

    async def _run(self, job_id: int) -> None:
        job = await self.job_service.get_job(job_id)
        if job is None:
            raise ValueError(f"Job {job_id} not found")

        job_dir = self.storage.job_dir(job_id)
        video_path = str(Path(job_dir) / "video.mp4")
        audio_path = str(Path(job_dir) / "audio.mp3")

        # Stage 1: Download
        if not await self.is_download_done(job_id, video_path):
            await self.job_service.update_stage(job_id, JobStage.downloading, progress=0.1)
            dl_result = await self.ingestion.download(str(job.youtube_url), job_dir)
            original_video_path = dl_result["file_path"]
            if Path(original_video_path).exists() and original_video_path != video_path:
                Path(original_video_path).rename(video_path)
            
            job.title = dl_result.get("title", "")
            raw_duration = dl_result.get("duration")
            job.duration_seconds = float(raw_duration) if raw_duration is not None else DEFAULT_VIDEO_DURATION_SECONDS
            await self.db.commit()
        else:
            logger.info(f"Skipping download for job {job_id}, video.mp4 already exists")

        # Stage 2: Extract Audio
        if not await self.is_audio_extracted_done(audio_path):
            await self.job_service.update_stage(job_id, JobStage.audio_extracted, progress=0.2)
            if Path(video_path).exists():
                try:
                    await self.audio_extractor.extract_audio(video_path, audio_path)
                except Exception as exc:
                    logger.error(f"Audio extraction failed for job {job_id}: {exc}")
        else:
            logger.info(f"Skipping audio extraction for job {job_id}, audio.mp3 already exists")

        if not Path(audio_path).exists():
            raise RuntimeError(
                f"Audio file not found at {audio_path}; download or extraction may have failed"
            )
        if Path(audio_path).stat().st_size == 0:
            raise RuntimeError(
                f"Audio file at {audio_path} is empty (0 bytes); audio extraction may have failed"
            )

        # Stage 3 & 4: Transcribe & Persist
        transcript_data = None
        if not await self.is_transcription_done(job_id):
            await self.job_service.update_stage(job_id, JobStage.transcribing, progress=0.3)
            transcript_data = await self.transcription_provider.transcribe(
                audio_path, duration_seconds=job.duration_seconds or DEFAULT_VIDEO_DURATION_SECONDS
            )

            await self.job_service.update_stage(job_id, JobStage.transcribed, progress=0.4)
            for chunk_data in transcript_data:
                chunk = TranscriptChunk(
                    job_id=job_id,
                    chunk_index=chunk_data.chunk_index,
                    start_seconds=chunk_data.start_seconds,
                    end_seconds=chunk_data.end_seconds,
                    text=chunk_data.text,
                    speaker_id=chunk_data.speaker_id,
                    confidence=chunk_data.confidence,
                )
                self.db.add(chunk)
            await self.db.commit()
        else:
            logger.info(f"Skipping transcription for job {job_id}, chunks already exist")
            transcript_data = await self.job_service.get_transcript(job_id)

        # Stage 5 & 6: Classify & Persist
        smoothed = None
        if not await self.is_classification_done(job_id):
            await self.job_service.update_stage(job_id, JobStage.classifying, progress=0.5)
            windows = create_windows(transcript_data)
            classification_windows = []
            for w in windows:
                classification_windows.append(CW(
                    start_seconds=w.start_seconds,
                    end_seconds=w.end_seconds,
                    text=w.text,
                    chunk_indices=w.chunk_indices,
                ))
            raw_results = await self.classifier.classify(classification_windows)

            await self.job_service.update_stage(job_id, JobStage.classified, progress=0.6)
            smoothed = smooth_and_merge(raw_results, min_duration_seconds=30.0)
            for seg in smoothed:
                section = SectionSegment(
                    job_id=job_id,
                    label=seg.label,
                    start_seconds=seg.start_seconds,
                    end_seconds=seg.end_seconds,
                    confidence=seg.confidence,
                )
                self.db.add(section)
            await self.db.commit()
        else:
            logger.info(f"Skipping classification for job {job_id}, sections already exist")
            smoothed, _, _ = await self.job_service.get_segments(job_id)

        # Stage 7 & 8: Detect services & Persist
        service_boundaries = None
        if not await self.is_service_detection_done(job_id):
            await self.job_service.update_stage(job_id, JobStage.detecting_services, progress=0.7)
            total_duration = job.duration_seconds or DEFAULT_VIDEO_DURATION_SECONDS
            service_boundaries = self.service_detector.detect(smoothed, total_duration)

            await self.job_service.update_stage(job_id, JobStage.services_detected, progress=0.75)
            for boundary in service_boundaries:
                svc = ServiceSegment(
                    job_id=job_id,
                    service_number=boundary.service_number,
                    start_seconds=boundary.start_seconds,
                    end_seconds=boundary.end_seconds,
                    confidence=boundary.confidence,
                )
                self.db.add(svc)
            await self.db.commit()
        else:
            logger.info(f"Skipping service detection for job {job_id}, services already exist")
            _, service_boundaries, _ = await self.job_service.get_segments(job_id)

        # Stage 9 & 10: Detect sermon & Persist
        sermon_result = None
        if not await self.is_sermon_detection_done(job_id):
            await self.job_service.update_stage(job_id, JobStage.detecting_sermon, progress=0.8)
            sermon_result = self.sermon_detector.detect(smoothed, service_boundaries)

            await self.job_service.update_stage(job_id, JobStage.sermon_detected, progress=0.85)
            if sermon_result:
                sermon = SermonSegment(
                    job_id=job_id,
                    service_number=sermon_result.service_number,
                    start_seconds=sermon_result.start_seconds,
                    end_seconds=sermon_result.end_seconds,
                    dominant_speaker=sermon_result.dominant_speaker,
                    confidence=sermon_result.confidence,
                )
                self.db.add(sermon)
                await self.db.commit()
                await self.db.refresh(sermon)
                sermon_result = sermon  # Use the model as sermon_result for subsequent stages
        else:
            logger.info(f"Skipping sermon detection for job {job_id}, sermon already exists")
            _, _, sermon_result = await self.job_service.get_segments(job_id)

        # Stage 11 & 12: Export sermon & Persist assets
        if not await self.is_sermon_export_done(job_dir):
            await self.job_service.update_stage(job_id, JobStage.exporting_sermon, progress=0.9)
            if sermon_result and Path(video_path).exists():
                sermon_video_path = str(Path(job_dir) / "sermon.mp4")
                srt_path = str(Path(job_dir) / "sermon.srt")
                vtt_path = str(Path(job_dir) / "sermon.vtt")
                try:
                    await self.video_cutter.cut_segment(video_path, sermon_result.start_seconds, sermon_result.end_seconds, sermon_video_path)
                    self.subtitle_generator.generate_srt(
                        transcript_data, 
                        sermon_result.start_seconds, 
                        srt_path,
                        sermon_end=sermon_result.end_seconds
                    )
                    self.subtitle_generator.generate_vtt(
                        transcript_data, 
                        sermon_result.start_seconds, 
                        vtt_path,
                        sermon_end=sermon_result.end_seconds
                    )
                    
                    # Persist sermon assets
                    self.db.add(MediaAsset(job_id=job_id, asset_type=AssetType.sermon_video.value, file_path=sermon_video_path, file_name="sermon.mp4", format="mp4"))
                    self.db.add(MediaAsset(job_id=job_id, asset_type=AssetType.subtitle_srt.value, file_path=srt_path, file_name="sermon.srt", format="srt"))
                    self.db.add(MediaAsset(job_id=job_id, asset_type=AssetType.subtitle_vtt.value, file_path=vtt_path, file_name="sermon.vtt", format="vtt"))
                    await self.db.commit()
                except Exception as e:
                    logger.warning(f"Export partially failed: {e}")
            await self.job_service.update_stage(job_id, JobStage.sermon_exported, progress=0.95)
        else:
            logger.info(f"Skipping sermon export for job {job_id}, sermon.mp4 already exists")

        # Stage 13 & 14: Generate highlights & Persist
        if not await self.is_highlights_generation_done(job_id):
            await self.job_service.update_stage(job_id, JobStage.generating_highlights, progress=0.98)
            if sermon_result:
                candidates = self.highlight_generator.generate_candidates(
                    transcript_data, sermon_result.start_seconds, sermon_result.end_seconds
                )
                scored_candidates = [(c, self.scorer.score(c)) for c in candidates]
                scored_candidates.sort(key=lambda x: x[1], reverse=True)
                top_candidates = scored_candidates[:10]

                await self.job_service.update_stage(job_id, JobStage.highlights_generated, progress=0.99)
                for candidate, score in top_candidates:
                    candidate.score = score
                    hl = HighlightClip(
                        job_id=job_id,
                        start_seconds=candidate.start_seconds,
                        end_seconds=candidate.end_seconds,
                        score=score,
                        category=candidate.category,
                        title=candidate.title,
                        hook_text=candidate.hook_text,
                        transcript=candidate.transcript,
                        reasons=candidate.reasons,
                        status=HighlightStatus.pending.value,
                    )
                    self.db.add(hl)
                await self.db.commit()
        else:
            logger.info(f"Skipping highlights generation for job {job_id}, highlights already exist")

        await self.job_service.update_stage(job_id, JobStage.completed, progress=1.0)

    async def render_highlight(self, job_id: int, highlight_id: int) -> None:
        try:
            await self._render_highlight(job_id, highlight_id)
        except Exception as exc:
            logger.exception(f"Render failed for highlight {highlight_id}: {exc}")

    async def _render_highlight(self, job_id: int, highlight_id: int) -> None:
        highlight = await self.job_service.get_highlight(highlight_id)
        if highlight is None:
            raise ValueError(f"Highlight {highlight_id} not found")

        job_dir = self.storage.job_dir(job_id)
        source_path = str(Path(job_dir) / "video.mp4")
        sermon_path = str(Path(job_dir) / "sermon.mp4")
        srt_path = str(Path(job_dir) / "sermon.srt")

        video_source = sermon_path if Path(sermon_path).exists() else source_path
        subtitle_source = srt_path if Path(srt_path).exists() else None

        output_filename = f"highlight_{highlight_id}_vertical.mp4"
        output_path = str(Path(job_dir) / output_filename)

        if not Path(video_source).exists():
            logger.warning(f"Source video not found for job {job_id}; skipping render")
            return

        await self.video_cutter.render_vertical(
            source_path=video_source,
            start=highlight.start_seconds,
            end=highlight.end_seconds,
            output_path=output_path,
            burn_subtitles_path=subtitle_source,
        )

        asset = MediaAsset(
            job_id=job_id,
            asset_type=AssetType.highlight_clip.value,
            file_path=output_path,
            file_name=output_filename,
            format="mp4",
            duration_seconds=highlight.end_seconds - highlight.start_seconds,
        )
        await self.job_service.attach_rendered_asset(highlight_id, asset)

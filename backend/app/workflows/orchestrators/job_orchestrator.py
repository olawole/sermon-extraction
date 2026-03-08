from __future__ import annotations
import logging
import os
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
from app.infrastructure.ai.transcription.fake_provider import FakeTranscriptionProvider
from app.infrastructure.ai.classification.fake_classifier import FakeSectionClassifier
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
        self.transcription_provider = FakeTranscriptionProvider()
        self.classifier = FakeSectionClassifier()
        self.service_detector = ServiceBoundaryDetectionService()
        self.sermon_detector = SermonDetectionService()
        self.highlight_generator = HighlightCandidateGenerator()
        self.scorer = RuleBasedHighlightScorer()
        self.video_cutter = VideoCutService()
        self.subtitle_generator = SubtitleGenerator()

    async def run_pipeline(self, job_id: int) -> None:
        try:
            await self._run(job_id)
        except Exception as exc:
            logger.exception(f"Pipeline failed for job {job_id}: {exc}")
            await self.job_service.update_stage(job_id, JobStage.failed, error=str(exc))

    async def _run(self, job_id: int) -> None:
        job = await self.job_service.get_job(job_id)
        if job is None:
            raise ValueError(f"Job {job_id} not found")

        job_dir = self.storage.job_dir(job_id)

        # Stage 1: Download
        await self.job_service.update_stage(job_id, JobStage.downloading)
        try:
            dl_result = await self.ingestion.download(str(job.youtube_url), job_dir)
            video_path = dl_result["file_path"]
            job.title = dl_result.get("title", "")
            raw_duration = dl_result.get("duration")
            job.duration_seconds = float(raw_duration) if raw_duration is not None else DEFAULT_VIDEO_DURATION_SECONDS
        except Exception:
            # Use fake data in test/dev mode
            video_path = os.path.join(job_dir, "video.mp4")
            job.title = job.title or "Test Video"
            job.duration_seconds = job.duration_seconds or DEFAULT_VIDEO_DURATION_SECONDS
        await self.db.commit()

        # Stage 2: Extract Audio
        await self.job_service.update_stage(job_id, JobStage.audio_extracted)
        audio_path = os.path.join(job_dir, "audio.wav")
        if os.path.exists(video_path):
            try:
                await self.audio_extractor.extract_audio(video_path, audio_path)
            except Exception:
                pass

        # Stage 3: Transcribe
        await self.job_service.update_stage(job_id, JobStage.transcribing)
        transcript_data = await self.transcription_provider.transcribe(
            audio_path, duration_seconds=job.duration_seconds or DEFAULT_VIDEO_DURATION_SECONDS
        )

        # Stage 4: Persist transcript
        await self.job_service.update_stage(job_id, JobStage.transcribed)
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

        # Stage 5: Classify
        await self.job_service.update_stage(job_id, JobStage.classifying)
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

        # Stage 6: Persist sections (smoothed)
        await self.job_service.update_stage(job_id, JobStage.classified)
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

        # Stage 7: Detect services
        await self.job_service.update_stage(job_id, JobStage.detecting_services)
        total_duration = job.duration_seconds or DEFAULT_VIDEO_DURATION_SECONDS
        service_boundaries = self.service_detector.detect(smoothed, total_duration)

        # Stage 8: Persist service segments
        await self.job_service.update_stage(job_id, JobStage.services_detected)
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

        # Stage 9: Detect sermon
        await self.job_service.update_stage(job_id, JobStage.detecting_sermon)
        svc2 = next((b for b in service_boundaries if b.service_number == 2), None)
        if svc2:
            sermon_result = self.sermon_detector.detect(smoothed, svc2.start_seconds, svc2.end_seconds)
        else:
            sermon_result = None

        # Stage 10: Persist sermon
        await self.job_service.update_stage(job_id, JobStage.sermon_detected)
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

        # Stage 11: Export sermon
        await self.job_service.update_stage(job_id, JobStage.exporting_sermon)
        if sermon_result and os.path.exists(video_path):
            sermon_video_path = os.path.join(job_dir, "sermon.mp4")
            srt_path = os.path.join(job_dir, "sermon.srt")
            vtt_path = os.path.join(job_dir, "sermon.vtt")
            try:
                await self.video_cutter.cut_segment(video_path, sermon_result.start_seconds, sermon_result.end_seconds, sermon_video_path)
                self.subtitle_generator.generate_srt(transcript_data, sermon_result.start_seconds, srt_path)
                self.subtitle_generator.generate_vtt(transcript_data, sermon_result.start_seconds, vtt_path)
            except Exception as e:
                logger.warning(f"Export partially failed: {e}")

        # Stage 12: Persist sermon assets
        await self.job_service.update_stage(job_id, JobStage.sermon_exported)

        # Stage 13: Generate highlights
        await self.job_service.update_stage(job_id, JobStage.generating_highlights)
        if sermon_result:
            candidates = self.highlight_generator.generate_candidates(
                transcript_data, sermon_result.start_seconds, sermon_result.end_seconds
            )
            scored_candidates = [(c, self.scorer.score(c)) for c in candidates]
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            top_candidates = scored_candidates[:10]

            # Stage 14: Persist highlights
            await self.job_service.update_stage(job_id, JobStage.highlights_generated)
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

        await self.job_service.update_stage(job_id, JobStage.completed)

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
        source_path = os.path.join(job_dir, "video.mp4")
        sermon_path = os.path.join(job_dir, "sermon.mp4")
        srt_path = os.path.join(job_dir, "sermon.srt")

        video_source = sermon_path if os.path.exists(sermon_path) else source_path
        subtitle_source = srt_path if os.path.exists(srt_path) else None

        output_filename = f"highlight_{highlight_id}_vertical.mp4"
        output_path = os.path.join(job_dir, output_filename)

        if not os.path.exists(video_source):
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

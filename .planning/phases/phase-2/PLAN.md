# Phase 2 Plan: Robust Execution

## Objective
Improve reliability and observability through job resumability and per-job logging.

## Tasks

### 1. Implement Stage-Based Checkpointing in `JobOrchestrator`
- **Goal**: Allow `JobOrchestrator._run` to resume from the last successful stage.
- **Approach**:
    - At the start of each stage, check if the work is already complete.
    - If `JobStage` is `downloading`, but `video.mp4` exists and `job.duration_seconds` is set, skip download.
    - If `JobStage` is `audio_extracted`, but `audio.wav` exists, skip extraction.
    - If `JobStage` is `transcribing`, but `transcript_chunks` exist in DB, skip transcription.
    - Repeat for all stages until `completed`.
- **Checkpoint logic**:
    - `is_download_done()`: Check for video file + duration in DB.
    - `is_audio_extracted_done()`: Check for audio file.
    - `is_transcription_done()`: Check for `TranscriptChunk` records.
    - `is_classification_done()`: Check for `SectionSegment` records.
    - `is_service_detection_done()`: Check for `ServiceSegment` records.
    - `is_sermon_detection_done()`: Check for `SermonSegment` records.
    - `is_sermon_export_done()`: Check for `sermon.mp4`.
    - `is_highlights_generation_done()`: Check for `HighlightClip` records.

### 2. Redirect Subprocess Output to Per-Job Log Files
- **Goal**: Write `stdout` and `stderr` from `yt-dlp` and `ffmpeg` to `storage/job_X/process.log`.
- **Approach**:
    - Update `run_subprocess` to support writing output to a file asynchronously.
    - Update `VideoIngestionService`, `AudioExtractionService`, and `VideoCutService` to pass the job's log path to `run_subprocess`.
    - Ensure the log file is created in the `job_dir`.

### 3. Improve Frontend Error Reporting in `JobStatusCard`
- **Goal**: Show detailed error messages and tracebacks in the frontend.
- **Approach**:
    - Backend: Use `traceback.format_exc()` in `JobOrchestrator.run_pipeline` to capture the full traceback.
    - Frontend:
        - Update `JobStatusCard` to use AntD `Collapse` for displaying long error messages or tracebacks.
        - Add a "Retry" button (optional but recommended) to re-trigger a failed job.

## Verification Strategy

### Automated Tests
- Create a unit test for `JobOrchestrator` to verify resumability:
    1. Mock stages to fail halfway.
    2. Run orchestrator, observe failure.
    3. Run orchestrator again, verify it skips the first successful stages.
- Verify `run_subprocess` correctly writes to a file.

### Manual Verification
- Manually fail a job (e.g., by disconnecting internet during download or killing the process).
- Restart the job and verify it continues from the correct stage.
- Check `storage/job_X/process.log` to see if logs are correctly populated.

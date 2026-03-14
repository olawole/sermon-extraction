# Quick Task: Fix Audio Size and Asyncio Error [COMPLETED]

## Description
1. Audio extraction is currently using uncompressed WAV (PCM), resulting in files that are nearly half the size of the video. This causes OOM and performance issues during transcription.
2. The large files lead to `asyncio` loop errors and `AssertionError` in `uvicorn` during heavy I/O or manual interrupts.

## Plan
1. **Optimize Audio Extraction**:
   - Change `AudioExtractionService` to use MP3 compression (`-acodec libmp3lame -b:a 64k`).
   - 64k is sufficient for speech transcription and significantly smaller.
2. **Update Orchestrator**:
   - Change `audio_path` extension from `.wav` to `.mp3`.
3. **Robust Transcription**:
   - Ensure `WhisperTranscriptionProvider` handles the new format (it already uses `io.BytesIO` but Whisper API supports many formats).

## Execution
- [x] Modify `backend/app/infrastructure/media/audio_extraction.py` to use libmp3lame.
- [x] Modify `backend/app/workflows/orchestrators/job_orchestrator.py` to use `audio.mp3`.
- [x] Update `backend/app/tests/unit/test_orchestrator_resumability.py` to reflect the name change if necessary.
- [x] Update `backend/app/tests/integration/test_full_pipeline.py` for consistency.

## Verification
- [x] Run unit tests to ensure the changes don't break resumability or ingestion logic.
  - Command: `backend\.venv\Scripts\python.exe -m pytest backend\app\tests\unit\test_orchestrator_resumability.py backend\app\tests\unit\test_video_ingestion.py`
  - Status: **Passed**

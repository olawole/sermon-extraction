# Quick Task: Fix Whisper Payload Too Large (413)

## Description
OpenAI's Whisper API has a 25MB limit. At 64kbps MP3, files exceed this limit for recordings longer than ~52 minutes. The user hit this limit with a file just over 25MB.

## Plan
1. **Reduce Audio Bitrate**:
   - Update `AudioExtractionService` in `backend/app/infrastructure/media/audio_extraction.py` to use `-b:a 32k` instead of `64k`.
   - 32kbps is still high quality for speech and doubles the maximum duration we can send (up to ~104 minutes).
2. **Add Size Validation (Optional but Recommended)**:
   - Add a pre-flight check in `WhisperTranscriptionProvider` to log a clearer error if the file still exceeds 25MB after compression.

## Execution
- Modified `backend/app/infrastructure/media/audio_extraction.py` to use `-b:a 32k`.
- Added file size validation in `backend/app/infrastructure/ai/transcription/whisper_provider.py`.
- Added unit test `test_whisper_transcribe_file_too_large` in `backend/app/tests/unit/test_whisper_provider.py`.
- Verified with unit tests: `backend\.venv\Scripts\python.exe -m pytest backend\app\tests\unit\test_whisper_provider.py` (5 passed).

## Status: Completed
- Date: 2025-05-22
- Changes applied and verified.

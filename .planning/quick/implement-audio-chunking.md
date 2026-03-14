# Quick Task: Implement Audio Chunking for Whisper

## Description
Current 32kbps bitrate only supports ~104 minutes before hitting OpenAI's 25MB limit. To support 4-hour (and longer) recordings, the system must split audio into chunks, transcribe each, and merge the results.

## Plan
1. **Update `WhisperTranscriptionProvider`**:
   - Detect if the audio file exceeds 24MB (leaving a safety margin).
   - If it does, use `ffmpeg` (via `subprocess_helper`) to split the audio into 20-minute segments.
   - Iterate through segments, transcribing each.
   - Adjust timestamps for each chunk (adding `chunk_index * chunk_duration`).
   - Merge all results into a single `TranscriptChunkData` list.
2. **Cleanup**: Ensure temporary audio segments are deleted after transcription.

## Execution
- [x] Modify `backend/app/infrastructure/ai/transcription/whisper_provider.py`.
- [x] Add a unit test to verify the merging logic with offsets.

## Status
- **COMPLETED**: Audio chunking implemented for recordings exceeding 24MB.
- **LOGIC**: Split into 20-minute segments using `ffmpeg`, transcribe with `AsyncOpenAI`, and merge with `chunk_index * 1200` offset.
- **VERIFIED**: Unit tests pass with correct timestamp merging and global re-indexing.

# Phase 3 Plan: AI Integration & Refinement

## Objective
Transition the pipeline from mock "fake" providers to high-accuracy AI services (OpenAI Whisper and GPT-4o-mini) and verify performance with real-world church service recordings.

## Tasks

### 1. Provider Verification & Unit Testing
- [ ] Create unit tests for `WhisperTranscriptionProvider` using short audio samples.
- [ ] Create unit tests for `OpenAISectionClassifier` with real transcript windows.
- [ ] Implement a simple CLI script to verify API connectivity and response formats.

### 2. Prompt Engineering & Refinement
- [x] Analyze `OpenAISectionClassifier` output on sample data.
- [x] Refine the system prompt in `backend/app/infrastructure/ai/classification/openai_classifier.py` to better distinguish between "Announcements", "Prayer", and "Sermon".
- [x] Add few-shot examples to the prompt if needed for consistency.

### 3. Subtitle Alignment & Quality
- [ ] Verify that Whisper's `verbose_json` segments correctly align with audio when burned into video.
- [ ] Adjust `SubtitleGenerator` if necessary to handle fine-grained timestamps from real transcription.

### 4. Integration & Benchmarking
- [ ] Run the full pipeline with `ai_provider=openai` on a known 60-90 minute service recording.
- [ ] Compare detected sermon boundaries with manual ground truth.
- [ ] Measure total processing time and API cost for a standard job.

## Verification Criteria
- [ ] `WhisperTranscriptionProvider` successfully transcribes a 5-minute audio clip with >95% word accuracy.
- [ ] `OpenAISectionClassifier` correctly identifies the "Sermon" block in a test recording.
- [ ] Full pipeline completes without errors using real API keys.
- [ ] Rendered highlight clips have perfectly synchronized subtitles.

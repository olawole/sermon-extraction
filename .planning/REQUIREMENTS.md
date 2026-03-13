# Requirements: Sermon Extraction Stabilization & Accuracy

## Phase 1: Stabilization (Immediate Priority)
- [ ] **Fix Service Boundary Detection:** Must correctly handle videos with a single service.
- [ ] **Fix Sermon Detection:** Must identify the sermon segment regardless of which service it's in (e.g., in a single-service video).
- [ ] **End-to-End Pipeline Validation:** Ensure a job can transition from `pending` to `completed` using the "fake" provider without manual intervention or crashing.
- [ ] **Subprocess Resiliency:** Implement timeouts and better logging for `yt-dlp` and `ffmpeg` calls.

## Phase 2: Robust Pipeline & Errors
- [ ] **Basic Resumability:** If a job fails at Stage 8, retrying should skip Stages 1-7.
- [ ] **Enhanced Logging:** Log all subprocess output to a per-job log file in the storage directory.
- [ ] **Error Reporting:** Capture and display more descriptive error messages in the frontend `JobStatusCard`.

## Phase 3: AI Accuracy & Providers
- [ ] **Real Transcription Integration:** Fully verify `WhisperProvider` works with real API keys.
- [ ] **Classification Prompt Refinement:** Update `OpenAISectionClassifier` prompts to improve sermon boundary detection.
- [ ] **Subtitle Accuracy:** Ensure generated SRT/VTT files align precisely with the extracted sermon clip.

## Phase 4: Advanced UI & Features
- [ ] **Timeline Navigation:** Enable users to click on the timeline to jump to specific segments in the transcript.
- [ ] **Manual Segment Overrides:** Allow users to manually adjust the start/end times of the detected sermon.
- [ ] **Vertical Video Optimization:** Refine the `render_vertical` logic (e.g., blurring sidebars, adding background overlays).
- [ ] **Multi-Provider Support:** Add options for other AI providers (e.g., Anthropic, Deepgram).

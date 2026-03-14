# Roadmap: Sermon Extraction

## Phase 1: Stabilization (2-4 Weeks)
**Goal:** Achieve a 100% success rate for the "fake" pipeline and handle diverse video lengths.
- [ ] Refactor `ServiceBoundaryDetectionService` and `SermonDetectionService` for accuracy.
- [ ] Add subprocess timeouts and error logging.
- [ ] End-to-end "fake" pipeline validation.

## Phase 2: Robust Execution (4-6 Weeks)
**Goal:** Improve reliability and observability.
- [ ] Basic job resumability in `JobOrchestrator`.
- [ ] Per-job logging to files.
- [ ] Improved frontend error reporting.

## Phase 3: AI Integration & Refinement (6-10 Weeks)
**Goal:** Transition to high-accuracy transcription and classification.
- [x] OpenAI Whisper/GPT-4o-mini integration and testing.
- [x] Classification prompt engineering for better sermon detection.
- [x] Subtitle alignment verification.

## Phase 4: Enhanced User Experience (10-14 Weeks)
**Goal:** Provide manual controls and advanced media features.
- [x] Timeline navigation and manual segment adjustment.
- [x] Improved vertical video rendering (blurred backgrounds).
- [x] Multi-provider support (Anthropic, Deepgram stubs).

## Phase 5: Advanced Distribution & Polish (14-18 Weeks)
**Goal:** Multi-user support, direct publishing, and visual styling.
- [ ] JWT authentication and user workspaces.
- [ ] Social media publishing (Instagram/TikTok).
- [ ] Stylized captions and B-roll suggestions.
- [ ] Storage cleanup and rate limiting.

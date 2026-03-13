# Project State: Sermon Extraction

## Current Summary
The codebase exists with a structured backend (FastAPI/SQLAlchemy) and a feature-complete frontend (React/AntD). However, the end-to-end "fake" pipeline is fragile, particularly in service and sermon detection, and the orchestrator is not resilient to failures.

## Major Issues Identified
- [ ] **Linear Pipeline Fragility:** `JobOrchestrator` fails completely on any stage error without resume capability.
- [ ] **Hardcoded Detection Logic:** `ServiceBoundaryDetectionService` arbitrarily splits videos into two services, and `SermonDetectionService` only looks in the "second" service.
- [ ] **Incomplete Subprocess Management:** `yt-dlp` and `ffmpeg` calls are basic and lack timeouts.
- [ ] **AI Provider Limitations:** Real-world transcription (Whisper) and classification (OpenAI) are implemented but not fully verified end-to-end.

## Recent Achievements
- [x] Initial codebase mapping complete.
- [x] Backend tests (unit/integration) are passing (mostly with mocks/fakes).
- [x] Frontend features for viewing transcript, segments, and highlights are implemented.

## Current Phase: Phase 1 (Stabilization)
**Objective:** Fix service/sermon detection and ensure a 100% success rate for the "fake" pipeline.
- [ ] Refactor `ServiceBoundaryDetectionService`.
- [ ] Refactor `SermonDetectionService`.
- [ ] Add basic subprocess timeouts.

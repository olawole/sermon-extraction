# Project State: Sermon Extraction

## Current Summary
Phase 2 (Robust Execution) is complete. The system now supports stage-based checkpointing for job resumability, per-job logging for observability, and enhanced frontend error reporting. The backend pipeline is highly resilient, and all unit and integration tests are passing.

## Recent Achievements
- [x] **Phase 4 Complete: Enhanced User Experience**: Delivered manual controls, improved video aesthetics, and multi-provider support.
- [x] **Manual Segment Adjustment**: Implemented `PUT` endpoints and frontend draggable handles for fine-tuning sermon and highlight boundaries.
- [x] **Advanced Vertical Rendering**: Upgraded `VideoCutService` to produce high-quality vertical clips with blurred backgrounds using complex FFmpeg filters.
- [x] **Multi-Provider Support**: Added architecture and stubs for Anthropic (Claude) and Deepgram providers, controlled via `.env`.
- [x] **UX Polish**: Added real-time pipeline progress tracking (0-100%) and a video preview modal for highlight candidates.

## Quick Tasks Completed
| Task | Description | Date |
|------|-------------|------|
| Fix Missing DB Column | Created and applied Alembic migration for `progress` column in `video_jobs`. | 2026-03-14 |
| Fix Download Performance | Added `ytdlp_format` constraints (max 1080p) and increased download timeout to 45m. | 2026-03-14 |
| Fix Download Performance V2 | Reverted to 720p cap and prioritized single-file MP4 for speed/size. | 2026-03-14 |
| Fix Audio Size & Asyncio | Switched to compressed MP3 (64k) for extraction and fixed uvicorn/asyncio hang. | 2026-03-14 |
| Fix Whisper 413 Payload | Reduced bitrate to 32kbps and added pre-flight size validation (max 25MB). | 2026-03-14 |
| Implement Audio Chunking | Added automatic 20-min segmenting for Whisper to support 4+ hour recordings. | 2026-03-14 |
| Implement Audio Chunking | Added ffmpeg-based 20-min segmentation for Whisper transcription to handle 4+ hour files. | 2026-03-15 |

## Current Phase: Phase 5 (Advanced Distribution & Polish)
**Objective:** Multi-user support, direct social publishing, and stylized overlays.
**Plan:** [.planning/phases/phase-5/PLAN.md](phases/phase-5/PLAN.md)
- [ ] Implement JWT-based authentication.
- [ ] Connect social media APIs (Instagram/TikTok).
- [ ] Stylize captions with custom FFmpeg filters.
- [ ] Auto-purge old assets.

## Future Goals (Post-Phase 5)
- [ ] Advanced AI features: B-roll insertion and style transfer.
- [ ] Mobile app for pastors to review/approve highlights.


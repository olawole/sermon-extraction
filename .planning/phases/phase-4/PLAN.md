# Phase 4 Plan: Enhanced User Experience

## Objective
Provide manual controls for segment adjustment, improve the visual quality of vertical clips, and expand AI provider options.

## Tasks

### 1. Manual Segment Adjustment (Frontend & Backend)
- [ ] **Backend API**: Add `PUT /jobs/{id}/sermon` and `PUT /highlights/{id}` endpoints to update start/end timestamps.
- [ ] **Frontend State**: Update `useJobs.ts` hook to include mutations for updating sermon and highlight boundaries.
- [ ] **Interactivity**: Refactor `TimelineView.tsx` to support draggable "handles" for the Sermon track and selected Highlight track.
- [ ] **Validation**: Ensure that updated boundaries trigger a re-render of associated assets if the user requests it.

### 2. Advanced Vertical Video Rendering
- [ ] **Blurred Background**: Update `VideoCutService.render_vertical` to use a multi-layer filter:
    - Layer 1: Scale to 1080:1920 (fill), crop to center, and apply `gblur`.
    - Layer 2: Original video scaled to 1080 width, centered on top.
- [ ] **Subtitle Styling**: Add basic styling options (font size, position) to the `SubtitleGenerator` and `VideoCutService`.

### 3. Multi-Provider Support
- [ ] **Anthropic Integration**: Implement `AnthropicSectionClassifier` using Claude 3.5 Sonnet.
- [ ] **Deepgram Integration**: Implement `DeepgramTranscriptionProvider` for faster/cheaper transcription options.
- [ ] **Configuration**: Update `provider_factory.py` and `Settings` to allow easy switching between providers via `.env`.

### 4. End-to-End UX Polish
- [ ] **Live Preview**: Add a simple video player to the `HighlightsList` to preview segments before rendering.
- [ ] **Progress Indicators**: Improve backend-to-frontend progress reporting (e.g., % completion for FFmpeg tasks).

## Verification Criteria
- [ ] User can drag a sermon boundary on the timeline and save the new timestamps to the database.
- [ ] Vertical video output features a blurred background instead of black bars.
- [ ] System successfully switches to Anthropic/Deepgram when configured in `.env`.
- [ ] UI correctly displays real-time progress for long-running render tasks.

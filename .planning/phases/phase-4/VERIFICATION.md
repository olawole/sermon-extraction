# Phase 4 Verification Plan: Enhanced User Experience

## 1. Manual Segment Adjustment Verification
- [ ] **API Check**: Use `curl` or a REST client to update a sermon segment's `start_seconds` and `end_seconds`. Verify the database reflects the changes.
- [ ] **UI Check**: Drag a handle on the `TimelineView` and ensure the updated timestamps are sent to the backend.
- [ ] **Sync Check**: Confirm that the `SermonSummaryCard` updates its displayed duration after a manual adjustment.

## 2. Advanced Media Rendering Verification
- [ ] **Visual Check**: Render a highlight clip and verify that the vertical output has a blurred background effect (no black bars).
- [ ] **Subtitle Check**: Ensure subtitles are still legible and correctly positioned on top of the blurred background.
- [ ] **Performance Check**: Measure if the blurred background rendering (which is more CPU intensive) stays within the 15-minute timeout window.

## 3. Multi-Provider Verification
- [ ] **Anthropic**: Configure `AI_PROVIDER=anthropic` in `.env` and run a classification job. Verify that the system uses the Claude model (via logs).
- [ ] **Deepgram**: Configure `TRANSCRIPTION_PROVIDER=deepgram` in `.env` and run a transcription job. Verify successful transcript generation.
- [ ] **Fallback**: Ensure the system handles missing API keys for secondary providers gracefully (e.g., informative error message).

## 4. UX Verification
- [ ] **Progress Bar**: Start a rendering job and verify that the UI shows a progress percentage that updates periodically.
- [ ] **Preview Player**: Click a highlight candidate and verify it opens in a video player at the correct start timestamp.

## 5. Automated Tests
- [ ] Create unit tests for the new `PUT /jobs/{id}/sermon` and `PUT /highlights/{id}` endpoints.
- [ ] Add integration tests for the `AnthropicSectionClassifier` (using mocks).
- [ ] Update `VideoCutService` tests to verify the generation of the complex filter string for blurred backgrounds.

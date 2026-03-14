# Phase 1: Stabilization Plan

## Objective
Achieve a 100% success rate for the "fake" pipeline and handle diverse video lengths (single vs. multi-service) with robust subprocess management.

## 1. Fix Service Boundary Detection
Move away from hardcoded two-service splitting.
- **Goal:** Correctly detect 1 or more services based on `transition` or `praise_worship` patterns.
- **Logic:** 
  - Scan for `transition` segments. (Note: Ensure `smooth_and_merge` threshold doesn't drop short transitions).
  - If no transitions, assume a single service spanning `0.0` to `total_duration` (remove midpoint splitting).
  - If transitions exist, use them as split points.
  - Ensure boundaries don't overlap.
- **Files:** `backend/app/domain/services/service_boundary_detection.py`

## 2. Fix Sermon Detection
Ensure the sermon can be found anywhere in the recording.
- **Goal:** Search all detected services for the best sermon candidate.
- **Logic:**
  - Iterate through all `ServiceBoundaryResult` objects.
  - Find `sermon` labels within each boundary.
  - Implement basic "dominant speaker" mock logic for the fake provider (e.g., if a segment is long enough and labeled sermon, it's likely the dominant speaker).
  - Merge adjacent sermon blocks if gap < 2 minutes.
  - Enforce min (15m) and max (60m) duration filters.
- **Files:** `backend/app/domain/services/sermon_detection.py`

## 3. Subprocess Resiliency
Prevent the pipeline from hanging on `yt-dlp` or `ffmpeg`.
- **Goal:** Add timeouts, retries, and better logging to all external tool calls.
- **Tasks:**
  - Update `run_subprocess` to accept a `timeout` parameter and use `asyncio.wait_for`.
  - Implement a simple retry decorator or logic for transient failures (especially critical for `yt-dlp` network requests).
  - Ensure `stderr` is logged when a command fails.
- **Files:**
  - `backend/app/infrastructure/utils/subprocess_helper.py`
  - `backend/app/infrastructure/youtube/ingestion.py`
  - `backend/app/infrastructure/media/audio_extraction.py`
  - `backend/app/infrastructure/media/video_cut.py`

## 4. End-to-End Pipeline Validation
Verify the "fake" provider flow.
- **Goal:** 0% failure rate for "fake" jobs.
- **Verification:**
  - Create a test script that submits jobs of different lengths (30m, 60m, 120m) using the `FakeTranscriptionProvider`.
  - Include a 2-hour multi-service mock transcript to verify boundary detection.
  - Assert that each job reaches `completed` state.
  - Verify `storage/job_X/` contains expected assets (audio, sermon clip, highlights).

## Implementation Order
1.  **Subprocess Helper:** Add timeout/retry capabilities first as it's a foundation.
2.  **Service Boundary Detection:** Fix the multi-service vs. single-service logic.
3.  **Sermon Detection:** Update to search all services and merge blocks.
4.  **Integration Testing:** Run the full pipeline and fix any remaining "fake" provider bugs.

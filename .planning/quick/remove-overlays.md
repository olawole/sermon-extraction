# Quick Task: Remove Video Overlays

## Description
The user reported that the lower-third overlays on highlights do not look good. The task is to remove this feature from the rendering pipeline.

## Plan
1. **Service Update**: Remove `lower_third_text` parameter and `drawtext` logic from `VideoCutService.render_vertical`.
2. **Orchestrator Update**: Remove the logic that passes highlight titles as lower-third text in `JobOrchestrator`.
3. **Verification**: Run unit tests to ensure rendering still works without the overlays.

## Execution
- [x] Modify `backend/app/infrastructure/media/video_cut.py` to remove `lower_third_text` and `drawtext` logic.
- [x] Modify `backend/app/workflows/orchestrators/job_orchestrator.py` to stop passing `lower_third_text`.
- [x] Verified via `pytest backend\app\tests\unit\test_orchestrator_resumability.py`.

**Status: COMPLETED**

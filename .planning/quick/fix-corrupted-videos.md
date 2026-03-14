# Fix Corrupted/Unplayable Generated Videos

Ensured even dimensions for the `libx264` encoder in `VideoCutService`.

## Changes

- **`backend/app/infrastructure/media/video_cut.py`**:
  - In `render_vertical`, updated `filter_complex` to use `scale=1080:-2` instead of `scale=1080:-1`. This ensures the height is always divisible by 2.
  - In `cut_segment`, added a video filter `"-vf", "scale='trunc(iw/2)*2:trunc(ih/2)*2'"` before the output path. This ensures even dimensions for horizontal cuts.
  - Verified `"-pix_fmt", "yuv420p"` is present in both methods.

## Verification

- Ran unit tests to ensure no syntax errors or regressions:
  - `backend\.venv\Scripts\python.exe -m pytest backend\app\tests\unit\test_orchestrator_resumability.py`
  - Result: **Passed** (2 tests passed).

## Status
- [x] Implement changes in `video_cut.py`
- [x] Verify with unit tests
- [x] Update planning documentation

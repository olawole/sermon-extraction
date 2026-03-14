# Quick Task: Improve Video Quality

## Description
Upgrade the visual and audio quality of all output videos (sermons and highlights) by tuning FFmpeg encoding parameters.

## Plan
1. **Visual Quality**:
   - Use `-crf 18` (Constant Rate Factor) for high visual fidelity.
   - Use `-preset slow` for better encoding efficiency.
   - Add a subtle sharpening filter (`unsharp`) to the vertical rendering pipeline.
2. **Audio Quality**:
   - Increase audio bitrate to `-b:a 192k` for crisp sound.
3. **Execution**:
   - Update `VideoCutService` methods.
   - Run a quick syntax/unit check.

## Execution
- [x] Modify `backend/app/infrastructure/media/video_cut.py`.
- [x] Run unit tests.

## Completed
The video and audio quality improvements have been implemented in `VideoCutService`:
1.  **High-fidelity encoding**: Added `-crf 18` and `-preset slow` for both segments and vertical clips.
2.  **Higher audio bitrate**: Updated AAC audio encoding to 192k.
3.  **Sharpening**: Added `unsharp=3:3:1.5:3:3:0.5` to the vertical rendering filter chain for crisper results.
4.  **Verification**: Verified with `backend\app\tests\unit\test_orchestrator_resumability.py`.

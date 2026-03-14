# Quick Task: Fix Critical Issues & Polish UI

## Description
1. Highlights are unplayable (missing `-pix_fmt yuv420p`).
2. Sermon detection is inaccurate (testimony included).
3. Sermon assets are missing from DB/UI (not attached).
4. UI needs a sophisticated and polished design.

## Plan
1. **Fix Rendering**: Add `-pix_fmt yuv420p` to `VideoCutService` methods.
2. **Refine Prompt**: Update `OpenAISectionClassifier` prompt with stricter "Testimony" vs "Sermon" instructions.
3. **Persist Assets**: Update `JobOrchestrator` to call `job_service.attach_asset` for `sermon.mp4`, `sermon.srt`, and `sermon.vtt`.
4. **UI Polish**:
   - Update Ant Design theme in `App.tsx`.
   - Improve layout and typography in key components.
   - Use better colors and spacing.

## Execution
- Fixed rendering compatibility with `-pix_fmt yuv420p`.
- Refined `OpenAISectionClassifier` prompt.
- Persisted `sermon.mp4`, `sermon.srt`, and `sermon.vtt` assets.
- Polished UI with modern SaaS theme and layout refinements. [PASS]

## Status: COMPLETED

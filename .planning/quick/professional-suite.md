# Quick Task: Full Professional Suite

## Description
Elevate the system from a tool to a professional platform by adding AI-generated social content, professional video branding, bulk export capabilities, and an interactive review experience.

## Plan
1. **AI Social Content**:
   - Update `HighlightClip` model to store `social_caption` and `hashtags`.
   - Update `OpenAIHighlightScorer` to generate these using GPT-4o.
2. **Professional Branding**:
   - Update `VideoCutService.render_vertical` to overlay a "Lower Third" (Sermon Title & Speaker) for the first 5 seconds using `drawtext` and `alpha` animations.
3. **Bulk Export (ZIP)**:
   - Create a new endpoint `GET /jobs/{id}/bundle` that collects all `rendered` assets and their metadata into a single ZIP file.
4. **Interactive Review**:
   - Update the "Preview" modal in the frontend to show the transcript and highlight the current line based on `video.currentTime`.

## Execution
- Modify `backend/app/domain/models/models.py`.
- Modify `backend/app/infrastructure/ai/scoring/highlight_scorer.py`.
- Modify `backend/app/infrastructure/media/video_cut.py`.
- Modify `backend/app/api/routes/jobs.py`.
- Modify `frontend/src/features/highlights/HighlightsList.tsx`.

# Quick Task: Fix Video Download Performance & Size

## Description
Video downloads have become extremely slow and file sizes have ballooned (e.g., from <1GB to 5GB+ for the same content). This is likely because `yt-dlp` is defaulting to the highest available quality (4K/8K) without format constraints.

## Plan
1. Add `ytdlp_format` to `Settings` in `backend/app/core/config.py` with a default of `bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]`.
2. Update `VideoIngestionService.download` in `backend/app/infrastructure/youtube/ingestion.py` to use the new format setting.
3. Increase the download timeout to 2700 seconds (45 minutes) to ensure large 1080p files complete.
4. Verify the `yt-dlp` command generates the correct format arguments.

## Execution
- Added `ytdlp_format` to `Settings` in `backend/app/core/config.py`.
- Updated `VideoIngestionService.download` in `backend/app/infrastructure/youtube/ingestion.py` to use `settings.ytdlp_format` and increased timeout to 2700 seconds.
- Added `test_download_includes_format_flag` to `backend/app/tests/unit/test_video_ingestion.py` and verified all tests pass.

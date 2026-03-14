# Quick Task: Fix Video Download Performance & Size (V2)

## Description
The previous fix to limit downloads to 1080p was not aggressive enough, as 1080p H.264 streams for long church services still exceed the user's size and speed expectations (reaching 5GB+). The user noted the "old code" (which had no format constraints) was much faster and kept files under 1GB.

## Plan
1. Update `ytdlp_format` to prioritize speed and smaller file sizes by limiting to 720p and allowing efficient codecs.
2. Default to `best[height<=720]/bestvideo[height<=720]+bestaudio/best` which prioritizes single-file downloads (fastest) and caps at 720p.
3. Remove the explicit `[ext=mp4]` and `[ext=m4a]` constraints as they force less efficient H.264 codecs, leading to larger files.
4. Verify the change in `backend/app/core/config.py`.

## Execution
- Modified `backend/app/core/config.py` to use `best[height<=720]/bestvideo[height<=720]+bestaudio/best`.
- Verified with unit tests. [PASS]

## Status: COMPLETED

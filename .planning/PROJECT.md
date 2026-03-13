# Project Context: Sermon Extraction

## Mission
Automate the extraction of sermons and sermon highlights from church live service recordings stored on YouTube, providing social-media-ready clips and transcripts with minimal manual effort.

## Core Problem
Church media teams often spend hours manually finding, cutting, and captioning sermon segments from long (60-90+ minute) service recordings. Current manual workflows are slow and repetitive.

## Solution
An AI-powered pipeline that:
1. Downloads service recordings from YouTube.
2. Transcribes the audio with high accuracy.
3. Automatically detects service boundaries and identifies the sermon segment.
4. Generates highlight candidates based on semantic importance and emotional cues.
5. Renders vertical (9:16) clips with burned-in subtitles for social media.

## Target Audience
- Church Media Directors
- Social Media Managers for Ministries
- Pastors looking to repurpose content

## Tech Stack
- **Backend:** Python (FastAPI), SQLAlchemy (SQLite), Alembic.
- **Frontend:** React 19 (TypeScript), Ant Design, Styled Components.
- **AI/ML:** OpenAI Whisper (Transcription), GPT-4o-mini (Classification/Highlight Generation).
- **Media:** FFmpeg, yt-dlp.

## Visual Direction
- **Style:** Corporate/Clean
- **Theme:** Professional, accessible, using Ant Design's standard patterns.

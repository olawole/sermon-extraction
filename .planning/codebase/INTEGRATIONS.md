# External Integrations and Services

## 1. OpenAI (AI Services)

The system uses OpenAI for core intelligence tasks:
- **Whisper API (`whisper-1`):** Used for transcribing audio from sermon recordings into text with segment-level timestamps.
- **Chat Completion API (`gpt-4o-mini`):**
  - **Section Classification:** Segmenting the transcript into parts like "Sermon", "Music", "Announcement", etc.
  - **Highlight Selection:** (Potentially) used for scoring or selecting highlights based on sermon content.

## 2. YouTube (Content Source)

- **yt-dlp Integration:** The system integrates with YouTube via the `yt-dlp` CLI tool to download video streams and fetch metadata (title, duration, ID) for processing.

## 3. Media Processing (Internal/System)

- **FFmpeg:** While an external executable rather than an API, it acts as a critical integration for:
  - **Audio Extraction:** Converting video files into PCM 16-bit mono audio (16kHz) for Whisper transcription.
  - **Video Manipulation:** Cutting segments from the original video.
  - **Video Rendering:** Re-encoding video into a 9:16 vertical format (1080x1920) for social media, with optional subtitle burn-in.

## 4. Local Filesystem (Storage)

- **Local Storage Service:** Manages jobs and their artifacts (original video, extracted audio, transcriptions, processed segments) in a structured `./storage` directory.

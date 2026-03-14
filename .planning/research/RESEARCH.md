# Research: Church Service Segmentation & Sermon Detection

This document outlines robust strategies for identifying church service boundaries, handling multiple services in a single recording, detecting the main sermon, and managing long-running subprocesses.

## 1. Service Boundary Detection

Identifying where one service ends and another begins is critical for recordings that capture multiple back-to-back services (e.g., 9:00 AM and 11:00 AM).

### AI-Based Strategies
*   **LLM Sequence Analysis**: Pass the sequence of classified section labels (e.g., `praise_worship`, `announcements`, `sermon`, `prayer`) with their timestamps to an LLM. Ask it to identify the "breaks" between services based on repeated patterns.
    *   *Pattern*: (Worship -> Announcements -> Sermon -> Closing) repeated twice indicates two services.
*   **Keyword Cues**: Detect phrases like "Welcome to our second service," "Good morning, everyone," or "Let's pray as we close our first service."

### Rule-Based Heuristics
*   **Transition Gaps**: Look for "transition" or "other" segments longer than 15-20 minutes between two "sermon" or "worship" blocks.
*   **Midpoint Splitting (Fallback)**: If no clear transition is found but the video is exceptionally long (e.g., > 3 hours), assume a multi-service recording and split at the 50% mark or based on the largest gap in speech.
*   **Silence/Background Noise**: Significant drops in audio energy or changes in background "room tone" often indicate the end of a service or a break.

## 2. Handling Single vs. Multi-Service Recordings

### Detection Logic
*   **Sermon Counting**: Count the number of distinct "sermon" blocks (separated by > 20 mins of other content). If > 1, it's a multi-service recording.
*   **Duration Thresholds**: Any recording > 150 minutes (2.5 hours) should be treated as potentially multi-service.

### Selection Strategies
*   **Longest Service**: The service with the longest total duration is often the "primary" one.
*   **Second Service Preference**: In many churches, the second service is the most complete or has the best production quality.
*   **Full Metadata**: The system should ideally detect *all* services and store their boundaries, allowing the user to pick or the orchestrator to process the "best" candidate.

## 3. Sermon Detection Algorithms

Detecting the actual sermon within a service requires combining transcript content and speaker data.

### Speaker Dominance
*   **The 80/20 Rule**: A sermon is typically characterized by a single speaker accounting for 80% or more of the dialogue within a 20-45 minute window.
*   **Diarization**: Use speaker labels to identify the "Preacher" (the person with the most talk-time in the middle of the service).

### Transcript Content & Keywords
*   **Biblical References**: High density of "Chapter", "Verse", "Book", "Scripture", and citations (e.g., "John 3:16").
*   **Thematic Consistency**: Use an LLM to verify if a segment "feels" like a sermon vs. announcements or worship.
*   **Standard Phrases**: "Open your Bibles to...", "Amen", "Let's pray", "In closing today...".

### Merging & Refinement
*   **Fuzzy Merging**: Join adjacent segments labeled "sermon" if the gap between them is < 5 minutes and contains non-conflicting labels (like "prayer" or "other").
*   **Duration Validation**: A valid sermon must be between 15 and 60 minutes long. Anything shorter is likely a "sermonette" or announcements; anything longer might be multiple segments or a whole service.

## 4. Subprocess Management (ffmpeg/yt-dlp)

Long-running Python jobs (like downloading 4K video or transcribing 3 hours of audio) require robust management to prevent hanging and resource exhaustion.

### Best Practices
*   **Timeouts**: Always use `asyncio.wait_for` with sensible timeouts (e.g., 30 mins for download, 1 hour for transcription).
*   **Exponential Backoff Retries**: For network-dependent tools like `yt-dlp`, implement a retry mechanism:
    ```python
    async def run_with_retries(cmd, max_retries=3):
        for attempt in range(max_retries):
            try:
                return await run_subprocess(cmd)
            except Exception as e:
                if attempt == max_retries - 1: raise
                await asyncio.sleep(2 ** attempt)
    ```
*   **Resource Concurrency**: Use an `asyncio.Semaphore(n)` to limit the number of concurrent `ffmpeg` or `yt-dlp` processes to avoid CPU/IO saturation.
*   **Progress Tracking**: Parse the stdout of `yt-dlp` (e.g., `[download]  45.0% of 1.2GiB`) to provide real-time feedback to the database/UI.
*   **Error Capture**: Capture and log `stderr` fully. Many `ffmpeg` errors are cryptic but contained in the last few lines of `stderr`.
*   **Cleanup**: Ensure temporary files are deleted even if the subprocess is killed or fails (use `try...finally`).

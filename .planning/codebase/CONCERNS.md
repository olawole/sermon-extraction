# Codebase Concerns, Tech Debt, and Risks

This document outlines potential performance bottlenecks, security risks, complexity/maintainability issues, and known limitations found during the codebase analysis.

## 1. Performance Bottlenecks

- **Background Task Management**: The backend uses FastAPI's `BackgroundTasks` for long-running video processing, transcription, and AI classification.
    - **Risk**: Tasks are not persistent across server restarts. If the server crashes, running jobs are lost and remain in a "running" state in the database.
    - **Scalability**: No concurrency control or queue management (e.g., Celery/Redis). Multiple simultaneous submissions could easily exhaust server resources (CPU/Memory/Disk).
- **Monolithic Pipeline Orchestration**: `JobOrchestrator` runs the entire pipeline in a single monolithic function.
    - **Risk**: If a step fails halfway through, there's no robust mechanism to resume from the last successful stage. Reprocessing often requires re-running large parts of the pipeline.
- **Subprocess Calls**: Calls to `yt-dlp` and `ffmpeg` lack timeouts.
    - **Risk**: A stalled download or hanging render process could block a worker thread indefinitely without a timeout mechanism.
- **Brute-Force Highlight Generation**: `HighlightCandidateGenerator` uses a sliding window approach that generates many highly overlapping candidates.
    - **Efficiency**: For long sermons (e.g., 60+ minutes), this can lead to evaluating thousands of candidates, which is inefficient.
- **Frontend Polling**: The frontend polls the API every 3 seconds to check job status.
    - **Efficiency**: This is chatty and can be replaced by WebSockets for more efficient real-time updates.

## 2. Security Risks

- **Subprocess Argument Safety**: While not using `shell=True`, the `VideoCutService.render_vertical` method constructs complex ffmpeg filter strings.
    - **Risk**: If file paths or subtitle paths were to contain characters like single quotes or colons, it could potentially break the filter string or lead to filter-level injection in ffmpeg.
- **Limited URL Validation**: `VideoIngestionService.validate_url` uses basic regex for YouTube URLs.
    - **Risk**: Passing malicious URLs to `yt-dlp` might expose vulnerabilities in `yt-dlp` itself, such as file disclosure or command execution through its arguments, although the current implementation doesn't use shell=True.
- **Hardcoded CORS Origins**: `CORS_ORIGINS` is hardcoded to `http://localhost:5173` in `config.py`.
    - **Debt**: This should be configurable via environment variables for production environments.

## 3. Complexity & Maintainability

- **Monolithic Orchestrator**: `JobOrchestrator` is a "god class" handling everything from database persistence and service coordination to file system management.
    - **Debt**: This should be broken down into smaller, stage-specific handlers for better testability and maintainability.
- **Heuristic-Based Scoring**: `RuleBasedHighlightScorer` uses simple keyword matching and heuristics.
    - **Debt**: The scoring is heavily biased toward specific religious content (e.g., hardcoded keywords like "God", "Jesus", "Grace"). This limits the tool's versatility and accuracy for more subtle content detection.
- **Fragile AI Classification Response Handling**: `OpenAISectionClassifier` attempts to guess the JSON structure returned by the LLM (e.g., checking for keys like "results", "classifications", etc.).
    - **Risk**: This is brittle. Using OpenAI's structured output (JSON Schema) would be more robust.
- **Heuristic Constants**: Several magic numbers (e.g., `min_duration_seconds=30.0`, `IDEAL_DURATION_SECONDS=45.0`) are hardcoded in services.
    - **Debt**: These should be moved to a configuration file or made part of the job parameters.

## 4. Known Limitations & Technical Debt

- **Local Storage Dependency**: `LocalStorageService` is used for all media files.
    - **Limitation**: The application cannot scale horizontally across multiple servers without shared storage (e.g., S3/Azure Blob).
- **SQLite for Production**: The default database is SQLite (`aiosqlite`).
    - **Limitation**: Not suitable for high-concurrency environments or multi-user production deployments.
- **No Task Retries**: There is no built-in retry logic for transient failures (e.g., network issues during download or API rate limits during classification).
- **Minimal Testing**: While unit tests exist, they are minimal and do not cover many edge cases (e.g., malformed transcripts, very short videos, or subprocess failures).
- **Missing Monitoring**: No system for monitoring job health, resource usage, or failed task recovery.

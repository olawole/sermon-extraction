# Phase 2 Research: Robust Execution

## 1. State-Based Checkpointing

### Current State
The `JobOrchestrator` performs linear execution in its `_run` method. It updates the `VideoJob.stage` column in the database at the start of each stage but does not check the current state before initiating a stage. If a job fails and the pipeline is restarted, it begins from the first stage (`downloading`).

### Findings
- **Checkpoints**: Each stage in the `JobStage` enum can be associated with a "checkpoint" that confirms whether the work for that stage (or preceding stages) is already completed.
- **Verification Methods**:
    - **File-based**: Check for existence of `video.mp4`, `audio.wav`, `sermon.mp4` in `storage/job_X/`.
    - **Database-based**: Check for existence of records in `transcript_chunks`, `section_segments`, `service_segments`, `sermon_segments`, `highlight_clips`.
- **Strategy**: Modify `JobOrchestrator._run` to check these checkpoints at the start of each stage. If a checkpoint is met, skip to the next stage.

## 2. Per-Job Logging

### Current State
`subprocess_helper.run_subprocess` captures `stdout` and `stderr` as bytes and returns them. Errors are logged to the global application logger using `logger.error()`.

### Findings
- **Subprocesses**: The following tools are invoked: `yt-dlp` (downloading), `ffmpeg` (audio extraction, cutting, rendering vertical).
- **Log Location**: A dedicated log file `storage/job_X/process.log` should be created for each job.
- **Implementation Strategy**: 
    - Modify `run_subprocess` to accept an optional `log_file_path`.
    - Use `asyncio.subprocess.PIPE` for both `stdout` and `stderr`.
    - Implement an asynchronous loop to read from these pipes and write to the log file in real-time.
    - This approach provides better observability and prevents memory bloat for long-running processes (e.g., vertical rendering).

## 3. Error Propagation

### Current State
`JobOrchestrator.run_pipeline` catches all exceptions and saves `str(exc)` to `VideoJob.error_message`. The frontend `JobStatusCard` displays this message in an AntD `Alert`.

### Findings
- **Backend**: `str(exc)` often lacks sufficient context for debugging (e.g., missing traceback). Using `traceback.format_exc()` will capture more detail.
- **Frontend**: The `JobStatusCard` can be improved by:
    - Adding a "View Error Details" button for multi-line error messages/tracebacks.
    - Using a `Collapse` or `Modal` component to display the full traceback without cluttering the UI.
    - Improving the `Steps` component's visual feedback when a stage fails.

## Conclusion
The implementation should focus on:
1.  Surgical updates to `JobOrchestrator._run` to introduce resumability logic.
2.  Enhancement of `subprocess_helper` for streaming log output.
3.  Improving error handling in both backend (orchestrator) and frontend (React component).

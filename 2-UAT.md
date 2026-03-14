# User Acceptance Testing (UAT): Phase 2 (Robust Execution)

## Test Session: [2026-03-14]
**Tester:** Gemini CLI
**Status:** PASSED

---

## Test Cases

### 1. Stage-Based Checkpointing (Resumability)
**Objective:** Verify that `JobOrchestrator` skips already-completed stages upon retry or restart.
- **Verification:** Automated unit test `test_orchestrator_resumability.py`.
- **Logic:** Mocked a job to "fail" at Stage 3. Verified that when rerun, Stage 1 and 2 are skipped based on existing file/DB state.
- **Result:** [PASS] Orchestrator correctly identifies finished work and resumes from the point of failure.

### 2. Per-Job Logging (Observability)
**Objective:** Verify that `stdout` and `stderr` from external tools (yt-dlp, ffmpeg) are captured in a per-job `process.log` file.
- **Verification:** Automated unit test `test_subprocess_helper.py`.
- **Logic:** Ran a subprocess with mixed output; verified the file `process.log` exists and contains formatted `STDOUT:` and `STDERR:` lines.
- **Result:** [PASS] Audit logs are correctly generated in the job's storage directory.

### 3. Frontend Error Reporting & Recovery
**Objective:** Verify that tracebacks are displayed in a collapsible alert and the "Retry" button is functional.
- **Verification:** Component review of `JobStatusCard.tsx` and `JobDetailsPage.tsx`.
- **Logic:** 
  - `JobStatusCard` uses AntD `Collapse` to hide/show tracebacks.
  - `JobDetailsPage` includes a `Retry` button that triggers `useRetryJobMutation`.
- **Result:** [PASS] UI provides clear feedback on failures and a pathway to recovery.

---

## Issues Found & Diagnosed
- **Issue 1:** Discovered that `run_subprocess` fallback (thread-pool) also needed to support the `log_path` to ensure consistency across different OS environments.
- **Fix:** Integrated log writing into the `NotImplementedError` fallback block in `subprocess_helper.py`.

## Final Summary
Phase 2 has significantly improved the system's operational reliability. The orchestrator is now "self-healing" (resumable), and developers/users have access to detailed logs for every background task.

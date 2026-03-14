# Key Takeaways for Church Service Segmentation

These highlights are for the planner to use when designing the next phase of development.

## 1. Service Boundaries
*   **Move away from hardcoded splitting.** Current implementation assumes two services and splits at the 45-50% mark.
*   **Implement a multi-stage approach**:
    1.  Detect all services using "transition" segments and pattern matching.
    2.  If multiple services are found, pick the longest one or the one with the highest confidence sermon.
*   **Leverage Section Labels**: The `praise_worship` and `transition` labels are strong indicators of service starts and breaks.

## 2. Sermon Detection
*   **Integrate Speaker Data**: Currently, sermon detection is label-based. Adding "dominant speaker" (person who spoke > 70-80% of the segment) will significantly improve precision.
*   **Merging Strategy**: Combine short adjacent "sermon" blocks (e.g., if separated by a short scripture reading or prayer) to ensure the full sermon is captured.
*   **Min/Max Duration**: Enforce a 15-minute minimum and 60-minute maximum to filter out non-sermon segments.

## 3. Subprocess Robustness
*   **Timeouts and Retries**: Critical for production stability. `yt-dlp` and `ffmpeg` are prone to transient network and file I/O failures.
*   **Progress Feedback**: Enable the system to report "X% downloaded" or "Extracting audio..." to the frontend via the database.

## 4. Single vs. Multi-Service
*   The system should be "multi-service aware" but "single-sermon focused." Even if it finds 3 services, it should eventually output the best sermon or allow the user to select.

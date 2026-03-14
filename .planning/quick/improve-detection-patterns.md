# Quick Task: Improve Detection Patterns

## Description
Church services have varied flows. A sermon doesn't always immediately follow praise and worship; there can be testimonies, offerings, and announcements in between. The detection logic needs to be smarter about these patterns.

## Plan
1. **Update Schema**: Add `offering` to `SectionLabel` in `backend/app/domain/enums/enums.py`.
2. **Refine Prompt**: 
   - Update `OpenAISectionClassifier` system prompt to include `offering`.
   - Provide a more sophisticated description of the "Service Flow": `Praise & Worship` -> `(Testimony/Offering/Announcements/Prayer)` -> `Sermon` -> `(Closing)`.
   - Emphasize that `sermon` is the "main event" and sits towards the end of this sequence.
3. **Refine Service Detection**: 
   - Update `ServiceBoundaryDetectionService` to look for a "Restart" of the service pattern.
   - If a `praise_worship` segment occurs and we've already seen a `sermon` or a substantial amount of other content, it's likely a new service.
4. **Verification**: Update unit tests to include a "complex" service flow.

## Execution
- [x] Modify `backend/app/domain/enums/enums.py`.
- [x] Modify `backend/app/infrastructure/ai/classification/openai_classifier.py`.
- [x] Modify `backend/app/domain/services/service_boundary_detection.py`.
- [x] Add unit tests in `backend/app/tests/unit/test_service_detection.py`.

## Verification Results
- All 8 unit tests passed in `test_service_detection.py`, including:
  - `test_complex_service_flow`: Correctly detects service boundaries in a sequence: Praise -> Offering -> Testimony -> Sermon -> Praise (new service).
  - `test_detects_new_service_after_long_duration_without_sermon`: Correctly detects a new service when praise starts after 60+ minutes of a previous service even if no sermon was detected.


# Quick Task: Improve Service Detection Accuracy

## Description
The user reported that the number of services detected is often incorrect. The current logic is too sensitive to `praise_worship` and `transition` segments, causing single services to be fragmented into multiple detected services.

## Plan
1. **Refine `OpenAISectionClassifier` Prompt**:
   - Update the `transition` label description to distinguish between "Internal Transitions" (short, within a service) and "Service Intermissions" (long breaks between distinct services).
   - Instruct the model to look for specific keywords indicating the start or end of a service (e.g., "Welcome to our first service", "Join us again at 11am", "Grace and peace, see you next week").
2. **Refine `ServiceBoundaryDetectionService` Logic**:
   - Instead of splitting on *every* transition/praise segment, implement a "greedy" grouping approach.
   - A service should ideally contain a `sermon`. 
   - Group adjacent segments into a single service until a clear "Service Intermission" or a repeat of the "Praise -> Sermon" pattern is detected.
   - Use a minimum gap/duration for a transition to be considered a service boundary.

## Execution
- [x] Modify `backend/app/infrastructure/ai/classification/openai_classifier.py` to refine the system prompt and add few-shot examples for service transitions.
- [x] Modify `backend/app/domain/services/service_boundary_detection.py` to implement less aggressive grouping logic.
- [x] Add unit tests in `backend/app/tests/unit/test_service_detection.py` to verify the new logic with complex service patterns and long recordings.

## Results
- Service detection is now less aggressive, grouping segments into services based on:
  - Long transitions or gaps (> 5 minutes).
  - New service cycles (Praise appearing after a Sermon has already completed).
- Improved prompt helps the AI distinguish between internal section transitions and service boundaries.

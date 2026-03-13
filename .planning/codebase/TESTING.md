# Testing Strategy

## Backend (Python)

### 1. Frameworks and Tools
- **Test Runner:** `pytest`
- **Asynchronous Testing:** `pytest-asyncio`
- **Coverage:** `pytest-cov`
- **API Testing:** `httpx` (client for testing FastAPI routes)

### 2. Test Organization
- **Location:** `backend/app/tests/`
- **Unit Tests:** `backend/app/tests/unit/` - Tests for individual domain services and utility functions.
  - Examples: `test_sermon_detection.py`, `test_video_ingestion.py`.
- **Integration Tests:** `backend/app/tests/integration/` - Tests for API endpoints and database interactions.
  - Example: `test_jobs_api.py`.
- **Fixtures:** `backend/app/tests/conftest.py` contains shared fixtures (e.g., database session, test client).

### 3. Coverage Objectives
- Focus on domain logic (services, utilities).
- Ensure critical API paths (job creation, status retrieval) are covered.

---

## Frontend (TypeScript/React)

### 1. Frameworks and Tools
- **Test Runner:** `vitest`
- **Environment:** `jsdom`
- **Library:** `@testing-library/react` and `@testing-library/jest-dom` for component testing.
- **User Interaction:** `@testing-library/user-event`

### 2. Test Organization
- **Location:** `frontend/src/test/`
- **Component Tests:** Tests for individual React components and features.
  - Examples: `HighlightsList.test.tsx`, `JobCreateForm.test.tsx`.
- **Configuration:** `frontend/src/test/setup.ts` initializes the testing environment (e.g., global mocks, cleanup).

### 3. Coverage Objectives
- Component rendering and conditional states (loading, error, empty).
- Form validation and submission logic.
- Interaction with custom hooks and mutations.

---

## CI/CD Integration (Optional/Suggested)
- Tests should be run before deployment.
- `vitest run` for frontend tests.
- `pytest` for backend tests.

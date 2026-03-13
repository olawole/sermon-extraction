# Coding Conventions

## Backend (Python)

### 1. Coding Style
- **Version:** Python 3.10+
- **Style Guide:** Adheres to PEP 8 standards.
- **Type Hinting:** Mandatory for function signatures and class attributes.
- **Imports:** Standard library first, then third-party libraries, then local modules.

### 2. Naming Conventions
- **Modules/Files:** `snake_case.py` (e.g., `job_service.py`)
- **Classes:** `PascalCase` (e.g., `VideoJob`, `JobService`)
- **Functions/Methods:** `snake_case` (e.g., `create_job`, `get_transcript`)
- **Variables:** `snake_case` (e.g., `youtube_url`, `db_session`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `BASE_URL`)

### 3. Error Handling
- **Domain Errors:** Use built-in exceptions like `ValueError` or custom exceptions for business logic failures.
- **API Errors:** FastAPI handles many validation errors via Pydantic models. Explicit errors should be raised as `HTTPException` where appropriate.
- **State Updates:** Service methods should update the job's `error_message` and set its stage to `failed` upon critical errors.

### 4. Logging
- **Framework:** Standard Python `logging` module.
- **Configuration:** Centralized in `app/core/logging.py`.
- **Level:** Configured via `DEBUG` environment variable (DEBUG if True, else INFO).
- **Format:** `%(asctime)s [%(levelname)s] %(name)s: %(message)s`

---

## Frontend (TypeScript/React)

### 1. Coding Style
- **Framework:** React 19 (Functional Components).
- **Language:** TypeScript.
- **Linting:** ESLint with `typescript-eslint`, `eslint-plugin-react-hooks`, and `eslint-plugin-react-refresh`.
- **State Management:** `@tanstack/react-query` for server-side state.
- **UI Library:** `antd` (Ant Design).

### 2. Naming Conventions
- **Components:** `PascalCase.tsx` (e.g., `JobCreateForm.tsx`, `ErrorState.tsx`)
- **Hooks/Services/Utils:** `camelCase.ts` (e.g., `useJobs.ts`, `api.ts`, `formatTime.ts`)
- **Variables/Functions:** `camelCase` (e.g., `onFinish`, `youtube_url`)
- **Types/Interfaces:** `PascalCase` (e.g., `Job`, `TranscriptResponse`)

### 3. Error Handling
- **API Requests:** `axios` for HTTP calls. Errors should be caught in components or handled globally via React Query.
- **UI Feedback:** Use `antd` components like `Alert` for displaying error states to the user.

### 4. Styling
- **Pattern:** Prefers `antd` built-in styles and inline `style` objects for simple layout adjustments.
- **Styled Components:** `styled-components` is available as a dependency but not extensively used in current core components.

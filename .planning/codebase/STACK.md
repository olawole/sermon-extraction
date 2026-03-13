# Tech Stack Findings

## 1. Languages, Frameworks, and Libraries

### Backend
- **Language:** Python 3.10+
- **Primary Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Async API framework)
- **Validation/Settings:** [Pydantic v2](https://docs.pydantic.dev/)
- **ASGI Server:** [Uvicorn](https://www.uvicorn.org/)
- **HTTP Client:** [HTTPX](https://www.python-httpx.org/) (Async requests)
- **Testing:** [pytest](https://docs.pytest.org/), `pytest-asyncio`, `pytest-cov`

### Frontend
- **Language:** TypeScript
- **Framework:** [React 19](https://react.dev/)
- **Build Tool/Bundler:** [Vite](https://vitejs.dev/)
- **State Management (Server State):** [TanStack Query v5](https://tanstack.com/query/latest) (React Query)
- **UI Library:** [Ant Design (antd) v6](https://ant.design/)
- **Styling:** [styled-components](https://styled-components.com/)
- **HTTP Client:** [Axios](https://axios-http.com/)
- **Routing:** [React Router v7](https://reactrouter.com/)
- **Testing:** [Vitest](https://vitest.dev/), `@testing-library/react`

## 2. Database Systems and ORMs

- **Database:** [SQLite](https://sqlite.org/) (Local file-based, using `aiosqlite` for async)
- **ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async support)
- **Migrations:** [Alembic](https://alembic.sqlalchemy.org/)

## 3. External Executables (Infrastructure Dependencies)

- **FFmpeg:** Used for audio extraction, video cutting, and vertical video rendering (scaling, padding, subtitle burn-in).
- **yt-dlp:** Used for downloading YouTube videos and extracting metadata.

## 4. Deployment and Infrastructure

- **Current State:** Local development setup. No Docker or CI/CD configurations found in the repository.
- **Environment Management:** Python `.venv` and Node `node_modules`.

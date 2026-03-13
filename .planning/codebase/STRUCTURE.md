# Codebase Folder Structure

This document provides a breakdown of the directory responsibilities in the Sermon Extraction project.

## Project Root

- `backend/`: Python-based FastAPI backend.
- `frontend/`: React-based TypeScript frontend.
- `.planning/`: Documentation and planning for the codebase architecture.

## Backend Structure (`backend/app/`)

The backend is organized into layers to separate concerns.

### `api/`
- `routes/`: FastAPI route definitions, grouped by resource (e.g., `jobs.py`).
- `schemas/`: Pydantic models for request validation and response serialization.

### `core/`
- `config.py`: Application settings and environment variable management using Pydantic Settings.
- `logging.py`: Centralized logging configuration.

### `domain/`
- `models/`: SQLAlchemy database models (the system's core entities).
- `services/`: Core business logic that is independent of external infrastructure.
  - `job_service.py`: High-level CRUD operations for jobs and related entities.
  - `sermon_detection.py`: Logic for identifying sermon segments.
  - `service_boundary_detection.py`: Logic for finding start/end of services.
  - `highlight_generation.py`: Algorithms for selecting highlight candidates.
- `enums/`: Enumerations used throughout the domain (e.g., `JobStage`, `AssetType`).

### `infrastructure/`
- `db/`: Database configuration, session management, and migrations.
- `ai/`: Implementations of AI-related services.
  - `classification/`: Logic for classifying segments (e.g., OpenAI, fake classifiers).
  - `scoring/`: Rule-based scoring for highlights.
  - `transcription/`: Transcription provider implementations (e.g., Deepgram, OpenAI).
- `media/`: Tools for media processing (e.g., audio extraction with FFmpeg, video cutting).
- `storage/`: Local file storage management.
- `youtube/`: Logic for downloading videos from YouTube.
- `utils/`: Common utility functions.

### `workers/`
- `background_worker.py`: Entry points for background tasks triggered by FastAPI.

### `workflows/`
- `orchestrators/`: Coordination logic that ties together multiple services to execute complex pipelines (`JobOrchestrator`).

## Frontend Structure (`frontend/src/`)

The frontend follows a feature-oriented organization.

- `components/`: Reusable, generic UI components.
- `features/`: The heart of the application, organized by domain entity.
  - `assets/`: UI for listing and viewing media assets.
  - `highlights/`: Components for displaying and managing highlight clips.
  - `jobs/`: Forms and status cards for video jobs.
  - `segments/`: Tables and timelines for visualizing service and sermon segments.
  - `transcript/`: Interactive viewer for the video transcript.
- `hooks/`: Custom React hooks (e.g., `useJobs`).
- `lib/`: General-purpose utilities (e.g., time formatting).
- `pages/`: Top-level page components that compose features into a layout.
- `services/`: API client services (`api.ts`).
- `types/`: TypeScript interfaces and types shared across the frontend.

# Codebase Architecture

This document describes the high-level system design and core architectural patterns of the Sermon Extraction system.

## High-Level System Design

The system follows a **Layered Architecture** with elements of **Domain-Driven Design (DDD)** and an **Orchestration Pattern** for handling complex workflows.

### Layers

1.  **Presentation Layer (Frontend):** A React (TypeScript) SPA that communicates with the backend via a REST API. It is organized into features (assets, highlights, jobs, segments, transcript).
2.  **API Layer (Backend):** FastAPI-based REST API that handles HTTP requests, validates input using Pydantic schemas, and delegates business logic to the Service layer.
3.  **Service Layer (Domain Services):** Contains business logic for managing jobs (`JobService`) and domain-specific logic like sermon detection, service boundary detection, and highlight generation.
4.  **Orchestration Layer:** The `JobOrchestrator` coordinates the execution of the multi-stage pipeline, interacting with both domain services and infrastructure services.
5.  **Infrastructure Layer:** Handles external concerns such as database access (SQLAlchemy), AI model interactions (OpenAI, etc.), media processing (FFmpeg), and file storage.

## Core Architectural Patterns

### Service Layer Pattern
`JobService` abstracts all database operations, providing a clean interface for the API and Orchestrator to interact with the data model.

### Orchestrator Pattern
`JobOrchestrator` manages the complex, long-running workflow of extracting segments and highlights from a video. It ensures that stages are executed in the correct order and handles error reporting by updating the job's state.

### Strategy / Factory Pattern
The `provider_factory.py` uses a factory pattern to instantiate different AI providers (e.g., for transcription or classification) based on configuration, allowing for easy swapping of backend AI services.

### Repository Pattern (Implicit)
While not using a formal Repository class, the `JobService` combined with SQLAlchemy's `AsyncSession` effectively implements the repository pattern by abstracting data access.

### Background Worker Pattern
FastAPI's `BackgroundTasks` are used to offload the heavy lifting of the video pipeline to background execution, allowing the API to remain responsive.

## Data Flow: API to Worker

1.  **Job Submission:**
    *   The frontend POSTs a YouTube URL to `/api/v1/jobs/`.
    *   The API route calls `JobService.create_job()`, which persists a `VideoJob` record in the `pending` stage.
    *   The API route adds the `run_job_pipeline` task to FastAPI's `BackgroundTasks`.
    *   The API immediately returns the job object to the client.

2.  **Pipeline Execution (Background):**
    *   `run_job_pipeline` is executed by the background worker.
    *   It instantiates a `JobOrchestrator` with a fresh database session.
    *   `JobOrchestrator.run_pipeline()` is called.
    *   The orchestrator updates the job's `stage` field in the database at each step (e.g., `downloading`, `transcribing`, `classifying`).
    *   Each stage involves calling infrastructure services (e.g., `VideoIngestionService`) or domain services (e.g., `SermonDetectionService`).
    *   Intermediate results (transcripts, segments, highlights) are persisted to the database via the `JobService`.

3.  **Completion/Failure:**
    *   Upon successful completion, the orchestrator sets the job stage to `completed`.
    *   If an exception occurs, the orchestrator catches it, logs the error, and sets the job stage to `failed` with an accompanying error message.

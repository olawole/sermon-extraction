## Project: AI Sermon Extraction and Highlight Generation System

## Goal

Build an MVP web application that accepts a **YouTube URL** of a church service recording and produces:

* the **full sermon from the second service**
* the **sermon transcript**
* **subtitle files**
* **ranked highlight clips**
* optional **rendered vertical reels**

The app must include:

* a **backend API and processing pipeline**
* a **frontend UI** for submitting jobs, tracking progress, reviewing transcript/segments/highlights, and downloading outputs

---

# 1. Product Scope

## Input

* One YouTube URL
* Video is typically ~4 hours long
* Contains two services
* Each service may contain worship, prayer, testimony, sermon, and transitions

## Required output

* detect second service
* detect sermon within second service
* export full sermon video
* generate transcript and subtitle files
* generate highlight candidates from sermon
* optionally render vertical clips

## Frontend requirements

* create job from YouTube URL
* view job status and progress
* view service and sermon timestamps
* view transcript and segmented sections
* view highlight clips and metadata
* preview/download generated assets

---

# 2. Recommended Tech Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL or SQLite for MVP
* Pydantic
* yt-dlp
* FFmpeg

## AI / analysis

* transcription provider abstraction
* classifier abstraction
* highlight scorer abstraction

## Frontend

* React
* TypeScript
* Vite
* React Query
* Ant Design
* styled-components

That frontend stack matches your usual preference and will be faster to work with.

---

# 3. High-Level Architecture

## Backend modules

* API layer
* Job orchestration layer
* YouTube ingestion service
* Media processing service
* Transcription service
* Section classification service
* Service boundary detection service
* Sermon detection service
* Sermon export service
* Highlight generation service
* Clip rendering service

## Frontend modules

* App shell / layout
* Job submission page
* Job details page
* Transcript viewer
* Segments timeline view
* Highlights review panel
* Asset download panel

---

# 4. Build Order

Build in this order:

1. Scaffold backend
2. Scaffold frontend
3. Define shared contracts
4. Implement job creation flow
5. Implement video download + audio extraction
6. Implement transcription
7. Implement section classification
8. Implement service boundary detection
9. Implement sermon detection
10. Implement sermon export
11. Implement highlight generation
12. Implement frontend job tracking
13. Implement transcript/segment UI
14. Implement highlights UI
15. Implement clip rendering
16. Add tests and documentation

Do not start with fancy UI before the backend pipeline works.

---

# 5. Copilot Prompting Strategy

Use Copilot in **small, targeted prompts**.
Do not ask it to build the whole app in one shot.

Use prompts like:

* “Create the FastAPI project structure with routers, services, repositories, and Pydantic schemas”
* “Implement the SQLAlchemy models for VideoJob, MediaAsset, TranscriptChunk, SectionSegment, ServiceSegment, SermonSegment, and HighlightClip”
* “Create a React page for job details using React Query and Ant Design”

Keep each prompt focused.

---

# 6. Phase 1 — Scaffold the backend

## Task 1.1 — Create backend project structure

Ask Copilot to create a Python FastAPI project with this structure:

```text
backend/
  app/
    api/
      routes/
      schemas/
    core/
      config.py
      logging.py
    domain/
      models/
      enums/
      services/
    infrastructure/
      db/
      storage/
      ai/
      media/
      youtube/
    workflows/
      orchestrators/
      jobs/
    workers/
    tests/
  requirements.txt
  README.md
```

## Prompt for Copilot

> Create a FastAPI backend project structure for an AI sermon extraction system. Use layered folders for api, domain, infrastructure, workflows, and tests. Add starter files for config, logging, database session management, and app startup.

---

## Task 1.2 — Add core backend dependencies

Install:

* fastapi
* uvicorn
* sqlalchemy
* pydantic
* pydantic-settings
* alembic
* httpx
* python-multipart
* psycopg2-binary or sqlite support
* pytest
* pytest-asyncio

## Prompt

> Add a requirements file for a FastAPI backend using SQLAlchemy, Alembic, Pydantic, pytest, and PostgreSQL support.

---

## Task 1.3 — Add configuration and app bootstrap

Implement:

* env-based settings
* DB connection config
* storage path config
* external tool path config
* AI provider config placeholders

## Prompt

> Implement a Pydantic settings module for FastAPI with environment variables for database URL, storage root, yt-dlp path, ffmpeg path, and AI provider settings. Also create the FastAPI app bootstrap with router registration and health endpoint.

---

# 7. Phase 2 — Scaffold the frontend

## Task 2.1 — Create frontend app

Use:

* React
* TypeScript
* Vite
* React Query
* Ant Design
* styled-components
* React Router

Suggested structure:

```text
frontend/
  src/
    app/
    components/
    features/
      jobs/
      transcript/
      segments/
      highlights/
      assets/
    hooks/
    lib/
    pages/
    routes/
    services/
    styles/
    types/
```

## Prompt

> Create a React + TypeScript + Vite application structure using React Router, React Query, Ant Design, and styled-components. Organize it into features for jobs, transcript, segments, highlights, and assets.

---

## Task 2.2 — Build app layout

Create:

* top navigation
* page container
* simple dashboard layout
* loading and empty states

## Prompt

> Build a clean application shell using Ant Design Layout and styled-components for a media processing dashboard. Add a top nav, content area, and reusable loading and empty state components.

---

# 8. Phase 3 — Define backend data model

## Task 3.1 — Create enums

Create enums for:

* JobStage
* AssetType
* SectionLabel
* HighlightStatus

## Prompt

> Create Python enums for job stages, media asset types, section labels, and highlight clip status for a sermon extraction backend.

---

## Task 3.2 — Create SQLAlchemy models

Required models:

* VideoJob
* MediaAsset
* TranscriptChunk
* SectionSegment
* ServiceSegment
* SermonSegment
* HighlightClip

## Prompt

> Implement SQLAlchemy models for VideoJob, MediaAsset, TranscriptChunk, SectionSegment, ServiceSegment, SermonSegment, and HighlightClip with proper relationships and timestamp fields.

---

## Task 3.3 — Create database migrations

Use Alembic.

## Prompt

> Set up Alembic for the current SQLAlchemy models and generate an initial migration for the sermon extraction system schema.

---

# 9. Phase 4 — Define API contracts

## Task 4.1 — Create request/response schemas

Schemas needed:

* CreateJobRequest
* JobResponse
* JobDetailResponse
* TranscriptResponse
* SegmentsResponse
* HighlightsResponse
* AssetListResponse

## Prompt

> Create Pydantic schemas for creating a processing job and returning job details, transcript, section segments, sermon segment, highlights, and generated assets.

---

## Task 4.2 — Add API routes

Create routes:

* `POST /jobs`
* `GET /jobs/{jobId}`
* `GET /jobs/{jobId}/transcript`
* `GET /jobs/{jobId}/segments`
* `GET /jobs/{jobId}/highlights`
* `GET /jobs/{jobId}/assets`
* `POST /jobs/{jobId}/reprocess`

## Prompt

> Create FastAPI route files for job creation, job detail retrieval, transcript retrieval, segment retrieval, highlight retrieval, asset retrieval, and stage reprocessing.

---

# 10. Phase 5 — Implement job creation flow

## Task 5.1 — Create repository/service for jobs

Implement:

* create job
* update status
* fetch by id
* list assets/highlights/transcript

## Prompt

> Implement a repository and service layer for VideoJob that supports create, get by id, update status, and loading related assets, transcript chunks, segments, and highlights.

---

## Task 5.2 — Build frontend job submission page

Create a page with:

* YouTube URL input
* submit button
* validation
* success redirect to job details page

## Prompt

> Create a React page with Ant Design form components for submitting a YouTube URL to create a sermon extraction job. On success, navigate to the job details page.

---

## Task 5.3 — Build frontend service calls

Implement API client methods:

* createJob
* getJob
* getTranscript
* getSegments
* getHighlights
* getAssets

## Prompt

> Create a typed frontend API client using fetch or axios for job creation and retrieval endpoints. Add TypeScript types matching the backend responses.

---

# 11. Phase 6 — Implement video download and audio extraction

## Task 6.1 — YouTube ingestion module

Create a wrapper over yt-dlp.

## Prompt

> Implement a VideoIngestionService in Python that validates a YouTube URL, downloads the best source video using yt-dlp, stores it locally, and returns metadata including title, duration, and file path.

---

## Task 6.2 — FFmpeg audio extraction module

Implement:

* extract audio
* normalize audio
* save output paths

## Prompt

> Implement an AudioExtractionService that uses FFmpeg to extract audio from a source video, normalize it, and store the output audio file path for later transcription.

---

## Task 6.3 — Wire job processing stage

When a job is created:

* stage -> downloading
* download video
* stage -> audio_extracted after extraction succeeds

Use a background task or worker.

## Prompt

> Create a background job orchestrator that runs the first two stages of the pipeline: downloading the source video and extracting normalized audio, while updating the job status after each successful stage.

---

## Task 6.4 — Frontend job status card

Show:

* title
* stage
* created date
* error if failed
* duration if known

## Prompt

> Build a React job status card using Ant Design that displays title, current stage, created date, duration, and any error message.

---

# 12. Phase 7 — Implement transcription

## Task 7.1 — Transcription provider abstraction

Define interface:

* input audio path
* output transcript chunks

## Prompt

> Create a transcription provider abstraction in Python that takes an audio file path and returns timestamped transcript chunks including start time, end time, text, confidence, and optional speaker id.

---

## Task 7.2 — Fake provider for development

Add a mock provider first so the rest of the pipeline can move fast.

## Prompt

> Implement a fake transcription provider that returns deterministic transcript chunks from fixture JSON data for local development and testing.

---

## Task 7.3 — Persist transcript chunks

Store transcript chunks in DB.

## Prompt

> Implement transcript persistence logic that stores ordered transcript chunks for a job in the database and supports querying them by job id.

---

## Task 7.4 — Frontend transcript viewer

Build a transcript view with:

* timestamp
* speaker label if available
* text
* scrollable container

## Prompt

> Create a React transcript viewer component with a scrollable list of timestamped transcript chunks. Show speaker labels when available and format timestamps clearly.

---

# 13. Phase 8 — Implement section classification

## Task 8.1 — Transcript windowing

Group transcript chunks into windows for classification.

## Prompt

> Implement a transcript windowing service that groups transcript chunks into overlapping or fixed semantic windows suitable for section classification.

---

## Task 8.2 — Raw section classifier

Return labels:

* praise_worship
* prayer
* testimony
* announcements
* sermon
* transition
* other

## Prompt

> Implement a section classification service that classifies transcript windows into praise_worship, prayer, testimony, announcements, sermon, transition, or other. Make the classifier pluggable so it can use a mock or AI-backed implementation.

---

## Task 8.3 — Segment smoothing and merging

Convert noisy window labels into clean segments.

## Prompt

> Implement deterministic post-processing that smooths noisy section labels, merges adjacent windows with the same label, removes tiny low-confidence fragments, and returns clean section segments.

---

## Task 8.4 — Frontend section segment table

Show:

* label
* start
* end
* confidence
* dominant speaker

## Prompt

> Build a React table for section segments using Ant Design. Include label, start time, end time, duration, confidence, and dominant speaker columns.

---

# 14. Phase 9 — Implement second service detection

## Task 9.1 — Service boundary detector

Use segments + transcript cues to detect second service.

## Prompt

> Implement a ServiceBoundaryDetectionService that identifies service 1 and service 2 using classified section segments, timeline patterns, and transcript cues rather than assuming the second half of the video.

---

## Task 9.2 — Persist service segments

Save service 1 and service 2 boundaries.

## Prompt

> Add persistence for service boundary detection results, storing service number, start time, end time, and confidence.

---

## Task 9.3 — Frontend service summary panel

Show detected service ranges.

## Prompt

> Build a React summary panel that displays detected service ranges and confidence scores for service 1 and service 2.

---

# 15. Phase 10 — Implement sermon detection

## Task 10.1 — Sermon detector

Use service 2 range only.

## Prompt

> Implement a SermonDetectionService that searches only inside the detected second service, finds sermon-like section segments, merges adjacent sermon blocks, validates the best candidate, and returns sermon start, end, dominant speaker, and confidence.

---

## Task 10.2 — Persist sermon segment

Store sermon detection result.

## Prompt

> Implement persistence for detected sermon segment metadata including service number, start time, end time, dominant speaker id, confidence, and approval status.

---

## Task 10.3 — Frontend sermon summary card

Show:

* sermon start
* sermon end
* duration
* confidence
* dominant speaker

## Prompt

> Build a React sermon summary card using Ant Design Descriptions to show start time, end time, duration, confidence, and dominant speaker.

---

# 16. Phase 11 — Implement sermon export

## Task 11.1 — Cut sermon video

Use FFmpeg to trim exact range.

## Prompt

> Implement a VideoCutService that cuts the detected sermon range from the source video using FFmpeg and stores the output sermon video as a media asset.

---

## Task 11.2 — Generate subtitles

Produce sermon `.srt` and `.vtt` aligned to sermon timestamps.

## Prompt

> Implement a subtitle generation service that converts sermon transcript chunks into SRT and VTT subtitle files with sermon-relative timestamps.

---

## Task 11.3 — Asset retrieval endpoint

Return sermon video and subtitle assets.

## Prompt

> Implement the asset retrieval API so the frontend can list generated sermon video, audio, transcript, and subtitle files for a job.

---

## Task 11.4 — Frontend asset panel

Show downloadable assets.

## Prompt

> Create a React asset panel that lists generated files with asset type, format, duration, and download link.

---

# 17. Phase 12 — Implement highlight generation

## Task 12.1 — Candidate generator

Create natural short clip windows inside sermon only.

## Prompt

> Implement a highlight candidate generator that takes the sermon transcript and sermon boundaries and creates clip candidates using sentence, pause, and rhetorical boundaries. Target durations of 15–30, 30–45, and 45–60 seconds.

---

## Task 12.2 — Highlight scoring

Score candidates for catchiness.

## Prompt

> Implement a highlight scoring service that ranks clip candidates based on hook strength, standalone clarity, emotional or spiritual intensity, memorable phrasing, subtitle readability, and context independence. Return a score, category, title, hook text, transcript, and reasons.

---

## Task 12.3 — Persist highlight clips

Store all generated highlight metadata.

## Prompt

> Add persistence for generated highlight clips including timestamps, score, category, title, hook text, transcript, reasons, and status.

---

## Task 12.4 — Frontend highlights list

Show:

* title
* score
* category
* duration
* timestamps
* reasons
* transcript snippet

## Prompt

> Build a React highlights list using Ant Design cards or table rows to display title, score, category, duration, timestamps, reasons, and transcript preview for generated highlight clips.

---

# 18. Phase 13 — Add highlight preview and review UI

## Task 13.1 — Highlight detail drawer or modal

Allow click to inspect full highlight details.

## Prompt

> Add a React drawer or modal that shows detailed highlight metadata including transcript, score breakdown, reasons, and clip timestamps.

---

## Task 13.2 — Approve/reject actions

Add basic review actions.

## Prompt

> Add approve and reject actions for highlight clips in the frontend and implement corresponding backend endpoints to update highlight status.

---

## Task 13.3 — Timeline-style UI improvement

Optional but useful.

## Prompt

> Build a simple horizontal timeline visualization showing section segments, the detected sermon range, and highlight clip positions within the sermon.

---

# 19. Phase 14 — Implement clip rendering

## Task 14.1 — Clip renderer

Render vertical 9:16 clips.

## Prompt

> Implement a ClipRenderService that cuts a highlight clip from the sermon or source video, formats it as a 9:16 vertical video, burns in subtitles, and optionally overlays title text.

---

## Task 14.2 — Render endpoint

Trigger rendering for one or all approved clips.

## Prompt

> Implement backend endpoints to render a single highlight clip or all approved highlight clips for a job.

---

## Task 14.3 — Frontend render controls

Add buttons to render clips.

## Prompt

> Add frontend controls to render individual highlight clips and display render progress or result asset links.

---

# 20. Phase 15 — Build main frontend pages

You should end up with these pages:

## Page 1 — Job submission page

Features:

* YouTube URL form
* submit button
* validation
* recent jobs optional later

## Page 2 — Job details page

Sections:

* job status header
* service summary
* sermon summary
* asset panel
* tabs for transcript, segments, highlights

## Suggested prompt

> Build a JobDetailsPage in React that loads job details, transcript, segments, highlights, and assets using React Query. Use Ant Design Tabs for Transcript, Segments, Highlights, and Assets.

---

# 21. Suggested frontend component list

Create these reusable components:

* `JobCreateForm`
* `JobStatusCard`
* `ServiceSummaryCard`
* `SermonSummaryCard`
* `TranscriptViewer`
* `SegmentsTable`
* `HighlightsList`
* `HighlightDetailsDrawer`
* `AssetListPanel`
* `TimelineView`

Prompt Copilot one component at a time.

---

# 22. State management approach

Use **React Query** for all server state.

Avoid adding Redux for MVP.

Use:

* `useCreateJobMutation`
* `useJobQuery`
* `useTranscriptQuery`
* `useSegmentsQuery`
* `useHighlightsQuery`
* `useAssetsQuery`

## Prompt

> Create React Query hooks for creating jobs and fetching job details, transcript, segments, highlights, and assets from the backend API.

---

# 23. Styling guidance for frontend

Use:

* Ant Design for layout, cards, tables, tabs, form controls, buttons
* styled-components for page-specific polish and spacing
* keep UI clean, readable, admin-dashboard style

Do not build an overdesigned marketing UI.

---

# 24. Phase 16 — Testing

## Backend unit tests

Write tests for:

* transcript windowing
* segment merging
* service detection
* sermon detection
* highlight scoring
* subtitle generation

## Backend integration tests

Write tests for:

* create job endpoint
* pipeline stage progression with fake providers
* transcript retrieval
* segment retrieval
* highlight retrieval

## Frontend tests

Add a few focused tests:

* job form submission
* job details rendering
* transcript viewer rendering
* highlights list rendering

## Prompt

> Create pytest unit tests for sermon detection, service boundary detection, section segment smoothing, and highlight scoring using fixture transcript data.

And:

> Create React component tests for the job submission form, transcript viewer, and highlights list using Testing Library.

---

# 25. Phase 17 — Developer experience and docs

## Backend docs

Add:

* `README.md`
* local setup instructions
* `.env.example`
* FFmpeg and yt-dlp setup notes
* API overview

## Frontend docs

Add:

* startup instructions
* backend API base URL config
* local dev notes

## Architecture docs

Add:

* pipeline stages
* domain models
* data flow
* assumptions
* future improvements

## Prompt

> Write a project README that explains how to run the backend and frontend locally, required environment variables, external dependencies like FFmpeg and yt-dlp, and the overall processing workflow.

---

# 26. Recommended implementation sequence for you

If I were structuring the actual build sessions, I’d do it like this:

## Session 1

* scaffold backend
* scaffold frontend
* define models and schemas
* create job form and job endpoint

## Session 2

* implement download and audio extraction
* show live job status on frontend

## Session 3

* implement transcription with fake provider first
* render transcript in frontend

## Session 4

* implement section classification and segment UI

## Session 5

* implement second service detection and sermon detection
* show service/sermon summaries in frontend

## Session 6

* implement sermon export and asset panel

## Session 7

* implement highlight generation and highlights UI

## Session 8

* implement rendering and review actions

## Session 9

* tighten tests, cleanup, docs

That sequence keeps momentum and stops Copilot from dragging the architecture into chaos.

---

# 27. Guardrails to give Copilot

Use these rules in your prompts:

* Do not put all business logic in route handlers
* Do not collapse everything into one service file
* Do not hardcode provider-specific logic without an interface
* Do not assume second service equals second half of the video
* Do not generate highlights from the entire recording
* Only generate highlights from the detected sermon
* Persist intermediate outputs
* Keep code complete and production-lean
* Do not leave TODO placeholders for core features

---

# 28. One master instruction block for Copilot

You can paste this at the start of your build session:

> Build an MVP full-stack application for AI-powered sermon extraction and highlight generation. The backend must use Python and FastAPI with a modular layered structure. The frontend must use React, TypeScript, React Query, Ant Design, and styled-components. The system must accept a YouTube URL, download the source video, extract audio, transcribe it, classify sections, detect the second service, detect the sermon within the second service, export the full sermon, generate ranked highlight clips from the sermon only, and expose results through API endpoints. The frontend must allow job submission, job tracking, transcript viewing, section viewing, sermon summary viewing, highlight review, and asset download. Keep the design modular, rerunnable, testable, and production-lean. Do not over-engineer the MVP.

---

# 29. Best next move

Your smartest move is to build with a **fake transcription/classification provider first**, get the full backend/frontend flow working end to end, then swap in real AI providers.

That way you’re not blocked by model integration while building the product shape.

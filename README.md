# Sermon Extraction

An AI-powered web application that accepts a YouTube URL of a church service recording and produces the full sermon from the second service, a sermon transcript, subtitle files, and ranked highlight clips.

## Overview

The system consists of two parts:

- **Backend** — a Python FastAPI application that handles job creation, video downloading, transcription, section classification, sermon detection, and asset generation.
- **Frontend** — a React + TypeScript + Vite application for submitting jobs, tracking progress, and reviewing transcripts, segments, highlights, and downloadable assets.

---

## Prerequisites

Install the following tools before setting up the project:

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| npm | 9+ | Frontend package manager |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | latest | YouTube video downloader |
| [FFmpeg](https://ffmpeg.org/) | 6+ | Video/audio processing |

**Install yt-dlp:**
```bash
pip install yt-dlp
# or
brew install yt-dlp   # macOS
```

**Install FFmpeg:**
```bash
brew install ffmpeg   # macOS
sudo apt install ffmpeg  # Ubuntu/Debian
```

---

## Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Copy the environment file and edit as needed
cp .env.example .env
```

### Environment Variables

Edit `backend/.env` to configure the backend. The available settings are:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./sermon_extraction.db` | Database connection string |
| `STORAGE_ROOT` | `./storage` | Directory for downloaded videos and generated assets |
| `YTDLP_PATH` | `yt-dlp` | Path to the `yt-dlp` executable |
| `FFMPEG_PATH` | `ffmpeg` | Path to the `ffmpeg` executable |
| `AI_PROVIDER` | `fake` | AI provider for analysis (`fake` uses stub responses for development) |
| `TRANSCRIPTION_PROVIDER` | `fake` | Transcription provider (`fake` uses stub responses) |
| `CLASSIFICATION_PROVIDER` | `fake` | Classification provider (`fake` uses stub responses) |
| `DEBUG` | `false` | Enable debug logging |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins |

### Run the Backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive API docs are at `http://localhost:8000/docs`.

### Run Backend Tests

```bash
cd backend
source .venv/bin/activate
pytest app/tests/ -v --tb=short
```

---

## Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### Run the Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`.

> **Note:** Make sure the backend is running at `http://localhost:8000` before using the frontend.

### Other Frontend Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start the development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview the production build |
| `npm run lint` | Run ESLint |
| `npm test` | Run tests with Vitest |

---

## Running the Full System

To run the complete application, start both the backend and frontend in separate terminals:

**Terminal 1 — Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Then open `http://localhost:5173` in your browser.

---

## Project Structure

```
sermon-extraction/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes and schemas
│   │   ├── core/         # Configuration and logging
│   │   ├── domain/       # Models, enums, and domain services
│   │   ├── infrastructure/ # DB, storage, AI, media, and YouTube integrations
│   │   ├── workflows/    # Job orchestration
│   │   ├── workers/      # Background workers
│   │   └── tests/        # Backend tests
│   ├── alembic/          # Database migrations
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── components/   # Shared UI components
    │   ├── features/     # Feature modules (jobs, transcript, segments, highlights)
    │   ├── pages/        # Page components
    │   ├── services/     # API client
    │   ├── hooks/        # Custom React hooks
    │   ├── lib/          # Utilities
    │   └── types/        # TypeScript types
    └── package.json
```
# Sermon Extraction Backend

FastAPI backend for AI-powered sermon extraction from church service videos.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

## Testing

```bash
pytest app/tests/ -v --tb=short
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./sermon_extraction.db` | Database connection URL |
| `STORAGE_ROOT` | `./storage` | Root directory for stored files |
| `YTDLP_PATH` | `yt-dlp` | Path to the yt-dlp binary |
| `FFMPEG_PATH` | `ffmpeg` | Path to the ffmpeg binary |
| `AI_PROVIDER` | `fake` | Global AI provider override |
| `TRANSCRIPTION_PROVIDER` | `fake` | Transcription provider. Valid values: `fake`, `whisper` |
| `CLASSIFICATION_PROVIDER` | `fake` | Classification provider. Valid values: `fake`, `openai` |
| `OPENAI_API_KEY` | *(empty)* | OpenAI API key (required when using `whisper` or `openai` providers) |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI chat model used for section classification |
| `WHISPER_MODEL` | `whisper-1` | OpenAI Whisper model used for transcription |
| `DEBUG` | `false` | Enable debug mode |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins |

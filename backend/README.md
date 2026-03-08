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

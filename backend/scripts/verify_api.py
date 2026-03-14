from __future__ import annotations
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to sys.path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from app.infrastructure.ai.classification.openai_classifier import OpenAISectionClassifier
from app.infrastructure.ai.classification.base import ClassificationWindow
from app.infrastructure.ai.transcription.whisper_provider import WhisperTranscriptionProvider
from app.core.config import settings

async def verify_api(api_key: str):
    print(f"Verifying API with key: {api_key[:8]}...")
    
    # Temporarily override settings
    settings.openai_api_key = api_key
    
    # 1. Verify Classification (real connectivity)
    print("\n--- Verifying Classification ---")
    classifier = OpenAISectionClassifier()
    windows = [
        ClassificationWindow(
            start_seconds=0.0, 
            end_seconds=30.0, 
            text="Welcome to our Sunday service! Let's start with a prayer."
        ),
        ClassificationWindow(
            start_seconds=30.0, 
            end_seconds=60.0, 
            text="The sermon today is about the importance of kindness, based on various scriptures."
        )
    ]
    try:
        results = await classifier.classify(windows)
        for i, res in enumerate(results):
            print(f"Window {i}: {res.label.value} (confidence: {res.confidence:.2f})")
        print("Classification connectivity verified.")
    except Exception as e:
        print(f"Classification failed: {e}")

    # 2. Verify Transcription (if an audio file is provided)
    audio_path = os.environ.get("VERIFY_AUDIO_PATH")
    if audio_path and os.path.exists(audio_path):
        print(f"\n--- Verifying Transcription with {audio_path} ---")
        provider = WhisperTranscriptionProvider()
        try:
            chunks = await provider.transcribe(audio_path)
            print(f"Successfully transcribed {len(chunks)} chunks.")
            if chunks:
                print(f"First chunk text: {chunks[0].text}")
            print("Transcription connectivity verified.")
        except Exception as e:
            print(f"Transcription failed: {e}")
    else:
        print("\n--- Skipping Transcription (no VERIFY_AUDIO_PATH provided) ---")

if __name__ == "__main__":
    # Look for .env in current and parent dirs
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    if not api_key:
        print("Error: Provide OPENAI_API_KEY as env var or as first argument.")
        sys.exit(1)
    
    asyncio.run(verify_api(api_key))

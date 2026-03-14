from __future__ import annotations
from app.infrastructure.ai.transcription.base import TranscriptionProvider
from app.infrastructure.ai.classification.base import SectionClassifier


def get_transcription_provider(provider_name: str) -> TranscriptionProvider:
    from app.core.config import settings
    name = provider_name.lower().strip()
    if name == "fake":
        from app.infrastructure.ai.transcription.fake_provider import FakeTranscriptionProvider
        return FakeTranscriptionProvider()
    if name in ("openai", "whisper"):
        from app.infrastructure.ai.transcription.whisper_provider import WhisperTranscriptionProvider
        return WhisperTranscriptionProvider()
    if name == "deepgram":
        from app.infrastructure.ai.transcription.deepgram_provider import DeepgramTranscriptionProvider
        return DeepgramTranscriptionProvider(api_key=settings.deepgram_api_key)
    raise ValueError(
        f"Unknown transcription provider: '{provider_name}'. "
        "Valid options are: 'fake', 'whisper', 'openai', 'deepgram'."
    )


def get_classification_provider(provider_name: str) -> SectionClassifier:
    from app.core.config import settings
    name = provider_name.lower().strip()
    if name == "fake":
        from app.infrastructure.ai.classification.fake_classifier import FakeSectionClassifier
        return FakeSectionClassifier()
    if name == "openai":
        from app.infrastructure.ai.classification.openai_classifier import OpenAISectionClassifier
        return OpenAISectionClassifier()
    if name == "anthropic":
        from app.infrastructure.ai.classification.anthropic_classifier import AnthropicSectionClassifier
        return AnthropicSectionClassifier(api_key=settings.anthropic_api_key)
    raise ValueError(
        f"Unknown classification provider: '{provider_name}'. "
        "Valid options are: 'fake', 'openai', 'anthropic'."
    )

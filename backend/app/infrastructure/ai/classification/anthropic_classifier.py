from __future__ import annotations
import logging
from app.infrastructure.ai.classification.base import SectionClassifier, ClassificationWindow, ClassificationResult
from app.domain.enums.enums import SectionLabel

logger = logging.getLogger(__name__)


class AnthropicSectionClassifier(SectionClassifier):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def classify(self, windows: list[ClassificationWindow]) -> list[ClassificationResult]:
        logger.info(f"AnthropicSectionClassifier: classifying {len(windows)} windows (STUB)")
        # This is a stub that currently returns nothing or could return fake data.
        # For now, we return an empty list as it's a mock.
        return []

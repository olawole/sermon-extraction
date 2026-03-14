from __future__ import annotations
import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.infrastructure.ai.classification.openai_classifier import OpenAISectionClassifier
from app.infrastructure.ai.classification.base import ClassificationWindow
from app.domain.enums.enums import SectionLabel

@pytest.mark.asyncio
async def test_openai_classifier_batching():
    classifier = OpenAISectionClassifier()
    # Mock batch size is 20 in openai_classifier.py
    windows = [
        ClassificationWindow(start_seconds=i*10, end_seconds=(i+1)*10, text=f"text {i}")
        for i in range(25)
    ]
    
    # First batch (20)
    mock_response_1 = MagicMock()
    mock_response_1.choices = [
        MagicMock(message=MagicMock(content=json.dumps([
            {"label": "sermon", "confidence": 0.9} for _ in range(20)
        ])))
    ]
    
    # Second batch (5)
    mock_response_2 = MagicMock()
    mock_response_2.choices = [
        MagicMock(message=MagicMock(content=json.dumps([
            {"label": "praise_worship", "confidence": 0.8} for _ in range(5)
        ])))
    ]
    
    classifier._client.chat.completions.create = AsyncMock()
    classifier._client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]
    
    results = await classifier.classify(windows)
    
    assert len(results) == 25
    assert classifier._client.chat.completions.create.call_count == 2
    assert results[0].label == SectionLabel.sermon
    assert results[20].label == SectionLabel.praise_worship

@pytest.mark.asyncio
async def test_openai_classifier_parsing_formats():
    classifier = OpenAISectionClassifier()
    window = ClassificationWindow(start_seconds=0, end_seconds=10, text="test")
    
    formats = [
        # Bare array
        json.dumps([{"label": "sermon", "confidence": 0.9}]),
        # Wrapped in "results"
        json.dumps({"results": [{"label": "sermon", "confidence": 0.9}]}),
        # Wrapped in "classifications"
        json.dumps({"classifications": [{"label": "sermon", "confidence": 0.9}]}),
        # Wrapped in some other key
        json.dumps({"data": [{"label": "sermon", "confidence": 0.9}]}),
    ]
    
    for fmt in formats:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=fmt))]
        classifier._client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        results = await classifier.classify([window])
        assert results[0].label == SectionLabel.sermon
        assert results[0].confidence == 0.9

@pytest.mark.asyncio
async def test_openai_classifier_fallback_on_error():
    classifier = OpenAISectionClassifier()
    window = ClassificationWindow(start_seconds=0, end_seconds=10, text="test")
    
    # Empty response or invalid JSON
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="{}"))]
    classifier._client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    results = await classifier.classify([window])
    assert results[0].label == SectionLabel.other
    assert results[0].confidence == 0.5

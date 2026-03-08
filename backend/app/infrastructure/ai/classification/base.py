from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from app.domain.enums.enums import SectionLabel


@dataclass
class ClassificationWindow:
    start_seconds: float
    end_seconds: float
    text: str
    chunk_indices: list[int] = field(default_factory=list)


@dataclass
class ClassificationResult:
    start_seconds: float
    end_seconds: float
    label: SectionLabel
    confidence: float


class SectionClassifier(ABC):
    @abstractmethod
    async def classify(self, windows: list[ClassificationWindow]) -> list[ClassificationResult]: ...

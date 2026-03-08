from __future__ import annotations
from abc import ABC, abstractmethod
from app.domain.services.highlight_generation import HighlightCandidate


class HighlightScorer(ABC):
    @abstractmethod
    def score(self, candidate: HighlightCandidate) -> float: ...

from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional, List
from app.domain.enums.enums import SectionLabel

logger = logging.getLogger(__name__)


@dataclass
class SermonDetectionResult:
    service_number: int
    start_seconds: float
    end_seconds: float
    dominant_speaker: Optional[str]
    confidence: float


class SermonDetectionService:
    def detect(
        self,
        section_segments: list,
        service_boundaries: list,
    ) -> Optional[SermonDetectionResult]:
        """
        Detects the best sermon candidate across all service boundaries.
        
        - Merges adjacent sermon segments if the gap is < 120 seconds.
        - Filters candidates by duration: 15 to 70 minutes.
        - Chooses the candidate with the highest average confidence.
        """
        all_candidates: List[SermonDetectionResult] = []

        for boundary in service_boundaries:
            # Find all sermon segments within this boundary
            sermon_segments = [
                s for s in section_segments
                if (s.label == SectionLabel.sermon.value or s.label == "sermon")
                and s.end_seconds > boundary.start_seconds
                and s.start_seconds < boundary.end_seconds
            ]

            if not sermon_segments:
                continue

            sermon_segments.sort(key=lambda s: s.start_seconds)

            # Merge adjacent sermon segments
            merged_blocks = []
            if sermon_segments:
                current_block = [sermon_segments[0]]
                for i in range(1, len(sermon_segments)):
                    prev = sermon_segments[i - 1]
                    curr = sermon_segments[i]
                    
                    gap = curr.start_seconds - prev.end_seconds
                    if gap < 120.0:
                        current_block.append(curr)
                    else:
                        merged_blocks.append(current_block)
                        current_block = [curr]
                merged_blocks.append(current_block)

            # Evaluate each merged block as a candidate
            for block in merged_blocks:
                start = max(block[0].start_seconds, boundary.start_seconds)
                end = min(block[-1].end_seconds, boundary.end_seconds)
                duration = end - start

                # Filter by duration: 15 to 70 minutes
                if duration < 900.0 or duration > 4200.0:
                    logger.debug(f"Sermon candidate rejected due to duration: {duration:.1f}s")
                    continue

                avg_confidence = sum(
                    getattr(s, "confidence", None) or 0.8 for s in block
                ) / len(block)

                # Find dominant speaker (most frequent in the block)
                speakers = [getattr(s, "dominant_speaker", None) for s in block if getattr(s, "dominant_speaker", None)]
                dominant_speaker = max(set(speakers), key=speakers.count) if speakers else None

                all_candidates.append(SermonDetectionResult(
                    service_number=boundary.service_number,
                    start_seconds=start,
                    end_seconds=end,
                    dominant_speaker=dominant_speaker,
                    confidence=avg_confidence,
                ))

        if not all_candidates:
            return None

        # Choose the candidate with the highest confidence
        # If confidence is tied, choose the longest duration
        all_candidates.sort(key=lambda x: (x.confidence, x.end_seconds - x.start_seconds), reverse=True)
        
        return all_candidates[0]

import pytest
from app.infrastructure.ai.scoring.highlight_scorer import RuleBasedHighlightScorer
from app.domain.services.highlight_generation import HighlightCandidate


def make_candidate(start, end, text):
    return HighlightCandidate(
        start_seconds=start,
        end_seconds=end,
        transcript=text,
        hook_text=text[:50],
        title="Test",
    )


def test_score_between_zero_and_one():
    scorer = RuleBasedHighlightScorer()
    candidate = make_candidate(0, 45, "God loves you and His grace is sufficient for all things. Believe in faith.")
    score = scorer.score(candidate)
    assert 0.0 <= score <= 1.0


def test_score_zero_duration():
    scorer = RuleBasedHighlightScorer()
    candidate = make_candidate(100, 100, "test")
    assert scorer.score(candidate) == 0.0


def test_longer_text_scores_higher():
    scorer = RuleBasedHighlightScorer()
    short = make_candidate(0, 45, "God.")
    long_text = make_candidate(0, 45, "God loves you and His grace is sufficient for all things. Faith and love. Jesus Christ our Savior.")
    assert scorer.score(long_text) > scorer.score(short)

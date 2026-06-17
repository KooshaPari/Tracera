"""Unit tests for embedding/VLM scoring strategies (``FR-TRC-020``).

Verifies that embedding-based scorers (SentenceTransformer, SigLIP, VLM blind-vs-intent)
satisfy the ``ScorerPort`` protocol contract. These tests scaffold the acceptance criteria
for Pillar A Phase 1 (text embeddings) and Pillar C Phase 2 (VLM scoring).

Each embedding/VLM strategy must:
1. Implement the ``ScorerPort`` protocol (``name`` property + ``score()`` method).
2. Return scores normalized to ``[0.0, 1.0]``.
3. Accept string inputs without raising TypeError.
4. Return a ``ScoreResult`` with populated ``score``, ``rationale``, and ``strategy``.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from unittest.mock import MagicMock, patch

import pytest

from tracertm.ports.scorer import ScorerPort, ScoreResult


class _MockEmbeddingScorer:
    """Stub embedding scorer for testing ScorerPort protocol satisfaction.

    This is a minimal implementation that satisfies the ScorerPort protocol:
    it has a ``name`` property and a ``score(str, str) -> ScoreResult`` method.
    """

    name = "mock_embeddings"

    def score(self, requirement_text: str, artifact_text: str) -> ScoreResult:
        """Return a mock score based on text length overlap."""
        req_len = len(requirement_text)
        art_len = len(artifact_text)

        if req_len == 0 and art_len == 0:
            return ScoreResult(0.0, "both inputs empty", self.name)

        max_len = max(req_len, art_len)
        min_len = min(req_len, art_len)
        overlap_ratio = min_len / max_len if max_len > 0 else 0.0

        return ScoreResult(
            score=round(overlap_ratio, 6),
            rationale=f"length-based overlap: {min_len}/{max_len}",
            strategy=self.name,
        )


class _ProtocolCheckScorer:
    """Scorer that only implements the protocol without full logic."""

    @property
    def name(self) -> str:
        return "protocol_check"

    def score(self, requirement_text: str, artifact_text: str) -> ScoreResult:
        return ScoreResult(
            score=0.5, rationale="protocol check scorer", strategy=self.name
        )


def test_scorer_port_protocol_has_score_method():
    """Verify ScorerPort protocol defines a ``score()`` callable."""
    # Inspect the ScorerPort protocol for the score method.
    assert hasattr(ScorerPort, "score")
    # The score method should be in the protocol's annotations or methods.
    assert callable(getattr(ScorerPort, "score", None))


def test_scorer_port_protocol_has_name_property():
    """Verify ScorerPort protocol defines a ``name`` property."""
    assert hasattr(ScorerPort, "name")


def test_mock_embedding_scorer_satisfies_port():
    """Verify that a stub embedding scorer passes isinstance/Protocol check.

    This confirms that any scorer implementing the protocol (name + score method)
    will be recognized as a ScorerPort at runtime.
    """
    scorer = _MockEmbeddingScorer()
    assert isinstance(scorer, ScorerPort)


def test_protocol_check_scorer_with_property_satisfies_port():
    """Verify that property-based ``name`` (not class attribute) satisfies protocol."""
    scorer = _ProtocolCheckScorer()
    assert isinstance(scorer, ScorerPort)


def test_scorer_returns_float_between_0_and_1():
    """Verify that ``score()`` returns a value in the valid range [0.0, 1.0]."""
    scorer = _MockEmbeddingScorer()

    # Test with some inputs
    result = scorer.score("requirement", "artifact")
    assert isinstance(result.score, float)
    assert 0.0 <= result.score <= 1.0


def test_scorer_returns_zero_on_empty_inputs():
    """Verify that ``score()`` returns 0.0 for empty inputs."""
    scorer = _MockEmbeddingScorer()
    result = scorer.score("", "")
    assert result.score == 0.0


def test_scorer_returns_one_on_identical_inputs():
    """Verify that ``score()`` returns 1.0 for identical inputs."""
    scorer = _MockEmbeddingScorer()
    result = scorer.score("identical text", "identical text")
    assert result.score == 1.0


def test_scorer_port_accepts_string_inputs():
    """Verify that ``score(str, str)`` does not raise TypeError on valid inputs."""
    scorer = _MockEmbeddingScorer()
    # Should not raise
    try:
        scorer.score("requirement text", "artifact text")
    except TypeError as e:
        pytest.fail(f"score() raised TypeError on valid string inputs: {e}")


def test_scorer_port_accepts_empty_string_inputs():
    """Verify that ``score()`` handles empty string inputs gracefully."""
    scorer = _MockEmbeddingScorer()
    result = scorer.score("", "")
    assert isinstance(result, ScoreResult)
    assert 0.0 <= result.score <= 1.0


def test_score_result_contains_rationale():
    """Verify that ScoreResult includes a human-readable rationale."""
    scorer = _MockEmbeddingScorer()
    result = scorer.score("requirement", "artifact")
    assert isinstance(result.rationale, str)
    assert len(result.rationale) > 0


def test_score_result_contains_strategy_name():
    """Verify that ScoreResult records which strategy produced the score."""
    scorer = _MockEmbeddingScorer()
    result = scorer.score("requirement", "artifact")
    assert result.strategy == scorer.name


def test_multiple_scorers_have_different_names():
    """Verify that different scorer strategies have distinct identifiers."""
    scorer1 = _MockEmbeddingScorer()
    scorer2 = _ProtocolCheckScorer()
    assert scorer1.name != scorer2.name


def test_scorer_name_is_stable():
    """Verify that a scorer's name does not change between calls."""
    scorer = _MockEmbeddingScorer()
    name1 = scorer.name
    name2 = scorer.name
    assert name1 == name2


def test_score_result_frozen_prevents_modification():
    """Verify that ScoreResult is immutable (dataclass frozen)."""
    result = ScoreResult(score=0.5, rationale="test", strategy="test_scorer")
    with pytest.raises(AttributeError):
        result.score = 0.7


def test_batch_scoring_pattern_accepts_scorer_port():
    """Verify that a generic batch scoring function accepts any ScorerPort.

    This demonstrates the strategy pattern: callers using ScorerPort can swap
    strategies without modification.
    """

    def batch_score(scorer: ScorerPort, pairs: list[tuple[str, str]]) -> list[float]:
        """Generic batch scoring function that works with any ScorerPort."""
        return [scorer.score(req, art).score for req, art in pairs]

    scorer = _MockEmbeddingScorer()
    pairs = [
        ("req1", "art1"),
        ("req2", "art2"),
        ("", ""),
    ]
    scores = batch_score(scorer, pairs)
    assert len(scores) == 3
    assert all(isinstance(s, float) and 0.0 <= s <= 1.0 for s in scores)


def test_scorer_port_duck_typing_with_mock():
    """Verify that unittest.mock can create a valid ScorerPort."""
    mock_scorer = MagicMock(spec=ScorerPort)
    mock_scorer.name = "mock_strategy"
    mock_scorer.score.return_value = ScoreResult(
        score=0.8, rationale="mocked", strategy="mock_strategy"
    )

    result = mock_scorer.score("requirement", "artifact")
    assert result.score == 0.8
    assert isinstance(mock_scorer, ScorerPort)


def test_scorer_consistency_across_calls():
    """Verify that a scorer returns consistent results for the same inputs."""
    scorer = _MockEmbeddingScorer()
    result1 = scorer.score("same requirement", "same artifact")
    result2 = scorer.score("same requirement", "same artifact")
    assert result1.score == result2.score
    assert result1.rationale == result2.rationale

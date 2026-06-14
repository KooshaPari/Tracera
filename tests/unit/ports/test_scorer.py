"""Unit tests for the pluggable agreement ``ScorerPort`` (``FR-TRC-019``)."""

from __future__ import annotations

import pytest

from tracertm.ports.scorer import (
    JaccardScorer,
    ScorerPort,
    ScoreResult,
)


def test_jaccard_satisfies_scorer_port_protocol():
    assert isinstance(JaccardScorer(), ScorerPort)


def test_identical_text_scores_one():
    r = JaccardScorer().score("user can log in", "user can log in")
    assert r.score == 1.0
    assert r.strategy == "jaccard"


def test_disjoint_text_scores_zero():
    r = JaccardScorer().score("alpha bravo", "charlie delta")
    assert r.score == 0.0
    assert "no shared tokens" in r.rationale


def test_partial_overlap_is_between_zero_and_one():
    r = JaccardScorer().score("user can log in securely", "user logs in")
    assert 0.0 < r.score < 1.0


def test_both_empty_scores_zero_without_error():
    r = JaccardScorer().score("", "")
    assert r.score == 0.0


def test_score_result_rejects_out_of_range():
    with pytest.raises(ValueError):
        ScoreResult(score=1.5, rationale="bad", strategy="x")


def test_callers_can_swap_strategy_without_changing_call_site():
    # Strategy pattern: any ScorerPort is interchangeable at the call site.
    def confidence(scorer: ScorerPort, a: str, b: str) -> float:
        return scorer.score(a, b).score

    assert confidence(JaccardScorer(), "trace link graph", "trace link graph") == 1.0

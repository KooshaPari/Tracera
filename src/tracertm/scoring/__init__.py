"""Pluggable agreement scoring strategies (``FR-TRC-020``).

Implements various scoring strategies that satisfy the :class:`ScorerPort` protocol.
Strategies include:

* :class:`JaccardScorer`     -- lexical overlap (dependency-free reference impl).
* :class:`TFIDFScorer`       -- TF-IDF cosine similarity (sklearn, with jaccard fallback).
* :class:`ScorerRegistry`    -- pluggable registry for registering and retrieving scorers.

Each scorer returns a normalized confidence in ``[0.0, 1.0]`` plus a human-readable rationale.
"""

from tracertm.scoring.jaccard_scorer import JaccardScorer
from tracertm.scoring.registry import ScorerRegistry
from tracertm.scoring.tfidf_scorer import TFIDFScorer

__all__ = [
    "JaccardScorer",
    "TFIDFScorer",
    "ScorerRegistry",
]

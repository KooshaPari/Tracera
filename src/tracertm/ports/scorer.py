"""Pluggable agreement ``ScorerPort`` (Pillar-A spine).

Implements ``FR-TRC-019`` (Pluggable Agreement Scorer Port). See
``docs/TRACERA_PLATFORM_RND.md`` §3.2.

The platform scores requirement<->artifact *agreement* in several places
(auto-linking, traceability confidence, blind-vs-intent verification). Today the
scoring is heuristic and baked into individual services. This port makes the
scoring **strategy** selectable at the call site without changing callers:

* :class:`JaccardScorer`     -- lexical overlap (dependency-free reference impl).

Only the dependency-free Jaccard strategy is implemented here; richer embedding /
VLM strategies may plug in behind the same :class:`ScorerPort` so callers never
change. Every scorer returns a normalized confidence in ``[0.0, 1.0]`` plus a
human-readable rationale (the acceptance criterion of ``FR-TRC-019``).

SentenceTransformerScorer (Gap #3) uses ``sentence-transformers`` for real
semantic scoring.  When the library is unavailable, a weighted-Jaccard fallback
ensures the port remains usable in dependency-free environments.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text or "")}


def _weighted_score(tokens_a: set[str], tokens_b: set[str]) -> float:
    """Weighted Jaccard scored as intersection-weight / max(a-weight, b-weight).

    Longer tokens receive proportionally more weight (``w = len / max_len``).
    Normalizing by ``max(|A|, |B|)`` instead of ``|A ∪ B|`` prevents
    artificially low scores when one document is much longer than the other.
    """
    if not tokens_a and not tokens_b:
        return 0.0
    all_tokens = tokens_a | tokens_b
    max_len = max((len(t) for t in all_tokens), default=1)
    inter = tokens_a & tokens_b
    w_inter = sum(len(t) / max_len for t in inter)
    w_a = sum(len(t) / max_len for t in tokens_a)
    w_b = sum(len(t) / max_len for t in tokens_b)
    denom = max(w_a, w_b)
    if denom == 0:
        return 0.0
    return w_inter / denom


@dataclass(frozen=True, slots=True)
class ScoreResult:
    """Normalized agreement score with provenance.

    Attributes:
        score: Confidence in ``[0.0, 1.0]``.
        rationale: Human-readable explanation of the score.
        strategy: Name of the scorer that produced this result.
    """

    score: float
    rationale: str
    strategy: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score must be in [0.0, 1.0], got {self.score}")


@runtime_checkable
class ScorerPort(Protocol):
    """Strategy interface for requirement<->artifact agreement scoring.

    Pillars A and C consume the *same* port; the concrete strategy is chosen at
    the call site (strategy pattern), satisfying ``FR-TRC-019``.
    """

    @property
    def name(self) -> str:
        """Stable identifier for this scoring strategy."""
        ...

    def score(self, requirement_text: str, artifact_text: str) -> ScoreResult:
        """Return a normalized agreement score in ``[0.0, 1.0]``."""
        ...

class JaccardScorer:
    """Lexical (Jaccard) agreement scorer -- the dependency-free reference impl.

    ``score = |tokens(req) ∩ tokens(art)| / |tokens(req) ∪ tokens(art)|``.

    This is the baseline strategy: it ships with zero extra dependencies so the
    spine is testable and usable immediately, while richer embedding/VLM
    strategies are added behind the same :class:`ScorerPort`.
    """

    name = "jaccard"

    def score(self, requirement_text: str, artifact_text: str) -> ScoreResult:
        req = _tokenize(requirement_text)
        art = _tokenize(artifact_text)
        if not req and not art:
            return ScoreResult(0.0, "both inputs empty", self.name)
        inter = req & art
        value = _weighted_score(req, art)
        rationale = (
            f"{len(inter)} shared tokens (weighted), {len(req)} req / {len(art)} art"
            if inter
            else f"no shared tokens ({len(req)} req, {len(art)} art)"
        )
        return ScoreResult(round(value, 6), rationale, self.name)


def _weighted_jaccard(text_a: str, text_b: str) -> float:
    """Module-level helper used as the fallback when sentence-transformers is
    unavailable."""
    return _weighted_score(_tokenize(text_a), _tokenize(text_b))


import threading
import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)


class SentenceTransformerScorer:
    """Semantic agreement scorer backed by ``sentence-transformers``.

    Uses cosine similarity between sentence embeddings as the agreement signal,
    yielding a ``[0.0, 1.0]`` normalized score (negative similarities clamped to
    0).  When ``sentence-transformers`` is not installed the class gracefully
    falls back to weighted Jaccard so the platform never breaks.

    Attributes:
        model_name: HuggingFace model identifier.
    """

    name = "sentence_transformer"

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._model = None
        self._lock = threading.Lock()
        self._fallback: Optional[JaccardScorer] = None

    def _get_model(self):
        if self._model is not None:
            return self._model
        with self._lock:
            if self._model is not None:
                return self._model
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self._model_name)
                logger.info(f"Loaded SentenceTransformer model: {self._model_name}")
            except ImportError:
                logger.warning("sentence_transformers not installed; falling back to JaccardScorer")
                self._fallback = JaccardScorer()
                self._model = None
        return self._model

    def score(self, requirement_text: str, artifact_text: str) -> ScoreResult:
        model = self._get_model()
        if model is None:
            value = self._fallback.score(requirement_text, artifact_text).score
            rationale = "sentence-transformers not installed; JaccardScorer fallback"
            return ScoreResult(round(value, 6), rationale, self.name)
        embeddings = model.encode([requirement_text, artifact_text])
        e0, e1 = embeddings[0], embeddings[1]
        norm0 = np.linalg.norm(e0)
        norm1 = np.linalg.norm(e1)
        if norm0 == 0 or norm1 == 0:
            value = 0.0
        else:
            value = float(np.clip(np.dot(e0, e1) / (norm0 * norm1), 0.0, 1.0))
        rationale = f"cosine similarity = {value:.6f} (model={self._model_name})"
        return ScoreResult(round(value, 6), rationale, self.name)

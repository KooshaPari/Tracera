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

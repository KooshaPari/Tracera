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

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


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


def _token_counts(text: str) -> Counter[str]:
    """Tokenize ``text`` into a lowercase term-frequency :class:`Counter`.

    Uses :class:`collections.Counter` so downstream scoring can leverage
    term frequencies (TF) instead of pure set membership. Returns an empty
    counter for ``None`` or empty input.
    """
    if not text:
        return Counter()
    return Counter(t.lower() for t in _TOKEN_RE.findall(text))


def _cosine(a: Counter[str], b: Counter[str]) -> float:
    """TF cosine similarity in ``[0.0, 1.0]``.

    Defined as ``dot(a, b) / (||a|| * ||b||)`` where the dot product and norms
    use term frequencies. Returns ``0.0`` when either side is empty.
    """
    if not a or not b:
        return 0.0
    if len(a) > len(b):
        a, b = b, a
    dot = sum(freq * b.get(term, 0) for term, freq in a.items())
    if dot == 0:
        return 0.0
    norm_a = math.sqrt(sum(f * f for f in a.values()))
    norm_b = math.sqrt(sum(f * f for f in b.values()))
    denom = norm_a * norm_b
    if denom == 0.0:
        return 0.0
    value = dot / denom
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def _weighted_jaccard(a: Counter[str], b: Counter[str]) -> float:
    """TF-weighted (a.k.a. "generalized") Jaccard in ``[0.0, 1.0]``.

    Defined as ``sum(min(a_t, b_t)) / sum(max(a_t, b_t))`` over all terms
    ``t``. Reduces to set-Jaccard when every count is 0 or 1, but rewards
    shared high-frequency terms rather than treating every distinct token
    equally. Returns ``0.0`` when both sides are empty.
    """
    if not a or not b:
        return 0.0
    if len(a) > len(b):
        a, b = b, a
    inter = 0
    for term, fa in a.items():
        fb = b.get(term, 0)
        inter += fa if fa < fb else fb
    union = sum(a.values()) + sum(b.values()) - inter
    if union == 0:
        return 0.0
    return inter / union


class JaccardScorer:
    """Weighted/normalized token-overlap agreement scorer.

    Public interface and method signature are unchanged from the original
    raw set-Jaccard implementation; the underlying math is upgraded to a
    term-frequency-aware score so that *important* (repeated) terms move the
    needle and the score is normalized against document length.

    The reported value is a hybrid of two normalized statistics:

    * **TF cosine** -- directional similarity, robust to length skew
      (``dot(a,b) / (||a|| * ||b||)``).
    * **Weighted (generalized) Jaccard** -- symmetric overlap that respects
      term frequencies (``sum(min) / sum(max)``).

    The final score is the arithmetic mean of the two, clamped to
    ``[0.0, 1.0]``, which correlates better with human agreement judgements
    than raw set-Jaccard (which collapses to a single bit per token and is
    dominated by stop-word-like filler).

    Still dependency-free -- uses only :mod:`collections.Counter` and
    :mod:`math` from the standard library -- so the spine remains testable
    without third-party packages.
    """

    name = "jaccard"

    def score(self, requirement_text: str, artifact_text: str) -> ScoreResult:
        req = _token_counts(requirement_text)
        art = _token_counts(artifact_text)
        if not req and not art:
            return ScoreResult(0.0, "both inputs empty", self.name)
        if not req or not art:
            return ScoreResult(
                0.0,
                f"one side empty (req_tokens={sum(req.values())}, "
                f"art_tokens={sum(art.values())})",
                self.name,
            )

        cosine = _cosine(req, art)
        wj = _weighted_jaccard(req, art)
        value = (cosine + wj) / 2.0
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0

        shared_terms = sorted(t for t in req if t in art)
        shared_distinct = len(shared_terms)
        shared_mass = sum(min(req[t], art[t]) for t in shared_terms)
        total_mass = sum(req.values()) + sum(art.values())
        shared_pct = (2 * shared_mass / total_mass * 100.0) if total_mass else 0.0

        sample = ", ".join(shared_terms[:8]) or "<none>"
        rationale = (
            f"weighted Jaccard={wj:.4f}, TF cosine={cosine:.4f}; "
            f"{shared_distinct} shared terms ({shared_mass}/{total_mass} "
            f"token-mass, {shared_pct:.1f}%) sample: {sample}"
        )
        return ScoreResult(round(value, 6), rationale, self.name)

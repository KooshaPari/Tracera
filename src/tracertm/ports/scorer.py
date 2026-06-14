"""Pluggable agreement ``ScorerPort`` (Pillar-A spine).

Implements ``FR-TRC-019`` (Pluggable Agreement Scorer Port). See
``docs/TRACERA_PLATFORM_RND.md`` §3.2.

The platform scores requirement<->artifact *agreement* in several places
(auto-linking, traceability confidence, blind-vs-intent verification). Today the
scoring is heuristic and baked into individual services. This port makes the
scoring **strategy** selectable at the call site without changing callers:

* :class:`JaccardScorer`     -- lexical overlap (dependency-free reference impl).
* ``SentenceTransformerScorer`` -- text embeddings (Pillar A, Phase 1).
* ``SigLIPScorer``           -- visual embeddings (Pillar C).
* VLM blind-vs-intent        -- "does the running code match the requirement?"
                                (Pillar C, Phase 2, ``FR-TRC-020``).

Only the dependency-free Jaccard strategy is implemented here; the embedding /
VLM strategies plug in behind the same :class:`ScorerPort` so callers never
change. Every scorer returns a normalized confidence in ``[0.0, 1.0]`` plus a
human-readable rationale (the acceptance criterion of ``FR-TRC-019``).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

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


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text or "")}


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
        union = req | art
        if not union:
            return ScoreResult(0.0, "no tokens", self.name)
        inter = req & art
        value = len(inter) / len(union)
        rationale = (
            f"{len(inter)} shared / {len(union)} total tokens"
            f" (shared: {', '.join(sorted(inter)[:8])})"
            if inter
            else "no shared tokens"
        )
        return ScoreResult(round(value, 6), rationale, self.name)


class SentenceTransformerScorer:
    """Text-embedding agreement scorer (Pillar A, Phase 1).

    Uses ``sentence-transformers`` when installed; otherwise falls back to
    :class:`JaccardScorer` with a ``[stub-ST]`` rationale prefix so callers
    can depend on the port without pulling ML deps in CI.
    """

    name = "sentence_transformer"

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._model: Any | None = None
        self._fallback = JaccardScorer()

    def _ensure_model(self) -> Any | None:
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            return None
        self._model = SentenceTransformer(self._model_name)
        return self._model

    def score(self, requirement_text: str, artifact_text: str) -> ScoreResult:
        model = self._ensure_model()
        if model is None:
            base = self._fallback.score(requirement_text, artifact_text)
            return ScoreResult(
                base.score,
                f"[stub-ST] {base.rationale} (install sentence-transformers for embeddings)",
                self.name,
            )
        import numpy as np

        emb = model.encode([requirement_text or "", artifact_text or ""])
        denom = float(np.linalg.norm(emb[0]) * np.linalg.norm(emb[1]))
        if denom == 0.0:
            return ScoreResult(0.0, "empty embedding", self.name)
        sim = float(np.dot(emb[0], emb[1]) / denom)
        clamped = max(0.0, min(1.0, (sim + 1.0) / 2.0))
        return ScoreResult(
            round(clamped, 6),
            f"cosine similarity via {self._model_name}",
            self.name,
        )


class SigLIPScorer:
    """Visual-embedding agreement scorer stub (Pillar C).

    Production use requires ``transformers`` + a SigLIP checkpoint. Until
    those deps are present the scorer delegates to :class:`JaccardScorer`
    over any text captions supplied alongside image paths.
    """

    name = "siglip"

    def __init__(self, model_id: str = "google/siglip-base-patch16-224") -> None:
        self._model_id = model_id
        self._fallback = JaccardScorer()

    def score(self, requirement_text: str, artifact_text: str) -> ScoreResult:
        try:
            import transformers  # noqa: F401
        except ImportError:
            base = self._fallback.score(requirement_text, artifact_text)
            return ScoreResult(
                base.score,
                f"[stub-SigLIP] {base.rationale} (install transformers for SigLIP)",
                self.name,
            )
        base = self._fallback.score(requirement_text, artifact_text)
        return ScoreResult(
            base.score,
            f"[siglip-pending] {base.rationale} (model={self._model_id})",
            self.name,
        )

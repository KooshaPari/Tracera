"""Lexical (Jaccard) agreement scorer -- dependency-free reference implementation.

Implements the Jaccard similarity coefficient for requirement<->artifact agreement scoring.
This is the baseline strategy: it ships with zero extra dependencies so the spine is
testable and usable immediately, while richer embedding/VLM strategies are added behind
the same :class:`ScorerPort`.
"""

from __future__ import annotations

import re

from tracertm.ports.scorer import ScoreResult, ScorerPort

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def _tokenize(text: str) -> set[str]:
    """Extract lowercase alphanumeric tokens from text."""
    return {t.lower() for t in _TOKEN_RE.findall(text or "")}


class JaccardScorer:
    """Lexical (Jaccard) agreement scorer.

    Computes the Jaccard similarity coefficient:
    ``score = |tokens(req) ∩ tokens(art)| / |tokens(req) ∪ tokens(art)|``.

    This is the dependency-free reference implementation that ships with Tracera.
    Richer embedding and VLM strategies plug in behind the same :class:`ScorerPort`.

    Implements :class:`ScorerPort` protocol:
        - ``name`` property: returns "jaccard"
        - ``score(requirement_text, artifact_text) -> ScoreResult``
    """

    name = "jaccard"

    def score(self, requirement_text: str, artifact_text: str) -> ScoreResult:
        """Return Jaccard similarity score.

        Args:
            requirement_text: The requirement text to score against.
            artifact_text: The artifact text to compare.

        Returns:
            ScoreResult with normalized score in [0.0, 1.0], rationale, and strategy name.

        Raises:
            ValueError: If ScoreResult is given an out-of-range value (should not occur).
        """
        req = _tokenize(requirement_text)
        art = _tokenize(artifact_text)

        if not req and not art:
            return ScoreResult(0.0, "both inputs empty", self.name)

        union = req | art
        inter = req & art
        value = len(inter) / len(union) if union else 0.0

        rationale = (
            f"{len(inter)} shared / {len(union)} total tokens"
            f" (shared: {', '.join(sorted(inter)[:8])})"
            if inter
            else "no shared tokens"
        )
        return ScoreResult(round(value, 6), rationale, self.name)

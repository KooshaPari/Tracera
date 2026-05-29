"""Duplicate and conflict detector for Tracera requirements + TraceLinks.

Implements FR-TRC-012: Automated duplicate / conflict detection via TraceLink
miner.

Two detection modes
-------------------
1. **Duplicate requirements** — pairs of :class:`~tracertm.models.trace_link.Requirement`
   (or generic :class:`~tracertm.models.trace_link.Artifact`) whose normalised
   text (title + description) share a token-Jaccard similarity above a
   configurable threshold (default 0.75). Uses Python stdlib ``difflib`` only —
   no external NLP dependency.

2. **Conflicting TraceLinks** — pairs of :class:`~tracertm.models.trace_link.TraceLink`
   where the same ordered (source, target) artifact pair is simultaneously
   tagged with mutually-exclusive link types.  Current conflict rules:

   * A link typed ``CONFLICTS_WITH`` co-exists with any of the cooperative link
     types (``SATISFIES``, ``VERIFIES``, ``IMPLEMENTS``, ``DERIVES_FROM``,
     ``REFINES``) on the **same (source, target) pair**.
   * The same (source, target) pair carries both ``SATISFIES`` and
     ``CONFLICTS_WITH``, or both ``IMPLEMENTS`` and ``CONFLICTS_WITH``.

Both detectors are **pure functions** (no DB access) so they can be composed
over any in-memory collection or graph projection.  The API layer feeds them
the materialised artifact/link lists from the repository.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Sequence

from tracertm.models.trace_link import Artifact, TraceLink, TraceLinkType

__all__ = [
    "ConflictFinding",
    "DuplicateFinding",
    "detect_conflicting_links",
    "detect_duplicate_requirements",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Link types that are inherently cooperative / positive relationships.
_COOPERATIVE_TYPES: frozenset[TraceLinkType] = frozenset({
    TraceLinkType.SATISFIES,
    TraceLinkType.VERIFIES,
    TraceLinkType.IMPLEMENTS,
    TraceLinkType.DERIVES_FROM,
    TraceLinkType.REFINES,
})

#: A link typed CONFLICTS_WITH alongside any cooperative type is a conflict.
_CONFLICT_PAIRS: frozenset[frozenset[TraceLinkType]] = frozenset({
    frozenset({TraceLinkType.CONFLICTS_WITH, t}) for t in _COOPERATIVE_TYPES
})


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DuplicateFinding:
    """A near-duplicate pair of requirements/artifacts."""

    artifact_a_id: uuid.UUID
    artifact_a_title: str
    artifact_b_id: uuid.UUID
    artifact_b_title: str
    #: Jaccard similarity score in [0.0, 1.0].
    similarity: float


@dataclass(frozen=True, slots=True)
class ConflictFinding:
    """A pair of TraceLinks that are mutually exclusive."""

    link_a_id: uuid.UUID
    link_b_id: uuid.UUID
    source_artifact_id: uuid.UUID
    target_artifact_id: uuid.UUID
    link_type_a: TraceLinkType
    link_type_b: TraceLinkType
    #: Confidence is 1.0 — structural contradiction, no probability involved.
    confidence: float = field(default=1.0)


# ---------------------------------------------------------------------------
# Text normalisation helpers
# ---------------------------------------------------------------------------


def _normalise(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _token_set(text: str) -> set[str]:
    """Return the set of non-empty tokens after normalisation."""
    return set(_normalise(text).split())


def _jaccard(a: set[str], b: set[str]) -> float:
    """Token Jaccard similarity: |A ∩ B| / |A ∪ B|.

    Returns 0.0 when both sets are empty (avoids division by zero).
    """
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def _artifact_tokens(artifact: Artifact) -> set[str]:
    """Combine title + description into one token set."""
    text = artifact.title
    if artifact.description:
        text = f"{text} {artifact.description}"
    return _token_set(text)


# ---------------------------------------------------------------------------
# Public detector functions
# ---------------------------------------------------------------------------


def detect_duplicate_requirements(
    artifacts: Sequence[Artifact],
    threshold: float = 0.75,
) -> list[DuplicateFinding]:
    """Detect near-duplicate requirements by token-Jaccard similarity.

    Compares every distinct pair in *O(n²)* — suitable for project-scoped
    batches (hundreds to low thousands of requirements).  Use a higher
    ``threshold`` (e.g. 0.90) if you want only near-exact duplicates.

    Args:
        artifacts: Iterable of :class:`~tracertm.models.trace_link.Artifact`
            (or :class:`~tracertm.models.trace_link.Requirement`) objects.
        threshold: Minimum Jaccard similarity to classify as a duplicate.
            Must be in (0.0, 1.0].  Default is 0.75.

    Returns:
        List of :class:`DuplicateFinding` for pairs whose similarity is
        at or above *threshold*, sorted descending by similarity.

    Raises:
        ValueError: If *threshold* is outside (0.0, 1.0].
    """
    if not 0.0 < threshold <= 1.0:
        msg = f"threshold must be in (0.0, 1.0], got {threshold!r}"
        raise ValueError(msg)

    items = list(artifacts)
    findings: list[DuplicateFinding] = []

    for i in range(len(items)):
        tokens_i = _artifact_tokens(items[i])
        for j in range(i + 1, len(items)):
            tokens_j = _artifact_tokens(items[j])
            score = _jaccard(tokens_i, tokens_j)
            if score >= threshold:
                findings.append(
                    DuplicateFinding(
                        artifact_a_id=items[i].id,
                        artifact_a_title=items[i].title,
                        artifact_b_id=items[j].id,
                        artifact_b_title=items[j].title,
                        similarity=round(score, 4),
                    )
                )

    findings.sort(key=lambda f: f.similarity, reverse=True)
    return findings


def detect_conflicting_links(
    links: Sequence[TraceLink],
) -> list[ConflictFinding]:
    """Detect mutually-exclusive TraceLink pairs on the same (source, target).

    A conflict is raised when the **same ordered (source_artifact_id,
    target_artifact_id) pair** carries two link types that are logically
    incompatible:

    * ``CONFLICTS_WITH`` paired with any cooperative type
      (``SATISFIES``, ``VERIFIES``, ``IMPLEMENTS``, ``DERIVES_FROM``,
      ``REFINES``).

    Args:
        links: Collection of :class:`~tracertm.models.trace_link.TraceLink`
            objects to inspect.

    Returns:
        List of :class:`ConflictFinding`, one per conflicting pair, sorted
        by (source_artifact_id, target_artifact_id, link_type_a).
    """
    # Group links by (source, target) pair.
    from collections import defaultdict

    pair_map: dict[
        tuple[uuid.UUID, uuid.UUID], list[TraceLink]
    ] = defaultdict(list)
    for link in links:
        pair_map[(link.source_artifact_id, link.target_artifact_id)].append(link)

    findings: list[ConflictFinding] = []
    seen: set[frozenset[uuid.UUID]] = set()

    for (src, tgt), group in pair_map.items():
        # Check every distinct link pair within this (source, target) group.
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                type_pair: frozenset[TraceLinkType] = frozenset({a.link_type, b.link_type})
                id_pair: frozenset[uuid.UUID] = frozenset({a.id, b.id})

                # Skip already-recorded pairs (can't happen with i<j, but safe).
                if id_pair in seen:
                    continue

                if type_pair in _CONFLICT_PAIRS:
                    seen.add(id_pair)
                    # Stable ordering: put CONFLICTS_WITH second for readability.
                    if a.link_type == TraceLinkType.CONFLICTS_WITH:
                        a, b = b, a
                    findings.append(
                        ConflictFinding(
                            link_a_id=a.id,
                            link_b_id=b.id,
                            source_artifact_id=src,
                            target_artifact_id=tgt,
                            link_type_a=a.link_type,
                            link_type_b=b.link_type,
                        )
                    )

    findings.sort(
        key=lambda f: (str(f.source_artifact_id), str(f.target_artifact_id), f.link_type_a.value)
    )
    return findings

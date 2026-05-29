"""Requirement miner service for Tracera.

Implements FR-TRC-011: given source text or file paths, extract candidate
Requirement statements using heuristic pattern matching and emit
``CandidateRequirement`` records that feed the existing Requirement /
TraceLink model.

Mining strategy (heuristic, no external NLP dependency)
--------------------------------------------------------
1. **Modal-verb sentences** — lines containing requirement-language modals
   (``shall``, ``must``, ``should``, ``will``, ``may``, ``can``) surrounded
   by context words that indicate a system/component obligation.  Confidence
   is highest for ``shall`` / ``must`` (0.90), then ``should`` / ``will``
   (0.70), then ``may`` / ``can`` (0.50).

2. **FR/NFR-pattern markers** — lines or inline tags matching
   ``FR-``, ``NFR-``, ``REQ-``, ``SYS-``, ``SRS-`` prefixes (case-insensitive).
   Confidence 0.95 (explicit tagging is high-signal).

3. **TODO/spec markers** — ``# TODO``, ``# FIXME``, ``# SPEC``, ``# REQUIREMENT``,
   ``@requirement``, ``@spec`` (code comments and docstrings).  Confidence 0.60
   (these are *candidate* requirements but may be implementation notes).

All findings are de-duplicated by normalised text and sorted descending by
confidence.  An embedding hook is intentionally left open (see
``_embedding_hook``) for future RAG integration once a vector library is
added as a project dependency.

Functional Requirements: FR-TRC-011
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

__all__ = [
    "CandidateRequirement",
    "MinerConfig",
    "mine_text",
    "mine_files",
]

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

#: Requirement-language modal verbs ranked by signal strength.
_MODAL_PATTERNS: list[tuple[re.Pattern[str], float]] = [
    # Shall / must — normative (RFC 2119 + ISO 29148)
    (re.compile(r"\b(?:shall|must)\b", re.IGNORECASE), 0.90),
    # Should / will — recommended / expected behaviour
    (re.compile(r"\b(?:should|will)\b", re.IGNORECASE), 0.70),
    # May / can — permitted / optional
    (re.compile(r"\b(?:may|can)\b", re.IGNORECASE), 0.50),
]

#: Explicit requirement-ID prefixes (FR-xxx, NFR-xxx, REQ-xxx, …).
_TAG_PATTERN: re.Pattern[str] = re.compile(
    r"\b(?:FR|NFR|REQ|SYS|SRS|UC|TC|AR)-[\w\-]+",
    re.IGNORECASE,
)

#: Code-comment / docstring spec markers.
_MARKER_PATTERN: re.Pattern[str] = re.compile(
    r"(?:#\s*(?:TODO|FIXME|SPEC|REQUIREMENT|HACK)|@(?:requirement|spec))\b",
    re.IGNORECASE,
)

#: Minimum non-whitespace characters for a sentence to be considered.
_MIN_LENGTH: int = 10

#: Maximum characters extracted per candidate (truncate for display).
_MAX_LENGTH: int = 500


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CandidateRequirement:
    """A candidate requirement extracted from source text.

    ``confidence`` is in [0.0, 1.0].  ``source_ref`` is an opaque string
    identifying where the candidate was found (e.g. ``"file.py:42"`` or
    ``"inline:3"``).  ``tags`` lists any explicit FR/NFR/REQ-xxx identifiers
    found in the sentence.
    """

    id: uuid.UUID
    text: str
    confidence: float
    source_ref: str
    tags: tuple[str, ...] = field(default_factory=tuple)

    # Hook: embedding vector populated by a downstream RAG layer.
    # Left as None here; callers with an embedding lib can enrich the
    # candidate before persisting it.
    embedding: tuple[float, ...] | None = None


@dataclass
class MinerConfig:
    """Configuration knobs for the requirement miner.

    Attributes
    ----------
    min_confidence:
        Candidates below this threshold are filtered out (default 0.45,
        just below the ``may/can`` tier so low-signal lines are skipped).
    include_markers:
        Whether to include TODO/SPEC/FIXME marker lines (default True).
    deduplicate:
        Whether to de-duplicate candidates by normalised text (default True).
    """

    min_confidence: float = 0.45
    include_markers: bool = True
    deduplicate: bool = True


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _normalise(text: str) -> str:
    """Return lowercase, whitespace-collapsed version of *text* for dedup."""
    return re.sub(r"\s+", " ", text.lower().strip())


def _extract_tags(text: str) -> tuple[str, ...]:
    return tuple(sorted({m.upper() for m in _TAG_PATTERN.findall(text)}))


def _score_sentence(sentence: str, include_markers: bool) -> float | None:
    """Return the best confidence score for *sentence*, or None if it is not
    a requirement candidate."""
    stripped = sentence.strip()
    if len(stripped) < _MIN_LENGTH:
        return None

    # Explicit tag is highest signal — return immediately.
    if _TAG_PATTERN.search(stripped):
        return 0.95

    # Modal verb — return highest-scoring match.
    best: float | None = None
    for pattern, score in _MODAL_PATTERNS:
        if pattern.search(stripped):
            if best is None or score > best:
                best = score
    if best is not None:
        return best

    # Comment / docstring marker.
    if include_markers and _MARKER_PATTERN.search(stripped):
        return 0.60

    return None


def _split_sentences(text: str) -> list[tuple[str, int]]:
    """Split *text* into (sentence, line_number) pairs.

    Splits on sentence-ending punctuation (. ! ?) and line boundaries,
    retaining the 1-based line number of the *first* character.
    """
    results: list[tuple[str, int]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        # Split each line on sentence boundaries while keeping the delimiters.
        parts = re.split(r"(?<=[.!?])\s+", line)
        for part in parts:
            part = part.strip()
            if part:
                results.append((part, lineno))
    return results


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def mine_text(
    text: str,
    *,
    source_ref: str = "inline",
    config: MinerConfig | None = None,
) -> list[CandidateRequirement]:
    """Extract candidate requirements from *text*.

    Parameters
    ----------
    text:
        Raw source text (code, markdown, docstring, free-form spec).
    source_ref:
        Label used in ``CandidateRequirement.source_ref`` (e.g. a filename).
    config:
        Miner configuration; defaults to ``MinerConfig()``.

    Returns
    -------
    list[CandidateRequirement]
        Candidates sorted descending by confidence.  Empty list if *text* is
        blank or no candidates meet the ``min_confidence`` threshold.
    """
    if config is None:
        config = MinerConfig()

    candidates: list[CandidateRequirement] = []
    seen_normalised: set[str] = set()

    for sentence, lineno in _split_sentences(text):
        score = _score_sentence(sentence, config.include_markers)
        if score is None or score < config.min_confidence:
            continue

        normalised = _normalise(sentence)
        if config.deduplicate and normalised in seen_normalised:
            continue
        seen_normalised.add(normalised)

        candidates.append(
            CandidateRequirement(
                id=uuid.uuid4(),
                text=sentence[:_MAX_LENGTH],
                confidence=score,
                source_ref=f"{source_ref}:{lineno}",
                tags=_extract_tags(sentence),
            )
        )

    # Sort descending by confidence, then alphabetically for determinism.
    candidates.sort(key=lambda c: (-c.confidence, c.text))
    return candidates


def mine_files(
    paths: Sequence[str | Path],
    *,
    config: MinerConfig | None = None,
) -> list[CandidateRequirement]:
    """Extract candidate requirements from one or more files.

    Files that cannot be read (missing, binary) are silently skipped.  Each
    candidate's ``source_ref`` is ``"<path>:<lineno>"``.

    Parameters
    ----------
    paths:
        Iterable of file paths (str or :class:`pathlib.Path`).
    config:
        Miner configuration; defaults to ``MinerConfig()``.

    Returns
    -------
    list[CandidateRequirement]
        Merged, deduplicated list sorted descending by confidence.
    """
    all_candidates: list[CandidateRequirement] = []
    for raw_path in paths:
        p = Path(raw_path)
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        all_candidates.extend(mine_text(text, source_ref=str(p), config=config))

    all_candidates.sort(key=lambda c: (-c.confidence, c.text))
    return all_candidates


# ---------------------------------------------------------------------------
# Embedding hook (stubbed, intentionally not wired until RAG dep lands)
# ---------------------------------------------------------------------------


def _embedding_hook(
    candidates: list[CandidateRequirement],
    # embed_fn: Callable[[str], list[float]] | None = None,
) -> list[CandidateRequirement]:
    """Placeholder for embedding enrichment.

    When a vector/embedding library is added as a project dependency, replace
    this stub with a real implementation that calls ``embed_fn(c.text)`` and
    returns enriched ``CandidateRequirement`` objects with ``embedding`` set.
    This function is intentionally a no-op until then.
    """
    return candidates

"""Unit tests for the requirement miner service.

Functional Requirements: FR-TRC-011

Coverage
--------
* Requirement-language sentence (shall/must) extracted as candidate.
* Non-requirement prose not flagged.
* FR-/NFR-pattern detected with high confidence (0.95).
* Confidence ordering: explicit tag > shall > should > may.
* Empty input returns empty list.
* Duplicate sentences de-duplicated (config.deduplicate=True).
* Duplicate sentences not de-duplicated when config.deduplicate=False.
* min_confidence filter respected.
* include_markers=False suppresses TODO/SPEC markers.
* TODO/SPEC markers included when include_markers=True.
* mine_files: returns candidates from a real temp file.
* mine_files: missing file silently skipped.
* mine_files: empty files return empty list.
* Multi-sentence text extracts multiple candidates.
* Tags extracted from FR-/NFR- patterns.
* CandidateRequirement has uuid4 id.
* Candidates sorted descending by confidence.
"""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from tracertm.services.requirement_miner import (
    CandidateRequirement,
    MinerConfig,
    mine_files,
    mine_text,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# mine_text — basic extraction
# ---------------------------------------------------------------------------


def test_shall_sentence_extracted() -> None:
    """A sentence with 'shall' must be extracted with confidence >= 0.9."""
    text = "The system shall store all user preferences persistently."
    results = mine_text(text)
    assert len(results) == 1
    assert results[0].confidence >= 0.90
    assert "shall" in results[0].text.lower()


def test_must_sentence_extracted() -> None:
    """A sentence with 'must' must be extracted."""
    text = "All API responses must include a Content-Type header."
    results = mine_text(text)
    assert len(results) == 1
    assert results[0].confidence >= 0.90


def test_should_sentence_extracted() -> None:
    """A sentence with 'should' is extracted at lower confidence."""
    text = "The UI should display a loading spinner during async operations."
    results = mine_text(text)
    assert len(results) == 1
    assert 0.65 <= results[0].confidence < 0.90


def test_may_sentence_extracted() -> None:
    """A sentence with 'may' is extracted at the lowest modal tier."""
    text = "Users may optionally provide a description field."
    results = mine_text(text)
    assert len(results) == 1
    assert 0.45 <= results[0].confidence < 0.70


def test_non_requirement_prose_not_flagged() -> None:
    """Ordinary prose without requirement language is not extracted."""
    text = "This is a general description of the architecture."
    results = mine_text(text)
    assert results == []


def test_empty_input_returns_empty() -> None:
    """Empty string produces empty candidate list."""
    assert mine_text("") == []


def test_whitespace_only_returns_empty() -> None:
    """Whitespace-only string produces empty candidate list."""
    assert mine_text("   \n\t  ") == []


# ---------------------------------------------------------------------------
# FR/NFR pattern detection
# ---------------------------------------------------------------------------


def test_fr_pattern_detected() -> None:
    """A line with an FR-xxx tag is extracted with confidence 0.95."""
    text = "FR-TRC-011: The miner service shall extract candidate requirements."
    results = mine_text(text)
    assert len(results) >= 1
    best = results[0]
    assert best.confidence == 0.95
    assert "FR-TRC-011" in best.tags


def test_nfr_pattern_detected() -> None:
    """A line with an NFR-xxx tag is extracted with confidence 0.95."""
    text = "NFR-PERF-003 The system must respond within 200 ms."
    results = mine_text(text)
    assert len(results) >= 1
    assert results[0].confidence == 0.95


def test_tags_extracted_from_text() -> None:
    """FR and NFR tags found in text are stored in CandidateRequirement.tags."""
    text = "See FR-AUTH-001 and NFR-SEC-002 for details on the login flow."
    results = mine_text(text)
    assert results
    tags = results[0].tags
    assert "FR-AUTH-001" in tags
    assert "NFR-SEC-002" in tags


# ---------------------------------------------------------------------------
# Confidence ordering
# ---------------------------------------------------------------------------


def test_confidence_ordering_explicit_tag_highest() -> None:
    """Explicit tag confidence (0.95) beats 'shall' confidence (0.90)."""
    text = (
        "FR-SYS-001: the component must handle errors.\n"
        "The service shall log all requests."
    )
    results = mine_text(text)
    assert results[0].confidence >= results[1].confidence
    assert results[0].confidence == 0.95


def test_candidates_sorted_descending_by_confidence() -> None:
    """Candidates list is sorted from highest to lowest confidence."""
    text = (
        "REQ-001: system shall authenticate users.\n"
        "The UI should show a confirmation dialog.\n"
        "Users may cancel at any time."
    )
    results = mine_text(text)
    confidences = [c.confidence for c in results]
    assert confidences == sorted(confidences, reverse=True)


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


def test_duplicate_sentences_deduped_by_default() -> None:
    """Identical sentences appear only once with default config."""
    text = (
        "The system shall log all errors.\n"
        "The system shall log all errors.\n"
    )
    results = mine_text(text)
    texts = [c.text for c in results]
    assert len(texts) == len(set(texts))


def test_duplicate_sentences_kept_when_dedup_disabled() -> None:
    """Identical sentences produce two candidates when deduplicate=False."""
    text = (
        "The system shall log all errors.\n"
        "The system shall log all errors.\n"
    )
    cfg = MinerConfig(deduplicate=False)
    results = mine_text(text, config=cfg)
    assert len(results) == 2


# ---------------------------------------------------------------------------
# min_confidence filter
# ---------------------------------------------------------------------------


def test_min_confidence_filters_low_score_candidates() -> None:
    """Candidates below min_confidence are excluded."""
    text = "Users may optionally provide a description field."
    cfg = MinerConfig(min_confidence=0.80)
    results = mine_text(text, config=cfg)
    assert results == []


def test_min_confidence_passes_high_score() -> None:
    """Candidates at or above min_confidence are included."""
    text = "The system must validate all inputs."
    cfg = MinerConfig(min_confidence=0.80)
    results = mine_text(text, config=cfg)
    assert len(results) == 1
    assert results[0].confidence >= 0.80


# ---------------------------------------------------------------------------
# Marker handling
# ---------------------------------------------------------------------------


def test_todo_marker_included_by_default() -> None:
    """# TODO lines are extracted when include_markers=True (default)."""
    text = "# TODO: the service must support pagination"
    results = mine_text(text)
    # 'must' should fire (0.90) OR marker fires (0.60); either way non-empty.
    assert len(results) >= 1


def test_spec_marker_included() -> None:
    """# SPEC lines are extracted."""
    text = "# SPEC: user authentication flow"
    results = mine_text(text, config=MinerConfig(min_confidence=0.55))
    assert len(results) >= 1
    assert results[0].confidence >= 0.60


def test_marker_suppressed_when_include_markers_false() -> None:
    """# SPEC lines are NOT extracted when include_markers=False."""
    text = "# SPEC: user authentication flow without any modal verbs here"
    cfg = MinerConfig(include_markers=False)
    results = mine_text(text, config=cfg)
    assert results == []


# ---------------------------------------------------------------------------
# Multi-sentence text
# ---------------------------------------------------------------------------


def test_multi_sentence_text_extracts_multiple() -> None:
    """Multiple requirement sentences in text each produce a candidate."""
    text = (
        "The database must be backed up daily.\n"
        "Users shall be notified of changes within five minutes.\n"
        "This is just a comment with no obligation language.\n"
    )
    results = mine_text(text)
    assert len(results) == 2


# ---------------------------------------------------------------------------
# CandidateRequirement structure
# ---------------------------------------------------------------------------


def test_candidate_has_uuid() -> None:
    """Every candidate has a valid UUID4 id."""
    text = "The service shall handle timeouts gracefully."
    results = mine_text(text)
    assert results
    c = results[0]
    assert isinstance(c.id, uuid.UUID)
    assert c.id.version == 4


def test_candidate_source_ref_contains_line_number() -> None:
    """source_ref is formatted as '<ref>:<lineno>'."""
    text = "The system must validate tokens on every request."
    results = mine_text(text, source_ref="auth.py")
    assert results
    assert "auth.py:" in results[0].source_ref


# ---------------------------------------------------------------------------
# mine_files
# ---------------------------------------------------------------------------


def test_mine_files_reads_temp_file(tmp_path: Path) -> None:
    """mine_files reads a real file and extracts candidates."""
    spec_file = tmp_path / "spec.md"
    spec_file.write_text(
        "# Authentication\nThe service shall authenticate all users via OAuth2.\n",
        encoding="utf-8",
    )
    results = mine_files([spec_file])
    assert len(results) >= 1
    assert results[0].confidence >= 0.90


def test_mine_files_missing_file_skipped(tmp_path: Path) -> None:
    """A non-existent file path is silently skipped."""
    results = mine_files([tmp_path / "does_not_exist.txt"])
    assert results == []


def test_mine_files_empty_file_returns_empty(tmp_path: Path) -> None:
    """An empty file produces no candidates."""
    empty = tmp_path / "empty.py"
    empty.write_text("", encoding="utf-8")
    assert mine_files([empty]) == []


def test_mine_files_multiple_files_merged(tmp_path: Path) -> None:
    """Candidates from multiple files are merged and sorted."""
    f1 = tmp_path / "a.py"
    f1.write_text(
        "# The system shall log all API calls.\n",
        encoding="utf-8",
    )
    f2 = tmp_path / "b.md"
    f2.write_text(
        "FR-LOG-001: the logger must support structured output.\n",
        encoding="utf-8",
    )
    results = mine_files([f1, f2])
    assert len(results) >= 2
    # FR-tagged item should be first (confidence 0.95).
    assert results[0].confidence == 0.95

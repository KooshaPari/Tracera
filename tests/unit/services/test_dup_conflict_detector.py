"""Unit tests for the duplicate / conflict detector service.

Functional Requirements: FR-TRC-012

Coverage
--------
* Near-duplicate pair detected above threshold.
* Distinct requirements NOT flagged as duplicates.
* Conflicting link pair detected.
* Clean link set returns empty findings.
* Edge cases: threshold validation, empty inputs.
"""

from __future__ import annotations

import uuid

import pytest

from tracertm.models.trace_link import Artifact, ArtifactKind, TraceLink, TraceLinkType
from tracertm.services.dup_conflict_detector import (
    detect_conflicting_links,
    detect_duplicate_requirements,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _req(title: str, description: str | None = None) -> Artifact:
    """Construct a minimal REQUIREMENT Artifact."""
    return Artifact(
        id=uuid.uuid4(),
        project_id=uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001"),
        kind=ArtifactKind.REQUIREMENT,
        title=title,
        description=description,
    )


def _link(
    src: uuid.UUID,
    tgt: uuid.UUID,
    link_type: TraceLinkType,
    *,
    project_id: uuid.UUID | None = None,
) -> TraceLink:
    """Construct a minimal TraceLink."""
    return TraceLink(
        id=uuid.uuid4(),
        project_id=project_id or uuid.UUID("bbbbbbbb-0000-0000-0000-000000000001"),
        source_artifact_id=src,
        target_artifact_id=tgt,
        link_type=link_type,
    )


# ---------------------------------------------------------------------------
# Duplicate detection tests
# ---------------------------------------------------------------------------


class TestDetectDuplicateRequirements:
    """Tests for detect_duplicate_requirements."""

    def test_near_duplicate_pair_detected(self) -> None:
        """Two requirements with near-identical text are flagged."""
        a = _req(
            "The system shall validate user input before processing",
            "Input validation is required",
        )
        b = _req(
            "The system shall validate user input before processing",
            "Input validation is required for all forms",
        )
        findings = detect_duplicate_requirements([a, b], threshold=0.70)
        assert len(findings) == 1
        finding = findings[0]
        assert {finding.artifact_a_id, finding.artifact_b_id} == {a.id, b.id}
        assert finding.similarity >= 0.70

    def test_exact_duplicates_detected_at_default_threshold(self) -> None:
        """Identical title+description is always above the 0.75 default."""
        same_title = "The system shall authenticate users via OAuth2"
        a = _req(same_title, "OAuth2 PKCE flow required")
        b = _req(same_title, "OAuth2 PKCE flow required")
        findings = detect_duplicate_requirements([a, b])
        assert len(findings) == 1
        assert findings[0].similarity == 1.0

    def test_distinct_requirements_not_flagged(self) -> None:
        """Requirements with clearly different text are not flagged."""
        a = _req("The system shall export reports to PDF", "PDF export via wkhtmltopdf")
        b = _req("The system shall authenticate users via SSO", "SAML 2.0 IdP required")
        c = _req("Database backups must run daily at midnight", "Automated pg_dump scheduled task")
        findings = detect_duplicate_requirements([a, b, c])
        assert findings == []

    def test_empty_input_returns_no_findings(self) -> None:
        """Empty artifact list yields empty findings."""
        assert detect_duplicate_requirements([]) == []

    def test_single_artifact_returns_no_findings(self) -> None:
        """Single artifact has no pair to compare against."""
        assert detect_duplicate_requirements([_req("Only one requirement")]) == []

    def test_findings_sorted_descending_by_similarity(self) -> None:
        """Multiple pairs are sorted highest similarity first."""
        base = "The system shall log all user actions to the audit trail"
        a = _req(base)
        b = _req(base)  # exact match → 1.0
        c = _req("The system shall log user actions to audit")  # partial match
        findings = detect_duplicate_requirements([a, b, c], threshold=0.5)
        assert len(findings) >= 2
        sims = [f.similarity for f in findings]
        assert sims == sorted(sims, reverse=True)

    def test_threshold_validation_raises_on_zero(self) -> None:
        """Threshold of 0.0 is invalid and raises ValueError."""
        with pytest.raises(ValueError, match="threshold"):
            detect_duplicate_requirements([_req("x")], threshold=0.0)

    def test_threshold_validation_raises_on_negative(self) -> None:
        """Negative threshold raises ValueError."""
        with pytest.raises(ValueError, match="threshold"):
            detect_duplicate_requirements([_req("x")], threshold=-0.1)

    def test_threshold_1_0_only_exact(self) -> None:
        """Threshold 1.0 flags only token-identical pairs."""
        a = _req("System shall validate input")
        b = _req("System shall validate input")          # exact
        c = _req("System shall validate all user input")  # slightly different
        findings = detect_duplicate_requirements([a, b, c], threshold=1.0)
        assert len(findings) == 1
        assert {findings[0].artifact_a_id, findings[0].artifact_b_id} == {a.id, b.id}

    def test_description_contributes_to_similarity(self) -> None:
        """Description text is included in the token set."""
        a = _req("Auth requirement", "Users must log in with their corporate SSO credentials")
        b = _req("Auth requirement", "Users must log in with their corporate SSO credentials")
        findings = detect_duplicate_requirements([a, b], threshold=0.9)
        assert len(findings) == 1


# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------


class TestDetectConflictingLinks:
    """Tests for detect_conflicting_links."""

    def test_satisfies_and_conflicts_with_flagged(self) -> None:
        """SATISFIES + CONFLICTS_WITH on same pair is a conflict."""
        src = uuid.uuid4()
        tgt = uuid.uuid4()
        satisfies = _link(src, tgt, TraceLinkType.SATISFIES)
        conflicts = _link(src, tgt, TraceLinkType.CONFLICTS_WITH)
        findings = detect_conflicting_links([satisfies, conflicts])
        assert len(findings) == 1
        f = findings[0]
        assert f.source_artifact_id == src
        assert f.target_artifact_id == tgt
        assert TraceLinkType.CONFLICTS_WITH.value in {f.link_type_a, f.link_type_b}
        assert f.confidence == 1.0

    def test_implements_and_conflicts_with_flagged(self) -> None:
        """IMPLEMENTS + CONFLICTS_WITH on same pair is a conflict."""
        src, tgt = uuid.uuid4(), uuid.uuid4()
        impl = _link(src, tgt, TraceLinkType.IMPLEMENTS)
        conf = _link(src, tgt, TraceLinkType.CONFLICTS_WITH)
        findings = detect_conflicting_links([impl, conf])
        assert len(findings) == 1

    def test_verifies_and_conflicts_with_flagged(self) -> None:
        """VERIFIES + CONFLICTS_WITH on same pair is a conflict."""
        src, tgt = uuid.uuid4(), uuid.uuid4()
        findings = detect_conflicting_links([
            _link(src, tgt, TraceLinkType.VERIFIES),
            _link(src, tgt, TraceLinkType.CONFLICTS_WITH),
        ])
        assert len(findings) == 1

    def test_derives_from_and_conflicts_with_flagged(self) -> None:
        """DERIVES_FROM + CONFLICTS_WITH on same pair is a conflict."""
        src, tgt = uuid.uuid4(), uuid.uuid4()
        findings = detect_conflicting_links([
            _link(src, tgt, TraceLinkType.DERIVES_FROM),
            _link(src, tgt, TraceLinkType.CONFLICTS_WITH),
        ])
        assert len(findings) == 1

    def test_refines_and_conflicts_with_flagged(self) -> None:
        """REFINES + CONFLICTS_WITH on same pair is a conflict."""
        src, tgt = uuid.uuid4(), uuid.uuid4()
        findings = detect_conflicting_links([
            _link(src, tgt, TraceLinkType.REFINES),
            _link(src, tgt, TraceLinkType.CONFLICTS_WITH),
        ])
        assert len(findings) == 1

    def test_different_pairs_no_cross_conflict(self) -> None:
        """CONFLICTS_WITH on one pair does not affect a different (src, tgt)."""
        src1, tgt1 = uuid.uuid4(), uuid.uuid4()
        src2, tgt2 = uuid.uuid4(), uuid.uuid4()
        findings = detect_conflicting_links([
            _link(src1, tgt1, TraceLinkType.SATISFIES),
            _link(src1, tgt1, TraceLinkType.CONFLICTS_WITH),
            _link(src2, tgt2, TraceLinkType.SATISFIES),
        ])
        assert len(findings) == 1
        assert findings[0].source_artifact_id == src1

    def test_clean_links_returns_empty(self) -> None:
        """A set of links with no conflicts returns an empty list."""
        src, tgt = uuid.uuid4(), uuid.uuid4()
        findings = detect_conflicting_links([
            _link(src, tgt, TraceLinkType.SATISFIES),
            _link(src, tgt, TraceLinkType.VERIFIES),
        ])
        assert findings == []

    def test_two_cooperative_types_no_conflict(self) -> None:
        """SATISFIES + IMPLEMENTS on same pair is NOT a conflict."""
        src, tgt = uuid.uuid4(), uuid.uuid4()
        assert detect_conflicting_links([
            _link(src, tgt, TraceLinkType.SATISFIES),
            _link(src, tgt, TraceLinkType.IMPLEMENTS),
        ]) == []

    def test_empty_links_returns_empty(self) -> None:
        """Empty link list yields empty findings."""
        assert detect_conflicting_links([]) == []

    def test_single_link_no_conflict(self) -> None:
        """A single link cannot conflict with itself."""
        src, tgt = uuid.uuid4(), uuid.uuid4()
        assert detect_conflicting_links([_link(src, tgt, TraceLinkType.SATISFIES)]) == []

    def test_conflicts_with_only_pair_no_conflict(self) -> None:
        """Two CONFLICTS_WITH links on same pair are NOT a structural conflict."""
        src, tgt = uuid.uuid4(), uuid.uuid4()
        findings = detect_conflicting_links([
            _link(src, tgt, TraceLinkType.CONFLICTS_WITH),
            _link(src, tgt, TraceLinkType.CONFLICTS_WITH),
        ])
        # CONFLICTS_WITH paired with itself is not in _CONFLICT_PAIRS
        assert findings == []

    def test_multiple_conflict_pairs_all_found(self) -> None:
        """Multiple conflicting pairs on different (src, tgt) are all reported."""
        pairs = [(uuid.uuid4(), uuid.uuid4()) for _ in range(3)]
        links = []
        for src, tgt in pairs:
            links.append(_link(src, tgt, TraceLinkType.SATISFIES))
            links.append(_link(src, tgt, TraceLinkType.CONFLICTS_WITH))
        findings = detect_conflicting_links(links)
        assert len(findings) == 3

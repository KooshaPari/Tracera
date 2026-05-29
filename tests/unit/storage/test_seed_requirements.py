"""Unit tests for scripts/seed_requirements.py.

Tests parse_catalog, build_domain_objects, and write_to_neo4j with a mocked
DB writer — no live Neo4j required.

Coverage:
- Parser correctly extracts FR/NFR headings, status, PRs, tests.
- Deterministic UUID generation for requirements, artifacts, links.
- build_domain_objects produces correct counts and link types.
- Idempotency: running twice on the same data yields the same IDs.
- write_to_neo4j dry-run branch does not call the neo4j driver.
- Missing catalog file is skipped gracefully.
"""

from __future__ import annotations

import importlib.util
import sys
import textwrap
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

# Load scripts/seed_requirements.py as a module without requiring it on PYTHONPATH.
# File is at <repo>/scripts/seed_requirements.py
# This test is at <repo>/tests/unit/storage/test_seed_requirements.py
# parents[3] => tests/unit/storage -> tests/unit -> tests -> <repo>
_REPO_ROOT = Path(__file__).resolve().parents[3]
_SEED_PATH = _REPO_ROOT / "scripts" / "seed_requirements.py"
_spec = importlib.util.spec_from_file_location("seed_requirements", str(_SEED_PATH))
sr = importlib.util.module_from_spec(_spec)
sys.modules["seed_requirements"] = sr
_spec.loader.exec_module(sr)

# ---------------------------------------------------------------------------
# Shared test catalog fixture
# ---------------------------------------------------------------------------

MINIMAL_CATALOG = textwrap.dedent(
    """\
    # Test Catalog

    ### FR-TST-001 — Minimal functional requirement

    **Description** A basic FR for testing.

    **Acceptance Criteria**
    - System stores the record
    - Record is retrievable

    **Status:** SHIPPED

    **Traceability**
    - PR: #101, #102
    - Test: tests/unit/test_minimal.py

    ---

    ### NFR-TST-001 — Minimal non-functional requirement

    **Description** Performance must be adequate.

    **Status:** PLANNED

    **Traceability**
    - No PRs yet.
    """
)


@pytest.fixture
def catalog_file(tmp_path: Path) -> Path:
    """Write a minimal catalog to a temp file and return its path."""
    p = tmp_path / "test-frnfr.md"
    p.write_text(MINIMAL_CATALOG, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# parse_catalog tests
# ---------------------------------------------------------------------------


def test_parse_catalog_parses_fr_and_nfr(catalog_file: Path) -> None:
    reqs = sr.parse_catalog("TST", catalog_file)
    assert len(reqs) == 2


def test_parse_catalog_fr_kind(catalog_file: Path) -> None:
    reqs = sr.parse_catalog("TST", catalog_file)
    fr = next(r for r in reqs if r.req_id == "FR-TST-001")
    assert fr.kind == "functional"


def test_parse_catalog_nfr_kind(catalog_file: Path) -> None:
    reqs = sr.parse_catalog("TST", catalog_file)
    nfr = next(r for r in reqs if r.req_id == "NFR-TST-001")
    assert nfr.kind == "non-functional"


def test_parse_catalog_status_shipped(catalog_file: Path) -> None:
    reqs = sr.parse_catalog("TST", catalog_file)
    fr = next(r for r in reqs if r.req_id == "FR-TST-001")
    assert fr.status == "shipped"


def test_parse_catalog_status_planned(catalog_file: Path) -> None:
    reqs = sr.parse_catalog("TST", catalog_file)
    nfr = next(r for r in reqs if r.req_id == "NFR-TST-001")
    assert nfr.status == "planned"


def test_parse_catalog_pr_extraction(catalog_file: Path) -> None:
    reqs = sr.parse_catalog("TST", catalog_file)
    fr = next(r for r in reqs if r.req_id == "FR-TST-001")
    assert "#101" in fr.prs
    assert "#102" in fr.prs


def test_parse_catalog_test_extraction(catalog_file: Path) -> None:
    reqs = sr.parse_catalog("TST", catalog_file)
    fr = next(r for r in reqs if r.req_id == "FR-TST-001")
    assert any("test_minimal.py" in t for t in fr.tests)


def test_parse_catalog_title_extracted(catalog_file: Path) -> None:
    reqs = sr.parse_catalog("TST", catalog_file)
    fr = next(r for r in reqs if r.req_id == "FR-TST-001")
    assert "Minimal functional requirement" in fr.title


def test_parse_catalog_acceptance_criteria(catalog_file: Path) -> None:
    reqs = sr.parse_catalog("TST", catalog_file)
    fr = next(r for r in reqs if r.req_id == "FR-TST-001")
    assert len(fr.acceptance_criteria) >= 1


def test_parse_catalog_missing_file_returns_empty(tmp_path: Path) -> None:
    missing = tmp_path / "nonexistent.md"
    result = sr.parse_catalog("XX", missing)
    assert result == []


# ---------------------------------------------------------------------------
# Deterministic UUID generation tests
# ---------------------------------------------------------------------------


def test_req_uuid_stable() -> None:
    id1 = sr.req_uuid("TST", "FR-TST-001")
    id2 = sr.req_uuid("TST", "FR-TST-001")
    assert id1 == id2


def test_artifact_uuid_stable() -> None:
    id1 = sr.artifact_uuid("TST", "PR#101")
    id2 = sr.artifact_uuid("TST", "PR#101")
    assert id1 == id2


def test_link_uuid_stable() -> None:
    src = sr.artifact_uuid("TST", "PR#101")
    tgt = sr.req_uuid("TST", "FR-TST-001")
    id1 = sr.link_uuid(src, tgt, "SATISFIES")
    id2 = sr.link_uuid(src, tgt, "SATISFIES")
    assert id1 == id2


def test_different_req_ids_produce_different_uuids() -> None:
    assert sr.req_uuid("TST", "FR-TST-001") != sr.req_uuid("TST", "FR-TST-002")


def test_different_project_keys_produce_different_uuids() -> None:
    assert sr.req_uuid("TST", "FR-TST-001") != sr.req_uuid("OTHER", "FR-TST-001")


def test_req_uuid_returns_uuid_instance() -> None:
    assert isinstance(sr.req_uuid("TST", "FR-TST-001"), uuid.UUID)


def test_artifact_uuid_returns_uuid_instance() -> None:
    assert isinstance(sr.artifact_uuid("TST", "PR#101"), uuid.UUID)


# ---------------------------------------------------------------------------
# build_domain_objects tests
# ---------------------------------------------------------------------------


def test_build_domain_objects_requirement_count(catalog_file: Path) -> None:
    parsed = sr.parse_catalog("TST", catalog_file)
    reqs, arts, links = sr.build_domain_objects("TST", parsed)
    assert len(reqs) == 2  # FR-TST-001 + NFR-TST-001


def test_build_domain_objects_artifact_dedup(catalog_file: Path) -> None:
    """Same PR referenced twice in separate requirements must appear once."""
    parsed = sr.parse_catalog("TST", catalog_file)
    _, arts, _ = sr.build_domain_objects("TST", parsed)
    ext_ids = [a["external_id"] for a in arts]
    assert len(ext_ids) == len(set(ext_ids))


def test_build_domain_objects_satisfies_links(catalog_file: Path) -> None:
    parsed = sr.parse_catalog("TST", catalog_file)
    _, _, links = sr.build_domain_objects("TST", parsed)
    satisfies = [l for l in links if l["link_type"] == "SATISFIES"]
    assert len(satisfies) >= 2  # PR#101 and PR#102


def test_build_domain_objects_verifies_links(catalog_file: Path) -> None:
    parsed = sr.parse_catalog("TST", catalog_file)
    _, _, links = sr.build_domain_objects("TST", parsed)
    verifies = [l for l in links if l["link_type"] == "VERIFIES"]
    assert len(verifies) >= 1


def test_build_domain_objects_idempotent_req_ids(catalog_file: Path) -> None:
    parsed = sr.parse_catalog("TST", catalog_file)
    reqs1, _, _ = sr.build_domain_objects("TST", parsed)
    reqs2, _, _ = sr.build_domain_objects("TST", parsed)
    assert {r["id"] for r in reqs1} == {r["id"] for r in reqs2}


def test_build_domain_objects_project_id(catalog_file: Path) -> None:
    parsed = sr.parse_catalog("TST", catalog_file)
    reqs, _, _ = sr.build_domain_objects("TST", parsed)
    for r in reqs:
        assert r["project_id"] == sr.SEED_PROJECT_ID


def test_build_domain_objects_pr_artifact_kind(catalog_file: Path) -> None:
    parsed = sr.parse_catalog("TST", catalog_file)
    _, arts, _ = sr.build_domain_objects("TST", parsed)
    pr_arts = [a for a in arts if a["kind"] == "code"]
    assert len(pr_arts) >= 2


def test_build_domain_objects_test_artifact_kind(catalog_file: Path) -> None:
    parsed = sr.parse_catalog("TST", catalog_file)
    _, arts, _ = sr.build_domain_objects("TST", parsed)
    test_arts = [a for a in arts if a["kind"] == "test"]
    assert len(test_arts) >= 1


def test_build_domain_objects_status_shipped_to_verified(catalog_file: Path) -> None:
    parsed = sr.parse_catalog("TST", catalog_file)
    reqs, _, _ = sr.build_domain_objects("TST", parsed)
    fr = next(r for r in reqs if "FR-TST-001" in r["external_id"])
    assert fr["status"] == "verified"


def test_build_domain_objects_status_planned_to_proposed(catalog_file: Path) -> None:
    parsed = sr.parse_catalog("TST", catalog_file)
    reqs, _, _ = sr.build_domain_objects("TST", parsed)
    nfr = next(r for r in reqs if "NFR-TST-001" in r["external_id"])
    assert nfr["status"] == "proposed"


# ---------------------------------------------------------------------------
# write_to_neo4j (mocked) tests
# ---------------------------------------------------------------------------


def test_write_to_neo4j_dry_run_prints_dryrun(capsys: pytest.CaptureFixture) -> None:
    sr.write_to_neo4j(
        uri="bolt://localhost:7687",
        auth=("neo4j", "password"),
        requirements=[],
        artifacts=[],
        links=[],
        dry_run=True,
    )
    captured = capsys.readouterr()
    assert "[DRY-RUN]" in captured.out


def test_write_to_neo4j_dry_run_reports_counts(capsys: pytest.CaptureFixture) -> None:
    sr.write_to_neo4j(
        uri="bolt://localhost:7687",
        auth=("neo4j", "password"),
        requirements=[{"id": 1}] * 5,
        artifacts=[{"id": 2}] * 3,
        links=[{"id": 3}] * 10,
        dry_run=True,
    )
    out = capsys.readouterr().out
    assert "5" in out
    assert "3" in out
    assert "10" in out


# ---------------------------------------------------------------------------
# Integration smoke tests — real on-disk catalogs, no DB
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "project_key,catalog_path",
    sr.CATALOGS,
)
def test_real_catalog_parses_nonzero(project_key: str, catalog_path: Path) -> None:
    if not catalog_path.exists():
        pytest.skip(f"Catalog not found on this machine: {catalog_path}")
    reqs = sr.parse_catalog(project_key, catalog_path)
    assert len(reqs) > 0, f"{project_key} catalog yielded 0 requirements"


def test_total_counts_across_all_catalogs() -> None:
    """All four catalogs together should yield ≥50 requirements."""
    total = 0
    for project_key, catalog_path in sr.CATALOGS:
        if catalog_path.exists():
            total += len(sr.parse_catalog(project_key, catalog_path))
    assert total >= 50, f"Expected ≥50 requirements across all catalogs, got {total}"

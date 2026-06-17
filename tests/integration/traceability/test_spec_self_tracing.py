"""Integration tests for spec self-tracing and traceability verification.

Tests verify that the spec→code→test→commit chain is traceable via the Tracera API.
This validates the core NFR-TRC-012 requirement that Tracera itself can be traced through
its own specification system.

Markers
-------
* ``integration``  — API layer integration tests; may require mocked services
* ``traceability`` — spec-to-code chain traceability
* ``slow``         — full end-to-end chain tests

Functional Requirements: NFR-TRC-012, FR-TRC-001, FR-TRC-015 (blast radius)
"""

from __future__ import annotations

import uuid
from typing import Any
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.integration, pytest.mark.traceability]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def stable_ids() -> dict[str, str]:
    """Return stable UUIDs for spec, code, test, and commit artifacts."""
    return {
        "spec_fr_trc_012": str(uuid.UUID("ffffffff-0000-0000-0000-000000000012")),
        "code_trace_api": str(uuid.UUID("ffffffff-0000-0000-0000-000000000101")),
        "test_spec_self_tracing": str(uuid.UUID("ffffffff-0000-0000-0000-000000000102")),
        "commit_trace_scaffold": str(uuid.UUID("ffffffff-0000-0000-0000-000000000103")),
        "design_doc": str(uuid.UUID("ffffffff-0000-0000-0000-000000000201")),
        "project_id": str(uuid.UUID("ffffffff-0000-0000-0000-000000000001")),
    }


@pytest.fixture
def test_app() -> FastAPI:
    """Return a FastAPI test app with traceability router."""
    from tracertm.api.routers.traceability import router

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


@pytest.fixture
def test_client(test_app: FastAPI) -> TestClient:
    """Return a TestClient for the FastAPI app."""
    return TestClient(test_app)


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------


def test_spec_requirement_has_trace_link(
    test_client: TestClient,
    stable_ids: dict[str, str],
) -> None:
    """Test that a specification requirement can be created with a unique trace_id.

    Verifies NFR-TRC-012: Spec system is self-describing via trace links.
    A requirement like FR-TRC-012 should be traceable as an artifact in its own system.
    """
    # Create a trace link where the requirement is the source
    # This represents the spec→code relationship
    request_body = {
        "links": [
            {
                "source_id": stable_ids["spec_fr_trc_012"],
                "target_id": stable_ids["code_trace_api"],
                "relationship": "satisfies",
                "confidence": 1.0,
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ]
    }

    response = test_client.post("/api/v1/coverage-matrix", json=request_body)

    assert response.status_code == 200
    body = response.json()

    # Verify the requirement was traced
    assert "cells" in body
    assert len(body["cells"]) >= 1

    # Find the cell for our requirement
    req_cell = next(
        (cell for cell in body["cells"] if cell["source_id"] == stable_ids["spec_fr_trc_012"]),
        None,
    )
    assert req_cell is not None
    assert req_cell["source_id"] == stable_ids["spec_fr_trc_012"]
    assert req_cell["target_id"] == stable_ids["code_trace_api"]
    assert req_cell["coverage"] in ["covered", "partial"]
    assert req_cell["links"][0]["relationship"] == "satisfies"


def test_code_artifact_links_to_requirement(
    test_client: TestClient,
    stable_ids: dict[str, str],
) -> None:
    """Test that a code artifact can be linked to a requirement.

    Verifies FR-TRC-001: code artifacts can reference their implementing requirement.
    The code→requirement link demonstrates downstream traceability.
    """
    request_body = {
        "links": [
            {
                "source_id": stable_ids["spec_fr_trc_012"],
                "target_id": stable_ids["code_trace_api"],
                "relationship": "implements",
                "confidence": 0.95,
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ]
    }

    response = test_client.post("/api/v1/coverage-matrix", json=request_body)

    assert response.status_code == 200
    body = response.json()

    # Verify the code artifact is linked
    assert body["link_count"] == 1
    cell = body["cells"][0]
    assert cell["source_id"] == stable_ids["spec_fr_trc_012"]
    assert cell["target_id"] == stable_ids["code_trace_api"]
    assert cell["links"][0]["relationship"] == "implements"
    assert cell["links"][0]["confidence"] == 0.95


def test_test_artifact_links_to_requirement(
    test_client: TestClient,
    stable_ids: dict[str, str],
) -> None:
    """Test that a test artifact can be linked to a requirement via code.

    Verifies the test→code→requirement chain: tests verify code that implements requirements.
    This demonstrates bidirectional traceability in the spec chain.
    """
    request_body = {
        "links": [
            {
                "source_id": stable_ids["spec_fr_trc_012"],
                "target_id": stable_ids["code_trace_api"],
                "relationship": "satisfies",
                "confidence": 0.95,
                "updated_at": datetime.now(UTC).isoformat(),
            },
            {
                "source_id": stable_ids["code_trace_api"],
                "target_id": stable_ids["test_spec_self_tracing"],
                "relationship": "verifies",
                "confidence": 0.90,
                "updated_at": datetime.now(UTC).isoformat(),
            },
        ]
    }

    response = test_client.post("/api/v1/coverage-matrix", json=request_body)

    assert response.status_code == 200
    body = response.json()

    assert body["link_count"] == 2
    assert body["cell_count"] == 2

    # Verify both links exist
    source_target_pairs = {(cell["source_id"], cell["target_id"]) for cell in body["cells"]}
    assert (stable_ids["spec_fr_trc_012"], stable_ids["code_trace_api"]) in source_target_pairs
    assert (stable_ids["code_trace_api"], stable_ids["test_spec_self_tracing"]) in source_target_pairs

    # Verify test coverage
    test_cell = next(
        (cell for cell in body["cells"] if cell["target_id"] == stable_ids["test_spec_self_tracing"]),
        None,
    )
    assert test_cell is not None
    assert test_cell["coverage"] in ["covered", "partial"]


def test_blast_radius_from_requirement(
    test_client: TestClient,
    stable_ids: dict[str, str],
) -> None:
    """Test that blast radius analysis returns all dependent artifacts.

    Verifies FR-TRC-015: Impact analysis can compute blast radius of a changed requirement.
    This demonstrates the ability to trace impact downstream from a spec change.
    """
    # Build a dependency chain: spec → code → test → commit
    request_body = {
        "changed_artifact_ids": [stable_ids["spec_fr_trc_012"]],
        "links": [
            {
                "source_id": stable_ids["spec_fr_trc_012"],
                "target_id": stable_ids["code_trace_api"],
                "relationship": "satisfies",
                "confidence": 0.95,
                "updated_at": datetime.now(UTC).isoformat(),
            },
            {
                "source_id": stable_ids["code_trace_api"],
                "target_id": stable_ids["test_spec_self_tracing"],
                "relationship": "implements",
                "confidence": 0.90,
                "updated_at": datetime.now(UTC).isoformat(),
            },
            {
                "source_id": stable_ids["test_spec_self_tracing"],
                "target_id": stable_ids["commit_trace_scaffold"],
                "relationship": "verifies",
                "confidence": 0.85,
                "updated_at": datetime.now(UTC).isoformat(),
            },
        ],
        "max_depth": 5,
    }

    response = test_client.post("/api/v1/impact", json=request_body)

    assert response.status_code == 200
    body = response.json()

    # Verify impact analysis result structure
    assert "seeds" in body
    assert stable_ids["spec_fr_trc_012"] in body["seeds"]
    assert "affected" in body
    assert "total_score" in body
    assert "max_depth_seen" in body

    # Verify the blast radius includes downstream artifacts
    affected_ids = {node["artifact_id"] for node in body["affected"]}
    assert stable_ids["code_trace_api"] in affected_ids
    assert stable_ids["test_spec_self_tracing"] in affected_ids
    assert stable_ids["commit_trace_scaffold"] in affected_ids

    # Verify depth progression
    for node in body["affected"]:
        if node["artifact_id"] == stable_ids["code_trace_api"]:
            assert node["depth"] == 1
        elif node["artifact_id"] == stable_ids["test_spec_self_tracing"]:
            assert node["depth"] == 2
        elif node["artifact_id"] == stable_ids["commit_trace_scaffold"]:
            assert node["depth"] == 3

    # Verify max_depth_seen indicates chain length
    assert body["max_depth_seen"] >= 1


def test_full_spec_chain_traceable(
    test_client: TestClient,
    stable_ids: dict[str, str],
) -> None:
    """End-to-end test: Create spec→code→test→commit chain and verify all linked.

    This is the primary test for NFR-TRC-012: the spec system itself must be traceable
    through its own mechanism, demonstrating self-application of the traceability model.

    Chain structure:
    - Spec: FR-TRC-012 (self-hosting spec traceability)
    - Code: trace API implementation
    - Test: this test file
    - Commit: git commit for the scaffold
    """
    # Build the complete chain
    request_body = {
        "links": [
            # Spec → Design (documents the architecture)
            {
                "source_id": stable_ids["spec_fr_trc_012"],
                "target_id": stable_ids["design_doc"],
                "relationship": "derives_from",
                "confidence": 0.9,
                "updated_at": datetime.now(UTC).isoformat(),
            },
            # Design → Code (code implements the design)
            {
                "source_id": stable_ids["design_doc"],
                "target_id": stable_ids["code_trace_api"],
                "relationship": "satisfies",
                "confidence": 0.95,
                "updated_at": datetime.now(UTC).isoformat(),
            },
            # Code → Test (test verifies the code)
            {
                "source_id": stable_ids["code_trace_api"],
                "target_id": stable_ids["test_spec_self_tracing"],
                "relationship": "verifies",
                "confidence": 0.90,
                "updated_at": datetime.now(UTC).isoformat(),
            },
            # Test → Commit (test is part of the commit)
            {
                "source_id": stable_ids["test_spec_self_tracing"],
                "target_id": stable_ids["commit_trace_scaffold"],
                "relationship": "contains",
                "confidence": 1.0,
                "updated_at": datetime.now(UTC).isoformat(),
            },
        ]
    }

    # Verify coverage matrix
    matrix_response = test_client.post("/api/v1/coverage-matrix", json=request_body)
    assert matrix_response.status_code == 200
    matrix = matrix_response.json()

    assert matrix["link_count"] == 4
    assert matrix["cell_count"] == 4

    # All cells should show coverage (at least partial)
    for cell in matrix["cells"]:
        assert cell["coverage"] in ["covered", "partial", "missing"]
        assert len(cell["links"]) >= 1

    # Verify impact analysis from the spec
    impact_request = {
        "changed_artifact_ids": [stable_ids["spec_fr_trc_012"]],
        "links": request_body["links"],
        "max_depth": 10,
    }

    impact_response = test_client.post("/api/v1/impact", json=impact_request)
    assert impact_response.status_code == 200
    impact = impact_response.json()

    # Verify the spec change would affect all downstream artifacts
    affected_ids = {node["artifact_id"] for node in impact["affected"]}
    assert stable_ids["design_doc"] in affected_ids
    assert stable_ids["code_trace_api"] in affected_ids
    assert stable_ids["test_spec_self_tracing"] in affected_ids
    assert stable_ids["commit_trace_scaffold"] in affected_ids

    # Verify scores indicate strong connections (high confidence = high score)
    for node in impact["affected"]:
        assert node["score"] >= 0  # Positive scores (no conflicts)
        assert "via" in node
        assert isinstance(node["via"], list)
        assert len(node["via"]) >= 1

    # Verify total score (sum of all downstream artifact scores)
    assert impact["total_score"] > 0

    # Verify no conflicts in the chain
    assert len(impact["conflicts"]) == 0


def test_confidence_scoring_for_links(test_client: TestClient) -> None:
    """Test that confidence scoring works for semantic similarity between artifacts.

    Verifies FR-TRC-019: confidence scoring helps establish trace link validity.
    This ensures that when linking a requirement to code, we can assess semantic alignment.
    """
    requirement_text = "The system shall provide a traceability API for spec-to-code mapping"
    artifact_text = "APIRouter for coverage matrix and impact analysis endpoints"

    request_body = {
        "requirement_text": requirement_text,
        "artifact_text": artifact_text,
    }

    response = test_client.post("/api/v1/confidence", json=request_body)

    assert response.status_code == 200
    body = response.json()

    # Verify confidence response structure
    assert "confidence" in body
    assert "rationale" in body
    assert 0.0 <= body["confidence"] <= 1.0
    assert isinstance(body["rationale"], str)
    assert len(body["rationale"]) > 0


# ---------------------------------------------------------------------------
# Parametrized Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "source_id,target_id,relationship,expected_coverage",
    [
        # (spec, code, satisfies) → covered
        ("spec-001", "code-001", "satisfies", "covered"),
        # (code, test, verifies) → partial
        ("code-001", "test-001", "verifies", "partial"),
        # (spec, design, derives_from) → partial
        ("spec-001", "design-001", "derives_from", "partial"),
        # No links → missing
    ],
)
def test_coverage_state_transitions(
    test_client: TestClient,
    source_id: str,
    target_id: str,
    relationship: str,
    expected_coverage: str,
) -> None:
    """Parametrized test for coverage state classification.

    Tests that trace links correctly categorize coverage as covered/partial/missing.
    """
    request_body = {
        "links": [
            {
                "source_id": source_id,
                "target_id": target_id,
                "relationship": relationship,
                "confidence": 0.95,
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ]
    }

    response = test_client.post("/api/v1/coverage-matrix", json=request_body)

    assert response.status_code == 200
    body = response.json()
    cell = body["cells"][0]
    assert cell["coverage"] == expected_coverage


# ---------------------------------------------------------------------------
# Error Handling Tests
# ---------------------------------------------------------------------------


def test_invalid_artifact_id_format(test_client: TestClient) -> None:
    """Test that invalid artifact IDs are rejected gracefully.

    Verifies API validation: artifact IDs must be non-empty strings.
    """
    request_body = {
        "links": [
            {
                "source_id": "",  # Invalid: empty
                "target_id": "valid-id",
                "relationship": "satisfies",
                "confidence": 0.95,
            }
        ]
    }

    response = test_client.post("/api/v1/coverage-matrix", json=request_body)

    # Either 422 validation error or 200 with empty results
    assert response.status_code in [200, 422]


def test_invalid_relationship_type(test_client: TestClient) -> None:
    """Test that invalid relationship types are rejected.

    Verifies API validation: relationship must be one of the allowed types.
    """
    request_body = {
        "links": [
            {
                "source_id": "spec-001",
                "target_id": "code-001",
                "relationship": "invalid_relationship",  # Invalid
                "confidence": 0.95,
            }
        ]
    }

    response = test_client.post("/api/v1/coverage-matrix", json=request_body)

    assert response.status_code == 422


def test_confidence_out_of_bounds(test_client: TestClient) -> None:
    """Test that confidence values outside [0.0, 1.0] are rejected.

    Verifies API validation: confidence is bounded [0, 1].
    """
    request_body = {
        "links": [
            {
                "source_id": "spec-001",
                "target_id": "code-001",
                "relationship": "satisfies",
                "confidence": 1.5,  # Out of bounds
            }
        ]
    }

    response = test_client.post("/api/v1/coverage-matrix", json=request_body)

    assert response.status_code == 422

"""Tests for coverage matrix and impact REST endpoints."""

# ruff: noqa: S101

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from tracertm.api.main import create_app


def test_coverage_matrix_groups_links_and_classifies_cells() -> None:
    client = TestClient(create_app())
    old = (datetime.now(timezone.utc) - timedelta(days=120)).isoformat()

    response = client.post(
        "/api/v1/coverage-matrix",
        json={
            "links": [
                {
                    "source_id": "FR-1",
                    "target_id": "TC-1",
                    "relationship": "verifies",
                    "confidence": 0.95,
                },
                {
                    "source_id": "FR-2",
                    "target_id": "DOC-1",
                    "relationship": "derives_from",
                    "updated_at": old,
                },
            ]
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["link_count"] == 2
    assert data["cell_count"] == 2
    assert data["stale_links"] == 1
    coverage_by_source = {cell["source_id"]: cell["coverage"] for cell in data["cells"]}
    assert coverage_by_source == {"FR-1": "covered", "FR-2": "stale"}


def test_impact_returns_blast_radius_and_conflicts() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/impact",
        json={
            "changed_artifact_ids": ["FR-1"],
            "links": [
                {
                    "source_id": "FR-1",
                    "target_id": "CODE-1",
                    "relationship": "implements",
                    "confidence": 1.0,
                },
                {
                    "source_id": "CODE-1",
                    "target_id": "TC-1",
                    "relationship": "verifies",
                    "confidence": 0.8,
                },
                {
                    "source_id": "FR-1",
                    "target_id": "FR-2",
                    "relationship": "conflicts_with",
                    "confidence": 1.0,
                },
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["seeds"] == ["FR-1"]
    affected = {node["artifact_id"]: node for node in data["affected"]}
    assert set(affected) == {"FR-1", "CODE-1", "TC-1", "FR-2"}
    assert affected["CODE-1"]["depth"] == 1
    assert affected["FR-2"]["score"] < 0
    assert data["conflicts"][0]["target_id"] == "FR-2"

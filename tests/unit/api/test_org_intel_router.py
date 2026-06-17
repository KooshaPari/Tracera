"""Unit tests for the Org-Intel router.

Covers:
- GET /api/v1/org-intel/health → 200 with pillar + status fields
- GET /api/v1/org-intel/metrics → 200 with required metric fields
- GET /api/v1/org-intel/teams → 200 with list of teams
- Default teams are seeded on first call to /teams
- MetricsResponse schema shape: total_artifacts (int), coverage_ratio (float), open_gaps (int)
- coverage_ratio is between 0.0 and 1.0
- Teams list is non-empty by default
- Each team has required schema fields
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tracertm.api.main import create_app
from tracertm.api.routers import org_intel as org_intel_module


@pytest.fixture(autouse=True)
def _reset_teams_store() -> None:
    """Clear the module-level teams store before each test for isolation."""
    org_intel_module._teams.clear()
    yield
    org_intel_module._teams.clear()


@pytest.fixture
def client() -> TestClient:
    """Return a TestClient wrapping the full FastAPI app."""
    app = create_app()
    return TestClient(app)


_BASE_URL = "/api/v1/org-intel"


class TestOrgIntelHealth:
    """GET /org-intel/health endpoint."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """Health endpoint must return HTTP 200."""
        response = client.get(f"{_BASE_URL}/health")
        assert response.status_code == 200

    def test_health_body_has_status_ok(self, client: TestClient) -> None:
        """Health body must contain status=ok."""
        response = client.get(f"{_BASE_URL}/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_body_identifies_pillar(self, client: TestClient) -> None:
        """Health body must identify the org_intel pillar."""
        response = client.get(f"{_BASE_URL}/health")
        data = response.json()
        assert data["pillar"] == "org_intel"


class TestOrgIntelMetrics:
    """GET /org-intel/metrics endpoint."""

    def test_metrics_returns_200(self, client: TestClient) -> None:
        """GET /metrics returns HTTP 200."""
        response = client.get(f"{_BASE_URL}/metrics")
        assert response.status_code == 200

    def test_metrics_has_total_artifacts_field(self, client: TestClient) -> None:
        """Metrics response includes total_artifacts as an integer."""
        response = client.get(f"{_BASE_URL}/metrics")
        data = response.json()
        assert "total_artifacts" in data
        assert isinstance(data["total_artifacts"], int)

    def test_metrics_has_coverage_ratio_field(self, client: TestClient) -> None:
        """Metrics response includes coverage_ratio as a float."""
        response = client.get(f"{_BASE_URL}/metrics")
        data = response.json()
        assert "coverage_ratio" in data
        assert isinstance(data["coverage_ratio"], float)

    def test_metrics_has_open_gaps_field(self, client: TestClient) -> None:
        """Metrics response includes open_gaps as an integer."""
        response = client.get(f"{_BASE_URL}/metrics")
        data = response.json()
        assert "open_gaps" in data
        assert isinstance(data["open_gaps"], int)

    def test_metrics_coverage_ratio_between_0_and_1(self, client: TestClient) -> None:
        """coverage_ratio must be in the range [0.0, 1.0]."""
        response = client.get(f"{_BASE_URL}/metrics")
        ratio = response.json()["coverage_ratio"]
        assert 0.0 <= ratio <= 1.0

    def test_metrics_total_artifacts_non_negative(self, client: TestClient) -> None:
        """total_artifacts must be >= 0."""
        response = client.get(f"{_BASE_URL}/metrics")
        assert response.json()["total_artifacts"] >= 0

    def test_metrics_open_gaps_non_negative(self, client: TestClient) -> None:
        """open_gaps must be >= 0."""
        response = client.get(f"{_BASE_URL}/metrics")
        assert response.json()["open_gaps"] >= 0

    def test_metrics_reflects_team_count(self, client: TestClient) -> None:
        """total_artifacts scales with team count (teams seeded first)."""
        # Seed teams via the /teams endpoint
        client.get(f"{_BASE_URL}/teams")
        team_count = len(org_intel_module._teams)

        metrics_resp = client.get(f"{_BASE_URL}/metrics")
        data = metrics_resp.json()
        # Router computes total_artifacts = len(_teams) * 10
        assert data["total_artifacts"] == team_count * 10


class TestOrgIntelTeams:
    """GET /org-intel/teams endpoint."""

    def test_teams_returns_200(self, client: TestClient) -> None:
        """GET /teams returns HTTP 200."""
        response = client.get(f"{_BASE_URL}/teams")
        assert response.status_code == 200

    def test_teams_returns_list(self, client: TestClient) -> None:
        """GET /teams response body is a JSON array."""
        response = client.get(f"{_BASE_URL}/teams")
        assert isinstance(response.json(), list)

    def test_teams_default_seeded_non_empty(self, client: TestClient) -> None:
        """GET /teams seeds default teams when store is empty; list is non-empty."""
        response = client.get(f"{_BASE_URL}/teams")
        assert len(response.json()) > 0

    def test_teams_default_seed_count_is_three(self, client: TestClient) -> None:
        """Default seed produces exactly 3 teams."""
        response = client.get(f"{_BASE_URL}/teams")
        assert len(response.json()) == 3

    def test_teams_each_has_id_field(self, client: TestClient) -> None:
        """Each team in the list has a non-empty 'id' field."""
        response = client.get(f"{_BASE_URL}/teams")
        for team in response.json():
            assert "id" in team
            assert team["id"]

    def test_teams_each_has_name_field(self, client: TestClient) -> None:
        """Each team in the list has a non-empty 'name' field."""
        response = client.get(f"{_BASE_URL}/teams")
        for team in response.json():
            assert "name" in team
            assert team["name"]

    def test_teams_each_has_description_field(self, client: TestClient) -> None:
        """Each team has a 'description' field."""
        response = client.get(f"{_BASE_URL}/teams")
        for team in response.json():
            assert "description" in team

    def test_teams_each_has_members_list(self, client: TestClient) -> None:
        """Each team has a 'members' field that is a list."""
        response = client.get(f"{_BASE_URL}/teams")
        for team in response.json():
            assert "members" in team
            assert isinstance(team["members"], list)

    def test_teams_each_has_timestamps(self, client: TestClient) -> None:
        """Each team has created_at and updated_at timestamp fields."""
        response = client.get(f"{_BASE_URL}/teams")
        for team in response.json():
            assert "created_at" in team
            assert "updated_at" in team

    def test_teams_second_call_returns_same_count(self, client: TestClient) -> None:
        """Calling GET /teams twice does not duplicate the default teams."""
        first = client.get(f"{_BASE_URL}/teams").json()
        second = client.get(f"{_BASE_URL}/teams").json()
        assert len(first) == len(second)

    def test_teams_known_default_names_present(self, client: TestClient) -> None:
        """Default seeded teams include 'Platform Team', 'Product Team', 'Security Team'."""
        response = client.get(f"{_BASE_URL}/teams")
        names = {t["name"] for t in response.json()}
        assert "Platform Team" in names
        assert "Product Team" in names
        assert "Security Team" in names

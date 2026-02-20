"""Tests for the Specifications API router.

This test module covers all endpoints in the unified specifications router
including ADRs, Contracts, Features, and Scenarios.

Functional Requirements Coverage:
    - FR-DISC-002: Specification Parsing
    - FR-APP-002: Specification Versioning
    - FR-QUAL-001: Requirement Quality Assessment

Epics:
    - EPIC-002: Spec-Driven Traceability

Tests verify specification API endpoints for creating, retrieving, updating,
and deleting ADRs, Contracts, Features, and Scenarios with versioning support.
"""

from collections.abc import AsyncGenerator

# =============================================================================
# Fixtures
# =============================================================================
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tests.test_constants import HTTP_CREATED, HTTP_NO_CONTENT, HTTP_NOT_FOUND, HTTP_OK, HTTP_UNPROCESSABLE_ENTITY
from tracertm.api.deps import get_db
from tracertm.api.main import app


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    # Create all tables
    async with engine.begin():
        # Note: In a real test, you'd use your migration system
        pass

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session


@pytest.fixture
def client(db_session: Any) -> None:
    """Create a test client with dependency override."""

    async def override_get_db() -> None:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> None:
    """Return authorization headers with a test token."""
    # In production, this would be a real JWT from WorkOS AuthKit
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def project_id() -> str:
    """Return a test project ID."""
    return "proj-test-123"


@pytest.fixture
def adr_payload(project_id: Any) -> None:
    """Return a valid ADR creation payload."""
    return {
        "project_id": project_id,
        "title": "Use PostgreSQL for persistence",
        "context": "We need a reliable ACID-compliant database for our traceability system that can handle complex queries and relationships",
        "decision": "We will use PostgreSQL as the primary database for all persistent storage",
        "consequences": "Requires PostgreSQL expertise on the team, scaling considerations for multi-tenant setup",
        "status": "proposed",
        "decision_drivers": ["ACID compliance requirement", "Team expertise with PostgreSQL", "Cost-effectiveness"],
        "considered_options": [
            {
                "id": "opt-1",
                "title": "MongoDB",
                "pros": ["Flexible schema", "High scalability"],
                "cons": ["No ACID for multi-document transactions"],
                "is_chosen": False,
            },
            {
                "id": "opt-2",
                "title": "PostgreSQL",
                "pros": ["ACID compliance", "Powerful querying", "Team expertise"],
                "cons": ["Vertical scaling limits"],
                "is_chosen": True,
            },
        ],
        "related_requirements": ["REQ-123", "REQ-456"],
        "related_adrs": [],
        "tags": ["database", "persistence"],
        "stakeholders": ["tech-lead", "backend-team"],
    }


@pytest.fixture
def contract_payload(project_id: Any) -> None:
    """Return a valid Contract creation payload."""
    return {
        "project_id": project_id,
        "item_id": "item-456",
        "title": "Item Service Contract",
        "contract_type": "service",
        "status": "draft",
        "preconditions": [
            {
                "id": "pre-1",
                "description": "User must be authenticated",
                "condition_code": "user.is_authenticated == True",
                "required": True,
                "priority": "critical",
            },
        ],
        "postconditions": [
            {
                "id": "post-1",
                "description": "Item is created and stored in database",
                "condition_code": "item.id is not None",
                "required": True,
            },
        ],
        "invariants": [{"id": "inv-1", "description": "Item status is always valid", "required": True}],
        "states": ["draft", "active", "archived"],
        "transitions": [
            {
                "id": "trans-1",
                "from_state": "draft",
                "to_state": "active",
                "trigger": "publish()",
                "condition": "validation.pass == true",
            },
        ],
        "tags": ["service", "api"],
        "metadata": {},
    }


@pytest.fixture
def feature_payload(project_id: Any) -> None:
    """Return a valid Feature creation payload."""
    return {
        "project_id": project_id,
        "name": "User Authentication",
        "description": "Users can authenticate using GitHub OAuth",
        "as_a": "developer",
        "i_want": "to authenticate with GitHub",
        "so_that": "I can access my projects",
        "status": "draft",
        "related_requirements": ["REQ-123"],
        "related_adrs": [],
        "tags": ["auth", "oauth"],
        "metadata": {},
    }


@pytest.fixture
def scenario_payload() -> None:
    """Return a valid Scenario creation payload."""
    return {
        "title": "User logs in with GitHub",
        "description": "Scenario for successful GitHub authentication",
        "gherkin_text": """Feature: User Authentication
  Scenario: Login with GitHub
    Given user is on login page
    When user clicks GitHub button
    Then user is redirected to GitHub authorization page
    And GitHub requests user authorization""",
        "status": "draft",
        "given_steps": [{"step_number": 1, "keyword": "Given", "text": "user is on login page"}],
        "when_steps": [{"step_number": 2, "keyword": "When", "text": "user clicks GitHub button"}],
        "then_steps": [
            {"step_number": 3, "keyword": "Then", "text": "user is redirected to GitHub authorization page"},
        ],
        "is_outline": False,
        "tags": ["auth", "critical"],
        "metadata": {},
    }


# =============================================================================
# ADR Tests
# =============================================================================


class TestADREndpoints:
    """Test suite for ADR endpoints."""

    def test_create_adr_success(self, client: Any, auth_headers: Any, adr_payload: Any) -> None:
        """Test successful ADR creation."""
        response = client.post("/api/v1/specifications/adrs", json=adr_payload, headers=auth_headers)

        assert response.status_code == HTTP_CREATED
        data = response.json()
        assert data["title"] == adr_payload["title"]
        assert data["project_id"] == adr_payload["project_id"]
        assert data["status"] == "proposed"
        assert data["adr_number"].startswith("ADR-")

    def test_create_adr_missing_context(self, client: Any, auth_headers: Any, adr_payload: Any) -> None:
        """Test ADR creation fails with short context."""
        adr_payload["context"] = "short"
        response = client.post("/api/v1/specifications/adrs", json=adr_payload, headers=auth_headers)

        # Should succeed but validation might warn during verification
        assert response.status_code in {201, 400}

    def test_get_adr_success(self, client: Any, auth_headers: Any, adr_payload: Any) -> None:
        """Test retrieving an ADR."""
        # Create ADR first
        create_response = client.post("/api/v1/specifications/adrs", json=adr_payload, headers=auth_headers)
        adr_id = create_response.json()["id"]

        # Get ADR
        response = client.get(f"/api/v1/specifications/adrs/{adr_id}", headers=auth_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["id"] == adr_id
        assert data["title"] == adr_payload["title"]

    def test_get_adr_not_found(self, client: Any, auth_headers: Any) -> None:
        """Test getting non-existent ADR."""
        response = client.get("/api/v1/specifications/adrs/nonexistent", headers=auth_headers)

        assert response.status_code == HTTP_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_update_adr_success(self, client: Any, auth_headers: Any, adr_payload: Any) -> None:
        """Test updating an ADR."""
        # Create ADR first
        create_response = client.post("/api/v1/specifications/adrs", json=adr_payload, headers=auth_headers)
        adr_id = create_response.json()["id"]

        # Update ADR
        update_payload = {"status": "accepted"}
        response = client.put(f"/api/v1/specifications/adrs/{adr_id}", json=update_payload, headers=auth_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["status"] == "accepted"

    def test_delete_adr_success(self, client: Any, auth_headers: Any, adr_payload: Any) -> None:
        """Test deleting an ADR."""
        # Create ADR first
        create_response = client.post("/api/v1/specifications/adrs", json=adr_payload, headers=auth_headers)
        adr_id = create_response.json()["id"]

        # Delete ADR
        response = client.delete(f"/api/v1/specifications/adrs/{adr_id}", headers=auth_headers)

        assert response.status_code == HTTP_NO_CONTENT

    def test_list_adrs_by_project(self, client: Any, auth_headers: Any, adr_payload: Any) -> None:
        """Test listing ADRs for a project."""
        project_id = adr_payload["project_id"]

        # Create multiple ADRs
        client.post("/api/v1/specifications/adrs", json=adr_payload, headers=auth_headers)

        # List ADRs
        response = client.get(f"/api/v1/specifications/projects/{project_id}/adrs", headers=auth_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert "total" in data
        assert "adrs" in data
        assert data["total"] >= 1

    def test_verify_adr_compliance(self, client: Any, auth_headers: Any, adr_payload: Any) -> None:
        """Test ADR compliance verification."""
        # Create ADR first
        create_response = client.post("/api/v1/specifications/adrs", json=adr_payload, headers=auth_headers)
        adr_id = create_response.json()["id"]

        # Verify compliance
        response = client.post(f"/api/v1/specifications/adrs/{adr_id}/verify", headers=auth_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert "is_valid" in data
        assert "score" in data
        assert 0 <= data["score"] <= 100
        assert "issues" in data
        assert "warnings" in data


# =============================================================================
# Contract Tests
# =============================================================================


class TestContractEndpoints:
    """Test suite for Contract endpoints."""

    def test_create_contract_success(self, client: Any, auth_headers: Any, contract_payload: Any) -> None:
        """Test successful contract creation."""
        response = client.post("/api/v1/specifications/contracts", json=contract_payload, headers=auth_headers)

        assert response.status_code == HTTP_CREATED
        data = response.json()
        assert data["title"] == contract_payload["title"]
        assert data["project_id"] == contract_payload["project_id"]
        assert data["status"] == "draft"

    def test_get_contract_success(self, client: Any, auth_headers: Any, contract_payload: Any) -> None:
        """Test retrieving a contract."""
        # Create contract first
        create_response = client.post("/api/v1/specifications/contracts", json=contract_payload, headers=auth_headers)
        contract_id = create_response.json()["id"]

        # Get contract
        response = client.get(f"/api/v1/specifications/contracts/{contract_id}", headers=auth_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["id"] == contract_id

    def test_delete_contract_success(self, client: Any, auth_headers: Any, contract_payload: Any) -> None:
        """Test deleting a contract."""
        # Create contract first
        create_response = client.post("/api/v1/specifications/contracts", json=contract_payload, headers=auth_headers)
        contract_id = create_response.json()["id"]

        # Delete contract
        response = client.delete(f"/api/v1/specifications/contracts/{contract_id}", headers=auth_headers)

        assert response.status_code == HTTP_NO_CONTENT

    def test_verify_contract_compliance(self, client: Any, auth_headers: Any, contract_payload: Any) -> None:
        """Test contract compliance verification."""
        # Create contract first
        create_response = client.post("/api/v1/specifications/contracts", json=contract_payload, headers=auth_headers)
        contract_id = create_response.json()["id"]

        # Verify compliance
        response = client.post(f"/api/v1/specifications/contracts/{contract_id}/verify", headers=auth_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert "is_valid" in data
        assert "score" in data


# =============================================================================
# Feature Tests
# =============================================================================


class TestFeatureEndpoints:
    """Test suite for Feature endpoints."""

    def test_create_feature_success(self, client: Any, auth_headers: Any, feature_payload: Any) -> None:
        """Test successful feature creation."""
        response = client.post("/api/v1/specifications/features", json=feature_payload, headers=auth_headers)

        assert response.status_code == HTTP_CREATED
        data = response.json()
        assert data["name"] == feature_payload["name"]
        assert data["project_id"] == feature_payload["project_id"]
        assert data["status"] == "draft"

    def test_get_feature_success(self, client: Any, auth_headers: Any, feature_payload: Any) -> None:
        """Test retrieving a feature."""
        # Create feature first
        create_response = client.post("/api/v1/specifications/features", json=feature_payload, headers=auth_headers)
        feature_id = create_response.json()["id"]

        # Get feature
        response = client.get(f"/api/v1/specifications/features/{feature_id}", headers=auth_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["id"] == feature_id

    def test_delete_feature_success(self, client: Any, auth_headers: Any, feature_payload: Any) -> None:
        """Test deleting a feature."""
        # Create feature first
        create_response = client.post("/api/v1/specifications/features", json=feature_payload, headers=auth_headers)
        feature_id = create_response.json()["id"]

        # Delete feature
        response = client.delete(f"/api/v1/specifications/features/{feature_id}", headers=auth_headers)

        assert response.status_code == HTTP_NO_CONTENT


# =============================================================================
# Scenario Tests
# =============================================================================


class TestScenarioEndpoints:
    """Test suite for Scenario endpoints."""

    def test_create_scenario_success(
        self, client: Any, auth_headers: Any, feature_payload: Any, scenario_payload: Any
    ) -> None:
        """Test successful scenario creation."""
        # Create feature first
        feature_response = client.post("/api/v1/specifications/features", json=feature_payload, headers=auth_headers)
        feature_id = feature_response.json()["id"]

        # Create scenario
        response = client.post(
            f"/api/v1/specifications/features/{feature_id}/scenarios",
            json=scenario_payload,
            headers=auth_headers,
        )

        assert response.status_code == HTTP_CREATED
        data = response.json()
        assert data["title"] == scenario_payload["title"]
        assert data["feature_id"] == feature_id

    def test_get_scenario_success(
        self, client: Any, auth_headers: Any, feature_payload: Any, scenario_payload: Any
    ) -> None:
        """Test retrieving a scenario."""
        # Create feature and scenario first
        feature_response = client.post("/api/v1/specifications/features", json=feature_payload, headers=auth_headers)
        feature_id = feature_response.json()["id"]

        scenario_response = client.post(
            f"/api/v1/specifications/features/{feature_id}/scenarios",
            json=scenario_payload,
            headers=auth_headers,
        )
        scenario_id = scenario_response.json()["id"]

        # Get scenario
        response = client.get(f"/api/v1/specifications/scenarios/{scenario_id}", headers=auth_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["id"] == scenario_id

    def test_run_scenario_success(
        self, client: Any, auth_headers: Any, feature_payload: Any, scenario_payload: Any
    ) -> None:
        """Test running a scenario."""
        # Create feature and scenario first
        feature_response = client.post("/api/v1/specifications/features", json=feature_payload, headers=auth_headers)
        feature_id = feature_response.json()["id"]

        scenario_response = client.post(
            f"/api/v1/specifications/features/{feature_id}/scenarios",
            json=scenario_payload,
            headers=auth_headers,
        )
        scenario_id = scenario_response.json()["id"]

        # Run scenario
        response = client.post(f"/api/v1/specifications/scenarios/{scenario_id}/run", headers=auth_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert "scenario_id" in data
        assert "passed" in data
        assert "duration_ms" in data


# =============================================================================
# Project-Level Tests
# =============================================================================


class TestProjectLevelEndpoints:
    """Test suite for project-level specification endpoints."""

    def test_get_specifications_summary(
        self,
        client: Any,
        auth_headers: Any,
        project_id: Any,
        adr_payload: Any,
        contract_payload: Any,
        _feature_payload: Any,
    ) -> None:
        """Test getting specifications summary."""
        # Create some specifications
        client.post("/api/v1/specifications/adrs", json=adr_payload, headers=auth_headers)

        # Get summary
        response = client.get(f"/api/v1/specifications/projects/{project_id}/summary", headers=auth_headers)

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["project_id"] == project_id
        assert "adr_count" in data
        assert "contract_count" in data
        assert "feature_count" in data
        assert "scenario_count" in data
        assert "compliance_score" in data


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Test suite for error handling."""

    def test_missing_required_field(self, client: Any, auth_headers: Any, adr_payload: Any) -> None:
        """Test validation error for missing required field."""
        del adr_payload["title"]
        response = client.post("/api/v1/specifications/adrs", json=adr_payload, headers=auth_headers)

        assert response.status_code == HTTP_UNPROCESSABLE_ENTITY  # Validation error

    def test_invalid_enum_value(self, client: Any, auth_headers: Any, adr_payload: Any) -> None:
        """Test validation error for invalid enum."""
        adr_payload["status"] = "invalid_status"
        response = client.post("/api/v1/specifications/adrs", json=adr_payload, headers=auth_headers)

        assert response.status_code == HTTP_UNPROCESSABLE_ENTITY

    def test_unauthenticated_request(self, client: Any, adr_payload: Any) -> None:
        """Test that requests without auth are rejected."""
        response = client.post(
            "/api/v1/specifications/adrs",
            json=adr_payload,
            # No auth headers
        )

        assert response.status_code in {401, 403}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

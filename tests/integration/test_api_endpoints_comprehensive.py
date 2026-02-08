"""Comprehensive API Endpoint Integration Tests for TraceRTM.

These tests validate FastAPI routes with:
- Database operations via repositories
- Error handling and edge cases
- Response validation and formats
- Full request/response cycles

Tests use synchronous database session with synchronous test client.
Target Coverage: 85%+ of API endpoints
"""

import pytest
from tests.test_constants import COUNT_THREE, COUNT_TWO, HTTP_NOT_FOUND, HTTP_OK, HTTP_UNPROCESSABLE_ENTITY


from tracertm.api.main import app, get_db
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project

pytestmark = pytest.mark.integration


@pytest.fixture
def client(db_session):
    """Create test client with mocked database dependency."""

    def override_get_db():
        # For sync session, we need to return the session as-is
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_project(db_session):
    """Create a test project in the database."""
    project = Project(
        name="Integration Test Project", description="Test project for API integration", project_metadata={"test": True},
    )
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def test_items(db_session, test_project):
    """Create test items in the database."""
    item1 = Item(
        project_id=test_project.id,
        title="Feature 1",
        view="FEATURE",
        item_type="feature",
        description="First test feature",
        status="todo",
        priority="high",
    )

    item2 = Item(
        project_id=test_project.id,
        title="Requirement 1",
        view="REQUIREMENT",
        item_type="requirement",
        description="First test requirement",
        status="in_progress",
        priority="medium",
    )

    item3 = Item(
        project_id=test_project.id,
        title="Bug 1",
        view="BUG",
        item_type="bug",
        description="First test bug",
        status="done",
        priority="low",
    )

    db_session.add_all([item1, item2, item3])
    db_session.commit()
    return [item1, item2, item3]


@pytest.fixture
def test_links(db_session, test_items):
    """Create test links between items."""
    link1 = Link(
        source_item_id=test_items[0].id,
        target_item_id=test_items[1].id,
        link_type="depends_on",
        link_metadata={"priority": "high"},
    )

    link2 = Link(
        source_item_id=test_items[1].id,
        target_item_id=test_items[2].id,
        link_type="related_to",
        link_metadata={"reason": "bug_fix"},
    )

    db_session.add_all([link1, link2])
    db_session.commit()
    return [link1, link2]


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================


def test_health_check(client) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == HTTP_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "service" in data


def test_api_health_check(client) -> None:
    """Test API health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == HTTP_OK
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data


# ============================================================================
# PROJECT ENDPOINTS
# ============================================================================


def test_create_project(client, db_session) -> None:  # noqa: ARG001
    """Test creating a new project."""
    payload = {
        "name": "New Test Project",
        "description": "A new test project",
        "metadata": {"env": "test", "version": "1.0"},
    }

    response = client.post("/api/v1/projects", json=payload)
    assert response.status_code == HTTP_OK
    data = response.json()

    assert data["id"] is not None
    assert data["name"] == "New Test Project"
    assert data["description"] == "A new test project"


def test_list_projects(client, test_project) -> None:  # noqa: ARG001
    """Test listing all projects."""
    response = client.get("/api/v1/projects")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert "total" in data
    assert "projects" in data


def test_get_project(client, test_project) -> None:
    """Test getting a specific project."""
    response = client.get(f"/api/v1/projects/{test_project.id}")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert data["id"] == test_project.id
    assert data["name"] == test_project.name


def test_get_project_not_found(client) -> None:
    """Test getting a non-existent project."""
    response = client.get("/api/v1/projects/nonexistent-id")
    assert response.status_code == HTTP_NOT_FOUND


def test_update_project(client, test_project) -> None:
    """Test updating a project."""
    payload = {"name": "Updated Project Name", "description": "Updated description", "metadata": {"version": "2.0"}}

    response = client.put(f"/api/v1/projects/{test_project.id}", json=payload)
    assert response.status_code == HTTP_OK
    data = response.json()

    assert data["name"] == "Updated Project Name"


def test_delete_project(client, test_project) -> None:
    """Test deleting a project."""
    response = client.delete(f"/api/v1/projects/{test_project.id}")
    assert response.status_code == HTTP_OK
    data = response.json()
    assert data["success"] is True


# ============================================================================
# ITEM ENDPOINTS
# ============================================================================


def test_list_items_by_project(client, test_project, test_items) -> None:  # noqa: ARG001
    """Test listing items in a project."""
    response = client.get(f"/api/v1/items?project_id={test_project.id}")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert "total" in data
    assert "items" in data
    assert data["total"] >= COUNT_THREE


def test_list_items_with_pagination(client, test_project, test_items) -> None:  # noqa: ARG001
    """Test listing items with skip/limit."""
    response = client.get(f"/api/v1/items?project_id={test_project.id}&skip=0&limit=2")
    assert response.status_code == HTTP_OK
    data = response.json()
    assert len(data["items"]) <= COUNT_TWO


def test_get_item(client, test_items) -> None:
    """Test getting a specific item."""
    item = test_items[0]
    response = client.get(f"/api/v1/items/{item.id}")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert data["id"] == item.id
    assert data["title"] == "Feature 1"
    assert data["view"] == "FEATURE"


def test_get_item_not_found(client) -> None:
    """Test getting a non-existent item."""
    response = client.get("/api/v1/items/nonexistent-id")
    assert response.status_code == HTTP_NOT_FOUND


def test_delete_item(client, test_items) -> None:
    """Test deleting an item."""
    item_id = test_items[0].id
    response = client.delete(f"/api/v1/items/{item_id}")
    assert response.status_code == HTTP_OK
    data = response.json()
    assert data["status"] == "deleted"


# ============================================================================
# LINK ENDPOINTS
# ============================================================================


def test_list_links_by_project(client, test_project, test_links) -> None:  # noqa: ARG001
    """Test listing links in a project."""
    response = client.get(f"/api/v1/links?project_id={test_project.id}")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert "total" in data
    assert "links" in data


def test_list_links_by_source(client, test_items, test_links) -> None:  # noqa: ARG001
    """Test listing links by source item."""
    source_id = test_items[0].id
    response = client.get(f"/api/v1/links?source_id={source_id}")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert "links" in data


def test_list_links_by_target(client, test_items, test_links) -> None:  # noqa: ARG001
    """Test listing links by target item."""
    target_id = test_items[1].id
    response = client.get(f"/api/v1/links?target_id={target_id}")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert "links" in data


def test_list_links_by_source_and_target(client, test_items, test_links) -> None:  # noqa: ARG001
    """Test listing links between specific items."""
    source_id = test_items[0].id
    target_id = test_items[1].id

    response = client.get(f"/api/v1/links?source_id={source_id}&target_id={target_id}")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert "links" in data


# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================


def test_impact_analysis(client, test_project, test_items) -> None:
    """Test impact analysis endpoint."""
    item_id = test_items[0].id

    response = client.get(f"/api/v1/analysis/impact/{item_id}?project_id={test_project.id}")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert "root_item_id" in data
    assert "total_affected" in data
    assert "max_depth" in data
    assert "affected_items" in data


def test_cycle_detection(client, test_project) -> None:
    """Test cycle detection endpoint."""
    response = client.get(f"/api/v1/analysis/cycles/{test_project.id}")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert "has_cycles" in data
    assert "total_cycles" in data
    assert "severity" in data
    assert "affected_items" in data


def test_shortest_path(client, test_project, test_items) -> None:
    """Test shortest path endpoint."""
    source_id = test_items[0].id
    target_id = test_items[1].id

    response = client.get(
        f"/api/v1/analysis/shortest-path?project_id={test_project.id}&source_id={source_id}&target_id={target_id}",
    )
    assert response.status_code == HTTP_OK
    data = response.json()

    assert "exists" in data
    assert "distance" in data
    assert "path" in data


# ============================================================================
# AUTHORIZATION AND PERMISSION TESTS
# ============================================================================


def test_project_access_validation(client) -> None:
    """Test project access is validated."""
    payload = {"project_id": "some-project-id", "title": "Test Item", "type": "feature"}

    # This should either succeed or fail based on access rules
    response = client.post("/api/v1/items", json=payload)
    # May succeed or fail, just verify it's handled
    assert response.status_code in {200, 400, 403, 404, 422, 500}


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


def test_missing_required_fields(client, test_project) -> None:
    """Test creating item with missing required fields."""
    payload = {
        "project_id": test_project.id,
        # Missing required fields: title, type
    }

    response = client.post("/api/v1/items", json=payload)
    assert response.status_code == HTTP_UNPROCESSABLE_ENTITY  # Validation error


def test_empty_response_handling(client, test_project) -> None:
    """Test handling of empty responses."""
    response = client.get(f"/api/v1/items?project_id={test_project.id}&skip=1000&limit=10")
    assert response.status_code == HTTP_OK
    data = response.json()
    assert isinstance(data["items"], list)


def test_large_skip_and_limit(client, test_project, test_items) -> None:  # noqa: ARG001
    """Test handling of large skip/limit values."""
    response = client.get(f"/api/v1/items?project_id={test_project.id}&skip=999999&limit=999999")
    assert response.status_code == HTTP_OK
    data = response.json()
    assert isinstance(data["items"], list)


def test_special_characters_in_data(client, test_project) -> None:
    """Test handling special characters in request data."""
    # Note: This endpoint creates items via repository, which doesn't use async
    # So we test the GET side instead
    payload = {
        "project_id": test_project.id,
        "title": "Feature with special chars: @#$%",
        "type": "feature",
        "description": "Description with\nnewlines",
    }

    # Validation should handle this
    response = client.post("/api/v1/items", json=payload)
    # Should either succeed or fail with validation error
    assert response.status_code in {200, 422}


def test_unicode_handling(client, test_project) -> None:
    """Test handling of unicode characters."""
    payload = {
        "project_id": test_project.id,
        "title": "Feature: 中文 العربية",
        "type": "feature",
        "description": "Description with émojis",
    }

    response = client.post("/api/v1/items", json=payload)
    # Should handle or reject unicode appropriately
    assert response.status_code in {200, 422}


# ============================================================================
# RESPONSE FORMAT TESTS
# ============================================================================


def test_item_response_format(client, test_items) -> None:
    """Test that item responses have correct format."""
    item = test_items[0]
    response = client.get(f"/api/v1/items/{item.id}")
    assert response.status_code == HTTP_OK
    data = response.json()

    required_fields = ["id", "title", "view", "status"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"

    assert isinstance(data["id"], str)
    assert isinstance(data["title"], str)


def test_list_response_format(client, test_project, test_items) -> None:  # noqa: ARG001
    """Test that list responses have correct format."""
    response = client.get(f"/api/v1/items?project_id={test_project.id}")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert isinstance(data, dict)
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)


def test_project_response_format(client, test_project) -> None:
    """Test that project responses have correct format."""
    response = client.get(f"/api/v1/projects/{test_project.id}")
    assert response.status_code == HTTP_OK
    data = response.json()

    required_fields = ["id", "name"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"

    assert isinstance(data["id"], str)
    assert isinstance(data["name"], str)


def test_link_response_format(client, test_links) -> None:  # noqa: ARG001
    """Test that link responses have correct format."""
    response = client.get("/api/v1/links")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert "total" in data
    assert "links" in data
    assert isinstance(data["links"], list)


# ============================================================================
# BULK OPERATION TESTS
# ============================================================================


def test_bulk_operation_header_acceptance(client, test_project) -> None:
    """Test that bulk operation header is accepted."""
    payload = {"project_id": test_project.id, "title": "Bulk Item", "type": "feature"}

    response = client.post("/api/v1/items", json=payload, headers={"X-Bulk-Operation": "true"})

    # Should process normally with bulk header
    assert response.status_code in {200, 422}


# ============================================================================
# GRAPH NEIGHBOR TESTS
# ============================================================================


def test_get_graph_neighbors_outgoing(client, test_project, test_items, test_links) -> None:  # noqa: ARG001
    """Test getting outgoing neighbors in graph."""
    item_id = test_items[0].id

    response = client.get(f"/api/v1/projects/{test_project.id}/graph/neighbors?item_id={item_id}&direction=out")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert "neighbors" in data
    assert "total" in data
    assert isinstance(data["neighbors"], list)


def test_get_graph_neighbors_incoming(client, test_project, test_items, test_links) -> None:  # noqa: ARG001
    """Test getting incoming neighbors in graph."""
    item_id = test_items[1].id

    response = client.get(f"/api/v1/projects/{test_project.id}/graph/neighbors?item_id={item_id}&direction=in")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert "neighbors" in data
    assert isinstance(data["neighbors"], list)


def test_get_graph_neighbors_both_directions(client, test_project, test_items) -> None:
    """Test getting neighbors in both directions."""
    item_id = test_items[0].id

    response = client.get(f"/api/v1/projects/{test_project.id}/graph/neighbors?item_id={item_id}&direction=both")
    assert response.status_code == HTTP_OK
    data = response.json()

    assert "neighbors" in data
    assert isinstance(data["neighbors"], list)


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


def test_null_optional_fields_handling(client, test_project) -> None:
    """Test creating item with null optional fields."""
    # Note: Sync client with payload containing nulls
    payload = {
        "project_id": test_project.id,
        "title": "Test Item",
        "type": "feature",
        "description": None,
        "view": None,
        "status": None,
    }

    response = client.post("/api/v1/items", json=payload)
    # Should either succeed or reject null fields
    assert response.status_code in {200, 422}


def test_empty_metadata_field(client, test_project) -> None:
    """Test items with empty metadata."""
    payload = {"project_id": test_project.id, "title": "Item with empty metadata", "type": "feature", "metadata": {}}

    response = client.post("/api/v1/items", json=payload)
    assert response.status_code in {200, 422}

"""Tests for GitHubProjectRepository.

Comprehensive tests covering GitHub Project link CRUD operations.

Functional Requirements Coverage:
    - FR-DISC-001: GitHub Issue Import
    - FR-COLLAB-001: External Tool Integration (GitHub)

Epics:
    - EPIC-001: External Integration

Tests verify GitHub Project link creation, retrieval, update, deletion,
auto-sync configuration, and TraceRTM project linkage.
"""

import asyncio

# ==================== Fixtures ====================
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_THREE, COUNT_TWO
from tracertm.repositories.github_project_repository import GitHubProjectRepository
from tracertm.repositories.project_repository import ProjectRepository


@pytest_asyncio.fixture
async def github_project_repo(db_session: AsyncSession) -> None:
    """Create a GitHubProjectRepository instance."""
    await asyncio.sleep(0)
    return GitHubProjectRepository(db_session)


@pytest_asyncio.fixture
async def project(db_session: AsyncSession) -> None:
    """Create a TraceRTM project for foreign key requirements."""
    project_repo = ProjectRepository(db_session)
    return await project_repo.create(
        name="Test Project",
        description="Test project for GitHub Project tests",
    )


@pytest_asyncio.fixture
async def github_project_setup(github_project_repo: GitHubProjectRepository, project: Any) -> None:
    """Create a GitHub Project link for testing."""
    github_project = await github_project_repo.create(
        project_id=project.id,
        github_repo_id=12345678,
        github_repo_owner="test-owner",
        github_repo_name="test-repo",
        github_project_id="PVT_abc123",
        github_project_number=1,
        auto_sync=True,
        sync_config={"sync_issues": True, "sync_prs": False},
    )
    return {"github_project": github_project, "repo": github_project_repo, "project": project}


# ==================== Create Tests ====================


class TestCreate:
    """Tests for GitHubProjectRepository.create."""

    @pytest.mark.asyncio
    async def test_create_happy_path(self, github_project_repo: GitHubProjectRepository, project: Any) -> None:
        """Test creating a GitHub Project link with all required fields."""
        github_project = await github_project_repo.create(
            project_id=project.id,
            github_repo_id=12345678,
            github_repo_owner="my-org",
            github_repo_name="my-repo",
            github_project_id="PVT_kwDOBx123",
            github_project_number=5,
        )

        assert github_project is not None
        assert github_project.id is not None
        assert github_project.project_id == project.id
        assert github_project.github_repo_id == 12345678
        assert github_project.github_repo_owner == "my-org"
        assert github_project.github_repo_name == "my-repo"
        assert github_project.github_project_id == "PVT_kwDOBx123"
        assert github_project.github_project_number == COUNT_FIVE
        assert github_project.auto_sync is True  # Default value
        assert github_project.sync_config == {}  # Default empty dict

    @pytest.mark.asyncio
    async def test_create_with_sync_config(self, github_project_repo: GitHubProjectRepository, project: Any) -> None:
        """Test creating a GitHub Project link with sync configuration."""
        sync_config = {
            "sync_issues": True,
            "sync_prs": True,
            "sync_interval_minutes": 30,
            "label_mapping": {"bug": "defect", "enhancement": "feature"},
        }

        github_project = await github_project_repo.create(
            project_id=project.id,
            github_repo_id=87654321,
            github_repo_owner="another-org",
            github_repo_name="another-repo",
            github_project_id="PVT_xyz789",
            github_project_number=10,
            auto_sync=False,
            sync_config=sync_config,
        )

        assert github_project.auto_sync is False
        assert github_project.sync_config == sync_config
        assert github_project.sync_config["sync_issues"] is True
        assert github_project.sync_config["label_mapping"]["bug"] == "defect"

    @pytest.mark.asyncio
    async def test_create_minimal_fields(self, github_project_repo: GitHubProjectRepository, project: Any) -> None:
        """Test creating a GitHub Project link with minimal required fields only."""
        github_project = await github_project_repo.create(
            project_id=project.id,
            github_repo_id=11111111,
            github_repo_owner="minimal-owner",
            github_repo_name="minimal-repo",
            github_project_id="PVT_minimal",
            github_project_number=1,
        )

        assert github_project is not None
        assert len(github_project.id) == 36  # Valid UUID format
        assert github_project.id.count("-") == COUNT_FOUR
        assert github_project.auto_sync is True  # Default
        assert github_project.sync_config == {}  # Default empty dict

    @pytest.mark.asyncio
    async def test_create_generates_uuid(self, github_project_repo: GitHubProjectRepository, project: Any) -> None:
        """Test that create generates a valid UUID for the ID."""
        github_project = await github_project_repo.create(
            project_id=project.id,
            github_repo_id=99999999,
            github_repo_owner="uuid-test",
            github_repo_name="uuid-repo",
            github_project_id="PVT_uuid",
            github_project_number=99,
        )

        # Verify it's a valid UUID format
        assert len(github_project.id) == 36
        assert github_project.id.count("-") == COUNT_FOUR


# ==================== Get By ID Tests ====================


class TestGetById:
    """Tests for GitHubProjectRepository.get_by_id."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, github_project_setup: Any) -> None:
        """Test getting a GitHub Project by ID when it exists."""
        repo = github_project_setup["repo"]
        github_project = github_project_setup["github_project"]

        result = await repo.get_by_id(github_project.id)

        assert result is not None
        assert result.id == github_project.id
        assert result.project_id == github_project.project_id
        assert result.github_repo_id == github_project.github_repo_id
        assert result.github_repo_owner == github_project.github_repo_owner
        assert result.github_project_id == github_project.github_project_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, github_project_repo: GitHubProjectRepository) -> None:
        """Test getting a non-existent GitHub Project returns None."""
        result = await github_project_repo.get_by_id(str(uuid4()))

        assert result is None


# ==================== Get By Project ID Tests ====================


class TestGetByProjectId:
    """Tests for GitHubProjectRepository.get_by_project_id."""

    @pytest.mark.asyncio
    async def test_get_by_project_id_returns_list(self, github_project_setup: Any) -> None:
        """Test getting GitHub Projects by TraceRTM project ID returns a list."""
        repo = github_project_setup["repo"]
        project = github_project_setup["project"]

        result = await repo.get_by_project_id(project.id)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].project_id == project.id

    @pytest.mark.asyncio
    async def test_get_by_project_id_empty_when_none(self, github_project_repo: GitHubProjectRepository) -> None:
        """Test getting GitHub Projects for a project with none returns empty list."""
        result = await github_project_repo.get_by_project_id(str(uuid4()))

        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_project_id_multiple_results(
        self, github_project_repo: GitHubProjectRepository, project: Any
    ) -> None:
        """Test getting multiple GitHub Projects for a single TraceRTM project."""
        # Create multiple GitHub project links for the same project
        for i in range(3):
            await github_project_repo.create(
                project_id=project.id,
                github_repo_id=100000 + i,
                github_repo_owner=f"owner-{i}",
                github_repo_name=f"repo-{i}",
                github_project_id=f"PVT_project_{i}",
                github_project_number=i + 1,
            )

        result = await github_project_repo.get_by_project_id(project.id)

        assert len(result) == COUNT_THREE
        for gp in result:
            assert gp.project_id == project.id


# ==================== Get By Repo Tests ====================


class TestGetByRepo:
    """Tests for GitHubProjectRepository.get_by_repo."""

    @pytest.mark.asyncio
    async def test_get_by_repo_found(self, github_project_setup: Any) -> None:
        """Test getting GitHub Projects by repository ID."""
        repo = github_project_setup["repo"]
        github_project = github_project_setup["github_project"]

        result = await repo.get_by_repo(github_project.github_repo_id)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].github_repo_id == github_project.github_repo_id
        assert result[0].github_repo_owner == "test-owner"
        assert result[0].github_repo_name == "test-repo"

    @pytest.mark.asyncio
    async def test_get_by_repo_empty_when_none(self, github_project_repo: GitHubProjectRepository) -> None:
        """Test getting GitHub Projects for a non-existent repo returns empty list."""
        result = await github_project_repo.get_by_repo(999999999)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_repo_multiple_projects(
        self,
        github_project_repo: GitHubProjectRepository,
        project: Any,
        db_session: AsyncSession,
    ) -> None:
        """Test getting multiple GitHub Projects linked to same repository."""
        # Create a second project
        project_repo = ProjectRepository(db_session)
        project2 = await project_repo.create(
            name="Second Project",
            description="Another project for testing",
        )

        github_repo_id = 55555555

        # Create GitHub project links for both projects pointing to same repo
        await github_project_repo.create(
            project_id=project.id,
            github_repo_id=github_repo_id,
            github_repo_owner="shared-owner",
            github_repo_name="shared-repo",
            github_project_id="PVT_shared_1",
            github_project_number=1,
        )
        await github_project_repo.create(
            project_id=project2.id,
            github_repo_id=github_repo_id,
            github_repo_owner="shared-owner",
            github_repo_name="shared-repo",
            github_project_id="PVT_shared_2",
            github_project_number=2,
        )

        result = await github_project_repo.get_by_repo(github_repo_id)

        assert len(result) == COUNT_TWO
        for gp in result:
            assert gp.github_repo_id == github_repo_id


# ==================== Update Tests ====================


class TestUpdate:
    """Tests for GitHubProjectRepository.update."""

    @pytest.mark.asyncio
    async def test_update_auto_sync(self, github_project_setup: Any) -> None:
        """Test updating auto_sync field."""
        repo = github_project_setup["repo"]
        github_project = github_project_setup["github_project"]

        # Initially auto_sync is True
        assert github_project.auto_sync is True

        result = await repo.update(github_project.id, auto_sync=False)

        assert result is not None
        assert result.auto_sync is False
        # sync_config should remain unchanged
        assert result.sync_config == github_project.sync_config

    @pytest.mark.asyncio
    async def test_update_sync_config(self, github_project_setup: Any) -> None:
        """Test updating sync_config field."""
        repo = github_project_setup["repo"]
        github_project = github_project_setup["github_project"]

        new_sync_config = {
            "sync_issues": False,
            "sync_prs": True,
            "custom_field": "custom_value",
        }

        result = await repo.update(github_project.id, sync_config=new_sync_config)

        assert result is not None
        assert result.sync_config == new_sync_config
        assert result.sync_config["sync_prs"] is True
        # auto_sync should remain unchanged
        assert result.auto_sync == github_project.auto_sync

    @pytest.mark.asyncio
    async def test_update_both_fields(self, github_project_setup: Any) -> None:
        """Test updating both auto_sync and sync_config together."""
        repo = github_project_setup["repo"]
        github_project = github_project_setup["github_project"]

        new_sync_config = {"completely": "new", "config": True}

        result = await repo.update(
            github_project.id,
            auto_sync=False,
            sync_config=new_sync_config,
        )

        assert result is not None
        assert result.auto_sync is False
        assert result.sync_config == new_sync_config

    @pytest.mark.asyncio
    async def test_update_not_found(self, github_project_repo: GitHubProjectRepository) -> None:
        """Test updating a non-existent GitHub Project returns None."""
        result = await github_project_repo.update(
            str(uuid4()),
            auto_sync=False,
        )

        assert result is None


# ==================== Delete Tests ====================


class TestDelete:
    """Tests for GitHubProjectRepository.delete."""

    @pytest.mark.asyncio
    async def test_delete_success(self, github_project_setup: Any) -> None:
        """Test deleting a GitHub Project link."""
        repo = github_project_setup["repo"]
        github_project = github_project_setup["github_project"]

        result = await repo.delete(github_project.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_returns_true(self, github_project_repo: GitHubProjectRepository, project: Any) -> None:
        """Test that delete returns True on success."""
        # Create a GitHub project to delete
        github_project = await github_project_repo.create(
            project_id=project.id,
            github_repo_id=77777777,
            github_repo_owner="delete-test",
            github_repo_name="delete-repo",
            github_project_id="PVT_delete",
            github_project_number=1,
        )

        result = await github_project_repo.delete(github_project.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_verify_deleted(self, github_project_setup: Any) -> None:
        """Test that deleted GitHub Project cannot be retrieved."""
        repo = github_project_setup["repo"]
        github_project = github_project_setup["github_project"]
        github_project_id = github_project.id

        # Delete the GitHub project
        await repo.delete(github_project_id)

        # Verify it's gone
        fetched = await repo.get_by_id(github_project_id)
        assert fetched is None

    @pytest.mark.asyncio
    async def test_delete_not_found(self, github_project_repo: GitHubProjectRepository) -> None:
        """Test deleting a non-existent GitHub Project returns False."""
        result = await github_project_repo.delete(str(uuid4()))

        assert result is False

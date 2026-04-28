"""Tests for GitHubAppInstallationRepository.

Comprehensive tests covering GitHub App installation CRUD operations.
"""

import asyncio
from datetime import datetime

# ==================== Fixtures ====================
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_THREE
from tracertm.repositories.account_repository import AccountRepository
from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository


@pytest_asyncio.fixture
async def github_app_repo(db_session: AsyncSession) -> None:
    """Create a GitHubAppInstallationRepository instance."""
    await asyncio.sleep(0)
    return GitHubAppInstallationRepository(db_session)


@pytest_asyncio.fixture
async def account_for_github_app(db_session: AsyncSession) -> None:
    """Create an account for GitHub App installation tests (FK requirement)."""
    account_repo = AccountRepository(db_session)
    return await account_repo.create(
        name="GitHub Test Account",
        slug=f"github-test-account-{uuid4().hex[:8]}",
        account_type="organization",
    )


@pytest_asyncio.fixture
async def github_app_setup(github_app_repo: GitHubAppInstallationRepository, account_for_github_app: Any) -> None:
    """Create a GitHub App installation for testing."""
    installation = await github_app_repo.create(
        account_id=account_for_github_app.id,
        installation_id=12345678,
        account_login="test-org",
        target_type="Organization",
        target_id=98765432,
        permissions={"contents": "read", "issues": "write"},
        repository_selection="all",
    )
    return {
        "installation": installation,
        "repo": github_app_repo,
        "account": account_for_github_app,
    }


# ==================== Create Tests ====================


class TestCreate:
    """Tests for GitHubAppInstallationRepository.create."""

    @pytest.mark.asyncio
    async def test_create_happy_path(
        self, github_app_repo: GitHubAppInstallationRepository, account_for_github_app: Any
    ) -> None:
        """Test creating a GitHub App installation with standard fields."""
        installation = await github_app_repo.create(
            account_id=account_for_github_app.id,
            installation_id=11111111,
            account_login="my-org",
            target_type="Organization",
            target_id=22222222,
            permissions={"contents": "read"},
            repository_selection="all",
        )

        assert installation is not None
        assert installation.id is not None
        assert len(installation.id) == 36  # UUID format
        assert installation.account_id == account_for_github_app.id
        assert installation.installation_id == 11111111
        assert installation.account_login == "my-org"
        assert installation.target_type == "Organization"
        assert installation.target_id == 22222222
        assert installation.permissions == {"contents": "read"}
        assert installation.repository_selection == "all"
        assert installation.suspended_at is None
        assert installation.suspended_by is None

    @pytest.mark.asyncio
    async def test_create_with_permissions_dict(
        self,
        github_app_repo: GitHubAppInstallationRepository,
        account_for_github_app: Any,
    ) -> None:
        """Test creating an installation with complex permissions dictionary."""
        complex_permissions = {
            "contents": "write",
            "issues": "read",
            "pull_requests": "write",
            "metadata": "read",
            "actions": "write",
        }

        installation = await github_app_repo.create(
            account_id=account_for_github_app.id,
            installation_id=33333333,
            account_login="enterprise-org",
            target_type="Organization",
            target_id=44444444,
            permissions=complex_permissions,
            repository_selection="selected",
        )

        assert installation.permissions == complex_permissions
        assert installation.repository_selection == "selected"

    @pytest.mark.asyncio
    async def test_create_minimal_fields(
        self,
        github_app_repo: GitHubAppInstallationRepository,
        account_for_github_app: Any,
    ) -> None:
        """Test creating an installation with minimal required fields (default repository_selection)."""
        installation = await github_app_repo.create(
            account_id=account_for_github_app.id,
            installation_id=55555555,
            account_login="user-account",
            target_type="User",
            target_id=66666666,
            permissions={},
        )

        assert installation.account_id == account_for_github_app.id
        assert installation.installation_id == 55555555
        assert installation.target_type == "User"
        assert installation.permissions == {}
        assert installation.repository_selection == "all"  # Default value


# ==================== Get By ID Tests ====================


class TestGetById:
    """Tests for GitHubAppInstallationRepository.get_by_id."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, github_app_setup: Any) -> None:
        """Test getting an installation by ID."""
        repo = github_app_setup["repo"]
        installation = github_app_setup["installation"]

        result = await repo.get_by_id(installation.id)

        assert result is not None
        assert result.id == installation.id
        assert result.installation_id == installation.installation_id
        assert result.account_login == installation.account_login

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, github_app_repo: GitHubAppInstallationRepository) -> None:
        """Test getting a non-existent installation returns None."""
        result = await github_app_repo.get_by_id(str(uuid4()))

        assert result is None


# ==================== Get By GitHub Installation ID Tests ====================


class TestGetByGitHubInstallationId:
    """Tests for GitHubAppInstallationRepository.get_by_github_installation_id."""

    @pytest.mark.asyncio
    async def test_get_by_github_installation_id_found(self, github_app_setup: Any) -> None:
        """Test getting an installation by GitHub's installation ID."""
        repo = github_app_setup["repo"]
        installation = github_app_setup["installation"]

        result = await repo.get_by_github_installation_id(installation.installation_id)

        assert result is not None
        assert result.id == installation.id
        assert result.installation_id == installation.installation_id

    @pytest.mark.asyncio
    async def test_get_by_github_installation_id_not_found(
        self, github_app_repo: GitHubAppInstallationRepository
    ) -> None:
        """Test getting by non-existent GitHub installation ID returns None."""
        result = await github_app_repo.get_by_github_installation_id(99999999)

        assert result is None


# ==================== List By Account Tests ====================


class TestListByAccount:
    """Tests for GitHubAppInstallationRepository.list_by_account."""

    @pytest.mark.asyncio
    async def test_list_by_account_returns_list(self, github_app_setup: Any) -> None:
        """Test listing installations returns a list for the account."""
        repo = github_app_setup["repo"]
        account = github_app_setup["account"]

        result = await repo.list_by_account(account.id)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].account_id == account.id

    @pytest.mark.asyncio
    async def test_list_by_account_excludes_suspended(
        self,
        github_app_repo: GitHubAppInstallationRepository,
        account_for_github_app: Any,
    ) -> None:
        """Test that list_by_account excludes suspended installations."""
        # Create an active installation
        active = await github_app_repo.create(
            account_id=account_for_github_app.id,
            installation_id=77777777,
            account_login="active-org",
            target_type="Organization",
            target_id=88888888,
            permissions={"contents": "read"},
        )

        # Create and suspend another installation
        suspended = await github_app_repo.create(
            account_id=account_for_github_app.id,
            installation_id=99999999,
            account_login="suspended-org",
            target_type="Organization",
            target_id=10101010,
            permissions={"contents": "read"},
        )
        await github_app_repo.update(suspended.id, suspended_at=True)

        result = await github_app_repo.list_by_account(account_for_github_app.id)

        assert len(result) == 1
        assert result[0].id == active.id

    @pytest.mark.asyncio
    async def test_list_by_account_empty_when_none(self, github_app_repo: GitHubAppInstallationRepository) -> None:
        """Test listing installations for an account with no installations returns empty list."""
        result = await github_app_repo.list_by_account(str(uuid4()))

        assert result == []

    @pytest.mark.asyncio
    async def test_list_by_account_multiple_installations(
        self,
        github_app_repo: GitHubAppInstallationRepository,
        account_for_github_app: Any,
    ) -> None:
        """Test listing multiple installations for an account."""
        # Create multiple installations
        expected_installation_ids = set()
        for i in range(3):
            installation = await github_app_repo.create(
                account_id=account_for_github_app.id,
                installation_id=20000000 + i,
                account_login=f"org-{i}",
                target_type="Organization",
                target_id=30000000 + i,
                permissions={"contents": "read"},
            )
            expected_installation_ids.add(installation.installation_id)

        result = await github_app_repo.list_by_account(account_for_github_app.id)

        assert len(result) == COUNT_THREE
        # Verify all installations are returned (order may vary with SQLite)
        actual_installation_ids = {r.installation_id for r in result}
        assert actual_installation_ids == expected_installation_ids


# ==================== Update Tests ====================


class TestUpdate:
    """Tests for GitHubAppInstallationRepository.update."""

    @pytest.mark.asyncio
    async def test_update_permissions(self, github_app_setup: Any) -> None:
        """Test updating installation permissions."""
        repo = github_app_setup["repo"]
        installation = github_app_setup["installation"]

        new_permissions = {"contents": "write", "actions": "read", "packages": "write"}
        result = await repo.update(installation.id, permissions=new_permissions)

        assert result is not None
        assert result.permissions == new_permissions

    @pytest.mark.asyncio
    async def test_update_suspend_installation(self, github_app_setup: Any) -> None:
        """Test suspending an installation."""
        repo = github_app_setup["repo"]
        installation = github_app_setup["installation"]

        result = await repo.update(installation.id, suspended_at=True)

        assert result is not None
        assert result.suspended_at is not None
        assert isinstance(result.suspended_at, datetime)

    @pytest.mark.asyncio
    async def test_update_unsuspend_installation(self, github_app_setup: Any) -> None:
        """Test unsuspending an installation."""
        repo = github_app_setup["repo"]
        installation = github_app_setup["installation"]

        # First suspend
        await repo.update(installation.id, suspended_at=True)

        # Then unsuspend
        result = await repo.update(installation.id, suspended_at=False)

        assert result is not None
        assert result.suspended_at is None

    @pytest.mark.asyncio
    async def test_update_not_found(self, github_app_repo: GitHubAppInstallationRepository) -> None:
        """Test updating a non-existent installation returns None."""
        result = await github_app_repo.update(str(uuid4()), permissions={"contents": "read"})

        assert result is None


# ==================== Delete Tests ====================


class TestDelete:
    """Tests for GitHubAppInstallationRepository.delete."""

    @pytest.mark.asyncio
    async def test_delete_success(self, github_app_setup: Any) -> None:
        """Test deleting an installation successfully."""
        repo = github_app_setup["repo"]
        installation = github_app_setup["installation"]

        result = await repo.delete(installation.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_verify_deleted(self, github_app_setup: Any) -> None:
        """Test that deleted installation cannot be retrieved."""
        repo = github_app_setup["repo"]
        installation = github_app_setup["installation"]

        await repo.delete(installation.id)

        # Verify it's actually deleted
        fetched = await repo.get_by_id(installation.id)
        assert fetched is None

    @pytest.mark.asyncio
    async def test_delete_not_found(self, github_app_repo: GitHubAppInstallationRepository) -> None:
        """Test deleting a non-existent installation returns False."""
        result = await github_app_repo.delete(str(uuid4()))

        assert result is False

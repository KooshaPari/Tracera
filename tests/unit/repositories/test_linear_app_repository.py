"""Tests for LinearAppInstallationRepository.

Comprehensive tests covering Linear App installation CRUD operations.
"""

from datetime import datetime

# ==================== Fixtures ====================
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FOUR, COUNT_THREE
from tracertm.models.linear_app import LinearAppInstallation
from tracertm.repositories.account_repository import AccountRepository
from tracertm.repositories.linear_app_repository import LinearAppInstallationRepository


@pytest_asyncio.fixture
def linear_repo(db_session: AsyncSession) -> None:
    """Create a LinearAppInstallationRepository instance."""
    return LinearAppInstallationRepository(db_session)


@pytest_asyncio.fixture
async def account_for_linear(db_session: AsyncSession) -> None:
    """Create an account for Linear app installation tests (FK requirement)."""
    account_repo = AccountRepository(db_session)
    return await account_repo.create(
        name="Test Account for Linear",
        slug=f"test-linear-{uuid4().hex[:8]}",
        account_type="organization",
    )


@pytest_asyncio.fixture
async def linear_setup(linear_repo: LinearAppInstallationRepository, account_for_linear: Any) -> None:
    """Create a Linear app installation for testing."""
    installation = await linear_repo.create(
        account_id=account_for_linear.id,
        workspace_id=f"linear-workspace-{uuid4().hex[:8]}",
        workspace_name="Test Workspace",
        scopes=["read", "write"],
    )
    return {
        "installation": installation,
        "repo": linear_repo,
        "account": account_for_linear,
    }


# ==================== Create Tests ====================


class TestCreate:
    """Tests for LinearAppInstallationRepository.create."""

    @pytest.mark.asyncio
    async def test_create_happy_path(
        self, linear_repo: LinearAppInstallationRepository, account_for_linear: Any
    ) -> None:
        """Test creating a Linear app installation with all fields."""
        installation = await linear_repo.create(
            account_id=account_for_linear.id,
            workspace_id="linear-workspace-123",
            workspace_name="My Linear Workspace",
            integration_credential_id=str(uuid4()),
            scopes=["read", "write", "issues:create"],
        )

        assert installation is not None
        assert installation.id is not None
        assert len(installation.id) == 36  # UUID format
        assert installation.account_id == account_for_linear.id
        assert installation.workspace_id == "linear-workspace-123"
        assert installation.workspace_name == "My Linear Workspace"
        assert installation.scopes == ["read", "write", "issues:create"]
        assert installation.suspended_at is None

    @pytest.mark.asyncio
    async def test_create_with_scopes_list(
        self, linear_repo: LinearAppInstallationRepository, account_for_linear: Any
    ) -> None:
        """Test creating an installation with specific scopes."""
        scopes = ["read", "write", "issues:create", "comments:write"]
        installation = await linear_repo.create(
            account_id=account_for_linear.id,
            workspace_id=f"ws-{uuid4().hex[:8]}",
            workspace_name="Scoped Workspace",
            scopes=scopes,
        )

        assert installation.scopes == scopes
        assert len(installation.scopes) == COUNT_FOUR

    @pytest.mark.asyncio
    async def test_create_minimal_fields(
        self, linear_repo: LinearAppInstallationRepository, account_for_linear: Any
    ) -> None:
        """Test creating an installation with minimal required fields."""
        installation = await linear_repo.create(
            account_id=account_for_linear.id,
            workspace_id=f"minimal-ws-{uuid4().hex[:8]}",
            workspace_name="Minimal Workspace",
        )

        assert installation is not None
        assert installation.id is not None
        assert installation.workspace_name == "Minimal Workspace"
        assert installation.scopes == []  # Default empty list
        assert installation.integration_credential_id is None
        assert installation.suspended_at is None

    @pytest.mark.asyncio
    async def test_create_generates_uuid(
        self, linear_repo: LinearAppInstallationRepository, account_for_linear: Any
    ) -> None:
        """Test that create generates a valid UUID for the installation."""
        installation = await linear_repo.create(
            account_id=account_for_linear.id,
            workspace_id=f"uuid-ws-{uuid4().hex[:8]}",
            workspace_name="UUID Test Workspace",
        )

        # Verify it's a valid UUID format
        assert len(installation.id) == 36
        assert installation.id.count("-") == COUNT_FOUR


# ==================== Get By ID Tests ====================


class TestGetById:
    """Tests for LinearAppInstallationRepository.get_by_id."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, linear_setup: Any) -> None:
        """Test getting an installation by ID."""
        repo = linear_setup["repo"]
        installation = linear_setup["installation"]

        result = await repo.get_by_id(installation.id)

        assert result is not None
        assert result.id == installation.id
        assert result.workspace_id == installation.workspace_id
        assert result.workspace_name == installation.workspace_name
        assert result.account_id == installation.account_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, linear_repo: LinearAppInstallationRepository) -> None:
        """Test getting a non-existent installation returns None."""
        result = await linear_repo.get_by_id(str(uuid4()))

        assert result is None


# ==================== Get By Workspace ID Tests ====================


class TestGetByWorkspaceId:
    """Tests for LinearAppInstallationRepository.get_by_workspace_id."""

    @pytest.mark.asyncio
    async def test_get_by_workspace_id_found(self, linear_setup: Any) -> None:
        """Test getting an installation by Linear workspace ID."""
        repo = linear_setup["repo"]
        installation = linear_setup["installation"]

        result = await repo.get_by_workspace_id(installation.workspace_id)

        assert result is not None
        assert result.id == installation.id
        assert result.workspace_id == installation.workspace_id

    @pytest.mark.asyncio
    async def test_get_by_workspace_id_not_found(self, linear_repo: LinearAppInstallationRepository) -> None:
        """Test getting by non-existent workspace ID returns None."""
        result = await linear_repo.get_by_workspace_id("non-existent-workspace-id")

        assert result is None


# ==================== List By Account Tests ====================


class TestListByAccount:
    """Tests for LinearAppInstallationRepository.list_by_account."""

    @pytest.mark.asyncio
    async def test_list_by_account_returns_list(self, linear_setup: Any) -> None:
        """Test listing installations for an account returns a list."""
        repo = linear_setup["repo"]
        account = linear_setup["account"]

        # Create additional installations
        for i in range(2):
            await repo.create(
                account_id=account.id,
                workspace_id=f"ws-list-{i}-{uuid4().hex[:8]}",
                workspace_name=f"Workspace {i}",
            )

        result = await repo.list_by_account(account.id)

        # 1 from setup + 2 created here = 3 total
        assert len(result) == COUNT_THREE
        assert all(isinstance(item, LinearAppInstallation) for item in result)
        assert all(item.account_id == account.id for item in result)

    @pytest.mark.asyncio
    async def test_list_by_account_excludes_suspended(self, linear_setup: Any) -> None:
        """Test that list_by_account excludes suspended installations."""
        repo = linear_setup["repo"]
        account = linear_setup["account"]
        installation = linear_setup["installation"]

        # Create another non-suspended installation
        active_install = await repo.create(
            account_id=account.id,
            workspace_id=f"active-ws-{uuid4().hex[:8]}",
            workspace_name="Active Workspace",
        )

        # Suspend the original installation
        await repo.update(installation.id, suspended_at=True)

        result = await repo.list_by_account(account.id)

        # Should only return the active installation
        assert len(result) == 1
        assert result[0].id == active_install.id
        assert result[0].suspended_at is None

    @pytest.mark.asyncio
    async def test_list_by_account_empty_when_none(self, linear_repo: LinearAppInstallationRepository) -> None:
        """Test listing installations for account with none returns empty list."""
        result = await linear_repo.list_by_account(str(uuid4()))

        assert result == []


# ==================== Update Tests ====================


class TestUpdate:
    """Tests for LinearAppInstallationRepository.update."""

    @pytest.mark.asyncio
    async def test_update_scopes(self, linear_setup: Any) -> None:
        """Test updating installation scopes."""
        repo = linear_setup["repo"]
        installation = linear_setup["installation"]

        new_scopes = ["read", "write", "admin"]
        result = await repo.update(installation.id, scopes=new_scopes)

        assert result is not None
        assert result.scopes == new_scopes

    @pytest.mark.asyncio
    async def test_update_suspend(self, linear_setup: Any) -> None:
        """Test suspending an installation."""
        repo = linear_setup["repo"]
        installation = linear_setup["installation"]

        # Suspend the installation
        result = await repo.update(installation.id, suspended_at=True)

        assert result is not None
        assert result.suspended_at is not None
        assert isinstance(result.suspended_at, datetime)

    @pytest.mark.asyncio
    async def test_update_unsuspend(self, linear_setup: Any) -> None:
        """Test unsuspending an installation."""
        repo = linear_setup["repo"]
        installation = linear_setup["installation"]

        # First suspend
        await repo.update(installation.id, suspended_at=True)

        # Then unsuspend
        result = await repo.update(installation.id, suspended_at=False)

        assert result is not None
        assert result.suspended_at is None

    @pytest.mark.asyncio
    async def test_update_credential_id(self, linear_setup: Any) -> None:
        """Test updating integration credential ID."""
        repo = linear_setup["repo"]
        installation = linear_setup["installation"]

        new_credential_id = str(uuid4())
        result = await repo.update(installation.id, integration_credential_id=new_credential_id)

        assert result is not None
        assert result.integration_credential_id == new_credential_id

    @pytest.mark.asyncio
    async def test_update_not_found(self, linear_repo: LinearAppInstallationRepository) -> None:
        """Test updating a non-existent installation returns None."""
        result = await linear_repo.update(str(uuid4()), scopes=["read"])

        assert result is None


# ==================== Delete Tests ====================


class TestDelete:
    """Tests for LinearAppInstallationRepository.delete."""

    @pytest.mark.asyncio
    async def test_delete_success(self, linear_setup: Any) -> None:
        """Test deleting an installation."""
        repo = linear_setup["repo"]
        installation = linear_setup["installation"]

        result = await repo.delete(installation.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_verify_deleted(self, linear_setup: Any) -> None:
        """Test that deleted installation is no longer retrievable."""
        repo = linear_setup["repo"]
        installation = linear_setup["installation"]

        await repo.delete(installation.id)

        # Verify deleted
        fetched = await repo.get_by_id(installation.id)
        assert fetched is None

    @pytest.mark.asyncio
    async def test_delete_not_found(self, linear_repo: LinearAppInstallationRepository) -> None:
        """Test deleting a non-existent installation returns False."""
        result = await linear_repo.delete(str(uuid4()))

        assert result is False

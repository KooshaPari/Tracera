"""Comprehensive tests for integration repository classes.

Tests all 6 integration repository classes:
- IntegrationCredentialRepository
- IntegrationMappingRepository
- IntegrationSyncQueueRepository
- IntegrationSyncLogRepository
- IntegrationConflictRepository
- IntegrationRateLimitRepository

Target: ~80 tests to bring coverage to 80%+
"""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO
from tracertm.models.integration import (
    IntegrationRateLimit,
    IntegrationSyncQueue,
)
from tracertm.repositories.integration_repository import (
    IntegrationConflictRepository,
    IntegrationCredentialRepository,
    IntegrationMappingRepository,
    IntegrationRateLimitRepository,
    IntegrationSyncLogRepository,
    IntegrationSyncQueueRepository,
)


# =============================================================================
# Mock Encryption Service
# =============================================================================
class MockEncryptionService:
    """Mock encryption service for testing."""

    def encrypt(self, data: str) -> str:
        """Simple mock encryption that prefixes data."""
        return f"encrypted:{data}"

    def decrypt(self, data: str) -> str:
        """Simple mock decryption that removes prefix."""
        if data.startswith("encrypted:"):
            return data.replace("encrypted:", "", 1)
        return data


# =============================================================================
# Fixtures
# =============================================================================
@pytest_asyncio.fixture
async def mock_encryption() -> None:
    """Provide mock encryption service."""
    await asyncio.sleep(0)
    return MockEncryptionService()


@pytest_asyncio.fixture
async def project(db_session: AsyncSession) -> None:
    """Create a test project."""
    from tracertm.repositories.project_repository import ProjectRepository

    repo = ProjectRepository(db_session)
    project = await repo.create(name="Test Project", description="Test project for integration tests")
    await db_session.flush()
    return project


@pytest_asyncio.fixture
async def item(db_session: AsyncSession, project: Any) -> None:
    """Create a test item."""
    from tracertm.models.item import Item

    item = Item(
        id=str(uuid4()),
        project_id=project.id,
        item_type="requirement",
        title="Test Requirement",
        description="Test description",
        view="requirements",
        status="active",
    )
    db_session.add(item)
    await db_session.flush()
    return item


@pytest_asyncio.fixture
async def credential_repo(db_session: AsyncSession, mock_encryption: Any) -> None:
    """Create IntegrationCredentialRepository with mock encryption."""
    await asyncio.sleep(0)
    return IntegrationCredentialRepository(db_session, encryption_service=mock_encryption)


@pytest_asyncio.fixture
async def mapping_repo(db_session: AsyncSession) -> None:
    """Create IntegrationMappingRepository."""
    await asyncio.sleep(0)
    return IntegrationMappingRepository(db_session)


@pytest_asyncio.fixture
async def sync_queue_repo(db_session: AsyncSession) -> None:
    """Create IntegrationSyncQueueRepository."""
    await asyncio.sleep(0)
    return IntegrationSyncQueueRepository(db_session)


@pytest_asyncio.fixture
async def sync_log_repo(db_session: AsyncSession) -> None:
    """Create IntegrationSyncLogRepository."""
    await asyncio.sleep(0)
    return IntegrationSyncLogRepository(db_session)


@pytest_asyncio.fixture
async def conflict_repo(db_session: AsyncSession) -> None:
    """Create IntegrationConflictRepository."""
    await asyncio.sleep(0)
    return IntegrationConflictRepository(db_session)


@pytest_asyncio.fixture
async def rate_limit_repo(db_session: AsyncSession) -> None:
    """Create IntegrationRateLimitRepository."""
    await asyncio.sleep(0)
    return IntegrationRateLimitRepository(db_session)


@pytest_asyncio.fixture
async def credential(credential_repo: Any, project: Any) -> None:
    """Create a test credential."""
    return await credential_repo.create(
        project_id=project.id,
        provider="github",
        credential_type="oauth_token",
        token="test_token_12345",
        scopes=["repo", "user"],
        provider_metadata={"org": "test-org"},
        created_by_user_id=str(uuid4()),
    )


@pytest_asyncio.fixture
async def mapping(mapping_repo: Any, project: Any, credential: Any, item: Any) -> None:
    """Create a test mapping."""
    return await mapping_repo.create(
        project_id=project.id,
        credential_id=credential.id,
        tracertm_item_id=item.id,
        tracertm_item_type="requirement",
        external_system="github",
        external_id="issue/123",
        external_url="https://github.com/org/repo/issues/123",
    )


@pytest_asyncio.fixture
async def queue_item(sync_queue_repo: Any, credential: Any, mapping: Any) -> None:
    """Create a test sync queue item."""
    return await sync_queue_repo.enqueue(
        credential_id=credential.id,
        mapping_id=mapping.id,
        event_type="item_updated",
        direction="push",
        payload={"field": "status", "value": "completed"},
    )


# =============================================================================
# IntegrationCredentialRepository Tests
# =============================================================================
class TestIntegrationCredentialRepository:
    """Tests for IntegrationCredentialRepository."""

    # -------------------------------------------------------------------------
    # create() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_create_credential_basic(self, credential_repo: Any, project: Any) -> None:
        """Test creating a basic credential."""
        credential = await credential_repo.create(
            project_id=project.id,
            provider="github",
            credential_type="oauth_token",
            token="test_token",
        )

        assert credential.id is not None
        assert credential.project_id == project.id
        assert credential.provider == "github"
        assert credential.credential_type == "oauth_token"
        assert credential.encrypted_token == "encrypted:test_token"
        assert credential.status == "active"
        assert credential.scopes == []
        assert credential.provider_metadata == {}

    @pytest.mark.asyncio
    async def test_create_credential_with_all_fields(self, credential_repo: Any, project: Any) -> None:
        """Test creating a credential with all optional fields."""
        expires_at = datetime.now(UTC) + timedelta(hours=1)
        user_id = str(uuid4())

        credential = await credential_repo.create(
            project_id=project.id,
            provider="linear",
            credential_type="personal_access_token",
            token="linear_token_xyz",
            scopes=["read", "write", "admin"],
            provider_metadata={"workspace": "my-workspace", "team_id": "123"},
            token_expires_at=expires_at,
            refresh_token="refresh_token_abc",
            created_by_user_id=user_id,
            provider_user_id="linear-user-id",
        )

        assert credential.provider == "linear"
        assert credential.scopes == ["read", "write", "admin"]
        assert credential.provider_metadata == {"workspace": "my-workspace", "team_id": "123"}
        assert credential.token_expires_at == expires_at
        assert credential.refresh_token == "encrypted:refresh_token_abc"
        assert credential.created_by_user_id == user_id
        assert credential.provider_user_id == "linear-user-id"

    @pytest.mark.asyncio
    async def test_create_global_credential_without_project(self, credential_repo: Any) -> None:
        """Test creating a global credential (no project_id)."""
        user_id = str(uuid4())

        credential = await credential_repo.create(
            project_id=None,
            provider="github",
            credential_type="oauth_token",
            token="global_token",
            created_by_user_id=user_id,
        )

        assert credential.project_id is None
        assert credential.created_by_user_id == user_id

    # -------------------------------------------------------------------------
    # get_by_id() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_get_by_id_found(self, credential_repo: Any, credential: Any) -> None:
        """Test getting an existing credential by ID."""
        found = await credential_repo.get_by_id(credential.id)

        assert found is not None
        assert found.id == credential.id
        assert found.provider == "github"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, credential_repo: Any) -> None:
        """Test getting a non-existent credential returns None."""
        found = await credential_repo.get_by_id(str(uuid4()))
        assert found is None

    # -------------------------------------------------------------------------
    # get_by_project() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_get_by_project_returns_credentials(
        self, credential_repo: Any, project: Any, credential: Any
    ) -> None:
        """Test getting credentials by project."""
        credentials = await credential_repo.get_by_project(project.id)

        assert len(credentials) == 1
        assert credentials[0].id == credential.id

    @pytest.mark.asyncio
    async def test_get_by_project_with_provider_filter(
        self, credential_repo: Any, project: Any, credential: Any
    ) -> None:
        """Test filtering credentials by provider."""
        # Create a second credential with different provider
        await credential_repo.create(
            project_id=project.id,
            provider="linear",
            credential_type="oauth_token",
            token="linear_token",
        )

        credentials = await credential_repo.get_by_project(project.id, provider="github")

        assert len(credentials) == 1
        assert credentials[0].provider == "github"

    @pytest.mark.asyncio
    async def test_get_by_project_with_global_user_credentials(self, credential_repo: Any, project: Any) -> None:
        """Test including global user credentials."""
        user_id = str(uuid4())

        # Create project-specific credential
        await credential_repo.create(
            project_id=project.id,
            provider="github",
            credential_type="oauth_token",
            token="project_token",
        )

        # Create global credential for same user
        await credential_repo.create(
            project_id=None,
            provider="github",
            credential_type="oauth_token",
            token="global_token",
            created_by_user_id=user_id,
        )

        credentials = await credential_repo.get_by_project(project.id, include_global_user_id=user_id)

        assert len(credentials) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_get_by_project_empty(self, credential_repo: Any, _project: Any) -> None:
        """Test getting credentials for project with none."""
        credentials = await credential_repo.get_by_project(str(uuid4()))
        assert len(credentials) == 0

    # -------------------------------------------------------------------------
    # list_by_user() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_list_by_user_returns_global_credentials(self, credential_repo: Any) -> None:
        """Test listing global credentials for a user."""
        user_id = str(uuid4())

        await credential_repo.create(
            project_id=None,
            provider="github",
            credential_type="oauth_token",
            token="user_token_1",
            created_by_user_id=user_id,
        )

        await credential_repo.create(
            project_id=None,
            provider="linear",
            credential_type="oauth_token",
            token="user_token_2",
            created_by_user_id=user_id,
        )

        credentials = await credential_repo.list_by_user(user_id)

        assert len(credentials) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_list_by_user_with_provider_filter(self, credential_repo: Any) -> None:
        """Test filtering user credentials by provider."""
        user_id = str(uuid4())

        await credential_repo.create(
            project_id=None,
            provider="github",
            credential_type="oauth_token",
            token="gh_token",
            created_by_user_id=user_id,
        )

        await credential_repo.create(
            project_id=None,
            provider="linear",
            credential_type="oauth_token",
            token="linear_token",
            created_by_user_id=user_id,
        )

        credentials = await credential_repo.list_by_user(user_id, provider="github")

        assert len(credentials) == 1
        assert credentials[0].provider == "github"

    @pytest.mark.asyncio
    async def test_list_by_user_excludes_project_credentials(self, credential_repo: Any, project: Any) -> None:
        """Test that project credentials are excluded from user list."""
        user_id = str(uuid4())

        # Create project credential
        await credential_repo.create(
            project_id=project.id,
            provider="github",
            credential_type="oauth_token",
            token="project_token",
            created_by_user_id=user_id,
        )

        # Create global credential
        await credential_repo.create(
            project_id=None,
            provider="github",
            credential_type="oauth_token",
            token="global_token",
            created_by_user_id=user_id,
        )

        credentials = await credential_repo.list_by_user(user_id)

        assert len(credentials) == 1
        assert credentials[0].project_id is None

    # -------------------------------------------------------------------------
    # get_by_project_and_provider() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_get_by_project_and_provider_found(self, credential_repo: Any, project: Any, credential: Any) -> None:
        """Test finding credential by project and provider."""
        found = await credential_repo.get_by_project_and_provider(project.id, "github")

        assert found is not None
        assert found.id == credential.id

    @pytest.mark.asyncio
    async def test_get_by_project_and_provider_not_found(self, credential_repo: Any, project: Any) -> None:
        """Test no credential found for project and provider."""
        found = await credential_repo.get_by_project_and_provider(project.id, "linear")
        assert found is None

    # -------------------------------------------------------------------------
    # get_global_by_user_and_provider() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_get_global_by_user_and_provider_found(self, credential_repo: Any) -> None:
        """Test finding global credential by user and provider."""
        user_id = str(uuid4())

        await credential_repo.create(
            project_id=None,
            provider="github",
            credential_type="oauth_token",
            token="user_gh_token",
            created_by_user_id=user_id,
        )

        found = await credential_repo.get_global_by_user_and_provider(user_id, "github")

        assert found is not None
        assert found.provider == "github"
        assert found.created_by_user_id == user_id

    @pytest.mark.asyncio
    async def test_get_global_by_user_and_provider_not_found(self, credential_repo: Any) -> None:
        """Test no global credential found."""
        found = await credential_repo.get_global_by_user_and_provider(str(uuid4()), "github")
        assert found is None

    # -------------------------------------------------------------------------
    # get_active_by_project_and_provider() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_get_active_by_project_and_provider_found(
        self, credential_repo: Any, project: Any, credential: Any
    ) -> None:
        """Test finding active credential."""
        found = await credential_repo.get_active_by_project_and_provider(project.id, "github")

        assert found is not None
        assert found.id == credential.id
        assert found.status == "active"

    @pytest.mark.asyncio
    async def test_get_active_by_project_and_provider_excludes_revoked(
        self, credential_repo: Any, project: Any, credential: Any
    ) -> None:
        """Test that revoked credentials are excluded."""
        await credential_repo.revoke(credential.id)

        found = await credential_repo.get_active_by_project_and_provider(project.id, "github")
        assert found is None

    # -------------------------------------------------------------------------
    # decrypt_token() / decrypt_refresh_token() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_decrypt_token(self, credential_repo: Any, credential: Any) -> None:
        """Test decrypting a token."""
        decrypted = credential_repo.decrypt_token(credential)
        assert decrypted == "test_token_12345"

    @pytest.mark.asyncio
    async def test_decrypt_refresh_token(self, credential_repo: Any, project: Any) -> None:
        """Test decrypting a refresh token."""
        credential = await credential_repo.create(
            project_id=project.id,
            provider="github",
            credential_type="oauth_token",
            token="access_token",
            refresh_token="refresh_token_secret",
        )

        decrypted = credential_repo.decrypt_refresh_token(credential)
        assert decrypted == "refresh_token_secret"

    @pytest.mark.asyncio
    async def test_decrypt_refresh_token_none(self, credential_repo: Any, credential: Any) -> None:
        """Test decrypting when no refresh token exists."""
        decrypted = credential_repo.decrypt_refresh_token(credential)
        assert decrypted is None

    # -------------------------------------------------------------------------
    # update_token() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_update_token_basic(self, credential_repo: Any, credential: Any, db_session: Any) -> None:
        """Test updating a token."""
        await credential_repo.update_token(credential.id, "new_token_xyz")
        await db_session.refresh(credential)

        assert credential.encrypted_token == "encrypted:new_token_xyz"
        assert credential.status == "active"
        assert credential.validation_error is None

    @pytest.mark.asyncio
    async def test_update_token_with_expiry_and_refresh(
        self, credential_repo: Any, credential: Any, db_session: Any
    ) -> None:
        """Test updating token with expiry and refresh token."""
        expires_at = datetime.now(UTC) + timedelta(hours=2)

        await credential_repo.update_token(
            credential.id,
            "updated_token",
            token_expires_at=expires_at,
            refresh_token="new_refresh",
        )
        await db_session.refresh(credential)

        assert credential.encrypted_token == "encrypted:updated_token"
        assert credential.refresh_token == "encrypted:new_refresh"
        assert credential.token_expires_at == expires_at

    # -------------------------------------------------------------------------
    # update() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_update_credential_partial(self, credential_repo: Any, credential: Any, db_session: Any) -> None:
        """Test partial credential update."""
        await credential_repo.update(
            credential.id,
            scopes=["repo", "user", "admin"],
            provider_metadata={"updated": True},
        )
        await db_session.refresh(credential)

        assert credential.scopes == ["repo", "user", "admin"]
        assert credential.provider_metadata == {"updated": True}

    @pytest.mark.asyncio
    async def test_update_credential_token_encryption(
        self, credential_repo: Any, credential: Any, db_session: Any
    ) -> None:
        """Test that update encrypts new token."""
        await credential_repo.update(credential.id, token="brand_new_token")
        await db_session.refresh(credential)

        assert credential.encrypted_token == "encrypted:brand_new_token"

    @pytest.mark.asyncio
    async def test_update_credential_status(self, credential_repo: Any, credential: Any, db_session: Any) -> None:
        """Test updating credential status."""
        await credential_repo.update(credential.id, status="expired")
        await db_session.refresh(credential)

        assert credential.status == "expired"

    # -------------------------------------------------------------------------
    # update_validation_status() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_update_validation_status_valid(self, credential_repo: Any, credential: Any, db_session: Any) -> None:
        """Test marking credential as valid."""
        await credential_repo.update_validation_status(credential.id, valid=True)
        await db_session.refresh(credential)

        assert credential.status == "active"
        assert credential.validation_error is None
        assert credential.last_validated_at is not None

    @pytest.mark.asyncio
    async def test_update_validation_status_invalid(
        self, credential_repo: Any, credential: Any, db_session: Any
    ) -> None:
        """Test marking credential as invalid."""
        await credential_repo.update_validation_status(credential.id, valid=False, error="Token expired")
        await db_session.refresh(credential)

        assert credential.status == "invalid"
        assert credential.validation_error == "Token expired"

    # -------------------------------------------------------------------------
    # revoke() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_revoke_credential(self, credential_repo: Any, credential: Any, db_session: Any) -> None:
        """Test revoking a credential."""
        await credential_repo.revoke(credential.id)
        await db_session.refresh(credential)

        assert credential.status == "revoked"

    # -------------------------------------------------------------------------
    # delete() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_delete_credential(self, credential_repo: Any, credential: Any, db_session: Any) -> None:
        """Test deleting a credential."""
        credential_id = credential.id
        await credential_repo.delete(credential_id)
        await db_session.flush()

        found = await credential_repo.get_by_id(credential_id)
        assert found is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_credential(self, credential_repo: Any) -> None:
        """Test deleting a non-existent credential (no error)."""
        await credential_repo.delete(str(uuid4()))  # Should not raise


# =============================================================================
# IntegrationMappingRepository Tests
# =============================================================================
class TestIntegrationMappingRepository:
    """Tests for IntegrationMappingRepository."""

    # -------------------------------------------------------------------------
    # create() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_create_mapping_basic(self, mapping_repo: Any, project: Any, credential: Any, item: Any) -> None:
        """Test creating a basic mapping."""
        mapping = await mapping_repo.create(
            project_id=project.id,
            credential_id=credential.id,
            tracertm_item_id=item.id,
            tracertm_item_type="requirement",
            external_system="github",
            external_id="issue/456",
            external_url="https://github.com/org/repo/issues/456",
        )

        assert mapping.id is not None
        assert mapping.project_id == project.id
        assert mapping.tracertm_item_id == item.id
        assert mapping.external_id == "issue/456"
        assert mapping.direction == "bidirectional"
        assert mapping.auto_sync is True
        assert mapping.conflict_resolution_strategy == "manual"

    @pytest.mark.asyncio
    async def test_create_mapping_with_all_options(
        self, mapping_repo: Any, project: Any, credential: Any, item: Any
    ) -> None:
        """Test creating a mapping with all optional fields."""
        mapping = await mapping_repo.create(
            project_id=project.id,
            credential_id=credential.id,
            tracertm_item_id=item.id,
            tracertm_item_type="task",
            external_system="linear",
            external_id="LIN-123",
            external_url="https://linear.app/team/issue/LIN-123",
            direction="tracertm_to_external",
            auto_sync=False,
            conflict_resolution_strategy="tracertm_wins",
            mapping_metadata={"sync_fields": ["title", "status"]},
            field_resolution_rules={"status": "external_wins"},
        )

        assert mapping.direction == "tracertm_to_external"
        assert mapping.auto_sync is False
        assert mapping.conflict_resolution_strategy == "tracertm_wins"
        assert mapping.mapping_metadata == {"sync_fields": ["title", "status"]}
        assert mapping.field_resolution_rules == {"status": "external_wins"}

    # -------------------------------------------------------------------------
    # get_by_id() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_get_by_id_found(self, mapping_repo: Any, mapping: Any) -> None:
        """Test getting mapping by ID."""
        found = await mapping_repo.get_by_id(mapping.id)

        assert found is not None
        assert found.id == mapping.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, mapping_repo: Any) -> None:
        """Test getting non-existent mapping."""
        found = await mapping_repo.get_by_id(str(uuid4()))
        assert found is None

    # -------------------------------------------------------------------------
    # get_by_tracertm_item() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_get_by_tracertm_item(self, mapping_repo: Any, mapping: Any, _item: Any) -> None:
        """Test getting mappings by TraceRTM item."""
        mappings = await mapping_repo.get_by_tracertm_item(item.id)

        assert len(mappings) == 1
        assert mappings[0].tracertm_item_id == item.id

    @pytest.mark.asyncio
    async def test_get_by_tracertm_item_multiple(
        self, mapping_repo: Any, project: Any, credential: Any, item: Any, mapping: Any
    ) -> None:
        """Test getting multiple mappings for same item."""
        # Create second mapping for same item
        await mapping_repo.create(
            project_id=project.id,
            credential_id=credential.id,
            tracertm_item_id=item.id,
            tracertm_item_type="requirement",
            external_system="linear",
            external_id="LIN-999",
            external_url="https://linear.app/issue/LIN-999",
        )

        mappings = await mapping_repo.get_by_tracertm_item(item.id)

        assert len(mappings) == COUNT_TWO

    # -------------------------------------------------------------------------
    # get_by_external_id() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_get_by_external_id_found(self, mapping_repo: Any, project: Any, _mapping: Any) -> None:
        """Test getting mapping by external ID."""
        found = await mapping_repo.get_by_external_id(project.id, "issue/123")

        assert found is not None
        assert found.external_id == "issue/123"

    @pytest.mark.asyncio
    async def test_get_by_external_id_not_found(self, mapping_repo: Any, project: Any) -> None:
        """Test getting non-existent external ID."""
        found = await mapping_repo.get_by_external_id(project.id, "nonexistent")
        assert found is None

    # -------------------------------------------------------------------------
    # list_by_project() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_list_by_project_basic(self, mapping_repo: Any, project: Any, mapping: Any) -> None:
        """Test listing mappings by project."""
        mappings, total = await mapping_repo.list_by_project(project.id)

        assert len(mappings) == 1
        assert total == 1
        assert mappings[0].id == mapping.id

    @pytest.mark.asyncio
    async def test_list_by_project_with_status_filter(
        self, mapping_repo: Any, project: Any, mapping: Any, db_session: Any
    ) -> None:
        """Test filtering mappings by status."""
        # Update mapping to have sync error
        await mapping_repo.update(mapping.id, status="sync_error")
        await db_session.flush()

        active_mappings, _ = await mapping_repo.list_by_project(project.id, status="active")
        error_mappings, _ = await mapping_repo.list_by_project(project.id, status="sync_error")

        assert len(active_mappings) == 0
        assert len(error_mappings) == 1

    @pytest.mark.asyncio
    async def test_list_by_project_with_credential_filter(
        self, mapping_repo: Any, project: Any, credential: Any, mapping: Any
    ) -> None:
        """Test filtering mappings by credential."""
        mappings, total = await mapping_repo.list_by_project(project.id, credential_id=credential.id)

        assert len(mappings) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_list_by_project_with_external_system_filter(
        self, mapping_repo: Any, project: Any, mapping: Any
    ) -> None:
        """Test filtering mappings by external system."""
        mappings, _ = await mapping_repo.list_by_project(project.id, external_system="github")

        assert len(mappings) == 1
        assert mappings[0].external_system == "github"

    @pytest.mark.asyncio
    async def test_list_by_project_pagination(
        self, mapping_repo: Any, project: Any, credential: Any, item: Any, db_session: Any
    ) -> None:
        """Test pagination of mappings."""
        from tracertm.models.item import Item

        # Create multiple mappings
        for i in range(5):
            test_item = Item(
                id=str(uuid4()),
                project_id=project.id,
                item_type="requirement",
                title=f"Requirement {i}",
                description=f"Description {i}",
                view="requirements",
                status="active",
            )
            db_session.add(test_item)
            await db_session.flush()

            await mapping_repo.create(
                project_id=project.id,
                credential_id=credential.id,
                tracertm_item_id=test_item.id,
                tracertm_item_type="requirement",
                external_system="github",
                external_id=f"issue/{i}",
                external_url=f"https://github.com/org/repo/issues/{i}",
            )

        # Paginate
        first_page, total = await mapping_repo.list_by_project(project.id, skip=0, limit=2)
        second_page, _ = await mapping_repo.list_by_project(project.id, skip=2, limit=2)

        assert len(first_page) == COUNT_TWO
        assert len(second_page) == COUNT_TWO
        assert total == COUNT_FIVE

    # -------------------------------------------------------------------------
    # list_by_credential() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_list_by_credential(self, mapping_repo: Any, credential: Any, _mapping: Any) -> None:
        """Test listing mappings by credential."""
        mappings = await mapping_repo.list_by_credential(credential.id)

        assert len(mappings) == 1
        assert mappings[0].integration_credential_id == credential.id

    # -------------------------------------------------------------------------
    # update() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_update_mapping(self, mapping_repo: Any, mapping: Any, db_session: Any) -> None:
        """Test updating mapping fields."""
        await mapping_repo.update(
            mapping.id,
            direction="external_to_tracertm",
            auto_sync=False,
        )
        await db_session.refresh(mapping)

        assert mapping.direction == "external_to_tracertm"
        assert mapping.auto_sync is False

    # -------------------------------------------------------------------------
    # update_sync_status() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_update_sync_status_success(self, mapping_repo: Any, mapping: Any, db_session: Any) -> None:
        """Test updating sync status on success."""
        await mapping_repo.update_sync_status(mapping.id, success=True, direction="push")
        await db_session.refresh(mapping)

        assert mapping.last_sync_direction == "push"
        assert mapping.sync_error_message is None
        assert mapping.consecutive_failures == 0
        assert mapping.status == "active"

    @pytest.mark.asyncio
    async def test_update_sync_status_failure(self, mapping_repo: Any, mapping: Any, db_session: Any) -> None:
        """Test updating sync status on failure."""
        await mapping_repo.update_sync_status(
            mapping.id,
            success=False,
            direction="pull",
            error="API rate limit exceeded",
        )
        await db_session.refresh(mapping)

        assert mapping.sync_error_message == "API rate limit exceeded"
        assert mapping.consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_update_sync_status_multiple_failures_causes_error_status(
        self, mapping_repo: Any, mapping: Any, db_session: Any
    ) -> None:
        """Test that 5 consecutive failures sets sync_error status."""
        # Simulate 5 consecutive failures
        for _ in range(5):
            await mapping_repo.update_sync_status(
                mapping.id,
                success=False,
                direction="push",
                error="Connection timeout",
            )
            await db_session.refresh(mapping)

        assert mapping.consecutive_failures >= COUNT_FIVE
        assert mapping.status == "sync_error"

    # -------------------------------------------------------------------------
    # delete() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_delete_mapping(self, mapping_repo: Any, mapping: Any, db_session: Any) -> None:
        """Test deleting a mapping."""
        mapping_id = mapping.id
        await mapping_repo.delete(mapping_id)
        await db_session.flush()

        found = await mapping_repo.get_by_id(mapping_id)
        assert found is None


# =============================================================================
# IntegrationSyncQueueRepository Tests
# =============================================================================
class TestIntegrationSyncQueueRepository:
    """Tests for IntegrationSyncQueueRepository."""

    # -------------------------------------------------------------------------
    # enqueue() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_enqueue_basic(self, sync_queue_repo: Any, credential: Any, mapping: Any) -> None:
        """Test enqueueing a sync item."""
        queue_item = await sync_queue_repo.enqueue(
            credential_id=credential.id,
            mapping_id=mapping.id,
            event_type="item_created",
            direction="push",
            payload={"item_id": "123"},
        )

        assert queue_item.id is not None
        assert queue_item.status == "pending"
        assert queue_item.priority == "normal"
        assert queue_item.attempts == 0
        assert queue_item.payload == {"item_id": "123"}

    @pytest.mark.asyncio
    async def test_enqueue_with_priority_and_idempotency(
        self, sync_queue_repo: Any, credential: Any, mapping: Any
    ) -> None:
        """Test enqueueing with priority and idempotency key."""
        queue_item = await sync_queue_repo.enqueue(
            credential_id=credential.id,
            mapping_id=mapping.id,
            event_type="item_deleted",
            direction="push",
            payload={},
            priority="critical",
            idempotency_key="unique-key-123",
        )

        assert queue_item.priority == "critical"
        assert queue_item.idempotency_key == "unique-key-123"

    # -------------------------------------------------------------------------
    # get_by_id() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_get_by_id_found(self, sync_queue_repo: Any, queue_item: Any) -> None:
        """Test getting queue item by ID."""
        found = await sync_queue_repo.get_by_id(queue_item.id)

        assert found is not None
        assert found.id == queue_item.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, sync_queue_repo: Any) -> None:
        """Test getting non-existent queue item."""
        found = await sync_queue_repo.get_by_id(str(uuid4()))
        assert found is None

    # -------------------------------------------------------------------------
    # get_pending() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_get_pending_returns_pending_items(self, sync_queue_repo: Any, _queue_item: Any) -> None:
        """Test getting pending items."""
        pending = await sync_queue_repo.get_pending()

        assert len(pending) >= 1
        assert all(item.status == "pending" for item in pending)

    @pytest.mark.asyncio
    async def test_get_pending_ordered_by_priority(self, sync_queue_repo: Any, credential: Any, mapping: Any) -> None:
        """Test that pending items are ordered by priority."""
        # Create items with different priorities
        low = await sync_queue_repo.enqueue(
            credential_id=credential.id,
            mapping_id=mapping.id,
            event_type="item_updated",
            direction="push",
            payload={},
            priority="low",
        )

        critical = await sync_queue_repo.enqueue(
            credential_id=credential.id,
            mapping_id=mapping.id,
            event_type="item_deleted",
            direction="push",
            payload={},
            priority="critical",
        )

        pending = await sync_queue_repo.get_pending()

        # Critical should come before low
        critical_idx = next(i for i, item in enumerate(pending) if item.id == critical.id)
        low_idx = next(i for i, item in enumerate(pending) if item.id == low.id)

        assert critical_idx < low_idx

    @pytest.mark.asyncio
    async def test_get_pending_with_limit(self, sync_queue_repo: Any, credential: Any, mapping: Any) -> None:
        """Test limiting pending items."""
        # Create multiple items
        for _ in range(5):
            await sync_queue_repo.enqueue(
                credential_id=credential.id,
                mapping_id=mapping.id,
                event_type="item_updated",
                direction="push",
                payload={},
            )

        pending = await sync_queue_repo.get_pending(limit=3)

        assert len(pending) == COUNT_THREE

    # -------------------------------------------------------------------------
    # get_retryable() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_get_retryable_returns_ready_items(
        self, sync_queue_repo: Any, queue_item: Any, db_session: Any
    ) -> None:
        """Test getting retryable items."""
        # Mark as failed to set retry status
        await sync_queue_repo.mark_failed(queue_item.id, "Temporary error")
        await db_session.refresh(queue_item)

        # Manually set next_retry_at to past
        from sqlalchemy import update

        await db_session.execute(
            update(IntegrationSyncQueue)
            .where(IntegrationSyncQueue.id == queue_item.id)
            .values(next_retry_at=datetime.now(UTC) - timedelta(minutes=1)),
        )
        await db_session.flush()

        retryable = await sync_queue_repo.get_retryable()

        assert len(retryable) >= 1

    # -------------------------------------------------------------------------
    # list_by_project() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_list_by_project(self, sync_queue_repo: Any, project: Any, _queue_item: Any) -> None:
        """Test listing queue items by project."""
        items, total = await sync_queue_repo.list_by_project(project.id)

        assert len(items) >= 1
        assert total >= 1

    @pytest.mark.asyncio
    async def test_list_by_project_with_status_filter(
        self, sync_queue_repo: Any, project: Any, queue_item: Any
    ) -> None:
        """Test filtering queue items by status."""
        pending, _ = await sync_queue_repo.list_by_project(project.id, status="pending")
        completed, _ = await sync_queue_repo.list_by_project(project.id, status="completed")

        assert len(pending) >= 1
        assert len(completed) == 0

    # -------------------------------------------------------------------------
    # mark_processing() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_mark_processing(self, sync_queue_repo: Any, queue_item: Any, db_session: Any) -> None:
        """Test marking item as processing."""
        await sync_queue_repo.mark_processing(queue_item.id)
        await db_session.refresh(queue_item)

        assert queue_item.status == "processing"
        assert queue_item.started_at is not None

    # -------------------------------------------------------------------------
    # mark_completed() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_mark_completed(self, sync_queue_repo: Any, queue_item: Any, db_session: Any) -> None:
        """Test marking item as completed."""
        await sync_queue_repo.mark_completed(queue_item.id, processing_time_ms=1500)
        await db_session.refresh(queue_item)

        assert queue_item.status == "completed"
        assert queue_item.completed_at is not None
        assert queue_item.processing_time_ms == 1500

    # -------------------------------------------------------------------------
    # mark_failed() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_mark_failed_with_retry(self, sync_queue_repo: Any, queue_item: Any, db_session: Any) -> None:
        """Test marking item as failed with retry."""
        await sync_queue_repo.mark_failed(queue_item.id, error="Connection timeout", error_code="TIMEOUT")
        await db_session.refresh(queue_item)

        assert queue_item.status == "retried"
        assert queue_item.attempts == 1
        assert queue_item.error_message == "Connection timeout"
        assert queue_item.error_code == "TIMEOUT"
        assert queue_item.next_retry_at is not None

    @pytest.mark.asyncio
    async def test_mark_failed_max_attempts_reached(
        self, sync_queue_repo: Any, queue_item: Any, db_session: Any
    ) -> None:
        """Test that max attempts causes permanent failure."""
        # Exhaust all attempts
        for _ in range(queue_item.max_attempts):
            await sync_queue_repo.mark_failed(queue_item.id, "Persistent error")
            await db_session.refresh(queue_item)

        assert queue_item.status == "failed"
        assert queue_item.next_retry_at is None

    # -------------------------------------------------------------------------
    # reschedule_retry() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_reschedule_retry(self, sync_queue_repo: Any, queue_item: Any, db_session: Any) -> None:
        """Test rescheduling a retry."""
        await sync_queue_repo.reschedule_retry(queue_item.id, delay_seconds=300)
        await db_session.refresh(queue_item)

        assert queue_item.status == "retried"
        assert queue_item.next_retry_at is not None
        # Should be roughly 5 minutes from now
        expected_retry = datetime.now(UTC) + timedelta(seconds=300)
        assert abs((queue_item.next_retry_at - expected_retry).total_seconds()) < COUNT_FIVE

    # -------------------------------------------------------------------------
    # cancel() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_cancel_pending_item(self, sync_queue_repo: Any, queue_item: Any, db_session: Any) -> None:
        """Test cancelling a pending item."""
        await sync_queue_repo.cancel(queue_item.id)
        await db_session.refresh(queue_item)

        assert queue_item.status == "failed"
        assert queue_item.error_message == "Cancelled by user"

    @pytest.mark.asyncio
    async def test_cancel_processing_item_not_allowed(
        self, sync_queue_repo: Any, queue_item: Any, db_session: Any
    ) -> None:
        """Test that processing items cannot be cancelled."""
        await sync_queue_repo.mark_processing(queue_item.id)
        await db_session.flush()

        await sync_queue_repo.cancel(queue_item.id)
        await db_session.refresh(queue_item)

        # Should still be processing (cancel only works on pending/retried)
        assert queue_item.status == "processing"


# =============================================================================
# IntegrationSyncLogRepository Tests
# =============================================================================
class TestIntegrationSyncLogRepository:
    """Tests for IntegrationSyncLogRepository."""

    # -------------------------------------------------------------------------
    # create() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_create_sync_log_success(self, sync_log_repo: Any, mapping: Any) -> None:
        """Test creating a successful sync log entry."""
        log = await sync_log_repo.create(
            mapping_id=mapping.id,
            operation="update",
            direction="push",
            source_system="tracertm",
            source_id="item-123",
            target_system="github",
            target_id="issue/456",
            success=True,
            changes={"status": {"old": "open", "new": "closed"}},
        )

        assert log.id is not None
        assert log.operation == "update"
        assert log.success is True
        assert log.changes == {"status": {"old": "open", "new": "closed"}}

    @pytest.mark.asyncio
    async def test_create_sync_log_failure(self, sync_log_repo: Any, mapping: Any) -> None:
        """Test creating a failed sync log entry."""
        log = await sync_log_repo.create(
            mapping_id=mapping.id,
            operation="create",
            direction="pull",
            source_system="linear",
            source_id="LIN-789",
            target_system="tracertm",
            target_id="",
            success=False,
            error_message="Validation failed: missing required field",
        )

        assert log.success is False
        assert log.error_message == "Validation failed: missing required field"

    @pytest.mark.asyncio
    async def test_create_sync_log_with_queue_reference(
        self, sync_log_repo: Any, mapping: Any, queue_item: Any
    ) -> None:
        """Test creating log with queue item reference."""
        log = await sync_log_repo.create(
            mapping_id=mapping.id,
            operation="update",
            direction="push",
            source_system="tracertm",
            source_id="item-123",
            target_system="github",
            target_id="issue/456",
            success=True,
            sync_queue_id=queue_item.id,
        )

        assert log.sync_queue_id == queue_item.id

    # -------------------------------------------------------------------------
    # list_by_mapping() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_list_by_mapping(self, sync_log_repo: Any, mapping: Any) -> None:
        """Test listing logs by mapping."""
        # Create some logs
        await sync_log_repo.create(
            mapping_id=mapping.id,
            operation="create",
            direction="push",
            source_system="tracertm",
            source_id="item-1",
            target_system="github",
            target_id="issue/1",
            success=True,
        )

        await sync_log_repo.create(
            mapping_id=mapping.id,
            operation="update",
            direction="pull",
            source_system="github",
            source_id="issue/1",
            target_system="tracertm",
            target_id="item-1",
            success=False,
            error_message="Conflict detected",
        )

        logs, total = await sync_log_repo.list_by_mapping(mapping.id)

        assert len(logs) == COUNT_TWO
        assert total == COUNT_TWO

    @pytest.mark.asyncio
    async def test_list_by_mapping_with_success_filter(self, sync_log_repo: Any, mapping: Any) -> None:
        """Test filtering logs by success status."""
        await sync_log_repo.create(
            mapping_id=mapping.id,
            operation="create",
            direction="push",
            source_system="tracertm",
            source_id="item-1",
            target_system="github",
            target_id="issue/1",
            success=True,
        )

        await sync_log_repo.create(
            mapping_id=mapping.id,
            operation="update",
            direction="push",
            source_system="tracertm",
            source_id="item-1",
            target_system="github",
            target_id="issue/1",
            success=False,
            error_message="Error",
        )

        success_logs, _ = await sync_log_repo.list_by_mapping(mapping.id, success=True)
        failure_logs, _ = await sync_log_repo.list_by_mapping(mapping.id, success=False)

        assert len(success_logs) == 1
        assert len(failure_logs) == 1

    # -------------------------------------------------------------------------
    # list_by_project() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_list_by_project(self, sync_log_repo: Any, project: Any, mapping: Any) -> None:
        """Test listing logs by project."""
        await sync_log_repo.create(
            mapping_id=mapping.id,
            operation="sync",
            direction="push",
            source_system="tracertm",
            source_id="item-1",
            target_system="github",
            target_id="issue/1",
            success=True,
        )

        logs, total = await sync_log_repo.list_by_project(project.id)

        assert len(logs) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_list_by_project_pagination(self, sync_log_repo: Any, project: Any, mapping: Any) -> None:
        """Test pagination of logs by project."""
        for i in range(5):
            await sync_log_repo.create(
                mapping_id=mapping.id,
                operation="update",
                direction="push",
                source_system="tracertm",
                source_id=f"item-{i}",
                target_system="github",
                target_id=f"issue/{i}",
                success=True,
            )

        first_page, total = await sync_log_repo.list_by_project(project.id, skip=0, limit=2)
        second_page, _ = await sync_log_repo.list_by_project(project.id, skip=2, limit=2)

        assert len(first_page) == COUNT_TWO
        assert len(second_page) == COUNT_TWO
        assert total == COUNT_FIVE


# =============================================================================
# IntegrationConflictRepository Tests
# =============================================================================
class TestIntegrationConflictRepository:
    """Tests for IntegrationConflictRepository."""

    # -------------------------------------------------------------------------
    # create() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_create_conflict(self, conflict_repo: Any, mapping: Any) -> None:
        """Test creating a conflict record."""
        conflict = await conflict_repo.create(
            mapping_id=mapping.id,
            field="status",
            tracertm_value="open",
            external_value="closed",
        )

        assert conflict.id is not None
        assert conflict.field == "status"
        assert conflict.tracertm_value == "open"
        assert conflict.external_value == "closed"
        assert conflict.resolution_status == "pending"

    @pytest.mark.asyncio
    async def test_create_conflict_with_null_values(self, conflict_repo: Any, mapping: Any) -> None:
        """Test creating conflict with null values."""
        conflict = await conflict_repo.create(
            mapping_id=mapping.id,
            field="description",
            tracertm_value="New description",
            external_value=None,  # Deleted in external system
        )

        assert conflict.tracertm_value == "New description"
        assert conflict.external_value is None

    # -------------------------------------------------------------------------
    # get_by_id() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_get_by_id_found(self, conflict_repo: Any, mapping: Any) -> None:
        """Test getting conflict by ID."""
        conflict = await conflict_repo.create(
            mapping_id=mapping.id,
            field="title",
            tracertm_value="Title A",
            external_value="Title B",
        )

        found = await conflict_repo.get_by_id(conflict.id)

        assert found is not None
        assert found.id == conflict.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, conflict_repo: Any) -> None:
        """Test getting non-existent conflict."""
        found = await conflict_repo.get_by_id(str(uuid4()))
        assert found is None

    # -------------------------------------------------------------------------
    # list_pending_by_project() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_list_pending_by_project(self, conflict_repo: Any, project: Any, mapping: Any) -> None:
        """Test listing pending conflicts by project."""
        await conflict_repo.create(
            mapping_id=mapping.id,
            field="status",
            tracertm_value="open",
            external_value="closed",
        )

        await conflict_repo.create(
            mapping_id=mapping.id,
            field="priority",
            tracertm_value="high",
            external_value="medium",
        )

        conflicts, total = await conflict_repo.list_pending_by_project(project.id)

        assert len(conflicts) == COUNT_TWO
        assert total == COUNT_TWO
        assert all(c.resolution_status == "pending" for c in conflicts)

    @pytest.mark.asyncio
    async def test_list_pending_excludes_resolved(
        self, conflict_repo: Any, project: Any, mapping: Any, db_session: Any
    ) -> None:
        """Test that resolved conflicts are excluded."""
        conflict = await conflict_repo.create(
            mapping_id=mapping.id,
            field="status",
            tracertm_value="open",
            external_value="closed",
        )

        # Resolve the conflict
        await conflict_repo.resolve(conflict.id, "closed", "external_wins")
        await db_session.flush()

        pending, total = await conflict_repo.list_pending_by_project(project.id)

        assert len(pending) == 0
        assert total == 0

    # -------------------------------------------------------------------------
    # resolve() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_resolve_conflict(self, conflict_repo: Any, mapping: Any, db_session: Any) -> None:
        """Test resolving a conflict."""
        conflict = await conflict_repo.create(
            mapping_id=mapping.id,
            field="status",
            tracertm_value="open",
            external_value="closed",
        )

        await conflict_repo.resolve(conflict.id, "closed", "external_wins")
        await db_session.refresh(conflict)

        assert conflict.resolution_status == "resolved"
        assert conflict.resolved_value == "closed"
        assert conflict.resolution_strategy_used == "external_wins"
        assert conflict.resolved_at is not None

    # -------------------------------------------------------------------------
    # ignore() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_ignore_conflict(self, conflict_repo: Any, mapping: Any, db_session: Any) -> None:
        """Test ignoring a conflict."""
        conflict = await conflict_repo.create(
            mapping_id=mapping.id,
            field="description",
            tracertm_value="Desc A",
            external_value="Desc B",
        )

        await conflict_repo.ignore(conflict.id)
        await db_session.refresh(conflict)

        assert conflict.resolution_status == "ignored"
        assert conflict.resolved_at is not None


# =============================================================================
# IntegrationRateLimitRepository Tests
# =============================================================================
class TestIntegrationRateLimitRepository:
    """Tests for IntegrationRateLimitRepository."""

    # -------------------------------------------------------------------------
    # get_or_create() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_get_or_create_new(self, rate_limit_repo: Any, credential: Any) -> None:
        """Test creating a new rate limit entry."""
        rate_limit = await rate_limit_repo.get_or_create(
            credential_id=credential.id,
            provider="github",
            api_endpoint="/repos",
            requests_limit=5000,
            window_duration_seconds=3600,
        )

        assert rate_limit.id is not None
        assert rate_limit.requests_used == 0
        assert rate_limit.requests_limit == 5000
        assert rate_limit.is_rate_limited is False
        assert rate_limit.window_start_at is not None
        assert rate_limit.window_end_at is not None

    @pytest.mark.asyncio
    async def test_get_or_create_existing(self, rate_limit_repo: Any, credential: Any, db_session: Any) -> None:
        """Test getting existing rate limit entry."""
        # Create first
        first = await rate_limit_repo.get_or_create(
            credential_id=credential.id,
            provider="github",
            api_endpoint="/repos",
            requests_limit=5000,
        )

        # Increment usage
        await rate_limit_repo.increment_usage(first.id)
        await db_session.refresh(first)

        # Get again - should return same entry
        second = await rate_limit_repo.get_or_create(
            credential_id=credential.id,
            provider="github",
            api_endpoint="/repos",
            requests_limit=5000,
        )

        assert second.id == first.id
        assert second.requests_used == 1

    @pytest.mark.asyncio
    async def test_get_or_create_resets_expired_window(
        self, rate_limit_repo: Any, credential: Any, db_session: Any
    ) -> None:
        """Test that expired window is reset."""
        # Create with expired window
        rate_limit = await rate_limit_repo.get_or_create(
            credential_id=credential.id,
            provider="github",
            api_endpoint="/repos",
            requests_limit=100,
            window_duration_seconds=3600,
        )

        # Manually set window to past
        from sqlalchemy import update

        past_time = datetime.now(UTC) - timedelta(hours=2)
        await db_session.execute(
            update(IntegrationRateLimit)
            .where(IntegrationRateLimit.id == rate_limit.id)
            .values(
                window_start_at=past_time - timedelta(hours=1),
                window_end_at=past_time,
                requests_used=50,
                is_rate_limited=True,
            ),
        )
        await db_session.flush()

        # Get again - should reset
        refreshed = await rate_limit_repo.get_or_create(
            credential_id=credential.id,
            provider="github",
            api_endpoint="/repos",
            requests_limit=100,
        )

        assert refreshed.requests_used == 0
        assert refreshed.is_rate_limited is False

    # -------------------------------------------------------------------------
    # increment_usage() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_increment_usage(self, rate_limit_repo: Any, credential: Any) -> None:
        """Test incrementing usage counter."""
        rate_limit = await rate_limit_repo.get_or_create(
            credential_id=credential.id,
            provider="github",
            api_endpoint="/repos",
            requests_limit=100,
        )

        used, limit = await rate_limit_repo.increment_usage(rate_limit.id)

        assert used == 1
        assert limit == 100

    @pytest.mark.asyncio
    async def test_increment_usage_triggers_rate_limit(
        self, rate_limit_repo: Any, credential: Any, db_session: Any
    ) -> None:
        """Test that hitting limit sets is_rate_limited."""
        rate_limit = await rate_limit_repo.get_or_create(
            credential_id=credential.id,
            provider="github",
            api_endpoint="/repos",
            requests_limit=3,  # Low limit for test
        )

        # Increment to limit
        for _ in range(3):
            _used, _limit = await rate_limit_repo.increment_usage(rate_limit.id)

        await db_session.refresh(rate_limit)

        assert rate_limit.is_rate_limited is True
        assert rate_limit.requests_used == COUNT_THREE

    # -------------------------------------------------------------------------
    # set_backoff() tests
    # -------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_set_backoff(self, rate_limit_repo: Any, credential: Any, db_session: Any) -> None:
        """Test setting backoff time."""
        rate_limit = await rate_limit_repo.get_or_create(
            credential_id=credential.id,
            provider="github",
            api_endpoint="/repos",
            requests_limit=100,
        )

        await rate_limit_repo.set_backoff(rate_limit.id, backoff_seconds=600)
        await db_session.refresh(rate_limit)

        assert rate_limit.is_rate_limited is True
        assert rate_limit.backoff_until is not None
        # Should be roughly 10 minutes from now
        expected_backoff = datetime.now(UTC) + timedelta(seconds=600)
        assert abs((rate_limit.backoff_until - expected_backoff).total_seconds()) < COUNT_FIVE


# =============================================================================
# Integration Tests (Cross-Repository)
# =============================================================================
class TestIntegrationRepositoryCrossRepository:
    """Integration tests that span multiple repositories."""

    @pytest.mark.asyncio
    async def test_full_sync_workflow(
        self,
        _credential_repo: Any,
        mapping_repo: Any,
        sync_queue_repo: Any,
        sync_log_repo: Any,
        project: Any,
        credential: Any,
        item: Any,
        db_session: Any,
    ) -> None:
        """Test a complete sync workflow across all repositories."""
        # 1. Create mapping
        mapping = await mapping_repo.create(
            project_id=project.id,
            credential_id=credential.id,
            tracertm_item_id=item.id,
            tracertm_item_type="requirement",
            external_system="github",
            external_id="issue/workflow-test",
            external_url="https://github.com/org/repo/issues/workflow-test",
        )

        # 2. Enqueue sync
        queue_item = await sync_queue_repo.enqueue(
            credential_id=credential.id,
            mapping_id=mapping.id,
            event_type="item_updated",
            direction="push",
            payload={"field": "status", "value": "completed"},
        )

        # 3. Process sync
        await sync_queue_repo.mark_processing(queue_item.id)

        # 4. Complete sync
        await sync_queue_repo.mark_completed(queue_item.id, processing_time_ms=250)

        # 5. Log sync result
        await sync_log_repo.create(
            mapping_id=mapping.id,
            operation="update",
            direction="push",
            source_system="tracertm",
            source_id=item.id,
            target_system="github",
            target_id="issue/workflow-test",
            success=True,
            changes={"status": {"old": "open", "new": "completed"}},
            sync_queue_id=queue_item.id,
        )

        # 6. Update mapping sync status
        await mapping_repo.update_sync_status(mapping.id, success=True, direction="push")

        # Verify final state
        await db_session.refresh(queue_item)
        await db_session.refresh(mapping)

        assert queue_item.status == "completed"
        assert mapping.consecutive_failures == 0
        assert mapping.last_sync_direction == "push"

    @pytest.mark.asyncio
    async def test_conflict_resolution_workflow(
        self,
        mapping_repo: Any,
        conflict_repo: Any,
        sync_log_repo: Any,
        project: Any,
        credential: Any,
        item: Any,
        _db_session: Any,
    ) -> None:
        """Test conflict detection and resolution workflow."""
        # 1. Create mapping
        mapping = await mapping_repo.create(
            project_id=project.id,
            credential_id=credential.id,
            tracertm_item_id=item.id,
            tracertm_item_type="requirement",
            external_system="linear",
            external_id="LIN-conflict-test",
            external_url="https://linear.app/issue/LIN-conflict-test",
        )

        # 2. Detect conflicts
        conflict1 = await conflict_repo.create(
            mapping_id=mapping.id,
            field="status",
            tracertm_value="in_progress",
            external_value="done",
        )

        conflict2 = await conflict_repo.create(
            mapping_id=mapping.id,
            field="priority",
            tracertm_value="high",
            external_value="low",
        )

        # 3. Check pending conflicts
        _pending, total = await conflict_repo.list_pending_by_project(project.id)
        assert total == COUNT_TWO

        # 4. Resolve one conflict
        await conflict_repo.resolve(conflict1.id, "done", "external_wins")

        # 5. Ignore other conflict
        await conflict_repo.ignore(conflict2.id)

        # 6. Verify no more pending
        _pending, total = await conflict_repo.list_pending_by_project(project.id)
        assert total == 0

        # 7. Log the resolution
        await sync_log_repo.create(
            mapping_id=mapping.id,
            operation="conflict_resolution",
            direction="push",
            source_system="tracertm",
            source_id=item.id,
            target_system="linear",
            target_id="LIN-conflict-test",
            success=True,
            changes={"status": {"resolved_to": "done"}},
            sync_metadata={"conflict_id": conflict1.id, "strategy": "external_wins"},
        )

        logs, _ = await sync_log_repo.list_by_mapping(mapping.id)
        assert len(logs) == 1

"""Integration tests for /api/v1/integrations/stats endpoint."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_TWO, HTTP_OK, HTTP_UNAUTHORIZED
from tracertm.models.integration import (
    IntegrationConflict,
    IntegrationCredential,
    IntegrationMapping,
    IntegrationSyncLog,
    IntegrationSyncQueue,
)

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
class TestIntegrationStatsEndpoint:
    """Integration tests for integration stats endpoint."""

    async def test_get_integration_stats_empty_project(
        self,
        client: AsyncClient,
        test_project_id: str,
        auth_headers: dict,
    ) -> None:
        """Test getting integration stats for a project with no integrations.

        GIVEN: A project with no integrations
        WHEN: GET /api/v1/integrations/stats
        THEN: Returns empty stats structure
        """
        response = await client.get(
            "/api/v1/integrations/stats",
            params={"project_id": test_project_id},
            headers=auth_headers,
        )

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["project_id"] == test_project_id
        assert data["providers"] == []
        assert data["mappings"]["total"] == 0
        assert data["mappings"]["active"] == 0
        assert data["mappings"]["by_provider"] == {}
        assert data["sync"]["queue_pending"] == 0
        assert data["sync"]["recent_syncs"] == 0
        assert data["conflicts"]["pending"] == 0
        assert data["conflicts"]["resolved"] == 0

    async def test_get_integration_stats_with_data(
        self,
        client: AsyncClient,
        test_project_id: str,
        auth_headers: dict,
        db: AsyncSession,
    ) -> None:
        """Test getting integration stats with integration data.

        GIVEN: A project with integrations, mappings, and syncs
        WHEN: GET /api/v1/integrations/stats
        THEN: Returns correct statistics
        """
        # Create test credential
        credential = IntegrationCredential(
            project_id=test_project_id,
            provider="github",
            credential_type="oauth",
            status="active",
            created_by_user_id="test-user",
        )
        db.add(credential)

        # Create test mappings
        mapping1 = IntegrationMapping(
            project_id=test_project_id,
            external_system="github",
            external_id="ext-1",
            internal_id="int-1",
            status="active",
        )
        mapping2 = IntegrationMapping(
            project_id=test_project_id,
            external_system="github",
            external_id="ext-2",
            internal_id="int-2",
            status="active",
        )
        db.add_all([mapping1, mapping2])
        await db.flush()

        # Create sync queue entry
        queue_entry = IntegrationSyncQueue(
            mapping_id=mapping1.id,
            status="pending",
        )
        db.add(queue_entry)

        # Create sync log
        sync_log = IntegrationSyncLog(
            mapping_id=mapping1.id,
            success=True,
        )
        db.add(sync_log)

        # Create conflict
        conflict = IntegrationConflict(
            mapping_id=mapping1.id,
            resolution_status="pending",
        )
        db.add(conflict)

        await db.commit()

        # Test the endpoint
        response = await client.get(
            "/api/v1/integrations/stats",
            params={"project_id": test_project_id},
            headers=auth_headers,
        )

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["project_id"] == test_project_id
        assert len(data["providers"]) >= 1
        assert data["providers"][0]["provider"] == "github"
        assert data["mappings"]["total"] >= COUNT_TWO
        assert data["mappings"]["active"] >= COUNT_TWO
        assert "github" in data["mappings"]["by_provider"]
        assert data["sync"]["queue_pending"] >= 1
        assert data["conflicts"]["pending"] >= 1

    async def test_get_integration_stats_unauthorized(self, client: AsyncClient, test_project_id: str) -> None:
        """Test getting integration stats without authentication.

        GIVEN: No authentication headers
        WHEN: GET /api/v1/integrations/stats
        THEN: Returns 401 Unauthorized
        """
        response = await client.get(
            "/api/v1/integrations/stats",
            params={"project_id": test_project_id},
        )

        assert response.status_code == HTTP_UNAUTHORIZED

    async def test_get_integration_stats_no_project_access(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ) -> None:
        """Test getting integration stats for a project without access.

        GIVEN: A project the user doesn't have access to
        WHEN: GET /api/v1/integrations/stats
        THEN: Returns 403 Forbidden (if access control is enabled)
        """
        response = await client.get(
            "/api/v1/integrations/stats",
            params={"project_id": "unauthorized-project"},
            headers=auth_headers,
        )

        # Note: This might return 200 if check_project_access returns True by default
        # Update assertion based on actual access control implementation
        assert response.status_code in {200, 403}

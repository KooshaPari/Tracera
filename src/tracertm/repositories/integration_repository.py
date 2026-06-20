"""Repository for external integrations."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.integration import (
    IntegrationConflict,
    IntegrationCredential,
    IntegrationMapping,
    IntegrationRateLimit,
    IntegrationSyncLog,
    IntegrationSyncQueue,
)
from tracertm.services.encryption_service import EncryptionService, get_encryption_service

SYNC_ERROR_FAILURE_THRESHOLD = 5


class IntegrationCredentialRepository:
    """Repository for integration credentials."""

    def __init__(
        self,
        session: AsyncSession,
        encryption_service: EncryptionService | None = None,
    ) -> None:
        """Initialize integration repository with database session.

        Args:
            session: AsyncSession for database operations.
            encryption_service: Optional encryption service for credentials.
        """
        self.session = session
        self._encryption = encryption_service

    @property
    def encryption(self) -> EncryptionService:
        """Lazy load encryption service."""
        if self._encryption is None:
            self._encryption = get_encryption_service()
        return self._encryption

    async def create(
        self,
        project_id: str | None,
        provider: str,
        credential_type: str,
        token: str,
        scopes: list[str] | None = None,
        provider_metadata: dict[str, Any] | None = None,
        token_expires_at: datetime | None = None,
        refresh_token: str | None = None,
        created_by_user_id: str | None = None,
        provider_user_id: str | None = None,
    ) -> IntegrationCredential:
        """Create new credential with encryption."""
        credential = IntegrationCredential(
            id=str(uuid.uuid4()),
            project_id=project_id,
            provider=provider,
            credential_type=credential_type,
            encrypted_token=self.encryption.encrypt(token),
            token_expires_at=token_expires_at,
            refresh_token=self.encryption.encrypt(refresh_token) if refresh_token else None,
            scopes=scopes or [],
            status="active",
            provider_metadata=provider_metadata or {},
            created_by_user_id=created_by_user_id,
            provider_user_id=provider_user_id,
            last_validated_at=datetime.now(UTC),
        )
        self.session.add(credential)
        await self.session.flush()
        return credential

    async def get_by_id(self, credential_id: str) -> IntegrationCredential | None:
        """Get credential by ID."""
        result = await self.session.execute(
            select(IntegrationCredential).where(IntegrationCredential.id == credential_id),
        )
        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: str,
        provider: str | None = None,
        include_global_user_id: str | None = None,
    ) -> list[IntegrationCredential]:
        """Get all credentials for project."""
        query = select(IntegrationCredential).where(IntegrationCredential.project_id == project_id)
        if include_global_user_id:
            query = select(IntegrationCredential).where(
                (IntegrationCredential.project_id == project_id)
                | (
                    IntegrationCredential.project_id.is_(None)
                    & (IntegrationCredential.created_by_user_id == include_global_user_id)
                ),
            )
        if provider:
            query = query.where(IntegrationCredential.provider == provider)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_user(self, user_id: str, provider: str | None = None) -> list[IntegrationCredential]:
        """Get all global credentials for a user."""
        query = select(IntegrationCredential).where(
            IntegrationCredential.project_id.is_(None),
            IntegrationCredential.created_by_user_id == user_id,
        )
        if provider:
            query = query.where(IntegrationCredential.provider == provider)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_project_and_provider(self, project_id: str, provider: str) -> IntegrationCredential | None:
        """Get credential for project and provider (any status)."""
        result = await self.session.execute(
            select(IntegrationCredential).where(
                IntegrationCredential.project_id == project_id,
                IntegrationCredential.provider == provider,
            ),
        )
        return result.scalar_one_or_none()

    async def get_global_by_user_and_provider(self, user_id: str, provider: str) -> IntegrationCredential | None:
        """Get global credential for user and provider."""
        result = await self.session.execute(
            select(IntegrationCredential).where(
                IntegrationCredential.project_id.is_(None),
                IntegrationCredential.created_by_user_id == user_id,
                IntegrationCredential.provider == provider,
            ),
        )
        return result.scalar_one_or_none()

    async def get_active_by_project_and_provider(self, project_id: str, provider: str) -> IntegrationCredential | None:
        """Get active credential for project and provider."""
        result = await self.session.execute(
            select(IntegrationCredential).where(
                IntegrationCredential.project_id == project_id,
                IntegrationCredential.provider == provider,
                IntegrationCredential.status == "active",
            ),
        )
        return result.scalar_one_or_none()

    def decrypt_token(self, credential: IntegrationCredential) -> str:
        """Decrypt credential token."""
        return str(self.encryption.decrypt(credential.encrypted_token))

    def decrypt_refresh_token(self, credential: IntegrationCredential) -> str | None:
        """Decrypt refresh token."""
        if credential.refresh_token:
            return str(self.encryption.decrypt(credential.refresh_token))
        return None

    async def update_token(
        self,
        credential_id: str,
        new_token: str,
        token_expires_at: datetime | None = None,
        refresh_token: str | None = None,
    ) -> None:
        """Update encrypted token."""
        update_data: dict[str, Any] = {
            "encrypted_token": self.encryption.encrypt(new_token),
            "updated_at": datetime.now(UTC),
            "rotated_at": datetime.now(UTC),
            "status": "active",
            "validation_error": None,
        }
        if token_expires_at:
            update_data["token_expires_at"] = token_expires_at
        if refresh_token:
            update_data["refresh_token"] = self.encryption.encrypt(refresh_token)

        await self.session.execute(
            update(IntegrationCredential).where(IntegrationCredential.id == credential_id).values(**update_data),
        )

    async def update(
        self,
        credential_id: str,
        token: str | None = None,
        refresh_token: str | None = None,
        expires_at: datetime | None = None,
        scopes: list[str] | None = None,
        provider_user_id: str | None = None,
        provider_metadata: dict[str, Any] | None = None,
        status: str | None = None,
    ) -> None:
        """Update credential fields with encryption."""
        update_data: dict[str, Any] = {
            "updated_at": datetime.now(UTC),
        }
        if token is not None:
            update_data["encrypted_token"] = self.encryption.encrypt(token)
        if refresh_token is not None:
            update_data["refresh_token"] = self.encryption.encrypt(refresh_token)
        if expires_at is not None:
            update_data["token_expires_at"] = expires_at
        if scopes is not None:
            update_data["scopes"] = scopes
        if provider_user_id is not None:
            update_data["provider_user_id"] = provider_user_id
        if provider_metadata is not None:
            update_data["provider_metadata"] = provider_metadata
        if status is not None:
            update_data["status"] = status

        await self.session.execute(
            update(IntegrationCredential).where(IntegrationCredential.id == credential_id).values(**update_data),
        )

    async def update_validation_status(
        self,
        credential_id: str,
        valid: bool,
        error: str | None = None,
    ) -> None:
        """Update credential validation status."""
        update_data: dict[str, Any] = {
            "last_validated_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        if valid:
            update_data["status"] = "active"
            update_data["validation_error"] = None
        else:
            update_data["status"] = "invalid"
            update_data["validation_error"] = error

        await self.session.execute(
            update(IntegrationCredential).where(IntegrationCredential.id == credential_id).values(**update_data),
        )

    async def revoke(self, credential_id: str) -> None:
        """Revoke credential."""
        await self.session.execute(
            update(IntegrationCredential)
            .where(IntegrationCredential.id == credential_id)
            .values(status="revoked", updated_at=datetime.now(UTC)),
        )

    async def delete(self, credential_id: str) -> None:
        """Delete credential (cascades to mappings)."""
        credential = await self.get_by_id(credential_id)
        if credential:
            await self.session.delete(credential)


class IntegrationMappingRepository:
    """Repository for item-to-external mappings."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        project_id: str,
        credential_id: str,
        tracertm_item_id: str,
        tracertm_item_type: str,
        external_system: str,
        external_id: str,
        external_url: str,
        direction: str = "bidirectional",
        auto_sync: bool = True,
        conflict_resolution_strategy: str = "manual",
        mapping_metadata: dict[str, Any] | None = None,
        field_resolution_rules: dict[str, Any] | None = None,
    ) -> IntegrationMapping:
        """Create mapping."""
        mapping = IntegrationMapping(
            id=str(uuid.uuid4()),
            project_id=project_id,
            integration_credential_id=credential_id,
            tracertm_item_id=tracertm_item_id,
            tracertm_item_type=tracertm_item_type,
            external_system=external_system,
            external_id=external_id,
            external_url=external_url,
            direction=direction,
            auto_sync=auto_sync,
            conflict_resolution_strategy=conflict_resolution_strategy,
            mapping_metadata=mapping_metadata or {},
            field_resolution_rules=field_resolution_rules or {},
        )
        self.session.add(mapping)
        await self.session.flush()
        return mapping

    async def get_by_id(self, mapping_id: str) -> IntegrationMapping | None:
        """Get mapping by ID."""
        result = await self.session.execute(select(IntegrationMapping).where(IntegrationMapping.id == mapping_id))
        return result.scalar_one_or_none()

    async def get_by_tracertm_item(self, item_id: str) -> list[IntegrationMapping]:
        """Get all mappings for TraceRTM item."""
        result = await self.session.execute(
            select(IntegrationMapping).where(IntegrationMapping.tracertm_item_id == item_id),
        )
        return list(result.scalars().all())

    async def get_by_external_id(self, project_id: str, external_id: str) -> IntegrationMapping | None:
        """Find mapping by external ID."""
        result = await self.session.execute(
            select(IntegrationMapping).where(
                IntegrationMapping.project_id == project_id,
                IntegrationMapping.external_id == external_id,
            ),
        )
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: str,
        status: str | None = None,
        credential_id: str | None = None,
        external_system: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[IntegrationMapping], int]:
        """Get mappings for project with filtering."""
        query = select(IntegrationMapping).where(IntegrationMapping.project_id == project_id)

        if status:
            query = query.where(IntegrationMapping.status == status)
        if credential_id:
            query = query.where(IntegrationMapping.integration_credential_id == credential_id)
        if external_system:
            query = query.where(IntegrationMapping.external_system == external_system)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Fetch
        query = query.offset(skip).limit(limit).order_by(IntegrationMapping.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def list_by_credential(self, credential_id: str) -> list[IntegrationMapping]:
        """Get all mappings for credential."""
        result = await self.session.execute(
            select(IntegrationMapping).where(IntegrationMapping.integration_credential_id == credential_id),
        )
        return list(result.scalars().all())

    async def update(
        self,
        mapping_id: str,
        **kwargs: object,
    ) -> None:
        """Update mapping fields."""
        kwargs["updated_at"] = datetime.now(UTC)
        await self.session.execute(
            update(IntegrationMapping).where(IntegrationMapping.id == mapping_id).values(**kwargs),
        )

    async def update_sync_status(
        self,
        mapping_id: str,
        success: bool,
        direction: str,
        error: str | None = None,
    ) -> None:
        """Update last sync status."""
        update_data: dict[str, Any] = {
            "last_sync_at": datetime.now(UTC),
            "last_sync_direction": direction,
            "updated_at": datetime.now(UTC),
        }
        if success:
            update_data["sync_error_message"] = None
            update_data["consecutive_failures"] = 0
            update_data["status"] = "active"
        else:
            update_data["sync_error_message"] = error
            # Increment failures
            mapping = await self.get_by_id(mapping_id)
            if mapping:
                update_data["consecutive_failures"] = mapping.consecutive_failures + 1
                if update_data["consecutive_failures"] >= SYNC_ERROR_FAILURE_THRESHOLD:
                    update_data["status"] = "sync_error"

        await self.session.execute(
            update(IntegrationMapping).where(IntegrationMapping.id == mapping_id).values(**update_data),
        )

    async def delete(self, mapping_id: str) -> None:
        """Delete mapping."""
        mapping = await self.get_by_id(mapping_id)
        if mapping:
            await self.session.delete(mapping)


class IntegrationSyncQueueRepository:
    """Repository for sync queue."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def enqueue(
        self,
        credential_id: str,
        mapping_id: str,
        event_type: str,
        direction: str,
        payload: dict[str, Any],
        priority: str = "normal",
        idempotency_key: str | None = None,
    ) -> IntegrationSyncQueue:
        """Add item to sync queue."""
        queue_item = IntegrationSyncQueue(
            id=str(uuid.uuid4()),
            integration_credential_id=credential_id,
            mapping_id=mapping_id,
            event_type=event_type,
            direction=direction,
            priority=priority,
            payload=payload,
            idempotency_key=idempotency_key,
        )
        self.session.add(queue_item)
        await self.session.flush()
        return queue_item

    async def get_by_id(self, queue_id: str) -> IntegrationSyncQueue | None:
        """Get queue item by ID."""
        result = await self.session.execute(select(IntegrationSyncQueue).where(IntegrationSyncQueue.id == queue_id))
        return result.scalar_one_or_none()

    async def get_pending(self, limit: int = 100) -> list[IntegrationSyncQueue]:
        """Get pending items ordered by priority and creation time."""
        priority_order = case(
            (IntegrationSyncQueue.priority == "critical", 1),
            (IntegrationSyncQueue.priority == "high", 2),
            (IntegrationSyncQueue.priority == "normal", 3),
            (IntegrationSyncQueue.priority == "low", 4),
            else_=5,
        )
        result = await self.session.execute(
            select(IntegrationSyncQueue)
            .where(IntegrationSyncQueue.status == "pending")
            .order_by(priority_order, IntegrationSyncQueue.created_at)
            .limit(limit),
        )
        return list(result.scalars().all())

    async def get_retryable(self) -> list[IntegrationSyncQueue]:
        """Get items ready for retry."""
        result = await self.session.execute(
            select(IntegrationSyncQueue).where(
                IntegrationSyncQueue.status == "retried",
                IntegrationSyncQueue.next_retry_at <= datetime.now(UTC),
            ),
        )
        return list(result.scalars().all())

    async def list_by_project(
        self,
        project_id: str,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[IntegrationSyncQueue], int]:
        """List queue items for project (via mappings)."""
        query = select(IntegrationSyncQueue).join(IntegrationMapping).where(IntegrationMapping.project_id == project_id)

        if status:
            query = query.where(IntegrationSyncQueue.status == status)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Fetch
        query = query.offset(skip).limit(limit).order_by(IntegrationSyncQueue.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def mark_processing(self, queue_id: str) -> None:
        """Mark as processing."""
        await self.session.execute(
            update(IntegrationSyncQueue)
            .where(IntegrationSyncQueue.id == queue_id)
            .values(
                status="processing",
                started_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        )

    async def mark_completed(self, queue_id: str, processing_time_ms: int) -> None:
        """Mark as completed."""
        await self.session.execute(
            update(IntegrationSyncQueue)
            .where(IntegrationSyncQueue.id == queue_id)
            .values(
                status="completed",
                completed_at=datetime.now(UTC),
                processing_time_ms=processing_time_ms,
                updated_at=datetime.now(UTC),
            ),
        )

    async def mark_failed(self, queue_id: str, error: str, error_code: str | None = None) -> None:
        """Mark as failed with error."""
        queue_item = await self.get_by_id(queue_id)
        if not queue_item:
            return

        new_attempts = queue_item.attempts + 1
        if new_attempts >= queue_item.max_attempts:
            status = "failed"
            next_retry_at = None
        else:
            status = "retried"
            # Exponential backoff: 60 * 2^attempts seconds
            backoff = 60 * (2**new_attempts)
            next_retry_at = datetime.now(UTC) + timedelta(seconds=backoff)

        await self.session.execute(
            update(IntegrationSyncQueue)
            .where(IntegrationSyncQueue.id == queue_id)
            .values(
                status=status,
                attempts=new_attempts,
                error_message=error,
                error_code=error_code,
                next_retry_at=next_retry_at,
                updated_at=datetime.now(UTC),
            ),
        )

    async def reschedule_retry(self, queue_id: str, delay_seconds: int) -> None:
        """Schedule retry."""
        await self.session.execute(
            update(IntegrationSyncQueue)
            .where(IntegrationSyncQueue.id == queue_id)
            .values(
                status="retried",
                next_retry_at=datetime.now(UTC) + timedelta(seconds=delay_seconds),
                updated_at=datetime.now(UTC),
            ),
        )

    async def cancel(self, queue_id: str) -> None:
        """Cancel pending sync operation."""
        await self.session.execute(
            update(IntegrationSyncQueue)
            .where(
                IntegrationSyncQueue.id == queue_id,
                IntegrationSyncQueue.status.in_(["pending", "retried"]),
            )
            .values(status="failed", error_message="Cancelled by user", updated_at=datetime.now(UTC)),
        )


class IntegrationSyncLogRepository:
    """Repository for sync logs."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        mapping_id: str,
        operation: str,
        direction: str,
        source_system: str,
        source_id: str,
        target_system: str,
        target_id: str,
        success: bool,
        changes: dict[str, Any] | None = None,
        error_message: str | None = None,
        sync_metadata: dict[str, Any] | None = None,
        sync_queue_id: str | None = None,
    ) -> IntegrationSyncLog:
        """Create sync log entry."""
        log = IntegrationSyncLog(
            id=str(uuid.uuid4()),
            sync_queue_id=sync_queue_id,
            mapping_id=mapping_id,
            operation=operation,
            direction=direction,
            source_system=source_system,
            source_id=source_id,
            target_system=target_system,
            target_id=target_id,
            changes=changes or {},
            success=success,
            error_message=error_message,
            sync_metadata=sync_metadata or {},
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def list_by_mapping(
        self,
        mapping_id: str,
        success: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[IntegrationSyncLog], int]:
        """Get sync logs for mapping."""
        query = select(IntegrationSyncLog).where(IntegrationSyncLog.mapping_id == mapping_id)

        if success is not None:
            query = query.where(IntegrationSyncLog.success == success)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Fetch
        query = query.offset(skip).limit(limit).order_by(IntegrationSyncLog.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def list_by_project(
        self,
        project_id: str,
        success: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[IntegrationSyncLog], int]:
        """Get sync logs for project."""
        query = select(IntegrationSyncLog).join(IntegrationMapping).where(IntegrationMapping.project_id == project_id)

        if success is not None:
            query = query.where(IntegrationSyncLog.success == success)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Fetch
        query = query.offset(skip).limit(limit).order_by(IntegrationSyncLog.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all()), total


class IntegrationConflictRepository:
    """Repository for sync conflicts."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        mapping_id: str,
        field: str,
        tracertm_value: str | None,
        external_value: str | None,
    ) -> IntegrationConflict:
        """Create conflict record."""
        conflict = IntegrationConflict(
            id=str(uuid.uuid4()),
            mapping_id=mapping_id,
            field=field,
            tracertm_value=tracertm_value,
            external_value=external_value,
            resolution_status="pending",
        )
        self.session.add(conflict)
        await self.session.flush()
        return conflict

    async def get_by_id(self, conflict_id: str) -> IntegrationConflict | None:
        """Get conflict by ID."""
        result = await self.session.execute(select(IntegrationConflict).where(IntegrationConflict.id == conflict_id))
        return result.scalar_one_or_none()

    async def list_pending_by_project(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[IntegrationConflict], int]:
        """Get pending conflicts for project."""
        query = (
            select(IntegrationConflict)
            .join(IntegrationMapping)
            .where(
                IntegrationMapping.project_id == project_id,
                IntegrationConflict.resolution_status == "pending",
            )
        )

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Fetch
        query = query.offset(skip).limit(limit).order_by(IntegrationConflict.detected_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def resolve(
        self,
        conflict_id: str,
        resolved_value: str,
        strategy_used: str,
    ) -> None:
        """Resolve conflict."""
        await self.session.execute(
            update(IntegrationConflict)
            .where(IntegrationConflict.id == conflict_id)
            .values(
                resolution_status="resolved",
                resolved_value=resolved_value,
                resolution_strategy_used=strategy_used,
                resolved_at=datetime.now(UTC),
            ),
        )

    async def ignore(self, conflict_id: str) -> None:
        """Ignore conflict."""
        await self.session.execute(
            update(IntegrationConflict)
            .where(IntegrationConflict.id == conflict_id)
            .values(
                resolution_status="ignored",
                resolved_at=datetime.now(UTC),
            ),
        )


class IntegrationRateLimitRepository:
    """Repository for rate limit tracking."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def get_or_create(
        self,
        credential_id: str,
        provider: str,
        api_endpoint: str,
        requests_limit: int,
        window_duration_seconds: int = 3600,
    ) -> IntegrationRateLimit:
        """Get or create rate limit entry."""
        result = await self.session.execute(
            select(IntegrationRateLimit).where(
                IntegrationRateLimit.integration_credential_id == credential_id,
                IntegrationRateLimit.api_endpoint == api_endpoint,
            ),
        )
        rate_limit = result.scalar_one_or_none()

        if rate_limit:
            # Check if window expired
            # Ensure timezone-aware comparison
            window_end = rate_limit.window_end_at
            if window_end.tzinfo is None:
                window_end = window_end.replace(tzinfo=UTC)

            if window_end <= datetime.now(UTC):
                # Reset window
                now = datetime.now(UTC)
                await self.session.execute(
                    update(IntegrationRateLimit)
                    .where(IntegrationRateLimit.id == rate_limit.id)
                    .values(
                        requests_used=0,
                        window_start_at=now,
                        window_end_at=now + timedelta(seconds=window_duration_seconds),
                        is_rate_limited=False,
                        backoff_until=None,
                        updated_at=now,
                    ),
                )
                await self.session.refresh(rate_limit)
            return rate_limit

        # Create new
        now = datetime.now(UTC)
        rate_limit = IntegrationRateLimit(
            id=str(uuid.uuid4()),
            integration_credential_id=credential_id,
            provider=provider,
            api_endpoint=api_endpoint,
            requests_limit=requests_limit,
            window_start_at=now,
            window_end_at=now + timedelta(seconds=window_duration_seconds),
        )
        self.session.add(rate_limit)
        await self.session.flush()
        return rate_limit

    async def increment_usage(self, rate_limit_id: str) -> tuple[int, int]:
        """Increment usage counter. Returns (used, limit)."""
        rate_limit_result = await self.session.execute(
            select(IntegrationRateLimit).where(IntegrationRateLimit.id == rate_limit_id),
        )
        rate_limit: IntegrationRateLimit = rate_limit_result.scalar_one()

        new_used = rate_limit.requests_used + 1
        is_limited = new_used >= rate_limit.requests_limit

        await self.session.execute(
            update(IntegrationRateLimit)
            .where(IntegrationRateLimit.id == rate_limit_id)
            .values(
                requests_used=new_used,
                is_rate_limited=is_limited,
                updated_at=datetime.now(UTC),
            ),
        )
        return new_used, rate_limit.requests_limit

    async def set_backoff(self, rate_limit_id: str, backoff_seconds: int) -> None:
        """Set backoff time."""
        await self.session.execute(
            update(IntegrationRateLimit)
            .where(IntegrationRateLimit.id == rate_limit_id)
            .values(
                is_rate_limited=True,
                backoff_until=datetime.now(UTC) + timedelta(seconds=backoff_seconds),
                updated_at=datetime.now(UTC),
            ),
        )

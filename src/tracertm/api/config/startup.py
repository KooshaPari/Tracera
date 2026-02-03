"""Startup configuration for the FastAPI application.

Extracted from main.py to reduce complexity (C901 violations).
Breaks down the monolithic startup_event (complexity 36) into focused functions.
"""

import asyncio
import logging
import os
import sys
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI

from tracertm.services.cache_service import RedisUnavailableError

if TYPE_CHECKING:
    from tracertm.preflight import PreflightCheck

logger = logging.getLogger(__name__)


def _backoff_delay(attempt: int, initial: float, cap: float, multiplier: float = 1.5) -> float:
    """Progressive backoff: initial, then initial*multiplier, ... capped at cap."""
    delay = initial * (multiplier ** (attempt - 1))
    return min(delay, cap)


async def _poll_one_service(
    service_name: str,
    check: "PreflightCheck",
    is_required: bool,
    interval_initial: float,
    interval_max: float,
) -> tuple[str, bool]:
    """Poll one preflight check indefinitely with progressive backoff (cap interval_max). Returns (check.name, ok)."""
    from tracertm.preflight import run_single_check

    # Initial wait so dependent services can start
    await asyncio.sleep(interval_initial)
    attempt = 0
    while True:
        attempt += 1
        result = await asyncio.to_thread(run_single_check, check)
        if result.ok:
            logger.info("[%s] %s ok (after attempt %d)", service_name, check.name, attempt)
            return (check.name, True)
        delay = _backoff_delay(attempt, interval_initial, interval_max)
        logger.info(
            "[%s] %s failed (attempt %d), retrying in %.1fs",
            service_name,
            check.name,
            attempt,
            delay,
        )
        await asyncio.sleep(delay)


async def _poll_services(
    service_name: str,
    required_names: tuple[str, ...],
    optional_names: tuple[str, ...],
    interval_initial: float = 2.0,
    interval_max: float = 30.0,
) -> None:
    """Poll required services in parallel with indefinite retries and progressive backoff (cap interval_max)."""
    from tracertm.preflight import build_api_checks

    checks = build_api_checks()
    to_poll_required = [c for c in checks if c.name in required_names and c.url and c.url.strip()]
    missing_required = [
        n for n in required_names if not any(c.name == n and c.url and c.url.strip() for c in checks)
    ]
    if missing_required:
        raise RuntimeError(f"Preflight failed for: {', '.join(missing_required)} (missing url)")

    # Required: poll all in parallel with indefinite retry and progressive backoff
    if to_poll_required:
        names = ", ".join(c.name for c in to_poll_required)
        sys.stderr.write(
            f"[{service_name}] Polling required (indefinite retry, backoff cap {interval_max}s): {names}...\n"
        )
        sys.stderr.flush()
        results = await asyncio.gather(
            *[_poll_one_service(service_name, c, True, interval_initial, interval_max) for c in to_poll_required]
        )
        required_failures = [name for name, ok in results if not ok]
        if required_failures:
            raise RuntimeError(f"Preflight failed for: {'; '.join(required_failures)}")


async def run_preflight_checks() -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Run preflight checks for all required services except those we poll.

    Returns:
        Tuple of (service names that were checked and passed, required_poll_services).
    """
    from tracertm.preflight import build_api_checks, run_preflight

    # Preflight: all services are required. Run checks for everything except the two we poll with retries.
    required_poll = ("go-backend", "temporal-host")
    optional_poll: tuple[str, ...] = ()
    all_checks = build_api_checks()
    excluded = set(required_poll + optional_poll)
    checked_now = tuple(c.name for c in all_checks if c.name not in excluded and c.url and c.url.strip())

    run_preflight(
        "python-api",
        all_checks,
        strict=True,
        exclude_names=required_poll + optional_poll,
    )

    return checked_now, required_poll


async def poll_required_services() -> None:
    """Poll required services with retries and progressive backoff."""
    # Wait & poll required services in parallel; retry indefinitely with progressive backoff (cap 30s).
    await _poll_services(
        "python-api",
        required_names=("go-backend", "temporal-host"),
        optional_names=(),
        interval_initial=2.0,
        interval_max=30.0,
    )


async def ensure_database_tables() -> None:
    """Ensure problems/processes tables exist (idempotent)."""
    try:
        from tracertm.database.ensure_problems_processes import (
            ensure_problems_processes_tables,
        )

        await ensure_problems_processes_tables()
    except Exception as e:
        logger.warning("ensure_problems_processes_tables: %s", e)


async def initialize_go_backend_client(app: FastAPI) -> None:
    """Initialize Go Backend Client and store in app state.

    Args:
        app: FastAPI application instance

    Raises:
        RuntimeError: If Go backend is unavailable (required dependency)
    """
    try:
        from tracertm.clients.go_client import GoBackendClient

        go_backend_url = os.getenv("GO_BACKEND_URL", "http://localhost:8080")
        service_token = os.getenv("SERVICE_TOKEN", "")

        go_client = GoBackendClient(go_backend_url, service_token)
        app.state.go_client = go_client
        logger.info("Go Backend Client initialized at %s", go_backend_url)
    except Exception as e:
        # Required dependency: fail clearly (CLAUDE.md).
        raise RuntimeError(f"Go backend unavailable: {e}") from e


def is_nats_enabled() -> bool:
    """Check if NATS bridge is enabled.

    NATS bridge is on by default; set NATS_BRIDGE_ENABLED=false to disable.
    """
    return os.getenv("NATS_BRIDGE_ENABLED", "true").lower() == "true"


async def initialize_nats_client() -> tuple[Any, Any]:
    """Initialize NATS client and connect.

    Returns:
        Tuple of (nats_client, event_bus)

    Raises:
        RuntimeError: If NATS is unavailable (required dependency)
    """
    try:
        from tracertm.infrastructure import EventBus, NATSClient

        # Initialize NATS client
        nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
        nats_creds = os.getenv("NATS_CREDS_PATH")

        nats_client = NATSClient(url=nats_url, creds_path=nats_creds)
        await nats_client.connect()

        # Initialize event bus
        event_bus = EventBus(nats_client)

        logger.info("NATS client initialized at %s", nats_url)
        return nats_client, event_bus
    except Exception as e:
        # Required dependency: fail clearly (CLAUDE.md).
        raise RuntimeError(f"NATS unavailable: {e}") from e


async def initialize_agent_service(event_bus: Any) -> Any:
    """Initialize agent service with DB, Redis cache, and NATS.

    Args:
        event_bus: EventBus instance for agent events

    Returns:
        AgentService instance
    """
    from tracertm.agent import AgentService
    from tracertm.agent.session_store import SessionSandboxStoreDB
    from tracertm.api.deps import get_cache_service

    try:
        cache_service = get_cache_service()
        session_store = SessionSandboxStoreDB(cache_service=cache_service)
    except Exception:
        session_store = SessionSandboxStoreDB()

    return AgentService(
        session_store=session_store,
        event_bus=event_bus,
    )


def create_event_handlers(cache_service: Any) -> dict[str, Any]:
    """Create event handlers for NATS events.

    Args:
        cache_service: Cache service for invalidation

    Returns:
        Dictionary mapping event names to handler functions
    """
    async def handle_item_created(event: dict[str, Any]) -> None:
        """Handle item.created events from NATS."""
        entity_id = event.get("entity_id")
        project_id = event.get("project_id")
        entity_type = event.get("entity_type")

        logger.info("Received item.created event: %s (type: %s, project: %s)", entity_id, entity_type, project_id)

        # Invalidate relevant caches for this project
        if project_id:
            await _invalidate_item_caches(cache_service, project_id)

        # Trigger workflows if needed (e.g., for requirements)
        if entity_type == "requirement":
            logger.info("Requirement created: %s, ready for AI analysis workflow", entity_id)
            # Future: Queue for AI analysis, traceability checks, etc.

    async def handle_item_updated(event: dict[str, Any]) -> None:
        """Handle item.updated events from NATS."""
        entity_id = event.get("entity_id")
        project_id = event.get("project_id")
        entity_type = event.get("entity_type")

        logger.info("Received item.updated event: %s (type: %s, project: %s)", entity_id, entity_type, project_id)

        # Invalidate relevant caches
        if project_id:
            await _invalidate_item_update_caches(cache_service, project_id)

    async def handle_item_deleted(event: dict[str, Any]) -> None:
        """Handle item.deleted events from NATS."""
        entity_id = event.get("entity_id")
        project_id = event.get("project_id")

        logger.info("Received item.deleted event: %s (project: %s)", entity_id, project_id)

        # Invalidate relevant caches
        if project_id:
            await _invalidate_item_deletion_caches(cache_service, project_id)

    async def handle_link_created(event: dict[str, Any]) -> None:
        """Handle link.created events from NATS."""
        entity_id = event.get("entity_id")
        project_id = event.get("project_id")

        logger.info("Received link.created event: %s (project: %s)", entity_id, project_id)

        # Invalidate relevant caches - links affect graph and traceability
        if project_id:
            await _invalidate_link_caches(cache_service, project_id)

    async def handle_link_deleted(event: dict[str, Any]) -> None:
        """Handle link.deleted events from NATS."""
        entity_id = event.get("entity_id")
        project_id = event.get("project_id")

        logger.info("Received link.deleted event: %s (project: %s)", entity_id, project_id)

        # Invalidate relevant caches
        if project_id:
            await _invalidate_link_caches(cache_service, project_id)

    async def handle_project_updated(event: dict[str, Any]) -> None:
        """Handle project.updated events from NATS."""
        project_id = event.get("project_id")

        logger.info("Received project.updated event: %s", project_id)

        # Invalidate project-level caches
        if project_id:
            await _invalidate_project_caches(cache_service, project_id)

    async def handle_project_deleted(event: dict[str, Any]) -> None:
        """Handle project.deleted events from NATS."""
        project_id = event.get("project_id")

        logger.info("Received project.deleted event: %s", project_id)

        # Invalidate all project-related caches
        if project_id:
            await _invalidate_project_caches(cache_service, project_id)

    return {
        "item_created": handle_item_created,
        "item_updated": handle_item_updated,
        "item_deleted": handle_item_deleted,
        "link_created": handle_link_created,
        "link_deleted": handle_link_deleted,
        "project_updated": handle_project_updated,
        "project_deleted": handle_project_deleted,
    }


async def _invalidate_item_caches(cache_service: Any, project_id: str) -> None:
    """Invalidate caches related to item creation."""
    try:
        # Invalidate project-wide caches that depend on items
        await cache_service.clear_prefix(f"items:{project_id}")
        await cache_service.clear_prefix(f"graph:{project_id}")
        await cache_service.invalidate("project", project_id=project_id)

        logger.debug("Invalidated caches for project %s after item creation", project_id)
    except (RedisUnavailableError, RuntimeError):
        raise
    except Exception as e:
        raise RedisUnavailableError(f"Redis unavailable: {e}") from e


async def _invalidate_item_update_caches(cache_service: Any, project_id: str) -> None:
    """Invalidate caches related to item updates."""
    try:
        await cache_service.clear_prefix(f"items:{project_id}")
        await cache_service.clear_prefix(f"graph:{project_id}")
        await cache_service.clear_prefix(f"impact:{project_id}")
        await cache_service.invalidate("project", project_id=project_id)

        logger.debug("Invalidated caches for project %s after item update", project_id)
    except (RedisUnavailableError, RuntimeError):
        raise
    except Exception as e:
        raise RedisUnavailableError(f"Redis unavailable: {e}") from e


async def _invalidate_item_deletion_caches(cache_service: Any, project_id: str) -> None:
    """Invalidate caches related to item deletion."""
    try:
        await cache_service.clear_prefix(f"items:{project_id}")
        await cache_service.clear_prefix(f"graph:{project_id}")
        await cache_service.clear_prefix(f"links:{project_id}")
        await cache_service.invalidate("project", project_id=project_id)

        logger.debug("Invalidated caches for project %s after item deletion", project_id)
    except (RedisUnavailableError, RuntimeError):
        raise
    except Exception as e:
        raise RedisUnavailableError(f"Redis unavailable: {e}") from e


async def _invalidate_link_caches(cache_service: Any, project_id: str) -> None:
    """Invalidate caches related to link creation/deletion."""
    try:
        await cache_service.clear_prefix(f"links:{project_id}")
        await cache_service.clear_prefix(f"graph:{project_id}")
        await cache_service.clear_prefix(f"ancestors:{project_id}")
        await cache_service.clear_prefix(f"descendants:{project_id}")
        await cache_service.clear_prefix(f"impact:{project_id}")

        logger.debug("Invalidated caches for project %s after link change", project_id)
    except (RedisUnavailableError, RuntimeError):
        raise
    except Exception as e:
        raise RedisUnavailableError(f"Redis unavailable: {e}") from e


async def _invalidate_project_caches(cache_service: Any, project_id: str) -> None:
    """Invalidate all caches for a project."""
    try:
        await cache_service.invalidate_project(project_id)
        await cache_service.clear_prefix("projects")  # Invalidate project list

        logger.debug("Invalidated all caches for project %s", project_id)
    except (RedisUnavailableError, RuntimeError):
        raise
    except Exception as e:
        raise RedisUnavailableError(f"Redis unavailable: {e}") from e


async def subscribe_to_events(event_bus: Any, handlers: dict[str, Any]) -> None:
    """Subscribe event handlers to NATS event bus.

    Args:
        event_bus: EventBus instance
        handlers: Dictionary of event handlers
    """
    from tracertm.infrastructure import EventBus

    # Subscribe to events from Go backend
    await event_bus.subscribe(EventBus.EVENT_ITEM_CREATED, handlers["item_created"])
    await event_bus.subscribe(EventBus.EVENT_ITEM_UPDATED, handlers["item_updated"])
    await event_bus.subscribe(EventBus.EVENT_ITEM_DELETED, handlers["item_deleted"])
    await event_bus.subscribe(EventBus.EVENT_LINK_CREATED, handlers["link_created"])
    await event_bus.subscribe(EventBus.EVENT_LINK_DELETED, handlers["link_deleted"])
    await event_bus.subscribe(EventBus.EVENT_PROJECT_UPDATED, handlers["project_updated"])
    await event_bus.subscribe(EventBus.EVENT_PROJECT_DELETED, handlers["project_deleted"])

    logger.info("Event handlers subscribed to NATS event bus")


async def initialize_nats_bridge(app: FastAPI) -> None:
    """Initialize NATS bridge with event handlers.

    This sets up the NATS client, event bus, agent service, and subscribes to events.

    Args:
        app: FastAPI application instance

    Raises:
        RuntimeError: If NATS is unavailable (required dependency)
    """
    if not is_nats_enabled():
        logger.info("NATS bridge disabled (NATS_BRIDGE_ENABLED=false)")
        return

    # Initialize NATS and event bus
    nats_client, event_bus = await initialize_nats_client()

    # Store in app state for access in routers
    app.state.nats_client = nats_client
    app.state.event_bus = event_bus

    # Initialize agent service
    agent_service = await initialize_agent_service(event_bus)
    app.state.agent_service = agent_service

    # Get cache service for event handlers
    from tracertm.api.deps import get_cache_service
    cache_service = get_cache_service()

    # Create and subscribe event handlers
    handlers = create_event_handlers(cache_service)
    await subscribe_to_events(event_bus, handlers)

    logger.info("NATS bridge initialized successfully at %s", os.getenv("NATS_URL", "nats://localhost:4222"))


async def startup_initialization(app: FastAPI) -> None:
    """Run all startup initialization tasks.

    This is the main orchestrator for startup that replaces the complex startup_event function.
    Complexity reduced from 36 to ~5 by extracting focused functions.

    Args:
        app: FastAPI application instance
    """
    # Run preflight checks
    checked, required_poll = await run_preflight_checks()
    if checked:
        logger.info(
            "[python-api] All required checks passed: %s. Now polling with retries: %s",
            ", ".join(checked),
            ", ".join(required_poll),
        )

    # Poll required services with retries
    await poll_required_services()

    # Ensure database tables
    await ensure_database_tables()

    # Initialize Go backend client
    await initialize_go_backend_client(app)

    # Initialize NATS bridge (includes event handlers)
    await initialize_nats_bridge(app)

"""Startup configuration for the FastAPI application.

Extracted from main.py to reduce complexity (C901 violations).
Breaks down the monolithic startup_event (complexity 36) into focused functions.
"""

import asyncio
import logging
import os
import sys
from functools import partial
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
    _is_required: bool,
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
    _optional_names: tuple[str, ...],
    interval_initial: float = 2.0,
    interval_max: float = 30.0,
) -> None:
    """Poll required services in parallel with indefinite retries and progressive backoff (cap interval_max)."""
    from tracertm.preflight import build_api_checks

    checks = build_api_checks()
    to_poll_required = [c for c in checks if c.name in required_names and c.url and c.url.strip()]
    missing_required = [n for n in required_names if not any(c.name == n and c.url and c.url.strip() for c in checks)]
    if missing_required:
        msg = f"Preflight failed for: {', '.join(missing_required)} (missing url)"
        raise RuntimeError(msg)

    # Required: poll all in parallel with indefinite retry and progressive backoff
    if to_poll_required:
        names = ", ".join(c.name for c in to_poll_required)
        sys.stderr.write(
            f"[{service_name}] Polling required (indefinite retry, backoff cap {interval_max}s): {names}...\n",
        )
        sys.stderr.flush()
        results = await asyncio.gather(*[
            _poll_one_service(service_name, c, True, interval_initial, interval_max) for c in to_poll_required
        ])
        required_failures = [name for name, ok in results if not ok]
        if required_failures:
            msg = f"Preflight failed for: {'; '.join(required_failures)}"
            raise RuntimeError(msg)


async def run_preflight_checks() -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Run preflight checks for all required services except those we poll.

    Returns:
        Tuple of (service names that were checked and passed, required_poll_services).
    """
    from tracertm.preflight import build_api_checks, run_preflight

    # Preflight: run checks for everything except those we poll with retries.
    # go-backend is optional (breaks circular startup dependency with python-backend).
    required_poll = ("temporal-host",)
    optional_poll: tuple[str, ...] = ("go-backend",)
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
    """Poll required services with retries and progressive backoff.

    Only temporal-host is required at startup. go-backend is optional
    (breaks circular startup dependency; Go client initializes lazily).
    """
    # Wait & poll required services in parallel; retry indefinitely with progressive backoff (cap 30s).
    await _poll_services(
        "python-api",
        required_names=("temporal-host",),
        _optional_names=("go-backend",),
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
    except (ImportError, RuntimeError, OSError, ValueError, TypeError) as e:
        logger.warning("ensure_problems_processes_tables: %s", e)


async def initialize_go_backend_client(app: FastAPI) -> None:
    """Initialize Go Backend Client and store in app state.

    The Go client is optional at startup to break the circular dependency
    between go-backend and python-backend. If Go is unavailable at startup,
    app.state.go_client is set to None and will be available lazily once
    go-backend comes up (health checks detect it at request time).

    Args:
        app: FastAPI application instance
    """
    try:
        from tracertm.clients.go_client import GoBackendClient

        go_backend_url = os.getenv("GO_BACKEND_URL", "http://localhost:8080")
        service_token = os.getenv("SERVICE_TOKEN", "")

        go_client = GoBackendClient(go_backend_url, service_token)
        app.state.go_client = go_client
        logger.info("Go Backend Client initialized at %s", go_backend_url)
    except (ImportError, RuntimeError, OSError, ValueError, TypeError) as e:
        # Optional at startup: log warning, set None (breaks circular startup dependency).
        logger.warning("Go backend unavailable at startup (will be available lazily): %s", e)
        app.state.go_client = None


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
    except (ImportError, RuntimeError, OSError, ValueError, TypeError, ConnectionError, TimeoutError) as e:
        # Required dependency: fail clearly (CLAUDE.md).
        msg = f"NATS unavailable: {e}"
        raise RuntimeError(msg) from e
    else:
        return nats_client, event_bus


async def initialize_agent_service(event_bus: object) -> object:
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
    except (RedisUnavailableError, RuntimeError, OSError, ValueError, TypeError):
        session_store = SessionSandboxStoreDB()

    return AgentService(
        session_store=session_store,
        event_bus=event_bus,
    )


async def _handle_item_created(cache_service: object, event: dict[str, Any]) -> None:
    """Handle item.created events from NATS."""
    from typing import cast

    entity_id = event.get("entity_id")
    project_id = event.get("project_id")
    entity_type = event.get("entity_type")

    logger.info("Received item.created event: %s (type: %s, project: %s)", entity_id, entity_type, project_id)

    if project_id:
        await _invalidate_item_caches(cache_service, cast("str", project_id))

    if entity_type == "requirement":
        logger.info("Requirement created: %s, ready for AI analysis workflow", entity_id)


async def _handle_item_updated(cache_service: object, event: dict[str, Any]) -> None:
    """Handle item.updated events from NATS."""
    from typing import cast

    entity_id = event.get("entity_id")
    project_id = event.get("project_id")
    entity_type = event.get("entity_type")

    logger.info("Received item.updated event: %s (type: %s, project: %s)", entity_id, entity_type, project_id)

    if project_id:
        await _invalidate_item_update_caches(cache_service, cast("str", project_id))


async def _handle_item_deleted(cache_service: object, event: dict[str, Any]) -> None:
    """Handle item.deleted events from NATS."""
    from typing import cast

    entity_id = event.get("entity_id")
    project_id = event.get("project_id")

    logger.info("Received item.deleted event: %s (project: %s)", entity_id, project_id)

    if project_id:
        await _invalidate_item_deletion_caches(cache_service, cast("str", project_id))


async def _handle_link_created(cache_service: object, event: dict[str, Any]) -> None:
    """Handle link.created events from NATS."""
    from typing import cast

    entity_id = event.get("entity_id")
    project_id = event.get("project_id")

    logger.info("Received link.created event: %s (project: %s)", entity_id, project_id)

    if project_id:
        await _invalidate_link_caches(cache_service, cast("str", project_id))


async def _handle_link_deleted(cache_service: object, event: dict[str, Any]) -> None:
    """Handle link.deleted events from NATS."""
    from typing import cast

    entity_id = event.get("entity_id")
    project_id = event.get("project_id")

    logger.info("Received link.deleted event: %s (project: %s)", entity_id, project_id)

    if project_id:
        await _invalidate_link_caches(cache_service, cast("str", project_id))


async def _handle_project_updated(cache_service: object, event: dict[str, Any]) -> None:
    """Handle project.updated events from NATS."""
    from typing import cast

    project_id = event.get("project_id")

    logger.info("Received project.updated event: %s", project_id)

    if project_id:
        await _invalidate_project_caches(cache_service, cast("str", project_id))


async def _handle_project_deleted(cache_service: object, event: dict[str, Any]) -> None:
    """Handle project.deleted events from NATS."""
    from typing import cast

    project_id = event.get("project_id")

    logger.info("Received project.deleted event: %s", project_id)

    if project_id:
        await _invalidate_project_caches(cache_service, cast("str", project_id))


def create_event_handlers(cache_service: object) -> dict[str, Any]:
    """Create event handlers for NATS events."""
    return {
        "item_created": partial(_handle_item_created, cache_service),
        "item_updated": partial(_handle_item_updated, cache_service),
        "item_deleted": partial(_handle_item_deleted, cache_service),
        "link_created": partial(_handle_link_created, cache_service),
        "link_deleted": partial(_handle_link_deleted, cache_service),
        "project_updated": partial(_handle_project_updated, cache_service),
        "project_deleted": partial(_handle_project_deleted, cache_service),
    }


async def _invalidate_item_caches(cache_service: object, project_id: str) -> None:
    """Invalidate caches related to item creation."""
    from typing import cast

    try:
        # Invalidate project-wide caches that depend on items
        await cast("Any", cache_service).clear_prefix(f"items:{project_id}")
        await cast("Any", cache_service).clear_prefix(f"graph:{project_id}")
        await cast("Any", cache_service).invalidate("project", project_id=project_id)

        logger.debug("Invalidated caches for project %s after item creation", project_id)
    except (RedisUnavailableError, RuntimeError):
        raise
    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError) as e:
        msg = f"Redis unavailable: {e}"
        raise RedisUnavailableError(msg) from e


async def _invalidate_item_update_caches(cache_service: object, project_id: str) -> None:
    """Invalidate caches related to item updates."""
    from typing import cast

    try:
        await cast("Any", cache_service).clear_prefix(f"items:{project_id}")
        await cast("Any", cache_service).clear_prefix(f"graph:{project_id}")
        await cast("Any", cache_service).clear_prefix(f"impact:{project_id}")
        await cast("Any", cache_service).invalidate("project", project_id=project_id)

        logger.debug("Invalidated caches for project %s after item update", project_id)
    except (RedisUnavailableError, RuntimeError):
        raise
    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError) as e:
        msg = f"Redis unavailable: {e}"
        raise RedisUnavailableError(msg) from e


async def _invalidate_item_deletion_caches(cache_service: object, project_id: str) -> None:
    """Invalidate caches related to item deletion."""
    from typing import cast

    try:
        await cast("Any", cache_service).clear_prefix(f"items:{project_id}")
        await cast("Any", cache_service).clear_prefix(f"graph:{project_id}")
        await cast("Any", cache_service).clear_prefix(f"links:{project_id}")
        await cast("Any", cache_service).invalidate("project", project_id=project_id)

        logger.debug("Invalidated caches for project %s after item deletion", project_id)
    except (RedisUnavailableError, RuntimeError):
        raise
    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError) as e:
        msg = f"Redis unavailable: {e}"
        raise RedisUnavailableError(msg) from e


async def _invalidate_link_caches(cache_service: object, project_id: str) -> None:
    """Invalidate caches related to link creation/deletion."""
    from typing import cast

    try:
        await cast("Any", cache_service).clear_prefix(f"links:{project_id}")
        await cast("Any", cache_service).clear_prefix(f"graph:{project_id}")
        await cast("Any", cache_service).clear_prefix(f"ancestors:{project_id}")
        await cast("Any", cache_service).clear_prefix(f"descendants:{project_id}")
        await cast("Any", cache_service).clear_prefix(f"impact:{project_id}")

        logger.debug("Invalidated caches for project %s after link change", project_id)
    except (RedisUnavailableError, RuntimeError):
        raise
    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError) as e:
        msg = f"Redis unavailable: {e}"
        raise RedisUnavailableError(msg) from e


async def _invalidate_project_caches(cache_service: object, project_id: str) -> None:
    """Invalidate all caches for a project."""
    from typing import cast

    try:
        await cast("Any", cache_service).invalidate_project(project_id)
        await cast("Any", cache_service).clear_prefix("projects")  # Invalidate project list

        logger.debug("Invalidated all caches for project %s", project_id)
    except (RedisUnavailableError, RuntimeError):
        raise
    except (ConnectionError, TimeoutError, OSError, ValueError, TypeError) as e:
        msg = f"Redis unavailable: {e}"
        raise RedisUnavailableError(msg) from e


async def subscribe_to_events(event_bus: object, handlers: dict[str, Any]) -> None:
    """Subscribe event handlers to NATS event bus.

    Args:
        event_bus: EventBus instance
        handlers: Dictionary of event handlers
    """
    from typing import cast

    from tracertm.infrastructure import EventBus

    # Subscribe to events from Go backend
    await cast("Any", event_bus).subscribe(EventBus.EVENT_ITEM_CREATED, handlers["item_created"])
    await cast("Any", event_bus).subscribe(EventBus.EVENT_ITEM_UPDATED, handlers["item_updated"])
    await cast("Any", event_bus).subscribe(EventBus.EVENT_ITEM_DELETED, handlers["item_deleted"])
    await cast("Any", event_bus).subscribe(EventBus.EVENT_LINK_CREATED, handlers["link_created"])
    await cast("Any", event_bus).subscribe(EventBus.EVENT_LINK_DELETED, handlers["link_deleted"])
    await cast("Any", event_bus).subscribe(EventBus.EVENT_PROJECT_UPDATED, handlers["project_updated"])
    await cast("Any", event_bus).subscribe(EventBus.EVENT_PROJECT_DELETED, handlers["project_deleted"])

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


async def initialize_grpc_server(app: FastAPI) -> None:
    """Initialize Python gRPC server (required for internal gRPC clients)."""
    try:
        from tracertm.grpc.server import start_grpc_server

        grpc_server = await start_grpc_server()
        app.state.grpc_server = grpc_server
    except (ImportError, RuntimeError, OSError, ValueError, TypeError) as e:
        # gRPC is required for Go->Python internal calls; fail clearly.
        msg = f"Python gRPC server failed to start: {e}"
        raise RuntimeError(msg) from e


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

    # Initialize Python gRPC server
    await initialize_grpc_server(app)

"""FastAPI application for TraceRTM."""

import inspect
import logging
import os
import signal
import warnings

# Suppress websockets legacy ws_handler deprecation (uvicorn/starlette integration).
# Filter without module= so it applies when the warning is triggered from any caller.
warnings.filterwarnings(
    "ignore",
    message="remove second argument of ws_handler",
    category=DeprecationWarning,
)
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from types import FrameType
from typing import Annotated, Any, cast


def _path_exists_str(path_str: str) -> bool:
    """Sync helper for Path(path).exists() (run via asyncio.to_thread)."""
    return Path(path_str).exists()


def _path_name_str(path_str: str) -> str:
    """Sync helper for Path(path).name (run via asyncio.to_thread)."""
    return Path(path_str).name


# Disable optional Pydantic plugins that are not part of this repo (ex: logfire).
if os.getenv("PYDANTIC_DISABLE_PLUGINS") is None:
    os.environ["PYDANTIC_DISABLE_PLUGINS"] = "logfire-plugin"

from datetime import UTC

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

# Load .env file if it exists
try:
    from dotenv import load_dotenv

    # Try to find .env file relative to project root
    env_path = Path(__file__).parent.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
except ImportError:
    # If python-dotenv not available, try to read .env manually
    env_path = Path(__file__).parent.parent.parent.parent / ".env"
    if env_path.exists():
        with Path(env_path).open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.config.startup import startup_initialization
from tracertm.api.deps import auth_guard, get_db
from tracertm.api.router_registry import register_api_routers
from tracertm.api.routers import projects
from tracertm.api.security import ensure_credential_access, ensure_project_access
from tracertm.repositories import item_repository, link_repository, project_repository
from tracertm.services import (
    cycle_detection_service,
    impact_analysis_service,
    shortest_path_service,
)
from tracertm.services.cache_service import RedisUnavailableError

logger = logging.getLogger(__name__)

# HTTP status threshold for server errors (health checks)
HTTP_OK = 200
HTTP_SERVER_ERROR_START = 500
STATE_PARTS_EXTENDED = 4  # state format: scope:project_id:provider or scope:project_id:provider:...

CycleDetectionService = cycle_detection_service.CycleDetectionService
ImpactAnalysisService = impact_analysis_service.ImpactAnalysisService
ShortestPathService = shortest_path_service.ShortestPathService
ItemRepository = item_repository.ItemRepository
LinkRepository = link_repository.LinkRepository
ProjectRepository = project_repository.ProjectRepository


async def _maybe_await(value: object) -> object:
    """Await values only when needed."""
    if inspect.isawaitable(value):
        return await value
    return value


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup then yield then shutdown (replaces deprecated on_event)."""
    # Startup - now using extracted module to reduce complexity
    await startup_initialization(app)
    try:
        yield
    finally:
        await _shutdown_event_impl(app)


# _startup_event_impl function now replaced by startup_initialization from tracertm.api.config.startup


async def _shutdown_event_impl(app: FastAPI) -> None:
    """Close connections on shutdown."""
    # Stop gRPC server
    if hasattr(app.state, "grpc_server") and app.state.grpc_server:
        try:
            from tracertm.grpc.server import stop_grpc_server

            await stop_grpc_server(app.state.grpc_server)
        except Exception:
            logger.exception("Error stopping gRPC server")

    # Close Go Backend Client
    if hasattr(app.state, "go_client") and app.state.go_client:
        try:
            await app.state.go_client.close()
            logger.info("Go Backend Client closed")
        except Exception:
            logger.exception("Error closing Go Backend Client")

    # Close NATS connection
    if hasattr(app.state, "nats_client") and app.state.nats_client:
        try:
            await app.state.nats_client.close()
            logger.info("NATS connection closed")
        except Exception:
            logger.exception("Error closing NATS connection")


# Create FastAPI app
app = FastAPI(
    title="TraceRTM API",
    description="Traceability Requirements Tracking Management API",
    version="1.0.0",
    lifespan=_lifespan,
)


def _install_signal_logging() -> None:
    """Log shutdown signals so supervisor-initiated stops are explicit."""

    def _wrap_handler(_sig: int, handler: object) -> Callable[[int, FrameType | None], Any] | int | None:
        if callable(handler):

            def _wrapped(signum: int, frame: FrameType | None) -> Any:
                logger.warning("Received shutdown signal: %s", signal.Signals(signum).name)
                return cast("Callable[[int, FrameType | None], Any]", handler)(signum, frame)

            return _wrapped
        return cast("int | None", handler)

    for sig in (signal.SIGTERM, signal.SIGINT):
        prev = signal.getsignal(sig)
        signal.signal(sig, _wrap_handler(sig, prev))


_install_signal_logging()

# Initialize APM instrumentation
try:
    from tracertm.observability import init_tracing, instrument_all, instrument_app

    # Check if tracing is enabled
    tracing_enabled = os.getenv("TRACING_ENABLED", "false").lower() == "true"

    if tracing_enabled:
        # Initialize distributed tracing
        init_tracing(
            service_name="tracertm-python-backend",
            service_version="1.0.0",
            environment=os.getenv("TRACING_ENVIRONMENT", "development"),
            otlp_endpoint=os.getenv(
                "PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT",
                "127.0.0.1:4317",
            ),
        )

        # Instrument FastAPI
        instrument_app(app)

        # Instrument HTTP clients and the Redis-compatible cache
        instrument_all()

        logger.info("✅ APM instrumentation enabled")
    else:
        logger.info("ℹ️  APM instrumentation disabled (set TRACING_ENABLED=true to enable)")
except ImportError as e:
    if tracing_enabled:
        logger.exception("APM instrumentation required but not available")
        raise
    logger.warning("APM instrumentation not available: %s", e)
except Exception:
    if tracing_enabled:
        logger.exception("Failed to initialize APM instrumentation (required)")
        raise
    logger.exception("Failed to initialize APM instrumentation")


@app.exception_handler(RedisUnavailableError)
async def redis_unavailable_handler(_request: Request, exc: RedisUnavailableError) -> JSONResponse:
    """Required Redis-compatible cache down: fail clearly with named item (CLAUDE.md)."""
    logger.error("Redis-compatible cache unavailable: %s", exc)
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc)},
    )


# GitHub / Linear client errors → HTTP with codes for frontend (toast, reconnect, etc.)
def _register_integration_exception_handlers() -> None:
    from datetime import datetime

    from tracertm.clients.github_client import (
        GitHubAuthError,
        GitHubNotFoundError,
        GitHubRateLimitError,
    )
    from tracertm.clients.linear_client import (
        LinearAuthError,
        LinearNotFoundError,
        LinearRateLimitError,
    )

    @app.exception_handler(GitHubAuthError)
    @app.exception_handler(LinearAuthError)
    async def integration_auth_handler(_request: Request, exc: Exception) -> JSONResponse:
        """Integration token expired/invalid: 401 + code so frontend can show reconnect (no full logout)."""
        logger.warning("Integration auth error: %s", exc)
        return JSONResponse(
            status_code=401,
            content={
                "detail": str(exc) or "Integration token expired or invalid. Please reconnect in Settings.",
                "code": "integration_auth_required",
            },
        )

    @app.exception_handler(GitHubRateLimitError)
    async def github_rate_limit_handler(_request: Request, exc: GitHubRateLimitError) -> JSONResponse:
        """GitHub rate limit: 429 + Retry-After for loud/graceful handling."""
        now = datetime.now(UTC)
        reset = exc.reset_at.replace(tzinfo=UTC) if getattr(exc.reset_at, "tzinfo", None) is None else exc.reset_at
        delta = (reset - now).total_seconds()
        retry_after = max(1, int(delta)) if delta > 0 else 60
        logger.warning("GitHub rate limit: retry after %s s", retry_after)
        return JSONResponse(
            status_code=429,
            content={
                "detail": "GitHub rate limit exceeded. Please try again later.",
                "code": "rate_limited",
                "retry_after": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    @app.exception_handler(LinearRateLimitError)
    async def linear_rate_limit_handler(_request: Request, _exc: LinearRateLimitError) -> JSONResponse:
        """Linear rate limit: 429 + Retry-After."""
        retry_after = 60
        logger.warning("Linear rate limit: retry after %s s", retry_after)
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Linear rate limit exceeded. Please try again later.",
                "code": "rate_limited",
                "retry_after": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    @app.exception_handler(GitHubNotFoundError)
    @app.exception_handler(LinearNotFoundError)
    async def integration_not_found_handler(_request: Request, exc: Exception) -> JSONResponse:
        """Integration resource not found: 404 + code for frontend toast."""
        logger.info("Integration not found: %s", exc)
        return JSONResponse(
            status_code=404,
            content={
                "detail": str(exc) or "Resource not found.",
                "code": "integration_not_found",
            },
        )


_register_integration_exception_handlers()


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Log unhandled exceptions and return a safe 500 response (no traceback leak)."""
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    logger.error("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# NATS Event Bus integration
# Helper functions (_backoff_delay, _poll_one_service, _poll_services) now in tracertm.api.config.startup

# Add CORS middleware (gateway + frontend only; no wildcards)
# External clients must use the gateway; allow gateway (4000) + frontend origins
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    (
        "http://localhost:4000,http://127.0.0.1:4000,"
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:3000,http://127.0.0.1:3000"
    ),
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include specification routers
from tracertm.api.middleware import AuthenticationMiddleware, CacheHeadersMiddleware

# Try to import Brotli compression (optional dependency)
try:
    from brotli_asgi import BrotliMiddleware

    brotli_available = True
    BrotliMiddleware_: type[BrotliMiddleware] | None = BrotliMiddleware
except ImportError:
    BrotliMiddleware_ = None
    brotli_available = False
    logger.info("brotli-asgi not installed - response compression disabled")

# Add performance middlewares (order matters - outermost first)
# 1. Brotli compression for smaller JSON responses (20-30% savings)
if brotli_available and BrotliMiddleware_ is not None:
    app.add_middleware(
        BrotliMiddleware_,
        quality=4,  # Balance between speed and compression (1-11)
        minimum_size=500,  # Only compress responses > 500 bytes
    )

# 2. Cache headers for browser caching optimization
app.add_middleware(CacheHeadersMiddleware)

# Authentication endpoints (device flow, token management, etc.)
# Register API routers from dedicated registry module
register_api_routers(app)

# 3. Authentication middleware (must be innermost to run first on request)
app.add_middleware(AuthenticationMiddleware)


# ==================== EXTERNAL INTEGRATIONS ====================


@app.post("/api/v1/integrations/oauth/start")
async def start_oauth_flow(
    request: Request,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
):
    """Start OAuth flow for an external integration provider."""
    import secrets
    import urllib.parse

    from tracertm.schemas.integration import IntegrationProvider

    enforce_rate_limit(request, claims)

    project_id = data.get("project_id")
    provider = data.get("provider")
    redirect_uri = data.get("redirect_uri")
    scopes = data.get("scopes", [])
    credential_scope = data.get("credential_scope", "project")

    if project_id:
        ensure_project_access(project_id, claims)

    # Validate provider
    valid_providers = [p.value for p in IntegrationProvider]
    if provider not in valid_providers:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")

    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store state in session or temporary storage (in production, use Redis/DB)
    # For now, encode project_id and provider in state
    state_data = f"{credential_scope}:{project_id or ''}:{provider}:{state}"

    # Build OAuth URL based on provider
    if provider == "github":
        client_id = os.environ.get("GITHUB_CLIENT_ID", "")
        oauth_url = "https://github.com/login/oauth/authorize"
        default_scopes = ["repo", "read:org", "read:user", "project"]
        scope_str = " ".join(scopes or default_scopes)
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope_str,
            "state": state_data,
        }
    elif provider == "linear":
        client_id = os.environ.get("LINEAR_CLIENT_ID", "")
        oauth_url = "https://linear.app/oauth/authorize"
        default_scopes = ["read", "write", "issues:create", "comments:create"]
        scope_str = ",".join(scopes or default_scopes)
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope_str,
            "state": state_data,
            "response_type": "code",
        }
    else:
        raise HTTPException(status_code=400, detail=f"OAuth not supported for {provider}")

    auth_url = f"{oauth_url}?{urllib.parse.urlencode(params)}"

    return {
        "auth_url": auth_url,
        "state": state_data,
        "provider": provider,
    }


@app.post("/api/v1/integrations/oauth/callback")
async def oauth_callback(
    request: Request,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Handle OAuth callback and store credentials."""
    from tracertm.api.handlers.oauth import oauth_callback as oauth_callback_handler

    return await oauth_callback_handler(
        request=request,
        data=data,
        claims=claims,
        db=db,
        ensure_project_access_fn=ensure_project_access,
    )


@app.get("/api/v1/integrations/credentials")
async def list_credentials(
    request: Request,
    project_id: str | None = None,
    include_global: bool = True,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List integration credentials for a project."""
    from tracertm.repositories.integration_repository import IntegrationCredentialRepository
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)
    if project_id:
        ensure_project_access(project_id, claims)

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    repo = IntegrationCredentialRepository(db, encryption_service)

    if project_id:
        sub = claims.get("sub") if include_global else None
        credentials = await repo.get_by_project(
            project_id,
            include_global_user_id=sub if isinstance(sub, str) else None,
        )
    else:
        sub = claims.get("sub")
        if not isinstance(sub, str):
            credentials = []
        else:
            credentials = await repo.list_by_user(sub)

    return {
        "credentials": [
            {
                "id": c.id,
                "provider": c.provider,
                "credential_type": c.credential_type,
                "status": c.status,
                "scopes": c.scopes,
                "provider_user_id": c.provider_user_id,
                "provider_metadata": c.provider_metadata,
                "last_validated_at": c.last_validated_at.isoformat() if c.last_validated_at else None,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in credentials
        ],
        "total": len(credentials),
    }


@app.post("/api/v1/integrations/credentials/{credential_id}/validate")
async def validate_credential(
    request: Request,
    credential_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Validate an integration credential."""
    from datetime import datetime

    from tracertm.repositories.integration_repository import IntegrationCredentialRepository
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    if not encryption_key:
        raise HTTPException(status_code=500, detail="Encryption key not configured")

    encryption_service = EncryptionService(encryption_key)
    repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access(credential, claims)

    # Decrypt token and validate
    token = repo.decrypt_token(credential)
    valid = False
    user_info = {}
    error = None

    try:
        client: object = None
        if credential.provider == "github":
            from tracertm.clients.github_client import GitHubClient

            client = GitHubClient(token)
            try:
                user_info = await client.get_authenticated_user()
                valid = True
            finally:
                await client.close()
        elif credential.provider == "linear":
            from tracertm.clients.linear_client import LinearClient

            client = LinearClient(token)
            try:
                user_info = await client.get_viewer()
                valid = True
            finally:
                await client.close()
    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as e:
        error = str(e)

    # Update validation status
    await repo.update_validation_status(
        credential_id,
        valid=valid,
        error=error,
    )

    return {
        "valid": valid,
        "credential_id": credential_id,
        "provider": credential.provider,
        "user": user_info if valid else None,
        "error": error,
        "validated_at": datetime.now(UTC).isoformat(),
    }


@app.delete("/api/v1/integrations/credentials/{credential_id}")
async def delete_credential(
    request: Request,
    credential_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete an integration credential."""
    from tracertm.repositories.integration_repository import IntegrationCredentialRepository
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access(credential, claims)

    await repo.delete(credential_id)

    return {"success": True, "deleted_id": credential_id}


# ==================== INTEGRATION MAPPINGS ====================


@app.get("/api/v1/integrations/mappings")
async def list_mappings(
    request: Request,
    project_id: str,
    provider: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List integration mappings for a project."""
    from tracertm.repositories.integration_repository import IntegrationMappingRepository

    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    repo = IntegrationMappingRepository(db)
    mappings, _total = await repo.list_by_project(project_id, external_system=provider)

    return {
        "mappings": [
            {
                "id": m.id,
                "credential_id": m.integration_credential_id,
                "provider": m.external_system,
                "direction": m.direction,
                "local_item_id": m.project_id if m.tracertm_item_type == "project_root" else m.tracertm_item_id,
                "local_item_type": "project" if m.tracertm_item_type == "project_root" else m.tracertm_item_type,
                "external_id": m.external_id,
                "external_type": m.external_system,
                "external_url": m.external_url,
                "external_key": (m.mapping_metadata or {}).get("external_key"),
                "mapping_metadata": m.mapping_metadata or {},
                "status": m.status,
                "sync_enabled": m.auto_sync,
                "last_synced_at": m.last_sync_at.isoformat() if m.last_sync_at else None,
                "field_mappings": (m.mapping_metadata or {}).get("field_mappings"),
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in mappings
        ],
        "total": len(mappings),
    }


@app.post("/api/v1/integrations/mappings")
async def create_mapping(
    request: Request,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new integration mapping."""
    from tracertm.repositories.integration_repository import (
        IntegrationCredentialRepository,
        IntegrationMappingRepository,
    )
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)

    credential_id = data.get("credential_id")
    if not credential_id:
        raise HTTPException(status_code=400, detail="credential_id required")
    assert isinstance(credential_id, str)
    local_item_id = data.get("local_item_id")
    local_item_type = data.get("local_item_type")
    project_id = data.get("project_id")
    external_id = data.get("external_id")
    external_type = data.get("external_type")
    direction = data.get("direction", "bidirectional")
    mapping_metadata = data.get("mapping_metadata") or {}

    if not project_id and local_item_type == "project":
        project_id = local_item_id

    if not project_id:
        raise HTTPException(status_code=400, detail="project_id required")

    # Validate credential
    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await cred_repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access(credential, claims)

    ensure_project_access(project_id, claims)

    tracertm_item_id = local_item_id
    tracertm_item_type = local_item_type
    if local_item_type == "project":
        from sqlalchemy import select

        from tracertm.models.item import Item
        from tracertm.repositories.item_repository import ItemRepository
        from tracertm.repositories.project_repository import ProjectRepository

        result = await db.execute(
            select(Item).where(
                Item.project_id == project_id,
                Item.item_type == "project_root",
                Item.title == "Integration Root",
            ),
        )
        root_item = result.scalar_one_or_none()
        if not root_item:
            project_repo = ProjectRepository(db)
            project = await project_repo.get_by_id(project_id)
            title = f"{project.name} Integration Root" if project else "Integration Root"
            item_repo = ItemRepository(db)
            root_item = await item_repo.create(
                project_id=project_id,
                title=title,
                view="configuration",
                item_type="project_root",
                description="Synthetic root item for project-level integrations.",
                status="active",
                priority="low",
            )
        tracertm_item_id = root_item.id
        tracertm_item_type = "project_root"

    # Create mapping
    repo = IntegrationMappingRepository(db)
    mapping = await repo.create(
        project_id=str(project_id),
        credential_id=str(credential_id),
        tracertm_item_id=str(tracertm_item_id),
        tracertm_item_type=str(tracertm_item_type),
        external_system=str(external_type),
        external_id=str(external_id) if external_id is not None else "",
        external_url=data.get("external_url") or "",
        direction=direction,
        auto_sync=data.get("sync_enabled", True),
        mapping_metadata={
            **mapping_metadata,
            "external_key": data.get("external_key"),
            "field_mappings": data.get("field_mappings"),
        },
    )

    return {
        "id": mapping.id,
        "credential_id": mapping.integration_credential_id,
        "provider": mapping.external_system,
        "direction": mapping.direction,
        "local_item_id": local_item_id,
        "local_item_type": local_item_type,
        "external_id": mapping.external_id,
        "external_url": mapping.external_url,
        "status": mapping.status,
        "mapping_metadata": mapping.mapping_metadata or {},
        "created_at": mapping.created_at.isoformat() if mapping.created_at else None,
    }


@app.put("/api/v1/integrations/mappings/{mapping_id}")
async def update_mapping(
    request: Request,
    mapping_id: str,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update an integration mapping."""
    from tracertm.repositories.integration_repository import (
        IntegrationCredentialRepository,
        IntegrationMappingRepository,
    )
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)

    repo = IntegrationMappingRepository(db)
    mapping = await repo.get_by_id(mapping_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")

    # Validate access via credential
    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await cred_repo.get_by_id(mapping.integration_credential_id)
    if credential:
        ensure_credential_access(credential, claims)

    # Update mapping (store field mappings inside mapping_metadata)
    updates: dict[str, Any] = {
        "direction": data.get("direction"),
        "status": data.get("status"),
    }
    if "sync_enabled" in data:
        updates["auto_sync"] = data.get("sync_enabled")
    if "field_mappings" in data:
        mapping_metadata = mapping.mapping_metadata or {}
        mapping_metadata["field_mappings"] = data.get("field_mappings")
        updates["mapping_metadata"] = mapping_metadata
    if "mapping_metadata" in data:
        mapping_metadata = mapping.mapping_metadata or {}
        mapping_metadata.update(data.get("mapping_metadata") or {})
        updates["mapping_metadata"] = mapping_metadata

    await repo.update(mapping_id, **updates)
    updated = await repo.get_by_id(mapping_id)

    if not updated:
        raise HTTPException(status_code=404, detail="Updated mapping not found")

    return {
        "id": updated.id,
        "direction": updated.direction,
        "sync_enabled": updated.auto_sync,
        "status": updated.status,
        "updated_at": updated.updated_at.isoformat() if updated.updated_at else None,
    }


@app.delete("/api/v1/integrations/mappings/{mapping_id}")
async def delete_mapping(
    request: Request,
    mapping_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete an integration mapping."""
    from tracertm.repositories.integration_repository import (
        IntegrationCredentialRepository,
        IntegrationMappingRepository,
    )
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)

    repo = IntegrationMappingRepository(db)
    mapping = await repo.get_by_id(mapping_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")

    # Validate access via credential
    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await cred_repo.get_by_id(mapping.integration_credential_id)
    if credential:
        ensure_credential_access(credential, claims)

    await repo.delete(mapping_id)

    return {"success": True, "deleted_id": mapping_id}


# ==================== SYNC MANAGEMENT ====================


@app.get("/api/v1/integrations/sync/status")
async def get_integration_sync_status(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get sync status summary for a project."""
    from sqlalchemy import func, select

    from tracertm.models.integration import (
        IntegrationMapping,
        IntegrationSyncLog,
        IntegrationSyncQueue,
    )
    from tracertm.repositories.integration_repository import (
        IntegrationCredentialRepository,
    )
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    # Get credentials for this project
    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    cred_repo = IntegrationCredentialRepository(db, encryption_service)
    credentials = await cred_repo.get_by_project(project_id, include_global_user_id=claims.get("sub"))

    # Get queue stats
    queue_result = await db.execute(
        select(IntegrationSyncQueue.status, func.count().label("count"))
        .join(IntegrationMapping)
        .where(IntegrationMapping.project_id == project_id)
        .group_by(IntegrationSyncQueue.status),
    )

    queue_stats = {"pending": 0, "processing": 0, "failed": 0, "completed": 0}
    for row in queue_result.all():
        status_val = row[0]
        count_val = row[1]
        queue_stats[str(status_val)] = int(cast("int | str", count_val))

    # Get recent sync logs
    log_result = await db.execute(
        select(IntegrationSyncLog)
        .join(IntegrationMapping)
        .where(IntegrationMapping.project_id == project_id)
        .order_by(IntegrationSyncLog.created_at.desc())
        .limit(10),
    )

    recent_syncs = [
        {
            "id": log.id,
            "provider": log.source_system,
            "event_type": log.operation,
            "direction": log.direction,
            "status": "completed" if log.success else "failed",
            "items_processed": 1 if log.success else 0,
            "items_failed": 0 if log.success else 1,
            "error_message": log.error_message,
            "started_at": log.created_at.isoformat() if log.created_at else None,
            "completed_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in log_result.scalars().all()
    ]

    # Provider summary
    providers = [
        {
            "provider": c.provider,
            "status": c.status,
            "last_validated": c.last_validated_at.isoformat() if c.last_validated_at else None,
        }
        for c in credentials
    ]

    return {
        "project_id": project_id,
        "queue": queue_stats,
        "recent_syncs": recent_syncs,
        "providers": providers,
    }


@app.post("/api/v1/integrations/sync/trigger")
async def trigger_sync(
    request: Request,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Trigger a manual sync for a mapping or credential."""
    from tracertm.repositories.integration_repository import (
        IntegrationCredentialRepository,
        IntegrationMappingRepository,
        IntegrationSyncQueueRepository,
    )
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)

    mapping_id = data.get("mapping_id")
    credential_id = data.get("credential_id")
    if not credential_id:
        raise HTTPException(status_code=400, detail="credential_id required")
    assert isinstance(credential_id, str)
    direction = data.get("direction", "pull")

    if not mapping_id:
        raise HTTPException(status_code=400, detail="mapping_id required")

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    mapping_repo = IntegrationMappingRepository(db)
    mapping = await mapping_repo.get_by_id(mapping_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    credential_id = mapping.integration_credential_id

    credential = await cred_repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access(credential, claims)

    # Create sync queue item
    queue_repo = IntegrationSyncQueueRepository(db)
    queue_item = await queue_repo.enqueue(
        credential_id=credential_id,
        mapping_id=mapping_id,
        event_type="manual_sync",
        direction=direction,
        payload=data.get("payload", {}),
        priority="high",
    )

    return {
        "queued": True,
        "queue_id": queue_item.id,
        "provider": credential.provider,
        "direction": direction,
    }


@app.get("/api/v1/integrations/sync/queue")
async def get_sync_queue(
    request: Request,
    project_id: str,
    status: str | None = None,
    limit: int = 50,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Get sync queue items for a project."""
    from tracertm.repositories.integration_repository import (
        IntegrationSyncQueueRepository,
    )

    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    queue_repo = IntegrationSyncQueueRepository(db)
    items, _total = await queue_repo.list_by_project(project_id, status=status, limit=limit)

    priority_map = {"low": 0, "normal": 1, "high": 2, "critical": 3}
    mapping_lookup = {}
    if items:
        from sqlalchemy import select

        from tracertm.models.integration import IntegrationMapping

        mapping_ids = list({item.mapping_id for item in items})
        result = await db.execute(select(IntegrationMapping).where(IntegrationMapping.id.in_(mapping_ids)))
        mapping_lookup = {m.id: m for m in result.scalars().all()}

    return {
        "items": [
            {
                "id": item.id,
                "provider": getattr(mapping_lookup.get(item.mapping_id), "external_system", "unknown"),
                "event_type": item.event_type,
                "direction": item.direction,
                "status": item.status,
                "priority": priority_map.get(item.priority, 1),
                "retry_count": item.attempts,
                "error_message": item.error_message,
                "scheduled_at": item.next_retry_at.isoformat() if item.next_retry_at else None,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in items
        ],
        "total": len(items),
    }


# ==================== CONFLICT RESOLUTION ====================


@app.get("/api/v1/integrations/conflicts")
async def list_conflicts(
    request: Request,
    project_id: str,
    status: str = "pending",
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List sync conflicts for a project."""
    from tracertm.repositories.integration_repository import (
        IntegrationConflictRepository,
        IntegrationMappingRepository,
    )

    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    conflict_repo = IntegrationConflictRepository(db)
    if status != "pending":
        return {"conflicts": [], "total": 0}
    conflicts, _total = await conflict_repo.list_pending_by_project(project_id)

    mapping_repo = IntegrationMappingRepository(db)
    mappings = {}
    if conflicts:
        mapping_ids = list({c.mapping_id for c in conflicts})
        for mapping_id in mapping_ids:
            mapping = await mapping_repo.get_by_id(mapping_id)
            if mapping:
                mappings[mapping_id] = mapping

    return {
        "conflicts": [
            {
                "id": c.id,
                "mapping_id": c.mapping_id,
                "provider": getattr(mappings.get(c.mapping_id), "external_system", "unknown"),
                "conflict_type": "field_mismatch",
                "field_name": c.field,
                "local_value": c.tracertm_value,
                "external_value": c.external_value,
                "status": c.resolution_status,
                "resolved_value": c.resolved_value,
                "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
                "created_at": c.detected_at.isoformat() if c.detected_at else None,
            }
            for c in conflicts
        ],
        "total": len(conflicts),
    }


@app.post("/api/v1/integrations/conflicts/{conflict_id}/resolve")
async def resolve_conflict(
    request: Request,
    conflict_id: str,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Resolve a sync conflict."""
    from tracertm.repositories.integration_repository import (
        IntegrationConflictRepository,
        IntegrationCredentialRepository,
        IntegrationMappingRepository,
    )
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)

    resolution = data.get("resolution")  # "local", "external", "merge", "skip"
    merged_value = data.get("merged_value")

    if resolution not in {"local", "external", "merge", "skip"}:
        raise HTTPException(status_code=400, detail="Invalid resolution strategy")

    if resolution == "merge" and not merged_value:
        raise HTTPException(status_code=400, detail="Merged value required for merge resolution")

    conflict_repo = IntegrationConflictRepository(db)
    conflict = await conflict_repo.get_by_id(conflict_id)
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")

    # Validate access via mapping
    mapping_repo = IntegrationMappingRepository(db)
    mapping = await mapping_repo.get_by_id(conflict.mapping_id)
    if mapping:
        encryption_key = os.environ.get("ENCRYPTION_KEY", "")
        encryption_service = EncryptionService(encryption_key) if encryption_key else None
        cred_repo = IntegrationCredentialRepository(db, encryption_service)
        credential = await cred_repo.get_by_id(mapping.integration_credential_id)
        if credential:
            ensure_credential_access(credential, claims)

    # Resolve conflict
    if resolution == "skip":
        await conflict_repo.ignore(conflict_id)
    else:
        resolved_value = (
            merged_value
            if resolution == "merge"
            else (conflict.tracertm_value if resolution == "local" else conflict.external_value)
        )
        await conflict_repo.resolve(
            conflict_id,
            resolved_value=str(resolved_value) if resolved_value is not None else "",
            strategy_used=resolution,
        )

    resolved = await conflict_repo.get_by_id(conflict_id)

    return {
        "resolved": True,
        "conflict_id": conflict_id,
        "resolution": resolution,
        "resolved_at": resolved.resolved_at.isoformat() if resolved and resolved.resolved_at else None,
    }


# ==================== EXTERNAL ITEM DISCOVERY ====================


@app.get("/api/v1/integrations/github/repos")
async def list_github_repos(
    request: Request,
    account_id: str | None = None,
    installation_id: str | None = None,
    credential_id: str | None = None,
    search: str | None = None,
    per_page: int = 30,
    page: int = 1,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List GitHub repositories accessible via GitHub App installation or OAuth credential."""
    from tracertm.clients.github_client import GitHubClient
    from tracertm.config.github_app import get_github_app_config
    from tracertm.repositories.account_repository import AccountRepository
    from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository
    from tracertm.repositories.integration_repository import IntegrationCredentialRepository
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)

    user_id = claims.get("sub") if isinstance(claims, dict) else None
    if account_id and user_id:
        # Verify user has access to account
        account_repo = AccountRepository(db)
        role = await account_repo.get_user_role(account_id, user_id)
        if not role:
            raise HTTPException(status_code=403, detail="Access denied to this account")

    client: GitHubClient | None = None
    repos: list[dict] = []

    try:
        # Prefer GitHub App installation if provided
        if installation_id:
            installation_repo = GitHubAppInstallationRepository(db)
            installation = await installation_repo.get_by_id(installation_id)

            if not installation:
                raise HTTPException(status_code=404, detail="Installation not found")

            if account_id and installation.account_id != account_id:
                raise HTTPException(status_code=403, detail="Installation does not belong to this account")

            config = get_github_app_config()
            if not config.is_configured():
                raise HTTPException(status_code=500, detail="GitHub App is not configured")

            # Create client from app installation
            client = await GitHubClient.from_app_installation(
                app_id=config.app_id,
                private_key=config.private_key,
                installation_id=installation.installation_id,
            )

            if search:
                result = await client.search_repos(
                    query=search,
                    per_page=per_page,
                    page=page,
                )
                repos = cast("list[dict[Any, Any]]", result.get("items", []))
            else:
                repos_result = await client.list_installation_repos(
                    _installation_id=installation.installation_id,
                    per_page=per_page,
                    page=page,
                )
                # Handle both formats: { repositories: [...] } and list
                if isinstance(repos_result, dict):
                    repos = cast("list[dict[Any, Any]]", repos_result.get("repositories", []))
                else:
                    repos = repos_result if isinstance(repos_result, list) else []

        # Fallback to OAuth credential
        elif credential_id:
            encryption_key = os.environ.get("ENCRYPTION_KEY", "")
            if not encryption_key:
                raise HTTPException(status_code=500, detail="Encryption key not configured")

            encryption_service = EncryptionService(encryption_key)
            cred_repo = IntegrationCredentialRepository(db, encryption_service)

            credential = await cred_repo.get_by_id(credential_id)
            if not credential:
                raise HTTPException(status_code=404, detail="Credential not found")

            ensure_credential_access(credential, claims)

            if credential.provider != "github":
                raise HTTPException(status_code=400, detail="Credential is not for GitHub")

            token = cred_repo.decrypt_token(credential)
            client = GitHubClient(token)

            if search:
                result = await client.search_repos(
                    query=search,
                    per_page=per_page,
                    page=page,
                )
                repos = cast("list[dict[Any, Any]]", result.get("items", []))
            else:
                repos = cast("list[dict[Any, Any]]", await client.list_user_repos(
                    per_page=per_page,
                    page=page,
                ))
        else:
            raise HTTPException(status_code=400, detail="Either installation_id or credential_id is required")
    finally:
        if client:
            await client.close()

    return {
        "repos": [
            {
                "id": r["id"],
                "name": r["name"],
                "full_name": r["full_name"],
                "description": r.get("description"),
                "html_url": r["html_url"],
                "private": r["private"],
                "owner": {
                    "login": r["owner"]["login"],
                    "avatar_url": r["owner"]["avatar_url"],
                },
                "default_branch": r.get("default_branch", "main"),
                "updated_at": r.get("updated_at"),
            }
            for r in repos
        ],
        "page": page,
        "per_page": per_page,
    }


@app.post("/api/v1/integrations/github/repos")
async def create_github_repo(
    request: Request,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new GitHub repository."""
    from tracertm.clients.github_client import GitHubClient
    from tracertm.config.github_app import get_github_app_config
    from tracertm.repositories.account_repository import AccountRepository
    from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository

    enforce_rate_limit(request, claims)

    user_id = claims.get("sub") if isinstance(claims, dict) else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    installation_id = data.get("installation_id")
    account_id = data.get("account_id")
    name = data.get("name")
    description = data.get("description")
    private = data.get("private", False)
    org = data.get("org")  # Optional organization name

    if not installation_id or not name:
        raise HTTPException(status_code=400, detail="installation_id and name are required")

    # Verify user has access to account
    if account_id:
        account_repo = AccountRepository(db)
        role = await account_repo.get_user_role(account_id, user_id)
        if not role:
            raise HTTPException(status_code=403, detail="Access denied to this account")

    installation_repo = GitHubAppInstallationRepository(db)
    installation = await installation_repo.get_by_id(installation_id)

    if not installation:
        raise HTTPException(status_code=404, detail="Installation not found")

    if account_id and installation.account_id != account_id:
        raise HTTPException(status_code=403, detail="Installation does not belong to this account")

    config = get_github_app_config()
    if not config.is_configured():
        raise HTTPException(status_code=500, detail="GitHub App is not configured")

    # Create client from app installation
    client = await GitHubClient.from_app_installation(
        app_id=config.app_id,
        private_key=config.private_key,
        installation_id=installation.installation_id,
    )

    try:
        created_repo = cast("dict[str, Any]", await client.create_repo(
            name=name,
            description=description,
            private=private,
            org=org or installation.account_login if installation.target_type == "Organization" else None,
        ))
    finally:
        await client.close()

    owner_info = cast("dict[str, Any]", created_repo.get("owner", {}))
    return {
        "id": created_repo["id"],
        "name": created_repo["name"],
        "full_name": created_repo["full_name"],
        "description": created_repo.get("description"),
        "html_url": created_repo["html_url"],
        "private": created_repo["private"],
        "owner": {
            "login": owner_info["login"],
            "avatar_url": owner_info["avatar_url"],
        },
        "default_branch": created_repo.get("default_branch", "main"),
        "created_at": created_repo.get("created_at"),
    }


@app.get("/api/v1/integrations/github/repos/{owner}/{repo}/issues")
async def list_github_issues(
    request: Request,
    owner: str,
    repo: str,
    credential_id: str,
    state: str = "open",
    per_page: int = 30,
    page: int = 1,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List GitHub issues for a repository."""
    from tracertm.clients.github_client import GitHubClient, IssueListParams
    from tracertm.repositories.integration_repository import IntegrationCredentialRepository
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    if not encryption_key:
        raise HTTPException(status_code=500, detail="Encryption key not configured")

    encryption_service = EncryptionService(encryption_key)
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await cred_repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access(credential, claims)

    token = cred_repo.decrypt_token(credential)
    client = GitHubClient(token)

    try:
        issues = cast("list[dict[str, Any]]", await client.list_issues(
            owner=owner,
            repo=repo,
            params=IssueListParams(state=state, per_page=per_page, page=page),
        ))
    finally:
        await client.close()

    return {
        "issues": [
            {
                "id": i["id"],
                "number": i["number"],
                "title": i["title"],
                "state": i["state"],
                "html_url": i["html_url"],
                "body": i.get("body", "")[:500] if i.get("body") else None,
                "user": {
                    "login": i["user"]["login"],
                    "avatar_url": i["user"]["avatar_url"],
                },
                "labels": [l["name"] for l in i.get("labels", [])],
                "assignees": [a["login"] for a in i.get("assignees", [])],
                "created_at": i["created_at"],
                "updated_at": i["updated_at"],
            }
            for i in issues
            if "pull_request" not in i  # Filter out PRs
        ],
        "page": page,
        "per_page": per_page,
    }


# ==================== GITHUB APP INSTALLATION ====================


@app.get("/api/v1/integrations/github/app/install-url")
async def get_github_app_install_url(
    account_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get GitHub App installation URL for an account."""
    from tracertm.config.github_app import get_github_app_config
    from tracertm.repositories.account_repository import AccountRepository

    user_id = claims.get("sub") if isinstance(claims, dict) else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Verify user has access to account
    account_repo = AccountRepository(db)
    role = await account_repo.get_user_role(account_id, user_id)
    if not role:
        raise HTTPException(status_code=403, detail="Access denied to this account")

    config = get_github_app_config()
    if not config.is_configured():
        raise HTTPException(status_code=500, detail="GitHub App is not configured")

    # Generate state token with account_id
    import secrets

    state = secrets.token_urlsafe(32)
    state_data = f"{account_id}:{state}"

    install_url = config.get_installation_url(state=state_data)

    return {
        "install_url": install_url,
        "state": state_data,
    }


@app.post("/api/v1/integrations/github/app/webhook")
async def github_app_webhook_endpoint(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Handle GitHub App webhook events."""
    from tracertm.api.handlers.webhooks import github_app_webhook

    return await github_app_webhook(request, db)


@app.get("/api/v1/integrations/github/app/installations")
async def list_github_app_installations(
    account_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List GitHub App installations for an account."""
    from tracertm.repositories.account_repository import AccountRepository
    from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository

    user_id = claims.get("sub") if isinstance(claims, dict) else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Verify user has access to account
    account_repo = AccountRepository(db)
    role = await account_repo.get_user_role(account_id, user_id)
    if not role:
        raise HTTPException(status_code=403, detail="Access denied to this account")

    installation_repo = GitHubAppInstallationRepository(db)
    installations = await installation_repo.list_by_account(account_id)

    return {
        "installations": [
            {
                "id": inst.id,
                "installation_id": inst.installation_id,
                "account_login": inst.account_login,
                "target_type": inst.target_type,
                "permissions": inst.permissions,
                "repository_selection": inst.repository_selection,
                "suspended_at": inst.suspended_at.isoformat() if inst.suspended_at else None,
                "created_at": inst.created_at.isoformat(),
            }
            for inst in installations
        ],
        "total": len(installations),
    }


@app.post("/api/v1/integrations/github/app/installations/{installation_id}/link")
async def link_github_app_installation(
    installation_id: str,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Link a GitHub App installation to an account.

    Functional Requirements:
    - FR-DISC-001

    User Stories:
    - US-INT-001

    Epics:
    - EPIC-001
    """
    from tracertm.repositories.account_repository import AccountRepository
    from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository

    user_id = claims.get("sub") if isinstance(claims, dict) else None
    account_id = data.get("account_id")

    if not user_id or not account_id:
        raise HTTPException(status_code=400, detail="account_id is required")

    # Verify user has access to account
    account_repo = AccountRepository(db)
    role = await account_repo.get_user_role(account_id, user_id)
    if not role:
        raise HTTPException(status_code=403, detail="Access denied to this account")

    installation_repo = GitHubAppInstallationRepository(db)
    installation = await installation_repo.get_by_id(installation_id)

    if not installation:
        raise HTTPException(status_code=404, detail="Installation not found")

    if installation.account_id and installation.account_id != account_id:
        raise HTTPException(status_code=400, detail="Installation already linked to another account")

    installation.account_id = account_id
    await db.commit()

    return {
        "status": "linked",
        "installation_id": installation.id,
        "account_id": account_id,
    }


@app.delete("/api/v1/integrations/github/app/installations/{installation_id}")
async def delete_github_app_installation(
    installation_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a GitHub App installation."""
    from tracertm.repositories.account_repository import AccountRepository
    from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository

    user_id = claims.get("sub") if isinstance(claims, dict) else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    installation_repo = GitHubAppInstallationRepository(db)
    installation = await installation_repo.get_by_id(installation_id)

    if not installation:
        raise HTTPException(status_code=404, detail="Installation not found")

    # Verify user has access to account
    if installation.account_id:
        account_repo = AccountRepository(db)
        role = await account_repo.get_user_role(installation.account_id, user_id)
        if not role:
            raise HTTPException(status_code=403, detail="Access denied")

    await installation_repo.delete(installation_id)
    await db.commit()

    return {"status": "deleted"}


@app.get("/api/v1/integrations/github/projects")
async def list_github_projects(
    request: Request,
    owner: str,
    installation_id: str | None = None,
    credential_id: str | None = None,
    is_org: bool = True,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List GitHub Projects v2 for an owner."""
    from tracertm.clients.github_client import GitHubClient
    from tracertm.config.github_app import get_github_app_config
    from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository
    from tracertm.repositories.integration_repository import IntegrationCredentialRepository
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)

    client: GitHubClient | None = None

    try:
        # Prefer GitHub App installation
        if installation_id:
            installation_repo = GitHubAppInstallationRepository(db)
            installation = await installation_repo.get_by_id(installation_id)

            if not installation:
                raise HTTPException(status_code=404, detail="Installation not found")

            config = get_github_app_config()
            if not config.is_configured():
                raise HTTPException(status_code=500, detail="GitHub App is not configured")

            client = await GitHubClient.from_app_installation(
                app_id=config.app_id,
                private_key=config.private_key,
                installation_id=installation.installation_id,
            )

        # Fallback to OAuth credential
        elif credential_id:
            encryption_key = os.environ.get("ENCRYPTION_KEY", "")
            if not encryption_key:
                raise HTTPException(status_code=500, detail="Encryption key not configured")

            encryption_service = EncryptionService(encryption_key)
            cred_repo = IntegrationCredentialRepository(db, encryption_service)

            credential = await cred_repo.get_by_id(credential_id)
            if not credential:
                raise HTTPException(status_code=404, detail="Credential not found")

            ensure_credential_access(credential, claims)

            token = cred_repo.decrypt_token(credential)
            client = GitHubClient(token)
        else:
            raise HTTPException(status_code=400, detail="Either installation_id or credential_id is required")

        projects = await client.list_projects_graphql(owner=owner, is_org=is_org)
    finally:
        if client:
            await client.close()

    return {
        "projects": [
            {
                "id": p["id"],
                "title": p["title"],
                "description": p.get("shortDescription"),
                "url": p["url"],
                "closed": p.get("closed", False),
                "public": p.get("public", False),
                "created_at": p.get("createdAt"),
                "updated_at": p.get("updatedAt"),
            }
            for p in projects
        ],
    }


@app.post("/api/v1/integrations/github/projects/auto-link")
async def auto_link_github_projects(
    request: Request,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Auto-link GitHub Projects for a repository."""
    from tracertm.clients.github_client import GitHubClient
    from tracertm.config.github_app import get_github_app_config
    from tracertm.repositories.github_app_repository import GitHubAppInstallationRepository
    from tracertm.services.github_project_service import GitHubProjectService

    enforce_rate_limit(request, claims)

    project_id = data.get("project_id")
    github_repo_owner = data.get("github_repo_owner")
    github_repo_name = data.get("github_repo_name")
    github_repo_id = data.get("github_repo_id")
    installation_id = data.get("installation_id")

    if not all([project_id, github_repo_owner, github_repo_name, github_repo_id, installation_id]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Type casting for mypy
    from typing import cast

    p_id = cast("str", project_id)
    i_id = cast("str", installation_id)
    repo_owner = cast("str", github_repo_owner)
    repo_name = cast("str", github_repo_name)
    repo_id = cast("int", github_repo_id)

    ensure_project_access(p_id, claims)

    installation_repo = GitHubAppInstallationRepository(db)
    installation = await installation_repo.get_by_id(i_id)

    if not installation:
        raise HTTPException(status_code=404, detail="Installation not found")

    config = get_github_app_config()
    if not config.is_configured():
        raise HTTPException(status_code=500, detail="GitHub App is not configured")

    # Create client from app installation
    client = await GitHubClient.from_app_installation(
        app_id=config.app_id,
        private_key=config.private_key,
        installation_id=installation.installation_id,
    )

    try:
        service = GitHubProjectService(db)
        linked_projects = await service.auto_link_projects_for_repo(
            project_id=p_id,
            github_repo_owner=repo_owner,
            github_repo_name=repo_name,
            github_repo_id=repo_id,
            client=client,
        )
    finally:
        await client.close()

    return {
        "linked_projects": linked_projects,
        "total": len(linked_projects),
    }


@app.get("/api/v1/integrations/github/projects/linked")
async def list_linked_github_projects(
    request: Request,
    project_id: str | None = None,
    github_repo_id: int | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List linked GitHub Projects."""
    from tracertm.repositories.github_project_repository import GitHubProjectRepository

    enforce_rate_limit(request, claims)

    repo = GitHubProjectRepository(db)

    if project_id:
        ensure_project_access(project_id, claims)
        projects = await repo.get_by_project_id(project_id)
    elif github_repo_id:
        projects = await repo.get_by_repo(github_repo_id)
    else:
        raise HTTPException(status_code=400, detail="Either project_id or github_repo_id is required")

    return {
        "projects": [
            {
                "id": p.id,
                "project_id": p.project_id,
                "github_repo_id": p.github_repo_id,
                "github_repo_owner": p.github_repo_owner,
                "github_repo_name": p.github_repo_name,
                "github_project_id": p.github_project_id,
                "github_project_number": p.github_project_number,
                "auto_sync": p.auto_sync,
                "sync_config": p.sync_config,
            }
            for p in projects
        ],
        "total": len(projects),
    }


@app.delete("/api/v1/integrations/github/projects/{github_project_id}/unlink")
async def unlink_github_project(
    request: Request,
    github_project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Unlink a GitHub Project from a TraceRTM project."""
    from tracertm.repositories.github_project_repository import GitHubProjectRepository

    enforce_rate_limit(request, claims)

    repo = GitHubProjectRepository(db)
    github_project = await repo.get_by_id(github_project_id)

    if not github_project:
        raise HTTPException(status_code=404, detail="GitHub Project link not found")

    ensure_project_access(github_project.project_id, claims)

    await repo.delete(github_project_id)
    await db.commit()

    return {"status": "unlinked"}


@app.get("/api/v1/integrations/linear/teams")
async def list_linear_teams(
    request: Request,
    credential_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List Linear teams accessible with the credential."""
    from tracertm.clients.linear_client import LinearClient
    from tracertm.repositories.integration_repository import IntegrationCredentialRepository
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    if not encryption_key:
        raise HTTPException(status_code=500, detail="Encryption key not configured")

    encryption_service = EncryptionService(encryption_key)
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await cred_repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access(credential, claims)

    if credential.provider != "linear":
        raise HTTPException(status_code=400, detail="Credential is not for Linear")

    token = cred_repo.decrypt_token(credential)
    client = LinearClient(token)

    try:
        teams = await client.list_teams()
    finally:
        await client.close()

    return {
        "teams": [
            {
                "id": t["id"],
                "name": t["name"],
                "key": t["key"],
                "description": t.get("description"),
                "icon": t.get("icon"),
                "color": t.get("color"),
            }
            for t in teams
        ],
    }


@app.get("/api/v1/integrations/linear/teams/{team_id}/issues")
async def list_linear_issues(
    request: Request,
    team_id: str,
    credential_id: str,
    first: int = 50,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List Linear issues for a team."""
    from tracertm.clients.linear_client import LinearClient
    from tracertm.repositories.integration_repository import IntegrationCredentialRepository
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    if not encryption_key:
        raise HTTPException(status_code=500, detail="Encryption key not configured")

    encryption_service = EncryptionService(encryption_key)
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await cred_repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access(credential, claims)

    token = cred_repo.decrypt_token(credential)
    client = LinearClient(token)

    try:
        issues_result = await client.list_issues(team_id=team_id, first=first)
        issues = cast("list[dict[str, Any]]", issues_result.get("nodes", []))
    finally:
        await client.close()

    return {
        "issues": [
            {
                "id": i["id"],
                "identifier": i["identifier"],
                "title": i["title"],
                "description": i.get("description", "")[:500] if i.get("description") else None,
                "state": i.get("state", {}).get("name"),
                "priority": i.get("priority"),
                "url": i["url"],
                "assignee": i.get("assignee", {}).get("name") if i.get("assignee") else None,
                "labels": [l["name"] for l in i.get("labels", {}).get("nodes", [])],
                "created_at": i.get("createdAt"),
                "updated_at": i.get("updatedAt"),
            }
            for i in issues
        ],
    }


@app.get("/api/v1/integrations/linear/projects")
async def list_linear_projects(
    request: Request,
    credential_id: str,
    _first: int = 50,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List Linear projects."""
    from tracertm.clients.linear_client import LinearClient
    from tracertm.repositories.integration_repository import IntegrationCredentialRepository
    from tracertm.services.encryption_service import EncryptionService

    enforce_rate_limit(request, claims)

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    if not encryption_key:
        raise HTTPException(status_code=500, detail="Encryption key not configured")

    encryption_service = EncryptionService(encryption_key)
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await cred_repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access(credential, claims)

    token = cred_repo.decrypt_token(credential)
    client = LinearClient(token)

    try:
        projects = await client.list_projects()
    finally:
        await client.close()

    return {
        "projects": [
            {
                "id": p["id"],
                "name": p["name"],
                "description": p.get("description"),
                "state": p.get("state"),
                "progress": p.get("progress"),
                "url": p["url"],
                "start_date": p.get("startDate"),
                "target_date": p.get("targetDate"),
            }
            for p in projects
        ],
    }


# ==================== EXTERNAL WEBHOOK RECEIVERS ====================


@app.post("/api/v1/webhooks/github/{webhook_id}")
async def receive_github_webhook(
    request: Request,
    webhook_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Receive GitHub webhook events."""
    import hashlib
    import hmac

    from tracertm.models.webhook_integration import WebhookStatus
    from tracertm.repositories.integration_repository import IntegrationSyncQueueRepository
    from tracertm.repositories.webhook_repository import WebhookRepository

    # Get webhook config
    webhook_repo = WebhookRepository(db)
    webhook = await webhook_repo.get_by_id(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    if webhook.status != WebhookStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Webhook is inactive")

    # Verify signature
    body = await request.body()
    signature_header = request.headers.get("X-Hub-Signature-256", "")

    if webhook.webhook_secret:
        expected_signature = "sha256=" + hmac.new(webhook.webhook_secret.encode(), body, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(signature_header, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse event
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    payload = await request.json()

    # Queue for processing
    # Note: Using enqueue with mapping_id=None might fail if model requires it.
    # For now, we use create_log and assume sync queue handles it via other means or fix mapping later.
    credential_id = getattr(webhook, "credential_id", None)
    if not credential_id:
        raise HTTPException(status_code=400, detail="Webhook missing credential_id")

    queue_repo = IntegrationSyncQueueRepository(db)
    await queue_repo.enqueue(
        credential_id=str(credential_id),
        mapping_id=str(getattr(webhook, "mapping_id", None) or webhook_id),
        event_type=f"webhook:{event_type}",
        direction="pull",
        payload={
            "webhook_id": webhook_id,
            "event_type": event_type,
            "delivery_id": request.headers.get("X-GitHub-Delivery"),
            "data": payload,
        },
    )

    # Log delivery
    await webhook_repo.create_log(
        webhook_id=webhook_id,
        event_type=event_type,
        payload_size_bytes=len(body),
        success=True,
        status_code=200,
    )

    return {"received": True, "event": event_type}


@app.post("/api/v1/webhooks/linear/{webhook_id}")
async def receive_linear_webhook(
    request: Request,
    webhook_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Receive Linear webhook events."""
    import hashlib
    import hmac

    from tracertm.models.webhook_integration import WebhookStatus
    from tracertm.repositories.integration_repository import IntegrationSyncQueueRepository
    from tracertm.repositories.webhook_repository import WebhookRepository

    # Get webhook config
    webhook_repo = WebhookRepository(db)
    webhook = await webhook_repo.get_by_id(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    if webhook.status != WebhookStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Webhook is inactive")

    # Verify signature
    body = await request.body()
    signature_header = request.headers.get("Linear-Signature", "")

    if webhook.webhook_secret:
        expected_signature = hmac.new(webhook.webhook_secret.encode(), body, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(signature_header, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse event
    payload = await request.json()
    event_type = payload.get("type", "unknown")
    action = payload.get("action", "")

    credential_id = getattr(webhook, "credential_id", None)
    if not credential_id:
        raise HTTPException(status_code=400, detail="Webhook missing credential_id")

    queue_repo = IntegrationSyncQueueRepository(db)
    await queue_repo.enqueue(
        credential_id=str(credential_id),
        mapping_id=str(getattr(webhook, "mapping_id", None) or webhook_id),
        event_type=f"webhook:{event_type}:{action}",
        direction="pull",
        payload={
            "webhook_id": webhook_id,
            "event_type": event_type,
            "action": action,
            "data": payload.get("data", {}),
        },
    )

    # Log delivery
    await webhook_repo.create_log(
        webhook_id=webhook_id,
        event_type=f"{event_type}:{action}",
        payload_size_bytes=len(body),
        success=True,
        status_code=200,
    )

    return {"received": True, "event": event_type, "action": action}


# ==================== INTEGRATION STATS ====================


@app.get("/api/v1/integrations/stats")
async def get_integration_stats(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get integration statistics for a project."""
    from tracertm.api.handlers.integrations import get_integration_stats_handler

    return await get_integration_stats_handler(request, project_id, claims, db)


# ==================== AI CHAT ====================

from tracertm.api.handlers.chat import simple_chat as _simple_chat_impl
from tracertm.api.handlers.chat import stream_chat as _stream_chat_impl

# Register chat endpoints
app.post("/api/v1/chat/stream")(_stream_chat_impl)
app.post("/api/v1/chat")(_simple_chat_impl)

CreateProjectRequest = projects.CreateProjectRequest
UpdateProjectRequest = projects.UpdateProjectRequest
ImportRequest = projects.ImportRequest
list_projects = projects.list_projects
get_project = projects.get_project
create_project = projects.create_project
update_project = projects.update_project
delete_project = projects.delete_project
export_project = projects.export_project
import_project = projects.import_project
import_full_project = projects.import_full_project

if __name__ == "__main__":
    import uvicorn

    # Dev-only: bind to all interfaces for local development
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # nosec B104 -- dev-only __main__ guard

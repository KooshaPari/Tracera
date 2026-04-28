"""FastAPI + Pheno-SDK example (integration-first stack)

Demonstrates: adapter-kit (DI), config-kit (config), HTTPX (client via pydevkit),
OpenTelemetry + structlog bootstrap using new helpers (Task 2.3).

Updated to use:
- observability_kit.helpers.configure_otel()
- observability_kit.helpers.configure_structlog()
- Standardized bootstrap pattern from docs/guides/observability-bootstrap.md

Note: Requires optional deps (fastapi, uvicorn, httpx, opentelemetry, structlog).
This file is illustrative and not executed by the test suite.
"""

try:  # Optional imports for illustration
    from fastapi import FastAPI
except Exception:  # pragma: no cover
    FastAPI = None  # type: ignore

from adapter_kit import Container
from pheno_config.integrations import PhenoConfig as Config

# Import observability helpers from pheno
try:
    from pheno.observability import (
        add_prometheus_endpoint,
        configure_otel,
        configure_structlog,
        get_logger,
        get_meter_provider,
        get_tracer_provider,
        init_otel,
    )

    _OBSERVABILITY_AVAILABLE = True
except ImportError:
    _OBSERVABILITY_AVAILABLE = False
    add_prometheus_endpoint = None  # type: ignore
    init_otel = None  # type: ignore

# HTTP client helpers
try:
    from pheno.dev.http import (
        build_async_httpx_correlation_hooks,
        build_async_httpx_otel_hooks,
        create_async_client,
    )

    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False


class Settings(Config):
    service_name: str = "demo-api"
    service_version: str = "1.0.0"
    environment: str = "dev"
    upstream_base: str = "https://httpbin.org"
    log_level: str = "INFO"
    # OTEL configuration
    enable_otel: bool = True
    enable_structlog: bool = True
    otlp_endpoint: str | None = None  # e.g., "localhost:4317"
    console_export: bool = True  # Export to console for dev


# Global container
container = Container()
settings = Settings.from_env(prefix="APP_")
container.register_instance(Settings, settings)

# Initialize observability (Task 2.3 - new bootstrap helpers)
if _OBSERVABILITY_AVAILABLE and settings.enable_otel:
    try:
        # Configure OpenTelemetry with new helpers
        configure_otel(
            service_name=settings.service_name,
            service_version=settings.service_version,
            environment=settings.environment,
            enable_tracing=True,
            enable_metrics=True,
            otlp_endpoint=settings.otlp_endpoint,
            console_export=settings.console_export,
        )
        print(f"✓ OpenTelemetry configured: {settings.service_name} ({settings.environment})")
    except Exception as e:
        print(f"⚠ OpenTelemetry setup failed: {e}")

if _OBSERVABILITY_AVAILABLE and settings.enable_structlog:
    try:
        # Configure structured logging
        configure_structlog(
            service_name=settings.service_name,
            environment=settings.environment,
            log_level=settings.log_level,
            json_logs=None,  # Auto-detect based on environment
            add_correlation_id=True,
        )

        # Get logger for application
        logger = get_logger(__name__)
        logger.info(
            "application_initialized",
            service=settings.service_name,
            version=settings.service_version,
            environment=settings.environment,
        )
        print(f"✓ Structlog configured: level={settings.log_level}")
    except Exception as e:
        print(f"⚠ Structlog setup failed: {e}")
        logger = None  # type: ignore
else:
    logger = None  # type: ignore


def create_app() -> FastAPI:  # type: ignore[valid-type]
    """
    Create FastAPI application with observability wiring.
    """
    app = FastAPI(
        title=settings.service_name,
        version=settings.service_version,
        description="Integrated FastAPI + Pheno-SDK example with OTEL/structlog",
    )

    # Legacy prometheus endpoint (if available)
    if add_prometheus_endpoint:
        try:
            add_prometheus_endpoint(app, path="/metrics")
        except Exception:
            pass

    @app.get("/healthz")
    async def healthz():
        """
        Health check endpoint.
        """
        if logger:
            logger.debug("health_check_requested")

        return {
            "status": "ok",
            "service": settings.service_name,
            "version": settings.service_version,
            "environment": settings.environment,
        }

    @app.get("/ip")
    async def show_ip():
        """
        Demonstrate HTTPX with OTEL/correlation hooks.
        """
        if logger:
            logger.info("ip_check_requested", upstream=settings.upstream_base)

        if not _HTTPX_AVAILABLE:
            return {"error": "HTTPX not available"}

        # Compose OTEL and correlation hooks if packages present
        hooks = {}
        try:
            ot = build_async_httpx_otel_hooks()
            for k, v in ot.items():
                hooks.setdefault(k, []).extend(v)
        except Exception:
            pass
        try:
            corr = build_async_httpx_correlation_hooks()
            for k, v in corr.items():
                hooks.setdefault(k, []).extend(v)
        except Exception:
            pass

        try:
            async with create_async_client(event_hooks=hooks) as http:
                resp = await http.get(f"{settings.upstream_base}/ip", timeout=5)
                data = resp.json()

                if logger:
                    logger.info("ip_check_completed", origin=data.get("origin"))

                return data
        except Exception as e:
            if logger:
                logger.error("ip_check_failed", error=str(e))
            return {"error": str(e)}

    @app.get("/observability")
    async def observability_status():
        """
        Show observability configuration status.
        """
        tracer_provider = get_tracer_provider() if _OBSERVABILITY_AVAILABLE else None
        meter_provider = get_meter_provider() if _OBSERVABILITY_AVAILABLE else None

        return {
            "observability": {
                "available": _OBSERVABILITY_AVAILABLE,
                "otel_configured": tracer_provider is not None,
                "metrics_configured": meter_provider is not None,
                "structlog_configured": logger is not None,
            },
            "settings": {
                "service": settings.service_name,
                "version": settings.service_version,
                "environment": settings.environment,
                "log_level": settings.log_level,
            },
        }

    return app


if __name__ == "__main__" and FastAPI is not None:  # pragma: no cover
    import uvicorn

    uvicorn.run(create_app(), host="127.0.0.1", port=8000)

"""FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from .handlers import router
from ..infrastructure.adapters.persistence import PostgresAdapter
from ..infrastructure.adapters.messaging import NatsAdapter
from ..infrastructure.config import settings
from ..infrastructure.logging import logger


# Global adapters
pg_adapter: PostgresAdapter | None = None
nats_adapter: NatsAdapter | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global pg_adapter, nats_adapter

    # Startup
    logger.info("starting_application", service=settings.service_name)
    pg_adapter = PostgresAdapter(settings.database_url)
    nats_adapter = NatsAdapter(settings.nats_url)

    try:
        await nats_adapter.connect()
    except Exception as e:
        logger.warning("nats_connection_failed", error=str(e))

    yield

    # Shutdown
    logger.info("shutting_down_application")
    if pg_adapter:
        await pg_adapter.close()
    if nats_adapter:
        await nats_adapter.close()


app = FastAPI(
    title=settings.service_name,
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/ready")
async def ready():
    """Readiness check endpoint."""
    return {"status": "ready"}

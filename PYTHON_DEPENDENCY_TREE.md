# Python Dependency Tree Analysis

**Scope:** `src/tracertm` and `backend/tests`
**Generated:** 2026-02-06

## High-Level Architecture

The project follows a standard layered architecture:

1.  **Presentation Layer (Consumers)**
    *   `tracertm.api` (FastAPI): Imports Services, Models, Repositories.
    *   `tracertm.cli` (Typer/Click): Imports Services, Models, Managers, Storage.
    *   `tracertm.mcp` (MCP Server): Imports Core, Services, Models.
    *   `tracertm.workflows` (Temporal): Imports Services, Repositories.

2.  **Business Logic Layer**
    *   `tracertm.services`: Core logic. Imports Repositories, Models, and other Services.
    *   `tracertm.agent`: Agent logic. Imports Events, Sandbox, Session Store.

3.  **Data Access Layer**
    *   `tracertm.repositories`: Database abstractions. Imports Models.
    *   `tracertm.storage`: Local file storage/sync. Imports Models.

4.  **Domain Layer**
    *   `tracertm.models`: Pydantic/SQLAlchemy models. Mostly independent (leaf nodes), imports `tracertm.models.base`.

5.  **Infrastructure/Core**
    *   `tracertm.core`: Config, Context, Concurrency.
    *   `tracertm.infrastructure`: Event Bus, NATS, Feature Flags.
    *   `tracertm.database`: DB Connection.

## Detailed Dependency Graph (Sampled)

### API (`tracertm.api`)
*   **entry point**: `tracertm.api.main`
    *   -> `tracertm.services` (cache, temporal, item, link...)
    *   -> `tracertm.repositories` (item, link, project, problem...)
    *   -> `tracertm.models` (item, link, integration...)
    *   -> `tracertm.api.handlers`
    *   -> `tracertm.api.routers`
*   **routers**: `tracertm.api.routers.*`
    *   -> `tracertm.services.*` (feature, scenario, contract, execution...)
    *   -> `tracertm.repositories.*` (event, item, link...)
    *   -> `tracertm.models.*`

### CLI (`tracertm.cli`)
*   **entry point**: `tracertm.cli.app`
    *   -> `tracertm.cli.commands.*`
*   **commands**: `tracertm.cli.commands.*`
    *   -> `tracertm.config.manager`
    *   -> `tracertm.storage.local_storage`
    *   -> `tracertm.models.*`
    *   -> `tracertm.services.*` (progress, chaos, benchmark...)
    *   -> `tracertm.cli.ui`

### Services (`tracertm.services`)
*   `tracertm.services.item_service`
    *   -> `tracertm.repositories.item_repository`
    *   -> `tracertm.repositories.event_repository`
    *   -> `tracertm.models.item`
*   `tracertm.services.event_service`
    *   -> `tracertm.repositories.event_repository`
    *   -> `tracertm.models.event`
*   `tracertm.services.graph_service`
    *   -> `tracertm.models.graph`
    *   -> `tracertm.models.item`
*   `tracertm.services.execution_service`
    *   -> `tracertm.repositories.execution_repository`
    *   -> `tracertm.services.execution.docker_orchestrator`
*   *Observation*: Heavy inter-service dependency (e.g., `graph_snapshot_service` -> `graph_service`).

### Repositories (`tracertm.repositories`)
*   `tracertm.repositories.item_repository`
    *   -> `tracertm.models.item`
    *   -> `tracertm.models.link`
    *   -> `tracertm.models.node_kind`
*   `tracertm.repositories.event_repository`
    *   -> `tracertm.models.event`
*   *Observation*: Generally clean, downward dependencies on Models.

### Models (`tracertm.models`)
*   `tracertm.models.item` -> `tracertm.models.base`, `tracertm.models.types`
*   `tracertm.models.project` -> `tracertm.models.base`
*   *Observation*: Base classes `tracertm.models.base` are the foundation.

### Infrastructure & Core
*   `tracertm.database.connection` -> `tracertm.models.base`
*   `tracertm.infrastructure.event_bus` -> `tracertm.infrastructure.nats_client`

### Backend Tests (`backend/tests`)
*   Tests in `backend/tests` (e.g., `integration/test_nats_events.py`) depend on `backend.tests.integration.test_helpers`.
*   They appear to test the system via external interfaces (NATS, API) rather than importing `tracertm` directly, ensuring separation.

## Key Relationships & Hotspots

1.  **`tracertm.models.item`**: The central data structure. Imported by:
    *   Repositories: `ItemRepository`, `LinkRepository`
    *   Services: `ItemService`, `GraphService`, `AgentMetricsService`
    *   CLI: `item`, `search`, `export` commands
    *   API: `items` handler, `main` app
    *   MCP: `tools.items`

2.  **`tracertm.repositories`**: The bridge between logic and data.
    *   Heavily used by Services.
    *   *Directly* accessed by API (`main.py`, `routers`) - This is a potential architectural shortcut; ideally, API should go through Services.

3.  **`tracertm.config.manager`**:
    *   Ubiquitous usage in CLI, API deps, and MCP tools.

4.  **`tracertm.storage.local_storage`**:
    *   Key for the CLI's local operation mode.
    *   Used by `tracertm.cli.commands.*` and `tracertm.mcp.tools`.

## Summary
The dependency tree confirms a monolithic modular structure within `src/tracertm`. The `backend/` directory is logically separate (Go service) with its own Python integration tests that treat the system as a black box (or grey box via helpers).

Internal Python dependencies are well-organized into standard layers, though some "layer skipping" (API -> Repository) exists.

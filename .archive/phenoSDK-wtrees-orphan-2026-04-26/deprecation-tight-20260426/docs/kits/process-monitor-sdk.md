# Process Monitor SDK

## At a Glance
- **Purpose:** Manage and observe long-running processes with health checks, TUIs, and API endpoints.
- **Best For:** Local development clusters, multi-process applications, or orchestrated background workers.
- **Key Building Blocks:** `MonitorFactory`, `BaseMonitor`, `ProcessManager`, `HealthMonitor`, TUI/API runners.

## Core Capabilities
- Start/stop/restart processes with auto-restart policies and graceful shutdown.
- Health monitoring via HTTP checks, port probes, and custom callables.
- Rich Textual-powered TUI dashboard for real-time status.
- REST + WebSocket server to expose process telemetry programmatically.
- YAML configuration loader for declarative setup.

## Getting Started

### Installation
```
pip install process-monitor-sdk
# Optional TUI + API extras
pip install "process-monitor-sdk[tui,api]"
```

### Minimal Example
```python
from process_monitor import MonitorFactory

monitor = MonitorFactory.create(
    name="stack",
    processes=[
        {"name": "api", "command": "uvicorn app:app", "port": 8000, "auto_restart": True},
        {"name": "worker", "command": "python worker.py"},
    ],
    health_checks=[{"url": "http://localhost:8000/health", "interval": 10}],
)

monitor.run_with_tui()
```

## How It Works
- `MonitorFactory` builds monitor instances from dictionaries or YAML files.
- `BaseMonitor` orchestrates process lifecycle via `components.ProcessManager` (start, stop, restart).
- `HealthMonitor` runs asynchronous checks and updates process status.
- Run modes:
  - `run_with_tui()` renders a Textual dashboard.
  - `run_headless()` monitors in background.
  - `run_with_api(port)` launches a FastAPI/WS WebSocket server.

## Usage Recipes
- Configure auto-restart for crash resilience:
  ```python
  {"name": "worker", "command": "python worker.py", "auto_restart": True, "max_restarts": 5}
  ```
- Integrate with workflow-kit to trigger monitors before executing workflows.
- Use deploy-kit to include process monitor as part of development container images.
- Emit status events through event-kit to power centralized dashboards.

## Interoperability
- Use config-kit to store monitor definitions and secrets (e.g., health check tokens).
- Observability-kit loggers and metrics capture process state changes.
- Works with resource-management-kit to track CPU/memory usage per process.

## Operations & Observability
- Expose `/health` endpoints from monitored services and register them with `HealthMonitor`.
- Configure WebSocket stream to push live updates to stream-kit clients.
- Persist logs/metrics to storage-kit for historical analysis.

## Testing & QA
- Use temporary scripts in tests to simulate processes; ensure auto-restart policies behave as expected.
- Mock health checks to simulate failures and verify alerting logic.
- Validate YAML configuration against schema helpers to prevent runtime errors.

## Troubleshooting
- **Processes not starting:** check `cwd` and ensure commands are valid in the runtime environment.
- **Health checks flapping:** increase intervals or timeouts; ensure endpoints are idempotent.
- **TUI not rendering:** install Textual extras and run in a compatible terminal.

## Primary API Surface
- `MonitorFactory.create(name, processes, health_checks=None, infrastructure=None)`
- `MonitorFactory.from_config(path)`
- `BaseMonitor.run_with_tui()` / `run_headless()` / `run_with_api(port)`
- `ProcessManager.start_process(...)` / `stop_process(name)` / `restart_process(name)`
- `HealthMonitor.add_http_check(url, interval, timeout)` / `add_port_check(port, interval)`

## Additional Resources
- Examples: `process-monitor-sdk/examples/`
- Tests: `process-monitor-sdk/tests/`
- Related concepts: [Operations](../guides/operations.md)

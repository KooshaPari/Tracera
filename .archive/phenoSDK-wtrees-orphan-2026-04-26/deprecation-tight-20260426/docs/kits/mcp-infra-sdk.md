# MCP Infra SDK

## At a Glance
- **Purpose:** Shared infrastructure components for MCP servers—launchers, TUIs, logging, and configuration.
- **Best For:** Operationalizing MCP agents with consistent runtimes, monitoring, and process management.
- **Key Building Blocks:** `BaseLauncher`, `BaseProductionTUI`, enhanced log viewer, configuration utilities.

## Core Capabilities
- Production-ready Textual TUIs with process tables, log viewers, and health panels.
- Launchers that allocate ports, manage tunnels, and start MCP servers.
- Process management and health checking utilities with retry/backoff.
- Configuration helpers for environment loading and validation.
- Logging enhancements: filtering, tailing, large buffer retention.

## Getting Started

### Installation
```
pip install mcp-infra-sdk
```

### Minimal Example
```python
from mcp_infra.startup import BaseLauncher

class Launcher(BaseLauncher):
    async def start_server(self, port: int):
        return await self.process_manager.start(["python", "server.py", "--port", str(port)])

launcher = Launcher(config={"port": 8001})
await launcher.start()
```

## How It Works
- `startup.BaseLauncher` orchestrates process startup, port allocation, and tunneling. Override `start_server` and optional hooks (`on_ready`, `on_shutdown`).
- TUIs in `tui` module extend `BaseProductionTUI`; supply process definitions and health checks for live monitoring.
- Logging utilities manage large buffers, filtering, and integration with observability pipelines.
- Config module provides base configs and env loaders to align with config-kit data models.

## Usage Recipes
- Build a custom operations console by subclassing `BaseProductionTUI` and integrating stream-kit updates.
- Use `ProcessManager` to start background services (MCP server, proxy, telemetry exporter) in development environments.
- Combine `HealthChecker` with workflow-kit to wait for readiness before running workflows.
- Load config via config-kit and pass into launchers for consistent environment setup.

## Interoperability
- Observability-kit loggers feed into enhanced log viewer for structured display.
- Process-monitor-sdk complements the TUI when you need both CLI and API access.
- Deploy-kit packages launchers/TUIs as part of deployment artifacts.
- Resource-management-kit can enforce budgets for MCP operations orchestrated by the launcher.

## Operations & Observability
- Configure log retention, log filtering, and color themes in the TUI to surface critical info.
- Use integrated health checks to retry startup until services respond.
- Expose monitoring data via FastAPI endpoints for remote dashboards.

## Testing & QA
- Mock process manager to simulate startup without spawning real processes.
- Unit test TUIs by driving them with Textual’s test harness.
- Validate configuration schemas with sample `.env` files and config-kit tests.

## Troubleshooting
- **Launcher fails to allocate port:** ensure port range is provided and not in use.
- **TUI blank:** check terminal compatibility and confirm `run()` is invoked.
- **Health check timeout:** verify endpoints exist and adjust retry intervals/timeouts.

## Primary API Surface
- `BaseLauncher(config)` / `start()` / `stop()` / override hooks
- `ProcessManager.start(command, cwd=None, env=None)`
- `HealthChecker.wait_for(url, timeout)`
- `BaseProductionTUI(service_name, config)` / `run()` / override `get_processes`, `get_health_checks`
- Logging helpers: `logging.EnhancedLogViewer`, `logging.LogFilter`

## Additional Resources
- Examples: `mcp-infra-sdk/examples/`
- Tests: `mcp-infra-sdk/tests/`
- Related guides: [Operations](../guides/operations.md)

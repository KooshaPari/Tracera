# MCP-QA Kit

## At a Glance
- **Purpose:** Shared quality assurance framework for Model Context Protocol (MCP) servers.
- **Best For:** Running automated integration tests, OAuth workflows, and interactive dashboards across MCP implementations.
- **Key Building Blocks:** `TestRunner`, credential brokers, adapters, reporters, TUI dashboard, health checks.

## Core Capabilities
- Unified OAuth automation with credential caching and Playwright flows.
- Client adapters for interacting with MCP servers via HTTP/WebSocket.
- Test registry and runner with reporter plugins (console, JSON, Markdown).
- TUI dashboard for live progress, OAuth status, and metrics.
- Health checks to validate server readiness and tool availability before tests run.
- Utilities for mocking, fixtures, collaborating sessions, and performance analysis.

## Getting Started

### Installation
```
pip install mcp-QA
```

### Minimal Example
```python
from pheno.mcp.qa.core import TestRunner
from pheno.mcp.qa.adapters import FastHTTPClient
from pheno.mcp.qa.reporters import ConsoleReporter

adapter = HttpClientAdapter(base_url="https://mcp.example.com/api/mcp")
runner = TestRunner(client_adapter=adapter, reporters=[ConsoleReporter()])
await runner.run_all()
```

## How It Works
- `core.test_runner.TestRunner` loads registered tests from `test_registry` and executes them via the selected adapter.
- OAuth module provides `UnifiedCredentialBroker` to fetch tokens and authenticated clients.
- Reporters emit results to console, JSON, Markdown, or custom sinks.
- TUI components (Textual-based) render live progress and integrate with stream-kit for remote viewing.
- Health module performs pre-flight checks (server reachability, tool availability, OAuth validity).

## Usage Recipes
- Add tests by registering functions with `@test_registry.register("category")`.
- Run selective suites: `await runner.run(category="auth")`.
- Combine with workflow-kit to execute QA flows after deployments.
- Export JSON reports and feed them into build-analyzer-kit for aggregate insights.

## Interoperability
- Works with deploy-kit to run smoke tests post-release.
- Observability-kit captures QA run metrics and logs.
- Stream-kit can broadcast test updates to dashboards or chat ops.
- Resource-management-kit ensures tests respect token budgets.

## Operations & Observability
- Run QA dashboards via TUI for staging/prod monitoring.
- Configure reporters to push summaries to Slack or incident systems.
- Health checks run before tests to reduce flakiness.

## Testing & QA
- Self-tests exist in `mcp-QA/tests`; run `pytest` to ensure framework integrity.
- Mock adapters allow unit testing without real MCP servers.
- Fixtures provide sample payloads and deterministic data for integration tests.

## Troubleshooting
- **OAuth failures:** refresh credentials by clearing cached tokens or re-running Playwright automation.
- **Missing tests:** ensure modules import the registry or use entrypoints to auto-discover.
- **Flaky network tests:** adjust retries/backoff, or run against stable staging environments.

## Primary API Surface
- `TestRunner(client_adapter, reporters)` / `run_all()` / `run(category=None)`
- `UnifiedCredentialBroker(base_url)` / `get_authenticated_client()`
- Adapters: `HttpClientAdapter`, `WebSocketAdapter`, `CombinedAdapter`
- Reporters: `ConsoleReporter`, `JSONReporter`, `MarkdownReporter`
- TUI: `tui.dashboard.QADashboard`
- Health checks: `health.checks.run_health_checks()`

## Additional Resources
- Examples: `mcp-QA/examples/`
- Tests: `mcp-QA/tests/`
- Related guides: [Testing & Quality](../concepts/testing-quality.md), [Operations](../guides/operations.md)

# Filewatch Kit

## At a Glance
- **Purpose:** Observe filesystem changes and dispatch async handlers with pattern filtering.
- **Best For:** Developer tooling, live reload pipelines, build automation.
- **Key Building Blocks:** `FileWatcher`, event filters, watcher backends (watchdog, polling), handler decorators.

## Core Capabilities
- Recursive directory watching with glob patterns and ignore lists.
- Event filtering by type (created, modified, deleted, moved).
- Async event handlers with concurrency controls.
- Custom watcher backends (polling fallback, watchdog integration).
- Debounce/throttle utilities to avoid event storms.

## Getting Started

### Installation
```
pip install filewatch-kit
# Optional extras for watchdog support
pip install "filewatch-kit[watchdog]"
```

### Minimal Example
```python
from filewatch_kit import FileWatcher, EventType

watcher = FileWatcher(path="./src", patterns=["*.py"], recursive=True)

@watcher.on(EventType.MODIFIED)
async def on_modified(event):
    print("Modified:", event.path)

await watcher.start()
```

## How It Works
- `FileWatcher` coordinates watchers and handlers. Backends live in `filewatch_kit.watchers`.
- Filters (`filewatch_kit.filters`) refine which events are passed to handlers.
- Handlers register via decorators (`@watcher.on`, `@watcher.on_any`).
- Events expose metadata: `path`, `event_type`, `timestamp`, optional payload.

## Usage Recipes
- Trigger build-analyzer-kit when source files change to re-run diagnostics.
- Reload configuration by invoking config-kit loaders when config files update.
- Combine with stream-kit to push change notifications to connected clients.
- Wire into workflow-kit to start workflows when new files appear in storage-mounted directories.

## Interoperability
- Send file events to event-kit for durable storage or fan-out.
- Use adapter-kit to inject watchers into CLI commands or background services.
- Log file events with observability-kit to monitor development environments.

## Operations & Observability
- Limit concurrency or apply debounce windows to manage high-frequency changes.
- Emit metrics for event counts and handler latency.
- Configure watchers to auto-restart on backend failures.

## Testing & QA
- Use temporary directories via `tmp_path` fixture in pytest.
- Simulate events with the `filewatch_kit.testing.emit_event` helper.
- Mock watchers to ensure handlers are invoked correctly without touching the filesystem.

## Troubleshooting
- **No events on macOS/Linux:** install `watchdog` extras for native FS notifications.
- **Duplicate events:** adjust debounce settings or ignore patterns.
- **Permission errors:** ensure the process can read the watched directories.

## Primary API Surface
- `FileWatcher(path, patterns=None, ignore=None, recursive=True)`
- Decorators: `@watcher.on(EventType.MODIFIED)`, `@watcher.on_any`
- Lifecycle: `await watcher.start()`, `await watcher.stop()`
- Backends: `watchers.WatchdogBackend`, `watchers.PollingBackend`
- Filters: `filters.PatternFilter`, `filters.EventTypeFilter`

## Additional Resources
- Examples: `filewatch-kit/examples/`
- Tests: `filewatch-kit/tests/`
- Related concepts: [Patterns](../concepts/patterns.md)

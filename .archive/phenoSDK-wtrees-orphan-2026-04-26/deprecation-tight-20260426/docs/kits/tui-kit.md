# TUI Kit

## At a Glance
- **Purpose:** Build rich Textual-based terminal interfaces with reusable widgets, layouts, and theming.
- **Best For:** Developer tooling, monitoring dashboards, configuration UIs, and CLI augmentation.
- **Key Building Blocks:** Widgets (log viewer, progress, metrics table), layouts (split, tabbed, grid), theming system, widget factories, stream capture.

## Core Capabilities
- Comprehensive widget library: `LogViewer`, `ProgressWidget`, `MetricsTable`, `StatusDashboard`, `TreeView`, `FormWidget`.
- Layout primitives for flexible composition (split, tabs, grid).
- Theme manager with dark/light palettes and color utilities.
- Stream capture for stdout/stderr/logs with syntax highlighting.
- Widget factory system for dynamic instantiation/configuration.
- Protocol utilities for integrating with stream-kit/observability sources.

## Getting Started

### Installation
```
pip install tui-kit
# Optional extras for monitoring widgets
pip install "tui-kit[monitoring]"
```

### Minimal Example
```python
from textual.app import App, ComposeResult
from tui_kit.widgets import LogViewer, LogLevel

class Demo(App):
    def compose(self) -> ComposeResult:
        yield LogViewer(max_entries=500)

    def on_mount(self) -> None:
        viewer = self.query_one(LogViewer)
        viewer.add_log("TUI ready", LogLevel.INFO)

Demo().run()
```

## How It Works
- Widgets live in `tui_kit.widgets` and extend Textual widgets with Pheno-specific features.
- Layouts (`tui_kit.layouts`) coordinate widget positioning and resizing.
- Themes and color utilities under `tui_kit.themes` and `tui_kit.utils.colors` manage presentation.
- Factories (`tui_kit.factories.widget_factory`) instantiate widget presets from configuration.
- Stream capture integrates with logging/observability to render live output inside TUIs.

## Usage Recipes
- Build a monitoring dashboard combining `StatusDashboard` and `MetricsTable` with data from observability-kit.
- Display workflow progress by streaming events from stream-kit into `ProgressWidget`.
- Provide interactive configuration editors using `FormWidget` and config-kit models.
- Use `TabbedLayout` to switch between log streams, metrics, and status panels.

## Interoperability
- Observability-kit loggers can stream directly into the log viewer via capture hooks.
- Stream-kit channels feed real-time updates into widgets using provided protocol adapters.
- Process-monitor-sdk can embed TUI dashboards for process control.
- Deploy-kit packaging includes sample TUI entrypoints for operations consoles.

## Operations & Observability
- Keep TUIs responsive by offloading heavy work with asyncio tasks.
- Emit metrics about widget updates for performance monitoring.
- Provide keyboard shortcuts (via `tui_kit.utils.keyboard`) and document them in your CLI help screens.

## Testing & QA
- Component tests use Textual’s pilot API; see `tui-kit/tests/` for patterns.
- Snapshot widget render output to detect regressions.
- Validate color themes across terminals by running automated theme checks.

## Troubleshooting
- **Blank screen:** ensure `App.run()` is invoked and your terminal supports Unicode.
- **Laggy updates:** batch UI updates, throttle progress events, or coalesce logs.
- **Theme issues:** verify theme registration via `ThemeManager.register()` before launching the app.

## Primary API Surface
- Widgets: `LogViewer`, `ProgressWidget`, `MetricsTable`, `StatusDashboard`, `TreeView`, `FormWidget`
- Layouts: `SplitLayout`, `TabbedLayout`, `GridLayout`
- Themes: `ThemeManager`, `load_theme`, color utilities (`darken`, `lighten`)
- Factories: `WidgetFactory.from_config(config)`
- Stream capture: `core.stream_capture.StreamCapture`

## Additional Resources
- Examples: `tui-kit/examples/`
- Tests: `tui-kit/tests/`
- Related guides: [Operations](../guides/operations.md), [Patterns](../concepts/patterns.md)

"""Test-related widgets for the TUI dashboard.

This module contains widgets for displaying test information:
- Test summary statistics
- Test progress tracking
- Performance metrics
- Auth/MFA events
"""

import logging

from rich.panel import Panel
from textual.reactive import reactive
from textual.widgets import Static

logger = logging.getLogger("atoms.tui")


class TestSummaryWidget(Static):
    """
    Display test summary statistics with real-time updates.
    """

    total = reactive(0)
    passed = reactive(0)
    failed = reactive(0)
    skipped = reactive(0)
    cached = reactive(0)
    duration = reactive(0.0)
    running = reactive(False)

    def render(self) -> Panel:
        """
        Render summary statistics in a rich panel.
        """
        pass_rate = (
            (self.passed / (self.total - self.skipped)) * 100
            if (self.total - self.skipped) > 0
            else 0
        )

        status_icon = (
            "🔄"
            if self.running
            else ("✅" if pass_rate >= 90 else "⚠️" if pass_rate >= 70 else "❌")
        )

        content = f"""[bold]{status_icon} Test Summary[/bold]

Total: [cyan]{self.total}[/cyan] | Passed: [green]{self.passed}[/green] | Failed: [red]{self.failed}[/red] | Skipped: [yellow]{self.skipped}[/yellow] | Cached: [blue]{self.cached}[/blue]

Pass Rate: [{'green' if pass_rate >= 90 else 'yellow' if pass_rate >= 70 else 'red'}]{pass_rate:.1f}%[/]
Duration: [cyan]{self.duration:.2f}s[/cyan]
Status: [{'yellow' if self.running else 'green'}]{'Running...' if self.running else 'Idle'}[/]"""

        return Panel(
            content,
            border_style="green" if pass_rate >= 90 else "yellow" if pass_rate >= 70 else "red",
        )


class TestProgressWidget(Static):
    """
    Display real-time test progress with progress bar.
    """

    current = reactive(0)
    total = reactive(0)
    current_test = reactive("")
    current_tool = reactive("")

    def render(self) -> Panel:
        """
        Render progress bar and current test info.
        """
        if self.total == 0:
            percent = 0
        else:
            percent = (self.current / self.total) * 100

        # ASCII progress bar
        bar_width = 40
        filled = int(bar_width * percent / 100)
        bar = "█" * filled + "░" * (bar_width - filled)

        content = f"""[bold]📈 Progress[/bold]

{bar} {percent:.1f}% ({self.current}/{self.total})

Currently running: [cyan]{self.current_test}[/cyan]
Tool: [yellow]{self.current_tool}[/yellow]"""

        return Panel(content, border_style="cyan")


class MetricsWidget(Static):
    """
    Display performance metrics and statistics (Phase 4).
    """

    avg_duration = reactive(0.0)
    min_duration = reactive(0.0)
    max_duration = reactive(0.0)
    total_duration = reactive(0.0)
    tests_per_second = reactive(0.0)
    cache_hit_rate = reactive(0.0)

    def render(self) -> Panel:
        """
        Render performance metrics.
        """
        content = f"""[bold]📊 Performance Metrics[/bold]

Average Duration: [cyan]{self.avg_duration:.2f}ms[/cyan]
Min: [green]{self.min_duration:.2f}ms[/green] | Max: [red]{self.max_duration:.2f}ms[/red]
Total Time: [yellow]{self.total_duration:.2f}s[/yellow]
Throughput: [blue]{self.tests_per_second:.1f} tests/sec[/blue]
Cache Hit Rate: [magenta]{self.cache_hit_rate:.1f}%[/magenta]"""

        return Panel(content, border_style="blue")


class AuthMFAEventsWidget(Static):
    """
    Tail recent OAuth/MFA structured events.
    """

    max_events = reactive(50)
    last_count = reactive(0)

    def render(self) -> Panel:
        try:
            from pheno.mcp.qa.logging.structured_events import get_recent_events

            evs = get_recent_events(self.max_events)
        except Exception:
            evs = []
        if not evs:
            content = "[dim]No recent auth/MFA events[/dim]"
        else:
            lines = ["[bold]Recent Auth/MFA Events[/bold]\n"]
            for ev in evs[-self.max_events :]:
                typ = ev.get("type", "")
                tid = ev.get("test_id", "")
                parts = []
                if typ:
                    parts.append(f"[cyan]{typ}[/cyan]")
                if tid:
                    parts.append(f"[yellow]{tid}[/yellow]")
                msg = ev.get("message", "")
                if msg:
                    parts.append(msg)
                lines.append(" ".join(parts))
            content = "\n".join(lines)

        return Panel(content, border_style="magenta", title="Auth Events")


class AuthProfileWidget(Static):
    """
    Display current auth profile information.
    """

    profile_name = reactive("")
    profile_type = reactive("")
    last_updated = reactive("")

    def render(self) -> Panel:
        """
        Render auth profile information.
        """
        content = f"""[bold]🔐 Auth Profile[/bold]

Name: [cyan]{self.profile_name or 'Not set'}[/cyan]
Type: [yellow]{self.profile_type or 'Unknown'}[/yellow]
Updated: [dim]{self.last_updated or 'Never'}[/dim]

[dim]Press 'P' to switch profile[/dim]"""

        return Panel(content, border_style="cyan", title="Profile")


class LiveMonitorWidget(Static):
    """
    Live monitoring widget for real-time updates (Phase 4).
    """

    monitor_active = reactive(False)
    last_update = reactive("")
    update_count = reactive(0)

    def render(self) -> Panel:
        """
        Render live monitor status.
        """
        status_icon = "🔄" if self.monitor_active else "⏸️"
        status_text = "Active" if self.monitor_active else "Paused"

        content = f"""[bold]{status_icon} Live Monitor[/bold]

Status: [{'green' if self.monitor_active else 'yellow'}]{status_text}[/]
Last Update: [cyan]{self.last_update or 'Never'}[/cyan]
Updates: [blue]{self.update_count}[/blue]

[dim]Press 'M' to toggle monitor[/dim]"""

        return Panel(
            content, border_style="green" if self.monitor_active else "yellow", title="Live Monitor",
        )


class FlowRunnerWidget(Static):
    """
    Widget for running and monitoring flows (Phase 4).
    """

    flow_name = reactive("")
    flow_status = reactive("idle")
    flow_progress = reactive(0.0)
    flow_duration = reactive(0.0)

    def render(self) -> Panel:
        """
        Render flow runner status.
        """
        status_colors = {
            "idle": "yellow",
            "running": "blue",
            "completed": "green",
            "failed": "red",
            "paused": "yellow",
        }

        status_color = status_colors.get(self.flow_status, "white")
        status_icon = {
            "idle": "⏸️",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "paused": "⏸️",
        }.get(self.flow_status, "❓")

        content = f"""[bold]{status_icon} Flow Runner[/bold]

Flow: [cyan]{self.flow_name or 'None'}[/cyan]
Status: [{status_color}]{self.flow_status.title()}[/{status_color}]
Progress: [blue]{self.flow_progress:.1f}%[/blue]
Duration: [yellow]{self.flow_duration:.2f}s[/yellow]

[dim]Press 'F' to start flow[/dim]"""

        return Panel(content, border_style=status_color, title="Flow Runner")


class HealthSummaryWidget(Static):
    """
    Display overall system health summary.
    """

    overall_health = reactive("unknown")
    component_count = reactive(0)
    healthy_components = reactive(0)
    last_check = reactive("")

    def render(self) -> Panel:
        """
        Render health summary.
        """
        health_colors = {
            "healthy": "green",
            "degraded": "yellow",
            "unhealthy": "red",
            "unknown": "white",
        }

        health_color = health_colors.get(self.overall_health, "white")
        health_icon = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌", "unknown": "❓"}.get(
            self.overall_health, "❓",
        )

        health_percentage = (
            (self.healthy_components / self.component_count * 100)
            if self.component_count > 0
            else 0
        )

        content = f"""[bold]{health_icon} System Health[/bold]

Overall: [{health_color}]{self.overall_health.title()}[/{health_color}]
Components: [cyan]{self.healthy_components}/{self.component_count}[/cyan] ({health_percentage:.1f}%)
Last Check: [dim]{self.last_check or 'Never'}[/dim]

[dim]Press 'H' for detailed health check[/dim]"""

        return Panel(content, border_style=health_color, title="Health")


class OIDCHealthWidget(Static):
    """
    Display OIDC health status.
    """

    oidc_healthy = reactive(False)
    oidc_endpoint = reactive("")
    last_check = reactive("")
    error_message = reactive("")

    def render(self) -> Panel:
        """
        Render OIDC health status.
        """
        status_color = "green" if self.oidc_healthy else "red"
        status_icon = "✅" if self.oidc_healthy else "❌"

        content = f"""[bold]{status_icon} OIDC Health[/bold]

Status: [{status_color}]{'Healthy' if self.oidc_healthy else 'Unhealthy'}[/{status_color}]
Endpoint: [cyan]{self.oidc_endpoint or 'Not configured'}[/cyan]
Error: [red]{self.error_message or 'None'}[/red]
Last Check: [dim]{self.last_check or 'Never'}[/dim]"""

        return Panel(content, border_style=status_color, title="OIDC")


class EnvHealthWidget(Static):
    """
    Display environment health status.
    """

    env_vars_loaded = reactive(0)
    env_vars_total = reactive(0)
    missing_vars = reactive([])
    last_check = reactive("")

    def render(self) -> Panel:
        """
        Render environment health status.
        """
        if self.env_vars_total == 0:
            status_color = "yellow"
            status_icon = "⚠️"
            status_text = "No vars"
        elif self.env_vars_loaded == self.env_vars_total:
            status_color = "green"
            status_icon = "✅"
            status_text = "Complete"
        else:
            status_color = "yellow"
            status_icon = "⚠️"
            status_text = "Partial"

        content = f"""[bold]{status_icon} Environment[/bold]

Status: [{status_color}]{status_text}[/{status_color}]
Loaded: [cyan]{self.env_vars_loaded}/{self.env_vars_total}[/cyan]
Missing: [red]{len(self.missing_vars)}[/red]
Last Check: [dim]{self.last_check or 'Never'}[/dim]"""

        return Panel(content, border_style=status_color, title="Environment")


class TeamVisibilityWidget(Static):
    """
    Show connected team members and their activity (Phase 5).
    """

    connected_users = reactive(0)
    active_users = reactive(0)
    last_activity = reactive("")
    team_name = reactive("")

    def render(self) -> Panel:
        """
        Render team visibility information.
        """
        content = f"""[bold]👥 Team Visibility[/bold]

Team: [cyan]{self.team_name or 'Not set'}[/cyan]
Connected: [green]{self.connected_users}[/green]
Active: [blue]{self.active_users}[/blue]
Last Activity: [dim]{self.last_activity or 'Never'}[/dim]

[dim]Press 'U' to show users[/dim]"""

        return Panel(content, border_style="green", title="Team")

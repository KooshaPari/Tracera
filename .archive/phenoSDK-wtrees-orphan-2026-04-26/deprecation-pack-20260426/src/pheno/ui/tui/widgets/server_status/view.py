"""
Rendering helpers for the server status widget.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from rich.panel import Panel
from rich.table import Table
from rich.text import Text


@dataclass
class StatusViewModel:
    connected: bool
    endpoint: str
    last_ping: float
    latency_ms: float
    server_version: str
    requests_per_sec: float
    error_rate: float
    latency_history: list[float]
    health_history: list[dict]
    error_message: str


def _generate_sparkline(values: list[float], width: int = 20) -> str:
    if not values:
        return ""

    block_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
    min_val = min(values)
    max_val = max(values)

    if max_val == min_val:
        return block_chars[len(block_chars) // 2] * min(len(values), width)

    sparkline = []
    for value in values[-width:]:
        normalized = (value - min_val) / (max_val - min_val)
        index = int(normalized * (len(block_chars) - 1))
        sparkline.append(block_chars[index])

    return "".join(sparkline)


def build_status_panel(model: StatusViewModel) -> Panel:
    status_color = "green" if model.connected else "red"
    status_icon = "●" if model.connected else "○"
    status_text = "Connected" if model.connected else "Disconnected"

    if model.last_ping > 0:
        time_since = time.time() - model.last_ping
        if time_since < 60:
            ping_text = f"{int(time_since)}s ago"
        elif time_since < 3600:
            ping_text = f"{int(time_since / 60)}m ago"
        else:
            ping_text = f"{int(time_since / 3600)}h ago"
    else:
        ping_text = "Never"

    display_endpoint = model.endpoint
    if len(display_endpoint) > 40:
        display_endpoint = "..." + display_endpoint[-37:]

    content = Text()
    content.append(f"{status_icon} MCP Server\n\n", style=f"bold {status_color}")

    table = Table.grid(padding=(0, 2))
    table.add_column(style="cyan", justify="right")
    table.add_column()
    table.add_row("Status:", Text(status_text, style=f"bold {status_color}"))
    table.add_row("Endpoint:", Text(display_endpoint, style="blue"))

    if model.latency_ms > 0:
        if model.latency_ms < 100:
            latency_color = "green"
        elif model.latency_ms < 500:
            latency_color = "yellow"
        else:
            latency_color = "red"
        table.add_row("Latency:", Text(f"{model.latency_ms:.1f}ms", style=latency_color))
    else:
        table.add_row("Latency:", Text("—", style="dim"))

    table.add_row("Last Check:", Text(ping_text, style="dim"))
    table.add_row("Version:", Text(model.server_version, style="magenta"))

    content.append(table)
    content.append("\n")

    metrics_table = Table.grid(padding=(0, 2))
    metrics_table.add_column(style="cyan", justify="right")
    metrics_table.add_column()
    metrics_table.add_row("Requests/sec:", Text(f"{model.requests_per_sec:.2f}", style="yellow"))

    if model.error_rate < 5:
        error_color = "green"
    elif model.error_rate < 20:
        error_color = "yellow"
    else:
        error_color = "red"
    metrics_table.add_row("Error Rate:", Text(f"{model.error_rate:.1f}%", style=error_color))

    if len(model.latency_history) > 1:
        sparkline = _generate_sparkline(model.latency_history)
        metrics_table.add_row("Latency:", Text(sparkline, style="cyan"))

    content.append(metrics_table)

    if model.health_history:
        recent_checks = model.health_history[-10:]
        success_count = sum(1 for check in recent_checks if check.get("success", False))
        health_percent = (success_count / len(recent_checks)) * 100
        if health_percent >= 90:
            health_color = "green"
        elif health_percent >= 70:
            health_color = "yellow"
        else:
            health_color = "red"
        content.append("\n")
        content.append(
            f"Health: {success_count}/{len(recent_checks)} checks OK ({health_percent:.0f}%)",
            style=health_color,
        )

    if model.error_message:
        content.append("\n\n")
        content.append("Error: ", style="bold red")
        content.append(model.error_message, style="red")

    content.append("\n\n")
    content.append("Press Ctrl+H to refresh", style="dim italic")

    return Panel(
        content,
        border_style=status_color,
        title="[bold]Server Status[/bold]",
        subtitle=f"[dim]{len(model.health_history)} checks[/dim]",
    )


__all__ = ["StatusViewModel", "build_status_panel"]

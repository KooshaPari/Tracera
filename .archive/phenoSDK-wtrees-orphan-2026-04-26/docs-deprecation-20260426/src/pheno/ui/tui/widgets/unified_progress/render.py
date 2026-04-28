"""
Rendering utilities for the unified progress widget.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .environment import Panel, Table

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .models import CategoryStats, Task


def build_category_panel(categories: dict[str, CategoryStats]) -> Panel:
    table = Table(show_header=True, box=None)
    table.add_column("Category", style="cyan")
    table.add_column("Progress", justify="center")
    table.add_column("Pass Rate", justify="right")
    table.add_column("Cache Hit", justify="right")

    for name, stats in sorted(categories.items()):
        progress = f"{stats.completed}/{stats.total}"
        pass_rate = f"{stats.pass_rate:.1f}%"
        cache_rate = f"{stats.cache_hit_rate:.1f}%"
        table.add_row(name, progress, pass_rate, cache_rate)

    return Panel(table, title="Categories", border_style="magenta")


def build_current_task_panel(task: Task, show_sparklines: bool, show_metrics: bool) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold")
    table.add_column()

    table.add_row("Task:", task.description)
    table.add_row("Status:", task.status.value.title())
    table.add_row("Progress:", f"{task.current}/{task.total} ({task.percent:.1f}%)")
    table.add_row("ETA:", task.eta_formatted)
    table.add_row("Elapsed:", task.elapsed_formatted)
    table.add_row("Speed:", task.throughput)

    if task.tool:
        table.add_row("Tool:", task.tool)
    if task.category:
        table.add_row("Category:", task.category)

    if show_sparklines and len(task.history) >= 2:
        table.add_row("Trend:", task.get_sparkline(width=20))

    if show_metrics:
        if task.metrics.cpu_percent > 0:
            table.add_row("CPU:", f"{task.metrics.cpu_percent:.1f}%")
        if task.metrics.memory_mb > 0:
            table.add_row("Memory:", f"{task.metrics.memory_mb:.1f} MB")
        if task.metrics.network_kb > 0:
            table.add_row("Network:", f"{task.metrics.network_kb:.1f} KB/s")

    return Panel(table, title="Current Task", border_style="blue")


def build_statistics_panel(tasks: Iterable[Task]) -> Panel:
    tasks = list(tasks)
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status.name in {"COMPLETED", "CACHED"})
    failed = sum(1 for t in tasks if t.status.name == "FAILED")
    cached = sum(1 for t in tasks if t.cache_hit)

    completed_tasks = [t for t in tasks if t.status.name in {"COMPLETED", "CACHED", "FAILED"}]
    avg_duration = (
        sum(t.duration_ms for t in completed_tasks) / len(completed_tasks) if completed_tasks else 0
    )

    pass_rate = (completed / total * 100) if total > 0 else 0
    cache_hit_rate = (cached / total * 100) if total > 0 else 0

    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold")
    table.add_column(justify="right")
    table.add_row("✅ Completed", f"[green]{completed}[/green]")
    table.add_row("❌ Failed", f"[red]{failed}[/red]")
    table.add_row("💾 Cached", f"[blue]{cached}[/blue]")
    table.add_row("📊 Pass Rate", f"[bold]{pass_rate:.1f}%[/bold]")
    table.add_row("⚡ Cache Hit", f"{cache_hit_rate:.1f}%")
    table.add_row("⏱️  Avg Duration", f"{avg_duration:.2f}ms")

    return Panel(table, title="Statistics", border_style="green")


__all__ = ["build_category_panel", "build_current_task_panel", "build_statistics_panel"]

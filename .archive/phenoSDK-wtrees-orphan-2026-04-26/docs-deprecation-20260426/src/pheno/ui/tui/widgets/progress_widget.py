"""
ProgressWidget - Multi-task progress tracking with ETA calculation.

Provides progress bars and statistics for concurrent tasks.
"""

import time
from dataclasses import dataclass, field

try:
    from rich.panel import Panel
    from rich.progress import Progress, TaskID
    from rich.table import Table
    from textual.app import ComposeResult
    from textual.containers import Container, Vertical
    from textual.reactive import reactive
    from textual.widgets import ProgressBar, Static

    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False
    Static = object
    ProgressBar = object
    def reactive(x):
        return x
    Container = object
    Vertical = object
    ComposeResult = object
    Panel = object
    Table = object
    Progress = object
    TaskID = object


@dataclass
class TaskProgress:
    """
    Individual task progress tracking.
    """

    task_id: str
    description: str
    total: int
    current: int = 0
    start_time: float = field(default_factory=time.time)
    status: str = "pending"
    error: str | None = None

    @property
    def percent(self) -> float:
        """
        Get completion percentage.
        """
        if self.total == 0:
            return 0.0
        return (self.current / self.total) * 100

    @property
    def eta_seconds(self) -> float | None:
        """
        Calculate estimated time to completion.
        """
        if self.current == 0 or self.status == "completed":
            return None

        elapsed = time.time() - self.start_time
        rate = self.current / elapsed

        if rate == 0:
            return None

        remaining = self.total - self.current
        return remaining / rate

    @property
    def eta_formatted(self) -> str:
        """
        Get formatted ETA string.
        """
        eta = self.eta_seconds
        if eta is None:
            return "Calculating..."

        if eta < 60:
            return f"{int(eta)}s"
        if eta < 3600:
            return f"{int(eta / 60)}m {int(eta % 60)}s"
        hours = int(eta / 3600)
        minutes = int((eta % 3600) / 60)
        return f"{hours}h {minutes}m"

    @property
    def duration_formatted(self) -> str:
        """
        Get formatted duration string.
        """
        duration = time.time() - self.start_time

        if duration < 60:
            return f"{duration:.1f}s"
        if duration < 3600:
            return f"{int(duration / 60)}m {int(duration % 60)}s"
        hours = int(duration / 3600)
        minutes = int((duration % 3600) / 60)
        return f"{hours}h {minutes}m"


class ProgressWidget(Static):
    """Multi-task progress widget with ETA calculation.

    Features:
    - Track multiple concurrent tasks
    - Calculate ETA for each task
    - Show overall progress
    - Display task statistics
    - Visual progress bars
    """

    total_tasks = reactive(0)
    completed_tasks = reactive(0)
    failed_tasks = reactive(0)

    def __init__(
        self,
        show_individual: bool = True,
        show_summary: bool = True,
        compact: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.show_individual = show_individual
        self.show_summary = show_summary
        self.compact = compact
        self._tasks: dict[str, TaskProgress] = {}

    def add_task(self, task_id: str, description: str, total: int) -> TaskProgress:
        """
        Add a new task to track.
        """
        task = TaskProgress(task_id=task_id, description=description, total=total, status="running")

        self._tasks[task_id] = task
        self.total_tasks = len(self._tasks)
        self.refresh()

        return task

    def update_task(
        self,
        task_id: str,
        current: int | None = None,
        advance: int = 0,
        status: str | None = None,
        error: str | None = None,
    ) -> None:
        """
        Update task progress.
        """
        if task_id not in self._tasks:
            return

        task = self._tasks[task_id]

        if current is not None:
            task.current = current

        if advance:
            task.current += advance

        if status:
            task.status = status

            if status == "completed":
                self.completed_tasks += 1
                task.current = task.total
            elif status == "failed":
                self.failed_tasks += 1

        if error:
            task.error = error

        self.refresh()

    def complete_task(self, task_id: str, error: str | None = None) -> None:
        """
        Mark task as completed.
        """
        if error:
            self.update_task(task_id, status="failed", error=error)
        else:
            self.update_task(task_id, status="completed")

    def render(self) -> Panel:
        """
        Render progress display.
        """
        if self.compact:
            return self._render_compact()
        return self._render_detailed()

    def _render_compact(self) -> Panel:
        """
        Render compact progress view.
        """
        if not self._tasks:
            content = "[dim]No tasks in progress[/dim]"
        else:
            lines = []

            for task in self._tasks.values():
                icon = (
                    "✅"
                    if task.status == "completed"
                    else "❌" if task.status == "failed" else "🔄"
                )
                bar_width = 20
                filled = int(bar_width * task.percent / 100)
                bar = "█" * filled + "░" * (bar_width - filled)

                line = f"{icon} {task.description[:30]:30s} {bar} {task.percent:.0f}%"

                if task.status == "running":
                    line += f" ETA: {task.eta_formatted}"

                lines.append(line)

            content = "\n".join(lines)

        return Panel(content, title="Progress", border_style="cyan")

    def _render_detailed(self) -> Panel:
        """
        Render detailed progress view.
        """
        if not self._tasks:
            content = "[dim]No tasks in progress[/dim]"
            return Panel(content, title="Progress", border_style="cyan")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Status", width=6)
        table.add_column("Task", width=30)
        table.add_column("Progress", width=25)
        table.add_column("Percent", width=8)
        table.add_column("ETA", width=12)
        table.add_column("Duration", width=12)

        for task in self._tasks.values():
            # Status icon
            if task.status == "completed":
                status = "[green]✅[/green]"
            elif task.status == "failed":
                status = "[red]❌[/red]"
            elif task.status == "running":
                status = "[yellow]🔄[/yellow]"
            else:
                status = "[dim]⏸️[/dim]"

            # Progress bar
            bar_width = 20
            filled = int(bar_width * task.percent / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            progress_str = f"{bar} {task.current}/{task.total}"

            # Percent
            percent_str = f"{task.percent:.1f}%"

            # ETA
            if task.status == "running":
                eta_str = task.eta_formatted
            elif task.status == "completed":
                eta_str = "[green]Done[/green]"
            elif task.status == "failed":
                eta_str = "[red]Failed[/red]"
            else:
                eta_str = "-"

            # Duration
            duration_str = task.duration_formatted

            # Add row
            table.add_row(
                status, task.description[:30], progress_str, percent_str, eta_str, duration_str,
            )

        # Add summary if enabled
        if self.show_summary:
            table.add_row("")  # Separator

            overall_percent = (
                (self.completed_tasks / self.total_tasks * 100) if self.total_tasks > 0 else 0
            )
            summary = f"[bold]Overall: {self.completed_tasks}/{self.total_tasks} completed ({overall_percent:.0f}%)[/bold]"

            if self.failed_tasks > 0:
                summary += f" [red]{self.failed_tasks} failed[/red]"

            table.add_row("", summary, "", "", "", "")

        return Panel(table, title="Task Progress", border_style="cyan")

    def get_task(self, task_id: str) -> TaskProgress | None:
        """
        Get task by ID.
        """
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[TaskProgress]:
        """
        Get all tasks.
        """
        return list(self._tasks.values())

    def get_running_tasks(self) -> list[TaskProgress]:
        """
        Get currently running tasks.
        """
        return [t for t in self._tasks.values() if t.status == "running"]

    def clear_completed(self) -> None:
        """
        Remove completed tasks.
        """
        self._tasks = {
            tid: task
            for tid, task in self._tasks.items()
            if task.status not in ["completed", "failed"]
        }

        # Recalculate counts
        self.total_tasks = len(self._tasks)
        self.completed_tasks = sum(1 for t in self._tasks.values() if t.status == "completed")
        self.failed_tasks = sum(1 for t in self._tasks.values() if t.status == "failed")

        self.refresh()

    def clear_all(self) -> None:
        """
        Clear all tasks.
        """
        self._tasks.clear()
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.refresh()

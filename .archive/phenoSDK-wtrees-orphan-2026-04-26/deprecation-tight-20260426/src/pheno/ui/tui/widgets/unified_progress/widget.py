"""
Unified progress widget implementation.
"""

from __future__ import annotations

import threading
import time
from typing import Self

from .environment import (
    HAS_RICH,
    BarColumn,
    Console,
    Group,
    Live,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from .models import (
    CategoryStats,
    Task,
    TaskMetrics,
    TaskPriority,
    TaskStatus,
)
from .render import (
    build_category_panel,
    build_current_task_panel,
    build_statistics_panel,
)

__all__ = ["Task", "TaskMetrics", "TaskPriority", "TaskStatus", "UnifiedProgressWidget"]


class UnifiedProgressWidget:
    """
    Unified progress widget supporting multiple rendering backends.
    """

    def __init__(
        self,
        total: int | None = None,
        categories: list[str] | None = None,
        show_sparklines: bool = True,
        show_metrics: bool = True,
        show_categories: bool = True,
        compact: bool = False,
        refresh_rate: int = 4,
        console: Console | None = None,
    ):
        if not HAS_RICH:
            raise RuntimeError("Rich library required. Install with: pip install rich")

        self.console = console or Console()
        self.show_sparklines = show_sparklines
        self.show_metrics = show_metrics
        self.show_categories = show_categories and categories is not None
        self.compact = compact
        self.refresh_rate = refresh_rate

        self._lock = threading.RLock()
        self._tasks: dict[str, Task] = {}
        self._task_order: list[str] = []

        self.categories: dict[str, CategoryStats] = {}
        if categories:
            for name in categories:
                self.categories[name] = CategoryStats(name=name)

        self.progress = self._create_progress()
        self._rich_task_ids: dict[str, TaskID] = {}

        self.live: Live | None = None
        self._is_running = False

        if total is not None:
            self.add_task("__main__", "Progress", total=total)

    def _create_progress(self) -> Progress:
        columns = [
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            TaskProgressColumn(),
        ]

        if not self.compact:
            columns.extend(
                [
                    MofNCompleteColumn(),
                    TimeElapsedColumn(),
                    TimeRemainingColumn(),
                ],
            )

        return Progress(*columns, console=self.console, transient=False)

    def add_task(
        self,
        task_id: str,
        description: str,
        total: int,
        parent_id: str | None = None,
        category: str | None = None,
        tool: str | None = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        **fields,
    ) -> Task:
        with self._lock:
            if task_id in self._tasks:
                raise ValueError(f"Task {task_id} already exists")

            task = Task(
                id=task_id,
                description=description,
                total=total,
                parent_id=parent_id,
                category=category,
                tool=tool,
                priority=priority,
                start_time=time.time(),
                status=TaskStatus.PENDING,
                fields=fields,
            )

            self._tasks[task_id] = task
            self._task_order.append(task_id)

            if parent_id and parent_id in self._tasks:
                self._tasks[parent_id].children.append(task_id)

            if category and category in self.categories:
                self.categories[category].total += 1

            if self._is_running:
                rich_task = self.progress.add_task(description, total=total)
                self._rich_task_ids[task_id] = rich_task

            return task

    def update(
        self,
        task_id: str,
        current: int | None = None,
        advance: int = 0,
        status: TaskStatus | None = None,
        description: str | None = None,
        metrics: TaskMetrics | None = None,
        error: str | None = None,
        cache_hit: bool = False,
        **fields,
    ) -> None:
        with self._lock:
            if task_id not in self._tasks:
                return

            task = self._tasks[task_id]

            # Update task properties
            self._update_task_progress(task, current, advance)
            self._update_task_status(task, status)
            self._update_task_metadata(task, description, metrics, error, cache_hit, fields)

            # Update display
            self._refresh_display(task_id, task)

    def _update_task_progress(self, task: Task, current: int | None, advance: int) -> None:
        """
        Update task progress (current value).
        """
        if current is not None:
            task.current = min(current, task.total)
        elif advance:
            task.current = min(task.current + advance, task.total)

    def _update_task_status(self, task: Task, status: TaskStatus | None) -> None:
        """
        Update task status and handle status transitions.
        """
        if not status:
            return

        previous = task.status
        task.status = status

        # Handle status transitions
        if status == TaskStatus.RUNNING and previous == TaskStatus.PENDING:
            task.start_time = time.time()
        elif status in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CACHED}:
            self._handle_task_completion(task)

        # Update category statistics
        self._update_category_stats(task, status)

    def _handle_task_completion(self, task: Task) -> None:
        """
        Handle task completion (set end time and calculate duration).
        """
        task.end_time = time.time()
        if task.start_time:
            task.duration_ms = (task.end_time - task.start_time) * 1000

    def _update_category_stats(self, task: Task, status: TaskStatus) -> None:
        """
        Update category statistics based on task status.
        """
        if not task.category or task.category not in self.categories:
            return

        cat = self.categories[task.category]
        cat.completed += 1

        if status == TaskStatus.COMPLETED:
            cat.passed += 1
        elif status == TaskStatus.FAILED:
            cat.failed += 1
        elif status == TaskStatus.CACHED:
            cat.cached += 1
        elif status == TaskStatus.SKIPPED:
            cat.skipped += 1

    def _update_task_metadata(
        self,
        task: Task,
        description: str | None,
        metrics: TaskMetrics | None,
        error: str | None,
        cache_hit: bool,
        fields: dict,
    ) -> None:
        """
        Update task metadata (description, metrics, error, etc.).
        """
        if description:
            task.description = description

        if metrics:
            task.metrics = metrics

        if error:
            task.error = error

        if cache_hit:
            task.cache_hit = True

        if fields:
            task.fields.update(fields)

        task.add_history_point()

    def _refresh_display(self, task_id: str, task: Task) -> None:
        """
        Refresh the display with updated task information.
        """
        if self._is_running and task_id in self._rich_task_ids:
            rich_id = self._rich_task_ids[task_id]
            self.progress.update(
                rich_id,
                completed=task.current,
                description=task.description,
            )

        if self.live:
            self.live.update(self._create_display())

    def complete(self, task_id: str, error: str | None = None) -> None:
        status = TaskStatus.FAILED if error else TaskStatus.COMPLETED
        total = self._tasks.get(task_id).total if task_id in self._tasks else None
        self.update(task_id, status=status, error=error, current=total)

    def start(self) -> UnifiedProgressWidget:
        self._is_running = True

        for task_id in self._task_order:
            task = self._tasks[task_id]
            rich_task = self.progress.add_task(
                task.description, total=task.total, completed=task.current,
            )
            self._rich_task_ids[task_id] = rich_task

        self.live = Live(
            self._create_display(),
            console=self.console,
            refresh_per_second=self.refresh_rate,
        )
        self.live.start()

        return self

    def stop(self) -> None:
        if self.live:
            self.live.stop()
            self.live = None
        self._is_running = False

    def __enter__(self) -> Self:
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

    def _create_display(self) -> Group:
        components = [self.progress]

        with self._lock:
            if self.show_categories and self.categories:
                components.append(build_category_panel(self.categories))

            if not self.compact:
                running_tasks = [t for t in self._tasks.values() if t.status == TaskStatus.RUNNING]
                if running_tasks:
                    components.append(
                        build_current_task_panel(
                            running_tasks[0],
                            show_sparklines=self.show_sparklines,
                            show_metrics=self.show_metrics,
                        ),
                    )

            components.append(build_statistics_panel(self._tasks.values()))

        return Group(*components)

    def get_task(self, task_id: str) -> Task | None:
        with self._lock:
            return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[Task]:
        with self._lock:
            return [self._tasks[tid] for tid in self._task_order]

    def clear(self) -> None:
        with self._lock:
            self._tasks.clear()
            self._task_order.clear()
            self._rich_task_ids.clear()
            for stats in self.categories.values():
                stats.total = stats.completed = stats.passed = stats.failed = stats.cached = (
                    stats.skipped
                ) = 0


ComprehensiveProgressDisplay = UnifiedProgressWidget
TestProgressTracker = UnifiedProgressWidget
ProgressWidget = UnifiedProgressWidget

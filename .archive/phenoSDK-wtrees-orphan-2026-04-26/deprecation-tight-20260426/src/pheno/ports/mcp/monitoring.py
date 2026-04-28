"""Monitoring Provider Port.

Defines the protocol for workflow and metrics monitoring in MCP.
"""

from datetime import datetime
from typing import Any, Protocol


class MonitoringProvider(Protocol):
    """Protocol for workflow and metrics monitoring.

    Provides tracking for MCP workflows, tool executions, and performance metrics.
    Implementations can send data to various backends (Prometheus, DataDog, etc.).

    Example:
        >>> monitor = get_monitoring_provider()
        >>>
        >>> # Track workflow
        >>> await monitor.track_workflow(
        ...     workflow_id="data-pipeline",
        ...     metadata={"user": "alice"}
        ... )
        >>>
        >>> # Record metrics
        >>> await monitor.record_metric(
        ...     name="tool_execution_time",
        ...     value=1.23,
        ...     tags={"tool": "search"}
        ... )
    """

    async def track_workflow(
        self, workflow_id: str, metadata: dict[str, Any] | None = None,
    ) -> None:
        """Track a workflow execution.

        Args:
            workflow_id: Unique workflow identifier
            metadata: Optional workflow metadata

        Example:
            >>> await monitor.track_workflow(
            ...     "data-pipeline",
            ...     metadata={"user": "alice", "env": "prod"}
            ... )
        """
        ...

    async def record_metric(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        """Record a metric value.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags for filtering
            timestamp: Optional timestamp (defaults to now)

        Example:
            >>> await monitor.record_metric(
            ...     "tool_execution_time",
            ...     1.23,
            ...     tags={"tool": "search", "status": "success"}
            ... )
        """
        ...

    async def record_counter(
        self, name: str, increment: int = 1, tags: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Counter name
            increment: Amount to increment
            tags: Optional tags

        Example:
            >>> await monitor.record_counter(
            ...     "tool_executions",
            ...     tags={"tool": "search"}
            ... )
        """
        ...

    async def record_histogram(
        self, name: str, value: float, tags: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram value.

        Args:
            name: Histogram name
            value: Value to record
            tags: Optional tags

        Example:
            >>> await monitor.record_histogram(
            ...     "response_size_bytes",
            ...     1024,
            ...     tags={"endpoint": "/api/search"}
            ... )
        """
        ...

    async def get_metrics(
        self,
        filters: dict[str, Any] | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Get recorded metrics.

        Args:
            filters: Optional filters (name, tags, etc.)
            start_time: Optional start time
            end_time: Optional end time

        Returns:
            List of metric records

        Example:
            >>> metrics = await monitor.get_metrics(
            ...     filters={"name": "tool_execution_time"},
            ...     start_time=datetime.now() - timedelta(hours=1)
            ... )
        """
        ...

    async def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        """Get status of a workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Workflow status dictionary

        Example:
            >>> status = await monitor.get_workflow_status("data-pipeline")
            >>> print(f"Status: {status['state']}")
        """
        ...

    async def list_workflows(
        self, filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """List tracked workflows.

        Args:
            filters: Optional filters

        Returns:
            List of workflow records

        Example:
            >>> workflows = await monitor.list_workflows(
            ...     filters={"user": "alice"}
            ... )
        """
        ...

    async def record_error(
        self, error: Exception, context: dict[str, Any] | None = None,
    ) -> None:
        """Record an error.

        Args:
            error: Exception that occurred
            context: Optional error context

        Example:
            >>> try:
            ...     await execute_tool(tool, params)
            ... except Exception as e:
            ...     await monitor.record_error(e, {"tool": "search"})
        """
        ...

    async def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> str:
        """Start a tracing span.

        Args:
            name: Span name
            attributes: Optional span attributes

        Returns:
            Span ID

        Example:
            >>> span_id = await monitor.start_span(
            ...     "tool_execution",
            ...     attributes={"tool": "search"}
            ... )
        """
        ...

    async def end_span(
        self, span_id: str, status: str = "ok", attributes: dict[str, Any] | None = None,
    ) -> None:
        """End a tracing span.

        Args:
            span_id: Span identifier
            status: Span status ("ok", "error")
            attributes: Optional additional attributes

        Example:
            >>> await monitor.end_span(span_id, status="ok")
        """
        ...

    async def flush(self) -> None:
        """Flush any buffered metrics.

        Example:
            >>> await monitor.flush()
        """
        ...


__all__ = ["MonitoringProvider"]

"""Service for performance tuning and optimization."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

# Average query time threshold (ms) above which to recommend indexes
AVG_TIME_MS_THRESHOLD = 100


class PerformanceTuningService:
    """Service for performance tuning and optimization."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.metrics: list[dict[str, Any]] = []
        self.recommendations: list[str] = []
        self.cache_config: dict[str, Any] = {
            "enabled": True,
            "ttl_seconds": 300,
            "max_size": 1000,
        }

    async def analyze_performance(self) -> dict[str, Any]:
        """Analyze overall performance."""
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "metrics_collected": len(self.metrics),
            "cache_enabled": self.cache_config["enabled"],
            "cache_ttl": self.cache_config["ttl_seconds"],
            "recommendations": len(self.recommendations),
        }

    def record_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
    ) -> None:
        """Record a performance metric."""
        metric = {
            "name": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self.metrics.append(metric)

    def get_metrics(self, metric_name: str | None = None) -> list[dict[str, Any]]:
        """Get recorded metrics, optionally filtered by name."""
        metrics = self.metrics

        if metric_name:
            metrics = [m for m in metrics if m["name"] == metric_name]

        return metrics

    def get_metric_stats(self, metric_name: str) -> dict[str, Any]:
        """Get statistics for a specific metric."""
        metrics = self.get_metrics(metric_name)

        if not metrics:
            return {"error": "No metrics found"}

        values = [m["value"] for m in metrics]

        return {
            "metric_name": metric_name,
            "count": len(values),
            "average": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "unit": metrics[0].get("unit", "ms"),
        }

    def add_recommendation(self, recommendation: str) -> None:
        """Add a performance recommendation."""
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)

    def get_recommendations(self) -> list[str]:
        """Get all recommendations."""
        return self.recommendations

    def clear_recommendations(self) -> int:
        """Clear all recommendations."""
        count = len(self.recommendations)
        self.recommendations.clear()
        return count

    def configure_cache(
        self,
        enabled: bool = True,
        ttl_seconds: int = 300,
        max_size: int = 1000,
    ) -> dict[str, Any]:
        """Configure cache settings."""
        self.cache_config = {
            "enabled": enabled,
            "ttl_seconds": ttl_seconds,
            "max_size": max_size,
        }
        return self.cache_config

    def get_cache_config(self) -> dict[str, Any]:
        """Get cache configuration."""
        return self.cache_config.copy()

    def enable_cache(self) -> None:
        """Enable caching."""
        self.cache_config["enabled"] = True

    def disable_cache(self) -> None:
        """Disable caching."""
        self.cache_config["enabled"] = False

    def is_cache_enabled(self) -> bool:
        """Check if caching is enabled."""
        return bool(self.cache_config["enabled"])

    def optimize_indexes(self) -> list[str]:
        """Generate index optimization recommendations."""
        recommendations: list[dict[str, Any]] = []

        # Analyze metrics to recommend indexes
        query_metrics = self.get_metrics("query_time")

        if query_metrics:
            avg_time = sum(m["value"] for m in query_metrics) / len(query_metrics)

            if avg_time > AVG_TIME_MS_THRESHOLD:
                recommendations.extend((
                    "CREATE INDEX idx_item_status ON items(status)",
                    "CREATE INDEX idx_item_view ON items(view)",
                    "CREATE INDEX idx_link_source ON links(source_item_id)",
                ))

        return recommendations  # type: ignore[return-value]

    def get_tuning_report(self) -> dict[str, Any]:
        """Generate comprehensive tuning report."""
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "metrics_count": len(self.metrics),
            "recommendations_count": len(self.recommendations),
            "cache_config": self.cache_config,
            "recommendations": self.recommendations,
            "index_recommendations": self.optimize_indexes(),
        }

    def reset_metrics(self) -> int:
        """Reset all metrics."""
        count = len(self.metrics)
        self.metrics.clear()
        return count

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary."""
        if not self.metrics:
            return {"error": "No metrics available"}

        metric_names = {m["name"] for m in self.metrics}

        summary = {}
        for name in metric_names:
            stats = self.get_metric_stats(name)
            if "error" not in stats:
                summary[name] = stats

        return {
            "total_metrics": len(self.metrics),
            "metric_types": len(metric_names),
            "metrics": summary,
        }

"""Service for query optimization and analysis."""

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository


class QueryOptimizationService:
    """Service for optimizing queries."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)
        self.query_cache: dict[str, Any] = {}
        self.query_stats: list[dict[str, Any]] = []

    async def analyze_query_performance(
        self,
        project_id: str,
        query_filters: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze query performance."""
        start_time = datetime.utcnow()

        # Execute query
        items = await self.items.query(project_id, query_filters)

        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()

        # Record stats
        stats = {
            "query_filters": query_filters,
            "execution_time_seconds": execution_time,
            "items_returned": len(items),
            "timestamp": start_time.isoformat(),
        }

        self.query_stats.append(stats)

        return {
            "execution_time_seconds": execution_time,
            "items_returned": len(items),
            "performance_rating": self._rate_performance(execution_time),
            "optimization_suggestions": self._suggest_optimizations(
                execution_time, len(items)
            ),
        }

    def _rate_performance(self, execution_time: float) -> str:
        """Rate query performance."""
        if execution_time < 0.1:
            return "Excellent"
        elif execution_time < 0.5:
            return "Good"
        elif execution_time < 1.0:
            return "Fair"
        else:
            return "Poor"

    def _suggest_optimizations(
        self, execution_time: float, result_count: int
    ) -> list[str]:
        """Suggest query optimizations."""
        suggestions = []

        if execution_time > 1.0:
            suggestions.append("Consider adding indexes to frequently queried fields")

        if result_count > 10000:
            suggestions.append("Consider using pagination for large result sets")

        if execution_time > 0.5 and result_count < 100:
            suggestions.append("Consider caching this query result")

        return suggestions

    def cache_query(
        self,
        query_key: str,
        result: Any,
        ttl_seconds: int = 300,
    ) -> None:
        """Cache query result."""
        self.query_cache[query_key] = {
            "result": result,
            "cached_at": datetime.utcnow().isoformat(),
            "ttl_seconds": ttl_seconds,
        }

    def get_cached_query(self, query_key: str) -> Any | None:
        """Get cached query result."""
        if query_key in self.query_cache:
            cached = self.query_cache[query_key]
            # Check if cache is still valid
            cached_at = datetime.fromisoformat(cached["cached_at"])
            age = (datetime.utcnow() - cached_at).total_seconds()

            if age < cached["ttl_seconds"]:
                return cached["result"]
            else:
                # Cache expired
                del self.query_cache[query_key]

        return None

    def clear_cache(self) -> int:
        """Clear all cached queries."""
        count = len(self.query_cache)
        self.query_cache.clear()
        return count

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_queries": len(self.query_cache),
            "total_queries_executed": len(self.query_stats),
            "cache_keys": list(self.query_cache.keys()),
        }

    def get_query_statistics(self) -> dict[str, Any]:
        """Get query execution statistics."""
        if not self.query_stats:
            return {
                "total_queries": 0,
                "average_execution_time": 0,
                "min_execution_time": 0,
                "max_execution_time": 0,
            }

        execution_times = [s["execution_time_seconds"] for s in self.query_stats]

        return {
            "total_queries": len(self.query_stats),
            "average_execution_time": sum(execution_times) / len(execution_times),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "total_items_returned": sum(s["items_returned"] for s in self.query_stats),
        }

    def recommend_indexes(self, project_id: str) -> list[str]:
        """Recommend indexes based on query patterns."""
        recommendations = []

        # Analyze query stats
        if len(self.query_stats) > 10:
            # If many queries filter by status, recommend status index
            status_queries = [
                s for s in self.query_stats if "status" in s.get("query_filters", {})
            ]
            if len(status_queries) > len(self.query_stats) * 0.5:
                recommendations.append("CREATE INDEX idx_item_status ON items(status)")

            # If many queries filter by view, recommend view index
            view_queries = [
                s for s in self.query_stats if "view" in s.get("query_filters", {})
            ]
            if len(view_queries) > len(self.query_stats) * 0.5:
                recommendations.append("CREATE INDEX idx_item_view ON items(view)")

        return recommendations

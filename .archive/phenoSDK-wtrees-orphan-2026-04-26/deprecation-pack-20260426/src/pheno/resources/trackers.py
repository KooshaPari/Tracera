"""Usage tracking and analysis components.

Provides historical analysis and predictive planning capabilities for resource usage.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from pheno.resources.budget import BudgetPeriod, ResourceAllocation, ResourceBudget


class UsageTracker:
    """Track resource usage over time.

    Maintains time-series data for resource consumption.
    """

    def __init__(self, retention_days: int = 90):
        """Initialize usage tracker.

        Args:
            retention_days: How long to retain usage data
        """
        self.retention_days = retention_days
        self.usage_events: list[dict[str, Any]] = []

    def record_usage(
        self,
        resource_type: str,
        units: float,
        cost_usd: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a usage event.

        Args:
            resource_type: Type of resource
            units: Amount of units used
            cost_usd: Cost in USD
            metadata: Additional metadata
        """
        event = {
            "timestamp": datetime.now(UTC),
            "resource_type": resource_type,
            "units": units,
            "cost_usd": cost_usd,
            "metadata": metadata or {},
        }
        self.usage_events.append(event)
        self._cleanup_old_events()

    def get_usage(
        self,
        resource_type: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Get usage events matching criteria.

        Args:
            resource_type: Filter by resource type
            start_time: Start of time range
            end_time: End of time range

        Returns:
            List of matching usage events
        """
        events = self.usage_events

        if resource_type:
            events = [e for e in events if e["resource_type"] == resource_type]

        if start_time:
            events = [e for e in events if e["timestamp"] >= start_time]

        if end_time:
            events = [e for e in events if e["timestamp"] <= end_time]

        return events

    def get_total_usage(
        self,
        resource_type: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, float]:
        """Get total usage for a time period.

        Args:
            resource_type: Filter by resource type
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Dictionary with total units and cost
        """
        events = self.get_usage(resource_type, start_time, end_time)

        total_units = sum(e["units"] for e in events)
        total_cost = sum(e["cost_usd"] for e in events)

        return {
            "total_units": total_units,
            "total_cost_usd": total_cost,
            "event_count": len(events),
        }

    def _cleanup_old_events(self) -> None:
        """
        Remove events older than retention period.
        """
        cutoff = datetime.now(UTC) - timedelta(days=self.retention_days)
        self.usage_events = [e for e in self.usage_events if e["timestamp"] >= cutoff]


class HistoricalAnalyzer:
    """Analyze historical usage patterns.

    Provides insights into resource consumption trends and patterns.
    """

    def __init__(self, tracker: UsageTracker):
        """Initialize historical analyzer.

        Args:
            tracker: Usage tracker instance
        """
        self.tracker = tracker

    def analyze_trends(
        self,
        resource_type: str,
        days: int = 30,
    ) -> dict[str, Any]:
        """Analyze usage trends over time.

        Args:
            resource_type: Type of resource to analyze
            days: Number of days to analyze

        Returns:
            Dictionary with trend analysis
        """
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(days=days)

        events = self.tracker.get_usage(resource_type, start_time, end_time)

        if not events:
            return {"error": "No data available"}

        # Group by day
        daily_usage: dict[str, float] = {}
        for event in events:
            day = event["timestamp"].date().isoformat()
            daily_usage[day] = daily_usage.get(day, 0.0) + event["units"]

        # Calculate statistics
        daily_values = list(daily_usage.values())
        avg_daily = sum(daily_values) / len(daily_values) if daily_values else 0
        max_daily = max(daily_values) if daily_values else 0
        min_daily = min(daily_values) if daily_values else 0

        # Calculate trend (simple linear regression)
        if len(daily_values) > 1:
            x_mean = len(daily_values) / 2
            y_mean = avg_daily
            numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(daily_values))
            denominator = sum((i - x_mean) ** 2 for i in range(len(daily_values)))
            slope = numerator / denominator if denominator != 0 else 0
            trend = "increasing" if slope > 0.1 else "decreasing" if slope < -0.1 else "stable"
        else:
            trend = "unknown"

        return {
            "resource_type": resource_type,
            "period_days": days,
            "total_usage": sum(daily_values),
            "average_daily": avg_daily,
            "max_daily": max_daily,
            "min_daily": min_daily,
            "trend": trend,
            "daily_breakdown": daily_usage,
        }

    def get_peak_usage_times(
        self,
        resource_type: str,
        days: int = 7,
    ) -> dict[str, Any]:
        """Identify peak usage times.

        Args:
            resource_type: Type of resource to analyze
            days: Number of days to analyze

        Returns:
            Dictionary with peak usage information
        """
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(days=days)

        events = self.tracker.get_usage(resource_type, start_time, end_time)

        if not events:
            return {"error": "No data available"}

        # Group by hour of day
        hourly_usage: dict[int, float] = {}
        for event in events:
            hour = event["timestamp"].hour
            hourly_usage[hour] = hourly_usage.get(hour, 0.0) + event["units"]

        # Find peak hours
        peak_hour = max(hourly_usage.items(), key=lambda x: x[1]) if hourly_usage else (0, 0)

        return {
            "resource_type": resource_type,
            "peak_hour": peak_hour[0],
            "peak_usage": peak_hour[1],
            "hourly_distribution": hourly_usage,
        }

    def analyze_allocation_efficiency(
        self, allocation_history: list[ResourceAllocation],
    ) -> dict[str, Any]:
        """Analyze allocation efficiency.

        Args:
            allocation_history: List of completed allocations

        Returns:
            Dictionary with efficiency metrics
        """
        if not allocation_history:
            return {"error": "No allocation history"}

        completed = [a for a in allocation_history if a.is_completed]

        if not completed:
            return {"error": "No completed allocations"}

        # Calculate efficiency metrics
        total_allocated = sum(a.allocated_units for a in completed)
        total_used = sum(a.used_units for a in completed)
        avg_efficiency = sum(a.efficiency_score for a in completed) / len(completed)

        wasted = sum(
            a.allocated_units - a.used_units for a in completed if a.allocated_units > a.used_units
        )
        exceeded = sum(
            a.used_units - a.allocated_units for a in completed if a.used_units > a.allocated_units
        )

        return {
            "total_allocations": len(completed),
            "total_allocated": total_allocated,
            "total_used": total_used,
            "average_efficiency": avg_efficiency,
            "wasted_units": wasted,
            "exceeded_units": exceeded,
            "exceeded_count": len([a for a in completed if a.exceeded_allocation]),
            "waste_percentage": (wasted / total_allocated * 100) if total_allocated > 0 else 0,
        }


class PredictivePlanner:
    """Predictive planning for resource budgets.

    Forecasts future usage and provides budget recommendations.
    """

    def __init__(self, analyzer: HistoricalAnalyzer):
        """Initialize predictive planner.

        Args:
            analyzer: Historical analyzer instance
        """
        self.analyzer = analyzer

    def predict_budget_exhaustion(
        self, budget: ResourceBudget, resource_type: str,
    ) -> datetime | None:
        """Predict when a budget will be exhausted.

        Args:
            budget: Budget to analyze
            resource_type: Type of resource

        Returns:
            Predicted exhaustion datetime or None
        """
        if budget.is_exhausted:
            return None

        # Calculate current usage rate
        time_elapsed = (datetime.now(UTC) - budget.period_start).total_seconds()
        if time_elapsed <= 0:
            return None

        units_per_second = budget.used_units / time_elapsed

        if units_per_second <= 0:
            return None

        # Predict exhaustion
        remaining_units = budget.available_units
        seconds_to_exhaustion = remaining_units / units_per_second

        predicted_exhaustion = datetime.now(UTC) + timedelta(seconds=seconds_to_exhaustion)

        # Don't predict beyond period end
        if budget.period_end and predicted_exhaustion > budget.period_end:
            return None

        return predicted_exhaustion

    def recommend_budget(
        self,
        resource_type: str,
        period: BudgetPeriod,
        historical_days: int = 30,
        buffer_multiplier: float = 1.2,
    ) -> dict[str, Any]:
        """Recommend budget based on historical usage.

        Args:
            resource_type: Type of resource
            period: Budget period
            historical_days: Days of history to consider
            buffer_multiplier: Safety buffer multiplier

        Returns:
            Dictionary with budget recommendation
        """
        # Analyze historical trends
        trends = self.analyzer.analyze_trends(resource_type, historical_days)

        if "error" in trends:
            return {"error": "Insufficient historical data"}

        # Calculate recommended budget based on period
        avg_daily = trends["average_daily"]

        period_multipliers = {
            BudgetPeriod.HOURLY: 1 / 24,
            BudgetPeriod.DAILY: 1,
            BudgetPeriod.WEEKLY: 7,
            BudgetPeriod.MONTHLY: 30,
        }

        multiplier = period_multipliers.get(period, 1)
        base_recommendation = avg_daily * multiplier

        # Add buffer for safety
        recommended_units = base_recommendation * buffer_multiplier

        # Consider trend
        if trends["trend"] == "increasing":
            # Add extra buffer for increasing trends
            recommended_units *= 1.1
        elif trends["trend"] == "decreasing":
            # Slightly reduce for decreasing trends
            recommended_units *= 0.95

        return {
            "resource_type": resource_type,
            "period": period.value,
            "recommended_units": recommended_units,
            "base_recommendation": base_recommendation,
            "buffer_multiplier": buffer_multiplier,
            "historical_average": avg_daily,
            "trend": trends["trend"],
            "confidence": (
                "high" if historical_days >= 30 else "medium" if historical_days >= 7 else "low"
            ),
        }

    def forecast_usage(
        self,
        resource_type: str,
        days_ahead: int = 7,
        historical_days: int = 30,
    ) -> dict[str, Any]:
        """Forecast future usage.

        Args:
            resource_type: Type of resource
            days_ahead: Number of days to forecast
            historical_days: Days of history to use

        Returns:
            Dictionary with usage forecast
        """
        trends = self.analyzer.analyze_trends(resource_type, historical_days)

        if "error" in trends:
            return {"error": "Insufficient historical data"}

        avg_daily = trends["average_daily"]

        # Simple forecast based on average and trend
        forecast = []
        for day in range(1, days_ahead + 1):
            # Adjust based on trend
            if trends["trend"] == "increasing":
                adjustment = 1 + (0.01 * day)  # 1% increase per day
            elif trends["trend"] == "decreasing":
                adjustment = 1 - (0.01 * day)  # 1% decrease per day
            else:
                adjustment = 1

            forecast.append(
                {
                    "day": day,
                    "date": (datetime.now(UTC) + timedelta(days=day)).date().isoformat(),
                    "predicted_usage": avg_daily * adjustment,
                },
            )

        return {
            "resource_type": resource_type,
            "forecast_days": days_ahead,
            "historical_days": historical_days,
            "forecast": forecast,
            "total_predicted": sum(f["predicted_usage"] for f in forecast),
        }

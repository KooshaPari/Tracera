"""Resource monitoring rendering and reporting utilities.

Provides visualization, reporting, and dashboard components for resource monitoring and
analysis.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from pheno.resources.budget import ResourceAllocation, ResourceBudget

logger = logging.getLogger(__name__)


class BudgetStatusRenderer:
    """
    Renders budget status and allocation information.
    """

    def __init__(self):
        self.visualization_engines = {
            "text": TextRenderer(),
            "json": JsonRenderer(),
            "html": HtmlRenderer(),
        }

    def render_budget_status(
        self, budgets: dict[str, ResourceBudget], format_type: str = "text",
    ) -> str:
        """Render budget status in specified format.

        Args:
            budgets: Dictionary of budgets by key
            format_type: Output format ('text', 'json', 'html')

        Returns:
            Formatted budget status string
        """
        renderer = self.visualization_engines.get(format_type)
        if not renderer:
            raise ValueError(f"Unsupported format type: {format_type}")

        return renderer.render_budgets(budgets)

    def render_allocation_report(
        self, allocations: list[ResourceAllocation], format_type: str = "text",
    ) -> str:
        """Render allocation report in specified format.

        Args:
            allocations: List of allocations
            format_type: Output format ('text', 'json', 'html')

        Returns:
            Formatted allocation report
        """
        renderer = self.visualization_engines.get(format_type)
        if not renderer:
            raise ValueError(f"Unsupported format type: {format_type}")

        return renderer.render_allocations(allocations)

    def render_utilization_summary(
        self,
        budgets: dict[str, ResourceBudget],
        allocations: list[ResourceAllocation],
        format_type: str = "text",
    ) -> str:
        """Render utilization summary combining budgets and allocations.

        Args:
            budgets: Dictionary of budgets
            allocations: List of allocations
            format_type: Output format ('text', 'json', 'html')

        Returns:
            Formatted utilization summary
        """
        renderer = self.visualization_engines.get(format_type)
        if not renderer:
            raise ValueError(f"Unsupported format type: {format_type}")

        return renderer.render_utilization(budgets, allocations)


class TextRenderer:
    """
    Text-based rendering for budgets and allocations.
    """

    def render_budgets(self, budgets: dict[str, ResourceBudget]) -> str:
        """
        Render budgets as formatted text.
        """
        if not budgets:
            return "No budgets found.\n"

        lines = ["=== Budget Status ===", ""]

        for budget in budgets.values():
            utilization = (
                (budget.used_units / budget.total_units * 100) if budget.total_units > 0 else 0
            )

            lines.append(f"Resource: {budget.resource_type}")
            lines.append(f"Period: {budget.period.value}")
            lines.append(f"Total: {budget.total_units:,.0f} units")
            lines.append(f"Used: {budget.used_units:,.0f} units ({utilization:.1f}%)")
            lines.append(f"Allocated: {budget.allocated_units:,.0f} units")
            lines.append(f"Available: {budget.available_units:,.0f} units")

            if budget.total_budget_usd:
                cost_utilization = (
                    (budget.used_budget_usd / budget.total_budget_usd * 100)
                    if budget.total_budget_usd > 0
                    else 0
                )
                lines.append(
                    f"Cost: ${budget.used_budget_usd:.2f} / ${budget.total_budget_usd:.2f} ({cost_utilization:.1f}%)",
                )

            lines.append(
                f"Period: {budget.period_start.strftime('%Y-%m-%d %H:%M')} to {budget.period_end.strftime('%Y-%m-%d %H:%M')}",
            )
            lines.append("")

        return "\n".join(lines)

    def render_allocations(self, allocations: list[ResourceAllocation]) -> str:
        """
        Render allocations as formatted text.
        """
        if not allocations:
            return "No allocations found.\n"

        lines = ["=== Allocation Report ===", ""]

        for allocation in allocations:
            lines.append(f"Allocation ID: {allocation.allocation_id}")
            lines.append(f"Request ID: {allocation.request_id}")
            lines.append(f"Resource: {allocation.resource_type}")
            if allocation.model_name:
                lines.append(f"Model: {allocation.model_name}")
            lines.append(f"Strategy: {allocation.strategy.value}")
            lines.append(f"Priority: {allocation.priority}")
            lines.append(f"Requested: {allocation.requested_units:,.0f} units")
            lines.append(f"Allocated: {allocation.allocated_units:,.0f} units")
            lines.append(f"Used: {allocation.used_units:,.0f} units")

            if allocation.allocated_units > 0:
                efficiency = allocation.used_units / allocation.allocated_units * 100
                lines.append(f"Efficiency: {efficiency:.1f}%")

            lines.append(f"Status: {'Active' if allocation.is_active else 'Completed'}")

            if allocation.exceeded_allocation:
                lines.append("⚠️  ALLOCATION EXCEEDED")

            lines.append("")

        return "\n".join(lines)

    def render_utilization(
        self, budgets: dict[str, ResourceBudget], allocations: list[ResourceAllocation],
    ) -> str:
        """
        Render utilization summary.
        """
        total_allocated = sum(b.allocated_units for b in budgets.values())
        total_used = sum(b.used_units for b in budgets.values())
        total_budget = sum(b.total_units for b in budgets.values())

        active_allocations = [a for a in allocations if a.is_active]

        lines = ["=== Utilization Summary ===", ""]
        lines.append(f"Total Budget: {total_budget:,.0f} units")
        lines.append(f"Total Allocated: {total_allocated:,.0f} units")
        lines.append(f"Total Used: {total_used:,.0f} units")
        lines.append(f"Active Allocations: {len(active_allocations)}")

        if total_budget > 0:
            overall_utilization = total_used / total_budget * 100
            allocation_efficiency = total_allocated / total_budget * 100
            lines.append(f"Overall Utilization: {overall_utilization:.1f}%")
            lines.append(f"Allocation Efficiency: {allocation_efficiency:.1f}%")

        lines.append("")

        # Resource type breakdown
        resource_breakdown = {}
        for budget in budgets.values():
            resource_type = budget.resource_type
            if resource_type not in resource_breakdown:
                resource_breakdown[resource_type] = {"total": 0, "used": 0, "allocated": 0}
            resource_breakdown[resource_type]["total"] += budget.total_units
            resource_breakdown[resource_type]["used"] += budget.used_units
            resource_breakdown[resource_type]["allocated"] += budget.allocated_units

        lines.append("Resource Type Breakdown:")
        for resource_type, stats in resource_breakdown.items():
            utilization = (stats["used"] / stats["total"] * 100) if stats["total"] > 0 else 0
            lines.append(
                f"  {resource_type}: {stats['used']:,.0f}/{stats['total']:,.0f} ({utilization:.1f}%)",
            )

        return "\n".join(lines)


class JsonRenderer:
    """
    JSON-based rendering for budgets and allocations.
    """

    def render_budgets(self, budgets: dict[str, ResourceBudget]) -> str:
        """
        Render budgets as JSON.
        """
        import json

        budget_data = {}
        for key, budget in budgets.items():
            budget_data[key] = budget.to_dict()

        return json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "total_budgets": len(budgets),
                "budgets": budget_data,
            },
            indent=2,
        )

    def render_allocations(self, allocations: list[ResourceAllocation]) -> str:
        """
        Render allocations as JSON.
        """
        import json

        allocation_data = []
        for allocation in allocations:
            allocation_data.append(allocation.to_dict())

        return json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "total_allocations": len(allocations),
                "allocations": allocation_data,
            },
            indent=2,
        )

    def render_utilization(
        self, budgets: dict[str, ResourceBudget], allocations: list[ResourceAllocation],
    ) -> str:
        """
        Render utilization as JSON.
        """
        import json

        utilization_data = self._calculate_utilization_metrics(budgets, allocations)

        return json.dumps(
            {"timestamp": datetime.now(UTC).isoformat(), "utilization": utilization_data},
            indent=2,
        )


class HtmlRenderer:
    """
    HTML-based rendering for budgets and allocations.
    """

    def render_budgets(self, budgets: dict[str, ResourceBudget]) -> str:
        """
        Render budgets as HTML table.
        """
        if not budgets:
            return "<p>No budgets found.</p>"

        html = """
        <div class="budget-status">
            <h2>Budget Status</h2>
            <table class="budget-table">
                <thead>
                    <tr>
                        <th>Resource</th>
                        <th>Period</th>
                        <th>Total</th>
                        <th>Used</th>
                        <th>Allocated</th>
                        <th>Available</th>
                        <th>Utilization</th>
                    </tr>
                </thead>
                <tbody>
        """

        for budget in budgets.values():
            utilization = (
                (budget.used_units / budget.total_units * 100) if budget.total_units > 0 else 0
            )

            html += f"""
                    <tr>
                        <td>{budget.resource_type}</td>
                        <td>{budget.period.value}</td>
                        <td>{budget.total_units:,.0f}</td>
                        <td>{budget.used_units:,.0f}</td>
                        <td>{budget.allocated_units:,.0f}</td>
                        <td>{budget.available_units:,.0f}</td>
                        <td>{utilization:.1f}%</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
        </div>
        """

        return html

    def render_allocations(self, allocations: list[ResourceAllocation]) -> str:
        """
        Render allocations as HTML table.
        """
        if not allocations:
            return "<p>No allocations found.</p>"

        html = """
        <div class="allocation-report">
            <h2>Allocation Report</h2>
            <table class="allocation-table">
                <thead>
                    <tr>
                        <th>Allocation ID</th>
                        <th>Resource</th>
                        <th>Model</th>
                        <th>Strategy</th>
                        <th>Requested</th>
                        <th>Allocated</th>
                        <th>Used</th>
                        <th>Efficiency</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        """

        for allocation in allocations:
            efficiency = (
                (allocation.used_units / allocation.allocated_units * 100)
                if allocation.allocated_units > 0
                else 0
            )
            status = "Active" if allocation.is_active else "Completed"
            status_class = "active" if allocation.is_active else "completed"

            if allocation.exceeded_allocation:
                status_class += " exceeded"

            html += f"""
                    <tr class="{status_class}">
                        <td>{allocation.allocation_id}</td>
                        <td>{allocation.resource_type}</td>
                        <td>{allocation.model_name or 'N/A'}</td>
                        <td>{allocation.strategy.value}</td>
                        <td>{allocation.requested_units:,.0f}</td>
                        <td>{allocation.allocated_units:,.0f}</td>
                        <td>{allocation.used_units:,.0f}</td>
                        <td>{efficiency:.1f}%</td>
                        <td>{status}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
        </div>
        """

        return html

    def render_utilization(
        self, budgets: dict[str, ResourceBudget], allocations: list[ResourceAllocation],
    ) -> str:
        """
        Render utilization summary as HTML.
        """
        metrics = self._calculate_utilization_metrics(budgets, allocations)

        html = """
        <div class="utilization-summary">
            <h2>Utilization Summary</h2>
            <div class="metrics-grid">
        """

        # Key metrics
        html += f"""
                <div class="metric-card">
                    <h3>Total Budget</h3>
                    <p class="metric-value">{metrics['total_budget']:,.0f} units</p>
                </div>
                <div class="metric-card">
                    <h3>Total Used</h3>
                    <p class="metric-value">{metrics['total_used']:,.0f} units</p>
                </div>
                <div class="metric-card">
                    <h3>Overall Utilization</h3>
                    <p class="metric-value">{metrics['overall_utilization']:.1f}%</p>
                </div>
                <div class="metric-card">
                    <h3>Active Allocations</h3>
                    <p class="metric-value">{metrics['active_allocations']}</p>
                </div>
        """

        html += """
            </div>
        </div>
        """

        return html

    def _calculate_utilization_metrics(
        self, budgets: dict[str, ResourceBudget], allocations: list[ResourceAllocation],
    ) -> dict[str, Any]:
        """
        Calculate utilization metrics.
        """
        total_allocated = sum(b.allocated_units for b in budgets.values())
        total_used = sum(b.used_units for b in budgets.values())
        total_budget = sum(b.total_units for b in budgets.values())

        active_allocations = len([a for a in allocations if a.is_active])

        overall_utilization = (total_used / total_budget * 100) if total_budget > 0 else 0

        return {
            "total_budget": total_budget,
            "total_allocated": total_allocated,
            "total_used": total_used,
            "overall_utilization": overall_utilization,
            "active_allocations": active_allocations,
        }


class AlertRenderer:
    """
    Renders alerts and warnings for resource management.
    """

    def render_budget_alerts(self, budgets: dict[str, ResourceBudget]) -> list[dict[str, Any]]:
        """
        Generate alerts for budget thresholds.
        """
        alerts = []

        for budget in budgets.values():
            utilization = (
                (budget.used_units / budget.total_units * 100) if budget.total_units > 0 else 0
            )

            # Low remaining budget alert
            if utilization >= 90:
                alerts.append(
                    {
                        "type": "critical",
                        "resource_type": budget.resource_type,
                        "period": budget.period.value,
                        "message": f"Budget {budget.resource_type} is {utilization:.1f}% used",
                        "utilization": utilization,
                        "remaining_units": budget.available_units,
                    },
                )
            elif utilization >= 75:
                alerts.append(
                    {
                        "type": "warning",
                        "resource_type": budget.resource_type,
                        "period": budget.period.value,
                        "message": f"Budget {budget.resource_type} is {utilization:.1f}% used",
                        "utilization": utilization,
                        "remaining_units": budget.available_units,
                    },
                )

            # Cost budget alerts
            if budget.total_budget_usd:
                cost_utilization = (
                    (budget.used_budget_usd / budget.total_budget_usd * 100)
                    if budget.total_budget_usd > 0
                    else 0
                )
                if cost_utilization >= 90:
                    alerts.append(
                        {
                            "type": "critical",
                            "resource_type": budget.resource_type,
                            "period": budget.period.value,
                            "message": f"Cost budget {budget.resource_type} is {cost_utilization:.1f}% used",
                            "utilization": cost_utilization,
                            "remaining_cost": budget.total_budget_usd - budget.used_budget_usd,
                        },
                    )

        return alerts

    def render_recommendations(
        self, budgets: dict[str, ResourceBudget], allocations: list[ResourceAllocation],
    ) -> list[dict[str, Any]]:
        """
        Generate recommendations based on usage patterns.
        """
        recommendations = []

        # Analyze efficiency
        completed_allocations = [a for a in allocations if a.is_completed]

        if completed_allocations:
            avg_efficiency = sum(a.efficiency_score for a in completed_allocations) / len(
                completed_allocations,
            )

            if avg_efficiency < 50:
                recommendations.append(
                    {
                        "type": "efficiency",
                        "priority": "high",
                        "message": f"Low allocation efficiency ({avg_efficiency:.1f}%). Consider reducing requested amounts.",
                        "suggested_action": "review_allocation_strategy",
                    },
                )

        # Check for underutilized budgets
        for budget in budgets.values():
            utilization = (
                (budget.used_units / budget.total_units * 100) if budget.total_units > 0 else 0
            )

            if utilization < 25:
                recommendations.append(
                    {
                        "type": "optimization",
                        "priority": "medium",
                        "resource_type": budget.resource_type,
                        "message": f"Budget {budget.resource_type} underutilized at {utilization:.1f}%",
                        "suggested_action": "reduce_budget_allocation",
                    },
                )

        return recommendations

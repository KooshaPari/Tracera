#!/usr/bin/env python3
"""Dashboard Snapshot Generator.

Creates quick status snapshots for project leads.
Useful for daily emails, Slack updates, or status reports.

Usage:
    python3 scripts/dashboard_snapshot.py
    # Outputs: DASHBOARD_SNAPSHOT_[date].md

    python3 scripts/dashboard_snapshot.py --format=slack
    # Outputs formatted for Slack posting

    python3 scripts/dashboard_snapshot.py --email=lead@example.com
    # Outputs and sends via email (requires SMTP setup)
"""

import argparse
import json
import operator
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class DashboardSnapshot:
    """Generate dashboard snapshots with key metrics and status."""

    def __init__(self, project_dir: Path | None = None) -> None:
        """Initialize."""
        self.project_dir = project_dir or Path.cwd()
        self.dashboard_file = self.project_dir / "COVERAGE_PROGRESS_DASHBOARD.md"
        self.standup_file = self.project_dir / "DAILY_STANDUP_LOG.md"
        self.metrics_dir = self.project_dir / ".coverage_tracking"

    def extract_current_coverage(self) -> float:
        """Extract current coverage % from dashboard or metrics."""
        # Try metrics first
        if self.metrics_dir.exists():
            metrics_files = sorted(self.metrics_dir.glob("metrics_*.json"))
            if metrics_files:
                try:
                    with Path(metrics_files[-1]).open(encoding="utf-8") as f:
                        data = json.load(f)
                        return data.get("line_coverage", 0.0)
                except Exception:
                    pass

        # Try dashboard
        if self.dashboard_file.exists():
            try:
                content = self.dashboard_file.read_text()
                match = re.search(r"Line Coverage:\s*(\d+\.?\d*)", content)
                if match:
                    return float(match.group(1))
            except Exception:
                pass

        return 0.0

    def extract_metrics_history(self, days: int = 7) -> list[dict[str, Any]]:
        """Extract coverage history from metrics files."""
        if not self.metrics_dir.exists():
            return []

        history = []
        metrics_files = sorted(self.metrics_dir.glob("metrics_*.json"))

        # Get last N files
        for mfile in metrics_files[-days:]:
            try:
                with Path(mfile).open(encoding="utf-8") as f:
                    data = json.load(f)
                    history.append({
                        "date": data.get("date", mfile.stem),
                        "coverage": data.get("line_coverage", 0),
                        "tests": data.get("tests_total", 0),
                    })
            except Exception:
                pass

        return history

    def count_active_blockers(self) -> int:
        """Count active blockers from standup log."""
        if not self.standup_file.exists():
            return 0

        try:
            content = self.standup_file.read_text()
            # Count BLOCKER: lines
            blockers = re.findall(r"^BLOCKER:", content, re.MULTILINE)
            return len(blockers)
        except Exception:
            return 0

    def extract_module_coverage(self) -> dict[str, float]:
        """Extract by-module coverage."""
        if not self.metrics_dir.exists():
            return {}

        # Load latest metrics
        metrics_files = sorted(self.metrics_dir.glob("metrics_*.json"))
        if not metrics_files:
            return {}

        try:
            with Path(metrics_files[-1]).open(encoding="utf-8") as f:
                data = json.load(f)
                return data.get("by_module", {})
        except Exception:
            return {}

    def calculate_trend(self, history: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate coverage trend."""
        if len(history) < 2:
            return {
                "direction": "→",
                "change_percent": 0.0,
                "days": 0,
            }

        start_coverage = history[0]["coverage"]
        end_coverage = history[-1]["coverage"]
        change = end_coverage - start_coverage
        days = len(history) - 1

        # Determine direction
        if change > 0.5:
            direction = "📈"
        elif change < -0.5:
            direction = "📉"
        else:
            direction = "→"

        return {
            "direction": direction,
            "change_percent": round(change, 2),
            "days": days,
        }

    def assess_risk(self, current_coverage: float, trend: dict[str, Any], blockers: int) -> str:
        """Assess overall risk status."""
        risk_score = 0

        # Coverage risk
        if current_coverage < 30:
            risk_score += 3
        elif current_coverage < 50:
            risk_score += 2
        elif current_coverage < 70:
            risk_score += 1

        # Trend risk
        if trend["change_percent"] < -2:
            risk_score += 2
        elif trend["direction"] == "→":
            risk_score += 1

        # Blocker risk
        if blockers > 2:
            risk_score += 2
        elif blockers > 0:
            risk_score += 1

        # Assess level
        if risk_score >= 6:
            return "🔴 CRITICAL"
        if risk_score >= 4:
            return "🟠 HIGH"
        if risk_score >= 2:
            return "🟡 MEDIUM"
        return "🟢 LOW"

    def generate_markdown_snapshot(self) -> str:
        """Generate snapshot in Markdown format."""
        current_coverage = self.extract_current_coverage()
        history = self.extract_metrics_history(days=7)
        blockers = self.count_active_blockers()
        modules = self.extract_module_coverage()
        trend = self.calculate_trend(history)
        risk = self.assess_risk(current_coverage, trend, blockers)

        # Forecast (simple linear projection)
        daily_gain = trend["change_percent"] / max(trend["days"], 1) if trend["days"] > 0 else 0
        week_forecast = current_coverage + (daily_gain * 5)

        snapshot = f"""# Dashboard Snapshot - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Status Overview

| Metric | Value | Status |
|--------|-------|--------|
| **Current Coverage** | {current_coverage:.2f}% | {risk} |
| **Trend** | {trend["direction"]} {trend["change_percent"]:+.2f}% (7-day) | {"✓" if trend["direction"] == "📈" else "⚠"} |
| **Active Blockers** | {blockers} | {"✓ OK" if blockers <= 1 else "⚠ Watch"} |
| **Forecast (5 days)** | {week_forecast:.2f}% | {"📈" if week_forecast > current_coverage else "📉"} |

## Coverage Breakdown

### By Module
"""

        if modules:
            for module, coverage in sorted(modules.items(), key=operator.itemgetter(1), reverse=True):
                bar_length = int(coverage / 10)
                bar = "█" * bar_length + "░" * (10 - bar_length)
                snapshot += f"- **{module}** {bar} {coverage:.1f}%\n"
        else:
            snapshot += "- *No module data available*\n"

        # Progress section
        snapshot += """
## Progress Tracking

### 7-Day History
"""

        if history:
            for entry in history[-7:]:
                date_str = entry.get("date", "N/A")
                coverage = entry.get("coverage", 0)
                bar_length = int(coverage / 10)
                bar = "█" * bar_length + "░" * (10 - bar_length)
                snapshot += f"- {date_str}: {bar} {coverage:.1f}%\n"
        else:
            snapshot += "- No history available\n"

        # Alerts section
        snapshot += "\n## Alerts & Recommendations\n\n"

        alerts = []

        # Check for regression
        if len(history) >= 2 and trend["change_percent"] < -1:
            alerts.append(
                f"⚠️ **Regression detected:** Coverage down {abs(trend['change_percent']):.2f}% in last 7 days",
            )

        # Check for stalled progress
        if len(history) >= 3 and all(h["coverage"] == history[0]["coverage"] for h in history):
            alerts.append("⚠️ **No progress:** Coverage flat for 7+ days")

        # Check for blockers
        if blockers > 1:
            alerts.append(f"⚠️ **Multiple blockers:** {blockers} active issues blocking progress")

        # Check if below phase target
        if current_coverage < 25:
            alerts.append("⚠️ **Behind phase target:** Week 1 target is 25%")

        # Positive alerts
        if trend["direction"] == "📈" and trend["change_percent"] > 2:
            alerts.append(f"✓ **Strong progress:** Coverage up {trend['change_percent']:.2f}% this week")

        if not alerts:
            alerts.append("✓ No critical alerts - proceeding normally")

        for alert in alerts:
            snapshot += f"{alert}\n"

        # Forecast section
        snapshot += f"""
## Forecast

**Current Pace:** +{daily_gain:.2f}% per day (if trend continues)

**Projected Coverage:**
- In 5 days: {week_forecast:.2f}%
- In 10 days: {current_coverage + (daily_gain * 10):.2f}%

**Target Path:**
- Week 1 (Day 7): 25% target
- Week 2 (Day 14): 40% target
- Week 4 (Day 28): 60% target
- Week 8 (Day 56): 85%+ target

**On Track?** {"✓ YES" if current_coverage >= 15 and week_forecast > current_coverage else "✗ AT RISK"}

---

*Generated: {datetime.now().isoformat()}*
*For detailed reports, see DAILY_STANDUP_LOG.md and COVERAGE_PROGRESS_DASHBOARD.md*
"""

        return snapshot

    def generate_slack_snapshot(self) -> str:
        """Generate snapshot formatted for Slack."""
        current_coverage = self.extract_current_coverage()
        history = self.extract_metrics_history(days=7)
        blockers = self.count_active_blockers()
        trend = self.calculate_trend(history)
        risk = self.assess_risk(current_coverage, trend, blockers)

        # Format for Slack
        daily_gain = trend["change_percent"] / max(trend["days"], 1) if trend["days"] > 0 else 0
        week_forecast = current_coverage + (daily_gain * 5)

        return f"""*Dashboard Snapshot* - {datetime.now().strftime("%Y-%m-%d %H:%M")}

*Status:* {risk}

*Coverage:*
• Current: {current_coverage:.2f}%
• Trend: {trend["direction"]} {trend["change_percent"]:+.2f}% (7-day)
• Forecast: {week_forecast:.2f}% in 5 days

*Blockers:* {blockers} active {"(⚠️ Watch)" if blockers > 1 else "(✓ OK)"}

*Pace:* +{daily_gain:.2f}% per day

_Detailed: See COVERAGE_PROGRESS_DASHBOARD.md_
"""

    def generate_plain_text_snapshot(self) -> str:
        """Generate snapshot in plain text format."""
        current_coverage = self.extract_current_coverage()
        history = self.extract_metrics_history(days=7)
        blockers = self.count_active_blockers()
        trend = self.calculate_trend(history)
        risk = self.assess_risk(current_coverage, trend, blockers)

        daily_gain = trend["change_percent"] / max(trend["days"], 1) if trend["days"] > 0 else 0

        text = f"""DASHBOARD SNAPSHOT - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{"=" * 70}

STATUS: {risk}

COVERAGE METRICS
  Current Coverage: {current_coverage:.2f}%
  Trend (7-day):    {trend["direction"]} {trend["change_percent"]:+.2f}%
  Daily Pace:       +{daily_gain:.2f}%
  Active Blockers:  {blockers}

PROGRESS
  Tests:     {history[-1].get("tests", 0) if history else 0}
  Status:    {"ON TRACK" if trend["change_percent"] > 0 else "AT RISK"}

RECOMMENDATION
"""

        if blockers > 1:
            text += "  - URGENT: Multiple blockers detected. Escalate!\n"
        if trend["change_percent"] < -1:
            text += "  - WATCH: Coverage regressing. Investigate.\n"
        if current_coverage < 15:
            text += "  - WARN: Behind phase target. Increase velocity.\n"

        if trend["change_percent"] > 2:
            text += "  - GOOD: Strong progress. Maintain pace!\n"

        text += f"\n{'=' * 70}\n"

        return text


def main() -> int:
    """Main execution."""
    parser = argparse.ArgumentParser(description="Generate dashboard snapshot")
    parser.add_argument(
        "--format",
        choices=["markdown", "slack", "text"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument("--output", type=Path, help="Output file (default: create timestamped file)")
    parser.add_argument("--email", help="Email to send snapshot to (requires SMTP setup)")
    parser.add_argument("--print", action="store_true", help="Print to stdout instead of file")

    args = parser.parse_args()

    generator = DashboardSnapshot()

    # Generate snapshot
    if args.format == "slack":
        content = generator.generate_slack_snapshot()
    elif args.format == "text":
        content = generator.generate_plain_text_snapshot()
    else:
        content = generator.generate_markdown_snapshot()

    # Output
    if args.print:
        pass
    else:
        # Determine output file
        if args.output:
            output_file = args.output
        else:
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = ".md" if args.format == "markdown" else ".txt"
            output_file = Path.cwd() / f"DASHBOARD_SNAPSHOT_{date_str}{ext}"

        output_file.write_text(content)

    if args.email:
        pass
        # tracked: https://github.com/KooshaPari/trace/issues/230

    return 0


if __name__ == "__main__":
    sys.exit(main())

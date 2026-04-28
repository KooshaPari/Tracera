#!/usr/bin/env python3
"""Weekly Report Generator.

Compiles standup logs into streamlined weekly summary (15-min format)
Automatically extracts metrics and calculates progress.

Usage:
    python3 scripts/generate_weekly_report.py [week_number]
    python3 scripts/generate_weekly_report.py 1

Output:
    - Appends to DAILY_STANDUP_LOG.md
    - Creates WEEKLY_REPORT_WEEK_N.md
"""

import json
import operator
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class WeeklyReportGenerator:
    """Generate weekly summary from standup logs."""

    def __init__(self, standup_log: Path | None = None, project_dir: Path | None = None) -> None:
        """Initialize."""
        self.project_dir = project_dir or Path.cwd()
        self.standup_log = standup_log or self.project_dir / "DAILY_STANDUP_LOG.md"
        self.dashboard = self.project_dir / "COVERAGE_PROGRESS_DASHBOARD.md"
        self.metrics_dir = self.project_dir / ".coverage_tracking"

    def extract_week_data(self, week_number: int) -> dict[str, Any]:
        """Extract all entries for a specific week from standup log."""
        if not self.standup_log.exists():
            return {}

        content = self.standup_log.read_text()

        # Find week section
        week_pattern = rf"## Week {week_number}\s*[-—].*?\n(.*?)(?=## Week \d+|$)"
        match = re.search(week_pattern, content, re.DOTALL | re.IGNORECASE)

        if not match:
            return {}

        week_content = match.group(1)

        # Extract daily entries
        days = {}
        day_pattern = r"### Day (\d+)\s*\((\w+)\).*?\n(.*?)(?=### Day|\Z)"
        for day_match in re.finditer(day_pattern, week_content, re.DOTALL | re.IGNORECASE):
            day_num = day_match.group(1)
            day_name = day_match.group(2)
            day_data = day_match.group(3)

            days[int(day_num)] = {
                "name": day_name,
                "data": day_data,
                "entries": self._parse_day_entries(day_data),
            }

        return {
            "week_number": week_number,
            "days": days,
            "raw_content": week_content,
        }

    def _parse_day_entries(self, day_content: str) -> list[dict[str, str]]:
        """Parse individual agent entries from a day."""
        entries = []

        # Pattern for agent entries
        agent_pattern = r"#### Agent \d+.*?\n(.*?)(?=#### Agent|###|$)"
        for match in re.finditer(agent_pattern, day_content, re.DOTALL | re.IGNORECASE):
            entry_text = match.group(1)
            entry = {
                "yesterday": self._extract_field(entry_text, "Yesterday"),
                "today": self._extract_field(entry_text, "Today"),
                "progress": self._extract_field(entry_text, "Progress"),
                "blockers": self._extract_field(entry_text, "Blockers"),
                "next": self._extract_field(entry_text, "Next"),
            }
            entries.append(entry)

        return entries

    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract a field from entry text."""
        pattern = rf"\*\*{field_name}:\*?\*?\s*([^\n]*)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def get_coverage_progress(self, _week_number: int) -> dict[str, float]:
        """Extract coverage start and end from metrics."""
        if not self.metrics_dir.exists():
            return {"start": 0.0, "end": 0.0}

        # Get all metrics files for the week
        metrics_files = sorted(self.metrics_dir.glob("metrics_*.json"))
        week_metrics = []

        for mfile in metrics_files:
            # Simple date filtering (assumes YYYYMMDD format)
            date_str = mfile.stem.split("_")[-1]
            # Would need proper date/week calculation here
            # For now, just load files
            try:
                with mfile.open() as f:
                    data = json.load(f)
                    week_metrics.append({
                        "date": data.get("date", date_str),
                        "coverage": data.get("line_coverage", 0),
                    })
            except Exception:
                pass

        if week_metrics:
            return {
                "start": week_metrics[0]["coverage"],
                "end": week_metrics[-1]["coverage"],
            }
        return {"start": 0.0, "end": 0.0}

    def count_blockers_by_category(self, week_data: dict[str, Any]) -> dict[str, int]:
        """Count blockers by category from week data."""
        categories = {}

        # Search all entries for BLOCKER lines
        content = week_data.get("raw_content", "")
        blocker_pattern = r"BLOCKER:\s*([^\n]+).*?- Category:\s*([^\n]+)"
        for match in re.finditer(blocker_pattern, content, re.DOTALL | re.IGNORECASE):
            category = match.group(2).strip()
            categories[category] = categories.get(category, 0) + 1

        return categories

    def calculate_metrics(self, week_data: dict[str, Any]) -> dict[str, Any]:
        """Calculate aggregate metrics for the week."""
        metrics = {
            "total_days": len(week_data.get("days", {})),
            "total_blockers": 0,
            "avg_blocker_duration_hours": 0,
            "agents_contributed": 0,
        }

        # Count unique agents
        agents = set()
        total_blockers = 0

        for _day_num, day_info in week_data.get("days", {}).values():
            for entry in day_info.get("entries", []):
                if entry.get("blockers"):
                    agents.add(f"Agent {len(agents) + 1}")
                    total_blockers += 1

        metrics["total_blockers"] = total_blockers
        metrics["agents_contributed"] = len(agents)

        return metrics

    def generate_report(self, week_number: int) -> str:
        """Generate the weekly report markdown."""
        week_data = self.extract_week_data(week_number)
        if not week_data:
            return ""

        coverage = self.get_coverage_progress(week_number)
        metrics = self.calculate_metrics(week_data)
        blockers_by_category = self.count_blockers_by_category(week_data)

        # Calculate coverage gain
        coverage_gain = coverage["end"] - coverage["start"]
        status = "ON TRACK" if coverage_gain > 0 else "AT RISK"

        report = f"""## Week {week_number} Review - [Week Dates]

### Coverage Progress
```
Start:     {coverage["start"]:.2f}%
End:       {coverage["end"]:.2f}%
Gain:      +{coverage_gain:.2f}%
Status:    {status}
```

### Work Package Status

**Completed This Week:**
- [Auto-populate from standup entries - use progress field]

**In Progress:**
- [Auto-populate from blockers and next field]

**Blockers This Week**

Total Blockers: {metrics["total_blockers"]}

By Category:
"""

        for category, count in sorted(blockers_by_category.items(), key=operator.itemgetter(1), reverse=True):
            report += f"- **{category}:** {count}\n"

        report += f"""

### Team Performance

**Agents Active:** {metrics["agents_contributed"]}
**Days Tracked:** {metrics["total_days"]}

| Metric | Value | Trend |
|--------|-------|-------|
| Coverage Gain | +{coverage_gain:.2f}% | ↗ |
| Tests Added | [Extract from entries] | ↗ |
| Blockers Count | {metrics["total_blockers"]} | → |
| Avg Blocker Duration | [Calculate from entries] | ↙ |

### Next Week Plan

**Expected Coverage Target:** {coverage["end"] + 5:.2f}% (assuming 5% weekly gain)

**Anticipated Challenges:**
- [Based on current blockers]

**Success Metrics:**
- Coverage: {coverage["end"]:.2f}% → {coverage["end"] + 5:.2f}%
- No regressions
- All blockers resolved within SLA

---

*Report generated: {datetime.now(UTC).isoformat()}*
"""

        return report

    def save_report(self, week_number: int, report_content: str) -> Path:
        """Save report to file."""
        output_file = self.project_dir / f"WEEKLY_REPORT_WEEK_{week_number}.md"
        output_file.write_text(report_content)
        return output_file

    def append_to_standup_log(self, week_number: int, report_content: str) -> bool:
        """Append report to standup log."""
        if not self.standup_log.exists():
            return False

        try:
            content = self.standup_log.read_text()

            # Find Week X section and insert report after it
            week_pattern = rf"(## Week {week_number}.*?\n)(.*?)(?=## Week \d+|$)"
            match = re.search(week_pattern, content, re.DOTALL | re.IGNORECASE)

            if match:
                # Insert report at the end of the week section
                insert_pos = match.end()
                content = content[:insert_pos] + "\n" + report_content + content[insert_pos:]
            else:
                # Append at end
                content += "\n" + report_content

            self.standup_log.write_text(content)
            return True

        except Exception:
            return False


def main() -> int:
    """Main execution."""
    if len(sys.argv) < 2:
        return 1

    try:
        week_number = int(sys.argv[1])
    except ValueError:
        return 1

    generator = WeeklyReportGenerator()

    # Generate report
    report = generator.generate_report(week_number)

    if not report:
        return 1

    # Save to file
    generator.save_report(week_number, report)

    # Append to standup log
    if generator.append_to_standup_log(week_number, report):
        pass

    # Print report for verification

    return 0


if __name__ == "__main__":
    sys.exit(main())

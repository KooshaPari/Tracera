#!/usr/bin/env python3
"""Database Slow Query Report Generator.

Connects to PostgreSQL database, analyzes slow queries using pg_stat_statements,
runs EXPLAIN ANALYZE on top queries, and generates a markdown report.

Usage:
    python scripts/db-slow-query-report.py --database-url postgresql://user:pass@localhost/tracertm
    python scripts/db-slow-query-report.py --help
"""

import argparse
import json
import os
import pathlib
import sys
from datetime import datetime
from typing import Any

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    sys.exit(1)


class SlowQueryAnalyzer:
    """SlowQueryAnalyzer."""

    def __init__(self, database_url: str) -> None:
        """Initialize."""
        self.database_url = database_url
        self.conn = None

    def connect(self) -> None:
        """Connect to database."""
        try:
            self.conn = psycopg2.connect(self.database_url)
        except Exception:
            sys.exit(1)

    def disconnect(self) -> None:
        """Disconnect from database."""
        if self.conn:
            self.conn.close()

    def get_slow_queries(self, limit: int = 20) -> list[dict[str, Any]]:
        """Fetch slow queries from pg_stat_statements."""
        query = """
            SELECT
                query,
                calls,
                total_exec_time,
                mean_exec_time,
                max_exec_time,
                stddev_exec_time,
                rows
            FROM pg_stat_statements
            WHERE query NOT LIKE '%pg_stat_statements%'
                AND query NOT LIKE '%pg_catalog%'
                AND mean_exec_time > 1.0
            ORDER BY mean_exec_time DESC
            LIMIT %s
        """

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (limit,))
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception:
            return []

    def explain_query(self, query: str) -> dict[str, Any]:
        """Run EXPLAIN ANALYZE on a query."""
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(explain_query)
                result = cursor.fetchone()[0]
                return result[0] if result else {}
        except Exception:
            return {}

    def analyze_query(self, query_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze a single query and generate suggestions."""
        query = query_data["query"]
        mean_time = float(query_data["mean_exec_time"])
        calls = int(query_data["calls"])

        analysis = {
            "query": query,
            "mean_time_ms": round(mean_time, 2),
            "total_time_ms": round(float(query_data["total_exec_time"]), 2),
            "max_time_ms": round(float(query_data["max_exec_time"]), 2),
            "calls": calls,
            "rows": int(query_data.get("rows", 0)),
            "suggestions": [],
            "severity": "low",
        }

        # Classify severity
        if mean_time > 100:
            analysis["severity"] = "high"
        elif mean_time > 50:
            analysis["severity"] = "medium"

        # Generate suggestions
        if mean_time > 100:
            analysis["suggestions"].append(
                f"⚠️  Very slow query ({mean_time:.2f}ms avg) - immediate optimization needed",
            )

        if calls > 1000 and mean_time > 10:
            analysis["suggestions"].append(f"🔥 Frequently called ({calls:,} times) - high impact optimization target")

        query_lower = query.lower()

        if "select *" in query_lower:
            analysis["suggestions"].append("💡 Avoid SELECT * - specify only needed columns")

        if "where" not in query_lower and "select" in query_lower:
            analysis["suggestions"].append("💡 Add WHERE clause to filter results")

        if "limit" not in query_lower and "select" in query_lower:
            analysis["suggestions"].append("💡 Consider adding LIMIT to reduce result set")

        # Run EXPLAIN ANALYZE
        explain_result = self.explain_query(query)

        if explain_result:
            analysis["explain"] = explain_result
            self._analyze_explain_plan(explain_result, analysis)

        return analysis

    def _analyze_explain_plan(self, plan: dict[str, Any], analysis: dict[str, Any]) -> None:
        """Analyze EXPLAIN plan and add suggestions."""
        plan_text = json.dumps(plan, indent=2).lower()

        if "seq scan" in plan_text:
            analysis["suggestions"].append("📊 Sequential scan detected - consider adding index")

        if "nested loop" in plan_text:
            analysis["suggestions"].append("🔄 Nested loop join - may benefit from hash join for large datasets")

        if "sort" in plan_text and "disk" in plan_text:
            analysis["suggestions"].append("💾 Sort spilling to disk - increase work_mem or optimize query")

    def generate_markdown_report(self, analyses: list[dict[str, Any]]) -> str:
        """Generate markdown report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md = f"""# Database Slow Query Report

**Generated:** {timestamp}
**Database:** {self.database_url.split("@")[1] if "@" in self.database_url else "N/A"}
**Queries Analyzed:** {len(analyses)}

---

## Executive Summary

"""

        # Summary statistics
        high_severity = sum(1 for a in analyses if a["severity"] == "high")
        medium_severity = sum(1 for a in analyses if a["severity"] == "medium")
        total_time = sum(a["total_time_ms"] for a in analyses)

        md += f"""
- **Critical Issues (>100ms):** {high_severity}
- **Medium Issues (50-100ms):** {medium_severity}
- **Total Query Time:** {total_time:,.2f}ms
- **Average Query Time:** {total_time / len(analyses) if analyses else 0:.2f}ms

"""

        # Top 10 slowest queries
        md += "## Top 10 Slowest Queries\n\n"

        for i, analysis in enumerate(analyses[:10], 1):
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(analysis["severity"], "⚪")

            md += f"""### {i}. {severity_icon} Query (Avg: {analysis["mean_time_ms"]}ms)

**Metrics:**
- Mean execution time: {analysis["mean_time_ms"]}ms
- Max execution time: {analysis["max_time_ms"]}ms
- Total execution time: {analysis["total_time_ms"]:,.2f}ms
- Call count: {analysis["calls"]:,}
- Rows returned: {analysis["rows"]:,}

**Query:**
```sql
{analysis["query"][:500]}{"..." if len(analysis["query"]) > 500 else ""}
```

"""

            if analysis["suggestions"]:
                md += "**Optimization Suggestions:**\n"
                for suggestion in analysis["suggestions"]:
                    md += f"- {suggestion}\n"
                md += "\n"

            if "explain" in analysis:
                md += "<details>\n<summary>View EXPLAIN Plan</summary>\n\n```json\n"
                md += json.dumps(analysis["explain"], indent=2)[:1000]
                md += "\n```\n</details>\n\n"

            md += "---\n\n"

        # Recommended Actions
        md += """## Recommended Actions

### Immediate (High Priority)
"""

        high_priority_queries = [a for a in analyses if a["severity"] == "high"]
        if high_priority_queries:
            for i, analysis in enumerate(high_priority_queries[:5], 1):
                md += f"{i}. Optimize query with {analysis['mean_time_ms']}ms avg time ({analysis['calls']:,} calls)\n"
        else:
            md += "✓ No critical performance issues detected\n"

        md += """
### Medium Priority
1. Run `ANALYZE` on frequently queried tables
2. Review and create suggested indexes (see below)
3. Enable query plan caching for prepared statements

### Maintenance
1. Run `VACUUM ANALYZE` on tables with high dead tuple count
2. Monitor replication lag if using read replicas
3. Review materialized view refresh schedule

## Suggested Index Creation

Run the following SQL to identify and create missing indexes:

```sql
-- Find tables with high sequential scans
SELECT
    schemaname,
    tablename,
    seq_scan,
    idx_scan,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_stat_user_tables
WHERE seq_scan > 1000
    AND (idx_scan < seq_scan / 10 OR idx_scan = 0)
ORDER BY seq_scan DESC
LIMIT 10;

-- Auto-generate index creation SQL
SELECT DISTINCT
    'CREATE INDEX CONCURRENTLY idx_' || t.relname || '_' || a.attname ||
    ' ON ' || t.relname || '(' || a.attname || ');' AS create_index_sql
FROM pg_stat_user_tables t
JOIN pg_attribute a ON a.attrelid = t.relid
LEFT JOIN pg_index i ON i.indrelid = t.relid AND a.attnum = ANY(i.indkey)
WHERE i.indrelid IS NULL
    AND a.attnum > 0
    AND NOT a.attisdropped
    AND t.seq_scan > 1000
LIMIT 10;
```

## Monitoring Queries

```sql
-- Check connection pool utilization
SELECT * FROM pg_stat_activity WHERE datname = current_database();

-- Check materialized view freshness
SELECT matviewname, last_refresh FROM pg_matviews;

-- Monitor cache hit ratio
SELECT
    ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) AS cache_hit_ratio
FROM pg_stat_database
WHERE datname = current_database();
```

---

**Next Steps:**
1. Implement suggested index optimizations
2. Optimize top 3 slowest queries
3. Re-run this report in 1 week to measure improvements
4. Set up continuous monitoring with `pg_stat_statements`

*Generated by db-slow-query-report.py*
"""

        return md

    def run_analysis(self, limit: int = 20, output_file: str | None = None) -> None:
        """Run full analysis and generate report."""
        self.connect()

        try:
            # Fetch slow queries
            slow_queries = self.get_slow_queries(limit)

            if not slow_queries:
                return

            # Analyze each query
            analyses = []
            for query_data in slow_queries:
                analysis = self.analyze_query(query_data)
                analyses.append(analysis)

            # Generate report
            report = self.generate_markdown_report(analyses)

            # Save to file
            if output_file:
                pathlib.Path(output_file).write_text(report, encoding="utf-8")
            else:
                # Default location
                report_date = datetime.now().strftime("%Y-%m-%d")
                output_file = f"docs/reports/db-slow-query-report-{report_date}.md"
                pathlib.Path(pathlib.Path(output_file).parent).mkdir(exist_ok=True, parents=True)
                pathlib.Path(output_file).write_text(report, encoding="utf-8")

        finally:
            self.disconnect()


def main() -> None:
    """Main."""
    parser = argparse.ArgumentParser(description="Generate database slow query analysis report")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL"),
        help="PostgreSQL connection URL (default: DATABASE_URL env var)",
    )
    parser.add_argument("--limit", type=int, default=20, help="Number of slow queries to analyze (default: 20)")
    parser.add_argument("--output", help="Output file path (default: docs/reports/db-slow-query-report-{date}.md)")

    args = parser.parse_args()

    if not args.database_url:
        sys.exit(1)

    analyzer = SlowQueryAnalyzer(args.database_url)
    analyzer.run_analysis(limit=args.limit, output_file=args.output)


if __name__ == "__main__":
    main()

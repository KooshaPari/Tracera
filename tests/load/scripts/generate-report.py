#!/usr/bin/env python3
"""Performance Test Report Generator.

Generates HTML report from k6 test results with charts and analysis.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Test Report - {timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; margin-bottom: 10px; }}
        h2 {{ color: #34495e; margin: 30px 0 15px; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        h3 {{ color: #7f8c8d; margin: 20px 0 10px; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}
        .metric-card.success {{ border-left-color: #27ae60; }}
        .metric-card.warning {{ border-left-color: #f39c12; }}
        .metric-card.error {{ border-left-color: #e74c3c; }}
        .metric-label {{
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-sub {{
            font-size: 12px;
            color: #95a5a6;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{
            background: #34495e;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .pass {{ color: #27ae60; font-weight: bold; }}
        .fail {{ color: #e74c3c; font-weight: bold; }}
        .warn {{ color: #f39c12; font-weight: bold; }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        .test-info {{
            background: #e8f5e9;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }}
        .test-info p {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Performance Test Report</h1>
        <p class="timestamp">Generated: {timestamp}</p>

        <div class="test-info">
            <h3>Test Configuration</h3>
            {test_info}
        </div>

        <h2>Executive Summary</h2>
        <div class="summary">
            {summary_cards}
        </div>

        <h2>Detailed Metrics</h2>
        {detailed_metrics}

        <h2>Threshold Analysis</h2>
        {threshold_analysis}

        {custom_metrics}
    </div>
</body>
</html>
"""


def format_duration(ms: float) -> str:
    """Format milliseconds to human-readable duration."""
    if ms < 1000:
        return f"{ms:.2f}ms"
    if ms < 60000:
        return f"{ms / 1000:.2f}s"
    return f"{ms / 60000:.2f}m"


def format_rate(rate: float) -> str:
    """Format rate as percentage."""
    return f"{rate * 100:.2f}%"


def generate_summary_card(label: str, value: str, sub: str = "", card_type: str = "") -> str:
    """Generate HTML for a metric card."""
    return f"""
        <div class="metric-card {card_type}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {f'<div class="metric-sub">{sub}</div>' if sub else ""}
        </div>
    """


def generate_metrics_table(metrics: dict[str, Any]) -> str:
    """Generate HTML table for detailed metrics."""
    rows = []

    for metric_name, metric_data in metrics.items():
        if not isinstance(metric_data, dict):
            continue

        # Format metric values
        values = []
        for key in ["min", "max", "avg", "med", "p90", "p95", "p99"]:
            if key in metric_data:
                val = metric_data[key]
                if "duration" in metric_name or "time" in metric_name:
                    values.append(f"<td>{format_duration(val)}</td>")
                elif "rate" in metric_name or "failed" in metric_name:
                    values.append(f"<td>{format_rate(val)}</td>")
                else:
                    values.append(f"<td>{val:.2f}</td>")
            else:
                values.append("<td>-</td>")

        row = f"""
            <tr>
                <td><strong>{metric_name}</strong></td>
                {"".join(values)}
            </tr>
        """
        rows.append(row)

    return f"""
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Min</th>
                    <th>Max</th>
                    <th>Avg</th>
                    <th>Median</th>
                    <th>P90</th>
                    <th>P95</th>
                    <th>P99</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows)}
            </tbody>
        </table>
    """


def analyze_thresholds(summary: dict[str, Any]) -> str:
    """Analyze threshold pass/fail status."""
    thresholds = summary.get("root_group", {}).get("checks", [])

    if not thresholds:
        return "<p>No threshold checks configured</p>"

    rows = []
    for check in thresholds:
        name = check.get("name", "Unknown")
        passes = check.get("passes", 0)
        fails = check.get("fails", 0)
        total = passes + fails

        if total == 0:
            status = '<span class="warn">SKIPPED</span>'
        elif fails == 0:
            status = '<span class="pass">PASS</span>'
        else:
            status = f'<span class="fail">FAIL ({fails}/{total})</span>'

        rows.append(f"""
            <tr>
                <td>{name}</td>
                <td>{status}</td>
                <td>{passes}</td>
                <td>{fails}</td>
            </tr>
        """)

    return f"""
        <table>
            <thead>
                <tr>
                    <th>Threshold</th>
                    <th>Status</th>
                    <th>Passes</th>
                    <th>Fails</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows)}
            </tbody>
        </table>
    """


def generate_report(results: list[dict[str, Any]], output: Path) -> None:
    """Generate HTML report from test results."""
    # Combine results (in case of multiple test types)
    all_metrics = {}
    test_info_parts = []

    for result in results:
        test_type = result.get("test_type", "Unknown")
        metrics = result.get("metrics", {})
        all_metrics.update(metrics)

        test_info_parts.append(
            f"<p><strong>{test_type}</strong>: {result.get('vus', 'N/A')} VUs, {result.get('duration', 'N/A')}</p>",
        )

    # Generate summary cards
    summary_cards = []

    # Total requests
    http_reqs = all_metrics.get("http_reqs", {})
    summary_cards.append(
        generate_summary_card(
            "Total Requests",
            f"{http_reqs.get('count', 0):,.0f}",
            f"{http_reqs.get('rate', 0):.2f} req/s",
            "success",
        ),
    )

    # P95 latency
    http_duration = all_metrics.get("http_req_duration", {})
    p95_duration = http_duration.get("p95", 0)
    card_type = "success" if p95_duration < 500 else "warning" if p95_duration < 1000 else "error"
    summary_cards.append(
        generate_summary_card(
            "P95 Latency",
            format_duration(p95_duration),
            f"Avg: {format_duration(http_duration.get('avg', 0))}",
            card_type,
        ),
    )

    # Error rate
    http_failed = all_metrics.get("http_req_failed", {})
    error_rate = http_failed.get("rate", 0)
    card_type = "success" if error_rate < 0.01 else "warning" if error_rate < 0.05 else "error"
    summary_cards.append(
        generate_summary_card(
            "Error Rate",
            format_rate(error_rate),
            f"{http_failed.get('fails', 0)} failures",
            card_type,
        ),
    )

    # Generate HTML
    html = HTML_TEMPLATE.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        test_info="".join(test_info_parts),
        summary_cards="".join(summary_cards),
        detailed_metrics=generate_metrics_table(all_metrics),
        threshold_analysis=analyze_thresholds(results[0] if results else {}),
        custom_metrics="",  # Could add custom metrics section
    )

    # Write report
    Path(output).write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate performance test report")
    parser.add_argument("--results-dir", type=Path, required=True, help="Directory containing test results")
    parser.add_argument("--output", type=Path, default=Path("performance-report.html"), help="Output HTML file path")

    args = parser.parse_args()

    # Find all result summary files
    results = []
    for result_file in args.results_dir.rglob("*summary.json"):
        try:
            with Path(result_file).open(encoding="utf-8") as f:
                data = json.load(f)
                results.append(data)
        except Exception:
            pass

    if not results:
        sys.exit(1)

    # Generate report
    generate_report(results, args.output)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate HTML report from k6 load test results."""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def parse_k6_output(file_path: Path) -> dict[str, Any]:
    """Parse k6 JSON output file."""
    metrics = {}
    thresholds = {}

    with file_path.open(encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                metric_type = data.get("type")

                if metric_type == "Metric":
                    metric_name = data["metric"]
                    metric_data = data["data"]

                    if metric_name not in metrics:
                        metrics[metric_name] = []

                    metrics[metric_name].append(metric_data)

                elif metric_type == "Threshold":
                    threshold_name = data["metric"]
                    thresholds[threshold_name] = {
                        "threshold": data.get("threshold"),
                        "passed": data.get("ok", False),
                    }

            except json.JSONDecodeError:
                continue

    return {"metrics": metrics, "thresholds": thresholds}


def aggregate_metrics(metrics: dict[str, list[Any]]) -> dict[str, dict[str, float]]:
    """Aggregate metric values."""
    aggregated = {}

    for metric_name, values in metrics.items():
        if not values:
            continue

        # Get the last value (final aggregated value from k6)
        last_value = values[-1]

        if "value" in last_value:
            aggregated[metric_name] = {
                "value": last_value["value"],
                "type": last_value.get("type", "unknown"),
            }

    return aggregated


def generate_html_report(results_dir: Path) -> None:
    """Generate HTML report from load test results."""
    results = {}

    for file in results_dir.glob("*.json"):
        parsed = parse_k6_output(file)
        aggregated = aggregate_metrics(parsed["metrics"])
        results[file.stem] = {
            "metrics": aggregated,
            "thresholds": parsed["thresholds"],
        }

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Load Test Report - {datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            padding: 10px;
            background-color: #ecf0f1;
            border-left: 5px solid #3498db;
        }}
        .meta {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        .pass {{
            color: #27ae60;
            font-weight: bold;
        }}
        .fail {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .metric-value {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
        }}
        .summary {{
            background-color: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .summary h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <h1>TraceRTM Load Test Results</h1>
    <p class="meta">Generated: {datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}</p>

    <div class="summary">
        <h3>Performance Targets</h3>
        <ul>
            <li><strong>Go API</strong>: &lt;50ms p95 latency, 10,000 req/s throughput</li>
            <li><strong>Python API</strong>: &lt;500ms p95 latency, 1,000 req/s throughput</li>
            <li><strong>WebSocket</strong>: 1,000+ concurrent connections</li>
        </ul>
    </div>
"""

    for test_name, test_data in results.items():
        metrics = test_data["metrics"]
        thresholds = test_data["thresholds"]

        html += f"<h2>{test_name.replace('-', ' ').title()}</h2>"

        # Metrics table
        html += "<h3>Metrics</h3><table>"
        html += "<tr><th>Metric</th><th>Value</th></tr>"

        for metric_name, metric_info in sorted(metrics.items()):
            value = metric_info.get("value", 0)

            # Format value based on metric type
            if "duration" in metric_name or "latency" in metric_name:
                formatted_value = f"{value:.2f} ms"
            elif "rate" in metric_name:
                formatted_value = f"{value:.2f} req/s"
            elif "count" in metric_name or metric_name == "http_reqs":
                formatted_value = f"{int(value)}"
            else:
                formatted_value = f"{value:.2f}"

            html += f"<tr><td>{metric_name}</td><td class='metric-value'>{formatted_value}</td></tr>"

        html += "</table>"

        # Thresholds table
        if thresholds:
            html += "<h3>Thresholds</h3><table>"
            html += "<tr><th>Metric</th><th>Threshold</th><th>Status</th></tr>"

            for threshold_name, threshold_info in sorted(thresholds.items()):
                threshold = threshold_info.get("threshold", "N/A")
                passed = threshold_info.get("passed", False)
                status_class = "pass" if passed else "fail"
                status_text = "PASS" if passed else "FAIL"

                html += f"<tr><td>{threshold_name}</td><td>{threshold}</td>"
                html += f"<td class='{status_class}'>{status_text}</td></tr>"

            html += "</table>"

    html += """
</body>
</html>
"""

    report_path = results_dir / "report.html"
    with report_path.open("w") as f:
        f.write(html)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)

    results_dir = Path(sys.argv[1])
    if not results_dir.exists():
        sys.exit(1)

    generate_html_report(results_dir)

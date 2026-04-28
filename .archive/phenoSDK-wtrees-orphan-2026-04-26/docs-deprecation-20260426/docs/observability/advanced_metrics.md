# Advanced Metrics System

## Overview

The Advanced Metrics System provides comprehensive tracking and observability for all aspects of your application, including token usage, performance, quality, and routing decisions. The system is backend-agnostic and supports integration with popular monitoring platforms like Prometheus, OpenTelemetry, and CloudWatch.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Metric Types](#metric-types)
3. [Collector API](#collector-api)
4. [Backend Integration](#backend-integration)
5. [Anomaly Detection](#anomaly-detection)
6. [Dashboard Setup](#dashboard-setup)
7. [Alerting Configuration](#alerting-configuration)
8. [Query Examples](#query-examples)
9. [Performance Impact](#performance-impact)
10. [FAQ](#faq)

## Quick Start

### Basic Usage

```python
from pheno.observability.metrics import get_metrics_collector

# Get the global metrics collector
collector = get_metrics_collector()

# Record token usage
collector.record_token_usage(
    input_tokens=1500,
    output_tokens=500,
    model="gpt-4",
    savings_tokens=200,  # Tokens saved through optimization
    compression_ratio=0.87  # 87% of original size
)

# Record performance metrics
collector.record_performance(
    latency_ms=250.5,
    success=True,
    throughput_rps=10.5
)

# Record quality metrics
collector.record_quality_metrics(
    quality_score=0.85,
    confidence_score=0.92
)

# Get comprehensive summary
summary = collector.get_summary()
print(f"Token savings: {summary['token_usage']['token_savings_pct']:.1f}%")
print(f"Average latency: {summary['performance']['average_latency_ms']:.1f}ms")
```

### With Alerting and Dashboards

```python
from pheno.observability.metrics import AdvancedMetricsCollector
from pheno.observability.adapters import PrometheusAlerting, GrafanaDashboard

# Create collector with backends
alerting = PrometheusAlerting(endpoint="http://alertmanager:9093")
dashboard = GrafanaDashboard(endpoint="http://grafana:3000")

collector = AdvancedMetricsCollector(
    alerting=alerting,
    dashboard=dashboard
)

# Configure anomaly detection thresholds
collector.configure_thresholds({
    "latency_max_ms": 3000.0,
    "success_rate_min_pct": 95.0,
    "quality_min": 0.7,
})

# Metrics will now trigger alerts and update dashboards automatically
collector.record_performance(latency_ms=5000, success=True)
# -> Triggers high latency alert
```

## Metric Types

### Token Metrics

Track token usage, cost, and savings from optimizations:

```python
class TokenMetrics:
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_cached_tokens: int
    total_savings_tokens: int
    average_compression_ratio: float
    per_model_tokens: dict[str, dict[str, int]]
```

**Key Methods:**
- `calculate_savings(cost_per_1k_tokens)`: Calculate cost savings
- `get_model_breakdown()`: Get per-model token usage

**Example:**
```python
collector.record_token_usage(
    input_tokens=2000,
    output_tokens=800,
    model="claude-3-sonnet",
    cached_tokens=500,
    savings_tokens=300,
    compression_ratio=0.85
)

savings = collector.metrics.token_metrics.calculate_savings(cost_per_1k_tokens=0.015)
print(f"Cost saved: ${savings['total_cost_saved_usd']:.2f}")
print(f"Token savings: {savings['token_savings_pct']:.1f}%")
```

### Quality Metrics

Track accuracy, relevance, and confidence:

```python
class QualityMetrics:
    total_measurements: int
    quality_scores: list[float]
    average_quality: float
    accuracy_scores: list[float]
    relevance_scores: list[float]
    confidence_scores: list[float]
```

**Key Methods:**
- `calculate_improvement(baseline_quality)`: Calculate improvement over baseline

**Example:**
```python
collector.record_quality_metrics(
    quality_score=0.88,
    accuracy_score=0.91,
    relevance_score=0.85,
    confidence_score=0.93
)

improvement = collector.metrics.quality_metrics.calculate_improvement(
    baseline_quality=0.75
)
print(f"Quality improvement: {improvement['quality_improvement_pct']:.1f}%")
```

### Performance Metrics

Track latency, throughput, and success rates:

```python
class PerformanceMetrics:
    total_requests: int
    successful_requests: int
    failed_requests: int
    latencies: list[float]
    throughput_per_second: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
```

**Key Methods:**
- `calculate_improvements(baseline_latency_ms)`: Calculate performance gains

**Example:**
```python
import time

start = time.time()
# ... perform operation ...
latency_ms = (time.time() - start) * 1000

collector.record_performance(
    latency_ms=latency_ms,
    success=True,
    throughput_rps=15.2
)

perf = collector.metrics.performance_metrics.calculate_improvements()
print(f"P95 latency: {perf['p95_latency_ms']:.1f}ms")
print(f"Success rate: {perf['success_rate_pct']:.1f}%")
```

### Routing Metrics

Track routing decisions and effectiveness:

```python
class RoutingMetrics:
    total_routes: int
    successful_routes: int
    fallback_routes: int
    model_selections: dict[str, int]
    method_votes: dict[str, int]
    routing_latencies: list[float]
    average_confidence: float
```

**Key Methods:**
- `get_routing_effectiveness()`: Get routing statistics

**Example:**
```python
collector.record_routing(
    model="gpt-4-turbo",
    confidence=0.89,
    success=True,
    is_fallback=False,
    routing_latency_ms=45.2,
    method_votes={
        "semantic": "gpt-4-turbo",
        "cost": "gpt-3.5-turbo",
        "capability": "gpt-4-turbo"
    }
)

effectiveness = collector.metrics.routing_metrics.get_routing_effectiveness()
print(f"Fallback rate: {effectiveness['fallback_rate_pct']:.1f}%")
print(f"Model distribution: {effectiveness['model_distribution']}")
```

### Custom Metrics

Track domain-specific metrics:

```python
# Register custom handler
def handle_cache_hit(value):
    print(f"Cache hit rate: {value:.1%}")

collector.register_custom_metric_handler("cache_hit_rate", handle_cache_hit)

# Record custom metric
collector.record_custom_metric("cache_hit_rate", 0.75)
collector.record_custom_metric("api_rate_limit_remaining", 9500)

# Access custom metrics
summary = collector.get_summary()
print(summary["custom"]["cache_hit_rate"])
```

## Collector API

### Core Methods

#### `record_token_usage()`
```python
def record_token_usage(
    input_tokens: int,
    output_tokens: int,
    model: str | None = None,
    cached_tokens: int = 0,
    savings_tokens: int = 0,
    compression_ratio: float | None = None,
) -> None
```

Record token usage for a request.

**Parameters:**
- `input_tokens`: Number of tokens in input
- `output_tokens`: Number of tokens in output
- `model`: Model name (optional, for per-model tracking)
- `cached_tokens`: Tokens retrieved from cache
- `savings_tokens`: Tokens saved through optimization
- `compression_ratio`: Compression ratio (0-1)

#### `record_quality_metrics()`
```python
def record_quality_metrics(
    quality_score: float | None = None,
    accuracy_score: float | None = None,
    relevance_score: float | None = None,
    confidence_score: float | None = None,
) -> None
```

Record quality-related metrics.

**Parameters:** All scores should be in range 0-1.

#### `record_performance()`
```python
def record_performance(
    latency_ms: float,
    success: bool,
    throughput_rps: float | None = None,
) -> None
```

Record performance metrics for a request.

#### `record_routing()`
```python
def record_routing(
    model: str,
    confidence: float,
    success: bool,
    is_fallback: bool = False,
    routing_latency_ms: float | None = None,
    method_votes: dict[str, str] | None = None,
) -> None
```

Record routing decision metrics.

### Configuration Methods

#### `configure_thresholds()`
```python
def configure_thresholds(thresholds: dict[str, float]) -> None
```

Configure anomaly detection thresholds.

**Available Thresholds:**
- `token_savings_min_pct`: Minimum token savings percentage
- `compression_ratio_min`: Minimum compression ratio
- `quality_min`: Minimum quality score
- `confidence_min`: Minimum confidence score
- `latency_max_ms`: Maximum acceptable latency
- `success_rate_min_pct`: Minimum success rate

**Example:**
```python
collector.configure_thresholds({
    "latency_max_ms": 2000.0,
    "success_rate_min_pct": 98.0,
    "quality_min": 0.8,
    "compression_ratio_min": 0.6,
})
```

#### `register_custom_metric_handler()`
```python
def register_custom_metric_handler(
    metric_name: str,
    handler: Callable
) -> None
```

Register a handler for custom metric processing.

### Query Methods

#### `get_summary()`
```python
def get_summary() -> dict[str, Any]
```

Get comprehensive summary of all metrics.

**Returns:**
```python
{
    "overview": {
        "uptime_seconds": float,
        "uptime_hours": float,
        "last_updated": str,
    },
    "token_usage": {
        "total_requests": int,
        "token_savings_pct": float,
        "cost_saved_usd": float,
        "model_breakdown": dict[str, dict]
    },
    "quality": {
        "average_quality": float,
        "quality_improvement_pct": float,
        "average_confidence": float
    },
    "performance": {
        "success_rate_pct": float,
        "average_latency_ms": float,
        "p95_latency_ms": float,
        "p99_latency_ms": float
    },
    "routing": {
        "success_rate_pct": float,
        "fallback_rate_pct": float,
        "model_distribution": dict[str, int]
    },
    "custom": dict[str, Any]
}
```

#### `get_alerts()`
```python
def get_alerts(
    since: float | None = None,
    severity: AlertSeverity | None = None,
    limit: int = 100,
) -> list[Alert]
```

Get recent anomaly alerts.

#### `get_dashboard_data()`
```python
async def get_dashboard_data() -> dict[str, Any]
```

Get formatted data for dashboard visualization including trends.

## Backend Integration

### Prometheus Integration

```python
from pheno.observability.adapters.prometheus import (
    PrometheusCollector,
    PrometheusExporter
)

# Create Prometheus collector
prom_collector = PrometheusCollector(
    namespace="myapp",
    subsystem="metrics"
)

# Create metrics collector with Prometheus
collector = AdvancedMetricsCollector()

# Export metrics to Prometheus
exporter = PrometheusExporter(endpoint="http://pushgateway:9091")
metrics = collector.export_metrics()
await exporter.push_to_backend(metrics, endpoint="http://pushgateway:9091/metrics/job/myapp")
```

**Prometheus Query Examples:**
```promql
# Average latency
rate(performance_latency_ms_sum[5m]) / rate(performance_latency_ms_count[5m])

# Token savings rate
rate(token_savings_total[5m]) / rate(token_input_total[5m]) * 100

# Success rate
rate(performance_successful_requests[5m]) / rate(performance_total_requests[5m]) * 100
```

### OpenTelemetry Integration

```python
from pheno.observability.adapters.opentelemetry import OTelCollector
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider

# Setup OpenTelemetry
exporter = OTLPMetricExporter(endpoint="http://otel-collector:4317")
provider = MeterProvider(metric_readers=[PeriodicExportingMetricReader(exporter)])
metrics.set_meter_provider(provider)

# Create collector
otel_collector = OTelCollector(meter=metrics.get_meter(__name__))
collector = AdvancedMetricsCollector()

# Metrics will be exported automatically via OTel
```

### CloudWatch Integration

```python
from pheno.observability.adapters.cloudwatch import CloudWatchCollector
import boto3

# Create CloudWatch client
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

# Create collector
cw_collector = CloudWatchCollector(
    client=cloudwatch,
    namespace="MyApp/Metrics"
)

collector = AdvancedMetricsCollector()

# Export to CloudWatch
metrics = collector.export_metrics()
for metric in metrics:
    cw_collector.put_metric(
        metric_name=metric.name,
        value=metric.value,
        unit="Count",  # or "Milliseconds", "Percent", etc.
        dimensions=[
            {"Name": k, "Value": v}
            for k, v in metric.labels.items()
        ]
    )
```

**CloudWatch Queries:**
```python
# Get average latency
response = cloudwatch.get_metric_statistics(
    Namespace='MyApp/Metrics',
    MetricName='performance.latency.average',
    StartTime=datetime.utcnow() - timedelta(hours=1),
    EndTime=datetime.utcnow(),
    Period=300,
    Statistics=['Average']
)
```

### Custom Backend

Implement the `MetricsExporterPort` protocol:

```python
from pheno.observability.ports import (
    MetricsExporterPort,
    MetricData,
    ExportFormat
)

class CustomExporter:
    """Custom metrics exporter."""

    async def export(
        self,
        metrics: list[MetricData],
        format: ExportFormat,
    ) -> str | bytes:
        """Export metrics in custom format."""
        if format == ExportFormat.JSON:
            return json.dumps([
                {
                    "name": m.name,
                    "value": m.value,
                    "type": m.metric_type.value,
                    "timestamp": m.timestamp,
                    "labels": m.labels
                }
                for m in metrics
            ])
        raise ValueError(f"Unsupported format: {format}")

    def supports_format(self, format: ExportFormat) -> bool:
        """Check format support."""
        return format in [ExportFormat.JSON, ExportFormat.CUSTOM]

    async def push_to_backend(
        self,
        metrics: list[MetricData],
        endpoint: str,
    ) -> bool:
        """Push to custom backend."""
        data = await self.export(metrics, ExportFormat.JSON)
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, data=data) as resp:
                return resp.status == 200
```

## Anomaly Detection

### Threshold-Based Detection

The system automatically detects anomalies based on configured thresholds:

```python
collector.configure_thresholds({
    "latency_max_ms": 3000.0,        # Alert if latency > 3s
    "success_rate_min_pct": 95.0,    # Alert if success rate < 95%
    "quality_min": 0.7,              # Alert if quality < 0.7
    "confidence_min": 0.6,           # Alert if confidence < 0.6
    "compression_ratio_min": 0.5,    # Alert if compression < 50%
})

# Anomalies are detected automatically
collector.record_performance(latency_ms=5000, success=True)
# -> Triggers "high_latency" alert

# Get alerts
alerts = collector.get_alerts(severity=AlertSeverity.WARNING)
for alert in alerts:
    print(f"{alert.severity.value}: {alert.message}")
```

### Statistical Anomaly Detection

For advanced anomaly detection, implement the `AnomalyDetectorPort`:

```python
from pheno.observability.ports import AnomalyDetectorPort
from sklearn.ensemble import IsolationForest
import numpy as np

class MLAnomalyDetector:
    """ML-based anomaly detector."""

    def __init__(self):
        self.models = {}

    def train_model(
        self,
        metric_name: str,
        historical_data: list[MetricData],
    ) -> None:
        """Train anomaly detection model."""
        values = np.array([m.value for m in historical_data]).reshape(-1, 1)
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(values)
        self.models[metric_name] = model

    async def detect_anomalies(
        self,
        metrics: list[MetricData],
    ) -> list[Alert]:
        """Detect anomalies using trained models."""
        alerts = []

        for metric in metrics:
            if metric.name in self.models:
                model = self.models[metric.name]
                prediction = model.predict([[metric.value]])

                if prediction[0] == -1:  # Anomaly detected
                    alerts.append(Alert(
                        alert_type="ml_anomaly",
                        severity=AlertSeverity.WARNING,
                        message=f"Anomaly detected in {metric.name}: {metric.value}",
                        timestamp=metric.timestamp,
                        source="MLAnomalyDetector",
                        metadata={"metric": metric.name, "value": metric.value}
                    ))

        return alerts
```

### Tuning Anomaly Detection

**Best Practices:**

1. **Start with conservative thresholds**: Begin with loose thresholds and tighten based on false positive rate
2. **Monitor alert frequency**: Too many alerts indicate thresholds are too strict
3. **Use percentile-based thresholds**: Better for metrics with variable distributions
4. **Consider time-of-day patterns**: Different thresholds for peak vs. off-peak hours
5. **Implement alert fatigue prevention**: Deduplicate and rate-limit similar alerts

```python
# Example: Dynamic threshold based on historical data
historical_latencies = collector.metrics.performance_metrics.latencies[-1000:]
if historical_latencies:
    p95_latency = np.percentile(historical_latencies, 95)
    p99_latency = np.percentile(historical_latencies, 99)

    # Set threshold at 1.5x p99
    collector.configure_thresholds({
        "latency_max_ms": p99_latency * 1.5
    })
```

## Dashboard Setup

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Advanced Metrics Dashboard",
    "panels": [
      {
        "title": "Token Savings",
        "targets": [
          {
            "expr": "rate(token_savings_total[5m]) / rate(token_input_total[5m]) * 100"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Latency Percentiles",
        "targets": [
          {"expr": "histogram_quantile(0.50, rate(performance_latency_ms_bucket[5m]))"},
          {"expr": "histogram_quantile(0.95, rate(performance_latency_ms_bucket[5m]))"},
          {"expr": "histogram_quantile(0.99, rate(performance_latency_ms_bucket[5m]))"}
        ],
        "type": "graph"
      },
      {
        "title": "Model Distribution",
        "targets": [
          {"expr": "rate(routing_model_selections[5m])"}
        ],
        "type": "piechart"
      },
      {
        "title": "Quality Score",
        "targets": [
          {"expr": "quality_average"}
        ],
        "type": "gauge"
      }
    ]
  }
}
```

### Programmatic Dashboard Generation

```python
from pheno.observability.ports import DashboardConfig, DashboardPort

class GrafanaDashboard:
    """Grafana dashboard generator."""

    async def generate_dashboard(
        self,
        config: DashboardConfig,
    ) -> dict[str, Any]:
        """Generate Grafana dashboard JSON."""
        panels = []

        for i, metric in enumerate(config.metrics):
            panel = {
                "id": i + 1,
                "title": metric.replace("_", " ").title(),
                "targets": [{"expr": f"{metric}_average"}],
                "type": "graph",
                "gridPos": {"x": 0, "y": i * 8, "w": 12, "h": 8}
            }
            panels.append(panel)

        return {
            "dashboard": {
                "title": config.name,
                "refresh": f"{config.refresh_interval_seconds}s",
                "panels": panels
            }
        }

    def add_panel(self, dashboard_name: str, panel_name: str,
                  metrics: list[str], visualization_type: str = "timeseries") -> None:
        """Add panel to existing dashboard."""
        # Implementation
        pass

# Use with collector
dashboard = GrafanaDashboard()
collector = AdvancedMetricsCollector(dashboard=dashboard)

# Get dashboard data
data = await collector.get_dashboard_data()
```

## Alerting Configuration

### Email Alerts

```python
from pheno.observability.adapters.email import EmailAlerting
import smtplib

alerting = EmailAlerting(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    username="alerts@example.com",
    password="app_password",
    recipients=["ops@example.com", "dev@example.com"]
)

collector = AdvancedMetricsCollector(alerting=alerting)

# Alerts will be sent via email automatically
```

### Slack Alerts

```python
from pheno.observability.adapters.slack import SlackAlerting

alerting = SlackAlerting(
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    channel="#alerts",
    username="Metrics Bot"
)

collector = AdvancedMetricsCollector(alerting=alerting)
```

### PagerDuty Integration

```python
from pheno.observability.adapters.pagerduty import PagerDutyAlerting

alerting = PagerDutyAlerting(
    integration_key="YOUR_INTEGRATION_KEY",
    severity_mapping={
        AlertSeverity.CRITICAL: "critical",
        AlertSeverity.ERROR: "error",
        AlertSeverity.WARNING: "warning",
    }
)

collector = AdvancedMetricsCollector(alerting=alerting)
```

### Custom Alerting

```python
from pheno.observability.ports import AlertingPort, Alert, AlertSeverity

class CustomAlerting:
    """Custom alerting implementation."""

    def __init__(self):
        self.rules = {}
        self.active_alerts = []

    def configure_rule(
        self,
        rule_name: str,
        condition: str,
        severity: AlertSeverity,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Configure alerting rule."""
        self.rules[rule_name] = {
            "condition": condition,
            "severity": severity,
            "metadata": metadata or {}
        }

    async def evaluate_rules(
        self,
        metrics: list[MetricData],
    ) -> list[Alert]:
        """Evaluate rules against metrics."""
        alerts = []

        for rule_name, rule in self.rules.items():
            # Evaluate condition
            # This is a simple example; real implementation would be more sophisticated
            for metric in metrics:
                if eval(rule["condition"], {"value": metric.value}):
                    alert = Alert(
                        alert_type=rule_name,
                        severity=rule["severity"],
                        message=f"Rule '{rule_name}' triggered for {metric.name}",
                        timestamp=time.time(),
                        metadata={"metric": metric.name, "value": metric.value}
                    )
                    alerts.append(alert)

        return alerts

    async def send_alert(
        self,
        alert: Alert,
        channels: list[str] | None = None,
    ) -> bool:
        """Send alert to channels."""
        # Custom implementation
        print(f"[{alert.severity.value.upper()}] {alert.message}")
        return True

    def get_active_alerts(self) -> list[Alert]:
        """Get active alerts."""
        return self.active_alerts
```

## Query Examples

### Python API Queries

```python
# Get metrics summary
summary = collector.get_summary()

# Filter by time range
one_hour_ago = time.time() - 3600
recent_alerts = collector.get_alerts(since=one_hour_ago)

# Filter by severity
critical_alerts = collector.get_alerts(severity=AlertSeverity.CRITICAL)

# Get specific metric breakdown
token_breakdown = collector.metrics.token_metrics.get_model_breakdown()
for model, tokens in token_breakdown.items():
    print(f"{model}: {tokens['input']} input, {tokens['output']} output")

# Calculate custom statistics
latencies = collector.metrics.performance_metrics.latencies
if latencies:
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    min_latency = min(latencies)
    print(f"Latency: avg={avg_latency:.1f}ms, min={min_latency:.1f}ms, max={max_latency:.1f}ms")
```

### Export for Analysis

```python
import pandas as pd
import json

# Export to JSON
summary = collector.get_summary()
with open("metrics_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

# Export to DataFrame for analysis
data = {
    "timestamp": [time.time()] * len(collector.metrics.performance_metrics.latencies),
    "latency_ms": collector.metrics.performance_metrics.latencies,
}
df = pd.DataFrame(data)
df.to_csv("latency_data.csv", index=False)

# Export all metrics
metrics = collector.export_metrics()
metrics_df = pd.DataFrame([
    {
        "name": m.name,
        "value": m.value,
        "type": m.metric_type.value,
        "timestamp": m.timestamp,
        **m.labels
    }
    for m in metrics
])
metrics_df.to_csv("all_metrics.csv", index=False)
```

## Performance Impact

### Overhead Analysis

The metrics system is designed to have minimal overhead:

| Operation | Overhead | Notes |
|-----------|----------|-------|
| `record_token_usage()` | ~0.01ms | Simple counter updates |
| `record_performance()` | ~0.02ms | Includes percentile calculation |
| `record_quality_metrics()` | ~0.01ms | Simple aggregation |
| `record_routing()` | ~0.02ms | Dictionary updates |
| `get_summary()` | ~0.5ms | Calculates all statistics |
| `get_alerts()` | ~0.1ms | List filtering |
| `export_metrics()` | ~1ms | Formats all metrics |

### Optimization Tips

1. **Batch metric recording**: Record multiple metrics at once when possible
2. **Async exports**: Use async methods for backend exports
3. **Sampling**: For very high-throughput systems, sample metrics
4. **Periodic summaries**: Cache summary calculations

```python
# Example: Sampling for high-throughput
import random

class SamplingCollector:
    def __init__(self, collector, sample_rate=0.1):
        self.collector = collector
        self.sample_rate = sample_rate

    def record_performance(self, *args, **kwargs):
        if random.random() < self.sample_rate:
            self.collector.record_performance(*args, **kwargs)

# Use sampled collector for high-volume metrics
sampled = SamplingCollector(collector, sample_rate=0.01)  # 1% sampling
```

### Memory Usage

- **Base overhead**: ~1-2 MB
- **Per-metric storage**: ~100 bytes
- **History retention**: Configurable (default 1000 data points per metric)

```python
# Control memory usage
class MemoryEfficientCollector(AdvancedMetricsCollector):
    def __init__(self, max_history=500, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_history = max_history

    def _trim_history(self):
        """Trim old data points."""
        tm = self.metrics.token_metrics
        if len(tm.compression_ratios) > self.max_history:
            tm.compression_ratios = tm.compression_ratios[-self.max_history:]

        pm = self.metrics.performance_metrics
        if len(pm.latencies) > self.max_history:
            pm.latencies = pm.latencies[-self.max_history:]
```

## FAQ

### 1. How do I integrate metrics with my existing monitoring system?

Implement the appropriate port interface (`MetricsExporterPort` or `AlertingPort`) for your backend. See [Backend Integration](#backend-integration) for examples.

### 2. Can I use multiple backends simultaneously?

Yes! Create multiple exporters and call them separately:

```python
prometheus_exporter = PrometheusExporter()
cloudwatch_exporter = CloudWatchExporter()

metrics = collector.export_metrics()
await prometheus_exporter.push_to_backend(metrics, prom_endpoint)
await cloudwatch_exporter.push_to_backend(metrics, cw_endpoint)
```

### 3. How do I reset metrics for a new measurement period?

```python
collector.reset_metrics()
```

For testing, use `reset_metrics_collector()` to create a fresh singleton.

### 4. What's the difference between quality_score and confidence_score?

- **quality_score**: Actual quality of output (accuracy, correctness)
- **confidence_score**: System's confidence in its decision/output

### 5. How do I track metrics per user or tenant?

Use labels when recording metrics:

```python
collector.record_performance(
    latency_ms=250,
    success=True,
    metadata={"user_id": "user123", "tenant": "acme_corp"}
)
```

Then export with labels:

```python
metrics = collector.export_metrics()
for metric in metrics:
    metric.labels["user_id"] = current_user_id
```

### 6. Can I use this with FastAPI/Flask?

Yes! Use middleware to automatically track metrics:

```python
# FastAPI example
from fastapi import FastAPI, Request
import time

app = FastAPI()
collector = get_metrics_collector()

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency_ms = (time.time() - start_time) * 1000

    collector.record_performance(
        latency_ms=latency_ms,
        success=response.status_code < 400
    )

    return response
```

### 7. How do I aggregate metrics across multiple instances?

Use a centralized backend (Prometheus, CloudWatch) and push metrics from all instances:

```python
# On each instance
collector = get_metrics_collector()
metrics = collector.export_metrics()

# Add instance label
for metric in metrics:
    metric.labels["instance"] = socket.gethostname()

# Push to central backend
await exporter.push_to_backend(metrics, central_endpoint)
```

### 8. What's the recommended alert threshold for production?

Start with these conservative values and adjust:

```python
collector.configure_thresholds({
    "latency_max_ms": 5000.0,        # 5 seconds
    "success_rate_min_pct": 90.0,    # 90%
    "quality_min": 0.6,              # 60%
    "confidence_min": 0.5,           # 50%
})
```

### 9. How do I export metrics for offline analysis?

```python
import json

# Export complete state
summary = collector.get_summary()
with open("metrics.json", "w") as f:
    json.dump(summary, f, indent=2)

# Export raw data
data = {
    "latencies": collector.metrics.performance_metrics.latencies,
    "quality_scores": collector.metrics.quality_metrics.quality_scores,
    "compression_ratios": collector.metrics.token_metrics.compression_ratios,
}
with open("raw_metrics.json", "w") as f:
    json.dump(data, f)
```

### 10. Can I use this for A/B testing?

Yes! Track metrics with experiment labels:

```python
# In experiment A
collector.record_performance(
    latency_ms=latency,
    success=True,
    metadata={"experiment": "A", "variant": "baseline"}
)

# In experiment B
collector.record_performance(
    latency_ms=latency,
    success=True,
    metadata={"experiment": "A", "variant": "optimized"}
)

# Analyze results
summary = collector.get_summary()
# Compare metrics by experiment variant
```

## Related Documentation

- [Observability Overview](./overview.md)
- [Logging Guide](./logging.md)
- [Tracing with OpenTelemetry](./tracing.md)
- [Health Checks](./health.md)
- [Monitoring Best Practices](./best_practices.md)

## Support

For questions or issues:
- GitHub Issues: [pheno-sdk/issues](https://github.com/your-org/pheno-sdk/issues)
- Documentation: [https://docs.pheno.dev](https://docs.pheno.dev)
- Community: [Discord](https://discord.gg/pheno)

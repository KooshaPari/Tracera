# Metrics Cookbook

Common patterns for HTTP services using observability_kit.metrics and exporters.

## Setup
```python
import os

from observability_kit.metrics.collector import MetricsCollector
from observability_kit.exporters import make_protected_metrics_app_from_collector
from fastapi import FastAPI

metrics = MetricsCollector()
app = FastAPI()
app.mount(
    "/metrics",
    make_protected_metrics_app_from_collector(
        metrics,
        bearer_token=os.environ["METRICS_BEARER_TOKEN"],
    ),
)
```

## HTTP Latency Histogram
```python
http_latency = metrics.histogram(
    "http_request_duration_seconds",
    description="HTTP request duration",
    labels=["method","route","status"],
    buckets=[0.05,0.1,0.25,0.5,1.0,2.5,5.0]
)

# Example usage in middleware/endpoint
# http_latency.observe(duration_seconds, {"method": method, "route": route, "status": str(status_code)})
```

## Throughput Counter
```python
http_requests_total = metrics.counter(
    "http_requests_total",
    description="HTTP requests",
    labels=["method","route","status"]
)

# http_requests_total.inc({"method": method, "route": route, "status": str(status_code)})
```

## Error Rate Counter
```python
http_errors_total = metrics.counter(
    "http_errors_total",
    description="HTTP error responses",
    labels=["method","route","status"]
)

# if status_code >= 500: http_errors_total.inc({"method": method, "route": route, "status": str(status_code)})
```

## Summary with Streaming Quantiles
```python
payload_size = metrics.summary(
    "http_response_size_bytes",
    description="HTTP response size",
    labels=["route"],
    quantiles=[0.5,0.9,0.99]
)
# Optional tighter error bound (more CPU/memory):
payload_size.epsilon = 0.005

# payload_size.observe(size_bytes, {"route": route})
```

## Notes
- Histograms are exported with cumulative buckets, plus _sum and _count
- Summaries use a GK/CKMS streaming estimator; rank error bounded by epsilon
- OpenMetrics is supported via PrometheusExporter(..., export_format="openmetrics")



## Decorators (MetricsCollector)
```python
from observability_kit.metrics.collector import MetricsCollector
from observability_kit.metrics.collector_decorators import (
    count_calls_collector, track_duration_collector
)

metrics = MetricsCollector()

@count_calls_collector(metrics, "pipeline_runs_total", labels=["stage"])  # labels from kwargs
@track_duration_collector(metrics, "pipeline_duration_seconds", labels=["stage"], buckets=[0.1,0.5,1.0])
def run_stage(stage: str):
    ...

run_stage(stage="ingest")
```

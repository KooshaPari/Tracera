"""Prometheus metrics."""
from prometheus_client import Counter, Histogram, Gauge, REGISTRY

# HTTP metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

http_request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
)

# Database metrics
db_operations_total = Counter(
    "db_operations_total",
    "Total database operations",
    ["operation", "status"],
)

# Business metrics
entities_total = Gauge(
    "entities_total",
    "Total number of entities",
)

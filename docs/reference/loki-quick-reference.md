# Loki Log Aggregation - Quick Reference

## Overview

Grafana Loki is integrated into TraceRTM for centralized log aggregation and analysis. Grafana Alloy collects logs from local services and ships them to Loki for search in Grafana.

## Services

- **Loki**: Log aggregation system (port 3100)
- **Grafana Alloy**: Log collector that ships logs to Loki (port 12345)
- **Grafana**: UI for querying and visualizing logs (port 3000)

## Quick Start

### 1. Install Dependencies

```bash
# macOS
brew install grafana/grafana/loki
brew install grafana-alloy

# If alloy-analyzer owns the alloy command, install the official release binary
# as grafana-alloy and export its path:
export GRAFANA_ALLOY_BIN="$HOME/.local/bin/grafana-alloy"

# Or check installation status
./scripts/check-loki-installation.sh
```

### 2. Start Services

```bash
make dev
```

All services (Loki, Alloy, Grafana) start automatically.

### 3. Access Grafana

1. Open http://localhost:3000
2. Login: `admin` / `admin`
3. Navigate to **Explore** (compass icon in sidebar)
4. Select **Loki** as the data source

## Log Sources

Alloy automatically collects logs from:

| Source | Path | Labels |
|--------|------|--------|
| Python Backend (JSON) | `.data/logs/tracertm.json` | `job=python-backend`, `service=tracertm-python` |
| Python Backend (Text) | `.data/logs/tracertm.log` | `job=python-backend-text` |
| Python Errors | `.data/logs/tracertm_errors.log` | `job=python-backend-errors`, `level=ERROR` |
| Process Compose | `.process-compose/logs/*.log` | `job=process-compose` |
| Go Backend | `backend/logs/*.log` | `job=go-backend`, `service=tracertm-go` |
| Temporal | `.temporal/logs/*.log` | `job=temporal`, `service=temporal` |

## Basic LogQL Queries

### View all logs
```logql
{job="python-backend"}
```

### Filter by level
```logql
{job="python-backend"} | json | level="ERROR"
```

### Search for text
```logql
{job="python-backend"} |= "user_login"
```

### Multiple conditions
```logql
{job="python-backend"} | json | level="INFO" | event="request_completed"
```

### Exclude text
```logql
{job="python-backend"} != "health"
```

## Common Queries

### Find errors for a specific user
```logql
{job="python-backend"} |= `user_id="123"` | json | level="ERROR"
```

### Slow API requests (>1 second)
```logql
{job="python-backend"}
  | json
  | event="request_completed"
  | duration_ms > 1000
```

### Database errors
```logql
{job="python-backend"}
  | json
  | event=~"db_.*"
  | level="ERROR"
```

### Count requests by endpoint
```logql
sum by (path) (
  count_over_time({job="python-backend"} | json | event="request_completed" [5m])
)
```

### 95th percentile response time
```logql
quantile_over_time(0.95,
  {job="python-backend"}
    | json
    | event="request_completed"
    | unwrap duration_ms [5m]
) by (path)
```

## Structured Logging

### Python (structlog)

```python
from tracertm.logging_config import get_structlog_logger

logger = get_structlog_logger(__name__)

# Log with context
logger.info(
    "user_login",
    user_id=user.id,
    username=user.email,
    ip=request.client.host
)
```

See [Structured Logging Guide](../guides/structured-logging-guide.md) for more details.

## Configuration

### Loki Configuration
- **File**: `monitoring/loki-local-config.yaml`
- **Storage**: `.loki/` directory
- **Retention**: 7 days (168h)
- **Port**: 3100

### Alloy Configuration
- **File**: `deploy/monitoring/alloy-local.alloy`
- **Storage**: `.alloy/data`
- **HTTP health/metrics port**: 12345
- **Repo-local OTLP gRPC receiver**: 4319
- **Shared org OTLP gRPC endpoint**: `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT` / `127.0.0.1:4317`

### Grafana Data Source
- **File**: `monitoring/grafana/provisioning/datasources/loki.yml`
- **Auto-provisioned** on Grafana startup

## Log Retention

| Log Type | Retention |
|----------|-----------|
| Loki (all logs) | 7 days |
| Python errors (file) | 30 days |
| Other logs (file) | 7 days |

Retention is enforced by:
- Loki compactor (automatic cleanup)
- Loguru file rotation (compression after 500MB)

## Troubleshooting

### Loki not starting
```bash
# Check if port 3100 is in use
lsof -i :3100

# Check Loki logs
cat .process-compose/logs/loki.log
```

### Alloy not collecting logs
```bash
# Check Alloy logs
cat .process-compose/logs/alloy.log

# Verify log files exist
ls -la .data/logs/

# Check Alloy health
curl http://localhost:12345/-/healthy
```

### No logs in Grafana
1. Check Loki data source: Configuration → Data Sources → Loki
2. Verify Alloy is running: `lsof -i :12345`
3. Check log file paths in `deploy/monitoring/alloy-local.alloy`
4. Verify structured logs are being written: `tail -f .data/logs/tracertm.json`

### Query too slow
- Add more specific filters: `{job="python-backend", level="ERROR"}`
- Reduce time range (use last 15m instead of last 24h)
- Use indexed labels instead of filtering on JSON fields

## Performance Tips

1. **Use label filters first**: `{job="python-backend"}` before `| json`
2. **Limit time range**: Query last 1h instead of last 7d
3. **Index common fields**: Add them as labels in Alloy config
4. **Aggregate in Loki**: Use `count_over_time()` instead of counting in browser

## Integration with Tracing

Loki can link to traces when logs include `trace_id`:

```python
from opentelemetry import trace

span = trace.get_current_span()
trace_id = format(span.get_span_context().trace_id, '032x')

logger.info("operation_completed", trace_id=trace_id, ...)
```

Click the TraceID link in Grafana to jump to the corresponding trace in Tempo.

## Useful Links

- **Grafana Explore**: http://localhost:3000/explore
- **Loki API**: http://localhost:3100
- **Alloy Metrics**: http://localhost:12345/metrics
- **Shared OTLP gRPC**: 127.0.0.1:4317
- **LogQL Documentation**: https://grafana.com/docs/loki/latest/logql/

## See Also

- [Structured Logging Guide](../guides/structured-logging-guide.md)
- [Prometheus Quick Reference](prometheus-quick-reference.md)
- [OpenTelemetry Quick Reference](OTEL_QUICK_REFERENCE.md)

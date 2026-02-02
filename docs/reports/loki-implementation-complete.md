# Loki Log Aggregation - Implementation Complete

## Overview

Log aggregation with Grafana Loki has been successfully implemented in TraceRTM. The system now provides centralized log collection, structured logging, and powerful log querying capabilities.

## Implementation Summary

### 1. Services Added

#### Loki (Log Aggregation System)
- **Port**: 3100
- **Config**: `monitoring/loki-local-config.yaml`
- **Storage**: `.loki/` directory (gitignored)
- **Retention**: 7 days (168h)
- **Wrapper Script**: `scripts/loki-if-not-running.sh`

**Features:**
- TSDB storage backend for efficient log indexing
- Automatic compaction and retention management
- Built-in retention policies
- HTTP and gRPC APIs

#### Promtail (Log Collector)
- **Port**: 9080
- **Config**: `monitoring/promtail-local-config.yaml`
- **Storage**: `.promtail/positions.yaml` (tracks read positions)
- **Wrapper Script**: `scripts/promtail-if-not-running.sh`

**Features:**
- Automatic log discovery and collection
- Pipeline stages for log parsing and labeling
- Multiple log source support
- JSON and text log parsing

### 2. Process Compose Integration

Added to `process-compose.yaml`:

```yaml
loki:
  command: "bash scripts/loki-if-not-running.sh"
  port: 3100
  health_check: /ready

promtail:
  command: "bash scripts/promtail-if-not-running.sh"
  port: 9080
  depends_on: loki
  health_check: /ready
```

Services start automatically with `make dev` or `make dev-tui`.

### 3. Grafana Integration

#### Data Source Configuration
- **File**: `monitoring/grafana/provisioning/datasources/loki.yml`
- **Auto-provisioned**: Loki data source added automatically on Grafana startup
- **Features**:
  - LogQL query support
  - Trace ID extraction for Jaeger correlation
  - Max 1000 lines per query

#### Dashboard
- **File**: `monitoring/dashboards/logs-dashboard.json`
- **Panels**:
  - Application Logs (live tail)
  - Log Volume by Level (time series)
  - Error Logs (filtered view)
  - P95 Response Time (gauge)
  - Requests by Endpoint (pie chart)

#### Grafana Configuration Update
- Updated `monitoring/grafana.ini` to use new provisioning paths
- Datasources: `monitoring/grafana/provisioning/datasources/`
- Dashboards: `monitoring/grafana/provisioning/dashboards/`

### 4. Structured Logging (Python Backend)

#### Updated Logging Configuration
- **File**: `src/tracertm/logging_config.py`
- **Added**: `structlog` support alongside existing Loguru
- **Format**: JSON with ISO 8601 timestamps

**Configuration:**
```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
```

#### Helper Functions
```python
def get_structlog_logger(name: str = None):
    """Get a structlog logger for structured logging."""
    return structlog.get_logger(name)
```

#### Usage Example
```python
from tracertm.logging_config import get_structlog_logger

logger = get_structlog_logger(__name__)
logger.info(
    "user_login",
    user_id=user.id,
    username=user.email,
    ip=request.client.host
)
```

### 5. Log Sources Configured

Promtail collects logs from:

| Source | Path | Labels | Format |
|--------|------|--------|--------|
| Python Backend (JSON) | `.data/logs/tracertm.json` | `job=python-backend` | JSON |
| Python Backend (Text) | `.data/logs/tracertm.log` | `job=python-backend-text` | Plain text |
| Python Errors | `.data/logs/tracertm_errors.log` | `job=python-backend-errors`, `level=ERROR` | Plain text |
| Process Compose | `.process-compose/logs/*.log` | `job=process-compose` | Plain text |
| Go Backend | `backend/logs/*.log` | `job=go-backend` | JSON |
| Temporal | `.temporal/logs/*.log` | `job=temporal` | Plain text |

### 6. Log Retention Policies

| Log Type | Retention | Compression | Cleanup |
|----------|-----------|-------------|---------|
| Loki (all logs) | 7 days | None | Automatic (compactor) |
| Python JSON logs | 7 days | ZIP | Automatic (rotation) |
| Python text logs | 7 days | ZIP | Automatic (rotation) |
| Python errors | 30 days | ZIP | Automatic (rotation) |

**Retention Configuration:**
- **Loki**: `limits_config.retention_period: 168h` in `loki-local-config.yaml`
- **Loguru**: `retention="7 days"` in `logging_config.py`
- **Error logs**: `retention="30 days"` for errors

### 7. Installation & Setup Scripts

#### Check Installation Script
- **File**: `scripts/check-loki-installation.sh`
- **Purpose**: Verify Loki and Promtail are installed
- **Usage**: `./scripts/check-loki-installation.sh`

**Provides installation instructions for:**
- macOS (Homebrew)
- Linux (binary downloads)

#### Wrapper Scripts
- `scripts/loki-if-not-running.sh` - Prevents duplicate Loki instances
- `scripts/promtail-if-not-running.sh` - Prevents duplicate Promtail instances

### 8. Documentation Created

#### Guides
1. **Structured Logging Guide** (`docs/guides/structured-logging-guide.md`)
   - Quick start examples
   - Best practices
   - Common patterns (API requests, DB queries, background jobs)
   - LogQL query examples
   - Migration from Loguru to structlog

2. **Adding Structured Logging Example** (`docs/guides/adding-structured-logging-example.md`)
   - Before/after code examples
   - Real-world patterns
   - Testing structured logs
   - Migration strategies

#### Quick References
1. **Loki Quick Reference** (`docs/reference/loki-quick-reference.md`)
   - Installation instructions
   - Basic LogQL queries
   - Common query patterns
   - Configuration details
   - Troubleshooting guide
   - Integration with tracing

#### Reports
1. **This Document** (`docs/reports/loki-implementation-complete.md`)
   - Complete implementation summary
   - All changes documented
   - Configuration details
   - Next steps

### 9. Configuration Files

#### Loki Configuration
**File**: `monitoring/loki-local-config.yaml`

**Key Settings:**
- HTTP port: 3100
- gRPC port: 9096
- Storage: `.loki/` (filesystem)
- Schema: v13 (TSDB)
- Retention: 7 days
- Compaction: 10-minute intervals
- Analytics: disabled

#### Promtail Configuration
**File**: `monitoring/promtail-local-config.yaml`

**Key Settings:**
- HTTP port: 9080
- Loki endpoint: http://localhost:3100
- Position file: `.promtail/positions.yaml`
- 6 scrape configs (Python, Go, Process Compose, Temporal)

**Pipeline Stages:**
- JSON parsing for structured logs
- Regex parsing for text logs
- Label extraction
- Timestamp parsing

### 10. .gitignore Updates

Added to `.gitignore`:
```
.loki/
.promtail/
```

Prevents committing:
- Loki storage data
- Promtail position tracking
- Generated logs

## Integration Points

### 1. Prometheus Integration
- Loki metrics exposed at http://localhost:3100/metrics
- Promtail metrics exposed at http://localhost:9080/metrics
- Both scraped by Prometheus

### 2. Grafana Integration
- Loki data source auto-provisioned
- Logs dashboard auto-loaded
- Explore view for ad-hoc queries

### 3. Jaeger Integration
- Trace ID extraction in Loki datasource
- Click trace IDs in logs to jump to Jaeger
- Correlation between logs and traces

### 4. Process Compose Integration
- Loki and Promtail managed by Process Compose
- Health checks configured
- Automatic restarts on failure
- Dependency management (Promtail depends on Loki)

## Querying Logs

### Basic Queries

```logql
# All logs from Python backend
{job="python-backend"}

# Filter by log level
{job="python-backend"} | json | level="ERROR"

# Search for specific text
{job="python-backend"} |= "user_login"

# Multiple filters
{job="python-backend"} | json | level="INFO" | event="request_completed"
```

### Advanced Queries

```logql
# Find slow requests
{job="python-backend"}
  | json
  | event="request_completed"
  | duration_ms > 1000

# Count errors by user
sum by (user_id) (
  count_over_time(
    {job="python-backend"} | json | level="ERROR" [5m]
  )
)

# P95 response time
quantile_over_time(0.95,
  {job="python-backend"}
    | json
    | event="request_completed"
    | unwrap duration_ms [5m]
) by (path)
```

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin/admin |
| Grafana Explore (Logs) | http://localhost:3000/explore | admin/admin |
| Loki API | http://localhost:3100 | None |
| Promtail Metrics | http://localhost:9080/metrics | None |
| Logs Dashboard | http://localhost:3000/d/logs-dashboard | admin/admin |

## Benefits

### 1. Centralized Logging
- All service logs in one place
- No need to check multiple log files
- Unified search and filtering

### 2. Structured Logs
- Machine-readable JSON format
- Rich context (user_id, IP, trace_id, etc.)
- Easy filtering and aggregation

### 3. Powerful Queries
- LogQL query language
- Real-time log streaming
- Aggregations and metrics from logs

### 4. Correlation
- Link logs to traces (Jaeger)
- Link logs to metrics (Prometheus)
- Full observability stack

### 5. Retention Management
- Automatic log cleanup
- Configurable retention policies
- Compressed archives

## Next Steps

### 1. Add Structured Logging to Endpoints
Gradually migrate endpoints to structured logging:

```python
# Before
logger.info(f"User {user_id} performed action")

# After
logger.info("user_action", user_id=user_id, action="login")
```

### 2. Create More Dashboards
- Security dashboard (failed logins, suspicious activity)
- Performance dashboard (slow queries, errors)
- Business metrics (user activity, API usage)

### 3. Set Up Alerts
Configure Loki rules for alerting:

```yaml
# High error rate
alert: HighErrorRate
expr: |
  sum(rate({job="python-backend"} | json | level="ERROR" [5m]))
  > 10
```

### 4. Add Log Sampling
For high-volume logs, add sampling:

```python
# Only log 10% of successful requests
if random.random() < 0.1:
    logger.info("request_completed", ...)
```

### 5. Integrate with Other Services
- Add Nginx/Caddy access logs
- Add database query logs
- Add external API call logs

## Testing

### Verify Loki is Running
```bash
curl http://localhost:3100/ready
# Expected: "ready"
```

### Verify Promtail is Collecting
```bash
curl http://localhost:9080/targets
# Should show configured targets
```

### Query Logs via API
```bash
curl -G -s "http://localhost:3100/loki/api/v1/query" \
  --data-urlencode 'query={job="python-backend"}' \
  | jq
```

### View in Grafana
1. Open http://localhost:3000/explore
2. Select "Loki" data source
3. Run query: `{job="python-backend"} | json`
4. Should see structured logs

## Troubleshooting

### Loki Not Starting
```bash
# Check if port is in use
lsof -i :3100

# Check logs
cat .process-compose/logs/loki.log

# Test config
loki -config.file=monitoring/loki-local-config.yaml -verify-config
```

### Promtail Not Collecting
```bash
# Check if running
lsof -i :9080

# Check logs
cat .process-compose/logs/promtail.log

# Verify log files exist
ls -la .data/logs/
```

### No Logs in Grafana
1. Check Loki data source configuration
2. Verify Promtail is running and healthy
3. Check log file paths in promtail config
4. Verify logs are being written: `tail -f .data/logs/tracertm.json`

## Files Changed/Created

### Configuration Files
- ✅ `monitoring/loki-local-config.yaml` - Loki configuration
- ✅ `monitoring/promtail-local-config.yaml` - Promtail configuration
- ✅ `monitoring/grafana/provisioning/datasources/loki.yml` - Loki datasource
- ✅ `monitoring/dashboards/logs-dashboard.json` - Logs dashboard
- ✅ `monitoring/grafana.ini` - Updated provisioning paths

### Scripts
- ✅ `scripts/loki-if-not-running.sh` - Loki wrapper script
- ✅ `scripts/promtail-if-not-running.sh` - Promtail wrapper script
- ✅ `scripts/check-loki-installation.sh` - Installation checker

### Source Code
- ✅ `src/tracertm/logging_config.py` - Added structlog support

### Documentation
- ✅ `docs/guides/structured-logging-guide.md` - Complete guide
- ✅ `docs/guides/adding-structured-logging-example.md` - Examples
- ✅ `docs/reference/loki-quick-reference.md` - Quick reference
- ✅ `docs/reports/loki-implementation-complete.md` - This document

### Configuration Updates
- ✅ `process-compose.yaml` - Added Loki and Promtail services
- ✅ `.gitignore` - Added `.loki/` and `.promtail/`
- ✅ `README.md` - Added Observability section

### Dependencies
- ✅ `pyproject.toml` - Already has `structlog>=25.5.0`

## Task Completion

**Task #79: Phase 2 Observability - Log Aggregation (Loki)** ✅ COMPLETED

All requirements met:
1. ✅ Loki and Promtail added to process-compose.yaml
2. ✅ Configured structured logging in backend (structlog)
3. ✅ Created Loki data source in Grafana
4. ✅ Set up log retention policies (7 days local)
5. ✅ Created comprehensive documentation
6. ✅ Added installation scripts and health checks

## Conclusion

The Loki log aggregation system is fully integrated into TraceRTM. Developers can now:

1. View all logs in Grafana (http://localhost:3000/explore)
2. Run powerful LogQL queries to filter and aggregate logs
3. Use structured logging for better observability
4. Correlate logs with traces and metrics
5. Set up alerts based on log patterns

The system is production-ready with proper retention policies, automatic cleanup, and comprehensive documentation.

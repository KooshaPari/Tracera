# Structured Logging Guide

## Overview

TraceRTM uses structured logging with **structlog** to enable powerful log aggregation and analysis with Grafana Loki. Structured logs make it easy to search, filter, and correlate logs across services.

## Quick Start

### Import the logger

```python
from tracertm.logging_config import get_structlog_logger

logger = get_structlog_logger(__name__)
```

### Basic logging

```python
# Simple message
logger.info("Application started")

# With context
logger.info("user_login", user_id=user.id, username=user.email)

# With multiple fields
logger.info(
    "api_request",
    method=request.method,
    path=request.url.path,
    ip=request.client.host,
    user_id=user.id if user else None
)
```

### Error logging

```python
try:
    result = process_data(data)
except Exception as e:
    logger.error(
        "data_processing_failed",
        error=str(e),
        data_id=data.id,
        exc_info=True  # Include stack trace
    )
    raise
```

## Best Practices

### 1. Use descriptive event names

**Good:**
```python
logger.info("user_registration_completed", user_id=user.id, source="oauth")
```

**Bad:**
```python
logger.info("User registered")  # Hard to search/filter
```

### 2. Include relevant context

Always include identifiers that help with debugging:

```python
logger.info(
    "database_query_executed",
    query_type="SELECT",
    table="items",
    duration_ms=duration,
    rows_returned=len(results),
    project_id=project_id
)
```

### 3. Use consistent field names

- `user_id` (not `userId` or `user`)
- `project_id` (not `projectId`)
- `duration_ms` (for milliseconds)
- `error` (for error messages)
- `trace_id` (for distributed tracing correlation)

### 4. Log at appropriate levels

- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General informational messages (user actions, state changes)
- **WARNING**: Warning messages (deprecated APIs, unusual conditions)
- **ERROR**: Error messages (caught exceptions, failures)
- **CRITICAL**: Critical errors (service unavailable, data corruption)

## Integration with Distributed Tracing

Include trace IDs in your logs to correlate with Jaeger traces:

```python
from opentelemetry import trace

span = trace.get_current_span()
trace_id = format(span.get_span_context().trace_id, '032x') if span else None

logger.info(
    "workflow_started",
    workflow_id=workflow.id,
    trace_id=trace_id  # Loki will link to Jaeger
)
```

## Common Patterns

### API Request Logging

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger = get_structlog_logger(__name__)

    start_time = time.time()

    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host
    )

    response = await call_next(request)

    duration_ms = (time.time() - start_time) * 1000

    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2)
    )

    return response
```

### Database Query Logging

```python
async def execute_query(query: str, params: dict):
    logger = get_structlog_logger(__name__)

    start_time = time.time()

    try:
        result = await db.execute(query, params)
        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "db_query_executed",
            query_type=query.split()[0],  # SELECT, INSERT, etc.
            duration_ms=round(duration_ms, 2),
            rows_affected=result.rowcount
        )

        return result
    except Exception as e:
        logger.error(
            "db_query_failed",
            query_type=query.split()[0],
            error=str(e),
            exc_info=True
        )
        raise
```

### Background Job Logging

```python
async def process_background_job(job_id: str, data: dict):
    logger = get_structlog_logger(__name__)

    logger.info("job_started", job_id=job_id, job_type=data.get("type"))

    try:
        result = await process_job(data)

        logger.info(
            "job_completed",
            job_id=job_id,
            result_status="success",
            items_processed=result.count
        )
    except Exception as e:
        logger.error(
            "job_failed",
            job_id=job_id,
            error=str(e),
            exc_info=True
        )
        raise
```

## Querying Logs in Grafana

### Find all errors for a user

```logql
{job="python-backend"} |= `user_id="123"` | json | level="ERROR"
```

### Find slow API requests

```logql
{job="python-backend"}
  | json
  | event="request_completed"
  | duration_ms > 1000
```

### Count requests by status code

```logql
sum by (status_code) (
  count_over_time({job="python-backend"} | json | event="request_completed" [5m])
)
```

### Find database errors

```logql
{job="python-backend"}
  | json
  | event=~"db_.*"
  | level="ERROR"
```

## Migration from Loguru

Both Loguru and structlog are available. Gradually migrate to structlog:

**Before (Loguru):**
```python
from tracertm.logging_config import get_logger

logger = get_logger(__name__)
logger.info(f"User {user_id} logged in from {ip}")
```

**After (structlog):**
```python
from tracertm.logging_config import get_structlog_logger

logger = get_structlog_logger(__name__)
logger.info("user_login", user_id=user_id, ip=ip)
```

## Configuration

Structured logging is configured in `src/tracertm/logging_config.py`. The configuration includes:

- JSON formatting for machine-readable logs
- ISO 8601 timestamps
- Automatic exception info rendering
- Context variables for request-scoped data

## Log Retention

- **Local logs**: 7 days (configured in Loki)
- **Error logs**: 30 days (Loguru file handler)
- **Loki storage**: `.loki/` directory (gitignored)

## See Also

- [Loki LogQL Documentation](https://grafana.com/docs/loki/latest/logql/)
- [structlog Documentation](https://www.structlog.org/)
- [Grafana Explore UI](http://localhost:3000/explore)

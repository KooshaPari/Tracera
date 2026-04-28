# Adding Structured Logging - Example

## Before and After Example

This guide shows how to migrate an existing endpoint from basic logging to structured logging.

## Example: User Authentication Endpoint

### Before (Basic Logging with Loguru)

```python
from tracertm.logging_config import get_logger

logger = get_logger(__name__)

@app.post("/auth/login")
async def login(request: LoginRequest):
    logger.info(f"Login attempt for user: {request.email}")

    try:
        user = await authenticate_user(request.email, request.password)

        logger.info(f"User {user.id} logged in successfully")

        return {"token": create_token(user)}

    except InvalidCredentialsError:
        logger.warning(f"Invalid login attempt for {request.email}")
        raise HTTPException(status_code=401)

    except Exception as e:
        logger.error(f"Login error for {request.email}: {str(e)}")
        raise
```

### After (Structured Logging with structlog)

```python
from tracertm.logging_config import get_structlog_logger

logger = get_structlog_logger(__name__)

@app.post("/auth/login")
async def login(request: LoginRequest):
    # Log with structured context
    logger.info(
        "login_attempt",
        email=request.email,
        ip=request.client.host,
        user_agent=request.headers.get("user-agent", "unknown")
    )

    try:
        user = await authenticate_user(request.email, request.password)

        logger.info(
            "login_success",
            user_id=user.id,
            email=user.email,
            ip=request.client.host
        )

        return {"token": create_token(user)}

    except InvalidCredentialsError:
        logger.warning(
            "login_failed",
            reason="invalid_credentials",
            email=request.email,
            ip=request.client.host
        )
        raise HTTPException(status_code=401)

    except Exception as e:
        logger.error(
            "login_error",
            error=str(e),
            email=request.email,
            ip=request.client.host,
            exc_info=True  # Include stack trace
        )
        raise
```

## Benefits

### 1. Easy Filtering in Loki

**Find all failed login attempts:**
```logql
{job="python-backend"} | json | event="login_failed"
```

**Find login attempts from specific IP:**
```logql
{job="python-backend"} | json | event=~"login_.*" | ip="192.168.1.100"
```

**Count successful logins per user:**
```logql
sum by (user_id) (
  count_over_time({job="python-backend"} | json | event="login_success" [1h])
)
```

### 2. Better Monitoring

Create alerts on structured data:

```yaml
# Alert if >5 failed login attempts in 5 minutes
alert: HighFailedLogins
expr: |
  sum(count_over_time({job="python-backend"} | json | event="login_failed" [5m]))
  > 5
```

### 3. Correlation with Traces

Add trace IDs to correlate logs with distributed traces:

```python
from opentelemetry import trace

span = trace.get_current_span()
trace_id = format(span.get_span_context().trace_id, '032x') if span else None

logger.info(
    "login_success",
    user_id=user.id,
    trace_id=trace_id  # Click in Grafana to view trace
)
```

## Migration Strategy

### Phase 1: Add Structured Logging Alongside Existing Logs

```python
# Keep both during transition
from tracertm.logging_config import get_logger, get_structlog_logger

loguru_logger = get_logger(__name__)
struct_logger = get_structlog_logger(__name__)

@app.post("/endpoint")
async def endpoint():
    # Old format (backwards compatibility)
    loguru_logger.info("Processing request")

    # New format (for Loki)
    struct_logger.info("request_started", endpoint="/endpoint")

    # ...
```

### Phase 2: Gradually Replace

Once confident in structured logging:

```python
from tracertm.logging_config import get_structlog_logger

logger = get_structlog_logger(__name__)

@app.post("/endpoint")
async def endpoint():
    # Only structured logging
    logger.info("request_started", endpoint="/endpoint")
    # ...
```

## Common Patterns

### HTTP Request Middleware

```python
import time
from tracertm.logging_config import get_structlog_logger

logger = get_structlog_logger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request start
    logger.info(
        "http_request_started",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent", "unknown")
    )

    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        # Log successful response
        logger.info(
            "http_request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2)
        )

        return response

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000

        # Log error
        logger.error(
            "http_request_failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            duration_ms=round(duration_ms, 2),
            exc_info=True
        )
        raise
```

### Database Operations

```python
async def create_item(db: AsyncSession, item: ItemCreate):
    logger = get_structlog_logger(__name__)

    logger.info(
        "db_create_item_started",
        item_type=item.type,
        project_id=item.project_id
    )

    try:
        db_item = Item(**item.dict())
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)

        logger.info(
            "db_create_item_completed",
            item_id=db_item.id,
            item_type=db_item.type,
            project_id=db_item.project_id
        )

        return db_item

    except Exception as e:
        await db.rollback()

        logger.error(
            "db_create_item_failed",
            item_type=item.type,
            error=str(e),
            exc_info=True
        )
        raise
```

### Background Tasks

```python
from temporalio import activity

@activity.defn
async def process_workflow(workflow_id: str, data: dict):
    logger = get_structlog_logger(__name__)

    logger.info(
        "workflow_activity_started",
        workflow_id=workflow_id,
        activity="process_workflow"
    )

    try:
        result = await process_data(data)

        logger.info(
            "workflow_activity_completed",
            workflow_id=workflow_id,
            activity="process_workflow",
            result_status="success",
            items_processed=len(result)
        )

        return result

    except Exception as e:
        logger.error(
            "workflow_activity_failed",
            workflow_id=workflow_id,
            activity="process_workflow",
            error=str(e),
            exc_info=True
        )
        raise
```

## Testing

### Unit Test Example

```python
import pytest
from unittest.mock import patch
import structlog

def test_login_logs_structured_data():
    # Capture structlog output
    with patch.object(structlog.get_logger(), 'info') as mock_log:
        # Perform login
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })

        # Verify structured logging was called
        mock_log.assert_called_with(
            "login_success",
            user_id=mock.ANY,
            email="test@example.com",
            ip=mock.ANY
        )
```

## See Also

- [Structured Logging Guide](structured-logging-guide.md)
- [Loki Quick Reference](../reference/loki-quick-reference.md)
- [structlog Documentation](https://www.structlog.org/)

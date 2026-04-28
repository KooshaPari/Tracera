# API Gateway Guide

Complete guide to using `pheno.gateway` for building production-ready API gateways with middleware.

## Overview

`pheno.gateway` provides:
- **ASGI Integration**: Easy integration with FastAPI/Starlette applications
- **Middleware Stack**: Framework-agnostic middleware composition
- **Rate Limiting**: Token bucket rate limiting with configurable keys
- **CORS**: Cross-Origin Resource Sharing configuration
- **Circuit Breaker**: Automatic failure detection and recovery
- **Retry Logic**: Exponential backoff retries for transient failures
- **Timeout Handling**: Request timeout enforcement
- **HTTP Metrics**: Prometheus metrics for HTTP requests

## Quick Start

### Basic ASGI Gateway

```python
from fastapi import FastAPI
from pheno.gateway import add_asgi_gateway
from pheno.observability import add_prometheus_endpoint

app = FastAPI()

# Add gateway middleware
add_asgi_gateway(
    app,
    rate_limit={"max_requests": 100, "window_seconds": 60},
    rate_limit_key="client_ip",
    cors={"allow_origins": ["*"]},
)

# Add metrics endpoint
add_prometheus_endpoint(app)

@app.get("/")
async def root():
    return {"message": "Hello!"}
```

## Middleware Components

### Rate Limiting

Limit requests per time window using token bucket algorithm:

```python
from pheno.gateway import add_asgi_gateway

add_asgi_gateway(
    app,
    rate_limit={
        "max_requests": 100,      # Max requests per window
        "window_seconds": 60,     # Time window in seconds
        "expose_headers": True,   # Add rate limit headers to response
    },
    rate_limit_key="client_ip",   # Key strategy: client_ip, path, method, header:X, cookie:Y, query:Z
)
```

**Rate Limit Keys:**
- `"client_ip"` - Limit by client IP address
- `"path"` - Limit by request path
- `"method"` - Limit by HTTP method
- `"header:X-API-Key"` - Limit by header value
- `"cookie:session"` - Limit by cookie value
- `"query:user_id"` - Limit by query parameter
- `"client_ip+path"` - Combine multiple keys

**Response Headers:**
When `expose_headers=True`:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in window
- `X-RateLimit-Window`: Window size in seconds
- `Retry-After`: Seconds until rate limit resets (on 429)

### CORS

Configure Cross-Origin Resource Sharing:

```python
add_asgi_gateway(
    app,
    cors={
        "allow_origins": ["http://localhost:3000", "https://example.com"],
        "allow_methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["*"],
        "allow_credentials": True,
        "max_age": 600,  # Preflight cache duration
    },
)
```

### Circuit Breaker

Prevent cascading failures with automatic circuit breaking:

```python
add_asgi_gateway(
    app,
    circuit_breaker={
        "failure_threshold": 5,      # Open after 5 failures
        "recovery_timeout": 60,      # Try recovery after 60 seconds
        "expected_exception": Exception,  # Exception type to track
    },
)
```

**States:**
- **Closed**: Normal operation, requests pass through
- **Open**: Too many failures, requests fail immediately
- **Half-Open**: Testing recovery, limited requests allowed

### Retry Logic

Automatically retry failed requests with exponential backoff:

```python
add_asgi_gateway(
    app,
    retry={
        "max_retries": 3,                    # Maximum retry attempts
        "backoff_factor": 1.0,               # Exponential backoff multiplier
        "retry_on_status": [502, 503, 504],  # HTTP status codes to retry
    },
)
```

**Backoff Calculation:**
```
wait_time = backoff_factor * (2 ** attempt)
```

### Timeout Handling

Enforce request timeouts:

```python
add_asgi_gateway(
    app,
    timeout={"timeout_seconds": 30},
)
```

### HTTP Metrics

Collect Prometheus metrics for HTTP requests:

```python
from pheno.gateway import add_http_metrics_middleware
from pheno.observability import add_prometheus_endpoint

# Add metrics middleware
add_http_metrics_middleware(app)

# Add metrics endpoint
add_prometheus_endpoint(app, path="/metrics")
```

**Metrics Collected:**
- `http_requests_total{method, path, status}` - Total requests counter
- `http_request_duration_seconds{method, path}` - Request duration histogram

## Framework-Agnostic Usage

Use middleware stack without ASGI:

```python
from pheno.gateway.stack import add_gateway_stack

async def my_handler(message: dict) -> dict:
    # Process message
    return {"status": "success"}

# Wrap with middleware
wrapped = add_gateway_stack(
    my_handler,
    rate_limit={
        "max_requests": 100,
        "window_seconds": 60,
        "key_func": lambda msg: msg.get("user_id", "anonymous"),
    },
    timeout={"timeout_seconds": 5},
    retry={"max_retries": 2},
)

# Use wrapped handler
result = await wrapped({"user_id": "123", "action": "test"})
```

## Complete Example

```python
from fastapi import FastAPI, Request
from pheno.gateway import add_asgi_gateway, add_http_metrics_middleware
from pheno.observability import add_prometheus_endpoint, configure_structlog

app = FastAPI(title="Production API")

# Configure logging
configure_structlog(service_name="api", environment="production")

# Add metrics middleware
add_http_metrics_middleware(app)

# Add gateway middleware
add_asgi_gateway(
    app,
    rate_limit={"max_requests": 1000, "window_seconds": 60},
    rate_limit_key="header:X-API-Key",
    cors={
        "allow_origins": ["https://app.example.com"],
        "allow_credentials": True,
    },
    timeout={"timeout_seconds": 30},
    retry={"max_retries": 3, "backoff_factor": 1.0},
    circuit_breaker={"failure_threshold": 10, "recovery_timeout": 60},
    structured_errors=True,
    correlation_header="X-Request-ID",
)

# Add metrics endpoint
add_prometheus_endpoint(app)

@app.get("/api/data")
async def get_data(request: Request):
    correlation_id = request.headers.get("X-Request-ID")
    return {"data": "example", "correlation_id": correlation_id}
```

## Direct Middleware Usage

Use individual middleware components:

```python
from pheno.gateway.middleware import (
    RateLimiter,
    CircuitBreaker,
    CORSMiddleware,
)

# Rate limiter
limiter = RateLimiter(max_requests=100, window_seconds=60)
if await limiter.allow("user123"):
    # Process request
    pass
else:
    # Rate limited
    pass

# Circuit breaker
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
try:
    result = await breaker.call(my_function)
except Exception as e:
    # Circuit open or function failed
    pass
```

## Best Practices

1. **Rate Limiting**: Choose appropriate keys based on your use case
   - API keys for authenticated APIs
   - Client IP for public endpoints
   - Combined keys for fine-grained control

2. **Circuit Breaker**: Set thresholds based on your SLA
   - Lower threshold for critical services
   - Higher recovery timeout for external dependencies

3. **Metrics**: Always enable HTTP metrics in production
   - Monitor request rates and latencies
   - Set up alerts on error rates

4. **Timeouts**: Set realistic timeouts
   - Consider downstream service latencies
   - Add buffer for network overhead

5. **CORS**: Be specific with allowed origins in production
   - Avoid `allow_origins=["*"]` in production
   - Enable credentials only when needed

## Examples

See the `examples/gateway/` directory for complete examples:
- `basic_gateway_example.py` - Minimal FastAPI integration
- `complete_gateway_example.py` - All features enabled
- `middleware_stack_example.py` - Framework-agnostic usage

## API Reference

### ASGI Integration

- `add_asgi_gateway(app, **config)` - Add gateway middleware to ASGI app
- `GatewayHTTPMiddleware` - ASGI middleware class

### Stack Composition

- `add_gateway_stack(handler, **config)` - Wrap handler with middleware
- `build_gateway_composer(**config)` - Build reusable composer function

### Middleware

- `RateLimiter` - Token bucket rate limiter
- `CircuitBreaker` - Circuit breaker pattern
- `CORSMiddleware` - CORS handling
- `RetryMiddleware` - Retry with backoff
- `TimeoutMiddleware` - Request timeout
- `HTTPMetricsMiddleware` - Prometheus metrics

## Migration from api-gateway-kit

```python
# Before (api-gateway-kit)
from api_gateway_kit import add_asgi_gateway
from api_gateway_kit.middleware import add_gateway_stack

# After (pheno.gateway)
from pheno.gateway import add_asgi_gateway, add_gateway_stack
```

All functionality is preserved with the same API.

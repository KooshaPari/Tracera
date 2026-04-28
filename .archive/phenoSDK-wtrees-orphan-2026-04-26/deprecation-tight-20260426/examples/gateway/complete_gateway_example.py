"""Complete API Gateway Example using pheno.gateway.

Demonstrates:
- ASGI gateway middleware integration
- Rate limiting
- CORS configuration
- Circuit breaker
- Retry logic
- Timeout handling
- HTTP metrics collection
- Prometheus metrics endpoint
"""

from fastapi import FastAPI, Request
from pheno.gateway import (
    add_asgi_gateway,
    add_http_metrics_middleware,
)

from pheno.observability import add_prometheus_endpoint, configure_structlog

# Initialize FastAPI app
app = FastAPI(title="Complete Gateway Example")

# Configure structured logging
configure_structlog(service_name="gateway-example", environment="dev")

# Add HTTP metrics middleware (must be added before gateway middleware)
add_http_metrics_middleware(app)

# Add gateway middleware with all features
add_asgi_gateway(
    app,
    # Rate limiting: 100 requests per 60 seconds per client IP
    rate_limit={
        "max_requests": 100,
        "window_seconds": 60,
        "expose_headers": True,
    },
    rate_limit_key="client_ip",  # Use client IP as rate limit key
    # CORS configuration
    cors={
        "allow_origins": ["http://localhost:3000", "https://example.com"],
        "allow_methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["*"],
        "allow_credentials": True,
    },
    # Timeout: 30 seconds per request
    timeout={"timeout_seconds": 30},
    # Retry: up to 3 retries with exponential backoff
    retry={
        "max_retries": 3,
        "backoff_factor": 1.0,
        "retry_on_status": [502, 503, 504],
    },
    # Circuit breaker: open after 5 failures, half-open after 60 seconds
    circuit_breaker={
        "failure_threshold": 5,
        "recovery_timeout": 60,
        "expected_exception": Exception,
    },
    # Enable structured error responses
    structured_errors=True,
    # Custom correlation header
    correlation_header="X-Request-ID",
)

# Add Prometheus metrics endpoint
add_prometheus_endpoint(app, path="/metrics")


# Example routes
@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {"message": "Welcome to the API Gateway Example"}


@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}


@app.get("/slow")
async def slow_endpoint():
    """
    Simulates a slow endpoint (will timeout after 30s).
    """
    import asyncio

    await asyncio.sleep(5)
    return {"message": "This took 5 seconds"}


@app.get("/error")
async def error_endpoint():
    """
    Simulates an error (will trigger circuit breaker after threshold).
    """
    raise Exception("Simulated error")


@app.get("/protected")
async def protected_endpoint(request: Request):
    """
    Example of accessing request metadata.
    """
    correlation_id = request.headers.get("X-Request-ID", "unknown")
    return {
        "message": "Protected endpoint",
        "correlation_id": correlation_id,
        "client_ip": request.client.host if request.client else "unknown",
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting API Gateway Example...")
    print("- API: http://localhost:8000")
    print("- Docs: http://localhost:8000/docs")
    print("- Metrics: http://localhost:8000/metrics")
    print("\nFeatures enabled:")
    print("  ✓ Rate limiting (100 req/min per IP)")
    print("  ✓ CORS")
    print("  ✓ Timeouts (30s)")
    print("  ✓ Retries (3x with backoff)")
    print("  ✓ Circuit breaker (5 failures)")
    print("  ✓ HTTP metrics")
    print("  ✓ Structured logging")

    uvicorn.run(app, host="0.0.0.0", port=8000)

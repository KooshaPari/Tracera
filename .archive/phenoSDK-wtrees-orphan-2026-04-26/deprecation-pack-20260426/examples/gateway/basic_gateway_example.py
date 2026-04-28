"""Basic API Gateway Example using pheno.gateway.

Minimal example showing rate limiting and CORS.
"""

from fastapi import FastAPI
from pheno.gateway import add_asgi_gateway

from pheno.observability import add_prometheus_endpoint

app = FastAPI(title="Basic Gateway Example")

# Add gateway with rate limiting and CORS
add_asgi_gateway(
    app,
    rate_limit={"max_requests": 100, "window_seconds": 60},
    rate_limit_key="client_ip",
    cors={
        "allow_origins": ["*"],
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    },
)

# Add metrics endpoint
add_prometheus_endpoint(app)


@app.get("/")
async def root():
    return {"message": "Hello from pheno.gateway!"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    print("Starting Basic Gateway Example on http://localhost:8000")
    print("- Docs: http://localhost:8000/docs")
    print("- Metrics: http://localhost:8000/metrics")
    uvicorn.run(app, host="0.0.0.0", port=8000)

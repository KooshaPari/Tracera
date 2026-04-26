# phenotype-api

FastAPI app factory with standard middleware and error handling for Phenotype services.

## Features

- **App Factory**: Pre-configured FastAPI with sensible defaults
- **Request ID Middleware**: Automatic UUID generation and propagation
- **CORS Support**: Configurable cross-origin resource sharing
- **Error Handling**: Global exception handler with structured responses
- **Health Checks**: Built-in health check endpoint

## Installation

```bash
pip install phenotype-api
```

## Quick Start

```python
from phenotype_api import create_app

# Create app with standard configuration
app = create_app(
    title="My Service",
    version="1.0.0",
    cors_origins=["http://localhost:3000"],
)

@app.get("/api/example")
async def example():
    return {"message": "Hello"}

# Health check available at /health
```

## License

MIT

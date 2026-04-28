# Getting Started with Pheno-SDK

> A comprehensive tutorial to get you up and running with Pheno-SDK

Welcome! This guide will walk you through building your first application with Pheno-SDK, from installation to deployment.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Your First Application](#your-first-application)
4. [Adding Observability](#adding-observability)
5. [Database Integration](#database-integration)
6. [File Storage](#file-storage)
7. [Real-Time Communication](#real-time-communication)
8. [Building a Complete API](#building-a-complete-api)
9. [Testing Your Application](#testing-your-application)
10. [Deployment](#deployment)
11. [Next Steps](#next-steps)

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.10 or higher** installed
- **pip** package manager
- Basic knowledge of Python and async/await
- A code editor (VS Code, PyCharm, etc.)

Verify your Python version:

```bash
python --version  # Should show 3.10 or higher
```

---

## Installation

### Step 1: Create a Virtual Environment

```bash
# Create a new directory for your project
mkdir my-pheno-app
cd my-pheno-app

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Pheno-SDK Kits

Start with the core kits:

```bash
# Core functionality
pip install adapter-kit config-kit

# Database and storage
pip install db-kit storage-kit

# Observability
pip install observability-kit

# Web framework (for REST API)
pip install fastapi uvicorn

# Optional: Terminal UI
pip install tui-kit
```

---

## Your First Application

Let's start with a simple "Hello World" application that demonstrates core concepts.

### Create `main.py`:

```python
"""
Simple Pheno-SDK application demonstrating core concepts.
"""
from config_kit import Config
from observability import StructuredLogger

# 1. Configuration
class AppConfig(Config):
    """Application configuration."""
    app_name: str = "my-pheno-app"
    debug: bool = False
    port: int = 8000

# 2. Load configuration from environment
config = AppConfig.from_env(prefix="APP_")

# 3. Set up logging
logger = StructuredLogger(
    config.app_name,
    environment="development" if config.debug else "production"
)

# 4. Main application logic
def main():
    """Run the application."""
    logger.info("Application starting",
        app_name=config.app_name,
        port=config.port
    )

    # Your application logic here
    logger.info("Hello from Pheno-SDK!")

    logger.info("Application completed successfully")

if __name__ == "__main__":
    main()
```

### Run it:

```bash
python main.py
```

You should see structured JSON logs:

```json
{"timestamp": "2025-10-10T12:00:00.123456Z", "level": "INFO", "message": "Application starting", ...}
{"timestamp": "2025-10-10T12:00:00.234567Z", "level": "INFO", "message": "Hello from Pheno-SDK!"}
```

**What we learned:**
- ✅ Configuration management with `config-kit`
- ✅ Structured logging with `observability-kit`
- ✅ Environment variable loading

---

## Adding Observability

Let's enhance our application with comprehensive observability: metrics and distributed tracing.

### Create `app.py`:

```python
"""
Application with full observability stack.
"""
import asyncio
from observability import (
    StructuredLogger,
    MetricsCollector,
    DistributedTracer,
    trace_async,
    set_default_tracer
)

# Initialize observability stack
logger = StructuredLogger("demo-app")
metrics = MetricsCollector()
tracer = DistributedTracer("demo-app")
set_default_tracer(tracer)

# Define metrics
operation_counter = metrics.counter(
    "operations_total",
    "Total operations performed",
    labels=["operation", "status"]
)

operation_duration = metrics.histogram(
    "operation_duration_seconds",
    "Operation duration",
    labels=["operation"]
)

# Traced function with decorator
@trace_async(capture_args=True, capture_result=True)
async def process_data(data: str) -> dict:
    """Process data with automatic tracing."""
    logger.info("Processing data", data_length=len(data))

    # Simulate processing
    await asyncio.sleep(0.1)

    result = {"processed": data.upper(), "length": len(data)}

    logger.info("Data processed", result_length=len(result))
    return result

async def main():
    """Main application logic."""
    logger.info("Application starting")

    # Create a span for the entire operation
    with tracer.start_span("main_operation") as span:
        span.set_attribute("environment", "development")

        try:
            # Process some data
            result = await process_data("hello world")

            # Record metrics
            operation_counter.inc({"operation": "process", "status": "success"})

            logger.info("Operation completed", result=result)

        except Exception as e:
            operation_counter.inc({"operation": "process", "status": "error"})
            logger.error("Operation failed", exc_info=e)
            raise

    # Export metrics (Prometheus format)
    print("\n=== Metrics ===")
    print(metrics.to_prometheus_text())

    # Export spans (for debugging)
    print("\n=== Traces ===")
    spans = tracer.export_spans()
    for span_data in spans:
        print(f"Span: {span_data['name']} - Duration: {span_data['duration_ns']/1e9:.3f}s")

if __name__ == "__main__":
    asyncio.run(main())
```

### Run it:

```bash
python app.py
```

**What we learned:**
- ✅ Structured logging with context
- ✅ Prometheus metrics (counters, histograms)
- ✅ Distributed tracing with spans
- ✅ Decorator-based function tracing
- ✅ Automatic metric and trace export

---

## Database Integration

Now let's add database operations using `db-kit`.

### Step 1: Set up Supabase (or another provider)

```bash
# Set environment variables
export NEXT_PUBLIC_SUPABASE_URL="https://your-project.supabase.co"
export NEXT_PUBLIC_SUPABASE_ANON_KEY="your-anon-key"
```

### Step 2: Create `database_app.py`:

```python
"""
Application with database integration.
"""
import asyncio
from db_kit import Database
from observability import StructuredLogger

logger = StructuredLogger("database-app")

async def main():
    """Database operations example."""
    logger.info("Connecting to database")

    # Initialize database (auto-configures from environment)
    db = Database.supabase()

    # Create a user
    logger.info("Creating user")
    new_user = await db.insert("users", {
        "username": "alice",
        "email": "alice@example.com",
        "active": True
    })
    logger.info("User created", user_id=new_user["id"])

    # Query users
    logger.info("Querying active users")
    active_users = await db.query(
        "users",
        filters={"active": True},
        order_by="created_at:desc",
        limit=10
    )
    logger.info("Found users", count=len(active_users))

    # Get single user
    user = await db.get_single(
        "users",
        filters={"email": "alice@example.com"}
    )
    logger.info("Retrieved user", username=user["username"])

    # Update user
    await db.update(
        "users",
        data={"last_login": "2025-10-10T12:00:00Z"},
        filters={"id": user["id"]}
    )
    logger.info("Updated user")

    # Advanced filtering
    adult_users = await db.query(
        "users",
        filters={
            "age": {"gte": 18},  # age >= 18
            "active": True,
            "email": {"like": "%@example.com"}
        }
    )
    logger.info("Found adult users", count=len(adult_users))

    # Count users
    total = await db.count("users")
    logger.info("Total users", count=total)

if __name__ == "__main__":
    asyncio.run(main())
```

### Run it:

```bash
python database_app.py
```

**What we learned:**
- ✅ Database connection with auto-configuration
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Advanced filtering with operators
- ✅ Query optimization (order_by, limit)
- ✅ Counting and aggregation

---

## File Storage

Let's add file storage capabilities.

### Create `storage_app.py`:

```python
"""
Application with file storage.
"""
import asyncio
from storage_kit import StorageClient
from storage_kit.providers import LocalStorageProvider
from observability import StructuredLogger

logger = StructuredLogger("storage-app")

async def main():
    """File storage example."""
    logger.info("Initializing storage")

    # Use local storage for demo (switch to S3/GCS in production)
    client = StorageClient(LocalStorageProvider(base_path="./storage"))

    # Upload a file
    logger.info("Uploading file")
    file = await client.upload(
        "documents/hello.txt",
        b"Hello from Pheno-SDK!",
        content_type="text/plain",
        metadata={"author": "tutorial"}
    )
    logger.info("File uploaded", path=file.path, size=file.size)

    # Download the file
    logger.info("Downloading file")
    data = await client.download("documents/hello.txt")
    logger.info("File downloaded", content=data.decode())

    # Get presigned URL (works with S3/GCS)
    # url = await client.get_url("documents/hello.txt", expires_in=3600)
    # logger.info("Presigned URL generated", url=url)

    # List files
    # files = await client.list("documents/")
    # logger.info("Files listed", count=len(files))

    # Delete file
    # await client.delete("documents/hello.txt")
    # logger.info("File deleted")

if __name__ == "__main__":
    asyncio.run(main())
```

### Run it:

```bash
python storage_app.py
```

**What we learned:**
- ✅ File upload with metadata
- ✅ File download
- ✅ Local storage (easily switch to S3/GCS)
- ✅ Content type handling

---

## Real-Time Communication

Add real-time capabilities with `stream-kit`.

### Create `streaming_app.py`:

```python
"""
Application with real-time streaming.
"""
import asyncio
from stream_kit import StreamingManager, StreamMessageType
from stream_kit.protocols import SSEProtocol
from observability import StructuredLogger

logger = StructuredLogger("streaming-app")

async def producer(manager: StreamingManager):
    """Produce messages to a channel."""
    for i in range(5):
        await asyncio.sleep(1)

        message = {"count": i, "message": f"Update {i}"}
        await manager.broadcast(
            channel="updates",
            content=message,
            message_type=StreamMessageType.STATUS_UPDATE
        )
        logger.info("Message broadcasted", count=i)

async def consumer(manager: StreamingManager):
    """Consume messages from a channel."""
    conn_id = "consumer-1"
    queue = await manager.register_sse(conn_id, channels=["updates"])

    logger.info("Consumer registered")

    try:
        while True:
            message = await queue.get()
            logger.info("Message received",
                content=message.content,
                type=message.message_type
            )

            if message.content.get("count") >= 4:
                break
    finally:
        await manager.unregister_connection(conn_id)
        logger.info("Consumer unregistered")

async def main():
    """Streaming example."""
    manager = StreamingManager()

    # Run producer and consumer concurrently
    await asyncio.gather(
        producer(manager),
        consumer(manager)
    )

    # Show statistics
    stats = manager.get_stats()
    logger.info("Streaming completed", stats=stats)

if __name__ == "__main__":
    asyncio.run(main())
```

### Run it:

```bash
python streaming_app.py
```

**What we learned:**
- ✅ Channel-based messaging
- ✅ Producer-consumer pattern
- ✅ Real-time message broadcasting
- ✅ Connection management

---

## Building a Complete API

Now let's build a complete REST API with everything we've learned.

### Create `api.py`:

```python
"""
Complete REST API with Pheno-SDK.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from observability import (
    StructuredLogger,
    MetricsCollector,
    DistributedTracer,
    SpanKind,
    generate_correlation_id
)
from db_kit import Database
from adapter_kit import Container
import time

# Configuration
app = FastAPI(title="Pheno-SDK API", version="1.0.0")

# Observability
logger = StructuredLogger("api", environment="development")
metrics = MetricsCollector()
tracer = DistributedTracer("api")

# Metrics
http_requests = metrics.counter(
    "http_requests_total",
    "Total HTTP requests",
    labels=["method", "endpoint", "status"]
)
http_duration = metrics.histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    labels=["method", "endpoint"]
)

# Database
db = Database.supabase()

# DI Container
container = Container()
container.register_instance(Database, db)
container.register_instance(StructuredLogger, logger)

# Models
class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    active: bool

# Middleware
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    """Add observability to all requests."""
    start_time = time.time()

    # Correlation ID
    correlation_id = request.headers.get("X-Correlation-ID", generate_correlation_id())
    logger.set_correlation_id(correlation_id)

    # Distributed tracing
    parent_context = tracer.extract_context(dict(request.headers))

    with tracer.start_span(
        f"{request.method} {request.url.path}",
        kind=SpanKind.SERVER,
        parent_context=parent_context
    ) as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))

        logger.set_trace_context(span.context.trace_id, span.context.span_id)
        logger.info("Request started",
            method=request.method,
            path=request.url.path
        )

        # Process request
        try:
            response = await call_next(request)

            # Record metrics
            duration = time.time() - start_time
            http_requests.inc({
                "method": request.method,
                "endpoint": request.url.path,
                "status": str(response.status_code)
            })
            http_duration.observe(duration, {
                "method": request.method,
                "endpoint": request.url.path
            })

            logger.info("Request completed",
                status=response.status_code,
                duration_ms=duration * 1000
            )

            # Add correlation ID to response
            response.headers["X-Correlation-ID"] = correlation_id

            return response

        except Exception as e:
            logger.error("Request failed", exc_info=e)
            http_requests.inc({
                "method": request.method,
                "endpoint": request.url.path,
                "status": "500"
            })
            raise

# Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Pheno-SDK API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user."""
    logger.info("Creating user", username=user.username)

    # Check if user exists
    existing = await db.query("users", filters={"email": user.email}, limit=1)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create user
    new_user = await db.insert("users", {
        "username": user.username,
        "email": user.email,
        "active": True
    })

    logger.info("User created", user_id=new_user["id"])
    return new_user

@app.get("/users", response_model=list[UserResponse])
async def list_users(active: bool = None, limit: int = 100):
    """List users with optional filtering."""
    logger.info("Listing users", active=active, limit=limit)

    filters = {"active": active} if active is not None else None
    users = await db.query("users", filters=filters, limit=limit)

    logger.info("Users retrieved", count=len(users))
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get a specific user."""
    logger.info("Retrieving user", user_id=user_id)

    user = await db.get_single("users", filters={"id": user_id})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info("User retrieved", user_id=user_id)
    return user

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    return JSONResponse(
        content=metrics.to_prometheus_text(),
        media_type="text/plain"
    )

# Run with: uvicorn api:app --reload
```

### Run the API:

```bash
uvicorn api:app --reload --port 8000
```

### Test the API:

```bash
# Health check
curl http://localhost:8000/health

# Create a user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com"}'

# List users
curl http://localhost:8000/users

# Get metrics
curl http://localhost:8000/metrics

# API documentation
open http://localhost:8000/docs
```

**What we learned:**
- ✅ Complete REST API with FastAPI
- ✅ Comprehensive observability middleware
- ✅ Distributed tracing across requests
- ✅ Prometheus metrics endpoint
- ✅ Correlation ID propagation
- ✅ Error handling and logging
- ✅ Database integration
- ✅ Dependency injection

---

## Testing Your Application

Let's write tests for our API.

### Create `test_api.py`:

```python
"""
Tests for the API.
"""
import pytest
from httpx import AsyncClient
from api import app
from db_kit import Database
from adapter_kit import InMemoryRepository

@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

@pytest.mark.asyncio
async def test_create_user(client):
    """Test user creation."""
    response = await client.post("/users", json={
        "username": "testuser",
        "email": "test@example.com"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_list_users(client):
    """Test user listing."""
    response = await client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_nonexistent_user(client):
    """Test getting non-existent user."""
    response = await client.get("/users/nonexistent-id")
    assert response.status_code == 404
```

### Run tests:

```bash
pip install pytest pytest-asyncio httpx
pytest test_api.py -v
```

**What we learned:**
- ✅ Async testing with pytest
- ✅ API endpoint testing
- ✅ Test fixtures
- ✅ Error case testing

---

## Deployment

Let's deploy your application using `deploy-kit`.

### Step 1: Vendor Pheno-SDK Packages

```bash
# Install deploy-kit
pip install deploy-kit

# Vendor packages for production
pheno-vendor setup

# This creates:
# - pheno_vendor/           (vendored packages)
# - requirements-prod.txt   (production requirements)
# - sitecustomize.py        (Python path setup)
```

### Step 2: Generate Platform Configs

```bash
# Generate Vercel config
pheno-vendor generate-hooks --platform vercel

# Generate Docker config
pheno-vendor generate-hooks --platform docker
```

### Step 3: Deploy to Vercel

Create `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api.py"
    }
  ],
  "env": {
    "PYTHONPATH": "pheno_vendor",
    "NEXT_PUBLIC_SUPABASE_URL": "@supabase-url",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase-key"
  }
}
```

Deploy:

```bash
vercel deploy
```

### Step 4: Deploy with Docker

Use the generated `Dockerfile`:

```bash
# Build
docker build -t my-pheno-app .

# Run
docker run -p 8000:8000 \
  -e NEXT_PUBLIC_SUPABASE_URL="your-url" \
  -e NEXT_PUBLIC_SUPABASE_ANON_KEY="your-key" \
  my-pheno-app
```

**What we learned:**
- ✅ Vendoring Pheno-SDK for production
- ✅ Generating platform-specific configs
- ✅ Deploying to Vercel
- ✅ Deploying with Docker

---

## Next Steps

Congratulations! You've built a complete application with Pheno-SDK. Here's what to explore next:

### 1. Advanced Features

**Workflow Orchestration:**
```bash
pip install workflow-kit
```
Learn about Saga pattern for distributed transactions.

**Vector Search:**
```bash
pip install vector-kit
```
Add semantic search to your application.

**Real-Time Streaming:**
```bash
pip install stream-kit
```
Build WebSocket and SSE endpoints.

### 2. Explore More Kits

- **[tui-kit](tui-kit/)** - Build terminal UIs for monitoring
- **[event-kit](event-kit/)** - Event-driven architecture
- **[orchestrator-kit](orchestrator-kit/)** - Multi-agent coordination
- **[mcp-sdk-kit](mcp-sdk-kit/)** - MCP server utilities

### 3. Learn Best Practices

Read:
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Design patterns and principles
- **[llms.txt](llms.txt)** - Comprehensive API reference
- **[docs/guides/](docs/guides/)** - Advanced guides

### 4. Join the Community

- **GitHub Discussions** - Ask questions and share projects
- **GitHub Issues** - Report bugs and request features
- **Contributing** - See [CONTRIBUTING.md](CONTRIBUTING.md)

### 5. Build Something Amazing!

Ideas for your next project:
- **REST API** with full observability
- **MCP Server** for AI agents
- **Microservices** with event-driven architecture
- **CLI Tool** with rich terminal UI
- **Real-Time Dashboard** with streaming updates

---

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Make sure packages are installed
pip list | grep kit

# Reinstall if needed
pip install --upgrade adapter-kit db-kit observability-kit
```

**Database Connection:**
```bash
# Check environment variables
echo $NEXT_PUBLIC_SUPABASE_URL
echo $NEXT_PUBLIC_SUPABASE_ANON_KEY

# Test connection
python -c "from db_kit import Database; db = Database.supabase(); print('Connected!')"
```

**Type Errors:**
```bash
# Install type stubs if needed
pip install types-requests types-pyyaml
```

### Getting Help

1. **Check Documentation:**
   - Individual kit READMEs
   - [llms.txt](llms.txt) for API reference
   - [ARCHITECTURE.md](ARCHITECTURE.md) for design patterns

2. **Search Issues:**
   - Check GitHub Issues for similar problems
   - Search GitHub Discussions

3. **Ask for Help:**
   - Create a GitHub Discussion
   - Open an issue with details

---

## Summary

You've learned how to:

- ✅ Install and configure Pheno-SDK
- ✅ Use configuration management
- ✅ Add structured logging and observability
- ✅ Integrate database operations
- ✅ Handle file storage
- ✅ Build REST APIs
- ✅ Add real-time communication
- ✅ Test your application
- ✅ Deploy to production

**You're now ready to build production-ready Python applications with Pheno-SDK!** 🚀

---

## Additional Resources

- **[README.md](README.md)** - SDK overview
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Design philosophy
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guide
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API docs
- **[llms.txt](llms.txt)** - AI-optimized comprehensive guide

---

<div align="center">

**Happy Building! 💙**

[Documentation](llms.txt) • [Architecture](ARCHITECTURE.md) • [Contributing](CONTRIBUTING.md)

</div>

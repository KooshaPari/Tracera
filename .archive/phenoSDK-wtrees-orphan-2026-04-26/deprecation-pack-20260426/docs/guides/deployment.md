# Deployment Guide

> Complete guide to deploying Pheno-SDK applications across different platforms

---

## Table of Contents

- [Overview](#overview)
- [Preparation](#preparation)
- [Vercel Deployment](#vercel-deployment)
- [Docker Deployment](#docker-deployment)
- [AWS Lambda](#aws-lambda)
- [Railway](#railway)
- [Fly.io](#flyio)
- [Self-Hosted](#self-hosted)
- [Best Practices](#best-practices)

---

## Overview

Pheno-SDK applications can be deployed to any Python-compatible platform. The `deploy-kit` provides utilities to simplify deployment across platforms.

### Deployment Checklist

- [ ] Application tested locally
- [ ] Environment variables configured
- [ ] Dependencies vendored (if needed)
- [ ] Database migrations applied
- [ ] Observability configured
- [ ] Health check endpoint implemented
- [ ] Error monitoring set up

---

## Preparation

### 1. Vendor Dependencies

For platforms with restricted file systems (Vercel, Lambda):

```bash
# Install deploy-kit
pip install deploy-kit

# Vendor pheno-sdk packages
pheno-vendor setup

# Validate vendored packages
pheno-vendor validate --test-imports
```

### 2. Environment Configuration

Create `.env.example`:

```bash
# Application
APP_NAME=my-pheno-app
APP_ENV=production
DEBUG=false

# Database
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Observability
LOG_LEVEL=INFO
SERVICE_NAME=my-service

# Storage (if using)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET=my-bucket
```

### 3. Health Check Endpoint

Add to your application:

```python
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }
```

---

## Vercel Deployment

### Step 1: Generate Config

```bash
pheno-vendor generate-hooks --platform vercel
```

### Step 2: Create `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api.py"
    }
  ],
  "env": {
    "PYTHONPATH": "pheno_vendor"
  }
}
```

### Step 3: Add Environment Variables

```bash
# Via CLI
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY

# Or via dashboard: vercel.com → project → settings → environment variables
```

### Step 4: Deploy

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy to production
vercel --prod
```

### Vercel-Specific Considerations

- **Size Limit:** 50MB max (use vendoring)
- **Cold Starts:** First request may be slow
- **Timeout:** 10s for hobby, 60s for pro
- **Memory:** 1024MB default

---

## Docker Deployment

### Step 1: Generate Dockerfile

```bash
pheno-vendor generate-hooks --platform docker --output Dockerfile
```

### Step 2: Customize Dockerfile

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Vendor pheno-sdk (if needed)
RUN pip install deploy-kit && pheno-vendor setup --no-validate

# Set environment
ENV PYTHONPATH=/app/pheno_vendor
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run application
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT}
```

### Step 3: Build and Run

```bash
# Build
docker build -t my-pheno-app .

# Run locally
docker run -p 8000:8000 \
  -e NEXT_PUBLIC_SUPABASE_URL="your-url" \
  -e NEXT_PUBLIC_SUPABASE_ANON_KEY="your-key" \
  my-pheno-app

# Test
curl http://localhost:8000/health
```

### Step 4: Deploy to Registry

```bash
# Tag for registry
docker tag my-pheno-app registry.example.com/my-pheno-app:latest

# Push
docker push registry.example.com/my-pheno-app:latest
```

### Docker Compose

For local development with dependencies:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./storage:/app/storage

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

volumes:
  postgres_data:
  redis_data:
```

---

## AWS Lambda

### Step 1: Generate Build Script

```bash
pheno-vendor generate-hooks --platform lambda
```

### Step 2: Create Lambda Handler

```python
# lambda_handler.py
from mangum import Mangum
from api import app

# Wrap FastAPI with Mangum for Lambda
handler = Mangum(app, lifespan="off")
```

### Step 3: Package Application

```bash
# Install dependencies
pip install -r requirements.txt -t package/

# Copy application files
cp -r api.py lambda_handler.py pheno_vendor/ package/

# Create deployment package
cd package && zip -r ../deployment.zip . && cd ..
```

### Step 4: Deploy with AWS CLI

```bash
# Create Lambda function
aws lambda create-function \
  --function-name my-pheno-app \
  --runtime python3.10 \
  --handler lambda_handler.handler \
  --zip-file fileb://deployment.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{
    NEXT_PUBLIC_SUPABASE_URL=your-url,
    NEXT_PUBLIC_SUPABASE_ANON_KEY=your-key
  }"

# Update function
aws lambda update-function-code \
  --function-name my-pheno-app \
  --zip-file fileb://deployment.zip
```

### Step 5: API Gateway

```bash
# Create REST API
aws apigatewayv2 create-api \
  --name my-pheno-app \
  --protocol-type HTTP \
  --target arn:aws:lambda:REGION:ACCOUNT_ID:function:my-pheno-app
```

### Lambda Considerations

- **Size Limit:** 50MB zipped, 250MB unzipped
- **Timeout:** Max 15 minutes
- **Memory:** 128MB - 10GB
- **Cold Starts:** Use provisioned concurrency for critical apps

---

## Railway

### Step 1: Create `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
```

### Step 2: Configure Nixpacks

Create `nixpacks.toml`:

```toml
[phases.setup]
nixPkgs = ["python310", "pip"]

[phases.install]
cmds = [
  "pip install -r requirements.txt",
  "pip install deploy-kit",
  "pheno-vendor setup --no-validate"
]

[phases.build]
cmds = ["echo 'Build complete'"]

[start]
cmd = "uvicorn api:app --host 0.0.0.0 --port $PORT"
```

### Step 3: Deploy

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

---

## Fly.io

### Step 1: Create `fly.toml`

```toml
app = "my-pheno-app"
primary_region = "sea"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"
  PYTHONPATH = "pheno_vendor"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

  [[http_service.checks]]
    grace_period = "10s"
    interval = "30s"
    method = "GET"
    timeout = "5s"
    path = "/health"

[[services]]
  protocol = "tcp"
  internal_port = 8000

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[[ services.tcp_checks ]]
  interval = "15s"
  timeout = "2s"
  grace_period = "1s"
```

### Step 2: Deploy

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
flyctl launch

# Set secrets
flyctl secrets set NEXT_PUBLIC_SUPABASE_URL="your-url"
flyctl secrets set NEXT_PUBLIC_SUPABASE_ANON_KEY="your-key"

# Deploy
flyctl deploy
```

---

## Self-Hosted

### Using Systemd

Create `/etc/systemd/system/pheno-app.service`:

```ini
[Unit]
Description=Pheno-SDK Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/pheno-app
Environment="PYTHONPATH=/opt/pheno-app/pheno_vendor"
Environment="PORT=8000"
EnvironmentFile=/opt/pheno-app/.env
ExecStart=/opt/pheno-app/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable pheno-app
sudo systemctl start pheno-app
sudo systemctl status pheno-app
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

---

## Best Practices

### 1. Environment Management

```python
# Use config-kit for configuration
from config_kit import Config

class ProductionConfig(Config):
    debug: bool = False
    log_level: str = "INFO"
    database_pool_size: int = 20

config = ProductionConfig.from_env()
```

### 2. Graceful Shutdown

```python
import signal

def handle_shutdown(signum, frame):
    logger.info("Shutting down gracefully")
    # Close database connections
    # Flush metrics
    # Stop background tasks
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)
```

### 3. Health Checks

```python
@app.get("/health")
async def health():
    """Comprehensive health check."""
    try:
        # Check database
        await db.query("users", limit=1)

        # Check cache (if used)
        # await cache.ping()

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": os.getenv("APP_VERSION", "unknown")
        }
    except Exception as e:
        logger.error("Health check failed", exc_info=e)
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )
```

### 4. Monitoring

```python
# Add Prometheus metrics endpoint
from observability import MetricsCollector, PrometheusExporter

metrics = MetricsCollector()
exporter = PrometheusExporter(metrics)
exporter.setup_fastapi(app, path="/metrics")
```

### 5. Error Tracking

```python
# Log errors with context
try:
    result = await process_request(request_id)
except Exception as e:
    logger.error("Request processing failed",
        request_id=request_id,
        user_id=user_id,
        exc_info=e
    )
    # Send to error tracking service (Sentry, etc.)
    raise
```

### 6. Database Migrations

```bash
# Use Alembic for migrations
alembic revision --autogenerate -m "Add users table"
alembic upgrade head
```

### 7. Security

- Use environment variables for secrets
- Enable HTTPS/TLS
- Implement rate limiting
- Use RLS for multi-tenant data
- Validate all input
- Keep dependencies updated

---

## Troubleshooting

### Deployment Fails

```bash
# Check logs
vercel logs
docker logs container-id
kubectl logs pod-name

# Validate configuration
pheno-vendor validate --test-imports

# Test locally first
python -c "import api; print('OK')"
```

### Import Errors

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=pheno_vendor

# Check vendored packages
ls pheno_vendor/
```

### Performance Issues

- Enable query caching in db-kit
- Use connection pooling
- Monitor with observability-kit
- Profile with cProfile
- Scale horizontally

---

## Summary

Choose the right platform for your needs:

- **Vercel:** Fast deployment, serverless, great for APIs
- **Docker:** Maximum flexibility, works everywhere
- **AWS Lambda:** Pay-per-use, scales automatically
- **Railway:** Simple, batteries-included platform
- **Fly.io:** Edge deployment, low latency
- **Self-Hosted:** Full control, custom infrastructure

All platforms work great with Pheno-SDK. Use `deploy-kit` to simplify the process!

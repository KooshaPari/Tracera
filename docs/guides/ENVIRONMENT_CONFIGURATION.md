# Environment Configuration Guide

Complete reference for all environment variables in TracerTM, covering development and production configurations.

## Table of Contents

- [Overview](#overview)
- [Configuration Hierarchy](#configuration-hierarchy)
- [Database Configuration](#database-configuration)
- [Cache and Message Broker](#cache-and-message-broker)
- [Authentication and Authorization](#authentication-and-authorization)
- [External Integrations](#external-integrations)
- [Embeddings and AI](#embeddings-and-ai)
- [Service Communication](#service-communication)
- [Application Settings](#application-settings)
- [Security Configuration](#security-configuration)
- [Feature Flags](#feature-flags)
- [Monitoring and Logging](#monitoring-and-logging)
- [Development vs Production](#development-vs-production)
- [Secret Management](#secret-management)
- [Configuration Validation](#configuration-validation)

---

## Overview

TracerTM uses environment variables for configuration across all services. Configuration is loaded from:

1. `.env` file in project root (development)
2. `/etc/tracertm/.env` (production)
3. Docker Compose environment variables
4. System environment variables (highest priority)

### Environment Files

```
.
├── .env.example          # Template with all variables
├── .env                  # Development configuration (gitignored)
├── backend/.env          # Backend-specific overrides
├── frontend/.env.local   # Frontend-specific variables
└── /etc/tracertm/.env    # Production configuration
```

### Variable Naming Convention

- **Uppercase with underscores**: `DATABASE_URL`, `JWT_SECRET`
- **Service prefixes**: `WORKOS_*`, `GITHUB_*`, `VOYAGE_*`
- **Boolean values**: `true` or `false` (lowercase)
- **Numeric values**: No quotes

---

## Configuration Hierarchy

### Priority Order (Highest to Lowest)

1. **System environment variables**
2. **Docker Compose `environment:` section**
3. **`.env` file**
4. **Service defaults**

### Required vs Optional

| Symbol | Meaning |
|--------|---------|
| **[REQUIRED]** | Must be set for service to start |
| **[OPTIONAL]** | Has a default value |
| **[PRODUCTION]** | Only required in production |
| **[DEVELOPMENT]** | Only used in development |

---

## Database Configuration

### PostgreSQL

```bash
# [REQUIRED] Primary database connection
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Individual components (alternative to DATABASE_URL)
DB_HOST=localhost              # [REQUIRED] Database host
DB_PORT=5432                   # [OPTIONAL] Default: 5432
DB_USER=tracertm               # [REQUIRED] Database user
DB_PASSWORD=your_password      # [REQUIRED] Database password
DB_NAME=tracertm               # [REQUIRED] Database name
DB_SSLMODE=disable             # [OPTIONAL] SSL mode: disable, require, verify-ca, verify-full

# Connection pooling
DB_MAX_CONNECTIONS=100         # [OPTIONAL] Max connections in pool (default: 100)
DB_MIN_CONNECTIONS=10          # [OPTIONAL] Min connections in pool (default: 10)
DB_CONNECTION_TIMEOUT=30       # [OPTIONAL] Connection timeout in seconds (default: 30)
DB_POOL_SIZE=20                # [OPTIONAL] Python backend pool size (default: 20)
DB_MAX_OVERFLOW=10             # [OPTIONAL] Python backend overflow (default: 10)
DB_ECHO=false                  # [DEVELOPMENT] Log SQL queries (default: false)
```

**Development Example:**
```bash
DATABASE_URL=postgresql+asyncpg://tracertm:devpassword@localhost:5432/tracertm
DB_ECHO=true
```

**Production Example:**
```bash
DATABASE_URL=postgresql+asyncpg://tracertm:STRONG_PROD_PASS@db.internal:5432/tracertm
DB_SSLMODE=require
DB_MAX_CONNECTIONS=200
```

### Neo4j (Optional)

```bash
# [OPTIONAL] Graph database for advanced features
NEO4J_URI=neo4j://localhost:7687    # [OPTIONAL] Neo4j connection URI
NEO4J_USER=neo4j                     # [OPTIONAL] Neo4j username
NEO4J_PASSWORD=neo4j_password        # [OPTIONAL] Neo4j password
NEO4J_DATABASE=neo4j                 # [OPTIONAL] Database name (default: neo4j)
NEO4J_MAX_CONNECTION_LIFETIME=3600   # [OPTIONAL] Max connection lifetime
NEO4J_MAX_CONNECTION_POOL_SIZE=50    # [OPTIONAL] Max connections
```

**Example:**
```bash
NEO4J_URI=neo4j+s://xxx.databases.neo4j.io:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

---

## Cache and Message Broker

### Redis

```bash
# [REQUIRED] Cache connection
REDIS_URL=redis://localhost:6379           # Full connection URL

# Or individual components
REDIS_HOST=localhost                       # [REQUIRED] Redis host
REDIS_PORT=6379                            # [OPTIONAL] Default: 6379
REDIS_PASSWORD=                            # [PRODUCTION] Redis password
REDIS_DB=0                                 # [OPTIONAL] Database number (default: 0)

# Connection settings
REDIS_MAX_CONNECTIONS=50                   # [OPTIONAL] Max connections (default: 50)
REDIS_SOCKET_TIMEOUT=5                     # [OPTIONAL] Socket timeout (default: 5)
REDIS_SOCKET_CONNECT_TIMEOUT=5             # [OPTIONAL] Connect timeout (default: 5)

# Cache settings
CACHE_TTL=3600                             # [OPTIONAL] Default TTL in seconds (default: 3600)
CACHE_PREFIX=tracertm:                     # [OPTIONAL] Key prefix (default: "tracertm:")
```

**Development Example:**
```bash
REDIS_URL=redis://localhost:6379
CACHE_TTL=300  # 5 minutes for faster testing
```

**Production Example:**
```bash
REDIS_URL=redis://:STRONG_PASSWORD@redis.internal:6379/0
REDIS_MAX_CONNECTIONS=100
CACHE_TTL=3600
```

### NATS

```bash
# [REQUIRED] Message broker
NATS_URL=nats://localhost:4222             # NATS server URL

# For NATS Cloud (NGS)
# NATS_URL=nats://connect.ngs.global:4222
# NATS_CREDS=/path/to/credentials.creds    # [OPTIONAL] Credentials file

# JetStream settings
NATS_STREAM_NAME=tracertm                  # [OPTIONAL] Stream name (default: tracertm)
NATS_CONSUMER_NAME=tracertm-worker         # [OPTIONAL] Consumer name
NATS_MAX_DELIVER=3                         # [OPTIONAL] Max delivery attempts (default: 3)
```

**Production with NGS:**
```bash
NATS_URL=nats://connect.ngs.global:4222
NATS_CREDS=/etc/tracertm/ngs-credentials.creds
```

---

## Authentication and Authorization

### WorkOS AuthKit

```bash
# [REQUIRED] WorkOS configuration
WORKOS_CLIENT_ID=client_XXXXXXXXXX         # [REQUIRED] WorkOS Client ID
WORKOS_API_KEY=sk_test_XXXXXXXXXX          # [REQUIRED] WorkOS API Key
WORKOS_API_BASE_URL=https://api.workos.com # [OPTIONAL] API base URL
WORKOS_JWKS_URL=https://api.workos.com/sso/jwks/${WORKOS_CLIENT_ID}
WORKOS_JWT_ISSUER=https://api.workos.com/
WORKOS_JWT_AUDIENCE=${WORKOS_CLIENT_ID}

# Redirect URLs (must match WorkOS dashboard)
WORKOS_REDIRECT_URI=http://localhost:3000/auth/callback     # [REQUIRED]
WORKOS_CALLBACK_URL=${WORKOS_REDIRECT_URI}                  # Alias
```

**Development Example:**
```bash
WORKOS_CLIENT_ID=client_test_123abc
WORKOS_API_KEY=sk_test_abc123def456
WORKOS_REDIRECT_URI=http://localhost:3000/auth/callback
```

**Production Example:**
```bash
WORKOS_CLIENT_ID=client_live_xyz789
WORKOS_API_KEY=sk_live_xyz789abc123
WORKOS_REDIRECT_URI=https://tracertm.example.com/auth/callback
```

### JWT (Service-to-Service)

```bash
# [REQUIRED] Internal service authentication
JWT_SECRET=your_random_32_byte_hex_string  # [REQUIRED] HS256 secret key
JWT_EXPIRY=24h                             # [OPTIONAL] Token expiry (default: 24h)
JWT_ALGORITHM=HS256                        # [OPTIONAL] Algorithm (default: HS256)
```

**Generate JWT Secret:**
```bash
openssl rand -hex 32
```

**Production:**
```bash
JWT_SECRET=8f3a7b2c9d4e1f6a5b8c7d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a
JWT_EXPIRY=12h  # Shorter expiry for production
```

### Session Management

```bash
# [PRODUCTION] Session configuration
SESSION_SECRET=session_secret_key          # [REQUIRED] Session signing key
SESSION_TIMEOUT=3600                       # [OPTIONAL] Session timeout (seconds)
SESSION_SECURE=true                        # [PRODUCTION] Require HTTPS (default: false)
SESSION_HTTPONLY=true                      # [OPTIONAL] HttpOnly flag (default: true)
SESSION_SAMESITE=strict                    # [OPTIONAL] SameSite policy (strict/lax/none)
```

---

## External Integrations

### GitHub App

```bash
# [OPTIONAL] GitHub integration
GITHUB_APP_ID=123456                       # [OPTIONAL] GitHub App ID
GITHUB_APP_CLIENT_ID=Iv_XXXXXXXXXX         # [OPTIONAL] OAuth Client ID
GITHUB_APP_CLIENT_SECRET=secret_abc123     # [OPTIONAL] OAuth Client Secret
GITHUB_WEBHOOK_SECRET=webhook_secret       # [OPTIONAL] Webhook secret
GITHUB_PRIVATE_KEY_PATH=/path/to/key.pem   # [OPTIONAL] Private key file path

# Alternative: Inline private key
# GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
```

**Setup Instructions:**
See [GitHub App Setup Guide](https://docs.github.com/apps/creating-github-apps)

### Temporal Workflow Engine

```bash
# [OPTIONAL] Temporal configuration
TEMPORAL_HOST=localhost:7233               # [OPTIONAL] Temporal server address
TEMPORAL_NAMESPACE=default                 # [OPTIONAL] Namespace (default: default)

# For Temporal Cloud
# TEMPORAL_HOST=namespace.tmprl.cloud:7233
# TEMPORAL_NAMESPACE=namespace
# TEMPORAL_TLS_CERT=/path/to/client.pem
# TEMPORAL_TLS_KEY=/path/to/client.key
```

---

## Embeddings and AI

### VoyageAI (Recommended)

```bash
# [OPTIONAL] VoyageAI embeddings
EMBEDDING_PROVIDER=voyage                  # [OPTIONAL] Provider: voyage, openrouter, local
VOYAGE_API_KEY=pa_XXXXXXXXXX               # [REQUIRED if provider=voyage]
VOYAGE_MODEL=voyage-3.5                    # [OPTIONAL] Model (default: voyage-3.5)
VOYAGE_DIMENSIONS=1024                     # [OPTIONAL] Dimensions (default: 1024)

# Reranking
RERANK_ENABLED=true                        # [OPTIONAL] Enable reranking (default: true)
RERANK_MODEL=rerank-2.5                    # [OPTIONAL] Rerank model (default: rerank-2.5)

# Performance
EMBEDDING_RATE_LIMIT=300                   # [OPTIONAL] Requests per minute (default: 300)
EMBEDDING_TIMEOUT=60                       # [OPTIONAL] Request timeout (default: 60)
EMBEDDING_MAX_RETRIES=3                    # [OPTIONAL] Max retries (default: 3)
EMBEDDING_BATCH_SIZE=128                   # [OPTIONAL] Batch size (default: 128)
```

**Get API Key:**
https://www.voyageai.com/

### OpenRouter (Alternative)

```bash
# [OPTIONAL] OpenRouter embeddings
EMBEDDING_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-XXXXXXXXXX    # [REQUIRED if provider=openrouter]
OPENROUTER_MODEL=openai/text-embedding-3-small
```

### Local Embeddings

```bash
# [OPTIONAL] Local embeddings (no API key needed)
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=nomic-embed-text-v1.5
EMBEDDING_DIMENSIONS=768
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
EMBEDDING_CACHE_DIR=/var/cache/embeddings
```

### Background Indexer

```bash
# [OPTIONAL] Embedding indexer configuration
INDEXER_ENABLED=true                       # [OPTIONAL] Enable indexer (default: true)
INDEXER_WORKERS=3                          # [OPTIONAL] Worker threads (default: 3)
INDEXER_BATCH_SIZE=50                      # [OPTIONAL] Batch size (default: 50)
INDEXER_POLL_INTERVAL=30                   # [OPTIONAL] Poll interval in seconds (default: 30)
```

---

## Service Communication

### Service URLs

```bash
# [REQUIRED] Inter-service communication
GO_BACKEND_URL=http://localhost:8080       # [REQUIRED] Go backend URL
PYTHON_BACKEND_URL=http://localhost:8000   # [REQUIRED] Python backend URL (internal; clients use gateway :4000)

# Service-to-service authentication
SERVICE_TOKEN=shared_service_token         # [REQUIRED] Inter-service auth token
```

**Docker Compose Example:**
```bash
GO_BACKEND_URL=http://go-backend:8080
PYTHON_BACKEND_URL=http://python-backend:8000
```

### gRPC

```bash
# [OPTIONAL] gRPC configuration
GRPC_PORT=9090                             # [OPTIONAL] gRPC port (default: 9090)
GRPC_GO_BACKEND_HOST=localhost:9090        # [OPTIONAL] gRPC server address
```

---

## Application Settings

### Go Backend

```bash
# [REQUIRED] Go application settings
PORT=8080                                  # [OPTIONAL] HTTP port (default: 8080)
GIN_MODE=release                           # [OPTIONAL] Gin mode: debug, release (default: debug)

# Performance
GO_MAX_PROCS=0                             # [OPTIONAL] Max Go processes (0 = all CPUs)
GO_GC_PERCENT=100                          # [OPTIONAL] GC trigger percentage
```

**Development:**
```bash
PORT=8080
GIN_MODE=debug
```

**Production:**
```bash
PORT=8080
GIN_MODE=release
GO_MAX_PROCS=8
```

### Python Backend

```bash
# [REQUIRED] Python application settings
LOG_LEVEL=INFO                             # [OPTIONAL] Log level: DEBUG, INFO, WARN, ERROR
REALTIME_PROVIDER=nats                     # [OPTIONAL] Realtime provider: nats, redis

# Performance
UVICORN_WORKERS=4                          # [OPTIONAL] Number of workers
UVICORN_HOST=0.0.0.0                       # [OPTIONAL] Bind address
UVICORN_PORT=8000                          # [OPTIONAL] Port
```

**Development:**
```bash
LOG_LEVEL=DEBUG
UVICORN_WORKERS=1
```

**Production:**
```bash
LOG_LEVEL=INFO
UVICORN_WORKERS=4
```

### Frontend

```bash
# [REQUIRED] Frontend configuration
VITE_API_BASE_URL=http://localhost:4000    # [REQUIRED] API base URL
VITE_WS_URL=ws://localhost:4000/ws         # [REQUIRED] WebSocket URL
VITE_WORKOS_CLIENT_ID=${WORKOS_CLIENT_ID}  # [REQUIRED] WorkOS Client ID

# [DEVELOPMENT] Feature flags
VITE_ENABLE_MOCK_DATA=false
VITE_ENABLE_DEBUG=false
```

**Production:**
```bash
VITE_API_BASE_URL=https://api.tracertm.example.com
VITE_WS_URL=wss://api.tracertm.example.com/ws
VITE_WORKOS_CLIENT_ID=client_live_xyz789
```

---

## Security Configuration

### CORS

```bash
# [REQUIRED] CORS configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000 # [REQUIRED] Comma-separated origins
CORS_ALLOW_CREDENTIALS=true                # [OPTIONAL] Allow credentials (default: true)
CORS_MAX_AGE=3600                          # [OPTIONAL] Preflight cache (default: 3600)
```

**Development:**
```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Production:**
```bash
CORS_ALLOWED_ORIGINS=https://tracertm.example.com
```

### Rate Limiting

```bash
# [PRODUCTION] Rate limiting
RATE_LIMIT_ENABLED=true                    # [OPTIONAL] Enable rate limiting (default: false)
RATE_LIMIT_REQUESTS=100                    # [OPTIONAL] Max requests (default: 100)
RATE_LIMIT_WINDOW=60                       # [OPTIONAL] Window in seconds (default: 60)
RATE_LIMIT_STRATEGY=sliding_window         # [OPTIONAL] Strategy: fixed_window, sliding_window
```

### Content Security Policy

```bash
# [PRODUCTION] CSP headers
CSP_ENABLED=true                           # [OPTIONAL] Enable CSP (default: false)
CSP_REPORT_ONLY=false                      # [OPTIONAL] Report-only mode (default: false)
CSP_REPORT_URI=/api/v1/csp-report          # [OPTIONAL] Report URI
```

---

## Feature Flags

```bash
# Feature toggles
ENABLE_WEBSOCKET=true                      # [OPTIONAL] WebSocket support (default: true)
ENABLE_EVENTS=true                         # [OPTIONAL] Event streaming (default: true)
ENABLE_SEARCH=true                         # [OPTIONAL] Search functionality (default: true)
ENABLE_VECTOR_SEARCH=true                  # [OPTIONAL] Vector search (default: true)
ENABLE_NATS=true                           # [OPTIONAL] NATS messaging (default: true)
ENABLE_REDIS_CACHE=true                    # [OPTIONAL] Redis caching (default: true)
ENABLE_NEO4J=false                         # [OPTIONAL] Neo4j graph (default: false)
ENABLE_TEMPORAL=false                      # [OPTIONAL] Temporal workflows (default: false)
```

---

## Monitoring and Logging

### Prometheus

```bash
# [PRODUCTION] Prometheus metrics
PROMETHEUS_ENABLED=true                    # [OPTIONAL] Enable metrics (default: true)
PROMETHEUS_PORT=9090                       # [OPTIONAL] Metrics port (default: 9090)
```

### Grafana

```bash
# [PRODUCTION] Grafana configuration
GRAFANA_ADMIN_USER=admin                   # [OPTIONAL] Admin username (default: admin)
GRAFANA_ADMIN_PASSWORD=admin               # [REQUIRED in production]
GRAFANA_INSTALL_PLUGINS=                   # [OPTIONAL] Comma-separated plugin list
```

**Production:**
```bash
GRAFANA_ADMIN_PASSWORD=STRONG_PASSWORD
GRAFANA_INSTALL_PLUGINS=redis-datasource,grafana-piechart-panel
```

### Logging

```bash
# Log configuration
LOG_FORMAT=json                            # [OPTIONAL] Format: json, text (default: json)
LOG_OUTPUT=stdout                          # [OPTIONAL] Output: stdout, file (default: stdout)
LOG_FILE=/var/log/tracertm/app.log         # [OPTIONAL if LOG_OUTPUT=file]
```

---

## Development vs Production

### Development Environment

```bash
# Minimal required variables for local development
DATABASE_URL=postgresql+asyncpg://tracertm:devpass@localhost:5432/tracertm
REDIS_URL=redis://localhost:6379
NATS_URL=nats://localhost:4222
WORKOS_CLIENT_ID=client_test_123
WORKOS_API_KEY=sk_test_123
JWT_SECRET=dev_secret_key_32_chars_minimum
GO_BACKEND_URL=http://localhost:8080
PYTHON_BACKEND_URL=http://localhost:8000
LOG_LEVEL=DEBUG
GIN_MODE=debug
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Production Environment

```bash
# Essential production variables
DATABASE_URL=postgresql+asyncpg://tracertm:PROD_PASS@db.internal:5432/tracertm
DB_SSLMODE=require
DB_MAX_CONNECTIONS=200
REDIS_URL=redis://:REDIS_PASS@redis.internal:6379/0
REDIS_MAX_CONNECTIONS=100
NATS_URL=nats://connect.ngs.global:4222
NATS_CREDS=/etc/tracertm/ngs.creds
WORKOS_CLIENT_ID=client_live_xyz
WORKOS_API_KEY=sk_live_xyz
JWT_SECRET=PRODUCTION_SECRET_64_CHARS_MINIMUM
GO_BACKEND_URL=http://go-backend:8080
PYTHON_BACKEND_URL=http://python-backend:8000
LOG_LEVEL=INFO
GIN_MODE=release
CORS_ALLOWED_ORIGINS=https://tracertm.example.com
RATE_LIMIT_ENABLED=true
SESSION_SECURE=true
GRAFANA_ADMIN_PASSWORD=STRONG_PASSWORD
```

---

## Secret Management

### Development

```bash
# Create .env file from template
cp .env.example .env

# Edit with your values
nano .env
```

### Production

#### Option 1: Secure File

```bash
# Create secure directory
sudo mkdir -p /etc/tracertm
sudo touch /etc/tracertm/.env
sudo chmod 600 /etc/tracertm/.env
sudo chown root:docker /etc/tracertm/.env

# Edit file
sudo nano /etc/tracertm/.env

# Reference in docker-compose.yml
env_file:
  - /etc/tracertm/.env
```

#### Option 2: Docker Secrets

```bash
# Create secrets
echo "DB_PASSWORD" | docker secret create db_password -
echo "JWT_SECRET" | docker secret create jwt_secret -

# Use in docker-compose.yml
secrets:
  - db_password
  - jwt_secret

# Read in application
password=$(cat /run/secrets/db_password)
```

#### Option 3: HashiCorp Vault

```bash
# Store in Vault
vault kv put secret/tracertm/prod \
  db_password="PASSWORD" \
  jwt_secret="SECRET"

# Retrieve
export DB_PASSWORD=$(vault kv get -field=db_password secret/tracertm/prod)
```

---

## Configuration Validation

### Validation Script

Create `/opt/tracertm/scripts/validate-config.sh`:

```bash
#!/bin/bash
set -euo pipefail

echo "Validating TracerTM Configuration"
echo "=================================="

# Load environment
source .env

# Required variables
REQUIRED_VARS=(
  "DATABASE_URL"
  "REDIS_URL"
  "NATS_URL"
  "WORKOS_CLIENT_ID"
  "WORKOS_API_KEY"
  "JWT_SECRET"
  "GO_BACKEND_URL"
  "PYTHON_BACKEND_URL"
)

# Check required variables
for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var:-}" ]; then
    echo "❌ Missing required variable: $var"
    exit 1
  else
    echo "✅ $var is set"
  fi
done

# Validate JWT secret length
if [ ${#JWT_SECRET} -lt 32 ]; then
  echo "❌ JWT_SECRET must be at least 32 characters"
  exit 1
fi

# Validate database connection
if ! docker compose exec -T postgres pg_isready -d "${DB_NAME}" -U "${DB_USER}" > /dev/null 2>&1; then
  echo "❌ Cannot connect to database"
  exit 1
else
  echo "✅ Database connection successful"
fi

# Validate Redis connection
if ! docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
  echo "❌ Cannot connect to Redis"
  exit 1
else
  echo "✅ Redis connection successful"
fi

echo ""
echo "✅ All configuration checks passed!"
```

### Run Validation

```bash
chmod +x /opt/tracertm/scripts/validate-config.sh
./scripts/validate-config.sh
```

---

## Quick Reference Tables

### By Service

| Service | Required Variables |
|---------|-------------------|
| **Go Backend** | `DATABASE_URL`, `REDIS_URL`, `NATS_URL`, `JWT_SECRET`, `PORT` |
| **Python Backend** | `DATABASE_URL`, `REDIS_URL`, `NATS_URL`, `LOG_LEVEL` |
| **Frontend** | `VITE_API_BASE_URL`, `VITE_WS_URL`, `VITE_WORKOS_CLIENT_ID` |
| **Authentication** | `WORKOS_CLIENT_ID`, `WORKOS_API_KEY`, `JWT_SECRET` |

### By Environment

| Variable | Development | Production |
|----------|-------------|------------|
| `GIN_MODE` | `debug` | `release` |
| `LOG_LEVEL` | `DEBUG` | `INFO` |
| `DB_SSLMODE` | `disable` | `require` |
| `SESSION_SECURE` | `false` | `true` |
| `RATE_LIMIT_ENABLED` | `false` | `true` |

---

For additional information, see:

- [Production Deployment Guide](/docs/guides/PRODUCTION_DEPLOYMENT.md)
- [Operations Runbook](/docs/guides/OPERATIONS_RUNBOOK.md)
- [Troubleshooting Guide](/docs/guides/TROUBLESHOOTING.md)

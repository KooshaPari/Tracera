# Production Deployment Guide

Complete guide for deploying TracerTM to production environments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Production vs Development](#production-vs-development)
- [Environment Configuration](#environment-configuration)
- [SSL/TLS Setup](#ssltls-setup)
- [Service Deployment](#service-deployment)
- [Security Hardening](#security-hardening)
- [Monitoring Setup](#monitoring-setup)
- [Backup and Disaster Recovery](#backup-and-disaster-recovery)
- [Post-Deployment Verification](#post-deployment-verification)

---

## Overview

TracerTM production deployment uses Docker Compose to orchestrate the following services:

- **Nginx** - API Gateway and load balancer
- **Go Backend** - Core API server
- **Python Backend** - Specifications and execution engine
- **PostgreSQL** - Primary database
- **Redis** - Caching layer
- **NATS** - Message broker with JetStream
- **Prometheus** - Metrics collection
- **Grafana** - Monitoring dashboards

---

## Prerequisites

### System Requirements

**Minimum Production Server:**
- **CPU:** 4 cores
- **RAM:** 8GB
- **Storage:** 50GB SSD
- **OS:** Ubuntu 22.04 LTS or similar

**Recommended Production Server:**
- **CPU:** 8+ cores
- **RAM:** 16GB+
- **Storage:** 100GB+ SSD with RAID
- **OS:** Ubuntu 22.04 LTS

### Required Software

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify installations
docker --version
docker compose version
```

### Domain and DNS

- Register a domain name
- Configure DNS A record pointing to your server IP
- Wait for DNS propagation (can take up to 48 hours)

```bash
# Verify DNS propagation
dig +short yourdomain.com
```

---

## Production vs Development

### Key Differences

| Aspect | Development | Production |
|--------|-------------|------------|
| **Port Exposure** | All ports exposed | Only 80/443 exposed |
| **SSL/TLS** | Optional (HTTP) | Required (HTTPS) |
| **Auth** | Relaxed | Strict enforcement |
| **Logging** | DEBUG level | INFO/WARN level |
| **CORS** | Permissive | Restricted origins |
| **Secrets** | `.env` files | Secrets management |
| **Health Checks** | Optional | Required |
| **Resource Limits** | None | CPU/Memory limits |
| **Restart Policy** | `no` | `unless-stopped` |
| **Database** | Local | Managed service |
| **Backups** | None | Automated |
| **Monitoring** | Optional | Required |

### Service Configuration

**Development (`GIN_MODE=debug`):**
- Detailed error messages
- Hot reload enabled
- CORS allows localhost
- All routes accessible

**Production (`GIN_MODE=release`):**
- Generic error messages
- No hot reload
- CORS restricted to domain
- Rate limiting enabled

---

## Environment Configuration

### Production Environment Variables

Create `/etc/tracertm/.env` with production values:

```bash
# ==============================================================================
# PRODUCTION ENVIRONMENT CONFIGURATION
# ==============================================================================

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
# Use managed PostgreSQL (AWS RDS, DigitalOcean, etc.) in production
DATABASE_URL=postgresql+asyncpg://tracertm:STRONG_PASSWORD@db-host:5432/tracertm
DB_HOST=db-host.region.provider.com
DB_PORT=5432
DB_USER=tracertm
DB_PASSWORD=STRONG_RANDOM_PASSWORD_HERE
DB_NAME=tracertm
DB_SSLMODE=require

# Connection pooling for production
DB_MAX_CONNECTIONS=100
DB_MIN_CONNECTIONS=10
DB_CONNECTION_TIMEOUT=30

# -----------------------------------------------------------------------------
# Redis Cache
# -----------------------------------------------------------------------------
# Use managed Redis (AWS ElastiCache, DigitalOcean, etc.)
REDIS_URL=redis://:REDIS_PASSWORD@redis-host:6379/0
REDIS_HOST=redis-host.region.provider.com
REDIS_PORT=6379
REDIS_PASSWORD=STRONG_REDIS_PASSWORD
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50

# -----------------------------------------------------------------------------
# NATS Message Broker
# -----------------------------------------------------------------------------
NATS_URL=nats://nats-host:4222
# For NATS Cloud (recommended for production):
# NATS_URL=nats://connect.ngs.global:4222
# NATS_CREDS=/etc/tracertm/ngs-credentials.creds

# -----------------------------------------------------------------------------
# Authentication (WorkOS AuthKit)
# -----------------------------------------------------------------------------
WORKOS_CLIENT_ID=client_PRODUCTION_ID
WORKOS_API_KEY=sk_live_PRODUCTION_KEY
WORKOS_API_BASE_URL=https://api.workos.com
WORKOS_JWKS_URL=https://api.workos.com/sso/jwks/${WORKOS_CLIENT_ID}
WORKOS_JWT_ISSUER=https://api.workos.com/
WORKOS_JWT_AUDIENCE=${WORKOS_CLIENT_ID}

# -----------------------------------------------------------------------------
# JWT Secret (Service-to-Service)
# -----------------------------------------------------------------------------
# Generate with: openssl rand -hex 32
JWT_SECRET=PRODUCTION_JWT_SECRET_64_CHARS_MINIMUM
JWT_EXPIRY=24h

# -----------------------------------------------------------------------------
# GitHub App Integration
# -----------------------------------------------------------------------------
GITHUB_APP_ID=YOUR_PRODUCTION_APP_ID
GITHUB_APP_CLIENT_ID=Iv_PRODUCTION_CLIENT_ID
GITHUB_APP_CLIENT_SECRET=PRODUCTION_CLIENT_SECRET
GITHUB_WEBHOOK_SECRET=PRODUCTION_WEBHOOK_SECRET
GITHUB_PRIVATE_KEY_PATH=/etc/tracertm/github-app-private-key.pem

# -----------------------------------------------------------------------------
# Embeddings Provider (VoyageAI)
# -----------------------------------------------------------------------------
EMBEDDING_PROVIDER=voyage
VOYAGE_API_KEY=pa_PRODUCTION_KEY
VOYAGE_MODEL=voyage-3.5
VOYAGE_DIMENSIONS=1024
RERANK_ENABLED=true
RERANK_MODEL=rerank-2.5

# Performance Settings
EMBEDDING_RATE_LIMIT=300
EMBEDDING_TIMEOUT=60
EMBEDDING_MAX_RETRIES=3
EMBEDDING_BATCH_SIZE=128

# Background Indexer
INDEXER_ENABLED=true
INDEXER_WORKERS=5
INDEXER_BATCH_SIZE=100
INDEXER_POLL_INTERVAL=30

# -----------------------------------------------------------------------------
# Object Storage (S3)
# -----------------------------------------------------------------------------
# Use managed S3-compatible service (AWS S3, DigitalOcean Spaces, etc.)
S3_ENDPOINT=https://s3.region.amazonaws.com
S3_ACCESS_KEY_ID=PRODUCTION_ACCESS_KEY
S3_SECRET_ACCESS_KEY=PRODUCTION_SECRET_KEY
S3_BUCKET=tracertm-production
S3_REGION=us-east-1

# -----------------------------------------------------------------------------
# Service URLs
# -----------------------------------------------------------------------------
GO_BACKEND_URL=http://go-backend:8080
PYTHON_BACKEND_URL=http://python-backend:8000
GRPC_PORT=9090
GRPC_GO_BACKEND_HOST=go-backend:9090

# Service-to-service authentication
SERVICE_TOKEN=PRODUCTION_SERVICE_TOKEN_64_CHARS_MINIMUM

# -----------------------------------------------------------------------------
# Application Configuration
# -----------------------------------------------------------------------------
# Go Backend
GIN_MODE=release
PORT=8080

# Python Backend
LOG_LEVEL=INFO
REALTIME_PROVIDER=nats

# -----------------------------------------------------------------------------
# CORS Configuration
# -----------------------------------------------------------------------------
# Replace with your actual production domain
CORS_ALLOWED_ORIGINS=https://tracertm.example.com

# -----------------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------------
# Session management
SESSION_SECRET=PRODUCTION_SESSION_SECRET_64_CHARS
SESSION_TIMEOUT=3600
SESSION_SECURE=true
SESSION_HTTPONLY=true
SESSION_SAMESITE=strict

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# -----------------------------------------------------------------------------
# Feature Flags
# -----------------------------------------------------------------------------
ENABLE_WEBSOCKET=true
ENABLE_EVENTS=true
ENABLE_SEARCH=true
ENABLE_VECTOR_SEARCH=true
ENABLE_NATS=true
ENABLE_REDIS_CACHE=true

# -----------------------------------------------------------------------------
# Monitoring
# -----------------------------------------------------------------------------
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=STRONG_GRAFANA_PASSWORD

# -----------------------------------------------------------------------------
# Temporal (if using)
# -----------------------------------------------------------------------------
TEMPORAL_HOST=temporal.region.tmprl.cloud:7233
TEMPORAL_NAMESPACE=production
TEMPORAL_TLS_CERT=/etc/tracertm/temporal-client.pem
TEMPORAL_TLS_KEY=/etc/tracertm/temporal-client.key
```

### Secret Management

**Never commit secrets to version control!**

#### Using Environment Variables (Basic)

```bash
# Create secure environment file
sudo mkdir -p /etc/tracertm
sudo touch /etc/tracertm/.env
sudo chmod 600 /etc/tracertm/.env
sudo chown root:docker /etc/tracertm/.env

# Edit with secure values
sudo nano /etc/tracertm/.env
```

#### Using Docker Secrets (Recommended)

```bash
# Create secrets
echo "STRONG_PASSWORD" | docker secret create db_password -
echo "JWT_SECRET_KEY" | docker secret create jwt_secret -
echo "WORKOS_API_KEY" | docker secret create workos_api_key -

# Reference in docker-compose.yml
secrets:
  - db_password
  - jwt_secret
  - workos_api_key
```

#### Using HashiCorp Vault (Enterprise)

```bash
# Store secrets in Vault
vault kv put secret/tracertm/production \
  db_password="STRONG_PASSWORD" \
  jwt_secret="JWT_SECRET_KEY" \
  workos_api_key="WORKOS_KEY"

# Retrieve at runtime
export DB_PASSWORD=$(vault kv get -field=db_password secret/tracertm/production)
```

---

## SSL/TLS Setup

### Option 1: Let's Encrypt with Nginx (Recommended)

#### Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

#### Obtain SSL Certificate

```bash
# Ensure Nginx is stopped
sudo docker compose down

# Obtain certificate
sudo certbot certonly --standalone \
  -d tracertm.example.com \
  -d api.tracertm.example.com \
  --email admin@example.com \
  --agree-tos \
  --non-interactive

# Certificates stored in:
# /etc/letsencrypt/live/tracertm.example.com/fullchain.pem
# /etc/letsencrypt/live/tracertm.example.com/privkey.pem
```

#### Configure Nginx for SSL

Update `nginx/conf.d/tracertm.conf`:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name tracertm.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name tracertm.example.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/tracertm.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tracertm.example.com/privkey.pem;

    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS (optional but recommended)
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Backend proxy
    location /api/ {
        proxy_pass http://nginx:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://nginx:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Frontend (if serving static files)
    location / {
        root /var/www/tracertm;
        try_files $uri $uri/ /index.html;
    }
}
```

#### Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Add cron job for auto-renewal
sudo crontab -e

# Add this line (renews twice daily)
0 0,12 * * * certbot renew --quiet --post-hook "docker compose exec nginx nginx -s reload"
```

### Option 2: Caddy with Automatic SSL (Easier)

Update `docker-compose.yml` to use Caddy instead of Nginx:

```yaml
caddy:
  image: caddy:latest
  container_name: tracertm-caddy
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./Caddyfile.prod:/etc/caddy/Caddyfile
    - caddy_data:/data
    - caddy_config:/config
  restart: unless-stopped
  networks:
    - tracertm

volumes:
  caddy_data:
  caddy_config:
```

Create `Caddyfile.prod`:

```caddyfile
tracertm.example.com {
    # Automatic HTTPS with Let's Encrypt

    # API routes to Go backend
    handle /api/v1/projects/* {
        reverse_proxy go-backend:8080
    }

    handle /api/v1/items/* {
        reverse_proxy go-backend:8080
    }

    # WebSocket
    handle /api/v1/ws {
        reverse_proxy go-backend:8080
    }

    # Python backend routes
    handle /api/v1/specifications/* {
        reverse_proxy python-backend:8000
    }

    handle /api/v1/executions/* {
        reverse_proxy python-backend:8000
    }

    # Frontend
    handle /* {
        reverse_proxy frontend:3000
    }

    # Security headers
    header {
        Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
        X-Frame-Options "SAMEORIGIN"
        X-Content-Type-Options "nosniff"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "no-referrer-when-downgrade"
    }

    # Logging
    log {
        output file /var/log/caddy/access.log
        format json
    }
}
```

---

## Service Deployment

### Deployment order and health checks (summary)

1. **Build order:** Clone repo → set env vars → build images → start PostgreSQL only → run migrations → start all services.
2. **Environment:** All required variables must be in `/etc/tracertm/.env` (see [Environment Configuration](#environment-configuration)). Do not start application services until DB and migrations are ready.
3. **Migration order:** Run **Go** migrations first (if your backend uses a migration runner), then **Python** (Alembic). Python migrations are required for `test_cases` and other Python-owned tables; skipping them causes 503 and unhealthy health.
4. **Health checks:** After start, probe gateway `/health`, Go `/health` (or gateway `/health/go`), and Python `/health` (or gateway `/health/python`). Use these URLs for Docker/Kubernetes liveness and readiness probes.

### Health endpoints

| Service   | Endpoint           | Use for probe |
|----------|--------------------|----------------|
| Gateway  | `GET /health`      | Liveness; may aggregate backends |
| Go       | `GET :8080/health` or `GET /health/go` via gateway | Go backend liveness |
| Python   | `GET :8000/health` or `GET /api/v1/health` via gateway | Python API liveness; includes DB/migrations check |

- **Go:** Returns 200 and JSON (`{"status":"ok"}` or similar). No auth.
- **Python:** Returns 200 when healthy; 503 when e.g. migrations not applied (see `/api/v1/health` response body for `migrations` status).
- **Kubernetes:** Configure liveness/readiness to hit the gateway or each backend’s health URL; failure should restart or exclude the pod from traffic.

### Pre-Deployment Checklist

- [ ] Domain DNS configured and propagated
- [ ] SSL certificates obtained or Caddy configured
- [ ] Environment variables set in `/etc/tracertm/.env`
- [ ] Secrets created (if using Docker secrets)
- [ ] Firewall rules configured
- [ ] Database backup tested
- [ ] Monitoring configured

### Deployment Steps

#### 1. Clone Repository

```bash
# Create deployment directory
sudo mkdir -p /opt/tracertm
cd /opt/tracertm

# Clone repository
git clone https://github.com/yourusername/tracertm.git .

# Checkout production branch/tag
git checkout v1.0.0
```

#### 2. Build Images

```bash
# Build all images
docker compose build --no-cache

# Verify images
docker images | grep tracertm
```

#### 3. Initialize Database

Run **both** Go and Python migrations before starting application services. The Python API owns tables such as `test_cases`; if Python migrations are skipped, the API will return 503 and health checks will report migrations as unhealthy.

```bash
# Start PostgreSQL only
docker compose up -d postgres

# Wait for PostgreSQL to be ready
docker compose exec postgres pg_isready -U tracertm

# Run Go migrations (if your backend uses a migration runner)
# e.g. docker compose run --rm go-backend ./migrate up

# Run Python (Alembic) migrations — required for test_cases and other Python-owned tables
docker compose run --rm python-backend alembic upgrade head
```

#### 4. Start All Services

```bash
# Start all services
docker compose up -d

# Verify all services are running
docker compose ps

# Check logs
docker compose logs --tail=50 --follow
```

#### 5. Verify Deployment

Probe health endpoints (see [Health endpoints](#health-endpoints)):

```bash
# Gateway (if using Nginx)
curl -f http://localhost/health || echo "Health check failed"

# Backends directly (or via gateway paths)
curl -f http://localhost:8080/health || echo "Go backend failed"
curl -f http://localhost:4000/health || echo "Python backend failed"
# Or via gateway: curl -f http://localhost/health/go && curl -f http://localhost/health/python

# Check SSL (if configured)
curl -I https://tracertm.example.com
```

### Service Management

```bash
# View logs
docker compose logs -f [service_name]

# Restart a service
docker compose restart [service_name]

# Stop all services
docker compose down

# Update a service
git pull
docker compose build [service_name]
docker compose up -d [service_name]

# View resource usage
docker stats
```

---

## Security Hardening

### Firewall Configuration

```bash
# Install UFW (Uncomplicated Firewall)
sudo apt install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow internal services (only from specific IPs if needed)
# sudo ufw allow from 10.0.0.0/8 to any port 5432 proto tcp  # PostgreSQL
# sudo ufw allow from 10.0.0.0/8 to any port 6379 proto tcp  # Redis

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

### Container Security

#### Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  go-backend:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
```

#### Non-Root User

Already configured in Dockerfiles:

```dockerfile
# Create non-root user
RUN addgroup -g 1000 tracertm && \
    adduser -D -u 1000 -G tracertm tracertm

USER tracertm
```

### Database Security

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U tracertm

# Revoke public schema privileges
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT CREATE ON SCHEMA public TO tracertm;

# Set strong password policy
ALTER SYSTEM SET password_encryption = 'scram-sha-256';

# Limit connections
ALTER SYSTEM SET max_connections = 100;

# Enable SSL (if not already enabled)
ALTER SYSTEM SET ssl = on;
```

### Redis Security

Add to Redis configuration:

```bash
# Require password
requirepass STRONG_REDIS_PASSWORD

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
rename-command SHUTDOWN SHUTDOWN_SAFE

# Bind to internal network only
bind 127.0.0.1 10.0.0.1
```

### Rate Limiting

Nginx rate limiting (already configured in `nginx.conf`):

```nginx
# Define rate limit zone
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# Apply to API routes
location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    limit_req_status 429;
    # ... rest of config ...
}
```

---

## Monitoring Setup

### Prometheus Configuration

Prometheus is already configured in `docker-compose.yml`. Access at `http://server-ip:9090`.

### Grafana Dashboards

1. **Access Grafana**: `http://server-ip:3000`
2. **Login**: Default credentials from `.env`
3. **Add Prometheus Data Source**:
   - URL: `http://prometheus:9090`
   - Access: Server (default)
   - Click "Save & Test"

4. **Import Dashboards**:
   - Go Backend: Dashboard ID `15489` (Go application metrics)
   - PostgreSQL: Dashboard ID `9628`
   - Redis: Dashboard ID `11835`
   - Nginx: Dashboard ID `12708`

### Alert Configuration

Create `monitoring/alerts.yml`:

```yaml
groups:
  - name: tracertm_alerts
    interval: 30s
    rules:
      # Service down
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"

      # High CPU
      - alert: HighCPU
        expr: rate(process_cpu_seconds_total[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.job }}"

      # High memory
      - alert: HighMemory
        expr: process_resident_memory_bytes / process_virtual_memory_max_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.job }}"

      # Database connections
      - alert: HighDatabaseConnections
        expr: pg_stat_database_numbackends > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections: {{ $value }}"
```

---

## Backup and Disaster Recovery

### PostgreSQL Backups

#### Automated Daily Backups

Create `/opt/tracertm/scripts/backup-postgres.sh`:

```bash
#!/bin/bash
set -euo pipefail

# Configuration
BACKUP_DIR="/backup/postgres"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="tracertm"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Perform backup
docker compose exec -T postgres pg_dump -U tracertm -Fc ${DB_NAME} > \
  "${BACKUP_DIR}/tracertm_${TIMESTAMP}.dump"

# Compress backup
gzip "${BACKUP_DIR}/tracertm_${TIMESTAMP}.dump"

# Remove old backups
find "${BACKUP_DIR}" -name "tracertm_*.dump.gz" -mtime +${RETENTION_DAYS} -delete

# Verify backup
if [ -f "${BACKUP_DIR}/tracertm_${TIMESTAMP}.dump.gz" ]; then
    echo "Backup successful: tracertm_${TIMESTAMP}.dump.gz"
    exit 0
else
    echo "Backup failed!"
    exit 1
fi
```

Make executable and schedule:

```bash
chmod +x /opt/tracertm/scripts/backup-postgres.sh

# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/tracertm/scripts/backup-postgres.sh >> /var/log/tracertm-backup.log 2>&1
```

#### Manual Backup

```bash
# Create backup
docker compose exec postgres pg_dump -U tracertm -Fc tracertm > backup.dump

# Restore backup
docker compose exec -T postgres pg_restore -U tracertm -d tracertm -c < backup.dump
```

### Redis Backups

Redis automatically creates `dump.rdb` in the data volume:

```bash
# Manual backup
docker compose exec redis redis-cli BGSAVE

# Copy backup
docker cp tracertm-redis:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb
```

### Volume Backups

```bash
# Backup all volumes
docker run --rm \
  -v tracertm_postgres_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/postgres_data_$(date +%Y%m%d).tar.gz /data

# Restore volume
docker run --rm \
  -v tracertm_postgres_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/postgres_data_20240101.tar.gz -C /
```

### Disaster Recovery Plan

1. **Identify Failure**
   - Check service health: `docker compose ps`
   - Review logs: `docker compose logs --tail=100`

2. **Stop Services**
   ```bash
   docker compose down
   ```

3. **Restore Database**
   ```bash
   # Start PostgreSQL
   docker compose up -d postgres

   # Restore latest backup
   cat /backup/postgres/tracertm_LATEST.dump.gz | gunzip | \
     docker compose exec -T postgres pg_restore -U tracertm -d tracertm -c
   ```

4. **Restore Volumes** (if needed)
   ```bash
   docker run --rm \
     -v tracertm_postgres_data:/data \
     -v /backup:/backup \
     alpine tar xzf /backup/postgres_data_LATEST.tar.gz -C /
   ```

5. **Start All Services**
   ```bash
   docker compose up -d
   ```

6. **Verify Recovery**
   ```bash
   # Health checks
   curl http://localhost/health

   # Check data integrity
   docker compose exec postgres psql -U tracertm -c "SELECT COUNT(*) FROM items;"
   ```

---

## Post-Deployment Verification

### Health Check Script

Create `/opt/tracertm/scripts/health-check.sh`:

```bash
#!/bin/bash

echo "TracerTM Health Check"
echo "====================="

# Check Docker
echo -n "Docker: "
docker --version > /dev/null 2>&1 && echo "✓" || echo "✗"

# Check services
echo -n "All services running: "
RUNNING=$(docker compose ps --services --filter "status=running" | wc -l)
TOTAL=$(docker compose ps --services | wc -l)
[ "$RUNNING" -eq "$TOTAL" ] && echo "✓ ($RUNNING/$TOTAL)" || echo "✗ ($RUNNING/$TOTAL)"

# Check endpoints
echo -n "Gateway health: "
curl -sf http://localhost/health > /dev/null && echo "✓" || echo "✗"

echo -n "Go backend: "
curl -sf http://localhost/health/go > /dev/null && echo "✓" || echo "✗"

echo -n "Python backend: "
curl -sf http://localhost/health/python > /dev/null && echo "✓" || echo "✗"

# Check SSL (if configured)
if [ -n "$1" ]; then
    echo -n "SSL: "
    curl -sf https://$1 > /dev/null && echo "✓" || echo "✗"
fi

# Check database
echo -n "Database: "
docker compose exec -T postgres pg_isready -U tracertm > /dev/null 2>&1 && echo "✓" || echo "✗"

# Check Redis
echo -n "Redis: "
docker compose exec -T redis redis-cli ping > /dev/null 2>&1 && echo "✓" || echo "✗"

# Check NATS
echo -n "NATS: "
curl -sf http://localhost:8222/healthz > /dev/null 2>&1 && echo "✓" || echo "✗"

echo ""
echo "Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Verification Checklist

- [ ] All services running: `docker compose ps`
- [ ] Health endpoints responding:
  - [ ] `curl http://localhost/health`
  - [ ] `curl http://localhost/health/go`
  - [ ] `curl http://localhost/health/python`
- [ ] SSL/TLS working: `curl https://tracertm.example.com`
- [ ] Database accessible
- [ ] Redis responding
- [ ] NATS healthy
- [ ] Prometheus collecting metrics
- [ ] Grafana dashboards displaying data
- [ ] Logs being written
- [ ] Backups scheduled and tested
- [ ] Monitoring alerts configured
- [ ] Firewall rules active

### Performance Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test API endpoint
ab -n 1000 -c 10 http://localhost/api/v1/health

# Test with authentication
ab -n 100 -c 5 -H "Authorization: Bearer TOKEN" \
  http://localhost/api/v1/projects
```

---

## Conclusion

Your TracerTM production deployment is now complete. For ongoing operations, see:

- [Operations Runbook](/docs/guides/OPERATIONS_RUNBOOK.md)
- [Troubleshooting Guide](/docs/guides/TROUBLESHOOTING.md)
- [Environment Configuration Guide](/docs/guides/ENVIRONMENT_CONFIGURATION.md)

For issues or questions, consult the documentation or file an issue on GitHub.

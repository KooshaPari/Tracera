# TraceRTM Deployment Guide (historical Python reference)

> **Not the current runtime path.** This recovered guide describes the retired
> Python/FastAPI stack (port 8000, PostgreSQL/Redis, Alembic, and JWT settings).
> The shipped service is the Rust `tracera-server` on `127.0.0.1:8080`; use
> [`../quickstart.md`](../quickstart.md) and [`../../deploy/selfhost/README.md`](../../deploy/selfhost/README.md)
> for current local and self-hosted deployment instructions. Do not copy the
> commands below to deploy the current service.

> **Recovered June 2026.** Restored from git history (`9e78f48dd^`). Production deployments must supply
> `TRACERA_JWT_SECRET`, `TRACERA_JWT_AUDIENCE`, and `TRACERA_JWT_ISSUER` (see [`../quickstart.md`](../quickstart.md)).
> The live API exposes 17 mounted business routes under `/api/v1` plus `/health` and `/ready` probes.

**Complete deployment and operations guide for TraceRTM**

---

## 🚀 QUICK START

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/tracertm.git
cd tracertm

# Start services
docker-compose up -d

# Run migrations
alembic upgrade head

# Start CLI
python -m tracertm.cli.app

# Start API
uvicorn tracertm.api.main:app --reload
```

### Docker Deployment

```bash
# Build image
docker build -t tracertm:latest .

# Run container
docker run -d \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  -e REDIS_URL=redis://host:6379 \
  -p 8000:8000 \
  tracertm:latest
```

---

## 📊 SERVICES

### PostgreSQL
- **Port**: 5432
- **Database**: tracertm
- **User**: tracertm
- **Password**: tracertm_password (change in production!)

### Redis
- **Port**: 6379
- **Purpose**: Caching, sessions

### API
- **Port**: 8000
- **Endpoint**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

### Prometheus
- **Port**: 9090
- **Metrics**: http://localhost:9090

### Grafana
- **Port**: 3000
- **Admin**: admin/admin

---

## 🔧 CONFIGURATION

### Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
REDIS_URL=redis://host:6379
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
# Inject this value from the deployment secret manager; never commit a literal.
TRACERA_JWT_SECRET="${TRACERA_JWT_SECRET:?set via the deployment secret manager}"
TRACERA_JWT_AUDIENCE=tracera-api
TRACERA_JWT_ISSUER=tracera
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📈 MONITORING

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database
pg_isready -h localhost -U tracertm

# Redis
redis-cli ping
```

### Metrics

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

---

## 🔐 SECURITY

### Production Checklist

- [ ] Change default passwords
- [ ] Enable SSL/TLS
- [ ] Configure firewall
- [ ] Set up backups
- [ ] Enable monitoring
- [ ] Configure logging
- [ ] Set up alerts
- [ ] Review permissions

---

## 📦 BACKUP & RESTORE

### Database Backup

```bash
pg_dump -U tracertm tracertm > backup.sql
```

### Database Restore

```bash
psql -U tracertm tracertm < backup.sql
```

---

## 🚨 TROUBLESHOOTING

### Connection Issues

```bash
# Check PostgreSQL
psql -h localhost -U tracertm -d tracertm

# Check Redis
redis-cli -h localhost ping
```

### Performance Issues

- Check database indexes
- Monitor cache hit rate
- Review slow queries
- Analyze query plans

---

**For more information, see README.md and API documentation.**

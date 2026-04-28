# ADR-0006: Deployment Architecture

**Status:** Accepted
**Date:** 2026-02-01
**Deciders:** Development Team
**Supersedes:** N/A

---

## Context

TraceRTM requires a deployment strategy that supports:

1. **Frontend hosting:** Static assets (React SPA) with CDN delivery
2. **Backend hosting:** Python (FastAPI) + Go (performance layer) + PostgreSQL
3. **Real-time features:** WebSocket connections, SSE streaming
4. **Scalability:** Handle 1000+ concurrent users
5. **Cost efficiency:** Optimize for startup/small teams
6. **Developer experience:** Easy local development, fast deployments

Deployment constraints:
- **Frontend:** SPA with client-side routing (TanStack Router)
- **Backend:** Multi-language (Python services + Go performance layer)
- **Database:** PostgreSQL with pgvector, full-text search
- **Storage:** S3-compatible object storage (MinIO/AWS S3)
- **Cache:** Redis for sessions, rate limiting

## Decision

**Frontend:** Vercel (Next.js/SPA mode)
**Backend:** Fly.io (Docker containers) OR Railway (Dockerfile support)
**Database:** Neon (serverless PostgreSQL) OR self-hosted PostgreSQL on Fly.io
**Storage:** AWS S3 OR MinIO (self-hosted)
**CDN:** Vercel Edge Network (automatic)

## Rationale

### Frontend Deployment (Vercel)

**Why Vercel:**
- **Zero config:** `vercel deploy` from Vite build output
- **Edge Network:** Global CDN (300+ locations)
- **Preview deployments:** Every PR gets preview URL
- **Free tier:** 100 GB bandwidth/month (sufficient for MVP)
- **Framework support:** React 19, Vite 8, TanStack Router

**Stack:**
```json
// frontend/package.json
{
  "scripts": {
    "build": "turbo build --filter=@tracertm/web",
    "deploy": "vercel deploy --prod"
  }
}
```

**Build output:**
```
frontend/apps/web/dist/
├── index.html
├── assets/
│   ├── index-[hash].js
│   └── index-[hash].css
└── favicon.ico
```

### Backend Deployment (Fly.io)

**Why Fly.io:**
- **Multi-region:** Deploy to 35+ regions
- **Persistent volumes:** PostgreSQL data, MinIO storage
- **WebSocket support:** Native (no proxy needed)
- **Dockerfile-based:** Full control over runtime
- **Free tier:** 3 VMs, 3GB RAM total

**fly.toml:**
```toml
app = "tracertm-backend"

[build]
  dockerfile = "Dockerfile"

[env]
  DATABASE_URL = "postgresql://..."
  REDIS_URL = "redis://..."

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[[services.http_checks]]
  path = "/health"
  interval = "10s"
```

**Dockerfile (multi-stage):**
```dockerfile
# Stage 1: Python backend
FROM python:3.12-slim AS python-backend
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev
COPY src/ ./src/
CMD ["uvicorn", "tracertm.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 2: Go performance layer
FROM golang:1.25.7-alpine AS go-backend
WORKDIR /app
COPY backend/go.mod backend/go.sum ./
RUN go mod download
COPY backend/ ./
RUN go build -o /app/go-backend ./cmd/server

# Stage 3: Runtime (combine Python + Go)
FROM python:3.12-slim
COPY --from=python-backend /app /app
COPY --from=go-backend /app/go-backend /app/go-backend
CMD ["/app/start.sh"]  # Start both Python + Go servers
```

### Database (Neon vs Fly PostgreSQL)

**Option A: Neon (Serverless PostgreSQL)**
- **Pros:** Serverless (scale to zero), free tier (0.5GB), branching (preview environments)
- **Cons:** Cold start latency (1-2s), $19/month after free tier

**Option B: Fly.io PostgreSQL (Self-hosted)**
- **Pros:** Full control, persistent volumes, no cold starts
- **Cons:** Always-on cost ($5/month), manual backups

**Decision: Neon for MVP (cost), Fly PostgreSQL for production (performance)**

### Storage (S3 vs MinIO)

**Option A: AWS S3**
- **Pros:** Reliable, 99.999999999% durability, no maintenance
- **Cons:** Cost (storage + bandwidth)

**Option B: MinIO on Fly.io**
- **Pros:** S3-compatible, cheaper (uses Fly volumes), open-source
- **Cons:** Must manage backups, availability

**Decision: MinIO for MVP (cost), S3 for production (reliability)**

## Alternatives Rejected

### Alternative 1: Vercel (Full Stack)

- **Description:** Deploy both frontend + backend on Vercel (serverless functions)
- **Pros:** Single platform, simple deployment
- **Cons:** Serverless cold starts, 10s function timeout (too short for graph analysis), expensive at scale
- **Why Rejected:** Backend needs long-running operations (graph queries >10s), persistent connections (WebSocket)

### Alternative 2: AWS (EC2 + RDS + S3 + CloudFront)

- **Description:** Traditional AWS deployment
- **Pros:** Maximum control, production-grade infrastructure
- **Cons:** Complex setup (IAM, VPC, load balancers), expensive (~$100/month minimum)
- **Why Rejected:** Overkill for MVP. Fly.io provides similar features with simpler management.

### Alternative 3: Heroku

- **Description:** PaaS with Heroku Postgres
- **Pros:** Simple deployment, add-ons marketplace
- **Cons:** Expensive ($25/month dynos), poor WebSocket support, deprecated free tier
- **Why Rejected:** Fly.io cheaper and better WebSocket support. Heroku's free tier removal makes it uncompetitive.

### Alternative 4: Self-hosted (VPS)

- **Description:** DigitalOcean/Linode droplet
- **Pros:** Cheapest ($5/month), full control
- **Cons:** Manual updates, no auto-scaling, single point of failure
- **Why Rejected:** Requires DevOps expertise, no built-in scaling. Fly.io provides managed infrastructure for similar cost.

## Consequences

### Positive

- **Fast deployments:** Vercel <2 min, Fly.io <5 min
- **Global CDN:** Vercel Edge Network (frontend)
- **Preview environments:** Every PR gets test URL (Vercel + Fly preview apps)
- **Cost-effective:** Free tier supports 1000+ users
- **Developer experience:** `vercel deploy`, `fly deploy` (single command)
- **Scalability:** Horizontal scaling (add Fly.io VMs)

### Negative

- **Vendor lock-in:** Vercel for frontend, Fly.io for backend
- **Multi-platform complexity:** Two deployment pipelines (Vercel + Fly)
- **Cold starts:** Neon database (1-2s on first query after idle)
- **WebSocket scaling:** Fly.io requires sticky sessions (added complexity)

### Neutral

- **Database backups:** Neon auto-backup, Fly PostgreSQL manual
- **Monitoring:** Vercel Analytics, Fly.io Metrics (separate dashboards)
- **Secrets management:** Vercel env vars, Fly secrets

## Implementation

### Affected Components

- `vercel.json` - Vercel config (frontend)
- `fly.toml` - Fly.io config (backend)
- `Dockerfile` - Multi-stage build (Python + Go)
- `.github/workflows/deploy.yml` - CI/CD pipeline
- `scripts/deploy.sh` - Deployment automation

### Migration Strategy

**Phase 1: Local → Vercel (Frontend)**
```bash
cd frontend
vercel --prod
```

**Phase 2: Local → Fly.io (Backend)**
```bash
fly launch --name tracertm-backend
fly deploy
```

**Phase 3: Database Migration**
```bash
# Neon
neon projects create tracertm
neon databases create tracertm-prod
alembic upgrade head

# OR Fly PostgreSQL
fly postgres create --name tracertm-db
fly postgres attach tracertm-db
```

**Phase 4: CI/CD**
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd frontend && vercel deploy --prod --token=${{ secrets.VERCEL_TOKEN }}

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
```

### Rollout Plan

- **Phase 1:** Deploy to staging (Vercel preview + Fly staging app)
- **Phase 2:** Deploy to production (manual trigger)
- **Phase 3:** Enable automatic deployments (main branch → production)

### Success Criteria

- [ ] Frontend deploys in <2 min
- [ ] Backend deploys in <5 min
- [ ] Database migrations automated (Alembic)
- [ ] Zero-downtime deployments (Fly blue-green)
- [ ] Preview deployments for PRs
- [ ] Health checks pass after deployment

## References

- [Vercel Documentation](https://vercel.com/docs)
- [Fly.io Documentation](https://fly.io/docs)
- [Neon PostgreSQL](https://neon.tech)
- [ADR-0007: Database Architecture](ADR-0007-database-architecture.md)
- [ADR-0011: Frontend Framework](ADR-0011-frontend-framework-architecture.md)

---

**Notes:**
- **Cost estimate (MVP):**
  - Vercel: Free (100 GB bandwidth)
  - Fly.io: Free (3 VMs, 3GB RAM)
  - Neon: Free (0.5GB database)
  - **Total: $0/month** (within free tiers)
- **Cost estimate (production 10k users):**
  - Vercel: $20/month (Pro plan)
  - Fly.io: $50/month (scaling VMs)
  - Neon: $19/month (Scale plan)
  - S3: $10/month (storage + bandwidth)
  - **Total: ~$100/month**

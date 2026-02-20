# Full Infrastructure Setup for TraceRTM

## Overview

Complete setup guide for all infrastructure services:
- **PostgreSQL** (Supabase) - Primary database with pgvector
- **Meilisearch** - Full-text search
- **NATS** (Synadia) - Event publishing
- **Redis** (Upstash) - Caching
- **Neo4j** (Aura) - Graph database
- **Hatchet** - Workflow orchestration
- **WorkOS** - Authentication

## Status

✅ **Supabase PostgreSQL** - Configured
✅ **Neo4j Aura** - Configured
✅ **NATS (Synadia)** - Configured
✅ **Upstash Redis** - Configured
✅ **Hatchet** - Token in .env
✅ **WorkOS** - Configured

## What's Needed

### 1. Add Hatchet Go SDK
```bash
cd backend
go get github.com/hatchet-dev/hatchet-go
```

### 2. Add Meilisearch Client
```bash
go get github.com/meilisearch/meilisearch-go
```

### 3. Create Infrastructure Clients
- `backend/internal/hatchet/client.go` - Hatchet client
- `backend/internal/search/meilisearch.go` - Meilisearch client
- `backend/internal/cache/redis.go` - Redis client
- `backend/internal/events/nats.go` - NATS client

### 4. Update Server to Initialize All Services
- Update `backend/internal/server/server.go`
- Add all clients to server struct
- Initialize in NewServer()

### 5. Create Adapter Pattern for All Services
- Dependency injection for all clients
- Consistent error handling
- Health checks for each service

### 6. Docker Compose for Local Development
- PostgreSQL (local)
- Meilisearch (local)
- NATS (local)
- Redis (local)
- Neo4j (local)

### 7. Environment Configuration
- Add all service URLs to config
- Support local and production URLs
- Sensible defaults

## Implementation Order

1. ✅ Add Go dependencies
2. ⏳ Create infrastructure clients
3. ⏳ Update server initialization
4. ⏳ Create Docker Compose
5. ⏳ Add health checks
6. ⏳ Create integration tests
7. ⏳ Document setup

## Next Steps

Ready to implement full infrastructure setup!


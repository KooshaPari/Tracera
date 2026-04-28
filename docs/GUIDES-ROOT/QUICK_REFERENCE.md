# TraceRTM Backend - Quick Reference

## Recommended Stack

```
PostgreSQL 16 + NATS + Redis + FastAPI
```

## Why Each Component?

| Component | Why | Alternative | Why Not |
|-----------|-----|-------------|---------|
| **PostgreSQL** | Handles graph + relational + JSONB + FTS | Neo4j | Expensive, overkill |
| **NATS** | Fast, simple agent coordination | Kafka | Overkill, complex |
| **Redis** | Fast caching + pub/sub | Memcached | Limited features |
| **FastAPI** | Modern, async, fast | Django | Overkill |

## What NOT to Use

| Technology | Why Not |
|-----------|---------|
| **Neo4j** | Expensive, use PostgreSQL instead (add later if needed) |
| **SurrealDB** | Too immature (v1.0 in 2024) |
| **ArangoDB** | PostgreSQL handles all use cases |
| **EdgeDB** | Very new, tiny ecosystem |
| **Elasticsearch** | PostgreSQL FTS sufficient (add later if needed) |
| **Kafka** | NATS provides all needed messaging |
| **Memcached** | Redis has more features |

## Quick Setup

### Docker Compose
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: tracertm
      POSTGRES_PASSWORD: dev
    ports:
      - "5432:5432"

  nats:
    image: nats:latest
    command: "-js"
    ports:
      - "4222:4222"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Run
```bash
docker-compose up
```

## Database Schema (Minimal)

```sql
-- Projects
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Items (universal entity)
CREATE TABLE items (
  id UUID PRIMARY KEY,
  project_id UUID NOT NULL REFERENCES projects(id),
  parent_id UUID REFERENCES items(id),
  view VARCHAR(50) NOT NULL,
  title VARCHAR(255) NOT NULL,
  status VARCHAR(50) DEFAULT 'draft',
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Links (relationships)
CREATE TABLE links (
  id UUID PRIMARY KEY,
  project_id UUID NOT NULL REFERENCES projects(id),
  source_item_id UUID NOT NULL REFERENCES items(id),
  target_item_id UUID NOT NULL REFERENCES items(id),
  link_type VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Events (audit trail)
CREATE TABLE events (
  id BIGSERIAL PRIMARY KEY,
  project_id UUID NOT NULL REFERENCES projects(id),
  event_type VARCHAR(50) NOT NULL,
  entity_id UUID NOT NULL,
  agent_id UUID,
  data JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## FastAPI Endpoints

```python
# Items
GET    /api/projects/{id}/items
POST   /api/projects/{id}/items
GET    /api/items/{id}
PUT    /api/items/{id}
DELETE /api/items/{id}

# Links
GET    /api/projects/{id}/links
POST   /api/projects/{id}/links
DELETE /api/links/{id}

# Search
GET    /api/search?q=...

# WebSocket
WS     /ws/projects/{id}
```

## NATS Topics

```
agents.register
agents.heartbeat
items.created
items.updated
items.deleted
links.created
links.deleted
agents.conflict
```

## Redis Keys

```
cache:item:{id}
cache:project:{id}
session:{id}
lock:item:{id}
```

## Performance Targets

| Operation | Target |
|-----------|--------|
| CRUD | <100ms |
| Hierarchy | <200ms |
| Search | <500ms |
| Graph | <300ms |
| Real-time | <100ms |

## Deployment

### Local
```bash
docker-compose up
```

### Production
- **DB**: AWS RDS PostgreSQL
- **Messaging**: NATS Cloud
- **Cache**: Redis Cloud
- **Backend**: AWS ECS / Kubernetes

## Cost (Monthly)

- PostgreSQL: $50-200
- NATS: $0-100
- Redis: $0-100
- Backend: $50-500
- **Total**: $100-900

## Phase 1 Checklist

- [ ] PostgreSQL schema
- [ ] FastAPI REST API
- [ ] NATS integration
- [ ] Redis caching
- [ ] WebSocket support
- [ ] CRUD operations
- [ ] Tests (80%+ coverage)
- [ ] Docker Compose setup

## Phase 2 (Optional)

- [ ] Full-text search optimization
- [ ] pgvector semantic search
- [ ] Event sourcing
- [ ] Agent conflict detection
- [ ] Temporal queries

## Phase 3 (Optional)

- [ ] Neo4j for analytics
- [ ] Materialized views
- [ ] Query optimization
- [ ] Performance monitoring

## Key Files to Create

```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── nats_client.py
│   ├── redis_client.py
│   ├── models/
│   │   ├── project.py
│   │   ├── item.py
│   │   ├── link.py
│   │   └── event.py
│   ├── schemas/
│   │   ├── project.py
│   │   ├── item.py
│   │   └── link.py
│   ├── api/
│   │   ├── projects.py
│   │   ├── items.py
│   │   ├── links.py
│   │   └── search.py
│   └── services/
│       ├── item_service.py
│       ├── link_service.py
│       └── search_service.py
├── migrations/
├── tests/
├── docker-compose.yml
└── requirements.txt
```

## Summary

✅ **PostgreSQL**: Primary data store
✅ **NATS**: Agent coordination
✅ **Redis**: Caching & sessions
✅ **FastAPI**: REST API
⏳ **Neo4j**: Phase 2+ (optional)

**Ready to build!** 🚀


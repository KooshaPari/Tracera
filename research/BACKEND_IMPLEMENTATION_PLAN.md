# TraceRTM Backend Implementation Plan

## Recommended Stack

### Primary Database: PostgreSQL 16 + pgvector
- **Why**: Mature, reliable, excellent for hierarchical + graph data
- **Features**: JSONB, recursive CTEs, full-text search, pgvector
- **Deployment**: Docker container or managed service (AWS RDS, Supabase)

### Message Queue: NATS
- **Why**: Lightweight, fast, perfect for agent coordination
- **Features**: Pub/sub, request/reply, JetStream persistence
- **Deployment**: Docker container or NATS Cloud

### Caching: Redis
- **Why**: Fast in-memory cache + pub/sub for real-time updates
- **Features**: Sessions, temporary data, real-time subscriptions
- **Deployment**: Docker container or managed service (Redis Cloud)

### Optional: Neo4j (Phase 2+)
- **Why**: Advanced graph analytics and visualization
- **Status**: Optional, not required for MVP
- **Deployment**: Separate from primary store

## NOT Needed

### ❌ Elasticsearch
- PostgreSQL full-text search sufficient for MVP
- Can add later if needed

### ❌ Kafka
- NATS provides all needed messaging
- Overkill for TraceRTM scale

### ❌ SurrealDB/ArangoDB/EdgeDB
- Too immature or unnecessary complexity
- PostgreSQL handles all use cases

## Implementation Phases

### Phase 1: Core Backend (Weeks 1-2)
**Deliverables:**
- PostgreSQL schema with Alembic migrations
- FastAPI REST API (CRUD for Items, Links, Projects)
- NATS integration for agent coordination
- Redis caching layer
- WebSocket support for real-time updates

**Key Files:**
```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # PostgreSQL connection
│   ├── nats_client.py       # NATS integration
│   ├── redis_client.py      # Redis integration
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/
│   │   ├── items.py         # Item endpoints
│   │   ├── links.py         # Link endpoints
│   │   ├── projects.py      # Project endpoints
│   │   └── agents.py        # Agent endpoints
│   └── services/            # Business logic
├── migrations/              # Alembic migrations
├── tests/                   # Unit + integration tests
└── docker-compose.yml       # Local development
```

### Phase 2: Enhanced Features (Weeks 3-4)
**Deliverables:**
- Full-text search optimization
- pgvector semantic search
- Event sourcing implementation
- Agent conflict detection
- Temporal queries (point-in-time)

### Phase 3: Analytics & Optimization (Weeks 5+)
**Deliverables:**
- Neo4j integration (optional)
- Materialized views for reporting
- Query optimization
- Performance monitoring

## Docker Compose Setup

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: tracertm
      POSTGRES_USER: tracertm
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nats:
    image: nats:latest
    ports:
      - "4222:4222"
      - "8222:8222"
    command: "-js"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - nats
      - redis
    environment:
      DATABASE_URL: postgresql://tracertm:dev_password@postgres:5432/tracertm
      NATS_URL: nats://nats:4222
      REDIS_URL: redis://redis:6379

volumes:
  postgres_data:
```

## API Endpoints (FastAPI)

### Items
- `GET /api/projects/{project_id}/items` - List items
- `POST /api/projects/{project_id}/items` - Create item
- `GET /api/items/{item_id}` - Get item
- `PUT /api/items/{item_id}` - Update item
- `DELETE /api/items/{item_id}` - Delete item
- `GET /api/items/{item_id}/descendants` - Get hierarchy
- `GET /api/items/search?q=...` - Full-text search

### Links
- `GET /api/projects/{project_id}/links` - List links
- `POST /api/projects/{project_id}/links` - Create link
- `DELETE /api/links/{link_id}` - Delete link
- `GET /api/items/{item_id}/graph` - Get connected items

### Projects
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/projects/{project_id}` - Get project
- `PUT /api/projects/{project_id}` - Update project

### Agents
- `POST /api/agents/register` - Register agent
- `POST /api/agents/{agent_id}/heartbeat` - Send heartbeat
- `GET /api/agents/{agent_id}/tasks` - Get pending tasks

### WebSocket
- `WS /ws/projects/{project_id}` - Real-time updates

## Database Schema (PostgreSQL)

```sql
-- Projects
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  description TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Items (universal entity)
CREATE TABLE items (
  id UUID PRIMARY KEY,
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  parent_id UUID REFERENCES items(id) ON DELETE CASCADE,
  view VARCHAR(50) NOT NULL,  -- feature, code, test, api, etc.
  item_type VARCHAR(50) NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(50) DEFAULT 'draft',
  owner VARCHAR(255),
  metadata JSONB DEFAULT '{}',
  search_vector tsvector,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP,
  INDEX idx_project_view (project_id, view),
  INDEX idx_project_status (project_id, status),
  INDEX idx_parent_id (parent_id),
  INDEX idx_search (search_vector)
);

-- Links (relationships)
CREATE TABLE links (
  id UUID PRIMARY KEY,
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  source_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  target_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  link_type VARCHAR(50) NOT NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE (source_item_id, target_item_id, link_type),
  INDEX idx_source (source_item_id),
  INDEX idx_target (target_item_id),
  INDEX idx_link_type (link_type)
);

-- Events (audit trail)
CREATE TABLE events (
  id BIGSERIAL PRIMARY KEY,
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  event_type VARCHAR(50) NOT NULL,
  entity_type VARCHAR(50) NOT NULL,
  entity_id UUID NOT NULL,
  agent_id UUID,
  data JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  INDEX idx_project_event (project_id, event_type),
  INDEX idx_entity (entity_type, entity_id)
);

-- Agents
CREATE TABLE agents (
  id UUID PRIMARY KEY,
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  agent_type VARCHAR(50) NOT NULL,
  status VARCHAR(50) DEFAULT 'active',
  last_activity_at TIMESTAMP,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);
```

## NATS Topics

```
# Agent coordination
agents.{agent_id}.register
agents.{agent_id}.heartbeat
agents.{agent_id}.tasks

# Item events
items.created
items.updated
items.deleted

# Link events
links.created
links.deleted

# Agent events
agents.conflict
agents.lock_acquired
agents.lock_released
```

## Redis Keys

```
# Caching
cache:item:{item_id}
cache:project:{project_id}
cache:search:{query_hash}

# Sessions
session:{session_id}

# Locks
lock:item:{item_id}
lock:agent:{agent_id}

# Real-time
updates:{project_id}
```

## Testing Strategy

- Unit tests: 80%+ coverage
- Integration tests: Database + NATS
- E2E tests: Full API workflows
- Load tests: Agent coordination under stress

## Success Criteria

✅ All CRUD operations working
✅ Hierarchical queries fast (<100ms)
✅ Full-text search working
✅ Agent coordination without conflicts
✅ Real-time updates via WebSocket
✅ 80%+ test coverage
✅ Docker Compose setup working


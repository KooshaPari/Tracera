# TraceRTM Architecture Summary

## Recommended Tech Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│  React 19 (Web) + Electron (Desktop) + Storybook           │
│  - Real-time updates via WebSocket                         │
│  - Command palette, graph visualization                    │
│  - Multi-view interface (Feature, Code, Test, etc.)        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   API Layer                                 │
│  FastAPI (Python) + Pydantic + SQLAlchemy                  │
│  - REST API for CRUD operations                            │
│  - WebSocket for real-time updates                         │
│  - Agent coordination endpoints                            │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────────┐
        │            │            │              │
┌───────▼──┐  ┌──────▼──┐  ┌────▼────┐  ┌─────▼──┐
│PostgreSQL│  │  NATS   │  │  Redis  │  │ Neo4j? │
│   16     │  │ (Msg Q) │  │(Cache)  │  │(Phase2)│
│          │  │         │  │         │  │        │
│ • Items  │  │ • Agent │  │ • Sess  │  │ • Graph│
│ • Links  │  │   coord │  │ • Cache │  │  Viz  │
│ • Events │  │ • Events│  │ • Locks │  │ • Anal│
│ • Search │  │ • Tasks │  │ • Pub/S │  │       │
└──────────┘  └─────────┘  └─────────┘  └───────┘
```

## Component Breakdown

### 1. PostgreSQL 16 (Primary Database)
**Purpose**: Core data store for all persistent data

**Tables**:
- `projects` - Project containers
- `items` - Universal entity (Features, Code, Tests, APIs, etc.)
- `links` - Typed relationships between items
- `events` - Complete audit trail
- `agents` - Agent registry and status

**Features**:
- Recursive CTEs for hierarchical queries
- JSONB for flexible metadata
- tsvector for full-text search
- pgvector extension for semantic search
- Soft deletes for data retention

**Indexes**:
- (project_id, view) - Fast filtering by view
- (project_id, status) - Fast filtering by status
- (parent_id) - Fast hierarchy traversal
- (search_vector) - Fast full-text search

### 2. NATS (Message Queue)
**Purpose**: Real-time agent coordination and event streaming

**Topics**:
- `agents.*.register` - Agent registration
- `agents.*.heartbeat` - Agent health checks
- `items.created/updated/deleted` - Item events
- `links.created/deleted` - Link events
- `agents.conflict` - Conflict detection
- `agents.lock_*` - Distributed locking

**Features**:
- JetStream for persistence
- Request/reply for synchronous operations
- Pub/sub for asynchronous events
- Built-in clustering for HA

### 3. Redis (Caching & Sessions)
**Purpose**: Fast caching and real-time updates

**Use Cases**:
- Session storage
- Item/project caching
- Search result caching
- Distributed locks
- Real-time pub/sub for WebSocket updates

**TTL Strategy**:
- Items: 5 minutes
- Projects: 10 minutes
- Search results: 1 hour
- Sessions: 24 hours

### 4. FastAPI Backend
**Purpose**: REST API and WebSocket server

**Endpoints**:
- `/api/projects/*` - Project CRUD
- `/api/items/*` - Item CRUD + hierarchy
- `/api/links/*` - Link CRUD
- `/api/search` - Full-text search
- `/api/agents/*` - Agent management
- `/ws/projects/{id}` - Real-time updates

**Features**:
- Async/await for high concurrency
- Dependency injection for clean code
- Automatic API documentation (Swagger)
- Request validation with Pydantic
- Error handling and logging

### 5. Neo4j (Optional - Phase 2+)
**Purpose**: Advanced graph analytics and visualization

**Use Cases**:
- Graph visualization (separate from primary store)
- Path finding algorithms
- Community detection
- Impact analysis
- Not required for MVP

## Data Flow

### Create Item
```
1. Frontend sends POST /api/items
2. FastAPI validates with Pydantic
3. SQLAlchemy inserts into PostgreSQL
4. Event published to NATS (items.created)
5. Event stored in events table
6. Cache invalidated in Redis
7. WebSocket broadcast to all clients
8. Response returned to frontend
```

### Agent Coordination
```
1. Agent A registers: agents.register topic
2. Agent B registers: agents.register topic
3. Both subscribe to items.* topics
4. Agent A creates item → NATS event
5. Agent B receives event via NATS
6. Both update local cache
7. Conflict detection via agent locks
8. Resolution via NATS request/reply
```

### Full-Text Search
```
1. Frontend sends GET /api/search?q=...
2. Check Redis cache first
3. If miss, query PostgreSQL tsvector
4. Results ranked by relevance
5. Cache results in Redis (1 hour TTL)
6. Return to frontend
```

## Scalability

### Horizontal Scaling
- **FastAPI**: Multiple instances behind load balancer
- **PostgreSQL**: Read replicas for queries, primary for writes
- **NATS**: Cluster mode for HA
- **Redis**: Cluster mode for distributed caching

### Vertical Scaling
- **PostgreSQL**: Increase CPU/RAM, optimize indexes
- **NATS**: Increase memory for JetStream
- **Redis**: Increase memory for cache

### Performance Targets
- Item CRUD: <100ms
- Hierarchy traversal: <200ms
- Full-text search: <500ms
- Graph traversal: <300ms
- Real-time updates: <100ms latency

## Security

### Authentication
- JWT tokens for API
- Session tokens for WebSocket
- Agent authentication via API keys

### Authorization
- Project-level access control
- Role-based permissions (admin, editor, viewer)
- Agent-specific permissions

### Data Protection
- Encryption at rest (PostgreSQL)
- Encryption in transit (TLS)
- Audit trail for compliance
- Soft deletes for data retention

## Monitoring & Observability

### Metrics
- API response times
- Database query performance
- NATS message throughput
- Redis cache hit rate
- Agent coordination latency

### Logging
- Structured logging (JSON)
- Centralized log aggregation
- Error tracking and alerting
- Audit trail for compliance

### Alerting
- High error rates
- Slow queries
- Agent failures
- Cache misses
- Disk space

## Deployment

### Local Development
```bash
docker-compose up
# PostgreSQL: localhost:5432
# NATS: localhost:4222
# Redis: localhost:6379
# FastAPI: localhost:8000
```

### Production
- **Database**: AWS RDS PostgreSQL or Supabase
- **Messaging**: NATS Cloud or self-hosted
- **Caching**: Redis Cloud or self-hosted
- **Backend**: AWS ECS, Kubernetes, or Railway
- **Frontend**: Vercel or Netlify

## Cost Analysis

### Monthly Costs (Production)
- PostgreSQL (RDS): $50-200
- NATS Cloud: $0-100
- Redis Cloud: $0-100
- Backend hosting: $50-500
- **Total**: $100-900/month

### Optimization
- Use spot instances for non-critical workloads
- Reserved instances for predictable load
- Auto-scaling based on demand
- Cache aggressively to reduce DB load

## Next Steps

1. ✅ Finalize architecture (this document)
2. ⏳ Setup PostgreSQL schema
3. ⏳ Implement FastAPI backend
4. ⏳ Setup NATS for messaging
5. ⏳ Implement Redis caching
6. ⏳ Add WebSocket support
7. ⏳ Implement full-text search
8. ⏳ Add pgvector for semantic search
9. ⏳ Optional: Neo4j for analytics


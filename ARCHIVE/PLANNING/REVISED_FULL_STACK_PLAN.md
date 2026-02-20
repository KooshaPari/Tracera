# TraceRTM - Revised Full Stack Plan

## Frontend: Project Management + Traceability Diagrammer

### Current State: ❌ Too Basic
- Just Storybook-like component showcase
- Missing project management experience
- No traceability visualization
- No diagram/graph interaction

### Revised Frontend: ✅ Professional PM Tool

**Core Views** (like Jira + Miro hybrid):

1. **Board View** (Kanban)
   - Drag-drop items by status
   - Swimlanes by owner/priority
   - Real-time collaboration

2. **Timeline View** (Gantt)
   - Project schedule visualization
   - Dependency chains
   - Milestone tracking

3. **Graph View** (Traceability Diagram)
   - Interactive node-link diagram
   - Cytoscape.js with custom layouts
   - Zoom, pan, filter, search
   - Highlight paths/dependencies
   - Real-time updates

4. **Table View** (Spreadsheet)
   - Sortable, filterable columns
   - Inline editing
   - Bulk operations
   - Export to CSV/Excel

5. **Roadmap View** (Timeline)
   - Feature roadmap
   - Release planning
   - Scope waves visualization

6. **Hierarchy View** (Tree)
   - Epic → Feature → Story → Task
   - Expand/collapse
   - Drag-drop reordering

7. **Search & Filter**
   - Global search (Meilisearch/Algolia)
   - Advanced filters
   - Saved views

### UI Components Needed

**From shadcn/ui**:
- DataTable (TanStack Table v8)
- Gantt Chart (Syncfusion or custom)
- Diagram/Graph (Cytoscape.js)
- Kanban Board (custom + dnd-kit)
- Timeline (custom)
- Tree View (custom)

**New Libraries**:
- `dnd-kit` - Drag and drop
- `cytoscape` - Graph visualization
- `react-gantt-chart` or `syncfusion` - Gantt
- `recharts` - Charts/analytics
- `zustand` - State management (replace Legend State)

## Backend: Cloud-First Architecture

### Database: Supabase (PostgreSQL)
✅ **Why**: Managed PostgreSQL with generous free tier
- 500MB storage free
- Real-time subscriptions
- Auth built-in
- Vector support (pgvector)
- Full-text search

### Caching: Upstash Redis
✅ **Why**: Serverless Redis with generous free tier
- 10,000 commands/day free
- No cold starts
- Global edge locations
- Valkey support (Redis fork)

### Messaging: Synadia NATS Cloud
✅ **Why**: Generous free tier for NATS
- Free tier available
- JetStream persistence
- Agent coordination
- Real-time events

### Search: Meilisearch (Self-Hosted or Cloud)
✅ **Why**: Open-source Algolia alternative
- Better than PostgreSQL FTS for MVP
- Typo tolerance
- Faceted search
- Free tier available
- Can self-host on Railway/Render

### Graph Database: Optional Neo4j Aura
⏳ **When**: Phase 2+
- Neo4j Aura has free tier
- Graph analytics
- Separate from primary store
- Not required for MVP

## Cloud Providers (Free Tier Friendly)

| Component | Provider | Free Tier | Cost |
|-----------|----------|-----------|------|
| **PostgreSQL** | Supabase | 500MB | $0-25/mo |
| **Redis** | Upstash | 10k cmds/day | $0-50/mo |
| **NATS** | Synadia Cloud | Generous | $0-100/mo |
| **Search** | Meilisearch Cloud | Free tier | $0-50/mo |
| **Backend** | Railway/Render | $5/mo | $5-50/mo |
| **Frontend** | Vercel | Free | $0 |
| **Neo4j** | Neo4j Aura | Free tier | $0-100/mo |
| **Total** | | | **$5-375/mo** |

## Architecture

```
┌─────────────────────────────────────────┐
│  Frontend (React 19 + Vite)             │
│  - Board, Timeline, Graph, Table views  │
│  - Drag-drop, real-time collab          │
│  - Deployed on Vercel                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  FastAPI Backend (Railway/Render)       │
│  - REST API + WebSocket                 │
│  - Agent coordination                   │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┬──────────┐
    │          │          │          │
┌───▼──┐  ┌───▼──┐  ┌───▼──┐  ┌───▼──┐
│Supa  │  │Syndia│  │Upstsh│  │Meili?│
│base  │  │NATS  │  │Redis │  │Search│
│(PG)  │  │Cloud │  │      │  │      │
└──────┘  └──────┘  └──────┘  └──────┘
```

## Implementation Phases

### Phase 1: MVP (Weeks 1-2)
**Backend**:
- Supabase PostgreSQL schema
- FastAPI REST API
- Synadia NATS integration
- Upstash Redis caching

**Frontend**:
- Board View (Kanban)
- Table View (Spreadsheet)
- Basic Graph View
- Search integration

### Phase 2: Enhanced (Weeks 3-4)
**Backend**:
- Meilisearch integration
- Event sourcing
- Agent coordination

**Frontend**:
- Timeline View (Gantt)
- Hierarchy View (Tree)
- Roadmap View
- Advanced filtering

### Phase 3: Analytics (Weeks 5+)
**Backend**:
- Neo4j Aura integration
- Materialized views
- Query optimization

**Frontend**:
- Analytics dashboard
- Impact analysis
- Scope wave visualization

## Key Differences from Original Plan

| Aspect | Original | Revised |
|--------|----------|---------|
| **Frontend** | Storybook showcase | Jira-like PM tool |
| **Views** | 7 basic views | 7 professional views |
| **Database** | Self-hosted PG | Supabase (managed) |
| **Caching** | Self-hosted Redis | Upstash (serverless) |
| **Messaging** | Self-hosted NATS | Synadia Cloud |
| **Search** | PostgreSQL FTS | Meilisearch |
| **Deployment** | Docker Compose | Cloud-native |
| **Cost** | $100-900/mo | $5-375/mo |
| **Complexity** | High (self-hosted) | Low (managed services) |

## Why This is Better

✅ **Lower cost** - Cloud free tiers
✅ **Less ops** - Managed services
✅ **Better UX** - Professional PM interface
✅ **Scalable** - Cloud-native
✅ **Maintainable** - Fewer moving parts
✅ **Production-ready** - Day 1

## Next Steps

1. Redesign frontend for PM experience
2. Setup Supabase project
3. Setup Upstash Redis
4. Setup Synadia NATS Cloud
5. Implement FastAPI backend
6. Integrate Meilisearch
7. Deploy to production

Ready to build the real thing! 🚀


# Complete Infrastructure Setup Guide

## Overview

This guide covers production-ready setup for:
- ✅ Redis (caching + sessions)
- ✅ NATS (event streaming)
- ✅ Supabase (PostgreSQL + auth)
- ✅ Neo4j (graph database)
- ✅ Algolia/Meilisearch (search)

## Quick Start (30 minutes)

### 1. Redis Setup (5 min)
```bash
# Local development
docker run -d -p 6379:6379 redis:7-alpine

# Production (Upstash)
# Get connection string from https://console.upstash.com
export REDIS_URL="redis://default:password@host:port"
```

### 2. NATS Setup (5 min)
```bash
# Local development
docker run -d -p 4222:4222 -p 8222:8222 nats:latest

# Production (Synadia Cloud)
# Get connection string from https://app.synadia.com
export NATS_URL="nats://user:password@host:port"
```

### 3. Supabase Setup (5 min)
```bash
# Already configured in previous phases
export SUPABASE_URL="https://project.supabase.co"
export SUPABASE_KEY="your-anon-key"
export DATABASE_URL="postgresql://user:password@host:port/db"
```

### 4. Neo4j Setup (5 min)
```bash
# Local development
docker run -d -p 7687:7687 -p 7474:7474 neo4j:latest

# Production (Neo4j Aura)
export NEO4J_URI="neo4j+s://host:port"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
```

### 5. Search Setup (5 min)
```bash
# Meilisearch (recommended for free tier)
docker run -d -p 7700:7700 getmeili/meilisearch:latest

# Or Algolia (if you prefer)
export ALGOLIA_APP_ID="your-app-id"
export ALGOLIA_API_KEY="your-api-key"
```

## Environment Variables

```bash
# Redis
REDIS_URL=redis://localhost:6379

# NATS
NATS_URL=nats://localhost:4222

# Supabase
SUPABASE_URL=https://project.supabase.co
SUPABASE_KEY=your-anon-key
DATABASE_URL=postgresql://user:password@localhost:5432/tracertm

# Neo4j
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Search (choose one)
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_KEY=your-master-key
# OR
ALGOLIA_APP_ID=your-app-id
ALGOLIA_API_KEY=your-api-key
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Go Backend                           │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Handlers   │  │   Services   │  │  Middleware  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
         │                │                │
    ┌────┴────┐      ┌────┴────┐      ┌────┴────┐
    │          │      │          │      │          │
    ▼          ▼      ▼          ▼      ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Redis  │ │ NATS   │ │Supabase│ │ Neo4j  │ │ Search │
│ Cache  │ │ Events │ │  SQL   │ │ Graph  │ │ Index  │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

## Data Flow

1. **Request** → Handler
2. **Cache Check** → Redis (cache-aside pattern)
3. **Query** → Supabase (PostgreSQL)
4. **Graph** → Neo4j (relationships)
5. **Event** → NATS (publish)
6. **Index** → Search (Algolia/Meilisearch)
7. **Response** → Client

## Next Steps

1. See REDIS_COMPLETE_SETUP.md
2. See NATS_COMPLETE_SETUP.md
3. See SUPABASE_COMPLETE_SETUP.md
4. See NEO4J_COMPLETE_SETUP.md
5. See SEARCH_COMPARISON.md
6. See INFRASTRUCTURE_INTEGRATION_TESTS.md


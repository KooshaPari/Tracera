# Cloud Providers Guide - Free Tier Friendly

## Database: Supabase (PostgreSQL)

### Why Supabase?
✅ Managed PostgreSQL with generous free tier
✅ Real-time subscriptions built-in
✅ Auth included
✅ pgvector support
✅ Full-text search
✅ Easy to scale

### Free Tier
- **Storage**: 500MB
- **Bandwidth**: 2GB/month
- **Connections**: 10
- **Real-time**: Included
- **Auth**: Included

### Pricing
- Free: $0
- Pro: $25/month (100GB storage)
- Team: $599/month

### Setup
```bash
# Create project at supabase.com
# Get connection string
DATABASE_URL=postgresql://user:pass@host/db

# Run migrations
alembic upgrade head
```

### Features
- PostgreSQL 15
- pgvector extension
- Full-text search (tsvector)
- Soft deletes
- Event sourcing
- Recursive CTEs for hierarchy

---

## Caching: Upstash Redis

### Why Upstash?
✅ Serverless Redis (no cold starts)
✅ Generous free tier
✅ Global edge locations
✅ Valkey support (Redis fork)
✅ Pay-as-you-go pricing

### Free Tier
- **Commands**: 10,000/day
- **Storage**: 256MB
- **Connections**: 100
- **Bandwidth**: Included

### Pricing
- Free: $0 (10k cmds/day)
- Pay-as-you-go: $0.20 per 100k commands
- Pro: $29/month (unlimited)

### Setup
```bash
# Create at upstash.com
# Get connection string
REDIS_URL=redis://default:password@host:port

# Use in Python
import redis
r = redis.from_url(os.getenv('REDIS_URL'))
```

### Use Cases
- Session storage
- Item/project caching
- Search result caching
- Distributed locks
- Real-time pub/sub

### Valkey Alternative
- Upstash supports Valkey (Redis fork)
- Same API as Redis
- Open source
- No licensing concerns

---

## Messaging: Synadia NATS Cloud

### Why Synadia NATS?
✅ Generous free tier
✅ Sub-millisecond latency
✅ JetStream persistence
✅ Agent coordination
✅ Real-time events

### Free Tier
- **Connections**: 10
- **Throughput**: Generous
- **Storage**: Limited
- **14-day trial**: Full features

### Pricing
- Free: $0 (limited)
- Starter: $0-50/month
- Pro: $100+/month

### Setup
```bash
# Create at synadia.com
# Get connection string
NATS_URL=nats://user:pass@host:port

# Use in Python
import nats
nc = await nats.connect(os.getenv('NATS_URL'))
```

### Features
- Pub/sub messaging
- Request/reply
- JetStream persistence
- Clustering
- Built-in monitoring

---

## Search: Meilisearch

### Why Meilisearch?
✅ Open-source Algolia alternative
✅ Better than PostgreSQL FTS
✅ Typo tolerance
✅ Faceted search
✅ Free tier available

### Options

#### 1. Meilisearch Cloud
- **Free tier**: Available
- **Pricing**: $0-50/month
- **Setup**: Managed service

#### 2. Self-Hosted (Railway/Render)
- **Cost**: $5-10/month
- **Setup**: Docker container
- **Control**: Full

### Setup
```bash
# Option 1: Cloud
MEILISEARCH_URL=https://...
MEILISEARCH_KEY=...

# Option 2: Self-hosted on Railway
docker run -p 7700:7700 getmeili/meilisearch

# Use in Python
from meilisearch import Client
client = Client(os.getenv('MEILISEARCH_URL'), os.getenv('MEILISEARCH_KEY'))
```

### Features
- Full-text search
- Typo tolerance
- Faceted search
- Sorting
- Filtering
- Ranking rules

---

## Graph Database: Neo4j Aura (Optional)

### Why Neo4j Aura?
✅ Managed Neo4j in cloud
✅ Free tier available
✅ Graph analytics
✅ Separate from primary store

### Free Tier
- **Storage**: 100GB
- **Throughput**: Limited
- **Connections**: 5

### Pricing
- Free: $0 (limited)
- Professional: $0.06/hour
- Enterprise: Custom

### When to Use
- Phase 2+
- Graph analytics
- Path finding
- Community detection
- Not required for MVP

### Setup
```bash
# Create at neo4j.com/cloud
# Get connection string
NEO4J_URL=neo4j+s://...
NEO4J_USER=neo4j
NEO4J_PASSWORD=...

# Use in Python
from neo4j import GraphDatabase
driver = GraphDatabase.driver(os.getenv('NEO4J_URL'), auth=(user, password))
```

---

## Backend: Railway or Render

### Railway
✅ $5/month credit
✅ Easy deployment
✅ PostgreSQL, Redis, etc.
✅ GitHub integration

### Render
✅ Free tier available
✅ Easy deployment
✅ Auto-scaling
✅ GitHub integration

### Setup
```bash
# Railway
railway login
railway init
railway up

# Render
# Connect GitHub repo
# Auto-deploy on push
```

---

## Frontend: Vercel

### Why Vercel?
✅ Free tier
✅ Next.js/Vite optimized
✅ Edge functions
✅ Analytics
✅ GitHub integration

### Free Tier
- **Deployments**: Unlimited
- **Bandwidth**: 100GB/month
- **Functions**: 100GB/month
- **Analytics**: Included

### Setup
```bash
# Connect GitHub repo
# Auto-deploy on push
# Custom domain
```

---

## Total Cost Estimate

| Service | Free Tier | Paid |
|---------|-----------|------|
| Supabase | $0 | $25/mo |
| Upstash | $0 | $20/mo |
| Synadia | $0 | $50/mo |
| Meilisearch | $0 | $10/mo |
| Railway | $5 | $5-50/mo |
| Vercel | $0 | $0 |
| Neo4j (optional) | $0 | $50+/mo |
| **Total** | **$5/mo** | **$160-200/mo** |

---

## Recommended Setup

### MVP (Free Tier)
```
Supabase (free) + Upstash (free) + Synadia (free) + 
Meilisearch (free) + Railway ($5) + Vercel (free)
= $5/month
```

### Production (Paid)
```
Supabase ($25) + Upstash ($20) + Synadia ($50) + 
Meilisearch ($10) + Railway ($50) + Vercel ($0)
= $155/month
```

### With Analytics (Paid)
```
Above + Neo4j Aura ($50)
= $205/month
```

---

## Setup Checklist

- [ ] Create Supabase project
- [ ] Create Upstash Redis instance
- [ ] Create Synadia NATS account
- [ ] Setup Meilisearch (cloud or self-hosted)
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Vercel
- [ ] Configure environment variables
- [ ] Test all integrations
- [ ] Setup monitoring/alerts

Ready to deploy! 🚀


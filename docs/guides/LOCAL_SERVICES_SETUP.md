# Local Services Setup Guide

## Prerequisites
```bash
brew install neo4j postgresql redis nats-server
```

---

## 1. PostgreSQL Setup

```bash
# Start PostgreSQL
brew services start postgresql

# Create database and user
createdb tracertm
psql tracertm -c "CREATE USER tracertm WITH PASSWORD 'tracertm_password';"
psql tracertm -c "ALTER USER tracertm CREATEDB;"

# Run migrations
cd backend
alembic upgrade head
```

---

## 2. Redis Setup

```bash
# Start Redis
brew services start redis

# Verify
redis-cli ping  # Should return PONG
```

---

## 3. NATS Setup

```bash
# Start NATS
brew services start nats-server

# Verify
nats-cli server info
```

---

## 4. Neo4j Setup (REQUIRED - Local Homebrew)

```bash
# Install
brew install neo4j

# Start service
brew services start neo4j

# Access web console
# http://localhost:7474
# Default: neo4j / neo4j
# Change password on first login

# Verify connection
cypher-shell -u neo4j -p <password> "RETURN 1"
```

**Update .env**:
```
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your-password>
```

---

## 5. Hatchet Setup (REQUIRED)

### Option A: Cloud Token (Recommended for Dev)
```bash
# Get token from https://cloud.onhatchet.run
# Add to .env:
HATCHET_CLIENT_TOKEN=<your-token>
```

### Option B: Local Instance
```bash
# Docker Compose (if available)
docker-compose up hatchet
```

---

## 6. Voyage AI Setup (REQUIRED)

```bash
# Get API key from https://www.voyageai.com
# Add to .env:
VOYAGE_API_KEY=pa_xxx
```

---

## 7. GitHub Integration Setup (REQUIRED)

```bash
# Private key already at:
# /Users/kooshapari/Downloads/tracertm.2026-01-28.private-key.pem

# Verify file exists
ls -la /Users/kooshapari/Downloads/tracertm.2026-01-28.private-key.pem

# Add to .env (already configured):
GITHUB_APP_ID=2750779
GITHUB_APP_CLIENT_ID=Iv23liGR8KgbxkmtriYr
GITHUB_PRIVATE_KEY_PATH=/Users/kooshapari/Downloads/tracertm.2026-01-28.private-key.pem
```

---

## Verification Script

```bash
#!/bin/bash
echo "Checking required services..."

# PostgreSQL
psql -U tracertm -d tracertm -c "SELECT 1" && echo "✅ PostgreSQL" || echo "❌ PostgreSQL"

# Redis
redis-cli ping | grep PONG && echo "✅ Redis" || echo "❌ Redis"

# NATS
nats-cli server info > /dev/null && echo "✅ NATS" || echo "❌ NATS"

# Neo4j
cypher-shell -u neo4j -p $NEO4J_PASSWORD "RETURN 1" && echo "✅ Neo4j" || echo "❌ Neo4j"

# Hatchet
curl -s -H "Authorization: Bearer $HATCHET_CLIENT_TOKEN" \
  https://cloud.onhatchet.run/api/health && echo "✅ Hatchet" || echo "❌ Hatchet"
```

---

## Troubleshooting

| Service | Issue | Solution |
|---------|-------|----------|
| Neo4j | Port 7687 in use | `lsof -i :7687` then kill process |
| Redis | Connection refused | `brew services restart redis` |
| NATS | Can't connect | `brew services restart nats-server` |
| Hatchet | Token invalid | Regenerate from cloud.onhatchet.run |


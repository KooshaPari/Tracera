# Infrastructure Deployment Guide

## Pre-Deployment Checklist

### Local Testing
- [ ] All services running locally
- [ ] All tests passing
- [ ] No connection errors
- [ ] Cache working
- [ ] Events publishing
- [ ] Search indexing
- [ ] Graph queries working

### Code Review
- [ ] No hardcoded credentials
- [ ] Environment variables set
- [ ] Error handling complete
- [ ] Logging configured
- [ ] Monitoring enabled

## Staging Deployment

### 1. Redis (Upstash)

```bash
# Create Upstash account
# Create Redis database
# Get connection string

# Test connection
redis-cli -u $REDIS_URL ping

# Set environment variable
export REDIS_URL="redis://default:password@host:port"
```

### 2. NATS (Synadia)

```bash
# Create Synadia account
# Create NATS account
# Get connection string

# Test connection
nats-cli -s $NATS_URL server info

# Set environment variable
export NATS_URL="nats://user:password@host:port"
```

### 3. Supabase (Already Set Up)

```bash
# Already configured
# Verify connection
psql $DATABASE_URL -c "SELECT 1"

# Environment variables
export SUPABASE_URL="https://..."
export DATABASE_URL="postgresql://..."
```

### 4. Neo4j (Aura)

```bash
# Create Neo4j Aura instance
# Get connection string

# Test connection
cypher-shell -a $NEO4J_URI -u $NEO4J_USER -p $NEO4J_PASSWORD "RETURN 1"

# Set environment variables
export NEO4J_URI="neo4j+s://..."
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="..."
```

### 5. Meilisearch (Cloud)

```bash
# Create Meilisearch Cloud account
# Create instance
# Get API key

# Test connection
curl -H "Authorization: Bearer $MEILISEARCH_KEY" $MEILISEARCH_URL/health

# Set environment variables
export MEILISEARCH_URL="https://..."
export MEILISEARCH_KEY="..."
```

### 6. Deploy Backend

```bash
# Build
cd backend
go build -o tracertm-backend

# Test
./tracertm-backend

# Deploy to staging server
scp tracertm-backend user@staging:/app/
ssh user@staging "cd /app && ./tracertm-backend"
```

## Production Deployment

### 1. Infrastructure Setup

```bash
# All services configured (same as staging)
# Add monitoring and alerting
# Enable backups
# Configure auto-scaling
```

### 2. Environment Variables

```bash
# Production .env
REDIS_URL=redis://...
NATS_URL=nats://...
DATABASE_URL=postgresql://...
NEO4J_URI=neo4j+s://...
NEO4J_USER=neo4j
NEO4J_PASSWORD=...
MEILISEARCH_URL=https://...
MEILISEARCH_KEY=...
```

### 3. Build and Deploy

```bash
# Build
go build -o tracertm-backend

# Test
./tracertm-backend

# Deploy
docker build -t tracertm-backend:latest .
docker push tracertm-backend:latest

# Deploy to production
kubectl apply -f k8s/deployment.yaml
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM golang:1.25-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o tracertm-backend backend/main.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/tracertm-backend .
EXPOSE 8080
CMD ["./tracertm-backend"]
```

### docker-compose.yml

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nats:
    image: nats:latest
    ports:
      - "4222:4222"
    volumes:
      - nats_data:/data

  neo4j:
    image: neo4j:latest
    ports:
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/password
    volumes:
      - neo4j_data:/data

  meilisearch:
    image: getmeili/meilisearch:latest
    ports:
      - "7700:7700"
    volumes:
      - meilisearch_data:/meili_data

  backend:
    build: .
    ports:
      - "8080:8080"
    environment:
      REDIS_URL: redis://redis:6379
      NATS_URL: nats://nats:4222
      DATABASE_URL: postgresql://...
      NEO4J_URI: neo4j://neo4j:7687
      MEILISEARCH_URL: http://meilisearch:7700
    depends_on:
      - redis
      - nats
      - neo4j
      - meilisearch

volumes:
  redis_data:
  nats_data:
  neo4j_data:
  meilisearch_data:
```

## Kubernetes Deployment

### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tracertm-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tracertm-backend
  template:
    metadata:
      labels:
        app: tracertm-backend
    spec:
      containers:
      - name: backend
        image: tracertm-backend:latest
        ports:
        - containerPort: 8080
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: infrastructure-secrets
              key: redis-url
        - name: NATS_URL
          valueFrom:
            secretKeyRef:
              name: infrastructure-secrets
              key: nats-url
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: infrastructure-secrets
              key: database-url
        - name: NEO4J_URI
          valueFrom:
            secretKeyRef:
              name: infrastructure-secrets
              key: neo4j-uri
        - name: MEILISEARCH_URL
          valueFrom:
            secretKeyRef:
              name: infrastructure-secrets
              key: meilisearch-url
```

## Monitoring & Alerting

### 1. Prometheus Metrics

```go
// backend/internal/metrics/metrics.go
import "github.com/prometheus/client_golang/prometheus"

var (
    requestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "request_duration_seconds",
        },
        []string{"method", "endpoint"},
    )
    
    cacheHits = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "cache_hits_total",
        },
        []string{"key"},
    )
)
```

### 2. Logging

```go
// Use structured logging
log.WithFields(log.Fields{
    "project_id": projectID,
    "action": "get_items",
    "duration": duration,
}).Info("Request completed")
```

### 3. Alerting

```yaml
# prometheus-rules.yaml
groups:
- name: tracertm
  rules:
  - alert: HighErrorRate
    expr: rate(errors_total[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected"
```

## Rollback Procedure

### 1. Identify Issue
```bash
# Check logs
kubectl logs -f deployment/tracertm-backend

# Check metrics
# Check error rates
```

### 2. Rollback
```bash
# Rollback to previous version
kubectl rollout undo deployment/tracertm-backend

# Or deploy specific version
kubectl set image deployment/tracertm-backend \
  backend=tracertm-backend:v1.0.0
```

## Post-Deployment

### 1. Verify
- [ ] All services connected
- [ ] No errors in logs
- [ ] Metrics normal
- [ ] Requests working
- [ ] Cache working
- [ ] Events publishing

### 2. Monitor
- [ ] Watch error rates
- [ ] Monitor latency
- [ ] Check resource usage
- [ ] Verify backups

### 3. Document
- [ ] Update runbooks
- [ ] Document issues
- [ ] Update procedures
- [ ] Share with team

## Cost Summary

| Service | Free Tier | Production |
|---------|-----------|-----------|
| Redis | Free (local) | $0/month (Upstash) |
| NATS | Free (local) | $0/month (Synadia) |
| Supabase | Free (500MB) | $25/month |
| Neo4j | Free (200K nodes) | $0.06/hour (Aura) |
| Meilisearch | Free (local) | $0.50/month (cloud) |
| **Total** | **Free** | **~$30/month** |

## Next Steps

1. Set up staging environment
2. Deploy and test
3. Fix any issues
4. Deploy to production
5. Monitor and optimize


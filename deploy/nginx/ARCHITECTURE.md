# TracerTM API Gateway Architecture

## Visual Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                    │
│                     (Web, Mobile, API Consumers)                        │
└────────────────────────────┬────────────────────────────────────────────┘
                             │ HTTPS (443) / HTTP (80)
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│                         NGINX API GATEWAY                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Rate Limiting                                                   │  │
│  │  • API:  100 req/s (burst 50)                                   │  │
│  │  • AI:   10 req/s  (burst 20)                                   │  │
│  │  • Conn: 50 concurrent/IP                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Caching (Go Backend Only)                                       │  │
│  │  • TTL: 5 minutes                                               │  │
│  │  • Size: 1GB max                                                │  │
│  │  • Key: URI + Body                                              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Security                                                        │  │
│  │  • SSL/TLS (Modern ciphers, TLS 1.2+)                          │  │
│  │  • HSTS, CSP, X-Frame-Options                                  │  │
│  │  • CORS with credentials                                        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────────────┬────────────────────────┘
             │                                  │
             │ Intelligent Routing              │
             │                                  │
    ┌────────▼────────┐              ┌─────────▼─────────┐
    │   Python Path   │              │    Go Path        │
    │   Detection     │              │   Detection       │
    └────────┬────────┘              └─────────┬─────────┘
             │                                  │
    /api/v1/ai/*                       /api/v1/items/*
    /api/v1/specifications/*           /api/v1/links/*
    /api/v1/spec-analytics/*           /api/v1/projects/*
    /api/v1/execution/*                /api/v1/graph/*
    /api/v1/auth/*                     /api/v1/bulk/*
    /api/v1/mcp/*                      /api/v1/search/*
    /api/v1/blockchain/*               /api/v1/webhooks/*
             │                         /ws (WebSocket)
             │                                  │
    ┌────────▼──────────────┐         ┌────────▼──────────────┐
    │  PYTHON BACKEND       │         │  GO BACKEND           │
    │  Port: 8000           │         │  Port: 8080           │
    │  ─────────────────    │         │  ─────────────────    │
    │  FastAPI/Uvicorn      │         │  Gin Framework        │
    │                       │         │                       │
    │  Features:            │         │  Features:            │
    │  • AI/LLM Operations  │         │  • High throughput    │
    │  • Spec Management    │         │  • Low latency        │
    │  • Analytics          │         │  • WebSocket          │
    │  • Test Execution     │         │  • CRUD operations    │
    │  • MCP Integration    │         │  • Graph operations   │
    │  • Authentication     │         │  • Bulk actions       │
    │                       │         │                       │
    │  Config:              │         │  Config:              │
    │  • Timeout: 600s      │         │  • Timeout: 300s      │
    │  • No buffering       │         │  • Caching enabled    │
    │  • Streaming          │         │  • Keepalive: 64      │
    │  • Keepalive: 32      │         │                       │
    └───────────┬───────────┘         └───────────┬───────────┘
                │                                  │
                └──────────┬───────────────────────┘
                           │
            ┌──────────────▼──────────────┐
            │      DATA LAYER             │
            │  ─────────────────────────  │
            │  • PostgreSQL (Primary DB)  │
            │  • Redis (Cache/Session)    │
            │  • NATS (Message Queue)     │
            └──────────────┬──────────────┘
                           │
            ┌──────────────▼──────────────┐
            │      MONITORING             │
            │  ─────────────────────────  │
            │  • Prometheus (Metrics)     │
            │  • Grafana (Dashboards)     │
            │  • Exporters (Nginx/DB)     │
            └─────────────────────────────┘
```

## Request Flow

### 1. Go Backend Request (e.g., GET /api/v1/items)

```
Client Request
    │
    ▼
[Nginx Gateway]
    │
    ├─→ [Rate Limiting] ✓ (100 req/s)
    │
    ├─→ [Path Detection] → Go backend
    │
    ├─→ [Cache Check] → HIT? → Return cached
    │                    MISS? ↓
    │
    ├─→ [Go Backend] → Process request
    │                  Query DB
    │                  Generate response
    │
    ├─→ [Cache Store] → Store for 5min
    │
    └─→ [Add Headers] → X-Cache-Status: MISS
                       CORS headers
                       Security headers
    │
    ▼
Response to Client
```

### 2. Python Backend Request (e.g., POST /api/v1/ai/chat)

```
Client Request
    │
    ▼
[Nginx Gateway]
    │
    ├─→ [Rate Limiting] ✓ (10 req/s for AI)
    │
    ├─→ [Path Detection] → Python backend
    │
    ├─→ [No Caching] → (POST/streaming)
    │
    ├─→ [Python Backend] → AI processing
    │                      Stream response
    │
    ├─→ [No Buffering] → Stream to client
    │
    └─→ [Add Headers] → CORS headers
                        Security headers
    │
    ▼
Streamed Response to Client
```

### 3. WebSocket Request (ws://domain/ws)

```
Client WebSocket
    │
    ▼
[Nginx Gateway]
    │
    ├─→ [Upgrade Check] → WebSocket upgrade
    │
    ├─→ [Go Backend] → Establish WS connection
    │
    └─→ [Long Timeout] → 24 hour timeout
    │
    ▼
Persistent Connection
```

## Component Responsibilities

### Nginx Gateway
- **Route requests** to appropriate backend
- **Enforce rate limits** to prevent abuse
- **Cache responses** from Go backend
- **Terminate SSL/TLS** connections
- **Add security headers**
- **Load balance** across backend instances
- **Health check** backends for failover

### Go Backend
- **High-performance operations**
  - CRUD for items, links, projects
  - Graph traversal and queries
  - Bulk operations
  - Search indexing
  - Webhook management
- **WebSocket server** for real-time updates
- **Cache-friendly** with stable responses

### Python Backend
- **Compute-intensive operations**
  - AI/LLM inference
  - Specification analysis
  - Analytics processing
  - Test execution orchestration
- **Streaming responses** for AI
- **Authentication** and authorization
- **MCP integration**

### Data Layer
- **PostgreSQL**: Primary relational database
- **Redis**: Session storage, caching, pub/sub
- **NATS**: Message queue for async operations

### Monitoring
- **Prometheus**: Collects metrics from all services
- **Grafana**: Visualizes performance dashboards
- **Exporters**: Specialized metric collectors

## Scaling Strategy

### Horizontal Scaling
```
        Load Balancer
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
 Nginx-1  Nginx-2  Nginx-3
    │         │         │
    └─────────┼─────────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
   Go-1     Go-2     Go-3
    │         │         │
  Python-1 Python-2 Python-3
    │         │         │
    └─────────┼─────────┘
              ▼
         Shared DB Pool
```

### Vertical Scaling Priorities
1. **Python**: Increase CPU/RAM first (AI workloads)
2. **Go**: Increase connections/workers (throughput)
3. **DB**: Increase connection pool, RAM for cache

## Network Topology

```
External Network (Internet)
         │
         │ Port 80, 443
         ▼
    ┌─────────┐
    │  Nginx  │ (DMZ)
    └────┬────┘
         │
    ─────┼───── Internal Network (Docker bridge)
         │
    ┌────┴───────────────────────┐
    │                            │
    ▼                            ▼
┌────────┐                  ┌────────┐
│   Go   │                  │ Python │
└───┬────┘                  └───┬────┘
    │                           │
    └────────┬──────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌────────┐      ┌─────────┐
│Postgres│      │  Redis  │
│  NATS  │      │         │
└────────┘      └─────────┘
```

## Security Zones

### Public Zone
- Nginx (port 80, 443)
- Exposed to internet
- Rate limiting enforced
- SSL/TLS termination

### Application Zone
- Go backend (internal only)
- Python backend (internal only)
- Service-to-service communication
- Mutual TLS (optional)

### Data Zone
- PostgreSQL (internal only)
- Redis (internal only)
- NATS (internal only)
- Encrypted at rest

## Performance Characteristics

### Nginx Gateway
- **Throughput**: 50,000+ req/s
- **Latency**: <1ms overhead
- **Connections**: 10,000+ concurrent
- **Memory**: ~50MB base + cache

### Go Backend
- **Throughput**: 5,000+ req/s per instance
- **Latency**: 5-50ms (p95)
- **Connections**: 10,000+ concurrent
- **Memory**: ~200MB per instance

### Python Backend
- **Throughput**: 500-1,000 req/s per instance
- **Latency**: 50-500ms (p95, excluding AI)
- **AI latency**: 1-10s (model dependent)
- **Memory**: ~500MB base + models

## Failure Modes & Recovery

### Nginx Failure
- **Detection**: Health check fails
- **Recovery**: Restart container (Docker)
- **Mitigation**: Run multiple Nginx instances

### Go Backend Failure
- **Detection**: Health check fails (3 failures)
- **Recovery**: Nginx stops routing for 30s
- **Mitigation**: Auto-restart, multiple instances

### Python Backend Failure
- **Detection**: Health check fails (3 failures)
- **Recovery**: Nginx stops routing for 30s
- **Mitigation**: Auto-restart, queue requests

### Database Failure
- **Detection**: Connection errors
- **Recovery**: Both backends retry
- **Mitigation**: DB replication, connection pooling

## Configuration Hierarchy

```
nginx/nginx.conf (Global settings)
    │
    ├─→ nginx/conf.d/tracertm.conf (Routing)
    │       │
    │       ├─→ Upstream definitions
    │       ├─→ Rate limiting zones
    │       ├─→ Cache configuration
    │       └─→ Location blocks
    │
    └─→ nginx/conf.d/ssl.conf (Production SSL)
            │
            ├─→ Certificate paths
            ├─→ Cipher configuration
            └─→ HSTS headers
```

## Deployment Workflow

```
1. Build
   ├─→ Build Go binary
   ├─→ Build Python image
   └─→ Pull Nginx image

2. Test
   ├─→ Unit tests
   ├─→ Integration tests
   └─→ Gateway tests

3. Deploy
   ├─→ Pull images
   ├─→ Start infrastructure (DB, Redis, NATS)
   ├─→ Start backends
   ├─→ Start Nginx
   └─→ Run health checks

4. Monitor
   ├─→ Check Grafana dashboards
   ├─→ Review error logs
   └─→ Verify metrics
```

## Summary

The TracerTM API Gateway provides:
- **Intelligent routing** between specialized backends
- **Performance optimization** through caching
- **Security** via SSL/TLS and headers
- **Reliability** through health checks and failover
- **Observability** via comprehensive monitoring
- **Scalability** to handle growing traffic

This architecture enables TracerTM to serve both high-throughput CRUD operations (Go) and compute-intensive AI workloads (Python) efficiently from a unified API endpoint.

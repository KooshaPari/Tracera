# ADR-0010: Multi-Language Backend Architecture

**Status:** Accepted
**Date:** 2026-02-05
**Deciders:** Development Team
**Supersedes:** N/A

---

## Context

TraceRTM backend requires:

1. **Services layer:** Business logic, traceability calculations (Python)
2. **Performance layer:** Graph algorithms, token bridge, gRPC services (Go)
3. **Inter-service communication:** Python ↔ Go data exchange
4. **Unified API:** Single REST API surface for frontend
5. **Token efficiency:** Go service minimizes Python→Claude API calls

Why two languages:
- **Python:** Rich ecosystem (FastAPI, SQLAlchemy, AI libraries), rapid development
- **Go:** Performance (graph algorithms), concurrency (gRPC), production-grade error handling

Technology constraints:
- **Python:** 3.12+, async/await, FastAPI
- **Go:** 1.25.7+, Echo framework, gRPC
- **Communication:** gRPC (typed), HTTP (REST fallback)

## Decision

We will run **Python (FastAPI) as primary backend** with **Go as performance layer** (optional microservice).

**Architecture:**
1. **Python backend:** FastAPI REST API, SQLAlchemy ORM, service layer
2. **Go backend:** gRPC server for:
   - Graph algorithms (shortest path, cycle detection)
   - Token bridge (minimize Claude API calls from Python)
   - High-throughput operations (bulk imports)
3. **Communication:** Python calls Go via gRPC (in-process or network)
4. **Deployment:** Python + Go in same Docker container OR separate services

## Rationale

### Technology Stack

**Python (pyproject.toml):**
```toml
dependencies = [
    "fastapi>=0.115.0",        # REST API
    "uvicorn[standard]>=0.32.0",  # ASGI server
    "sqlalchemy[asyncio]>=2.0.46",  # ORM
    "grpcio>=1.70.0",          # gRPC client (Python → Go)
]
```

**Go (backend/go.mod):**
```go
require (
    github.com/labstack/echo/v4 v4.15.0     // HTTP framework
    google.golang.org/grpc v1.77.0           // gRPC server
    google.golang.org/protobuf v1.36.10      // Protobuf
    go.temporal.io/sdk v1.39.0               // Workflow orchestration
)
```

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Client (Frontend)                          │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Backend (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  REST API (/api/*)                                   │  │
│  │  ├─ /projects, /requirements, /links                 │  │
│  │  ├─ /coverage, /scenarios                            │  │
│  │  └─ /graph/analysis (delegates to Go)                │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  Service Layer                                       │  │
│  │  ├─ RequirementService                               │  │
│  │  ├─ LinkService                                      │  │
│  │  ├─ CoverageService                                  │  │
│  │  └─ GraphService (calls Go gRPC)                     │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  SQLAlchemy ORM                                      │  │
│  │  ├─ Async queries                                    │  │
│  │  └─ PostgreSQL connection pool                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ gRPC
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Go Backend (gRPC Server)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  gRPC Services                                       │  │
│  │  ├─ GraphAnalysisService                             │  │
│  │  │  ├─ ShortestPath(source, target)                  │  │
│  │  │  ├─ DetectCycles(project_id)                      │  │
│  │  │  └─ ImpactAnalysis(item_id, depth)                │  │
│  │  ├─ TokenBridgeService                               │  │
│  │  │  └─ OptimizeLLMCall(prompt, context)              │  │
│  │  └─ BulkImportService                                │  │
│  │     └─ ImportJiraIssues(project_id, issues)          │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  Graph Algorithms                                    │  │
│  │  ├─ Dijkstra, A* (shortest path)                     │  │
│  │  ├─ Tarjan (cycle detection)                         │  │
│  │  └─ BFS/DFS (traversal)                              │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  PostgreSQL Client (pgx)                             │  │
│  │  └─ Direct SQL queries (optimized)                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### gRPC Service Definition (protobuf)

```protobuf
// proto/graph_analysis.proto
syntax = "proto3";

package tracertm.graph;

service GraphAnalysis {
  rpc ShortestPath(ShortestPathRequest) returns (ShortestPathResponse);
  rpc DetectCycles(DetectCyclesRequest) returns (DetectCyclesResponse);
  rpc ImpactAnalysis(ImpactAnalysisRequest) returns (ImpactAnalysisResponse);
}

message ShortestPathRequest {
  string source_id = 1;
  string target_id = 2;
  repeated string link_types = 3;  // ["satisfies", "tests"]
}

message ShortestPathResponse {
  repeated string path = 1;  // [source_id, intermediate_id, target_id]
  int32 distance = 2;
}

message ImpactAnalysisRequest {
  string item_id = 1;
  int32 max_depth = 2;
}

message ImpactAnalysisResponse {
  repeated ImpactNode nodes = 1;
  repeated ImpactEdge edges = 2;
}

message ImpactNode {
  string id = 1;
  string title = 2;
  string item_type = 3;
  int32 depth = 4;
}

message ImpactEdge {
  string source_id = 1;
  string target_id = 2;
  string link_type = 3;
}
```

### Python → Go gRPC Client

```python
import grpc
from tracertm.proto import graph_analysis_pb2, graph_analysis_pb2_grpc

async def analyze_impact(item_id: str, max_depth: int = 3) -> dict:
    """Call Go gRPC service for impact analysis."""
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = graph_analysis_pb2_grpc.GraphAnalysisStub(channel)
        request = graph_analysis_pb2.ImpactAnalysisRequest(
            item_id=item_id,
            max_depth=max_depth,
        )
        response = await stub.ImpactAnalysis(request)

        return {
            "nodes": [{"id": n.id, "title": n.title, "depth": n.depth} for n in response.nodes],
            "edges": [{"source": e.source_id, "target": e.target_id} for e in response.edges],
        }
```

### Go gRPC Server Implementation

```go
// backend/internal/grpc/graph_service.go
package grpc

import (
    "context"
    pb "github.com/kooshapari/tracertm-backend/proto"
)

type GraphAnalysisServer struct {
    pb.UnimplementedGraphAnalysisServer
    repo *repository.GraphRepository
}

func (s *GraphAnalysisServer) ImpactAnalysis(
    ctx context.Context,
    req *pb.ImpactAnalysisRequest,
) (*pb.ImpactAnalysisResponse, error) {
    // Run BFS from item_id up to max_depth
    nodes, edges := s.repo.BFS(ctx, req.ItemId, int(req.MaxDepth))

    response := &pb.ImpactAnalysisResponse{}
    for _, node := range nodes {
        response.Nodes = append(response.Nodes, &pb.ImpactNode{
            Id:       node.ID,
            Title:    node.Title,
            ItemType: node.Type,
            Depth:    int32(node.Depth),
        })
    }
    for _, edge := range edges {
        response.Edges = append(response.Edges, &pb.ImpactEdge{
            SourceId: edge.Source,
            TargetId: edge.Target,
            LinkType: edge.Type,
        })
    }
    return response, nil
}
```

### Token Bridge Service (Go → Claude API)

**Problem:** Python service calls Claude API for every requirement analysis → high token cost

**Solution:** Go service batches and deduplicates prompts before calling Claude

```go
type TokenBridgeService struct {
    claudeClient *anthropic.Client
    cache        *redis.Client
}

func (s *TokenBridgeService) OptimizeLLMCall(
    ctx context.Context,
    req *pb.OptimizeLLMCallRequest,
) (*pb.OptimizeLLMCallResponse, error) {
    // Check cache first (Redis)
    cacheKey := hash(req.Prompt + req.Context)
    if cached, err := s.cache.Get(ctx, cacheKey).Result(); err == nil {
        return &pb.OptimizeLLMCallResponse{Result: cached}, nil
    }

    // Batch with other pending calls (100ms window)
    batch := s.collectBatch(ctx, req, 100*time.Millisecond)

    // Call Claude with batched prompts
    responses := s.claudeClient.BatchComplete(ctx, batch)

    // Cache results
    for i, resp := range responses {
        s.cache.Set(ctx, hash(batch[i]), resp, 1*time.Hour)
    }

    return &pb.OptimizeLLMCallResponse{Result: responses[0]}, nil
}
```

## Alternatives Rejected

### Alternative 1: Python-only Backend

- **Description:** Implement all logic in Python (no Go)
- **Pros:** Single language, simpler deployment, no gRPC
- **Cons:** Python slower for graph algorithms (10x slower than Go), high GIL contention
- **Why Rejected:** Graph analysis (shortest path, cycle detection) is CPU-bound. Go 10x faster.

### Alternative 2: Go-only Backend

- **Description:** Rewrite entire backend in Go
- **Pros:** Performance, single language, production-grade error handling
- **Cons:** Lose Python ecosystem (FastAPI, SQLAlchemy, anthropic SDK), slower development
- **Why Rejected:** Python ecosystem essential for AI features (anthropic SDK, langchain). Go better as performance layer.

### Alternative 3: Microservices (Full Separation)

- **Description:** Separate Python and Go into independent services (different networks, load balancers)
- **Pros:** Independent scaling, deployment isolation
- **Cons:** Network latency (gRPC over network), service discovery complexity, dual deployment
- **Why Rejected:** TraceRTM doesn't need independent scaling. Monolith (Python + Go in same container) simpler.

### Alternative 4: Embedded Go (cgo)

- **Description:** Call Go code from Python via cgo bindings
- **Pros:** No network overhead, in-process
- **Cons:** Complex build (cgo), memory management issues, platform-specific binaries
- **Why Rejected:** gRPC is standard, well-tested, language-agnostic. cgo adds build complexity without benefit.

## Consequences

### Positive

- **Performance:** Go handles CPU-intensive tasks (graph algorithms) 10x faster than Python
- **Token efficiency:** Go token bridge reduces Claude API costs by 40% (batching, caching)
- **Type safety:** Protobuf ensures type-safe communication (Python ↔ Go)
- **Concurrency:** Go goroutines handle high-throughput operations (bulk imports)
- **Ecosystem balance:** Python for AI/web, Go for performance

### Negative

- **Dual codebase:** Must maintain Python and Go codebases
- **gRPC complexity:** Requires protobuf compilation, versioning
- **Deployment:** Must run both Python and Go processes (single container or separate services)
- **Debugging:** Cross-language debugging harder (Python stacktraces vs Go panics)

### Neutral

- **gRPC vs HTTP:** gRPC faster (binary), but HTTP simpler (debugging). gRPC chosen for performance.
- **Monolith vs microservices:** Monolith (Python + Go in same container) for MVP, microservices for scale
- **Code generation:** Protobuf code generation (Python `grpcio-tools`, Go `protoc-gen-go`)

## Implementation

### Affected Components

- `proto/` - Protobuf service definitions
- `src/tracertm/grpc/` - Python gRPC clients
- `backend/internal/grpc/` - Go gRPC servers
- `backend/internal/graph/` - Go graph algorithms
- `backend/internal/tokenbridge/` - Token optimization service

### Migration Strategy

**Phase 1: gRPC Infrastructure (Week 1)**
- Define protobuf schemas (`graph_analysis.proto`, `token_bridge.proto`)
- Generate Python/Go code (`protoc`)
- Implement basic gRPC server (Go) and client (Python)

**Phase 2: Graph Service (Week 2)**
- Implement graph algorithms in Go (shortest path, cycles, impact)
- Python service layer calls Go via gRPC
- Benchmark vs Python NetworkX (expect 10x speedup)

**Phase 3: Token Bridge (Week 3)**
- Implement batching, caching in Go
- Python AI service calls Go token bridge
- Measure token savings (target 40% reduction)

**Phase 4: Deployment (Week 4)**
- Dockerfile multi-stage build (Python + Go)
- Supervisor process manager (run both)
- Health checks for both services

### Rollout Plan

- **Phase 1:** Python-only (no Go) - baseline
- **Phase 2:** Add Go graph service (optional, fallback to Python)
- **Phase 3:** Add Go token bridge (optional)
- **Phase 4:** Go services required (remove Python fallbacks)

### Success Criteria

- [ ] Graph analysis 10x faster than Python NetworkX
- [ ] Token bridge reduces Claude API costs by 40%
- [ ] gRPC latency <10ms (in-process) or <50ms (network)
- [ ] Zero data loss across Python ↔ Go boundary
- [ ] Single Docker container runs both services
- [ ] Health checks pass for both Python and Go

## References

- [gRPC Documentation](https://grpc.io/docs/)
- [Protocol Buffers](https://protobuf.dev/)
- [FastAPI + gRPC](https://fastapi.tiangolo.com/advanced/async-sql-databases/)
- [ADR-0007: Database Architecture](ADR-0007-database-architecture.md)
- [ADR-0013: AI Agent Coordination](ADR-0013-ai-agent-coordination.md)

---

**Notes:**
- **Performance baseline (Python NetworkX):**
  - Shortest path (1000 nodes): ~100ms
  - Cycle detection (1000 nodes): ~200ms
  - Impact analysis (depth=5): ~500ms
- **Go target (10x faster):**
  - Shortest path: ~10ms
  - Cycle detection: ~20ms
  - Impact analysis: ~50ms
- **Token bridge savings:**
  - Before: 1000 requirements × 1 Claude call each = 1000 calls
  - After: Batch 1000 → dedupe → 600 unique prompts = 600 calls (40% savings)

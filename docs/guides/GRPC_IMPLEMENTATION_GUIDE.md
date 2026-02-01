# gRPC Inter-Service Communication Implementation Guide

**Version:** 1.0.0
**Date:** January 31, 2026
**Phase:** Phase 4 - Unified Infrastructure Architecture

---

## Overview

This guide covers the implementation of gRPC inter-service communication in TraceRTM, enabling high-performance RPC between Go and Python backends.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  TraceRTM gRPC Architecture                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Python Backend (Port 8000)          Go Backend (Port 8080)│
│      │                                        │             │
│      │                                        │             │
│      │ ◄─── gRPC GraphService ───── Go gRPC Server         │
│      │        (Port 9090)                     │             │
│      │                                        │             │
│      │ - Impact Analysis                      │             │
│      │ - Cycle Detection                      │             │
│      │ - Path Calculation                     │             │
│      │ - Graph Streaming                      │             │
│      │                                        │             │
│      Python gRPC Client ────► AnalyzeImpact() │             │
│                          ────► FindCycles()   │             │
│                          ────► CalculatePath()│             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Services

#### GraphService (Go → Python)
**Provided by:** Go backend
**Consumed by:** Python services
**Port:** 9090

Operations:
- `AnalyzeImpact`: Impact analysis for graph changes
- `FindCycles`: Circular dependency detection
- `CalculatePath`: Shortest path calculation
- `StreamGraphUpdates`: Real-time graph updates

#### AIService (Python → Go)
**Provided by:** Python backend
**Consumed by:** Go services
**Status:** Planned for future implementation

---

## Prerequisites

### 1. Protocol Buffers Compiler

```bash
# macOS
brew install protobuf

# Verify installation
protoc --version
# Expected: libprotoc 33.4 or later
```

### 2. Go gRPC Plugins

```bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Verify installation
which protoc-gen-go protoc-gen-go-grpc
```

### 3. Python gRPC Tools

```bash
pip install grpcio grpcio-tools

# Verify installation
python -c "import grpc; print(grpc.__version__)"
# Expected: 1.76.0 or later
```

---

## Quick Start

### 1. Environment Configuration

Add to your `.env` file:

```bash
# gRPC Configuration
GRPC_PORT=9090
GRPC_GO_BACKEND_HOST=localhost:9090
```

### 2. Generate gRPC Code

From the project root:

```bash
# Generate Go code
protoc --go_out=backend/pkg/proto \
  --go_opt=paths=source_relative \
  --go-grpc_out=backend/pkg/proto \
  --go-grpc_opt=paths=source_relative \
  proto/tracertm.proto

# Generate Python code
python -m grpc_tools.protoc -I. \
  --python_out=src/tracertm/proto \
  --grpc_python_out=src/tracertm/proto \
  proto/tracertm.proto
```

### 3. Start the Go Backend

```bash
cd backend
go run main.go
```

Expected output:
```
🚀 TraceRTM HTTP API starting on :8080
🚀 gRPC server listening on port 9090
```

### 4. Use the Python Client

```python
from tracertm.services.grpc_client import GoBackendClient

async def example():
    async with GoBackendClient() as client:
        # Analyze impact
        result = await client.analyze_impact(
            item_id="item-123",
            project_id="proj-456",
            direction="upstream",
            max_depth=3
        )

        print(f"Found {result['total_count']} impacted items")
        for item in result['impacted_items']:
            print(f"  - {item['title']} (depth: {item['depth']})")

# Run with asyncio
import asyncio
asyncio.run(example())
```

---

## Protocol Buffers Schema

The gRPC services are defined in `proto/tracertm.proto`.

### Key Message Types

#### ImpactRequest
```protobuf
message ImpactRequest {
  string item_id = 1;
  string project_id = 2;
  string direction = 3;        // "upstream", "downstream", "both"
  int32 max_depth = 4;          // 0 = unlimited
  repeated string link_types = 5;
}
```

#### ImpactResponse
```protobuf
message ImpactResponse {
  string item_id = 1;
  repeated ImpactedItem impacted_items = 2;
  int32 total_count = 3;
  map<string, int32> items_by_type = 4;
  map<string, int32> items_by_depth = 5;
  repeated string critical_paths = 6;
}
```

### Service Definition

```protobuf
service GraphService {
  rpc AnalyzeImpact(ImpactRequest) returns (ImpactResponse);
  rpc FindCycles(CycleRequest) returns (CycleResponse);
  rpc CalculatePath(PathRequest) returns (PathResponse);
  rpc StreamGraphUpdates(GraphStreamRequest) returns (stream GraphUpdate);
}
```

---

## Go Implementation

### Server Implementation

Location: `backend/internal/grpc/server.go`

Key components:

1. **GraphServiceServer struct**
```go
type GraphServiceServer struct {
    pb.UnimplementedGraphServiceServer
    itemRepo *repository.ItemRepository
    linkRepo *repository.LinkRepository
    graphSvc *graph.Service
}
```

2. **AnalyzeImpact method**
```go
func (s *GraphServiceServer) AnalyzeImpact(
    ctx context.Context,
    req *pb.ImpactRequest,
) (*pb.ImpactResponse, error) {
    // Validation
    // Graph traversal with BFS
    // Response construction
}
```

3. **Server initialization**
```go
grpcSrv, err := grpcserver.NewServer(
    9090,
    infra.ItemRepository,
    infra.LinkRepository,
    infra.GraphService,
)
```

### Integration with main.go

The gRPC server runs alongside the HTTP server:

```go
// Start HTTP server
go func() {
    log.Printf("🚀 TraceRTM HTTP API starting on %s", addr)
    if err := srv.Start(addr); err != nil {
        log.Fatalf("HTTP server error: %v", err)
    }
}()

// Start gRPC server
go func() {
    if err := grpcSrv.Start(); err != nil {
        log.Fatalf("gRPC server error: %v", err)
    }
}()
```

---

## Python Implementation

### Client Implementation

Location: `src/tracertm/services/grpc_client.py`

Key components:

1. **GoBackendClient class**
```python
class GoBackendClient:
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        max_retries: int = 3,
        timeout: int = 30,
    ):
        # Initialize connection settings
        # Set up retry logic
```

2. **Connection management**
```python
async def connect(self):
    self._channel = aio.insecure_channel(
        self.address,
        options=[
            ("grpc.keepalive_time_ms", 30000),
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),
        ]
    )
    self._stub = tracertm_pb2_grpc.GraphServiceStub(self._channel)
```

3. **Async context manager**
```python
async with GoBackendClient() as client:
    result = await client.analyze_impact(...)
```

### Error Handling

The client includes comprehensive error handling:

```python
async with self._retry_context("analyze_impact"):
    response = await self._stub.AnalyzeImpact(
        request,
        timeout=self.timeout,
    )
```

Retry logic:
- Retries on `UNAVAILABLE`, `DEADLINE_EXCEEDED`, `RESOURCE_EXHAUSTED`
- Exponential backoff: 1s, 2s, 4s
- Maximum 3 attempts by default

---

## Testing

### Manual Testing

#### 1. Test gRPC Server

```bash
# Install grpcurl
brew install grpcurl

# List services
grpcurl -plaintext localhost:9090 list

# List methods
grpcurl -plaintext localhost:9090 list tracertm.GraphService

# Call AnalyzeImpact
grpcurl -plaintext -d '{
  "item_id": "item-123",
  "project_id": "proj-456",
  "direction": "both",
  "max_depth": 2
}' localhost:9090 tracertm.GraphService/AnalyzeImpact
```

#### 2. Test Python Client

Create a test script `test_grpc_client.py`:

```python
import asyncio
from tracertm.services.grpc_client import GoBackendClient

async def test_impact_analysis():
    async with GoBackendClient() as client:
        try:
            result = await client.analyze_impact(
                item_id="item-test-123",
                project_id="proj-test-456",
                direction="both",
                max_depth=2
            )
            print(f"Success! Found {result['total_count']} impacted items")
            print(f"Items by type: {result['items_by_type']}")
            print(f"Critical paths: {result['critical_paths']}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_impact_analysis())
```

Run the test:
```bash
python test_grpc_client.py
```

### Integration Testing

Create integration tests in `backend/internal/grpc/server_test.go`:

```go
func TestAnalyzeImpact(t *testing.T) {
    // Set up test database
    // Create test items and links
    // Call AnalyzeImpact
    // Verify response
}
```

Run tests:
```bash
cd backend
go test ./internal/grpc/...
```

---

## Performance Tuning

### Connection Pooling

The Python client uses connection pooling by default:

```python
self._channel = aio.insecure_channel(
    self.address,
    options=[
        ("grpc.keepalive_time_ms", 30000),
        ("grpc.keepalive_timeout_ms", 10000),
        ("grpc.keepalive_permit_without_calls", True),
    ]
)
```

### Message Size Limits

Increase for large responses:

**Go:**
```go
grpcServer := grpc.NewServer(
    grpc.MaxRecvMsgSize(10 * 1024 * 1024), // 10MB
    grpc.MaxSendMsgSize(10 * 1024 * 1024),
)
```

**Python:**
```python
options=[
    ("grpc.max_receive_message_length", 10 * 1024 * 1024),
    ("grpc.max_send_message_length", 10 * 1024 * 1024),
]
```

### Timeout Configuration

Adjust timeouts based on operation complexity:

```python
client = GoBackendClient(timeout=60)  # 60 seconds
```

---

## Monitoring & Debugging

### Logging

**Go server logs:**
```
[gRPC] Analyzing impact for item item-123 in project proj-456 (direction: both, max_depth: 2)
[gRPC] Impact analysis complete: 15 impacted items
```

**Python client logs:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Shows detailed gRPC communication
```

### Health Checks

The gRPC server includes a health check service:

```bash
grpcurl -plaintext localhost:9090 grpc.health.v1.Health/Check
```

Expected response:
```json
{
  "status": "SERVING"
}
```

### Common Issues

#### 1. Connection Refused
```
Error: failed to connect to all addresses
```

**Solution:**
- Verify Go backend is running
- Check `GRPC_PORT` in `.env`
- Ensure no firewall blocking port 9090

#### 2. Import Errors (Python)
```
ModuleNotFoundError: No module named 'tracertm_pb2'
```

**Solution:**
```bash
# Regenerate Python protobuf code
python -m grpc_tools.protoc -I. \
  --python_out=src/tracertm/proto \
  --grpc_python_out=src/tracertm/proto \
  proto/tracertm.proto
```

#### 3. Method Not Found
```
Code: UNIMPLEMENTED
Message: method StreamGraphUpdates not implemented
```

**Solution:** This method is planned but not yet implemented. Use only implemented methods.

---

## Best Practices

### 1. Use Context Managers

Always use async context managers for automatic cleanup:

```python
async with GoBackendClient() as client:
    result = await client.analyze_impact(...)
```

### 2. Handle Errors Gracefully

```python
try:
    result = await client.analyze_impact(...)
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.NOT_FOUND:
        logger.error(f"Item not found: {item_id}")
    else:
        logger.error(f"gRPC error: {e.details()}")
```

### 3. Reuse Connections

For multiple requests, reuse the client:

```python
async with GoBackendClient() as client:
    for item_id in item_ids:
        result = await client.analyze_impact(item_id=item_id, ...)
```

### 4. Set Appropriate Timeouts

```python
# Quick operations
client = GoBackendClient(timeout=10)

# Complex graph analysis
client = GoBackendClient(timeout=60)
```

---

## Future Enhancements

### Phase 5: AIService Implementation

Implement the Python AIService for Go consumption:

```python
# src/tracertm/services/grpc_server.py
class AIServiceServicer(tracertm_pb2_grpc.AIServiceServicer):
    async def AnalyzeRequirement(self, request, context):
        # NLP analysis implementation
        pass
```

### TLS/mTLS Security

Add secure communication:

**Go:**
```go
creds, _ := credentials.NewServerTLSFromFile("server.crt", "server.key")
grpcServer := grpc.NewServer(grpc.Creds(creds))
```

**Python:**
```python
with open('client.crt', 'rb') as f:
    creds = grpc.ssl_channel_credentials(f.read())
channel = aio.secure_channel('localhost:9090', creds)
```

### Metrics & Observability

Integrate Prometheus metrics:

```go
import grpc_prometheus "github.com/grpc-ecosystem/go-grpc-prometheus"

grpcServer := grpc.NewServer(
    grpc.UnaryInterceptor(grpc_prometheus.UnaryServerInterceptor),
)
```

---

## References

- [Protocol Buffers Documentation](https://protobuf.dev/)
- [gRPC Go Tutorial](https://grpc.io/docs/languages/go/basics/)
- [gRPC Python Tutorial](https://grpc.io/docs/languages/python/basics/)
- [Backend Communication Protocols Research](../research/BACKEND_COMMUNICATION_PROTOCOLS.md)

---

**Status:** Production Ready
**Next Steps:** Monitor performance and implement AIService (Phase 5)

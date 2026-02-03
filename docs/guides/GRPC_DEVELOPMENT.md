# gRPC Development Guide

Complete guide for developing and testing gRPC services in TraceRTM.

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Adding New Services](#adding-new-services)
- [Modifying Existing Services](#modifying-existing-services)
- [Code Generation](#code-generation)
- [Testing gRPC Services](#testing-grpc-services)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Quick Start

### Prerequisites

```bash
# Install protoc compiler
brew install protobuf

# Install Go plugins
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Install Python tools
pip install grpcio-tools

# Optional: Install buf for better proto management
brew install bufbuild/buf/buf

# Optional: Install fswatch for auto-regeneration
brew install fswatch
```

### Generate gRPC Code

```bash
# Generate all gRPC code (Go + Python)
make proto-gen

# Or use the script directly
./scripts/generate-grpc.sh

# Generate with TypeScript support
make proto-gen-ts

# Watch mode (auto-regenerate on changes)
make proto-watch
```

### Test gRPC Services

```bash
# Run gRPC integration tests
make proto-test

# Or use the test script directly
python scripts/python/test_grpc.py
```

---

## Architecture

TraceRTM uses gRPC for inter-service communication:

```
┌─────────────────┐         gRPC          ┌─────────────────┐
│   Python API    │ ◄──────────────────► │    Go Backend   │
│   (FastAPI)     │                       │   (GraphService)│
├─────────────────┤                       ├─────────────────┤
│  AI Services    │                       │ Graph Analysis  │
│  - NLP Analysis │                       │ - Impact        │
│  - Equivalence  │                       │ - Cycles        │
│  - Suggestions  │                       │ - Paths         │
└─────────────────┘                       └─────────────────┘
```

### Service Definitions

**Location:** `proto/tracertm.proto`

**Services:**

1. **GraphService** (Go → consumed by Python)
   - Impact analysis
   - Cycle detection
   - Path calculation
   - Graph streaming

2. **AIService** (Python → consumed by Go)
   - Requirement analysis
   - Suggestions (streaming)
   - Equivalence detection
   - Entity extraction

---

## Adding New Services

### Step 1: Define Service in Proto

Edit `proto/tracertm.proto`:

```protobuf
service MyNewService {
  // Unary RPC
  rpc DoSomething(MyRequest) returns (MyResponse);

  // Server streaming RPC
  rpc StreamResults(StreamRequest) returns (stream StreamItem);

  // Client streaming RPC
  rpc UploadData(stream DataChunk) returns (UploadResponse);

  // Bidirectional streaming RPC
  rpc Chat(stream Message) returns (stream Message);
}

message MyRequest {
  string id = 1;
  string data = 2;
}

message MyResponse {
  bool success = 1;
  string result = 2;
}
```

### Step 2: Generate Code

```bash
make proto-gen
```

This generates:
- Go: `backend/pkg/proto/tracertm.pb.go` and `tracertm_grpc.pb.go`
- Python: `src/tracertm/proto/tracertm_pb2.py` and `tracertm_pb2_grpc.py`

### Step 3: Implement Server (Go Example)

Create `backend/internal/grpc/mynew_service.go`:

```go
package grpc

import (
    "context"

    pb "github.com/kooshapari/tracertm-backend/pkg/proto"
)

type MyNewService struct {
    pb.UnimplementedMyNewServiceServer
}

func NewMyNewService() *MyNewService {
    return &MyNewService{}
}

func (s *MyNewService) DoSomething(
    ctx context.Context,
    req *pb.MyRequest,
) (*pb.MyResponse, error) {
    // Validate request
    if req.Id == "" {
        return nil, status.Error(codes.InvalidArgument, "id is required")
    }

    // Process request
    result := processData(req.Data)

    // Return response
    return &pb.MyResponse{
        Success: true,
        Result:  result,
    }, nil
}

func (s *MyNewService) StreamResults(
    req *pb.StreamRequest,
    stream pb.MyNewService_StreamResultsServer,
) error {
    // Generate results
    for i := 0; i < 10; i++ {
        item := &pb.StreamItem{
            Id:   fmt.Sprintf("item-%d", i),
            Data: fmt.Sprintf("data-%d", i),
        }

        if err := stream.Send(item); err != nil {
            return err
        }
    }

    return nil
}
```

### Step 4: Register Service

Update `backend/internal/grpc/server.go`:

```go
func NewServer() *grpc.Server {
    server := grpc.NewServer()

    // Register existing services
    pb.RegisterGraphServiceServer(server, NewGraphService())

    // Register new service
    pb.RegisterMyNewServiceServer(server, NewMyNewService())

    return server
}
```

### Step 5: Implement Client (Python Example)

Create or update `src/tracertm/services/grpc_client.py`:

```python
from tracertm.proto import tracertm_pb2, tracertm_pb2_grpc

class GoBackendClient:
    async def do_something(self, id: str, data: str) -> dict:
        """Call MyNewService.DoSomething"""
        request = tracertm_pb2.MyRequest(
            id=id,
            data=data,
        )

        response = await self.mynew_stub.DoSomething(request)

        return {
            "success": response.success,
            "result": response.result,
        }

    async def stream_results(self, stream_id: str) -> list[dict]:
        """Call MyNewService.StreamResults (streaming)"""
        request = tracertm_pb2.StreamRequest(id=stream_id)

        results = []
        async for item in self.mynew_stub.StreamResults(request):
            results.append({
                "id": item.id,
                "data": item.data,
            })

        return results
```

### Step 6: Write Tests

See [Testing gRPC Services](#testing-grpc-services) below.

---

## Modifying Existing Services

### Step 1: Update Proto Definition

Edit `proto/tracertm.proto` to add fields or modify messages:

```protobuf
message ImpactRequest {
  string item_id = 1;
  string project_id = 2;
  string direction = 3;
  int32 max_depth = 4;
  repeated string link_types = 5;

  // NEW: Add filtering options
  bool include_archived = 6;  // New field
  int64 timestamp_cutoff = 7;  // New field
}
```

**Important:** Follow protobuf compatibility rules:
- Never change field numbers
- Never change field types
- Add new fields with new numbers
- Mark removed fields as `reserved`

### Step 2: Check for Breaking Changes (Optional)

```bash
make proto-breaking
```

### Step 3: Regenerate Code

```bash
make proto-gen
```

### Step 4: Update Implementation

Update server implementation to use new fields:

```go
func (s *GraphService) AnalyzeImpact(
    ctx context.Context,
    req *pb.ImpactRequest,
) (*pb.ImpactResponse, error) {
    // Use new fields with backward compatibility
    includeArchived := req.IncludeArchived  // Defaults to false
    timestampCutoff := req.TimestampCutoff  // Defaults to 0

    // ... rest of implementation
}
```

Update client to use new fields:

```python
async def analyze_impact(
    self,
    item_id: str,
    project_id: str,
    include_archived: bool = False,
    timestamp_cutoff: int = 0,
) -> dict:
    request = tracertm_pb2.ImpactRequest(
        item_id=item_id,
        project_id=project_id,
        include_archived=include_archived,
        timestamp_cutoff=timestamp_cutoff,
    )

    response = await self.graph_stub.AnalyzeImpact(request)
    return self._parse_impact_response(response)
```

### Step 5: Update Tests

Update tests to verify new functionality.

---

## Code Generation

### Using Make (Recommended)

```bash
# Generate all code
make proto-gen

# Generate with TypeScript
make proto-gen-ts

# Watch mode (auto-regenerate)
make proto-watch

# Lint proto files
make proto-lint

# Check breaking changes
make proto-breaking
```

### Using Script Directly

```bash
# Basic generation
./scripts/generate-grpc.sh

# With TypeScript
./scripts/generate-grpc.sh --typescript

# Watch mode
./scripts/generate-grpc.sh --watch

# Help
./scripts/generate-grpc.sh --help
```

### Using Buf (Optional)

```bash
# Install buf
brew install bufbuild/buf/buf

# Generate code
buf generate

# Lint proto files
buf lint

# Check breaking changes
buf breaking --against '.git#branch=main'
```

### Generated Files

After running code generation:

**Go (Server):**
- `backend/pkg/proto/tracertm.pb.go` - Protocol buffer messages
- `backend/pkg/proto/tracertm_grpc.pb.go` - gRPC service stubs

**Python (Client):**
- `src/tracertm/proto/tracertm_pb2.py` - Protocol buffer messages
- `src/tracertm/proto/tracertm_pb2_grpc.py` - gRPC service stubs

**TypeScript (Optional):**
- `frontend/apps/web/src/api/grpc/tracertm_pb.js`
- `frontend/apps/web/src/api/grpc/tracertm_grpc_web_pb.js`

---

## Testing gRPC Services

### Python Testing

#### Using Test Helpers

```python
import pytest
from tests.grpc.test_helpers import (
    GRPCTestLogger,
    grpc_test_channel,
    wait_for_server,
    assert_grpc_error,
)
from tracertm.proto import tracertm_pb2, tracertm_pb2_grpc

@pytest.mark.asyncio
async def test_analyze_impact():
    # Wait for server
    assert await wait_for_server("localhost", 50051, timeout=5.0)

    # Create client
    async with grpc_test_channel("localhost", 50051) as channel:
        logger = GRPCTestLogger("GraphService", verbose=True)
        stub = tracertm_pb2_grpc.GraphServiceStub(channel)

        # Make request
        request = tracertm_pb2.ImpactRequest(
            item_id="test-123",
            project_id="proj-456",
            direction="both",
            max_depth=2,
        )

        logger.log_request("AnalyzeImpact", request)
        response = await stub.AnalyzeImpact(request)
        logger.log_response("AnalyzeImpact", response, 0.5)

        # Verify
        assert response.total_count > 0

        # Check stats
        stats = logger.get_stats()
        assert stats["successful"] == 1

@pytest.mark.asyncio
async def test_error_handling():
    async with grpc_test_channel() as channel:
        stub = tracertm_pb2_grpc.GraphServiceStub(channel)

        # Invalid request
        try:
            request = tracertm_pb2.ImpactRequest(item_id="")
            await stub.AnalyzeImpact(request)
            pytest.fail("Should have raised error")
        except grpc.RpcError as e:
            assert_grpc_error(
                e,
                grpc.StatusCode.INVALID_ARGUMENT,
                "item_id is required"
            )
```

#### Manual Testing Script

```bash
# Run test script
python scripts/python/test_grpc.py

# Or use pytest
pytest tests/grpc/ -v
```

### Go Testing

#### Using Test Helpers

```go
package grpc_test

import (
    "context"
    "testing"

    pb "github.com/kooshapari/tracertm-backend/pkg/proto"
    grpctest "github.com/kooshapari/tracertm-backend/internal/grpc/testing"
)

func TestGraphService_AnalyzeImpact(t *testing.T) {
    // Create test server
    ts := grpctest.NewTestServer(t)
    defer ts.Stop()

    // Register service
    service := NewGraphService()
    pb.RegisterGraphServiceServer(ts.Server, service)
    ts.Start()

    // Create client
    ctx := context.Background()
    conn, err := ts.NewClient(ctx)
    if err != nil {
        t.Fatalf("Failed to create client: %v", err)
    }
    defer conn.Close()

    client := pb.NewGraphServiceClient(conn)
    logger := grpctest.NewRequestLogger("GraphService", true)

    // Make request
    req := &pb.ImpactRequest{
        ItemId:    "test-123",
        ProjectId: "proj-456",
        Direction: "both",
        MaxDepth:  2,
    }

    logger.LogRequest("AnalyzeImpact", req)
    resp, err := client.AnalyzeImpact(ctx, req)
    if err != nil {
        t.Fatalf("AnalyzeImpact failed: %v", err)
    }
    logger.LogResponse("AnalyzeImpact", resp, 0)

    // Verify
    if resp.TotalCount == 0 {
        t.Error("Expected non-zero impact count")
    }
}

func TestGraphService_ErrorHandling(t *testing.T) {
    ts := grpctest.NewTestServer(t)
    defer ts.Stop()

    service := NewGraphService()
    pb.RegisterGraphServiceServer(ts.Server, service)
    ts.Start()

    ctx := context.Background()
    conn, err := ts.NewClient(ctx)
    if err != nil {
        t.Fatalf("Failed to create client: %v", err)
    }
    defer conn.Close()

    client := pb.NewGraphServiceClient(conn)

    // Invalid request
    req := &pb.ImpactRequest{ItemId: ""}
    _, err = client.AnalyzeImpact(ctx, req)

    grpctest.AssertGRPCError(t, err, codes.InvalidArgument, "item_id")
}
```

---

## Troubleshooting

### Code Generation Issues

#### Problem: `protoc: command not found`

```bash
# Install protobuf compiler
brew install protobuf

# Verify installation
protoc --version
```

#### Problem: Go plugins not found

```bash
# Install Go plugins
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Add to PATH if needed
export PATH="$PATH:$(go env GOPATH)/bin"
```

#### Problem: Python grpcio-tools not found

```bash
# Install Python tools
pip install grpcio-tools

# Or with uv
uv pip install grpcio-tools
```

#### Problem: Import path errors in generated Go code

Check `proto/tracertm.proto`:
```protobuf
option go_package = "github.com/kooshapari/tracertm-backend/pkg/proto";
```

Regenerate:
```bash
make proto-gen
```

### Runtime Issues

#### Problem: Connection refused

```bash
# Check if gRPC server is running
lsof -i :50051

# Start Go backend
cd backend && air -c .air.toml

# Or with overmind
overmind start -f Procfile
```

#### Problem: Method not implemented

Server must implement all RPC methods or embed `Unimplemented*Server`:

```go
type MyService struct {
    pb.UnimplementedMyServiceServer  // Provides default implementations
}
```

#### Problem: Python import errors

Regenerate with proper __init__.py:
```bash
make proto-gen
```

Check that `src/tracertm/proto/__init__.py` exists.

### Performance Issues

#### Problem: High latency

1. Enable keepalive:
```go
grpc.NewServer(
    grpc.KeepaliveParams(keepalive.ServerParameters{
        Time:    30 * time.Second,
        Timeout: 10 * time.Second,
    }),
)
```

2. Use connection pooling (Python):
```python
# Reuse channel instead of creating new ones
self.channel = grpc.aio.insecure_channel(target)
```

#### Problem: Large message errors

Increase message size limits:
```go
grpc.NewServer(
    grpc.MaxRecvMsgSize(10 * 1024 * 1024),  // 10MB
    grpc.MaxSendMsgSize(10 * 1024 * 1024),
)
```

---

## Best Practices

### Proto Design

1. **Use meaningful names**
   ```protobuf
   // Good
   message ImpactAnalysisRequest { ... }

   // Bad
   message IAReq { ... }
   ```

2. **Add comments**
   ```protobuf
   // Analyzes the impact of changes to an item
   rpc AnalyzeImpact(ImpactRequest) returns (ImpactResponse);
   ```

3. **Plan for evolution**
   ```protobuf
   message Request {
     string id = 1;

     // Reserve field numbers for future use
     reserved 10 to 15;

     // Mark deprecated fields
     string old_field = 2 [deprecated = true];
   }
   ```

4. **Use enums for constants**
   ```protobuf
   enum Direction {
     DIRECTION_UNSPECIFIED = 0;
     UPSTREAM = 1;
     DOWNSTREAM = 2;
     BOTH = 3;
   }
   ```

### Error Handling

1. **Use standard gRPC status codes**
   ```go
   if req.ItemId == "" {
       return nil, status.Error(codes.InvalidArgument, "item_id is required")
   }
   ```

2. **Provide descriptive error messages**
   ```go
   return nil, status.Errorf(
       codes.NotFound,
       "item %s not found in project %s",
       req.ItemId,
       req.ProjectId,
   )
   ```

3. **Use error details for structured errors**
   ```go
   st := status.New(codes.InvalidArgument, "validation failed")
   st, _ = st.WithDetails(&pb.ValidationError{
       Field: "item_id",
       Message: "must not be empty",
   })
   return nil, st.Err()
   ```

### Testing

1. **Test error cases**
   ```python
   try:
       await client.call_method(invalid_request)
       pytest.fail("Should have raised error")
   except grpc.RpcError as e:
       assert_grpc_error(e, grpc.StatusCode.INVALID_ARGUMENT)
   ```

2. **Use test helpers**
   - Python: `tests/grpc/test_helpers.py`
   - Go: `backend/internal/grpc/testing/helpers.go`

3. **Mock external dependencies**
   ```go
   type MockRepository struct {
       Items map[string]*Item
   }

   func (m *MockRepository) GetItem(id string) (*Item, error) {
       if item, ok := m.Items[id]; ok {
           return item, nil
       }
       return nil, fmt.Errorf("not found")
   }
   ```

### Development Workflow

1. **Use watch mode during development**
   ```bash
   make proto-watch
   ```

2. **Lint proto files before committing**
   ```bash
   make proto-lint
   ```

3. **Check for breaking changes**
   ```bash
   make proto-breaking
   ```

4. **Run tests before pushing**
   ```bash
   make proto-test
   make test
   ```

---

## Additional Resources

- [gRPC Official Documentation](https://grpc.io/docs/)
- [Protocol Buffers Guide](https://developers.google.com/protocol-buffers)
- [Buf Documentation](https://docs.buf.build/)
- [gRPC Go Tutorial](https://grpc.io/docs/languages/go/quickstart/)
- [gRPC Python Tutorial](https://grpc.io/docs/languages/python/quickstart/)

---

**Need help?** See [Troubleshooting](#troubleshooting) or check existing tests in:
- `tests/grpc/`
- `backend/internal/grpc/*_test.go`

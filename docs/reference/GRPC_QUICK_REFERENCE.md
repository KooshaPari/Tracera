# gRPC Quick Reference

Fast reference for common gRPC development tasks in TraceRTM.

## Table of Contents

- [Commands](#commands)
- [Code Generation](#code-generation)
- [Common Patterns](#common-patterns)
- [Error Codes](#error-codes)
- [Testing](#testing)

---

## Commands

### Code Generation

```bash
# Generate gRPC code (Go + Python)
make proto-gen

# Generate with TypeScript
make proto-gen-ts

# Watch proto files (auto-regenerate)
make proto-watch

# Using script directly
./scripts/generate-grpc.sh
./scripts/generate-grpc.sh --typescript
./scripts/generate-grpc.sh --watch
```

### Testing

```bash
# Run gRPC integration tests
make proto-test

# Test Go services
cd backend && go test ./internal/grpc/... -v

# Test Python services
pytest tests/grpc/ -v
```

### Linting & Quality

```bash
# Lint proto files (requires buf)
make proto-lint

# Check for breaking changes
make proto-breaking

# Format proto files (requires clang-format)
find proto -name "*.proto" -exec clang-format -i {} \;
```

---

## Code Generation

### Output Locations

| Language   | Location                                    | Purpose       |
|------------|---------------------------------------------|---------------|
| Go         | `backend/pkg/proto/*.pb.go`                 | Server stubs  |
| Go         | `backend/pkg/proto/*_grpc.pb.go`            | gRPC services |
| Python     | `src/tracertm/proto/*_pb2.py`               | Client stubs  |
| Python     | `src/tracertm/proto/*_pb2_grpc.py`          | gRPC services |
| TypeScript | `frontend/apps/web/src/api/grpc/*.js`       | Web client    |

### Prerequisites

```bash
# macOS
brew install protobuf
brew install fswatch  # optional, for watch mode
brew install bufbuild/buf/buf  # optional, for linting

# Go plugins
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Python tools
pip install grpcio-tools
```

---

## Common Patterns

### Server Implementation (Go)

```go
package grpc

import (
    "context"
    pb "github.com/kooshapari/tracertm-backend/pkg/proto"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
)

type GraphService struct {
    pb.UnimplementedGraphServiceServer
    repo Repository
}

func (s *GraphService) AnalyzeImpact(
    ctx context.Context,
    req *pb.ImpactRequest,
) (*pb.ImpactResponse, error) {
    // 1. Validate input
    if req.ItemId == "" {
        return nil, status.Error(codes.InvalidArgument, "item_id is required")
    }

    // 2. Call business logic
    result, err := s.repo.AnalyzeImpact(req.ItemId, req.ProjectId)
    if err != nil {
        return nil, status.Error(codes.Internal, err.Error())
    }

    // 3. Build response
    return &pb.ImpactResponse{
        ItemId:     req.ItemId,
        TotalCount: result.Count,
    }, nil
}
```

### Client Implementation (Python)

```python
from tracertm.proto import tracertm_pb2, tracertm_pb2_grpc
import grpc

class GoBackendClient:
    def __init__(self, host="localhost", port=50051):
        self.channel = grpc.aio.insecure_channel(f"{host}:{port}")
        self.graph_stub = tracertm_pb2_grpc.GraphServiceStub(self.channel)

    async def analyze_impact(
        self,
        item_id: str,
        project_id: str,
        direction: str = "both",
        max_depth: int = 5,
    ) -> dict:
        request = tracertm_pb2.ImpactRequest(
            item_id=item_id,
            project_id=project_id,
            direction=direction,
            max_depth=max_depth,
        )

        try:
            response = await self.graph_stub.AnalyzeImpact(request)
            return {
                "item_id": response.item_id,
                "total_count": response.total_count,
                "impacted_items": [
                    {
                        "id": item.id,
                        "type": item.type,
                        "title": item.title,
                        "depth": item.depth,
                    }
                    for item in response.impacted_items
                ],
            }
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.code()} - {e.details()}")

    async def close(self):
        await self.channel.close()
```

### Streaming Response (Go)

```go
func (s *GraphService) StreamGraphUpdates(
    req *pb.GraphStreamRequest,
    stream pb.GraphService_StreamGraphUpdatesServer,
) error {
    // Create subscription
    updates := make(chan *pb.GraphUpdate)

    // Send updates
    for update := range updates {
        if err := stream.Send(update); err != nil {
            return err
        }
    }

    return nil
}
```

### Streaming Response (Python Client)

```python
async def stream_graph_updates(self, project_id: str):
    request = tracertm_pb2.GraphStreamRequest(
        project_id=project_id,
        event_types=["item_created", "item_updated"],
    )

    async for update in self.graph_stub.StreamGraphUpdates(request):
        yield {
            "event_type": update.event_type,
            "item_id": update.item_id,
            "timestamp": update.timestamp,
        }
```

---

## Error Codes

### Standard gRPC Status Codes

| Code              | HTTP | When to Use                                    |
|-------------------|------|------------------------------------------------|
| OK                | 200  | Success                                        |
| INVALID_ARGUMENT  | 400  | Client specified invalid argument              |
| NOT_FOUND         | 404  | Resource not found                             |
| ALREADY_EXISTS    | 409  | Resource already exists                        |
| PERMISSION_DENIED | 403  | Permission denied                              |
| UNAUTHENTICATED   | 401  | Authentication failed                          |
| RESOURCE_EXHAUSTED| 429  | Rate limit exceeded                            |
| FAILED_PRECONDITION| 400 | Operation rejected due to system state         |
| INTERNAL          | 500  | Server error                                   |
| UNAVAILABLE       | 503  | Service unavailable                            |
| DEADLINE_EXCEEDED | 504  | Operation timeout                              |

### Go Error Creation

```go
import (
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
)

// Simple error
return nil, status.Error(codes.InvalidArgument, "item_id is required")

// Formatted error
return nil, status.Errorf(
    codes.NotFound,
    "item %s not found in project %s",
    itemId, projectId,
)

// Error with details
st := status.New(codes.InvalidArgument, "validation failed")
st, _ = st.WithDetails(&pb.ValidationError{
    Field: "item_id",
    Message: "must not be empty",
})
return nil, st.Err()
```

### Python Error Handling

```python
import grpc

try:
    response = await stub.Method(request)
except grpc.RpcError as e:
    code = e.code()
    details = e.details()

    if code == grpc.StatusCode.INVALID_ARGUMENT:
        # Handle validation error
        pass
    elif code == grpc.StatusCode.NOT_FOUND:
        # Handle not found
        pass
    else:
        # Handle other errors
        raise
```

---

## Testing

### Python Test Template

```python
import pytest
from tests.grpc.test_helpers import (
    grpc_test_channel,
    wait_for_server,
    GRPCTestLogger,
)
from tracertm.proto import tracertm_pb2_grpc

@pytest.mark.asyncio
async def test_service_method():
    # Wait for server
    assert await wait_for_server(timeout=5.0)

    # Create client
    async with grpc_test_channel() as channel:
        logger = GRPCTestLogger("GraphService")
        stub = tracertm_pb2_grpc.GraphServiceStub(channel)

        # Make request
        request = tracertm_pb2.ImpactRequest(
            item_id="test-123",
            project_id="proj-456",
        )

        response = await stub.AnalyzeImpact(request)

        # Verify
        assert response.total_count > 0
```

### Go Test Template

```go
package grpc_test

import (
    "context"
    "testing"

    pb "github.com/kooshapari/tracertm-backend/pkg/proto"
    grpctest "github.com/kooshapari/tracertm-backend/internal/grpc/testing"
)

func TestGraphService(t *testing.T) {
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
    require.NoError(t, err)
    defer conn.Close()

    client := pb.NewGraphServiceClient(conn)

    // Make request
    req := &pb.ImpactRequest{
        ItemId:    "test-123",
        ProjectId: "proj-456",
    }

    resp, err := client.AnalyzeImpact(ctx, req)
    require.NoError(t, err)
    assert.Greater(t, resp.TotalCount, int32(0))
}
```

### Test Utilities

**Python:**
```python
from tests.grpc.test_helpers import (
    GRPCTestLogger,          # Request/response logging
    GRPCTestClient,          # Base test client
    grpc_test_channel,       # Test channel context manager
    wait_for_server,         # Wait for server ready
    assert_grpc_error,       # Assert error details
    MockGRPCServicer,        # Mock server base class
)
```

**Go:**
```go
import grpctest "github.com/kooshapari/tracertm-backend/internal/grpc/testing"

grpctest.NewTestServer(t)              // Create test server
grpctest.NewRequestLogger("Service")   // Create logger
grpctest.AssertGRPCError(t, err, code) // Assert error
grpctest.WaitForServer(ctx, target)    // Wait for server
```

---

## Proto File Snippets

### Service Definition

```protobuf
service MyService {
  // Unary RPC
  rpc GetItem(GetItemRequest) returns (Item);

  // Server streaming
  rpc ListItems(ListItemsRequest) returns (stream Item);

  // Client streaming
  rpc CreateItems(stream CreateItemRequest) returns (CreateItemsResponse);

  // Bidirectional streaming
  rpc SyncItems(stream SyncRequest) returns (stream SyncResponse);
}
```

### Message Definition

```protobuf
message Item {
  string id = 1;
  string title = 2;
  ItemType type = 3;
  map<string, string> metadata = 4;
  repeated string tags = 5;

  // Nested message
  message Status {
    string state = 1;
    int64 timestamp = 2;
  }
  Status status = 6;
}

enum ItemType {
  ITEM_TYPE_UNSPECIFIED = 0;
  REQUIREMENT = 1;
  TASK = 2;
  TEST = 3;
}
```

### Field Types

| Proto Type | Go Type    | Python Type | Notes                    |
|------------|------------|-------------|--------------------------|
| double     | float64    | float       |                          |
| float      | float32    | float       |                          |
| int32      | int32      | int         |                          |
| int64      | int64      | int         |                          |
| uint32     | uint32     | int         |                          |
| uint64     | uint64     | int         |                          |
| bool       | bool       | bool        |                          |
| string     | string     | str         | UTF-8 or 7-bit ASCII     |
| bytes      | []byte     | bytes       | Arbitrary byte sequence  |
| repeated   | []T        | list[T]     | Array/list               |
| map        | map[K]V    | dict[K, V]  | Key-value pairs          |

---

## Watch Mode

Enable automatic regeneration when proto files change:

```bash
# In Procfile (uncomment)
proto_watch: bash scripts/generate-grpc.sh --watch

# Start with overmind
overmind start -f Procfile

# Or run directly
make proto-watch
```

---

## Quick Troubleshooting

| Problem                           | Solution                                        |
|-----------------------------------|-------------------------------------------------|
| `protoc: command not found`       | `brew install protobuf`                         |
| Go plugin not found               | `go install google.golang.org/protobuf/cmd/...` |
| Python import error               | Regenerate: `make proto-gen`                    |
| Connection refused                | Check server: `lsof -i :50051`                  |
| Method not implemented            | Add `Unimplemented*Server` to struct            |
| Large message error               | Increase limits with `MaxRecvMsgSize`           |
| Import path error (Go)            | Check `go_package` option in proto              |

---

## Files & Locations

| File/Directory                    | Purpose                                |
|-----------------------------------|----------------------------------------|
| `proto/tracertm/v1/tracertm.proto`            | Service definitions                    |
| `scripts/generate-grpc.sh`        | Code generation script                 |
| `scripts/python/test_grpc.py`     | gRPC integration test                  |
| `tests/grpc/test_helpers.py`      | Python test utilities                  |
| `backend/internal/grpc/testing/`  | Go test utilities                      |
| `buf.yaml`                        | Buf configuration (optional)           |
| `buf.gen.yaml`                    | Buf generation config (optional)       |
| `Makefile`                        | Make targets for gRPC                  |
| `Procfile`                        | Process configuration (watch mode)     |

---

## Additional Help

- Full guide: `docs/guides/GRPC_DEVELOPMENT.md`
- gRPC docs: https://grpc.io/docs/
- Proto docs: https://developers.google.com/protocol-buffers
- Buf docs: https://docs.buf.build/

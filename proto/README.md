# TraceRTM gRPC Protocol Definitions

This directory contains the Protocol Buffer definitions for TraceRTM's gRPC services.

**gRPC is internal-only:** The gRPC server (port 9091) is not exposed on the Caddy gateway. It is for server-to-server use (e.g. Go ↔ Python) only.

## Code generation (buf preferred)

From project root:

```bash
# Prefer buf (lint + managed mode)
buf generate

# Or use package script (tries buf, then protoc)
bun run generate:grpc
```

If `buf` is not installed: `brew install bufbuild/buf/buf`. Fallback: `./scripts/generate-grpc.sh` (uses `protoc`).

## Services

### GraphService (Go → Python)
Provided by the Go backend, consumed by Python services:
- `AnalyzeImpact`: Impact analysis for graph changes
- `FindCycles`: Circular dependency detection
- `CalculatePath`: Shortest path calculation
- `StreamGraphUpdates`: Real-time graph update streaming

### AIService (Python → Go)
Provided by the Python backend, consumed by Go services:
- `AnalyzeRequirement`: NLP analysis of requirements
- `GenerateSuggestions`: AI-powered suggestion generation
- `DetectEquivalences`: Semantic equivalence detection
- `ExtractEntities`: Named entity extraction

## Code Generation

### Generate Go Code

```bash
# From project root
protoc --go_out=backend/pkg/proto \
  --go_opt=paths=source_relative \
  --go-grpc_out=backend/pkg/proto \
  --go-grpc_opt=paths=source_relative \
  proto/tracertm/v1/tracertm.proto
```

**Output:**
- `backend/pkg/proto/tracertm.pb.go` - Message types
- `backend/pkg/proto/tracertm_grpc.pb.go` - Service interfaces

### Generate Python Code

```bash
# From project root
GRPC_TOOLS_PROTO_PATH="$(python - <<'PY'
import os
import grpc_tools
print(os.path.join(os.path.dirname(grpc_tools.__file__), "_proto"))
PY
)"

env -u PROTOC_INCLUDE python -m grpc_tools.protoc -Iproto -I"$GRPC_TOOLS_PROTO_PATH" \
  --python_out=src/tracertm/proto \
  --grpc_python_out=src/tracertm/proto \
  proto/tracertm/v1/tracertm.proto
```

**Output:**
- `src/tracertm/proto/tracertm_pb2.py` - Message types
- `src/tracertm/proto/tracertm_pb2_grpc.py` - Service stubs

## Prerequisites

### Go
```bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
```

### Python
```bash
pip install grpcio grpcio-tools
```

### Protocol Buffers Compiler
```bash
# macOS
brew install protobuf

# Linux (Ubuntu/Debian)
apt-get install -y protobuf-compiler

# Verify installation
protoc --version
```

## Regenerating Code

After modifying `tracertm.proto`:

```bash
# Prefer buf (from project root)
buf generate

# Or script (buf first, then protoc)
bun run generate:grpc
# Or: ./scripts/generate-grpc.sh
```

## Version

- Protocol Buffers: proto3
- gRPC: Latest stable
- Go package: `github.com/kooshapari/tracertm-backend/pkg/proto`

## References

- [Protocol Buffers Documentation](https://protobuf.dev/)
- [gRPC Go Tutorial](https://grpc.io/docs/languages/go/basics/)
- [gRPC Python Tutorial](https://grpc.io/docs/languages/python/basics/)

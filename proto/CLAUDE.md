# CLAUDE.md — proto (Tracera monorepo subdirectory)

Protocol Buffer definitions for TraceRTM gRPC services.

**gRPC is internal-only**: The gRPC server (port 9091) is not exposed on the Caddy gateway. Server-to-server use only (Go ↔ Python).

## Stack

| Layer | Technology |
|-------|------------|
| Schema | Protocol Buffers 3 (`proto/tracertm/v1/`) |
| Go code | `protoc-gen-go`, `protoc-gen-go-grpc` |
| Python code | `grpc_tools.protoc` |
| Build tool | `buf` (preferred), `protoc` fallback |
| Generated Go | `backend/pkg/proto/` (in tracertm-backend) |
| Generated Python | `src/tracertm/proto/` (in tracertm Python service) |

## Services

### GraphService (Go → Python)

Provided by Go backend, consumed by Python services:
- `AnalyzeImpact`: Impact analysis for graph changes
- `FindCycles`: Circular dependency detection
- `CalculatePath`: Shortest path calculation
- `StreamGraphUpdates`: Real-time graph update streaming

### AIService (Python → Go)

Provided by Python backend, consumed by Go services:
- `AnalyzeRequirement`: NLP analysis of requirements
- `GenerateSuggestions`: AI-powered suggestion generation
- `DetectEquivalences`: Semantic equivalence detection
- `ExtractEntities`: Named entity extraction

## Generate Code

```bash
# Prefer buf (lint + managed mode, from project root)
buf generate

# Or use bun script (tries buf, then protoc)
bun run generate:grpc

# Manual protoc (Go)
protoc --go_out=backend/pkg/proto \
  --go_opt=paths=source_relative \
  --go-grpc_out=backend/pkg/proto \
  --go-grpc_opt=paths=source_relative \
  proto/tracertm/v1/tracertm.proto

# Manual protoc (Python)
GRPC_TOOLS_PROTO_PATH="$(python - <<'PY'
import os, grpc_tools
print(os.path.join(os.path.dirname(grpc_tools.__file__), "_proto"))
PY
)"
env -u PROTOC_INCLUDE python -m grpc_tools.protoc -Iproto -I"$GRPC_TOOLS_PROTO_PATH" \
  --python_out=src/tracertm/proto \
  --grpc_python_out=src/tracertm/proto \
  proto/tracertm/v1/tracertm.proto
```

## Prerequisites

```bash
# buf (preferred)
brew install bufbuild/buf/buf

# protoc (fallback)
brew install protobuf

# Go generators
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Python generators
pip install grpcio grpcio-tools
```

## Workflow

1. Edit `proto/tracertm/v1/tracertm.proto`
2. Run `buf generate` (or `bun run generate:grpc`)
3. Commit both `.proto` changes and generated code

## Generated Output Locations

| Language | Output path | Consumed by |
|----------|-------------|-------------|
| Go | `backend/pkg/proto/tracertm.pb.go`, `tracertm_grpc.pb.go` | Go backend |
| Python | `src/tracertm/proto/tracertm_pb2.py`, `tracertm_pb2_grpc.py` | Python services |

## Governance

- Reference: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
- Specs: `AgilePlus/kitty-specs/<feature-id>/`
- Worklog: `AgilePlus/.work-audit/worklog.md`

## Note

This is a Tracera monorepo subdirectory. All work is committed via the Tracera worktree (`/Users/kooshapari/CodeProjects/Phenotype/repos/`), not a standalone repo.

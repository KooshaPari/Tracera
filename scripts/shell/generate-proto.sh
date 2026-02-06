#!/bin/bash
# Generate gRPC code from Protocol Buffer definitions
# Usage: ./scripts/generate-proto.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔧 Generating gRPC code from protobuf definitions..."

# Check if protoc is installed
if ! command -v protoc &> /dev/null; then
    echo "❌ Error: protoc is not installed"
    echo "Install with: brew install protobuf"
    exit 1
fi

# Generate Go code
echo "📦 Generating Go code..."
mkdir -p backend/pkg/proto
protoc -Iproto --go_out=backend/pkg/proto \
  --go_opt=paths=source_relative \
  --go-grpc_out=backend/pkg/proto \
  --go-grpc_opt=paths=source_relative \
  tracertm/v1/tracertm.proto

if [ $? -eq 0 ]; then
    echo "✅ Go code generated successfully"
else
    echo "❌ Failed to generate Go code"
    exit 1
fi

# Generate Python code
echo "🐍 Generating Python code..."
mkdir -p src/tracertm/proto/tracertm/v1
GRPC_TOOLS_PROTO_PATH="$(python - <<'PY'
import os
import grpc_tools
print(os.path.join(os.path.dirname(grpc_tools.__file__), "_proto"))
PY
)"

env -u PROTOC_INCLUDE python -m grpc_tools.protoc -Iproto -I"$GRPC_TOOLS_PROTO_PATH" \
  --python_out=src/tracertm/proto \
  --grpc_python_out=src/tracertm/proto \
  tracertm/v1/tracertm.proto

if [ $? -eq 0 ]; then
    echo "✅ Python code generated successfully"
else
    echo "❌ Failed to generate Python code"
    exit 1
fi

# Create __init__.py if it doesn't exist
if [ ! -f src/tracertm/proto/__init__.py ]; then
    cat > src/tracertm/proto/__init__.py << 'EOF'
"""Generated protobuf and gRPC code for TraceRTM services."""

try:
    from .tracertm.v1.tracertm_pb2 import *
    from .tracertm.v1.tracertm_pb2_grpc import *
except ImportError:
    pass
EOF
    echo "✅ Created __init__.py"
fi

echo ""
echo "✨ Code generation complete!"
echo ""
echo "Generated files:"
echo "  - backend/pkg/proto/tracertm/v1/tracertm.pb.go"
echo "  - backend/pkg/proto/tracertm/v1/tracertm_grpc.pb.go"
echo "  - src/tracertm/proto/tracertm/v1/tracertm_pb2.py"
echo "  - src/tracertm/proto/tracertm/v1/tracertm_pb2_grpc.py"

#!/bin/bash
# Generate gRPC code from Protocol Buffer definitions
# Usage: ./scripts/generate-grpc.sh [--watch] [--typescript]
#
# Options:
#   --watch       Run in watch mode (requires fswatch)
#   --typescript  Also generate TypeScript grpc-web client
#   --help        Show this help message

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
WATCH_MODE=false
GENERATE_TS=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --watch)
      WATCH_MODE=true
      shift
      ;;
    --typescript)
      GENERATE_TS=true
      shift
      ;;
    --help)
      echo "Usage: $0 [--watch] [--typescript]"
      echo ""
      echo "Options:"
      echo "  --watch       Run in watch mode (requires fswatch)"
      echo "  --typescript  Also generate TypeScript grpc-web client"
      echo "  --help        Show this help message"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Function to generate gRPC code
generate_grpc_code() {
  echo -e "${BLUE}🔧 Generating gRPC code from protobuf definitions...${NC}"
  echo ""

  # Prefer buf if available (lint + managed mode + consistent output)
  if command -v buf &> /dev/null && [ "${SKIP_BUF:-}" != "1" ]; then
    echo -e "${YELLOW}Using buf generate (buf.gen.yaml)...${NC}"
    if buf generate; then
      echo -e "${GREEN}✅ buf generate completed${NC}"
      return 0
    fi
    echo -e "${YELLOW}buf generate failed, falling back to protoc${NC}"
  fi

  # Check if protoc is installed
  if ! command -v protoc &> /dev/null; then
    echo -e "${RED}❌ Error: protoc is not installed${NC}"
    echo "Install with: brew install protobuf (or: brew install bufbuild/buf/buf for buf)"
    exit 1
  fi

  # Generate Go code
  echo -e "${YELLOW}📦 Generating Go server stubs...${NC}"
  mkdir -p backend/pkg/proto

  # Check if Go protoc plugins are installed
  if ! command -v protoc-gen-go &> /dev/null; then
    echo -e "${YELLOW}Installing protoc-gen-go...${NC}"
    cd backend && go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
    cd "$PROJECT_ROOT"
  fi

  if ! command -v protoc-gen-go-grpc &> /dev/null; then
    echo -e "${YELLOW}Installing protoc-gen-go-grpc...${NC}"
    cd backend && go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
    cd "$PROJECT_ROOT"
  fi

  protoc -Iproto --go_out=backend/pkg/proto \
    --go_opt=paths=source_relative \
    --go-grpc_out=backend/pkg/proto \
    --go-grpc_opt=paths=source_relative \
    tracertm/v1/tracertm.proto

  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Go code generated successfully${NC}"
  else
    echo -e "${RED}❌ Failed to generate Go code${NC}"
    exit 1
  fi

  # Generate Python code
  echo -e "${YELLOW}🐍 Generating Python client stubs...${NC}"
  mkdir -p src/tracertm/proto

  # Check if grpcio-tools is installed
  if ! python -c "import grpc_tools" &> /dev/null; then
    echo -e "${YELLOW}Installing grpcio-tools...${NC}"
    pip install grpcio-tools
  fi

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
    echo -e "${GREEN}✅ Python code generated successfully${NC}"
  else
    echo -e "${RED}❌ Failed to generate Python code${NC}"
    exit 1
  fi

  # Create __init__.py if it doesn't exist
  mkdir -p src/tracertm/proto/tracertm/v1
  if [ ! -f src/tracertm/proto/__init__.py ]; then
    cat > src/tracertm/proto/__init__.py << 'EOF'
"""Generated protobuf and gRPC code for TraceRTM services."""

# Import generated modules for easier access
try:
    from .tracertm.v1.tracertm_pb2 import *
    from .tracertm.v1.tracertm_pb2_grpc import *
except ImportError:
    # Generated files don't exist yet
    pass
EOF
    echo -e "${GREEN}✅ Created __init__.py${NC}"
  fi

  # Generate TypeScript code if requested
  if [ "$GENERATE_TS" = true ]; then
    echo -e "${YELLOW}📘 Generating TypeScript grpc-web client...${NC}"

    # Check if protoc-gen-grpc-web is installed
    if ! command -v protoc-gen-grpc-web &> /dev/null; then
      echo -e "${RED}❌ Error: protoc-gen-grpc-web is required for TypeScript generation${NC}"
      echo "Install manually:"
      echo "  macOS: brew install protoc-gen-grpc-web"
      echo "  Linux: Download from https://github.com/grpc/grpc-web/releases"
      exit 1
    fi

    mkdir -p frontend/apps/web/src/api/grpc

    protoc -Iproto \
      --js_out=import_style=commonjs:frontend/apps/web/src/api/grpc \
      --grpc-web_out=import_style=typescript,mode=grpcwebtext:frontend/apps/web/src/api/grpc \
      tracertm/v1/tracertm.proto

    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✅ TypeScript code generated successfully${NC}"
    else
      echo -e "${RED}❌ Failed to generate TypeScript code${NC}"
      exit 1
    fi
  fi

  echo ""
  echo -e "${GREEN}✨ Code generation complete!${NC}"
  echo ""
  echo "Generated files:"
  echo "  ${GREEN}Go (server):${NC}"
  echo "    - backend/pkg/proto/tracertm/v1/tracertm.pb.go"
  echo "    - backend/pkg/proto/tracertm/v1/tracertm_grpc.pb.go"
  echo "  ${GREEN}Python (client):${NC}"
  echo "    - src/tracertm/proto/tracertm/v1/tracertm_pb2.py"
  echo "    - src/tracertm/proto/tracertm/v1/tracertm_pb2_grpc.py"

  if [ "$GENERATE_TS" = true ] && command -v protoc-gen-grpc-web &> /dev/null; then
    echo "  ${GREEN}TypeScript (client):${NC}"
    echo "    - frontend/apps/web/src/api/grpc/tracertm_pb.js"
    echo "    - frontend/apps/web/src/api/grpc/tracertm_grpc_web_pb.js"
  fi
  echo ""
}

# Function to watch proto files for changes
watch_proto_files() {
  echo -e "${BLUE}👀 Watching proto files for changes...${NC}"
  echo "Press Ctrl+C to stop"
  echo ""

  # Check if fswatch is installed
  if ! command -v fswatch &> /dev/null; then
    echo -e "${RED}❌ Error: fswatch is not installed${NC}"
    echo "Install with: brew install fswatch"
    exit 1
  fi

  # Initial generation
  generate_grpc_code

  # Watch for changes
  fswatch -o proto/*.proto | while read f; do
    echo ""
    echo -e "${YELLOW}📝 Proto file changed, regenerating...${NC}"
    generate_grpc_code
  done
}

# Main execution
if [ "$WATCH_MODE" = true ]; then
  watch_proto_files
else
  generate_grpc_code
fi

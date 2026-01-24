# TracerTM

Agent-native, multi-view requirements traceability and project management system.

## Overview

TracerTM is a comprehensive requirements traceability matrix (RTM) system designed for modern software development workflows. It provides:

- **Multi-view project management** - View your projects through code, API, database, deployment, and documentation lenses
- **AI agent integration** - Native support for AI-assisted traceability and analysis
- **Real-time sync** - WebSocket-based live updates across all clients
- **Graph visualization** - Interactive dependency graphs and impact analysis
- **Full traceability** - Link requirements to code, tests, and deployments

## Architecture

The system consists of three main components:

- **Backend** (Go) - High-performance API server with PostgreSQL, Neo4j, and NATS
- **Frontend** (TypeScript/React) - Modern SPA with TanStack Router and Zustand
- **Python CLI/TUI** - Terminal interface with Textual for local workflows

## Quick Start

### Backend

```bash
cd backend
go build ./...
go run ./cmd/api
```

### Frontend

```bash
cd frontend
bun install
bun run dev
```

### Python CLI

```bash
pip install -e .
tracertm --help
```

## Development

### Running Tests

```bash
# Go backend
cd backend && go test ./internal/...

# Frontend
cd frontend && bun test

# Python
pytest tests/
```

### Linting

```bash
# Go
cd backend && golangci-lint run

# Frontend
cd frontend && bun run lint

# Python
ruff check src/
```

## License

MIT License - see LICENSE file for details.

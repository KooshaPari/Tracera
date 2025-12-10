# TraceRTM - Multi-View Requirements Traceability System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Go Version](https://img.shields.io/badge/Go-1.23+-00ADD8?logo=go)](https://golang.org)
[![Python Version](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?logo=postgresql)](https://postgresql.org)

TraceRTM is a hybrid, agent-native requirements traceability and project management system designed for modern software development. It provides 16 professional views, 60+ link types, and intelligent CRUD operations to manage complex projects at any scale.

## Features

- **16 Professional Views**: Feature, Code, Wireframe, API, Test, Database, Architecture, Infrastructure, Data Flow, Security, Performance, Monitoring, Domain Model, User Journey, Configuration, Dependency
- **60+ Link Types**: Rich relationship modeling across 12 categories (Hierarchical, Dependency, Implementation, Testing, Temporal, Conflict, Communication, Data, Deployment, Security, Performance, Monitoring)
- **Intelligent CRUD**: Auto-generation, smart extension, and intelligent collapse
- **Agent-Native**: Support for 1-1000 concurrent autonomous agents
- **Event Sourcing**: Complete audit trail and time-travel capabilities
- **Multi-Platform**: CLI (Python), REST API (Go), Web UI (React), Desktop (Tauri)

## Quick Start

### Prerequisites

- Go 1.23+
- Python 3.12+
- PostgreSQL 14+
- Docker (optional)

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/tracertm/tracertm.git
cd tracertm

# 2. Start infrastructure
docker-compose up -d postgres redis nats

# 3. Setup backend
cd backend
cp .env.example .env
go mod download
sqlc generate
go run main.go

# 4. Setup CLI (in another terminal)
cd cli
pip install -e .
trace health

# 5. Create your first project
trace project create "My Project"
```

See [QUICK_START.md](QUICK_START.md) for detailed setup instructions.

## Architecture

TraceRTM uses a layered hexagonal architecture with CQRS pattern:

```
┌──────────────────────────────────────────────────────────────┐
│              Client Layer                                     │
│  Web UI (React 19) | Desktop (Tauri/Rust) | CLI (Python)     │
└──────────────────────────────────────────────────────────────┘
                         │
┌──────────────────────────────────────────────────────────────┐
│              Backend Services (Go + Echo)                     │
│  REST API | GraphQL | WebSocket                              │
└──────────────────────────────────────────────────────────────┘
                         │
┌──────────────────────────────────────────────────────────────┐
│              Service Layer (Hexagonal Architecture)           │
│  Project | Item | Link | Agent Services (SQLC repositories)  │
└──────────────────────────────────────────────────────────────┘
                         │
┌──────────────────────────────────────────────────────────────┐
│              Data Layer                                       │
│  PostgreSQL (pgx/SQLC) | Neo4j (graph) | Redis | NATS        │
└──────────────────────────────────────────────────────────────┘
```

See [docs/architecture/README.md](docs/architecture/README.md) for complete architecture documentation.

## Usage

### CLI Commands

```bash
# Project management
trace project create "E-commerce Platform"
trace project list
trace project get <project-id>

# Item management (Features, Code, Tests, etc.)
trace item create <project-id> "User Authentication" \
  --type feature \
  --status todo \
  --priority 90

trace item list --project-id <project-id>
trace item list --type feature

# Link management (60+ link types)
trace link create <source-id> <target-id> --type implements
trace link create <test-id> <feature-id> --type tests
trace link list --source-id <item-id>

# Agent management
trace agent create <project-id> "Developer Agent" \
  --status active
trace agent list --project-id <project-id>

# Health check
trace health
```

See [docs/cli/README.md](docs/cli/README.md) for complete CLI reference.

### REST API

```bash
# Create project
curl -X POST http://localhost:8080/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "description": "Description"}'

# Create item
curl -X POST http://localhost:8080/api/v1/items \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "123e4567-...",
    "title": "User Authentication",
    "type": "feature",
    "status": "todo",
    "priority": 90
  }'

# Create link
curl -X POST http://localhost:8080/api/v1/links \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "223e4567-...",
    "target_id": "323e4567-...",
    "type": "depends_on"
  }'
```

See [docs/api/README.md](docs/api/README.md) for complete API reference.

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend API** | Go 1.23+ with Echo framework |
| **Database** | PostgreSQL 14+ (pgx driver) + Neo4j (graph database) |
| **Query Builder** | SQLC (type-safe SQL code generation) |
| **Web UI** | React 19 + TypeScript + Vite + TailwindCSS |
| **Desktop App** | Tauri 2 (Rust backend) + React (frontend) |
| **CLI/TUI** | Python 3.12+ with Typer + Textual + Rich |
| **Caching** | Redis 7+ |
| **Messaging** | NATS 2.9+ |

## Documentation

### Getting Started
- [Quick Start Guide](QUICK_START.md) - 5-minute setup
- [Start Here](START_HERE.md) - Project orientation
- [Installation Guide](docs/development/README.md#development-setup) - Detailed setup

### Reference
- [API Reference](docs/api/README.md) - Complete REST API documentation
- [CLI Reference](docs/cli/README.md) - All CLI commands and examples
- [Architecture](docs/architecture/README.md) - System architecture and design
- [Development Guide](docs/development/README.md) - Contributing and development workflow

### Planning & Research
- [Implementation Status](IMPLEMENTATION_STATUS.md) - Current progress (25% complete)
- [Roadmap](HYBRID_IMPLEMENTATION_ROADMAP.md) - 16-week implementation plan
- [Research Summary](FINAL_RESEARCH_SYNTHESIS.md) - Complete research documentation

## Project Structure

```
tracertm/
├── backend/              # Go REST API
│   ├── internal/        # Private application code
│   │   ├── config/     # Configuration management
│   │   ├── database/   # Database connection
│   │   ├── db/         # Generated sqlc code
│   │   ├── handlers/   # HTTP handlers
│   │   ├── models/     # Domain models
│   │   ├── server/     # Server setup
│   │   └── services/   # Business logic
│   ├── schema.sql      # Database schema
│   ├── queries.sql     # SQL queries for sqlc
│   └── main.go         # Application entry point
│
├── cli/                 # Python CLI
│   └── tracertm/       # CLI package
│       ├── api/        # API client
│       ├── commands/   # CLI commands
│       └── cli.py      # Main CLI app
│
├── docs/                # Documentation
│   ├── api/            # API reference
│   ├── cli/            # CLI reference
│   ├── architecture/   # Architecture docs
│   └── development/    # Development guide
│
├── tests/               # Tests
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── e2e/            # End-to-end tests
│
└── docker-compose.yml   # Docker Compose config
```

## Development

### Setup Development Environment

```bash
# Backend
cd backend
go mod download
sqlc generate
go run main.go

# CLI
cd cli
pip install -e ".[dev]"
trace --version

# Run tests
go test ./...        # Backend tests
pytest               # CLI tests
```

### Running Tests

```bash
# Backend tests
cd backend
go test ./...
go test -cover ./...

# CLI tests
cd cli
pytest
pytest --cov=tracertm

# Integration tests
docker-compose -f docker-compose.test.yml up -d
go test -tags=integration ./...
```

### Code Quality

```bash
# Backend (Go)
golangci-lint run
go fmt ./...

# CLI (Python)
ruff check .
black tracertm/
mypy tracertm/
```

See [docs/development/README.md](docs/development/README.md) for complete development guide.

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`go test ./...` and `pytest`)
6. Commit with conventional commits (`feat:`, `fix:`, `docs:`, etc.)
7. Push to your fork (`git push origin feature/amazing-feature`)
8. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Roadmap

### Phase 1 - Foundation (Weeks 1-4) ✅ COMPLETE
- ✅ Backend scaffolding (13 files)
- ✅ CLI scaffolding (12 files)
- ✅ 24 REST endpoints
- ✅ 16 CLI commands
- ✅ Documentation

### Phase 2 - Core Features (Weeks 5-8) 🚧 IN PROGRESS
- GraphQL API
- WebSocket real-time updates
- Advanced querying and filtering
- Bulk operations
- Event sourcing implementation

### Phase 3 - Web UI (Weeks 9-12)
- React 19 web application
- Multi-view interface
- Real-time collaboration
- Visual link editor

### Phase 4 - Desktop & Mobile (Weeks 13-16)
- Tauri desktop application
- React Native mobile apps
- Offline-first capabilities
- Cross-platform sync

### Phase 5 - AI & Advanced Features (Future)
- AI-powered auto-generation
- NLP for natural language queries
- Graph database integration (Neo4j)
- Advanced analytics and insights

See [HYBRID_IMPLEMENTATION_ROADMAP.md](HYBRID_IMPLEMENTATION_ROADMAP.md) for complete roadmap.

## Current Status

**Overall Progress**: 25% Complete

- ✅ **Research & Planning**: 100% (34 documents, ~400KB)
- ✅ **Phase 1 (Foundation)**: 100% (Backend + CLI scaffolded)
- 🚧 **Phase 2 (Core Features)**: 0% (Starting)
- ⏳ **Phase 3 (Web UI)**: 0%
- ⏳ **Phase 4 (Desktop/Mobile)**: 0%
- ⏳ **Phase 5 (AI Features)**: 0%

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for detailed status.

## Multi-View System

TraceRTM provides 16 professional views for comprehensive project management:

### Core Views
1. **Feature View**: Feature requirements and user stories
2. **Code View**: Source code implementations
3. **Test View**: Test cases and coverage
4. **API View**: API endpoints and contracts

### Design Views
5. **Wireframe View**: UI/UX designs and mockups
6. **Architecture View**: System components and diagrams
7. **Domain Model View**: Domain entities and relationships
8. **User Journey View**: User flows and experiences

### Infrastructure Views
9. **Database View**: Database schemas and migrations
10. **Infrastructure View**: Deployment and infrastructure
11. **Configuration View**: Configuration management
12. **Dependency View**: External dependencies and versions

### Operational Views
13. **Data Flow View**: Data pipelines and transformations
14. **Security View**: Security requirements and vulnerabilities
15. **Performance View**: Performance metrics and benchmarks
16. **Monitoring View**: Monitoring dashboards and alerts

## Link System

60+ link types across 12 categories:

1. **Hierarchical**: parent_of, child_of, contains, part_of
2. **Dependency**: depends_on, blocks, enables, requires
3. **Implementation**: implements, realizes, satisfies
4. **Testing**: tests, verifies, validates
5. **Temporal**: precedes, follows, triggers
6. **Conflict**: conflicts_with, contradicts, mutually_exclusive_with
7. **Communication**: relates_to, references, derived_from
8. **Data**: produces, consumes, transforms
9. **Deployment**: deploys_to, runs_on, scales_with
10. **Security**: authenticates, authorizes, encrypts
11. **Performance**: optimizes, caches, indexes
12. **Monitoring**: monitors, alerts_on, logs

## Agent Architecture

Support for 1-1000 concurrent autonomous agents:

- **Agent Registration**: Register agents with the system
- **Heartbeat Monitoring**: Track agent health and activity
- **Message Passing**: NATS-based pub/sub communication
- **Coordination**: Multi-agent workflow orchestration
- **Conflict Resolution**: Handle concurrent operations

## Examples

### Create a Complete Feature Workflow

```bash
# 1. Create project
PROJECT_ID=$(trace project create "E-commerce" --output json | jq -r '.id')

# 2. Create feature
FEATURE_ID=$(trace item create $PROJECT_ID "Shopping Cart" \
  --type feature --output json | jq -r '.id')

# 3. Create implementation
CODE_ID=$(trace item create $PROJECT_ID "CartService.go" \
  --type code --output json | jq -r '.id')

# 4. Create test
TEST_ID=$(trace item create $PROJECT_ID "Test: Add to Cart" \
  --type test --output json | jq -r '.id')

# 5. Link implementation to feature
trace link create $CODE_ID $FEATURE_ID --type implements

# 6. Link test to feature
trace link create $TEST_ID $FEATURE_ID --type tests

# 7. View complete feature graph
trace item get $FEATURE_ID
```

### Multi-Agent Workflow

```bash
# Create developer, tester, and reviewer agents
DEV=$(trace agent create $PROJECT_ID "Dev Agent" --output json | jq -r '.id')
TEST=$(trace agent create $PROJECT_ID "Test Agent" --output json | jq -r '.id')
REVIEW=$(trace agent create $PROJECT_ID "Review Agent" --output json | jq -r '.id')

# List all agents
trace agent list --project-id $PROJECT_ID
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: https://docs.tracertm.com (coming soon)
- **GitHub Issues**: https://github.com/tracertm/tracertm/issues
- **Discussions**: https://github.com/tracertm/tracertm/discussions
- **Discord**: Coming soon

## Acknowledgments

Built with:
- [Go](https://golang.org) - Backend language
- [Echo](https://echo.labstack.com) - Go web framework
- [SQLC](https://sqlc.dev) - Type-safe SQL code generation
- [PostgreSQL](https://postgresql.org) - Primary database
- [Neo4j](https://neo4j.com) - Graph database
- [Python](https://python.org) - CLI/TUI language
- [Typer](https://typer.tiangolo.com) - CLI framework
- [Textual](https://textual.textualize.io) - Terminal UI framework
- [Rich](https://rich.readthedocs.io) - Terminal formatting
- [React 19](https://react.dev) - Web UI framework
- [Tauri](https://tauri.app) - Desktop app framework (Rust)
- [Redis](https://redis.io) - Caching
- [NATS](https://nats.io) - Messaging

## Authors

- BMad Team - Initial work and architecture

---

**Last Updated**: 2025-11-29
**Version**: 0.1.0
**Status**: Phase 1 Complete, Phase 2 In Progress

---

Made with ❤️ for modern software development

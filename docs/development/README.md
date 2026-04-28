# TraceRTM Development Guide

Complete guide for setting up development environment and contributing to TraceRTM.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Database Migrations](#database-migrations)
- [API Development](#api-development)
- [CLI Development](#cli-development)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

**Required:**
- Go 1.23+
- Python 3.12+
- PostgreSQL 14+
- Git

**Recommended:**
- Docker & Docker Compose
- Make
- sqlc (for database code generation)
- UV (Python package manager)
- Redis (for caching)
- NATS (for messaging)

### Quick Start (5 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/tracertm/tracertm.git
cd tracertm

# 2. Start infrastructure (PostgreSQL, Redis, NATS)
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

# 5. Verify setup
trace project list
```

## Development Setup

### Backend Setup (Go)

#### 1. Install Dependencies

```bash
cd backend

# Download Go modules
go mod download

# Install development tools
go install github.com/sqlc-dev/sqlc/cmd/sqlc@latest
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
```

#### 2. Configure Environment

Create `.env` file:

```bash
# Database
DATABASE_URL=postgres://tracertm:tracertm@localhost:5432/tracertm?sslmode=disable

# Server
PORT=8080
ENV=development
DEBUG=true

# Redis (optional)
REDIS_URL=redis://localhost:6379

# NATS (optional)
NATS_URL=nats://localhost:4222

# JWT (for future authentication)
JWT_SECRET=your-secret-key-here
JWT_EXPIRATION=24h
```

#### 3. Setup Database

```bash
# Create database
createdb tracertm

# Run schema
psql tracertm < schema.sql

# Generate sqlc code
sqlc generate
```

#### 4. Run Backend

```bash
# Development mode (hot reload with air)
go install github.com/cosmtrek/air@latest
air

# Or standard run
go run main.go
```

**Backend will be available at:** `http://localhost:8080`

### CLI Setup (Python)

#### 1. Install UV (Recommended)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. Create Virtual Environment

```bash
cd cli

# With UV
uv venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Or with standard Python
python -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies

```bash
# With UV (recommended)
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

#### 4. Configure Environment

Create `.env` file:

```bash
API_URL=http://localhost:8080
API_TIMEOUT=30
DEBUG=true
VERBOSE=false
```

#### 5. Test CLI

```bash
trace --version
trace health
```

### Docker Setup (Easiest)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

## Project Structure

```
tracertm/
├── backend/                 # Go REST API
│   ├── internal/           # Private application code
│   │   ├── config/        # Configuration management
│   │   ├── database/      # Database connection
│   │   ├── db/            # Generated sqlc code
│   │   ├── handlers/      # HTTP handlers
│   │   ├── models/        # Domain models
│   │   ├── server/        # Server setup
│   │   └── services/      # Business logic
│   ├── schema.sql         # Database schema
│   ├── queries.sql        # SQL queries for sqlc
│   ├── sqlc.yaml          # sqlc configuration
│   ├── main.go            # Application entry point
│   ├── go.mod             # Go dependencies
│   └── Dockerfile         # Docker image
│
├── cli/                    # Python CLI
│   ├── tracertm/          # CLI package
│   │   ├── api/          # API client
│   │   ├── commands/     # CLI commands
│   │   ├── config.py     # Configuration
│   │   └── cli.py        # Main CLI app
│   ├── pyproject.toml    # Python dependencies
│   └── README.md         # CLI documentation
│
├── docs/                   # Documentation
│   ├── api/               # API reference
│   ├── cli/               # CLI reference
│   ├── architecture/      # Architecture docs
│   └── development/       # Development guide
│
├── tests/                  # Tests
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
│
├── docker-compose.yml      # Docker Compose config
├── .gitignore             # Git ignore rules
├── LICENSE                # MIT License
└── README.md              # Project overview
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

#### Backend Changes

```bash
cd backend

# Edit code
vim internal/handlers/item_handler.go

# If adding new SQL queries
vim queries.sql
sqlc generate

# Run backend
go run main.go
```

#### CLI Changes

```bash
cd cli

# Edit code
vim tracertm/commands/item.py

# Test locally
trace item list
```

### 3. Test Changes

```bash
# Backend tests
cd backend
go test ./...

# CLI tests
cd cli
pytest
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build/tooling changes

### 5. Push and Create PR

```bash
git push origin feature/my-feature

# Create pull request on GitHub
```

## Testing

### Backend Tests (Go)

#### Unit Tests

```bash
cd backend

# Run all tests
go test ./...

# Run with coverage
go test -cover ./...

# Run specific package
go test ./internal/handlers/...

# Verbose output
go test -v ./...

# Run specific test
go test -run TestCreateItem ./internal/handlers/...
```

#### Test Example

```go
// internal/handlers/item_handler_test.go
package handlers

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestCreateItem(t *testing.T) {
    // Setup
    handler := NewItemHandler(mockRepo)

    // Test
    req := CreateItemRequest{
        Title: "Test Item",
        Type:  "feature",
    }

    item, err := handler.CreateItem(context.Background(), req)

    // Assert
    assert.NoError(t, err)
    assert.NotNil(t, item)
    assert.Equal(t, "Test Item", item.Title)
}
```

### CLI Tests (Python)

#### Unit Tests

```bash
cd cli

# Run all tests
pytest

# Run with coverage
pytest --cov=tracertm --cov-report=html

# Run specific test file
pytest tests/test_commands.py

# Run specific test
pytest tests/test_commands.py::test_create_project

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

#### Test Example

```python
# tests/test_commands.py
import pytest
from tracertm.commands import project

def test_create_project():
    # Given
    name = "Test Project"
    description = "Test description"

    # When
    result = project.create(name, description)

    # Then
    assert result.success
    assert result.data.name == name
```

### Integration Tests

```bash
# Start test infrastructure
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
go test -tags=integration ./...

# Or for Python
pytest -m integration

# Cleanup
docker-compose -f docker-compose.test.yml down
```

### E2E Tests

```bash
# Start full stack
docker-compose up -d

# Run E2E tests
pytest tests/e2e/

# Cleanup
docker-compose down
```

## Code Quality

### Backend (Go)

#### Linting

```bash
cd backend

# Install golangci-lint
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Run linter
golangci-lint run

# Auto-fix issues
golangci-lint run --fix
```

#### Formatting

```bash
# Format code
go fmt ./...

# Or use gofmt
gofmt -s -w .

# Or use goimports
go install golang.org/x/tools/cmd/goimports@latest
goimports -w .
```

### CLI (Python)

#### Linting

```bash
cd cli

# Ruff (recommended - fast, all-in-one)
ruff check .
ruff check --fix .

# Or separate tools
flake8 tracertm/
pylint tracertm/
```

#### Formatting

```bash
# Black (recommended)
black tracertm/

# Or ruff format
ruff format .
```

#### Type Checking

```bash
# ty (type checking)
ty check src/ --error-on-warning
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix]
```

## Database Migrations

### Using sqlc (Current Approach)

#### 1. Modify Schema

```bash
cd backend

# Edit schema.sql
vim schema.sql
```

#### 2. Add Queries

```bash
# Edit queries.sql
vim queries.sql

# Example: Add new query
-- name: GetItemsByStatus :many
SELECT * FROM items
WHERE project_id = $1 AND status = $2
ORDER BY created_at DESC;
```

#### 3. Generate Code

```bash
sqlc generate
```

#### 4. Use Generated Code

```go
items, err := queries.GetItemsByStatus(ctx, db.GetItemsByStatusParams{
    ProjectID: projectID,
    Status:    "todo",
})
```

### Using Alembic (Alternative)

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Add new table"

# Review migration
cat alembic/versions/001_add_new_table.py

# Run migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## API Development

### Adding New Endpoint

#### 1. Add SQL Query

```sql
-- queries.sql
-- name: GetItemsByPriority :many
SELECT * FROM items
WHERE project_id = $1 AND priority >= $2
ORDER BY priority DESC;
```

#### 2. Generate sqlc Code

```bash
sqlc generate
```

#### 3. Create Handler

```go
// internal/handlers/item_handler.go
func (h *ItemHandler) GetItemsByPriority(c echo.Context) error {
    projectID := c.Param("projectId")
    minPriority := c.QueryParam("min_priority")

    items, err := h.queries.GetItemsByPriority(c.Request().Context(),
        db.GetItemsByPriorityParams{
            ProjectID: uuid.MustParse(projectID),
            Priority:  parseInt(minPriority),
        })

    if err != nil {
        return c.JSON(500, map[string]string{"error": err.Error()})
    }

    return c.JSON(200, items)
}
```

#### 4. Register Route

```go
// internal/server/server.go
func (s *Server) setupRoutes() {
    api := s.echo.Group("/api/v1")

    // Existing routes...

    // New route
    api.GET("/projects/:projectId/items/by-priority",
        s.itemHandler.GetItemsByPriority)
}
```

#### 5. Test Endpoint

```bash
curl http://localhost:8080/api/v1/projects/{id}/items/by-priority?min_priority=80
```

## CLI Development

### Adding New Command

#### 1. Create Command File

```python
# tracertm/commands/search.py
import typer
from rich.console import Console
from tracertm.api import client

app = typer.Typer(help="Search commands")
console = Console()

@app.command()
def items(
    query: str = typer.Argument(..., help="Search query"),
    project_id: str = typer.Option(None, help="Filter by project"),
):
    """Search for items"""
    try:
        results = client.search_items(query, project_id)

        # Display results
        console.print(f"Found {len(results)} items")
        for item in results:
            console.print(f"  - {item['title']} ({item['type']})")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
```

#### 2. Register Command

```python
# tracertm/cli.py
from tracertm.commands import project, item, link, agent, search

app = typer.Typer()

app.add_typer(project.app, name="project")
app.add_typer(item.app, name="item")
app.add_typer(link.app, name="link")
app.add_typer(agent.app, name="agent")
app.add_typer(search.app, name="search")  # New command
```

#### 3. Test Command

```bash
trace search items "authentication"
trace search items "database" --project-id 123e4567-...
```

## Contributing

### Code Style

#### Go
- Follow [Effective Go](https://golang.org/doc/effective_go.html)
- Use `gofmt` for formatting
- Use meaningful variable names
- Add comments for exported functions
- Keep functions small and focused

#### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints (Python 3.12+)
- Use `black` for formatting
- Write docstrings for all functions
- Keep functions small and focused

### Pull Request Guidelines

1. **Branch Naming**
   - `feature/` - New features
   - `fix/` - Bug fixes
   - `docs/` - Documentation
   - `refactor/` - Code refactoring
   - `test/` - Test additions

2. **PR Title**
   - Use conventional commits format
   - Examples: `feat: add search endpoint`, `fix: resolve nil pointer`

3. **PR Description**
   - What changed
   - Why it changed
   - How to test
   - Screenshots (if UI changes)

4. **Checklist**
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] Code formatted
   - [ ] Linter passes
   - [ ] No breaking changes (or documented)

### Code Review Process

1. Submit PR
2. Automated checks run (tests, linting)
3. Reviewer assigned
4. Address feedback
5. Approval
6. Merge to main

## Troubleshooting

### Backend Issues

#### Database Connection Errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
psql tracertm -c "SELECT 1"

# Verify DATABASE_URL
echo $DATABASE_URL
```

#### Port Already in Use

```bash
# Find process using port 8080
lsof -i :8080

# Kill process
kill -9 <PID>

# Or change port in .env
PORT=8081
```

#### sqlc Generation Errors

```bash
# Verify sqlc installation
sqlc version

# Clean and regenerate
rm -rf internal/db/
sqlc generate
```

### CLI Issues

#### Import Errors

```bash
# Reinstall in development mode
pip install -e .

# Or with UV
uv pip install -e .
```

#### API Connection Errors

```bash
# Verify backend is running
curl http://localhost:8080/health

# Check API_URL in .env
echo $API_URL
```

#### Virtual Environment Issues

```bash
# Deactivate and recreate
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Docker Issues

#### Container Won't Start

```bash
# View logs
docker-compose logs backend

# Rebuild containers
docker-compose down
docker-compose up -d --build
```

#### Database Not Initialized

```bash
# Run schema manually
docker-compose exec postgres psql -U tracertm -d tracertm -f /schema.sql
```

### Common Errors

#### Error: "UUID not recognized"

**Solution:** Ensure PostgreSQL version 13+ and extension enabled:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

#### Error: "CORS policy blocking request"

**Solution:** Add CORS middleware in backend:
```go
e.Use(middleware.CORSWithConfig(middleware.CORSConfig{
    AllowOrigins: []string{"http://localhost:3000"},
}))
```

---

## Additional Resources

### Documentation
- [Architecture Overview](../architecture/README.md)
- [API Reference](../api/README.md)
- [CLI Reference](../cli/README.md)

### External Resources
- [Go Documentation](https://golang.org/doc/)
- [Echo Framework](https://echo.labstack.com/)
- [sqlc Documentation](https://docs.sqlc.dev/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)

### Community
- GitHub Issues: https://github.com/tracertm/tracertm/issues
- Discussions: https://github.com/tracertm/tracertm/discussions
- Discord: Coming soon

---

## License

MIT License - see LICENSE file for details.

## Questions?

If you have questions or need help:
1. Check existing [GitHub Issues](https://github.com/tracertm/tracertm/issues)
2. Create a new issue with detailed information
3. Join our community discussions

Happy coding!

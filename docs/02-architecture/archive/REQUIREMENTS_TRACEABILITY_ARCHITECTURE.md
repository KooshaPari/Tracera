# Requirements Traceability System - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Layer (Typer + Rich)                 │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │   Commands   │   TUI (Textual)  │  Export  │             │
│  └──────────────┴──────────────┴──────────────┘             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Service Layer (Business Logic)             │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │ Requirement  │   Linking    │  Versioning  │             │
│  │   Service    │   Service    │   Service    │             │
│  └──────────────┴──────────────┴──────────────┘             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Core Layer (Domain Models)                 │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │  Pydantic    │   Graph      │  Validators  │             │
│  │   Models     │   Engine     │              │             │
│  └──────────────┴──────────────┴──────────────┘             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Storage Layer (Adapters)                       │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │   SQLite     │   Neo4j      │   File-based │             │
│  │   Adapter    │   Adapter    │   Adapter    │             │
│  └──────────────┴──────────────┴──────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

```
rtm/
├── __init__.py
├── cli/
│   ├── __init__.py
│   ├── main.py              # Typer app entry point
│   ├── commands/
│   │   ├── requirement.py   # CRUD commands
│   │   ├── link.py          # Linking commands
│   │   ├── query.py         # Query commands
│   │   └── export.py        # Export commands
│   └── tui/
│       ├── __init__.py
│       ├── app.py           # Textual app
│       └── widgets/         # Custom widgets
├── core/
│   ├── __init__.py
│   ├── models.py            # Pydantic schemas
│   ├── graph.py             # Graph algorithms
│   └── validators.py        # Business rules
├── services/
│   ├── __init__.py
│   ├── requirement.py       # Requirement service
│   ├── linking.py           # Linking service
│   └── versioning.py        # Version management
├── storage/
│   ├── __init__.py
│   ├── base.py              # Abstract adapter
│   ├── sqlite.py            # SQLite implementation
│   ├── neo4j.py             # Neo4j implementation
│   └── migrations/          # Schema migrations
├── extractors/
│   ├── __init__.py
│   ├── python.py            # Python code parser
│   ├── go.py                # Go code parser
│   ├── rust.py              # Rust code parser
│   └── typescript.py        # TypeScript parser
├── integrations/
│   ├── __init__.py
│   ├── mcp.py               # MCP server
│   ├── linter.py            # Linter hooks
│   └── compiler.py          # Compiler hooks
└── utils/
    ├── __init__.py
    ├── config.py            # Configuration
    └── logging.py           # Logging setup
```

## Data Flow

### Create Requirement
```
CLI Command → Service Layer → Validation → Storage → Graph Index
```

### Link Requirements
```
CLI Command → Linking Service → Validate Links → Storage → Update Graph
```

### Query Graph
```
CLI Query → Graph Engine → Transitive Closure → Format Results → Display
```

### Extract from Code
```
Code File → Language Parser → Extract Annotations → Link to Requirements
```

## Key Design Patterns

### 1. Adapter Pattern
- Abstract storage interface
- Multiple implementations (SQLite, Neo4j, File)
- Easy to swap implementations

### 2. Service Layer
- Business logic isolated from CLI
- Reusable across interfaces (CLI, MCP, API)
- Testable independently

### 3. Graph Algorithms
- Transitive closure for hierarchy
- Topological sort for dependencies
- Shortest path for impact analysis

### 4. Temporal Versioning
- Bi-temporal model (valid_from, valid_to)
- Immutable snapshots
- Point-in-time queries

## Integration Architecture

### MCP Server
```
MCP Client (Claude/Agent)
    ↓
MCP Protocol
    ↓
MCP Server (rtm)
    ↓
Service Layer
    ↓
Storage Layer
```

### Code Extraction Pipeline
```
Source Code
    ↓
Language Parser
    ↓
Annotation Extractor
    ↓
Requirement Linker
    ↓
Storage
```

## Performance Considerations

### Query Optimization
- Index on requirement type, status
- Index on link source/target
- Materialized views for common queries
- Query result caching

### Scalability
- Batch operations for bulk imports
- Lazy loading for large graphs
- Pagination for list operations
- Async operations for long-running tasks

## Security & Validation

### Input Validation
- Pydantic schema validation
- Link cycle detection
- Orphaned requirement detection
- Duplicate prevention

### Access Control
- Owner-based permissions
- Role-based access (future)
- Audit logging
- Change tracking


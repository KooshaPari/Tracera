# Requirements Traceability System - MVP Implementation Guide

## MVP Scope (Phase 1)

### Core Features
1. **Requirement CRUD**: Create, read, update, delete requirements
2. **Basic Linking**: Create parent-child and implementation links
3. **Simple Queries**: List, filter, search requirements
4. **Versioning**: Track requirement changes over time
5. **CLI Interface**: Typer-based command-line tool

### Out of Scope (Phase 2+)
- TUI (Textual) - CLI only for MVP
- Multi-language support - Python only
- Smart contracts - Future phase
- MCP integration - Future phase
- Neo4j support - SQLite only

## MVP Database Schema

```sql
CREATE TABLE requirements (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'draft',
    priority TEXT DEFAULT 'medium',
    owner TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE links (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    link_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES requirements(id),
    FOREIGN KEY (target_id) REFERENCES requirements(id)
);

CREATE TABLE versions (
    id TEXT PRIMARY KEY,
    requirement_id TEXT NOT NULL,
    version_num INTEGER NOT NULL,
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP,
    data_snapshot JSON,
    FOREIGN KEY (requirement_id) REFERENCES requirements(id)
);

CREATE INDEX idx_req_type ON requirements(type);
CREATE INDEX idx_req_status ON requirements(status);
CREATE INDEX idx_links_source ON links(source_id);
CREATE INDEX idx_links_target ON links(target_id);
```

## MVP CLI Commands

```bash
# Initialize project
rtm init my-project

# Create requirements
rtm create epic "User Authentication System"
rtm create story "As a user, I want to login"
rtm create test "Test login with valid credentials"

# Link requirements
rtm link epic-1 story-1 decomposes_to
rtm link story-1 test-1 tests

# Query requirements
rtm list
rtm list --type story
rtm list --status active
rtm show req-1
rtm search "login"

# Versioning
rtm history req-1
rtm show req-1 --version 2

# Export
rtm export --format json
rtm export --format csv
```

## MVP Pydantic Models

```python
# core/models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RequirementType(str, Enum):
    EPIC = "epic"
    FEATURE = "feature"
    STORY = "story"
    TASK = "task"
    TEST = "test"
    SPEC = "spec"

class RequirementStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class Requirement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: RequirementType
    title: str
    description: Optional[str] = None
    status: RequirementStatus = RequirementStatus.DRAFT
    priority: str = "medium"
    owner: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = 1

class Link(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    target_id: str
    link_type: str
    created_at: datetime = Field(default_factory=datetime.now)
```

## MVP Storage Implementation

```python
# storage/sqlite.py
import sqlite3
from typing import List, Optional
from core.models import Requirement, Link

class SQLiteStorage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        # Execute schema creation SQL
        pass
    
    def create_requirement(self, req: Requirement) -> Requirement:
        """Insert requirement"""
        pass
    
    def get_requirement(self, req_id: str) -> Optional[Requirement]:
        """Fetch requirement by ID"""
        pass
    
    def list_requirements(self, filters: dict) -> List[Requirement]:
        """List requirements with filters"""
        pass
    
    def create_link(self, link: Link) -> Link:
        """Create traceability link"""
        pass
    
    def get_links(self, source_id: str) -> List[Link]:
        """Get all links from source"""
        pass
```

## MVP CLI Implementation

```python
# cli/main.py
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def init(project_name: str):
    """Initialize new project"""
    console.print(f"[green]✓[/green] Project '{project_name}' initialized")

@app.command()
def create(req_type: str, title: str):
    """Create new requirement"""
    console.print(f"[green]✓[/green] Created {req_type}: {title}")

@app.command()
def list_reqs(req_type: Optional[str] = None):
    """List requirements"""
    table = Table(title="Requirements")
    table.add_column("ID")
    table.add_column("Type")
    table.add_column("Title")
    console.print(table)

if __name__ == "__main__":
    app()
```

## MVP Testing Strategy

```python
# tests/test_storage.py
def test_create_requirement():
    storage = SQLiteStorage(":memory:")
    req = Requirement(type="story", title="Test")
    result = storage.create_requirement(req)
    assert result.id is not None

def test_create_link():
    storage = SQLiteStorage(":memory:")
    link = Link(source_id="1", target_id="2", link_type="decomposes_to")
    result = storage.create_link(link)
    assert result.id is not None
```

## MVP Deliverables

- [ ] SQLite schema + migrations
- [ ] Pydantic models
- [ ] Storage adapter (SQLite)
- [ ] Service layer (CRUD)
- [ ] CLI commands (Typer)
- [ ] Unit tests (90%+ coverage)
- [ ] Documentation
- [ ] Example project


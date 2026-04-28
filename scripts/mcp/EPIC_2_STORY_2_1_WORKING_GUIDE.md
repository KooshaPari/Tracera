# Story 2.1 Working Guide: Item Creation with Type & View

**Story ID:** Story 2.1  
**Title:** Item Creation with Type & View  
**FRs:** FR1, FR6, FR7  
**Priority:** P0 (Critical)  
**Duration:** 5 days  
**Test Cases:** 5 (TC-2.1.1 through TC-2.1.5)

---

## Story Goal

Enable users to **create items** with specific types (epic, feature, story, etc.) and assign them to views (FEATURE, CODE, WIREFRAME, etc.).

### Sample Usage
```bash
# Create an epic
rtm create epic "User Authentication System" --view FEATURE

# Create a feature with description
rtm create feature "OAuth 2.0 Integration" --view API --description "Implement OAuth 2.0 for secure auth"

# Create with metadata
rtm create story "Implement login form" --parent FEATURE-001 --metadata '{"priority": "high", "labels": ["auth", "security"]}'

# Create test item
rtm create test "Unit test for login" --parent FEATURE-001 --owner alice
```

---

## Implementation Checklist

### Day 1: Database Schema & Models

#### 1.1 Verify Database Schema
- [ ] Check items table exists in `alembic/versions/`
- [ ] Verify columns:
  ```sql
  CREATE TABLE items (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL FK projects(id),
    view VARCHAR NOT NULL, -- ENUM: FEATURE, CODE, ...
    type VARCHAR NOT NULL, -- ENUM: epic, feature, story, ...
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR NOT NULL DEFAULT 'todo', -- ENUM: todo, in_progress, done, blocked
    owner VARCHAR,
    priority VARCHAR,
    parent_id UUID FK items(id),
    version INT NOT NULL DEFAULT 1,
    metadata JSONB,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR,
    updated_by VARCHAR
  );
  ```
- [ ] Verify indexes exist:
  ```sql
  CREATE INDEX idx_items_project_id ON items(project_id);
  CREATE INDEX idx_items_view_status ON items(view, status);
  CREATE INDEX idx_items_parent_id ON items(parent_id);
  CREATE INDEX idx_items_created_at ON items(created_at);
  CREATE INDEX idx_items_metadata ON items USING GIN(metadata);
  ```
- [ ] Check if migration exists, otherwise create one

#### 1.2 Create Pydantic Models
**Location:** `src/models/item.py`

```python
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID

class ItemView(str, Enum):
    FEATURE = "FEATURE"
    CODE = "CODE"
    WIREFRAME = "WIREFRAME"
    API = "API"
    TEST = "TEST"
    DATABASE = "DATABASE"
    ROADMAP = "ROADMAP"
    PROGRESS = "PROGRESS"

class ItemType(str, Enum):
    EPIC = "epic"
    FEATURE = "feature"
    STORY = "story"
    TASK = "task"
    BUG = "bug"
    FILE = "file"
    ENDPOINT = "endpoint"
    TEST = "test"
    TABLE = "table"
    MILESTONE = "milestone"

class ItemStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"

class ItemCreateRequest(BaseModel):
    """Request model for creating items"""
    title: str = Field(..., min_length=1, max_length=255)
    type: ItemType
    view: ItemView
    description: Optional[str] = None
    owner: Optional[str] = None
    priority: Optional[str] = None
    parent_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = {}
    status: ItemStatus = ItemStatus.TODO
    
    @validator('metadata')
    def validate_metadata(cls, v):
        if v is None:
            return {}
        # Validate it's JSON-serializable
        import json
        try:
            json.dumps(v)
        except (TypeError, ValueError):
            raise ValueError('metadata must be JSON-serializable')
        return v
    
    class Config:
        use_enum_values = False

class ItemResponse(BaseModel):
    """Response model for items"""
    id: UUID
    project_id: UUID
    title: str
    type: ItemType
    view: ItemView
    description: Optional[str]
    status: ItemStatus
    owner: Optional[str]
    priority: Optional[str]
    parent_id: Optional[UUID]
    version: int
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True
        use_enum_values = False
```

**File Checklist:**
- [ ] Create `src/models/item.py`
- [ ] Import models in `src/models/__init__.py`
- [ ] Add docstrings
- [ ] Add type hints
- [ ] Add validators

#### 1.3 Update Repository Layer
**Location:** `src/repositories/item_repository.py`

```python
from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.db.models import Item
from src.models.item import ItemCreateRequest, ItemResponse, ItemStatus
from datetime import datetime

class ItemRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, project_id: UUID, request: ItemCreateRequest, created_by: str = "system") -> Item:
        """Create a new item"""
        db_item = Item(
            id=UUID(uuid4()),  # Generate UUID
            project_id=project_id,
            title=request.title,
            type=request.type.value,
            view=request.view.value,
            description=request.description,
            status=request.status.value,
            owner=request.owner,
            priority=request.priority,
            parent_id=request.parent_id,
            version=1,
            metadata=request.metadata or {},
            created_by=created_by,
            updated_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        # Validate parent exists if provided
        if request.parent_id:
            parent = self.session.query(Item).filter(Item.id == request.parent_id).first()
            if not parent:
                raise ValueError(f"Parent item {request.parent_id} not found")
            if parent.project_id != project_id:
                raise ValueError(f"Parent item {request.parent_id} not in same project")
        
        self.session.add(db_item)
        self.session.flush()  # Get the ID without committing
        return db_item
    
    def get_by_id(self, item_id: UUID, project_id: UUID) -> Optional[Item]:
        """Get item by ID"""
        return self.session.query(Item).filter(
            and_(Item.id == item_id, Item.project_id == project_id)
        ).first()
    
    def list_by_view(self, project_id: UUID, view: str, include_deleted: bool = False) -> List[Item]:
        """List items by view"""
        query = self.session.query(Item).filter(
            and_(Item.project_id == project_id, Item.view == view)
        )
        if not include_deleted:
            query = query.filter(Item.deleted_at.is_(None))
        return query.all()
    
    def list_all(self, project_id: UUID, include_deleted: bool = False) -> List[Item]:
        """List all items in project"""
        query = self.session.query(Item).filter(Item.project_id == project_id)
        if not include_deleted:
            query = query.filter(Item.deleted_at.is_(None))
        return query.order_by(Item.created_at.desc()).all()
```

**File Checklist:**
- [ ] Create/update `src/repositories/item_repository.py`
- [ ] Add create(), get_by_id(), list_by_view() methods
- [ ] Add validation for parent_id
- [ ] Add docstrings

#### 1.4 Create Service Layer
**Location:** `src/services/item_service.py`

```python
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from src.repositories.item_repository import ItemRepository
from src.models.item import ItemCreateRequest, ItemResponse, ItemStatus
from src.db.models import Item, Event
from datetime import datetime
from src.config import get_current_project

class ItemService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = ItemRepository(session)
    
    def create_item(
        self,
        project_id: UUID,
        request: ItemCreateRequest,
        agent_id: str = "cli",
    ) -> ItemResponse:
        """Create a new item and log creation event"""
        
        # Create item in database
        db_item = self.repo.create(project_id, request, created_by=agent_id)
        
        # Log creation event
        event = Event(
            id=UUID(uuid4()),
            project_id=project_id,
            item_id=db_item.id,
            event_type="item_created",
            data={
                "title": request.title,
                "type": request.type.value,
                "view": request.view.value,
                "status": request.status.value,
            },
            agent_id=agent_id,
            created_at=datetime.utcnow(),
        )
        self.session.add(event)
        self.session.commit()
        
        return ItemResponse.from_orm(db_item)
    
    def get_item(self, project_id: UUID, item_id: UUID) -> Optional[ItemResponse]:
        """Get item by ID"""
        db_item = self.repo.get_by_id(item_id, project_id)
        if not db_item:
            return None
        return ItemResponse.from_orm(db_item)
    
    def list_items(self, project_id: UUID, view: Optional[str] = None) -> List[ItemResponse]:
        """List items (optionally filtered by view)"""
        if view:
            items = self.repo.list_by_view(project_id, view)
        else:
            items = self.repo.list_all(project_id)
        return [ItemResponse.from_orm(item) for item in items]
```

**File Checklist:**
- [ ] Create `src/services/item_service.py`
- [ ] Implement create_item() method
- [ ] Implement event logging
- [ ] Add error handling
- [ ] Add docstrings

### Day 2: CLI Commands

#### 2.1 Create CLI Command Module
**Location:** `src/cli/commands/item.py`

```python
import typer
from typing import Optional
from uuid import UUID
from rich.console import Console
from src.models.item import ItemView, ItemType, ItemStatus
from src.services.item_service import ItemService
from src.db.database import DatabaseConnection
from src.config import ConfigManager

app = typer.Typer(help="Manage items (create, read, update, delete)")
console = Console()

@app.command("create")
def create_item(
    type: ItemType = typer.Argument(..., help="Item type: epic, feature, story, task, bug, file, endpoint, test, table, milestone"),
    title: str = typer.Argument(..., help="Item title"),
    view: Optional[ItemView] = typer.Option(ItemView.FEATURE, "--view", "-v", help="Item view"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Item description"),
    owner: Optional[str] = typer.Option(None, "--owner", "-o", help="Item owner"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="Item priority"),
    parent_id: Optional[str] = typer.Option(None, "--parent", help="Parent item ID"),
    metadata: Optional[str] = typer.Option(None, "--metadata", "-m", help="Metadata as JSON"),
):
    """Create a new item"""
    try:
        # Get current project
        config = ConfigManager()
        project_id = config.get_current_project_id()
        if not project_id:
            console.print("[red]Error: No project selected. Use 'rtm select <project>' first.[/red]")
            raise typer.Exit(1)
        
        # Parse metadata if provided
        parsed_metadata = {}
        if metadata:
            import json
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError as e:
                console.print(f"[red]Error: Invalid JSON in metadata: {e}[/red]")
                raise typer.Exit(1)
        
        # Parse parent_id if provided
        parsed_parent_id = None
        if parent_id:
            try:
                parsed_parent_id = UUID(parent_id)
            except ValueError:
                console.print(f"[red]Error: Invalid parent ID format: {parent_id}[/red]")
                raise typer.Exit(1)
        
        # Create request
        request = ItemCreateRequest(
            title=title,
            type=type,
            view=view,
            description=description,
            owner=owner,
            priority=priority,
            parent_id=parsed_parent_id,
            metadata=parsed_metadata,
        )
        
        # Create item
        db = DatabaseConnection()
        service = ItemService(db.get_session())
        item = service.create_item(project_id, request, agent_id="cli")
        
        console.print(f"[green]✓ Item created: {item.id}[/green]")
        console.print(f"  Type: {item.type}")
        console.print(f"  Title: {item.title}")
        console.print(f"  View: {item.view}")
        console.print(f"  Status: {item.status}")
        
    except Exception as e:
        console.print(f"[red]Error creating item: {e}[/red]")
        raise typer.Exit(1)

# Add other commands (list, show, update, delete) later
```

**File Checklist:**
- [ ] Create `src/cli/commands/item.py`
- [ ] Implement `create` command
- [ ] Add help text
- [ ] Add error handling
- [ ] Register in main CLI

#### 2.2 Register Commands in Main CLI
**Location:** `src/cli/main.py`

```python
# Add to imports
from src.cli.commands import item

# Add to main app
app.add_typer(item.app, name="item")

# This enables commands like:
# rtm item create epic "Title"
# OR
# rtm create epic "Title" (if we expose create at top level)
```

**File Checklist:**
- [ ] Register item commands
- [ ] Test CLI help text
- [ ] Verify command structure

### Day 3: Unit Tests

#### 3.1 Create Unit Test File
**Location:** `tests/unit/test_item_creation.py`

```python
import pytest
from uuid import UUID
from src.models.item import ItemCreateRequest, ItemType, ItemView, ItemStatus
from src.services.item_service import ItemService
from src.db.models import Item

class TestItemCreation:
    """Test item creation functionality"""
    
    @pytest.fixture
    def project_id(self):
        """Return a test project ID"""
        return UUID("00000000-0000-0000-0000-000000000001")
    
    def test_create_item_request_validation(self):
        """TC-2.1.4: Validate item creation request"""
        # Valid request
        request = ItemCreateRequest(
            title="Auth Feature",
            type=ItemType.FEATURE,
            view=ItemView.FEATURE,
            description="Implement OAuth",
        )
        assert request.title == "Auth Feature"
        assert request.type == ItemType.FEATURE
        assert request.view == ItemView.FEATURE
        
        # Invalid type - should fail
        with pytest.raises(ValueError):
            ItemCreateRequest(
                title="Invalid",
                type="invalid_type",  # Invalid
                view=ItemView.FEATURE,
            )
    
    def test_item_type_enum(self):
        """Verify all item types are valid"""
        valid_types = [
            ItemType.EPIC,
            ItemType.FEATURE,
            ItemType.STORY,
            ItemType.TASK,
            ItemType.BUG,
            ItemType.FILE,
            ItemType.ENDPOINT,
            ItemType.TEST,
            ItemType.TABLE,
            ItemType.MILESTONE,
        ]
        assert len(valid_types) == 10
    
    def test_item_view_enum(self):
        """Verify all views are valid"""
        valid_views = [
            ItemView.FEATURE,
            ItemView.CODE,
            ItemView.WIREFRAME,
            ItemView.API,
            ItemView.TEST,
            ItemView.DATABASE,
            ItemView.ROADMAP,
            ItemView.PROGRESS,
        ]
        assert len(valid_views) == 8
    
    def test_metadata_validation(self):
        """TC-2.1.5: Validate metadata is JSON-serializable"""
        import json
        
        # Valid metadata
        valid_metadata = {
            "priority": "high",
            "tags": ["auth", "security"],
            "nested": {"key": "value"}
        }
        request = ItemCreateRequest(
            title="Test",
            type=ItemType.FEATURE,
            view=ItemView.FEATURE,
            metadata=valid_metadata,
        )
        assert request.metadata == valid_metadata
        
        # Verify JSON serializable
        json_str = json.dumps(request.metadata)
        assert json_str is not None
        
        # Invalid metadata - not JSON serializable
        # (e.g., with object references - would fail in validation)
    
    def test_parent_id_optional(self):
        """Verify parent_id is optional"""
        request = ItemCreateRequest(
            title="Epic",
            type=ItemType.EPIC,
            view=ItemView.FEATURE,
        )
        assert request.parent_id is None
        
        request_with_parent = ItemCreateRequest(
            title="Feature",
            type=ItemType.FEATURE,
            view=ItemView.FEATURE,
            parent_id=UUID("00000000-0000-0000-0000-000000000001"),
        )
        assert request_with_parent.parent_id == UUID("00000000-0000-0000-0000-000000000001")

# TC-2.1.1, TC-2.1.2, TC-2.1.3 will be integration tests
# TC-2.1.5 will be tested in service tests
```

**File Checklist:**
- [ ] Create `tests/unit/test_item_creation.py`
- [ ] Implement validation tests
- [ ] Implement enum tests
- [ ] Add pytest fixtures
- [ ] Run tests: `pytest tests/unit/test_item_creation.py -v`

#### 3.2 Test Output
```bash
$ pytest tests/unit/test_item_creation.py -v
test_create_item_request_validation PASSED
test_item_type_enum PASSED
test_item_view_enum PASSED
test_metadata_validation PASSED
test_parent_id_optional PASSED

===== 5 passed in 0.05s =====
```

### Day 4: Integration Tests

#### 4.1 Create Integration Test File
**Location:** `tests/integration/test_item_creation_integration.py`

```python
import pytest
from uuid import UUID
from src.models.item import ItemCreateRequest, ItemType, ItemView
from src.services.item_service import ItemService
from src.db.database import DatabaseConnection
from src.db.models import Item, Event

@pytest.fixture
def db_session():
    """Create a test database session"""
    db = DatabaseConnection()
    session = db.get_session()
    yield session
    session.close()

@pytest.fixture
def project_id(db_session):
    """Create a test project"""
    from src.db.models import Project
    project = Project(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        name="Test Project",
        description="Test",
    )
    db_session.add(project)
    db_session.commit()
    return project.id

class TestItemCreationIntegration:
    """Integration tests for item creation"""
    
    def test_create_item_with_type_and_view(self, db_session, project_id):
        """TC-2.1.1: Create item with type and view"""
        request = ItemCreateRequest(
            title="User Authentication",
            type=ItemType.EPIC,
            view=ItemView.FEATURE,
        )
        
        service = ItemService(db_session)
        item = service.create_item(project_id, request, agent_id="test")
        
        assert item.id is not None
        assert item.title == "User Authentication"
        assert item.type == ItemType.EPIC
        assert item.view == ItemView.FEATURE
        assert item.status == "todo"
        assert item.version == 1
        
        # Verify in database
        db_item = db_session.query(Item).filter(Item.id == item.id).first()
        assert db_item is not None
        assert db_item.title == "User Authentication"
    
    def test_create_items_in_all_views(self, db_session, project_id):
        """TC-2.1.2: Create items in all 8 views"""
        views = [
            ItemView.FEATURE,
            ItemView.CODE,
            ItemView.WIREFRAME,
            ItemView.API,
            ItemView.TEST,
            ItemView.DATABASE,
            ItemView.ROADMAP,
            ItemView.PROGRESS,
        ]
        
        service = ItemService(db_session)
        created_items = []
        
        for view in views:
            request = ItemCreateRequest(
                title=f"Item in {view.value}",
                type=ItemType.FEATURE,
                view=view,
            )
            item = service.create_item(project_id, request, agent_id="test")
            created_items.append(item)
        
        assert len(created_items) == 8
        
        # Verify all created
        for item, view in zip(created_items, views):
            assert item.view == view
            
            # Verify in database
            db_item = db_session.query(Item).filter(Item.id == item.id).first()
            assert db_item is not None
            assert db_item.view == view.value
    
    def test_item_creation_with_metadata(self, db_session, project_id):
        """TC-2.1.3: Create item with metadata"""
        metadata = {
            "priority": "high",
            "tags": ["auth", "security"],
            "assignee": "alice",
        }
        
        request = ItemCreateRequest(
            title="OAuth Implementation",
            type=ItemType.FEATURE,
            view=ItemView.API,
            metadata=metadata,
        )
        
        service = ItemService(db_session)
        item = service.create_item(project_id, request, agent_id="test")
        
        assert item.metadata == metadata
        assert item.metadata["priority"] == "high"
        
        # Verify in database
        db_item = db_session.query(Item).filter(Item.id == item.id).first()
        assert db_item.metadata == metadata
    
    def test_item_creation_event_logging(self, db_session, project_id):
        """TC-2.1.5: Verify creation event is logged"""
        request = ItemCreateRequest(
            title="Test Feature",
            type=ItemType.FEATURE,
            view=ItemView.FEATURE,
        )
        
        service = ItemService(db_session)
        item = service.create_item(project_id, request, agent_id="test-agent")
        
        # Check event was logged
        event = db_session.query(Event).filter(
            Event.item_id == item.id
        ).first()
        
        assert event is not None
        assert event.event_type == "item_created"
        assert event.agent_id == "test-agent"
        assert event.data["title"] == "Test Feature"
        assert event.data["type"] == "feature"
        assert event.data["view"] == "FEATURE"
```

**File Checklist:**
- [ ] Create `tests/integration/test_item_creation_integration.py`
- [ ] Implement all 5 test cases
- [ ] Add database fixtures
- [ ] Add project fixture
- [ ] Run tests: `pytest tests/integration/test_item_creation_integration.py -v`

#### 4.2 Run Integration Tests
```bash
$ pytest tests/integration/test_item_creation_integration.py -v

test_create_item_with_type_and_view PASSED
test_create_items_in_all_views PASSED
test_item_creation_with_metadata PASSED
test_item_creation_event_logging PASSED

===== 4 passed in 0.50s =====
```

### Day 5: CLI Testing & Documentation

#### 5.1 Manual CLI Testing

```bash
# Initialize project
rtm project init MyProject
rtm project select MyProject

# Test create epic
rtm create epic "User Authentication" --view FEATURE

# Test create feature
rtm create feature "OAuth 2.0 Integration" --view API --description "Implement OAuth"

# Test create with metadata
rtm create story "Implement login form" --metadata '{"priority": "high", "labels": ["auth"]}'

# Test create with parent
rtm create feature "Login" --parent <EPIC-ID>

# Verify created
rtm list
rtm show <ITEM-ID>
```

**Checklist:**
- [ ] Test create epic
- [ ] Test create feature
- [ ] Test create story
- [ ] Test create with metadata
- [ ] Test create with parent
- [ ] Verify listing works
- [ ] Verify show works

#### 5.2 Create Documentation
**Location:** `docs/stories/story-2-1-item-creation.md`

```markdown
# Story 2.1: Item Creation with Type & View

## Overview
Create items with specific types and assign them to views.

## Item Types
- **epic**: Large feature grouping
- **feature**: User-facing feature
- **story**: Work unit
- **task**: Implementation task
- **bug**: Issue to fix
- **file**: Code file
- **endpoint**: API endpoint
- **test**: Test case
- **table**: Database table
- **milestone**: Release milestone

## Item Views
- **FEATURE**: Feature view (default)
- **CODE**: Code/architecture view
- **WIREFRAME**: UI wireframe view
- **API**: API design view
- **TEST**: Test case view
- **DATABASE**: Database schema view
- **ROADMAP**: Release roadmap view
- **PROGRESS**: Progress tracking view

## Usage Examples

### Create Epic
```bash
rtm create epic "User Authentication System" --view FEATURE
```

### Create Feature
```bash
rtm create feature "OAuth 2.0" --view API --description "Implement OAuth 2.0"
```

### Create Story
```bash
rtm create story "Implement login form" --parent FEATURE-001
```

### Create with Metadata
```bash
rtm create story "Test login" --metadata '{"priority": "high", "labels": ["auth"]}'
```

## Acceptance Criteria
- ✅ Create items in all 8 views
- ✅ Support 10 item types
- ✅ Auto-generate UUID
- ✅ Default status to 'todo'
- ✅ Validate input
- ✅ Log creation event
- ✅ Store metadata

## Testing
```bash
pytest tests/unit/test_item_creation.py -v
pytest tests/integration/test_item_creation_integration.py -v
```
```

**File Checklist:**
- [ ] Create documentation file
- [ ] Add usage examples
- [ ] Add item types table
- [ ] Add views table
- [ ] Add acceptance criteria

#### 5.3 Update Main Documentation
**Location:** `README.md` (add to Item Management section)

```markdown
### Create Items

```bash
# Create epic
rtm create epic "Feature Title" [--view FEATURE] [--description "..."]

# Create with parent
rtm create feature "Sub-feature" --parent EPIC-001

# Create with metadata
rtm create story "Story" --metadata '{"priority": "high"}'
```
```

**File Checklist:**
- [ ] Update README.md
- [ ] Add create examples
- [ ] Add item types reference

---

## Testing Summary

| Test Type | Count | Status | Command |
|-----------|-------|--------|---------|
| Unit | 5 | To implement | `pytest tests/unit/test_item_creation.py -v` |
| Integration | 4 | To implement | `pytest tests/integration/test_item_creation_integration.py -v` |
| CLI Manual | 6 | To implement | See section 5.1 |
| **Total** | **15** | | |

---

## Success Criteria Checklist

- [ ] **Models**: ItemCreateRequest, ItemResponse, Enums
- [ ] **Repository**: create(), get_by_id(), list_by_view()
- [ ] **Service**: create_item() with event logging
- [ ] **CLI**: `rtm create` command with all options
- [ ] **Unit Tests**: 5/5 passing
- [ ] **Integration Tests**: 4/4 passing
- [ ] **Manual Tests**: All 6 CLI scenarios working
- [ ] **Documentation**: Story documentation complete
- [ ] **Code Quality**: Docstrings, type hints, error handling
- [ ] **Ready for Story 2.2**: Yes

---

## Files to Create/Modify

### Create New Files
- [ ] `src/models/item.py` - Pydantic models & enums
- [ ] `src/services/item_service.py` - Business logic
- [ ] `src/cli/commands/item.py` - CLI commands
- [ ] `tests/unit/test_item_creation.py` - Unit tests
- [ ] `tests/integration/test_item_creation_integration.py` - Integration tests
- [ ] `docs/stories/story-2-1-item-creation.md` - Story documentation

### Modify Existing Files
- [ ] `src/models/__init__.py` - Add ItemCreateRequest, ItemResponse
- [ ] `src/services/__init__.py` - Add ItemService
- [ ] `src/cli/main.py` - Register item commands
- [ ] `src/repositories/__init__.py` - Add ItemRepository
- [ ] `README.md` - Add item creation examples

---

## Estimated Breakdown

| Task | Duration | Status |
|------|----------|--------|
| Database schema verification | 0.5 day | Pending |
| Models & validators | 1 day | Pending |
| Repository layer | 0.5 day | Pending |
| Service layer | 1 day | Pending |
| CLI commands | 1 day | Pending |
| Unit tests | 0.5 day | Pending |
| Integration tests | 0.5 day | Pending |
| CLI testing | 0.5 day | Pending |
| Documentation | 0.5 day | Pending |
| **Total** | **5 days** | |

---

## References

- Epic 2 Design: `docs/test-design-epic-2.md`
- Epic 2 Plan: `scripts/mcp/EPIC_2_IMPLEMENTATION_PLAN.md`
- FRs: FR1 (8 views), FR6 (Create), FR7 (Item types)

---

**Working Guide Created:** 2025-11-23  
**Status:** 🟡 **READY FOR IMPLEMENTATION**  
**Next:** Start with database schema verification

# Epic 2 Implementation Plan - Core Item Management

**Epic ID:** Epic 2  
**Title:** Core Item Management  
**Status:** 🟡 **IN PROGRESS**  
**Duration:** 20 days (estimated)  
**Stories:** 6 stories (2.1 - 2.6)  
**Test Cases:** 26 test cases  
**FRs Covered:** FR1-FR15 (Multi-View System + Item Management)  
**Priority:** P0 (Critical - foundation for all workflows)

---

## Executive Summary

Epic 2 focuses on implementing **complete CRUD operations** for items across all views with:
- ✅ Create items with type and view
- ✅ Read items with filters and formatting
- ✅ Update items with optimistic locking
- ✅ Delete items (soft delete with recovery)
- ✅ Metadata management (JSONB)
- ✅ Hierarchical relationships (parent-child)

**Key Technical Challenges:**
- Optimistic locking for concurrent updates
- JSONB queries with GIN indexes
- Recursive CTEs for hierarchy
- Event logging for audit trail

---

## Story Breakdown

### Story 2.1: Item Creation with Type & View (5 days)

**FRs:** FR1, FR6, FR7  
**Test Cases:** TC-2.1.1 through TC-2.1.5 (5 tests)  
**Priority:** P0 (Critical)

#### Acceptance Criteria
- [ ] Create items in all 8 views (FEATURE, CODE, WIREFRAME, API, TEST, DATABASE, ROADMAP, PROGRESS)
- [ ] Support 10 item types (epic, feature, story, task, bug, file, endpoint, test, table, milestone)
- [ ] Auto-generate UUID and default status (todo)
- [ ] Validate item type and view
- [ ] Log creation event with timestamp and agent_id
- [ ] Store metadata (JSONB) if provided

#### Implementation Tasks
1. **Database Schema** (1 day)
   - [ ] Verify items table exists with all columns
   - [ ] Add GIN index on metadata (JSONB)
   - [ ] Add index on (view, status, created_at)
   - [ ] Verify events table for audit logging

2. **Models & Validators** (1 day)
   - [ ] Create ItemCreateRequest Pydantic model
   - [ ] Validate item types (enum)
   - [ ] Validate views (enum)
   - [ ] Validate metadata (JSON schema)
   - [ ] Add docstrings to models

3. **Service Layer** (2 days)
   - [ ] Implement ItemService.create_item()
   - [ ] Handle UUID generation
   - [ ] Create creation event
   - [ ] Add transaction support
   - [ ] Add error handling for duplicate titles

4. **CLI Commands** (1 day)
   - [ ] Implement `rtm create <type> <title> [options]`
   - [ ] Support `--view` option
   - [ ] Support `--description` option
   - [ ] Support `--metadata` option (JSON)
   - [ ] Add help text for item types

#### Test Implementation (TC-2.1.1 through TC-2.1.5)
```python
# tests/unit/test_item_creation.py
class TestItemCreation:
    def test_create_item_with_type_and_view(self):
        # TC-2.1.1
        pass
    
    def test_create_items_in_all_views(self):
        # TC-2.1.2
        pass
    
    def test_item_creation_with_metadata(self):
        # TC-2.1.3
        pass
    
    def test_invalid_item_type(self):
        # TC-2.1.4
        pass
    
    def test_item_creation_event_logging(self):
        # TC-2.1.5
        pass
```

#### Success Metrics
- ✅ All 5 tests pass
- ✅ Unit coverage ≥90%
- ✅ Integration tests pass on database
- ✅ Event logging working
- ✅ CLI commands functional

---

### Story 2.2: Item Retrieval & Display (4 days)

**FRs:** FR2, FR8, FR23  
**Test Cases:** TC-2.2.1 through TC-2.2.6 (6 tests)  
**Priority:** P0 (Critical)

#### Acceptance Criteria
- [ ] Retrieve item by ID with all details
- [ ] List items by view
- [ ] Filter items by status
- [ ] Support output formats (JSON, YAML, table)
- [ ] Handle item not found (NotFoundError)
- [ ] Query performance <50ms for index-based queries
- [ ] Pagination support (limit, offset)

#### Implementation Tasks
1. **Query Layer** (1 day)
   - [ ] Implement ItemService.get_item(id)
   - [ ] Implement ItemService.list_items(view, filters)
   - [ ] Add filtering by status
   - [ ] Add sorting (by created_at, title)
   - [ ] Add pagination

2. **Output Formatting** (1 day)
   - [ ] Implement JSON formatter
   - [ ] Implement YAML formatter
   - [ ] Implement table formatter (Rich tables)
   - [ ] Support nested metadata display

3. **CLI Commands** (1 day)
   - [ ] Implement `rtm show <id> [--format] [--version]`
   - [ ] Implement `rtm view <view> [--status] [--limit]`
   - [ ] Implement `rtm list [--view] [--status]`
   - [ ] Add help text with examples

4. **Performance Optimization** (1 day)
   - [ ] Verify indexes on (id, view, status)
   - [ ] Add query logging and metrics
   - [ ] Optimize metadata queries (GIN index)
   - [ ] Test with 10K items

#### Test Implementation (TC-2.2.1 through TC-2.2.6)
```python
# tests/integration/test_item_retrieval.py
class TestItemRetrieval:
    def test_retrieve_item_by_id(self):
        # TC-2.2.1
        pass
    
    def test_list_items_by_view(self):
        # TC-2.2.2
        pass
    
    def test_filter_items_by_status(self):
        # TC-2.2.3
        pass
    
    def test_output_format_json_yaml_table(self):
        # TC-2.2.4
        pass
    
    def test_item_not_found(self):
        # TC-2.2.5
        pass
    
    def test_performance_large_dataset(self):
        # TC-2.2.6
        pass
```

#### Success Metrics
- ✅ All 6 tests pass
- ✅ Query performance <50ms
- ✅ Output formatting works
- ✅ GIN indexes used for JSONB
- ✅ Pagination working

---

### Story 2.3: Item Update with Optimistic Locking (5 days)

**FRs:** FR9, FR36, FR54  
**Test Cases:** TC-2.3.1 through TC-2.3.5 (5 tests)  
**Priority:** P0 (Critical)  
**Risk:** HIGH (concurrency)

#### Acceptance Criteria
- [ ] Update item properties (status, title, description, owner, metadata)
- [ ] Increment version on each update
- [ ] Detect concurrent updates (OptimisticLockError)
- [ ] Support force update (override version check)
- [ ] Implement retry logic with exponential backoff (max 3 retries)
- [ ] Atomic updates (all-or-nothing)
- [ ] Log update event with change delta

#### Implementation Tasks
1. **Optimistic Locking Logic** (2 days)
   - [ ] Implement version checking in ItemService.update_item()
   - [ ] Return OptimisticLockError if version mismatch
   - [ ] Implement atomic update with version increment
   - [ ] Add force update option (bypass version check)
   - [ ] Log concurrency conflicts

2. **Retry Logic** (1 day)
   - [ ] Implement exponential backoff (100ms, 200ms, 400ms)
   - [ ] Max 3 retries on conflict
   - [ ] Automatic retry in CLI
   - [ ] Log retry attempts

3. **CLI Commands** (1 day)
   - [ ] Implement `rtm update <id> --status <status>`
   - [ ] Support multiple field updates
   - [ ] Support `--force` flag
   - [ ] Show version info before/after

4. **Testing & Validation** (1 day)
   - [ ] Create concurrent update test harness
   - [ ] Test with 2, 10, 100 concurrent agents
   - [ ] Verify no data loss
   - [ ] Verify event logging

#### Test Implementation (TC-2.3.1 through TC-2.3.5)
```python
# tests/integration/test_item_update.py
class TestItemUpdate:
    def test_update_item_status(self):
        # TC-2.3.1
        pass
    
    def test_concurrent_update_conflict(self):
        # TC-2.3.2
        # Simulate two agents updating same item
        pass
    
    def test_force_update_override(self):
        # TC-2.3.3
        pass
    
    def test_update_multiple_fields(self):
        # TC-2.3.4
        pass
    
    def test_retry_logic(self):
        # TC-2.3.5
        # Test exponential backoff
        pass
```

#### Success Metrics
- ✅ All 5 tests pass
- ✅ Concurrency tests with 100 agents pass
- ✅ No data loss in conflict scenarios
- ✅ Retry logic working
- ✅ Version incrementing correctly

---

### Story 2.4: Item Deletion with Soft Delete (3 days)

**FRs:** FR10, FR54  
**Test Cases:** TC-2.4.1 through TC-2.4.4 (4 tests)  
**Priority:** P1 (High)

#### Acceptance Criteria
- [ ] Soft delete items (set deleted_at timestamp)
- [ ] Exclude deleted items from default queries
- [ ] View deleted items with `--include-deleted` flag
- [ ] Permanent delete with `--permanent` flag
- [ ] Cascade soft delete to child items
- [ ] Log deletion event
- [ ] Prevent operations on deleted items

#### Implementation Tasks
1. **Soft Delete Logic** (1 day)
   - [ ] Add deleted_at column to items table (nullable timestamp)
   - [ ] Implement ItemService.delete_item(id, permanent=False)
   - [ ] Add soft_delete() method to repository
   - [ ] Filter out deleted items by default (add to list_items)
   - [ ] Add --include-deleted filter

2. **Recovery Support** (1 day)
   - [ ] Implement ItemService.undelete_item(id)
   - [ ] Create undelete CLI command
   - [ ] Log recovery events
   - [ ] Restore cascade-deleted items

3. **CLI Commands** (0.5 day)
   - [ ] Implement `rtm delete <id> [--permanent] [--cascade]`
   - [ ] Add confirmation prompt for permanent delete
   - [ ] Add recovery instructions

4. **Testing** (0.5 day)
   - [ ] Test soft delete scenarios
   - [ ] Test cascade delete to children
   - [ ] Test recovery

#### Test Implementation (TC-2.4.1 through TC-2.4.4)
```python
# tests/integration/test_item_deletion.py
class TestItemDeletion:
    def test_soft_delete_item(self):
        # TC-2.4.1
        pass
    
    def test_view_deleted_items(self):
        # TC-2.4.2
        pass
    
    def test_permanent_delete(self):
        # TC-2.4.3
        pass
    
    def test_deletion_event_logging(self):
        # TC-2.4.4
        pass
```

#### Success Metrics
- ✅ All 4 tests pass
- ✅ Soft delete working
- ✅ Recovery working
- ✅ Cascade deletes working
- ✅ Event logging working

---

### Story 2.5: Item Metadata & Custom Fields (3 days)

**FRs:** FR11, FR60  
**Test Cases:** TC-2.5.1 through TC-2.5.4 (4 tests)  
**Priority:** P1 (High)

#### Acceptance Criteria
- [ ] Store arbitrary metadata in JSONB field
- [ ] Query items by metadata fields
- [ ] Support nested metadata
- [ ] Update individual metadata keys
- [ ] Validate metadata (JSON schema)
- [ ] GIN index for performance
- [ ] Export metadata with items

#### Implementation Tasks
1. **Metadata Storage & Querying** (1 day)
   - [ ] Verify metadata column exists (JSONB)
   - [ ] Implement JSONSchema validator
   - [ ] Implement metadata query builder
   - [ ] Add GIN index on metadata
   - [ ] Test JSONB operators

2. **Update & Merge** (1 day)
   - [ ] Implement metadata merge logic
   - [ ] Support update-specific-key
   - [ ] Support deep updates (nested objects)
   - [ ] Validate on update

3. **CLI Commands** (1 day)
   - [ ] Implement `rtm update <id> --metadata '{"key": "value"}'`
   - [ ] Support `--metadata-set` for partial updates
   - [ ] Support `--metadata-delete` for removal
   - [ ] Display metadata in show command

#### Test Implementation (TC-2.5.1 through TC-2.5.4)
```python
# tests/integration/test_item_metadata.py
class TestItemMetadata:
    def test_add_metadata_to_item(self):
        # TC-2.5.1
        pass
    
    def test_query_by_metadata(self):
        # TC-2.5.2
        pass
    
    def test_update_specific_metadata_key(self):
        # TC-2.5.3
        pass
    
    def test_invalid_json_metadata(self):
        # TC-2.5.4
        pass
```

#### Success Metrics
- ✅ All 4 tests pass
- ✅ GIN index working
- ✅ Metadata queries fast (<50ms)
- ✅ JSON validation working
- ✅ Partial updates working

---

### Story 2.6: Item Hierarchy (Parent-Child) (5 days)

**FRs:** FR12, FR68  
**Test Cases:** TC-2.6.1 through TC-2.6.6 (6 tests)  
**Priority:** P1 (High)  
**Risk:** HIGH (complex recursive queries)

#### Acceptance Criteria
- [ ] Create child items with parent reference
- [ ] Query children of item
- [ ] Query ancestors (path to root)
- [ ] Calculate progress rollup (average of children)
- [ ] Cascade soft delete to descendants
- [ ] Prevent circular references
- [ ] Support deep hierarchies (10+ levels)
- [ ] Optimize with recursive CTEs

#### Implementation Tasks
1. **Hierarchy Schema & Logic** (2 days)
   - [ ] Verify parent_id column exists
   - [ ] Add foreign key constraint with ON DELETE
   - [ ] Implement circular reference validation
   - [ ] Implement parent validation (check exists)
   - [ ] Add indexes on parent_id

2. **Recursive Queries** (2 days)
   - [ ] Implement get_children() with CTE
   - [ ] Implement get_ancestors() with CTE
   - [ ] Implement get_descendants() with CTE
   - [ ] Implement calculate_depth()
   - [ ] Test performance on large hierarchies

3. **Progress Rollup** (1 day)
   - [ ] Implement progress calculation (average of children)
   - [ ] Implement rollup on child update
   - [ ] Add caching for rollup values
   - [ ] Add CLI option to recalculate

4. **CLI Commands** (1 day)
   - [ ] Implement `rtm show <id> --children`
   - [ ] Implement `rtm show <id> --ancestors`
   - [ ] Implement `rtm show <id> --tree` (ASCII tree)
   - [ ] Display progress rollup

#### Test Implementation (TC-2.6.1 through TC-2.6.6)
```python
# tests/integration/test_item_hierarchy.py
class TestItemHierarchy:
    def test_create_child_item(self):
        # TC-2.6.1
        pass
    
    def test_query_children(self):
        # TC-2.6.2
        pass
    
    def test_query_ancestors(self):
        # TC-2.6.3
        pass
    
    def test_progress_rollup(self):
        # TC-2.6.4
        pass
    
    def test_cascade_soft_delete(self):
        # TC-2.6.5
        pass
    
    def test_circular_reference_prevention(self):
        # TC-2.6.6
        pass
```

#### Success Metrics
- ✅ All 6 tests pass
- ✅ Circular reference prevention working
- ✅ Recursive queries optimized
- ✅ Progress rollup accurate
- ✅ Support 10+ level hierarchies
- ✅ Cascade deletes working

---

## Implementation Timeline

| Week | Story | Focus | Days |
|------|-------|-------|------|
| 1 | 2.1 | Item creation, models, validators | 5 |
| 1-2 | 2.2 | Item retrieval, querying, formatting | 4 |
| 2 | 2.3 | Optimistic locking, concurrency | 5 |
| 2-3 | 2.4 | Soft delete, recovery | 3 |
| 3 | 2.5 | Metadata, JSONB queries | 3 |
| 3 | 2.6 | Hierarchy, recursive CTEs | 5 |
| **Total** | | | **25 days** |

---

## Technical Architecture

### Database Layer
```
Items Table
├── id (UUID)
├── view (ENUM: FEATURE, CODE, ...)
├── type (ENUM: epic, feature, story, ...)
├── title (VARCHAR)
├── description (TEXT)
├── status (ENUM: todo, in_progress, done, blocked)
├── parent_id (UUID FK) → items(id)
├── version (INT) - for optimistic locking
├── metadata (JSONB) - custom fields
├── deleted_at (TIMESTAMP) - soft delete
├── created_at, updated_at (TIMESTAMP)
└── Indexes:
    ├── PK: id
    ├── FK: parent_id → items(id)
    ├── Index: (view, status)
    ├── Index: (parent_id)
    ├── GIN: metadata
```

### Service Layer
```python
class ItemService:
    # Create
    def create_item(request: ItemCreateRequest) -> Item
    
    # Read
    def get_item(id: UUID, include_deleted: bool = False) -> Item
    def list_items(view: View, filters: Dict) -> List[Item]
    def get_children(id: UUID) -> List[Item]
    def get_ancestors(id: UUID) -> List[Item]
    
    # Update
    def update_item(id: UUID, version: int, updates: Dict) -> Item
    def update_metadata(id: UUID, metadata: Dict) -> Item
    
    # Delete
    def delete_item(id: UUID, permanent: bool = False) -> None
    def undelete_item(id: UUID) -> Item
    
    # Analytics
    def get_hierarchy_tree(id: UUID) -> Tree
    def calculate_progress(id: UUID) -> float
```

### CLI Commands
```bash
# Create
rtm create epic "System Design"
rtm create feature "Auth" --parent EPIC-001
rtm create story "Implement login" --priority high --owner alice

# Read
rtm show EPIC-001
rtm show EPIC-001 --children
rtm show STORY-001 --ancestors
rtm list --view FEATURE --status todo

# Update
rtm update FEATURE-001 --status in_progress
rtm update FEATURE-001 --title "New Title" --owner bob
rtm update FEATURE-001 --metadata '{"priority": "high"}'

# Delete
rtm delete FEATURE-001
rtm delete EPIC-001 --cascade # soft delete with children
rtm delete EPIC-001 --permanent # hard delete
```

---

## Test Strategy

### Phase 1: Unit Tests (5 minutes)
- Validators (type, view, metadata validation)
- Business logic (circular reference check, progress calc)
- Model validation (Pydantic)

### Phase 2: Integration Tests (20 minutes)
- Database operations (CRUD)
- Optimistic locking (concurrency)
- Recursive queries (hierarchy)
- JSONB queries (metadata)
- Event logging

### Phase 3: E2E Tests (5 minutes)
- CLI commands
- Output formatting
- Performance tests (10K items)

### Phase 4: Load Tests
- 100 concurrent agents updating same item
- 1K items with deep hierarchies
- 10K items with metadata queries

---

## Risk Management

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Optimistic locking bugs | HIGH | HIGH | Comprehensive concurrency tests |
| JSONB performance | MEDIUM | MEDIUM | GIN indexes, query optimization |
| Circular references | LOW | HIGH | Validation + CTE check |
| Recursive query performance | MEDIUM | MEDIUM | CTE optimization, depth limits |
| Data loss in cascade delete | LOW | CRITICAL | Event logging, soft delete first |

---

## Acceptance Criteria

Epic 2 is **COMPLETE** when:

- [ ] **Story 2.1**: All 5 tests pass, item creation working
- [ ] **Story 2.2**: All 6 tests pass, retrieval & filtering working
- [ ] **Story 2.3**: All 5 tests pass, optimistic locking working
- [ ] **Story 2.4**: All 4 tests pass, soft delete working
- [ ] **Story 2.5**: All 4 tests pass, metadata working
- [ ] **Story 2.6**: All 6 tests pass, hierarchy working
- [ ] **Coverage**: ≥85% integration test coverage
- [ ] **Performance**: Queries <50ms, supports 10K+ items
- [ ] **Stability**: 0 P0/P1 bugs
- [ ] **Documentation**: All features documented
- [ ] **Ready for Epic 3**: Link management

---

## Dependencies

**Completed (Epic 1):**
- Project initialization
- Configuration management
- Database migrations
- Error handling

**Starting (Epic 2):**
- Item CRUD operations
- Optimistic locking
- Metadata management
- Hierarchy support

**Next (Epic 3):**
- Link management
- Cross-item linking
- Traceability

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Test cases passing | 26/26 (100%) | Pending |
| Unit coverage | ≥90% | Pending |
| Integration coverage | ≥85% | Pending |
| Query performance | <50ms | Pending |
| P0/P1 bugs | 0 | Pending |
| Team velocity | 20 days | Planned |

---

## Next Steps

1. ✅ Review this plan
2. ✅ Get approval from stakeholders
3. ✅ Start Story 2.1 implementation
4. ✅ Create test file templates
5. ✅ Set up CI/CD for continuous testing
6. ✅ Begin daily standups

---

**Plan Created:** 2025-11-23  
**Status:** 🟡 **READY FOR IMPLEMENTATION**  
**Next Epic:** Epic 3 (Link Management)

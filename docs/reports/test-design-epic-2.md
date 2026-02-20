# Test Design: Epic 2 - Core Item Management

**Epic:** Epic 2 - Core Item Management  
**Stories:** 6 stories (2.1 - 2.6)  
**FRs Covered:** FR1-FR15 (Multi-View System + Item Management)  
**Test Architect:** Murat (TEA)  
**Date:** 2025-11-21  
**Status:** Ready for Implementation

---

## Executive Summary

**Epic Goal:** Enable users to create, read, update, and delete items across all views with full CRUD operations.

**Test Strategy:** Comprehensive CRUD testing with focus on optimistic locking, soft delete, and hierarchical relationships.

**Risk Assessment:** HIGH
- **Technical Risk**: Optimistic locking, concurrent updates, JSONB queries
- **Business Risk**: Core functionality - any bugs block all workflows
- **Priority**: P0 (Critical - foundation for all item operations)

**Test Coverage Target:**
- Unit Tests: 90%+ (repositories, validators, business logic)
- Integration Tests: 85%+ (database operations, CRUD)
- E2E Tests: 100% (critical CRUD workflows)

---

## Test Levels Strategy

### Unit Tests (tests/unit/)
**Purpose**: Test repositories and business logic in isolation  
**Coverage**: 90%+  
**Speed**: <100ms per test

**Focus Areas:**
- ItemRepository CRUD methods (mocked database)
- Optimistic locking logic
- Metadata validation (Pydantic)
- Hierarchy queries (parent-child)

### Integration Tests (tests/integration/)
**Purpose**: Test database operations with real database  
**Coverage**: 85%+  
**Speed**: <1s per test

**Focus Areas:**
- Item CRUD operations
- Optimistic locking with concurrent updates
- Soft delete and recovery
- JSONB metadata queries
- Hierarchical queries (recursive CTEs)

### E2E Tests (tests/e2e/)
**Purpose**: Test complete CRUD workflows via CLI  
**Coverage**: 100% of critical workflows  
**Speed**: <5s per test

**Focus Areas:**
- Create → Read → Update → Delete workflow
- Multi-view item creation
- Concurrent update scenarios
- Metadata filtering
- Hierarchy navigation

---

## Story-by-Story Test Plan

### Story 2.1: Item Creation with Type & View

**FRs**: FR1, FR6, FR7  
**Priority**: P0 (Critical)  
**Risk**: MEDIUM (foundation for all item operations)

#### Test Cases

**TC-2.1.1: Create Item with Type and View**
- **Type**: Integration
- **Given**: Project initialized
- **When**: User runs `rtm create feature "User Auth" --view FEATURE`
- **Then**: Item created with type=feature, view=FEATURE
- **And**: Auto-generated UUID assigned
- **And**: Default status=todo, version=1
- **Validation**: Item exists in database, event logged

**TC-2.1.2: Create Items in All 8 Views**
- **Type**: Integration
- **Given**: Project initialized
- **When**: User creates items in all 8 views (FEATURE, CODE, WIREFRAME, API, TEST, DATABASE, ROADMAP, PROGRESS)
- **Then**: All items created successfully
- **Validation**: 8 items exist, each with correct view

**TC-2.1.3: Item Creation with Metadata**
- **Type**: Integration
- **Given**: Project initialized
- **When**: User runs `rtm create feature "Auth" --metadata '{"priority": "high"}'`
- **Then**: Item created with metadata stored in JSONB
- **Validation**: Metadata queryable via JSONB operators

**TC-2.1.4: Invalid Item Type**
- **Type**: Unit (Negative)
- **Given**: User provides invalid item type
- **When**: `rtm create invalid_type "Title"`
- **Then**: Validation error with list of valid types
- **Validation**: No item created

**TC-2.1.5: Item Creation Event Logging**
- **Type**: Integration
- **Given**: Project initialized
- **When**: Item created
- **Then**: Creation event logged to events table
- **Validation**: Event contains item_id, agent_id, timestamp

#### Test Data
- Valid types: epic, feature, story, task, bug, file, endpoint, test, table, milestone
- Valid views: FEATURE, CODE, WIREFRAME, API, TEST, DATABASE, ROADMAP, PROGRESS
- Invalid types: "invalid", "", "123"

#### Dependencies
- Story 1.3 (Project initialization)

---

### Story 2.2: Item Retrieval & Display

**FRs**: FR2, FR8, FR23  
**Priority**: P0 (Critical)  
**Risk**: MEDIUM (performance critical for large datasets)

#### Test Cases

**TC-2.2.1: Retrieve Item by ID**
- **Type**: Integration
- **Given**: Item exists
- **When**: User runs `rtm show <item-id>`
- **Then**: Item details displayed (title, description, status, metadata, links)
- **Validation**: Query completes in <50ms

**TC-2.2.2: List Items by View**
- **Type**: Integration
- **Given**: 100 items across multiple views
- **When**: User runs `rtm view FEATURE`
- **Then**: Only FEATURE items displayed
- **Validation**: Correct filtering, pagination works

**TC-2.2.3: Filter Items by Status**
- **Type**: Integration
- **Given**: Items with various statuses
- **When**: User runs `rtm view FEATURE --status todo`
- **Then**: Only todo items displayed
- **Validation**: Correct filtering

**TC-2.2.4: Output Format (JSON, YAML, Table)**
- **Type**: E2E
- **Given**: Items exist
- **When**: User runs `rtm show <id> --format json`
- **Then**: Output in valid JSON format
- **Validation**: JSON parseable, contains all fields

**TC-2.2.5: Item Not Found**
- **Type**: Integration (Negative)
- **Given**: Item ID doesn't exist
- **When**: User runs `rtm show invalid-id`
- **Then**: NotFoundError with helpful message
- **Validation**: Suggests using `rtm view` to find items

**TC-2.2.6: Performance - Large Dataset**
- **Type**: Integration (Performance)
- **Given**: 10K items in database
- **When**: User runs `rtm show <item-id>`
- **Then**: Query completes in <50ms
- **Validation**: Index on id used

#### Test Data
- Small dataset: 10 items
- Medium dataset: 1K items
- Large dataset: 10K items
- Statuses: todo, in_progress, done, blocked

#### Dependencies
- Story 2.1 (Item creation)

---

### Story 2.3: Item Update with Optimistic Locking

**FRs**: FR9, FR36, FR54  
**Priority**: P0 (Critical)  
**Risk**: HIGH (concurrency bugs can cause data loss)

#### Test Cases

**TC-2.3.1: Update Item Status**
- **Type**: Integration
- **Given**: Item with version=1
- **When**: User runs `rtm update <id> --status in_progress`
- **Then**: Status updated, version incremented to 2
- **Validation**: Update event logged

**TC-2.3.2: Concurrent Update Conflict**
- **Type**: Integration
- **Given**: Two agents have same item (version=1)
- **When**: Agent A updates (version → 2), then Agent B tries to update (still version=1)
- **Then**: Agent B gets ConcurrencyError
- **Validation**: Agent B's update rejected, data integrity maintained

**TC-2.3.3: Force Update Override**
- **Type**: Integration
- **Given**: Concurrent update conflict
- **When**: User runs `rtm update <id> --status done --force`
- **Then**: Update succeeds, overriding version check
- **Validation**: Warning logged about forced update

**TC-2.3.4: Update Multiple Fields**
- **Type**: Integration
- **Given**: Item exists
- **When**: User runs `rtm update <id> --title "New Title" --description "New Desc" --status done`
- **Then**: All fields updated atomically
- **Validation**: Single version increment

**TC-2.3.5: Retry Logic**
- **Type**: Unit
- **Given**: Concurrent update conflict
- **When**: Retry with exponential backoff
- **Then**: Update succeeds after retry
- **Validation**: Max 3 retries, backoff: 100ms, 200ms, 400ms

#### Test Data
- Concurrent agents: 2, 10, 100
- Update fields: title, description, status, owner, metadata
- Retry scenarios: success on 1st retry, 2nd retry, failure after 3 retries

#### Dependencies
- Story 2.2 (Item retrieval)

---

### Story 2.4: Item Deletion with Soft Delete

**FRs**: FR10, FR54
**Priority**: P1 (High)
**Risk**: MEDIUM (data recovery critical)

#### Test Cases

**TC-2.4.1: Soft Delete Item**
- **Type**: Integration
- **Given**: Item exists
- **When**: User runs `rtm delete <item-id>`
- **Then**: Item soft-deleted (deleted_at timestamp set)
- **And**: Item not in default queries
- **Validation**: Item still in database, deleted_at set

**TC-2.4.2: View Deleted Items**
- **Type**: Integration
- **Given**: Soft-deleted items exist
- **When**: User runs `rtm view FEATURE --include-deleted`
- **Then**: Deleted items displayed with deleted_at timestamp
- **Validation**: Deleted items marked clearly

**TC-2.4.3: Permanent Delete**
- **Type**: Integration
- **Given**: Soft-deleted item exists
- **When**: User runs `rtm delete <item-id> --permanent`
- **Then**: Item permanently deleted from database
- **Validation**: Item no longer exists, cannot be recovered

**TC-2.4.4: Deletion Event Logging**
- **Type**: Integration
- **Given**: Item exists
- **When**: Item deleted (soft or permanent)
- **Then**: Deletion event logged
- **Validation**: Event contains item_id, deletion_type, agent_id

#### Test Data
- Deletion types: soft, permanent
- Item states: active, already soft-deleted

#### Dependencies
- Story 2.2 (Item retrieval)

---

### Story 2.5: Item Metadata & Custom Fields

**FRs**: FR11, FR60
**Priority**: P1 (High)
**Risk**: MEDIUM (JSONB query performance)

#### Test Cases

**TC-2.5.1: Add Metadata to Item**
- **Type**: Integration
- **Given**: Item exists
- **When**: User runs `rtm update <id> --metadata '{"priority": "high", "tags": ["auth"]}'`
- **Then**: Metadata stored in JSONB field
- **Validation**: Metadata queryable

**TC-2.5.2: Query by Metadata**
- **Type**: Integration
- **Given**: Items with various metadata
- **When**: User runs `rtm view FEATURE --filter 'metadata.priority=high'`
- **Then**: Only items with priority=high displayed
- **Validation**: JSONB query uses GIN index

**TC-2.5.3: Update Specific Metadata Key**
- **Type**: Integration
- **Given**: Item with metadata `{"priority": "low", "tags": ["auth"]}`
- **When**: User updates `--metadata-set priority=high`
- **Then**: Only priority updated, tags unchanged
- **Validation**: Partial metadata update works

**TC-2.5.4: Invalid JSON Metadata**
- **Type**: Unit (Negative)
- **Given**: User provides invalid JSON
- **When**: `rtm update <id> --metadata 'invalid json'`
- **Then**: Validation error with JSON syntax help
- **Validation**: No update applied

#### Test Data
- Valid metadata: `{"priority": "high"}`, `{"tags": ["auth", "security"]}`
- Invalid metadata: `invalid json`, `{unclosed`, `null`

#### Dependencies
- Story 2.3 (Item update)

---

### Story 2.6: Item Hierarchy (Parent-Child Relationships)

**FRs**: FR12, FR68
**Priority**: P1 (High)
**Risk**: HIGH (recursive queries, progress rollup complexity)

#### Test Cases

**TC-2.6.1: Create Child Item**
- **Type**: Integration
- **Given**: Epic exists
- **When**: User runs `rtm create feature "OAuth" --parent <epic-id>`
- **Then**: Feature created with parent_id set
- **Validation**: Parent-child relationship established

**TC-2.6.2: Query Children**
- **Type**: Integration
- **Given**: Epic with 3 child features
- **When**: User runs `rtm show <epic-id> --children`
- **Then**: All 3 children displayed
- **Validation**: Recursive query works

**TC-2.6.3: Query Ancestors**
- **Type**: Integration
- **Given**: Task → Story → Feature → Epic hierarchy
- **When**: User runs `rtm show <task-id> --ancestors`
- **Then**: Story, Feature, Epic displayed in order
- **Validation**: Recursive CTE query works

**TC-2.6.4: Progress Rollup**
- **Type**: Integration
- **Given**: Epic with 3 features (progress: 0%, 50%, 100%)
- **When**: Progress calculated
- **Then**: Epic progress = 50% (average of children)
- **Validation**: Rollup calculation correct

**TC-2.6.5: Cascade Soft Delete**
- **Type**: Integration
- **Given**: Epic with 3 child features
- **When**: User deletes epic
- **Then**: All children soft-deleted
- **Validation**: Cascade delete works

**TC-2.6.6: Circular Reference Prevention**
- **Type**: Unit (Negative)
- **Given**: Item A with parent B
- **When**: User tries to set B's parent to A
- **Then**: Validation error (circular reference)
- **Validation**: No circular references allowed

#### Test Data
- Hierarchy depths: 2 levels, 4 levels, 10 levels
- Children per parent: 1, 10, 100
- Progress values: 0%, 25%, 50%, 75%, 100%

#### Dependencies
- Story 2.1 (Item creation)

---

## Traceability Matrix

### FR → Story → Test Case Mapping

| FR ID | Requirement | Story | Test Cases | Status |
|-------|-------------|-------|------------|--------|
| FR1 | 8 core views | 2.1 | TC-2.1.2 | ✅ Mapped |
| FR2 | View items by view | 2.2 | TC-2.2.2 | ✅ Mapped |
| FR6 | Create items | 2.1 | TC-2.1.1, TC-2.1.2 | ✅ Mapped |
| FR7 | Item types | 2.1 | TC-2.1.1, TC-2.1.4 | ✅ Mapped |
| FR8 | View item details | 2.2 | TC-2.2.1 | ✅ Mapped |
| FR9 | Edit item properties | 2.3 | TC-2.3.1, TC-2.3.4 | ✅ Mapped |
| FR10 | Delete items | 2.4 | TC-2.4.1, TC-2.4.3 | ✅ Mapped |
| FR11 | Custom metadata | 2.5 | TC-2.5.1 | ✅ Mapped |
| FR12 | Hierarchical relationships | 2.6 | TC-2.6.1, TC-2.6.2 | ✅ Mapped |
| FR23 | CLI commands | 2.2 | TC-2.2.4 | ✅ Mapped |
| FR36 | Concurrent operations | 2.3 | TC-2.3.2 | ✅ Mapped |
| FR54 | Version tracking | 2.3, 2.4 | TC-2.3.1, TC-2.4.4 | ✅ Mapped |
| FR60 | Filter by metadata | 2.5 | TC-2.5.2 | ✅ Mapped |
| FR68 | Progress rollup | 2.6 | TC-2.6.4 | ✅ Mapped |

**Total FRs**: 14
**Total Stories**: 6
**Total Test Cases**: 26
**Coverage**: 100% (all FRs mapped to test cases)

---

## Test Execution Order

### Phase 1: Unit Tests (Fast Feedback)
1. TC-2.1.4: Invalid Item Type
2. TC-2.3.5: Retry Logic
3. TC-2.5.4: Invalid JSON Metadata
4. TC-2.6.6: Circular Reference Prevention

**Estimated Time**: 5 minutes
**Coverage Target**: 90%+

### Phase 2: Integration Tests (Database)
1. TC-2.1.1-2.1.3: Item Creation
2. TC-2.2.1-2.2.3: Item Retrieval
3. TC-2.3.1-2.3.4: Item Update
4. TC-2.4.1-2.4.4: Item Deletion
5. TC-2.5.1-2.5.3: Metadata
6. TC-2.6.1-2.6.5: Hierarchy

**Estimated Time**: 20 minutes
**Coverage Target**: 85%+

### Phase 3: E2E Tests (Critical Workflows)
1. TC-2.2.4: Output Formats
2. TC-2.2.6: Performance Test

**Estimated Time**: 5 minutes
**Coverage Target**: 100% of critical workflows

**Total Estimated Time**: 30 minutes

---

## Risk Assessment

| Risk Category | Probability | Impact | Score | Mitigation |
|---------------|-------------|--------|-------|------------|
| Optimistic locking failures | HIGH | HIGH | 9 | TC-2.3.2, TC-2.3.5, retry logic, comprehensive testing |
| JSONB query performance | MEDIUM | HIGH | 6 | TC-2.5.2, GIN indexes, query optimization |
| Recursive query performance | MEDIUM | MEDIUM | 4 | TC-2.6.2-2.6.3, CTE optimization, depth limits |
| Data loss from concurrent updates | LOW | CRITICAL | 6 | TC-2.3.2, optimistic locking, event logging |
| Circular reference bugs | LOW | MEDIUM | 2 | TC-2.6.6, validation logic |

**Overall Epic Risk**: HIGH (Score: 5.4)

---

## Success Criteria

**Epic 2 is complete when:**

1. ✅ All 26 test cases pass (100%)
2. ✅ Unit test coverage ≥90%
3. ✅ Integration test coverage ≥85%
4. ✅ E2E test coverage = 100% of critical workflows
5. ✅ All FRs (FR1-FR15) validated by tests
6. ✅ No P0/P1 bugs remaining
7. ✅ Performance targets met (<50ms simple queries)
8. ✅ Optimistic locking working correctly
9. ✅ JSONB queries using GIN indexes
10. ✅ Recursive queries optimized

---

**Test Design Complete**: 2025-11-21
**Test Architect**: Murat (TEA)
**Status**: ✅ **READY FOR IMPLEMENTATION**
**Next Epic**: Epic 3 (Link Management)



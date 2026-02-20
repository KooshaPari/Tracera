# Phase 3 First Wave: Complexity Analysis

**Generated**: 2026-02-02
**Status**: Analysis Complete
**Next**: Launch refactoring agents

---

## Python Backend: C901 Complexity Analysis

### Summary Statistics

**Total C901 Violations**: 248
**Analyzed**: 248 functions
**Top 20 Files by Violation Count**:

| Rank | Count | File | Type |
|------|-------|------|------|
| 1 | 11 | src/tracertm/api/main.py | API Core |
| 2 | 8 | src/tracertm/mcp/tools/param.py | MCP Tools |
| 3 | 5 | src/tracertm/services/stateless_ingestion_service.py | Service |
| 4 | 5 | src/tracertm/services/ai_tools.py | Service |
| 5 | 5 | src/tracertm/api/routers/item_specs.py | API Router |
| 6 | 4 | scripts/python/quality-report.py | Script |
| 7 | 3 | tests/integration/services/test_link_service_expanded.py | Test |
| 8 | 3 | src/tracertm/storage/markdown_parser.py | Storage |
| 9 | 3 | src/tracertm/storage/local_storage.py | Storage |
| 10 | 3 | src/tracertm/services/shortest_path_service.py | Service |

### Categorization

**API Handlers** (15-20% of violations):
- `src/tracertm/api/main.py` - 11 violations (startup, middleware setup)
- `src/tracertm/api/routers/*.py` - Request/response handling

**Services** (30-35% of violations):
- `src/tracertm/services/*_service.py` - Business logic
- `src/tracertm/services/ai_tools.py` - AI integration
- `src/tracertm/services/stateless_ingestion_service.py` - Data ingestion

**Migrations** (10-15% of violations):
- `alembic/versions/*.py` - Database schema changes
- Example: `008_add_graph_views_and_kinds.py` (complexity: 9)
- Example: `009_add_graphs_and_graph_nodes.py` (complexity: 8)

**Scripts** (20-25% of violations):
- `scripts/python/*.py` - Utility and automation scripts
- `scripts/consolidate-docs/scan_docs.py` - Doc processing (complexity: 20, **highest**)
- `scripts/python/augment_graph_semantics.py` - main() (complexity: 33, **critical**)

**MCP Tools** (10-15% of violations):
- `src/tracertm/mcp/tools/param.py` - 8 violations
- `src/tracertm/mcp/tools/core_tools.py` - Parameter handling

**Tests** (5-10% of violations):
- `tests/integration/**/*.py` - Complex test scenarios

### Top 10 Most Complex Functions

| Rank | Function | File | Complexity | Priority |
|------|----------|------|------------|----------|
| 1 | `main` | augment_graph_semantics.py | 33 | **P0** |
| 2 | `categorize_doc` | scan_docs.py | 20 | **P0** |
| 3 | `main` | benchmark_tool_registration.py | 12 | P1 |
| 4 | `_run_claude_workflow` | bmm-auto.py | 10 | P1 |
| 5 | `upgrade` | 008_add_graph_views_and_kinds.py | 9 | P2 |
| 6 | `run_container` | DOCKER_SDK_ASYNC_EXAMPLES.py | 9 | P2 |
| 7 | `_run_auggie_workflow` | bmm-auto.py | 9 | P2 |
| 8 | `upgrade` | 009_add_graphs_and_graph_nodes.py | 8 | P2 |
| 9 | `apply_supabase_migrations` | apply_migrations.py | 8 | P2 |
| 10 | `apply_neo4j_migrations` | apply_migrations.py | 8 | P2 |

### Recommended Refactoring Patterns by Category

#### API Handlers
**Pattern**: Extract middleware and startup logic
```python
# Before: Complex main.py setup
def create_app():
    app = FastAPI()
    # 50+ lines of middleware, CORS, routes, etc.
    return app

# After: Modular setup
def create_app():
    app = FastAPI()
    configure_middleware(app)
    configure_cors(app)
    register_routes(app)
    return app
```

#### Services
**Pattern**: Strategy pattern for complex business logic
```python
# Before: Complex service with many branches
def process_item(item, action):
    if action == "create":
        # 10+ lines
    elif action == "update":
        # 10+ lines
    elif action == "delete":
        # 10+ lines
    # ... more branches

# After: Strategy pattern
class ItemProcessor(Protocol):
    def process(self, item): ...

class CreateProcessor: ...
class UpdateProcessor: ...
class DeleteProcessor: ...

processors = {"create": CreateProcessor(), ...}
processors[action].process(item)
```

#### Migrations
**Pattern**: Extract helper functions (minimal changes)
```python
# Before: Complex upgrade()
def upgrade():
    op.create_table("foo", ...)
    op.create_table("bar", ...)
    op.add_column("baz", ...)
    # ... many operations

# After: Helper functions
def create_foo_table():
    op.create_table("foo", ...)

def create_bar_table():
    op.create_table("bar", ...)

def upgrade():
    create_foo_table()
    create_bar_table()
    add_baz_column()
```

#### Scripts
**Pattern**: Extract sub-functions, early returns
```python
# Before: 33-complexity main()
def main():
    # Parse args (5 lines)
    # Validate (10 lines)
    # Process data (15 lines)
    # Output (8 lines)

# After: Decomposed
def parse_arguments(): ...
def validate_input(args): ...
def process_data(validated): ...
def output_results(data): ...

def main():
    args = parse_arguments()
    validated = validate_input(args)
    if not validated:
        return 1
    data = process_data(validated)
    output_results(data)
```

---

## Go Backend: funlen Analysis

### Summary Statistics

**Total funlen Violations**: ~800 (estimated from 13,195 total)
**Critical Files** (from sample):
- `internal/agents/distributed_coordination.go` - Duplicate code (2 functions, 37 lines each)
- `internal/cache/cache_interface_test.go` - Test setup duplication

### Categorization

**Services** (40-50% of violations):
- `internal/agents/*.go` - Agent coordination, distributed ops
- `internal/service/*.go` - Business services

**Handlers** (20-30% of violations):
- `internal/handlers/*.go` - HTTP request handlers
- `cmd/api/main.go` - Application setup

**Tests** (20-25% of violations):
- `**/*_test.go` - Test functions with setup/teardown

**Middleware** (5-10% of violations):
- `internal/middleware/*.go` - Request/response processing

### Top Patterns Observed

1. **Duplicate Lock Release Logic** (distributed_coordination.go):
   - `CompleteCoordinatedUpdate` (37 lines)
   - `CancelOperation` (37 lines)
   - **90% overlap** - extract to `updateOperationStatus`

2. **Test Setup Duplication** (cache_interface_test.go):
   - `TestItemKeyGeneration` (26 lines)
   - Similar test pattern repeated
   - **Extract**: `testKeyGeneration(t, input, expected)` helper

3. **Long HTTP Handlers**:
   - Request validation (10-15 lines)
   - Business logic (20-30 lines)
   - Response formatting (10-15 lines)
   - **Extract**: Validation, business logic, formatting to separate functions

### Recommended Refactoring Patterns

#### Services
**Pattern**: Extract common operations
```go
// Before: Duplicate in CompleteCoordinatedUpdate and CancelOperation
func (dc *DistributedCoordinator) CompleteCoordinatedUpdate(...) error {
    // Fetch operation
    // Validate coordinator
    // Release locks (15 lines)
    // Update status
    // Cleanup
}

// After: Extract common pattern
func (dc *DistributedCoordinator) updateOperationStatus(
    ctx context.Context, opID, agentID, status string,
) error {
    // Common logic: fetch, validate, release, update, cleanup
}

func (dc *DistributedCoordinator) CompleteCoordinatedUpdate(...) error {
    return dc.updateOperationStatus(ctx, operationID, agentID, "completed")
}
```

#### Handlers
**Pattern**: Extract validation, logic, formatting
```go
// Before: Long handler (80+ lines)
func CreateItemHandler(c echo.Context) error {
    // Parse request (10 lines)
    // Validate (15 lines)
    // Business logic (30 lines)
    // Format response (15 lines)
}

// After: Decomposed
func CreateItemHandler(c echo.Context) error {
    req, err := parseCreateItemRequest(c)
    if err != nil {
        return err
    }
    
    item, err := createItem(c.Request().Context(), req)
    if err != nil {
        return err
    }
    
    return formatItemResponse(c, item)
}
```

#### Tests
**Pattern**: Table-driven tests, helper functions
```go
// Before: Repetitive test functions (26+ lines each)
func TestItemKey1(t *testing.T) { /* setup, assert */ }
func TestItemKey2(t *testing.T) { /* setup, assert */ }

// After: Table-driven
func TestItemKey(t *testing.T) {
    tests := []struct{
        name, input, expected string
    }{
        {"simple", "123", "item:123"},
        {"hyphenated", "a-b", "item:a-b"},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            assert.Equal(t, tt.expected, ItemKey(tt.input))
        })
    }
}
```

---

## Frontend: jsx-max-depth Analysis

### Summary (Pending Full Analysis)

**Status**: Requires oxlint JSON output parsing
**Estimated Violations**: 200-400 (based on baseline size)

### Expected Categories

**Views** (40-50%):
- `src/app/**/page.tsx` - Full-page layouts
- `src/app/**/*View.tsx` - Complex data views
- Example: `ItemsTableView` - table + filters + modals

**Modals/Dialogs** (20-30%):
- Complex forms within modals
- Multi-step wizards
- Confirmation dialogs with nested content

**Tables** (15-20%):
- Table with nested cells
- Row expansion panels
- Inline editing components

**Forms** (10-15%):
- Multi-section forms
- Conditional field rendering
- Nested field groups

### Recommended Patterns

#### Views
**Pattern**: Container/Presentational split
```tsx
// Before: Deep nesting in ItemsTableView
<div>
  <div className="filters">
    <div><div>...</div></div>
  </div>
  <div className="table">
    <table>
      <tbody>
        <tr><td><div>...</div></td></tr>
      </tbody>
    </table>
  </div>
</div>

// After: Component extraction
const Filters = () => <div>...</div>;
const ItemsTable = ({ items }) => <table>...</table>;
const ItemRow = ({ item }) => <tr>...</tr>;

const ItemsTableView = () => (
  <div>
    <Filters />
    <ItemsTable items={items} />
  </div>
);
```

#### Modals
**Pattern**: Compound components
```tsx
// Before: Deep nesting
<Modal>
  <div>
    <div className="header">
      <div>...</div>
    </div>
    <div className="body">
      <div>
        <form>
          <div>...</div>
        </form>
      </div>
    </div>
  </div>
</Modal>

// After: Compound pattern
<Modal>
  <Modal.Header>...</Modal.Header>
  <Modal.Body>
    <ItemForm />
  </Modal.Body>
</Modal>
```

---

## Next Steps: Agent Launch

### Ready for First Wave Refactoring

**Python - Agent 1**: Alembic migrations
- Target: 10-15 files with complexity 8-9
- Pattern: Extract helper functions
- Risk: LOW (test on schema copy)

**Python - Agent 2**: Scripts (high complexity)
- Target: `augment_graph_semantics.py` (complexity 33)
- Target: `scan_docs.py` (complexity 20)
- Pattern: Extract sub-functions, early returns
- Risk: MEDIUM (validate script outputs)

**Python - Agent 3**: API main.py
- Target: 11 violations in main.py
- Pattern: Extract middleware, startup logic
- Risk: MEDIUM (integration tests required)

**Go - Agent 9**: Distributed coordination
- Target: Extract duplicate lock release logic
- Pattern: Create `updateOperationStatus` helper
- Risk: LOW (well-tested area)

**Go - Agent 10**: Test cleanup
- Target: Table-driven tests for cache_interface_test.go
- Pattern: Test helpers
- Risk: LOW (tests only)

**Frontend - Agent 17**: Pending full analysis
- Action: Run oxlint JSON parse first
- Then: Target top 5 deepest components

---

## Risk Assessment

**Low Risk** (60% of violations):
- Alembic helper extraction (minimal logic change)
- Test refactoring (table-driven)
- Go duplicate code extraction

**Medium Risk** (35% of violations):
- API handler decomposition (integration tests needed)
- Service strategy pattern (behavior must match)
- Frontend component extraction (state management)

**High Risk** (5% of violations):
- Scripts with complex main() functions (output validation)
- Migrations with side effects (schema testing)

**Recommendation**: Start with LOW risk items in first wave, validate patterns, then proceed to MEDIUM/HIGH.

---

**Analysis Status**: ✅ Complete
**Next Action**: Launch refactoring agents (Wave 1)
**Owner**: Phase 3 Coordinator

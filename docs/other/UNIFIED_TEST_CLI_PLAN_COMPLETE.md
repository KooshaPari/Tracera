# Unified Test CLI & Test Suite Completion Plan (Complete)

## Executive Summary

**Goal**: Create a unified `rtm test` command that aggregates and manages all tests across the polyglot codebase (Python, Go, TypeScript) with domain/functional/user story groupings, dependency-aware staging, and traceability matrix reporting.

**Reference Implementation**: Based on atoms-mcp-prod CLI patterns (test environment management, orchestrator, dependency registry)

**Current State**:
- **Python**: ~3,149 tests (pytest) across unit/component/integration/e2e
- **Go**: ~30+ test files (go test) in backend/
- **TypeScript**: E2E tests (Playwright) in tests/e2e/
- **CLI**: Typer-based CLI already exists (`rtm`)

**Target State**:
- Unified `rtm test` command with comprehensive subcommands
- Cross-language test discovery and execution
- Dependency-aware test staging (like atoms-mcp-prod)
- Environment management (local/dev/prod)
- Domain/functional/user story grouping
- Traceability matrix reporting
- Coverage aggregation across languages
- Parallel execution by default
- Test result visualization

---

## Part 1: Test Suite Completion Plan

### 1.1 Python Test Suite (Current: ~3,149 tests → Target: ~3,649 tests)

#### Gaps to Address:

1. **CLI Command Tests** (Priority: High) - **+200 tests**
   - Complete coverage for all 30+ CLI commands
   - Test error handling, edge cases, validation
   - Test command aliases and shortcuts
   - Test help system and completion
   - Test performance optimizations

2. **Backend Integration Tests** (Priority: High) - **+150 tests**
   - API endpoint tests (currently minimal)
   - Database transaction tests
   - Service integration tests
   - Cross-service communication tests

3. **Edge Cases & Error Handling** (Priority: Medium) - **+100 tests**
   - Concurrency edge cases
   - File system error scenarios
   - Network failure handling
   - Database connection failures
   - Invalid input handling

4. **Performance & Load Tests** (Priority: Medium) - **+50 tests**
   - Large dataset handling
   - Concurrent operations
   - Memory leak detection
   - Query performance benchmarks

**Python Test Completion Target**: +500 tests → **~3,649 total**

### 1.2 Go Backend Test Suite (Current: ~30 test files → Target: ~145 test files)

#### Gaps to Address:

1. **Handler Tests** (Priority: High) - **+50 test files**
   - Complete HTTP handler coverage
   - Request/response validation
   - Error response handling
   - Middleware testing
   - Authentication/authorization handlers

2. **Service Layer Tests** (Priority: High) - **+30 test files**
   - Business logic coverage
   - Transaction handling
   - Service integration
   - Error propagation
   - Retry logic

3. **Repository Tests** (Priority: Medium) - **+20 test files**
   - Database query tests
   - CRUD operations
   - Query optimization
   - Connection pooling
   - Transaction isolation

4. **Security Tests** (Priority: High) - **+15 test files**
   - Authentication/authorization
   - Input validation
   - SQL injection prevention
   - XSS prevention
   - Rate limiting

**Go Test Completion Target**: +115 test files → **~145 total**

### 1.3 TypeScript E2E Test Suite (Current: ~20+ spec files → Target: ~60 spec files)

#### Gaps to Address:

1. **User Journey Tests** (Priority: High) - **+30 spec files**
   - Complete all 12 journey specs
   - Cross-browser testing (Chrome, Firefox, Safari)
   - Mobile/tablet scenarios
   - Accessibility testing
   - Performance testing

2. **Workflow Tests** (Priority: Medium) - **+10 spec files**
   - Complete workflow coverage
   - Error recovery scenarios
   - Offline/online transitions
   - Multi-user scenarios

**TypeScript E2E Completion Target**: +40 spec files → **~60 total**

---

## Part 2: Unified Test CLI Architecture (Based on atoms-mcp-prod Patterns)

### 2.1 Command Structure (Complete)

```python
# Main test command with comprehensive options
rtm test [OPTIONS]                    # Run all tests with smart defaults
rtm test --scope unit                 # Unit tests only
rtm test --scope integration           # Integration tests only
rtm test --scope e2e                  # E2E tests only
rtm test --scope all                  # All tests without marker filtering

# Language-specific commands
rtm test python                       # Run Python tests only
rtm test go                           # Run Go tests only
rtm test e2e                          # Run TypeScript E2E tests only

# Specialized test commands (like atoms-mcp-prod)
rtm test:unit                         # Unit tests (fast, local)
rtm test:int                          # Integration tests (dev by default)
rtm test:e2e                          # E2E tests (dev by default)
rtm test:cov                          # Coverage report
rtm test:matrix                       # Traceability matrix
rtm test:comprehensive                # Comprehensive test suite
rtm test:story                        # Story-based tests
rtm test:epic                         # Epic-based tests

# Filtering and organization
rtm test --domain services            # Filter by domain
rtm test --epic "Epic 1"              # Filter by epic
rtm test --story "User can create"    # Filter by user story
rtm test --function crud              # Filter by function
rtm test --marker slow                # Filter by pytest marker
rtm test --keyword "item"              # Filter by keyword

# Execution options
rtm test --parallel                   # Dependency-ordered stages (like atoms)
rtm test --no-parallel                # Disable parallelization
rtm test --max-workers 4              # Override worker count
rtm test --env local                  # Environment: local/dev/prod
rtm test --verbose                    # Verbose output
rtm test --coverage                   # Generate coverage
rtm test --watch                      # Watch mode for TDD
rtm test --lf                         # Last failed only
rtm test --ff                         # Failed first

# Discovery and listing
rtm test list                         # List all tests
rtm test list --domain services       # List tests by domain
rtm test list --epic "Epic 1"         # List tests by epic
```

### 2.2 Test Environment Management (Like atoms-mcp-prod)

```python
# src/tracertm/cli/commands/test/env_manager.py

class TestEnvironment(Enum):
    """Supported test environments."""
    LOCAL = "local"      # Local development (localhost)
    DEV = "dev"          # Development deployment
    PROD = "prod"        # Production deployment

class TestEnvManager:
    """Manages test environment configuration (inspired by atoms-mcp-prod)."""
    
    CONFIGS = {
        TestEnvironment.LOCAL: {
            "name": "Local Development",
            "api_url": "http://localhost:8000",
            "db_url": "sqlite+aiosqlite:///:memory:",
            "timeout": 10,
            "description": "Local development with local services",
        },
        TestEnvironment.DEV: {
            "name": "Development",
            "api_url": "https://dev.tracertm.example.com",
            "db_url": os.getenv("DEV_DATABASE_URL"),
            "timeout": 30,
            "description": "Development deployment",
        },
        TestEnvironment.PROD: {
            "name": "Production",
            "api_url": "https://tracertm.example.com",
            "db_url": os.getenv("PROD_DATABASE_URL"),
            "timeout": 60,
            "description": "Production deployment",
        },
    }
    
    @classmethod
    def get_environment_for_scope(cls, scope: str) -> TestEnvironment:
        """Auto-detect environment based on test scope."""
        if scope == "unit":
            return TestEnvironment.LOCAL
        elif scope in ["integration", "e2e"]:
            return TestEnvironment.DEV  # Default to dev
        return TestEnvironment.LOCAL
    
    @classmethod
    def setup_environment(cls, environment: TestEnvironment) -> None:
        """Set up environment variables for testing."""
        config = cls.get_config(environment)
        os.environ["TRACERTM_API_URL"] = config["api_url"]
        os.environ["TRACERTM_DB_URL"] = config["db_url"]
        os.environ["TRACERTM_TIMEOUT"] = str(config["timeout"])
```

### 2.3 Test Orchestrator (Dependency-Aware Staging)

```python
# src/tracertm/cli/commands/test/orchestrator.py

class TestOrchestrator:
    """Runs tests in dependency-aware stages (inspired by atoms-mcp-prod)."""
    
    def build_stage_plan(self) -> List[TestStage]:
        """Build ordered stage definitions covering the full suite."""
        return [
            TestStage(
                name="foundation",
                display_name="Foundation",
                description="Core models, storage, basic operations",
                paths=["tests/unit/core/**", "tests/unit/models/**"],
                depends_on=[],
            ),
            TestStage(
                name="repositories",
                display_name="Repositories",
                description="Database repositories and queries",
                paths=["tests/unit/repositories/**"],
                depends_on=["foundation"],
            ),
            TestStage(
                name="services",
                display_name="Services",
                description="Business logic services",
                paths=["tests/unit/services/**", "tests/component/services/**"],
                depends_on=["repositories"],
            ),
            TestStage(
                name="api",
                display_name="API",
                description="HTTP handlers and endpoints",
                paths=["tests/unit/api/**", "tests/component/api/**"],
                depends_on=["services"],
            ),
            TestStage(
                name="cli",
                display_name="CLI",
                description="CLI commands and user interface",
                paths=["tests/unit/cli/**", "tests/e2e/test_cli_*.py"],
                depends_on=["api"],
            ),
            TestStage(
                name="integration",
                display_name="Integration",
                description="Cross-service integration tests",
                paths=["tests/integration/**"],
                depends_on=["cli"],
            ),
            TestStage(
                name="e2e",
                display_name="End-to-End",
                description="Full workflow coverage",
                paths=["tests/e2e/**"],
                depends_on=["integration"],
            ),
            TestStage(
                name="performance",
                display_name="Performance",
                description="Performance and load tests",
                paths=["tests/performance/**"],
                depends_on=["e2e"],
            ),
        ]
```

### 2.4 Test Dependencies Registry

```python
# src/tracertm/cli/commands/test/dependencies.py

class TestDependencies:
    """Central registry of test dependencies (inspired by atoms-mcp-prod)."""
    
    FOUNDATION = {
        "test_storage_initialized": {
            "layer": "unit",
            "file": "tests/unit/storage/test_local_storage.py",
            "order": 1,
            "description": "Storage must initialize",
            "depends_on": [],
        },
        "test_database_connection": {
            "layer": "unit",
            "file": "tests/unit/database/test_connection.py",
            "order": 2,
            "description": "Database must be accessible",
            "depends_on": ["test_storage_initialized"],
        },
    }
    
    SERVICES = {
        "test_item_service_crud": {
            "layer": "unit",
            "file": "tests/unit/services/test_item_service.py",
            "depends_on": ["test_database_connection"],
            "description": "Item service CRUD operations",
        },
        # ... more service dependencies
    }
    
    # ... more dependency layers
```

### 2.5 Test Discovery & Metadata

```python
# Enhanced discovery with metadata extraction

class TestMetadata:
    """Metadata for a single test."""
    name: str
    language: str  # "python", "go", "typescript"
    file_path: Path
    domain: List[str]
    function: List[str]
    user_story: Optional[str]
    epic: Optional[str]
    markers: List[str]  # pytest markers, go build tags
    dependencies: List[str]
    coverage_target: Optional[str]
    scope: str  # "unit", "integration", "e2e"
    environment: str  # "local", "dev", "prod"
```

---

## Part 3: Implementation Details

### 3.1 File Structure

```
src/tracertm/cli/commands/test/
├── __init__.py
├── app.py                    # Main Typer app
├── discover.py               # Test discovery across languages
├── execute.py                # Test execution with parallelization
├── filter.py                 # Domain/functional/user story filtering
├── report.py                 # Coverage and result reporting
├── matrix.py                 # Traceability matrix generation
├── visualize.py              # Rich-based visualization
├── metadata.py               # Test metadata schema
├── env_manager.py            # Environment management (like atoms)
├── orchestrator.py           # Dependency-aware staging (like atoms)
├── dependencies.py           # Test dependencies registry (like atoms)
└── utils.py                  # Utility functions
```

### 3.2 Test Markers & Organization

```python
# pytest.ini / pyproject.toml markers
markers = [
    "unit: Unit tests (fast, no external dependencies)",
    "integration: Integration tests (database, file system)",
    "e2e: End-to-end tests (full CLI workflows)",
    "cli: CLI command tests",
    "slow: Slow tests (>1s execution time)",
    "agent: Agent coordination tests",
    "asyncio: Async tests",
    "performance: Performance and load tests",
    "property: Property-based tests using Hypothesis",
    "benchmark: Benchmark tests",
    "smoke: Minimal critical-path checks",
    # New markers for traceability
    "story: User story tests",
    "epic: Epic-level tests",
    "domain:core: Core domain tests",
    "domain:services: Services domain tests",
    "domain:api: API domain tests",
    "domain:cli: CLI domain tests",
    "function:crud: CRUD operation tests",
    "function:query: Query/search tests",
    "function:sync: Sync operation tests",
]
```

### 3.3 Test Execution Flow

```python
# Execution flow (inspired by atoms-mcp-prod)

1. Environment Detection
   - Auto-detect based on scope (unit → local, integration/e2e → dev)
   - Allow override with --env flag
   - Set up environment variables

2. Test Discovery
   - Discover Python tests (pytest --collect-only)
   - Discover Go tests (go test -list)
   - Discover TypeScript tests (playwright test --list)
   - Extract metadata (domain, function, story, epic)

3. Test Filtering
   - Apply domain/function/story/epic filters
   - Apply marker/keyword filters
   - Apply scope filters

4. Dependency Resolution
   - Build dependency graph
   - Order tests by dependencies
   - Create execution stages

5. Test Execution
   - Run stages sequentially (if dependencies)
   - Run tests in parallel within stages (pytest-xdist)
   - Aggregate results across languages

6. Reporting
   - Generate coverage reports
   - Generate traceability matrix
   - Visualize results with Rich
```

---

## Part 4: Complete Implementation Plan

### Phase 1: Core Infrastructure (Week 1-2)

**Week 1: Foundation**
- [ ] Create `test.py` command module structure
- [ ] Implement `TestEnvManager` (like atoms-mcp-prod)
- [ ] Implement basic test discovery for Python
- [ ] Implement basic test discovery for Go
- [ ] Implement basic test discovery for TypeScript
- [ ] Basic test execution (sequential)

**Week 2: Parallelization**
- [ ] Integrate pytest-xdist for Python
- [ ] Implement parallel Go test execution
- [ ] Implement parallel TypeScript test execution
- [ ] Result aggregation across languages
- [ ] Basic error handling

### Phase 2: Filtering & Grouping (Week 3-4)

**Week 3: Domain & Function Grouping**
- [ ] Implement domain-based filtering
- [ ] Implement functional grouping
- [ ] Test metadata extraction (markers, tags)
- [ ] Domain mapping configuration
- [ ] Function mapping configuration

**Week 4: Story & Epic Mapping**
- [ ] Implement user story mapping
- [ ] Implement epic mapping
- [ ] Test dependency registry (like atoms)
- [ ] Story/epic metadata extraction
- [ ] Test organization by traceability

### Phase 3: Orchestration & Staging (Week 5-6)

**Week 5: Dependency-Aware Staging**
- [ ] Implement `TestOrchestrator` (like atoms)
- [ ] Build dependency graph
- [ ] Create execution stages
- [ ] Implement stage execution
- [ ] Handle stage failures gracefully

**Week 6: Advanced Execution**
- [ ] Implement `--parallel` mode (dependency-ordered stages)
- [ ] Implement `--no-parallel` mode
- [ ] Worker count management
- [ ] Test retry logic
- [ ] Flaky test detection

### Phase 4: Reporting & Visualization (Week 7-8)

**Week 7: Coverage & Matrix**
- [ ] Coverage aggregation across languages
- [ ] Generate traceability matrix
- [ ] Link tests to requirements
- [ ] Coverage visualization
- [ ] Matrix export (JSON/XML/HTML)

**Week 8: Visualization & Advanced Features**
- [ ] Rich console output (tables, trees, progress)
- [ ] HTML report generation
- [ ] Test result dashboard
- [ ] Watch mode for TDD
- [ ] Test profiling

---

## Part 5: Reference Implementation Patterns (atoms-mcp-prod)

### 5.1 Environment Management Pattern

```python
# Pattern from atoms-mcp-prod/test_env_manager.py

class TestEnvManager:
    """Manages test environment configuration."""
    
    @classmethod
    def setup_environment(cls, environment: TestEnvironment) -> None:
        """Set up environment variables for testing."""
        config = cls.get_config(environment)
        os.environ["MCP_BASE_URL"] = config["mcp_base_url"]
        os.environ["MCP_TIMEOUT"] = str(config["timeout"])
        # ... more env vars
    
    @classmethod
    def get_environment_for_scope(cls, scope: str) -> TestEnvironment:
        """Auto-detect environment based on test scope."""
        if scope == "unit":
            return TestEnvironment.LOCAL
        elif scope in ["integration", "e2e"]:
            return TestEnvironment.DEV
        return TestEnvironment.LOCAL
```

### 5.2 Orchestrator Pattern

```python
# Pattern from atoms-mcp-prod/test_orchestrator.py

class TestOrchestrator:
    """Runs pytest suites in dependency-aware stages."""
    
    def run(self) -> TestRunSummary:
        """Execute all stages sequentially until one fails."""
        stages = self.build_stage_plan()
        stage_results = []
        
        for stage in stages:
            # Check dependencies
            blocking = failed_stages.intersection(stage.depends_on)
            if blocking:
                # Skip stage if dependency failed
                continue
            
            # Run stage
            result = self._run_stage(stage)
            stage_results.append(result)
            
            if result.status == "failed":
                failed_stages.add(stage.name)
        
        return TestRunSummary(success=not failed_stages, stage_results=stage_results)
```

### 5.3 Test Command Pattern

```python
# Pattern from atoms-mcp-prod/cli.py

@app.command()
def test(
    scope: Optional[str] = typer.Option(None, "--scope"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    coverage: bool = typer.Option(False, "--cov"),
    marker: Optional[str] = typer.Option(None, "-m", "--marker"),
    keyword: Optional[str] = typer.Option(None, "-k", "--keyword"),
    env: Optional[str] = typer.Option(None, "--env"),
    parallel: bool = typer.Option(False, "--parallel"),
    no_parallel: bool = typer.Option(False, "--no-parallel"),
    max_workers: Optional[int] = typer.Option(None, "--max-workers"),
    last_failed: bool = typer.Option(False, "--lf", "--last-failed"),
    failed_first: bool = typer.Option(False, "--ff", "--failed-first"),
) -> None:
    """Run the test suite with automatic environment targeting."""
    # Determine environment
    if env:
        environment = TestEnvironment.from_string(env)
    else:
        environment = TestEnvManager.get_environment_for_scope(scope or "unit")
    
    # Set up environment
    TestEnvManager.setup_environment(environment)
    TestEnvManager.print_environment_info(environment)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Enable parallelization by default (unless --no-parallel)
    if not no_parallel:
        worker_count = str(max_workers) if max_workers else "auto"
        cmd.extend(["-n", worker_count])
    
    # Add markers, keywords, etc.
    if marker:
        cmd.extend(["-m", marker])
    elif scope:
        cmd.extend(["-m", scope])
    
    if keyword:
        cmd.extend(["-k", keyword])
    
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    if verbose:
        cmd.append("-v")
    
    if last_failed:
        cmd.append("--lf")
    elif failed_first:
        cmd.append("--ff")
    
    cmd.append("tests/")
    
    # Execute
    result = subprocess.run(cmd, env=os.environ.copy())
    sys.exit(result.returncode)
```

---

## Part 6: Complete Command Reference

### 6.1 Main Test Command

```bash
# Basic usage
rtm test                          # Run all tests (unit + integration + e2e, local, parallel)
rtm test --scope unit             # Unit tests only (local, parallel)
rtm test --scope integration       # Integration tests (dev, parallel)
rtm test --scope e2e              # E2E tests (dev, parallel)
rtm test --scope all              # All tests without marker filtering

# Language-specific
rtm test python                   # Python tests only
rtm test go                       # Go tests only
rtm test e2e                      # TypeScript E2E tests only

# Filtering
rtm test --domain services        # Filter by domain
rtm test --epic "Epic 1"          # Filter by epic
rtm test --story "User can create" # Filter by user story
rtm test --function crud          # Filter by function
rtm test --marker slow            # Filter by pytest marker
rtm test --keyword "item"         # Filter by keyword

# Execution options
rtm test --parallel               # Dependency-ordered stages
rtm test --no-parallel            # Disable parallelization
rtm test --max-workers 4         # Override worker count
rtm test --env local              # Environment: local/dev/prod
rtm test --verbose                # Verbose output
rtm test --coverage               # Generate coverage
rtm test --lf                     # Last failed only
rtm test --ff                     # Failed first
rtm test --cache-clear            # Clear pytest cache

# Discovery
rtm test list                     # List all tests
rtm test list --domain services   # List by domain
rtm test list --epic "Epic 1"     # List by epic
```

### 6.2 Specialized Commands

```bash
# Quick commands (like atoms-mcp-prod)
rtm test:unit                     # Unit tests (local, parallel)
rtm test:unit -v                  # Verbose
rtm test:unit --no-parallel       # Disable parallel

rtm test:int                      # Integration tests (dev, parallel)
rtm test:int --env local          # Override to local
rtm test:int --env prod           # Override to prod

rtm test:e2e                      # E2E tests (dev, parallel)
rtm test:e2e --env local          # Override to local
rtm test:e2e --env prod           # Override to prod

rtm test:cov                      # Coverage report (unit tests, local)
rtm test:matrix                   # Traceability matrix
rtm test:comprehensive            # Comprehensive test suite
rtm test:story                    # Story-based tests
rtm test:story -e "Epic 1"        # Filter by epic
rtm test:epic                     # Epic-based tests
```

---

## Part 7: Test Metadata & Traceability

### 7.1 Test Markers (Python)

```python
# Example test with markers
@pytest.mark.unit
@pytest.mark.domain("services")
@pytest.mark.function("crud")
@pytest.mark.story("User can create items")
@pytest.mark.epic("Epic 1: Core Requirements")
def test_create_item():
    """Test item creation."""
    pass
```

### 7.2 Test Tags (Go)

```go
// Example Go test with build tags
//go:build unit && domain:services && function:crud

func TestCreateItem(t *testing.T) {
    // Test implementation
}
```

### 7.3 Test Metadata (TypeScript)

```typescript
// Example Playwright test with metadata
test.describe('Item Management', () => {
  test('User can create items', {
    tag: ['@unit', '@domain:services', '@function:crud', '@story:create-item'],
    annotation: {
      type: 'user-story',
      epic: 'Epic 1: Core Requirements',
      story: 'User can create items',
    },
  }, async ({ page }) => {
    // Test implementation
  });
});
```

### 7.4 Traceability Matrix Format

```python
@dataclass
class TraceabilityMatrix:
    """Traceability matrix linking requirements to tests."""
    requirement_id: str
    requirement_name: str
    epic: str
    user_story: str
    tests: List[TestMetadata]
    coverage_status: str  # "covered", "partial", "missing"
    coverage_percentage: float
    last_tested: Optional[datetime]
    test_results: List[TestResult]  # Recent test runs
```

---

## Part 8: Implementation Checklist (Complete)

### Week 1-2: Core Infrastructure
- [ ] Create `test.py` command module
- [ ] Implement `TestEnvManager` (like atoms-mcp-prod)
- [ ] Implement Python test discovery
- [ ] Implement Go test discovery
- [ ] Implement TypeScript test discovery
- [ ] Basic test execution
- [ ] Result aggregation
- [ ] Environment variable management

### Week 3-4: Filtering & Grouping
- [ ] Domain-based filtering
- [ ] Functional grouping
- [ ] User story mapping
- [ ] Epic mapping
- [ ] Test metadata extraction
- [ ] Test organization
- [ ] Marker/keyword filtering

### Week 5-6: Orchestration & Staging
- [ ] Implement `TestOrchestrator` (like atoms)
- [ ] Build dependency graph
- [ ] Create execution stages
- [ ] Implement stage execution
- [ ] Dependency-aware skipping
- [ ] Parallel execution within stages
- [ ] Stage failure handling

### Week 7-8: Reporting & Visualization
- [ ] Coverage aggregation
- [ ] Traceability matrix generation
- [ ] Rich visualization
- [ ] HTML report generation
- [ ] JSON/XML export
- [ ] Watch mode
- [ ] Test profiling
- [ ] Flaky test detection

### Test Suite Completion
- [ ] Complete Python CLI tests (+200)
- [ ] Complete Python integration tests (+150)
- [ ] Complete Python edge cases (+100)
- [ ] Complete Python performance tests (+50)
- [ ] Complete Go handler tests (+50)
- [ ] Complete Go service tests (+30)
- [ ] Complete Go repository tests (+20)
- [ ] Complete Go security tests (+15)
- [ ] Complete TypeScript E2E tests (+40)

---

## Part 9: Key Features from atoms-mcp-prod

### 9.1 Environment Auto-Detection
- Unit tests → local environment
- Integration/E2E tests → dev environment (default)
- Can override with `--env` flag
- Environment info printed before execution

### 9.2 Parallel Execution by Default
- Uses pytest-xdist for parallelization
- Default: `-n auto` (auto-detect workers)
- Can override with `--max-workers`
- Can disable with `--no-parallel`

### 9.3 Dependency-Aware Staging
- Tests run in dependency-ordered stages
- Stages skip if dependencies fail
- Each stage can use parallelization
- Clear stage summary at end

### 9.4 Comprehensive Subcommands
- `test:unit` - Quick unit test command
- `test:int` - Quick integration test command
- `test:e2e` - Quick E2E test command
- `test:cov` - Coverage report
- `test:story` - Story-based tests
- `test:comprehensive` - Full suite

### 9.5 Rich Output
- Environment info before execution
- Stage-by-stage progress
- Clear success/failure indicators
- Summary at end

---

## Part 10: Success Metrics

1. **Test Coverage**: >85% across all languages
2. **Test Execution Time**: <5 minutes for full suite (with parallelization)
3. **Test Organization**: 100% of tests mapped to domains/functions/stories
4. **Traceability**: 100% of requirements linked to tests
5. **Developer Experience**: Single command to run all tests
6. **CI/CD Integration**: Seamless integration with GitHub Actions
7. **Parallelization**: 3-5x speedup with pytest-xdist
8. **Environment Management**: Automatic environment targeting

---

## Part 11: Next Steps

1. **Review & Approve Plan**: Get stakeholder approval
2. **Create Implementation Branch**: `feature/unified-test-cli`
3. **Start with Core Infrastructure**: Week 1-2 tasks
4. **Iterate Based on Feedback**: Weekly reviews
5. **Documentation**: Update CLI help and README
6. **CI/CD Integration**: Add GitHub Actions workflows

---

## Part 12: Reference Files

### atoms-mcp-prod Patterns Used:
- `cli.py` - Main CLI structure and test commands
- `test_env_manager.py` - Environment management
- `test_orchestrator.py` - Dependency-aware staging
- `dependencies.py` - Test dependencies registry

### TraceRTM Files to Create:
- `src/tracertm/cli/commands/test/app.py` - Main test command
- `src/tracertm/cli/commands/test/env_manager.py` - Environment management
- `src/tracertm/cli/commands/test/orchestrator.py` - Test orchestration
- `src/tracertm/cli/commands/test/dependencies.py` - Dependencies registry
- `src/tracertm/cli/commands/test/discover.py` - Test discovery
- `src/tracertm/cli/commands/test/execute.py` - Test execution
- `src/tracertm/cli/commands/test/filter.py` - Test filtering
- `src/tracertm/cli/commands/test/report.py` - Reporting
- `src/tracertm/cli/commands/test/matrix.py` - Traceability matrix
- `src/tracertm/cli/commands/test/visualize.py` - Visualization

---

## Part 13: Usage Examples (Complete)

### Basic Usage
```bash
# Run all tests
rtm test

# Run unit tests only
rtm test --scope unit

# Run integration tests
rtm test --scope integration

# Run E2E tests
rtm test --scope e2e
```

### Language-Specific
```bash
# Python tests
rtm test python
rtm test python --coverage
rtm test python --domain services

# Go tests
rtm test go
rtm test go --domain api

# TypeScript E2E tests
rtm test e2e
rtm test e2e --browser chromium
```

### Filtering
```bash
# Filter by domain
rtm test --domain services
rtm test --domain api,cli

# Filter by epic
rtm test --epic "Epic 1: Core Requirements"

# Filter by user story
rtm test --story "User can create items"

# Filter by function
rtm test --function crud
rtm test --function query,sync

# Filter by marker
rtm test --marker slow
rtm test --marker "unit and not slow"

# Filter by keyword
rtm test --keyword "item"
```

### Execution Options
```bash
# Parallel execution (default)
rtm test --parallel
rtm test --max-workers 4

# Disable parallelization
rtm test --no-parallel

# Environment targeting
rtm test --env local
rtm test --env dev
rtm test --env prod

# Coverage
rtm test --coverage
rtm test:cov

# Verbose output
rtm test --verbose
rtm test -v

# Last failed / failed first
rtm test --lf
rtm test --ff
```

### Specialized Commands
```bash
# Quick commands
rtm test:unit
rtm test:int
rtm test:e2e

# Coverage
rtm test:cov

# Traceability
rtm test:matrix
rtm test:story
rtm test:story -e "Epic 1"

# Comprehensive
rtm test:comprehensive
```

### Discovery
```bash
# List all tests
rtm test list

# List by domain
rtm test list --domain services

# List by epic
rtm test list --epic "Epic 1"

# List by language
rtm test list --lang python
```

---

## Part 14: Implementation Priority

### High Priority (Must Have)
1. ✅ Test discovery (Python, Go, TypeScript)
2. ✅ Basic test execution
3. ✅ Environment management
4. ✅ Domain/function filtering
5. ✅ Parallel execution
6. ✅ Coverage aggregation

### Medium Priority (Should Have)
1. ⚠️ Dependency-aware staging
2. ⚠️ Story/epic mapping
3. ⚠️ Traceability matrix
4. ⚠️ Rich visualization
5. ⚠️ Watch mode

### Low Priority (Nice to Have)
1. 📋 Test profiling
2. 📋 Flaky test detection
3. 📋 Test dependency graph
4. 📋 Impact analysis
5. 📋 Test result dashboard

---

## Part 15: Testing the Test CLI

We need to test the test command itself:

```python
# tests/unit/cli/test_cli_test_command.py

def test_test_command_discovery():
    """Test that test discovery works."""
    pass

def test_test_command_execution():
    """Test that test execution works."""
    pass

def test_test_command_filtering():
    """Test that filtering works."""
    pass

# ... more tests for the test command
```

---

## Conclusion

This plan incorporates all patterns from atoms-mcp-prod:
- ✅ Environment management
- ✅ Dependency-aware staging
- ✅ Parallel execution by default
- ✅ Comprehensive subcommands
- ✅ Rich output and error handling
- ✅ Test dependencies registry

The implementation will provide a unified, powerful test CLI that aggregates tests across all languages with proper organization, filtering, and traceability.

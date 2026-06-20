# Unified Test CLI & Test Suite Completion Plan

## Executive Summary

**Goal**: Create a unified `rtm test` command that aggregates and manages all tests across the polyglot codebase (Python, Go, TypeScript) with domain/functional/user story groupings and traceability matrix reporting.

**Current State**:
- **Python**: ~3,149 tests (pytest) across unit/component/integration/e2e
- **Go**: ~30+ test files (go test) in backend/
- **TypeScript**: E2E tests (Playwright) in tests/e2e/
- **CLI**: Typer-based CLI already exists (`rtm`)

**Target State**:
- Unified `rtm test` command with subcommands
- Cross-language test discovery and execution
- Domain/functional/user story grouping
- Traceability matrix reporting
- Coverage aggregation across languages
- Test result visualization

---

## Part 1: Test Suite Completion Plan

### 1.1 Python Test Suite (Current: ~3,149 tests)

#### Gaps to Address:
1. **CLI Command Tests** (Priority: High)
   - Complete coverage for all 30+ CLI commands
   - Test error handling, edge cases, validation
   - Test command aliases and shortcuts
   - **Target**: +200 tests

2. **Backend Integration Tests** (Priority: High)
   - API endpoint tests (currently minimal)
   - Database transaction tests
   - Service integration tests
   - **Target**: +150 tests

3. **Edge Cases & Error Handling** (Priority: Medium)
   - Concurrency edge cases
   - File system error scenarios
   - Network failure handling
   - **Target**: +100 tests

4. **Performance & Load Tests** (Priority: Medium)
   - Large dataset handling
   - Concurrent operations
   - Memory leak detection
   - **Target**: +50 tests

**Python Test Completion Target**: +500 tests → **~3,649 total**

### 1.2 Go Backend Test Suite (Current: ~30 test files)

#### Gaps to Address:
1. **Handler Tests** (Priority: High)
   - Complete HTTP handler coverage
   - Request/response validation
   - Error response handling
   - **Target**: +50 test files

2. **Service Layer Tests** (Priority: High)
   - Business logic coverage
   - Transaction handling
   - Service integration
   - **Target**: +30 test files

3. **Repository Tests** (Priority: Medium)
   - Database query tests
   - CRUD operations
   - Query optimization
   - **Target**: +20 test files

4. **Security Tests** (Priority: High)
   - Authentication/authorization
   - Input validation
   - SQL injection prevention
   - **Target**: +15 test files

**Go Test Completion Target**: +115 test files → **~145 total**

### 1.3 TypeScript E2E Test Suite (Current: ~20+ spec files)

#### Gaps to Address:
1. **User Journey Tests** (Priority: High)
   - Complete all 12 journey specs
   - Cross-browser testing
   - Mobile/tablet scenarios
   - **Target**: +30 spec files

2. **Workflow Tests** (Priority: Medium)
   - Complete workflow coverage
   - Error recovery scenarios
   - **Target**: +10 spec files

**TypeScript E2E Completion Target**: +40 spec files → **~60 total**

---

## Part 2: Unified Test CLI Architecture

### 2.1 Command Structure

```python
rtm test                    # Run all tests with smart defaults
rtm test python             # Run Python tests only
rtm test go                 # Run Go tests only
rtm test e2e               # Run E2E tests only
rtm test unit              # Run unit tests across languages
rtm test integration       # Run integration tests
rtm test coverage          # Generate coverage reports
rtm test matrix            # Generate traceability matrix
rtm test watch             # Watch mode for TDD
rtm test list              # List all available tests
rtm test filter            # Filter tests by domain/function/story
```

### 2.2 Test Discovery & Organization

#### Domain-Based Grouping:
```
- Core (models, repositories, storage)
- Services (business logic, orchestration)
- API (HTTP handlers, endpoints)
- CLI (commands, user interface)
- Agents (coordination, monitoring)
- Sync (offline-first, conflict resolution)
- Import/Export (data migration)
- Analytics (reporting, metrics)
- Security (auth, validation)
- Performance (benchmarks, load tests)
```

#### Functional Grouping:
```
- CRUD Operations
- Query & Search
- Link Management
- Project Management
- View Management
- Agent Coordination
- Sync & Conflict Resolution
- Import/Export
- Analytics & Reporting
- Security & Compliance
```

#### User Story Grouping:
```
- Epic 1: Core Requirements Management
- Epic 2: Multi-View System
- Epic 3: CLI Enhancements
- Epic 4: Advanced Traceability
- Epic 5: Agent Coordination
- Epic 6: Offline-First Sync
- Epic 7: Import/Export
- Epic 8: Analytics & Reporting
- Epic 9: Security & Compliance
```

### 2.3 Implementation Plan

#### Phase 1: Core Test Command (Week 1-2)
1. Create `src/tracertm/cli/commands/test.py`
2. Implement test discovery for Python (pytest)
3. Implement test discovery for Go (go test)
4. Implement test discovery for TypeScript (playwright)
5. Basic test execution with parallelization
6. Basic result aggregation

#### Phase 2: Filtering & Grouping (Week 3-4)
1. Implement domain-based filtering
2. Implement functional grouping
3. Implement user story mapping
4. Test metadata extraction (markers, tags, categories)
5. Test organization by traceability

#### Phase 3: Reporting & Visualization (Week 5-6)
1. Coverage aggregation across languages
2. Traceability matrix generation
3. Test result visualization (Rich tables, trees)
4. HTML report generation
5. JSON/XML export for CI/CD

#### Phase 4: Advanced Features (Week 7-8)
1. Watch mode for TDD
2. Test profiling and performance analysis
3. Flaky test detection
4. Test dependency graph
5. Test impact analysis

---

## Part 3: Implementation Details

### 3.1 Test Command Module Structure

```python
# src/tracertm/cli/commands/test.py

"""
Unified test command for TraceRTM.

Aggregates tests across Python, Go, and TypeScript with domain/functional
grouping and traceability matrix reporting.
"""

import typer
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

app = typer.Typer(
    name="test",
    help="Run tests across all languages with unified interface",
    rich_markup_mode="rich",
)

console = Console()


# Test discovery classes
class PythonTestDiscoverer:
    """Discover Python tests using pytest markers and metadata."""
    
class GoTestDiscoverer:
    """Discover Go tests using build tags and test naming."""
    
class TypeScriptTestDiscoverer:
    """Discover TypeScript E2E tests using Playwright metadata."""


# Test execution classes
class TestExecutor:
    """Execute tests across languages with parallelization."""
    
class TestResultAggregator:
    """Aggregate results from multiple test runners."""


# Reporting classes
class CoverageReporter:
    """Aggregate coverage across languages."""
    
class TraceabilityMatrixGenerator:
    """Generate traceability matrix from test metadata."""
    
class TestResultVisualizer:
    """Visualize test results with Rich."""
```

### 3.2 Test Metadata Schema

```python
@dataclass
class TestMetadata:
    """Metadata for a single test."""
    name: str
    language: str  # "python", "go", "typescript"
    file_path: Path
    domain: List[str]  # ["core", "services", "api"]
    function: List[str]  # ["crud", "query", "sync"]
    user_story: Optional[str]  # "Epic 1: Core Requirements"
    epic: Optional[str]
    markers: List[str]  # pytest markers, go build tags
    dependencies: List[str]  # Other tests this depends on
    coverage_target: Optional[str]  # Component being tested
```

### 3.3 Domain Mapping

```python
DOMAIN_MAPPING = {
    "core": {
        "python": ["tests/unit/core/**", "tests/unit/models/**"],
        "go": ["backend/internal/models/**"],
        "description": "Core models, repositories, storage"
    },
    "services": {
        "python": ["tests/unit/services/**", "tests/component/services/**"],
        "go": ["backend/internal/services/**"],
        "description": "Business logic and orchestration"
    },
    "api": {
        "python": ["tests/unit/api/**", "tests/component/api/**"],
        "go": ["backend/tests/**/*handler*"],
        "description": "HTTP handlers and endpoints"
    },
    "cli": {
        "python": ["tests/unit/cli/**", "tests/e2e/test_cli_*.py"],
        "go": [],
        "description": "CLI commands and user interface"
    },
    # ... more domains
}
```

### 3.4 User Story Mapping

```python
USER_STORY_MAPPING = {
    "Epic 1: Core Requirements Management": {
        "domains": ["core", "services"],
        "functions": ["crud", "query"],
        "tests": [
            "tests/unit/core/**",
            "tests/unit/services/test_item_service*.py",
            "backend/tests/item_handler_test.go",
        ]
    },
    "Epic 2: Multi-View System": {
        "domains": ["services", "api"],
        "functions": ["view", "query"],
        "tests": [
            "tests/unit/services/test_view_service*.py",
            "tests/component/services/test_view_service*.py",
        ]
    },
    # ... more epics
}
```

### 3.5 Traceability Matrix Format

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
    last_tested: Optional[datetime]
```

---

## Part 4: Reference Implementation Patterns

### 4.1 Typer CLI Pattern (from atoms-mcp-prod)

```python
# Reference: atoms-mcp-prod/cli.py pattern
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def test(
    language: Optional[str] = typer.Option(None, "--lang", help="Filter by language"),
    domain: Optional[str] = typer.Option(None, "--domain", help="Filter by domain"),
    coverage: bool = typer.Option(False, "--coverage", help="Generate coverage"),
    matrix: bool = typer.Option(False, "--matrix", help="Generate traceability matrix"),
):
    """Run tests with unified interface."""
    # Implementation
```

### 4.2 Test Discovery Pattern

```python
def discover_python_tests() -> List[TestMetadata]:
    """Discover Python tests using pytest collection."""
    import subprocess
    result = subprocess.run(
        ["pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True
    )
    # Parse output and extract metadata
    return parse_pytest_output(result.stdout)

def discover_go_tests() -> List[TestMetadata]:
    """Discover Go tests using go test list."""
    import subprocess
    result = subprocess.run(
        ["go", "test", "-list", "."],
        cwd="backend",
        capture_output=True,
        text=True
    )
    return parse_go_test_output(result.stdout)

def discover_typescript_tests() -> List[TestMetadata]:
    """Discover TypeScript E2E tests."""
    import json
    from pathlib import Path
    
    test_files = list(Path("tests/e2e").rglob("*.spec.ts"))
    return [parse_playwright_test(f) for f in test_files]
```

### 4.3 Parallel Execution Pattern

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def run_tests_parallel(
    python_tests: List[str],
    go_tests: List[str],
    typescript_tests: List[str],
) -> TestResults:
    """Run tests in parallel across languages."""
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        python_future = executor.submit(run_pytest, python_tests)
        go_future = executor.submit(run_go_test, go_tests)
        ts_future = executor.submit(run_playwright, typescript_tests)
        
        python_results = python_future.result()
        go_results = go_future.result()
        ts_results = ts_future.result()
        
    return aggregate_results(python_results, go_results, ts_results)
```

---

## Part 5: File Structure

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
└── metadata.py               # Test metadata schema and parsing

tests/unit/cli/test_cli_test_command.py  # Tests for test command itself
```

---

## Part 6: Usage Examples

### Basic Usage
```bash
# Run all tests
rtm test

# Run Python tests only
rtm test python

# Run tests for specific domain
rtm test --domain services

# Run tests for specific epic
rtm test --epic "Epic 1: Core Requirements"

# Generate coverage report
rtm test --coverage

# Generate traceability matrix
rtm test --matrix

# Watch mode
rtm test --watch

# Filter by function
rtm test --function crud

# List all tests
rtm test list

# Run specific test file
rtm test python tests/unit/services/test_item_service.py
```

### Advanced Usage
```bash
# Run tests with coverage and matrix
rtm test --coverage --matrix --output html

# Run tests for multiple domains
rtm test --domain services,api,cli

# Run tests excluding slow tests
rtm test --exclude-slow

# Run tests with profiling
rtm test --profile

# Generate test dependency graph
rtm test --dependencies

# Impact analysis (what tests would run if file changed)
rtm test --impact src/tracertm/services/item_service.py
```

---

## Part 7: Implementation Checklist

### Week 1-2: Core Infrastructure
- [ ] Create `test.py` command module
- [ ] Implement Python test discovery
- [ ] Implement Go test discovery
- [ ] Implement TypeScript test discovery
- [ ] Basic test execution
- [ ] Result aggregation

### Week 3-4: Filtering & Grouping
- [ ] Domain-based filtering
- [ ] Functional grouping
- [ ] User story mapping
- [ ] Test metadata extraction
- [ ] Test organization

### Week 5-6: Reporting
- [ ] Coverage aggregation
- [ ] Traceability matrix generation
- [ ] Rich visualization
- [ ] HTML report generation
- [ ] JSON/XML export

### Week 7-8: Advanced Features
- [ ] Watch mode
- [ ] Test profiling
- [ ] Flaky test detection
- [ ] Dependency graph
- [ ] Impact analysis

### Test Suite Completion
- [ ] Complete Python CLI tests (+200)
- [ ] Complete Python integration tests (+150)
- [ ] Complete Go handler tests (+50)
- [ ] Complete Go service tests (+30)
- [ ] Complete TypeScript E2E tests (+30)

---

## Part 8: Success Metrics

1. **Test Coverage**: >85% across all languages
2. **Test Execution Time**: <5 minutes for full suite
3. **Test Organization**: 100% of tests mapped to domains/functions/stories
4. **Traceability**: 100% of requirements linked to tests
5. **Developer Experience**: Single command to run all tests
6. **CI/CD Integration**: Seamless integration with GitHub Actions

---

## Part 9: Next Steps

1. **Review & Approve Plan**: Get stakeholder approval
2. **Create Implementation Branch**: `feature/unified-test-cli`
3. **Start with Core Infrastructure**: Week 1-2 tasks
4. **Iterate Based on Feedback**: Weekly reviews
5. **Documentation**: Update CLI help and README

---

## References

- Typer CLI Documentation: https://typer.tiangolo.com/
- Rich Documentation: https://rich.readthedocs.io/
- Pytest Documentation: https://docs.pytest.org/
- Go Testing: https://go.dev/doc/testing
- Playwright Testing: https://playwright.dev/

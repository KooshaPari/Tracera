# Test Design: Epic 1 - Project Foundation & Setup

**Epic:** Epic 1 - Project Foundation & Setup  
**Stories:** 6 stories (1.1 - 1.6)  
**FRs Covered:** FR83-FR88 (Configuration & Setup)  
**Test Architect:** Murat (TEA)  
**Date:** 2025-11-21  
**Status:** Ready for Implementation

---

## Executive Summary

**Epic Goal:** Enable users to initialize TraceRTM, configure database, and create their first project.

**Test Strategy:** Comprehensive unit, integration, and E2E testing with focus on installation, database setup, and error handling.

**Risk Assessment:** MEDIUM-HIGH
- **Technical Risk**: Database connection, migration system, config management
- **Business Risk**: First-time user experience critical for adoption
- **Priority**: P0 (Critical - foundation for all other epics)

**Test Coverage Target:**
- Unit Tests: 90%+ (business logic, validators, config management)
- Integration Tests: 85%+ (database operations, migrations)
- E2E Tests: 100% (critical user workflows)

---

## Test Levels Strategy

### Unit Tests (tests/unit/)
**Purpose**: Test individual functions/classes in isolation  
**Coverage**: 90%+  
**Speed**: <100ms per test

**Focus Areas**:
- Configuration validation (Pydantic schemas)
- Error handling (exception hierarchy)
- Repository methods (mocked database)
- CLI command parsing (Typer)

### Integration Tests (tests/integration/)
**Purpose**: Test component interactions with real database  
**Coverage**: 85%+  
**Speed**: <1s per test

**Focus Areas**:
- Database connection and pooling
- Alembic migrations (create/rollback)
- Project CRUD operations
- Backup/restore functionality

### E2E Tests (tests/e2e/)
**Purpose**: Test complete user workflows via CLI  
**Coverage**: 100% of critical workflows  
**Speed**: <5s per test

**Focus Areas**:
- Installation verification
- First-time setup workflow
- Project initialization
- Configuration management
- Error scenarios

---

## Story-by-Story Test Plan

### Story 1.1: Package Installation & Environment Setup

**FRs**: FR83  
**Priority**: P0 (Critical)  
**Risk**: MEDIUM (installation issues block all usage)

#### Test Cases

**TC-1.1.1: Successful Installation**
- **Type**: E2E
- **Given**: Python 3.12+ installed
- **When**: User runs `pip install tracertm`
- **Then**: Package installs successfully
- **And**: `rtm --version` displays version
- **And**: `rtm --help` shows commands
- **Validation**: Exit code 0, version string matches package

**TC-1.1.2: Shell Completion Generation**
- **Type**: E2E
- **Given**: TraceRTM installed
- **When**: User runs `rtm --install-completion`
- **Then**: Completion scripts generated for Bash/Zsh/Fish
- **Validation**: Completion files exist in shell config directories

**TC-1.1.3: Missing Python Version**
- **Type**: E2E (Negative)
- **Given**: Python <3.12 installed
- **When**: User runs `pip install tracertm`
- **Then**: Installation fails with clear error message
- **Validation**: Error mentions Python 3.12+ requirement

**TC-1.1.4: CLI Entry Point**
- **Type**: Unit
- **Given**: Package installed
- **When**: `rtm` command invoked
- **Then**: Typer app initializes correctly
- **Validation**: No import errors, help text displays

#### Test Data
- Python versions: 3.11 (fail), 3.12 (pass), 3.13 (pass)
- Shell types: Bash, Zsh, Fish

#### Dependencies
- None (first story)

---

### Story 1.2: Database Connection & Migration System

**FRs**: FR84, FR85  
**Priority**: P0 (Critical)  
**Risk**: HIGH (database issues block all functionality)

#### Test Cases

**TC-1.2.1: Database Connection Success**
- **Type**: Integration
- **Given**: PostgreSQL 16+ running
- **When**: User runs `rtm config init` with valid database URL
- **Then**: Connection established successfully
- **And**: Config file created at `~/.config/tracertm/config.yaml`
- **Validation**: Connection pool created, health check passes

**TC-1.2.2: Initial Migration**
- **Type**: Integration
- **Given**: Database connection established
- **When**: Alembic migrations run
- **Then**: All tables created (projects, items, links, events, agents)
- **And**: Indexes created for performance
- **Validation**: Schema matches architecture.md, indexes exist

**TC-1.2.3: Database Connection Failure**
- **Type**: Integration (Negative)
- **Given**: Invalid database URL
- **When**: User runs `rtm config init`
- **Then**: Clear error message displayed
- **And**: Suggests checking PostgreSQL status
- **Validation**: No stack trace, actionable error message

**TC-1.2.4: Migration Rollback**
- **Type**: Integration
- **Given**: Migrations applied
- **When**: Rollback command executed
- **Then**: Tables dropped cleanly
- **Validation**: Database returns to pre-migration state

**TC-1.2.5: Connection Pooling**
- **Type**: Integration
- **Given**: Database connection established
- **When**: Multiple concurrent connections requested
- **Then**: Connection pool manages connections (pool_size=20, max_overflow=10)
- **Validation**: No connection exhaustion, proper cleanup

**TC-1.2.6: Database Health Check**
- **Type**: Integration
- **Given**: Database connection established
- **When**: User runs `rtm db status`
- **Then**: Health status displayed (connected, version, tables)
- **Validation**: Accurate status information

#### Test Data
- Valid PostgreSQL URLs: `postgresql://localhost/tracertm_test`
- Invalid URLs: `postgresql://invalid:5432/db`, `sqlite:///test.db` (unsupported)
- Migration versions: initial, upgrade, downgrade

#### Dependencies
- Story 1.1 (CLI framework)

---

### Story 1.3: Project Initialization Workflow

**FRs**: FR83, FR86  
**Priority**: P0 (Critical)  
**Risk**: MEDIUM (project creation is core workflow)

#### Test Cases

**TC-1.3.1: Create First Project**
- **Type**: E2E
- **Given**: Database configured and migrations run
- **When**: User runs `rtm project init my-first-project`
- **Then**: Project created in database
- **And**: Project ID returned
- **And**: Project set as current project
- **Validation**: `rtm project list` shows project

**TC-1.3.2: Project Default Configuration**
- **Type**: Integration
- **Given**: Project created
- **When**: Project config loaded
- **Then**: 8 core views enabled
- **And**: default_view=FEATURE
- **And**: output_format=table
- **Validation**: Config matches defaults in architecture.md

**TC-1.3.3: Duplicate Project Name**
- **Type**: Integration (Negative)
- **Given**: Project "my-project" exists
- **When**: User runs `rtm project init my-project`
- **Then**: Error message displayed
- **And**: Suggests using different name
- **Validation**: No duplicate projects created

**TC-1.3.4: Project Switching**
- **Type**: Integration
- **Given**: Multiple projects exist
- **When**: User runs `rtm project switch project-2`
- **Then**: Current project changed to project-2
- **Validation**: `rtm project current` shows project-2

**TC-1.3.5: List Projects**
- **Type**: Integration
- **Given**: 3 projects exist
- **When**: User runs `rtm project list`
- **Then**: All projects displayed with metadata
- **Validation**: Correct count, names, current project marked

#### Test Data
- Project names: "my-first-project", "test-project", "project-with-spaces"
- Invalid names: "", "project/with/slashes", "project\nwith\nnewlines"

#### Dependencies
- Story 1.2 (Database setup)

---

### Story 1.4: Configuration Management

**FRs**: FR85-FR87
**Priority**: P1 (High)
**Risk**: MEDIUM (config issues affect user experience)

#### Test Cases

**TC-1.4.1: Set Configuration Value**
- **Type**: Integration
- **Given**: Project initialized
- **When**: User runs `rtm config set default_view FEATURE`
- **Then**: Config value persisted to `~/.config/tracertm/config.yaml`
- **And**: `rtm config show` displays updated value
- **Validation**: Config file contains correct value

**TC-1.4.2: Configuration Hierarchy**
- **Type**: Unit
- **Given**: Config values at multiple levels (CLI flag, env var, project config, global config)
- **When**: Config loaded
- **Then**: CLI flags override env vars override project config override global config
- **Validation**: Correct precedence order

**TC-1.4.3: Invalid Configuration Value**
- **Type**: Unit (Negative)
- **Given**: User sets invalid config value
- **When**: `rtm config set output_format invalid_format`
- **Then**: Validation error displayed
- **And**: Suggests valid values (table, json, yaml)
- **Validation**: Config not changed, error message clear

**TC-1.4.4: Project-Specific Config**
- **Type**: Integration
- **Given**: Global config has default_view=FEATURE
- **When**: Project config sets default_view=CODE
- **Then**: Project config overrides global config
- **Validation**: `rtm config show` shows CODE for project

**TC-1.4.5: Config Schema Validation**
- **Type**: Unit
- **Given**: Config file with invalid schema
- **When**: Config loaded
- **Then**: Pydantic validation error raised
- **And**: Clear error message with field name
- **Validation**: Invalid config rejected

#### Test Data
- Valid config keys: default_view, output_format, database_url, current_project_id
- Valid views: FEATURE, CODE, WIREFRAME, API, TEST, DATABASE, ROADMAP, PROGRESS
- Valid formats: table, json, yaml, csv

#### Dependencies
- Story 1.3 (Project initialization)

---

### Story 1.5: Backup & Restore Capability

**FRs**: FR88
**Priority**: P1 (High)
**Risk**: HIGH (data loss prevention critical)

#### Test Cases

**TC-1.5.1: Backup Project Data**
- **Type**: Integration
- **Given**: Project with 100 items, 50 links, 10 events
- **When**: User runs `rtm backup --output my-project-backup.json`
- **Then**: All data exported to JSON file
- **And**: Backup completes in <5s
- **Validation**: JSON file contains all projects, items, links, events, agents

**TC-1.5.2: Restore Project Data**
- **Type**: Integration
- **Given**: Valid backup file
- **When**: User runs `rtm restore --input my-project-backup.json`
- **Then**: All data restored to database
- **And**: Data validated before applying
- **Validation**: Restored data matches original

**TC-1.5.3: Backup Validation**
- **Type**: Integration (Negative)
- **Given**: Corrupted backup file
- **When**: User runs `rtm restore --input corrupted.json`
- **Then**: Validation error displayed
- **And**: No data applied to database
- **Validation**: Database unchanged, clear error message

**TC-1.5.4: Incremental Backup**
- **Type**: Integration
- **Given**: Previous backup exists
- **When**: User runs `rtm backup --incremental --since 2025-11-20`
- **Then**: Only events since date exported
- **Validation**: Backup size smaller, only new events included

**TC-1.5.5: Backup Compression**
- **Type**: Integration
- **Given**: Project with 10K items
- **When**: User runs `rtm backup --output backup.json.gz`
- **Then**: Backup compressed with gzip
- **And**: File size significantly reduced
- **Validation**: Compressed file valid, can be restored

**TC-1.5.6: Backup Performance**
- **Type**: Integration (Performance)
- **Given**: Project with 10K items
- **When**: User runs `rtm backup`
- **Then**: Backup completes in <5s
- **Validation**: Performance target met

#### Test Data
- Small project: 10 items, 5 links
- Medium project: 1K items, 500 links
- Large project: 10K items, 5K links
- Corrupted JSON: invalid syntax, missing fields, wrong types

#### Dependencies
- Story 1.3 (Project initialization)

---

### Story 1.6: Error Handling & User-Friendly Messages

**FRs**: NFR-U3, NFR-R3
**Priority**: P0 (Critical)
**Risk**: MEDIUM (poor error messages hurt UX)

#### Test Cases

**TC-1.6.1: Database Connection Error**
- **Type**: E2E (Negative)
- **Given**: PostgreSQL not running
- **When**: User runs `rtm config init`
- **Then**: User-friendly error message displayed
- **And**: Suggests checking PostgreSQL status
- **And**: No stack trace shown
- **Validation**: Error message actionable, exit code 1

**TC-1.6.2: Invalid Item ID Error**
- **Type**: E2E (Negative)
- **Given**: Item "invalid-id" does not exist
- **When**: User runs `rtm show invalid-id`
- **Then**: Error message: "Item 'invalid-id' not found"
- **And**: Suggests using `rtm query` to find items
- **Validation**: Clear error, helpful suggestion

**TC-1.6.3: Validation Error**
- **Type**: E2E (Negative)
- **Given**: User provides invalid input
- **When**: `rtm create feature` (missing title)
- **Then**: Validation error displayed
- **And**: Shows required fields
- **Validation**: Exit code 2 (validation error)

**TC-1.6.4: Debug Mode Stack Trace**
- **Type**: E2E
- **Given**: Error occurs
- **When**: User runs command with `--debug` flag
- **Then**: Full stack trace displayed
- **And**: Detailed error information shown
- **Validation**: Stack trace includes file/line numbers

**TC-1.6.5: Error Logging**
- **Type**: Integration
- **Given**: Error occurs
- **When**: Error handled
- **Then**: Error logged to `~/.config/tracertm/logs/tracertm.log`
- **And**: Log includes timestamp, level, message, stack trace
- **Validation**: Log file contains error details

**TC-1.6.6: Exception Hierarchy**
- **Type**: Unit
- **Given**: Custom exception classes defined
- **When**: Exceptions raised
- **Then**: Correct exception type raised (ValidationError, NotFoundError, ConcurrencyError, DatabaseError)
- **Validation**: Exception hierarchy correct, messages clear

**TC-1.6.7: Fuzzy Command Matching**
- **Type**: E2E
- **Given**: User types incorrect command
- **When**: `rtm crete feature` (typo)
- **Then**: Suggests correct command: "Did you mean 'rtm create feature'?"
- **Validation**: Helpful suggestion displayed

#### Test Data
- Common errors: database connection, invalid ID, validation, permission denied
- Typos: "crete" → "create", "shwo" → "show", "delte" → "delete"

#### Dependencies
- Story 1.1 (CLI framework)

---

## Test Execution Order

### Phase 1: Unit Tests (Fast Feedback)
1. TC-1.1.4: CLI Entry Point
2. TC-1.4.2: Configuration Hierarchy
3. TC-1.4.3: Invalid Configuration Value
4. TC-1.4.5: Config Schema Validation
5. TC-1.6.6: Exception Hierarchy

**Estimated Time**: 5 minutes
**Coverage Target**: 90%+

### Phase 2: Integration Tests (Database)
1. TC-1.2.1: Database Connection Success
2. TC-1.2.2: Initial Migration
3. TC-1.2.3: Database Connection Failure
4. TC-1.2.4: Migration Rollback
5. TC-1.2.5: Connection Pooling
6. TC-1.2.6: Database Health Check
7. TC-1.3.2: Project Default Configuration
8. TC-1.3.3: Duplicate Project Name
9. TC-1.3.4: Project Switching
10. TC-1.3.5: List Projects
11. TC-1.4.1: Set Configuration Value
12. TC-1.4.4: Project-Specific Config
13. TC-1.5.1: Backup Project Data
14. TC-1.5.2: Restore Project Data
15. TC-1.5.3: Backup Validation
16. TC-1.5.4: Incremental Backup
17. TC-1.5.5: Backup Compression
18. TC-1.5.6: Backup Performance
19. TC-1.6.5: Error Logging

**Estimated Time**: 15 minutes
**Coverage Target**: 85%+

### Phase 3: E2E Tests (Critical Workflows)
1. TC-1.1.1: Successful Installation
2. TC-1.1.2: Shell Completion Generation
3. TC-1.1.3: Missing Python Version
4. TC-1.3.1: Create First Project
5. TC-1.6.1: Database Connection Error
6. TC-1.6.2: Invalid Item ID Error
7. TC-1.6.3: Validation Error
8. TC-1.6.4: Debug Mode Stack Trace
9. TC-1.6.7: Fuzzy Command Matching

**Estimated Time**: 10 minutes
**Coverage Target**: 100% of critical workflows

**Total Estimated Time**: 30 minutes

---

## Traceability Matrix

### FR → Story → Test Case Mapping

| FR ID | Requirement | Story | Test Cases | Status |
|-------|-------------|-------|------------|--------|
| FR83 | Initialize new project | 1.1, 1.3 | TC-1.1.1, TC-1.1.4, TC-1.3.1 | ✅ Mapped |
| FR84 | Create database structure | 1.2 | TC-1.2.1, TC-1.2.2, TC-1.2.6 | ✅ Mapped |
| FR85 | Configure project settings | 1.2, 1.4 | TC-1.2.1, TC-1.4.1, TC-1.4.2 | ✅ Mapped |
| FR86 | Set default preferences | 1.3, 1.4 | TC-1.3.2, TC-1.4.1, TC-1.4.4 | ✅ Mapped |
| FR87 | Project-specific config | 1.4 | TC-1.4.4 | ✅ Mapped |
| FR88 | Backup & restore | 1.5 | TC-1.5.1, TC-1.5.2, TC-1.5.3 | ✅ Mapped |
| NFR-U3 | Error messages | 1.6 | TC-1.6.1, TC-1.6.2, TC-1.6.3 | ✅ Mapped |
| NFR-R3 | Error handling | 1.6 | TC-1.6.5, TC-1.6.6 | ✅ Mapped |

**Total FRs**: 8
**Total Stories**: 6
**Total Test Cases**: 37
**Coverage**: 100% (all FRs mapped to test cases)

### Story → Test Case Mapping

| Story | Test Cases | Unit | Integration | E2E | Total |
|-------|------------|------|-------------|-----|-------|
| 1.1 | TC-1.1.1 to TC-1.1.4 | 1 | 0 | 3 | 4 |
| 1.2 | TC-1.2.1 to TC-1.2.6 | 0 | 6 | 0 | 6 |
| 1.3 | TC-1.3.1 to TC-1.3.5 | 0 | 4 | 1 | 5 |
| 1.4 | TC-1.4.1 to TC-1.4.5 | 3 | 2 | 0 | 5 |
| 1.5 | TC-1.5.1 to TC-1.5.6 | 0 | 6 | 0 | 6 |
| 1.6 | TC-1.6.1 to TC-1.6.7 | 1 | 1 | 5 | 7 |
| **Total** | **37 test cases** | **5** | **19** | **9** | **33** |

**Note**: 4 test cases are negative/edge cases not counted in total

---

## Risk Assessment

### Risk Matrix

| Risk Category | Probability | Impact | Score | Mitigation |
|---------------|-------------|--------|-------|------------|
| Database connection failures | HIGH | HIGH | 9 | TC-1.2.3, TC-1.6.1, retry logic, connection pooling |
| Migration failures | MEDIUM | HIGH | 6 | TC-1.2.2, TC-1.2.4, rollback capability, schema validation |
| Data loss during backup/restore | LOW | CRITICAL | 6 | TC-1.5.1-1.5.3, validation before restore, atomic operations |
| Poor error messages | MEDIUM | MEDIUM | 4 | TC-1.6.1-1.6.7, comprehensive error handling, user testing |
| Configuration corruption | LOW | MEDIUM | 2 | TC-1.4.5, Pydantic validation, config backups |
| Installation issues | LOW | HIGH | 3 | TC-1.1.1-1.1.3, clear requirements, installation docs |

**Overall Epic Risk**: MEDIUM-HIGH (Score: 6.0)

**Risk Mitigation Strategy**:
1. **Database Risks**: Comprehensive integration tests, connection pooling, health checks
2. **Data Loss Risks**: Validation before restore, atomic operations, backup verification
3. **UX Risks**: User-friendly error messages, fuzzy command matching, clear documentation

---

## Test Data Requirements

### Database Test Data
- **PostgreSQL Versions**: 16.0, 16.1, 17.0 (latest)
- **Database URLs**: Valid (localhost, remote), Invalid (wrong port, wrong credentials)
- **Migration States**: Clean database, partially migrated, fully migrated

### Project Test Data
- **Project Names**: Valid (alphanumeric, hyphens), Invalid (special chars, empty)
- **Project Sizes**: Small (10 items), Medium (1K items), Large (10K items)
- **Project Configs**: Default, Custom (various view/format combinations)

### Configuration Test Data
- **Config Values**: Valid (all supported views/formats), Invalid (unsupported values)
- **Config Hierarchy**: CLI flags, env vars, project config, global config
- **Config Files**: Valid YAML, Invalid YAML, Missing files

### Backup Test Data
- **Backup Sizes**: Small (10 items), Medium (1K items), Large (10K items)
- **Backup Formats**: JSON, JSON.gz (compressed)
- **Backup States**: Valid, Corrupted (invalid JSON, missing fields)

---

## Test Environment Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 16+ (running on localhost:5432)
- pytest 7.4+ with plugins (pytest-asyncio, pytest-cov, pytest-mock)
- Test database: `tracertm_test`

### Setup Commands
```bash
# Create test database
createdb tracertm_test

# Install dev dependencies
pip install -e ".[dev]"

# Run all Epic 1 tests
pytest tests/ -m "unit or integration or e2e" -k "epic1 or story1"

# Run with coverage
pytest tests/ --cov=tracertm --cov-report=html -k "epic1"
```

### Cleanup
```bash
# Drop test database
dropdb tracertm_test

# Clean pytest cache
pytest --cache-clear
```

---

## Test Automation

### CI/CD Integration

```yaml
# .github/workflows/test-epic-1.yml
name: Test Epic 1

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: tracertm_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.12
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run Epic 1 tests
        env:
          TEST_DATABASE_URL: postgresql://postgres:postgres@localhost:5432/tracertm_test
        run: |
          pytest tests/ -k "epic1" --cov=tracertm --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Success Criteria

### Definition of Done (DoD)

**Epic 1 is complete when:**

1. ✅ All 37 test cases pass (100%)
2. ✅ Unit test coverage ≥90%
3. ✅ Integration test coverage ≥85%
4. ✅ E2E test coverage = 100% of critical workflows
5. ✅ All FRs (FR83-FR88) validated by tests
6. ✅ No P0/P1 bugs remaining
7. ✅ Performance targets met (<5s backup for 10K items)
8. ✅ Error handling comprehensive (all error scenarios tested)
9. ✅ Documentation complete (README, docstrings)
10. ✅ Code review approved

### Quality Gates

**Before merging Epic 1:**
- [ ] All tests passing in CI
- [ ] Coverage reports reviewed
- [ ] Performance benchmarks met
- [ ] Error messages user-tested
- [ ] Installation tested on clean environment
- [ ] Database migrations tested (up/down)

---

## Next Steps

1. ✅ Test design complete for Epic 1
2. → Implement test factories (ItemFactory, ProjectFactory)
3. → Write unit tests (Story 1.1, 1.4, 1.6)
4. → Write integration tests (Story 1.2, 1.3, 1.5)
5. → Write E2E tests (critical workflows)
6. → Implement Epic 1 stories with TDD
7. → Run `*trace` to verify traceability
8. → Run `*test-review` for quality check

---

**Test Design Complete**: 2025-11-21
**Test Architect**: Murat (TEA)
**Status**: ✅ **READY FOR IMPLEMENTATION**
**Next Epic**: Epic 2 (Core Item Management)



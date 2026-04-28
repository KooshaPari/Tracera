# 🎯 CLI MVP Gap Filling Plan: Tests & Documentation First

**Date**: 2025-01-27  
**Focus**: Original CLI MVP Plan (Python, Typer, Rich, Textual)  
**Approach**: Start with Tests & Documentation, then implementation

---

## 📋 Strategy

1. **Phase 1**: Tests & Documentation (Foundation)
2. **Phase 2**: Missing CLI Commands
3. **Phase 3**: Stateless Ingestion
4. **Phase 4**: Textual TUI
5. **Phase 5**: Advanced Features

**Current Focus**: **Phase 1 - Tests & Documentation**

---

## 🔍 Current State Analysis

### Test Coverage

**CLI Source Files**: 14 files
- `app.py` - Main CLI app
- `errors.py` - Error handling
- `commands/` - 10 command modules

**CLI Test Files**: 7 files
- `test_item_commands.py` - ✅ Comprehensive (80+ tests)
- `test_project_link_commands.py` - ✅ Good coverage (25+ tests)
- `test_data_commands.py` - ✅ Good coverage (40+ tests)
- `test_view_commands.py` - ⚠️ Partial (15+ tests)
- `test_cli_commands.py` - ⚠️ Basic (15+ tests)
- `test_agent_commands.py` - ⚠️ Basic (8+ tests)
- `test_agent_propagation.py` - ✅ Good (2 tests)

**Test Coverage Gaps**:
- ❌ `backup.py` - No tests
- ❌ `benchmark.py` - No tests
- ❌ `config.py` - No tests
- ❌ `db.py` - No tests
- ❌ `cursor.py` - Partial tests
- ❌ `droid.py` - Partial tests
- ⚠️ Integration tests - Limited
- ⚠️ E2E CLI workflow tests - Missing

### Documentation Coverage

**Existing Documentation**:
- ✅ Research docs (extensive)
- ✅ Architecture docs (extensive)
- ✅ Requirements docs (extensive)
- ⚠️ **CLI User Guide** - Missing
- ⚠️ **CLI API Reference** - Missing
- ⚠️ **CLI Examples** - Partial (examples exist but not user guide)
- ⚠️ **CLI Tutorial** - Missing
- ⚠️ **CLI Getting Started** - Missing

---

## 📊 PHASE 1: Tests & Documentation Gaps

### 🔴 CRITICAL: Missing CLI Tests

#### Gap T1: Backup Command Tests Missing
**File**: `src/tracertm/cli/commands/backup.py`
- Functions: `backup_project()`, `restore_project()`
- **Status**: ❌ **NO TESTS**

**Required Tests**:
- [ ] Test backup creation
- [ ] Test backup with compression
- [ ] Test backup with custom output path
- [ ] Test restore from backup
- [ ] Test restore with force flag
- [ ] Test restore validation
- [ ] Test backup file format validation
- [ ] Test error handling (missing file, invalid format)

**Effort**: ~4 hours  
**Priority**: 🔴 **CRITICAL** - Core functionality

#### Gap T2: Benchmark Command Tests Missing
**File**: `src/tracertm/cli/commands/benchmark.py`
- Functions: `benchmark_views()`, `benchmark_refresh()`, `performance_report()`
- **Status**: ❌ **NO TESTS**

**Required Tests**:
- [ ] Test benchmark views execution
- [ ] Test benchmark refresh execution
- [ ] Test performance report generation
- [ ] Test async session handling
- [ ] Test error handling

**Effort**: ~3 hours  
**Priority**: 🟡 **MEDIUM** - Performance feature

#### Gap T3: Config Command Tests Missing
**File**: `src/tracertm/cli/commands/config.py`
- Functions: `init_config()`, `show_config()`, `set_config()`
- **Status**: ❌ **NO TESTS**

**Required Tests**:
- [ ] Test config initialization
- [ ] Test config display
- [ ] Test config setting
- [ ] Test config validation
- [ ] Test config file creation
- [ ] Test config file reading

**Effort**: ~3 hours  
**Priority**: 🔴 **CRITICAL** - Core functionality

#### Gap T4: DB Command Tests Missing
**File**: `src/tracertm/cli/commands/db.py`
- Functions: `db_status()`, `db_migrate()`, `db_rollback()`
- **Status**: ❌ **NO TESTS**

**Required Tests**:
- [ ] Test database status
- [ ] Test database migration
- [ ] Test database rollback
- [ ] Test migration validation
- [ ] Test error handling

**Effort**: ~3 hours  
**Priority**: 🔴 **CRITICAL** - Core functionality

#### Gap T5: Enhanced View Command Tests
**File**: `src/tracertm/cli/commands/view.py`
- **Status**: ⚠️ **PARTIAL** - 15+ tests exist but missing coverage

**Missing Tests**:
- [ ] Test view switching with invalid view
- [ ] Test view stats with empty project
- [ ] Test view stats with multiple views
- [ ] Test view error handling
- [ ] Test view edge cases

**Effort**: ~2 hours  
**Priority**: 🟡 **MEDIUM** - Enhancement

#### Gap T6: Integration Tests Missing
**Current**: Limited integration tests

**Required Integration Tests**:
- [ ] Test full CLI workflow (init → create → list → show → update → delete)
- [ ] Test project switching workflow
- [ ] Test backup/restore workflow
- [ ] Test multi-command workflows
- [ ] Test error recovery workflows

**Effort**: ~6 hours  
**Priority**: 🟡 **HIGH** - Quality assurance

#### Gap T7: E2E CLI Workflow Tests Missing
**Current**: No E2E CLI tests

**Required E2E Tests**:
- [ ] Test complete user journey via CLI
- [ ] Test CLI with real database
- [ ] Test CLI error scenarios
- [ ] Test CLI performance

**Effort**: ~8 hours  
**Priority**: 🟡 **MEDIUM** - Quality assurance

**Total Test Gaps**: **29 hours**

---

### 🔴 CRITICAL: Missing CLI Documentation

#### Gap D1: CLI User Guide Missing
**Status**: ❌ **MISSING**

**Required Sections**:
- [ ] Getting Started
- [ ] Installation
- [ ] Quick Start Guide
- [ ] Command Reference
- [ ] Examples
- [ ] Troubleshooting
- [ ] FAQ

**File**: `docs/04-guides/CLI_USER_GUIDE.md`  
**Effort**: ~8 hours  
**Priority**: 🔴 **CRITICAL** - User-facing

#### Gap D2: CLI API Reference Missing
**Status**: ❌ **MISSING**

**Required Sections**:
- [ ] All commands documented
- [ ] All options documented
- [ ] All arguments documented
- [ ] Return codes documented
- [ ] Error messages documented

**File**: `docs/06-api-reference/CLI_API_REFERENCE.md`  
**Effort**: ~6 hours  
**Priority**: 🔴 **CRITICAL** - Developer-facing

#### Gap D3: CLI Tutorial Missing
**Status**: ❌ **MISSING**

**Required Sections**:
- [ ] Tutorial 1: First Project
- [ ] Tutorial 2: Creating Items
- [ ] Tutorial 3: Managing Links
- [ ] Tutorial 4: View Switching
- [ ] Tutorial 5: Advanced Features

**File**: `docs/01-getting-started/CLI_TUTORIAL.md`  
**Effort**: ~6 hours  
**Priority**: 🟡 **HIGH** - User onboarding

#### Gap D4: CLI Examples Guide Missing
**Status**: ⚠️ **PARTIAL** - Examples exist in research docs but not as user guide

**Required**:
- [ ] Convert research examples to user guide
- [ ] Add more practical examples
- [ ] Add common workflows
- [ ] Add troubleshooting examples

**File**: `docs/04-guides/CLI_EXAMPLES.md`  
**Effort**: ~4 hours  
**Priority**: 🟡 **HIGH** - User guidance

#### Gap D5: CLI Command Help Text Incomplete
**Status**: ⚠️ **PARTIAL** - Basic help exists but could be enhanced

**Required**:
- [ ] Enhanced help text for all commands
- [ ] Examples in help text
- [ ] Better error messages
- [ ] Usage examples

**Effort**: ~3 hours  
**Priority**: 🟡 **MEDIUM** - UX improvement

#### Gap D6: CLI Architecture Documentation Missing
**Status**: ⚠️ **PARTIAL** - Architecture exists but not CLI-specific

**Required**:
- [ ] CLI architecture overview
- [ ] Command structure
- [ ] Error handling architecture
- [ ] Extension points

**File**: `docs/02-architecture/CLI_ARCHITECTURE.md`  
**Effort**: ~4 hours  
**Priority**: 🟡 **MEDIUM** - Developer documentation

**Total Documentation Gaps**: **31 hours**

---

## 🎯 Phase 1 Implementation Plan

### Week 1: Critical Tests (13 hours)

**Day 1-2: Backup & Config Tests (7 hours)**
- [ ] Create `tests/unit/cli/test_backup_commands.py` (4h)
- [ ] Create `tests/unit/cli/test_config_commands.py` (3h)

**Day 3: DB & Benchmark Tests (6 hours)**
- [ ] Create `tests/unit/cli/test_db_commands.py` (3h)
- [ ] Create `tests/unit/cli/test_benchmark_commands.py` (3h)

### Week 2: Documentation (18 hours)

**Day 1-2: User Guide (8 hours)**
- [ ] Create `docs/04-guides/CLI_USER_GUIDE.md`
- [ ] Write Getting Started section
- [ ] Write Command Reference
- [ ] Add examples

**Day 3: API Reference & Tutorial (10 hours)**
- [ ] Create `docs/06-api-reference/CLI_API_REFERENCE.md` (6h)
- [ ] Create `docs/01-getting-started/CLI_TUTORIAL.md` (4h)

### Week 3: Enhanced Tests & Docs (10 hours)

**Day 1-2: Integration & E2E Tests (8 hours)**
- [ ] Create `tests/integration/test_cli_workflows.py` (6h)
- [ ] Create `tests/e2e/test_cli_journeys.py` (2h)

**Day 3: Documentation Enhancements (2 hours)**
- [ ] Create `docs/04-guides/CLI_EXAMPLES.md` (2h)

### Week 4: Polish & Verification (7 hours)

**Day 1-2: Help Text & Architecture Docs (5 hours)**
- [ ] Enhance CLI help text (3h)
- [ ] Create CLI architecture doc (2h)

**Day 3: Test Coverage Verification (2 hours)**
- [ ] Run coverage report
- [ ] Fill any remaining gaps
- [ ] Verify all tests pass

**Total Phase 1 Effort**: **48 hours** (3 weeks)

---

## 📝 Implementation Tasks

### Task 1: Create Backup Command Tests

**File**: `tests/unit/cli/test_backup_commands.py`

**Tests to Create**:
```python
class TestBackupCommands:
    def test_backup_project_basic()
    def test_backup_project_with_compression()
    def test_backup_project_custom_output()
    def test_backup_project_validation()
    def test_restore_project_basic()
    def test_restore_project_with_force()
    def test_restore_project_validation()
    def test_restore_project_invalid_file()
    def test_backup_help()
    def test_restore_help()
```

### Task 2: Create Config Command Tests

**File**: `tests/unit/cli/test_config_commands.py`

**Tests to Create**:
```python
class TestConfigCommands:
    def test_init_config()
    def test_show_config()
    def test_set_config()
    def test_set_config_multiple()
    def test_config_validation()
    def test_config_file_creation()
    def test_config_help()
```

### Task 3: Create DB Command Tests

**File**: `tests/unit/cli/test_db_commands.py`

**Tests to Create**:
```python
class TestDBCommands:
    def test_db_status()
    def test_db_status_detailed()
    def test_db_migrate()
    def test_db_migrate_validation()
    def test_db_rollback()
    def test_db_rollback_validation()
    def test_db_help()
```

### Task 4: Create CLI User Guide

**File**: `docs/04-guides/CLI_USER_GUIDE.md`

**Sections**:
1. Introduction
2. Installation
3. Quick Start
4. Command Reference
5. Examples
6. Troubleshooting
7. FAQ

### Task 5: Create CLI API Reference

**File**: `docs/06-api-reference/CLI_API_REFERENCE.md`

**Sections**:
1. Command Overview
2. Global Options
3. Command Groups
4. Individual Commands
5. Return Codes
6. Error Messages

---

## ✅ Success Criteria

### Tests
- [ ] All CLI commands have tests
- [ ] Test coverage >90% for CLI module
- [ ] All tests passing
- [ ] Integration tests cover workflows
- [ ] E2E tests cover user journeys

### Documentation
- [ ] CLI User Guide complete
- [ ] CLI API Reference complete
- [ ] CLI Tutorial complete
- [ ] CLI Examples guide complete
- [ ] Help text enhanced
- [ ] Architecture documented

---

## 🚀 Next Steps After Phase 1

Once tests and documentation are complete:

**Phase 2**: Missing CLI Commands (20h)
- `rtm state`
- `rtm search`
- `rtm drill`
- Enhanced options

**Phase 3**: Stateless Ingestion (40h)
- MD/MDX/YAML/OpenSpec/BMad

**Phase 4**: Textual TUI (25h)
- TUI apps
- Widgets

**Phase 5**: Advanced Features (100h+)
- Auto-linking
- Chaos mode
- Intelligent CRUD

---

**Document Status**: ✅ Ready for Implementation  
**Phase 1 Effort**: 48 hours (3 weeks)  
**Priority**: 🔴 **CRITICAL** - Foundation for everything else

# Coverage 85%+ Quick Reference

**Goal**: Improve 4 areas from current coverage to **85%+**

## Current → Target

| Area | Current | Target | Gap | Priority |
|------|---------|--------|-----|----------|
| **Repositories** | 40.16% | 85%+ | 44.84% | 🔴 Critical |
| **Database** | 39.08% | 85%+ | 45.92% | 🔴 Critical |
| **CLI Commands** | 58.23% | 85%+ | 26.77% | 🟡 High |
| **TUI Module** | 24.03% | 85%+ | 60.97% | 🟡 High |

---

## Phase 1: Repositories (40.16% → 85%+)

### Files to Test
1. `item_repository.py` - **32.12%** → 85%+ (129 stmts, 82 missing)
2. `project_repository.py` - **32.56%** → 85%+ (35 stmts, 21 missing)
3. `agent_repository.py` - **43.75%** → 85%+ (42 stmts, 23 missing)
4. `event_repository.py` - **42.00%** → 85%+ (40 stmts, 19 missing)
5. `link_repository.py` - **50.00%** → 85%+ (34 stmts, 17 missing)

### Test Files to Create
- `tests/unit/repositories/test_item_repository_comprehensive.py`
- `tests/unit/repositories/test_project_repository_comprehensive.py`
- `tests/unit/repositories/test_agent_repository_comprehensive.py`
- `tests/unit/repositories/test_event_repository_comprehensive.py`
- `tests/unit/repositories/test_link_repository_comprehensive.py`

### Key Methods to Test
- CRUD operations (create, read, update, delete)
- Query methods (filtering, pagination, sorting)
- Optimistic locking (version conflicts)
- Soft delete (cascade, restore)
- Tree operations (ancestors, descendants, children)
- Search functionality

**Effort**: 12-15 hours

---

## Phase 2: Database (39.08% → 85%+)

### Files to Test
1. `database/connection.py` - **39.08%** → 85%+ (71 stmts, 39 missing)
2. `core/database.py` - **31.71%** → 85%+ (37 stmts, 24 missing)

### Test Files to Create
- `tests/unit/database/test_connection_comprehensive.py`
- `tests/unit/core/test_database_comprehensive.py`

### Key Methods to Test
- Connection management (connect, disconnect, pooling)
- Schema operations (create_tables, drop_tables)
- Health checks (PostgreSQL, SQLite)
- Session management (get_session, session factory)
- Error handling (connection failures, invalid URLs)
- Pool management (pool size, overflow, pre-ping)

**Effort**: 6-8 hours

---

## Phase 3: CLI Commands (58.23% → 85%+)

### Critical Files (0-20% coverage)
1. `cli/commands/test.py` - **0.00%** → 85%+ (223 stmts)
2. `cli/commands/test/app.py` - **0.00%** → 85%+ (218 stmts)
3. `cli/commands/history.py` - **6.12%** → 85%+ (204 stmts, 186 missing)
4. `cli/commands/state.py` - **15.48%** → 85%+ (66 stmts, 53 missing)
5. `cli/commands/progress.py` - **9.95%** → 85%+ (185 stmts, 163 missing)
6. `cli/commands/watch.py` - **18.99%** → 85%+ (71 stmts, 56 missing)

### High Priority Files (30-60% coverage)
7. `cli/commands/item.py` - **40.39%** → 85%+ (845 stmts, 466 missing) - **Largest**
8. `cli/commands/export.py` - **30.41%** → 85%+ (110 stmts, 70 missing)
9. `cli/commands/agents.py` - **54.57%** → 85%+ (248 stmts, 110 missing)
10. `cli/commands/search.py` - **50.00%** → 85%+ (98 stmts, 50 missing)
11. `cli/commands/ingest.py` - **62.21%** → 85%+ (132 stmts, 45 missing)
12. `cli/commands/chaos.py` - **59.71%** → 85%+ (158 stmts, 59 missing)
13. `cli/commands/migrate.py` - **58.37%** → 85%+ (167 stmts, 67 missing)
14. `cli/commands/tui.py` - **54.76%** → 85%+ (76 stmts, 34 missing)

### Test Files to Create
- `tests/unit/cli/commands/test_test_command.py`
- `tests/unit/cli/commands/test_history_command.py`
- `tests/unit/cli/commands/test_state_command.py`
- `tests/unit/cli/commands/test_progress_command.py`
- `tests/unit/cli/commands/test_watch_command.py`
- `tests/unit/cli/commands/test_item_command_comprehensive.py`
- `tests/unit/cli/commands/test_export_command.py`
- `tests/unit/cli/commands/test_agents_command.py`
- `tests/unit/cli/commands/test_search_command.py`
- `tests/unit/cli/commands/test_ingest_command.py`

### Key Functionality to Test
- Command execution (success paths, error handling)
- Argument parsing (required args, optional args, flags)
- Output formatting (tables, trees, progress bars)
- Error handling (validation errors, not found errors)
- Integration (storage operations, database queries)

**Effort**: 15-20 hours

---

## Phase 4: TUI Module (24.03% → 85%+)

### Files to Test
1. `tui/adapters/storage_adapter.py` - **24.03%** → 85%+ (138 stmts, 101 missing)
2. `tui/apps/browser.py` - **21.48%** → 85%+ (115 stmts, 87 missing)
3. `tui/apps/dashboard.py` - **18.34%** → 85%+ (141 stmts, 111 missing)
4. `tui/apps/dashboard_v2.py` - **17.02%** → 85%+ (199 stmts, 160 missing)
5. `tui/apps/graph.py` - **20.86%** → 85%+ (123 stmts, 95 missing)
6. `tui/widgets/conflict_panel.py` - **20.45%** → 85%+ (106 stmts, 80 missing)
7. `tui/widgets/sync_status.py` - **26.54%** → 85%+ (132 stmts, 90 missing)
8. `tui/widgets/view_switcher.py` - **39.13%** → 85%+ (19 stmts, 11 missing)
9. `tui/widgets/item_list.py` - **36.36%** → 85%+ (18 stmts, 11 missing)
10. `tui/widgets/graph_view.py` - **46.67%** → 85%+ (13 stmts, 7 missing)
11. `tui/widgets/state_display.py` - **33.33%** → 85%+ (20 stmts, 13 missing)

### Test Files to Create
- `tests/unit/tui/adapters/test_storage_adapter.py`
- `tests/unit/tui/apps/test_browser_app.py`
- `tests/unit/tui/apps/test_dashboard_app.py`
- `tests/unit/tui/apps/test_dashboard_v2_app.py`
- `tests/unit/tui/apps/test_graph_app.py`
- `tests/unit/tui/widgets/test_conflict_panel.py`
- `tests/unit/tui/widgets/test_sync_status.py`
- `tests/unit/tui/widgets/test_view_switcher.py`
- `tests/unit/tui/widgets/test_item_list.py`
- `tests/unit/tui/widgets/test_graph_view.py`
- `tests/unit/tui/widgets/test_state_display.py`

### Key Functionality to Test
- Widget initialization (setup, data loading)
- Business logic (data processing, calculations)
- Event handlers (key handlers, action handlers)
- State management (state updates, state queries)
- Error handling (error states, error recovery)

**Note**: Focus on business logic, not UI rendering. Use Textual's testing utilities.

**Effort**: 7-10 hours

---

## Quick Commands

### Check Current Coverage
```bash
# Overall
coverage report --show-missing | grep TOTAL

# By Module
coverage report --show-missing | grep -E "(repositories|cli|tui|database)"
```

### Run Tests with Coverage
```bash
# Repositories
pytest tests/unit/repositories/ --cov=src/tracertm/repositories --cov-report=term-missing

# Database
pytest tests/unit/database/ tests/unit/core/test_database*.py --cov=src/tracertm/database --cov=src/tracertm/core/database --cov-report=term-missing

# CLI Commands
pytest tests/unit/cli/commands/ --cov=src/tracertm/cli/commands --cov-report=term-missing

# TUI Module
pytest tests/unit/tui/ --cov=src/tracertm/tui --cov-report=term-missing
```

### Generate HTML Report
```bash
pytest --cov=src/tracertm --cov-report=html
open htmlcov/index.html
```

---

## Timeline Estimate

- **Week 1**: Repositories + Database (18-23 hours)
- **Week 2**: CLI Commands Critical (15-20 hours)
- **Week 3**: CLI Commands Medium + TUI (22-30 hours)
- **Week 4**: Finalization & Verification (5-10 hours)

**Total**: ~60-83 hours

---

## Success Metrics

✅ All 4 areas at **85%+ coverage**  
✅ Critical paths tested  
✅ Error handling covered  
✅ Edge cases covered  
✅ Integration tests for complex flows

---

**See**: `COVERAGE_IMPROVEMENT_PLAN_85_PERCENT.md` for detailed plan

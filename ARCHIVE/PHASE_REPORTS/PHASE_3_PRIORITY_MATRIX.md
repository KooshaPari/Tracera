# Phase 3 Coverage Priority Matrix

**Generated**: 2024-12-09
**Scope**: Top 20 uncovered files by business impact
**Target Coverage**: 95-100% in 10 weeks

---

## Priority Matrix: Business Impact vs Effort

```
HIGH IMPACT / MANAGEABLE EFFORT - START HERE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. BulkOperationService     [310 min | 5.2h]  - CRITICAL
2. StatusWorkflowService    [115 min | 1.9h]  - CRITICAL
3. StorageHelper            [455 min | 7.6h]  - CRITICAL
   Subtotal Tier 1:         880 min | 14.7h

HIGH IMPACT / MODERATE EFFORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. DashboardV2              [180 min | 3h]    - HIGH
5. SyncStatusWidget         [120 min | 2h]    - HIGH
6. AdvancedTraceabilityService [100 min | 1.7h] - HIGH
7-12. Import/Export/Analysis Services [1,200 min | 20h] - HIGH

MODERATE IMPACT / MANAGEABLE EFFORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
13-32. TUI Widgets, Utilities, Schemas [1,100 min | 18h] - MEDIUM
```

---

## Ranked Priority List (Top 20 by Business Impact)

### TIER 1: CRITICAL (Blocking other features)

| Rank | Service | File | Statements | Coverage | Effort | Priority |
|------|---------|------|-----------|----------|--------|----------|
| **1** | **BulkOperationService** | `src/tracertm/services/bulk_operation_service.py` | 196 | 0% | 5.2h | **🔴 P0** |
| **2** | **StatusWorkflowService** | `src/tracertm/services/status_workflow_service.py` | 34 | 0% | 1.9h | **🔴 P0** |
| **3** | **StorageHelper** | `src/tracertm/cli/storage_helper.py` | 206 | 0% | 7.6h | **🔴 P0** |

**Subtotal**: 436 statements | 14.7 hours | Required for Phase 3 completion

---

### TIER 2: IMPORTANT (Enable major workflows)

| Rank | Service | File | Statements | Coverage | Effort | Priority |
|------|---------|------|-----------|----------|--------|----------|
| **4** | DashboardV2 | `src/tracertm/tui/apps/dashboard_v2.py` | 190 | 0% | 3h | 🟠 P1 |
| **5** | SyncStatusWidget | `src/tracertm/tui/widgets/sync_status.py` | 127 | 0% | 2h | 🟠 P1 |
| **6** | AdvancedTraceabilityService | `src/tracertm/services/advanced_traceability_enhancements_service.py` | 102 | 0% | 1.7h | 🟠 P1 |
| **7** | ExportImportService | `src/tracertm/services/export_import_service.py` | 88 | 0% | 1.5h | 🟠 P1 |
| **8** | ImpactAnalysisService | `src/tracertm/services/impact_analysis_service.py` | 88 | 0% | 1.5h | 🟠 P1 |
| **9** | TraceabilityMatrixService | `src/tracertm/services/traceability_matrix_service.py` | 81 | 0% | 1.5h | 🟠 P1 |
| **10** | CriticalPathService | `src/tracertm/services/critical_path_service.py` | 80 | 0% | 1.5h | 🟠 P1 |
| **11** | ExportService | `src/tracertm/services/export_service.py` | 79 | 0% | 1.5h | 🟠 P1 |
| **12** | AdvancedAnalyticsService | `src/tracertm/services/advanced_analytics_service.py` | 75 | 0% | 1.5h | 🟠 P1 |

**Subtotal**: ~890 statements | 18 hours | High priority, secondary focus

---

### TIER 3: SUPPORTING (Enhance functionality)

| Rank | Service | File | Statements | Coverage | Effort | Priority |
|------|---------|------|-----------|----------|--------|----------|
| **13** | ApiWebhooksService | `src/tracertm/services/api_webhooks_service.py` | 74 | 0% | 1.5h | 🟡 P2 |
| **14** | GithubImportService | `src/tracertm/services/github_import_service.py` | 74 | 0% | 1.5h | 🟡 P2 |
| **15** | JiraImportService | `src/tracertm/services/jira_import_service.py` | 89 | 0% | 1.5h | 🟡 P2 |
| **16** | CacheService | `src/tracertm/services/cache_service.py` | 88 | 0% | 1.5h | 🟡 P2 |
| **17** | PluginService | `src/tracertm/services/plugin_service.py` | 94 | 0% | 1.5h | 🟡 P2 |
| **18** | ProjectBackupService | `src/tracertm/services/project_backup_service.py` | 92 | 0% | 1.5h | 🟡 P2 |
| **19** | FigmaUtil | `src/tracertm/utils/figma.py` | 96 | 0% | 1.5h | 🟡 P2 |
| **20** | StorageAdapter | `src/tracertm/tui/adapters/storage_adapter.py` | 138 | 0% | 2h | 🟡 P2 |

**Subtotal**: ~845 statements | 13 hours | Lower priority, can parallelize

---

## Implementation Schedule

### Phase 3A: Foundation (Weeks 1-2, 15 hours)
**Goal**: Complete Tier 1 critical path

**Week 1 (Monday-Wednesday)**:
```
Mon-Tue: BulkOperationService (5.2h)
  - bulk_update_preview()      [45 min]
  - bulk_update_items()        [60 min]
  - bulk_delete_items()        [40 min]
  - bulk_create_preview()      [90 min]
  - bulk_create_items()        [75 min]

Wed: StatusWorkflowService (1.9h)
  - validate_transition()      [30 min]
  - update_item_status()       [50 min]
  - get_status_history()       [35 min]
```

**Week 2 (Thursday-Friday + next week)**:
```
Thu-Fri: StorageHelper (7.6h)
  - Singleton pattern (45 min)
  - Project context (60 min)
  - Sync management (75 min)
  - Display formatting (175 min)
  - Error handling (35 min)

SUBTOTAL: 14.7 hours
```

**Deliverable**: 95%+ coverage on Tier 1, all tests passing

---

### Phase 3B: Enhancement (Weeks 3-5, 18 hours)
**Goal**: Complete Tier 2 important features

**Weeks 3-4** (40 hours team capacity):
```
DashboardV2                   [3h]
SyncStatusWidget              [2h]
AdvancedTraceabilityService   [1.7h]
ExportImportService           [1.5h]
ImpactAnalysisService         [1.5h]
TraceabilityMatrixService     [1.5h]
CriticalPathService           [1.5h]
ExportService                 [1.5h]

SUBTOTAL: 18 hours
```

**Deliverable**: 85%+ coverage on Tier 2 services

---

### Phase 3C: Completion (Weeks 6-8, 18 hours)
**Goal**: Complete Tier 3 supporting features

**Weeks 6-7**:
```
Schemas & Factories           [2.5h]
CLI Utilities                 [3.5h]
TUI Widgets & Adapters        [6h]

Weeks 7-8:
Integration Services          [6h]

SUBTOTAL: 18 hours
```

**Deliverable**: 75%+ coverage on Tier 3 services

---

### Phase 3D: Optimization (Weeks 9-10, 5 hours)
**Goal**: Gap filling and validation

```
Test refactoring              [2h]
Edge case coverage            [2h]
Performance baselines         [1h]

SUBTOTAL: 5 hours
```

**Deliverable**: 95%+ coverage across all files, all tests green

---

## Team Allocation Recommendation

### Suggested Team Structure:
```
Lead Developer (40 hours):
  → BulkOperationService (5.2h)
  → StatusWorkflowService (1.9h)
  → StorageHelper (7.6h)
  → DashboardV2 (3h)
  → SyncStatusWidget (2h)
  → Optimization (5h)

Developer 2 (40 hours):
  → AdvancedTraceabilityService (1.7h)
  → ExportImportService (1.5h)
  → ImpactAnalysisService (1.5h)
  → TraceabilityMatrixService (1.5h)
  → CriticalPathService (1.5h)
  → ExportService (1.5h)
  → AdvancedAnalyticsService (1.5h)
  → TUI Widgets batch 1 (15h)

Developer 3 (40 hours):
  → ApiWebhooksService (1.5h)
  → GithubImportService (1.5h)
  → JiraImportService (1.5h)
  → CacheService (1.5h)
  → PluginService (1.5h)
  → ProjectBackupService (1.5h)
  → Figma utils (1.5h)
  → TUI Widgets batch 2 (15h)
  → Schemas & utilities (10h)

Total: 120 hours (distributed across 3 devs, 40 hours each)
```

---

## Success Metrics

### By Milestone:

**End of Week 2**:
- Tier 1 coverage: 95%+ ✓
- Tests added: 200+
- Stories completed: 3/3

**End of Week 5**:
- Tier 1+2 coverage: 90%+ ✓
- Tests added: 500+
- Stories completed: 12/12

**End of Week 8**:
- Tier 1+2+3 coverage: 85%+ ✓
- Tests added: 800+
- Stories completed: 20+/20+

**End of Week 10**:
- Overall coverage: 95%+ ✓
- All tests: 100% passing ✓
- Performance: Baselines set ✓

---

## Known Dependencies

### Critical Dependency Order:
1. **StatusWorkflowService** (independent)
2. **BulkOperationService** (depends on: Item, Event, StatusWorkflowService)
3. **StorageHelper** (depends on: all storage/CLI infrastructure)
4. **Dashboard services** (depend on: Tier 1 + models)
5. **Import/Export services** (depend on: Tier 1 + storage)
6. **Integration services** (mostly independent)

### Parallel Work Possible:
- Tier 2 and 3 services can be developed in parallel after Tier 1 complete
- CLI utilities independent from API services
- TUI widgets can be tested with mocked storage

---

## Risk Assessment

### High Risk Areas:
- **BulkOperationService**: CSV parsing edge cases, transaction atomicity
- **StorageHelper**: Decorator patterns, singleton isolation
- **Dashboard**: TUI framework integration, async handling

### Medium Risk Areas:
- Import/export services: External API mocking
- Traceability services: Complex query logic
- Sync widgets: State management

### Low Risk Areas:
- Schemas: Simple data validation
- CLI utilities: Self-contained logic
- Cache service: Standard patterns

---

## Quick Links

- **Full Analysis**: `PHASE_3_COVERAGE_GAP_ANALYSIS.md`
- **Quick Reference**: `PHASE_3_COVERAGE_QUICK_REFERENCE.md`
- **Coverage Report**: `coverage.json` / `htmlcov/index.html`

---

## Next Steps

1. **Immediate** (Today):
   - Review priority matrix with team
   - Assign developers to tiers
   - Set up test fixtures

2. **This Week**:
   - Begin Tier 1 implementation
   - Create test templates
   - Set up CI integration

3. **Next Week**:
   - Complete Tier 1 coverage
   - Start Tier 2 services
   - Track coverage metrics

---

**Document Version**: 1.0
**Classification**: Team Planning
**Review Cycle**: Weekly during Phase 3

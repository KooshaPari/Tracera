# Hatchet References Audit

Complete audit of all Hatchet references in the TraceRTM codebase.

**Date**: 2026-01-31
**Purpose**: Document all files requiring migration from Hatchet to Temporal
**Status**: Ready for Migration

---

## Executive Summary

**Total Files Found**: 106 files containing "hatchet" references
**Critical Files Requiring Code Changes**: 4 files
**Documentation Files**: 102 files (reference only)

### Migration Priority

1. **HIGH** - Active Code (4 files)
2. **MEDIUM** - Dependencies (1 file)
3. **LOW** - Documentation (102 files - update references only)

---

## Active Code Files (HIGH PRIORITY)

### 1. `/src/tracertm/services/hatchet_service.py`

**Status**: Replace with `temporal_service.py`
**Lines**: 113 lines
**Dependencies**: Used by `main.py`

**Current Functionality**:
- `HatchetService` class for workflow orchestration
- Workflow triggering via HTTP API
- Cron schedule management
- Health checks

**Migration Actions**:
```bash
# Action 1: Update import in main.py
# FROM: from tracertm.services.hatchet_service import HatchetService
# TO:   from tracertm.services.temporal_service import TemporalService

# Action 2: Archive hatchet_service.py
mv src/tracertm/services/hatchet_service.py src/tracertm/services/_archived_hatchet_service.py

# Action 3: Update all service initialization
# FROM: hatchet_service = HatchetService()
# TO:   temporal_service = TemporalService()
```

**Equivalent Temporal Implementation**: ✅ Already exists in `temporal_service.py`

---

### 2. `/src/tracertm/workflows/hatchet_worker.py`

**Status**: Archive or delete
**Lines**: 133 lines
**Dependencies**: None (legacy worker)

**Current Functionality**:
- Hatchet worker registration
- Task decorators for workflows
- Workflow execution handlers

**Migration Actions**:
```bash
# Action 1: Archive the file
mv src/tracertm/workflows/hatchet_worker.py src/tracertm/workflows/_archived_hatchet_worker.py

# Action 2: Verify Procfile uses new worker
# CORRECT: temporal_worker: python -m tracertm.workflows.worker
# REMOVE:  hatchet_worker: python -m tracertm.workflows.hatchet_worker (if exists)
```

**Equivalent Temporal Implementation**: ✅ Already exists in `worker.py`

---

### 3. `/src/tracertm/api/main.py`

**Status**: Update import
**Line**: 1 import statement

**Current Code**:
```python
from tracertm.services.hatchet_service import HatchetService
```

**Migration Actions**:
```python
# Replace import
from tracertm.services.temporal_service import TemporalService

# Update service initialization (search for HatchetService())
# FROM: hatchet = HatchetService()
# TO:   temporal = TemporalService()

# Update health check endpoints
# FROM: hatchet_health = await hatchet.health_check()
# TO:   temporal_health = await temporal.health_check()
```

**Search Pattern**:
```bash
grep -n "HatchetService\|hatchet\." src/tracertm/api/main.py
```

---

### 4. `/src/tracertm/preflight.py`

**Status**: Update preflight checks
**Expected Changes**: Remove Hatchet checks, add Temporal checks

**Migration Actions**:
```python
# Remove Hatchet preflight checks
# Search for: HATCHET, hatchet

# Add Temporal preflight check
@dataclass(frozen=True)
class PreflightCheck:
    name = "Temporal Server"
    url = os.getenv("TEMPORAL_HOST", "localhost:7233")
    required = False  # Optional for dev
    kind = "tcp"
    timeout = 2.0
```

**Search Pattern**:
```bash
grep -n -i "hatchet" src/tracertm/preflight.py
```

---

## Dependency Files (MEDIUM PRIORITY)

### 5. `/pyproject.toml`

**Status**: Remove Hatchet dependency
**Lines**: 2 references

**Current Dependencies**:
```toml
dependencies = [
    # ... other deps
    "hatchet-sdk>=1.22.13",
]

[project.optional-dependencies]
full = [
    # ... other deps
    "hatchet-sdk>=1.22.13",
]
```

**Migration Actions**:
```bash
# Action 1: Remove hatchet-sdk from dependencies
sed -i '' '/hatchet-sdk/d' pyproject.toml

# Action 2: Verify temporalio is in dependencies
grep "temporalio" pyproject.toml
# Expected: "temporalio>=1.0.0"

# Action 3: Update lockfile
uv lock --upgrade
```

**Note**: Temporal Python SDK should already be in dependencies. Verify before removing Hatchet.

---

## Documentation Files (LOW PRIORITY)

### Files Requiring Updates

All documentation files below contain references to Hatchet. These should be updated to:
1. Replace "Hatchet" with "Temporal"
2. Update workflow examples
3. Update setup instructions
4. Add migration notes where appropriate

**Category 1: Setup Guides** (18 files)
```
docs/guides/quick-start/QUICK_START.md
docs/guides/LOCAL_SERVICES_SETUP.md
docs/guides/ENVIRONMENT_AUDIT_AND_CONSOLIDATION_PLAN.md
docs/guides/00_START_HERE_UNIFIED_PLAN.md
docs/guides/FINAL_SETUP_GUIDE.md
docs/guides/MANUAL_SETUP_GUIDE.md
docs/guides/FINAL_CHECKLIST.md
docs/guides/INFRASTRUCTURE_QUICK_REFERENCE.md
docs/guides/INFRASTRUCTURE_DOCUMENTATION_INDEX.md
docs/guides/README_START_HERE.md
docs/guides/PRODUCTION_READINESS_CHECKLIST.md
```

**Category 2: Implementation Guides** (15 files)
```
docs/guides/DELEGATION_CLIENTS_IMPLEMENTATION.md
docs/guides/NGINX_GATEWAY_IMPLEMENTATION.md
docs/guides/BACKEND_CONSOLIDATION_ROADMAP.md
docs/implementation/FULL_INFRASTRUCTURE_SETUP.md
docs/INDEX_IMPLEMENTATION_STATUS.md
docs/IMPLEMENTATION_ANALYSIS_FINAL.md
docs/IMPLEMENTATION_STATUS.md
docs/IMPLEMENTATION_STATUS_QUICK_REFERENCE.md
```

**Category 3: Reports & Summaries** (25 files)
```
docs/reports/PHASE_5_TEMPORAL_IMPLEMENTATION_COMPLETE.md
docs/reports/TEMPORAL_MIGRATION_ANALYSIS.md
docs/reports/BACKEND_CONSOLIDATION_COMPLETE.md
docs/reports/BACKEND_CONSOLIDATION_PHASE_1_COMPLETE.md
docs/reports/PHASE_1.1_ROUTES_REGISTRATION_SUMMARY.md
docs/reports/PHASE_1.1_FILES_MODIFIED.md
docs/reports/IMPLEMENTATION_SUMMARY_VALIDATION_CONFIG_FLAGS.md
.trace/COMPLETE_SESSION_SUMMARY.md
.trace/ALL_ISSUES_FIXED_SUMMARY.md
.trace/FINAL_STATUS_SUMMARY.md
.trace/BACKEND_CONSOLIDATION_IMPLEMENTATION_COMPLETE.md
.trace/PHASE_1_4_COMPLETION_SUMMARY.md
.trace/PHASE_1_4_IMPLEMENTATION.md
```

**Category 4: Research & Analysis** (12 files)
```
docs/research/HATCHET_TEMPORAL_EVALUATION.md
docs/research/INDEX.md
docs/research/CODEBASE_AUDIT_AND_REMAINING_WORK.md
docs/research/CODEBASE_COMPLETION_AUDIT.md
docs/research/FEATURE_GAP_ANALYSIS_SUMMARY.md
docs/research/FEATURE_GAP_ANALYSIS_COMPLETE.md
docs/research/PROJECT_COMPLETION_REPORT.md
```

**Category 5: Archive/Historical** (32 files)
```
ARCHIVE/DOCUMENTATION/docs-site/content/docs/03-development/05-deployment/07-production-runbook/index.mdx
docs-site/content/docs/03-development/05-deployment/07-production-runbook/index.mdx
docs/other/*.md (various historical files)
docs/07-reports/archive/*.md (archived reports)
docs/archive/test-docs/*.md (test documentation)
```

**Category 6: Frontend Files** (3 files)
```
frontend/apps/web/src/api/client.ts
frontend/apps/web/src/components/CommandPalette.tsx
frontend/apps/web/src/pages/projects/views/WorkflowRunsView.tsx
```

**Category 7: Configuration Files** (2 files)
```
nginx/conf.d/tracertm.conf
ARCHIVE/DOCKER/docker-compose.prod.yml
```

---

## Migration Task Checklist

### Phase 1: Core Service Migration

- [ ] **Task 1.1**: Update `src/tracertm/api/main.py`
  - Replace `HatchetService` import with `TemporalService`
  - Update service initialization
  - Update health check endpoints
  - Test API startup

- [ ] **Task 1.2**: Update `src/tracertm/preflight.py`
  - Remove Hatchet preflight checks
  - Add Temporal server checks
  - Test preflight validation

- [ ] **Task 1.3**: Archive legacy files
  - Move `hatchet_service.py` to archived
  - Move `hatchet_worker.py` to archived
  - Update `.gitignore` if needed

- [ ] **Task 1.4**: Update dependencies
  - Remove `hatchet-sdk` from `pyproject.toml`
  - Verify `temporalio` is in dependencies
  - Run `uv lock --upgrade`
  - Test environment installation

### Phase 2: Verification & Testing

- [ ] **Task 2.1**: Test Temporal service
  - Start Temporal server
  - Start Temporal worker
  - Execute test workflow
  - Verify in Temporal UI

- [ ] **Task 2.2**: Test API endpoints
  - Test workflow start endpoint
  - Test workflow status endpoint
  - Test health check endpoint

- [ ] **Task 2.3**: Integration testing
  - Test all graph workflows
  - Test integration sync workflows
  - Verify error handling

### Phase 3: Documentation Updates

- [ ] **Task 3.1**: Update quick-start guides (18 files)
  - Replace Hatchet references
  - Update setup instructions
  - Update environment variables

- [ ] **Task 3.2**: Update implementation guides (15 files)
  - Update workflow examples
  - Update API examples
  - Update troubleshooting sections

- [ ] **Task 3.3**: Update reports (25 files)
  - Add migration completion notes
  - Update status indicators
  - Archive outdated reports

- [ ] **Task 3.4**: Update research docs (12 files)
  - Note migration completion
  - Update comparison matrices
  - Archive evaluation docs

- [ ] **Task 3.5**: Update frontend references (3 files)
  - Update workflow status displays
  - Update API client calls
  - Update UI labels

- [ ] **Task 3.6**: Update configuration (2 files)
  - Update nginx config if needed
  - Update docker-compose if needed

### Phase 4: Cleanup

- [ ] **Task 4.1**: Remove archived files
  - After 30 days of successful Temporal usage
  - Create backup before deletion

- [ ] **Task 4.2**: Update main README
  - Remove Hatchet references
  - Add Temporal setup instructions
  - Update architecture diagrams

- [ ] **Task 4.3**: Update CHANGELOG
  - Document Hatchet removal
  - Document Temporal adoption
  - List breaking changes

---

## Testing Strategy

### Unit Tests

```bash
# Test temporal service
pytest tests/services/test_temporal_service.py

# Test workflows
pytest tests/workflows/test_workflows.py

# Test activities
pytest tests/workflows/test_activities.py
```

### Integration Tests

```bash
# Test end-to-end workflow execution
pytest tests/integration/test_temporal_integration.py

# Test API endpoints
pytest tests/api/test_workflow_endpoints.py
```

### Manual Testing

```bash
# 1. Start all services
overmind start

# 2. Verify Temporal UI
open http://localhost:8233

# 3. Execute test workflow
temporal workflow execute \
  --type GraphSnapshotWorkflow \
  --task-queue tracertm-tasks \
  --input '{"project_id": "test", "graph_id": "test"}'

# 4. Verify in UI
# Check workflow appears in Temporal UI
# Verify completion status
```

---

## Rollback Plan

If migration fails, rollback steps:

```bash
# 1. Restore hatchet_service.py
git restore src/tracertm/services/hatchet_service.py

# 2. Restore hatchet_worker.py
git restore src/tracertm/workflows/hatchet_worker.py

# 3. Restore main.py imports
git restore src/tracertm/api/main.py

# 4. Restore dependencies
git restore pyproject.toml
uv lock

# 5. Restart services
overmind restart
```

---

## Success Criteria

Migration is complete when:

1. ✅ All code references to Hatchet are removed
2. ✅ Temporal service is functional and tested
3. ✅ All workflows execute successfully
4. ✅ API endpoints work correctly
5. ✅ Documentation is updated
6. ✅ Dependencies are cleaned up
7. ✅ Tests pass
8. ✅ Production deployment is successful

---

## Timeline Estimate

- **Phase 1** (Core Migration): 2-4 hours
- **Phase 2** (Testing): 2-3 hours
- **Phase 3** (Documentation): 3-5 hours
- **Phase 4** (Cleanup): 1-2 hours

**Total**: 8-14 hours of focused work

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Service downtime | Low | High | Blue-green deployment |
| Workflow failures | Medium | High | Comprehensive testing |
| Missing dependencies | Low | Medium | Lock file management |
| Documentation gaps | Medium | Low | Systematic review |

---

## Next Steps

1. **Review this audit** with team
2. **Create migration branch**: `git checkout -b migrate/hatchet-to-temporal`
3. **Execute Phase 1** tasks
4. **Validate functionality**
5. **Update documentation**
6. **Merge to main**

---

## Related Documentation

- [HATCHET_TO_TEMPORAL_MIGRATION.md](../guides/HATCHET_TO_TEMPORAL_MIGRATION.md) - Migration guide
- [TEMPORAL_SETUP.md](../guides/TEMPORAL_SETUP.md) - Setup instructions
- [TEMPORAL_QUICK_REFERENCE.md](../reference/TEMPORAL_QUICK_REFERENCE.md) - Quick reference

---

**Last Updated**: 2026-01-31
**Audited By**: TraceRTM Development Team
**Status**: Ready for Migration

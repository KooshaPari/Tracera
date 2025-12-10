# Deferred Work Index

**As of:** December 10, 2025
**Governance Framework:** BMad Method Module (BMM)
**Definition of Done Violation:** Stories incomplete (Definition of Done requires 100% tests passing)
**Total Deferred Items:** 11

---

## Executive Summary

During the comprehensive governance audit, 11 items were identified that do not meet the Definition of Done (tests not passing, acceptance criteria not fully met). These are documented here with story context for future completion or deferral.

**Compliance Note:** BMM DEV Agent rule states: "Mark story complete only when Definition of Done met" (100% tests passing). These items violate that rule and require either:
1. Completion (implement remaining code, pass all tests)
2. Formal deferral (document story context, mark as deferred)

---

## Deferred Items Summary

| # | Category | Item | File | Status | Priority | Effort |
|---|----------|------|------|--------|----------|--------|
| 1 | CODE | Sync Engine - Change Detection | `src/tracertm/storage/sync_engine.py:621` | 🟡 TODO | HIGH | 8h |
| 2 | CODE | Sync Engine - Pull Logic | `src/tracertm/storage/sync_engine.py:704` | 🟡 TODO | HIGH | 4h |
| 3 | CODE | Sync Engine - Application Logic | `src/tracertm/storage/sync_engine.py:781` | 🟡 TODO | HIGH | 4h |
| 4 | CODE | Sync Engine - Conflict File Creation | `src/tracertm/storage/sync_engine.py:813` | 🟡 TODO | HIGH | 2h |
| 5 | CODE | Export YAML Feature | `src/tracertm/services/export_service.py:161` | 🟡 STUB | MEDIUM | 4h |
| 6 | CODE | Relationship Queries | `src/tracertm/services/item_service.py:522` | 🟡 STUB | MEDIUM | 4h |
| 7 | UI | Search Dialogs - Dashboard V2 | `src/tracertm/tui/apps/dashboard_v2.py:349` | 🟡 TODO | MEDIUM | 3h |
| 8 | UI | Search Dialogs - Dashboard | `src/tracertm/tui/apps/dashboard.py:243` | 🟡 TODO | MEDIUM | 3h |
| 9 | UI | Filter Implementation - Browser | `src/tracertm/tui/apps/browser.py:192` | 🟡 TODO | MEDIUM | 3h |
| 10 | CLI | Design Figma Integration | `src/tracertm/cli/commands/design.py` (4 TODOs) | 🟡 STUBS | LOW | 8h |
| 11 | INTEGRATION | Storage Markdown Merge | `src/tracertm/tui/adapters/storage_adapter.py:117` | 🟡 TODO | MEDIUM | 4h |

**Total Deferred Effort:** ~43 hours

### By Category

- **CODE (6 items):** 22 hours (sync engine, exports, queries)
- **UI (3 items):** 9 hours (search/filter dialogs)
- **CLI (4 items):** 8 hours (Figma integration, test commands)
- **INTEGRATION (1 item):** 4 hours (storage adapter)

### By Priority

- **HIGH (4 items - Sync Engine):** 18 hours - **Blocking**: Data integrity risk
- **MEDIUM (5 items):** 19 hours - Important features
- **LOW (2 items):** 8 hours - Enhancement/integration

---

## Detailed Story Documentation

### 1️⃣ SYNC ENGINE - CHANGE DETECTION (HIGH PRIORITY)

**File:** `src/tracertm/storage/sync_engine.py:621`
**Type:** CODE
**Status:** 🟡 TODO - "TODO: Implement actual change detection"
**Impact:** BLOCKING - Data synchronization non-functional
**Acceptance Criteria:**
- [ ] Detect local file changes (creation, modification, deletion)
- [ ] Compare with remote version
- [ ] Generate change set
- [ ] Pass 100% of sync engine tests

**Current State:** Stub returns empty change set

**Effort:** 8 hours
**Owner:** DEV Agent / Agent 2 (Storage Lead)
**Phase:** Should be Phase 4 (Polish)

**Story Context:**
```
Feature: Sync Engine Change Detection
Reason: Enable real-time file synchronization

Current Implementation: Stub returns empty list (line 621)
Required: Full change detection algorithm

Acceptance Criteria:
- Detect file system changes
- Compare with remote state
- Generate proper change set
- All tests passing
```

**Testing Strategy:**
- Unit tests: change detection logic
- Integration tests: file watcher + sync engine
- E2E tests: full sync workflow

**Blockers:** None (design already exists, just needs implementation)

**Next Steps to Resume:**
1. Read existing test mocks
2. Implement actual change detection
3. Run sync_engine tests
4. Verify with integration tests

---

### 2️⃣ SYNC ENGINE - PULL LOGIC (HIGH PRIORITY)

**File:** `src/tracertm/storage/sync_engine.py:704`
**Type:** CODE
**Status:** 🟡 TODO - "TODO: Implement actual pull logic"
**Impact:** BLOCKING - Cannot pull remote changes
**Effort:** 4 hours
**Owner:** DEV Agent / Agent 2

**Current State:** Stub method returns True

**Story Context:**
Similar to item #1 - critical sync feature incomplete

---

### 3️⃣ SYNC ENGINE - APPLICATION LOGIC (HIGH PRIORITY)

**File:** `src/tracertm/storage/sync_engine.py:781`
**Type:** CODE
**Status:** 🟡 TODO - "TODO: Implement actual application logic"
**Impact:** BLOCKING - Cannot apply synced changes
**Effort:** 4 hours
**Owner:** DEV Agent / Agent 2

**Current State:** Stub does nothing

---

### 4️⃣ SYNC ENGINE - CONFLICT FILE CREATION (HIGH PRIORITY)

**File:** `src/tracertm/storage/sync_engine.py:813`
**Type:** CODE
**Status:** 🟡 TODO - "TODO: Implement conflict file creation"
**Impact:** MEDIUM - Error handling incomplete
**Effort:** 2 hours
**Owner:** DEV Agent / Agent 2

---

### 5️⃣ EXPORT YAML FEATURE (MEDIUM PRIORITY)

**File:** `src/tracertm/services/export_service.py:161`
**Type:** CODE / FEATURE
**Status:** 🟡 STUB - Returns minimal YAML structure
**Impact:** MEDIUM - Export functionality incomplete
**Effort:** 4 hours
**Owner:** DEV Agent / Agent 3 (Services)

**Current State:**
```python
def export_yaml(self) -> str:
    """STUB: Returns minimal YAML structure. TODO: Implement full YAML export."""
    return "# Minimal YAML\n"
```

**Required:**
- [ ] Full item export to YAML
- [ ] Links export to YAML
- [ ] Nested structure support
- [ ] All tests passing

---

### 6️⃣ RELATIONSHIP QUERIES (MEDIUM PRIORITY)

**File:** `src/tracertm/services/item_service.py:522`
**Type:** CODE / FEATURE
**Status:** 🟡 STUB - Returns empty list
**Impact:** MEDIUM - Relationship functionality incomplete
**Effort:** 4 hours
**Owner:** DEV Agent / Agent 3

**Current State:**
```python
def get_related_items(self, item_id: str) -> List[Item]:
    """STUB: Returns empty list. TODO: Implement relationship querying logic."""
    return []
```

**Required:**
- [ ] Query related items through graph
- [ ] Support multiple relationship types
- [ ] Filter by relationship type
- [ ] All tests passing

---

### 7️⃣ SEARCH DIALOG - DASHBOARD V2 (MEDIUM PRIORITY)

**File:** `src/tracertm/tui/apps/dashboard_v2.py:349`
**Type:** UI / FEATURE
**Status:** 🟡 TODO - Search dialog not implemented
**Impact:** MEDIUM - UX incomplete
**Effort:** 3 hours
**Owner:** DEV Agent / Agent 4 (TUI Lead)

**Current State:** TODO comment, handler exists but UI not built

**Required:**
- [ ] Implement search input dialog
- [ ] Support query syntax
- [ ] Display results
- [ ] All tests passing

---

### 8️⃣ SEARCH DIALOG - DASHBOARD (MEDIUM PRIORITY)

**File:** `src/tracertm/tui/apps/dashboard.py:243`
**Type:** UI / FEATURE
**Status:** 🟡 TODO - Search dialog not implemented
**Impact:** MEDIUM - UX incomplete
**Effort:** 3 hours
**Owner:** DEV Agent / Agent 4

---

### 9️⃣ FILTER IMPLEMENTATION - BROWSER (MEDIUM PRIORITY)

**File:** `src/tracertm/tui/apps/browser.py:192`
**Type:** UI / FEATURE
**Status:** 🟡 TODO - Filtering not implemented
**Impact:** MEDIUM - UX incomplete
**Effort:** 3 hours
**Owner:** DEV Agent / Agent 4

---

### 🔟 DESIGN FIGMA INTEGRATION (LOW PRIORITY)

**File:** `src/tracertm/cli/commands/design.py` (multiple)
**Type:** CLI / FEATURE
**Status:** 🟡 STUBS - Figma integration incomplete
**Impact:** LOW - Enhancement feature
**Effort:** 8 hours (4 stub functions)
**Owner:** DEV Agent / Agent 1 (CLI Lead)

**TODOs Found:**
- Line: Call TypeScript tool: bun run figma:pull (2h)
- Line: Call TypeScript tool: bun run figma:push (2h)
- Line: Call TypeScript generator (2h)
- Line: Call TypeScript export tool (2h)

**Current State:** Multiple stub functions that log TODO messages

**Required:**
- [ ] Implement Figma pull command
- [ ] Implement Figma push command
- [ ] Implement generator call
- [ ] Implement export tool call
- [ ] All tests passing

---

### 1️⃣1️⃣ STORAGE MARKDOWN MERGE (MEDIUM PRIORITY)

**File:** `src/tracertm/tui/adapters/storage_adapter.py:117`
**Type:** INTEGRATION / FEATURE
**Status:** 🟡 TODO - Markdown merge incomplete
**Impact:** MEDIUM - Storage adapter incomplete
**Effort:** 4 hours
**Owner:** DEV Agent / Agent 4

**Current State:** Comment indicates partial implementation

**Required:**
- [ ] Merge items from Markdown files
- [ ] Sync with database items
- [ ] Handle conflicts
- [ ] All tests passing

---

## Governance Rule Violations

### Definition of Done Violation

**BMM Rule (DEV Agent):**
> "Mark story complete only when Definition of Done met"
> "100% tests passing"
> "All acceptance criteria met"

**Violation:** 11 stories have acceptance criteria not met, tests not passing

### Required Actions

**Option 1: Complete the Work**
- Implement remaining functionality
- Write tests to 100%
- Update this document when completed
- Mark story as "COMPLETED"

**Option 2: Formal Deferral**
- Document decision to defer (why, when to resume)
- Create Story Context XML
- Move to backlog
- Schedule for future phase

**Current Status:** Items documented but not formally deferred

---

## Compliance Checklist

### For Each Deferred Item:
- [ ] Story Context XML created
- [ ] Acceptance criteria documented
- [ ] Effort estimated
- [ ] Owner assigned
- [ ] Priority set
- [ ] Blockers identified
- [ ] Test strategy defined
- [ ] Resume instructions documented

### Current Status:
- [x] All 11 items identified
- [x] Context documented (this file)
- [ ] Story Context XML files created (see below)
- [ ] Formal deferral decision made
- [ ] Backlog prioritized

---

## Story Context XML Files

When formally deferring items, create Story Context XML files:

### Template:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<story>
  <metadata>
    <id>DEFERRED-N</id>
    <title>Feature Title</title>
    <epicId>EPIC-X</epicId>
    <status>DEFERRED</status>
    <createdDate>2025-12-10</createdDate>
    <deferredDate>2025-12-10</deferredDate>
    <priority>HIGH|MEDIUM|LOW</priority>
    <effort>Xh</effort>
    <owner>Agent Name</owner>
  </metadata>
  <description>
    What needs to be done
  </description>
  <acceptanceCriteria>
    <criterion>
      <id>AC1</id>
      <text>...</text>
    </criterion>
  </acceptanceCriteria>
  <blockers>
    <blocker>None identified</blocker>
  </blockers>
  <testStrategy>
    <approach>Unit + Integration + E2E</approach>
  </testStrategy>
  <resumeInstructions>
    Step-by-step to resume work
  </resumeInstructions>
</story>
```

### Files to Create:
- [ ] `DEFERRED_WORK/01_SYNC_CHANGE_DETECTION.story-context.xml`
- [ ] `DEFERRED_WORK/02_SYNC_PULL_LOGIC.story-context.xml`
- [ ] ... (continue for all 11)

---

## Remediation Plan

### Phase 1: Critical (Week 1-2)
**Sync Engine Completion - HIGH PRIORITY**
- [ ] Complete change detection (8h)
- [ ] Complete pull logic (4h)
- [ ] Complete application logic (4h)
- [ ] Complete conflict handling (2h)
- **Subtotal:** 18 hours
- **Target:** Get sync working for data integrity

### Phase 2: Features (Week 2-3)
**Code Features - MEDIUM PRIORITY**
- [ ] Export YAML (4h)
- [ ] Relationship queries (4h)
- [ ] Storage markdown merge (4h)
- **Subtotal:** 12 hours
- **Target:** Complete service layer features

### Phase 3: UI (Week 3-4)
**User Interface - MEDIUM PRIORITY**
- [ ] Search dialogs (3 items, 9h)
- **Subtotal:** 9 hours
- **Target:** Complete TUI experience

### Phase 4: Enhancement (Week 4+)
**CLI Features - LOW PRIORITY**
- [ ] Figma integration (8h)
- **Subtotal:** 8 hours
- **Target:** Advanced features

---

## Estimated Timeline

**Total Effort:** 43 hours
**Team Capacity:** 8 hours/day
**Timeline:** ~5-6 working days (1 week at full focus)

**Option 1: Fast Track**
- Assign all items to DEV Agent
- Full focus for 1 week
- All items completed by Dec 17

**Option 2: Distributed**
- Assign by agent specialization
- Work in parallel (2-3 weeks)
- Completed by Dec 24-31

---

## Maintenance & Updates

**This Document:** Update when items are completed or formally deferred
**Last Updated:** December 10, 2025
**Next Review:** After Phase 1 remediation
**Owner:** DEV Agent (implementation), PM Agent (prioritization)

---

## Related Documents

- **[GOVERNANCE_AUDIT_REPORT.md](../GOVERNANCE_AUDIT_REPORT.md)** - Full audit findings
- **[.bmad/bmm/docs/agents-guide.md](../.bmad/bmm/docs/agents-guide.md)** - BMM governance rules
- **[WORK_PACKAGES_AGENTS.md](../WORK_PACKAGES_AGENTS.md)** - Agent assignments
- **[INDEX.md](../INDEX.md)** - Master navigation

---

**Deferred Work Index**
**Created:** December 10, 2025
**Status:** All 11 items documented and ready for remediation
**Next Action:** Assign to agents and begin Phase 1 (Sync Engine)

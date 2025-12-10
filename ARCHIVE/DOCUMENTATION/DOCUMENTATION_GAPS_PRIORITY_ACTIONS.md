# Documentation Gaps - Priority Actions

**Date:** 2025-01-XX  
**Status:** ⚠️ **45% Complete - Action Required**

---

## Executive Summary

**Documentation Coverage:** ~45% of CLI/MD-first requirements

**Critical Finding:** 21 new commands from Epic 3-8 are **completely missing** from user-facing documentation (CLI_USER_GUIDE.md, CLI_API_REFERENCE.md, CLI_TUTORIAL.md, CLI_EXAMPLES.md).

---

## Immediate Actions (High Priority)

### Action 1: Update CLI Reference ⚠️ CRITICAL

**File:** `docs/06-api-reference/CLI_API_REFERENCE.md`

**Missing Commands to Add:**
1. `rtm query` - Query with filters (FR29, FR21, FR49)
2. `rtm saved-queries` - Saved queries (FR65)
3. `rtm link detect-cycles` - Cycle detection (FR22)
4. `rtm link auto-link` - Auto-linking (FR18)
5. `rtm dashboard` - Multi-project dashboard (FR50)
6. `rtm project export` - Project export (FR53)
7. `rtm project import` - Project import (FR53)
8. `rtm history --at` - Temporal queries (FR56, FR59)
9. `rtm history rollback` - Rollback (FR57)
10. `rtm search` (enhanced) - Enhanced search (FR60-FR67)
11. `rtm progress show` - Progress (FR68, FR69)
12. `rtm progress blocked` - Blocked items (FR70)
13. `rtm progress stalled` - Stalled items (FR71)
14. `rtm progress velocity` - Velocity (FR73)
15. `rtm progress report` - Reports (FR72)
16. `rtm import json` - JSON import (FR78)
17. `rtm import yaml` - YAML import (FR79)
18. `rtm import jira` - Jira import (FR80)
19. `rtm import github` - GitHub import (FR81)

**Estimated Time:** 4-6 hours

---

### Action 2: Update CLI User Guide ⚠️ CRITICAL

**File:** `docs/04-guides/CLI_USER_GUIDE.md`

**Missing Commands:** Same 19 commands as Action 1

**Estimated Time:** 4-6 hours

---

### Action 3: Expand CLI Tutorial ⚠️ HIGH

**File:** `docs/01-getting-started/CLI_TUTORIAL.md`

**Missing Tutorials:**
1. Tutorial 6: Querying Items
2. Tutorial 7: Saved Queries
3. Tutorial 8: Progress Tracking
4. Tutorial 9: History & Rollback
5. Tutorial 10: Importing Data
6. Tutorial 11: Multi-Project Management
7. Tutorial 12: Advanced Workflows

**Estimated Time:** 4-6 hours

---

### Action 4: Expand CLI Examples ⚠️ HIGH

**File:** `docs/04-guides/CLI_EXAMPLES.md`

**Missing Examples:**
1. Query examples
2. Saved queries examples
3. Progress tracking examples
4. History and temporal queries examples
5. Import examples (Jira, GitHub)
6. Cross-project query examples
7. Dashboard examples

**Estimated Time:** 3-4 hours

---

## Medium Priority Actions

### Action 5: Create Example Projects

**New Files Needed:**
1. `docs/examples/simple-todo-app.md` - Simple TODO app (10 features, 1 view)
2. `docs/examples/medium-web-app.md` - Medium web app (50 features, 4 views)
3. `docs/examples/complex-system.md` - Complex system (200+ features, 8 views)
4. `docs/examples/multi-project-setup.md` - Multi-project setup (3 projects, shared agents)

**Estimated Time:** 6-8 hours

---

### Action 6: Complete Migration Guides

**Files to Create/Update:**
1. `docs/04-guides/migration-jira.md` - Jira import guide
2. `docs/04-guides/migration-github.md` - GitHub import guide
3. `docs/04-guides/migration-spreadsheet.md` - CSV import guide
4. `docs/04-guides/migration-notion.md` - Notion migration guide (if needed)

**Estimated Time:** 4-6 hours

---

### Action 7: Expand Agent Integration Guide

**File to Create/Update:**
- `docs/04-guides/agent-integration-guide.md`

**Content Needed:**
- Python API comprehensive reference
- Agent coordination patterns
- Best practices
- Code examples
- Troubleshooting

**Estimated Time:** 4-6 hours

---

## Low Priority Actions

### Action 8: Generate Man Pages

**Implementation:**
- Create man page generation script
- Generate from help text
- Test `man rtm` command

**Estimated Time:** 4-6 hours

---

## Summary

**Total Estimated Effort:** 29-42 hours

**Priority Order:**
1. Update CLI Reference (4-6h) - **CRITICAL**
2. Update CLI User Guide (4-6h) - **CRITICAL**
3. Expand CLI Tutorial (4-6h) - **HIGH**
4. Expand CLI Examples (3-4h) - **HIGH**
5. Create Example Projects (6-8h) - **MEDIUM**
6. Complete Migration Guides (4-6h) - **MEDIUM**
7. Expand Agent Integration Guide (4-6h) - **MEDIUM**
8. Generate Man Pages (4-6h) - **LOW**

---

**Status:** ⚠️ **Action Required - 21 Commands Missing from Documentation**

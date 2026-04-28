# TraceRTM Documentation System Architecture

**Version:** 1.0
**Author:** Claude (Agent) for Team Lead
**Date:** 2026-02-12
**Status:** Draft — Awaiting Team Lead Approval

---

## Executive Summary

This document defines the comprehensive documentation system architecture for TraceRTM, a production-grade traceability management platform with 50+ models, 90+ services, 200+ REST APIs, and 50+ MCP tools across 7 major functional areas.

**Design Goals:**
1. **Traceability:** Every functional requirement traces to code entities and user stories
2. **Maintainability:** Templates and schemas enable agent-driven documentation updates
3. **Discoverability:** Consistent ID notation and organization enable fast navigation
4. **Auditability:** Metadata and status tracking enable progress visibility

**Scope:** Documentation structure, templates, ID notation, metadata schemas, and organization — NOT automation (separate implementation phase).

---

## 1. Core Documentation Structure

### 1.1 The Five Core Documents

Following the Job Hunter reference model, TraceRTM will have **5 core living documents**:

| Document | Purpose | Ownership | Update Frequency |
|----------|---------|-----------|------------------|
| **PRD.md** | Product vision, success metrics, epic hierarchy | Product Owner | Major releases |
| **FUNCTIONAL_REQUIREMENTS.md** | Testable requirements organized by category | Technical Lead | Per epic/feature |
| **ADR_INDEX.md** | Architecture Decision Records index with links | Tech Architect | Per significant decision |
| **USER_JOURNEYS.md** | End-to-end user scenarios with system flows | UX/Product | Per major feature |
| **IMPLEMENTATION_PLAN.md** | Phased roadmap with DAGs and progress tracking | Engineering Manager | Sprint/iteration |

**Location:** `docs/core/` (never in root per CLAUDE.md conventions)

---

## 2. ID Notation System

### 2.1 Functional Requirements

**Pattern:** `FR-{CATEGORY}-{NNN}`

**Categories (9 total):**
- `FR-DISC` — Discovery & Capture (import, ingestion, auto-link)
- `FR-QUAL` — Qualification & Analysis (scoring, graph analysis, impact)
- `FR-APP` — Application & Tracking (item CRUD, status workflow, progress)
- `FR-VER` — Verification & Validation (test execution, coverage, verification)
- `FR-RPT` — Reporting & Analytics (matrices, dashboards, metrics)
- `FR-COLLAB` — Collaboration & Integration (WebSocket, sync, webhooks)
- `FR-AI` — AI & Automation (agents, auto-link, workflows)
- `FR-INFRA` — Infrastructure (cache, storage, events, auth)
- `FR-MCP` — MCP Server (tools, resources, performance)

**Examples:**
- `FR-DISC-001`: Multi-Source Requirements Import (GitHub, Jira, Linear)
- `FR-QUAL-014`: Requirement Quality Scoring Engine
- `FR-AI-023`: Agent Coordination Service

**Numbering:** Sequential within category, starting at 001. Gaps allowed (retired/deprecated FRs).

---

### 2.2 Architecture Decision Records

**Pattern:** `ADR-{NNN}`

**Sequential numbering:** 001–999, never reused. Deprecated ADRs marked with status but retain ID.

**Examples:**
- `ADR-001`: Python FastAPI + Go Echo Dual Backend Architecture
- `ADR-015`: Neo4j for Graph Storage vs PostgreSQL Recursive CTEs
- `ADR-023`: MCP Server as Primary AI Agent Interface

---

### 2.3 Epics and User Stories

**Epic Pattern:** `E{N}.{M}`
- `E{N}` — Top-level epic (e.g., `E2: Qualification & Analysis`)
- `E{N}.{M}` — Sub-epic (e.g., `E2.1: Requirement Quality Scoring`)

**User Story Pattern:** `E{N}.{M}.{K}` or `US-{NNN}`
- Use `E{N}.{M}.{K}` when story is tightly coupled to an epic (e.g., `E2.1.3`)
- Use `US-{NNN}` for cross-cutting or standalone stories (e.g., `US-042: User Login Flow`)

**Examples:**
- `E1.1.1`: As a user, I import requirements from GitHub issues so that I can trace them to code.
- `E2.3.5`: As a developer, I view graph cycle detection results so that I can fix circular dependencies.
- `US-017`: As an admin, I configure SSO authentication so that my team can use corporate credentials.

---

### 2.4 User Journeys

**Pattern:** `UJ-{N}`

**Numbering:** Sequential, starting at 1. Each journey represents a complete end-to-end scenario.

**Examples:**
- `UJ-1`: Happy Path — Requirements Import to Traceability Matrix
- `UJ-2`: Developer Workflow — Feature to Test Coverage Verification
- `UJ-3`: Agent Workflow — Automated Linking and Quality Validation

---

## 3. Metadata Schemas

### 3.1 Functional Requirement Metadata

Every FR document entry includes:

```markdown
### FR-{CAT}-{NNN}: {Title}
**Traces to:** {Epic IDs, User Story IDs}
**Implemented in:** {Component paths or "Not Implemented"}
**Tests:** {Test file paths or "No Coverage"}
**Status:** Draft | In Progress | Implemented | Deprecated
**Priority:** P0 (Critical) | P1 (High) | P2 (Medium) | P3 (Low)
**Description:** {What the system SHALL do}
**Input:** {Expected inputs}
**Output:** {Expected outputs}
**Constraints:** {Technical constraints, limits, edge cases}
**Acceptance Criteria:** {Testable conditions}
```

**Example:**
```markdown
### FR-DISC-001: Multi-Source Requirements Import
**Traces to:** E1.1.1, E1.1.2, E1.1.3
**Implemented in:**
- `src/tracertm/services/github_import_service.py`
- `src/tracertm/services/jira_import_service.py`
- `src/tracertm/api/routers/integrations.py`
**Tests:**
- `tests/integration/test_github_import.py`
- `tests/integration/test_jira_import.py`
**Status:** Implemented
**Priority:** P0
**Description:** The system SHALL import requirements from external systems (GitHub Issues, Jira, Linear) with normalization and deduplication.
**Input:** Integration credentials, project ID, filter parameters
**Output:** Normalized item records in `items` table
**Constraints:**
- Each source adapter SHALL produce items conforming to the `Item` model
- Duplicate detection based on external_id + integration_type
- Imports SHALL be idempotent
**Acceptance Criteria:**
- [ ] GitHub issues imported with title, description, labels, assignees
- [ ] Jira issues imported with custom fields mapped to metadata
- [ ] Duplicates skipped based on external_id
- [ ] Import errors logged with actionable messages
```

---

### 3.2 Architecture Decision Record Metadata

Every ADR file includes YAML frontmatter:

```yaml
---
adr: ADR-{NNN}
title: {Decision Title}
status: Proposed | Accepted | Deprecated | Superseded
date: YYYY-MM-DD
author: {Name/Role}
supersedes: {ADR-XXX} (if applicable)
superseded_by: {ADR-YYY} (if applicable)
tags: [category1, category2]
---
```

**Body Structure (standardized):**
```markdown
## Context
{Problem statement, constraints, requirements}

## Decision
{What was decided — the "what"}

## Rationale
{Why this decision was made — the "why"}
- **Reason 1:** Explanation
- **Reason 2:** Explanation

## Alternatives Considered
### Alternative 1: {Name}
- **Pros:** ...
- **Cons:** ...
- **Rejected because:** ...

### Alternative 2: {Name}
- **Pros:** ...
- **Cons:** ...
- **Rejected because:** ...

## Consequences

### Positive
- Impact 1
- Impact 2

### Negative
- Impact 1
- Mitigation strategy

### Risks
- Risk 1 (Likelihood: High/Med/Low, Impact: High/Med/Low)
- Mitigation: ...

## Implementation Notes
- Technical details for implementers
- File paths, config changes, migration steps

## References
- Related ADRs: ADR-XXX, ADR-YYY
- External docs: [Title](URL)
```

---

### 3.3 User Journey Metadata

Every journey includes:

```markdown
## UJ-{N}: {Journey Title}

**Actor:** {Primary user/agent role}
**Frequency:** {How often this journey occurs}
**Goal:** {High-level objective}
**Prerequisites:** {Required setup, permissions, data}
**Success Criteria:** {How to know the journey succeeded}
```

**Flow Format:**
- Use ASCII flowcharts for visual clarity
- Include decision points, error paths, escalations
- Annotate with timing (if relevant), system components, data flows

**Example:**
```markdown
## UJ-1: Requirements Import to Traceability Matrix

**Actor:** Requirements Engineer
**Frequency:** 2-3 times per sprint
**Goal:** Import requirements from Jira → validate quality → generate traceability matrix
**Prerequisites:** Jira integration configured, target project created
**Success Criteria:** All Jira issues imported, quality scores >70%, matrix generated

[Flow diagram with timing and components]
```

---

### 3.4 Epic Metadata

**PRD Epic Section Format:**
```markdown
### E{N}: {Epic Name}

**Owner:** {Role/Name}
**Status:** Not Started | In Progress | Completed | On Hold
**Target Release:** {Version or date}
**Dependencies:** {Other epics this depends on}
**Success Metrics:** {Measurable outcomes}

#### E{N}.{M}: {Sub-Epic Name}

**Intent:** {Why this sub-epic exists}

| Story ID | User Story | Acceptance Criteria | Priority | Status |
|----------|-----------|-------------------|----------|--------|
| E{N}.{M}.1 | As a {role}, I {action} so that {benefit}. | {Testable criteria} | P0 | ✅ Done |
```

---

## 4. Template Design

### 4.1 ADR Template

**File:** `docs/templates/ADR_TEMPLATE.md`

```markdown
---
adr: ADR-{NNN}
title: {Short Title}
status: Proposed
date: YYYY-MM-DD
author: {Your Name}
tags: []
---

# ADR-{NNN}: {Full Title}

## Context

{What problem are we solving? What constraints exist?}

## Decision

{What did we decide to do?}

## Rationale

- **Reason 1:** Explanation
- **Reason 2:** Explanation

## Alternatives Considered

### Alternative 1: {Name}
- **Pros:**
- **Cons:**
- **Rejected because:**

## Consequences

### Positive
-

### Negative
-

### Risks
-

## Implementation Notes

{Technical details, migration steps, file changes}

## References

- Related ADRs:
- External docs:
```

---

### 4.2 Functional Requirement Template

**File:** `docs/templates/FR_TEMPLATE.md`

```markdown
### FR-{CAT}-{NNN}: {Title}
**Traces to:** {Epic IDs}
**Implemented in:** {Component paths or "Not Implemented"}
**Tests:** {Test paths or "No Coverage"}
**Status:** Draft
**Priority:** P0
**Description:** The system SHALL {action}.
**Input:** {Expected inputs}
**Output:** {Expected outputs}
**Constraints:**
- Constraint 1
**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
```

---

### 4.3 User Story Template

**File:** `docs/templates/USER_STORY_TEMPLATE.md`

```markdown
| Story ID | User Story | Acceptance Criteria | Priority | Status |
|----------|-----------|-------------------|----------|--------|
| E{N}.{M}.{K} | As a {role}, I {action} so that {benefit}. | {Testable criteria} | P0 | 🔵 Not Started |
```

**Status Icons:**
- 🔵 Not Started
- 🟡 In Progress
- ✅ Done
- ⏸️ Blocked
- ❌ Canceled

---

### 4.4 User Journey Template

**File:** `docs/templates/USER_JOURNEY_TEMPLATE.md`

```markdown
## UJ-{N}: {Journey Title}

**Actor:** {Primary user/agent}
**Frequency:** {Daily | Weekly | Per sprint | Ad-hoc}
**Goal:** {High-level objective}
**Prerequisites:** {Required setup}
**Success Criteria:** {Measurable outcomes}

### Flow

```
[Start] Trigger event
     │
     ▼
Step 1: {Action}
     │
     ├─ Success → Step 2
     └─ Error → {Error handling}
     │
     ▼
Step 2: {Action}
...
```

### Error Paths

{Describe failure scenarios and recovery}

### Performance Expectations

{Timing, throughput, resource usage}
```

---

## 5. File Organization Strategy

### 5.1 Directory Structure

```
docs/
├── core/                              # 5 core living documents
│   ├── PRD.md
│   ├── FUNCTIONAL_REQUIREMENTS.md
│   ├── ADR_INDEX.md
│   ├── USER_JOURNEYS.md
│   └── IMPLEMENTATION_PLAN.md
│
├── adr/                               # Individual ADR files
│   ├── ADR-001-dual-backend-architecture.md
│   ├── ADR-002-neo4j-graph-storage.md
│   ├── ADR-003-mcp-server-integration.md
│   └── ... (sequential)
│
├── user-stories/                      # User stories organized by epic
│   ├── E1-discovery-capture/
│   │   ├── E1.1-multi-source-aggregation.md
│   │   └── E1.2-normalization-deduplication.md
│   ├── E2-qualification-analysis/
│   │   ├── E2.1-requirement-quality.md
│   │   └── E2.2-graph-analysis.md
│   └── standalone/
│       └── US-042-user-login-flow.md
│
├── templates/                         # Reusable templates
│   ├── ADR_TEMPLATE.md
│   ├── FR_TEMPLATE.md
│   ├── USER_STORY_TEMPLATE.md
│   └── USER_JOURNEY_TEMPLATE.md
│
├── reference/                         # Quick refs, API docs (existing)
│   ├── TRACERTM_CODEBASE_ENTITY_MAP.md
│   ├── API_QUICK_REFERENCE.md
│   └── ...
│
├── guides/                            # Implementation guides (existing)
│   └── ...
│
├── reports/                           # Status reports (existing)
│   └── ...
│
└── research/                          # Research summaries (existing)
    └── ...
```

---

### 5.2 Naming Conventions

**ADR Files:**
- Pattern: `ADR-{NNN}-{kebab-case-title}.md`
- Example: `ADR-015-neo4j-graph-storage.md`

**User Story Files:**
- Pattern: `E{N}.{M}-{kebab-case-title}.md` OR `US-{NNN}-{kebab-case-title}.md`
- Example: `E2.1-requirement-quality.md`

**Core Documents:**
- ALL CAPS with underscores: `FUNCTIONAL_REQUIREMENTS.md`
- Matches Job Hunter reference style

---

### 5.3 Cross-Referencing Strategy

**Within Documents:**
- Link to other docs: `[ADR-015](../adr/ADR-015-neo4j-graph-storage.md)`
- Link to code: `src/tracertm/services/graph_service.py:142` (file:line)
- Link to tests: `tests/integration/test_graph_service.py::test_cycle_detection`

**From Code to Docs:**
- Docstrings reference FRs: `# Implements FR-QUAL-014`
- Test files reference FRs: `# Tests FR-DISC-001, FR-DISC-003`

**FR to Code Mapping:**
- `FUNCTIONAL_REQUIREMENTS.md` **Implemented in:** field lists exact file paths
- Update required on every code change that affects an FR

---

## 6. Content Organization Principles

### 6.1 PRD.md Structure

```markdown
# TraceRTM — Product Requirements Document

**Version:** {X.Y}
**Author:** {Name/Role}
**Date:** {YYYY-MM-DD}
**Status:** {Draft | Approved | Deprecated}

---

## 1. Product Vision

{High-level vision, target users, value proposition}

## 2. Target Users

**Primary:** {User persona}
**Secondary:** {Agent/automation persona}

## 3. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| ... | ... | ... |

## 4. Epic Hierarchy

```
E1: Discovery & Capture
  E1.1: Multi-Source Aggregation
  E1.2: Normalization & Deduplication
E2: Qualification & Analysis
  E2.1: Requirement Quality Scoring
  E2.2: Graph Analysis
...
```

## 5. Epic Details — Sub-Epics and User Stories

{Nested structure with tables per sub-epic}
```

---

### 6.2 FUNCTIONAL_REQUIREMENTS.md Structure

```markdown
# TraceRTM — Functional Requirements Specification

**Version:** {X.Y}
**Date:** {YYYY-MM-DD}

---

## FR Categories

{List all 9 categories with descriptions}

---

## FR-DISC: Discovery & Capture

{Grouped FRs with full metadata}

## FR-QUAL: Qualification & Analysis

{Grouped FRs with full metadata}

...
```

**Organization:** Group by category, then sequential within category.

---

### 6.3 ADR_INDEX.md Structure

```markdown
# TraceRTM — Architecture Decision Records Index

**Last Updated:** {YYYY-MM-DD}

---

## Active ADRs

| ADR | Title | Status | Date | Tags |
|-----|-------|--------|------|------|
| [ADR-001](adr/ADR-001-dual-backend-architecture.md) | Dual Backend Architecture | Accepted | 2026-01-15 | architecture, backend |
| [ADR-002](adr/ADR-002-neo4j-graph-storage.md) | Neo4j for Graph Storage | Accepted | 2026-01-20 | database, graph |
| ... | ... | ... | ... | ... |

---

## Deprecated ADRs

| ADR | Title | Deprecated Date | Superseded By |
|-----|-------|-----------------|---------------|
| ADR-008 | PostgreSQL for Graph Storage | 2026-01-20 | ADR-002 |

---

## ADRs by Category

### Architecture
- ADR-001, ADR-005, ADR-012

### Database
- ADR-002, ADR-007, ADR-013

### Integration
- ADR-003, ADR-009, ADR-015

...
```

---

### 6.4 USER_JOURNEYS.md Structure

```markdown
# TraceRTM — User Journeys

**Version:** {X.Y}
**Date:** {YYYY-MM-DD}

---

## Journey Index

| UJ | Title | Actor | Frequency |
|----|-------|-------|-----------|
| UJ-1 | Requirements Import to Matrix | Requirements Engineer | Per sprint |
| UJ-2 | Developer Feature Workflow | Developer | Daily |
| ... | ... | ... | ... |

---

## UJ-1: {Full Journey}

{Full journey with metadata, flow, error paths}

---

## UJ-2: {Full Journey}

...
```

---

### 6.5 IMPLEMENTATION_PLAN.md Structure

```markdown
# TraceRTM — Implementation Plan

**Version:** {X.Y}
**Date:** {YYYY-MM-DD}

---

## Mission Statement

{High-level objective, timeline, success criteria}

---

## Phase 1: {Phase Name}

**Goal:** {Phase objective}
**Duration:** {Estimated wall-clock time}
**Success Criteria:** {Measurable outcomes}

### Work Packages

| Task ID | Description | Depends On | Owner | Status |
|---------|-------------|------------|-------|--------|
| P1.1 | {Task} | — | Agent-X | ✅ Done |
| P1.2 | {Task} | P1.1 | Agent-Y | 🟡 In Progress |
| ... | ... | ... | ... | ... |

---

## Phase 2: {Phase Name}

...

---

## Dependency Graph (DAG)

```
P1.1 → P1.2 → P2.1
    ↘ P1.3 ↗     ↓
            P2.2 → P3.1
```

---

## Progress Tracking

{Overall completion %, blockers, risks}
```

---

## 7. Metadata Standards

### 7.1 File Header Standards

**All Core Docs:**
```markdown
# TraceRTM — {Document Title}

**Version:** X.Y
**Author:** {Name/Role}
**Date:** YYYY-MM-DD
**Status:** Draft | In Progress | Approved | Deprecated
```

**All ADRs:**
```yaml
---
adr: ADR-{NNN}
title: {Title}
status: Proposed | Accepted | Deprecated | Superseded
date: YYYY-MM-DD
author: {Name}
tags: [tag1, tag2]
---
```

---

### 7.2 Status Values

**Document Status:**
- `Draft` — Work in progress, not approved
- `In Progress` — Under active development/implementation
- `Approved` — Signed off by stakeholders
- `Deprecated` — No longer current

**ADR Status:**
- `Proposed` — Under review
- `Accepted` — Active decision
- `Deprecated` — No longer recommended
- `Superseded` — Replaced by newer ADR

**FR Status:**
- `Draft` — Not finalized
- `In Progress` — Being implemented
- `Implemented` — Code complete, tests passing
- `Deprecated` — Feature removed or replaced

**User Story Status:**
- 🔵 Not Started
- 🟡 In Progress
- ✅ Done
- ⏸️ Blocked
- ❌ Canceled

---

### 7.3 Priority Levels

**P0 (Critical):** Core functionality, blocks other work, production-critical
**P1 (High):** Important feature, needed for milestone/release
**P2 (Medium):** Nice to have, improves UX/performance
**P3 (Low):** Future enhancement, exploratory

---

## 8. Traceability Matrix

### 8.1 FR → Code Mapping

**Maintained in:** `FUNCTIONAL_REQUIREMENTS.md` **Implemented in:** field

**Format:**
```markdown
**Implemented in:**
- `src/tracertm/services/{service_name}.py`
- `src/tracertm/api/routers/{router_name}.py`
- `backend/internal/handlers/{handler_name}.go`
```

**Update Trigger:** Every code change that implements/modifies an FR

---

### 8.2 FR → Test Mapping

**Maintained in:** `FUNCTIONAL_REQUIREMENTS.md` **Tests:** field

**Format:**
```markdown
**Tests:**
- `tests/integration/test_{feature}.py::test_{scenario}`
- `backend/internal/handlers/{handler}_test.go`
- `frontend/apps/web/src/__tests__/{component}.test.tsx`
```

**Coverage Report:** Generated from test runs, cross-referenced with FRs

---

### 8.3 FR → Epic/User Story Mapping

**Maintained in:** `FUNCTIONAL_REQUIREMENTS.md` **Traces to:** field

**Format:**
```markdown
**Traces to:** E1.1.1, E1.1.2, US-042
```

**Bi-directional:** PRD user stories also reference implementing FRs

---

## 9. Document Lifecycle

### 9.1 Creating a New ADR

1. **Assign ID:** Next sequential number (check `ADR_INDEX.md`)
2. **Create file:** `docs/adr/ADR-{NNN}-{kebab-title}.md` from template
3. **Write content:** Fill all sections (Context, Decision, Rationale, Alternatives, Consequences)
4. **Set status:** `Proposed`
5. **Add to index:** Update `ADR_INDEX.md` table
6. **Review:** Team review, feedback, revisions
7. **Accept:** Change status to `Accepted`, update date
8. **Communicate:** Announce decision, update related docs

---

### 9.2 Creating a New FR

1. **Determine category:** Select from 9 FR categories
2. **Assign ID:** Next sequential within category (e.g., `FR-DISC-015`)
3. **Fill metadata:** All required fields (traces to, priority, status)
4. **Write specification:** Description, input/output, constraints, acceptance criteria
5. **Link to epics:** Add to **Traces to:** field
6. **Add to FR doc:** Insert in category section of `FUNCTIONAL_REQUIREMENTS.md`
7. **Review:** Technical review for completeness
8. **Approve:** Set status to `Draft` or `In Progress`

**Implementation Flow:**
1. FR created (status: `Draft`)
2. Code written (status: `In Progress`, update **Implemented in:** field)
3. Tests passing (update **Tests:** field)
4. Code merged (status: `Implemented`)

---

### 9.3 Creating a New User Story

1. **Assign ID:** `E{N}.{M}.{K}` (if part of epic) or `US-{NNN}` (standalone)
2. **Write story:** "As a {role}, I {action} so that {benefit}."
3. **Define acceptance criteria:** Testable conditions
4. **Set priority:** P0–P3
5. **Add to PRD:** In epic section or standalone stories section
6. **Create file (optional):** `docs/user-stories/{epic-or-standalone}/` for detailed stories
7. **Link FRs:** Cross-reference in `FUNCTIONAL_REQUIREMENTS.md`

---

### 9.4 Creating a New User Journey

1. **Assign ID:** `UJ-{N}` (sequential)
2. **Define metadata:** Actor, frequency, goal, prerequisites, success criteria
3. **Draw flow:** ASCII flowchart with decision points, timing, components
4. **Document errors:** Error paths and recovery strategies
5. **Add to doc:** `USER_JOURNEYS.md` in sequence
6. **Cross-reference:** Link related FRs, ADRs, epics

---

## 10. Automation Readiness

### 10.1 Agent-Parseable Formats

**All metadata fields are structured for agent parsing:**
- **YAML frontmatter:** ADR metadata
- **Markdown tables:** User stories, FR index, ADR index
- **Field markers:** `**Traces to:**`, `**Implemented in:**`, `**Tests:**`
- **Checkboxes:** `- [ ]` for acceptance criteria

**Automation can:**
- Extract all FRs and their metadata
- Build FR → Code traceability matrix
- Generate coverage reports (FR with tests vs without)
- Detect orphaned code (no FR reference)
- Validate cross-references (broken links, missing IDs)

---

### 10.2 Validation Rules (Future Automation)

**FR Validation:**
- [ ] All FRs have unique IDs within category
- [ ] All FRs have status, priority, description
- [ ] All **Implemented in:** paths exist in codebase
- [ ] All **Tests:** paths exist in test suite
- [ ] All **Traces to:** IDs exist in PRD

**ADR Validation:**
- [ ] All ADRs have unique sequential IDs
- [ ] All ADRs have frontmatter with required fields
- [ ] All ADRs have Context, Decision, Rationale sections
- [ ] All superseded ADRs reference superseding ADR

**User Story Validation:**
- [ ] All stories have unique IDs
- [ ] All stories follow "As a... I... so that..." format
- [ ] All stories have acceptance criteria
- [ ] All epic-linked stories exist in PRD

---

### 10.3 Code → Doc Sync Patterns

**Docstring Pattern (Python):**
```python
def import_github_issues(project_id: str) -> ImportResult:
    """Import GitHub issues into TraceRTM items.

    Implements: FR-DISC-001
    Tests: tests/integration/test_github_import.py::test_import_issues
    Related ADRs: ADR-003 (MCP Integration), ADR-007 (Import Pipeline)
    """
```

**Test Comment Pattern:**
```python
# Tests FR-DISC-001: Multi-Source Requirements Import
# Tests FR-DISC-003: Deduplication
def test_import_github_issues_deduplicates():
    """Verify duplicate issues are skipped based on external_id."""
```

**Automation:** Extract these patterns to auto-populate FR metadata fields.

---

## 11. Success Metrics

**Documentation Completeness:**
- [ ] All 7 functional areas have ≥5 FRs each (target: 35+ FRs total)
- [ ] All major architectural decisions have ADRs (target: 15–25 ADRs)
- [ ] All core workflows have User Journeys (target: 8–12 journeys)
- [ ] All epics decompose into user stories (target: 100+ stories)

**Traceability Coverage:**
- [ ] 100% of implemented features have FRs
- [ ] 90%+ of FRs have **Implemented in:** paths
- [ ] 80%+ of FRs have **Tests:** references
- [ ] All FRs trace to ≥1 epic/user story

**Maintainability:**
- [ ] Templates exist for all doc types
- [ ] All docs follow consistent structure
- [ ] All IDs follow notation system
- [ ] All cross-references are valid

**Agent Readiness:**
- [ ] 100% of metadata in structured formats
- [ ] Validation rules defined and documented
- [ ] Code-to-doc sync patterns established

---

## 12. Next Steps (Implementation Phase — Separate Agent)

**Not in scope for this architecture design:**

1. ✅ **Generate initial content:** Populate PRD with 7 epics, FUNCTIONAL_REQUIREMENTS with 35+ FRs, ADR_INDEX with 15+ ADRs
2. ✅ **Build automation:** Scripts to validate cross-references, generate coverage reports, sync code-to-doc
3. ✅ **Migrate existing docs:** Consolidate scattered user stories, ADRs, and requirements into new structure
4. ✅ **Create templates:** Instantiate all 4 template files in `docs/templates/`
5. ✅ **Tooling:** MCP tools for agents to read/write/update documentation programmatically

**This architecture provides the foundation. Automation agent will execute.**

---

## 13. Appendix: Reference Mapping

**Job Hunter → TraceRTM Adaptations:**

| Job Hunter Pattern | TraceRTM Adaptation | Reason |
|--------------------|---------------------|--------|
| 8 epics | 7 functional areas | Different domain scope |
| FR-{3-letter-CAT}-{NNN} | FR-{4-letter-CAT}-{NNN} | More categories, clearer names |
| 13 ADRs | 15–25 ADRs target | More complex architecture |
| Single user (Koosha) | Multi-user + agents | Enterprise vs personal tool |
| n8n + NocoDB stack | Python/Go/React stack | Different tech stack |
| Email tracking | Real-time WebSocket | Different integration model |

**Core principles preserved:**
- ✅ 5 core documents
- ✅ ID notation system
- ✅ Metadata schemas
- ✅ Templates for consistency
- ✅ Traceability matrix approach
- ✅ Agent-parseable formats

---

## 14. Questions for Team Lead

**Before implementation begins:**

1. **Epic Count:** Are 7 functional areas sufficient, or should we expand/merge?
2. **FR Granularity:** Aim for 35+ FRs total (5 per area), or more detailed (10+ per area)?
3. **ADR Backfill:** Should we retroactively document past decisions, or only new ones?
4. **User Story Format:** Prefer all in PRD tables, or separate detailed files in `user-stories/`?
5. **Automation Priority:** Which validation/sync automation is highest priority for Phase 1?

**Approval Gate:** Team lead sign-off required before proceeding to content generation phase.

---

**END OF ARCHITECTURE DOCUMENT**

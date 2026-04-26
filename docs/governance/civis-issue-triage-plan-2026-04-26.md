# Civis Issue Triage Plan (2026-04-26)

## Executive Summary

KooshaPari/Civis has 159 open issues representing a significant backlog. This triage plan identifies opportunities for bulk closure, establishes labeling standards, and prioritizes the 10 most critical issues requiring immediate human attention.

**Key Finding:** 151/159 issues (95%) are older than 60 days with minimal engagement — strong candidates for cleanup/archival post-review.

---

## Issue Counts by Category

| Category | Count | % | Notes |
|----------|-------|---|-------|
| **Total Open** | 159 | 100% | |
| **Labeled** | 106 | 67% | Partial tagging coverage |
| **Untagged** | 53 | 33% | Need labeling or removal |
| **Auto-filed (CI/Bot)** | 8 | 5% | Bot-generated; bulk-closeable |
| **Older than 60 days** | 151 | 95% | Stale; likely abandoned |
| **Newer than 60 days** | 8 | 5% | Recent activity |

---

## Label Coverage & Breakdown

### Current Label Distribution

**Type Labels** (mutually exclusive):
- `type:feature` — 85 issues (53%)
- `type:epic` — 10 issues (6%)
- `type:bug` — 1 issue
- `type:documentation` — 1 issue
- `type:infrastructure` — 1 issue
- *(Untagged type: 53 issues)*

**Priority Labels**:
- `priority:high` — 22 issues (14%)
- `priority:medium` — 24 issues (15%)
- `priority:low` — 2 issues (1%)
- *(No priority: 111 issues)*

**Phase Labels** (feature grouping):
- `phase:foundation` — 11 issues
- `phase:assets` — 3 issues
- `phase:ui` — 3 issues
- `phase:data`, `phase:ai`, `phase:media`, `phase:extensions`, `phase:optimization`, `phase:integration` — 2 each

**Documentation Type Labels**:
- `doc:spec` — 20 issues
- `doc:research` — 10 issues
- `doc:adr` — 3 issues

**Auto-filed Labels** (bot-managed):
- `auto-alert-sync` — 8 issues
- `source:ci` — 8 issues (overlaps with auto-alert)

---

## Recommended Bulk-Close Criteria

### 1. CI/Auto-filed Issues (8 issues)

**Criteria:** All issues with `auto-alert-sync` AND `source:ci` labels, created >30 days ago with no engagement.

**Issues Identified:**
- #237: [CI] Security Guard (Hooks) failing on main
- #236: [CI] Security Guard failing on main
- #235: [CI] Release Drafter failing on main
- #234: [CI] pages-deploy failing on main
- #172: [CI] Docs Site failing on main
- #171: [CI] Pages Deploy failing on main
- #170: [CI] codeql failing on main
- #169: [CI] Quality failing on main

**Rationale:**
- These are auto-generated CI failures, created April 1 & March 1.
- If CI was broken and auto-closed, these are stale.
- If CI is currently fixed, these are noise.
- Recommend: **Close all 8** if main branch CI is currently passing. If still broken, fix the CI first.

**Action:** Query CI status for main branch. If green, close with comment: "CI auto-alert; issue auto-resolved when CI passed."

### 2. Untagged Bulk Items (53 issues)

**Issues:** All "Item: civ NNN" and "Task: civ NNN" issues without labels (issues #101–#153).

**Criteria for closure:**
- If these are completed work items migrated from another system (e.g., Jira, AirtableAPI), they should be:
  - Closed with label `wontfix` + comment linking to archive/migration
  - OR re-tagged as `type:feature` and assigned a `priority`
- If they are genuine work still in queue, they **must** be tagged with `type:feature` and `priority:high|medium|low`.

**Rationale:**
- Created uniformly on 2026-02-24, batch-imported appearance suggests migration.
- Zero follow-up comments indicate either completed work or forgotten tickets.
- 60+ days with no engagement = evidence of abandonment.

**Action:** 
1. Verify origin — are these from a Jira/Trello export?
2. If completed/archived: close with comment "Bulk archived from [source]" + link.
3. If active: apply `type:feature`, `priority:X`, and `phase:Y` labels immediately.

### 3. Old Issues with No Engagement (90+ issues, 60+ days old)

**Criteria:**
- Created before 2026-02-24 (>60 days ago)
- Zero comments or reactions
- Not part of an active epic

**Recommended actions:**
- **For type:feature issues:** Add `priority:low` label; review roadmap. If not planned, close with `wontfix`.
- **For type:epic issues:** Verify if epic is still in scope. If stale, close and reference successor epic.
- **For type:documentation issues:** Archive if superseded by newer docs.

---

## Top 10 Issues Requiring Real Triage

These issues have sufficient context to warrant immediate human review:

### 1. #8 — Epic: Core Simulation Engine
- **Status:** Foundational epic for the entire project
- **Created:** 2026-02-24 (60+ days)
- **Labels:** `type:epic`, `priority:high`, `phase:foundation`
- **Triage Action:** 
  - Is this epic still in active development?
  - Verify sub-task completion rate (issues #18–#39 appear to be sub-specs/research).
  - If active: update issue with status comment and target completion date.
  - If stale: close and link to successor epic.

### 2. #9 — Epic: Economy System
- **Status:** Economic mechanics system
- **Created:** 2026-02-24 (60+ days)
- **Labels:** `type:epic`, `priority:high`, `phase:foundation`
- **Related specs:** #26 (Joule Economy)
- **Triage Action:**
  - Verify implementation status of sub-specs (#19–#26).
  - Check if economy v1 (#19) is shipped or in progress.
  - Update parent epic with rollup status.

### 3. #10 — Epic: Client Protocol
- **Status:** Network/protocol epic
- **Created:** 2026-02-24 (60+ days)
- **Labels:** `type:epic`, `priority:high`, `phase:integration`
- **Triage Action:**
  - Verify status of #27 (Client Protocol spec).
  - If design complete, move to implementation phase.
  - Update roadmap with target delivery date.

### 4. #11 — Epic: UI/UX System
- **Status:** Client interface epic
- **Created:** 2026-02-24 (60+ days)
- **Labels:** `type:epic`, `priority:high`, `phase:ui`
- **Related specs:** #28–#29 (UI/UX, NPC Behavior)
- **Triage Action:**
  - Assess design maturity (check specs #28–#29).
  - Verify component library/framework decision.
  - Identify blockers on asset pipeline (#13 — Asset Pipeline epic).

### 5. #12 — Epic: Performance Optimization
- **Status:** Performance/optimization epic
- **Created:** 2026-02-24 (60+ days)
- **Labels:** `type:epic`, `priority:high`, `phase:optimization`
- **Triage Action:**
  - When does this phase start relative to foundation/UI phases?
  - Are baseline metrics established (from #30 — Performance Optimization spec)?
  - Update dependency graph (likely depends on #8–#11).

### 6. #13 — Epic: Asset Pipeline
- **Status:** Asset production workflow
- **Created:** 2026-02-24 (60+ days)
- **Labels:** `type:epic`, `priority:high`, `phase:assets`
- **Related specs:** #31 (2D), #32 (3D); **Research:** #44–#49
- **Triage Action:**
  - Blockers: Research outcomes (#44–#49 are 60+ days old).
  - Verify if SDXL/3D tool research (#44–#45) has conclusions.
  - Update timeline based on research phase closure.

### 7. #7 — bug: Fix memory leak in cache
- **Status:** Production bug
- **Created:** 2026-02-24 (60+ days)
- **Labels:** `type:bug`, `priority:high`
- **Triage Action:**
  - Is this bug fixed or reproduced in latest build?
  - If fixed: close with link to fix PR.
  - If still open: add reproduction steps or assign to owner.
  - If unknown: escalate to engineering lead.

### 8. #6 — feat: Add API rate limiting
- **Status:** Feature request
- **Created:** 2026-02-24 (60+ days)
- **Labels:** `type:feature`, `priority:medium`
- **Triage Action:**
  - Is rate limiting implemented?
  - If yes: close with PR link.
  - If no: verify if it's still required; adjust priority or close.

### 9. #5 — infra: Set up monitoring and observability
- **Status:** Infrastructure work
- **Created:** 2026-02-24 (60+ days)
- **Labels:** `type:infrastructure`, `priority:medium`
- **Triage Action:**
  - Has monitoring been deployed to prod?
  - If yes: close with link to monitoring dashboard.
  - If no: move to next sprint with clear acceptance criteria.

### 10. #4 — docs: Update API documentation
- **Status:** Documentation task
- **Created:** 2026-02-24 (60+ days)
- **Labels:** `type:documentation`, `priority:medium`
- **Triage Action:**
  - Is API documentation current?
  - If yes: close with link to docs site.
  - If no: re-estimate effort and add to roadmap.

---

## Label Standardization Recommendations

### Required Labels (All Issues)

1. **Type** (choose one):
   - `type:feature` — New feature or enhancement
   - `type:bug` — Bug fix
   - `type:documentation` — Docs only
   - `type:epic` — Major feature grouping
   - `type:infrastructure` — DevOps/tooling

2. **Priority** (choose one):
   - `priority:high` — Blocks shipping/critical path
   - `priority:medium` — Important but not blocking
   - `priority:low` — Nice-to-have / future consideration

### Optional Labels (Context)

3. **Phase** (for epics & features, choose one):
   - `phase:foundation`, `phase:integration`, `phase:ui`, `phase:assets`, `phase:optimization`, `phase:ai`, `phase:data`, `phase:media`, `phase:extensions`

4. **Document Type** (for specs/research):
   - `doc:spec` — Specification
   - `doc:research` — Research findings
   - `doc:adr` — Architecture Decision Record

### Deprecated Labels (Stop Using)

- `auto-alert-sync` — retire after CI cleanup
- `source:ci` — retire after CI cleanup

---

## Triage Effort Estimate

| Task | Effort | Owner |
|------|--------|-------|
| Review & close CI auto-alerts (8 issues) | 15 min | Engineering |
| Review untagged bulk items & decide (53 issues) | 45 min | PM / Project Lead |
| Triage top 10 issues (detailed review) | 45 min | Engineering / PM |
| Apply missing labels to remaining issues | 30 min | PM / Automation |
| **Total** | **~2.5 hours** | — |

---

## Implementation Roadmap

### Phase 1: Quick Wins (15 min)
1. Check CI status for main branch.
2. Close all 8 auto-alert issues if CI is green.
3. Close any obvious wontfix issues (superseded, never started).

### Phase 2: Bulk Labeling (30 min)
1. Identify source of untagged bulk items (#101–#153).
2. Bulk-apply `type:feature` to all remaining items.
3. Bulk-apply priority labels based on roadmap.

### Phase 3: Epic Review (45 min)
1. Review top 10 issues with stakeholders.
2. Update issue descriptions with status & next steps.
3. Link related issues (specs, sub-tasks, blockers).

### Phase 4: Automation Setup (Optional)
- Add GitHub Actions workflow to enforce label requirements on new issues.
- Auto-close stale issues >90 days with no activity (after initial triage).

---

## Success Criteria

- [ ] CI auto-alerts closed (8 issues → 0)
- [ ] All open issues have a `type` label (53 untagged → 0)
- [ ] All open issues have a `priority` label
- [ ] Top 10 issues have updated status comments
- [ ] Issue count reduced to <100 (net -59 issues via cleanup)
- [ ] GitHub issue templates updated to enforce Type + Priority labels

---

## Reference

**Triage Date:** 2026-04-26  
**Analyst:** Haiku Agent (Claude Code)  
**Methodology:** Label-based categorization + age analysis  
**Data Source:** `gh issue list -R KooshaPari/Civis --state open --limit 159`

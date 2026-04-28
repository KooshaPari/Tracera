# TraceRTM - Phase 2 Epics & User Stories

**Project:** TraceRTM v2.0  
**Phase:** Phase 2 (Advanced Features)  
**Date:** 2025-11-21  
**Status:** Designed - Ready for Implementation

**Related Documents:**
- **MVP Epics**: `docs/epics.md` - Epics 1-8 (56 stories)
- **Sprint Planning**: `docs/sprint-artifacts/complete-sprint-plan.md` - Sprints 9-12
- **Test Design**: `docs/test-design-phase-2.md` - 90 test cases
- **PRD Enhanced**: `docs/PRD-ENHANCED.md` - Complete requirements

---

## Overview

**Phase 2 Goal:** Add advanced features for power users and external integrations

**Scope:**
- 4 Epics (Epic 9-12)
- 12 User Stories
- 90 Test Cases
- 8 weeks (Sprints 9-12)

**Prerequisites:**
- MVP Complete (Epic 1-8)
- All 200 MVP tests passing
- v1.0.0 released

---

## Epic 9: Advanced Versioning & History

**Epic ID:** EPIC-9  
**Priority:** P1 (High)  
**Sprint:** Sprint 9 (Weeks 17-18)  
**FRs Covered:** FR56-FR59  
**Stories:** 3  
**Test Cases:** 18  
**Estimated Effort:** 25-35 hours

### Epic Goal

Enable temporal queries and rollback capabilities for advanced debugging and auditing.

### User Stories

---

### Story 9.1: Temporal Queries

**Story ID:** STORY-9.1  
**Priority:** P1  
**Estimated Effort:** 10-12 hours  
**Test Cases:** 4 (TC-9.1.1 to TC-9.1.4)

**As a** developer  
**I want to** query the state of items at any point in time  
**So that** I can debug issues, understand project evolution, and audit changes

**Acceptance Criteria:**
1. Can query single item state at specific date: `rtm show <id> --at 2025-11-15`
2. Can query all items in a view at specific date: `rtm view FEATURE --at 2025-11-15`
3. Temporal queries complete in <500ms
4. Supports ISO 8601 dates and relative dates (yesterday, last week)
5. Clear error message for invalid dates

**Technical Notes:**
- Event replay from event log
- Efficient state reconstruction
- Cache recent temporal queries
- Limit history depth to 90 days initially

**Dependencies:**
- Story 7.1 (Event Sourcing) must be complete
- Event log table populated

**Test Cases:**
- TC-9.1.1: Query Item State at Specific Date
- TC-9.1.2: Temporal Query Performance
- TC-9.1.3: Query All Items at Date
- TC-9.1.4: Invalid Date Format

---

### Story 9.2: Item Rollback

**Story ID:** STORY-9.2  
**Priority:** P1  
**Estimated Effort:** 10-12 hours  
**Test Cases:** 4 (TC-9.2.1 to TC-9.2.4)

**As a** developer  
**I want to** rollback items to previous versions  
**So that** I can undo mistakes and recover from bad changes

**Acceptance Criteria:**
1. Can rollback to specific version: `rtm rollback <id> --to-version 3`
2. Can rollback to previous version: `rtm rollback <id>`
3. Rollback requires confirmation: `--confirm` flag
4. Rollback creates new version (doesn't delete history)
5. Rollback event logged with metadata (who, when, from_version, to_version)

**Technical Notes:**
- Rollback creates new version (version N+1) with state from version M
- Complete audit trail maintained
- Rollback is itself a versioned operation
- Can rollback a rollback

**Dependencies:**
- Story 2.3 (Optimistic Locking) must be complete
- Version tracking working

**Test Cases:**
- TC-9.2.1: Rollback to Previous Version
- TC-9.2.2: Rollback with Confirmation
- TC-9.2.3: Rollback Metadata Tracking
- TC-9.2.4: Rollback Invalid Version

---

### Story 9.3: Version History Display

**Story ID:** STORY-9.3  
**Priority:** P1  
**Estimated Effort:** 8-10 hours  
**Test Cases:** 4 (TC-9.3.1 to TC-9.3.4)

**As a** developer  
**I want to** view complete version history with diffs  
**So that** I can understand how items evolved over time

**Acceptance Criteria:**
1. Can view all versions: `rtm history <id>`
2. Can view diffs between versions: `rtm history <id> --diff`
3. Can filter by date range: `rtm history <id> --since 2025-11-01`
4. History paginated (50 versions per page)
5. Shows who made each change and when

**Technical Notes:**
- Display in reverse chronological order (newest first)
- Diff shows field-by-field changes
- Pagination for items with 1000+ versions
- Color-coded diffs (green=added, red=removed, yellow=modified)

**Dependencies:**
- Story 7.1 (Event Sourcing) must be complete

**Test Cases:**
- TC-9.3.1: View Item History
- TC-9.3.2: History with Diffs
- TC-9.3.3: Filter History by Date Range
- TC-9.3.4: History Pagination

---

## Epic 10: Advanced Search & Filter

**Epic ID:** EPIC-10  
**Priority:** P1 (High)  
**Sprint:** Sprint 10 (Weeks 19-20)  
**FRs Covered:** FR60-FR67  
**Stories:** 3  
**Test Cases:** 32  
**Estimated Effort:** 30-40 hours

### Epic Goal

Provide powerful search and filtering capabilities for finding items quickly in large projects.

### User Stories

---

### Story 10.1: Full-Text Search

**Story ID:** STORY-10.1  
**Priority:** P1  
**Estimated Effort:** 12-15 hours  
**Test Cases:** 5 (TC-10.1.1 to TC-10.1.5)

**As a** developer  
**I want to** search across all item content with fuzzy matching  
**So that** I can find items quickly even with typos

**Acceptance Criteria:**
1. Can search all fields: `rtm search "authentication"`
2. Fuzzy matching for typos (edit distance ≤2)
3. Results ranked by relevance (title > description > metadata)
4. Search completes in <200ms on 10K items
5. Matching terms highlighted in results

**Technical Notes:**
- PostgreSQL full-text search (tsvector, tsquery)
- GIN index on searchable fields
- Trigram similarity for fuzzy matching
- Ranking algorithm: title weight=1.0, description=0.5, metadata=0.3

**Dependencies:**
- Story 2.2 (Item Retrieval) must be complete
- Database indexes created

**Test Cases:**
- TC-10.1.1: Basic Full-Text Search
- TC-10.1.2: Fuzzy Matching
- TC-10.1.3: Search Ranking
- TC-10.1.4: Search Performance
- TC-10.1.5: Search Highlighting

---

### Story 10.2: Advanced Filtering

**Story ID:** STORY-10.2  
**Priority:** P1  
**Estimated Effort:** 15-18 hours  
**Test Cases:** 7 (TC-10.2.1 to TC-10.2.7)

**As a** developer  
**I want to** filter items with complex expressions  
**So that** I can find exactly what I need

**Acceptance Criteria:**
1. Can filter by status: `rtm view FEATURE --status todo,in_progress`
2. Can filter by type: `rtm view FEATURE --type epic,feature`
3. Can filter by owner: `rtm view FEATURE --owner agent-12`
4. Can filter by date range: `rtm view FEATURE --created-after 2025-11-01`
5. Can combine filters with AND: `rtm view FEATURE --status blocked --owner agent-12`
6. Can combine filters with OR: `rtm view FEATURE --status "blocked OR in_progress"`
7. Can use complex expressions: `rtm query "(status:blocked AND owner:agent-12) OR priority:high"`

**Technical Notes:**
- Expression parser for complex queries
- SQL query builder from expressions
- Support for AND, OR, NOT operators
- Parentheses for grouping
- Field-specific filters (status:, type:, owner:, etc.)

**Dependencies:**
- Story 2.2 (Item Retrieval) must be complete

**Test Cases:**
- TC-10.2.1: Filter by Status
- TC-10.2.2: Filter by Type
- TC-10.2.3: Filter by Owner
- TC-10.2.4: Filter by Date Range
- TC-10.2.5: Combined Filters (AND)
- TC-10.2.6: Combined Filters (OR)
- TC-10.2.7: Complex Filter Expression

---

### Story 10.3: Saved Queries

**Story ID:** STORY-10.3  
**Priority:** P2  
**Estimated Effort:** 6-8 hours  
**Test Cases:** 4 (TC-10.3.1 to TC-10.3.4)

**As a** developer  
**I want to** save frequently used queries  
**So that** I can reuse them without retyping

**Acceptance Criteria:**
1. Can save query: `rtm query save "blocked-features" --query "status:blocked AND type:feature"`
2. Can execute saved query: `rtm query run blocked-features`
3. Can list saved queries: `rtm query list`
4. Can delete saved query: `rtm query delete blocked-features`
5. Saved queries stored per project

**Technical Notes:**
- Store in database (saved_queries table)
- Query name must be unique per project
- Store query string and optional description
- Can update existing saved query

**Dependencies:**
- Story 10.2 (Advanced Filtering) must be complete

**Test Cases:**
- TC-10.3.1: Save Query
- TC-10.3.2: Execute Saved Query
- TC-10.3.3: List Saved Queries
- TC-10.3.4: Delete Saved Query

---

## Epic 11: Progress Tracking & Reporting

**Epic ID:** EPIC-11  
**Priority:** P1 (High)  
**Sprint:** Sprint 11 (Weeks 21-22)  
**FRs Covered:** FR68-FR73  
**Stories:** 3  
**Test Cases:** 24  
**Estimated Effort:** 25-35 hours

### Epic Goal

Provide comprehensive progress tracking, blocking item detection, and velocity reporting.

### User Stories

---

### Story 11.1: Progress Calculation

**Story ID:** STORY-11.1  
**Priority:** P1  
**Estimated Effort:** 10-12 hours  
**Test Cases:** 4 (TC-11.1.1 to TC-11.1.4)

**As a** developer  
**I want to** see automatic progress calculation with rollup  
**So that** I can track project completion without manual updates

**Acceptance Criteria:**
1. Progress auto-calculated from children (average of child progress)
2. Progress rolls up through hierarchy (Task → Story → Feature → Epic)
3. Real-time progress bars in PROGRESS view
4. Progress calculation completes in <100ms for 100 children
5. Manual progress override supported

**Technical Notes:**
- Recursive CTE for hierarchy traversal
- Cache progress calculations
- Invalidate cache on child updates
- Progress = (sum of child progress) / (number of children)

**Dependencies:**
- Story 2.6 (Item Hierarchy) must be complete

**Test Cases:**
- TC-11.1.1: Auto-Calculate Completion Percentage
- TC-11.1.2: Recursive Progress Rollup
- TC-11.1.3: Real-Time Progress Display
- TC-11.1.4: Progress Calculation Performance

---

### Story 11.2: Blocking Items Detection

**Story ID:** STORY-11.2  
**Priority:** P1  
**Estimated Effort:** 8-10 hours  
**Test Cases:** 3 (TC-11.2.1 to TC-11.2.3)

**As a** developer  
**I want to** identify blocking and stalled items  
**So that** I can unblock progress and focus on critical issues

**Acceptance Criteria:**
1. Can show blockers: `rtm view FEATURE --show-blockers`
2. Can find stalled items: `rtm query stalled --days 30`
3. Can analyze blocker chains: `rtm show <id> --blocker-chain`
4. Transitive blocker detection (A blocks B blocks C)
5. Highlight critical path items

**Technical Notes:**
- Use link table to find "blocks" relationships
- Recursive query for transitive blockers
- Stalled = no updates in N days
- Critical path = longest blocker chain

**Dependencies:**
- Story 4.1 (Link Creation) must be complete

**Test Cases:**
- TC-11.2.1: Identify Blocking Items
- TC-11.2.2: Identify Stalled Items
- TC-11.2.3: Blocker Chain Analysis

---

### Story 11.3: Progress Reports

**Story ID:** STORY-11.3  
**Priority:** P2  
**Estimated Effort:** 8-10 hours  
**Test Cases:** 4 (TC-11.3.1 to TC-11.3.4)

**As a** developer  
**I want to** generate progress reports and track velocity  
**So that** I can forecast completion and identify trends

**Acceptance Criteria:**
1. Can generate report: `rtm report progress --period month`
2. Report shows completion stats (items completed, velocity, burndown)
3. Can track velocity: items completed per week
4. Can export report to CSV
5. Burndown chart data available

**Technical Notes:**
- Query events table for completion events
- Calculate velocity = items completed / time period
- Burndown = remaining items over time
- Support periods: day, week, month, quarter

**Dependencies:**
- Story 7.1 (Event Sourcing) must be complete

**Test Cases:**
- TC-11.3.1: Generate Progress Report
- TC-11.3.2: Velocity Tracking
- TC-11.3.3: Burndown Chart Data
- TC-11.3.4: Export Report

---

## Epic 12: Advanced Import/Export

**Epic ID:** EPIC-12  
**Priority:** P2 (Medium)  
**Sprint:** Sprint 12 (Weeks 23-24)  
**FRs Covered:** FR76, FR79-FR81  
**Stories:** 3  
**Test Cases:** 16  
**Estimated Effort:** 20-30 hours

### Epic Goal

Enable data portability with Markdown export and imports from external tools (Jira, GitHub Projects).

### User Stories

---

### Story 12.1: Markdown Export

**Story ID:** STORY-12.1  
**Priority:** P2  
**Estimated Effort:** 6-8 hours  
**Test Cases:** 3 (TC-12.1.1 to TC-12.1.3)

**As a** developer  
**I want to** export projects as Markdown  
**So that** I can share documentation and use in other tools

**Acceptance Criteria:**
1. Can export to Markdown: `rtm export --format markdown --output project.md`
2. Hierarchy represented with heading levels (# Epic, ## Feature, ### Story)
3. Links represented as Markdown links
4. Metadata included in YAML frontmatter
5. Readable structure for humans

**Technical Notes:**
- Use heading levels for hierarchy
- Internal links use anchors
- External links preserved
- YAML frontmatter for metadata

**Dependencies:**
- Story 2.6 (Item Hierarchy) must be complete

**Test Cases:**
- TC-12.1.1: Export Project as Markdown
- TC-12.1.2: Markdown Hierarchy
- TC-12.1.3: Markdown Links

---

### Story 12.2: External Tool Import

**Story ID:** STORY-12.2  
**Priority:** P2  
**Estimated Effort:** 12-15 hours  
**Test Cases:** 4 (TC-12.2.1 to TC-12.2.4)

**As a** developer  
**I want to** import from Jira and GitHub Projects  
**So that** I can migrate existing projects to TraceRTM

**Acceptance Criteria:**
1. Can import from Jira: `rtm import --source jira --file jira-export.json`
2. Can import from GitHub Projects: `rtm import --source github --file github-export.json`
3. Field mapping configurable (Jira fields → TraceRTM fields)
4. Import validation before applying
5. Conflict resolution strategy (skip, update, merge)

**Technical Notes:**
- Use Jira REST API export format
- Use GitHub Projects GraphQL export format
- Map Jira issue types to TraceRTM item types
- Map GitHub issue/PR to TraceRTM items
- Preserve links and relationships

**Dependencies:**
- Story 8.4 (JSON Import) must be complete

**Test Cases:**
- TC-12.2.1: Import from Jira
- TC-12.2.2: Import from GitHub Projects
- TC-12.2.3: Import Validation
- TC-12.2.4: Import Conflict Resolution

---

### Story 12.3: Import Validation & Conflict Resolution

**Story ID:** STORY-12.3  
**Priority:** P2  
**Estimated Effort:** 6-8 hours  
**Test Cases:** 3 (TC-12.3.1 to TC-12.3.3)

**As a** developer  
**I want to** validate imports and resolve conflicts  
**So that** I can ensure data integrity during migration

**Acceptance Criteria:**
1. Validation before import (schema check, required fields)
2. Conflict detection (duplicate IDs, missing references)
3. Conflict resolution strategies: skip, update, merge
4. Dry-run mode: `rtm import --dry-run`
5. Import summary report (items imported, skipped, errors)

**Technical Notes:**
- Validate against Pydantic schemas
- Check referential integrity
- Transaction-based import (all or nothing)
- Rollback on error

**Dependencies:**
- Story 12.2 (External Tool Import) must be complete

**Test Cases:**
- TC-12.3.1: Import Validation
- TC-12.3.2: Conflict Detection
- TC-12.3.3: Dry-Run Mode

---

## Phase 2 Summary

### Statistics

| Metric | Count |
|--------|-------|
| Epics | 4 |
| Stories | 12 |
| Test Cases | 90 |
| Sprints | 4 (Sprints 9-12) |
| Duration | 8 weeks |
| Estimated Hours | 100-140 hours |

### Deliverables

**Epic 9: Advanced Versioning**
- Temporal queries (query state at any point in time)
- Item rollback to previous versions
- Version history with diffs

**Epic 10: Advanced Search**
- Full-text search with fuzzy matching
- Complex filter expressions (AND/OR)
- Saved queries

**Epic 11: Progress Tracking**
- Automatic progress calculation with rollup
- Blocking item detection
- Progress reports and velocity tracking

**Epic 12: Advanced Import/Export**
- Markdown export
- Import from Jira
- Import from GitHub Projects

### Dependencies

**Prerequisites:**
- MVP Complete (Epic 1-8)
- All 200 MVP tests passing
- v1.0.0 released

**Sprint Dependencies:**
- Sprint 9 depends on Sprint 8 (MVP complete)
- Sprint 10-12 can run in parallel (independent features)

---

**Document Status:** ✅ **COMPLETE - READY FOR IMPLEMENTATION**  
**Phase:** Phase 2 (Advanced Features)  
**Last Updated:** 2025-11-21  
**Next Review:** End of Sprint 8 (2026-03-12)

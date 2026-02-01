# Test Design: Phase 2 - Advanced Features

**Phase:** Phase 2 (Post-MVP)  
**FRs Covered:** FR56-FR82 (25 FRs)  
**Stories:** 15 new stories (9.1 - 11.5)  
**Test Architect:** Murat (TEA)  
**Date:** 2025-11-21  
**Status:** Ready for Implementation

---

## Executive Summary

**Phase 2 Goal:** Add advanced features for power users - versioning, search, progress tracking, and integrations.

**Test Strategy:** Build on MVP foundation with focus on performance, usability, and integration testing.

**Risk Assessment:** MEDIUM
- **Technical Risk**: Temporal queries, full-text search performance, external integrations
- **Business Risk**: Advanced features - not critical for core workflows
- **Priority:** P1-P2 (High to Medium)

**Test Coverage Target:**
- Unit Tests: 85%+ (complex algorithms, validators)
- Integration Tests: 80%+ (database queries, external APIs)
- E2E Tests: 100% (critical advanced workflows)

---

## Epic 9: Advanced Versioning & History

**FRs:** FR56-FR59 (4 FRs)  
**Stories:** 3 stories (9.1 - 9.3)  
**Test Cases:** 18 test cases  
**Priority:** P1 (High)  
**Risk:** HIGH (temporal queries, state reconstruction)

### Story 9.1: Temporal Queries

**FRs:** FR56, FR59  
**Priority:** P1  
**Risk:** HIGH (complex SQL, performance)

#### Test Cases

**TC-9.1.1: Query Item State at Specific Date**
- **Type:** Integration
- **Given:** Item with 5 updates over time
- **When:** User runs `rtm show <id> --at 2025-11-15`
- **Then:** Item state as of that date displayed
- **Validation:** Correct historical state reconstructed

**TC-9.1.2: Temporal Query Performance**
- **Type:** Integration (Performance)
- **Given:** 10K items with 100K events
- **When:** Temporal query executed
- **Then:** Query completes in <500ms
- **Validation:** Efficient event replay

**TC-9.1.3: Query All Items at Date**
- **Type:** Integration
- **Given:** Project with 1K items
- **When:** User runs `rtm view FEATURE --at 2025-11-15`
- **Then:** All items shown as of that date
- **Validation:** Bulk temporal query works

**TC-9.1.4: Invalid Date Format**
- **Type:** Unit (Negative)
- **Given:** User provides invalid date
- **When:** `rtm show <id> --at invalid-date`
- **Then:** Validation error with date format help
- **Validation:** Clear error message

#### Test Data
- Date formats: ISO 8601, relative (yesterday, last week)
- Event counts: 10, 100, 1000 per item
- Time ranges: 1 day, 1 week, 1 month, 1 year

---

### Story 9.2: Item Rollback

**FRs:** FR57, FR58  
**Priority:** P1  
**Risk:** MEDIUM (data integrity, event logging)

#### Test Cases

**TC-9.2.1: Rollback to Previous Version**
- **Type:** Integration
- **Given:** Item at version 5
- **When:** User runs `rtm rollback <id> --to-version 3`
- **Then:** Item rolled back to version 3 state
- **And:** Rollback event logged
- **Validation:** State matches version 3, version incremented to 6

**TC-9.2.2: Rollback with Confirmation**
- **Type:** E2E
- **Given:** Item exists
- **When:** User runs `rtm rollback <id>` without --confirm
- **Then:** Confirmation prompt displayed
- **Validation:** No rollback without confirmation

**TC-9.2.3: Rollback Metadata Tracking**
- **Type:** Integration
- **Given:** Rollback performed
- **When:** Rollback event queried
- **Then:** Event contains who, when, from_version, to_version
- **Validation:** Complete audit trail

**TC-9.2.4: Rollback Invalid Version**
- **Type:** Integration (Negative)
- **Given:** Item at version 5
- **When:** User tries to rollback to version 10 (doesn't exist)
- **Then:** Error message displayed
- **Validation:** No rollback performed

#### Test Data
- Version ranges: 1-5, 1-100
- Rollback targets: previous version, specific version, first version

---

### Story 9.3: Version History Display

**FRs:** FR55, FR58  
**Priority:** P1  
**Risk:** LOW (display logic)

#### Test Cases

**TC-9.3.1: View Item History**
- **Type:** Integration
- **Given:** Item with 10 versions
- **When:** User runs `rtm history <id>`
- **Then:** All versions displayed with metadata
- **Validation:** Correct chronological order

**TC-9.3.2: History with Diffs**
- **Type:** Integration
- **Given:** Item with field changes
- **When:** User runs `rtm history <id> --diff`
- **Then:** Changes between versions highlighted
- **Validation:** Diff shows what changed

**TC-9.3.3: Filter History by Date Range**
- **Type:** Integration
- **Given:** Item with 100 versions over 1 year
- **When:** User runs `rtm history <id> --since 2025-11-01`
- **Then:** Only versions since date shown
- **Validation:** Correct filtering

**TC-9.3.4: History Pagination**
- **Type:** Integration
- **Given:** Item with 1000 versions
- **When:** User views history
- **Then:** Results paginated (50 per page)
- **Validation:** Performance acceptable

#### Test Data
- Version counts: 10, 100, 1000
- Time ranges: 1 day, 1 month, 1 year
- Change types: title, description, status, metadata

---

## Epic 10: Advanced Search & Filter

**FRs:** FR60-FR67 (8 FRs)  
**Stories:** 5 stories (10.1 - 10.5)  
**Test Cases:** 32 test cases  
**Priority:** P1 (High)  
**Risk:** MEDIUM (search performance, query complexity)

### Story 10.1: Full-Text Search

**FRs:** FR60, FR66  
**Priority:** P1  
**Risk:** HIGH (search performance, relevance ranking)

#### Test Cases

**TC-10.1.1: Basic Full-Text Search**
- **Type:** Integration
- **Given:** 1K items with various content
- **When:** User runs `rtm search "authentication"`
- **Then:** All items containing "authentication" returned
- **Validation:** Search completes in <200ms

**TC-10.1.2: Fuzzy Matching**
- **Type:** Integration
- **Given:** Items exist
- **When:** User searches "autentication" (typo)
- **Then:** Items with "authentication" returned
- **Validation:** Fuzzy matching works (edit distance ≤2)

**TC-10.1.3: Search Ranking**
- **Type:** Integration
- **Given:** Multiple items match query
- **When:** Search executed
- **Then:** Results ranked by relevance (title > description > metadata)
- **Validation:** Most relevant items first

**TC-10.1.4: Search Performance**
- **Type:** Integration (Performance)
- **Given:** 10K items
- **When:** Full-text search executed
- **Then:** Results in <200ms
- **Validation:** Full-text index used

**TC-10.1.5: Search Highlighting**
- **Type:** E2E
- **Given:** Search results returned
- **When:** Results displayed
- **Then:** Matching terms highlighted
- **Validation:** Visual highlighting works

#### Test Data
- Dataset sizes: 100, 1K, 10K items
- Query types: single word, phrase, typo, partial match
- Content locations: title, description, metadata

---

### Story 10.2: Advanced Filtering

**FRs:** FR61-FR64, FR67  
**Priority:** P1  
**Risk:** MEDIUM (complex query building)

#### Test Cases

**TC-10.2.1: Filter by Status**
- **Type:** Integration
- **Given:** Items with various statuses
- **When:** User runs `rtm view FEATURE --status todo,in_progress`
- **Then:** Only items with those statuses shown
- **Validation:** Correct filtering

**TC-10.2.2: Filter by Type**
- **Type:** Integration
- **Given:** Items of various types
- **When:** User runs `rtm view FEATURE --type epic,feature`
- **Then:** Only epics and features shown
- **Validation:** Correct filtering

**TC-10.2.3: Filter by Owner**
- **Type:** Integration
- **Given:** Items assigned to various agents
- **When:** User runs `rtm view FEATURE --owner agent-12`
- **Then:** Only items owned by agent-12 shown
- **Validation:** Correct filtering

**TC-10.2.4: Filter by Date Range**
- **Type:** Integration
- **Given:** Items created over time
- **When:** User runs `rtm view FEATURE --created-after 2025-11-01 --created-before 2025-11-30`
- **Then:** Only items in date range shown
- **Validation:** Correct date filtering

**TC-10.2.5: Combined Filters (AND)**
- **Type:** Integration
- **Given:** Items with various attributes
- **When:** User runs `rtm view FEATURE --status blocked --owner agent-12 --type feature`
- **Then:** Only items matching ALL criteria shown
- **Validation:** AND logic works

**TC-10.2.6: Combined Filters (OR)**
- **Type:** Integration
- **Given:** Items with various attributes
- **When:** User runs `rtm view FEATURE --status "blocked OR in_progress"`
- **Then:** Items matching ANY status shown
- **Validation:** OR logic works

**TC-10.2.7: Complex Filter Expression**
- **Type:** Integration
- **Given:** Items exist
- **When:** User runs `rtm query "(status:blocked AND owner:agent-12) OR priority:high"`
- **Then:** Complex query evaluated correctly
- **Validation:** Expression parser works

#### Test Data
- Statuses: todo, in_progress, blocked, complete, cancelled
- Types: epic, feature, story, task, bug
- Owners: agent-1 to agent-100
- Date ranges: last day, last week, last month, custom range

---

### Story 10.3: Saved Queries

**FRs:** FR65
**Priority:** P2
**Risk:** LOW (simple CRUD)

#### Test Cases

**TC-10.3.1: Save Query**
- **Type:** Integration
- **Given:** User executes complex query
- **When:** User runs `rtm query save "blocked-features" --query "status:blocked AND type:feature"`
- **Then:** Query saved with name
- **Validation:** Query persisted to database

**TC-10.3.2: Execute Saved Query**
- **Type:** Integration
- **Given:** Saved query exists
- **When:** User runs `rtm query run blocked-features`
- **Then:** Saved query executed
- **Validation:** Results match original query

**TC-10.3.3: List Saved Queries**
- **Type:** Integration
- **Given:** 5 saved queries exist
- **When:** User runs `rtm query list`
- **Then:** All saved queries displayed
- **Validation:** Correct list

**TC-10.3.4: Delete Saved Query**
- **Type:** Integration
- **Given:** Saved query exists
- **When:** User runs `rtm query delete blocked-features`
- **Then:** Query deleted
- **Validation:** Query no longer exists

#### Test Data
- Query types: simple, complex, with filters, with search
- Query names: valid, duplicate, invalid characters

---

## Epic 11: Progress Tracking & Reporting

**FRs:** FR68-FR73 (6 FRs)
**Stories:** 4 stories (11.1 - 11.4)
**Test Cases:** 24 test cases
**Priority:** P1 (High)
**Risk:** MEDIUM (calculation complexity, performance)

### Story 11.1: Progress Calculation

**FRs:** FR68, FR69
**Priority:** P1
**Risk:** MEDIUM (recursive calculation, caching)

#### Test Cases

**TC-11.1.1: Auto-Calculate Completion Percentage**
- **Type:** Integration
- **Given:** Epic with 4 features (0%, 50%, 100%, 100%)
- **When:** Progress calculated
- **Then:** Epic progress = 62.5% (average)
- **Validation:** Correct calculation

**TC-11.1.2: Recursive Progress Rollup**
- **Type:** Integration
- **Given:** Epic → Features → Stories → Tasks (4 levels)
- **When:** Task completed
- **Then:** Progress rolls up through all levels
- **Validation:** All parent progress updated

**TC-11.1.3: Real-Time Progress Display**
- **Type:** E2E
- **Given:** Items in PROGRESS view
- **When:** User views progress
- **Then:** Real-time progress bars displayed
- **Validation:** Visual progress indicators

**TC-11.1.4: Progress Calculation Performance**
- **Type:** Integration (Performance)
- **Given:** Epic with 100 children (3 levels deep)
- **When:** Progress calculated
- **Then:** Calculation completes in <100ms
- **Validation:** Efficient recursive query

#### Test Data
- Hierarchy depths: 2, 3, 4 levels
- Children per parent: 1, 10, 100
- Progress values: 0%, 25%, 50%, 75%, 100%

---

### Story 11.2: Blocking Items Detection

**FRs:** FR70, FR71
**Priority:** P1
**Risk:** LOW (query logic)

#### Test Cases

**TC-11.2.1: Identify Blocking Items**
- **Type:** Integration
- **Given:** Item A blocks Item B (via link)
- **When:** User runs `rtm view FEATURE --show-blockers`
- **Then:** Blocking relationships displayed
- **Validation:** Correct blocker identification

**TC-11.2.2: Identify Stalled Items**
- **Type:** Integration
- **Given:** Items with no updates in 30 days
- **When:** User runs `rtm query stalled --days 30`
- **Then:** Stalled items displayed
- **Validation:** Correct date calculation

**TC-11.2.3: Blocker Chain Analysis**
- **Type:** Integration
- **Given:** A blocks B blocks C blocks D
- **When:** User analyzes blockers for D
- **Then:** Full blocker chain displayed
- **Validation:** Transitive blocker detection

#### Test Data
- Blocker chains: 1 level, 3 levels, 5 levels
- Stalled periods: 7 days, 30 days, 90 days

---

### Story 11.3: Progress Reports

**FRs:** FR72, FR73
**Priority:** P2
**Risk:** LOW (reporting logic)

#### Test Cases

**TC-11.3.1: Generate Progress Report**
- **Type:** Integration
- **Given:** Project with activity over 1 month
- **When:** User runs `rtm report progress --period month`
- **Then:** Report generated with completion stats
- **Validation:** Correct statistics

**TC-11.3.2: Velocity Tracking**
- **Type:** Integration
- **Given:** 20 items completed in last week
- **When:** Velocity calculated
- **Then:** Velocity = 20 items/week
- **Validation:** Correct velocity calculation

**TC-11.3.3: Burndown Chart Data**
- **Type:** Integration
- **Given:** Sprint with 50 items
- **When:** User requests burndown data
- **Then:** Daily completion data returned
- **Validation:** Data suitable for charting

**TC-11.3.4: Export Report**
- **Type:** Integration
- **Given:** Report generated
- **When:** User exports to CSV
- **Then:** CSV file created with report data
- **Validation:** Valid CSV format

#### Test Data
- Time periods: day, week, month, quarter
- Item counts: 10, 100, 1000
- Report formats: table, JSON, CSV

---

## Epic 12: Advanced Import/Export

**FRs:** FR76, FR79-FR81 (4 FRs)
**Stories:** 3 stories (12.1 - 12.3)
**Test Cases:** 16 test cases
**Priority:** P2 (Medium)
**Risk:** MEDIUM (external format compatibility)

### Story 12.1: Markdown Export

**FRs:** FR76
**Priority:** P2
**Risk:** LOW (formatting logic)

#### Test Cases

**TC-12.1.1: Export Project as Markdown**
- **Type:** Integration
- **Given:** Project with 100 items
- **When:** User runs `rtm export --format markdown --output project.md`
- **Then:** Markdown file created with all items
- **Validation:** Valid Markdown, readable structure

**TC-12.1.2: Markdown Hierarchy**
- **Type:** Integration
- **Given:** Items with parent-child relationships
- **When:** Exported to Markdown
- **Then:** Hierarchy represented with heading levels
- **Validation:** Correct nesting

**TC-12.1.3: Markdown Links**
- **Type:** Integration
- **Given:** Items with links
- **When:** Exported to Markdown
- **Then:** Links represented as Markdown links
- **Validation:** Links clickable in Markdown viewers

#### Test Data
- Project sizes: 10, 100, 1000 items
- Hierarchy depths: 2, 3, 4 levels

---

### Story 12.2: External Tool Import

**FRs:** FR79-FR81
**Priority:** P2
**Risk:** HIGH (format compatibility, data mapping)

#### Test Cases

**TC-12.2.1: Import from Jira**
- **Type:** Integration
- **Given:** Jira export JSON file
- **When:** User runs `rtm import --source jira --file jira-export.json`
- **Then:** Items imported with correct mapping
- **Validation:** Jira fields mapped to TraceRTM fields

**TC-12.2.2: Import from GitHub Projects**
- **Type:** Integration
- **Given:** GitHub Projects export
- **When:** User imports
- **Then:** Issues/PRs imported as items
- **Validation:** GitHub metadata preserved

**TC-12.2.3: Import Validation**
- **Type:** Integration (Negative)
- **Given:** Invalid Jira export file
- **When:** User attempts import
- **Then:** Validation errors displayed
- **And:** No data imported
- **Validation:** Data integrity maintained

**TC-12.2.4: Import Conflict Resolution**
- **Type:** Integration
- **Given:** Import contains duplicate IDs
- **When:** User imports with --merge flag
- **Then:** Conflicts resolved (update existing)
- **Validation:** Merge strategy works

#### Test Data
- Jira exports: small (10 issues), large (1000 issues)
- GitHub exports: issues only, issues + PRs
- Conflict scenarios: duplicate IDs, missing fields

---

## Traceability Matrix - Phase 2

### FR → Story → Test Case Mapping

| FR ID | Requirement | Story | Test Cases | Status |
|-------|-------------|-------|------------|--------|
| FR56 | Query at specific date | 9.1 | TC-9.1.1, TC-9.1.3 | ✅ Mapped |
| FR57 | Rollback to previous version | 9.2 | TC-9.2.1, TC-9.2.4 | ✅ Mapped |
| FR58 | Version metadata | 9.2, 9.3 | TC-9.2.3, TC-9.3.1 | ✅ Mapped |
| FR59 | Temporal queries | 9.1 | TC-9.1.1, TC-9.1.2 | ✅ Mapped |
| FR60 | Full-text search | 10.1 | TC-10.1.1, TC-10.1.4 | ✅ Mapped |
| FR61 | Filter by status | 10.2 | TC-10.2.1 | ✅ Mapped |
| FR62 | Filter by type | 10.2 | TC-10.2.2 | ✅ Mapped |
| FR63 | Filter by owner | 10.2 | TC-10.2.3 | ✅ Mapped |
| FR64 | Filter by date range | 10.2 | TC-10.2.4 | ✅ Mapped |
| FR65 | Saved queries | 10.3 | TC-10.3.1, TC-10.3.2 | ✅ Mapped |
| FR66 | Fuzzy matching | 10.1 | TC-10.1.2 | ✅ Mapped |
| FR67 | Combined filters | 10.2 | TC-10.2.5, TC-10.2.7 | ✅ Mapped |
| FR68 | Auto-calculate progress | 11.1 | TC-11.1.1, TC-11.1.2 | ✅ Mapped |
| FR69 | Real-time progress | 11.1 | TC-11.1.3 | ✅ Mapped |
| FR70 | Blocking items | 11.2 | TC-11.2.1, TC-11.2.3 | ✅ Mapped |
| FR71 | Stalled items | 11.2 | TC-11.2.2 | ✅ Mapped |
| FR72 | Progress reports | 11.3 | TC-11.3.1, TC-11.3.4 | ✅ Mapped |
| FR73 | Velocity tracking | 11.3 | TC-11.3.2, TC-11.3.3 | ✅ Mapped |
| FR76 | Export as Markdown | 12.1 | TC-12.1.1, TC-12.1.2 | ✅ Mapped |
| FR79 | Import from YAML | 12.2 | (covered by generic import) | ✅ Mapped |
| FR80 | Import from Jira | 12.2 | TC-12.2.1, TC-12.2.3 | ✅ Mapped |
| FR81 | Import from GitHub | 12.2 | TC-12.2.2 | ✅ Mapped |

**Total Phase 2 FRs**: 22/25 mapped (88%)
**Note**: FR74, FR75, FR77, FR78, FR82 partially covered in Epic 7

---

## Summary Statistics

| Epic | Stories | Test Cases | FRs Covered | Priority | Risk |
|------|---------|------------|-------------|----------|------|
| Epic 9 | 3 | 18 | 4 | P1 | HIGH |
| Epic 10 | 3 | 32 | 8 | P1 | MEDIUM |
| Epic 11 | 3 | 24 | 6 | P1 | MEDIUM |
| Epic 12 | 3 | 16 | 4 | P2 | MEDIUM |
| **Total** | **12** | **90** | **22** | - | - |

**Total Phase 2 Test Cases**: 90
**Combined with MVP**: 200 + 90 = **290 total test cases**

---

**Test Design Complete**: 2025-11-21
**Test Architect**: Murat (TEA)
**Status**: ✅ **READY FOR IMPLEMENTATION**
**Next Step**: Implement Phase 2 features



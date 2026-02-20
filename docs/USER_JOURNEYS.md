# TraceRTM — User Journeys

**Version:** 1.0
**Date:** 2026-02-12

This document describes 15 key user journeys for TraceRTM, following the ASCII flow diagram format with timing annotations.

---

## UJ-1: Import Requirements from GitHub Issue (Happy Path)

**Actor:** Requirements Engineer + System
**Frequency:** Daily during active development
**Goal:** Discover → Import → Validate → Link requirements from GitHub issues without manual data entry

```
[09:00] User opens TraceRTM web interface
     │
     ▼
Navigate to Projects → Select "Mobile App Rewrite"
     │
     ▼
Click "Import" → Select "GitHub Issues"
     │
     ▼
Enter GitHub repo: "acme-corp/mobile-app"
Enter filter: labels=["requirements", "enhancement"]
Click "Preview Import"
     │ [0.8s] System calls GitHub API
     ▼
System displays:
  - 47 issues found matching criteria
  - Preview shows: title, body, labels, assignees
  - Status mapping: open→todo, closed→complete
  - Type detection: enhancement→feature, bug→defect
     │
     ▼
User reviews and clicks "Import All"
     │ [2.3s] Batch import processing
     ▼
GitHubImportService processes each issue:
  ├─ Parse issue body for structured data
  ├─ Extract acceptance criteria from checklists
  ├─ Map GitHub labels → TraceRTM tags
  ├─ Create Item records (type=requirement, view=FEATURE)
  ├─ Extract cross-references (#123 → links)
  └─ Log import event for each item
     │
     ▼
[09:00:03] Import complete notification:
  ✅ 47 requirements imported
  ✅ 23 cross-reference links created
  ⚠️  3 items need manual review (ambiguous status)
     │
     ▼
System opens "Review Queue" showing 3 flagged items
User assigns proper status/type to ambiguous items
     │
     ▼
System auto-triggers:
  ├─ AI-based requirement quality check
  ├─ Auto-link to existing code (if enabled)
  └─ Traceability gap analysis
     │
     ▼
Dashboard updates:
  - Requirements coverage: 47/125 (38% → 75%)
  - Unlinked items: 47 new (queued for auto-linking)
  - Next action: "Run Auto-Link Service"
```

**Key Services:**
- `GitHubImportService` - Import from GitHub API
- `ItemRepository` - Create requirement items
- `LinkRepository` - Create traceability links
- `EventRepository` - Log import events

---

## UJ-2: Auto-Link Requirements to Existing Code Using AI

**Actor:** System (triggered by user) + AI Service
**Trigger:** New requirements imported OR user clicks "Auto-Link"
**Goal:** Automatically discover and create traceability links between requirements and code

```
[09:05] User clicks "Auto-Link" button on Requirements view
     │
     ▼
System displays configuration dialog:
  - Link types: [code_implements, code_references, code_tests]
  - Confidence threshold: 0.75 (slider: 0.5-0.95)
  - Scope: "All unlinked requirements" (47 items)
  - AI provider: Claude (via MCP)
     │
     ▼
User confirms → "Start Auto-Linking"
     │ [0.1s] System prepares context
     ▼
AutoLinkService initializes:
  ├─ Load 47 unlinked requirements
  ├─ Scan project codebase (src/, tests/)
  ├─ Build vector index of code + requirements
  └─ Prepare AI prompts with examples
     │
     ▼
[09:05:01] Processing batch 1/5 (10 requirements)
     │
     ▼
For each requirement (e.g., REQ-AUTH-001: "User login with MFA"):
  ├─ AI analyzes requirement text
  ├─ Search codebase for related implementations:
  │   ├─ Pattern match: "MFA", "multi-factor", "authentication"
  │   ├─ Semantic search: authentication flow files
  │   └─ Test file detection: *_test.*, test_*
  ├─ AI scores each candidate file (0.0-1.0):
  │   - src/tracertm/services/workos_auth_service.py: 0.92 (implements MFA)
  │   - tests/test_auth.py: 0.88 (tests MFA flow)
  │   - src/tracertm/api/auth.py: 0.79 (API endpoint)
  └─ Filter by confidence threshold (≥0.75)
     │
     ▼
System proposes links:
  REQ-AUTH-001 → code_implements → workos_auth_service.py (0.92)
  REQ-AUTH-001 → code_tests → tests/test_auth.py (0.88)
  REQ-AUTH-001 → code_references → api/auth.py (0.79)
     │
     ▼
[09:05:08] Batch 1 complete. Results:
  ✅ 10 requirements processed
  ✅ 34 links proposed (28 auto-created, 6 need review)
     │
     ▼
[Batches 2-5 process in parallel via async swarm]
     │ [12s total] All batches complete
     ▼
[09:05:20] Auto-linking complete:
  ✅ 47 requirements processed
  ✅ 142 links created (confidence ≥0.75)
  ⚠️  23 links flagged for manual review (0.65-0.74)
  ❌ 8 requirements found no matches (need manual linking)
     │
     ▼
System displays review panel:
  - High confidence (auto-linked): 142 [Expand]
  - Medium confidence (review): 23 [Review Now]
  - No matches found: 8 [Manual Link]
     │
     ▼
User clicks "Review Now" on medium-confidence links
System shows side-by-side:
  [Requirement Text] ←→ [Code Snippet + AI Rationale]
User approves 18, rejects 5
     │
     ▼
Final tally:
  ✅ 160 links created
  📊 Traceability coverage: 47/47 requirements (100%)
  🔍 Avg confidence: 0.84
```

**Key Services:**
- `AutoLinkService` - Parse commit messages, match items
- `AIService` - Semantic code analysis via MCP
- `LinkRepository` - Create verified links

---

## UJ-3: Generate Traceability Matrix for Compliance Audit

**Actor:** QA Manager
**Trigger:** Quarterly compliance audit scheduled
**Goal:** Generate comprehensive traceability report showing requirements → code → tests coverage

```
[14:00] Compliance audit notification arrives
     │
     ▼
QA Manager opens TraceRTM → "Reports" section
     │
     ▼
Click "Generate Traceability Matrix"
     │
     ▼
System displays matrix configuration:
  - Source view: FEATURE (requirements)
  - Target views: CODE, TEST, DEPLOYMENT
  - Format: [Interactive HTML] [PDF] [Excel] [JSON]
  - Filters:
    ├─ Tags: ["security", "HIPAA-compliance"]
    ├─ Status: [complete, verified]
    └─ Date range: 2025-Q4 to 2026-Q1
     │
     ▼
User selects:
  - Source: FEATURE → Target: CODE, TEST
  - Format: PDF + Excel
  - Filters: Tags include "HIPAA-compliance"
  - Click "Generate Report"
     │ [1.2s] System queries database
     ▼
TraceabilityService.generate_matrix() executes:
  ├─ Query all FEATURE items with "HIPAA-compliance" tag (37 items)
  ├─ For each requirement:
  │   ├─ Find all outbound links (type=code_implements, code_tests)
  │   ├─ Resolve target items (CODE view, TEST view)
  │   ├─ Check link status and verification timestamp
  │   └─ Calculate coverage score
  ├─ Identify gaps:
  │   ├─ Requirements with no CODE links (0 found)
  │   ├─ Requirements with no TEST links (3 found)
  │   └─ CODE items with no TEST links (12 found)
  └─ Compute statistics:
      - Total requirements: 37
      - Fully traced: 34 (92%)
      - Partially traced: 3 (8%)
      - Coverage score: 92%
     │
     ▼
[14:00:02] Report generated
     │
     ▼
System displays preview (HTML):
╔══════════════════════════════════════════════════════════════════╗
║ TraceRTM Traceability Matrix                                    ║
║ Project: Healthcare Portal | Date: 2026-02-12 14:00             ║
║ Filter: HIPAA-compliance | Period: 2025-Q4 to 2026-Q1          ║
╠══════════════════════════════════════════════════════════════════╣
║ Requirement ID    │ Title           │ Code   │ Tests  │ Status  ║
╠═══════════════════╪═════════════════╪════════╪════════╪═════════╣
║ REQ-SEC-001       │ Patient data    │ ✅ 3   │ ✅ 5   │ ✓ 100%  ║
║                   │ encryption      │        │        │         ║
║ REQ-SEC-002       │ Audit logging   │ ✅ 2   │ ✅ 3   │ ✓ 100%  ║
║ REQ-AUTH-003      │ MFA requirement │ ✅ 4   │ ⚠️  0  │ ⚠️  67% ║
║ ...               │ ...             │ ...    │ ...    │ ...     ║
╠═══════════════════╧═════════════════╧════════╧════════╧═════════╣
║ SUMMARY:                                                         ║
║ • Total Requirements: 37                                         ║
║ • Fully Traced (100%): 34 (92%)                                  ║
║ • Partially Traced: 3 (8%)                                       ║
║ • Gaps Identified: 3 requirements missing test coverage          ║
║ • Compliance Score: 92% (threshold: 90%) ✅ PASS                ║
╚══════════════════════════════════════════════════════════════════╝
     │
     ▼
User downloads PDF and Excel versions
System emails report to audit team
System logs audit event for compliance trail
```

**Key Services:**
- `TraceabilityService` - Generate matrix, compute coverage
- `ExportService` - PDF/Excel rendering
- `EventRepository` - Log audit events

---

## UJ-4: Analyze Impact of Requirement Change on Downstream Tests

**Actor:** Product Manager + System
**Trigger:** Requirement change request approved
**Goal:** Understand blast radius before implementing change

```
[10:30] PM receives change request:
        "REQ-API-007: Add pagination to user search endpoint"
     │
     ▼
PM opens TraceRTM → Search "REQ-API-007"
     │
     ▼
Requirement details page displays:
  - Current state: "Returns all users (no pagination)"
  - Status: complete
  - Linked code: 3 files
  - Linked tests: 8 test cases
     │
     ▼
PM clicks "Analyze Impact" button
     │ [0.5s] System runs impact analysis
     ▼
ImpactAnalysisService.analyze() executes:
  ├─ Find all direct links from REQ-API-007:
  │   ├─ CODE: src/tracertm/api/users.py (get_all_users endpoint)
  │   ├─ CODE: frontend/src/api/users.ts (client SDK)
  │   └─ CODE: backend/handlers/users.go (backup handler)
  ├─ Find all test links:
  │   ├─ TEST: tests/test_users_api.py (8 test cases)
  │   └─ TEST: frontend/tests/users.test.ts (12 test cases)
  ├─ Recursively find downstream dependencies:
  │   ├─ Level 1: Direct dependencies (11 items)
  │   ├─ Level 2: Tests that call get_all_users (20 items)
  │   └─ Level 3: Integration tests with user flows (7 items)
  └─ Calculate impact score:
      - Directly affected: 11 items (3 CODE + 8 TEST)
      - Indirectly affected: 27 items (20 tests + 7 integrations)
      - Total impact: 38 items
      - Risk level: HIGH (>30 items affected)
     │
     ▼
[10:30:01] Impact analysis complete
     │
     ▼
System displays interactive impact graph:
                     ┌─────────────────┐
                     │  REQ-API-007    │ ← Change here
                     │  (User Search)  │
                     └────────┬────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        [users.py]     [users.ts]      [users.go]
        3 functions    2 functions     1 function
              │               │               │
        ┌─────┴─────┐   ┌─────┴─────┐   ┌───┴────┐
        ▼           ▼   ▼           ▼   ▼        ▼
    8 Python    12 TS  5 Go      7 E2E   3 Load   2 Perf
    tests       tests  tests     tests   tests    tests
     │
     ▼
System generates change plan:
  1. Update API endpoint (users.py, users.go, users.ts)
  2. Add pagination parameters (page, page_size, cursor)
  3. Update 8 Python tests (add pagination assertions)
  4. Update 12 TS tests (handle paginated responses)
  5. Update E2E tests (loop through pages)
  6. Update documentation (API spec, user guide)
  Estimated effort: 8-12 hours
  Tests to update: 38
```

**Key Services:**
- `ImpactAnalysisService` - Recursive dependency traversal
- `GraphAnalysisService` - Dependency graph visualization
- `ItemRepository` - Query linked items

---

## UJ-5: Execute BDD Scenarios Written in Gherkin

**Actor:** QA Engineer + Test Execution Engine
**Trigger:** Nightly test run OR manual trigger
**Goal:** Run Gherkin scenarios, report results, update traceability

```
[22:00 Cron] Nightly test run triggers
     │
     ▼
System loads test configuration:
  - Project: "E-Commerce Platform"
  - Feature: "Checkout Flow" (FEAT-0042)
  - Scenarios: 23 (status=ready)
  - Environment: staging
  - Browser: Chrome headless
     │
     ▼
ScenarioService.get_scenarios_by_feature() loads Gherkin:
  SCENARIO-0156: "Guest checkout with credit card"
    Given I am on the product page
      And I add "Blue Widget" to cart
    When I proceed to checkout as guest
      And I enter shipping address "123 Main St, Austin TX"
      And I enter credit card "4111-1111-1111-1111"
      And I click "Place Order"
    Then I should see "Order Confirmation"
      And I should receive email to "guest@example.com"
      And order status should be "pending"
     │
     ▼
[22:00:05] Test runner executes step-by-step:
     │
     ▼
[Step 1] Given I am on the product page
  → Navigate to https://staging.acme.com/product/blue-widget
  → Wait for page load (1.2s)
  ✅ PASS
     │
     ▼
[Step 2] And I add "Blue Widget" to cart
  → Click button[data-test="add-to-cart"]
  → Wait for cart count update
  ✅ PASS (0.3s)
     │
     ▼
[22:12:45] Test run complete
  ✅ Passed: 18/23 (78%)
  ❌ Failed: 4/23 (17%)
  ⏭️  Skipped: 1/23 (4%)
     │
     ▼
System generates report and updates traceability:
  - REQ-PAY-003 → status: needs_attention
  - 4 incidents created and assigned
```

**Key Services:**
- `ScenarioService` - Manage BDD scenarios
- `FeatureService` - Group scenarios by feature
- Test execution engine (Playwright/Selenium integration)

---

## UJ-6: Create ADR with AI Assistance (Using MCP Tools)

**Actor:** Tech Lead + AI (Claude via MCP)
**Trigger:** Architecture decision needed
**Goal:** Document decision with context, alternatives, and consequences using AI assistance

```
[15:00] Tech Lead identifies need for decision:
        "How should we handle real-time notifications?"
     │
     ▼
Tech Lead opens Claude chat (with MCP tools enabled)
     │
     ▼
Tech Lead: "I need to create an ADR for real-time notifications.
            Options: WebSockets, Server-Sent Events, or long polling.
            Help me document this decision."
     │
     ▼
Claude → MCP tool: tracertm_list_adrs(project="E-Commerce Platform")
  Returns: 23 existing ADRs
     │
     ▼
Claude → MCP tool: tracertm_search_requirements(keywords=["notification", "real-time"])
  Returns: 5 related requirements
     │
     ▼
Claude drafts ADR and presents recommendation
     │
     ▼
Tech Lead approves: "Yes, create it. Add tag 'architecture'"
     │
     ▼
Claude → MCP tool: tracertm_create_adr(
  project_id="e-commerce-platform",
  title="Real-Time Notifications Using Server-Sent Events + NATS",
  context="[...context text...]",
  decision="Use Server-Sent Events (SSE) with NATS pub/sub backend",
  consequences="[...consequences...]",
  status="accepted"
)
     │
     ▼
[15:05] ADR-0024 created successfully and linked to requirements
```

**Key Services:**
- `ADRService` - Create and manage ADRs
- MCP integration - AI-assisted documentation
- `LinkRepository` - Link ADRs to requirements

---

## UJ-7: Sync Requirements Bidirectionally with Jira

**Actor:** System (scheduled sync) + User (manual trigger)
**Trigger:** Hourly sync cron OR user clicks "Sync Now"
**Goal:** Keep TraceRTM and Jira requirements in sync without manual copy-paste

```
[Hourly at :00] Sync cron triggers
     │
     ▼
JiraImportService.sync_project() executes:
  ├─ Load sync configuration
  ├─ Query Jira API for changes since last sync
  │   → Returns 8 updated issues
  └─ Query TraceRTM for changes since last sync
      → Returns 5 updated items
     │
     ▼
[Phase 1: Jira → TraceRTM]
  ├─ 5 items updated in TraceRTM
  └─ 3 items created in TraceRTM
     │
     ▼
[Phase 2: TraceRTM → Jira]
  ├─ 2 items updated in Jira
  └─ 3 items need Jira issue creation
     │
     ▼
[14:00:08] Sync complete notification:
  ✅ 8 items synced from Jira
  ✅ 2 items synced to Jira
  ⚠️  3 items need Jira issue creation
  No conflicts detected
```

**Key Services:**
- `JiraImportService` - Bidirectional sync
- `SyncService` - Conflict detection and resolution
- `EventRepository` - Log sync events

---

## UJ-8: Generate Test Coverage Report Filtered by Feature

**Actor:** Release Manager
**Trigger:** Pre-release gate OR weekly report
**Goal:** Verify test coverage for specific feature before release approval

```
[16:00] Release Manager prepares for v2.3.0 release
     │
     ▼
Opens TraceRTM → "Test Coverage" dashboard
     │
     ▼
Selects filters:
  - Feature: "Payment Gateway Integration" (FEAT-0042)
  - Include: Unit tests, Integration tests, E2E tests
  - Date range: Sprint 23 (Jan 15 - Feb 12, 2026)
     │
     ▼
Click "Generate Coverage Report"
     │ [0.8s] System queries test execution data
     ▼
System aggregates:
  ├─ Find all requirements under FEAT-0042 (12 requirements)
  ├─ Find all test cases linked (47 tests)
  ├─ Find all code files linked (23 files)
  ├─ Query test execution history (last 30 days)
  └─ Calculate code coverage from test runs
     │
     ▼
[16:00:01] Report generated showing:
  - Requirements: 12 total
  - Test Cases: 47 total
  - Code Coverage: 83% (target: 80%) ✅
  - Test Pass Rate: 94% (44/47) ⚠️
  - Blockers: 2 requirements with no tests
```

**Key Services:**
- Test coverage aggregation service
- `TraceabilityService` - Requirements → tests mapping
- `ExportService` - PDF/Excel reporting

---

## UJ-9: Collaborate in Real-Time (Presence Tracking, Conflict Resolution)

**Actor:** Multiple team members (Alice, Bob) + System
**Trigger:** Concurrent editing of same requirement
**Goal:** Prevent conflicts, show real-time presence, merge changes gracefully

```
[11:00:00] Alice opens requirement REQ-FEAT-042
     │
     ▼
System establishes WebSocket connection
System registers presence:
  - User: Alice
  - Item: REQ-FEAT-042
  - Action: viewing
     │
     ▼
Alice starts editing title:
  Before: "User profile page"
  After: "User profile page with avatar upload"
     │
     ▼
[11:00:15] Bob opens same requirement
     │
     ▼
System sends presence notification:
  ⚠️  "Alice is currently editing this item (title field)"
     │
     ▼
[CONFLICT SCENARIO - Both edit acceptance criteria]
     │
     ▼
System detects conflict and triggers resolution UI:
  - Alice's changes: "Must support JPEG, PNG, GIF"
  - Bob's changes: "Must validate file size (max 5MB)"
     │
     ▼
Alice clicks "Merge both" (AI-assisted merge)
System proposes merged version
Both users accept merge
     │
     ▼
[11:02:45] Conflict resolved
  - New version 6 created with merged changes
  - Audit log records conflict and resolution
```

**Key Services:**
- `ConflictResolutionService` - Detect and resolve conflicts
- WebSocket service - Real-time presence
- `EventRepository` - Log collaboration events

---

## UJ-10: Build and Visualize Dependency Graph

**Actor:** Engineering Manager
**Trigger:** Sprint planning OR architecture review
**Goal:** Understand requirement dependencies and identify critical path

```
[09:30] Engineering Manager opens TraceRTM
     │
     ▼
Navigate to Project "Mobile App Rewrite" → "Dependency Graph"
     │
     ▼
User selects:
  - View: FEATURE
  - Layout: Hierarchical
  - Link types: depends_on, blocks
  - Highlight: Critical path
  - Click "Generate Graph"
     │ [1.2s] System builds graph
     ▼
GraphAnalysisService.build_dependency_graph() executes:
  ├─ Query all FEATURE items (87 items)
  ├─ Query all links (156 dependencies)
  ├─ Build directed graph (NetworkX)
  ├─ Detect cycles (if any)
  ├─ Calculate critical path
  └─ Generate layout coordinates
     │
     ▼
[09:30:02] Graph rendered in browser with interactive controls:
  - Zoom, pan, center, fit to screen
  - Collapse/expand subtrees
  - Filter by tag/status
  - Export as PNG/SVG/JSON
     │
     ▼
User analyzes critical path and identifies bottlenecks
Team adjusts sprint plan based on dependencies
```

**Key Services:**
- `GraphAnalysisService` - Dependency graph computation
- `CriticalPathService` - Longest path analysis
- `CycleDetectionService` - Detect circular dependencies

---

## UJ-11: Execute Temporal Workflow with Checkpointing

**Actor:** System (Temporal worker) + User (monitoring)
**Trigger:** Long-running data migration OR scheduled batch job
**Goal:** Execute multi-step workflow with fault tolerance and progress tracking

```
[02:00 Cron] Nightly data migration job triggers
     │
     ▼
TemporalService.start_workflow() executes:
  - Workflow: "Migrate Legacy Requirements"
  - Steps: 5 (extract, transform, validate, load, verify)
  - Estimated duration: 45 minutes
  - Checkpointing: enabled (every step)
     │
     ▼
[02:00:05] STEP 1: Extract Legacy Data
  ├─ Connect to legacy MySQL database
  ├─ Query: SELECT * FROM requirements WHERE migrated_at IS NULL
  ├─ Returns: 2,847 requirements
  └─ Checkpoint: Step 1 complete
     │ Duration: 3m 12s
     ▼
[02:03:17] STEP 2: Transform Data
  ├─ Parse legacy format (XML → JSON)
  ├─ Map fields: legacy_status → TraceRTM status
  ├─ Progress: 2,847/2,847 (100%)
  └─ Checkpoint: Step 2 complete
     │ Duration: 8m 45s
     ▼
[02:14:20] STEP 4: Load to TraceRTM
  ├─ Begin database transaction
  ├─ Insert valid requirements (2,798) in batches
  │
  │ [02:18:45] ❌ ERROR: Database connection lost
     │
     ▼
Temporal automatically retries:
  - Retry 1: Reconnect to database → Success
  - Resume from checkpoint (Step 3 complete)
  - Continue loading from batch 1600/2798
     │
     ▼
[02:22:27] Workflow complete
     │ Total duration: 22m 22s (including 1 retry)
     ▼
System sends completion notification with summary
```

**Key Services:**
- `TemporalService` - Workflow orchestration
- Temporal server - Checkpointing and retry logic
- `ImportService` - Data migration logic

---

## UJ-12: Use TraceRTM via Claude MCP Integration

**Actor:** Developer + Claude (AI assistant)
**Trigger:** Developer needs to create requirements from user story
**Goal:** Create and link requirements using natural language via Claude MCP tools

```
[10:00] Developer opens Claude chat (MCP enabled)
     │
     ▼
Developer: "I need to create requirements for our new search feature.
            Here's the user story: 'As a user, I want to search for
            requirements by keywords so I can find relevant items quickly.'
            Break this down into requirements and create them in TraceRTM."
     │
     ▼
Claude → MCP tool: tracertm_list_projects()
  Returns: ["Mobile App Rewrite", "E-Commerce Platform"]
     │
     ▼
Claude plans requirement breakdown and asks clarifications
     │
     ▼
Developer: "Mobile App Rewrite, and add tags 'search' and 'sprint-24'"
     │
     ▼
Claude → MCP tool: tracertm_create_item() [5 times]
  Creates: FR-SEARCH-001 through FR-SEARCH-005
     │
     ▼
Claude → MCP tool: tracertm_create_link() [4 times]
  Links: FR-SEARCH-001 depends_on FR-SEARCH-002..005
     │
     ▼
[10:00:10] All requirements created and linked
     │
     ▼
Claude provides summary with TraceRTM link
Developer can immediately view in web UI
```

**Key Services:**
- MCP server - Claude integration
- `ItemService` - Create requirements
- `LinkRepository` - Create dependencies

---

## UJ-13: Deploy to Production with Health Checks

**Actor:** DevOps Engineer + CI/CD System
**Trigger:** Release candidate ready OR manual deploy request
**Goal:** Deploy with automated health checks and rollback capability

```
[17:00] DevOps engineer approves release v2.3.0
     │
     ▼
CI/CD pipeline (GitHub Actions) starts:
  - Job: Deploy TraceRTM v2.3.0 to Production
  - Environment: production-us-east-1
  - Strategy: Blue/Green deployment
     │
     ▼
[Step 1: Pre-deployment Checks] [0:30]
  ├─ Verify Docker images built
  ├─ Run security scan
  ├─ Check database migrations
  ├─ Verify secrets in Vault
  └─ Backup current production database
     │
     ▼
[Step 2: Deploy to Blue Environment] [2:15]
  ├─ kubectl apply -f k8s/blue-environment/
  ├─ Wait for pods to be Ready
  └─ All pods ready
     │
     ▼
[Step 3: Run Database Migrations] [0:45]
  ├─ alembic upgrade head
  └─ 3 migrations applied successfully
     │
     ▼
[Step 4: Health Check Blue Environment] [1:30]
  ├─ HTTP health endpoints: ✅
  ├─ Smoke tests: ✅
  └─ Performance tests: ✅
     │
     ▼
[Step 5: Canary Testing] [5:00]
  ├─ Route 5% traffic to blue
  ├─ Monitor for 5 minutes
  └─ Canary successful
     │
     ▼
[Step 6: Full Cutover to Blue] [0:10]
  ├─ Route 100% traffic to blue
  └─ Verify traffic routing
     │
     ▼
[17:22] Deployment complete:
  ✅ All health checks passed
  ✅ Zero downtime cutover
  ✅ Rollback available for 24 hours
```

**Key Services:**
- Kubernetes deployment
- Health check endpoints
- Prometheus metrics

---

## UJ-14: Troubleshoot Failed Test Using Trace Logs

**Actor:** QA Engineer
**Trigger:** Test failure notification
**Goal:** Diagnose root cause using distributed tracing and logs

```
[14:30] QA Engineer receives alert:
        "❌ E2E Test Failed: Checkout Flow - Payment Processing"
     │
     ▼
Opens TraceRTM → "Test Runs" → Search test run ID
     │
     ▼
Test run details display:
  - Scenario: SCENARIO-0156 (Guest checkout)
  - Status: FAILED
  - Failed step: "Enter credit card and submit payment"
  - Error: "Element #cvv-field not found (timeout)"
     │
     ▼
QA Engineer clicks "View Trace Logs"
     │ [0.5s] System loads distributed trace
     ▼
System displays trace timeline (OpenTelemetry spans):
  - Trace ID: 7f3e9c8d-4b2a-11ef-9a5c-0242ac120002
  - Duration: 12.5s | Spans: 47 | Errors: 1
     │
     ▼
QA Engineer drills down to error span:
  - stripe_api.create_payment_intent
  - Status: 503 Service Unavailable
  - Error: "The server is temporarily unable to service your request"
     │
     ▼
Root cause identified: External Stripe API outage
     │
     ▼
QA Engineer documents findings:
  - Update test result: FAILED → EXTERNAL_ISSUE
  - Note: "Stripe API 503 during test execution"
  - Schedule re-run after incident resolved
```

**Key Services:**
- OpenTelemetry integration
- Distributed tracing service
- Log aggregation

---

## UJ-15: Audit Compliance Requirements for Regulatory Review

**Actor:** Compliance Officer + System
**Trigger:** Annual regulatory audit (HIPAA, SOC2, FDA)
**Goal:** Generate comprehensive audit report with full traceability chain

```
[09:00] Compliance Officer prepares for HIPAA audit
     │
     ▼
Opens TraceRTM → "Compliance Audit" section
     │
     ▼
System displays audit configuration:
  - Regulatory framework: [HIPAA] [SOC2] [FDA 21 CFR Part 11]
  - Audit period: Q4 2025 (Oct 1 - Dec 31)
  - Scope: All HIPAA-tagged requirements
  - Output format: [PDF] [Excel] [JSON] [Audit Trail Log]
     │
     ▼
User selects HIPAA framework and clicks "Generate Audit Report"
     │ [5.2s] System aggregates compliance data
     ▼
System executes compliance query:
  ├─ Query all requirements with HIPAA tags (73 requirements)
  ├─ For each requirement:
  │   ├─ Find linked code implementations
  │   ├─ Find linked test cases
  │   ├─ Find test execution records
  │   ├─ Find code review records
  │   └─ Check deployment status
  ├─ Identify compliance gaps
  └─ Calculate compliance score:
      - Total requirements: 73
      - Fully compliant: 66 (90%)
      - Partially compliant: 7 (10%)
      - Overall score: 90% ✅ (threshold: 85%)
     │
     ▼
[09:00:06] Report generated
     │
     ▼
System displays audit report with:
  - Executive summary
  - Requirement coverage by HIPAA section
  - Full traceability chains (requirement → code → test → deploy)
  - Compliance gaps and remediation plans
  - Audit trail integrity verification
  - Change history
  - Digital signature
     │
     ▼
Compliance Officer reviews and exports report
Shares with auditors and regulatory body
System archives for 7 years (retention policy)
```

**Key Services:**
- Compliance audit service
- `TraceabilityService` - Full traceability chains
- `EventRepository` - Audit trail verification
- `ExportService` - PDF/Excel with digital signatures

---

## Journey Summary

| ID | Journey | Frequency | Automation Level |
|----|---------|-----------|------------------|
| UJ-1 | Import GitHub Requirements | Daily | 80% automated |
| UJ-2 | Auto-Link Requirements to Code | On-demand | 90% automated |
| UJ-3 | Generate Traceability Matrix | Weekly/Audit | 95% automated |
| UJ-4 | Analyze Requirement Change Impact | Per change | 85% automated |
| UJ-5 | Execute BDD Scenarios | Nightly/CI | 100% automated |
| UJ-6 | Create ADR with AI (MCP) | As needed | 70% AI-assisted |
| UJ-7 | Sync with Jira Bidirectionally | Hourly | 100% automated |
| UJ-8 | Generate Test Coverage Report | Weekly/Release | 95% automated |
| UJ-9 | Real-Time Collaboration | Continuous | 95% automated |
| UJ-10 | Visualize Dependency Graph | Sprint planning | 90% automated |
| UJ-11 | Execute Temporal Workflow | Scheduled/On-demand | 100% automated |
| UJ-12 | Use TraceRTM via Claude MCP | As needed | 60% AI-assisted |
| UJ-13 | Deploy with Health Checks | Per release | 95% automated |
| UJ-14 | Troubleshoot Failed Test | Per failure | 50% manual |
| UJ-15 | Audit Compliance Requirements | Quarterly/Annual | 90% automated |

---

## Key Patterns

### Timing Annotations
All journeys include precise timing (e.g., `[09:00:03]`, `[2.3s]`) showing:
- Wall-clock time for user-initiated actions
- Duration for system operations
- Cumulative time for multi-step processes

### Error Handling
Multiple journeys demonstrate:
- Graceful degradation (UJ-5: external API failures, UJ-11: DB connection lost)
- Automatic retries with exponential backoff
- User notifications with actionable context
- Fallback strategies (UJ-9: conflict resolution)

### Integration Points
Journeys show integration with:
- External systems (GitHub, Jira, Stripe, Temporal)
- AI/MCP tools (UJ-2, UJ-6, UJ-12)
- CI/CD pipelines (UJ-13)
- Observability tools (UJ-14: OpenTelemetry)

### User Experience
All journeys emphasize:
- Real-time feedback (progress indicators, notifications)
- Contextual actions (drill-down, quick links)
- Bulk operations (batch imports, parallel processing)
- Collaboration features (presence, conflict resolution)

### Service Architecture
Each journey explicitly references the key TraceRTM services involved:
- `GitHubImportService`, `JiraImportService` - External integrations
- `TraceabilityService` - Matrix generation, coverage analysis
- `ImpactAnalysisService`, `GraphAnalysisService` - Dependency analysis
- `ScenarioService`, `FeatureService` - BDD test management
- `ADRService` - Architecture decision records
- `ConflictResolutionService` - Real-time collaboration
- `TemporalService` - Workflow orchestration
- MCP integration - AI-assisted operations

---

## Cross-Journey Workflows

### Full Requirements Lifecycle (UJ-1 → UJ-2 → UJ-3)
1. Import requirements from GitHub (UJ-1)
2. Auto-link to existing code (UJ-2)
3. Generate traceability matrix for audit (UJ-3)

### Change Impact Analysis (UJ-4 → UJ-8 → UJ-13)
1. Analyze impact of requirement change (UJ-4)
2. Verify test coverage before release (UJ-8)
3. Deploy with health checks (UJ-13)

### AI-Assisted Documentation (UJ-6 → UJ-12)
1. Create ADR with AI assistance (UJ-6)
2. Use Claude MCP for requirement creation (UJ-12)

### Troubleshooting and Compliance (UJ-14 → UJ-15)
1. Debug failed tests using traces (UJ-14)
2. Generate compliance audit report (UJ-15)

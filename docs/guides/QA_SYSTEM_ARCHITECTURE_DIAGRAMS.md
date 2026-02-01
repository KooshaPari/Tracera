# QA System Architecture - Visual Diagrams

## 1. System Component Diagram

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                            TraceRTM QA+QC System                               │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────────────┐                    ┌─────────────────────────┐  │
│  │  Frontend Layer          │                    │  GitHub External API    │  │
│  ├──────────────────────────┤                    │  ┌─────────────────────┐│  │
│  │                          │                    │  │ - Check Runs        ││  │
│  │ ┌──────────────────────┐ │                    │  │ - PR Comments       ││  │
│  │ │ Enhanced Graph View  │ │                    │  │ - Webhooks          ││  │
│  │ │ - Rich Nodes         │ │◄──────────────────►│  │ - Status Checks     ││  │
│  │ │ - Test Metrics       │ │                    │  └─────────────────────┘│  │
│  │ │ - Artifacts          │ │                    │                          │  │
│  │ └──────────────────────┘ │                    └─────────────────────────┘  │
│  │                          │                                                  │
│  │ ┌──────────────────────┐ │                    ┌─────────────────────────┐  │
│  │ │ Execution Controls   │ │                    │  Container Registry    │  │
│  │ │ - Run Tests          │ │                    │  ┌─────────────────────┐│  │
│  │ │ - Monitor Progress   │ │◄──────────────────►│  │ Docker Hub/ECR      ││  │
│  │ │ - View Results       │ │                    │  │ Node:20, Python:3.12││  │
│  │ └──────────────────────┘ │                    │  │ etc                 ││  │
│  │                          │                    │  └─────────────────────┘│  │
│  │ ┌──────────────────────┐ │                    └─────────────────────────┘  │
│  │ │ Artifact Gallery     │ │                                                  │
│  │ │ - Screenshots        │ │                    ┌─────────────────────────┐  │
│  │ │ - Videos             │ │◄──────────────────►│  S3 / S3-Compatible    │  │
│  │ │ - Logs               │ │                    │  Object Storage        │  │
│  │ │ - Metrics            │ │                    └─────────────────────────┘  │
│  │ └──────────────────────┘ │                                                  │
│  │                          │                                                  │
│  └──────────────────────────┘                                                  │
│                   ▲                                                             │
│                   │ tRPC API                                                   │
│                   │ REST API                                                   │
│                   │ WebSockets                                                 │
│                   ▼                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │              Backend API Layer (FastAPI)                               │   │
│  ├────────────────────────────────────────────────────────────────────────┤   │
│  │ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │   │
│  │ │ Execution    │  │ Artifact     │  │ GitHub       │  │ Integration│ │   │
│  │ │ Endpoints    │  │ Endpoints    │  │ Endpoints    │  │ Endpoints  │ │   │
│  │ ├──────────────┤  ├──────────────┤  ├──────────────┤  ├────────────┤ │   │
│  │ │ - Execute    │  │ - Upload     │  │ - Webhook    │  │ - Config   │ │   │
│  │ │ - Status     │  │ - Download   │  │ - Check Run  │  │ - Sync     │ │   │
│  │ │ - Logs       │  │ - Preview    │  │ - Comment    │  │            │ │   │
│  │ │ - Cancel     │  │ - Share      │  │ - Status     │  │            │ │   │
│  │ └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │   │
│  │                                                                        │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                   ▲                                                             │
│                   │ Service Interfaces                                         │
│                   ▼                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │              Business Logic Service Layer                              │   │
│  ├────────────────────────────────────────────────────────────────────────┤   │
│  │ ┌──────────────────────────┐  ┌──────────────────────────────────────┐│   │
│  │ │ Execution Orchestration  │  │ Artifact Management                  ││   │
│  │ ├──────────────────────────┤  ├──────────────────────────────────────┤│   │
│  │ │ ExecutionEnvironment     │  │ ArtifactCaptureService               ││   │
│  │ │ ExecutionSession         │  │ ArtifactProcessorService             ││   │
│  │ │ TestEnvironmentOrchest.  │  │ ArtifactStorageService               ││   │
│  │ │ DockerTestRunner         │  │ RetentionPolicyService               ││   │
│  │ │ GitHubWebhookHandler     │  │                                      ││   │
│  │ │ GitHubCheckRunsService   │  │                                      ││   │
│  │ └──────────────────────────┘  └──────────────────────────────────────┘│   │
│  │                                                                        │   │
│  │ ┌──────────────────────────────────────────────────────────────────┐ │   │
│  │ │ Test Framework Adapters                                          │ │   │
│  │ │ - Jest/Vitest (Node.js)    - Pytest/Unittest (Python)            │ │   │
│  │ │ - Playwright/Cypress       - Go Test                             │ │   │
│  │ │ - Cargo Test (Rust)                                              │ │   │
│  │ └──────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                        │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                   ▲                                                             │
│                   │ Repository Interfaces                                      │
│                   ▼                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │              Data Access Layer (Repositories)                          │   │
│  ├────────────────────────────────────────────────────────────────────────┤   │
│  │ ExecutionEnvironmentRepository                                        │   │
│  │ ExecutionSessionRepository                                           │   │
│  │ ExecutionArtifactRepository                                          │   │
│  │ TestNodeMetadataRepository                                           │   │
│  │ IntegrationMappingRepository (existing, enhanced)                   │   │
│  │                                                                        │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                   ▲                                                             │
│                   │ SQLAlchemy ORM                                             │
│                   ▼                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │              Persistent Storage Layer                                  │   │
│  ├────────────────────────────────────────────────────────────────────────┤   │
│  │ PostgreSQL / SQLite                                                   │   │
│  │ - execution_environments                                              │   │
│  │ - execution_sessions                                                  │   │
│  │ - execution_artifacts                                                 │   │
│  │ - test_node_metadata                                                  │   │
│  │ - test_results (enhanced)                                             │   │
│  │ - test_runs (existing)                                                │   │
│  │ - integration_mappings (existing)                                     │   │
│  │                                                                        │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└────────────────────────────────────────────────────────────────────────────────┘

                               ┌──────────────────────────┐
                               │   Docker Daemon          │
                               │  (Code Execution)        │
                               │                          │
                               │ ┌────────────────────────┤
                               │ │ Container Instances    │
                               │ │ - Isolated Filesystems │
                               │ │ - Resource Limits      │
                               │ │ - Network Isolation    │
                               │ └────────────────────────┤
                               └──────────────────────────┘
```

---

## 2. Execution Flow Diagram

```
User Action / Webhook Event
        │
        ▼
    ┌────────────────────────────────┐
    │ Execution Request Handler      │
    │ - Validate inputs              │
    │ - Find/create environment      │
    │ - Create execution session     │
    └────────────┬───────────────────┘
                 │
        ┌────────▼────────┐
        │ Update DB:      │
        │ ExecutionSession│
        │ status=pending  │
        └────────┬────────┘
                 │
        ┌────────▼────────────────────────┐
        │ TestEnvironmentOrchestrator     │
        │ .execute_test_suite()           │
        └────────┬───────────────────────┘
                 │
        ┌────────▼──────────────────┐
        │ DockerTestRunner          │
        │ .provision_container()    │
        │ - Pull base image         │
        │ - Clone repository        │
        │ - Install dependencies    │
        │ - Setup environment       │
        └────────┬──────────────────┘
                 │
        ┌────────▼──────────────────┐
        │ Update DB:                │
        │ status=provisioning       │
        │ container_id set          │
        └────────┬──────────────────┘
                 │
        ┌────────▼──────────────────────────┐
        │ DockerTestRunner                  │
        │ .execute_tests()                  │
        │ - Run test command in container   │
        │ - Capture real-time output        │
        │ - Stream logs via WebSocket       │
        │ - Trigger artifact capture hooks  │
        └────────┬───────────────────────────┘
                 │
        ┌────────▼──────────────────────┐
        │ ArtifactCaptureService        │
        │ (Parallel to test execution)  │
        │ - Screenshots on failure      │
        │ - Video recording             │
        │ - Coverage reports            │
        │ - Console logs                │
        └────────┬───────────────────────┘
                 │
        ┌────────▼──────────────────────┐
        │ ArtifactStorageService        │
        │ - Compress images             │
        │ - Generate thumbnails         │
        │ - Upload to S3                │
        │ - Update DB with paths        │
        └────────┬───────────────────────┘
                 │
        ┌────────▼──────────────────────┐
        │ All tests completed           │
        │ Parse results (JSON/XML)      │
        └────────┬───────────────────────┘
                 │
        ┌────────▼──────────────────────────┐
        │ Update DB:                        │
        │ - TestResult records              │
        │ - ExecutionSession metrics        │
        │ - TestNodeMetadata (pass_rate)    │
        │ - status=completed                │
        └────────┬───────────────────────────┘
                 │
        ┌────────▼──────────────────────┐
        │ IF GitHub Integration:        │
        │ GitHubCheckRunsService        │
        │ .update_check_run()           │
        │ .post_test_results_comment()  │
        └────────┬───────────────────────┘
                 │
        ┌────────▼──────────────────────┐
        │ Cleanup                       │
        │ - Stop Docker container       │
        │ - Remove temporary files      │
        │ - Update metrics              │
        └────────┬───────────────────────┘
                 │
        ┌────────▼──────────────────────┐
        │ Return Results to Frontend    │
        │ - Update ExecutionSession UI  │
        │ - Show artifacts              │
        │ - Update graph node metrics   │
        └───────────────────────────────┘
```

---

## 3. Data Model Relationships

```
┌──────────────────┐
│   Project        │
│  (existing)      │
└────────┬─────────┘
         │1
         │
         │ N
    ┌────▼──────────────────────────────┐
    │ ExecutionEnvironment              │
    ├──────────────────────────────────┤
    │ id (PK)                          │
    │ project_id (FK) ─────────────────┼──────────┐
    │ repo_url                         │          │
    │ runtime                          │          │
    │ package_manager                  │          │
    │ detected_frameworks[]            │          │
    │ status                           │          │
    │ integration_credential_id (FK)   │          │
    │ created_at, updated_at           │          │
    └────┬──────────────────────────────┘          │
         │ 1                                       │
         │                                         │
         │ N                                       │
    ┌────▼──────────────────────────────┐          │
    │ ExecutionSession                 │          │
    ├──────────────────────────────────┤          │
    │ id (PK)                          │          │
    │ environment_id (FK) ─────────────┤──────────┘
    │ test_run_id (FK) ────────────────┼──────────┐
    │ status                           │          │
    │ container_id                     │          │
    │ tests_executed, passed, failed   │          │
    │ test_coverage_percent            │          │
    │ git_commit_sha, github_pr_number │          │
    │ github_check_run_id              │          │
    │ started_at, completed_at         │          │
    └────┬──────────────────────────────┘          │
         │ 1                                       │
         │                                         │
         │ N                                       │
    ┌────▼──────────────────────────────┐          │
    │ ExecutionArtifact                │          │
    ├──────────────────────────────────┤          │
    │ id (PK)                          │          │
    │ execution_session_id (FK) ───────┤──┐       │
    │ test_result_id (FK) ─────────────┼──┼───┐   │
    │ artifact_type                    │  │   │   │
    │ storage_path (S3)                │  │   │   │
    │ captured_at                      │  │   │   │
    │ share_token                      │  │   │   │
    │ width, height, duration          │  │   │   │
    └────────────────────────────────────┘   │   │
                                             │   │
                          ┌──────────────────┘   │
                          │                      │
                  ┌───────▼──────────────┐       │
                  │ TestResult           │       │
                  │ (existing, enhanced) │       │
                  ├──────────────────────┤       │
                  │ id (PK)              │       │
                  │ run_id (FK) ──────────┐      │
                  │ test_case_id (FK)    │ │    │
                  │ status               │ │    │
                  │ failure_reason       │ │    │
                  │ error_message        │ │    │
                  │ actual_result        │ │    │
                  │ github_check_run_id  │ │    │
                  │ execution_session_id ├─┼────┘
                  │ created_at           │ │
                  └──────────────────────┘ │
                                           │
                        ┌──────────────────┘
                        │
                  ┌─────▼──────────────┐
                  │ TestRun            │
                  │ (existing)         │
                  ├────────────────────┤
                  │ id (PK)            │
                  │ run_number         │
                  │ suite_id           │
                  │ name, description  │
                  │ status, run_type   │
                  │ build_number       │
                  │ commit_sha         │
                  │ environment        │
                  │ created_at         │
                  └─────────────────────┘

┌────────────────────────────┐
│ GraphNode (existing)       │
├────────────────────────────┤
│ graph_id (PK)              │
│ item_id (PK)               │
│ project_id                 │
│ is_primary                 │
└────┬───────────────────────┘
     │ 1:1
     │
     │
┌────▼──────────────────────────────┐
│ TestNodeMetadata (NEW)            │
├───────────────────────────────────┤
│ id (PK)                           │
│ graph_id, item_id (FK to above)   │
│ last_test_result                  │
│ execution_count, pass_count       │
│ pass_rate, test_coverage_percent  │
│ primary_artifact_id (FK) ─┐       │
│ artifact_ids[]            │       │
│ test_status               │       │
│ is_flaky, flaky_indicator │       │
│ node_display_config       │       │
└──────────────────────────────┬────┘
                              │
                    ┌─────────▼─────────┐
                    │ ExecutionArtifact │
                    │ (referenced above)│
                    └───────────────────┘
```

---

## 4. GitHub Integration Sequence

```
GitHub                           TraceRTM API              Services                Database
  │                                   │                        │                      │
  │─ Push/PR Webhook Event ──────────►│                        │                      │
  │   (with X-Hub-Signature)          │                        │                      │
  │                                   │                        │                      │
  │                                   ├─ Verify Signature ────┐│                      │
  │                                   │                      │ │                      │
  │                                   │◄─ Signature OK ───────┘│                      │
  │                                   │                        │                      │
  │                                   ├─ Extract Repo, Branch ►│                      │
  │                                   │   Commit, PR# (if PR) │                      │
  │                                   │                        │                      │
  │                                   ├─ Find Integration ────►│                      │
  │                                   │   Mapping              │                      │
  │                                   │                        ├─ Query DB ──────────►│
  │                                   │                        │                      │
  │                                   │◄───── Mapping ─────────┤                      │
  │                                   │                        │◄─ Mapping ───────────┤
  │                                   │                        │                      │
  │                                   ├─ Create ExecutionSession ─────┐              │
  │                                   │                        │      │              │
  │                                   ├────────────────────────────────────► Insert ─►│
  │                                   │                        │      │              │
  │                                   │                        │      └─ Get ID ────┐│
  │                                   │                        │                    ││
  │                                   │      ┌─ Async Task ───┐│                    ││
  │                                   │      │                │ │                    ││
  │                                   │◄─ Session ID ────────┘│                     ││
  │                          ┌────────┤ (Return immediately)   │                     ││
  │                          │        │                        │                     ││
  │ ◄─ 200 OK with ─────────┘        │                        │                     ││
  │   session_id                      │                        │                     ││
  │                                   │                        │                     ││
  │                                   │                  Background Execution Task:  ││
  │                                   │                        │                     ││
  │                                   ├─ Create Check Run ────►│                     ││
  │                                   │   (status: in_progress)│                     ││
  │  ◄────── POST /repos/.../checks ◄┤                        │                     ││
  │         (Create)                  │                        │                     ││
  │                                   │                        │                     ││
  │  Check Run ID ────────────────────┼───────────────────────►│                     ││
  │                                   │                        │                     ││
  │                                   │   [Tests Running...]   │ Update Session ────┐│├──► Update
  │                                   │                        │                    │││
  │                                   │                        │ (stream logs)      │││
  │                                   │                        │                    │││
  │                                   ├─ Tests Complete ──────►│                    │││
  │                                   │                        │                    │││
  │                                   ├─ Update Check Run ────►│                    │││
  │                                   │   (status: completed)  │                    │││
  │  ◄────── PATCH /repos/.../checks ◄┤   (conclusion: pass/fail)                    │││
  │                                   │                        │                    │││
  │                                   ├─ Post PR Comment ─────►│                    │││
  │  ◄─────── POST /repos/.../issues/│                        │                    │││
  │           comments ◄──────────────┤   (with test results)  │                    │││
  │                                   │                        │                    │││
  │                                   │                        ├─ Update Metadata ──┼┼┼──► Update
  │                                   │                        │   (pass_rate, etc) │││
  │                                   │                        │                    │││
  │                                   │                        └─ Insert Artifacts ─┘│├──► Insert
  │                                   │                                             ││
  │                                   │                                             ││
  │ [GitHub checks & comments visible on PR]                                        ││
  │                                   │                                             ││
```

---

## 5. Frontend Component Tree

```
App
├── Layout
│   ├── Header
│   ├── Sidebar
│   └── Main Content
│       │
│       └── ProjectView
│           └── GraphViews (Tab)
│               │
│               ├── FlowGraphViewEnhanced (NEW ENHANCED)
│               │   │
│               │   ├── PerspectiveSelector
│               │   ├── LayoutControls
│               │   │
│               │   ├── ReactFlow Container
│               │   │   │
│               │   │   └── Canvas
│               │   │       │
│               │   │       ├── Node: RichNodePill (ENHANCED)
│               │   │       │   │
│               │   │       │   ├── NodeHeader
│               │   │       │   │   ├── Title (left)
│               │   │       │   │   └── MetricBadges (right)
│               │   │       │   │       ├── Coverage%
│               │   │       │   │       └── TestStatus
│               │   │       │   │
│               │   │       │   ├── NodeImage (NEW)
│               │   │       │   │   ├── RoundedPill (image)
│               │   │       │   │   └── PlayIcon (if video)
│               │   │       │   │
│               │   │       │   └── NodeFooter (NEW)
│               │   │       │       ├── PassRateBar
│               │   │       │       └── LastExecution
│               │   │       │
│               │   │       ├── Edge: Link Line
│               │   │       │   └── LinkLabel (if shown)
│               │   │       │
│               │   │       └── Background & Controls
│               │   │           ├── Grid Background
│               │   │           ├── Zoom Controls
│               │   │           └── MiniMap
│               │   │
│               │   ├── NodeDetailPanel (existing, enhanced)
│               │   │   └── Item details + test metrics
│               │   │
│               │   └── NodeExpandPopup (NEW MODAL)
│               │       │
│               │       ├── Header
│               │       │   ├── Title
│               │       │   └── Close Button
│               │       │
│               │       ├── Main Layout (flex row)
│               │       │   │
│               │       │   ├── Sidebar (flex column)
│               │       │   │   │
│               │       │   │   ├── PillTab (Screenshots)
│               │       │   │   │   ├── Icon
│               │       │   │   │   ├── Badge (count)
│               │       │   │   │   └── Tooltip
│               │       │   │   │
│               │       │   │   ├── PillTab (Videos)
│               │       │   │   ├── PillTab (Logs)
│               │       │   │   └── PillTab (Metrics)
│               │       │   │
│               │       │   └── Content Area (flex column)
│               │       │       │
│               │       │       ├── When: Screenshots selected
│               │       │       │   └── ScreenshotGallery
│               │       │       │       ├── MainViewer
│               │       │       │       │   ├── Image Display
│               │       │       │       │   ├── Zoom Control
│               │       │       │       │   └── Download Button
│               │       │       │       │
│               │       │       │       ├── ThumbnailStrip
│               │       │       │       │   └── Thumbnail Images
│               │       │       │       │
│               │       │       │       └── Navigation
│               │       │       │           ├── Previous
│               │       │       │           ├── Counter
│               │       │       │           └── Next
│               │       │       │
│               │       │       ├── When: Videos selected
│               │       │       │   └── VideoPlayer
│               │       │       │       ├── VideoElement
│               │       │       │       ├── Controls
│               │       │       │       └── Timeline
│               │       │       │
│               │       │       ├── When: Logs selected
│               │       │       │   └── LogsViewer
│               │       │       │       ├── SyntaxHighlight
│               │       │       │       ├── Virtualization
│               │       │       │       ├── SearchBox
│               │       │       │       └── Download Button
│               │       │       │
│               │       │       └── When: Metrics selected
│               │       │           └── MetricsPanel
│               │       │               ├── PassRateCard
│               │       │               ├── CoverageCard
│               │       │               ├── FlakinessCard
│               │       │               ├── ExecutionChart
│               │       │               └── EnvironmentInfo
│               │       │
│               │       └── Footer
│               │           ├── RunTestsButton
│               │           ├── ViewReportButton
│               │           ├── DownloadButton
│               │           └── ShareButton
│               │
│               └── ExecutionControlPanel (NEW)
│                   ├── ExecuteButton
│                   ├── CancelButton
│                   ├── ProgressBar
│                   ├── StatusBadge
│                   └── LogsPreview
```

---

## 6. State Management Flow (Frontend)

```
Redux/Zustand Store
│
├── Execution State
│   ├── activeSessions: Map<sessionId, ExecutionSession>
│   │   ├── status: 'pending'|'running'|'completed'|'failed'
│   │   ├── progress: 0-100
│   │   ├── logsStream: string[]
│   │   ├── results: {passed, failed, total}
│   │   └── artifacts: ExecutionArtifact[]
│   │
│   ├── selectedSession: ExecutionSession | null
│   └── executionHistory: ExecutionSession[]
│
├── Artifact State
│   ├── artifacts: Map<artifactId, ExecutionArtifact>
│   ├── artifactCache: Map<artifactId, ImageBitmap>
│   ├── selectedArtifact: ExecutionArtifact | null
│   └── artifactLoading: Map<artifactId, boolean>
│
├── Graph Node State
│   ├── nodeMetadata: Map<nodeId, TestNodeMetadata>
│   ├── expandedNodes: Set<nodeId>
│   ├── selectedNode: string | null
│   └── nodeMetadataRefreshInterval: number
│
├── UI State
│   ├── expandPopupOpen: boolean
│   ├── selectedTab: 'screenshots'|'videos'|'logs'|'metrics'
│   ├── zoomLevel: number
│   └── showDetailPanel: boolean
│
└── Settings
    ├── autoRefreshMetrics: boolean
    ├── metricsRefreshInterval: number
    └── defaultArtifactStorage: 's3'|'local'
```

---

## 7. Docker Container Execution Lifecycle

```
┌──────────────────────────────────────────────────────────┐
│  Execution Session Lifecycle                             │
└──────────────────────────────────────────────────────────┘

[Phase 1: Provisioning]
┌─────────────────────────────────┐
│ docker pull node:20-alpine      │
│ docker create --name=tr-abc...  │
│   --cpus=2 --memory=2048m       │
│   --volume=/tmp/repo:/workspace │
│   --volume=/tmp/out:/results    │
│   node:20-alpine bash           │
└──────────────┬──────────────────┘
               │
               ▼
        Container created
        (not yet running)
               │
               ▼
┌─────────────────────────────────┐
│ docker exec tr-abc... git clone │
│   https://github.com/.../repo   │
│   /workspace                    │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ docker exec tr-abc... npm install│
│   (from /workspace)             │
└──────────────┬──────────────────┘
               │
               ▼
        Environment ready
        (Dependencies installed)


[Phase 2: Execution]
┌─────────────────────────────────────────┐
│ docker exec tr-abc... npm test --json   │
│   --outputFile=/results/results.json    │
│   --coverage --coverageReporters=json   │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Parallel Artifact Capture:          │ │
│ │ - Screenshot via Playwright API     │ │
│ │ - Console log capture               │ │
│ │ - Coverage report extraction        │ │
│ │ - Video frame recording (if enabled)│ │
│ └─────────────────────────────────────┘ │
└──────────────┬────────────────────────────┘
               │
               ▼
        Tests completed
        Results written to disk


[Phase 3: Collection]
┌──────────────────────────────────────┐
│ docker cp tr-abc...:/results/.  /tmp/│
│   - Test results JSON                │
│   - Coverage reports                 │
│   - Artifact files                   │
│   - Console logs                     │
└──────────────┬───────────────────────┘
               │
               ▼
        Files copied to host


[Phase 4: Processing]
┌──────────────────────────────────────┐
│ ArtifactProcessor                    │
│ - Compress images to WebP            │
│ - Generate thumbnails                │
│ - Extract image metadata (OCR, dims) │
│ - Upload to S3                       │
│ - Store metadata in DB               │
└──────────────┬───────────────────────┘
               │
               ▼
        Artifacts stored & indexed


[Phase 5: Cleanup]
┌──────────────────────────────────────┐
│ docker stop tr-abc...                │
│ docker rm tr-abc...                  │
│ rm -rf /tmp/repo                     │
│ rm -rf /tmp/out                      │
└──────────────┬───────────────────────┘
               │
               ▼
        Container destroyed
        Host resources freed


Resource Limits & Isolation:
┌───────────────────────────────────────┐
│ --cpus=2.0                            │
│ --memory=2048m                        │
│ --memory-swap=2048m (no swap)         │
│ --pids-limit=100                      │
│ --read-only (optional)                │
│ --tmpfs /tmp:size=1024m               │
│ --network=bridge (limited)            │
│ --cap-drop ALL (security)             │
│ --security-opt no-new-privileges      │
│ --user=1000:1000 (non-root)           │
└───────────────────────────────────────┘

Timeout: 60 minutes (hard limit)
Logging: All stdout/stderr captured
Success: Exit code 0 = passed
```

---

## 8. Database Indexing Strategy

```
ExecutionEnvironment Indexes:
  - (project_id, status)          // Find active envs for project
  - (runtime)                      // Find all Python envs, etc
  - (created_at DESC)              // Recent environments
  - UNIQUE (project_id, name)      // Name uniqueness per project

ExecutionSession Indexes:
  - (environment_id, status)       // Running sessions for env
  - (test_run_id)                  // Find session for test run
  - (status, created_at DESC)      // Recent sessions
  - (git_commit_sha)               // Find execution by commit
  - (github_pr_number)             // Find execution by PR

ExecutionArtifact Indexes:
  - (execution_session_id, artifact_type)  // Get screenshots/videos
  - (test_result_id)               // Find artifacts for result
  - (created_at DESC)              // Recent artifacts
  - (storage_backend, storage_path)// Orphan cleanup queries
  - (share_token)                  // Shared artifact lookup

TestNodeMetadata Indexes:
  - UNIQUE (graph_id, item_id)     // 1:1 relationship
  - (test_coverage_percent DESC)   // Coverage sorting
  - (test_status)                  // Filter by status
  - (is_flaky)                     // Find flaky tests
  - (last_execution_at DESC)       // Recent activity
```

---

This comprehensive visual architecture guide provides developers with clear understanding of:
- Component relationships and dependencies
- Data flow between systems
- Execution lifecycle and phases
- Frontend component structure
- GitHub integration sequence
- Container execution with resource limits
- Database optimization strategies


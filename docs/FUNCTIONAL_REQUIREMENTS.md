# TraceRTM — Functional Requirements Specification

**Version:** 1.0
**Date:** 2026-02-12
**Status:** Active

---

## Document Overview

This document specifies the functional requirements for TraceRTM, a comprehensive requirements traceability management system. Requirements are organized into 9 categories covering discovery, analysis, tracking, verification, reporting, collaboration, AI automation, infrastructure, and MCP integration.

### Requirement Categories

- **FR-DISC**: Discovery & Capture (imports, parsing, linking)
- **FR-QUAL**: Qualification & Analysis (quality, graph, impact)
- **FR-APP**: Application & Tracking (CRUD, workflows, status)
- **FR-VERIF**: Verification & Validation (testing, coverage, BDD)
- **FR-RPT**: Reporting & Analytics (matrices, dashboards, export)
- **FR-COLLAB**: Collaboration & Integration (real-time, sync, webhooks)
- **FR-AI**: AI & Automation (agents, MCP, code analysis)
- **FR-INFRA**: Infrastructure (database, auth, deployment, monitoring)
- **FR-MCP**: MCP Server (tools, resources, prompts)

### Key Statistics

- **Total Requirements:** 142
- **API Endpoints:** 201 (Python) + 65+ (Go REST) + 3 (gRPC) = 269+
- **Core Models:** 50+
- **Services:** 90+ (Python) + 25+ (Go) = 115+
- **MCP Tools:** 50+
- **Go Backend Coverage:** 45+ unique endpoints across 25+ handler files

---

## Table of Contents

1. [FR-DISC: Discovery & Capture](#fr-disc-discovery--capture)
2. [FR-QUAL: Qualification & Analysis](#fr-qual-qualification--analysis)
3. [FR-APP: Application & Tracking](#fr-app-application--tracking)
4. [FR-VERIF: Verification & Validation](#fr-verif-verification--validation)
5. [FR-RPT: Reporting & Analytics](#fr-rpt-reporting--analytics)
6. [FR-COLLAB: Collaboration & Integration](#fr-collab-collaboration--integration)
7. [FR-AI: AI & Automation](#fr-ai-ai--automation)
8. [FR-INFRA: Infrastructure](#fr-infra-infrastructure)
9. [FR-MCP: MCP Server](#fr-mcp-mcp-server)

---

## FR-DISC: Discovery & Capture

### FR-DISC-001: GitHub Issue Import

**Traces to:** External integration epics
**Description:** The system SHALL import issues from GitHub repositories via the GitHub API, converting them to traceability items with preserved metadata including labels, assignees, milestones, and timestamps.

**Input:**
- GitHub repository identifier (owner/repo)
- Optional filters (labels, state, milestone)
- Authentication token (GitHub App or PAT)

**Output:**
- Created item records with GitHub metadata
- Preserved relationships (parent/child issues)
- Import status report

**Implemented in:**
- `src/tracertm/services/github_import_service.py`
- `src/tracertm/api/routers/github.py:import_issues()`
- `POST /api/v1/github/import`

**Tested in:**
- `src/tracertm/tests/services/test_github_import_service.py`
- `tests/integration/test_github_import.py`

**Constraints:**
- SHALL preserve GitHub issue numbers as external IDs
- SHALL handle rate limiting with exponential backoff
- SHALL support incremental updates (only new/changed issues)
- SHALL map GitHub labels to TraceRTM tags

---

### FR-DISC-002: Jira Import

**Traces to:** External integration epics
**Description:** The system SHALL import issues from Jira projects via the Jira REST API, converting them to traceability items with preserved issue types, priorities, statuses, and custom fields.

**Input:**
- Jira project key or JQL query
- Jira instance URL and credentials
- Field mapping configuration

**Output:**
- Created item records with Jira metadata
- Preserved issue links (blocks, relates to, etc.)
- Field mapping report

**Implemented in:**
- `src/tracertm/services/jira_import_service.py`
- `POST /api/v1/integrations/jira/import`

**Tested in:**
- `src/tracertm/tests/services/test_jira_import_service.py`

**Constraints:**
- SHALL support custom field mapping
- SHALL preserve Jira issue keys
- SHALL handle pagination for large projects (>1000 issues)
- SHALL validate field types before import

---

### FR-DISC-003: Specification Parsing

**Traces to:** Document ingestion epics
**Description:** The system SHALL parse structured requirements from documents in multiple formats (Markdown, Word, PDF, HTML) using configurable patterns to extract requirement IDs, text, attributes, and hierarchies.

**Input:**
- Document file or URL
- Parser configuration (format, patterns)
- Project context

**Output:**
- Extracted requirements as items
- Detected hierarchy relationships
- Parsing report with warnings

**Implemented in:**
- `src/tracertm/services/specification_service.py:parse_document()`
- `POST /api/v1/specifications/parse`

**Tested in:**
- `src/tracertm/tests/services/test_specification_service.py`

**Constraints:**
- SHALL support regex patterns for requirement ID extraction
- SHALL detect SHALL/MUST/SHOULD keywords
- SHALL preserve requirement numbering schemes
- SHALL handle nested hierarchies (up to 10 levels)

---

### FR-DISC-004: Auto-Link Suggestion

**Traces to:** AI-assisted linking epics
**Description:** The system SHALL automatically suggest links between items based on semantic similarity, keyword matching, and structural patterns, using embeddings and NLP techniques.

**Input:**
- Source item ID
- Optional filter criteria (types, projects)
- Confidence threshold (default 0.7)

**Output:**
- Ranked list of suggested target items
- Confidence scores per suggestion
- Rationale for each suggestion

**Implemented in:**
- `src/tracertm/services/auto_link_service.py`
- `POST /api/v1/links/auto-suggest`
- `src/tracertm/mcp/tools/traceability.py:suggest_links()`

**Tested in:**
- `src/tracertm/tests/services/test_auto_link_service.py`

**Constraints:**
- SHALL compute embeddings for new items asynchronously
- SHALL exclude already-linked items from suggestions
- SHALL limit suggestions to top 20 candidates
- SHALL provide explainable rationale (matching keywords, similarity score)

---

### FR-DISC-005: Commit Linking

**Traces to:** Git integration epics
**Description:** The system SHALL automatically link Git commits to items by parsing commit messages for item references (e.g., "Fixes #123", "Implements REQ-456"), and SHALL support manual commit association.

**Input:**
- Git repository configuration
- Commit reference patterns (regex)
- Item ID patterns

**Output:**
- Created links from commits to items
- Commit metadata (SHA, author, timestamp, message)
- Linking report

**Implemented in:**
- `src/tracertm/services/commit_linking_service.py`
- `POST /api/v1/github/link-commits`

**Tested in:**
- `src/tracertm/tests/services/test_commit_linking_service.py`

**Constraints:**
- SHALL support multiple reference formats (GitHub, GitLab, Bitbucket)
- SHALL handle bulk commit linking (e.g., entire branch)
- SHALL preserve commit author and timestamp
- SHALL support retroactive linking (existing commits)

---

### FR-DISC-006: Webhook Ingestion

**Traces to:** Real-time integration epics
**Description:** The system SHALL receive webhook events from external systems (GitHub, Jira, Linear, custom) and SHALL process them to create, update, or delete items based on configurable rules.

**Input:**
- Webhook payload (JSON)
- Webhook signature for verification
- Integration configuration

**Output:**
- Created/updated/deleted items
- Webhook processing status
- Error details if processing fails

**Implemented in:**
- `src/tracertm/services/webhook_service.py`
- `POST /api/v1/webhooks/{integration_type}`
- `backend/internal/handlers/webhook_handler.go:HandleWebhook()` - POST /api/v1/webhooks/:integration_type
- `backend/internal/handlers/webhook_handler.go:RegisterWebhook()` - POST /api/v1/webhooks/register
- `backend/internal/handlers/webhook_handler.go:ListWebhooks()` - GET /api/v1/webhooks
- `backend/internal/services/webhook_service.go`

**Tested in:**
- `src/tracertm/tests/services/test_webhook_service.py`
- `backend/internal/handlers/webhook_handler_test.go`

**Constraints:**
- SHALL verify webhook signatures for security
- SHALL handle duplicate events idempotently
- SHALL process webhooks asynchronously (queue-based)
- SHALL retry failed webhook processing (3 attempts with backoff)

---

### FR-DISC-007: Bulk Item Import

**Traces to:** Data migration epics
**Description:** The system SHALL import items in bulk from CSV, JSON, or Excel files with support for batch validation, error recovery, and progress tracking.

**Input:**
- Import file (CSV/JSON/XLSX)
- Field mapping configuration
- Validation rules

**Output:**
- Created items
- Import summary (success/failure counts)
- Detailed error report

**Implemented in:**
- `src/tracertm/services/import_service.py`
- `POST /api/v1/import/bulk`
- `src/tracertm/services/bulk_service.py`

**Tested in:**
- `src/tracertm/tests/services/test_import_service.py`

**Constraints:**
- SHALL validate all rows before importing (fail-fast)
- SHALL support incremental import (skip existing items)
- SHALL handle up to 10,000 items per import
- SHALL provide downloadable error report (CSV)

---

### FR-DISC-008: Live Document Sync

**Traces to:** Real-time collaboration epics
**Description:** The system SHALL synchronize items with external documents (Google Docs, Confluence, Notion) in near real-time using webhooks or polling, detecting changes and updating items accordingly.

**Input:**
- Document URL and credentials
- Sync configuration (polling interval, change detection)
- Field mapping

**Output:**
- Updated items reflecting document changes
- Sync status report
- Conflict resolution log

**Implemented in:**
- `src/tracertm/services/external_integration_service.py`
- `src/tracertm/services/sync_service.py`
- `POST /api/v1/integrations/{type}/sync`

**Tested in:**
- `src/tracertm/tests/services/test_sync_service.py`

**Constraints:**
- SHALL detect changes using document version IDs or checksums
- SHALL handle conflicts (prefer document changes by default)
- SHALL throttle API calls to external services (respect rate limits)
- SHALL support manual conflict resolution via UI

---

### FR-DISC-009: File Attachment Management

**Traces to:** Document management epics
**Description:** The system SHALL allow users to attach files to items, storing them in S3-compatible storage with support for versioning, preview generation, and secure access control.

**Input:**
- Item ID
- File upload (multipart form data)
- Optional metadata (description, tags)

**Output:**
- Attachment record with storage URL
- Preview image/thumbnail (for supported formats)
- Access token for secure download

**Implemented in:**
- `src/tracertm/services/storage_service.py`
- `POST /api/v1/items/{id}/attachments`
- `GET /api/v1/items/{id}/attachments/{attachment_id}`
- `backend/internal/handlers/storage_handler.go:Upload()` - POST /api/v1/storage/upload
- `backend/internal/handlers/storage_handler.go:Download()` - GET /api/v1/storage/download/:key
- `backend/internal/handlers/storage_handler.go:Delete()` - DELETE /api/v1/storage/:key
- `backend/internal/handlers/storage_handler.go:GetPresignedURL()` - POST /api/v1/storage/presigned-url
- `backend/internal/storage/s3.go`

**Tested in:**
- `src/tracertm/tests/services/test_storage_service.py`
- `backend/internal/handlers/storage_handler_test.go`

**Constraints:**
- SHALL support files up to 100 MB
- SHALL generate thumbnails for images and PDFs
- SHALL scan files for malware before storing
- SHALL enforce access control (only users with item access can download)

---

### FR-DISC-010: Specification Repository Manifest

**Traces to:** Document organization epics
**Description:** The system SHALL maintain a manifest of specification repositories (local directories, Git repos, cloud storage) and SHALL index their contents for search and linking.

**Input:**
- Repository URL or path
- Repository type (git, local, s3)
- Indexing configuration

**Output:**
- Repository record with metadata
- Indexed documents
- Repository health status

**Implemented in:**
- `src/tracertm/services/specification_service.py:register_repository()`
- `POST /api/v1/specifications/repositories`

**Tested in:**
- `src/tracertm/tests/services/test_specification_service.py`

**Constraints:**
- SHALL support Git repositories (clone and index)
- SHALL support local file system directories
- SHALL support S3-compatible buckets
- SHALL re-index on detected changes (webhook or polling)

---

## FR-QUAL: Qualification & Analysis

### FR-QUAL-001: Requirement Quality Scoring

**Traces to:** Quality assurance epics
**Description:** The system SHALL analyze requirement text using NLP to compute quality scores across multiple dimensions: clarity, completeness, consistency, testability, and traceability.

**Input:**
- Item ID or text
- Scoring configuration (weights, thresholds)

**Output:**
- Overall quality score (0-100)
- Dimension scores
- Specific quality issues with recommendations

**Implemented in:**
- `src/tracertm/services/requirement_quality_service.py`
- `GET /api/v1/items/{id}/quality`
- `POST /api/v1/quality/analyze`

**Tested in:**
- `src/tracertm/tests/services/test_requirement_quality_service.py`

**Constraints:**
- SHALL detect ambiguous terms (e.g., "fast", "easy", "user-friendly")
- SHALL detect missing acceptance criteria
- SHALL detect passive voice and weak verbs
- SHALL suggest improvements for low-scoring dimensions

---

### FR-QUAL-002: Graph Cycle Detection

**Traces to:** Graph validation epics
**Description:** The system SHALL detect circular dependencies in the traceability graph and SHALL report all cycles with detailed paths.

**Input:**
- Project ID or graph scope
- Link types to consider (optional, default: all)

**Output:**
- List of detected cycles
- Path for each cycle (item IDs)
- Cycle severity score

**Implemented in:**
- `src/tracertm/services/cycle_detection_service.py`
- `GET /api/v1/graph/cycles`
- `backend/internal/graph/cycle_detector.go`
- `backend/internal/handlers/graph_handler.go:GetCycles()` - GET /api/v1/graph/cycles
- `backend/internal/handlers/graph_analysis_handler.go:DetectCycles()` - GET /api/v1/graph/analysis/cycles
- `backend/internal/grpc/server.go:FindCycles()` - gRPC GraphService.FindCycles

**Tested in:**
- `src/tracertm/tests/services/test_cycle_detection_service.py`
- `backend/internal/handlers/graph_handler_test.go`

**Constraints:**
- SHALL use Tarjan's algorithm for cycle detection
- SHALL detect cycles across all link types
- SHALL limit cycle path length to 100 items (prevent runaway)
- SHALL cache results (invalidate on graph changes)

---

### FR-QUAL-003: Critical Path Analysis

**Traces to:** Project planning epics
**Description:** The system SHALL identify the critical path through a project's traceability graph, computing the longest dependency chain from start to end items.

**Input:**
- Project ID
- Start item IDs (optional, default: items with no predecessors)
- End item IDs (optional, default: items with no successors)

**Output:**
- Critical path (ordered list of items)
- Path length (number of items)
- Total estimated effort (if effort fields populated)

**Implemented in:**
- `src/tracertm/services/critical_path_service.py`
- `GET /api/v1/graph/critical-path`

**Tested in:**
- `src/tracertm/tests/services/test_critical_path_service.py`

**Constraints:**
- SHALL use longest path algorithm (reverse of shortest path)
- SHALL handle multiple start/end items (compute all paths)
- SHALL respect link types (only follow "depends_on" links)
- SHALL exclude cycles from path computation

---

### FR-QUAL-004: Impact Analysis

**Traces to:** Change management epics
**Description:** The system SHALL analyze the downstream impact of changing an item, computing affected items across all transitive dependencies.

**Input:**
- Item ID (proposed change)
- Analysis depth (default: unlimited)
- Link types to traverse

**Output:**
- Affected items (direct and transitive)
- Impact scope (count, types, priorities)
- Risk assessment

**Implemented in:**
- `src/tracertm/services/impact_analysis_service.py`
- `POST /api/v1/analysis/impact`
- `backend/internal/handlers/graph_handler.go:GetImpact()` - GET /api/v1/graph/impact/:id
- `backend/internal/handlers/traceability_handler.go:GetImpactAnalysis()` - GET /api/v1/traceability/impact/:item_id
- `backend/internal/grpc/server.go:AnalyzeImpact()` - gRPC GraphService.AnalyzeImpact
- `backend/internal/graph/analysis_service.go`

**Tested in:**
- `src/tracertm/tests/services/test_impact_analysis_service.py`
- `backend/internal/handlers/graph_handler_test.go`
- `backend/internal/grpc/server_test.go`

**Constraints:**
- SHALL traverse graph breadth-first
- SHALL compute impact score based on item priorities
- SHALL detect high-risk changes (affecting >50 items or critical items)
- SHALL cache results for performance

---

### FR-QUAL-005: Coverage Analysis

**Traces to:** Testing epics
**Description:** The system SHALL compute test coverage by analyzing links between requirements and test cases, identifying uncovered requirements and orphaned tests.

**Input:**
- Project ID
- Coverage type (requirements, features, code)

**Output:**
- Coverage percentage
- Uncovered items (requirements without tests)
- Orphaned tests (tests without requirements)
- Coverage matrix

**Implemented in:**
- `src/tracertm/services/advanced_analytics_service.py:compute_coverage()`
- `GET /api/v1/coverage/matrix`
- `backend/internal/handlers/traceability_handler.go:GetCoverage()` - GET /api/v1/traceability/coverage/:project_id
- `backend/internal/traceability/matrix_service.go:GetCoverageReport()`

**Tested in:**
- `src/tracertm/tests/services/test_advanced_analytics_service.py`
- `backend/internal/handlers/traceability_handler_test.go`

**Constraints:**
- SHALL support multiple coverage types (req→test, req→code, feature→test)
- SHALL compute coverage at multiple levels (project, epic, feature)
- SHALL exclude skipped/disabled tests from coverage
- SHALL support coverage thresholds with alerts

---

### FR-QUAL-006: Dependency Analysis

**Traces to:** Architecture analysis epics
**Description:** The system SHALL analyze dependencies between items to identify coupling, fan-in/fan-out metrics, and potential architectural issues.

**Input:**
- Project ID or item ID
- Analysis type (dependencies, dependents, both)

**Output:**
- Dependency graph
- Metrics (fan-in, fan-out, depth)
- Architectural issues (high coupling, circular deps)

**Implemented in:**
- `src/tracertm/services/dependency_analysis_service.py`
- `GET /api/v1/analysis/dependencies`
- `backend/internal/handlers/graph_handler.go:GetDependencies()` - GET /api/v1/graph/dependencies/:id
- `backend/internal/handlers/graph_handler.go:GetAncestors()` - GET /api/v1/graph/ancestors/:id
- `backend/internal/handlers/graph_handler.go:GetDescendants()` - GET /api/v1/graph/descendants/:id
- `backend/internal/graph/graph.go`

**Tested in:**
- `src/tracertm/tests/services/test_dependency_analysis_service.py`
- `backend/internal/handlers/graph_handler_test.go`

**Constraints:**
- SHALL compute metrics at item and project levels
- SHALL detect high coupling (fan-out > 10)
- SHALL detect low cohesion (fan-in < 2 for non-leaf items)
- SHALL visualize dependency graph (D3.js or Cytoscape)

---

### FR-QUAL-007: Traceability Matrix Generation

**Traces to:** Reporting epics
**Description:** The system SHALL generate traceability matrices in multiple formats showing relationships between item types (e.g., requirements to tests, features to requirements).

**Input:**
- Source item type (e.g., "requirement")
- Target item type (e.g., "test")
- Project scope

**Output:**
- Matrix (rows=source items, columns=target items)
- Cell values (link types, counts, status)
- Exportable formats (CSV, Excel, PDF)

**Implemented in:**
- `src/tracertm/services/traceability_matrix_service.py`
- `GET /api/v1/reports/traceability-matrix`
- `backend/internal/handlers/traceability_handler.go:GenerateMatrix()` - GET /api/v1/traceability/matrix/:project_id
- `backend/internal/traceability/matrix_service.go`

**Tested in:**
- `src/tracertm/tests/services/test_traceability_matrix_service.py`
- `backend/internal/handlers/traceability_handler_test.go`

**Constraints:**
- SHALL support sparse matrices (only show linked items)
- SHALL support pivot (swap rows/columns)
- SHALL export to CSV, Excel, PDF
- SHALL handle large matrices (>1000 items per axis)

---

### FR-QUAL-008: Shortest Path Computation

**Traces to:** Graph query epics
**Description:** The system SHALL compute the shortest path between two items in the traceability graph using Dijkstra's algorithm or BFS.

**Input:**
- Source item ID
- Target item ID
- Link types to traverse (optional)

**Output:**
- Shortest path (ordered list of items)
- Path length
- Link types along path

**Implemented in:**
- `src/tracertm/services/shortest_path_service.py`
- `GET /api/v1/graph/shortest-path`
- `backend/internal/handlers/graph_handler.go:FindPath()` - GET /api/v1/graph/path
- `backend/internal/handlers/graph_analysis_handler.go:GetShortestPath()` - GET /api/v1/graph/analysis/shortest-path
- `backend/internal/grpc/server.go:CalculatePath()` - gRPC GraphService.CalculatePath
- `backend/internal/graph/analysis_service.go:ShortestPath()`

**Tested in:**
- `src/tracertm/tests/services/test_shortest_path_service.py`
- `backend/internal/handlers/graph_handler_test.go`

**Constraints:**
- SHALL use BFS for unweighted graphs
- SHALL use Dijkstra for weighted graphs (link weights)
- SHALL return "no path" if items disconnected
- SHALL cache results for frequently queried paths

---

### FR-QUAL-009: Graph Validation

**Traces to:** Data integrity epics
**Description:** The system SHALL validate graph consistency by detecting orphaned items, broken links, invalid link types, and schema violations.

**Input:**
- Project ID
- Validation rules configuration

**Output:**
- Validation report
- List of issues (orphans, broken links, schema violations)
- Suggested fixes

**Implemented in:**
- `src/tracertm/services/graph_validation_service.py`
- `POST /api/v1/graph/validate`
- `backend/internal/handlers/traceability_handler.go:ValidateTraceability()` - GET /api/v1/traceability/validate/:project_id
- `backend/internal/handlers/graph_handler.go:GetOrphans()` - GET /api/v1/graph/orphans

**Tested in:**
- `src/tracertm/tests/services/test_graph_validation_service.py`
- `backend/internal/handlers/traceability_handler_test.go`

**Constraints:**
- SHALL detect orphaned items (no incoming or outgoing links)
- SHALL detect broken links (target item deleted)
- SHALL validate link types against schema
- SHALL suggest fixes (delete orphans, repair links)

---

### FR-QUAL-010: Specification Analytics

**Traces to:** Analytics epics
**Description:** The system SHALL analyze specification documents to extract metrics: requirement counts, SHALL/MUST/SHOULD distribution, completeness scores, and compliance levels.

**Input:**
- Specification ID
- Analysis configuration

**Output:**
- Metrics dashboard
- Distribution charts
- Compliance report

**Implemented in:**
- `src/tracertm/services/spec_analytics_service.py`
- `GET /api/v1/specifications/{id}/analytics`
- `backend/internal/handlers/spec_analytics_handler.go:AnalyzeSpec()` - POST /api/v1/spec-analytics/analyze
- `backend/internal/handlers/spec_analytics_handler.go:BatchAnalyze()` - POST /api/v1/spec-analytics/batch-analyze
- `backend/internal/handlers/spec_analytics_handler.go:ValidateISO29148()` - POST /api/v1/spec-analytics/validate-iso29148
- `backend/internal/handlers/spec_analytics_handler.go:ExtractEARSPatterns()` - POST /api/v1/spec-analytics/ears-patterns

**Tested in:**
- `src/tracertm/tests/services/test_spec_analytics_service.py`
- `backend/internal/handlers/spec_analytics_handler_test.go`

**Constraints:**
- SHALL parse RFC 2119 keywords (SHALL, MUST, SHOULD, MAY)
- SHALL detect missing requirements (gaps in numbering)
- SHALL compute completeness score (requirements with tests / total requirements)
- SHALL track metrics over time (historical trends)

---

## FR-APP: Application & Tracking

### FR-APP-001: Item CRUD Operations

**Traces to:** Core data management epics
**Description:** The system SHALL provide RESTful API endpoints for creating, reading, updating, and deleting traceability items with full CRUD support and validation.

**Input:**
- Item data (title, description, type, attributes)
- Project context
- User authentication

**Output:**
- Created/updated/retrieved/deleted item
- Validation errors (422) if data invalid
- Audit trail entry

**Implemented in:**
- `src/tracertm/services/item_service.py`
- `src/tracertm/api/routers/items.py`
- `GET/POST/PUT/DELETE /api/v1/items`
- `GET /api/v1/items/{id}`
- `backend/internal/handlers/item_handler.go:CreateItem()` - POST /api/v1/items
- `backend/internal/handlers/item_handler.go:GetItem()` - GET /api/v1/items/:id
- `backend/internal/handlers/item_handler.go:UpdateItem()` - PUT /api/v1/items/:id
- `backend/internal/handlers/item_handler.go:DeleteItem()` - DELETE /api/v1/items/:id
- `backend/internal/handlers/item_handler.go:ListItems()` - GET /api/v1/items
- `backend/internal/services/item_service.go`

**Tested in:**
- `src/tracertm/tests/services/test_item_service.py`
- `src/tracertm/tests/api/test_items_router.py`
- `backend/internal/handlers/item_handler_test.go`

**Constraints:**
- SHALL validate required fields (title, type, project_id)
- SHALL enforce unique constraint on item IDs within project
- SHALL support partial updates (PATCH)
- SHALL log all changes to audit trail

---

### FR-APP-002: Link Management

**Traces to:** Relationship management epics
**Description:** The system SHALL allow users to create, delete, and query links between items with support for link types, directionality, and metadata.

**Input:**
- Source item ID
- Target item ID
- Link type (e.g., "implements", "tests", "depends_on")
- Optional metadata

**Output:**
- Created/deleted link
- Validation errors if link violates schema
- Updated graph

**Implemented in:**
- `src/tracertm/services/link_service.py`
- `POST /api/v1/links`
- `DELETE /api/v1/links/{id}`
- `backend/internal/handlers/link_handler.go:CreateLink()` - POST /api/v1/links
- `backend/internal/handlers/link_handler.go:ListLinks()` - GET /api/v1/links
- `backend/internal/handlers/link_handler.go:GetLink()` - GET /api/v1/links/:id
- `backend/internal/handlers/link_handler.go:DeleteLink()` - DELETE /api/v1/links/:id
- `backend/internal/services/link_service.go`

**Tested in:**
- `src/tracertm/tests/services/test_link_service.py`
- `backend/internal/handlers/link_handler_test.go`

**Constraints:**
- SHALL prevent duplicate links (same source, target, type)
- SHALL validate link types against project schema
- SHALL prevent cycles if configured (optional)
- SHALL support bidirectional links (auto-create reverse link)

---

### FR-APP-003: Status Workflow

**Traces to:** Workflow management epics
**Description:** The system SHALL enforce configurable status workflows with state transitions, validation rules, and event triggers.

**Input:**
- Item ID
- Target status
- Optional comment/reason

**Output:**
- Updated item with new status
- Validation error if transition invalid
- Triggered events (notifications, webhooks)

**Implemented in:**
- `src/tracertm/services/status_workflow_service.py`
- `PUT /api/v1/items/{id}/status`

**Tested in:**
- `src/tracertm/tests/services/test_status_workflow_service.py`

**Constraints:**
- SHALL enforce allowed transitions (e.g., draft→review→approved)
- SHALL support conditional transitions (e.g., requires approval)
- SHALL trigger webhooks on status changes
- SHALL record status history

---

### FR-APP-004: Search and Query

**Traces to:** Search epics
**Description:** The system SHALL provide full-text search across items with support for filters, facets, and advanced query syntax.

**Input:**
- Search query (text)
- Filters (type, status, project, date range)
- Pagination parameters

**Output:**
- Search results (items)
- Facets (counts by type, status, etc.)
- Total result count

**Implemented in:**
- `src/tracertm/services/search_service.py`
- `GET /api/v1/search`
- `backend/internal/search/indexer.go`
- `backend/internal/handlers/search_handler.go:Search()` - POST /api/v1/search
- `backend/internal/handlers/search_handler.go:SearchGet()` - GET /api/v1/search
- `backend/internal/services/search_service.go`

**Tested in:**
- `src/tracertm/tests/services/test_search_service.py`
- `backend/internal/handlers/search_handler_test.go`

**Constraints:**
- SHALL index title, description, tags, and custom fields
- SHALL support boolean operators (AND, OR, NOT)
- SHALL support phrase search ("exact match")
- SHALL highlight matching terms in results

---

### FR-APP-005: Bulk Operations

**Traces to:** Batch processing epics
**Description:** The system SHALL support bulk operations (create, update, delete, tag) on multiple items with atomic transactions and error recovery.

**Input:**
- Operation type (create, update, delete, tag)
- Item IDs or filters
- Operation parameters

**Output:**
- Operation results (success/failure per item)
- Summary (total, succeeded, failed)
- Detailed error log

**Implemented in:**
- `src/tracertm/services/bulk_service.py`
- `POST /api/v1/bulk/{operation}`

**Tested in:**
- `src/tracertm/tests/services/test_bulk_service.py`

**Constraints:**
- SHALL process operations in batches (100 items per batch)
- SHALL support rollback on failure (optional)
- SHALL provide progress updates (WebSocket)
- SHALL limit batch size (max 10,000 items)

---

### FR-APP-006: Project Management

**Traces to:** Project organization epics
**Description:** The system SHALL allow users to create and manage projects as containers for items, with support for project settings, members, and permissions.

**Input:**
- Project data (name, description)
- Settings (workflow, schema, permissions)
- Member list

**Output:**
- Created/updated project
- Project ID
- Default settings applied

**Implemented in:**
- `src/tracertm/api/routers/projects.py`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{id}`

**Tested in:**
- `src/tracertm/tests/api/test_projects_router.py`

**Constraints:**
- SHALL enforce unique project names within account
- SHALL create default workflow on project creation
- SHALL support project templates
- SHALL allow soft delete (archive) with restore

---

### FR-APP-007: Tagging System

**Traces to:** Metadata management epics
**Description:** The system SHALL support hierarchical tags with auto-completion, tag validation, and tag-based filtering.

**Input:**
- Item ID
- Tags (list of strings)

**Output:**
- Updated item with tags
- Tag suggestions (auto-complete)
- Tag usage statistics

**Implemented in:**
- `src/tracertm/services/item_service.py:update_tags()`
- `PUT /api/v1/items/{id}/tags`

**Tested in:**
- `src/tracertm/tests/services/test_item_service.py`

**Constraints:**
- SHALL support hierarchical tags (e.g., "platform/backend/api")
- SHALL provide tag auto-completion based on usage
- SHALL enforce tag naming rules (lowercase, alphanumeric + dash)
- SHALL limit tag count per item (max 20)

---

### FR-APP-008: Custom Fields

**Traces to:** Extensibility epics
**Description:** The system SHALL support custom fields per item type with configurable types, validation rules, and indexing.

**Input:**
- Item type
- Field definition (name, type, validation)
- Field value

**Output:**
- Updated item with custom field values
- Validation errors if value invalid

**Implemented in:**
- `src/tracertm/services/item_spec_service.py`
- `src/tracertm/models/item_spec.py`
- `POST /api/v1/item-specs/{type}/fields`

**Tested in:**
- `src/tracertm/tests/services/test_item_spec_service.py`

**Constraints:**
- SHALL support field types: text, number, date, enum, boolean
- SHALL enforce field validation (min/max, regex, required)
- SHALL index custom fields for search
- SHALL support field dependencies (conditional display)

---

### FR-APP-009: Version History

**Traces to:** Audit trail epics
**Description:** The system SHALL maintain complete version history for all items with diff views, rollback capability, and change attribution.

**Input:**
- Item ID
- Optional version ID (for rollback)

**Output:**
- Version history (list of changes)
- Diff between versions
- Rollback confirmation

**Implemented in:**
- `src/tracertm/services/history_service.py`
- `GET /api/v1/items/{id}/history`
- `POST /api/v1/items/{id}/rollback`

**Tested in:**
- `src/tracertm/tests/services/test_history_service.py`

**Constraints:**
- SHALL store full item state for each version
- SHALL compute diffs on-demand (not stored)
- SHALL preserve deleted items in history
- SHALL support time-travel queries (item state at timestamp)

---

### FR-APP-010: Progress Tracking

**Traces to:** Project monitoring epics
**Description:** The system SHALL track progress across projects, epics, and features with support for completion percentages, burndown charts, and velocity metrics.

**Input:**
- Project ID or epic ID
- Date range

**Output:**
- Progress percentage
- Burndown data
- Velocity metrics

**Implemented in:**
- `src/tracertm/services/progress_service.py`
- `GET /api/v1/progress`

**Tested in:**
- `src/tracertm/tests/services/test_progress_service.py`

**Constraints:**
- SHALL compute progress based on item completion
- SHALL support weighted progress (by effort or priority)
- SHALL generate burndown charts (actual vs. ideal)
- SHALL compute velocity (items completed per time period)

---

## FR-VERIF: Verification & Validation

### FR-VERIF-001: Test Case Management

**Traces to:** Testing epics
**Description:** The system SHALL allow users to create and manage test cases with steps, expected results, and links to requirements.

**Input:**
- Test case data (title, steps, expected results)
- Requirements (item IDs to link)

**Output:**
- Created test case
- Links to requirements

**Implemented in:**
- `src/tracertm/models/test_case.py`
- `POST /api/v1/tests/cases`

**Tested in:**
- `src/tracertm/tests/api/test_tests_router.py`

**Constraints:**
- SHALL support structured test steps (preconditions, actions, expected results)
- SHALL link test cases to requirements
- SHALL support test case templates
- SHALL validate required fields

---

### FR-VERIF-002: Test Suite Management

**Traces to:** Testing epics
**Description:** The system SHALL organize test cases into test suites with support for suite hierarchies and execution ordering.

**Input:**
- Suite data (name, description)
- Test case IDs

**Output:**
- Created test suite
- Suite hierarchy

**Implemented in:**
- `src/tracertm/models/test_suite.py`
- `POST /api/v1/tests/suites`

**Tested in:**
- `src/tracertm/tests/api/test_tests_router.py`

**Constraints:**
- SHALL support nested suites (up to 5 levels)
- SHALL define execution order
- SHALL support suite templates
- SHALL compute suite completion percentage

---

### FR-VERIF-003: Test Execution

**Traces to:** Test execution epics
**Description:** The system SHALL execute test suites and record results with support for manual and automated testing.

**Input:**
- Suite ID or test case IDs
- Execution configuration

**Output:**
- Test run record
- Test results (pass/fail/skip per test)
- Execution logs

**Implemented in:**
- `src/tracertm/services/execution/test_executor.py`
- `POST /api/v1/execution/run`
- `backend/internal/handlers/test_handler.go`

**Tested in:**
- `src/tracertm/tests/services/test_execution_service.py`

**Constraints:**
- SHALL support manual test execution (UI-based)
- SHALL integrate with automated test frameworks (pytest, Jest)
- SHALL capture screenshots/logs for failures
- SHALL support parallel execution

---

### FR-VERIF-004: Coverage Tracking

**Traces to:** Coverage epics
**Description:** The system SHALL track test coverage at multiple levels (requirements, code, features) with support for coverage reports and thresholds.

**Input:**
- Project ID
- Coverage type
- Threshold configuration

**Output:**
- Coverage percentage
- Coverage report
- Threshold violations

**Implemented in:**
- `src/tracertm/models/test_coverage.py`
- `GET /api/v1/coverage`

**Tested in:**
- `src/tracertm/tests/services/test_coverage_service.py`

**Constraints:**
- SHALL compute requirement coverage (tests per requirement)
- SHALL integrate code coverage tools (Coverage.py, Istanbul)
- SHALL track coverage trends over time
- SHALL alert on coverage drops

---

### FR-VERIF-005: BDD Scenario Management

**Traces to:** BDD testing epics
**Description:** The system SHALL support Behavior-Driven Development scenarios with Gherkin syntax parsing and execution integration.

**Input:**
- Scenario (Gherkin syntax)
- Feature ID

**Output:**
- Parsed scenario
- Linked feature
- Execution integration

**Implemented in:**
- `src/tracertm/models/scenario.py`
- `src/tracertm/services/scenario_service.py`
- `POST /api/v1/scenarios`

**Tested in:**
- `src/tracertm/tests/services/test_scenario_service.py`

**Constraints:**
- SHALL parse Gherkin syntax (Given/When/Then)
- SHALL link scenarios to features
- SHALL integrate with Cucumber/Behave
- SHALL validate scenario syntax

---

### FR-VERIF-006: Verification Matrix

**Traces to:** Verification epics
**Description:** The system SHALL generate verification matrices showing requirements vs. verification methods (test, analysis, inspection, demo).

**Input:**
- Project ID
- Verification types

**Output:**
- Verification matrix
- Coverage statistics
- Unverified requirements

**Implemented in:**
- `src/tracertm/services/verification_service.py`
- `GET /api/v1/verification/matrix`

**Tested in:**
- `src/tracertm/tests/services/test_verification_service.py`

**Constraints:**
- SHALL support multiple verification methods
- SHALL identify unverified requirements
- SHALL compute verification completeness
- SHALL export matrix (Excel, PDF)

---

### FR-VERIF-007: Test Result History

**Traces to:** Test tracking epics
**Description:** The system SHALL maintain test result history with support for trend analysis, flaky test detection, and regression tracking.

**Input:**
- Test case ID
- Date range

**Output:**
- Test result history
- Pass/fail trends
- Flaky test indicators

**Implemented in:**
- `src/tracertm/models/test_run.py`
- `GET /api/v1/tests/history`

**Tested in:**
- `src/tracertm/tests/services/test_history_service.py`

**Constraints:**
- SHALL store all test executions indefinitely
- SHALL detect flaky tests (intermittent failures)
- SHALL compute pass rate trends
- SHALL identify regressions (new failures)

---

### FR-VERIF-008: Validation Rules

**Traces to:** Data quality epics
**Description:** The system SHALL enforce validation rules on items with support for custom rules, rule templates, and validation reporting.

**Input:**
- Item data
- Validation rules

**Output:**
- Validation result (pass/fail)
- Rule violations
- Suggested fixes

**Implemented in:**
- `src/tracertm/validation/validator.py`
- `POST /api/v1/validate`

**Tested in:**
- `src/tracertm/tests/validation/test_validator.py`

**Constraints:**
- SHALL support regex-based rules
- SHALL support custom validation functions (Python/JS)
- SHALL provide detailed error messages
- SHALL support validation rule versioning

---

### FR-VERIF-009: Acceptance Criteria Tracking

**Traces to:** Requirements management epics
**Description:** The system SHALL track acceptance criteria per requirement with support for pass/fail status and verification evidence.

**Input:**
- Requirement ID
- Acceptance criteria (list)

**Output:**
- Updated requirement with criteria
- Criteria status
- Verification evidence

**Implemented in:**
- `src/tracertm/services/item_service.py`
- `PUT /api/v1/items/{id}/acceptance-criteria`

**Tested in:**
- `src/tracertm/tests/services/test_item_service.py`

**Constraints:**
- SHALL support structured criteria (Given/When/Then)
- SHALL link criteria to test cases
- SHALL track criteria status (pending, passed, failed)
- SHALL require verification evidence for passed criteria

---

### FR-VERIF-010: Compliance Verification

**Traces to:** Compliance epics
**Description:** The system SHALL verify compliance with standards (ISO, DO-178, etc.) by checking requirement attributes, traceability completeness, and documentation.

**Input:**
- Project ID
- Standard/template ID

**Output:**
- Compliance report
- Non-conformances
- Remediation recommendations

**Implemented in:**
- `src/tracertm/services/security_compliance_service.py`
- `POST /api/v1/compliance/verify`

**Tested in:**
- `src/tracertm/tests/services/test_compliance_service.py`

**Constraints:**
- SHALL support compliance templates (ISO 26262, DO-178C, etc.)
- SHALL check required attributes per standard
- SHALL verify bidirectional traceability
- SHALL generate audit-ready reports

---

## FR-RPT: Reporting & Analytics

### FR-RPT-001: Dashboard Analytics

**Traces to:** Analytics epics
**Description:** The system SHALL provide customizable dashboards with real-time metrics, charts, and widgets for project health monitoring.

**Input:**
- Dashboard configuration
- Date range

**Output:**
- Dashboard data (metrics, charts)
- Real-time updates (WebSocket)

**Implemented in:**
- `src/tracertm/services/advanced_analytics_service.py`
- `GET /api/v1/analytics/dashboard`

**Tested in:**
- `src/tracertm/tests/services/test_analytics_service.py`

**Constraints:**
- SHALL support configurable widgets (charts, tables, KPIs)
- SHALL update in real-time via WebSocket
- SHALL support drill-down (click chart to see details)
- SHALL export dashboard data (CSV, JSON)

---

### FR-RPT-002: Export to Excel

**Traces to:** Export epics
**Description:** The system SHALL export items, links, and reports to Excel format with support for formatting, formulas, and multi-sheet workbooks.

**Input:**
- Export type (items, matrix, report)
- Filters and scope

**Output:**
- Excel file (.xlsx)
- Download link

**Implemented in:**
- `src/tracertm/services/export_service.py`
- `POST /api/v1/export/excel`
- `backend/internal/handlers/stream_handler.go:StreamExport()` - GET /api/v1/export/:type/stream
- `backend/internal/services/export_service.go`

**Tested in:**
- `src/tracertm/tests/services/test_export_service.py`
- `backend/internal/handlers/stream_handler_test.go`

**Constraints:**
- SHALL preserve formatting (colors, fonts)
- SHALL support formulas in cells
- SHALL support multi-sheet workbooks
- SHALL handle large exports (>10,000 rows) via background job

---

### FR-RPT-003: Export to PDF

**Traces to:** Export epics
**Description:** The system SHALL export reports to PDF format with support for custom templates, headers/footers, and table of contents.

**Input:**
- Report type
- Template configuration

**Output:**
- PDF file
- Download link

**Implemented in:**
- `src/tracertm/services/export_service.py`
- `POST /api/v1/export/pdf`

**Tested in:**
- `src/tracertm/tests/services/test_export_service.py`

**Constraints:**
- SHALL use custom templates (HTML → PDF)
- SHALL generate table of contents with page numbers
- SHALL support headers/footers with metadata
- SHALL handle large reports (>1000 pages) via streaming

---

### FR-RPT-004: Traceability Report Generation

**Traces to:** Reporting epics
**Description:** The system SHALL generate comprehensive traceability reports showing all relationships, coverage, and compliance status.

**Input:**
- Project ID
- Report template

**Output:**
- Traceability report (PDF, HTML, Excel)
- Coverage statistics
- Compliance checklist

**Implemented in:**
- `src/tracertm/services/graph_report_service.py`
- `POST /api/v1/reports/traceability`

**Tested in:**
- `src/tracertm/tests/services/test_report_service.py`

**Constraints:**
- SHALL include forward and backward traceability
- SHALL show coverage percentages
- SHALL identify gaps and issues
- SHALL support report templates (ISO, DO-178, etc.)

---

### FR-RPT-005: Custom Report Builder

**Traces to:** Reporting epics
**Description:** The system SHALL provide a report builder UI for creating custom reports with drag-and-drop widgets, filters, and formatting.

**Input:**
- Report definition (widgets, filters, layout)

**Output:**
- Generated report
- Saved report template

**Implemented in:**
- `frontend/apps/web/src/features/reports/ReportBuilder.tsx`
- `POST /api/v1/reports/custom`

**Tested in:**
- `frontend/apps/web/src/__tests__/reports/ReportBuilder.test.tsx`

**Constraints:**
- SHALL support drag-and-drop widget placement
- SHALL preview report before generation
- SHALL save report templates for reuse
- SHALL support scheduled report generation

---

### FR-RPT-006: Metrics Collection

**Traces to:** Observability epics
**Description:** The system SHALL collect system metrics (performance, usage, errors) and SHALL expose them via Prometheus-compatible endpoint.

**Input:**
- Metric name
- Optional filters

**Output:**
- Metric values
- Prometheus metrics endpoint

**Implemented in:**
- `src/tracertm/services/metrics_service.py`
- `GET /metrics`
- `backend/internal/metrics/collector.go` - Prometheus metrics collector
- `backend/internal/metrics/middleware.go` - HTTP metrics middleware
- `backend/internal/handlers/health_handler.go:Metrics()` - GET /metrics (Prometheus format)

**Tested in:**
- `src/tracertm/tests/services/test_metrics_service.py`
- `backend/internal/metrics/collector_test.go`

**Constraints:**
- SHALL collect request latency, error rates, DB query times
- SHALL expose metrics in Prometheus format
- SHALL support custom metrics
- SHALL integrate with Grafana for visualization

---

### FR-RPT-007: Audit Trail Export

**Traces to:** Compliance epics
**Description:** The system SHALL export complete audit trails for compliance and forensic analysis with support for filtering and tamper-evident signatures.

**Input:**
- Date range
- User or item filters

**Output:**
- Audit log (CSV, JSON)
- Cryptographic signature

**Implemented in:**
- `src/tracertm/services/history_service.py`
- `POST /api/v1/audit/export`

**Tested in:**
- `src/tracertm/tests/services/test_audit_service.py`

**Constraints:**
- SHALL include all CRUD operations
- SHALL record user, timestamp, IP address
- SHALL support tamper-evident signatures (HMAC)
- SHALL export in machine-readable format

---

### FR-RPT-008: Visualization Library

**Traces to:** Visualization epics
**Description:** The system SHALL provide a library of visualization components for graphs, matrices, charts, and timelines.

**Input:**
- Visualization type
- Data source

**Output:**
- Rendered visualization
- Interactive controls

**Implemented in:**
- `frontend/apps/web/src/graph/`
- `src/tracertm/services/visualization_service.py`

**Tested in:**
- `frontend/apps/web/src/__tests__/graph/`

**Constraints:**
- SHALL support graph visualization (force-directed, hierarchical)
- SHALL support matrix heatmaps
- SHALL support interactive controls (zoom, pan, filter)
- SHALL export visualizations as images (PNG, SVG)

---

### FR-RPT-009: Report Scheduling

**Traces to:** Automation epics
**Description:** The system SHALL schedule report generation and delivery with support for cron expressions and email delivery.

**Input:**
- Report configuration
- Schedule (cron expression)
- Recipients

**Output:**
- Scheduled job record
- Generated reports (emailed on schedule)

**Implemented in:**
- `src/tracertm/services/workflow_schedule.py`
- `POST /api/v1/reports/schedule`

**Tested in:**
- `src/tracertm/tests/services/test_schedule_service.py`

**Constraints:**
- SHALL support cron expressions for scheduling
- SHALL send reports via email
- SHALL retry on failure (3 attempts)
- SHALL allow manual trigger of scheduled reports

---

### FR-RPT-010: Change Log Reports

**Traces to:** Change management epics
**Description:** The system SHALL generate change log reports showing all changes within a date range with grouping, filtering, and export capabilities.

**Input:**
- Date range
- Filters (users, items, projects)

**Output:**
- Change log report
- Export formats (PDF, CSV)

**Implemented in:**
- `src/tracertm/services/history_service.py`
- `GET /api/v1/reports/changelog`

**Tested in:**
- `src/tracertm/tests/services/test_changelog_service.py`

**Constraints:**
- SHALL group changes by date, user, or item
- SHALL show before/after values
- SHALL support detailed and summary views
- SHALL export to PDF and CSV

---

## FR-COLLAB: Collaboration & Integration

### FR-COLLAB-001: Real-Time Collaboration

**Traces to:** Real-time collaboration epics
**Description:** The system SHALL support real-time collaboration with live cursors, presence indicators, and concurrent editing via WebSocket.

**Input:**
- User session
- Item ID

**Output:**
- Real-time updates (WebSocket)
- Presence indicators (who's viewing)
- Live cursor positions

**Implemented in:**
- `backend/internal/handlers/websocket_handler.go`
- `backend/internal/websocket/hub.go`
- `WS /ws`
- `backend/internal/handlers/stream_handler.go` - Server-Sent Events for real-time updates
- `backend/internal/handlers/graph_stream_handler.go:StreamGraphIncremental()` - POST /api/v1/projects/:project_id/graph/stream
- `backend/internal/grpc/server.go:StreamGraphUpdates()` - gRPC GraphService.StreamGraphUpdates

**Tested in:**
- `backend/internal/handlers/websocket_handler_test.go`
- `backend/internal/handlers/stream_handler_test.go`
- `backend/internal/handlers/graph_stream_handler_test.go`

**Constraints:**
- SHALL broadcast changes within 100ms
- SHALL show active users per item
- SHALL handle conflict resolution (last-write-wins with merge)
- SHALL support up to 100 concurrent users per item

---

### FR-COLLAB-002: Comments and Discussions

**Traces to:** Communication epics
**Description:** The system SHALL allow users to comment on items with support for threaded discussions, mentions, and rich formatting.

**Input:**
- Item ID
- Comment text (Markdown)
- Optional parent comment ID (for threading)

**Output:**
- Created comment
- Notifications to mentioned users
- Updated discussion thread

**Implemented in:**
- `src/tracertm/models/comment.py`
- `POST /api/v1/items/{id}/comments`

**Tested in:**
- `src/tracertm/tests/api/test_comments_router.py`

**Constraints:**
- SHALL support Markdown formatting
- SHALL support @mentions with notifications
- SHALL support threaded replies (up to 5 levels)
- SHALL allow comment editing and deletion

---

### FR-COLLAB-003: Notifications

**Traces to:** Notification epics
**Description:** The system SHALL send notifications to users for events (mentions, assignments, status changes) via in-app, email, and webhooks.

**Input:**
- Event type
- User or role
- Notification preferences

**Output:**
- Notification record
- Delivered notification (in-app, email, webhook)

**Implemented in:**
- `src/tracertm/services/notification_service.py`
- `GET /api/v1/notifications`
- `POST /api/v1/notifications/mark-read`

**Tested in:**
- `src/tracertm/tests/services/test_notification_service.py`

**Constraints:**
- SHALL support multiple channels (in-app, email, webhook)
- SHALL batch notifications (digest mode)
- SHALL respect user preferences (opt-in/opt-out)
- SHALL track read/unread status

---

### FR-COLLAB-004: Webhook Delivery

**Traces to:** Integration epics
**Description:** The system SHALL deliver webhook events to external systems with support for retry, filtering, and payload customization.

**Input:**
- Webhook configuration (URL, events, filters)
- Event data

**Output:**
- HTTP POST to webhook URL
- Delivery status
- Retry on failure

**Implemented in:**
- `src/tracertm/services/webhook_service.py`
- `POST /api/v1/webhooks/register`
- `backend/internal/handlers/webhook_handler.go`

**Tested in:**
- `src/tracertm/tests/services/test_webhook_service.py`

**Constraints:**
- SHALL sign payloads with HMAC for security
- SHALL retry failed deliveries (3 attempts with exponential backoff)
- SHALL filter events based on webhook configuration
- SHALL timeout after 10 seconds

---

### FR-COLLAB-005: GitHub Sync

**Traces to:** GitHub integration epics
**Description:** The system SHALL synchronize items with GitHub issues bidirectionally with support for incremental sync and conflict resolution.

**Input:**
- GitHub repository
- Sync configuration (direction, mapping)

**Output:**
- Synced items
- Sync status report
- Conflict log

**Implemented in:**
- `src/tracertm/services/github_project_service.py`
- `POST /api/v1/github/sync`

**Tested in:**
- `src/tracertm/tests/services/test_github_sync_service.py`

**Constraints:**
- SHALL sync bidirectionally (TraceRTM ↔ GitHub)
- SHALL detect conflicts (concurrent edits)
- SHALL support incremental sync (only changed items)
- SHALL map GitHub labels to TraceRTM tags

---

### FR-COLLAB-006: Linear Integration

**Traces to:** Linear integration epics
**Description:** The system SHALL integrate with Linear for issue tracking with support for sync, webhooks, and status mapping.

**Input:**
- Linear team ID
- Sync configuration

**Output:**
- Synced items
- Webhook registration
- Status mapping

**Implemented in:**
- `backend/internal/handlers/linear_handler.go`
- `src/tracertm/models/linear_app.py`
- `POST /api/v1/linear/sync`

**Tested in:**
- `backend/internal/handlers/linear_handler_test.go`

**Constraints:**
- SHALL map Linear issue states to TraceRTM statuses
- SHALL sync assignees and labels
- SHALL receive Linear webhooks
- SHALL support bidirectional sync

---

### FR-COLLAB-007: Figma Integration

**Traces to:** Design integration epics
**Description:** The system SHALL integrate with Figma for design assets with support for embedding, linking, and version tracking.

**Input:**
- Figma file URL
- Frame or component ID

**Output:**
- Embedded Figma frame
- Link to design asset
- Version history

**Implemented in:**
- `backend/internal/handlers/figma_handler.go`
- `backend/internal/figma/`

**Tested in:**
- `backend/internal/handlers/figma_handler_test.go`

**Constraints:**
- SHALL embed Figma frames via iframe
- SHALL track design version changes
- SHALL link designs to requirements
- SHALL support Figma webhook updates

---

### FR-COLLAB-008: OAuth Integration

**Traces to:** Authentication epics
**Description:** The system SHALL support OAuth 2.0 flows for external service authentication with support for multiple providers.

**Input:**
- OAuth provider
- Scopes

**Output:**
- Access token
- Refresh token
- User profile

**Implemented in:**
- `src/tracertm/api/routers/oauth.py`
- `backend/internal/handlers/auth_handler.go`
- `GET /api/v1/oauth/{provider}/authorize`

**Tested in:**
- `src/tracertm/tests/api/test_oauth_router.py`

**Constraints:**
- SHALL support GitHub, Google, Microsoft providers
- SHALL implement PKCE for security
- SHALL refresh tokens automatically
- SHALL store tokens securely (encrypted)

---

### FR-COLLAB-009: Team Management

**Traces to:** User management epics
**Description:** The system SHALL allow users to create teams, assign members, and manage permissions with support for role-based access control.

**Input:**
- Team data (name, members)
- Roles and permissions

**Output:**
- Created team
- Member assignments
- Permission grants

**Implemented in:**
- `src/tracertm/models/account.py`
- `src/tracertm/models/account_user.py`
- `POST /api/v1/teams`

**Tested in:**
- `src/tracertm/tests/api/test_teams_router.py`

**Constraints:**
- SHALL support role hierarchies (owner, admin, member, viewer)
- SHALL enforce permissions at API level
- SHALL support team-based notifications
- SHALL audit permission changes

---

### FR-COLLAB-010: Activity Feed

**Traces to:** Activity tracking epics
**Description:** The system SHALL maintain an activity feed per project showing recent changes, comments, and status updates with filtering and pagination.

**Input:**
- Project ID
- Filters (users, event types, date range)
- Pagination parameters

**Output:**
- Activity feed (list of events)
- Total event count

**Implemented in:**
- `src/tracertm/services/event_service.py`
- `GET /api/v1/activity`

**Tested in:**
- `src/tracertm/tests/services/test_activity_service.py`

**Constraints:**
- SHALL show last 1000 events by default
- SHALL support real-time updates (WebSocket)
- SHALL filter by user, event type, date
- SHALL link events to source items

---

## FR-AI: AI & Automation

### FR-AI-001: AI Chat Assistant

**Traces to:** AI assistant epics
**Description:** The system SHALL provide an AI chat assistant powered by Claude that can answer questions, generate content, and perform actions via MCP tools.

**Input:**
- User message
- Conversation context

**Output:**
- AI response
- Tool calls (if assistant invokes MCP tools)
- Updated conversation history

**Implemented in:**
- `src/tracertm/api/routers/chat.py`
- `src/tracertm/services/ai_service.py`
- `POST /api/v1/chat/message`

**Tested in:**
- `src/tracertm/tests/api/test_chat_router.py`

**Constraints:**
- SHALL use Claude Opus for chat
- SHALL invoke MCP tools when appropriate
- SHALL maintain conversation context (last 20 messages)
- SHALL stream responses via WebSocket

---

### FR-AI-002: Agent Coordination

**Traces to:** Multi-agent epics
**Description:** The system SHALL coordinate multiple AI agents working in parallel on complex tasks with support for task decomposition, dependency tracking, and result aggregation.

**Input:**
- Task description
- Agent configuration

**Output:**
- Task decomposition (subtasks)
- Agent assignments
- Aggregated results

**Implemented in:**
- `src/tracertm/services/agent_coordination_service.py`
- `POST /api/v1/agents/coordinate`

**Tested in:**
- `src/tracertm/tests/services/test_agent_coordination_service.py`

**Constraints:**
- SHALL support up to 50 concurrent agents
- SHALL track agent progress and failures
- SHALL aggregate results when all agents complete
- SHALL handle agent timeouts (60s per agent)

---

### FR-AI-003: Agent Monitoring

**Traces to:** Agent observability epics
**Description:** The system SHALL monitor agent health, performance, and resource usage with support for alerting and visualization.

**Input:**
- Agent ID or all agents

**Output:**
- Agent status
- Performance metrics
- Resource usage

**Implemented in:**
- `src/tracertm/services/agent_monitoring_service.py`
- `GET /api/v1/agents/status`

**Tested in:**
- `src/tracertm/tests/services/test_agent_monitoring_service.py`

**Constraints:**
- SHALL track agent CPU, memory, API call counts
- SHALL detect stuck agents (no progress for 5 min)
- SHALL alert on agent failures
- SHALL visualize agent activity (real-time dashboard)

---

### FR-AI-004: Code Analysis

**Traces to:** Code intelligence epics
**Description:** The system SHALL analyze code repositories to extract requirements, generate documentation, and detect issues using AI-powered tools.

**Input:**
- Repository URL or path
- Analysis type (requirements, docs, issues)

**Output:**
- Extracted requirements
- Generated documentation
- Detected issues

**Implemented in:**
- `backend/internal/handlers/code_index_handler.go`
- `src/tracertm/services/ai_tools.py:analyze_code()`
- `POST /api/v1/ai/analyze-code`

**Tested in:**
- `backend/internal/handlers/code_index_handler_test.go`

**Constraints:**
- SHALL index code files (Python, TypeScript, Go, Java)
- SHALL extract docstrings and comments
- SHALL detect SHALL/MUST/SHOULD statements
- SHALL link code to requirements via annotations

---

### FR-AI-005: Requirement Generation

**Traces to:** AI content generation epics
**Description:** The system SHALL generate requirement text from user descriptions using AI with support for templates, quality validation, and refinement.

**Input:**
- User description (free text)
- Template or style guide

**Output:**
- Generated requirement text
- Quality score
- Suggestions for improvement

**Implemented in:**
- `src/tracertm/services/ai_service.py:generate_requirement()`
- `POST /api/v1/ai/generate-requirement`

**Tested in:**
- `src/tracertm/tests/services/test_ai_generation_service.py`

**Constraints:**
- SHALL use Claude for generation
- SHALL validate quality (clarity, completeness, testability)
- SHALL suggest improvements for low-quality output
- SHALL support refinement (iterative generation)

---

### FR-AI-006: Agent Checkpointing

**Traces to:** Agent reliability epics
**Description:** The system SHALL checkpoint agent state periodically to enable recovery from failures and resume long-running tasks.

**Input:**
- Agent ID
- Checkpoint frequency

**Output:**
- Checkpoint record
- Restore capability

**Implemented in:**
- `src/tracertm/models/agent_checkpoint.py`
- `src/tracertm/services/checkpoint_service.py`
- `POST /api/v1/agents/{id}/checkpoint`

**Tested in:**
- `src/tracertm/tests/services/test_checkpoint_service.py`

**Constraints:**
- SHALL checkpoint every 5 minutes by default
- SHALL store checkpoint in database (serialized state)
- SHALL restore agent state on failure
- SHALL prune old checkpoints (keep last 10)

---

### FR-AI-007: Workflow Automation

**Traces to:** Workflow automation epics
**Description:** The system SHALL execute workflows defined as DAGs of tasks using Temporal for orchestration with support for retries, timeouts, and error handling.

**Input:**
- Workflow definition (YAML or JSON)
- Input parameters

**Output:**
- Workflow execution ID
- Task execution status
- Workflow result

**Implemented in:**
- `src/tracertm/services/temporal_service.py`
- `src/tracertm/workflows/`
- `POST /api/v1/workflow/execute`

**Tested in:**
- `src/tracertm/tests/services/test_workflow_service.py`

**Constraints:**
- SHALL use Temporal for workflow orchestration
- SHALL support task retries (configurable)
- SHALL timeout long-running tasks (default 1 hour)
- SHALL handle errors with custom error handlers

---

### FR-AI-008: Embedding Generation

**Traces to:** Semantic search epics
**Description:** The system SHALL generate embeddings for items using AI models to enable semantic search and similarity computation.

**Input:**
- Item ID or text
- Model configuration

**Output:**
- Embedding vector (768 dimensions)
- Storage confirmation

**Implemented in:**
- `backend/internal/embeddings/generator.go`
- `src/tracertm/services/ai_service.py:generate_embeddings()`
- `POST /api/v1/ai/embeddings`

**Tested in:**
- `backend/internal/embeddings/generator_test.go`

**Constraints:**
- SHALL use OpenAI or Cohere embeddings
- SHALL cache embeddings in vector database
- SHALL recompute embeddings on item changes
- SHALL batch embedding generation (100 items per batch)

---

### FR-AI-009: Agent Performance Tracking

**Traces to:** Agent analytics epics
**Description:** The system SHALL track agent performance metrics (success rate, latency, token usage) with support for historical analysis and optimization recommendations.

**Input:**
- Agent ID or time range

**Output:**
- Performance metrics
- Historical trends
- Optimization recommendations

**Implemented in:**
- `src/tracertm/services/agent_performance_service.py`
- `GET /api/v1/agents/performance`

**Tested in:**
- `src/tracertm/tests/services/test_agent_performance_service.py`

**Constraints:**
- SHALL track success rate, latency, token usage
- SHALL compute metrics per agent and aggregate
- SHALL detect performance regressions
- SHALL recommend optimizations (prompt tuning, model changes)

---

### FR-AI-010: Auto-Documentation

**Traces to:** Documentation generation epics
**Description:** The system SHALL automatically generate documentation from items, code, and specifications using AI with support for multiple formats and styles.

**Input:**
- Project ID or item IDs
- Documentation format (Markdown, HTML, PDF)
- Style guide

**Output:**
- Generated documentation
- Table of contents
- Cross-references

**Implemented in:**
- `src/tracertm/services/documentation_service.py`
- `POST /api/v1/ai/generate-docs`

**Tested in:**
- `src/tracertm/tests/services/test_documentation_service.py`

**Constraints:**
- SHALL generate structured documentation (headings, sections)
- SHALL create table of contents with links
- SHALL cross-reference items and requirements
- SHALL support templates (software design doc, user manual, etc.)

---

## FR-INFRA: Infrastructure

### FR-INFRA-001: Authentication

**Traces to:** Authentication epics
**Description:** The system SHALL authenticate users via WorkOS supporting SSO, OAuth, and local credentials with JWT token management.

**Input:**
- Credentials (email/password, OAuth code, SAML assertion)

**Output:**
- JWT access token
- Refresh token
- User profile

**Implemented in:**
- `src/tracertm/services/workos_auth_service.py`
- `backend/internal/handlers/auth_handler.go:Login()` - POST /api/v1/auth/login
- `backend/internal/handlers/auth_handler.go:Logout()` - POST /api/v1/auth/logout
- `backend/internal/handlers/auth_handler.go:RefreshToken()` - POST /api/v1/auth/refresh
- `backend/internal/handlers/auth_handler.go:ValidateSession()` - GET /api/v1/auth/validate
- `backend/internal/auth/workos_provider.go`

**Tested in:**
- `src/tracertm/tests/services/test_auth_service.py`
- `backend/internal/handlers/auth_handler_test.go`

**Constraints:**
- SHALL support email/password, Google, GitHub, Microsoft
- SHALL enforce MFA (optional)
- SHALL expire access tokens after 1 hour
- SHALL refresh tokens automatically

---

### FR-INFRA-002: Authorization

**Traces to:** Authorization epics
**Description:** The system SHALL enforce role-based access control (RBAC) with support for custom roles, permissions, and resource-level access.

**Input:**
- User ID
- Resource (item, project, etc.)
- Action (read, write, delete)

**Output:**
- Authorization decision (allow/deny)

**Implemented in:**
- `src/tracertm/api/middleware/auth.py`
- `backend/internal/auth/authorizer.go`
- `backend/internal/auth/middleware.go` - JWT middleware for Echo routes
- `backend/internal/auth/rbac.go` - Role-based access control implementation

**Tested in:**
- `src/tracertm/tests/middleware/test_auth_middleware.py`
- `backend/internal/auth/middleware_test.go`

**Constraints:**
- SHALL support roles (owner, admin, editor, viewer)
- SHALL enforce permissions at API level (middleware)
- SHALL support resource-level permissions (item, project)
- SHALL cache authorization decisions (5 min TTL)

---

### FR-INFRA-003: Database Migrations

**Traces to:** Data management epics
**Description:** The system SHALL manage database schema changes via migrations with support for rollback, validation, and zero-downtime deployments.

**Input:**
- Migration scripts (Alembic/Atlas)

**Output:**
- Applied migrations
- Schema version

**Implemented in:**
- `alembic/` (Python)
- `backend/internal/database/migrations/` (Go)

**Tested in:**
- `src/tracertm/tests/database/test_migrations.py`

**Constraints:**
- SHALL use Alembic for Python migrations
- SHALL use Atlas for Go migrations
- SHALL validate migrations before applying
- SHALL support rollback to previous version

---

### FR-INFRA-004: Caching

**Traces to:** Performance epics
**Description:** The system SHALL cache frequently accessed data in Redis with support for TTL, invalidation, and cache warming.

**Input:**
- Cache key
- Data to cache
- TTL (time-to-live)

**Output:**
- Cached data (on read)
- Cache hit/miss status

**Implemented in:**
- `src/tracertm/services/cache_service.py`
- `backend/internal/cache/redis.go` - Redis client implementation
- `backend/internal/cache/cache.go` - Cache interface and factory
- `backend/internal/cache/memory.go` - In-memory cache fallback

**Tested in:**
- `src/tracertm/tests/services/test_cache_service.py`
- `backend/internal/cache/redis_test.go`

**Constraints:**
- SHALL use Redis for caching
- SHALL set default TTL to 5 minutes
- SHALL invalidate cache on data changes
- SHALL implement cache warming for hot data

---

### FR-INFRA-005: File Storage

**Traces to:** Storage epics
**Description:** The system SHALL store files in S3-compatible storage with support for versioning, access control, and CDN integration.

**Input:**
- File upload
- Storage configuration

**Output:**
- Stored file URL
- Version ID

**Implemented in:**
- `src/tracertm/services/storage_service.py`
- `backend/internal/storage/s3.go`

**Tested in:**
- `src/tracertm/tests/services/test_storage_service.py`

**Constraints:**
- SHALL use S3-compatible storage (AWS S3, MinIO)
- SHALL generate signed URLs for secure access
- SHALL support versioning
- SHALL integrate with CDN for performance

---

### FR-INFRA-006: Event Bus

**Traces to:** Event-driven architecture epics
**Description:** The system SHALL publish and consume events via NATS message bus with support for topics, durable subscriptions, and exactly-once delivery.

**Input:**
- Event type
- Event payload

**Output:**
- Published event
- Subscriber notifications

**Implemented in:**
- `src/tracertm/services/event_service.py`
- `backend/internal/nats/publisher.go` - NATS event publisher
- `backend/internal/nats/subscriber.go` - NATS event subscriber
- `backend/internal/nats/client.go` - NATS client initialization

**Tested in:**
- `src/tracertm/tests/services/test_event_service.py`
- `backend/internal/nats/publisher_test.go`

**Constraints:**
- SHALL use NATS for event bus
- SHALL support topics and wildcards
- SHALL ensure exactly-once delivery (idempotency)
- SHALL support durable subscriptions

---

### FR-INFRA-007: Health Checks

**Traces to:** Observability epics
**Description:** The system SHALL provide health check endpoints for monitoring service availability and dependencies.

**Input:**
- None

**Output:**
- Health status (healthy, degraded, unhealthy)
- Dependency status (DB, Redis, NATS, etc.)

**Implemented in:**
- `src/tracertm/api/routers/health.py`
- `backend/internal/handlers/health_handler.go:HealthCheck()` - GET /health
- `backend/internal/handlers/health_handler.go:ReadinessCheck()` - GET /ready
- `backend/internal/handlers/health_handler.go:LivenessCheck()` - GET /live
- `backend/internal/handlers/health_canary.go` - Canary deployment health checks
- `backend/internal/health/checker.go`

**Tested in:**
- `src/tracertm/tests/api/test_health_router.py`
- `backend/internal/handlers/health_handler_test.go`

**Constraints:**
- SHALL check database connectivity
- SHALL check Redis connectivity
- SHALL check NATS connectivity
- SHALL return 200 if healthy, 503 if unhealthy

---

### FR-INFRA-008: Rate Limiting

**Traces to:** Security epics
**Description:** The system SHALL enforce rate limits per user and endpoint to prevent abuse and ensure fair usage.

**Input:**
- User ID
- Endpoint
- Request

**Output:**
- Allow/deny decision
- Rate limit headers (X-RateLimit-*)

**Implemented in:**
- `src/tracertm/api/config/rate_limiting.py`
- `backend/internal/ratelimit/limiter.go`

**Tested in:**
- `src/tracertm/tests/api/test_rate_limiting.py`

**Constraints:**
- SHALL limit API calls to 1000/hour per user
- SHALL limit expensive operations (exports) to 10/hour
- SHALL return 429 (Too Many Requests) when limit exceeded
- SHALL include rate limit headers in responses

---

### FR-INFRA-009: Logging

**Traces to:** Observability epics
**Description:** The system SHALL log all requests, errors, and significant events with structured logging and log aggregation.

**Input:**
- Log message
- Log level
- Context (user, request ID, etc.)

**Output:**
- Logged message (stdout, file, or aggregator)

**Implemented in:**
- `src/tracertm/logging_config.py`
- `backend/internal/logger/logger.go`

**Tested in:**
- `src/tracertm/tests/test_logging.py`

**Constraints:**
- SHALL use structured logging (JSON format)
- SHALL include request ID in all logs
- SHALL log errors with stack traces
- SHALL integrate with log aggregators (e.g., ELK, Datadog)

---

### FR-INFRA-010: Secrets Management

**Traces to:** Security epics
**Description:** The system SHALL store secrets (API keys, DB passwords) in Vault with support for rotation, access control, and audit logging.

**Input:**
- Secret key
- Optional TTL

**Output:**
- Secret value
- Audit log entry

**Implemented in:**
- `backend/internal/vault/client.go` - Vault client for Go backend
- `backend/internal/vault/secrets.go` - Secret management utilities
- `src/tracertm/vault/client.py` - Vault client for Python backend

**Tested in:**
- `backend/internal/vault/client_test.go`
- `src/tracertm/tests/vault/test_client.py`

**Constraints:**
- SHALL use HashiCorp Vault for secrets
- SHALL support secret rotation
- SHALL audit all secret access
- SHALL encrypt secrets at rest

---

## FR-MCP: MCP Server

### FR-MCP-001: MCP Server Initialization

**Traces to:** MCP architecture epics
**Description:** The system SHALL initialize the MCP server with tool registry, resource registry, and transport configuration.

**Input:**
- Server configuration (port, transport)
- Tool and resource definitions

**Output:**
- Running MCP server
- Health status

**Implemented in:**
- `src/tracertm/mcp/server.py`
- `src/tracertm/mcp/core.py`
- `src/tracertm/mcp/__main__.py`

**Tested in:**
- `src/tracertm/tests/mcp/test_server.py`

**Constraints:**
- SHALL support stdio and HTTP transports
- SHALL register all tools on startup
- SHALL register all resources on startup
- SHALL expose health check endpoint

---

### FR-MCP-002: Tool Registration

**Traces to:** MCP tool system epics
**Description:** The system SHALL dynamically register MCP tools with parameter schemas, descriptions, and handler functions.

**Input:**
- Tool definition (name, schema, handler)

**Output:**
- Registered tool
- Tool manifest entry

**Implemented in:**
- `src/tracertm/mcp/registry.py`
- `src/tracertm/mcp/tools/base.py`

**Tested in:**
- `src/tracertm/tests/mcp/test_registry.py`

**Constraints:**
- SHALL validate tool schemas (JSON Schema)
- SHALL prevent duplicate tool names
- SHALL support tool versioning
- SHALL generate tool manifest for clients

---

### FR-MCP-003: Resource System

**Traces to:** MCP resource system epics
**Description:** The system SHALL expose resources (schemas, templates, docs) via MCP for agent context augmentation.

**Input:**
- Resource URI
- Optional filters

**Output:**
- Resource content
- Resource metadata

**Implemented in:**
- `src/tracertm/mcp/resources/`
- `src/tracertm/mcp/registry.py:get_resource()`

**Tested in:**
- `src/tracertm/tests/mcp/test_resources.py`

**Constraints:**
- SHALL support file-based resources (Markdown, JSON, YAML)
- SHALL support dynamic resources (computed on-demand)
- SHALL cache resource content (5 min TTL)
- SHALL track resource access for analytics

---

### FR-MCP-004: Prompt Templates

**Traces to:** MCP prompt system epics
**Description:** The system SHALL provide prompt templates for common agent tasks with variable substitution and context injection.

**Input:**
- Template name
- Variables (key-value pairs)

**Output:**
- Rendered prompt
- Token count estimate

**Implemented in:**
- `src/tracertm/mcp/prompts/`
- `src/tracertm/mcp/tools/base.py:render_prompt()`

**Tested in:**
- `src/tracertm/tests/mcp/test_prompts.py`

**Constraints:**
- SHALL support Jinja2 template syntax
- SHALL inject system context automatically
- SHALL estimate token count before sending
- SHALL cache rendered prompts (1 min TTL)

---

### FR-MCP-005: Tool Execution Logging

**Traces to:** MCP observability epics
**Description:** The system SHALL log all tool executions with parameters, results, errors, and latency.

**Input:**
- Tool name
- Parameters
- Execution result

**Output:**
- Log entry
- Metrics update

**Implemented in:**
- `src/tracertm/mcp/middleware.py`
- `src/tracertm/mcp/metrics.py`

**Tested in:**
- `src/tracertm/tests/mcp/test_logging.py`

**Constraints:**
- SHALL log all tool calls (success and failure)
- SHALL record latency per tool
- SHALL track token usage per tool
- SHALL expose metrics via Prometheus

---

### FR-MCP-006: Error Handling

**Traces to:** MCP reliability epics
**Description:** The system SHALL handle tool errors gracefully with retry logic, error messages, and fallback strategies.

**Input:**
- Tool execution error

**Output:**
- Error message (structured)
- Retry attempt or fallback

**Implemented in:**
- `src/tracertm/mcp/error_handlers.py`
- `src/tracertm/mcp/tools/base.py:handle_error()`

**Tested in:**
- `src/tracertm/tests/mcp/test_error_handling.py`

**Constraints:**
- SHALL retry transient errors (network, timeout)
- SHALL NOT retry validation errors
- SHALL log all errors with context
- SHALL return structured error messages

---

### FR-MCP-007: Streaming Responses

**Traces to:** MCP streaming epics
**Description:** The system SHALL support streaming responses for long-running tools to provide incremental results.

**Input:**
- Tool call (streaming enabled)

**Output:**
- Streaming response (SSE or WebSocket)

**Implemented in:**
- `src/tracertm/mcp/tools/streaming.py`
- `src/tracertm/mcp/http_transport.py`

**Tested in:**
- `src/tracertm/tests/mcp/test_streaming.py`

**Constraints:**
- SHALL support Server-Sent Events (SSE)
- SHALL support WebSocket for bidirectional streaming
- SHALL send progress updates every 1 second
- SHALL handle client disconnects gracefully

---

### FR-MCP-008: Tool Optimization

**Traces to:** MCP performance epics
**Description:** The system SHALL optimize tool responses by compressing payloads, batching requests, and caching results.

**Input:**
- Tool call
- Optimization flags

**Output:**
- Optimized response
- Performance metrics

**Implemented in:**
- `src/tracertm/mcp/tools/response_optimizer.py`
- `src/tracertm/mcp/query_optimizer.py`

**Tested in:**
- `src/tracertm/tests/mcp/test_optimization.py`

**Constraints:**
- SHALL compress responses >1KB (gzip)
- SHALL batch database queries where possible
- SHALL cache identical tool calls (5 min TTL)
- SHALL limit response size (max 100KB per tool call)

---

### FR-MCP-009: Tool Discovery

**Traces to:** MCP tool system epics
**Description:** The system SHALL expose tool discovery endpoints for clients to query available tools, schemas, and capabilities.

**Input:**
- Optional filter (category, name pattern)

**Output:**
- Tool manifest (list of tools)
- Tool schemas

**Implemented in:**
- `src/tracertm/mcp/server.py:list_tools()`
- `GET /mcp/tools`

**Tested in:**
- `src/tracertm/tests/mcp/test_discovery.py`

**Constraints:**
- SHALL return all tools matching filter
- SHALL include parameter schemas (JSON Schema)
- SHALL include tool descriptions and examples
- SHALL version tool schemas

---

### FR-MCP-010: MCP Metrics

**Traces to:** MCP observability epics
**Description:** The system SHALL expose metrics for MCP server performance, tool usage, and error rates.

**Input:**
- Metric query (optional filters)

**Output:**
- Metrics (Prometheus format)

**Implemented in:**
- `src/tracertm/mcp/metrics.py`
- `src/tracertm/mcp/metrics_endpoint.py`
- `GET /mcp/metrics`

**Tested in:**
- `src/tracertm/tests/mcp/test_metrics.py`

**Constraints:**
- SHALL track tool call counts, latency, errors
- SHALL track token usage per tool
- SHALL expose metrics in Prometheus format
- SHALL integrate with Grafana for visualization

---

## Summary

This Functional Requirements Specification defines 142 requirements across 9 categories covering all major features of TraceRTM. Each requirement traces to implementation locations and test files, providing a comprehensive blueprint for development and verification.

### Coverage by Category

| Category | Requirements | Implementation Coverage |
|----------|--------------|------------------------|
| FR-DISC | 10 | ✓ Services, API, Tests |
| FR-QUAL | 10 | ✓ Services, API, Tests |
| FR-APP | 10 | ✓ Services, API, Tests |
| FR-VERIF | 10 | ✓ Services, API, Tests |
| FR-RPT | 10 | ✓ Services, API, Tests |
| FR-COLLAB | 10 | ✓ Services, API, Tests |
| FR-AI | 10 | ✓ Services, API, Tests |
| FR-INFRA | 10 | ✓ Services, Go, Tests |
| FR-MCP | 10 | ✓ MCP Server, Tests |
| **Total** | **142** | **100%** |

### Next Steps

1. ~~Map Go backend API endpoints to requirements~~ ✓ **COMPLETED**
2. Create FR-to-Test matrix for coverage tracking
3. Add requirement priorities (P0, P1, P2)
4. Link requirements to PRD epics and user stories
5. Generate traceability matrix (FR → Implementation → Tests)

---

## Go Backend Implementation Summary

The following table shows comprehensive Go backend implementation coverage across functional requirements:

### Graph & Analysis Operations (FR-QUAL)

| Requirement | Go Handler | REST Endpoint | gRPC Service |
|-------------|-----------|---------------|--------------|
| FR-QUAL-002 (Cycle Detection) | `graph_handler.go`, `graph_analysis_handler.go` | GET /api/v1/graph/cycles | GraphService.FindCycles |
| FR-QUAL-003 (Critical Path) | `graph_handler.go` | GET /api/v1/graph/impact-paths/:id | - |
| FR-QUAL-004 (Impact Analysis) | `graph_handler.go`, `traceability_handler.go` | GET /api/v1/graph/impact/:id | GraphService.AnalyzeImpact |
| FR-QUAL-005 (Coverage) | `traceability_handler.go` | GET /api/v1/traceability/coverage/:project_id | - |
| FR-QUAL-006 (Dependencies) | `graph_handler.go` | GET /api/v1/graph/ancestors/:id, /descendants/:id | - |
| FR-QUAL-007 (Matrix) | `traceability_handler.go` | GET /api/v1/traceability/matrix/:project_id | - |
| FR-QUAL-008 (Shortest Path) | `graph_handler.go`, `graph_analysis_handler.go` | GET /api/v1/graph/path | GraphService.CalculatePath |
| FR-QUAL-009 (Validation) | `graph_handler.go`, `traceability_handler.go` | GET /api/v1/graph/orphans | - |
| FR-QUAL-010 (Spec Analytics) | `spec_analytics_handler.go` | POST /api/v1/spec-analytics/analyze | - |

**Coverage:** 9/10 FRs implemented in Go (90%)

### Core Application (FR-APP)

| Requirement | Go Handler | REST Endpoint |
|-------------|-----------|---------------|
| FR-APP-001 (Item CRUD) | `item_handler.go` | GET/POST/PUT/DELETE /api/v1/items |
| FR-APP-002 (Link Management) | `link_handler.go` | GET/POST/DELETE /api/v1/links |
| FR-APP-004 (Search) | `search_handler.go` | GET/POST /api/v1/search |

**Coverage:** 3/10 FRs implemented in Go (30%)

### Collaboration & Real-time (FR-COLLAB)

| Requirement | Go Handler | Transport |
|-------------|-----------|-----------|
| FR-COLLAB-001 (Real-time Collaboration) | `websocket_handler.go`, `stream_handler.go`, `graph_stream_handler.go` | WebSocket, SSE, gRPC Streaming |
| FR-COLLAB-004 (Webhook Delivery) | `webhook_handler.go` | POST /api/v1/webhooks/:integration_type |

**Coverage:** 2/10 FRs implemented in Go (20%)

### Infrastructure (FR-INFRA)

| Requirement | Go Component | Endpoint/Service |
|-------------|--------------|------------------|
| FR-INFRA-001 (Authentication) | `auth_handler.go`, `auth/workos_provider.go` | POST /api/v1/auth/login |
| FR-INFRA-002 (Authorization) | `auth/middleware.go`, `auth/rbac.go` | Middleware |
| FR-INFRA-004 (Caching) | `cache/redis.go`, `cache/memory.go` | Service Layer |
| FR-INFRA-005 (File Storage) | `storage_handler.go`, `storage/s3.go` | GET/POST /api/v1/storage |
| FR-INFRA-006 (Event Bus) | `nats/publisher.go`, `nats/subscriber.go` | NATS |
| FR-INFRA-007 (Health Checks) | `health_handler.go`, `health_canary.go` | GET /health, /ready, /live |
| FR-INFRA-009 (Logging) | `logger/logger.go` | Structured logging |
| FR-INFRA-010 (Secrets) | `vault/client.go`, `vault/secrets.go` | Vault integration |

**Coverage:** 8/10 FRs implemented in Go (80%)

### Reporting (FR-RPT)

| Requirement | Go Handler | Endpoint |
|-------------|-----------|----------|
| FR-RPT-002 (Export Excel) | `stream_handler.go` | GET /api/v1/export/:type/stream |
| FR-RPT-006 (Metrics) | `metrics/collector.go` | GET /metrics |

**Coverage:** 2/10 FRs implemented in Go (20%)

### Overall Go Backend Statistics

- **Total Go REST Endpoints:** 65+
- **Total gRPC Services:** 3 (AnalyzeImpact, FindCycles, CalculatePath)
- **WebSocket/SSE Streams:** 5+ streaming endpoints
- **Handler Files:** 25+ (excluding tests)
- **Service Layer Files:** 25+
- **Requirements with Go Implementation:** 24/142 (17%)
- **Critical Performance Paths:** Graph operations, real-time collaboration, file storage

### Performance-Optimized Operations in Go

The Go backend handles performance-critical operations:

1. **Graph Traversal** - BFS/DFS algorithms for large graphs (10,000+ nodes)
2. **Real-time Streaming** - WebSocket, SSE, gRPC streaming for live updates
3. **Concurrent Operations** - Parallel impact analysis, bulk operations
4. **Cache Management** - Redis-backed caching with TTL and invalidation
5. **File Storage** - S3 operations with presigned URLs
6. **Event Processing** - NATS pub/sub for distributed events
7. **Health Monitoring** - Sub-millisecond health checks with dependency status

### Go-Python Hybrid Architecture

The system uses a **hybrid architecture** where:

- **Go Backend:** Performance-critical paths (graph, real-time, storage, auth)
- **Python Backend:** Business logic, AI/ML, integrations, workflows
- **Shared:** PostgreSQL database, Redis cache, NATS event bus
- **Communication:** REST APIs, gRPC for internal services, shared database

---

**End of Document**

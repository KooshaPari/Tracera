# Routes Index - Complete Reference

## Route Registration Status

All 68 routes are properly registered and accessible. This document provides a complete reference guide for developers.

## Root Route

### File: `src/routes/__root.tsx`

- **Path:** `/`
- **Component:** Root layout with navigation
- **Purpose:** Application shell, wraps all routes
- **Key Features:**
  - Global navigation (sidebar, header)
  - Authentication state management
  - Theme provider
  - Error boundary

---

## Authentication Routes

### File: `src/routes/auth.login.tsx`

- **Path:** `/auth/login`
- **Component:** LoginPage
- **Purpose:** User login
- **Authentication:** Public (no auth required)
- **Related:** WorkOS AuthKit integration

### File: `src/routes/auth.register.tsx`

- **Path:** `/auth/register`
- **Component:** RegisterPage
- **Purpose:** User registration
- **Authentication:** Public (no auth required)

### File: `src/routes/auth.reset-password.tsx`

- **Path:** `/auth/reset-password`
- **Component:** ResetPasswordPage
- **Purpose:** Password recovery
- **Authentication:** Public (no auth required)

### File: `src/routes/auth.callback.tsx`

- **Path:** `/auth/callback`
- **Component:** AuthCallbackPage
- **Purpose:** OAuth provider callback
- **Authentication:** Public
- **Related:** WorkOS OAuth flow

### File: `src/routes/auth.logout.tsx`

- **Path:** `/auth/logout`
- **Component:** LogoutPage
- **Purpose:** User logout handler
- **Authentication:** Protected
- **Behavior:** Clears auth state and redirects to login

---

## Main Dashboard Routes

### File: `src/routes/index.tsx`

- **Path:** `/`
- **Component:** IndexPage / HomePage
- **Purpose:** Default landing page
- **Authentication:** Protected (redirects to login if not authenticated)

### File: `src/routes/projects.index.tsx`

- **Path:** `/projects`
- **Component:** ProjectsListView
- **Purpose:** List all projects
- **Features:** Create, filter, search projects

### File: `src/routes/items.index.tsx`

- **Path:** `/items`
- **Component:** ItemsView
- **Purpose:** List all items (requirements, features, etc.)
- **Features:** Multiple view modes (table, kanban, tree)

### File: `src/routes/items.tree.tsx`

- **Path:** `/items/tree`
- **Component:** ItemsTreeView
- **Purpose:** Tree view of items with hierarchy
- **Features:** Hierarchical display, expand/collapse

### File: `src/routes/items.kanban.tsx`

- **Path:** `/items/kanban`
- **Component:** ItemsKanbanView
- **Purpose:** Kanban board view of items
- **Features:** Drag-and-drop, status columns

### File: `src/routes/links.index.tsx`

- **Path:** `/links`
- **Component:** LinksView
- **Purpose:** Display relationships between items
- **Features:** Link creation, management, visualization

### File: `src/routes/graph.index.tsx`

- **Path:** `/graph`
- **Component:** GraphView
- **Purpose:** Interactive graph visualization
- **Features:** Node/edge display, layout algorithms, search

### File: `src/routes/search.index.tsx`

- **Path:** `/search`
- **Component:** SearchView
- **Purpose:** Cross-perspective search
- **Features:** Semantic search, filters, suggestions

### File: `src/routes/reports.index.tsx`

- **Path:** `/reports`
- **Component:** ReportsView
- **Purpose:** Reports and analytics
- **Features:** Custom report generation, export

### File: `src/routes/settings.index.tsx`

- **Path:** `/settings`
- **Component:** SettingsView
- **Purpose:** User and application settings
- **Features:** Preferences, integrations, workspace config

---

## Matrix & Analysis Routes

### File: `src/routes/matrix.index.tsx`

- **Path:** `/matrix`
- **Component:** TraceabilityMatrixView
- **Purpose:** Traceability matrix homepage
- **Features:** Matrix visualization, navigation

### File: `src/routes/matrix.traceability.index.tsx`

- **Path:** `/matrix/traceability`
- **Component:** TraceabilityMatrixDetailView
- **Purpose:** Detailed traceability analysis
- **Features:** Coverage analysis, gap analysis

### File: `src/routes/impact.index.tsx`

- **Path:** `/impact`
- **Component:** ImpactAnalysisView
- **Purpose:** Impact analysis homepage
- **Features:** Navigation, overview

### File: `src/routes/impact.analysis.index.tsx`

- **Path:** `/impact/analysis`
- **Component:** ImpactAnalysisDetailView
- **Purpose:** Detailed impact analysis
- **Features:** Dependency analysis, scope assessment

### File: `src/routes/events.index.tsx`

- **Path:** `/events`
- **Component:** EventsTimelineView
- **Purpose:** Event timeline
- **Features:** Timeline visualization, filtering

### File: `src/routes/events.timeline.index.tsx`

- **Path:** `/events/timeline`
- **Component:** EventsTimelineDetailView
- **Purpose:** Detailed event timeline
- **Features:** Chronological view, annotations

---

## Project Routes

### File: `src/routes/projects.$projectId.tsx`

- **Path:** `/projects/:projectId`
- **Params:** `projectId` (UUID)
- **Component:** ProjectDetailView
- **Purpose:** Project overview/dashboard
- **Features:** Project info, stats, navigation
- **Children:** All project-specific routes

### File: `src/routes/projects.$projectId.agents.tsx`

- **Path:** `/projects/:projectId/agents`
- **Params:** `projectId`
- **Component:** AgentsView
- **Purpose:** AI agents for the project

### File: `src/routes/projects.$projectId.compliance.tsx`

- **Path:** `/projects/:projectId/compliance`
- **Params:** `projectId`
- **Component:** ComplianceView
- **Purpose:** Compliance tracking

### File: `src/routes/projects.$projectId.contracts.tsx`

- **Path:** `/projects/:projectId/contracts`
- **Params:** `projectId`
- **Component:** ContractsView
- **Purpose:** List project contracts

### File: `src/routes/projects.$projectId.contracts.$contractId.tsx`

- **Path:** `/projects/:projectId/contracts/:contractId`
- **Params:** `projectId`, `contractId`
- **Component:** ContractDetailView
- **Purpose:** Contract detail/editing

### File: `src/routes/projects.$projectId.specifications.tsx`

- **Path:** `/projects/:projectId/specifications`
- **Params:** `projectId`
- **Component:** SpecificationsView
- **Purpose:** Project specifications

### File: `src/routes/projects.$projectId.settings.tsx`

- **Path:** `/projects/:projectId/settings`
- **Params:** `projectId`
- **Component:** ProjectSettingsView
- **Purpose:** Project configuration

### File: `src/routes/projects.$projectId.adrs.tsx`

- **Path:** `/projects/:projectId/adrs`
- **Params:** `projectId`
- **Component:** ADRsView
- **Purpose:** Architecture decision records

### File: `src/routes/projects.$projectId.adrs.$adrId.tsx`

- **Path:** `/projects/:projectId/adrs/:adrId`
- **Params:** `projectId`, `adrId`
- **Component:** ADRDetailView
- **Purpose:** ADR detail/editing

### File: `src/routes/projects.$projectId.features.tsx`

- **Path:** `/projects/:projectId/features`
- **Params:** `projectId`
- **Component:** FeaturesView
- **Purpose:** List project features

### File: `src/routes/projects.$projectId.features.$featureId.tsx`

- **Path:** `/projects/:projectId/features/:featureId`
- **Params:** `projectId`, `featureId`
- **Component:** FeatureDetailView
- **Purpose:** Feature detail/editing

---

## Project View Routes

### Base View Route

**File:** `src/routes/projects.$projectId.views.$viewType.tsx`

- **Path:** `/projects/:projectId/views/:viewType`
- **Params:** `projectId`, `viewType`
- **Component:** EnhancedGraphView or view-type-specific component
- **Purpose:** Dynamic view based on type

**File:** `src/routes/projects.$projectId.views.$viewType.$itemId.tsx`

- **Path:** `/projects/:projectId/views/:viewType/:itemId`
- **Params:** `projectId`, `viewType`, `itemId`
- **Component:** ItemDetailView in context
- **Purpose:** Item detail within a specific view

### Specialized View Routes

#### Architecture & Design

**File:** `src/routes/projects.$projectId.views.architecture.tsx`

- **Path:** `/projects/:projectId/views/architecture`
- **Component:** ArchitectureView
- **Features:** System architecture visualization

**File:** `src/routes/projects.$projectId.views.wireframe.tsx`

- **Path:** `/projects/:projectId/views/wireframe`
- **Component:** WireframeView
- **Features:** UI wireframes, mockups

**File:** `src/routes/projects.$projectId.views.domain.tsx`

- **Path:** `/projects/:projectId/views/domain`
- **Component:** DomainView
- **Features:** Domain model visualization

#### Development

**File:** `src/routes/projects.$projectId.views.code.tsx`

- **Path:** `/projects/:projectId/views/code`
- **Component:** CodeView
- **Features:** Code exploration, repository integration

**File:** `src/routes/projects.$projectId.views.api.tsx`

- **Path:** `/projects/:projectId/views/api`
- **Component:** ApiView
- **Features:** API documentation, endpoints

**File:** `src/routes/projects.$projectId.views.database.tsx`

- **Path:** `/projects/:projectId/views/database`
- **Component:** DatabaseView
- **Features:** Database schema, tables

#### Testing & Quality

**File:** `src/routes/projects.$projectId.views.test.tsx`

- **Path:** `/projects/:projectId/views/test`
- **Component:** TestView
- **Features:** Test overview, management

**File:** `src/routes/projects.$projectId.views.test-cases.tsx`

- **Path:** `/projects/:projectId/views/test-cases`
- **Component:** TestCasesView
- **Features:** Test case management

**File:** `src/routes/projects.$projectId.views.test-runs.tsx`

- **Path:** `/projects/:projectId/views/test-runs`
- **Component:** TestRunsView
- **Features:** Test execution history

**File:** `src/routes/projects.$projectId.views.test-suites.tsx`

- **Path:** `/projects/:projectId/views/test-suites`
- **Component:** TestSuitesView
- **Features:** Test suite organization

**File:** `src/routes/projects.$projectId.views.qa-dashboard.tsx`

- **Path:** `/projects/:projectId/views/qa-dashboard`
- **Component:** QADashboardView
- **Features:** QA metrics and status

**File:** `src/routes/projects.$projectId.views.coverage.tsx`

- **Path:** `/projects/:projectId/views/coverage`
- **Component:** CoverageView
- **Features:** Test coverage analysis

#### Operations

**File:** `src/routes/projects.$projectId.views.infrastructure.tsx`

- **Path:** `/projects/:projectId/views/infrastructure`
- **Component:** InfrastructureView
- **Features:** Infrastructure topology, deployment

**File:** `src/routes/projects.$projectId.views.configuration.tsx`

- **Path:** `/projects/:projectId/views/configuration`
- **Component:** ConfigurationView
- **Features:** Environment config, settings

**File:** `src/routes/projects.$projectId.views.monitoring.tsx`

- **Path:** `/projects/:projectId/views/monitoring`
- **Component:** MonitoringView
- **Features:** System monitoring, metrics

**File:** `src/routes/projects.$projectId.views.webhooks.tsx`

- **Path:** `/projects/:projectId/views/webhooks`
- **Component:** WebhooksView
- **Features:** Webhook configuration, logs

**File:** `src/routes/projects.$projectId.views.integrations.tsx`

- **Path:** `/projects/:projectId/views/integrations`
- **Component:** IntegrationsView
- **Features:** Third-party integrations

#### Analysis

**File:** `src/routes/projects.$projectId.views.performance.tsx`

- **Path:** `/projects/:projectId/views/performance`
- **Component:** PerformanceView
- **Features:** Performance metrics, profiling

**File:** `src/routes/projects.$projectId.views.security.tsx`

- **Path:** `/projects/:projectId/views/security`
- **Component:** SecurityView
- **Features:** Security analysis, vulnerabilities

**File:** `src/routes/projects.$projectId.views.dependency.tsx`

- **Path:** `/projects/:projectId/views/dependency`
- **Component:** DependencyView
- **Features:** Dependency graph, analysis

**File:** `src/routes/projects.$projectId.views.dataflow.tsx`

- **Path:** `/projects/:projectId/views/dataflow`
- **Component:** DataflowView
- **Features:** Data flow visualization

**File:** `src/routes/projects.$projectId.views.journey.tsx`

- **Path:** `/projects/:projectId/views/journey`
- **Component:** JourneyView
- **Features:** User journey mapping

**File:** `src/routes/projects.$projectId.views.problem.tsx`

- **Path:** `/projects/:projectId/views/problem`
- **Component:** ProblemView
- **Features:** Problem statement, scope

**File:** `src/routes/projects.$projectId.views.process.tsx`

- **Path:** `/projects/:projectId/views/process`
- **Component:** ProcessView
- **Features:** Process documentation, flow

---

## Item Routes

### File: `src/routes/items.$itemId.tsx`

- **Path:** `/items/:itemId`
- **Params:** `itemId`
- **Component:** ItemDetailView
- **Purpose:** Item detail/editing (cross-project)

---

## Integration Routes

### File: `src/routes/integrations.callback.tsx`

- **Path:** `/integrations/callback`
- **Purpose:** Third-party integration callback
- **Authentication:** Public
- **Features:** OAuth flow for integrations

---

## API Documentation Routes

### File: `src/routes/api-docs.index.tsx`

- **Path:** `/api-docs`
- **Component:** ApiDocsPage
- **Purpose:** API documentation home

### File: `src/routes/api-docs.swagger.tsx`

- **Path:** `/api-docs/swagger`
- **Component:** SwaggerUI
- **Purpose:** Interactive API documentation (Swagger)
- **Features:** Try-it-out, request/response examples

### File: `src/routes/api-docs.redoc.tsx`

- **Path:** `/api-docs/redoc`
- **Component:** ReDocUI
- **Purpose:** Read-only API documentation (ReDoc)
- **Features:** Clean, developer-friendly layout

---

## API Routes (Non-UI)

### File: `src/routes/api/spec.tsx`

- **Path:** `/api/spec`
- **Purpose:** OpenAPI specification
- **Content-Type:** application/json
- **Returns:** OpenAPI 3.0 specification

### File: `src/routes/api/auth-test.tsx`

- **Path:** `/api/auth-test`
- **Purpose:** Authentication test endpoint
- **Authentication:** Protected
- **Returns:** Current user info

### File: `src/routes/api/swagger-config.tsx`

- **Path:** `/api/swagger-config`
- **Purpose:** Swagger UI configuration
- **Returns:** Swagger configuration object

---

## Route Usage Patterns

### Protected Routes

All routes except auth routes require authentication. When user is not authenticated:

1. Route redirects to `/auth/login`
2. After login, user is redirected back to requested route
3. Uses `beforeLoad` hook for authentication check

```tsx
export const Route = createFileRoute('/projects')({
  beforeLoad: async ({ location }) => {
    const isAuthenticated = /* check auth */
    if (!isAuthenticated) {
      throw redirect({
        to: '/auth/login',
        search: { redirect: location.href }
      })
    }
  },
  component: ProjectsListView,
})
```

### Dynamic Routes

Parameters are passed via URL and accessed with `Route.useParams()`:

```tsx
function FeatureDetailPage() {
  const { projectId, featureId } = Route.useParams();
  const { data } = useQuery({
    queryKey: [projectId, featureId],
    queryFn: () => api.features.get(featureId),
  });
  return <FeatureDetailView feature={data} />;
}
```

### Search Parameters

Query strings are accessed with `Route.useSearch()`:

```tsx
function SearchPage() {
  const { q, type } = Route.useSearch();
  return <SearchResults query={q} type={type} />;
}
```

### Navigation

Type-safe navigation using `Link` and `useNavigate()`:

```tsx
// Link component
<Link to='/projects/$projectId' params={{ projectId: '123' }}>
  View Project
</Link>;

// Programmatic navigation
const navigate = useNavigate();
navigate({ to: '/projects/$projectId', params: { projectId: '123' } });
```

---

## Future Routes

Reserved paths for future implementation:

- `/admin/*` - Admin dashboard
- `/profile/*` - User profile
- `/help/*` - Help and documentation
- `/templates/*` - Project templates
- `/export/*` - Export functionality
- `/import/*` - Import functionality

---

## Migration Notes

When moving routes:

1. Keep file name synchronized with URL path
2. Update route parameter prefixes (use `$`)
3. Regenerate route tree: `bunx @tanstack/router-cli@latest generate`
4. Test navigation with `bun run dev`
5. Update documentation
6. No production impact (file-based routing is automatic)

---

**Last Updated:** 2026-01-29
**Routing Framework:** TanStack Router v1.157.16
**File Convention:** Kebab-case with `$` prefix for parameters

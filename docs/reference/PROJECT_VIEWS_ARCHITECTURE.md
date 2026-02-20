# Project Views Architecture

**Summary:** Many project view pages use a **generic item registry** (`ItemsTableView` filtered by type). A smaller set use **domain-optimized** components. This is **by design**, not a bug.

## Generic item-registry views (ItemsTableView)

These routes render the same table component with a different `view` prop (filter by item type). Same UI, different data slice:

| View route | `view` prop | Notes |
|------------|-------------|--------|
| `/projects/:id/views/domain` | `domain` | No custom title |
| `/projects/:id/views/code` | `code` | Title: "Code" |
| `/projects/:id/views/test` | `test` | Title: "Tests" |
| `/projects/:id/views/database` | `database` | Title: "Database" |
| `/projects/:id/views/wireframe` | `wireframe` | Title: "Wireframes" |
| `/projects/:id/views/architecture` | `architecture` | |
| `/projects/:id/views/infrastructure` | `infrastructure` | |
| `/projects/:id/views/dataflow` | `dataflow` | |
| `/projects/:id/views/dependency` | `dependency` | |
| `/projects/:id/views/security` | `security` | |
| `/projects/:id/views/performance` | `performance` | |
| `/projects/:id/views/monitoring` | `monitoring` | |
| `/projects/:id/views/journey` | `journey` | |
| `/projects/:id/views/configuration` | `configuration` | |

**Component:** `@/views/ItemsTableView` (header text "Item Registry" in UI).

## Domain-optimized views (custom components)

These routes render dedicated pages with domain-specific UI, forms, and workflows:

| View route | Component | Location |
|------------|-----------|----------|
| `/projects/:id/views/feature` | `FeatureView` | `pages/projects/views/FeatureView.tsx` (epic/feature hierarchy, real data) |
| `/projects/:id/views/api` | `ApiView` | `pages/projects/views/ApiView.tsx` (project API items + reference) |
| `/projects/:id/views/test-cases` | `TestCaseView` | `pages/projects/views/TestCaseView.tsx` |
| `/projects/:id/views/test-runs` | `TestRunView` | `pages/projects/views/TestRunView.tsx` |
| `/projects/:id/views/test-suites` | `TestSuiteView` | `pages/projects/views/TestSuiteView.tsx` |
| `/projects/:id/views/coverage` | `CoverageMatrixView` | `pages/projects/views/CoverageMatrixView.tsx` |
| `/projects/:id/views/qa-dashboard` | `QADashboardView` | `pages/projects/views/QADashboardView.tsx` |
| `/projects/:id/views/problem` | `ProblemView` | `pages/projects/views/ProblemView.tsx` |
| `/projects/:id/views/process` | `ProcessView` | `pages/projects/views/ProcessView.tsx` |
| `/projects/:id/views/webhooks` | `WebhookIntegrationsView` | `pages/projects/views/WebhookIntegrationsView.tsx` |
| `/projects/:id/views/graph` | `GraphView` | `pages/projects/views/GraphView.tsx` |
| `/projects/:id/views/integrations` | `IntegrationsView` | `pages/projects/views/IntegrationsView.tsx` |
| `/projects/:id/views/impact-analysis` | `ImpactAnalysisView` | `views/ImpactAnalysisView.tsx` |
| `/projects/:id/views/traceability` | `TraceabilityMatrixView` | `views/TraceabilityMatrixView.tsx` |
| `/projects/:id/views/workflows` | `WorkflowRunsView` | `pages/projects/views/WorkflowRunsView.tsx` |

## Project dashboard (root)

`/projects/:id` (no sub-path) renders **ProjectDetailView** — a custom dashboard with charts, stats, and links to views (not the item registry).

## Making more views domain-optimized

To turn a generic view (e.g. Domain, Code, Database) into a domain-optimized one:

1. Add a new component under `frontend/apps/web/src/pages/projects/views/` (e.g. `DomainView.tsx` with entities/relationships, custom filters, create flows).
2. In the per-view route file (e.g. `projects.$projectId.views.domain.tsx`), import the page component and export a wrapper that gets `projectId` from `useParams` and renders it: `<DomainView projectId={projectId} />`.
3. The catch-all route `projects.$projectId.views.$viewType.tsx` imports `FEATURE_VIEW` / `API_VIEW` etc. from those route files and renders them in the switch (no props; the wrapper gets `projectId` from params).

**Feature** and **API** are now domain-optimized: `FeatureView` shows epic/feature hierarchy with real items and Add Epic/Add Feature; `ApiView` shows project API items (from items with view=api) plus a static Reference section.

## Modal and detail consistency

Create flows and item detail pages use **view-specific labels** so the UI reads like the current context (e.g. "Create Feature", "New Feature", "Feature Details"):

- **ItemsTableView**  
  `VIEW_LABELS` includes per-view `createModalTitle`, `createButtonLabel`, and `newButtonLabel`. The inline create modal and header/empty-state "New" button use these (e.g. "Create Feature", "New Feature" on the feature view).

- **CreateItemForm**  
  Optional `title`, `submitLabel`, and `submitBusyLabel` props (e.g. FeatureView passes "Create Feature").

- **Detail pages**  
  `DetailHeader` and `ItemDetailView` show a view/type prefix line above the title (e.g. "Feature · epic"). `OverviewTab` uses a view-aware section heading (e.g. "Feature Details").

- **Create modals**  
  All create modals (TestRun, TestSuite, Process, Problem, Contract, ADR, Feature list, CreateItemForm, CreateTestCaseForm, CreateProcessForm, CreateProblemForm) use `role="dialog"`, `aria-modal="true"`, `aria-labelledby` on the title, and a close button with `aria-label="Close dialog"`.

- **ProjectDetailView**  
  The primary create action is labeled "New Feature" and navigates to the feature view with `?action=create`.

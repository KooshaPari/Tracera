# Specification Views Implementation Guide

## Overview

This document describes the comprehensive specification views system for managing architectural decisions, contracts, and BDD features in the application.

## Created Views

### 1. ADRListView.tsx

**Location**: `/src/views/ADRListView.tsx`

#### Purpose

Central management view for Architecture Decision Records (ADRs) with multiple visualization modes.

#### Features

- **Multiple View Modes**:
  - Cards View: Grid of ADR cards with compliance gauges
  - Timeline View: Chronological ADR progression
  - Graph View: Visual relationships between ADRs

- **Filtering & Search**:
  - Full-text search across title, number, and context
  - Status filtering (proposed, accepted, deprecated, superseded, rejected)
  - Date range filtering (week, month, quarter, all-time)

- **Quick Actions**:
  - Create new ADR modal with context, decision, and status fields
  - Status count badges for quick overview
  - Click to view detailed ADR

#### Props

```typescript
interface ADRListViewProps {
  projectId: string;
}
```

#### Usage

```tsx
import { ADRListView } from '@/views';

function MyComponent() {
  return <ADRListView projectId='proj-123' />;
}
```

#### Styling

- Uses `ItemsTableView` as pattern reference for consistency
- Rounded cards (xl) with subtle shadows
- Status-based color coding:
  - Proposed: Yellow
  - Accepted: Green
  - Deprecated: Gray
  - Superseded: Orange
  - Rejected: Red

---

### 2. ADRDetailView.tsx

**Location**: `/src/views/ADRDetailView.tsx`

#### Purpose

Detailed view of a single ADR with MADR (Markdown Architecture Decision Record) format support.

#### Features

- **MADR Format Sections**:
  - Context: Business and technical background
  - Decision: What was decided and why
  - Consequences: Trade-offs and implications
  - Considered Options: Alternative approaches evaluated

- **Edit Mode**:
  - Toggle between view and edit modes
  - Inline editing of all MADR sections
  - Save/Cancel actions with loading states

- **Sidebar Information**:
  - Compliance score gauge (0-100)
  - Decision drivers (tags)
  - Related requirements links
  - Version history timeline
  - Tag management
  - Supersedes/Superseded by relationships

- **Tabbed Content**:
  - MADR Format (default)
  - Decision Matrix: Visual comparison of considered options
  - Version History: Change timeline with authors

#### Props

```typescript
interface ADRDetailViewProps {
  adrId?: string; // Retrieved from route params if not provided
}
```

#### Usage

```tsx
import { ADRDetailView } from '@/views';

function MyComponent() {
  return <ADRDetailView adrId='adr-123' />;
}
```

#### Data Requirements

ADR object structure:

```typescript
interface ADR {
  id: string;
  projectId: string;
  adrNumber: string;
  title: string;
  status: 'proposed' | 'accepted' | 'deprecated' | 'superseded' | 'rejected';
  context: string;
  decision: string;
  consequences: string;
  date: string;
  tags: string[];
  complianceScore?: number;
  relatedRequirements?: string[];
  decisionDrivers?: string[];
  consideredOptions?: Option[];
  version: number;
}
```

---

### 3. ContractListView.tsx

**Location**: `/src/views/ContractListView.tsx`

#### Purpose

Overview and management of all contract specifications (API, function, invariant, data, integration).

#### Features

- **Verification Summary Cards**:
  - Total contracts count
  - Verified contracts count
  - Violated contracts count
  - Pass rate percentage

- **Filtering Options**:
  - Status: draft, active, verified, violated, deprecated
  - Type: API, function, invariant, data, integration
  - Search by title, number, or description

- **Contract Grid**:
  - Visual cards showing contract status
  - Condition counts (preconditions, postconditions, invariants)
  - State machine indicators
  - Verification status badges
  - Executable specification indicator

#### Props

```typescript
interface ContractListViewProps {
  projectId: string;
}
```

#### Components Used

- `ContractCard`: Display individual contracts
- `VerificationBadge`: Show verification status
- Custom status indicators

#### Color Coding

- Draft: Gray
- Active: Blue
- Verified: Green (with checkmark)
- Violated: Red (with warning icon)
- Deprecated: Orange

---

### 4. FeatureListView.tsx

**Location**: `/src/views/FeatureListView.tsx`

#### Purpose

Management of BDD (Behavior-Driven Development) features and their test scenarios.

#### Features

- **Scenario Summary Cards**:
  - Total scenarios count
  - Passing scenarios count
  - Failing scenarios count
  - Pending scenarios count
  - Overall pass rate percentage

- **Feature Cards**:
  - User story in formatted text
  - Scenario pass rate with visual progress
  - Status badges
  - Tag display

- **Filtering**:
  - Status: draft, active, deprecated, archived
  - Search by name or feature number

#### Props

```typescript
interface FeatureListViewProps {
  projectId: string;
}
```

#### Components Used

- `FeatureCard`: Individual feature display
- `Progress`: Visual pass rate indicator

---

### 5. FeatureDetailView2.tsx

**Location**: `/src/views/FeatureDetailView2.tsx`

#### Purpose

Comprehensive feature editing and scenario management with Gherkin support.

#### Features

- **Feature Header**:
  - Editable feature name
  - Status badges
  - Tag management
  - Feature metadata

- **Scenario Management**:
  - Create new scenarios (with modal dialog)
  - Edit scenario Gherkin text
  - Delete scenarios
  - Copy Gherkin to clipboard

- **Gherkin Support**:
  - `GherkinEditor`: Create/edit scenario text
  - `GherkinViewer`: Display formatted Gherkin
  - Syntax highlighting
  - Step parsing

- **Test Execution**:
  - Run all scenarios button
  - Execution statistics (passed/failed/pending)
  - Pass rate progress bar
  - Status visualization

- **Sidebar Stats**:
  - Execution summary
  - User story display
  - Feature description

#### Props

```typescript
interface FeatureDetailViewProps {
  featureId?: string; // Retrieved from route params if not provided
}
```

#### Gherkin Format Example

```gherkin
Scenario: Successful Login
  Given a user with email 'test@example.com' and password 'password123'
  When they click the login button
  Then they are redirected to the dashboard
  And their profile is displayed
```

---

### 6. SpecificationsDashboardView.tsx

**Location**: `/src/views/SpecificationsDashboardView.tsx`

#### Purpose

Unified dashboard providing an overview of all specification types (ADRs, contracts, features) with health metrics and gap analysis.

#### Features

- **Quick Navigation Cards**:
  - Architecture Decisions card (blue)
  - API Contracts card (green)
  - BDD Features card (purple)
  - Click-through to detailed views

- **Main Dashboard Sections**:
  - Overall Health Score (ring gauge)
  - Coverage Heatmap: Visual representation of specification coverage
  - Gap Analysis: Automated detection of missing specifications
  - Health Details: Category breakdown with scores
  - Recent Activity: Timeline of specification changes

- **Metrics Calculated**:
  - ADR compliance average
  - Contract verification rate
  - Feature test pass rate
  - Overall health score (weighted average)
  - Gap priority levels (critical, high, medium, low)

- **Interactive Elements**:
  - Navigate to individual specification types
  - Create new ADRs or features
  - Click gaps to see details
  - Tab-based organization (Coverage, Gaps, Health, Activity)

#### Props

```typescript
interface SpecificationsDashboardViewProps {
  projectId: string;
}
```

#### Health Score Weights

```
- Architecture: 30%
- Contracts: 35%
- Features: 35%
```

#### Components Used

- `SpecificationDashboard`: Main dashboard component
- `ComplianceGauge`: Health visualization
- `CoverageHeatmap`: Coverage grid display
- `GapAnalysis`: Gap detection and display
- `HealthScoreRing`: Circular health visualization

---

## Routing Integration

### Suggested Route Structure

```typescript
// src/routes configuration

// ADR Routes
{
  path: "/specifications/adrs",
  component: ADRListView,
  params: { projectId: string }
}

{
  path: "/adr/:adrId",
  component: ADRDetailView
}

// Contract Routes
{
  path: "/specifications/contracts",
  component: ContractListView,
  params: { projectId: string }
}

{
  path: "/contract/:contractId",
  component: ContractDetailView
}

// Feature Routes
{
  path: "/specifications/features",
  component: FeatureListView,
  params: { projectId: string }
}

{
  path: "/feature/:featureId",
  component: FeatureDetailView2
}

// Dashboard Route
{
  path: "/specifications/dashboard",
  component: SpecificationsDashboardView,
  params: { projectId: string }
}
```

---

## Hook Dependencies

All views depend on the `useSpecifications` hook:

```typescript
// Available hooks from @/hooks/useSpecifications

export function useADRs(projectId: string);
export function useCreateADR();
export function useContracts(projectId: string);
export function useFeatures(projectId: string);
export function useQualityReport(projectId: string);
```

---

## Styling Patterns

### Color Scheme

- **Status Colors**: Consistent with ADRCard component
- **Summary Cards**: Gradient backgrounds (blue, green, purple, red, yellow)
- **Action Buttons**: Primary with shadow for CTAs
- **Filters**: Transparent background with icon indicators
- **Empty States**: Muted icons (40% opacity) with descriptive text

### Typography

- **Headers**: 2xl-3xl font-black uppercase
- **Titles**: text-lg font-semibold
- **Labels**: text-xs font-medium uppercase
- **Content**: text-sm text-muted-foreground

### Spacing

- **Main container**: p-6, max-w-[1600px]
- **Cards**: rounded-2xl or rounded-xl
- **Grid gap**: gap-4 or gap-6

---

## Implementation Checklist

When integrating these views:

- [ ] Install `useSpecifications` hooks
- [ ] Set up route handlers for all view paths
- [ ] Configure mock data or API endpoints
- [ ] Test all filtering combinations
- [ ] Verify create/edit/delete operations
- [ ] Test search functionality
- [ ] Validate sorting and pagination
- [ ] Test responsive behavior on mobile
- [ ] Verify accessibility (keyboard nav, ARIA labels)
- [ ] Test error states and loading skeletons

---

## Future Enhancements

1. **Bulk Operations**:
   - Bulk status updates
   - Bulk tagging
   - Batch compliance checks

2. **Advanced Analytics**:
   - Compliance trend charts
   - Test execution history
   - ADR adoption metrics

3. **Collaboration Features**:
   - Comments on ADRs
   - Review workflows
   - Change approvals

4. **Integration Features**:
   - GitHub sync for ADRs
   - JIRA task creation
   - Slack notifications

5. **Export Capabilities**:
   - PDF reports
   - Excel exports
   - HTML documentation generation

---

## Troubleshooting

### Empty Views

- Verify hooks are returning data
- Check API endpoints are configured
- Review mock data is loaded

### Filter Not Working

- Ensure searchParams are properly typed
- Check filter values are passed to hooks
- Verify data transformation in useMemo

### Modal Not Closing

- Verify state reset on success
- Check onClick handlers stop propagation
- Review modal z-index if overlapping

### Sorting Issues

- Ensure sort function handles all data types
- Verify date parsing for timestamp sorts
- Check null/undefined handling

---

## File Locations Summary

| View                        | Path                                         |
| --------------------------- | -------------------------------------------- |
| ADRListView                 | `/src/views/ADRListView.tsx`                 |
| ADRDetailView               | `/src/views/ADRDetailView.tsx`               |
| ContractListView            | `/src/views/ContractListView.tsx`            |
| FeatureListView             | `/src/views/FeatureListView.tsx`             |
| FeatureDetailView2          | `/src/views/FeatureDetailView2.tsx`          |
| SpecificationsDashboardView | `/src/views/SpecificationsDashboardView.tsx` |
| Exports                     | `/src/views/index.ts`                        |

---

## Contributing

When modifying these views:

1. Maintain consistent styling with existing patterns
2. Update TypeScript interfaces in `@tracertm/types`
3. Add comprehensive error handling
4. Include loading states for async operations
5. Test with mock data before connecting to real APIs
6. Document any new hooks or utilities
7. Ensure accessibility compliance

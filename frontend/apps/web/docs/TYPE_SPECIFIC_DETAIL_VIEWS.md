# Type-Specific Detail Views

## Overview

The detail view system provides specialized, type-aware components for displaying different item types. Each view is optimized for its specific data structure and use case.

## Architecture

```
ItemDetailRouter
├── RequirementDetailView (requirement items)
├── TestDetailView (test, test_case, test_suite)
├── EpicDetailView (epic items)
├── UserStoryDetailView (user_story, story) [Coming Soon]
├── TaskDetailView (task items) [Coming Soon]
├── DefectDetailView (bug, defect items) [Coming Soon]
└── ItemDetailView (fallback for other types)
```

## Available Detail Views

### 1. RequirementDetailView

**Item Types**: `requirement`

**Features**:
- EARS pattern visualization (trigger, precondition, postcondition)
- Quality metrics (verifiability, traceability, clarity)
- ISO 29148 compliance indicators
- Risk assessment and WSJF scoring
- Verification status tracking
- Constraint visualization

**Color Theme**: Purple (`#8b5cf6`)

**Tabs**:
1. Overview - Key metrics and status
2. EARS Pattern - Requirement syntax breakdown
3. Quality - ISO 29148 quality dimensions
4. Risk & Verification - Risk levels and verification evidence
5. Traceability - Upstream/downstream links
6. History - Change tracking and volatility

**Usage**:
```tsx
import { RequirementDetailView } from '@/views/details';

<RequirementDetailView item={requirementItem} projectId={projectId} />
```

---

### 2. TestDetailView

**Item Types**: `test`, `test_case`, `test_suite`

**Features**:
- Test execution metrics
- Flakiness tracking and quarantine status
- Coverage metrics (line, branch, mutation, MC/DC)
- Performance baselines and trends
- Safety level indicators (DO-178C compliance)
- Test dependency visualization

**Color Theme**: Green (`#10b981`)

**Tabs**:
1. Overview - Test summary and status
2. Test Spec - Configuration and framework details
3. Execution - Run history and results
4. Metrics - Coverage and performance data
5. Links - Requirement and contract traceability
6. History - Change log and version tracking

**Usage**:
```tsx
import { TestDetailView } from '@/views/details';

<TestDetailView item={testItem} projectId={projectId} />
```

**Special Features**:
- Quarantine warning banner
- Flakiness score visualization
- Safety-critical test indicators
- Expected vs actual result comparison

---

### 3. EpicDetailView

**Item Types**: `epic`

**Features**:
- Business value tracking
- Timeline and milestone visualization
- Story breakdown and completion tracking
- Success criteria checklist
- Risk assessment with mitigation strategies
- Stakeholder management

**Color Theme**: Deep Purple (`#7c3aed`)

**Tabs**:
1. Overview - Business value, stories, completion
2. Epic Specification - Objectives, scope, constraints
3. Timeline - Start/end dates, progress tracking
4. Stories - User story links and themes
5. Acceptance Criteria - Success criteria and risks

**Usage**:
```tsx
import { EpicDetailView } from '@/views/details';

<EpicDetailView item={epicItem} projectId={projectId} />
```

**Special Features**:
- Timeline progress bar
- Story completion percentage
- Out-of-scope items tracking
- Assumptions and constraints visualization

---

## Router Component

### ItemDetailRouter

The router component automatically selects the correct detail view based on item type using TypeScript type guards.

**Location**: `/frontend/apps/web/src/views/details/ItemDetailRouter.tsx`

**Type Guards Used**:
- `isRequirementItem(item)` → RequirementDetailView
- `isTestItem(item)` → TestDetailView
- `isEpicItem(item)` → EpicDetailView
- `isUserStoryItem(item)` → [Coming Soon]
- `isTaskItem(item)` → [Coming Soon]
- `isDefectItem(item)` → [Coming Soon]
- Fallback → ItemDetailView

**Usage**:
```tsx
import { ItemDetailRouter } from '@/views/details';

<ItemDetailRouter item={item} projectId={projectId} />
```

**Route Integration**:
```tsx
// In route file: projects.$projectId.views.$viewType.$itemId.tsx
import { ItemDetailRouter } from '@/views/details';
import { useItem } from '@/hooks/useItems';

function ItemDetailComponent() {
  const { projectId, itemId } = useParams({ strict: false });
  const { data: item } = useItem(projectId, itemId);

  return <ItemDetailRouter item={item} projectId={projectId} />;
}
```

---

## BaseDetailView Component

All detail views use `BaseDetailView` for consistent layout and behavior.

**Features**:
- Responsive header with breadcrumbs
- Tab navigation with badges
- Action toolbar
- Mobile-optimized layout
- Gradient backgrounds
- Loading states

**Props**:
```typescript
interface BaseDetailViewProps {
  item: TypedItem;              // Item being displayed
  tabs: DetailTab[];            // Tab configurations
  defaultTab?: string;          // Initial tab
  actions?: DetailAction[];     // Header actions
  headerContent?: ReactNode;    // Additional header content
  footerContent?: ReactNode;    // Additional footer content
  onBack?: () => void;          // Back navigation handler
  className?: string;           // Custom classes
  isLoading?: boolean;          // Loading state
}
```

**DetailTab Structure**:
```typescript
interface DetailTab {
  id: string;                   // Unique identifier
  label: string;                // Tab label
  content: ReactNode;           // Tab content
  badge?: string | number;      // Optional badge
  ariaLabel?: string;           // Accessibility label
}
```

---

## Creating a New Detail View

### Step 1: Create the Component

```tsx
// frontend/apps/web/src/views/details/UserStoryDetailView.tsx
import { isUserStoryItem, type UserStoryItem } from "@tracertm/types";
import { BaseDetailView, type DetailTab } from "./BaseDetailView";
import { useUserStorySpecByItem } from "@/hooks/useItemSpecs";

interface UserStoryDetailViewProps {
  item: UserStoryItem;
  projectId: string;
}

export function UserStoryDetailView({ item, projectId }: UserStoryDetailViewProps) {
  // Type guard check
  if (!isUserStoryItem(item)) {
    return <ErrorCard message="Not a user story" />;
  }

  // Fetch spec data
  const { data: spec, isLoading } = useUserStorySpecByItem(projectId, item.id);

  // Define tabs
  const tabs: DetailTab[] = [
    {
      id: "overview",
      label: "Overview",
      content: <OverviewContent item={item} spec={spec} />,
    },
    // ... more tabs
  ];

  return (
    <BaseDetailView
      item={item}
      tabs={tabs}
      defaultTab="overview"
      isLoading={isLoading}
    />
  );
}
```

### Step 2: Add to Router

```tsx
// frontend/apps/web/src/views/details/ItemDetailRouter.tsx
import { UserStoryDetailView } from "./UserStoryDetailView";

// In the router component:
if (isUserStoryItem(item)) {
  return <UserStoryDetailView item={item} projectId={projectId} />;
}
```

### Step 3: Export from Index

```tsx
// frontend/apps/web/src/views/details/index.ts
export { UserStoryDetailView } from "./UserStoryDetailView";
```

---

## Item Specs System

Detail views use the `useItemSpecs` hooks to fetch enhanced specification data.

**Available Hooks**:
```tsx
// Requirement specs
useRequirementSpecByItem(projectId, itemId)

// Test specs
useTestSpecByItem(projectId, itemId)

// Epic specs
useEpicSpecByItem(projectId, itemId)

// User story specs
useUserStorySpecByItem(projectId, itemId)

// Task specs
useTaskSpecByItem(projectId, itemId)

// Defect specs
useDefectSpecByItem(projectId, itemId)
```

**Pattern**:
```tsx
const { data: spec, isLoading, error } = useRequirementSpecByItem(
  projectId,
  item.id
);
```

---

## Migration Guide

### From Old ItemDetailView

**Before**:
```tsx
import { ItemDetailView } from '@/views/ItemDetailView';

<ItemDetailView />
```

**After**:
```tsx
import { ItemDetailRouter } from '@/views/details';

<ItemDetailRouter item={item} projectId={projectId} />
```

### Route File Changes

**Before**:
```tsx
function ItemDetailComponent() {
  return <ItemDetailView />;
}
```

**After**:
```tsx
function ItemDetailComponent() {
  const { projectId, itemId } = useParams({ strict: false });
  const { data: item } = useItem(projectId, itemId);

  return <ItemDetailRouter item={item} projectId={projectId} />;
}
```

---

## Type Guards Reference

Type guards ensure type safety and proper routing:

```typescript
// From @tracertm/types

isRequirementItem(item: Item): item is RequirementItem
  → type === "requirement"

isTestItem(item: Item): item is TestItem
  → type === "test" | "test_case" | "test_suite"

isEpicItem(item: Item): item is EpicItem
  → type === "epic"

isUserStoryItem(item: Item): item is UserStoryItem
  → type === "user_story" | "story"

isTaskItem(item: Item): item is TaskItem
  → type === "task"

isDefectItem(item: Item): item is DefectItem
  → type === "bug" | "defect"
```

---

## Design Patterns

### 1. Type Guard First

Always check item type before rendering:

```tsx
if (!isEpicItem(item)) {
  return <ErrorCard />;
}
```

### 2. Spec Data with Hooks

Use specialized hooks for enhanced data:

```tsx
const { data: spec, isLoading } = useEpicSpecByItem(projectId, item.id);
```

### 3. Tab-Based Organization

Organize content into logical tabs:

```tsx
const tabs: DetailTab[] = [
  { id: "overview", label: "Overview", content: <Overview /> },
  { id: "details", label: "Details", content: <Details /> },
];
```

### 4. Consistent Theming

Use distinct colors for each type:
- Requirements: Purple (#8b5cf6)
- Tests: Green (#10b981)
- Epics: Deep Purple (#7c3aed)
- User Stories: Blue (#3b82f6)
- Tasks: Orange (#f97316)
- Defects: Red (#ef4444)

---

## Accessibility

All detail views include:

- ARIA labels on tabs
- Keyboard navigation support
- Screen reader announcements
- Focus management
- High contrast mode support

**Example**:
```tsx
<TabsTrigger
  value="overview"
  aria-label="Overview section with key metrics"
>
  Overview
</TabsTrigger>
```

---

## Performance

### Optimization Strategies

1. **Lazy Tab Loading**: Tab content renders only when active
2. **Spec Data Caching**: TanStack Query caches API responses
3. **Memoized Tabs**: Use `useMemo` for tab definitions
4. **Conditional Rendering**: Hide sections with no data

**Example**:
```tsx
const tabs = useMemo(() => {
  return [
    {
      id: "overview",
      label: "Overview",
      content: <Overview />,
    },
  ];
}, [item, spec]);
```

---

## Testing

### Unit Tests

```tsx
describe("EpicDetailView", () => {
  it("renders epic data correctly", () => {
    const item = createMockEpicItem();
    render(<EpicDetailView item={item} projectId="123" />);

    expect(screen.getByText(item.title)).toBeInTheDocument();
  });

  it("shows error for non-epic items", () => {
    const item = createMockRequirementItem();
    render(<EpicDetailView item={item} projectId="123" />);

    expect(screen.getByText(/not an epic/i)).toBeInTheDocument();
  });
});
```

### E2E Tests

```tsx
test("navigates to epic detail view", async ({ page }) => {
  await page.goto("/projects/123/views/table/epic-456");

  await expect(page.getByRole("heading", { name: /epic title/i })).toBeVisible();
  await expect(page.getByRole("tab", { name: /overview/i })).toBeVisible();
});
```

---

## Coming Soon

The following detail views are planned:

1. **UserStoryDetailView** - User story format with acceptance criteria
2. **TaskDetailView** - Task breakdown with checklist tracking
3. **DefectDetailView** - Bug tracking with reproduction steps

---

## Related Documentation

- [BaseDetailView Component](./BASE_DETAIL_VIEW.md)
- [Item Specs System](../hooks/ITEM_SPECS_QUICK_REFERENCE.md)
- [Type Guards](../../packages/types/README.md)
- [Routing Architecture](./ROUTING.md)

---

## Quick Reference

| Item Type | View Component | Hook | Color |
|-----------|---------------|------|-------|
| requirement | RequirementDetailView | useRequirementSpecByItem | Purple |
| test | TestDetailView | useTestSpecByItem | Green |
| epic | EpicDetailView | useEpicSpecByItem | Deep Purple |
| user_story | [Coming Soon] | useUserStorySpecByItem | Blue |
| task | [Coming Soon] | useTaskSpecByItem | Orange |
| bug/defect | [Coming Soon] | useDefectSpecByItem | Red |

---

**Last Updated**: Phase 1 Complete (Requirement, Test, Epic views implemented)

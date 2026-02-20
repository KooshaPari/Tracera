# Frontend Type Diversification & Robustification Plan

**Date**: 2026-01-30
**Status**: Planning Phase
**Scope**: Extend type-aware system across entire frontend

---

## Executive Summary

**Problem**: The type-aware node system is currently isolated to:
- Graph view nodes (TestNode, RequirementNode, EpicNode)
- Item creation dialog (CreateItemDialog)

**Gap**: The rest of the frontend still treats items generically:
- Item detail pages (`items/[item]`)
- Table views (ItemsTableView)
- Kanban boards (ItemsKanbanView)
- Tree views (ItemsTreeView)
- List views (FeatureListView)
- Cards (RequirementSpecCard, TestSpecCard)
- Dashboards

**Goal**: Extend type-specific rendering, editing, and interaction patterns across the entire application for a cohesive, spec-aware user experience.

---

## Audit: Current State

### Components Using Items (Generic Treatment)

**Detail Views**:
1. `/frontend/apps/web/src/views/ItemDetailView.tsx` - Generic item detail page
2. `/frontend/apps/web/src/views/FeatureDetailView.tsx` - Feature-specific detail

**List Views**:
3. `/frontend/apps/web/src/views/ItemsTableView.tsx` - Generic table with virtual scrolling
4. `/frontend/apps/web/src/views/ItemsKanbanView.tsx` - Generic kanban board
5. `/frontend/apps/web/src/views/ItemsTreeView.tsx` - Hierarchical tree view
6. `/frontend/apps/web/src/views/FeatureListView.tsx` - Feature list

**Dashboards**:
7. `/frontend/apps/web/src/views/DashboardView.tsx` - Project dashboard
8. `/frontend/apps/web/src/views/SpecificationsDashboardView.tsx` - Specs dashboard

**Cards** (Already Type-Specific - Good!):
9. `/frontend/apps/web/src/components/RequirementSpecCard.tsx` - Requirement card
10. `/frontend/apps/web/src/components/TestSpecCard.tsx` - Test card
11. `/frontend/apps/web/src/components/FeatureSpecCard.tsx` - Feature card

**Forms**:
12. `/frontend/apps/web/src/components/forms/CreateItemForm.tsx` - OLD generic form (deprecate)
13. `/frontend/apps/web/src/components/forms/CreateTestCaseForm.tsx` - Old test form
14. `/frontend/apps/web/src/components/forms/CreateProcessForm.tsx` - Process form
15. `/frontend/apps/web/src/components/forms/CreateProblemForm.tsx` - Problem form

**Graph Components**:
16. `/frontend/apps/web/src/components/graph/RichNodePill.tsx` - Generic fallback node (keep)
17. `/frontend/apps/web/src/components/graph/QAEnhancedNode.tsx` - QA-enhanced node

**Routes**:
18. `/frontend/apps/web/src/routes/projects.$projectId.views.$viewType.tsx` - View router
19. `/frontend/apps/web/src/routes/projects.$projectId.items.$itemId.tsx` - Item detail route

---

## Phase 1: Type-Specific Detail Pages

**Goal**: Replace generic ItemDetailView with type-specific detail pages

### 1.1 Create Type-Specific Detail Components

**Files to Create**:

1. `/frontend/apps/web/src/views/details/TestDetailView.tsx`
   - Test execution history
   - Flakiness trends chart
   - Coverage breakdown
   - Quarantine status banner
   - Test steps with results
   - Safety level indicators
   - Related requirements links

2. `/frontend/apps/web/src/views/details/RequirementDetailView.tsx`
   - EARS pattern breakdown (trigger/precondition/postcondition)
   - Quality dimensions radar chart
   - Risk assessment panel
   - Verification status timeline
   - Linked ADR/Contract references
   - Traceability matrix section

3. `/frontend/apps/web/src/views/details/EpicDetailView.tsx`
   - Business value justification
   - Timeline Gantt chart
   - Story breakdown list
   - Progress visualization
   - Stakeholder section
   - Acceptance criteria checklist

4. `/frontend/apps/web/src/views/details/UserStoryDetailView.tsx`
   - As-a/I-want/So-that display
   - Acceptance criteria checklist (editable)
   - Story points estimator
   - Sprint assignment
   - Linked tasks/subtasks
   - Definition of Done tracker

5. `/frontend/apps/web/src/views/details/TaskDetailView.tsx`
   - Time tracking widget (estimated vs actual)
   - Subtask checklist
   - Completion percentage slider
   - Assignee section with workload
   - Dependency graph
   - Effort breakdown

6. `/frontend/apps/web/src/views/details/DefectDetailView.tsx`
   - Severity badge and CVSS score
   - Reproduction steps with copy button
   - Root cause analysis section
   - Affected versions list
   - Fix progress tracker
   - Related test failures

### 1.2 Create Detail View Router

**File**: `/frontend/apps/web/src/views/details/index.tsx`

```typescript
import type { TypedItem } from '@tracertm/types';
import { isTestItem, isRequirementItem, isEpicItem, /* ... */ } from '@tracertm/types';
import { TestDetailView } from './TestDetailView';
import { RequirementDetailView } from './RequirementDetailView';
// ... import others

interface ItemDetailRouterProps {
  item: TypedItem;
  projectId: string;
}

export function ItemDetailRouter({ item, projectId }: ItemDetailRouterProps) {
  if (isTestItem(item)) {
    return <TestDetailView item={item} projectId={projectId} />;
  }
  if (isRequirementItem(item)) {
    return <RequirementDetailView item={item} projectId={projectId} />;
  }
  if (isEpicItem(item)) {
    return <EpicDetailView item={item} projectId={projectId} />;
  }
  // ... other types

  // Fallback to generic view
  return <GenericItemDetailView item={item} projectId={projectId} />;
}
```

### 1.3 Update Route Handler

**File**: `/frontend/apps/web/src/routes/projects.$projectId.items.$itemId.tsx`

**Change**:
```typescript
// OLD
import { ItemDetailView } from '@/views/ItemDetailView';
<ItemDetailView item={item} />

// NEW
import { ItemDetailRouter } from '@/views/details';
<ItemDetailRouter item={item} projectId={projectId} />
```

---

## Phase 2: Type-Specific Edit Forms

**Goal**: Replace inline editing with type-specific edit dialogs

### 2.1 Create Edit Form Components

**Pattern**: Reuse creation forms but populate with existing data

**Files to Create**:

1. `/frontend/apps/web/src/components/forms/EditTestItemForm.tsx`
   - Same fields as CreateTestItemForm
   - Pre-populated with item.spec data
   - PATCH endpoint instead of POST
   - Optimistic updates

2. `/frontend/apps/web/src/components/forms/EditRequirementItemForm.tsx`
3. `/frontend/apps/web/src/components/forms/EditEpicItemForm.tsx`
4. `/frontend/apps/web/src/components/forms/EditUserStoryItemForm.tsx`
5. `/frontend/apps/web/src/components/forms/EditTaskItemForm.tsx`
6. `/frontend/apps/web/src/components/forms/EditDefectItemForm.tsx`

### 2.2 Create Unified Edit Dialog

**File**: `/frontend/apps/web/src/components/forms/EditItemDialog.tsx`

```typescript
import type { TypedItem } from '@tracertm/types';
import { isTestItem, /* ... */ } from '@tracertm/types';
import { EditTestItemForm } from './EditTestItemForm';
// ... import others

interface EditItemDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  item: TypedItem;
}

export function EditItemDialog({ open, onOpenChange, item }: EditItemDialogProps) {
  const renderForm = () => {
    if (isTestItem(item)) {
      return <EditTestItemForm item={item} onClose={() => onOpenChange(false)} />;
    }
    // ... other types
    return <EditGenericItemForm item={item} onClose={() => onOpenChange(false)} />;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Edit {item.type}</DialogTitle>
        </DialogHeader>
        {renderForm()}
      </DialogContent>
    </Dialog>
  );
}
```

---

## Phase 3: Type-Specific Table Columns

**Goal**: Show type-specific columns in ItemsTableView

### 3.1 Create Column Configuration Registry

**File**: `/frontend/apps/web/src/lib/tableColumnConfig.ts`

```typescript
import type { ColumnDef } from '@tanstack/react-table';
import type { TypedItem } from '@tracertm/types';

export const TEST_ITEM_COLUMNS: ColumnDef<TypedItem>[] = [
  { accessorKey: 'title', header: 'Test Name' },
  { accessorKey: 'spec.test_type', header: 'Type' },
  { accessorKey: 'spec.test_framework', header: 'Framework' },
  {
    accessorKey: 'spec.flakiness_score',
    header: 'Flakiness',
    cell: ({ getValue }) => {
      const score = getValue() as number;
      return <FlakinessCell score={score} />;
    }
  },
  { accessorKey: 'spec.coverage_percentage', header: 'Coverage' },
  { accessorKey: 'spec.safety_level', header: 'Safety Level' },
  { accessorKey: 'status', header: 'Status' },
];

export const REQUIREMENT_ITEM_COLUMNS: ColumnDef<TypedItem>[] = [
  { accessorKey: 'title', header: 'Requirement' },
  { accessorKey: 'spec.ears_pattern_type', header: 'EARS Pattern' },
  { accessorKey: 'spec.risk_level', header: 'Risk' },
  {
    accessorKey: 'spec.quality_dimensions.verifiability',
    header: 'Verifiability',
    cell: ({ getValue }) => <QualityGauge value={getValue() as number} />
  },
  { accessorKey: 'spec.verification_status', header: 'Verification' },
  { accessorKey: 'status', header: 'Status' },
];

// ... EPIC_ITEM_COLUMNS, STORY_ITEM_COLUMNS, etc.

export function getColumnsForItemType(type: string): ColumnDef<TypedItem>[] {
  switch (type) {
    case 'test':
    case 'suite':
    case 'case':
    case 'scenario':
      return TEST_ITEM_COLUMNS;
    case 'requirement':
      return REQUIREMENT_ITEM_COLUMNS;
    case 'epic':
      return EPIC_ITEM_COLUMNS;
    case 'story':
    case 'user_story':
      return STORY_ITEM_COLUMNS;
    case 'task':
      return TASK_ITEM_COLUMNS;
    case 'defect':
    case 'bug':
      return DEFECT_ITEM_COLUMNS;
    default:
      return DEFAULT_ITEM_COLUMNS;
  }
}
```

### 3.2 Update ItemsTableView

**File**: `/frontend/apps/web/src/views/ItemsTableView.tsx`

**Change**:
```typescript
import { getColumnsForItemType } from '@/lib/tableColumnConfig';

// Inside component
const [selectedType, setSelectedType] = useState<string>('all');
const columns = useMemo(() => {
  if (selectedType === 'all') return DEFAULT_ITEM_COLUMNS;
  return getColumnsForItemType(selectedType);
}, [selectedType]);

// Add type filter dropdown
<Select value={selectedType} onValueChange={setSelectedType}>
  <SelectTrigger>
    <SelectValue />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="all">All Types</SelectItem>
    <SelectItem value="test">Tests</SelectItem>
    <SelectItem value="requirement">Requirements</SelectItem>
    <SelectItem value="epic">Epics</SelectItem>
    {/* ... */}
  </SelectContent>
</Select>
```

---

## Phase 4: Type-Specific Kanban Lanes

**Goal**: Customize kanban lanes based on item type

### 4.1 Create Lane Configuration

**File**: `/frontend/apps/web/src/lib/kanbanLaneConfig.ts`

```typescript
export const TEST_KANBAN_LANES = [
  { id: 'todo', title: 'To Run', color: '#94a3b8' },
  { id: 'in_progress', title: 'Running', color: '#3b82f6' },
  { id: 'done', title: 'Passed', color: '#22c55e' },
  { id: 'blocked', title: 'Failed', color: '#ef4444' },
  { id: 'quarantined', title: 'Quarantined', color: '#f59e0b' },
];

export const REQUIREMENT_KANBAN_LANES = [
  { id: 'draft', title: 'Draft', color: '#94a3b8' },
  { id: 'review', title: 'In Review', color: '#3b82f6' },
  { id: 'approved', title: 'Approved', color: '#22c55e' },
  { id: 'implemented', title: 'Implemented', color: '#10b981' },
  { id: 'verified', title: 'Verified', color: '#06b6d4' },
];

export const EPIC_KANBAN_LANES = [
  { id: 'backlog', title: 'Backlog', color: '#94a3b8' },
  { id: 'planning', title: 'Planning', color: '#3b82f6' },
  { id: 'in_progress', title: 'In Progress', color: '#f59e0b' },
  { id: 'done', title: 'Done', color: '#22c55e' },
];

export function getLanesForItemType(type: string) {
  switch (type) {
    case 'test': return TEST_KANBAN_LANES;
    case 'requirement': return REQUIREMENT_KANBAN_LANES;
    case 'epic': return EPIC_KANBAN_LANES;
    // ... others
    default: return DEFAULT_LANES;
  }
}
```

### 4.2 Create Type-Specific Kanban Cards

**Files to Create**:

1. `/frontend/apps/web/src/components/kanban/TestKanbanCard.tsx`
   - Flakiness indicator
   - Test type badge
   - Last run timestamp
   - Coverage mini-gauge

2. `/frontend/apps/web/src/components/kanban/RequirementKanbanCard.tsx`
   - EARS pattern badge
   - Risk level indicator
   - Verification status

3. `/frontend/apps/web/src/components/kanban/EpicKanbanCard.tsx`
   - Business value stars
   - Story count badge
   - Timeline progress bar

### 4.3 Update ItemsKanbanView

**File**: `/frontend/apps/web/src/views/ItemsKanbanView.tsx`

**Change**:
```typescript
import { getLanesForItemType } from '@/lib/kanbanLaneConfig';
import { TestKanbanCard, RequirementKanbanCard, /* ... */ } from '@/components/kanban';

const lanes = getLanesForItemType(currentItemType);

// Render type-specific cards
const renderCard = (item: TypedItem) => {
  if (isTestItem(item)) return <TestKanbanCard item={item} />;
  if (isRequirementItem(item)) return <RequirementKanbanCard item={item} />;
  // ... others
  return <GenericKanbanCard item={item} />;
};
```

---

## Phase 5: Type-Specific Dashboard Widgets

**Goal**: Add type-specific metrics to dashboards

### 5.1 Create Widget Components

**Files to Create**:

1. `/frontend/apps/web/src/components/dashboard/TestMetricsWidget.tsx`
   - Flakiness trend chart
   - Pass/fail ratio
   - Average execution time
   - Quarantined tests count

2. `/frontend/apps/web/src/components/dashboard/RequirementMetricsWidget.tsx`
   - Verification status pie chart
   - Risk distribution
   - Quality dimensions heatmap
   - EARS pattern breakdown

3. `/frontend/apps/web/src/components/dashboard/EpicMetricsWidget.tsx`
   - Business value ROI chart
   - Timeline burndown
   - Story completion funnel
   - Velocity trends

### 5.2 Update DashboardView

**File**: `/frontend/apps/web/src/views/DashboardView.tsx`

**Add**:
```typescript
import { TestMetricsWidget, RequirementMetricsWidget, EpicMetricsWidget } from '@/components/dashboard';

// Detect dominant item types in project
const dominantTypes = useMemo(() => {
  const typeCounts = items.reduce((acc, item) => {
    acc[item.type] = (acc[item.type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return Object.entries(typeCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3)
    .map(([type]) => type);
}, [items]);

// Render widgets for dominant types
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {dominantTypes.includes('test') && <TestMetricsWidget items={items} />}
  {dominantTypes.includes('requirement') && <RequirementMetricsWidget items={items} />}
  {dominantTypes.includes('epic') && <EpicMetricsWidget items={items} />}
</div>
```

---

## Phase 6: Type-Specific Filters & Search

**Goal**: Add type-specific filter panels

### 6.1 Create Filter Components

**Files to Create**:

1. `/frontend/apps/web/src/components/filters/TestFilters.tsx`
   ```typescript
   - Test type multi-select (unit, integration, e2e, etc.)
   - Framework select
   - Flakiness threshold slider
   - Coverage range
   - Safety level checkboxes
   - Quarantine status toggle
   ```

2. `/frontend/apps/web/src/components/filters/RequirementFilters.tsx`
   ```typescript
   - EARS pattern multi-select
   - Risk level range
   - Verification status
   - Quality dimensions sliders
   - ADR/Contract linked toggle
   ```

3. `/frontend/apps/web/src/components/filters/EpicFilters.tsx`
   ```typescript
   - Business value range
   - Timeline date picker
   - Story count range
   - Completion percentage slider
   ```

### 6.2 Create Unified Filter Panel

**File**: `/frontend/apps/web/src/components/filters/ItemFilterPanel.tsx`

```typescript
interface ItemFilterPanelProps {
  itemType: string;
  filters: Record<string, any>;
  onFiltersChange: (filters: Record<string, any>) => void;
}

export function ItemFilterPanel({ itemType, filters, onFiltersChange }: ItemFilterPanelProps) {
  const renderFilters = () => {
    switch (itemType) {
      case 'test':
        return <TestFilters filters={filters} onChange={onFiltersChange} />;
      case 'requirement':
        return <RequirementFilters filters={filters} onChange={onFiltersChange} />;
      // ... others
      default:
        return <GenericFilters filters={filters} onChange={onFiltersChange} />;
    }
  };

  return (
    <div className="p-4 border rounded-lg bg-card">
      <h3 className="font-semibold mb-4">Filters</h3>
      {renderFilters()}
    </div>
  );
}
```

---

## Phase 7: Type-Specific Bulk Operations

**Goal**: Add type-specific bulk actions

### 7.1 Create Bulk Action Menus

**File**: `/frontend/apps/web/src/components/BulkActionMenu.tsx` (UPDATE)

```typescript
const TEST_BULK_ACTIONS = [
  { id: 'run', label: 'Run Selected Tests', icon: Play },
  { id: 'quarantine', label: 'Quarantine', icon: AlertTriangle },
  { id: 'unquarantine', label: 'Unquarantine', icon: CheckCircle },
  { id: 'change-framework', label: 'Change Framework', icon: Settings },
  { id: 'delete', label: 'Delete', icon: Trash2 },
];

const REQUIREMENT_BULK_ACTIONS = [
  { id: 'verify', label: 'Mark as Verified', icon: CheckCircle },
  { id: 'link-adr', label: 'Link to ADR', icon: Link },
  { id: 'export-srs', label: 'Export SRS', icon: FileDown },
  { id: 'change-risk', label: 'Change Risk Level', icon: AlertTriangle },
  { id: 'delete', label: 'Delete', icon: Trash2 },
];

export function getBulkActionsForType(type: string) {
  switch (type) {
    case 'test': return TEST_BULK_ACTIONS;
    case 'requirement': return REQUIREMENT_BULK_ACTIONS;
    // ... others
    default: return DEFAULT_BULK_ACTIONS;
  }
}
```

---

## Phase 8: Type-Specific Validation & Constraints

**Goal**: Add runtime validation for type-specific business rules

### 8.1 Create Validation Rules

**File**: `/frontend/apps/web/src/lib/itemValidation.ts`

```typescript
export const TEST_VALIDATION_RULES = {
  // Critical tests must have safety level
  criticalMustHaveSafetyLevel: (item: TestItem) => {
    if (item.spec?.is_critical_path && !item.spec?.safety_level) {
      return { valid: false, message: 'Critical tests must specify safety level' };
    }
    return { valid: true };
  },

  // E2E tests should have higher timeout
  e2eTimeoutCheck: (item: TestItem) => {
    if (item.spec?.test_type === 'e2e' &&
        (item.spec?.expected_duration_ms ?? 0) < 5000) {
      return {
        valid: false,
        message: 'E2E tests should have at least 5s timeout',
        severity: 'warning'
      };
    }
    return { valid: true };
  },
};

export const REQUIREMENT_VALIDATION_RULES = {
  // EARS patterns must have all components
  earsPatternComplete: (item: RequirementItem) => {
    const spec = item.spec;
    if (!spec) return { valid: true };

    const pattern = spec.ears_pattern_type;
    if (pattern === 'event_driven' && !spec.ears_trigger) {
      return { valid: false, message: 'Event-driven requirements must specify trigger' };
    }
    return { valid: true };
  },

  // High-risk requirements must have verification
  highRiskMustVerify: (item: RequirementItem) => {
    if (item.spec?.risk_level === 'critical' &&
        item.spec?.verification_status === 'unverified') {
      return {
        valid: false,
        message: 'Critical risk requirements must have verification plan'
      };
    }
    return { valid: true };
  },
};
```

### 8.2 Add Validation to Forms

**Update**: All Edit/Create forms to run validation rules before submit

```typescript
const validationResults = validateItem(formData);
const errors = validationResults.filter(r => !r.valid && r.severity === 'error');
const warnings = validationResults.filter(r => !r.valid && r.severity === 'warning');

if (errors.length > 0) {
  toast.error(`Validation failed: ${errors[0].message}`);
  return;
}

if (warnings.length > 0) {
  // Show warning dialog
  const confirmed = await confirmDialog({
    title: 'Validation Warnings',
    message: warnings.map(w => w.message).join('\n'),
    confirmText: 'Save Anyway',
  });
  if (!confirmed) return;
}
```

---

## Implementation Priority

### 🔥 High Priority (Week 1-2)

1. **Phase 1: Type-Specific Detail Pages** - Most visible impact
   - Users spend most time in detail views
   - High ROI for UX improvement

2. **Phase 2: Type-Specific Edit Forms** - Completes CRUD cycle
   - Necessary for practical use
   - Builds on Phase 1 investment

### 🚀 Medium Priority (Week 3-4)

3. **Phase 3: Type-Specific Table Columns** - Improves data density
   - Power users need this
   - Enables better filtering/sorting

4. **Phase 5: Type-Specific Dashboard Widgets** - Analytics value
   - Project managers need metrics
   - Shows spec data value

### 📊 Lower Priority (Week 5-6)

5. **Phase 4: Type-Specific Kanban Lanes** - Nice-to-have
   - Not all users use kanban
   - Can use generic lanes initially

6. **Phase 6: Type-Specific Filters** - Advanced feature
   - Enhances Phase 3
   - Power user feature

7. **Phase 7: Type-Specific Bulk Operations** - Efficiency gain
   - Advanced workflows
   - Lower usage frequency

8. **Phase 8: Validation & Constraints** - Quality assurance
   - Prevents bad data
   - Can add incrementally

---

## File Structure

```
frontend/apps/web/src/
├── views/
│   ├── details/                          # NEW
│   │   ├── index.tsx                     # ItemDetailRouter
│   │   ├── TestDetailView.tsx
│   │   ├── RequirementDetailView.tsx
│   │   ├── EpicDetailView.tsx
│   │   ├── UserStoryDetailView.tsx
│   │   ├── TaskDetailView.tsx
│   │   └── DefectDetailView.tsx
│   ├── ItemDetailView.tsx                # DEPRECATE
│   ├── ItemsTableView.tsx                # UPDATE
│   ├── ItemsKanbanView.tsx               # UPDATE
│   └── DashboardView.tsx                 # UPDATE
│
├── components/
│   ├── forms/
│   │   ├── EditTestItemForm.tsx          # NEW
│   │   ├── EditRequirementItemForm.tsx   # NEW
│   │   ├── EditEpicItemForm.tsx          # NEW
│   │   ├── EditUserStoryItemForm.tsx     # NEW
│   │   ├── EditTaskItemForm.tsx          # NEW
│   │   ├── EditDefectItemForm.tsx        # NEW
│   │   └── EditItemDialog.tsx            # NEW
│   │
│   ├── kanban/                            # NEW
│   │   ├── TestKanbanCard.tsx
│   │   ├── RequirementKanbanCard.tsx
│   │   └── EpicKanbanCard.tsx
│   │
│   ├── dashboard/                         # NEW
│   │   ├── TestMetricsWidget.tsx
│   │   ├── RequirementMetricsWidget.tsx
│   │   └── EpicMetricsWidget.tsx
│   │
│   └── filters/                           # NEW
│       ├── ItemFilterPanel.tsx
│       ├── TestFilters.tsx
│       ├── RequirementFilters.tsx
│       └── EpicFilters.tsx
│
└── lib/
    ├── tableColumnConfig.ts               # NEW
    ├── kanbanLaneConfig.ts                # NEW
    └── itemValidation.ts                  # NEW
```

---

## Success Metrics

| Phase | Metric | Target |
|-------|--------|--------|
| Detail Pages | User time on detail pages | +30% (more engaging) |
| Edit Forms | Edit completion rate | >90% |
| Table Columns | Clicks to find data | -50% (visible) |
| Dashboard Widgets | Dashboard usage | +40% |
| Filters | Search efficiency | -60% time to find |
| Bulk Operations | Time saved on batch ops | -70% |
| Validation | Bad data created | -80% |

---

## Rollout Strategy

### Week 1-2: Foundation
- Phase 1 (Detail Pages) - 3 types minimum (Test, Requirement, Epic)
- Phase 2 (Edit Forms) - Same 3 types

### Week 3-4: Expansion
- Phase 3 (Table Columns) - All types
- Phase 5 (Dashboard Widgets) - 3 widgets

### Week 5-6: Polish
- Remaining phases as needed
- User feedback incorporation
- Performance optimization

---

## Risk Mitigation

**Backward Compatibility**:
- Keep generic fallbacks for unknown types
- Gradual migration (feature flags if needed)
- Don't break existing URLs/bookmarks

**Performance**:
- Lazy load type-specific components
- Code split by item type
- Monitor bundle size

**Maintenance**:
- Shared base components (reduce duplication)
- Configuration-driven where possible
- Comprehensive documentation

---

## Next Steps

1. **Review this plan** - Confirm scope and priorities
2. **Create Phase 1 ticket** - Type-specific detail pages
3. **Design mockups** - UI/UX for each detail page
4. **Backend coordination** - Ensure spec data availability
5. **Implement incrementally** - One phase at a time

---

**Status**: Ready for review and approval
**Estimated Total Effort**: 6 weeks (1 developer full-time)
**Expected Value**: Dramatic improvement in type-aware UX across application

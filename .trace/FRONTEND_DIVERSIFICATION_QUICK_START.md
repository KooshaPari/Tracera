# Frontend Type Diversification - Quick Start Guide

**Goal**: Extend type-aware system from graph nodes to all UI components

---

## Current State ✅

**Already Type-Aware**:
- ✅ Graph nodes (TestNode, RequirementNode, EpicNode)
- ✅ Item creation (CreateItemDialog with type selector)
- ✅ Type system (discriminated unions, type guards)
- ✅ Some cards (RequirementSpecCard, TestSpecCard)

---

## What Needs Type-Awareness ⚠️

**Generic Components** (treat all items the same):
- ❌ Item detail pages (`/items/[id]`)
- ❌ Table views (ItemsTableView)
- ❌ Kanban boards (ItemsKanbanView)
- ❌ Tree views (ItemsTreeView)
- ❌ Dashboards (metrics, widgets)
- ❌ Edit forms (currently generic)
- ❌ Filters and search
- ❌ Bulk operations

---

## Implementation Phases (Priority Order)

### 🔥 Phase 1: Type-Specific Detail Pages (HIGHEST PRIORITY)

**Impact**: Users spend 60%+ time in detail views

**Create 6 detail views**:
```
/views/details/
  ├── TestDetailView.tsx         - Test execution, flakiness, coverage
  ├── RequirementDetailView.tsx  - EARS breakdown, quality radar
  ├── EpicDetailView.tsx         - Business value, timeline
  ├── UserStoryDetailView.tsx    - Acceptance criteria, points
  ├── TaskDetailView.tsx         - Time tracking, subtasks
  └── DefectDetailView.tsx       - CVSS, root cause, repro steps
```

**Router component**:
```typescript
// /views/details/index.tsx
export function ItemDetailRouter({ item }: { item: TypedItem }) {
  if (isTestItem(item)) return <TestDetailView item={item} />;
  if (isRequirementItem(item)) return <RequirementDetailView item={item} />;
  // ... etc
  return <GenericItemDetailView item={item} />; // Fallback
}
```

**Integration**:
```typescript
// Replace in routes/projects.$projectId.items.$itemId.tsx
- <ItemDetailView item={item} />
+ <ItemDetailRouter item={item} />
```

**Estimated Time**: 1 week (3 types first, then expand)

---

### 🚀 Phase 2: Type-Specific Edit Forms

**Impact**: Completes CRUD cycle, necessary for users

**Create 6 edit forms** (reuse creation form schemas):
```
/components/forms/
  ├── EditTestItemForm.tsx
  ├── EditRequirementItemForm.tsx
  ├── EditEpicItemForm.tsx
  ├── EditUserStoryItemForm.tsx
  ├── EditTaskItemForm.tsx
  └── EditDefectItemForm.tsx
```

**Pattern**:
```typescript
// Same as CreateTestItemForm but:
1. Pre-populate with item.spec data
2. Use PATCH /api/items/:id instead of POST
3. Add optimistic UI updates
4. Include delete button
```

**Unified edit dialog**:
```typescript
// /components/forms/EditItemDialog.tsx
<EditItemDialog open={open} onOpenChange={setOpen} item={selectedItem} />
// Internally routes to correct form based on item type
```

**Estimated Time**: 1 week

---

### 📊 Phase 3: Type-Specific Table Columns

**Impact**: Power users see relevant data immediately

**Column configurations**:
```typescript
// /lib/tableColumnConfig.ts
export const TEST_ITEM_COLUMNS = [
  { key: 'title', header: 'Test Name' },
  { key: 'spec.test_type', header: 'Type' },
  { key: 'spec.flakiness_score', header: 'Flakiness', cell: FlakinessCell },
  { key: 'spec.coverage_percentage', header: 'Coverage' },
  { key: 'spec.safety_level', header: 'Safety' },
];

export const REQUIREMENT_ITEM_COLUMNS = [
  { key: 'title', header: 'Requirement' },
  { key: 'spec.ears_pattern_type', header: 'EARS' },
  { key: 'spec.risk_level', header: 'Risk' },
  { key: 'spec.verification_status', header: 'Verified' },
];
```

**Update ItemsTableView**:
```typescript
const columns = getColumnsForItemType(selectedType);
```

**Add type filter dropdown**:
```typescript
<Select value={type} onValueChange={setType}>
  <SelectItem value="all">All Types</SelectItem>
  <SelectItem value="test">Tests</SelectItem>
  <SelectItem value="requirement">Requirements</SelectItem>
</Select>
```

**Estimated Time**: 3-4 days

---

### 🎨 Phase 4: Type-Specific Dashboard Widgets

**Impact**: Shows value of spec data, improves analytics

**Create widgets**:
```
/components/dashboard/
  ├── TestMetricsWidget.tsx         - Flakiness trends, pass/fail ratio
  ├── RequirementMetricsWidget.tsx  - Risk distribution, quality heatmap
  └── EpicMetricsWidget.tsx         - Business value ROI, burndown
```

**Auto-detect dominant types**:
```typescript
const dominantTypes = items.reduce((acc, item) => { /* count */ });
// Show widgets for top 3 types in project
```

**Estimated Time**: 3-4 days

---

### 🎯 Phase 5: Type-Specific Kanban Lanes

**Impact**: Better workflow visualization

**Lane configurations**:
```typescript
// /lib/kanbanLaneConfig.ts
export const TEST_KANBAN_LANES = [
  { id: 'todo', title: 'To Run' },
  { id: 'in_progress', title: 'Running' },
  { id: 'done', title: 'Passed' },
  { id: 'blocked', title: 'Failed' },
  { id: 'quarantined', title: 'Quarantined' }, // Test-specific!
];
```

**Card components**:
```
/components/kanban/
  ├── TestKanbanCard.tsx         - Flakiness badge, last run
  ├── RequirementKanbanCard.tsx  - EARS badge, risk
  └── EpicKanbanCard.tsx         - Business value, progress
```

**Estimated Time**: 2-3 days

---

### 🔍 Phase 6: Type-Specific Filters

**Impact**: Power users can narrow down precisely

**Filter components**:
```
/components/filters/
  ├── TestFilters.tsx
  │   - Test type multi-select
  │   - Flakiness threshold slider
  │   - Coverage range
  │   - Safety level checkboxes
  │
  ├── RequirementFilters.tsx
  │   - EARS pattern multi-select
  │   - Risk level range
  │   - Verification status
  │
  └── EpicFilters.tsx
      - Business value range
      - Timeline date picker
```

**Estimated Time**: 2-3 days

---

### ⚡ Phase 7: Type-Specific Bulk Operations

**Impact**: Efficiency for batch operations

**Bulk action menus**:
```typescript
const TEST_BULK_ACTIONS = [
  { id: 'run', label: 'Run Selected Tests' },
  { id: 'quarantine', label: 'Quarantine' },
  { id: 'change-framework', label: 'Change Framework' },
];

const REQUIREMENT_BULK_ACTIONS = [
  { id: 'verify', label: 'Mark as Verified' },
  { id: 'link-adr', label: 'Link to ADR' },
  { id: 'export-srs', label: 'Export SRS' },
];
```

**Estimated Time**: 2 days

---

### ✅ Phase 8: Type-Specific Validation

**Impact**: Data quality, prevents errors

**Validation rules**:
```typescript
// /lib/itemValidation.ts
export const TEST_VALIDATION_RULES = {
  criticalMustHaveSafetyLevel: (item: TestItem) => {
    if (item.spec?.is_critical_path && !item.spec?.safety_level) {
      return { valid: false, message: 'Critical tests need safety level' };
    }
    return { valid: true };
  },
};
```

**Apply in forms**:
```typescript
const errors = validateItem(formData);
if (errors.length > 0) {
  toast.error(errors[0].message);
  return;
}
```

**Estimated Time**: 2 days

---

## Total Timeline

| Week | Phases | Deliverable |
|------|--------|-------------|
| 1-2 | 1, 2 | Detail pages + Edit forms (3 types minimum) |
| 3 | 3 | Table columns (all types) |
| 3-4 | 4, 5 | Dashboard widgets + Kanban |
| 5 | 6, 7 | Filters + Bulk operations |
| 6 | 8 | Validation + Polish |

**Total**: 6 weeks for full implementation

---

## Quick Wins (Week 1)

**Start with these 3 types** (cover 80% of use cases):
1. **TestDetailView** - Most common in TEST projects
2. **RequirementDetailView** - Core to FEATURE projects
3. **EpicDetailView** - PM/planning workflows

**Then expand** to UserStory, Task, Defect in week 2

---

## Code Reuse Strategy

**Don't duplicate everything!**

**Shared base components**:
```typescript
// /components/details/BaseDetailView.tsx
export function BaseDetailView({ item, children }: Props) {
  return (
    <div className="detail-page">
      <DetailHeader item={item} />
      <DetailTabs>
        {children}
      </DetailTabs>
      <DetailFooter item={item} />
    </div>
  );
}

// Then in type-specific views:
export function TestDetailView({ item }: { item: TestItem }) {
  return (
    <BaseDetailView item={item}>
      <TestExecutionTab item={item} />
      <TestMetricsTab item={item} />
      <TestLinksTab item={item} />
    </BaseDetailView>
  );
}
```

**Configuration over duplication**:
- Use `itemTypeConfig.ts` for colors, icons, labels
- Use column config for tables
- Use lane config for kanban

---

## Testing Strategy

**For each type-specific component**:

1. **Unit tests** - Component renders correctly
2. **Integration tests** - Form submission works
3. **Type guard tests** - Correct component shown for type
4. **Fallback tests** - Unknown types use generic view

**Example**:
```typescript
describe('ItemDetailRouter', () => {
  it('shows TestDetailView for test items', () => {
    const item = { type: 'test', spec: { test_type: 'unit' } };
    render(<ItemDetailRouter item={item} />);
    expect(screen.getByText('Test Execution')).toBeInTheDocument();
  });

  it('shows GenericDetailView for unknown types', () => {
    const item = { type: 'unknown_type' };
    render(<ItemDetailRouter item={item} />);
    expect(screen.getByText('Item Details')).toBeInTheDocument();
  });
});
```

---

## Migration Path

**Phase 1 rollout**:
```typescript
// Feature flag for gradual rollout
const USE_TYPE_SPECIFIC_DETAILS =
  process.env.VITE_TYPE_SPECIFIC_DETAILS === 'true';

if (USE_TYPE_SPECIFIC_DETAILS) {
  return <ItemDetailRouter item={item} />;
} else {
  return <ItemDetailView item={item} />; // Old generic view
}
```

**Once stable** (after 1-2 weeks):
- Remove feature flag
- Remove old generic components
- Update all routes

---

## Documentation Checklist

For each phase:
- [ ] Component API documentation
- [ ] Usage examples
- [ ] Storybook stories
- [ ] Migration guide
- [ ] Performance notes

---

## Success Criteria

**Phase 1 (Detail Pages)**:
- ✅ 3 type-specific detail views created
- ✅ Router component working
- ✅ Zero TypeScript errors
- ✅ All spec fields displayed
- ✅ User testing shows improved engagement

**Phase 2 (Edit Forms)**:
- ✅ 3 type-specific edit forms
- ✅ Unified edit dialog
- ✅ PATCH endpoints integrated
- ✅ Optimistic UI updates
- ✅ Form validation working

**Repeat for other phases...**

---

## Getting Started

1. **Read full plan**: `.trace/FRONTEND_TYPE_DIVERSIFICATION_PLAN.md`
2. **Start Phase 1**: Create `TestDetailView.tsx`
3. **Follow pattern**: Use graph node components as reference
4. **Reuse types**: Import from `@tracertm/types`
5. **Test early**: Write tests as you build

---

**Questions?** Check the full plan or ask for clarification on specific phases.

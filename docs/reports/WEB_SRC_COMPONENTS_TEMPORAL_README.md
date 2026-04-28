# Temporal Navigation Components

Version and branch navigation components for managing project versions across different branches.

## Components

### TemporalNavigator

Main navigation component with 4 view modes:

- **Timeline**: Horizontal version history with zoom controls
- **Branches**: Tree visualization of branch structure
- **Comparison**: Side-by-side branch comparison
- **Progress**: Version completion and branch status metrics

**Features:**

- Branch selector with status indicators
- View mode toggle buttons
- Expandable content area
- Current version/branch info display
- Support for branch creation and merge operations

**Props:**

```typescript
interface TemporalNavigatorProps {
  projectId: string;
  currentBranchId: string;
  currentVersionId: string;
  branches: Branch[];
  versions: Version[];
  isLoading?: boolean;
  onBranchChange: (branchId: string) => void;
  onVersionChange: (versionId: string) => void;
  onBranchCreate?: () => void;
  onMergeRequest?: (sourceBranchId: string, targetBranchId: string) => void;
}
```

### TimelineView

Horizontal timeline displaying version markers with interactive navigation.

**Features:**

- Version markers with timeline indicators
- Zoom in/out controls
- Scroll navigation
- Version tags and status badges
- Author and timestamp information
- Version descriptions with hover tooltips
- Date range display

**Props:**

```typescript
interface TimelineViewProps {
  versions: Version[];
  currentVersionId: string;
  onVersionChange: (versionId: string) => void;
}
```

### BranchExplorer

Tree visualization of branch structure with merge operations.

**Features:**

- Hierarchical branch tree
- Branch status indicators (active, review, merged, abandoned)
- Expandable/collapsible nodes
- Merge source selection and confirmation
- Branch creation button
- Branch statistics display
- Parent-child relationships

**Props:**

```typescript
interface BranchExplorerProps {
  projectId: string;
  branches: Branch[];
  currentBranchId: string;
  onBranchChange: (branchId: string) => void;
  onMergeRequest?: (sourceBranchId: string, targetBranchId: string) => void;
  onBranchCreate?: () => void;
}
```

## Type Definitions

### Branch

```typescript
interface Branch {
  id: string;
  name: string;
  description?: string;
  parentId?: string;
  status: 'active' | 'review' | 'merged' | 'abandoned';
  createdAt: Date;
  updatedAt: Date;
  author?: string;
  mergeRequestCount: number;
}
```

### Version

```typescript
interface Version {
  id: string;
  branchId: string;
  tag?: string;
  title: string;
  description?: string;
  timestamp: Date;
  author?: string;
  status: 'draft' | 'published' | 'archived';
  snapshot?: Record<string, any>;
}
```

## React Query Hooks

### useBranches

Fetch branches for a project.

```typescript
const { data: branches, isLoading } = useBranches(projectId);
```

### useVersions

Fetch versions for a branch.

```typescript
const { data: versions, isLoading } = useVersions(branchId);
```

### useCreateBranch

Create a new branch.

```typescript
const { mutate: createBranch } = useCreateBranch();
createBranch({
  projectId: 'proj-1',
  name: 'feature/new',
  parentId: 'main',
});
```

### useCreateVersion

Create a new version.

```typescript
const { mutate: createVersion } = useCreateVersion();
createVersion({
  branchId: 'branch-1',
  title: 'v2.0.0',
  tag: '2.0.0',
  status: 'draft',
});
```

### useMergeBranch

Merge one branch into another.

```typescript
const { mutate: mergeBranch } = useMergeBranch();
mergeBranch({
  sourceBranchId: 'feature-auth',
  targetBranchId: 'develop',
  conflictResolution: 'manual',
});
```

### useVersionSnapshot

Get a version's snapshot data.

```typescript
const { data: snapshot } = useVersionSnapshot(versionId);
```

### useCompareBranches

Compare two branches for differences.

```typescript
const { data: comparison } = useCompareBranches(sourceBranchId, targetBranchId);
```

## Usage Example

```typescript
import {
  TemporalNavigator,
  useBranches,
  useVersions
} from '@/components/temporal';

function ProjectTimeline() {
  const { data: branches } = useBranches(projectId);
  const { data: versions } = useVersions(currentBranchId);
  const [currentBranchId, setCurrentBranchId] = useState(initialBranchId);
  const [currentVersionId, setCurrentVersionId] = useState(initialVersionId);

  return (
    <TemporalNavigator
      projectId={projectId}
      currentBranchId={currentBranchId}
      currentVersionId={currentVersionId}
      branches={branches || []}
      versions={versions || []}
      onBranchChange={setCurrentBranchId}
      onVersionChange={setCurrentVersionId}
      onBranchCreate={handleCreateBranch}
      onMergeRequest={handleMergeRequest}
    />
  );
}
```

## Styling

Components use Tailwind CSS with dark mode support:

- Light/dark theme support
- Responsive design
- Accessible color contrasts
- Smooth transitions and animations

## Testing

Test files included in `__tests__/`:

- `TemporalNavigator.test.tsx` - Navigation and branch switching
- `TimelineView.test.tsx` - Timeline interactions and version selection
- `BranchExplorer.test.tsx` - Tree visualization and merge operations

Coverage target: >85%

## Storybook

Interactive component stories in `__stories__/`:

- `TemporalNavigator.stories.tsx`
- `TimelineView.stories.tsx`
- `BranchExplorer.stories.tsx`

Run with: `npm run storybook`

## API Integration

Components expect REST API endpoints:

- `GET /api/v1/projects/:projectId/branches`
- `GET /api/v1/branches/:branchId/versions`
- `POST /api/v1/projects/:projectId/branches`
- `POST /api/v1/branches/:branchId/versions`
- `POST /api/v1/branches/:targetBranchId/merge`
- `GET /api/v1/versions/:versionId/snapshot`

See `useTemporal.ts` for implementation details.

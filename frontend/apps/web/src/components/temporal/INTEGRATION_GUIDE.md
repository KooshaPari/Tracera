# Temporal Navigation - Integration Guide

Complete guide for integrating temporal navigation components into your application.

## Quick Start

### 1. Basic Setup

```typescript
import {
  TemporalNavigator,
  useBranches,
  useVersions,
} from '@/components/temporal';
import { useState } from 'react';

function ProjectPage() {
  const projectId = 'proj-123';
  const [currentBranchId, setCurrentBranchId] = useState('main');
  const [currentVersionId, setCurrentVersionId] = useState('v1.0.0');

  const { data: branches = [] } = useBranches(projectId);
  const { data: versions = [] } = useVersions(currentBranchId);

  return (
    <TemporalNavigator
      projectId={projectId}
      currentBranchId={currentBranchId}
      currentVersionId={currentVersionId}
      branches={branches}
      versions={versions}
      onBranchChange={setCurrentBranchId}
      onVersionChange={setCurrentVersionId}
    />
  );
}
```

### 2. With Create Actions

```typescript
import { useCreateBranch, useMergeBranch } from '@/hooks/useTemporal';

function ProjectPageWithActions() {
  // ... previous code ...

  const { mutate: createBranch } = useCreateBranch();
  const { mutate: mergeBranch } = useMergeBranch();

  const handleCreateBranch = () => {
    const name = prompt('New branch name:');
    if (name) {
      createBranch({
        projectId,
        name,
        parentId: currentBranchId,
      });
    }
  };

  const handleMergeRequest = (source, target) => {
    mergeBranch({
      sourceBranchId: source,
      targetBranchId: target,
      conflictResolution: 'manual',
    });
  };

  return (
    <TemporalNavigator
      // ... props ...
      onBranchCreate={handleCreateBranch}
      onMergeRequest={handleMergeRequest}
    />
  );
}
```

## Component Integration Patterns

### Pattern 1: Sidebar Navigation

```typescript
import { TemporalNavigator } from '@/components/temporal';

function AppLayout() {
  return (
    <div className="flex">
      <aside className="w-64 border-r">
        <TemporalNavigator
          // ... props ...
        />
      </aside>
      <main className="flex-1">
        {/* Main content */}
      </main>
    </div>
  );
}
```

### Pattern 2: Header Bar

```typescript
function AppHeader() {
  return (
    <header className="border-b">
      <TemporalNavigator
        // ... props ...
      />
    </header>
  );
}
```

### Pattern 3: Modal Dialog

```typescript
import { Dialog, DialogContent } from '@tracertm/ui/components/Dialog';

function VersionHistoryModal({ open, onClose }) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <TemporalNavigator
          // ... props ...
        />
      </DialogContent>
    </Dialog>
  );
}
```

## Hook Usage Examples

### Fetching Data

```typescript
// Get all branches
const { data: branches, isLoading: loading } = useBranches(projectId);

// Get versions for a branch
const { data: versions } = useVersions(branchId);

// Get a version's snapshot
const { data: snapshot } = useVersionSnapshot(versionId);

// Compare two branches
const { data: comparison } = useCompareBranches(
  'feature/auth',
  'develop'
);
```

### Creating Resources

```typescript
// Create a new branch
const { mutate: createBranch, isPending } = useCreateBranch();

createBranch({
  projectId: 'proj-123',
  name: 'feature/new-feature',
  description: 'New feature development',
  parentId: 'develop',
});

// Create a new version
const { mutate: createVersion } = useCreateVersion();

createVersion({
  branchId: 'branch-123',
  title: 'v2.0.0',
  tag: '2.0.0',
  description: 'Major release',
  status: 'draft',
});
```

### Mutations with Error Handling

```typescript
const { mutate: mergeBranch, isError, error } = useMergeBranch();

mergeBranch(
  {
    sourceBranchId: 'feature/auth',
    targetBranchId: 'develop',
    conflictResolution: 'manual',
  },
  {
    onSuccess: () => {
      console.log('Merge completed successfully');
      showSuccessNotification('Branches merged');
    },
    onError: (err) => {
      console.error('Merge failed:', err);
      showErrorNotification('Merge failed: ' + err.message);
    },
  }
);
```

## State Management Integration

### With Zustand

```typescript
import { create } from 'zustand';

interface TemporalStore {
  currentProjectId: string;
  currentBranchId: string;
  currentVersionId: string;
  setBranch: (branchId: string) => void;
  setVersion: (versionId: string) => void;
}

const useTemporalStore = create<TemporalStore>((set) => ({
  currentProjectId: 'proj-123',
  currentBranchId: 'main',
  currentVersionId: 'v1.0.0',
  setBranch: (branchId) => set({ currentBranchId: branchId }),
  setVersion: (versionId) => set({ currentVersionId: versionId }),
}));

// Usage in component
function MyComponent() {
  const { currentProjectId, currentBranchId, setBranch, setVersion } =
    useTemporalStore();
  const { data: branches } = useBranches(currentProjectId);

  return (
    <TemporalNavigator
      projectId={currentProjectId}
      currentBranchId={currentBranchId}
      branches={branches || []}
      onBranchChange={setBranch}
      onVersionChange={setVersion}
    />
  );
}
```

### With Context API

```typescript
import { createContext, useContext, useState } from 'react';

interface TemporalContextType {
  projectId: string;
  branchId: string;
  versionId: string;
  setBranchId: (id: string) => void;
  setVersionId: (id: string) => void;
}

const TemporalContext = createContext<TemporalContextType | null>(null);

export function TemporalProvider({ children }) {
  const [branchId, setBranchId] = useState('main');
  const [versionId, setVersionId] = useState('v1.0.0');

  return (
    <TemporalContext.Provider
      value={{
        projectId: 'proj-123',
        branchId,
        versionId,
        setBranchId,
        setVersionId,
      }}
    >
      {children}
    </TemporalContext.Provider>
  );
}

export function useTemporal() {
  const context = useContext(TemporalContext);
  if (!context) {
    throw new Error('useTemporal must be used within TemporalProvider');
  }
  return context;
}
```

## Customization

### Styling

Components use Tailwind CSS classes that can be customized via config:

```typescript
// tailwind.config.ts
export default {
  theme: {
    colors: {
      // Customize brand colors
      blue: '#0066cc',
      green: '#00cc66',
      orange: '#ff9933',
      red: '#ff3333',
    },
  },
};
```

### View Mode Defaults

```typescript
function CustomTemporalNavigator() {
  const [viewMode, setViewMode] = useState<ViewMode>('branches');

  return (
    <TemporalNavigator
      // ... props ...
      defaultViewMode={viewMode}
    />
  );
}
```

## Event Handling

### Custom Callbacks

```typescript
function handleBranchChange(branchId: string) {
  // Log analytics
  analytics.trackEvent('branch_changed', { branchId });

  // Update state
  setCurrentBranchId(branchId);

  // Load related data
  loadBranchItems(branchId);
}

function handleVersionChange(versionId: string) {
  // Fetch version details
  loadVersionDetails(versionId);

  // Update URL
  updateUrlParams({ version: versionId });

  // Emit event for other components
  eventBus.emit('versionChanged', { versionId });
}
```

## Error Boundaries

```typescript
import { ErrorBoundary } from '@/components/layout/ErrorBoundary';

function PageWithTemporal() {
  return (
    <ErrorBoundary fallback={<TemporalNavigatorFallback />}>
      <TemporalNavigator
        // ... props ...
      />
    </ErrorBoundary>
  );
}

function TemporalNavigatorFallback() {
  return (
    <div className="p-4 bg-red-50 text-red-700 rounded">
      <p>Failed to load temporal navigation</p>
    </div>
  );
}
```

## Performance Optimization

### Memoization

```typescript
import { useMemo } from 'react';

function OptimizedComponent() {
  const branches = useMemo(() => branches, [branches]);
  const versions = useMemo(() => versions, [versions]);

  return (
    <TemporalNavigator
      branches={branches}
      versions={versions}
      // ... other props ...
    />
  );
}
```

### Lazy Loading

```typescript
import { Suspense, lazy } from 'react';

const TemporalNavigator = lazy(() =>
  import('@/components/temporal').then((m) => ({
    default: m.TemporalNavigator,
  }))
);

function Page() {
  return (
    <Suspense fallback={<TemporalSkeleton />}>
      <TemporalNavigator
        // ... props ...
      />
    </Suspense>
  );
}
```

## Testing Integration

### Unit Tests

```typescript
import { render, screen } from '@testing-library/react';
import { TemporalNavigator } from '@/components/temporal';

describe('TemporalNavigator integration', () => {
  it('renders with data', () => {
    render(
      <TemporalNavigator
        projectId="proj-1"
        branches={mockBranches}
        versions={mockVersions}
        // ... other props ...
      />
    );

    expect(screen.getByText('main')).toBeInTheDocument();
  });
});
```

### E2E Tests

```typescript
import { test, expect } from '@playwright/test';

test('temporal navigation workflow', async ({ page }) => {
  await page.goto('/projects/123');

  // Switch branch
  await page.click('[data-testid=branch-selector]');
  await page.click('text=develop');

  // Select version
  await page.click('text=v1.1.0');

  // Verify URL updated
  expect(page.url()).toContain('branch=develop&version=v1.1.0');
});
```

## Common Issues and Solutions

### Issue: Branches not loading
```typescript
// Solution: Check API endpoint and error handling
const { data, error, isLoading } = useBranches(projectId);

if (error) {
  console.error('Failed to load branches:', error);
}

if (isLoading) {
  return <TemporalSkeleton />;
}
```

### Issue: Merge conflicts not resolved
```typescript
// Solution: Use proper conflict resolution strategy
mergeBranch({
  sourceBranchId,
  targetBranchId,
  conflictResolution: 'manual', // or 'source' or 'target'
});
```

### Issue: Performance lag with many versions
```typescript
// Solution: Implement virtualization
import { FixedSizeList } from 'react-window';

// Or use pagination
useVersions(branchId, { limit: 20, offset: 0 });
```

## Migration Guide

### From Old Version Selection
```typescript
// Old approach
const [version, setVersion] = useState(null);

// New approach with temporal navigator
const [currentVersionId, setCurrentVersionId] = useState('');
const [currentBranchId, setCurrentBranchId] = useState('');
```

## API Reference

See `/src/components/temporal/README.md` for detailed component and hook APIs.

## Support

For issues, questions, or feature requests, see:
- Component documentation: `README.md`
- Storybook: `npm run storybook`
- Tests: `__tests__/` directory

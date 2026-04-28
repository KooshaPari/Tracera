# Specification Views - Quick Reference

## View Components Summary

### ADRListView

```tsx
import { ADRListView } from '@/views';

<ADRListView projectId='proj-123' />;
```

- **What**: List of Architecture Decision Records with filtering
- **Where**: `/specifications/adrs`
- **Actions**: Create, search, filter by status/date, view details
- **Views**: Cards, Timeline, Graph

### ADRDetailView

```tsx
import { ADRDetailView } from '@/views';

<ADRDetailView adrId='adr-123' />;
```

- **What**: Single ADR in MADR format with edit capabilities
- **Where**: `/adr/:adrId`
- **Sections**: Context, Decision, Consequences, Options, History
- **Sidebar**: Compliance score, drivers, requirements, tags

### ContractListView

```tsx
import { ContractListView } from '@/views';

<ContractListView projectId='proj-123' />;
```

- **What**: API and function contracts with verification status
- **Where**: `/specifications/contracts`
- **Types**: API, function, invariant, data, integration
- **Status**: draft, active, verified, violated, deprecated

### FeatureListView

```tsx
import { FeatureListView } from '@/views';

<FeatureListView projectId='proj-123' />;
```

- **What**: BDD features with scenario counts and pass rates
- **Where**: `/specifications/features`
- **Stats**: Total scenarios, pass/fail/pending counts
- **Filtering**: By status, search by name

### FeatureDetailView (v2)

```tsx
import { FeatureDetailView as FeatureDetailViewV2 } from '@/views';

<FeatureDetailViewV2 featureId='feat-123' />;
```

- **What**: Feature with scenarios and Gherkin editor
- **Where**: `/feature/:featureId`
- **Actions**: Create/edit/delete scenarios, run all tests
- **Gherkin**: Full editor with syntax support

### SpecificationsDashboardView

```tsx
import { SpecificationsDashboardView } from '@/views';

<SpecificationsDashboardView projectId='proj-123' />;
```

- **What**: Overview of all specifications with health metrics
- **Where**: `/specifications/dashboard`
- **Tabs**: Coverage, Gaps, Health, Activity
- **Cards**: Navigate to ADRs, Contracts, Features

---

## Common Patterns

### Filter Implementation

```tsx
const filteredItems = useMemo(() => {
  return items.filter((item) => {
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
    const matchesQuery = item.title.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesQuery;
  });
}, [items, statusFilter, searchQuery]);
```

### Create Modal

```tsx
{
  showCreateModal && (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      <div
        className='fixed inset-0 bg-black/50 backdrop-blur-sm'
        onClick={() => setShowCreateModal(false)}
      />
      <div className='relative w-full max-w-2xl rounded-xl border bg-background p-6'>
        {/* Form content */}
      </div>
    </div>
  );
}
```

### Loading State

```tsx
if (isLoading) {
  return (
    <div className='p-6 space-y-8 animate-pulse'>
      <Skeleton className='h-10 w-48' />
      {[1, 2, 3, 4, 5].map((i) => (
        <Skeleton key={i} className='h-32 rounded-xl' />
      ))}
    </div>
  );
}
```

### Empty State

```tsx
{
  filteredItems.length > 0 ? (
    <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>{/* Items */}</div>
  ) : (
    <Card className='border-none bg-muted/20 py-12'>
      <div className='flex flex-col items-center justify-center text-muted-foreground/40'>
        <IconComponent className='h-12 w-12 mb-4' />
        <p className='text-sm font-medium'>No items found</p>
      </div>
    </Card>
  );
}
```

---

## State Management

### useADRs Hook

```tsx
const { data: adrsData, isLoading } = useADRs(projectId);
const adrs = Array.isArray(adrsData) ? adrsData : [];
```

### useCreateADR Mutation

```tsx
const createADR = useCreateADR();

const handleCreate = async () => {
  await createADR.mutateAsync({
    projectId,
    title: newTitle,
    status: newStatus,
    context: newContext,
    decision: newDecision,
    date: new Date().toISOString(),
  });
};
```

---

## Navigation

### Using useNavigate

```tsx
import { useNavigate } from '@tanstack/react-router';

const navigate = useNavigate();

// Navigate to detail view
navigate({ to: `/adr/${adr.id}` });

// Navigate with search params
navigate({ to: '/specifications/adrs', search: { status: 'accepted' } });
```

### Using useSearch

```tsx
import { useSearch } from '@tanstack/react-router';

const searchParams = useSearch({ strict: false });
const statusFilter = searchParams?.status || 'all';
```

---

## Styling Quick Tips

### Status Badge Colors

```typescript
const statusColors = {
  proposed: 'bg-yellow-500/10 text-yellow-600',
  accepted: 'bg-green-500/10 text-green-600',
  deprecated: 'bg-gray-500/10 text-gray-600',
  superseded: 'bg-orange-500/10 text-orange-600',
  rejected: 'bg-red-500/10 text-red-600',
};
```

### Summary Card Gradients

```tsx
// Blue for ADRs
className =
  'bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-950/20 dark:to-blue-900/20';

// Green for Contracts
className =
  'bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-950/20 dark:to-green-900/20';

// Purple for Features
className =
  'bg-gradient-to-br from-purple-50 to-purple-100/50 dark:from-purple-950/20 dark:to-purple-900/20';
```

### Filter Bar

```tsx
<Card className='p-3 border-none bg-muted/30 rounded-2xl flex flex-wrap items-center gap-3'>
  {/* Filters */}
</Card>
```

---

## Toast Notifications

```tsx
import { toast } from 'sonner';

// Success
toast.success('Item created successfully');

// Error
toast.error('Failed to create item');

// Custom
toast('Custom message');
```

---

## Common Imports

```typescript
// UI Components
import {
  Badge,
  Button,
  Card,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Skeleton,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@tracertm/ui';

// Icons
import {
  Plus,
  Search,
  Filter,
  ArrowLeft,
  Edit2,
  Save,
  Trash2,
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
} from 'lucide-react';

// Utilities
import { useNavigate, useSearch, useParams } from '@tanstack/react-router';
import { useQuery, useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';
import { useState, useMemo } from 'react';
import { format } from 'date-fns';

// Hooks
import { useADRs, useCreateADR, useContracts, useFeatures } from '@/hooks/useSpecifications';

// Components
import { ADRCard } from '@/components/specifications/adr/ADRCard';
import { ContractCard } from '@/components/specifications/contracts/ContractCard';
import { FeatureCard } from '@/components/specifications/bdd/FeatureCard';
import { SpecificationDashboard } from '@/components/specifications/dashboard/SpecificationDashboard';
```

---

## Data Type Reference

### ADR

```typescript
type ADRStatus = 'proposed' | 'accepted' | 'deprecated' | 'superseded' | 'rejected';

interface ADR {
  id: string;
  projectId: string;
  adrNumber: string;
  title: string;
  status: ADRStatus;
  context?: string;
  decision?: string;
  consequences?: string;
  date: string;
  tags?: string[];
  complianceScore?: number;
  relatedRequirements?: string[];
  decisionDrivers?: string[];
  consideredOptions?: Option[];
  supersedes?: string;
  supersededBy?: string;
  version: number;
  createdAt: string;
  updatedAt: string;
}
```

### Contract

```typescript
type ContractStatus = 'draft' | 'active' | 'verified' | 'violated' | 'deprecated';

interface Contract {
  id: string;
  projectId: string;
  itemId: string;
  contractNumber: string;
  title: string;
  contractType: 'api' | 'function' | 'invariant' | 'data' | 'integration';
  status: ContractStatus;
  description?: string;
  preconditions?: Condition[];
  postconditions?: Condition[];
  invariants?: Condition[];
  states?: State[];
  verificationResult?: VerificationResult;
  lastVerifiedAt?: string;
  version: number;
  createdAt: string;
  updatedAt: string;
}
```

### Feature

```typescript
type FeatureStatus = 'draft' | 'active' | 'deprecated' | 'archived';

interface Feature {
  id: string;
  projectId: string;
  featureNumber: string;
  name: string;
  description?: string;
  asA?: string;
  iWant?: string;
  soThat?: string;
  status: FeatureStatus;
  scenarioCount: number;
  passedScenarios: number;
  failedScenarios: number;
  pendingScenarios: number;
  tags?: string[];
  version: number;
  createdAt: string;
  updatedAt: string;
}
```

### Scenario

```typescript
type ScenarioStatus = 'pending' | 'passing' | 'failing';

interface Scenario {
  id: string;
  featureId: string;
  scenarioNumber: string;
  title: string;
  gherkinText: string;
  status: ScenarioStatus;
  executionCount: number;
  passRate: number;
  givenSteps: string[];
  whenSteps: string[];
  thenSteps: string[];
  isOutline: boolean;
  version: number;
  createdAt: string;
  updatedAt: string;
}
```

---

## Troubleshooting Checklist

- [ ] Data loading? Check `useADRs`, `useContracts`, `useFeatures` return values
- [ ] Filters not working? Verify `useMemo` dependencies
- [ ] Modal not opening? Check `showModal` state initialization
- [ ] API call failing? Verify mock data or API endpoint
- [ ] Search not finding items? Check `toLowerCase()` in filter logic
- [ ] Types missing? Verify imports from `@tracertm/types`
- [ ] Styling off? Check `rounded-xl`, `rounded-2xl`, spacing classes
- [ ] Navigation broken? Verify route paths in `useNavigate`

---

## Next Steps

1. Connect views to actual API endpoints
2. Implement create/update/delete mutations
3. Add error boundary wrapper
4. Set up route guards for auth
5. Add analytics tracking
6. Implement pagination for large datasets
7. Add bulk operations
8. Create print/export functionality

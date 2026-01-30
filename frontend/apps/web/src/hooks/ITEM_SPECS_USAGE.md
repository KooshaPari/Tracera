# Item Specs Hooks Documentation

Complete React Query hooks for managing enhanced Item specifications with full CRUD, specialized queries, optimistic updates, and cache invalidation.

## Overview

The `useItemSpecs` hook library provides TanStack Query integration for 6 spec types:

1. **RequirementSpec** - Detailed requirements with EARS format, risk assessment, quality metrics
2. **TestSpec** - Test specifications with flakiness detection, quarantine management, health reports
3. **EpicSpec** - Epic-level specifications with business value, dependencies, objectives
4. **UserStorySpec** - User stories with acceptance criteria, story points, parent epics
5. **TaskSpec** - Implementation tasks with checklists, subtasks, dependencies
6. **DefectSpec** - Defect tracking with severity, reproduction steps, root cause analysis

## Key Features

- Full CRUD operations (Create, Read, Update, Delete)
- Specialized queries (flaky tests, high-risk requirements, filtered by status, etc.)
- Optimistic updates with automatic cache invalidation
- Proper query key management for cache isolation
- Type-safe TypeScript interfaces
- Automatic query invalidation on mutations
- Bulk operation support with `X-Bulk-Operation` header

## Quick Start

### Import Hooks

```typescript
import {
  useRequirementSpecs,
  useTestSpecs,
  useEpicSpecs,
  useUserStorySpecs,
  useTaskSpecs,
  useDefectSpecs,
  itemSpecKeys,
} from '@/hooks';
```

### Basic Usage Examples

#### Requirement Specs

```typescript
// Fetch all requirements
const { data, isLoading } = useRequirementSpecs(projectId);

// Fetch requirements with filters
const { data } = useRequirementSpecs(projectId, {
  requirementType: 'ubiquitous',
  riskLevel: 'high',
  verificationStatus: 'unverified',
  limit: 50,
  offset: 0,
});

// Fetch specific requirement
const { data: spec } = useRequirementSpec(projectId, specId);

// Fetch requirement by item
const { data: spec } = useRequirementSpecByItem(projectId, itemId);

// Fetch unverified requirements
const { data } = useUnverifiedRequirements(projectId, limit);

// Fetch high-risk requirements
const { data } = useHighRiskRequirements(projectId, limit);

// Create requirement
const createMutation = useCreateRequirementSpec(projectId);
await createMutation.mutateAsync({
  item_id: 'item-123',
  requirement_type: 'ubiquitous',
  constraint_type: 'hard',
  risk_level: 'medium',
  business_value: 85,
  stakeholders: ['alice@example.com'],
});

// Update requirement
const updateMutation = useUpdateRequirementSpec(projectId);
await updateMutation.mutateAsync({
  specId: 'spec-123',
  data: {
    verification_status: 'verified',
    verified_at: new Date().toISOString(),
  },
});

// Delete requirement
const deleteMutation = useDeleteRequirementSpec(projectId);
await deleteMutation.mutateAsync('spec-123');

// Analyze quality
const analyzeQuality = useAnalyzeRequirementQuality(projectId);
await analyzeQuality.mutateAsync('spec-123');

// Analyze impact
const analyzeImpact = useAnalyzeRequirementImpact(projectId);
await analyzeImpact.mutateAsync('spec-123');

// Verify requirement
const verify = useVerifyRequirement(projectId);
await verify.mutateAsync({
  specId: 'spec-123',
  evidenceType: 'test_case',
  evidenceReference: 'TC-456',
  description: 'Verified by test case TC-456',
});
```

#### Test Specs

```typescript
// Fetch all tests
const { data } = useTestSpecs(projectId);

// Fetch tests with filters
const { data } = useTestSpecs(projectId, {
  testType: 'unit',
  isQuarantined: false,
  limit: 100,
});

// Fetch flaky tests
const { data } = useFlakyTests(projectId, 0.2, 50); // threshold, limit

// Fetch quarantined tests
const { data } = useQuarantinedTests(projectId, 50);

// Fetch test health report
const { data: report } = useTestHealthReport(projectId);
// Returns: {
//   total_tests: 500,
//   flaky_count: 15,
//   quarantined_count: 3,
//   total_runs: 5000,
//   pass_rate: 0.95,
//   average_duration_ms: 1250,
//   health_score: 0.92
// }

// Create test
const createTest = useCreateTestSpec(projectId);
await createTest.mutateAsync({
  item_id: 'item-123',
  test_type: 'unit',
  test_framework: 'jest',
  test_file_path: 'src/__tests__/auth.test.ts',
  preconditions: ['Mock API server running'],
  verifies_requirements: ['req-456'],
  performance_baseline_ms: 100,
  performance_threshold_ms: 500,
});

// Record test run
const recordRun = useRecordTestRun(projectId);
await recordRun.mutateAsync({
  specId: 'spec-123',
  status: 'passed',
  durationMs: 245,
  environment: 'ci',
});

// Quarantine test (for flaky tests)
const quarantine = useQuarantineTest(projectId);
await quarantine.mutateAsync({
  specId: 'spec-123',
  reason: 'Intermittent network timeout in CI',
});

// Unquarantine test
const unquarantine = useUnquarantineTest(projectId);
await unquarantine.mutateAsync('spec-123');
```

#### Epic Specs

```typescript
// Fetch all epics
const { data } = useEpicSpecs(projectId);

// Fetch epics by status
const { data } = useEpicSpecs(projectId, {
  status: 'in_progress',
  limit: 25,
});

// Fetch specific epic
const { data: epic } = useEpicSpec(projectId, specId);

// Create epic
const createEpic = useCreateEpicSpec(projectId);
await createEpic.mutateAsync({
  item_id: 'item-123',
  epic_name: 'Authentication System Overhaul',
  business_value: 95,
  target_release: 'v2.0',
  objectives: [
    'Improve security',
    'Reduce authentication latency',
  ],
  success_criteria: [
    'Pass security audit',
    'Auth latency < 200ms',
  ],
  stakeholders: ['security-lead@example.com'],
  constraints: ['Must use OAuth 2.0', 'GDPR compliant'],
});

// Update epic
const updateEpic = useUpdateEpicSpec(projectId);
await updateEpic.mutateAsync({
  specId: 'spec-123',
  data: {
    status: 'completed',
    end_date: new Date().toISOString(),
  },
});
```

#### User Story Specs

```typescript
// Fetch all user stories
const { data } = useUserStorySpecs(projectId);

// Fetch stories by status
const { data } = useUserStorySpecs(projectId, {
  status: 'in_progress',
});

// Fetch stories for epic
const { data } = useUserStorySpecs(projectId, {
  epicId: 'epic-123',
});

// Create story
const createStory = useCreateUserStorySpec(projectId);
await createStory.mutateAsync({
  item_id: 'item-123',
  as_a: 'developer',
  i_want: 'to integrate SSO',
  so_that: 'users can login with corporate credentials',
  story_points: 8,
  acceptance_criteria: [
    { criterion: 'OIDC provider configured' },
    { criterion: 'User mapping completed' },
    { criterion: 'Token refresh working' },
  ],
  definition_of_done: [
    'Code reviewed',
    'Tests passing',
    'Docs updated',
  ],
  priority: 1,
  parent_epic: 'epic-456',
});

// Update story
const updateStory = useUpdateUserStorySpec(projectId);
await updateStory.mutateAsync({
  specId: 'spec-123',
  data: {
    status: 'done',
    story_points: 8,
    acceptance_criteria: [
      { criterion: 'OIDC provider configured', completed: true },
      { criterion: 'User mapping completed', completed: true },
      { criterion: 'Token refresh working', completed: true },
    ],
  },
});
```

#### Task Specs

```typescript
// Fetch all tasks
const { data } = useTaskSpecs(projectId);

// Fetch tasks by status
const { data } = useTaskSpecs(projectId, {
  status: 'in_progress',
});

// Fetch tasks for story
const { data } = useTaskSpecs(projectId, {
  storyId: 'story-123',
});

// Create task
const createTask = useCreateTaskSpec(projectId);
await createTask.mutateAsync({
  item_id: 'item-123',
  task_title: 'Implement OAuth provider integration',
  description: 'Configure and test OAuth 2.0 provider',
  priority: 1,
  estimated_hours: 4,
  parent_story: 'story-456',
  dependencies: ['task-789'],
});

// Update task
const updateTask = useUpdateTaskSpec(projectId);
await updateTask.mutateAsync({
  specId: 'task-123',
  data: {
    status: 'done',
    actual_hours: 3.5,
  },
});
```

#### Defect Specs

```typescript
// Fetch all defects
const { data } = useDefectSpecs(projectId);

// Fetch critical defects
const { data } = useDefectSpecs(projectId, {
  severity: 'critical',
  status: 'new',
});

// Create defect
const createDefect = useCreateDefectSpec(projectId);
await createDefect.mutateAsync({
  item_id: 'item-123',
  defect_title: 'Login fails on Safari',
  description: 'OIDC callback not processed',
  severity: 'critical',
  environment: 'production',
  steps_to_reproduce: [
    '1. Open Safari browser',
    '2. Click Login',
    '3. Complete SSO flow',
    '4. Not redirected back to app',
  ],
  expected_behavior: 'User logged in and redirected to dashboard',
  actual_behavior: 'Blank page, console shows error',
  priority: 1,
  reported_by: 'qa-team@example.com',
});

// Update defect
const updateDefect = useUpdateDefectSpec(projectId);
await updateDefect.mutateAsync({
  specId: 'defect-123',
  data: {
    status: 'resolved',
    root_cause: 'Safari blocking third-party cookies',
    resolution: 'Updated SameSite attribute to None',
  },
});
```

## Query Key Management

All hooks use a factory pattern for consistent query key management:

```typescript
import { itemSpecKeys } from '@/hooks';

// Manually invalidate requirements
queryClient.invalidateQueries({
  queryKey: itemSpecKeys.requirements(projectId),
});

// Manually invalidate flaky tests
queryClient.invalidateQueries({
  queryKey: itemSpecKeys.flakyTests(projectId),
});

// Manually invalidate all specs
queryClient.invalidateQueries({
  queryKey: itemSpecKeys.all,
});
```

## Mutation Patterns

### Optimistic Updates

```typescript
const updateMutation = useUpdateRequirementSpec(projectId);

// Mutations automatically invalidate related queries
await updateMutation.mutateAsync({
  specId: 'spec-123',
  data: { verification_status: 'verified' },
});

// All related queries are refreshed:
// - useRequirementSpecs(projectId)
// - useRequirementSpec(projectId, specId)
// - useRequirementSpecByItem(projectId, itemId)
// - useUnverifiedRequirements(projectId)
```

### Cascade Invalidation

When updating specs with relationships, cascading invalidation occurs:

```typescript
const updateStory = useUpdateUserStorySpec(projectId);

// Invalidates:
// - User story queries
// - Parent epic queries
// - Task queries (if tasks link to story)
await updateStory.mutateAsync({
  specId: 'story-123',
  data: { status: 'done' },
});
```

## Error Handling

All hooks follow consistent error patterns:

```typescript
const { data, isLoading, error, isError } = useRequirementSpecs(projectId);

if (isError) {
  return <ErrorBoundary error={error?.message} />;
}

if (isLoading) {
  return <Skeleton />;
}

return <SpecsList specs={data.specs} />;
```

For mutations:

```typescript
const createMutation = useCreateRequirementSpec(projectId);

const handleCreate = async (formData) => {
  try {
    const result = await createMutation.mutateAsync(formData);
    toast.success('Created requirement');
    return result;
  } catch (error) {
    toast.error(error.message);
  }
};
```

## Performance Optimization

### Pagination

```typescript
const [page, setPage] = useState(0);

const { data } = useRequirementSpecs(projectId, {
  limit: 50,
  offset: page * 50,
});

// Results: { specs: [...], total: 1250 }
```

### Filtering

```typescript
// Only fetch high-risk requirements
const { data } = useHighRiskRequirements(projectId, 100);

// Only fetch flaky tests
const { data } = useFlakyTests(projectId, 0.2, 50);

// Filter by multiple criteria
const { data } = useRequirementSpecs(projectId, {
  requirementType: 'complex',
  riskLevel: 'critical',
  verificationStatus: 'failed',
});
```

### Bulk Operations

Queries include the `X-Bulk-Operation: true` header to skip rate limiting:

```typescript
// Fast bulk fetch (no rate limiting)
const { data } = useTestSpecs(projectId, { limit: 500 });
```

## Type Safety

All types are exported and strongly typed:

```typescript
import type {
  RequirementSpec,
  TestSpec,
  EpicSpec,
  UserStorySpec,
  TaskSpec,
  DefectSpec,
  RequirementType,
  RiskLevel,
  VerificationStatus,
  TestType,
  TestResultStatus,
  EpicStatus,
  UserStoryStatus,
  TaskStatus,
  DefectSeverity,
  DefectStatus,
} from '@/hooks';

const spec: RequirementSpec = {
  id: 'spec-123',
  item_id: 'item-456',
  requirement_type: 'ubiquitous',
  // ... all fields typed
};
```

## Cache Invalidation Strategy

Mutations automatically invalidate related queries:

1. **Create mutations** invalidate list queries and stats
2. **Update mutations** invalidate list, detail, and related queries
3. **Delete mutations** invalidate list and stats
4. **Action mutations** (verify, analyze, quarantine) invalidate detail and derived queries

Example:

```typescript
// Creating a requirement automatically invalidates:
await createRequirementSpec.mutateAsync(data);
// Invalidated:
// - itemSpecKeys.requirements(projectId)
// - itemSpecKeys.stats(projectId)

// Verifying a requirement invalidates:
await verifyRequirement.mutateAsync(...);
// Invalidated:
// - itemSpecKeys.requirements(projectId)
// - itemSpecKeys.unverifiedRequirements(projectId)
// - itemSpecKeys.requirement(projectId, specId)
```

## Advanced Usage

### Dependent Queries

```typescript
// Only fetch epic details after epic is loaded
const { data: epic } = useEpicSpec(projectId, epicId);
const { data: stories } = useUserStorySpecs(projectId, {
  epicId: epic?.id, // Only fetches when epic is available
});
```

### Combining Hooks

```typescript
function RequirementsDashboard({ projectId }) {
  const unverified = useUnverifiedRequirements(projectId);
  const highRisk = useHighRiskRequirements(projectId);

  return (
    <>
      <UnverifiedCount count={unverified.data?.total} />
      <HighRiskList specs={highRisk.data?.specs} />
    </>
  );
}
```

### Custom Cache Updates

```typescript
const queryClient = useQueryClient();

// Manually update cache after external change
queryClient.setQueryData(
  itemSpecKeys.requirement(projectId, specId),
  updatedSpec
);
```

## Testing

Mock the hooks in tests:

```typescript
import { useRequirementSpecs } from '@/hooks';
import { vi } from 'vitest';

vi.mock('@/hooks', () => ({
  useRequirementSpecs: vi.fn(() => ({
    data: { specs: [...], total: 10 },
    isLoading: false,
    error: null,
  })),
}));
```

## Migration from REST API

If migrating from direct REST API calls:

```typescript
// Before
const response = await fetch('/api/v1/projects/proj-123/item-specs/requirements');
const data = await response.json();

// After
const { data } = useRequirementSpecs('proj-123');

// Benefits:
// - Automatic caching
// - Optimistic updates
// - Deduplication
// - Background refetching
// - Type safety
// - Automatic error handling
```

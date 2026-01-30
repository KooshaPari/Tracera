# Item Specs Hooks - Quick Reference

## Import

```typescript
import {
  // Requirements
  useRequirementSpecs,
  useRequirementSpec,
  useRequirementSpecByItem,
  useUnverifiedRequirements,
  useHighRiskRequirements,
  useCreateRequirementSpec,
  useUpdateRequirementSpec,
  useDeleteRequirementSpec,
  useAnalyzeRequirementQuality,
  useAnalyzeRequirementImpact,
  useVerifyRequirement,

  // Tests
  useTestSpecs,
  useTestSpec,
  useTestSpecByItem,
  useFlakyTests,
  useQuarantinedTests,
  useTestHealthReport,
  useCreateTestSpec,
  useUpdateTestSpec,
  useDeleteTestSpec,
  useRecordTestRun,
  useQuarantineTest,
  useUnquarantineTest,

  // Epics
  useEpicSpecs,
  useEpicSpec,
  useEpicSpecByItem,
  useCreateEpicSpec,
  useUpdateEpicSpec,
  useDeleteEpicSpec,

  // User Stories
  useUserStorySpecs,
  useUserStorySpec,
  useUserStorySpecByItem,
  useCreateUserStorySpec,
  useUpdateUserStorySpec,
  useDeleteUserStorySpec,

  // Tasks
  useTaskSpecs,
  useTaskSpec,
  useTaskSpecByItem,
  useCreateTaskSpec,
  useUpdateTaskSpec,
  useDeleteTaskSpec,

  // Defects
  useDefectSpecs,
  useDefectSpec,
  useDefectSpecByItem,
  useCreateDefectSpec,
  useUpdateDefectSpec,
  useDeleteDefectSpec,

  // Types
  type RequirementSpec,
  type TestSpec,
  type EpicSpec,
  type UserStorySpec,
  type TaskSpec,
  type DefectSpec,
  type RequirementType,
  type TestType,
  type RiskLevel,
  type VerificationStatus,
  type TestResultStatus,
  type EpicStatus,
  type UserStoryStatus,
  type TaskStatus,
  type DefectSeverity,
  type DefectStatus,

  // Query Keys
  itemSpecKeys,
} from '@/hooks';
```

## Common Patterns

### List with Filters
```typescript
const { data, isLoading } = useRequirementSpecs(projectId, {
  riskLevel: 'high',
  verificationStatus: 'unverified',
});
```

### Single Spec
```typescript
const { data: spec } = useRequirementSpec(projectId, specId);
```

### Create
```typescript
const mutation = useCreateRequirementSpec(projectId);
await mutation.mutateAsync({ item_id, requirement_type, ... });
```

### Update
```typescript
const mutation = useUpdateRequirementSpec(projectId);
await mutation.mutateAsync({ specId, data: { ... } });
```

### Delete
```typescript
const mutation = useDeleteRequirementSpec(projectId);
await mutation.mutateAsync(specId);
```

## Requirement Specs

| Hook | Purpose |
|------|---------|
| `useRequirementSpecs()` | List all requirements with filters |
| `useRequirementSpec()` | Get single requirement |
| `useRequirementSpecByItem()` | Get requirement for item |
| `useUnverifiedRequirements()` | Get unverified requirements |
| `useHighRiskRequirements()` | Get high-risk requirements |
| `useCreateRequirementSpec()` | Create requirement |
| `useUpdateRequirementSpec()` | Update requirement |
| `useDeleteRequirementSpec()` | Delete requirement |
| `useAnalyzeRequirementQuality()` | Analyze quality metrics |
| `useAnalyzeRequirementImpact()` | Analyze impact |
| `useVerifyRequirement()` | Verify with evidence |

### Filters
```typescript
{
  requirementType?: 'ubiquitous' | 'event_driven' | 'state_driven' | 'optional' | 'complex' | 'unwanted',
  riskLevel?: 'critical' | 'high' | 'medium' | 'low' | 'minimal',
  verificationStatus?: 'unverified' | 'pending' | 'verified' | 'failed' | 'expired',
  limit?: number,
  offset?: number,
}
```

## Test Specs

| Hook | Purpose |
|------|---------|
| `useTestSpecs()` | List all tests with filters |
| `useTestSpec()` | Get single test |
| `useTestSpecByItem()` | Get test for item |
| `useFlakyTests()` | Get flaky tests |
| `useQuarantinedTests()` | Get quarantined tests |
| `useTestHealthReport()` | Get health metrics |
| `useCreateTestSpec()` | Create test |
| `useUpdateTestSpec()` | Update test |
| `useDeleteTestSpec()` | Delete test |
| `useRecordTestRun()` | Record test execution |
| `useQuarantineTest()` | Quarantine flaky test |
| `useUnquarantineTest()` | Unquarantine test |

### Filters
```typescript
{
  testType?: 'unit' | 'integration' | 'e2e' | 'performance' | 'security' | 'accessibility' | 'contract' | 'mutation' | 'fuzz' | 'property',
  isQuarantined?: boolean,
  limit?: number,
  offset?: number,
}
```

### Test Health Report
```typescript
{
  total_tests: number,
  flaky_count: number,
  quarantined_count: number,
  total_runs: number,
  pass_rate: number,
  average_duration_ms: number,
  health_score: number,
}
```

## Epic Specs

| Hook | Purpose |
|------|---------|
| `useEpicSpecs()` | List all epics with filters |
| `useEpicSpec()` | Get single epic |
| `useEpicSpecByItem()` | Get epic for item |
| `useCreateEpicSpec()` | Create epic |
| `useUpdateEpicSpec()` | Update epic |
| `useDeleteEpicSpec()` | Delete epic |

### Filters
```typescript
{
  status?: 'backlog' | 'in_progress' | 'completed' | 'archived',
  limit?: number,
  offset?: number,
}
```

## User Story Specs

| Hook | Purpose |
|------|---------|
| `useUserStorySpecs()` | List all stories with filters |
| `useUserStorySpec()` | Get single story |
| `useUserStorySpecByItem()` | Get story for item |
| `useCreateUserStorySpec()` | Create story |
| `useUpdateUserStorySpec()` | Update story |
| `useDeleteUserStorySpec()` | Delete story |

### Filters
```typescript
{
  status?: 'backlog' | 'ready' | 'in_progress' | 'review' | 'done' | 'archived',
  epicId?: string,
  limit?: number,
  offset?: number,
}
```

## Task Specs

| Hook | Purpose |
|------|---------|
| `useTaskSpecs()` | List all tasks with filters |
| `useTaskSpec()` | Get single task |
| `useTaskSpecByItem()` | Get task for item |
| `useCreateTaskSpec()` | Create task |
| `useUpdateTaskSpec()` | Update task |
| `useDeleteTaskSpec()` | Delete task |

### Filters
```typescript
{
  status?: 'todo' | 'in_progress' | 'review' | 'done' | 'blocked',
  storyId?: string,
  limit?: number,
  offset?: number,
}
```

## Defect Specs

| Hook | Purpose |
|------|---------|
| `useDefectSpecs()` | List all defects with filters |
| `useDefectSpec()` | Get single defect |
| `useDefectSpecByItem()` | Get defect for item |
| `useCreateDefectSpec()` | Create defect |
| `useUpdateDefectSpec()` | Update defect |
| `useDeleteDefectSpec()` | Delete defect |

### Filters
```typescript
{
  severity?: 'critical' | 'major' | 'minor' | 'trivial',
  status?: 'new' | 'assigned' | 'in_progress' | 'resolved' | 'verified' | 'closed' | 'reopened',
  limit?: number,
  offset?: number,
}
```

## Common Usage Examples

### Fetch and Display
```typescript
function RequirementsList({ projectId }) {
  const { data, isLoading, error } = useRequirementSpecs(projectId);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {data.specs.map(spec => (
        <li key={spec.id}>{spec.id}</li>
      ))}
    </ul>
  );
}
```

### Create Form
```typescript
function CreateRequirementForm({ projectId }) {
  const mutation = useCreateRequirementSpec(projectId);
  const [formData, setFormData] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await mutation.mutateAsync({
        item_id: formData.itemId,
        requirement_type: formData.type,
        risk_level: formData.riskLevel,
      });
      setFormData({});
    } catch (err) {
      console.error('Failed:', err);
    }
  };

  return <form onSubmit={handleSubmit}>{/* fields */}</form>;
}
```

### Filter and Search
```typescript
function FilteredRequirements({ projectId }) {
  const [riskLevel, setRiskLevel] = useState('high');
  const { data } = useHighRiskRequirements(projectId, 100);

  return (
    <>
      <select value={riskLevel} onChange={e => setRiskLevel(e.target.value)}>
        <option value="high">High Risk</option>
        <option value="medium">Medium Risk</option>
      </select>
      <SpecsList specs={data.specs} />
    </>
  );
}
```

### Test Monitoring
```typescript
function TestDashboard({ projectId }) {
  const health = useTestHealthReport(projectId);
  const flaky = useFlakyTests(projectId, 0.2);

  return (
    <div>
      <div>Health Score: {health.data?.health_score}</div>
      <div>Flaky Tests: {flaky.data?.total}</div>
    </div>
  );
}
```

## Mutation Status

All mutations return objects with:
```typescript
{
  data?: T,
  error?: Error,
  isLoading: boolean,
  isPending: boolean,
  mutate: (vars) => void,
  mutateAsync: (vars) => Promise<T>,
}
```

## Query Status

All queries return objects with:
```typescript
{
  data?: T,
  error?: Error,
  isLoading: boolean,
  isFetching: boolean,
  isError: boolean,
  isSuccess: boolean,
}
```

## Cache Keys

Manually invalidate with:
```typescript
import { itemSpecKeys } from '@/hooks';

// All requirements
queryClient.invalidateQueries({
  queryKey: itemSpecKeys.requirements(projectId),
});

// All tests
queryClient.invalidateQueries({
  queryKey: itemSpecKeys.tests(projectId),
});

// Everything
queryClient.invalidateQueries({
  queryKey: itemSpecKeys.all,
});
```

## Error Handling

```typescript
const mutation = useCreateRequirementSpec(projectId);

try {
  const result = await mutation.mutateAsync(data);
} catch (error) {
  // Error is automatically thrown
  // Common: "Failed to create requirement spec"
  console.error(error.message);
}
```

## Type Safety

All hooks are fully typed:
```typescript
// Input types
type RequirementSpecCreate = {
  item_id: string;
  requirement_type?: RequirementType;
  constraint_type?: ConstraintType;
  risk_level?: RiskLevel;
  // ...
};

// Output types
type RequirementSpec = {
  id: string;
  item_id: string;
  requirement_type: RequirementType;
  // ...
};
```

# Contract Components Quick Reference

## Import All Components

```typescript
import {
  ContractCard,
  ContractEditor,
  ConditionList,
  StateMachineViewer,
  VerificationBadge,
  PassVerificationBadge,
  FailVerificationBadge,
  PendingVerificationBadge,
  UnverifiedBadge,
} from '@/components/specifications/contracts';
```

## Component Cheat Sheet

### ContractCard - Display summary

```tsx
<ContractCard
  contract={contract}
  onClick={() => navigate(`/contracts/${contract.id}`)}
  isSelected={selectedId === contract.id}
/>
```

**Props:**

- `contract: Contract` (required)
- `onClick?: () => void`
- `className?: string`
- `isSelected?: boolean`

---

### ContractEditor - Create/Edit

```tsx
<ContractEditor
  initialData={editingContract}
  onSave={async (data) => await api.updateContract(data)}
  onCancel={() => setEditing(false)}
/>
```

**Props:**

- `initialData?: Partial<Contract>`
- `onSave: (data: Partial<Contract>) => Promise<void>` (required)
- `onCancel: () => void` (required)

---

### ConditionList - Display conditions

```tsx
<ConditionList
  preconditions={contract.preconditions}
  postconditions={contract.postconditions}
  invariants={contract.invariants}
  onConditionClick={(cond) => setSelected(cond)}
/>
```

**Props:**

- `preconditions?: ContractCondition[]`
- `postconditions?: ContractCondition[]`
- `invariants?: ContractCondition[]`
- `onConditionClick?: (condition: ContractCondition) => void`
- `className?: string`

---

### StateMachineViewer - Visualize states

```tsx
<StateMachineViewer
  states={contract.states}
  initialState={contract.initialState}
  currentState={currentState}
  transitions={contract.transitions}
  onStateSelect={setCurrentState}
  onTransitionTrigger={async (trans) => executeTransition(trans)}
  isExecutable={true}
/>
```

**Props:**

- `states?: string[]`
- `initialState?: string`
- `currentState?: string`
- `transitions?: ContractTransition[]`
- `onStateSelect?: (state: string) => void`
- `onTransitionTrigger?: (transition: ContractTransition) => Promise<void>`
- `isExecutable?: boolean`
- `className?: string`

---

### VerificationBadge - Show status

```tsx
<VerificationBadge
  status={contract.verificationResult?.status || 'unknown'}
  lastVerifiedAt={contract.lastVerifiedAt}
  passedCount={passed}
  failedCount={failed}
  totalCount={total}
  showTimestamp={true}
  showDetails={true}
/>
```

**Status Values:** `"pass" | "fail" | "pending" | "error" | "unknown"`

**Props:**

- `status: VerificationStatus` (required)
- `lastVerifiedAt?: string`
- `details?: string`
- `passedCount?: number`
- `failedCount?: number`
- `totalCount?: number`
- `showTimestamp?: boolean`
- `showDetails?: boolean`
- `className?: string`

---

### Preset Badges

**PassVerificationBadge**

```tsx
<PassVerificationBadge lastVerifiedAt={contract.lastVerifiedAt} passedCount={10} totalCount={10} />
```

**FailVerificationBadge**

```tsx
<FailVerificationBadge
  lastVerifiedAt={contract.lastVerifiedAt}
  passedCount={8}
  failedCount={2}
  totalCount={10}
  details='Array bounds check failed'
/>
```

**PendingVerificationBadge**

```tsx
<PendingVerificationBadge lastVerifiedAt={contract.lastVerifiedAt} />
```

**UnverifiedBadge**

```tsx
<UnverifiedBadge />
```

---

## Common Patterns

### Create Contract

```typescript
const handleCreate = async (data: Partial<Contract>) => {
  const result = await api.contracts.create.mutate(data);
  navigate(`/contracts/${result.id}`);
};

<ContractEditor onSave={handleCreate} onCancel={() => navigate(-1)} />
```

### Edit Contract

```typescript
const [editing, setEditing] = useState<Contract>();

const handleSave = async (data: Partial<Contract>) => {
  await api.contracts.update.mutate({ id: editing.id, ...data });
  setEditing(null);
};

{editing && (
  <ContractEditor
    initialData={editing}
    onSave={handleSave}
    onCancel={() => setEditing(null)}
  />
)}
```

### Display Contract

```typescript
<div className="space-y-6">
  <h1>{contract.title}</h1>
  <VerificationBadge status={contract.verificationResult?.status} />
  <ConditionList {...contract} />
  {contract.states && <StateMachineViewer {...contract} />}
</div>
```

### List Contracts

```typescript
<div className="grid gap-4 grid-cols-3">
  {contracts.map((contract) => (
    <ContractCard
      key={contract.id}
      contract={contract}
      onClick={() => navigate(`/contracts/${contract.id}`)}
    />
  ))}
</div>
```

---

## Type Reference

### Contract

```typescript
interface Contract {
  id: string;
  projectId: string;
  itemId: string;
  contractNumber: string; // CONTRACT-001
  title: string;
  description?: string;
  contractType: ContractType; // api|function|invariant|data|integration
  status: ContractStatus; // draft|active|verified|violated|deprecated
  preconditions: ContractCondition[];
  postconditions: ContractCondition[];
  invariants: ContractCondition[];
  states?: string[];
  initialState?: string;
  transitions?: ContractTransition[];
  executableSpec?: string;
  specLanguage?: 'typescript' | 'python' | 'gherkin';
  lastVerifiedAt?: string;
  verificationResult?: {
    status: 'pass' | 'fail' | 'error';
    passedConditions: number;
    failedConditions: number;
    details?: string;
  };
  tags?: string[];
  metadata?: Record<string, unknown>;
  version: number;
  createdAt: string;
  updatedAt: string;
}
```

### ContractCondition

```typescript
interface ContractCondition {
  id: string;
  description: string;
  expression?: string; // Optional formal expression
  isRequired: boolean;
  lastVerifiedResult?: 'pass' | 'fail' | 'skip';
}
```

### ContractTransition

```typescript
interface ContractTransition {
  id: string;
  fromState: string;
  toState: string;
  trigger: string;
  guards?: string[];
  actions?: string[];
}
```

---

## Styling with Tailwind

All components work with Tailwind CSS:

```tsx
// Add custom spacing
<div className="space-y-6">
  <ContractCard contract={contract} className="w-full" />
</div>

// Use responsive classes
<div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {contracts.map(c => <ContractCard key={c.id} contract={c} />)}
</div>

// Dark mode support (built-in)
<div className="dark:bg-slate-900">
  <ContractCard contract={contract} />
</div>
```

---

## Animation Timing

| Component     | Animation          | Duration   |
| ------------- | ------------------ | ---------- |
| ContractCard  | Fade in + slide up | 200ms      |
| Conditions    | Staggered fade in  | 200ms each |
| State Machine | Scale transitions  | 200ms      |
| Verification  | Pulse (pending)    | 2s cycle   |
| Tooltip       | Fade in            | 200ms      |

---

## Accessibility

All components include:

- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus indicators
- Color contrast (WCAG AA)
- Screen reader support

---

## Performance Tips

1. **Memoize Props**: Use `useMemo` for condition lists
2. **Lazy Load**: Use React.lazy for editor
3. **Pagination**: Split large condition lists
4. **Debounce**: Debounce form input changes
5. **Keys**: Always provide keys in lists

---

## Common Issues & Solutions

### "Contract type is not assignable"

**Solution**: Ensure `contractType` is one of: `api | function | invariant | data | integration`

### "Verification status is unknown"

**Solution**: Set `verificationResult` when verification completes

### "State machine not showing"

**Solution**: Provide `states` array with at least 2 states and `transitions`

### "Conditions not appearing"

**Solution**: Ensure arrays are provided (can be empty) not `undefined`

### "Animations stuttering"

**Solution**: Check browser hardware acceleration, reduce animation complexity

---

## Testing with Playwright

```typescript
// Click contract card
await page.click('[data-testid="contract-card"]');

// Fill form
await page.fill('input[id="title"]', 'New Contract');
await page.selectOption('select[id="contractType"]', 'function');

// Add condition
await page.click('button:has-text("Add Condition")');
await page.fill('input:has-text("Describe this condition")', 'Test');

// Select state
await page.click('circle'); // SVG state node

// Verify badge
await page.hover('[data-testid="verification-badge"]');
await page.waitForSelector('text=Verified');
```

---

## Environment Variables

No specific environment variables required. Components use:

- React context (if needed)
- Props for configuration
- Tailwind CSS variables for theming

---

## File Locations

```
frontend/apps/web/src/components/specifications/contracts/
├── ContractCard.tsx
├── ContractEditor.tsx
├── ConditionList.tsx
├── StateMachineViewer.tsx
├── VerificationBadge.tsx
├── index.ts
├── README.md
├── IMPLEMENTATION_SUMMARY.md
├── TYPES_AND_PATTERNS.md
└── QUICK_REFERENCE.md (this file)
```

---

## Related Documentation

- **README.md** - Full component documentation
- **IMPLEMENTATION_SUMMARY.md** - Architecture details
- **TYPES_AND_PATTERNS.md** - Type examples and patterns
- **@tracertm/types** - Type definitions

---

## Version Info

- **React**: 18.0+
- **TypeScript**: 5.0+
- **Framer Motion**: 10.16.4+
- **Tailwind CSS**: 3.0+

**Last Updated**: January 29, 2026
**Status**: Production Ready ✓

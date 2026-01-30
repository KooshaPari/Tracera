# Contract Components: Types and Patterns

## Type Definitions Reference

All types are imported from `@tracertm/types`:

### Contract Interface
```typescript
interface Contract {
  id: string;
  projectId: string;
  itemId: string;
  contractNumber: string; // CONTRACT-001
  title: string;
  description?: string;
  contractType: ContractType; // api | function | invariant | data | integration
  status: ContractStatus; // draft | active | verified | violated | deprecated

  // Conditions
  preconditions: ContractCondition[];
  postconditions: ContractCondition[];
  invariants: ContractCondition[];

  // State Machine
  states?: string[];
  initialState?: string;
  transitions?: ContractTransition[];

  // Executable Specification
  executableSpec?: string;
  specLanguage?: "typescript" | "python" | "gherkin";

  // Verification
  lastVerifiedAt?: string;
  verificationResult?: {
    status: "pass" | "fail" | "error";
    passedConditions: number;
    failedConditions: number;
    details?: string;
  };

  // Metadata
  tags?: string[];
  metadata?: Record<string, unknown>;
  version: number;
  createdAt: string;
  updatedAt: string;
}
```

### ContractCondition Interface
```typescript
interface ContractCondition {
  id: string;
  description: string;
  expression?: string; // Formal expression (optional)
  isRequired: boolean;
  lastVerifiedResult?: "pass" | "fail" | "skip";
}
```

### ContractTransition Interface
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

### Enums

#### ContractType
```typescript
type ContractType = "api" | "function" | "invariant" | "data" | "integration";
```

#### ContractStatus
```typescript
type ContractStatus = "draft" | "active" | "verified" | "violated" | "deprecated";
```

## Component Prop Patterns

### ContractCard Props
```typescript
interface ContractCardProps {
  contract: Contract;           // Required contract data
  onClick?: () => void;         // Click handler
  className?: string;           // Additional CSS classes
  isSelected?: boolean;         // Selection state
}
```

**Usage Pattern:**
```tsx
const [selectedId, setSelectedId] = useState<string>();

return (
  <div className="grid gap-4">
    {contracts.map((contract) => (
      <ContractCard
        key={contract.id}
        contract={contract}
        isSelected={selectedId === contract.id}
        onClick={() => setSelectedId(contract.id)}
      />
    ))}
  </div>
);
```

### ContractEditor Props
```typescript
interface ContractEditorProps {
  initialData?: Partial<Contract>;              // Pre-fill form
  onSave: (data: Partial<Contract>) => Promise<void>; // Save handler
  onCancel: () => void;                         // Cancel handler
}
```

**Usage Pattern:**
```tsx
const [editingId, setEditingId] = useState<string>();
const contract = contracts.find(c => c.id === editingId);

return (
  <ContractEditor
    key={editingId}
    initialData={contract}
    onSave={async (data) => {
      await api.updateContract(editingId, data);
      setEditingId(undefined);
      await refetchContracts();
    }}
    onCancel={() => setEditingId(undefined)}
  />
);
```

### ConditionList Props
```typescript
interface ConditionListProps {
  preconditions?: ContractCondition[];
  postconditions?: ContractCondition[];
  invariants?: ContractCondition[];
  onConditionClick?: (condition: ContractCondition) => void;
  className?: string;
}
```

**Usage Pattern:**
```tsx
const [selectedCondition, setSelectedCondition] = useState<ContractCondition>();

return (
  <ConditionList
    preconditions={contract.preconditions}
    postconditions={contract.postconditions}
    invariants={contract.invariants}
    onConditionClick={setSelectedCondition}
    className="flex-1"
  />
);
```

### StateMachineViewer Props
```typescript
interface StateMachineViewerProps {
  states?: string[];
  initialState?: string;
  currentState?: string;
  transitions?: ContractTransition[];
  onStateSelect?: (state: string) => void;
  onTransitionTrigger?: (transition: ContractTransition) => Promise<void>;
  isExecutable?: boolean;
  className?: string;
}
```

**Usage Pattern:**
```tsx
const [currentState, setCurrentState] = useState(contract.initialState);

return (
  <StateMachineViewer
    states={contract.states}
    initialState={contract.initialState}
    currentState={currentState}
    transitions={contract.transitions}
    onStateSelect={setCurrentState}
    onTransitionTrigger={async (trans) => {
      await executeTransition(trans);
      setCurrentState(trans.toState);
    }}
    isExecutable={contract.status === "active"}
  />
);
```

### VerificationBadge Props
```typescript
interface VerificationBadgeProps {
  status: VerificationStatus;
  lastVerifiedAt?: string | undefined;
  details?: string | undefined;
  passedCount?: number | undefined;
  failedCount?: number | undefined;
  totalCount?: number | undefined;
  showTimestamp?: boolean | undefined;
  showDetails?: boolean | undefined;
  className?: string | undefined;
}

type VerificationStatus = "pass" | "fail" | "pending" | "error" | "unknown";
```

**Usage Pattern:**
```tsx
const result = contract.verificationResult;

return (
  <VerificationBadge
    status={result?.status || "unknown"}
    lastVerifiedAt={contract.lastVerifiedAt}
    passedCount={result?.passedConditions}
    failedCount={result?.failedConditions}
    totalCount={
      (contract.preconditions?.length || 0) +
      (contract.postconditions?.length || 0) +
      (contract.invariants?.length || 0)
    }
    showTimestamp={true}
    showDetails={true}
  />
);
```

## Common Patterns

### Pattern 1: Create Contract
```typescript
async function createContract(data: Partial<Contract>) {
  const result = await api.contracts.create.mutate({
    title: data.title,
    contractType: data.contractType,
    description: data.description,
    preconditions: data.preconditions || [],
    postconditions: data.postconditions || [],
    invariants: data.invariants || [],
    states: data.states,
    transitions: data.transitions,
    executableSpec: data.executableSpec,
    specLanguage: data.specLanguage,
  });
  return result;
}

// In component
<ContractEditor
  onSave={async (data) => {
    try {
      const created = await createContract(data);
      showSuccess(`Contract ${created.contractNumber} created`);
      navigate(`/contracts/${created.id}`);
    } catch (error) {
      showError(error.message);
    }
  }}
  onCancel={() => navigate(-1)}
/>
```

### Pattern 2: Edit Contract
```typescript
async function updateContract(id: string, data: Partial<Contract>) {
  const result = await api.contracts.update.mutate({ id, ...data });
  return result;
}

// In component
const handleEdit = (contract: Contract) => {
  setEditingContract(contract);
};

const handleSave = async (data: Partial<Contract>) => {
  try {
    const updated = await updateContract(editingContract.id, data);
    setContracts(contracts.map(c => c.id === updated.id ? updated : c));
    setEditingContract(null);
    showSuccess("Contract updated");
  } catch (error) {
    showError(error.message);
  }
};

<ContractEditor
  key={editingContract.id}
  initialData={editingContract}
  onSave={handleSave}
  onCancel={() => setEditingContract(null)}
/>
```

### Pattern 3: Display Contract
```typescript
export function ContractView({ contract }: { contract: Contract }) {
  const [selectedCondition, setSelectedCondition] = useState<ContractCondition>();
  const [currentState, setCurrentState] = useState(contract.initialState);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold">{contract.title}</h1>
          <p className="text-sm text-muted-foreground mt-1">{contract.description}</p>
        </div>
        <VerificationBadge
          status={contract.verificationResult?.status || "unknown"}
          lastVerifiedAt={contract.lastVerifiedAt}
          totalCount={
            (contract.preconditions?.length || 0) +
            (contract.postconditions?.length || 0) +
            (contract.invariants?.length || 0)
          }
        />
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Conditions */}
        <div className="col-span-2">
          <ConditionList
            preconditions={contract.preconditions}
            postconditions={contract.postconditions}
            invariants={contract.invariants}
            onConditionClick={setSelectedCondition}
          />
        </div>

        {/* Condition Details */}
        {selectedCondition && (
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold">{selectedCondition.description}</h3>
            {selectedCondition.expression && (
              <pre className="mt-4 text-xs bg-muted p-2 rounded overflow-auto">
                {selectedCondition.expression}
              </pre>
            )}
          </div>
        )}
      </div>

      {/* State Machine */}
      {contract.states && contract.states.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold mb-4">State Machine</h2>
          <StateMachineViewer
            states={contract.states}
            initialState={contract.initialState}
            currentState={currentState}
            transitions={contract.transitions}
            onStateSelect={setCurrentState}
            isExecutable={contract.status === "active"}
          />
        </div>
      )}
    </div>
  );
}
```

### Pattern 4: Contract List
```typescript
export function ContractsList() {
  const { data: contracts } = useQuery(
    ["contracts"],
    () => api.contracts.list.query()
  );
  const [selectedId, setSelectedId] = useState<string>();

  if (!contracts) return <LoadingSpinner />;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Contracts</h1>
        <Button onClick={() => navigate("/contracts/new")}>
          Create Contract
        </Button>
      </div>

      {contracts.length === 0 ? (
        <EmptyState
          title="No contracts"
          description="Create your first contract to get started"
          action={<Button onClick={() => navigate("/contracts/new")}>Create Contract</Button>}
        />
      ) : (
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {contracts.map((contract) => (
            <ContractCard
              key={contract.id}
              contract={contract}
              isSelected={selectedId === contract.id}
              onClick={() => navigate(`/contracts/${contract.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
```

### Pattern 5: Verification Status Handling
```typescript
function getVerificationColor(
  status: Contract["verificationResult"]["status"] | undefined
): string {
  switch (status) {
    case "pass":
      return "text-green-600";
    case "fail":
      return "text-red-600";
    case "error":
      return "text-orange-600";
    default:
      return "text-gray-600";
  }
}

function renderVerificationIndicator(contract: Contract) {
  if (!contract.verificationResult) {
    return <span className="text-gray-500">Never verified</span>;
  }

  const percentage =
    (contract.verificationResult.passedConditions /
      (contract.verificationResult.passedConditions +
       contract.verificationResult.failedConditions)) * 100;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">Verification</span>
        <VerificationBadge
          status={contract.verificationResult.status}
          passedCount={contract.verificationResult.passedConditions}
          failedCount={contract.verificationResult.failedConditions}
          totalCount={
            contract.verificationResult.passedConditions +
            contract.verificationResult.failedConditions
          }
        />
      </div>
      <ProgressBar value={percentage} />
    </div>
  );
}
```

## Type Guard Patterns

### Safe Contract Type Checking
```typescript
function isValidContract(data: unknown): data is Contract {
  return (
    typeof data === "object" &&
    data !== null &&
    "id" in data &&
    "title" in data &&
    "contractType" in data &&
    "status" in data
  );
}

// Usage
if (isValidContract(contractData)) {
  // TypeScript now knows contractData is Contract
  renderContractCard(contractData);
}
```

### Condition Type Checking
```typescript
function isPrecondition(condition: ContractCondition, type: string): boolean {
  return type === "precondition";
}

function getConditionColor(type: string): string {
  switch (type) {
    case "precondition":
      return "blue";
    case "postcondition":
      return "green";
    case "invariant":
      return "purple";
    default:
      return "gray";
  }
}
```

## State Management Patterns

### Using Zustand with Contracts
```typescript
import { create } from "zustand";

interface ContractStore {
  contracts: Contract[];
  selectedId: string | null;
  editingId: string | null;

  setContracts: (contracts: Contract[]) => void;
  selectContract: (id: string) => void;
  startEditing: (id: string) => void;
  stopEditing: () => void;
  updateContract: (id: string, data: Partial<Contract>) => void;
}

export const useContractStore = create<ContractStore>((set) => ({
  contracts: [],
  selectedId: null,
  editingId: null,

  setContracts: (contracts) => set({ contracts }),
  selectContract: (id) => set({ selectedId: id }),
  startEditing: (id) => set({ editingId: id }),
  stopEditing: () => set({ editingId: null }),
  updateContract: (id, data) =>
    set((state) => ({
      contracts: state.contracts.map((c) =>
        c.id === id ? { ...c, ...data } : c
      ),
    })),
}));
```

## Async/Await Patterns

### Verification Flow
```typescript
async function verifyContract(contract: Contract): Promise<void> {
  try {
    // Show loading state
    setIsVerifying(true);

    // Execute verification
    const result = await api.contracts.verify.mutate({ id: contract.id });

    // Update contract with verification result
    setContract({
      ...contract,
      verificationResult: result.verificationResult,
      lastVerifiedAt: new Date().toISOString(),
    });

    // Show success notification
    showNotification({
      type: "success",
      title: "Verification Complete",
      message: `${result.verificationResult.passedConditions}/${
        result.verificationResult.passedConditions +
        result.verificationResult.failedConditions
      } conditions verified`,
    });
  } catch (error) {
    showNotification({
      type: "error",
      title: "Verification Failed",
      message: error.message,
    });
  } finally {
    setIsVerifying(false);
  }
}
```

## Error Handling Patterns

### Form Validation Errors
```typescript
interface FormErrors {
  title?: string;
  contractType?: string;
  preconditions?: string[];
  [key: string]: string | string[] | undefined;
}

function validateContract(data: Partial<Contract>): FormErrors {
  const errors: FormErrors = {};

  if (!data.title?.trim()) {
    errors.title = "Title is required";
  }

  if (!data.contractType) {
    errors.contractType = "Contract type is required";
  }

  return errors;
}

// Usage in component
const handleSubmit = async (data: Partial<Contract>) => {
  const errors = validateContract(data);

  if (Object.keys(errors).length > 0) {
    setFormErrors(errors);
    return;
  }

  await onSave(data);
};
```

## Testing Patterns

### Unit Test Template
```typescript
import { render, screen } from "@testing-library/react";
import { ContractCard } from "./ContractCard";
import type { Contract } from "@tracertm/types";

const mockContract: Contract = {
  id: "1",
  projectId: "proj-1",
  itemId: "item-1",
  contractNumber: "CONTRACT-001",
  title: "Test Contract",
  contractType: "function",
  status: "active",
  preconditions: [],
  postconditions: [],
  invariants: [],
  version: 1,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

describe("ContractCard", () => {
  it("renders contract information", () => {
    render(<ContractCard contract={mockContract} />);

    expect(screen.getByText("Test Contract")).toBeInTheDocument();
    expect(screen.getByText("CONTRACT-001")).toBeInTheDocument();
    expect(screen.getByText("active")).toBeInTheDocument();
  });

  it("calls onClick handler when clicked", async () => {
    const onClick = vi.fn();
    const { user } = render(
      <ContractCard contract={mockContract} onClick={onClick} />
    );

    await user.click(screen.getByRole("button", { name: /view contract/i }));
    expect(onClick).toHaveBeenCalled();
  });
});
```

## Best Practices

1. **Always type your props**: Use the component interfaces
2. **Handle loading states**: Show appropriate UI during async operations
3. **Validate user input**: Check data before sending to API
4. **Error recovery**: Provide clear error messages and recovery options
5. **Performance**: Memoize expensive calculations and components
6. **Accessibility**: Test with keyboard navigation and screen readers
7. **Testing**: Write tests for user interactions, not just rendering
8. **Documentation**: Keep JSDoc comments for complex logic

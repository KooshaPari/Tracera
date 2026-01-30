# Contract Components

Comprehensive UI components for design-by-contract specifications in TraceRTM. These components provide a complete interface for defining, editing, visualizing, and verifying contract specifications.

## Components Overview

### 1. ContractCard.tsx
Display contract summary information in a card format.

**Features:**
- Contract number and title display
- Type badge (api, function, invariant, data, integration)
- Status indicators (draft, active, verified, violated, deprecated)
- Condition counts with visual icons
- State machine indicator
- Verification badge with tooltip
- Executable spec indicator
- Selection state styling

**Props:**
```typescript
interface ContractCardProps {
  contract: Contract;
  onClick?: () => void;
  className?: string;
  isSelected?: boolean;
}
```

**Usage:**
```tsx
<ContractCard
  contract={myContract}
  onClick={() => navigate(`/contracts/${myContract.id}`)}
  isSelected={selectedId === myContract.id}
/>
```

### 2. ContractEditor.tsx
Visual contract builder for creating and editing contracts.

**Features:**
- Basic contract information (title, type, description)
- Condition builder with multiple tabs:
  - Preconditions
  - Postconditions
  - Invariants
- Each condition supports:
  - Description
  - Expression (optional formal expression)
  - Required/optional flag
  - Individual add/remove actions
- State machine definition:
  - State management
  - Transition definition with triggers, guards, and actions
- Executable specification editor with language selection (TypeScript, Python, Gherkin)
- Save/cancel actions with loading state

**Props:**
```typescript
interface ContractEditorProps {
  initialData?: Partial<Contract>;
  onSave: (data: Partial<Contract>) => Promise<void>;
  onCancel: () => void;
}
```

**Usage:**
```tsx
<ContractEditor
  initialData={existingContract}
  onSave={async (data) => {
    await api.updateContract(data);
  }}
  onCancel={() => setEditMode(false)}
/>
```

### 3. ConditionList.tsx
Display preconditions, postconditions, and invariants with visual grouping.

**Features:**
- Grouped display by condition type
- Visual icons for each type:
  - Blue shield for preconditions
  - Green shield for postconditions
  - Purple shield for invariants
- Severity indicators (critical, high, medium, low)
- Verification status (pass, fail, skip, undefined)
- Expression syntax highlighting
- Optional/required indicators
- Required/optional badge
- Empty state message
- Hover interactions

**Props:**
```typescript
interface ConditionListProps {
  preconditions?: ContractCondition[];
  postconditions?: ContractCondition[];
  invariants?: ContractCondition[];
  onConditionClick?: (condition: ContractCondition) => void;
  className?: string;
}
```

**Usage:**
```tsx
<ConditionList
  preconditions={contract.preconditions}
  postconditions={contract.postconditions}
  invariants={contract.invariants}
  onConditionClick={(cond) => openConditionDetail(cond)}
/>
```

### 4. StateMachineViewer.tsx
Interactive state diagram visualization with execution capabilities.

**Features:**
- SVG-based state diagram:
  - Circular state layout
  - Curved transition arrows with labels
  - Self-loop support for reflexive transitions
- State nodes with:
  - Current state highlighting
  - Initial state indicator (green dashed circle)
  - Available transitions indicator (yellow dot)
  - Click to select state
- Transition display with:
  - From/to states
  - Trigger event name
  - Optional guards and actions
  - Hover effects
- Current state details panel:
  - Selected state info
  - Available transitions list
  - Click-to-trigger execution (if enabled)
  - Animated transitions
- Empty state message
- Initial state information display

**Props:**
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

**Usage:**
```tsx
<StateMachineViewer
  states={contract.states}
  initialState={contract.initialState}
  currentState={currentState}
  transitions={contract.transitions}
  onStateSelect={(state) => setCurrentState(state)}
  onTransitionTrigger={async (trans) => {
    await executeTransition(trans);
  }}
  isExecutable={true}
/>
```

### 5. VerificationBadge.tsx
Display contract verification status with detailed tooltip.

**Features:**
- Status types: pass, fail, pending, error, unknown
- Visual indicators with icons and colors
- Pulsing animation for pending status
- Tooltip with:
  - Pass/fail counts
  - Total condition count
  - Details message
  - Last verified timestamp
  - Relative time formatting (e.g., "2h ago")
- Hover effects
- Optional timestamp display
- Optional detail display

**Preset Components:**
- `PassVerificationBadge` - For successful verification
- `FailVerificationBadge` - For failed verification with details
- `PendingVerificationBadge` - For in-progress verification
- `UnverifiedBadge` - For never-verified contracts

**Props:**
```typescript
interface VerificationBadgeProps {
  status: "pass" | "fail" | "pending" | "error" | "unknown";
  lastVerifiedAt?: string;
  details?: string;
  passedCount?: number;
  failedCount?: number;
  totalCount?: number;
  showTimestamp?: boolean;
  showDetails?: boolean;
  className?: string;
}
```

**Usage:**
```tsx
<VerificationBadge
  status={contract.verificationResult?.status || "unknown"}
  lastVerifiedAt={contract.lastVerifiedAt}
  passedCount={contract.verificationResult?.passedConditions}
  failedCount={contract.verificationResult?.failedConditions}
  totalCount={totalConditionCount}
  showTimestamp={true}
  showDetails={true}
/>
```

Or use presets:
```tsx
<PassVerificationBadge
  lastVerifiedAt={contract.lastVerifiedAt}
  passedCount={10}
  totalCount={10}
/>

<FailVerificationBadge
  lastVerifiedAt={contract.lastVerifiedAt}
  passedCount={8}
  failedCount={2}
  totalCount={10}
  details="Array bounds check failed"
/>
```

## Barrel Export

All components are exported from `index.ts`:

```typescript
export { ContractCard } from "./ContractCard";
export { ContractEditor } from "./ContractEditor";
export { ConditionList } from "./ConditionList";
export { StateMachineViewer } from "./StateMachineViewer";
export {
  VerificationBadge,
  PassVerificationBadge,
  FailVerificationBadge,
  PendingVerificationBadge,
  UnverifiedBadge,
} from "./VerificationBadge";
```

## Example: Complete Contract View

```tsx
import { useState } from "react";
import {
  ContractCard,
  ContractEditor,
  ConditionList,
  StateMachineViewer,
  VerificationBadge,
} from "@/components/specifications/contracts";
import type { Contract } from "@tracertm/types";

export function ContractDetailView({ contractId }: { contractId: string }) {
  const [contract, setContract] = useState<Contract | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [currentState, setCurrentState] = useState<string | undefined>();

  const handleSave = async (data: Partial<Contract>) => {
    const updated = await api.updateContract(contractId, data);
    setContract(updated);
    setIsEditing(false);
  };

  if (!contract) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header with verification status */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">{contract.title}</h1>
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

      {/* Editor or Display */}
      {isEditing ? (
        <ContractEditor
          initialData={contract}
          onSave={handleSave}
          onCancel={() => setIsEditing(false)}
        />
      ) : (
        <div className="grid gap-6">
          {/* Conditions */}
          <ConditionList
            preconditions={contract.preconditions}
            postconditions={contract.postconditions}
            invariants={contract.invariants}
          />

          {/* State Machine */}
          {contract.states && contract.states.length > 0 && (
            <StateMachineViewer
              states={contract.states}
              initialState={contract.initialState}
              currentState={currentState}
              transitions={contract.transitions}
              onStateSelect={setCurrentState}
            />
          )}

          {/* Edit Button */}
          <button onClick={() => setIsEditing(true)}>
            Edit Contract
          </button>
        </div>
      )}
    </div>
  );
}
```

## Styling

All components use:
- **shadcn/ui** for base components (Button, Card, Badge, Select, Input, Textarea, Tabs, Tooltip)
- **Tailwind CSS** for styling and responsive design
- **framer-motion** for animations and transitions
- **lucide-react** for icons

## Type Support

All components are fully typed with TypeScript and support the following types from `@tracertm/types`:

- `Contract`
- `ContractCondition`
- `ContractTransition`
- `ContractType`
- `ContractStatus`

## Animation Details

### ContractCard
- Entrance: Fade in + slide up (200ms)
- Status badge: Scale on hover (1.05x)
- Smooth transitions for all state changes

### ConditionList
- Condition items: Fade in + slide left (200ms)
- Staggered animations for multiple conditions
- Smooth color transitions on hover

### StateMachineViewer
- State nodes: Scale animation for current state
- Transitions: Hover effects on arrows
- Smooth layout transitions

### VerificationBadge
- Pending status: Pulsing opacity (2s cycle)
- Tooltip: Fade in on hover (200ms)
- Background highlight on hover

## Accessibility

- Semantic HTML structure
- ARIA labels for interactive elements
- Keyboard navigation support
- Color contrast compliance
- Focus management in forms
- Descriptive button and link text

## Responsive Design

All components are responsive:
- **Mobile**: Single column, compact spacing
- **Tablet**: Two column layouts where applicable
- **Desktop**: Full layouts with optimal spacing

Hidden responsive elements:
- State machine on mobile (when narrow)
- Detailed labels on small screens (abbreviated versions shown)
- Icon-only mode for conditions list on mobile

## Performance Considerations

- Memoization of condition lists for large contracts
- Efficient SVG rendering in state machine viewer
- Lazy loading of executable spec editor
- Optimized animations with `will-change` CSS hints
- Debounced form input handling in editor

## Dependencies

External libraries:
- `framer-motion` - 10.16.4+ (animations)
- `lucide-react` - Latest (icons)
- `@tracertm/ui` - Local shadcn/ui components
- `@tracertm/types` - Type definitions

## Integration Guide

### With Route Handlers
```typescript
// In your route/page component
import { ContractCard } from "@/components/specifications/contracts";

export default function ContractsPage() {
  const contracts = useQuery(/* ... */);

  return (
    <div className="grid gap-4">
      {contracts.map((contract) => (
        <ContractCard
          key={contract.id}
          contract={contract}
          onClick={() => navigate(`/contracts/${contract.id}`)}
        />
      ))}
    </div>
  );
}
```

### With Forms
```typescript
// In your form component
import { ContractEditor } from "@/components/specifications/contracts";

export function CreateContractForm() {
  const handleSave = async (data) => {
    const result = await trpc.contracts.create.mutate(data);
    showNotification("Contract created successfully");
  };

  return (
    <ContractEditor
      onSave={handleSave}
      onCancel={() => navigate("/contracts")}
    />
  );
}
```

## Known Limitations

- SVG state machine viewer is optimized for up to 10 states
- Condition expression syntax highlighting is basic (plain monospace)
- State machine transitions don't currently support animated state changes
- Verification badge tooltip is limited to 3 lines

## Future Enhancements

- Advanced expression syntax highlighting with CodeMirror
- Animated state transitions with visual feedback
- Condition templating for common patterns
- Batch condition creation
- Contract comparison view
- Export to different formats (PDF, Gherkin, etc.)
- Real-time collaboration indicators

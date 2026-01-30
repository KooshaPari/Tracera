# ADR (Architecture Decision Records) Components

Comprehensive UI component library for managing Architecture Decision Records (ADRs) following the MADR 4.0 format.

## Overview

These components provide a complete solution for visualizing, editing, and managing ADRs with support for:

- **MADR 4.0 Format**: Context, Decision, Consequences structure
- **Decision Drivers**: Track what motivated the decision
- **Considered Options**: Compare pros/cons of alternatives
- **Traceability**: Link ADRs to requirements and other ADRs
- **Compliance**: Track compliance scores and verification
- **Visualization**: Graph-based relationship visualization
- **Timeline**: Chronological view with status filtering

## Components

### ADRCard

Displays a summary card for an ADR with status badge, compliance gauge, and metadata.

```tsx
import { ADRCard } from "@/components/specifications/adr";

<ADRCard
  adr={adrData}
  onClick={() => handleAdrSelect(adrData)}
  compact={false}
  showComplianceGauge={true}
  className="w-full"
/>
```

**Props:**
- `adr: ADR` - The ADR data object
- `onClick?: () => void` - Handler for card clicks
- `className?: string` - Tailwind CSS classes
- `compact?: boolean` - Compact/inline layout (default: false)
- `showComplianceGauge?: boolean` - Display compliance gauge (default: true)

**Features:**
- Status-colored badge (proposed, accepted, deprecated, superseded, rejected)
- Compliance score gauge with color coding
- Context and decision summary with line-clamping
- Metadata indicators for drivers, requirements, and options
- Tag display with overflow indicator

### ADREditor

Comprehensive MADR 4.0 format editor with support for all decision record components.

```tsx
import { ADREditor } from "@/components/specifications/adr";

<ADREditor
  initialData={existingAdr}
  onSave={handleSave}
  onCancel={handleCancel}
  showDecisionDrivers={true}
  showRelatedRequirements={true}
/>
```

**Props:**
- `initialData?: Partial<ADR>` - Pre-fill editor with ADR data
- `onSave: (data: Partial<ADR>) => Promise<void>` - Save handler
- `onCancel: () => void` - Cancel handler
- `showDecisionDrivers?: boolean` - Show decision drivers section (default: true)
- `showRelatedRequirements?: boolean` - Show requirements section (default: true)

**Features:**
- MADR core sections (Context, Decision, Consequences)
- Dynamic list management for decision drivers
- Requirement linking with validation
- Tag management
- Form validation with required fields
- Loading state during save

### ADRTimeline

Chronological visualization of ADRs with filtering and status transitions.

```tsx
import { ADRTimeline } from "@/components/specifications/adr";

<ADRTimeline
  adrs={adrList}
  onADRClick={(adr) => handleAdrClick(adr)}
  className="w-full"
/>
```

**Props:**
- `adrs: ADR[]` - List of ADRs to display
- `onADRClick?: (adr: ADR) => void` - Handler for ADR selection
- `className?: string` - Tailwind CSS classes

**Features:**
- Vertical timeline with year/month grouping
- Status filtering (proposed, accepted, deprecated, superseded, all)
- Sort order toggle (newest/oldest first)
- Expandable cards with full details
- Supersession relationship visualization
- Compliance score display
- Animated transitions

### ADRGraph

Relationship visualization showing supersession chains and dependencies.

```tsx
import { ADRGraph } from "@/components/specifications/adr";

<ADRGraph
  adrs={adrList}
  selectedAdrId={selectedId}
  onAdrSelect={(adr) => handleSelect(adr)}
  className="w-full"
/>
```

**Props:**
- `adrs: ADR[]` - List of ADRs to visualize
- `selectedAdrId?: string` - Currently selected ADR ID
- `onAdrSelect?: (adr: ADR) => void` - Selection handler
- `className?: string` - Tailwind CSS classes

**Features:**
- SVG-based graph visualization
- Automatic layout with topological sorting
- Zoom controls (0.5x - 3x)
- Pan support
- Export graph data as JSON
- Legend and edge type indicators
- Relationship summary for selected ADR
- Color-coded by status

### DecisionMatrix

Comparison table for options with pros/cons and scoring.

```tsx
import { DecisionMatrix } from "@/components/specifications/adr";

<DecisionMatrix
  options={consideredOptions}
  onOptionEdit={(option) => handleEdit(option)}
  onOptionAdd={() => handleAdd()}
  onOptionRemove={(id) => handleRemove(id)}
  editable={true}
  showScoring={true}
  className="w-full"
/>
```

**Props:**
- `options: ADROption[]` - List of options to compare
- `onOptionEdit?: (option: ADROption) => void` - Edit handler
- `onOptionAdd?: () => void` - Add new option handler
- `onOptionRemove?: (optionId: string) => void` - Remove option handler
- `editable?: boolean` - Enable edit/remove actions (default: false)
- `showScoring?: boolean` - Show score column (default: false)
- `className?: string` - Tailwind CSS classes

**Features:**
- Responsive table layout
- "Chosen" option highlighting
- Sort by chosen, most pros, or fewest cons
- Automatic score calculation (pros - cons × 10)
- Edit and remove buttons
- No data state with add button

### ComplianceGauge

Circular gauge showing compliance score with color coding.

```tsx
import { ComplianceGauge } from "@/components/specifications/adr";

<ComplianceGauge
  score={85}
  size={100}
  showLabel={true}
  className="w-24 h-24"
/>
```

**Props:**
- `score: number` - Compliance percentage (0-100)
- `size?: number` - Gauge diameter in pixels (default: 100)
- `showLabel?: boolean` - Display percentage text (default: true)
- `className?: string` - Tailwind CSS classes

**Features:**
- Donut-style progress indicator
- Color coding: Green (≥90%), Yellow (70-89%), Red (<70%)
- Responsive sizing
- Optional label display

## Types

All components use types from `@tracertm/types`:

```typescript
interface ADR {
  id: string;
  projectId: string;
  adrNumber: string; // ADR-0001
  title: string;
  status: ADRStatus;

  // MADR Format
  context: string;
  decision: string;
  consequences: string;

  // Extended
  decisionDrivers?: string[];
  consideredOptions?: ADROption[];
  relatedRequirements?: string[];
  relatedAdrs?: string[];
  supersedes?: string;
  supersededBy?: string;
  complianceScore?: number;

  // Metadata
  deciders?: string[];
  stakeholders?: string[];
  date?: string;
  tags?: string[];
  version: number;
  createdAt: string;
  updatedAt: string;
}

type ADRStatus =
  | "proposed"
  | "accepted"
  | "deprecated"
  | "superseded"
  | "rejected";

interface ADROption {
  id: string;
  title: string;
  description: string;
  pros?: string[];
  cons?: string[];
  isChosen: boolean;
}
```

## Usage Examples

### Creating an ADR

```tsx
import { ADREditor } from "@/components/specifications/adr";
import { useState } from "react";

export function CreateADRModal() {
  const [isOpen, setIsOpen] = useState(false);

  const handleSave = async (data: Partial<ADR>) => {
    const response = await fetch("/api/adrs", {
      method: "POST",
      body: JSON.stringify(data),
    });
    // Handle response
    setIsOpen(false);
  };

  return (
    <>
      <button onClick={() => setIsOpen(true)}>New ADR</button>
      {isOpen && (
        <ADREditor
          onSave={handleSave}
          onCancel={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
```

### Displaying ADRs

```tsx
import { ADRCard, ADRTimeline } from "@/components/specifications/adr";
import { useState } from "react";

export function ADRList({ adrs }: { adrs: ADR[] }) {
  const [view, setView] = useState<"cards" | "timeline">("cards");

  return (
    <>
      <div className="flex gap-2 mb-4">
        <button onClick={() => setView("cards")}>Cards</button>
        <button onClick={() => setView("timeline")}>Timeline</button>
      </div>

      {view === "cards" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {adrs.map((adr) => (
            <ADRCard key={adr.id} adr={adr} />
          ))}
        </div>
      ) : (
        <ADRTimeline adrs={adrs} />
      )}
    </>
  );
}
```

### Visualizing Relationships

```tsx
import { ADRGraph } from "@/components/specifications/adr";
import { useState } from "react";

export function ADRDashboard({ adrs }: { adrs: ADR[] }) {
  const [selected, setSelected] = useState<string | undefined>();

  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="col-span-2">
        <ADRGraph
          adrs={adrs}
          selectedAdrId={selected}
          onAdrSelect={(adr) => setSelected(adr.id)}
        />
      </div>
      <div>
        {selected && (
          <ADRCard
            adr={adrs.find((a) => a.id === selected)!}
            compact={true}
          />
        )}
      </div>
    </div>
  );
}
```

### Comparing Options

```tsx
import { DecisionMatrix } from "@/components/specifications/adr";

export function OptionComparison({ adr }: { adr: ADR }) {
  return (
    <DecisionMatrix
      options={adr.consideredOptions || []}
      editable={false}
      showScoring={true}
    />
  );
}
```

## Styling

All components use:
- **Tailwind CSS** for styling
- **shadcn/ui** components for base elements
- **Lucide React** for icons
- **Recharts** for ComplianceGauge visualization

Customize colors via Tailwind config or inline className overrides.

## Accessibility

Components include:
- Semantic HTML structure
- ARIA labels where appropriate
- Keyboard navigation support
- Focus management
- Color contrast compliance

## Performance

- Memoized calculations in ADRGraph and ADRTimeline
- Lazy rendering of expanded details
- Optimized re-renders with React hooks
- SVG rendering for graph (scalable)

## Best Practices

1. **Always provide a key** when rendering multiple cards
2. **Use compact mode** for dense layouts
3. **Filter ADRs before rendering** large lists
4. **Memoize callbacks** passed to editors
5. **Validate data** before passing to components
6. **Handle loading states** appropriately

## Contributing

When adding new features:
1. Maintain MADR 4.0 format compatibility
2. Update TypeScript types in `@tracertm/types`
3. Add accessibility attributes
4. Include loading/error states
5. Test with various ADR data sizes

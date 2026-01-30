# ADR Components - Implementation Examples

## Quick Start

### Import Components
```typescript
import {
  ADRCard,
  ADREditor,
  ADRTimeline,
  ADRGraph,
  DecisionMatrix,
  ComplianceGauge,
} from "@/components/specifications/adr";
```

## Example 1: Basic ADR Display

**File**: `src/pages/projects/views/ADRListView.tsx`

```typescript
import { ADRCard, ADRTimeline } from "@/components/specifications/adr";
import { useState } from "react";
import type { ADR } from "@tracertm/types";

interface ADRListViewProps {
  adrs: ADR[];
  projectId: string;
}

export function ADRListView({ adrs }: ADRListViewProps) {
  const [view, setView] = useState<"cards" | "timeline">("cards");
  const [selectedId, setSelectedId] = useState<string>();

  return (
    <div className="space-y-6">
      {/* View Toggle */}
      <div className="flex gap-2 border-b pb-4">
        <button
          onClick={() => setView("cards")}
          className={`px-4 py-2 rounded ${
            view === "cards" ? "bg-primary text-white" : "bg-muted"
          }`}
        >
          Cards
        </button>
        <button
          onClick={() => setView("timeline")}
          className={`px-4 py-2 rounded ${
            view === "timeline" ? "bg-primary text-white" : "bg-muted"
          }`}
        >
          Timeline
        </button>
      </div>

      {/* Cards View */}
      {view === "cards" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {adrs.map((adr) => (
            <ADRCard
              key={adr.id}
              adr={adr}
              onClick={() => setSelectedId(adr.id)}
              className={
                selectedId === adr.id ? "ring-2 ring-primary" : ""
              }
            />
          ))}
        </div>
      )}

      {/* Timeline View */}
      {view === "timeline" && (
        <ADRTimeline
          adrs={adrs}
          onADRClick={(adr) => setSelectedId(adr.id)}
        />
      )}
    </div>
  );
}
```

## Example 2: ADR Creation Flow

**File**: `src/components/ADRCreateDialog.tsx`

```typescript
import { ADREditor } from "@/components/specifications/adr";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@tracertm/ui";
import { useState } from "react";
import type { ADR } from "@tracertm/types";

interface ADRCreateDialogProps {
  projectId: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (adr: ADR) => void;
}

export function ADRCreateDialog({
  projectId,
  isOpen,
  onClose,
  onSuccess,
}: ADRCreateDialogProps) {
  const [error, setError] = useState<string>();

  const handleSave = async (data: Partial<ADR>) => {
    try {
      const response = await fetch(`/api/projects/${projectId}/adrs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...data,
          projectId,
          adrNumber: `ADR-${Date.now()}`, // Generate number
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create ADR");
      }

      const adr = await response.json();
      onSuccess?.(adr);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Create Architecture Decision Record</DialogTitle>
        </DialogHeader>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded">
            {error}
          </div>
        )}

        <ADREditor
          onSave={handleSave}
          onCancel={onClose}
          showDecisionDrivers={true}
          showRelatedRequirements={true}
        />
      </DialogContent>
    </Dialog>
  );
}
```

## Example 3: ADR Detail View with Graph

**File**: `src/pages/projects/views/ADRDetailView.tsx`

```typescript
import {
  ADRCard,
  ADREditor,
  ADRGraph,
  DecisionMatrix,
  ComplianceGauge,
} from "@/components/specifications/adr";
import { Card, CardContent, CardHeader, CardTitle } from "@tracertm/ui";
import { useState } from "react";
import type { ADR } from "@tracertm/types";

interface ADRDetailViewProps {
  adr: ADR;
  relatedAdrs: ADR[];
  projectId: string;
}

export function ADRDetailView({
  adr,
  relatedAdrs,
  projectId,
}: ADRDetailViewProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [selectedRelated, setSelectedRelated] = useState<string>();

  const handleSave = async (data: Partial<ADR>) => {
    const response = await fetch(
      `/api/projects/${projectId}/adrs/${adr.id}`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }
    );

    if (response.ok) {
      setIsEditing(false);
      // Refetch data
    }
  };

  const allAdrs = [adr, ...relatedAdrs];

  return (
    <div className="space-y-6">
      {/* Header with Compliance */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">{adr.title}</h1>
          <p className="text-muted-foreground mt-1">{adr.adrNumber}</p>
        </div>

        {adr.complianceScore !== undefined && (
          <ComplianceGauge score={adr.complianceScore} size={120} />
        )}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Editor or Display */}
        <div className="col-span-2">
          {isEditing ? (
            <ADREditor
              initialData={adr}
              onSave={handleSave}
              onCancel={() => setIsEditing(false)}
            />
          ) : (
            <ADRCard adr={adr} className="sticky top-4" />
          )}
        </div>

        {/* Sidebar Info */}
        <div className="space-y-4">
          {/* Status */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Status</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="capitalize font-medium">{adr.status}</span>
              {adr.date && (
                <p className="text-xs text-muted-foreground mt-2">
                  {new Date(adr.date).toLocaleDateString()}
                </p>
              )}
            </CardContent>
          </Card>

          {/* Decision Drivers */}
          {adr.decisionDrivers && adr.decisionDrivers.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">
                  Decision Drivers ({adr.decisionDrivers.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-1 text-xs">
                  {adr.decisionDrivers.map((driver, i) => (
                    <li key={i}>• {driver}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Related Requirements */}
          {adr.relatedRequirements && adr.relatedRequirements.length > 0 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">
                  Requirements ({adr.relatedRequirements.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-1">
                  {adr.relatedRequirements.map((req) => (
                    <span
                      key={req}
                      className="bg-primary/10 text-primary text-xs px-2 py-1 rounded"
                    >
                      {req}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Options Comparison */}
      {adr.consideredOptions && adr.consideredOptions.length > 0 && (
        <DecisionMatrix
          options={adr.consideredOptions}
          editable={isEditing}
          showScoring={true}
        />
      )}

      {/* Relationship Graph */}
      {relatedAdrs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Related Architecture Decisions</CardTitle>
          </CardHeader>
          <CardContent>
            <ADRGraph
              adrs={allAdrs}
              selectedAdrId={selectedRelated || adr.id}
              onAdrSelect={(selected) => setSelectedRelated(selected.id)}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
```

## Example 4: Timeline with Filtering

**File**: `src/components/ADRTimelineFilter.tsx`

```typescript
import { ADRTimeline } from "@/components/specifications/adr";
import { Button } from "@tracertm/ui";
import { useState, useMemo } from "react";
import type { ADR, ADRStatus } from "@tracertm/types";

interface ADRTimelineFilterProps {
  adrs: ADR[];
}

export function ADRTimelineFilter({ adrs }: ADRTimelineFilterProps) {
  const [selectedStatuses, setSelectedStatuses] = useState<ADRStatus[]>([
    "proposed",
    "accepted",
  ]);
  const [yearRange, setYearRange] = useState<[number, number] | undefined>();

  const filtered = useMemo(() => {
    return adrs.filter((adr) => {
      // Status filter
      if (!selectedStatuses.includes(adr.status)) return false;

      // Year filter
      if (yearRange) {
        const year = new Date(adr.date || adr.createdAt).getFullYear();
        if (year < yearRange[0] || year > yearRange[1]) return false;
      }

      return true;
    });
  }, [adrs, selectedStatuses, yearRange]);

  const toggleStatus = (status: ADRStatus) => {
    setSelectedStatuses((prev) =>
      prev.includes(status)
        ? prev.filter((s) => s !== status)
        : [...prev, status]
    );
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="bg-muted p-4 rounded-lg space-y-3">
        <div>
          <h3 className="text-sm font-semibold mb-2">Status</h3>
          <div className="flex flex-wrap gap-2">
            {(
              [
                "proposed",
                "accepted",
                "deprecated",
                "superseded",
                "rejected",
              ] as ADRStatus[]
            ).map((status) => (
              <Button
                key={status}
                variant={
                  selectedStatuses.includes(status)
                    ? "default"
                    : "outline"
                }
                size="sm"
                onClick={() => toggleStatus(status)}
              >
                {status}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Timeline */}
      <ADRTimeline adrs={filtered} />

      {/* Results Summary */}
      <div className="text-sm text-muted-foreground">
        Showing {filtered.length} of {adrs.length} decisions
      </div>
    </div>
  );
}
```

## Example 5: Comparison Dashboard

**File**: `src/pages/projects/views/ADRComparisonView.tsx`

```typescript
import {
  ADRCard,
  ComplianceGauge,
  DecisionMatrix,
} from "@/components/specifications/adr";
import { Card, CardContent, CardHeader, CardTitle } from "@tracertm/ui";
import type { ADR } from "@tracertm/types";

interface ADRComparisonViewProps {
  adrs: ADR[];
}

export function ADRComparisonView({ adrs }: ADRComparisonViewProps) {
  // Get ADRs with options for comparison
  const adrsWithOptions = adrs.filter(
    (a) => a.consideredOptions && a.consideredOptions.length > 0
  );

  // Calculate stats
  const stats = {
    total: adrs.length,
    accepted: adrs.filter((a) => a.status === "accepted").length,
    proposed: adrs.filter((a) => a.status === "proposed").length,
    avgCompliance:
      adrs.filter((a) => a.complianceScore !== undefined).length > 0
        ? adrs
            .filter((a) => a.complianceScore !== undefined)
            .reduce((sum, a) => sum + (a.complianceScore || 0), 0) /
          adrs.filter((a) => a.complianceScore !== undefined).length
        : 0,
  };

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold">{stats.total}</div>
              <div className="text-xs text-muted-foreground">Total ADRs</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {stats.accepted}
              </div>
              <div className="text-xs text-muted-foreground">Accepted</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-600">
                {stats.proposed}
              </div>
              <div className="text-xs text-muted-foreground">Proposed</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold">
                {Math.round(stats.avgCompliance)}%
              </div>
              <div className="text-xs text-muted-foreground">
                Avg Compliance
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top ADRs */}
      <Card>
        <CardHeader>
          <CardTitle>ADRs with Highest Compliance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[...adrs]
              .sort(
                (a, b) =>
                  (b.complianceScore || 0) - (a.complianceScore || 0)
              )
              .slice(0, 3)
              .map((adr) => (
                <div
                  key={adr.id}
                  className="space-y-3 p-4 border rounded-lg"
                >
                  <div className="font-semibold text-sm">{adr.title}</div>
                  {adr.complianceScore !== undefined && (
                    <ComplianceGauge
                      score={adr.complianceScore}
                      size={80}
                    />
                  )}
                </div>
              ))}
          </div>
        </CardContent>
      </Card>

      {/* Options Comparison Matrix */}
      {adrsWithOptions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Decision Options Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {adrsWithOptions.map((adr) => (
              <div key={adr.id}>
                <h3 className="font-semibold mb-3">{adr.title}</h3>
                <DecisionMatrix
                  options={adr.consideredOptions || []}
                  showScoring={true}
                />
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
```

## Example 6: Integration with Forms

**File**: `src/components/ADRFormIntegration.tsx`

```typescript
import { ADREditor } from "@/components/specifications/adr";
import type { ADR } from "@tracertm/types";
import { useCallback, useState } from "react";

interface ADRFormIntegrationProps {
  projectId: string;
  onAdrCreated: (adr: ADR) => void;
}

export function ADRFormIntegration({
  projectId,
  onAdrCreated,
}: ADRFormIntegrationProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = useCallback(
    async (data: Partial<ADR>) => {
      setIsLoading(true);
      setError(null);

      try {
        // Generate next ADR number
        const response = await fetch(
          `/api/projects/${projectId}/adrs/next-number`
        );
        const { nextNumber } = await response.json();

        // Save ADR
        const saveResponse = await fetch(
          `/api/projects/${projectId}/adrs`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              ...data,
              projectId,
              adrNumber: nextNumber,
            }),
          }
        );

        if (!saveResponse.ok) {
          throw new Error("Failed to save ADR");
        }

        const adr = await saveResponse.json();
        onAdrCreated(adr);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Unknown error occurred"
        );
      } finally {
        setIsLoading(false);
      }
    },
    [projectId, onAdrCreated]
  );

  const handleCancel = useCallback(() => {
    // Handle cancel logic
  }, []);

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded">
          {error}
        </div>
      )}

      <ADREditor
        onSave={handleSave}
        onCancel={handleCancel}
      />

      {isLoading && (
        <div className="text-center text-sm text-muted-foreground">
          Saving ADR...
        </div>
      )}
    </div>
  );
}
```

## Styling Examples

### Custom Theme

```typescript
// Override default colors
const customAdrs = adrs.map((adr) => ({
  ...adr,
  className: "rounded-xl shadow-lg border-2 border-purple-500",
}));

<ADRCard
  adr={customAdrs[0]}
  className="hover:shadow-2xl hover:border-purple-600"
/>
```

### Responsive Layouts

```typescript
// Mobile-first responsive
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {adrs.map((adr) => (
    <ADRCard key={adr.id} adr={adr} compact={true} />
  ))}
</div>

// Responsive graph
<div className="w-full h-96 md:h-96 lg:h-screen">
  <ADRGraph adrs={adrs} />
</div>
```

## Error Handling

```typescript
try {
  const result = await onSave(adrData);
  console.log("Saved successfully:", result);
} catch (error) {
  if (error instanceof Error) {
    console.error("Save failed:", error.message);
  }
}
```

---

These examples provide starting points for common use cases. Adapt them to your specific needs and project structure.

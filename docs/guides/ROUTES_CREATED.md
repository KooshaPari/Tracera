# TanStack Router Routes - Specifications Implementation

## Summary

Successfully created 7 TanStack Router route files for specifications management in the frontend application.

## Routes Created

### 1. ADR (Architecture Decision Records) Routes

**File:** `projects.$projectId.adrs.tsx`
- **Path:** `/projects/{projectId}/adrs`
- **Component:** `ADRsPage`
- **View:** `ADRView`
- **Purpose:** List all ADRs for a project

**File:** `projects.$projectId.adrs.$adrId.tsx`
- **Path:** `/projects/{projectId}/adrs/{adrId}`
- **Component:** `ADRDetailPage`
- **View:** `ADRView` (with adrId prop)
- **Purpose:** Display individual ADR details

### 2. Contracts Routes

**File:** `projects.$projectId.contracts.tsx`
- **Path:** `/projects/{projectId}/contracts`
- **Component:** `ContractsPage`
- **View:** `ContractView`
- **Purpose:** List all contracts for a project

**File:** `projects.$projectId.contracts.$contractId.tsx`
- **Path:** `/projects/{projectId}/contracts/{contractId}`
- **Component:** `ContractDetailPage`
- **View:** `ContractView` (with contractId prop)
- **Purpose:** Display individual contract details

### 3. Features Routes

**File:** `projects.$projectId.features.tsx`
- **Path:** `/projects/{projectId}/features`
- **Component:** `FeaturesPage`
- **View:** `FeatureDetailView`
- **Purpose:** List all features for a project

**File:** `projects.$projectId.features.$featureId.tsx`
- **Path:** `/projects/{projectId}/features/{featureId}`
- **Component:** `FeatureDetailPage`
- **View:** `FeatureDetailView` (with featureId prop)
- **Purpose:** Display individual feature details with scenarios

### 4. Specifications Dashboard Route

**File:** `projects.$projectId.specifications.tsx`
- **Path:** `/projects/{projectId}/specifications`
- **Component:** `SpecificationsRoute`
- **View:** `SpecificationDashboard`
- **Purpose:** Unified specifications dashboard showing:
  - ADR summary (total, accepted, proposed, compliance)
  - Contract summary (total, active, verified, violated)
  - Feature summary (total, scenarios, pass rate, coverage)
  - Overall health score with detailed metrics

## Route Pattern

All routes follow the established Atoms.tech pattern:

```typescript
import { createFileRoute } from "@tanstack/react-router";
import { ComponentName } from "@/views/ComponentName";

// @ts-expect-error - Route manually registered in routeTree.gen.ts (plugin disabled)
export const Route = createFileRoute("/projects/$projectId/path")({
	component: PageComponent,
});

function PageComponent() {
	const { projectId, optionalId } = Route.useParams();
	return <ComponentName projectId={projectId} optionalId={optionalId} />;
}
```

## Key Features

- **Parameter Extraction:** All routes properly extract `projectId` and optional detail IDs using `Route.useParams()`
- **TypeScript Support:** Uses `@ts-expect-error` comment as per project convention
- **View Components:** All routes connect to existing view components that handle data fetching
- **Consistency:** Follows the same pattern as existing routes like `projects.$projectId.settings.tsx`
- **Manual Route Registration:** Routes are manually registered in `routeTree.gen.ts` with plugin disabled

## Integration Notes

1. Routes require manual registration in `routeTree.gen.ts`
2. View components (`ADRView`, `ContractView`, `FeatureDetailView`, `SpecificationDashboard`) handle their own data fetching
3. Routes support both list and detail views through optional URL parameters
4. Navigation can be implemented using TanStack Router's navigation utilities

## File Locations

All route files are located in:
```
/frontend/apps/web/src/routes/
```

Files created:
- `projects.$projectId.adrs.tsx`
- `projects.$projectId.adrs.$adrId.tsx`
- `projects.$projectId.contracts.tsx`
- `projects.$projectId.contracts.$contractId.tsx`
- `projects.$projectId.features.tsx`
- `projects.$projectId.features.$featureId.tsx`
- `projects.$projectId.specifications.tsx`

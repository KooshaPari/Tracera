# Specification Views Integration Examples

## Route Configuration Examples

### TanStack Router Setup

```typescript
// src/routes/specifications.tsx
import { createFileRoute } from '@tanstack/react-router'
import {
  ADRListView,
  ADRDetailView,
  ContractListView,
  FeatureListView,
  FeatureDetailViewV2,
  SpecificationsDashboardView,
} from '@/views'

// Specifications Dashboard
export const Route = createFileRoute('/specifications/dashboard')({
  component: SpecificationsDashboardComponent,
  params: {
    projectId: z.string(),
  },
})

function SpecificationsDashboardComponent() {
  const { projectId } = Route.useParams()
  return <SpecificationsDashboardView projectId={projectId} />
}

// ADR List
export const ADRListRoute = createFileRoute('/specifications/adrs')({
  component: ADRListComponent,
  params: {
    projectId: z.string(),
  },
})

function ADRListComponent() {
  const { projectId } = Route.useParams()
  return <ADRListView projectId={projectId} />
}

// ADR Detail
export const ADRDetailRoute = createFileRoute('/adr/$adrId')({
  component: ADRDetailComponent,
})

function ADRDetailComponent() {
  const { adrId } = Route.useParams()
  return <ADRDetailView adrId={adrId} />
}

// Contract List
export const ContractListRoute = createFileRoute('/specifications/contracts')({
  component: ContractListComponent,
  params: {
    projectId: z.string(),
  },
})

function ContractListComponent() {
  const { projectId } = Route.useParams()
  return <ContractListView projectId={projectId} />
}

// Feature List
export const FeatureListRoute = createFileRoute('/specifications/features')({
  component: FeatureListComponent,
  params: {
    projectId: z.string(),
  },
})

function FeatureListComponent() {
  const { projectId } = Route.useParams()
  return <FeatureListView projectId={projectId} />
}

// Feature Detail
export const FeatureDetailRoute = createFileRoute('/feature/$featureId')({
  component: FeatureDetailComponent,
})

function FeatureDetailComponent() {
  const { featureId } = Route.useParams()
  return <FeatureDetailViewV2 featureId={featureId} />
}
```

---

## API Hook Implementation Examples

### Creating useADRs Hook

```typescript
// src/hooks/useSpecifications.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { ADR, Contract, Feature, RequirementQuality } from '@tracertm/types';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:3000';

// ADR Hooks
export function useADRs(projectId: string) {
  return useQuery({
    queryKey: ['adrs', projectId],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/api/projects/${projectId}/adrs`);
      if (!response.ok) throw new Error('Failed to fetch ADRs');
      return response.json() as Promise<ADR[]>;
    },
    enabled: !!projectId,
  });
}

export function useADR(adrId: string) {
  return useQuery({
    queryKey: ['adrs', adrId],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/api/adrs/${adrId}`);
      if (!response.ok) throw new Error('Failed to fetch ADR');
      return response.json() as Promise<ADR>;
    },
    enabled: !!adrId,
  });
}

export function useCreateADR() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<ADR>) => {
      const response = await fetch(`${API_BASE}/api/adrs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to create ADR');
      return response.json() as Promise<ADR>;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['adrs'] });
      queryClient.setQueryData(['adrs', data.id], data);
    },
  });
}

export function useUpdateADR() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<ADR> }) => {
      const response = await fetch(`${API_BASE}/api/adrs/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to update ADR');
      return response.json() as Promise<ADR>;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['adrs'] });
      queryClient.setQueryData(['adrs', data.id], data);
    },
  });
}

export function useDeleteADR() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (adrId: string) => {
      const response = await fetch(`${API_BASE}/api/adrs/${adrId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete ADR');
      return adrId;
    },
    onSuccess: (adrId) => {
      queryClient.invalidateQueries({ queryKey: ['adrs'] });
      queryClient.removeQueries({ queryKey: ['adrs', adrId] });
    },
  });
}

// Contract Hooks
export function useContracts(projectId: string) {
  return useQuery({
    queryKey: ['contracts', projectId],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/api/projects/${projectId}/contracts`);
      if (!response.ok) throw new Error('Failed to fetch contracts');
      return response.json() as Promise<Contract[]>;
    },
    enabled: !!projectId,
  });
}

export function useCreateContract() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<Contract>) => {
      const response = await fetch(`${API_BASE}/api/contracts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to create contract');
      return response.json() as Promise<Contract>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}

// Feature Hooks
export function useFeatures(projectId: string) {
  return useQuery({
    queryKey: ['features', projectId],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/api/projects/${projectId}/features`);
      if (!response.ok) throw new Error('Failed to fetch features');
      return response.json() as Promise<Feature[]>;
    },
    enabled: !!projectId,
  });
}

export function useCreateFeature() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<Feature>) => {
      const response = await fetch(`${API_BASE}/api/features`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Failed to create feature');
      return response.json() as Promise<Feature>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['features'] });
    },
  });
}
```

---

## Component Usage in Page Example

### Specifications Management Page

```typescript
// src/routes/projects.$projectId.specifications.tsx
import { createFileRoute } from '@tanstack/react-router'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui'
import {
  ADRListView,
  ContractListView,
  FeatureListView,
  SpecificationsDashboardView,
} from '@/views'
import {
  FileText,
  Shield,
  BookOpen,
  Activity,
} from 'lucide-react'

export const Route = createFileRoute('/projects/$projectId/specifications')({
  component: SpecificationsPage,
})

function SpecificationsPage() {
  const { projectId } = Route.useParams()
  const [activeTab, setActiveTab] = React.useState('dashboard')

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="w-full justify-start bg-transparent border-b">
          <TabsTrigger
            value="dashboard"
            className="gap-2"
          >
            <Activity className="h-4 w-4" />
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="adrs" className="gap-2">
            <FileText className="h-4 w-4" />
            ADRs
          </TabsTrigger>
          <TabsTrigger value="contracts" className="gap-2">
            <Shield className="h-4 w-4" />
            Contracts
          </TabsTrigger>
          <TabsTrigger value="features" className="gap-2">
            <BookOpen className="h-4 w-4" />
            Features
          </TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard">
          <SpecificationsDashboardView projectId={projectId} />
        </TabsContent>

        <TabsContent value="adrs">
          <ADRListView projectId={projectId} />
        </TabsContent>

        <TabsContent value="contracts">
          <ContractListView projectId={projectId} />
        </TabsContent>

        <TabsContent value="features">
          <FeatureListView projectId={projectId} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

---

## Testing Examples

### ADRListView Test

```typescript
// src/__tests__/views/ADRListView.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ADRListView } from '@/views'
import * as hooks from '@/hooks/useSpecifications'

describe('ADRListView', () => {
  const mockADRs = [
    {
      id: 'adr-1',
      projectId: 'proj-1',
      adrNumber: 'ADR-0001',
      title: 'Use PostgreSQL',
      status: 'accepted',
      context: 'Need reliable storage',
      decision: 'Use Postgres',
      date: '2025-01-15',
      tags: ['database'],
      version: 1,
      createdAt: '',
      updatedAt: '',
    },
  ]

  beforeEach(() => {
    jest.spyOn(hooks, 'useADRs').mockReturnValue({
      data: mockADRs,
      isLoading: false,
      error: null,
    } as any)
  })

  it('should render ADR list', () => {
    const queryClient = new QueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <ADRListView projectId="proj-1" />
      </QueryClientProvider>
    )

    expect(screen.getByText('Architecture Decision Records')).toBeInTheDocument()
    expect(screen.getByText('Use PostgreSQL')).toBeInTheDocument()
  })

  it('should filter ADRs by status', async () => {
    const queryClient = new QueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <ADRListView projectId="proj-1" />
      </QueryClientProvider>
    )

    const statusFilter = screen.getByDisplayValue('Status')
    fireEvent.click(statusFilter)

    const proposedOption = screen.getByText('Proposed')
    fireEvent.click(proposedOption)

    // Verify filter applied
    expect(statusFilter).toHaveValue('proposed')
  })

  it('should search ADRs', async () => {
    const queryClient = new QueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <ADRListView projectId="proj-1" />
      </QueryClientProvider>
    )

    const searchInput = screen.getByPlaceholderText(/Search/i)
    fireEvent.change(searchInput, { target: { value: 'PostgreSQL' } })

    expect(searchInput).toHaveValue('PostgreSQL')
  })

  it('should open create modal', async () => {
    const queryClient = new QueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <ADRListView projectId="proj-1" />
      </QueryClientProvider>
    )

    const createButton = screen.getByText('New ADR')
    fireEvent.click(createButton)

    await waitFor(() => {
      expect(screen.getByText('Create New ADR')).toBeInTheDocument()
    })
  })
})
```

---

## Error Handling Pattern

```typescript
// Custom error boundary for specification views
import { Component, ErrorInfo } from 'react'
import { Card, Button } from '@tracertm/ui'
import { AlertTriangle, RefreshCw } from 'lucide-react'

interface Props {
  children: React.ReactNode
  viewName: string
}

interface State {
  hasError: boolean
  error?: Error
}

export class SpecificationViewErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error(`Error in ${this.props.viewName}:`, error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 min-h-screen flex items-center justify-center">
          <Card className="border-none bg-red-50 dark:bg-red-950/20 w-full max-w-md">
            <div className="p-6 text-center space-y-4">
              <AlertTriangle className="h-12 w-12 text-red-600 mx-auto" />
              <h2 className="text-lg font-semibold">
                Error Loading {this.props.viewName}
              </h2>
              <p className="text-sm text-muted-foreground">
                {this.state.error?.message || 'An unexpected error occurred'}
              </p>
              <Button
                onClick={() => window.location.reload()}
                className="gap-2 w-full"
              >
                <RefreshCw className="h-4 w-4" />
                Reload Page
              </Button>
            </div>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

// Usage
<SpecificationViewErrorBoundary viewName="ADR List">
  <ADRListView projectId={projectId} />
</SpecificationViewErrorBoundary>
```

---

## Performance Optimization

### Memoized List Component

```typescript
import { memo, useMemo } from 'react'
import { ADRCard } from '@/components/specifications/adr/ADRCard'
import type { ADR } from '@tracertm/types'

interface ADRListItemProps {
  adr: ADR
  onClick: (adr: ADR) => void
}

const ADRListItem = memo(({ adr, onClick }: ADRListItemProps) => (
  <button onClick={() => onClick(adr)} className="text-left">
    <ADRCard adr={adr} />
  </button>
))

ADRListItem.displayName = 'ADRListItem'

// In ADRListView
const renderedADRs = useMemo(
  () =>
    filteredADRs.map((adr) => (
      <ADRListItem
        key={adr.id}
        adr={adr}
        onClick={(selected) => navigate({ to: `/adr/${selected.id}` })}
      />
    )),
  [filteredADRs, navigate]
)

return <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">{renderedADRs}</div>
```

---

## API Response Transformation

```typescript
// Transform raw API response to match view expectations
function transformADRResponse(raw: any): ADR {
  return {
    id: raw.id,
    projectId: raw.project_id,
    adrNumber: raw.adr_number,
    title: raw.title,
    status: raw.status as ADRStatus,
    context: raw.context,
    decision: raw.decision,
    consequences: raw.consequences,
    date: new Date(raw.date).toISOString(),
    tags: raw.tags || [],
    complianceScore: raw.compliance_score,
    relatedRequirements: raw.related_requirements || [],
    decisionDrivers: raw.decision_drivers || [],
    consideredOptions: raw.considered_options || [],
    version: raw.version,
    createdAt: raw.created_at,
    updatedAt: raw.updated_at,
  };
}
```

---

## Navigation Utilities

```typescript
// src/lib/navigation.ts
import { useNavigate } from '@tanstack/react-router';

export function useSpecificationNavigation() {
  const navigate = useNavigate();

  return {
    toADRs: (projectId: string) => navigate({ to: '/specifications/adrs', search: { projectId } }),
    toADRDetail: (adrId: string) => navigate({ to: `/adr/${adrId}` }),
    toContracts: (projectId: string) =>
      navigate({ to: '/specifications/contracts', search: { projectId } }),
    toFeatures: (projectId: string) =>
      navigate({ to: '/specifications/features', search: { projectId } }),
    toFeatureDetail: (featureId: string) => navigate({ to: `/feature/${featureId}` }),
    toDashboard: (projectId: string) =>
      navigate({ to: '/specifications/dashboard', search: { projectId } }),
  };
}

// Usage in component
const nav = useSpecificationNavigation();
nav.toADRDetail(adr.id);
```

---

## Accessibility Enhancements

```typescript
// Add ARIA labels and keyboard navigation
<div
  className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
  role="list"
  aria-label="Architecture Decision Records"
>
  {filteredADRs.map((adr) => (
    <button
      key={adr.id}
      onClick={() => navigate({ to: `/adr/${adr.id}` })}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          navigate({ to: `/adr/${adr.id}` })
        }
      }}
      aria-label={`View ${adr.adrNumber}: ${adr.title}`}
      role="listitem"
      className="text-left focus:outline-none focus:ring-2 focus:ring-primary rounded-lg"
    >
      <ADRCard adr={adr} />
    </button>
  ))}
</div>
```

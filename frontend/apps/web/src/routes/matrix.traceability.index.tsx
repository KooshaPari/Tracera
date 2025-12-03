import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { TraceabilityMatrixView } from '@/views/TraceabilityMatrixView'

export const Route = createFileRoute('/matrix/traceability/')({
  component: MatrixComponent,
  loader: async ({ searchParams }) => {
    const { fetchTraceabilityMatrix } = await import('@/api/matrix')
    const matrix = await fetchTraceabilityMatrix({ 
      projectId: searchParams.projectId as string,
      sourceType: searchParams.sourceType as string,
      targetType: searchParams.targetType as string,
      linkCategory: searchParams.category as string
    })
    
    const { fetchProjects } = await import('@/api/projects')
    const projects = await fetchProjects({ limit: 50 })
    
    return { matrix, projects, searchParams }
  }
})

function MatrixComponent() {
  const { matrix, projects, searchParams } = useLoaderData({ from: '/matrix/traceability/' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Traceability Matrix</h1>
          <p className="text-muted-foreground">
            Comprehensive traceability relationships between items and views
          </p>
        </div>
      </div>
      
      <TraceabilityMatrixView 
        matrix={matrix}
        projects={projects}
        filters={searchParams}
        loading={false}
      />
    </div>
  )
}

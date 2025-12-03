import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ImpactAnalysisView } from '@/views/ImpactAnalysisView'

export const Route = createFileRoute('/impact/analysis/')({
  component: ImpactAnalysisComponent,
  loader: async ({ searchParams }) => {
    const { fetchImpactAnalysis } = await import('@/api/impact')
    const analysis = await fetchImpactAnalysis({ 
      itemId: searchParams.itemId as string,
      projectId: searchParams.projectId as string,
      depth: parseInt(searchParams.depth as string) || 5,
      includeIndirect: searchParams.includeIndirect === 'true'
    })
    
    const { fetchProjects } = await import('@/api/projects')
    const projects = await fetchProjects({ limit: 50 })
    
    return { analysis, projects, searchParams }
  }
})

function ImpactAnalysisComponent() {
  const { analysis, projects, searchParams } = useLoaderData({ from: '/impact/analysis/' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Impact Analysis</h1>
          <p className="text-muted-foreground">
            Analyze dependencies and cascading effects across your project
          </p>
        </div>
      </div>
      
      <ImpactAnalysisView 
        analysis={analysis}
        projects={projects}
        filters={searchParams}
        loading={false}
      />
    </div>
  )
}

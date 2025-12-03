import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ReportsView } from '@/views/ReportsView'

export const Route = createFileRoute('/reports/')({
  component: ReportsComponent,
  loader: async ({ searchParams }) => {
    const { fetchReports } = await import('@/api/reports')
    const reports = await fetchReports({ 
      projectId: searchParams.projectId as string,
      type: searchParams.type as string,
      dateRange: searchParams.dateRange as string,
      format: searchParams.format as string || 'json'
    })
    
    const { fetchProjects } = await import('@/api/projects')
    const projects = await fetchProjects({ limit: 50 })
    
    return { reports, projects, searchParams }
  }
})

function ReportsComponent() {
  const { reports, projects, searchParams } = useLoaderData({ from: '/reports/' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Project Reports</h1>
          <p className="text-muted-foreground">
            Comprehensive analytics and reporting across all project metrics
          </p>
        </div>
      </div>
      
      <ReportsView 
        reports={reports}
        projects={projects}
        filters={searchParams}
        loading={false}
      />
    </div>
  )
}

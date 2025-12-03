import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { AgentsView } from '@/views/AgentsView'

export const Route = createFileRoute('/agents/')({
  component: AgentsComponent,
  loader: async ({ searchParams }) => {
    const { fetchAgents } = await import('@/api/agents')
    const agents = await fetchAgents({ 
      limit: 100,
      status: searchParams.status as string,
      projectId: searchParams.projectId as string,
      sortBy: searchParams.sortBy as string || 'created_at',
      sortOrder: searchParams.sortOrder as string || 'desc'
    })
    
    const { fetchProjects } = await import('@/api/projects')
    const projects = await fetchProjects({ limit: 50 })
    
    return { agents, projects, searchParams }
  }
})

function AgentsComponent() {
  const { agents, projects, searchParams } = useLoaderData({ from: '/agents/' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Agent Management</h1>
          <p className="text-muted-foreground">
            Coordinate and monitor 1-1000 concurrent autonomous agents
          </p>
        </div>
      </div>
      
      <AgentsView 
        agents={agents}
        projects={projects}
        filters={searchParams}
        loading={false}
      />
    </div>
  )
}

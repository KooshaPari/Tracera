import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ItemsTableView } from '@/views/ItemsTableView'

export const Route = createFileRoute('/projects/$projectId/views/api')({
  component: ApiView,
  loader: async ({ params }) => {
    const [{ fetchProject }, { fetchProjectApis }] = await Promise.all([
      import('@/api/projects'),
      import('@/api/items')
    ])
    
    const [project, apis] = await Promise.all([
      fetchProject(params.projectId),
      fetchProjectApis(params.projectId, { 
        limit: 100,
        sortBy: 'method',
        sortOrder: 'asc'
      })
    ])
    
    return { project, apis, type: 'api' as const }
  }
})

function ApiView() {
  const { project, apis, type } = useLoaderData({ from: '/projects/$projectId/views/api' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">API Endpoints</h1>
          <p className="text-muted-foreground">
            REST API contracts and specifications for {project.name}
          </p>
        </div>
      </div>
      
      <ItemsTableView 
        items={apis}
        type={type}
        project={project}
        loading={false}
      />
    </div>
  )
}


export const API_VIEW = ApiView



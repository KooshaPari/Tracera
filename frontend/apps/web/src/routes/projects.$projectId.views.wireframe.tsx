import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ItemsTableView } from '@/views/ItemsTableView'

export const Route = createFileRoute('/projects/$projectId/views/wireframe')({
  component: WireframeView,
  loader: async ({ params }) => {
    const [{ fetchProject }, { fetchProjectWireframes }] = await Promise.all([
      import('@/api/projects'),
      import('@/api/items')
    ])
    
    const [project, wireframes] = await Promise.all([
      fetchProject(params.projectId),
      fetchProjectWireframes(params.projectId, { 
        limit: 100,
        sortBy: 'created_at',
        sortOrder: 'desc'
      })
    ])
    
    return { project, wireframes, type: 'wireframe' as const }
  }
})

function WireframeView() {
  const { project, wireframes, type } = useLoaderData({ from: '/projects/$projectId/views/wireframe' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Wireframes & UI</h1>
          <p className="text-muted-foreground">
            UI/UX designs and wireframes for {project.name}
          </p>
        </div>
      </div>
      
      <ItemsTableView 
        items={wireframes}
        type={type}
        project={project}
        loading={false}
      />
    </div>
  )
}


export const WIREFRAME_VIEW = WireframeView



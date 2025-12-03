import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ItemsTableView } from '@/views/ItemsTableView'

export const Route = createFileRoute('/projects/$projectId/views/code')({
  component: CodeView,
  loader: async ({ params }) => {
    const [{ fetchProject }, { fetchProjectCode }] = await Promise.all([
      import('@/api/projects'),
      import('@/api/items')
    ])
    
    const [project, code] = await Promise.all([
      fetchProject(params.projectId),
      fetchProjectCode(params.projectId, { 
        limit: 200,
        sortBy: 'updated_at',
        sortOrder: 'desc'
      })
    ])
    
    return { project, code, type: 'code' as const }
  }
})

function CodeView() {
  const { project, code, type } = useLoaderData({ from: '/projects/$projectId/views/code' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Code Implementation</h1>
          <p className="text-muted-foreground">
            Source code implementations for {project.name}
          </p>
        </div>
      </div>
      
      <ItemsTableView 
        items={code}
        type={type}
        project={project}
        loading={false}
      />
    </div>
  )
}


export const CODE_VIEW = CodeView



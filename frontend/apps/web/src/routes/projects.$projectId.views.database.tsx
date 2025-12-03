import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ItemsTableView } from '@/views/ItemsTableView'

export const Route = createFileRoute('/projects/$projectId/views/database')({
  component: DatabaseView,
  loader: async ({ params }) => {
    const [{ fetchProject }, { fetchProjectDatabases }] = await Promise.all([
      import('@/api/projects'),
      import('@/api/items')
    ])
    
    const [project, databases] = await Promise.all([
      fetchProject(params.projectId),
      fetchProjectDatabases(params.projectId, { 
        limit: 100,
        sortBy: 'table_count',
        sortOrder: 'desc'
      })
    ])
    
    return { project, databases, type: 'database' as const }
  }
})

function DatabaseView() {
  const { project, databases, type } = useLoaderData({ from: '/projects/$projectId/views/database' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Database Schemas</h1>
          <p className="text-muted-foreground">
            Database designs, schemas, and migrations for {project.name}
          </p>
        </div>
      </div>
      
      <ItemsTableView 
        items={databases}
        type={type}
        project={project}
        loading={false}
      />
    </div>
  )
}


export const DATABASE_VIEW = DatabaseView



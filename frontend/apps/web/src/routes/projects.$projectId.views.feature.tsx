import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ItemsTableView } from '@/views/ItemsTableView'

export const Route = createFileRoute('/projects/$projectId/views/feature')({
  component: FeatureView,
  loader: async ({ params }) => {
    const [{ fetchProject }, { fetchProjectFeatures }] = await Promise.all([
      import('@/api/projects'),
      import('@/api/items')
    ])
    
    const [project, features] = await Promise.all([
      fetchProject(params.projectId),
      fetchProjectFeatures(params.projectId, { 
        limit: 100,
        sortBy: 'priority',
        sortOrder: 'desc'
      })
    ])
    
    return { project, features, type: 'feature' as const }
  }
})

function FeatureView() {
  const { project, features, type } = useLoaderData({ from: '/projects/$projectId/views/feature' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Features</h1>
          <p className="text-muted-foreground">
            Manage feature requirements and user stories for {project.name}
          </p>
        </div>
      </div>
      
      <ItemsTableView 
        items={features}
        type={type}
        project={project}
        loading={false}
      />
    </div>
  )
}


export const FEATURE_VIEW = FeatureView



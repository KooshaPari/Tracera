import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ItemsTableView } from '@/views/ItemsTableView'

export const Route = createFileRoute('/projects/$projectId/views/test')({
  component: TestView,
  loader: async ({ params }) => {
    const [{ fetchProject }, { fetchProjectTests }] = await Promise.all([
      import('@/api/projects'),
      import('@/api/items')
    ])
    
    const [project, tests] = await Promise.all([
      fetchProject(params.projectId),
      fetchProjectTests(params.projectId, { 
        limit: 200,
        sortBy: 'coverage',
        sortOrder: 'desc'
      })
    ])
    
    return { project, tests, type: 'test' as const }
  }
})

function TestView() {
  const { project, tests, type } = useLoaderData({ from: '/projects/$projectId/views/test' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Test Coverage</h1>
          <p className="text-muted-foreground">
            Test cases and coverage metrics for {project.name}
          </p>
        </div>
      </div>
      
      <ItemsTableView 
        items={tests}
        type={type}
        project={project}
        loading={false}
      />
    </div>
  )
}


export const TEST_VIEW = TestView



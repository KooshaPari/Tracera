import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ProjectDetailView } from '@/views/ProjectDetailView'
import type { Project } from '@tracertm/types'

interface RouteParams {
  projectId: string
}

export const Route = createFileRoute('/projects/$projectId')({
  component: ProjectDetailComponent,
  loader: async ({ params }) => {
    const [{ fetchProject }, { fetchProjectItems }, { fetchProjectLinks }] = await Promise.all([
      import('@/api/projects'),
      import('@/api/items'),
      import('@/api/links')
    ])
    
    const [project, items, links] = await Promise.all([
      fetchProject(params.projectId),
      fetchProjectItems(params.projectId, { limit: 100 }),
      fetchProjectLinks(params.projectId, { limit: 200 })
    ])
    
    return { project, items, links }
  },
  errorComponent: ErrorComponent,
})

function ProjectDetailComponent() {
  const { project, items, links } = useLoaderData({ from: '/projects/$projectId' })
  
  return <ProjectDetailView project={project} items={items} links={links} />
}

function ErrorComponent({ error }: { error: Error }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground">
      <h1 className="text-2xl font-bold text-destructive mb-4">Project Not Found</h1>
      <p className="text-muted-foreground mb-6">The project you're looking for doesn't exist or you don't have access.</p>
      <button 
        onClick={() => window.history.back()}
        className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
      >
        Go Back
      </button>
    </div>
  )
}

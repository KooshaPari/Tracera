import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ProjectsListView } from '@/views/ProjectsListView'

export const Route = createFileRoute('/projects/')({
  component: ProjectsComponent,
  loader: async () => {
    const { fetchProjects } = await import('@/api/projects')
    const projects = await fetchProjects({ 
      limit: 50,
      sortBy: 'updated_at',
      sortOrder: 'desc'
    })
    
    return { projects }
  }
})

function ProjectsComponent() {
  const { projects } = useLoaderData({ from: '/projects/' })
  
  return <ProjectsListView projects={projects} loading={false} />
}

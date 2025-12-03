import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { LinksView } from '@/views/LinksView'

export const Route = createFileRoute('/links/')({
  component: LinksComponent,
  loader: async ({ searchParams }) => {
    const { fetchLinks } = await import('@/api/links')
    const links = await fetchLinks({ 
      limit: 200,
      type: searchParams.type as string,
      sourceType: searchParams.sourceType as string,
      targetType: searchParams.targetType as string,
      projectId: searchParams.projectId as string
    })
    
    const { fetchProjects } = await import('@/api/projects')
    const projects = await fetchProjects({ limit: 50 })
    
    return { links, projects, searchParams }
  }
})

function LinksComponent() {
  const { links, projects, searchParams } = useLoaderData({ from: '/links/' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Relationship Links</h1>
          <p className="text-muted-foreground">
            Manage 60+ link types and relationships between project items
          </p>
        </div>
      </div>
      
      <LinksView 
        links={links} 
        projects={projects}
        filters={searchParams}
        loading={false}
      />
    </div>
  )
}

import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { SearchView } from '@/views/SearchView'

export const Route = createFileRoute('/search/')({
  component: SearchComponent,
  loader: async ({ searchParams }) => {
    const { fetchSearchResults } = await import('@/api/search')
    const results = await fetchSearchResults({ 
      query: searchParams.q as string || '',
      type: searchParams.type as string,
      projectId: searchParams.projectId as string,
      limit: parseInt(searchParams.limit as string) || 50,
      offset: parseInt(searchParams.offset as string) || 0
    })
    
    const { fetchProjects } = await import('@/api/projects')
    const projects = await fetchProjects({ limit: 50 })
    
    return { results, projects, searchParams }
  }
})

function SearchComponent() {
  const { results, projects, searchParams } = useLoaderData({ from: '/search/' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Search Results</h1>
          <p className="text-muted-foreground">
            Enterprise search across all project items, code, and documentation
          </p>
        </div>
      </div>
      
      <SearchView 
        results={results}
        projects={projects}
        query={searchParams}
        loading={false}
      />
    </div>
  )
}

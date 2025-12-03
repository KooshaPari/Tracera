import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ItemDetailView } from '@/views/ItemDetailView'
import type { Item, ItemType } from '@tracertm/types'

interface RouteParams {
  projectId: string
  viewType: ItemType
  itemId: string
}

const VIEW_TYPES = ['feature', 'code', 'test', 'api', 'database', 'wireframe', 'architecture', 'infrastructure', 'dataflow', 'security', 'performance', 'monitoring', 'domain', 'journey', 'configuration', 'dependency'] as const
type ViewType = typeof VIEW_TYPES[number]

export const Route = createFileRoute('/projects/$projectId/views/$viewType/$itemId')({
  component: ItemDetailComponent,
  loader: async ({ params }) => {
    // Validate viewType is a supported type
    if (!VIEW_TYPES.includes(params.viewType as ViewType)) {
      throw new Error(`Invalid view type: ${params.viewType}`)
    }
    
    const [{ fetchProject }, { fetchItem }, { fetchItemLinks }, { fetchRelatedItems }] = await Promise.all([
      import('@/api/projects'),
      import('@/api/items'),
      import('@/api/links'),
      import('@/api/items')
    ])
    
    const [project, item, links, relatedItems] = await Promise.all([
      fetchProject(params.projectId),
      fetchItem(params.itemId),
      fetchItemLinks(params.itemId),
      fetchRelatedItems(params.itemId, params.viewType)
    ])
    
    return { 
      project, 
      item, 
      links, 
      relatedItems,
      viewType: params.viewType 
    }
  },
  errorComponent: ({ error }) => (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground">
      <h1 className="text-2xl font-bold text-destructive mb-4">Item Not Found</h1>
      <p className="text-muted-foreground">{error.message}</p>
    </div>
  ),
})

function ItemDetailComponent() {
  const { project, item, links, relatedItems, viewType } = useLoaderData({ 
    from: '/projects/$projectId/views/$viewType/$itemId' 
  })
  
  return (
    <ItemDetailView 
      project={project}
      item={item} 
      links={links} 
      relatedItems={relatedItems}
      viewType={viewType}
    />
  )
}


export const ITEMDETAILCOMPONENT_VIEW = ItemDetailComponent

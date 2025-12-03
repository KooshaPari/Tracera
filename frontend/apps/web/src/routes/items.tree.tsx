import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ItemsTreeView } from '@/views/ItemsTreeView'

export const Route = createFileRoute('/items/tree')({
  component: TreeComponent,
  loader: async ({ searchParams }) => {
    const { fetchItemsTree } = await import('@/api/items')
    const tree = await fetchItemsTree({ 
      type: searchParams.type as string,
      projectId: searchParams.projectId as string
    })
    
    return { tree, searchParams }
  }
})

function TreeComponent() {
  const { tree, searchParams } = useLoaderData({ from: '/items/tree' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Item Hierarchy</h1>
          <p className="text-muted-foreground">
            Hierarchical view of project relationships and dependencies
          </p>
        </div>
      </div>
      
      <ItemsTreeView 
        tree={tree}
        type={searchParams.type as any}
        loading={false}
      />
    </div>
  )
}

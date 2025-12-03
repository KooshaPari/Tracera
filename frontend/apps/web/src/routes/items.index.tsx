import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ItemsTableView } from '@/views/ItemsTableView'

export const Route = createFileRoute('/items/')({
  component: ItemsComponent,
  loader: async ({ searchParams }) => {
    const { fetchItems } = await import('@/api/items')
    const items = await fetchItems({ 
      limit: 100,
      type: searchParams.type as string,
      status: searchParams.status as string,
      sortBy: searchParams.sortBy as string || 'updated_at',
      sortOrder: searchParams.sortOrder as string || 'desc'
    })
    
    return { items, searchParams }
  }
})

function ItemsComponent() {
  const { items, searchParams } = useLoaderData({ from: '/items/' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">All Items</h1>
          <p className="text-muted-foreground">
            Browse and manage all project items across all views
          </p>
        </div>
      </div>
      
      <ItemsTableView 
        items={items}
        type={searchParams.type as any}
        project={null}
        loading={false}
      />
    </div>
  )
}

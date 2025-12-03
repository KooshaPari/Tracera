import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { ItemsKanbanView } from '@/views/ItemsKanbanView'

export const Route = createFileRoute('/items/kanban')({
  component: KanbanComponent,
  loader: async ({ searchParams }) => {
    const { fetchItems } = await import('@/api/items')
    const items = await fetchItems({ 
      limit: 200,
      type: searchParams.type as string,
      status: searchParams.status as string
    })
    
    return { items, searchParams }
  }
})

function KanbanComponent() {
  const { items, searchParams } = useLoaderData({ from: '/items/kanban' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Kanban Board</h1>
          <p className="text-muted-foreground">
            Visual workflow management for all project items
          </p>
        </div>
      </div>
      
      <ItemsKanbanView 
        items={items}
        type={searchParams.type as any}
        loading={false}
      />
    </div>
  )
}

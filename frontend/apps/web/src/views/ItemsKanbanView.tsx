import type { Item, ItemStatus } from '@tracertm/types'
import { Alert } from '@tracertm/ui/components/Alert'
import { Badge } from '@tracertm/ui/components/Badge'
import { Button } from '@tracertm/ui/components/Button'
import { Card } from '@tracertm/ui/components/Card'
import { Input } from '@tracertm/ui/components/Input'
import { Skeleton } from '@tracertm/ui/components/Skeleton'
import { useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useItems, useUpdateItem } from '../hooks/useItems'
import { useProjects } from '../hooks/useProjects'

interface KanbanColumn {
  status: ItemStatus
  title: string
  color: string
  icon: string
}

const columns: KanbanColumn[] = [
  { status: 'todo', title: 'To Do', color: 'bg-gray-100 dark:bg-gray-800', icon: '📋' },
  {
    status: 'in_progress',
    title: 'In Progress',
    color: 'bg-blue-100 dark:bg-blue-900',
    icon: '🔄',
  },
  { status: 'done', title: 'Done', color: 'bg-green-100 dark:bg-green-900', icon: '✓' },
  { status: 'blocked', title: 'Blocked', color: 'bg-red-100 dark:bg-red-900', icon: '🚫' },
]

interface ItemCardProps {
  item: Item
  onDragStart: (item: Item) => void
}

function ItemCard({ item, onDragStart }: ItemCardProps) {
  return (
    <div
      draggable
      onDragStart={() => onDragStart(item)}
      className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 cursor-move hover:shadow-md transition-shadow"
    >
      <Link to={`/items/${item.id}`}>
        <div className="space-y-2">
          <div className="flex items-start justify-between">
            <h3 className="font-medium text-gray-900 dark:text-white line-clamp-2">{item.title}</h3>
          </div>

          {item.description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
              {item.description}
            </p>
          )}

          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="secondary" className="text-xs">
              {item.type}
            </Badge>
            {item.priority && (
              <Badge
                variant={
                  item.priority === 'critical' || item.priority === 'high'
                    ? 'destructive'
                    : 'secondary'
                }
                className="text-xs"
              >
                {item.priority}
              </Badge>
            )}
          </div>

          {item.owner && (
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <span>👤</span>
              <span>{item.owner}</span>
            </div>
          )}
        </div>
      </Link>
    </div>
  )
}

interface KanbanColumnProps {
  column: KanbanColumn
  items: Item[]
  onDrop: (status: ItemStatus) => void
  onDragStart: (item: Item) => void
}

function KanbanColumnComponent({ column, items, onDrop, onDragStart }: KanbanColumnProps) {
  const [isDraggingOver, setIsDraggingOver] = useState(false)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDraggingOver(true)
  }

  const handleDragLeave = () => {
    setIsDraggingOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDraggingOver(false)
    onDrop(column.status)
  }

  return (
    <div className="flex-1 min-w-80">
      <div
        className={`${column.color} rounded-t-lg p-4 border-b border-gray-200 dark:border-gray-700`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">{column.icon}</span>
            <h2 className="font-semibold text-gray-900 dark:text-white">{column.title}</h2>
          </div>
          <Badge variant="secondary">{items.length}</Badge>
        </div>
      </div>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`min-h-screen p-4 space-y-3 bg-gray-50 dark:bg-gray-900 border-x border-b border-gray-200 dark:border-gray-700 rounded-b-lg transition-colors ${
          isDraggingOver
            ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700'
            : ''
        }`}
      >
        {items.map((item) => (
          <ItemCard key={item.id} item={item} onDragStart={onDragStart} />
        ))}
        {items.length === 0 && (
          <div className="text-center py-8 text-gray-400 dark:text-gray-600">Drop items here</div>
        )}
      </div>
    </div>
  )
}

export function ItemsKanbanView() {
  const [searchParams] = useSearchParams()
  const projectFilter = searchParams.get('project') || undefined
  const typeFilter = searchParams.get('type') || undefined

  const { data: items, isLoading, error } = useItems({ projectId: projectFilter })
  const { data: projects } = useProjects()
  const updateItem = useUpdateItem()

  const [searchQuery, setSearchQuery] = useState('')
  const [draggedItem, setDraggedItem] = useState<Item | null>(null)

  // Filter items
  const filteredItems = useMemo(() => {
    if (!items) return []

    return items.filter((item) => {
      if (typeFilter && item.type !== typeFilter) return false
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        return (
          item.title.toLowerCase().includes(query) ||
          item.description?.toLowerCase().includes(query)
        )
      }
      return true
    })
  }, [items, typeFilter, searchQuery])

  // Group items by status
  const itemsByStatus = useMemo(() => {
    const grouped: Record<ItemStatus, Item[]> = {
      todo: [],
      in_progress: [],
      done: [],
      blocked: [],
      cancelled: [],
    }

    filteredItems.forEach((item) => {
      if (grouped[item.status]) {
        grouped[item.status]!.push(item)
      }
    })

    return grouped
  }, [filteredItems])

  const handleDragStart = (item: Item) => {
    setDraggedItem(item)
  }

  const handleDrop = async (newStatus: ItemStatus) => {
    if (!draggedItem || draggedItem.status === newStatus) {
      setDraggedItem(null)
      return
    }

    try {
      await updateItem.mutateAsync({
        id: draggedItem.id,
        data: { status: newStatus },
      })
      setDraggedItem(null)
    } catch (err) {
      console.error('Failed to update item status:', err)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-full" />
        <div className="flex gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="flex-1 h-96" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return <Alert variant="destructive">Failed to load items: {error.message}</Alert>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Kanban Board</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Drag and drop items to update their status
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/items">
            <Button variant="outline">Table View</Button>
          </Link>
          <Link to="/items/tree">
            <Button variant="outline">Tree View</Button>
          </Link>
          <Link to={`/items?action=create`}>
            <Button>+ New Item</Button>
          </Link>
        </div>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            type="search"
            placeholder="Search items..."
            value={searchQuery}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setSearchQuery((e.currentTarget as HTMLInputElement).value)
            }
          />
          {projects && (
            <select
              value={projectFilter || ''}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                const params = new URLSearchParams(searchParams)
                const value = (e.currentTarget as HTMLSelectElement).value
                if (value) {
                  params.set('project', value)
                } else {
                  params.delete('project')
                }
                if (typeof window !== 'undefined') {
                  window.history.replaceState({}, '', `?${params.toString()}`)
                }
              }}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
            >
              <option value="">All Projects</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          )}
          <select
            value={typeFilter || ''}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
              const params = new URLSearchParams(searchParams)
              const value = (e.currentTarget as HTMLSelectElement).value
              if (value) {
                params.set('type', value)
              } else {
                params.delete('type')
              }
              if (typeof window !== 'undefined') {
                window.history.replaceState({}, '', `?${params.toString()}`)
              }
            }}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
          >
            <option value="">All Types</option>
            <option value="requirement">Requirement</option>
            <option value="feature">Feature</option>
            <option value="test">Test</option>
            <option value="bug">Bug</option>
          </select>
        </div>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {columns.map((column) => (
          <Card key={column.status} className="p-4">
            <div className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {column.title}
            </div>
            <div className="mt-2 text-2xl font-semibold text-gray-900 dark:text-white">
              {itemsByStatus[column.status].length}
            </div>
          </Card>
        ))}
      </div>

      {/* Kanban Board */}
      <div className="flex gap-4 overflow-x-auto pb-4">
        {columns.map((column) => (
          <KanbanColumnComponent
            key={column.status}
            column={column}
            items={itemsByStatus[column.status]}
            onDrop={handleDrop}
            onDragStart={handleDragStart}
          />
        ))}
      </div>

      {/* Help Text */}
      <Card className="p-4 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
        <div className="flex items-start gap-3">
          <span className="text-xl">💡</span>
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white mb-1">How to use</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Drag items between columns to update their status. Click on an item to view details.
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}

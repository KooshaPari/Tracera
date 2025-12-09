import type { ItemStatus, Priority } from '@tracertm/types'
import { Alert } from '@tracertm/ui/components/Alert'
import { Badge } from '@tracertm/ui/components/Badge'
import { Button } from '@tracertm/ui/components/Button'
import { Card } from '@tracertm/ui/components/Card'
import { Input } from '@tracertm/ui/components/Input'
import { Skeleton } from '@tracertm/ui/components/Skeleton'
import { useMemo, useState } from 'react'
import { Link, useSearch, useNavigate } from '@tanstack/react-router'
import { useDeleteItem, useItems, useUpdateItem } from '../hooks/useItems'
import { useProjects } from '../hooks/useProjects'

interface TableColumn {
  id: string
  header: string
  width?: string
  sortable?: boolean
}

const columns: TableColumn[] = [
  { id: 'select', header: '', width: 'w-12' },
  { id: 'title', header: 'Title', sortable: true },
  { id: 'type', header: 'Type', width: 'w-32', sortable: true },
  { id: 'status', header: 'Status', width: 'w-32', sortable: true },
  { id: 'priority', header: 'Priority', width: 'w-24', sortable: true },
  { id: 'owner', header: 'Owner', width: 'w-32', sortable: true },
  { id: 'created', header: 'Created', width: 'w-32', sortable: true },
  { id: 'actions', header: '', width: 'w-24' },
]

function getStatusColor(status: ItemStatus): string {
  switch (status) {
    case 'done':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
    case 'in_progress':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
    case 'blocked':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
  }
}

function getPriorityColor(priority?: Priority): string {
  switch (priority) {
    case 'critical':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    case 'high':
      return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
    case 'low':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
  }
}

interface BulkActionsBarProps {
  selectedCount: number
  onClearSelection: () => void
  onBulkDelete: () => void
  onBulkStatusChange: (status: ItemStatus) => void
}

function BulkActionsBar({
  selectedCount,
  onClearSelection,
  onBulkDelete,
  onBulkStatusChange,
}: BulkActionsBarProps) {
  return (
    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <span className="font-medium text-gray-900 dark:text-white">
          {selectedCount} item{selectedCount !== 1 ? 's' : ''} selected
        </span>
        <Button variant="ghost" size="sm" onClick={onClearSelection}>
          Clear
        </Button>
      </div>
      <div className="flex items-center gap-2">
        <select
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
            onBulkStatusChange((e.currentTarget as HTMLSelectElement).value as ItemStatus)
          }
          className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
        >
          <option value="">Change Status...</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="done">Done</option>
          <option value="blocked">Blocked</option>
        </select>
        <Button variant="destructive" size="sm" onClick={onBulkDelete}>
          Delete
        </Button>
      </div>
    </div>
  )
}

export function ItemsTableView() {
  const navigate = useNavigate()
  const searchParams = useSearch({ strict: false }) as any
  const projectFilter = searchParams?.project || undefined
  const typeFilter = searchParams?.type || undefined
  const statusFilter = searchParams?.status || undefined

  const { data: items, isLoading, error } = useItems({ projectId: projectFilter })
  const { data: projects } = useProjects()
  const updateItem = useUpdateItem()
  const deleteItem = useDeleteItem()

  const [searchQuery, setSearchQuery] = useState('')
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  const [sortColumn, setSortColumn] = useState<string>('created')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 20

  // Filter and sort items
  const filteredAndSortedItems = useMemo(() => {
    if (!items) return []

    const filtered = items.filter((item) => {
      if (typeFilter && item.type !== typeFilter) return false
      if (statusFilter && item.status !== statusFilter) return false
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        return (
          item.title.toLowerCase().includes(query) ||
          item.description?.toLowerCase().includes(query) ||
          item.type.toLowerCase().includes(query)
        )
      }
      return true
    })

    filtered.sort((a, b) => {
      let comparison = 0

      switch (sortColumn) {
        case 'title':
          comparison = a.title.localeCompare(b.title)
          break
        case 'type':
          comparison = a.type.localeCompare(b.type)
          break
        case 'status':
          comparison = a.status.localeCompare(b.status)
          break
        case 'priority':
          comparison = (a.priority || '').localeCompare(b.priority || '')
          break
        case 'owner':
          comparison = (a.owner || '').localeCompare(b.owner || '')
          break
        case 'created':
          comparison = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
          break
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })

    return filtered
  }, [items, typeFilter, statusFilter, searchQuery, sortColumn, sortOrder])

  // Pagination
  const totalPages = Math.ceil(filteredAndSortedItems.length / pageSize)
  const paginatedItems = filteredAndSortedItems.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortOrder('asc')
    }
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedItems(new Set(paginatedItems.map((item) => item.id)))
    } else {
      setSelectedItems(new Set())
    }
  }

  const handleSelectItem = (id: string, checked: boolean) => {
    const newSelection = new Set(selectedItems)
    if (checked) {
      newSelection.add(id)
    } else {
      newSelection.delete(id)
    }
    setSelectedItems(newSelection)
  }

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${selectedItems.size} items?`)) return

    for (const id of selectedItems) {
      await deleteItem.mutateAsync(id)
    }
    setSelectedItems(new Set())
  }

  const handleBulkStatusChange = async (status: ItemStatus) => {
    if (!status) return

    for (const id of selectedItems) {
      await updateItem.mutateAsync({ id, data: { status } })
    }
    setSelectedItems(new Set())
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-96" />
      </div>
    )
  }

  if (error) {
    return <Alert variant="destructive">Failed to load items: {error.message}</Alert>
  }

  const allSelected =
    paginatedItems.length > 0 && paginatedItems.every((item) => selectedItems.has(item.id))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Items</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Manage all project items in table view
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/items/kanban">
            <Button variant="outline">Kanban View</Button>
          </Link>
          <Link to="/items/tree">
            <Button variant="outline">Tree View</Button>
          </Link>
          <Link to={`/items?${searchParams}&action=create`}>
            <Button>+ New Item</Button>
          </Link>
        </div>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
                const value = (e.currentTarget as HTMLSelectElement).value
                if (value) {
                  searchParams.set('project', value)
                } else {
                  searchParams.delete('project')
                }
                setSearchParams(searchParams)
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
              const value = (e.currentTarget as HTMLSelectElement).value
              if (value) {
                searchParams.set('type', value)
              } else {
                searchParams.delete('type')
              }
              setSearchParams(searchParams)
            }}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
          >
            <option value="">All Types</option>
            <option value="requirement">Requirement</option>
            <option value="feature">Feature</option>
            <option value="test">Test</option>
            <option value="bug">Bug</option>
          </select>
          <select
            value={statusFilter || ''}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
              const value = (e.currentTarget as HTMLSelectElement).value
              if (value) {
                searchParams.set('status', value)
              } else {
                searchParams.delete('status')
              }
              setSearchParams(searchParams)
            }}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
          >
            <option value="">All Statuses</option>
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
            <option value="blocked">Blocked</option>
          </select>
        </div>
      </Card>

      {/* Bulk Actions */}
      {selectedItems.size > 0 && (
        <BulkActionsBar
          selectedCount={selectedItems.size}
          onClearSelection={() => setSelectedItems(new Set())}
          onBulkDelete={handleBulkDelete}
          onBulkStatusChange={handleBulkStatusChange}
        />
      )}

      {/* Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
              <tr>
                {columns.map((column) => (
                  <th
                    key={column.id}
                    className={`px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider ${column.width || ''}`}
                  >
                    {column.id === 'select' ? (
                      <input
                        type="checkbox"
                        checked={allSelected}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                          handleSelectAll((e.currentTarget as HTMLInputElement).checked)
                        }
                        className="rounded border-gray-300 dark:border-gray-600"
                      />
                    ) : column.sortable ? (
                      <button
                        onClick={() => handleSort(column.id)}
                        className="flex items-center gap-1 hover:text-gray-900 dark:hover:text-white"
                      >
                        {column.header}
                        {sortColumn === column.id && <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>}
                      </button>
                    ) : (
                      column.header
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              {paginatedItems.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type="checkbox"
                      checked={selectedItems.has(item.id)}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                        handleSelectItem(item.id, (e.currentTarget as HTMLInputElement).checked)
                      }
                      className="rounded border-gray-300 dark:border-gray-600"
                    />
                  </td>
                  <td className="px-6 py-4">
                    <Link
                      to={`/items/${item.id}`}
                      className="font-medium text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400"
                    >
                      {item.title}
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge variant="secondary">{item.type}</Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${getStatusColor(item.status)}`}
                    >
                      {item.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {item.priority && (
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(item.priority)}`}
                      >
                        {item.priority}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {item.owner || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {new Date(item.createdAt).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link to={`/items/${item.id}`}>
                      <Button variant="ghost" size="sm">
                        View
                      </Button>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Showing {(currentPage - 1) * pageSize + 1} to{' '}
              {Math.min(currentPage * pageSize, filteredAndSortedItems.length)} of{' '}
              {filteredAndSortedItems.length} items
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Page {currentPage} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
              >
                Next
              </Button>
            </div>
          </div>
        )}

        {paginatedItems.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p>No items found</p>
          </div>
        )}
      </Card>
    </div>
  )
}

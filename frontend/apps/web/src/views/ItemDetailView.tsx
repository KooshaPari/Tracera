import { Alert } from '@tracertm/ui/components/Alert'
import { Badge } from '@tracertm/ui/components/Badge'
import { Button } from '@tracertm/ui/components/Button'
import { Card } from '@tracertm/ui/components/Card'
import { Skeleton } from '@tracertm/ui/components/Skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui/components/Tabs'
import { useState } from 'react'
import { Link, useNavigate, useParams } from '@tanstack/react-router'
import { useDeleteItem, useItem } from '../hooks/useItems'
import { useLinks } from '../hooks/useLinks'

export function ItemDetailView() {
  const { itemId } = useParams<{ itemId: string }>()
  const navigate = useNavigate()
  const { data: item, isLoading, error } = useItem(itemId!)
  const { data: links } = useLinks({ sourceId: itemId })
  const deleteItem = useDeleteItem()

  const [isEditing, setIsEditing] = useState(false)

  const handleDelete = async () => {
    if (!(itemId && confirm('Delete this item?'))) return
    try {
      await deleteItem.mutateAsync(itemId)
      navigate('/items')
    } catch (err) {
      console.error('Failed to delete item:', err)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (error || !item) {
    return <Alert variant="destructive">Failed to load item</Alert>
  }

  const sourceLinks = links?.filter((l) => l.sourceId === item.id) || []
  const targetLinks = links?.filter((l) => l.targetId === item.id) || []

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center text-sm text-gray-500">
        <Link to="/items" className="hover:text-gray-900">
          Items
        </Link>
        <span className="mx-2">/</span>
        <span className="text-gray-900">{item.title}</span>
      </div>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{item.title}</h1>
            <Badge variant="secondary">{item.type}</Badge>
            <Badge variant={item.status === 'done' ? 'success' : 'info'}>{item.status}</Badge>
          </div>
          {item.description && (
            <p className="text-gray-600 dark:text-gray-400">{item.description}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={() => setIsEditing(!isEditing)}>{isEditing ? 'Cancel' : 'Edit'}</Button>
          <Button variant="destructive" onClick={handleDelete}>
            Delete
          </Button>
        </div>
      </div>

      {/* Details */}
      <Card className="p-6">
        <Tabs defaultValue="details">
          <TabsList>
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="links">
              Links ({sourceLinks.length + targetLinks.length})
            </TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
          </TabsList>

          <TabsContent value="details">
            <div className="grid grid-cols-2 gap-6 mt-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Status
                </label>
                <p className="text-gray-900 dark:text-white">{item.status}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Priority
                </label>
                <p className="text-gray-900 dark:text-white">{item.priority || 'None'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Owner
                </label>
                <p className="text-gray-900 dark:text-white">{item.owner || 'Unassigned'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Created
                </label>
                <p className="text-gray-900 dark:text-white">
                  {new Date(item.createdAt).toLocaleString()}
                </p>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="links">
            <div className="space-y-6 mt-6">
              <div>
                <h3 className="font-semibold mb-3">Outgoing Links ({sourceLinks.length})</h3>
                {sourceLinks.length > 0 ? (
                  <div className="space-y-2">
                    {sourceLinks.map((link) => (
                      <div key={link.id} className="p-3 border rounded-lg">
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary">{link.type}</Badge>
                          <span>→ {link.targetId}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No outgoing links</p>
                )}
              </div>
              <div>
                <h3 className="font-semibold mb-3">Incoming Links ({targetLinks.length})</h3>
                {targetLinks.length > 0 ? (
                  <div className="space-y-2">
                    {targetLinks.map((link) => (
                      <div key={link.id} className="p-3 border rounded-lg">
                        <div className="flex items-center gap-2">
                          <span>{link.sourceId} →</span>
                          <Badge variant="secondary">{link.type}</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No incoming links</p>
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="history">
            <div className="mt-6">
              <p className="text-gray-500">History timeline coming soon</p>
            </div>
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  )
}

import { Alert } from '@tracertm/ui/components/Alert'
import { Badge } from '@tracertm/ui/components/Badge'
import { Button } from '@tracertm/ui/components/Button'
import { Card } from '@tracertm/ui/components/Card'
import { Skeleton } from '@tracertm/ui/components/Skeleton'
import { useState } from 'react'
import { useDeleteLink, useLinks } from '../hooks/useLinks'

export function LinksView() {
  const { data: links, isLoading, error } = useLinks()
  useLinks()
  const deleteLink = useDeleteLink()

  const [_showCreateDialog, setShowCreateDialog] = useState(false)

  if (isLoading) return <Skeleton className="h-96" />
  if (error) return <Alert variant="destructive">Failed to load links</Alert>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Links</h1>
          <p className="text-gray-600">Manage item relationships</p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>+ Create Link</Button>
      </div>

      <Card className="p-6">
        <div className="space-y-4">
          {links && links.length > 0 ? (
            links.map((link) => (
              <div
                key={link.id}
                className="p-4 border rounded-lg flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  <span className="font-medium">{link.sourceId}</span>
                  <Badge variant="secondary">{link.type}</Badge>
                  <span>→</span>
                  <span className="font-medium">{link.targetId}</span>
                </div>
                <Button variant="ghost" size="sm" onClick={() => deleteLink.mutateAsync(link.id)}>
                  Delete
                </Button>
              </div>
            ))
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>No links yet</p>
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}

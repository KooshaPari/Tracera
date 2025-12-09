import { Button } from '@tracertm/ui/components/Button'
import { Card } from '@tracertm/ui/components/Card'
import { Skeleton } from '@tracertm/ui/components/Skeleton'
import { useEffect, useRef } from 'react'
import { useNavigate, useSearch } from '@tanstack/react-router'
import { useItems } from '../hooks/useItems'
import { useLinks } from '../hooks/useLinks'

export function GraphView() {
  const navigate = useNavigate()
  const searchParams = useSearch({ strict: false }) as any
  const projectFilter = searchParams?.project || undefined

  const { data: items, isLoading: itemsLoading } = useItems({ projectId: projectFilter })
  const { data: links, isLoading: linksLoading } = useLinks({ projectId: projectFilter })
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!(items && links && containerRef.current)) return

    // TODO: Initialize Cytoscape.js graph here
    // This is a placeholder - actual implementation would use cytoscape
    console.log('Graph data:', { items, links })
  }, [items, links])

  if (itemsLoading || linksLoading) {
    return <Skeleton className="h-screen" />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Graph View</h1>
          <p className="text-gray-600">Visualize item relationships</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">Fit View</Button>
          <Button variant="outline">Export</Button>
        </div>
      </div>

      <Card className="p-0 h-[calc(100vh-200px)]">
        <div
          ref={containerRef}
          className="w-full h-full flex items-center justify-center bg-gray-50 dark:bg-gray-900"
        >
          <div className="text-center text-gray-500">
            <p className="text-6xl mb-4">🕸️</p>
            <p>Graph visualization</p>
            <p className="text-sm">Cytoscape.js integration pending</p>
          </div>
        </div>
      </Card>
    </div>
  )
}

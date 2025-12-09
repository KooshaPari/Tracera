import { Button } from '@tracertm/ui/components/Button'
import { Card } from '@tracertm/ui/components/Card'
import { Skeleton } from '@tracertm/ui/components/Skeleton'
import { useMemo } from 'react'
import { useNavigate, useSearch } from '@tanstack/react-router'
import { useItems } from '../hooks/useItems'
import { useLinks } from '../hooks/useLinks'

export function TraceabilityMatrixView() {
  const navigate = useNavigate()
  const searchParams = useSearch({ strict: false }) as any
  const projectFilter = searchParams?.project

  const { data: items, isLoading } = useItems({ projectId: projectFilter || undefined })
  const { data: links } = useLinks({ projectId: projectFilter || undefined })

  const matrix = useMemo(() => {
    if (!(items && links)) return { requirements: [], features: [], coverage: {} }

    const requirements = items.filter((i) => i.type === 'requirement')
    const features = items.filter((i) => i.type === 'feature')

    const coverage: Record<string, Set<string>> = {}
    links.forEach((link) => {
      if (!coverage[link.sourceId]) coverage[link.sourceId] = new Set()
      coverage[link.sourceId]!.add(link.targetId)
    })

    return { requirements, features, coverage }
  }, [items, links])

  if (isLoading) return <Skeleton className="h-screen" />

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Traceability Matrix</h1>
          <p className="text-gray-600">Requirements coverage overview</p>
        </div>
        <Button variant="outline">Export</Button>
      </div>

      <Card className="p-6 overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              <th className="border p-2 bg-gray-50 dark:bg-gray-800">Requirement</th>
              {matrix.features.map((feature) => (
                <th key={feature.id} className="border p-2 bg-gray-50 dark:bg-gray-800 min-w-32">
                  {feature.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {matrix.requirements.map((req) => (
              <tr key={req.id}>
                <td className="border p-2 font-medium">{req.title}</td>
                {matrix.features.map((feature) => (
                  <td key={feature.id} className="border p-2 text-center">
                    {matrix.coverage[req.id]?.has(feature.id) ? (
                      <span className="text-green-600 text-xl">✓</span>
                    ) : (
                      <span className="text-gray-300">-</span>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>

        {matrix.requirements.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p>No requirements found</p>
          </div>
        )}
      </Card>

      <div className="grid grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="text-sm text-gray-600">Total Requirements</div>
          <div className="text-2xl font-semibold">{matrix.requirements.length}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600">Total Features</div>
          <div className="text-2xl font-semibold">{matrix.features.length}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600">Coverage</div>
          <div className="text-2xl font-semibold">
            {matrix.requirements.length > 0
              ? Math.round((Object.keys(matrix.coverage).length / matrix.requirements.length) * 100)
              : 0}
            %
          </div>
        </Card>
      </div>
    </div>
  )
}

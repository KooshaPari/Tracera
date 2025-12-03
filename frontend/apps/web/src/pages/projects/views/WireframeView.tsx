import { ExternalLink, Layout, Monitor, Plus, Smartphone, Tablet } from 'lucide-react'
import { useState } from 'react'

interface Wireframe {
  id: string
  name: string
  description: string
  screen: 'desktop' | 'tablet' | 'mobile'
  status: 'draft' | 'review' | 'approved'
  thumbnail: string
  linkedFeatures: string[]
}

const wireframes: Wireframe[] = [
  {
    id: '1',
    name: 'Dashboard',
    description: 'Main dashboard with stats and quick actions',
    screen: 'desktop',
    status: 'approved',
    thumbnail: '📊',
    linkedFeatures: ['Dashboard Feature', 'Analytics'],
  },
  {
    id: '2',
    name: 'Project List',
    description: 'Grid view of all projects',
    screen: 'desktop',
    status: 'approved',
    thumbnail: '📁',
    linkedFeatures: ['Project Management'],
  },
  {
    id: '3',
    name: 'Graph View',
    description: 'Traceability visualization',
    screen: 'desktop',
    status: 'review',
    thumbnail: '🔗',
    linkedFeatures: ['Graph Visualization', 'Traceability'],
  },
  {
    id: '4',
    name: 'Item Detail',
    description: 'Single item view with metadata',
    screen: 'desktop',
    status: 'draft',
    thumbnail: '📝',
    linkedFeatures: ['Item CRUD'],
  },
  {
    id: '5',
    name: 'Mobile Dashboard',
    description: 'Responsive dashboard for mobile',
    screen: 'mobile',
    status: 'draft',
    thumbnail: '📱',
    linkedFeatures: ['Mobile Support'],
  },
  {
    id: '6',
    name: 'Settings',
    description: 'User and project settings',
    screen: 'desktop',
    status: 'approved',
    thumbnail: '⚙️',
    linkedFeatures: ['Settings Management'],
  },
]

const screenIcons = { desktop: Monitor, tablet: Tablet, mobile: Smartphone }
const statusColors = {
  draft: 'bg-gray-100 text-gray-600',
  review: 'bg-yellow-100 text-yellow-600',
  approved: 'bg-green-100 text-green-600',
}

export function WireframeView() {
  const [filter, setFilter] = useState<string | null>(null)
  const [selected, setSelected] = useState<Wireframe | null>(null)

  const filtered = filter ? wireframes.filter((w) => w.screen === filter) : wireframes

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Wireframe View</h3>
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border p-1">
            <button
              onClick={() => setFilter(null)}
              className={`rounded px-2 py-1 text-sm ${!filter ? 'bg-accent' : ''}`}
            >
              All
            </button>
            <button
              onClick={() => setFilter('desktop')}
              className={`rounded px-2 py-1 text-sm ${filter === 'desktop' ? 'bg-accent' : ''}`}
            >
              <Monitor className="h-4 w-4" />
            </button>
            <button
              onClick={() => setFilter('tablet')}
              className={`rounded px-2 py-1 text-sm ${filter === 'tablet' ? 'bg-accent' : ''}`}
            >
              <Tablet className="h-4 w-4" />
            </button>
            <button
              onClick={() => setFilter('mobile')}
              className={`rounded px-2 py-1 text-sm ${filter === 'mobile' ? 'bg-accent' : ''}`}
            >
              <Smartphone className="h-4 w-4" />
            </button>
          </div>
          <button className="flex items-center gap-2 rounded-lg bg-primary px-3 py-1.5 text-sm text-primary-foreground">
            <Plus className="h-4 w-4" /> Add Wireframe
          </button>
        </div>
      </div>

      <div className="flex gap-4">
        <div className="grid flex-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((wf) => {
            const Icon = screenIcons[wf.screen]
            return (
              <div
                key={wf.id}
                onClick={() => setSelected(wf)}
                className={`cursor-pointer rounded-lg border p-4 transition-all hover:shadow-md ${selected?.id === wf.id ? 'ring-2 ring-primary' : ''}`}
              >
                <div className="flex aspect-video items-center justify-center rounded-lg bg-muted text-6xl">
                  {wf.thumbnail}
                </div>
                <div className="mt-3 flex items-center gap-2">
                  <Icon className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium">{wf.name}</span>
                  <span
                    className={`ml-auto rounded-full px-2 py-0.5 text-xs ${statusColors[wf.status]}`}
                  >
                    {wf.status}
                  </span>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">{wf.description}</p>
              </div>
            )
          })}
        </div>

        {selected && (
          <div className="w-72 rounded-lg border bg-card p-4">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold">{selected.name}</h4>
              <button className="rounded p-1 hover:bg-accent">
                <ExternalLink className="h-4 w-4" />
              </button>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">{selected.description}</p>
            <div className="mt-4 space-y-3 text-sm">
              <div>
                <span className="text-muted-foreground">Screen:</span>{' '}
                <span className="capitalize">{selected.screen}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Status:</span>{' '}
                <span
                  className={`ml-2 rounded-full px-2 py-0.5 text-xs ${statusColors[selected.status]}`}
                >
                  {selected.status}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Linked Features:</span>
                <ul className="mt-1 space-y-1">
                  {selected.linkedFeatures.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-primary">
                      <Layout className="h-3 w-3" /> {f}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="mt-4 flex gap-2">
              <button className="flex-1 rounded-lg border px-3 py-1.5 text-sm hover:bg-accent">
                Edit
              </button>
              <button className="flex-1 rounded-lg bg-primary px-3 py-1.5 text-sm text-primary-foreground">
                Preview
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

import { Book, ChevronRight, Edit, Eye, FileText, Plus, Search } from 'lucide-react'
import { useState } from 'react'

interface Doc {
  id: string
  title: string
  type: 'guide' | 'reference' | 'tutorial' | 'changelog'
  status: 'draft' | 'published' | 'outdated'
  lastUpdated: string
  author: string
  linkedItems: number
}

const docs: Doc[] = [
  {
    id: '1',
    title: 'Getting Started Guide',
    type: 'guide',
    status: 'published',
    lastUpdated: '2024-11-28',
    author: 'Team',
    linkedItems: 5,
  },
  {
    id: '2',
    title: 'CLI Reference',
    type: 'reference',
    status: 'published',
    lastUpdated: '2024-11-27',
    author: 'KooshaPari',
    linkedItems: 48,
  },
  {
    id: '3',
    title: 'Multi-View Architecture',
    type: 'guide',
    status: 'published',
    lastUpdated: '2024-11-25',
    author: 'Team',
    linkedItems: 8,
  },
  {
    id: '4',
    title: 'Agent Integration Tutorial',
    type: 'tutorial',
    status: 'draft',
    lastUpdated: '2024-11-29',
    author: 'KooshaPari',
    linkedItems: 12,
  },
  {
    id: '5',
    title: 'API Documentation',
    type: 'reference',
    status: 'published',
    lastUpdated: '2024-11-26',
    author: 'Team',
    linkedItems: 24,
  },
  {
    id: '6',
    title: 'Release Notes v1.0',
    type: 'changelog',
    status: 'published',
    lastUpdated: '2024-11-20',
    author: 'Team',
    linkedItems: 0,
  },
  {
    id: '7',
    title: 'Graph Visualization Guide',
    type: 'guide',
    status: 'outdated',
    lastUpdated: '2024-10-15',
    author: 'Team',
    linkedItems: 3,
  },
]

const typeIcons = { guide: Book, reference: FileText, tutorial: FileText, changelog: FileText }
const typeColors = {
  guide: 'bg-blue-100 text-blue-600',
  reference: 'bg-purple-100 text-purple-600',
  tutorial: 'bg-green-100 text-green-600',
  changelog: 'bg-orange-100 text-orange-600',
}
const statusColors = {
  draft: 'text-yellow-600',
  published: 'text-green-600',
  outdated: 'text-red-600',
}

export function DocumentationView() {
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState<string | null>(null)

  const filtered = docs.filter(
    (d) =>
      d.title.toLowerCase().includes(search.toLowerCase()) && (!typeFilter || d.type === typeFilter)
  )

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Documentation View</h3>
        <button className="flex items-center gap-2 rounded-lg bg-primary px-3 py-1.5 text-sm text-primary-foreground">
          <Plus className="h-4 w-4" /> New Document
        </button>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search documentation..."
            value={search}
            onChange={(e) => setSearch((e.target as HTMLInputElement).value)}
            className="w-full rounded-lg border bg-background py-2 pl-10 pr-4"
          />
        </div>
        <select
          value={typeFilter || ''}
          onChange={(e) => setTypeFilter((e.target as HTMLSelectElement).value || null)}
          className="rounded-lg border px-3 py-2"
        >
          <option value="">All Types</option>
          <option value="guide">Guides</option>
          <option value="reference">Reference</option>
          <option value="tutorial">Tutorials</option>
          <option value="changelog">Changelog</option>
        </select>
      </div>

      <div className="rounded-lg border">
        {filtered.map((doc) => {
          const Icon = typeIcons[doc.type]
          return (
            <div
              key={doc.id}
              className="flex items-center gap-4 border-b p-4 last:border-b-0 hover:bg-accent/30"
            >
              <div className={`rounded-lg p-2 ${typeColors[doc.type]}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{doc.title}</span>
                  <span className={`text-xs ${statusColors[doc.status]}`}>● {doc.status}</span>
                </div>
                <div className="mt-1 flex items-center gap-4 text-xs text-muted-foreground">
                  <span>{doc.author}</span>
                  <span>Updated {doc.lastUpdated}</span>
                  <span>{doc.linkedItems} linked items</span>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button className="rounded p-2 hover:bg-accent" title="Preview">
                  <Eye className="h-4 w-4" />
                </button>
                <button className="rounded p-2 hover:bg-accent" title="Edit">
                  <Edit className="h-4 w-4" />
                </button>
                <button className="rounded p-2 hover:bg-accent" title="Open">
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )
        })}
        {filtered.length === 0 && (
          <div className="p-8 text-center text-muted-foreground">
            No documents found matching your criteria.
          </div>
        )}
      </div>
    </div>
  )
}

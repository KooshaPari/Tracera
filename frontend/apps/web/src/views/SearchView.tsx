import { Badge } from '@tracertm/ui/components/Badge'
import { Card } from '@tracertm/ui/components/Card'
import { Input } from '@tracertm/ui/components/Input'
import { Skeleton } from '@tracertm/ui/components/Skeleton'
import { useState } from 'react'
import { Link } from '@tanstack/react-router'
import { useSearch } from '../hooks/useSearch'

export function SearchView() {
  const [query, setQuery] = useState('')
  const [filters, setFilters] = useState({
    type: '',
    status: '',
    project: '',
  })

  const { results, isLoading } = useSearch({ q: query, ...filters })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Search</h1>
        <p className="text-gray-600">Find items, projects, and links</p>
      </div>

      <Card className="p-4">
        <div className="space-y-4">
          <Input
            type="search"
            placeholder="Search everything..."
            value={query}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setQuery((e.currentTarget as HTMLInputElement).value)
            }
            autoFocus
          />

          <div className="flex gap-2">
            <select
              value={filters.type}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                setFilters({ ...filters, type: (e.currentTarget as HTMLSelectElement).value })
              }
              className="px-3 py-2 border rounded-md"
            >
              <option value="">All Types</option>
              <option value="requirement">Requirement</option>
              <option value="feature">Feature</option>
              <option value="test">Test</option>
            </select>
            <select
              value={filters.status}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                setFilters({ ...filters, status: (e.currentTarget as HTMLSelectElement).value })
              }
              className="px-3 py-2 border rounded-md"
            >
              <option value="">All Statuses</option>
              <option value="todo">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="done">Done</option>
            </select>
          </div>
        </div>
      </Card>

      {isLoading && <Skeleton className="h-64" />}

      {results && results.items && results.items.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Results ({results.items.length})</h2>
          <div className="space-y-3">
            {results.items.map((item) => (
              <Link key={item.id} to={`/items/${item.id}`}>
                <Card className="p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium">{item.title}</h3>
                        <Badge variant="secondary">{item.type}</Badge>
                      </div>
                      {item.description && (
                        <p className="text-sm text-gray-600 line-clamp-2">{item.description}</p>
                      )}
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      )}

      {query && results && results.items?.length === 0 && (
        <Card className="p-12 text-center text-gray-500">
          <p>No results found for "{query}"</p>
        </Card>
      )}
    </div>
  )
}

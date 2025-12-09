import type { Item, Link as LinkType } from '@tracertm/types'
import { Alert } from '@tracertm/ui/components/Alert'
import { Badge } from '@tracertm/ui/components/Badge'
import { Button } from '@tracertm/ui/components/Button'
import { Card } from '@tracertm/ui/components/Card'
import { Skeleton } from '@tracertm/ui/components/Skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui/components/Tabs'
import { useMemo } from 'react'
import { Link, useNavigate, useParams } from '@tanstack/react-router'
import { useItems } from '../hooks/useItems'
import { useLinks } from '../hooks/useLinks'
import { useProject, useUpdateProject } from '../hooks/useProjects'
import { useProjectStore } from '../stores'

interface ItemsByType {
  [key: string]: Item[]
}

interface ProjectStatsProps {
  items: Item[]
  links: LinkType[]
}

function ProjectStats({ items, links }: ProjectStatsProps) {
  const stats = useMemo(() => {
    const itemsByStatus = items.reduce(
      (acc, item) => {
        acc[item.status] = (acc[item.status] || 0) + 1
        return acc
      },
      {} as Record<string, number>
    )

    const itemsByType = items.reduce(
      (acc, item) => {
        acc[item.type] = (acc[item.type] || 0) + 1
        return acc
      },
      {} as Record<string, number>
    )

    const completionRate = items.length
      ? Math.round(((itemsByStatus.done || 0) / items.length) * 100)
      : 0

    return {
      total: items.length,
      todo: itemsByStatus.todo || 0,
      in_progress: itemsByStatus.in_progress || 0,
      done: itemsByStatus.done || 0,
      blocked: itemsByStatus.blocked || 0,
      completionRate,
      links: links.length,
      itemsByType,
    }
  }, [items, links])

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card className="p-4">
        <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Items</div>
        <div className="mt-2 text-2xl font-semibold text-gray-900 dark:text-white">
          {stats.total}
        </div>
      </Card>
      <Card className="p-4">
        <div className="text-sm font-medium text-gray-600 dark:text-gray-400">In Progress</div>
        <div className="mt-2 text-2xl font-semibold text-blue-600 dark:text-blue-400">
          {stats.in_progress}
        </div>
      </Card>
      <Card className="p-4">
        <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Completed</div>
        <div className="mt-2 text-2xl font-semibold text-green-600 dark:text-green-400">
          {stats.done}
        </div>
      </Card>
      <Card className="p-4">
        <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Completion</div>
        <div className="mt-2 text-2xl font-semibold text-purple-600 dark:text-purple-400">
          {stats.completionRate}%
        </div>
      </Card>
    </div>
  )
}

interface ItemsListProps {
  items: Item[]
  title: string
  emptyMessage: string
}

function ItemsList({ items, title: _title, emptyMessage }: ItemsListProps) {
  if (items.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {items.map((item) => (
        <Link key={item.id} to={`/items/${item.id}`}>
          <div className="p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-400 hover:shadow-md transition-all">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-medium text-gray-900 dark:text-white">{item.title}</h3>
                  <Badge
                    variant={
                      item.status === 'done'
                        ? 'success'
                        : item.status === 'in_progress'
                          ? 'info'
                          : 'secondary'
                    }
                  >
                    {item.status.replace('_', ' ')}
                  </Badge>
                </div>
                {item.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                    {item.description}
                  </p>
                )}
                <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                  <span>Type: {item.type}</span>
                  {item.priority && <span>Priority: {item.priority}</span>}
                  {item.owner && <span>Owner: {item.owner}</span>}
                </div>
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  )
}

function QuickActions({ projectId }: { projectId: string }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Link to={`/items?project=${projectId}`}>
        <Card className="p-4 hover:shadow-lg transition-shadow cursor-pointer h-full">
          <div className="text-2xl mb-2">📋</div>
          <div className="font-medium text-gray-900 dark:text-white">View Items</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Table view</div>
        </Card>
      </Link>
      <Link to={`/items/kanban?project=${projectId}`}>
        <Card className="p-4 hover:shadow-lg transition-shadow cursor-pointer h-full">
          <div className="text-2xl mb-2">📊</div>
          <div className="font-medium text-gray-900 dark:text-white">Kanban Board</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Workflow view</div>
        </Card>
      </Link>
      <Link to={`/graph?project=${projectId}`}>
        <Card className="p-4 hover:shadow-lg transition-shadow cursor-pointer h-full">
          <div className="text-2xl mb-2">🕸️</div>
          <div className="font-medium text-gray-900 dark:text-white">Graph View</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Relationships</div>
        </Card>
      </Link>
      <Link to={`/matrix?project=${projectId}`}>
        <Card className="p-4 hover:shadow-lg transition-shadow cursor-pointer h-full">
          <div className="text-2xl mb-2">📈</div>
          <div className="font-medium text-gray-900 dark:text-white">Matrix</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Coverage</div>
        </Card>
      </Link>
    </div>
  )
}

export function ProjectDetailView() {
  const { projectId } = useParams<{ projectId: string }>()
  useNavigate()
  const { data: project, isLoading: projectLoading, error: projectError } = useProject(projectId!)
  const { data: items, isLoading: itemsLoading } = useItems({ projectId })
  const { data: links, isLoading: linksLoading } = useLinks({ projectId })
  const { setCurrentProject } = useProjectStore()
  useUpdateProject()

  // Set current project in store
  useMemo(() => {
    if (project) {
      setCurrentProject(project)
    }
  }, [project, setCurrentProject])

  // Group items by type
  const itemsByType = useMemo(() => {
    if (!items) return {}
    return items.reduce((acc, item) => {
      if (!acc[item.type]) {
        acc[item.type] = []
      }
      acc[item.type]!.push(item)
      return acc
    }, {} as ItemsByType)
  }, [items])

  // Recent items (last 5)
  const recentItems = useMemo(() => {
    if (!items) return []
    return [...items]
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, 5)
  }, [items])

  if (projectLoading || itemsLoading || linksLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-full" />
        <div className="grid grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (projectError || !project) {
    return <Alert variant="destructive">Failed to load project. {projectError?.message}</Alert>
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
        <Link to="/projects" className="hover:text-gray-900 dark:hover:text-white">
          Projects
        </Link>
        <span className="mx-2">/</span>
        <span className="text-gray-900 dark:text-white">{project.name}</span>
      </div>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{project.name}</h1>
          {project.description && (
            <p className="text-gray-600 dark:text-gray-400">{project.description}</p>
          )}
          <div className="flex items-center gap-4 mt-4 text-sm text-gray-500">
            <span>Created: {new Date(project.createdAt).toLocaleDateString()}</span>
            {project.updatedAt && (
              <span>Updated: {new Date(project.updatedAt).toLocaleDateString()}</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link to={`/items?project=${project.id}&action=create`}>
            <Button>+ Add Item</Button>
          </Link>
          <Button variant="outline">Edit</Button>
        </div>
      </div>

      {/* Stats */}
      <ProjectStats items={items || []} links={links || []} />

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
        <QuickActions projectId={project.id} />
      </div>

      {/* Content Tabs */}
      <Card className="p-6">
        <Tabs defaultValue="overview">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="items">Items by Type</TabsTrigger>
            <TabsTrigger value="recent">Recent Activity</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <div className="space-y-6 mt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {Object.entries(itemsByType).map(([type, typeItems]) => (
                  <Card key={type} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-gray-900 dark:text-white capitalize">
                        {type}s
                      </h3>
                      <Badge variant="secondary">{typeItems.length}</Badge>
                    </div>
                    <div className="space-y-2">
                      {typeItems.slice(0, 3).map((item) => (
                        <Link key={item.id} to={`/items/${item.id}`}>
                          <div className="text-sm p-2 rounded hover:bg-gray-50 dark:hover:bg-gray-800">
                            {item.title}
                          </div>
                        </Link>
                      ))}
                      {typeItems.length > 3 && (
                        <Link to={`/items?project=${project.id}&type=${type}`}>
                          <div className="text-sm text-blue-600 dark:text-blue-400 hover:underline">
                            View all {typeItems.length} {type}s
                          </div>
                        </Link>
                      )}
                    </div>
                  </Card>
                ))}
              </div>

              {Object.keys(itemsByType).length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <p>No items yet in this project</p>
                  <Link to={`/items?project=${project.id}&action=create`}>
                    <Button variant="outline" className="mt-4">
                      Create First Item
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="items">
            <div className="space-y-6 mt-6">
              {Object.entries(itemsByType).map(([type, typeItems]) => (
                <div key={type}>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                      {type}s ({typeItems.length})
                    </h3>
                    <Link to={`/items?project=${project.id}&type=${type}`}>
                      <Button variant="ghost" size="sm">
                        View All
                      </Button>
                    </Link>
                  </div>
                  <ItemsList items={typeItems} title={type} emptyMessage={`No ${type}s yet`} />
                </div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="recent">
            <div className="mt-6">
              <ItemsList
                items={recentItems}
                title="Recent Activity"
                emptyMessage="No recent activity"
              />
            </div>
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  )
}

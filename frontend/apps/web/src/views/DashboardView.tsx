import type { Project } from '@tracertm/types'
import { Badge } from '@tracertm/ui/components/Badge'
import { Button } from '@tracertm/ui/components/Button'
import { Card } from '@tracertm/ui/components/Card'
import { Skeleton } from '@tracertm/ui/components/Skeleton'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useItems } from '../hooks/useItems'
import { useProjects } from '../hooks/useProjects'
import { useProjectStore } from '../stores'

interface StatCardProps {
  title: string
  value: number
  description: string
  trend?: { value: number; direction: 'up' | 'down' }
  icon: string
  color: string
}

function StatCard({ title, value, description, trend, icon, color }: StatCardProps) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-gray-900 dark:text-white">{value}</p>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{description}</p>
          {trend && (
            <div
              className={`mt-2 flex items-center text-sm ${trend.direction === 'up' ? 'text-green-600' : 'text-red-600'}`}
            >
              <span>{trend.direction === 'up' ? '↑' : '↓'}</span>
              <span className="ml-1">{Math.abs(trend.value)}%</span>
              <span className="ml-1 text-gray-500">from last week</span>
            </div>
          )}
        </div>
        <div className={`rounded-lg p-3 ${color}`}>
          <span className="text-2xl">{icon}</span>
        </div>
      </div>
    </Card>
  )
}

interface RecentActivityItem {
  id: string
  type: 'item_created' | 'item_updated' | 'link_created' | 'project_created'
  title: string
  subtitle: string
  timestamp: Date
  user: string
}

function RecentActivity({ activities }: { activities: RecentActivityItem[] }) {
  if (activities.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No recent activity</p>
      </div>
    )
  }

  const getActivityIcon = (type: RecentActivityItem['type']) => {
    switch (type) {
      case 'item_created':
        return '+'
      case 'item_updated':
        return '✏️'
      case 'link_created':
        return '🔗'
      case 'project_created':
        return '📁'
      default:
        return '•'
    }
  }

  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <div
          key={activity.id}
          className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
        >
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
            <span>{getActivityIcon(activity.type)}</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {activity.title}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {activity.subtitle} by {activity.user}
            </p>
          </div>
          <div className="flex-shrink-0 text-sm text-gray-400">
            {formatTimeAgo(activity.timestamp)}
          </div>
        </div>
      ))}
    </div>
  )
}

function formatTimeAgo(date: Date): string {
  const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000)

  if (seconds < 60) return 'just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`
  return date.toLocaleDateString()
}

interface QuickAction {
  id: string
  label: string
  description: string
  icon: string
  href: string
  color: string
}

function QuickActions() {
  const actions: QuickAction[] = [
    {
      id: 'new-item',
      label: 'Create Item',
      description: 'Add a new requirement, feature, or test',
      icon: '➕',
      href: '/items?action=create',
      color: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
    },
    {
      id: 'new-project',
      label: 'New Project',
      description: 'Start a new project',
      icon: '📁',
      href: '/projects?action=create',
      color: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400',
    },
    {
      id: 'view-graph',
      label: 'View Graph',
      description: 'Visualize relationships',
      icon: '🕸️',
      href: '/graph',
      color: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400',
    },
    {
      id: 'run-analysis',
      label: 'Impact Analysis',
      description: 'Analyze change impact',
      icon: '🎯',
      href: '/impact',
      color: 'bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {actions.map((action) => (
        <Link key={action.id} to={action.href}>
          <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer h-full">
            <div
              className={`w-12 h-12 rounded-lg ${action.color} flex items-center justify-center mb-4`}
            >
              <span className="text-2xl">{action.icon}</span>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{action.label}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">{action.description}</p>
          </Card>
        </Link>
      ))}
    </div>
  )
}

export function DashboardView() {
  const { data: projects, isLoading: projectsLoading } = useProjects()
  const { data: items, isLoading: itemsLoading } = useItems()
  useProjectStore()
  const [recentActivity, setRecentActivity] = useState<RecentActivityItem[]>([])

  // Calculate stats
  const stats = {
    totalProjects: projects?.length || 0,
    totalItems: items?.length || 0,
    activeItems: items?.filter((item) => item.status !== 'done').length || 0,
    completionRate: items?.length
      ? Math.round((items.filter((item) => item.status === 'done').length / items.length) * 100)
      : 0,
  }

  // Mock recent activity (in production, this would come from an API)
  useEffect(() => {
    if (items && items.length > 0) {
      const activities: RecentActivityItem[] = items.slice(0, 5).map((item) => ({
        id: item.id,
        type: 'item_created' as const,
        title: item.title,
        subtitle: item.type,
        timestamp: new Date(item.createdAt),
        user: item.owner || 'Unknown',
      }))
      setRecentActivity(activities)
    }
  }, [items])

  if (projectsLoading || itemsLoading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-48 mb-2" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Welcome back! Here's an overview of your projects and items.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Projects"
          value={stats.totalProjects}
          description="Active projects"
          icon="📁"
          color="bg-blue-100 dark:bg-blue-900"
          trend={{ value: 12, direction: 'up' }}
        />
        <StatCard
          title="Total Items"
          value={stats.totalItems}
          description="All items across projects"
          icon="📋"
          color="bg-green-100 dark:bg-green-900"
          trend={{ value: 8, direction: 'up' }}
        />
        <StatCard
          title="Active Items"
          value={stats.activeItems}
          description="In progress or pending"
          icon="⚡"
          color="bg-yellow-100 dark:bg-yellow-900"
        />
        <StatCard
          title="Completion"
          value={stats.completionRate}
          description="Overall completion rate"
          icon="✓"
          color="bg-purple-100 dark:bg-purple-900"
          trend={{ value: 5, direction: 'up' }}
        />
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
        <QuickActions />
      </div>

      {/* Recent Projects & Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Projects */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Recent Projects</h2>
            <Link to="/projects">
              <Button variant="ghost" size="sm">
                View All
              </Button>
            </Link>
          </div>
          {projects && projects.length > 0 ? (
            <div className="space-y-3">
              {projects.slice(0, 5).map((project: Project) => (
                <Link key={project.id} to={`/projects/${project.id}`}>
                  <div className="p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900 dark:text-white">
                          {project.name}
                        </h3>
                        {project.description && (
                          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                            {project.description}
                          </p>
                        )}
                      </div>
                      <Badge variant="secondary">
                        {items?.filter((item) => item.projectId === project.id).length || 0} items
                      </Badge>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>No projects yet</p>
              <Link to="/projects?action=create">
                <Button variant="outline" size="sm" className="mt-4">
                  Create your first project
                </Button>
              </Link>
            </div>
          )}
        </Card>

        {/* Recent Activity */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Recent Activity</h2>
            <Link to="/events">
              <Button variant="ghost" size="sm">
                View All
              </Button>
            </Link>
          </div>
          <RecentActivity activities={recentActivity} />
        </Card>
      </div>

      {/* Coverage Overview */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Coverage Overview</h2>
          <Link to="/matrix">
            <Button variant="ghost" size="sm">
              View Matrix
            </Button>
          </Link>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {items?.filter((item) => item.type === 'requirement').length || 0}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">Requirements</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {items?.filter((item) => item.type === 'feature').length || 0}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">Features</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {items?.filter((item) => item.type === 'test').length || 0}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">Tests</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
              {Math.round(
                ((items?.filter((item) => item.type === 'test').length || 0) /
                  Math.max(items?.filter((item) => item.type === 'requirement').length || 1, 1)) *
                  100
              )}
              %
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">Test Coverage</div>
          </div>
        </div>
      </Card>
    </div>
  )
}

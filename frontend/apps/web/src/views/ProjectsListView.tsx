import type { Project } from '@tracertm/types'
import { Alert } from '@tracertm/ui/components/Alert'
import { Button } from '@tracertm/ui/components/Button'
import { Card } from '@tracertm/ui/components/Card'
import { Dialog } from '@tracertm/ui/components/Dialog'
import { Input } from '@tracertm/ui/components/Input'
import { Skeleton } from '@tracertm/ui/components/Skeleton'
import { useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useItems } from '../hooks/useItems'
import { useCreateProject, useDeleteProject, useProjects } from '../hooks/useProjects'

interface ProjectCardProps {
  project: Project
  itemCount: number
  onDelete: () => void
}

function ProjectCard({ project, itemCount, onDelete }: ProjectCardProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  return (
    <>
      <Card className="p-6 hover:shadow-lg transition-shadow">
        <div className="flex items-start justify-between mb-4">
          <Link to={`/projects/${project.id}`} className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400">
              {project.name}
            </h3>
          </Link>
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.preventDefault()
                setShowDeleteDialog(true)
              }}
            >
              🗑️
            </Button>
          </div>
        </div>

        {project.description && (
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
            {project.description}
          </p>
        )}

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center space-x-1">
              <span>📋</span>
              <span>{itemCount} items</span>
            </div>
            <div className="flex items-center space-x-1">
              <span>📅</span>
              <span>{new Date(project.createdAt).toLocaleDateString()}</span>
            </div>
          </div>
          <Link to={`/projects/${project.id}`}>
            <Button variant="outline" size="sm">
              View
            </Button>
          </Link>
        </div>
      </Card>

      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <div className="p-6">
          <h2 className="text-xl font-semibold mb-4">Delete Project</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Are you sure you want to delete "{project.name}"? This action cannot be undone.
          </p>
          <div className="flex justify-end space-x-3">
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                onDelete()
                setShowDeleteDialog(false)
              }}
            >
              Delete
            </Button>
          </div>
        </div>
      </Dialog>
    </>
  )
}

function CreateProjectDialog({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)
  const createProject = useCreateProject()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!name.trim()) {
      setError('Project name is required')
      return
    }

    try {
      const project = await createProject.mutateAsync({
        name: name.trim(),
        description: description.trim() || undefined,
      })
      setName('')
      setDescription('')
      onOpenChange(false)
      navigate(`/projects/${project.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-4">Create New Project</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <Alert variant="destructive">{error}</Alert>}

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Project Name *
            </label>
            <Input
              value={name}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setName((e.currentTarget as HTMLInputElement).value)
              }
              placeholder="Enter project name"
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                setDescription((e.currentTarget as HTMLTextAreaElement).value)
              }
              placeholder="Enter project description (optional)"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
              rows={4}
            />
          </div>

          <div className="flex justify-end space-x-3">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createProject.isPending}>
              {createProject.isPending ? 'Creating...' : 'Create Project'}
            </Button>
          </div>
        </form>
      </div>
    </Dialog>
  )
}

export function ProjectsListView() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { data: projects, isLoading: projectsLoading, error: projectsError } = useProjects()
  const { data: items } = useItems()
  const deleteProject = useDeleteProject()

  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'items'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  const showCreateDialog = searchParams.get('action') === 'create'

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      searchParams.delete('action')
      setSearchParams(searchParams)
    }
  }

  // Filter and sort projects
  const filteredAndSortedProjects = useMemo(() => {
    if (!projects) return []

    const filtered = projects.filter((project) => {
      if (!searchQuery) return true
      const query = searchQuery.toLowerCase()
      return (
        project.name.toLowerCase().includes(query) ||
        project.description?.toLowerCase().includes(query)
      )
    })

    // Count items per project
    const projectsWithCounts = filtered.map((project) => ({
      project,
      itemCount: items?.filter((item) => item.projectId === project.id).length || 0,
    }))

    // Sort
    projectsWithCounts.sort((a, b) => {
      let comparison = 0

      switch (sortBy) {
        case 'name':
          comparison = a.project.name.localeCompare(b.project.name)
          break
        case 'date':
          comparison =
            new Date(a.project.createdAt).getTime() - new Date(b.project.createdAt).getTime()
          break
        case 'items':
          comparison = a.itemCount - b.itemCount
          break
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })

    return projectsWithCounts
  }, [projects, items, searchQuery, sortBy, sortOrder])

  const handleDelete = async (id: string) => {
    try {
      await deleteProject.mutateAsync(id)
    } catch (err) {
      console.error('Failed to delete project:', err)
    }
  }

  if (projectsLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-full" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      </div>
    )
  }

  if (projectsError) {
    return <Alert variant="destructive">Failed to load projects: {projectsError.message}</Alert>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Projects</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Manage your traceability projects</p>
        </div>
        <Button onClick={() => setSearchParams({ action: 'create' })}>+ New Project</Button>
      </div>

      {/* Filters and Search */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <Input
              type="search"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setSearchQuery((e.currentTarget as HTMLInputElement).value)
              }
            />
          </div>
          <div className="flex items-center gap-2">
            <select
              value={sortBy}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                setSortBy((e.currentTarget as HTMLSelectElement).value as 'name' | 'date' | 'items')
              }
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
            >
              <option value="date">Sort by Date</option>
              <option value="name">Sort by Name</option>
              <option value="items">Sort by Items</option>
            </select>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </Button>
          </div>
        </div>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Projects</div>
          <div className="mt-2 text-3xl font-semibold text-gray-900 dark:text-white">
            {projects?.length || 0}
          </div>
        </Card>
        <Card className="p-6">
          <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Items</div>
          <div className="mt-2 text-3xl font-semibold text-gray-900 dark:text-white">
            {items?.length || 0}
          </div>
        </Card>
        <Card className="p-6">
          <div className="text-sm font-medium text-gray-600 dark:text-gray-400">
            Avg Items/Project
          </div>
          <div className="mt-2 text-3xl font-semibold text-gray-900 dark:text-white">
            {projects?.length ? Math.round((items?.length || 0) / projects.length) : 0}
          </div>
        </Card>
      </div>

      {/* Projects Grid */}
      {filteredAndSortedProjects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAndSortedProjects.map(({ project, itemCount }) => (
            <ProjectCard
              key={project.id}
              project={project}
              itemCount={itemCount}
              onDelete={() => handleDelete(project.id)}
            />
          ))}
        </div>
      ) : (
        <Card className="p-12">
          <div className="text-center">
            <div className="text-6xl mb-4">📁</div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              {searchQuery ? 'No projects found' : 'No projects yet'}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {searchQuery
                ? 'Try adjusting your search criteria'
                : 'Get started by creating your first project'}
            </p>
            {!searchQuery && (
              <Button onClick={() => setSearchParams({ action: 'create' })}>Create Project</Button>
            )}
          </div>
        </Card>
      )}

      {/* Create Dialog */}
      <CreateProjectDialog open={showCreateDialog} onOpenChange={handleOpenChange} />
    </div>
  )
}

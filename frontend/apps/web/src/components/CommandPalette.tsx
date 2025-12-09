import {
  ArrowRight,
  BookOpen,
  Cloud,
  Code,
  Database,
  FileText,
  FolderOpen,
  GitBranch,
  Globe,
  Home,
  Image,
  Layout,
  Search,
  Settings,
  TestTube,
} from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from '@tanstack/react-router'

interface Command {
  id: string
  title: string
  description?: string
  icon: typeof Search
  action: () => void
  keywords?: string[]
  category: 'navigation' | 'view' | 'action' | 'recent'
}

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState(0)
  const navigate = useNavigate()

  const commands: Command[] = useMemo(
    () => [
      // Navigation
      {
        id: 'nav-home',
        title: 'Go to Dashboard',
        icon: Home,
        action: () => navigate('/'),
        category: 'navigation',
        keywords: ['home', 'dashboard'],
      },
      {
        id: 'nav-projects',
        title: 'Go to Projects',
        icon: FolderOpen,
        action: () => navigate('/projects'),
        category: 'navigation',
        keywords: ['projects', 'list'],
      },
      {
        id: 'nav-settings',
        title: 'Go to Settings',
        icon: Settings,
        action: () => navigate('/settings'),
        category: 'navigation',
        keywords: ['settings', 'config'],
      },
      // Views
      {
        id: 'view-feature',
        title: 'Feature View',
        description: 'Epics, features, stories',
        icon: Layout,
        action: () => navigate('/projects/1/feature'),
        category: 'view',
        keywords: ['feature', 'epic', 'story'],
      },
      {
        id: 'view-code',
        title: 'Code View',
        description: 'Modules and files',
        icon: Code,
        action: () => navigate('/projects/1/code'),
        category: 'view',
        keywords: ['code', 'module', 'file'],
      },
      {
        id: 'view-test',
        title: 'Test View',
        description: 'Test suites and cases',
        icon: TestTube,
        action: () => navigate('/projects/1/test'),
        category: 'view',
        keywords: ['test', 'suite', 'case'],
      },
      {
        id: 'view-graph',
        title: 'Graph View',
        description: 'Traceability visualization',
        icon: GitBranch,
        action: () => navigate('/projects/1/graph'),
        category: 'view',
        keywords: ['graph', 'trace', 'link'],
      },
      {
        id: 'view-api',
        title: 'API View',
        description: 'Endpoints and schemas',
        icon: Globe,
        action: () => navigate('/projects/1/api'),
        category: 'view',
        keywords: ['api', 'endpoint', 'rest'],
      },
      {
        id: 'view-db',
        title: 'Database View',
        description: 'Tables and schemas',
        icon: Database,
        action: () => navigate('/projects/1/database'),
        category: 'view',
        keywords: ['database', 'table', 'schema'],
      },
      {
        id: 'view-wireframe',
        title: 'Wireframe View',
        description: 'UI mockups',
        icon: Image,
        action: () => navigate('/projects/1/wireframe'),
        category: 'view',
        keywords: ['wireframe', 'mockup', 'ui'],
      },
      {
        id: 'view-docs',
        title: 'Documentation View',
        description: 'Guides and references',
        icon: BookOpen,
        action: () => navigate('/projects/1/documentation'),
        category: 'view',
        keywords: ['docs', 'documentation', 'guide'],
      },
      {
        id: 'view-deploy',
        title: 'Deployment View',
        description: 'Environments and releases',
        icon: Cloud,
        action: () => navigate('/projects/1/deployment'),
        category: 'view',
        keywords: ['deploy', 'release', 'environment'],
      },
      // Actions
      {
        id: 'action-new-item',
        title: 'Create New Item',
        description: 'Add a new requirement or artifact',
        icon: FileText,
        action: () => console.log('Create item'),
        category: 'action',
        keywords: ['create', 'new', 'add', 'item'],
      },
    ],
    [navigate]
  )

  const filtered = useMemo(() => {
    if (!query) return commands
    const q = query.toLowerCase()
    return commands.filter(
      (c) =>
        c.title.toLowerCase().includes(q) ||
        c.description?.toLowerCase().includes(q) ||
        c.keywords?.some((k) => k.includes(q))
    )
  }, [query, commands])

  const handleKeyDown = useCallback(
    (e: globalThis.KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setOpen((o) => !o)
        setQuery('')
        setSelected(0)
      }
      if (!open) return
      if (e.key === 'Escape') {
        setOpen(false)
        setQuery('')
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelected((s) => Math.min(s + 1, filtered.length - 1))
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelected((s) => Math.max(s - 1, 0))
      }
      if (e.key === 'Enter' && filtered[selected]) {
        filtered[selected].action()
        setOpen(false)
        setQuery('')
      }
    },
    [open, filtered, selected]
  )

  useEffect(() => {
    if (typeof globalThis.window === 'undefined') {
      return
    }

    globalThis.window.addEventListener('keydown', handleKeyDown)
    return () => globalThis.window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  useEffect(() => {
    setSelected(0)
  }, [query])

  if (!open) return null

  const grouped = {
    navigation: filtered.filter((c) => c.category === 'navigation'),
    view: filtered.filter((c) => c.category === 'view'),
    action: filtered.filter((c) => c.category === 'action'),
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]"
      onClick={() => setOpen(false)}
    >
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
      <div
        className="relative w-full max-w-lg rounded-xl border bg-background shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 border-b px-4 py-3">
          <Search className="h-5 w-5 text-muted-foreground" />
          <input
            autoFocus
            type="text"
            placeholder="Search commands, views, items..."
            value={query}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
            className="flex-1 bg-transparent text-lg outline-none placeholder:text-muted-foreground"
          />
          <kbd className="rounded border bg-muted px-2 py-0.5 text-xs">ESC</kbd>
        </div>
        <div className="max-h-[400px] overflow-y-auto p-2">
          {Object.entries(grouped).map(
            ([category, items]) =>
              items.length > 0 && (
                <div key={category}>
                  <div className="px-2 py-1 text-xs font-medium text-muted-foreground uppercase">
                    {category}
                  </div>
                  {items.map((cmd) => {
                    const globalIndex = filtered.indexOf(cmd)
                    return (
                      <button
                        key={cmd.id}
                        onClick={() => {
                          cmd.action()
                          setOpen(false)
                          setQuery('')
                        }}
                        className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left ${globalIndex === selected ? 'bg-accent' : 'hover:bg-accent/50'}`}
                      >
                        <cmd.icon className="h-5 w-5 text-muted-foreground" />
                        <div className="flex-1">
                          <div className="font-medium">{cmd.title}</div>
                          {cmd.description && (
                            <div className="text-xs text-muted-foreground">{cmd.description}</div>
                          )}
                        </div>
                        <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100" />
                      </button>
                    )
                  })}
                </div>
              )
          )}
          {filtered.length === 0 && (
            <div className="p-8 text-center text-muted-foreground">
              No results found for "{query}"
            </div>
          )}
        </div>
        <div className="border-t px-4 py-2 text-xs text-muted-foreground">
          <span className="mr-4">
            <kbd className="rounded border bg-muted px-1">↑↓</kbd> Navigate
          </span>
          <span className="mr-4">
            <kbd className="rounded border bg-muted px-1">↵</kbd> Select
          </span>
          <span>
            <kbd className="rounded border bg-muted px-1">⌘K</kbd> Toggle
          </span>
        </div>
      </div>
    </div>
  )
}

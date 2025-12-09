import {
  Code,
  Database,
  FileText,
  FolderOpen,
  GitBranch,
  Globe,
  Image,
  LayoutDashboard,
  Rocket,
  Settings,
  TestTube,
} from 'lucide-react'
import { Link, useLocation } from '@tanstack/react-router'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Projects', href: '/projects', icon: FolderOpen },
]

const views = [
  { name: 'Feature', href: 'feature', icon: FileText },
  { name: 'Code', href: 'code', icon: Code },
  { name: 'Test', href: 'test', icon: TestTube },
  { name: 'Graph', href: 'graph', icon: GitBranch },
  { name: 'API', href: 'api', icon: Globe },
  { name: 'Database', href: 'database', icon: Database },
  { name: 'Wireframe', href: 'wireframe', icon: Image },
  { name: 'Documentation', href: 'documentation', icon: FileText },
  { name: 'Deployment', href: 'deployment', icon: Rocket },
]

export function Sidebar() {
  const location = useLocation()
  const isProjectPage = location.pathname.includes('/projects/')

  return (
    <aside className="flex w-64 flex-col border-r bg-card">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 border-b px-6">
        <GitBranch className="h-8 w-8 text-primary" />
        <span className="text-xl font-bold">TraceRTM</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}

        {/* Views (shown when on project page) */}
        {isProjectPage && (
          <>
            <div className="my-4 border-t pt-4">
              <p className="px-3 text-xs font-semibold uppercase text-muted-foreground">Views</p>
            </div>
            {views.map((view) => {
              const viewPath = location.pathname.split('/').slice(0, 3).join('/') + '/' + view.href
              const isActive = location.pathname.endsWith('/' + view.href)
              return (
                <Link
                  key={view.name}
                  to={viewPath}
                  className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  )}
                >
                  <view.icon className="h-5 w-5" />
                  {view.name}
                </Link>
              )
            })}
          </>
        )}
      </nav>

      {/* Settings */}
      <div className="border-t p-4">
        <Link
          to="/settings"
          className={cn(
            'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
            location.pathname === '/settings'
              ? 'bg-primary text-primary-foreground'
              : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
          )}
        >
          <Settings className="h-5 w-5" />
          Settings
        </Link>
      </div>
    </aside>
  )
}

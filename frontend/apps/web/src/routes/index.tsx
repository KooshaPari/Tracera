import { createFileRoute } from '@tanstack/react-router'
import { DashboardView } from '@/views/DashboardView'

export const Route = createFileRoute('/')({
  component: DashboardView,
  loader: async () => {
    // Preload dashboard data for enterprise feel
    const [{ fetchProjects }, { fetchRecentItems }, { fetchSystemStatus }] = await Promise.all([
      import('@/api/projects'),
      import('@/api/items'),
      import('@/api/system')
    ])
    
    const [projects, recentItems, systemStatus] = await Promise.all([
      fetchProjects({ limit: 10 }),
      fetchRecentItems({ limit: 20 }),
      fetchSystemStatus()
    ])
    
    return { projects, recentItems, systemStatus }
  }
})

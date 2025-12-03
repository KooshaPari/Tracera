import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { SettingsView } from '@/views/SettingsView'

export const Route = createFileRoute('/settings/')({
  component: SettingsComponent,
  loader: async () => {
    const { fetchSettings } = await import('@/api/settings')
    const settings = await fetchSettings()
    
    return { settings }
  }
})

function SettingsComponent() {
  const { settings } = useLoaderData({ from: '/settings/' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Configure your TraceRTM platform preferences and integrations
          </p>
        </div>
      </div>
      
      <SettingsView settings={settings} loading={false} />
    </div>
  )
}

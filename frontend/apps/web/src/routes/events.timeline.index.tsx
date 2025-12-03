import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { EventsTimelineView } from '@/views/EventsTimelineView'

export const Route = createFileRoute('/events/timeline/')({
  component: EventsTimelineComponent,
  loader: async ({ searchParams }) => {
    const { fetchEvents } = await import('@/api/events')
    const events = await fetchEvents({ 
      projectId: searchParams.projectId as string,
      type: searchParams.type as string,
      startDate: searchParams.startDate as string,
      endDate: searchParams.endDate as string,
      limit: parseInt(searchParams.limit as string) || 100
    })
    
    const { fetchProjects } = await import('@/api/projects')
    const projects = await fetchProjects({ limit: 50 })
    
    return { events, projects, searchParams }
  }
})

function EventsTimelineComponent() {
  const { events, projects, searchParams } = useLoaderData({ from: '/events/timeline/' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Events Timeline</h1>
          <p className="text-muted-foreground">
            Complete audit trail and project history with time-travel capabilities
          </p>
        </div>
      </div>
      
      <EventsTimelineView 
        events={events}
        projects={projects}
        filters={searchParams}
        loading={false}
      />
    </div>
  )
}

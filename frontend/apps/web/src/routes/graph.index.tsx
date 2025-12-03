import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { GraphView } from '@/views/GraphView'

export const Route = createFileRoute('/graph/')({
  component: GraphComponent,
  loader: async ({ searchParams }) => {
    const { fetchGraphData } = await import('@/api/graph')
    const graphData = await fetchGraphData({ 
      projectId: searchParams.projectId as string,
      type: searchParams.type as string,
      depth: parseInt(searchParams.depth as string) || 3,
      nodeLimit: parseInt(searchParams.nodeLimit as string) || 100
    })
    
    return { graphData, searchParams }
  }
})

function GraphComponent() {
  const { graphData, searchParams } = useLoaderData({ from: '/graph/' })
  
  return (
    <div className="flex-1 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Graph Visualization</h1>
          <p className="text-muted-foreground">
            Interactive graph of project relationships and dependencies
          </p>
        </div>
      </div>
      
      <GraphView 
        data={graphData}
        filters={searchParams}
        loading={false}
      />
    </div>
  )
}

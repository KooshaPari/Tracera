import { createFileRoute, useLoaderData, redirect } from '@tanstack/react-router'
import { FEATURE_VIEW } from '@/routes/projects.$projectId.views.feature'
import { CODE_VIEW } from '@/routes/projects.$projectId.views.code'
import { TEST_VIEW } from '@/routes/projects.$projectId.views.test'
import { API_VIEW } from '@/routes/projects.$projectId.views.api'
import { DATABASE_VIEW } from '@/routes/projects.$projectId.views.database'
import { WIREFRAME_VIEW } from '@/routes/projects.$projectId.views.wireframe'
import { ARCHITECTURE_VIEW } from '@/routes/projects.$projectId.views.architecture'
import { INFRASTRUCTURE_VIEW } from '@/routes/projects.$projectId.views.infrastructure'
import { DATAFLOW_VIEW } from '@/routes/projects.$projectId.views.dataflow'
import { SECURITY_VIEW } from '@/routes/projects.$projectId.views.security'
import { PERFORMANCE_VIEW } from '@/routes/projects.$projectId.views.performance'
import { MONITORING_VIEW } from '@/routes/projects.$projectId.views.monitoring'
import { DOMAIN_VIEW } from '@/routes/projects.$projectId.views.domain'
import { JOURNEY_VIEW } from '@/routes/projects.$projectId.views.journey'
import { CONFIGURATION_VIEW } from '@/routes/projects.$projectId.views.configuration'
import { DEPENDENCY_VIEW } from '@/routes/projects.$projectId.views.dependency'

interface RouteParams {
  projectId: string
  viewType: string
}

export const Route = createFileRoute('/projects/$projectId/views/$viewType')({
  component: ViewTypeComponent,
  loader: async ({ params }) => {
    const { fetchProject } = await import('@/api/projects')
    const project = await fetchProject(params.projectId)
    
    return { project, viewType: params.viewType }
  },
})

function ViewTypeComponent() {
  const { project, viewType } = useLoaderData({ from: '/projects/$projectId/views/$viewType' })
  
  // Based on viewType, render the appropriate view component
  switch (viewType) {
    case 'feature':
      return <FEATURE_VIEW />
    case 'code':
      return <CODE_VIEW />
    case 'test':
      return <TEST_VIEW />
    case 'api':
      return <API_VIEW />
    case 'database':
      return <DATABASE_VIEW />
    case 'wireframe':
      return <WIREFRAME_VIEW />
    case 'architecture':
      return <ARCHITECTURE_VIEW />
    case 'infrastructure':
      return <INFRASTRUCTURE_VIEW />
    case 'dataflow':
      return <DATAFLOW_VIEW />
    case 'security':
      return <SECURITY_VIEW />
    case 'performance':
      return <PERFORMANCE_VIEW />
    case 'monitoring':
      return <MONITORING_VIEW />
    case 'domain':
      return <DOMAIN_VIEW />
    case 'journey':
      return <JOURNEY_VIEW />
    case 'configuration':
      return <CONFIGURATION_VIEW />
    case 'dependency':
      return <DEPENDENCY_VIEW />
    default:
      throw new Error(`Unknown view type: ${viewType}`)
  }
}



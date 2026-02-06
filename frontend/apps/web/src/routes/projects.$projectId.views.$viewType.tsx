import {
  Outlet,
  createFileRoute,
  useLoaderData,
  useLocation,
  useParams,
} from '@tanstack/react-router';
import React, { Suspense, lazy } from 'react';

import { ChunkLoadingSkeleton } from '@/lib/lazy-loading';
import { logger } from '@/lib/logger';
import { requireAuth } from '@/lib/route-guards';
import { API_VIEW } from '@/routes/projects.$projectId.views.api';
import { ARCHITECTURE_VIEW } from '@/routes/projects.$projectId.views.architecture';
import { CODE_VIEW } from '@/routes/projects.$projectId.views.code';
import { CONFIGURATION_VIEW } from '@/routes/projects.$projectId.views.configuration';
import { DATABASE_VIEW } from '@/routes/projects.$projectId.views.database';
import { DATAFLOW_VIEW } from '@/routes/projects.$projectId.views.dataflow';
import { DEPENDENCY_VIEW } from '@/routes/projects.$projectId.views.dependency';
import { DOMAIN_VIEW } from '@/routes/projects.$projectId.views.domain';
import { FEATURE_VIEW } from '@/routes/projects.$projectId.views.feature';
import { INFRASTRUCTURE_VIEW } from '@/routes/projects.$projectId.views.infrastructure';
import { JOURNEY_VIEW } from '@/routes/projects.$projectId.views.journey';
import { MONITORING_VIEW } from '@/routes/projects.$projectId.views.monitoring';
import { PERFORMANCE_VIEW } from '@/routes/projects.$projectId.views.performance';
import { PROBLEM_VIEW } from '@/routes/projects.$projectId.views.problem';
import { PROCESS_VIEW } from '@/routes/projects.$projectId.views.process';
import { SECURITY_VIEW } from '@/routes/projects.$projectId.views.security';
import { TEST_VIEW } from '@/routes/projects.$projectId.views.test';
import { WIREFRAME_VIEW } from '@/routes/projects.$projectId.views.wireframe';

// Lazy load heavy components that use graph visualization
// These components import elkjs, cytoscape, @xyflow which are all heavy
const GraphViewLazy = lazy((() =>
  import('@/pages/projects/views/GraphView')
    .then((m) => {
      const Comp = m?.GraphView;
      if (typeof Comp !== 'function') {
        logger.error('GraphView module did not export GraphView', m);
        return {
          default: () => <LazyFallback message='Failed to load Graph view.' />,
        };
      }
      return { default: Comp };
    })
    .catch((error) => {
      logger.error('GraphView chunk failed to load', error);
      return {
        default: () => <LazyFallback message='Failed to load Graph view.' />,
      };
    })) as any);
function LazyFallback({ message }: { message: string }) {
  return (
    <div className='text-destructive p-6' role='alert'>
      {message}
    </div>
  );
}

const IntegrationsViewLazy = lazy((() =>
  import('@/pages/projects/views/IntegrationsView').then((m) => {
    const Comp = m.default ?? (m as { IntegrationsView?: unknown }).IntegrationsView;
    if (typeof Comp !== 'function' && typeof Comp !== 'object') {
      logger.error('IntegrationsView module did not export a component', m);
      return {
        default: () => <LazyFallback message='Failed to load Integrations view.' />,
      };
    }
    return { default: Comp as React.ComponentType<{ projectId: string }> };
  })) as any);
const CoverageMatrixViewLazy = lazy((() =>
  import('@/pages/projects/views/CoverageMatrixView').then((m) => {
    const Comp = m?.CoverageMatrixView;
    if (typeof Comp !== 'function') {
      logger.error('CoverageMatrixView module did not export CoverageMatrixView', m);
      return {
        default: () => <LazyFallback message='Failed to load Coverage view.' />,
      };
    }
    return { default: Comp as React.ComponentType<{ projectId: string }> };
  })) as any);
const QADashboardViewLazy = lazy((() =>
  import('@/pages/projects/views/QADashboardView').then((m) => {
    const Comp = m?.QADashboardView;
    if (typeof Comp !== 'function') {
      logger.error('QADashboardView module did not export QADashboardView', m);
      return {
        default: () => <LazyFallback message='Failed to load QA Dashboard view.' />,
      };
    }
    return { default: Comp as React.ComponentType<{ projectId: string }> };
  })) as any);
const TestCaseViewLazy = lazy((() =>
  import('@/pages/projects/views/TestCaseView').then((m) => {
    const Comp = m?.TestCaseView ?? m?.default;
    if (typeof Comp !== 'function') {
      logger.error('TestCaseView module did not export TestCaseView', m);
      return {
        default: () => <LazyFallback message='Failed to load Test Cases view.' />,
      };
    }
    return { default: Comp as React.ComponentType<{ projectId: string }> };
  })) as any);
const TestRunViewLazy = lazy((() =>
  import('@/pages/projects/views/TestRunView').then((m) => {
    const Comp = m?.TestRunView ?? m?.default;
    if (typeof Comp !== 'function') {
      logger.error('TestRunView module did not export TestRunView', m);
      return {
        default: () => <LazyFallback message='Failed to load Test Runs view.' />,
      };
    }
    return { default: Comp as React.ComponentType<{ projectId: string }> };
  })) as any);
const TestSuiteViewLazy = lazy((() =>
  import('@/pages/projects/views/TestSuiteView').then((m) => {
    const Comp = m?.TestSuiteView ?? m?.default;
    if (typeof Comp !== 'function') {
      logger.error('TestSuiteView module did not export TestSuiteView', m);
      return {
        default: () => <LazyFallback message='Failed to load Test Suites view.' />,
      };
    }
    return { default: Comp as React.ComponentType<{ projectId: string }> };
  })) as any);
const WebhookIntegrationsViewLazy = lazy((() =>
  import('@/pages/projects/views/WebhookIntegrationsView').then((m) => {
    const Comp = m?.WebhookIntegrationsView;
    if (typeof Comp !== 'function') {
      logger.error('WebhookIntegrationsView module did not export WebhookIntegrationsView', m);
      return {
        default: () => <LazyFallback message='Failed to load Webhooks view.' />,
      };
    }
    return { default: Comp as React.ComponentType<{ projectId: string }> };
  })) as any);
const WorkflowRunsViewLazy = lazy((() =>
  import('@/pages/projects/views/WorkflowRunsView').then((m) => {
    const Comp = m?.WorkflowRunsView;
    if (typeof Comp !== 'function') {
      logger.error('WorkflowRunsView module did not export WorkflowRunsView', m);
      return {
        default: () => <LazyFallback message='Failed to load Workflows view.' />,
      };
    }
    return { default: Comp as React.ComponentType<{ projectId: string }> };
  })) as any);
const ImpactAnalysisViewLazy = lazy((() =>
  import('@/views/ImpactAnalysisView').then((m) => {
    const Comp = m?.ImpactAnalysisView;
    if (typeof Comp !== 'function') {
      logger.error('ImpactAnalysisView module did not export ImpactAnalysisView', m);
      return {
        default: () => <LazyFallback message='Failed to load Impact Analysis view.' />,
      };
    }
    return { default: Comp as React.ComponentType<{ projectId: string }> };
  })) as any);
const TraceabilityMatrixViewLazy = lazy((() =>
  import('@/views/TraceabilityMatrixView').then((m) => {
    const Comp = m?.TraceabilityMatrixView;
    if (typeof Comp !== 'function') {
      logger.error('TraceabilityMatrixView module did not export TraceabilityMatrixView', m);
      return {
        default: () => <LazyFallback message='Failed to load Traceability view.' />,
      };
    }
    return { default: Comp as React.ComponentType<{ projectId: string }> };
  })) as any);

function LoadingFallback() {
  return <ChunkLoadingSkeleton message='Loading view...' />;
}

function ViewTypeComponent() {
  const { viewType } = useLoaderData({
    from: '/projects/$projectId/views/$viewType',
  });
  const { projectId } = useParams({
    from: '/projects/$projectId/views/$viewType',
  });
  const location = useLocation();

  // When URL has an itemId (e.g. /projects/x/views/feature/y), render the item-detail child route instead of the list/registry
  const pathParts = location.pathname.split('/').filter(Boolean);
  const isItemDetailRoute =
    pathParts[0] === 'projects' && pathParts[2] === 'views' && pathParts.length >= 5;
  if (isItemDetailRoute) {
    return <Outlet />;
  }

  // Based on viewType, render the appropriate view component (list/registry)
  switch (viewType) {
    case 'feature':
    case 'story': {
      return <FEATURE_VIEW />;
    }
    case 'code': {
      return <CODE_VIEW />;
    }
    case 'test': {
      return <TEST_VIEW />;
    }
    case 'api': {
      return <API_VIEW />;
    }
    case 'database': {
      return <DATABASE_VIEW />;
    }
    case 'wireframe': {
      return <WIREFRAME_VIEW />;
    }
    case 'architecture': {
      return <ARCHITECTURE_VIEW />;
    }
    case 'infrastructure': {
      return <INFRASTRUCTURE_VIEW />;
    }
    case 'dataflow': {
      return <DATAFLOW_VIEW />;
    }
    case 'security': {
      return <SECURITY_VIEW />;
    }
    case 'performance': {
      return <PERFORMANCE_VIEW />;
    }
    case 'monitoring': {
      return <MONITORING_VIEW />;
    }
    case 'domain': {
      return <DOMAIN_VIEW />;
    }
    case 'journey': {
      return <JOURNEY_VIEW />;
    }
    case 'configuration': {
      return <CONFIGURATION_VIEW />;
    }
    case 'dependency': {
      return <DEPENDENCY_VIEW />;
    }
    case 'problem': {
      return <PROBLEM_VIEW />;
    }
    case 'process': {
      return <PROCESS_VIEW />;
    }
    case 'graph': {
      if (!projectId) {
        return (
          <div className='p-6'>
            <h1 className='text-2xl font-semibold'>Project required</h1>
            <p className='text-muted-foreground'>
              Graph view requires a project. Go to Projects and open a project, then use Graph from
              the sidebar.
            </p>
          </div>
        );
      }
      return (
        <Suspense fallback={<LoadingFallback />}>
          <GraphViewLazy projectId={projectId} />
        </Suspense>
      );
    }
    case 'integrations': {
      return (
        <Suspense fallback={<LoadingFallback />}>
          <IntegrationsViewLazy projectId={projectId} />
        </Suspense>
      );
    }
    case 'webhooks': {
      return (
        <Suspense fallback={<LoadingFallback />}>
          <WebhookIntegrationsViewLazy projectId={projectId} />
        </Suspense>
      );
    }
    case 'coverage': {
      return (
        <Suspense fallback={<LoadingFallback />}>
          <CoverageMatrixViewLazy projectId={projectId} />
        </Suspense>
      );
    }
    case 'qa-dashboard': {
      return (
        <Suspense fallback={<LoadingFallback />}>
          <QADashboardViewLazy projectId={projectId} />
        </Suspense>
      );
    }
    case 'test-cases': {
      return (
        <Suspense fallback={<LoadingFallback />}>
          <TestCaseViewLazy projectId={projectId} />
        </Suspense>
      );
    }
    case 'test-runs': {
      return (
        <Suspense fallback={<LoadingFallback />}>
          <TestRunViewLazy projectId={projectId} />
        </Suspense>
      );
    }
    case 'test-suites': {
      return (
        <Suspense fallback={<LoadingFallback />}>
          <TestSuiteViewLazy projectId={projectId} />
        </Suspense>
      );
    }
    case 'workflows': {
      return (
        <Suspense fallback={<LoadingFallback />}>
          <WorkflowRunsViewLazy projectId={projectId} />
        </Suspense>
      );
    }
    case 'impact-analysis': {
      return (
        <Suspense fallback={<LoadingFallback />}>
          <ImpactAnalysisViewLazy projectId={projectId} />
        </Suspense>
      );
    }
    case 'traceability':
    case 'matrix': {
      return (
        <Suspense fallback={<LoadingFallback />}>
          <TraceabilityMatrixViewLazy projectId={projectId} />
        </Suspense>
      );
    }
    default: {
      return (
        <div className='p-6'>
          <h1 className='text-2xl font-semibold'>Unknown view</h1>
          <p className='text-muted-foreground'>Unknown view type: {viewType}</p>
        </div>
      );
    }
  }
}

export const Route = createFileRoute('/projects/$projectId/views/$viewType')({
  beforeLoad: async () => await requireAuth(),
  component: ViewTypeComponent,
  loader: async ({ params }: { params: { viewType: string } }) => ({
    viewType: params.viewType,
  }),
});

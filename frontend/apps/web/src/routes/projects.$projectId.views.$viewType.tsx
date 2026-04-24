import { Outlet, createFileRoute, useLocation, useParams } from '@tanstack/react-router';
import React, { Suspense, lazy } from 'react';

import { ChunkLoadingSkeleton } from '@/lib/lazy-loading';
import { logger } from '@/lib/logger';
import { requireAuth } from '@/lib/route-guards';
import { API_VIEW as ApiView } from '@/routes/projects.$projectId.views.api';
import { ARCHITECTURE_VIEW as ArchitectureView } from '@/routes/projects.$projectId.views.architecture';
import { CODE_VIEW as CodeView } from '@/routes/projects.$projectId.views.code';
import { CONFIGURATION_VIEW as ConfigurationView } from '@/routes/projects.$projectId.views.configuration';
import { DATABASE_VIEW as DatabaseView } from '@/routes/projects.$projectId.views.database';
import { DATAFLOW_VIEW as DataflowView } from '@/routes/projects.$projectId.views.dataflow';
import { DEPENDENCY_VIEW as DependencyView } from '@/routes/projects.$projectId.views.dependency';
import { DOMAIN_VIEW as DomainView } from '@/routes/projects.$projectId.views.domain';
import { FEATURE_VIEW as FeatureView } from '@/routes/projects.$projectId.views.feature';
import { INFRASTRUCTURE_VIEW as InfrastructureView } from '@/routes/projects.$projectId.views.infrastructure';
import { JOURNEY_VIEW as JourneyView } from '@/routes/projects.$projectId.views.journey';
import { MONITORING_VIEW as MonitoringView } from '@/routes/projects.$projectId.views.monitoring';
import { PERFORMANCE_VIEW as PerformanceView } from '@/routes/projects.$projectId.views.performance';
import { PROBLEM_VIEW as ProblemView } from '@/routes/projects.$projectId.views.problem';
import { PROCESS_VIEW as ProcessView } from '@/routes/projects.$projectId.views.process';
import { SECURITY_VIEW as SecurityView } from '@/routes/projects.$projectId.views.security';
import { TEST_VIEW as TestView } from '@/routes/projects.$projectId.views.test';
import { WIREFRAME_VIEW as WireframeView } from '@/routes/projects.$projectId.views.wireframe';

interface ProjectViewProps {
  projectId: string;
}

interface LazyComponentModule<TProps> {
  default: React.ComponentType<TProps>;
}

type UnknownModule = Record<string, unknown>;
type ProjectViewComponent = React.ComponentType<ProjectViewProps>;
type StaticViewComponent = React.ComponentType;
interface LazyViewDefinition {
  component: React.LazyExoticComponent<ProjectViewComponent>;
  requiresProjectId?: boolean;
}

const ROUTE_PATH = '/projects/$projectId/views/$viewType';

function LazyFallback({ message }: { message: string }): React.JSX.Element {
  return (
    <div className='text-destructive p-6' role='alert'>
      {message}
    </div>
  );
}

function LoadingFallback(): React.JSX.Element {
  return <ChunkLoadingSkeleton message='Loading view...' />;
}

const loadingFallbackNode = <LoadingFallback />;

function isComponentType(candidateComponent: unknown): candidateComponent is ProjectViewComponent {
  if (typeof candidateComponent === 'function') {
    return true;
  }

  return typeof candidateComponent === 'object' && candidateComponent !== null;
}

function createFailureComponent(message: string): ProjectViewComponent {
  return function LazyErrorFallback(): React.JSX.Element {
    return <LazyFallback message={message} />;
  };
}

function createLazyView(
  loader: () => Promise<UnknownModule>,
  exportNames: readonly string[],
  logName: string,
  fallbackMessage: string,
): React.LazyExoticComponent<ProjectViewComponent> {
  return lazy(async (): Promise<LazyComponentModule<ProjectViewProps>> => {
    try {
      const moduleExports = await loader();
      for (const exportName of exportNames) {
        const candidateExport = moduleExports[exportName];
        if (isComponentType(candidateExport)) {
          return { default: candidateExport };
        }
      }

      logger.error(`${logName} module did not export expected component`, moduleExports);
    } catch (loadError: unknown) {
      logger.error(`${logName} chunk failed to load`, loadError);
    }

    return { default: createFailureComponent(fallbackMessage) };
  });
}

const GraphViewLazy = createLazyView(
  async () => import('@/pages/projects/views/GraphView'),
  ['GraphView'],
  'GraphView',
  'Failed to load Graph view.',
);

const IntegrationsViewLazy = createLazyView(
  async () => import('@/pages/projects/views/IntegrationsView'),
  ['default', 'IntegrationsView'],
  'IntegrationsView',
  'Failed to load Integrations view.',
);

const CoverageMatrixViewLazy = createLazyView(
  async () => import('@/pages/projects/views/CoverageMatrixView'),
  ['CoverageMatrixView'],
  'CoverageMatrixView',
  'Failed to load Coverage view.',
);

const QADashboardViewLazy = createLazyView(
  async () => import('@/pages/projects/views/QADashboardView'),
  ['QADashboardView'],
  'QADashboardView',
  'Failed to load QA Dashboard view.',
);

const TestCaseViewLazy = createLazyView(
  async () => import('@/pages/projects/views/TestCaseView'),
  ['TestCaseView', 'default'],
  'TestCaseView',
  'Failed to load Test Cases view.',
);

const TestRunViewLazy = createLazyView(
  async () => import('@/pages/projects/views/TestRunView'),
  ['TestRunView', 'default'],
  'TestRunView',
  'Failed to load Test Runs view.',
);

const TestSuiteViewLazy = createLazyView(
  async () => import('@/pages/projects/views/TestSuiteView'),
  ['TestSuiteView', 'default'],
  'TestSuiteView',
  'Failed to load Test Suites view.',
);

const WebhookIntegrationsViewLazy = createLazyView(
  async () => import('@/pages/projects/views/WebhookIntegrationsView'),
  ['WebhookIntegrationsView'],
  'WebhookIntegrationsView',
  'Failed to load Webhooks view.',
);

const WorkflowRunsViewLazy = createLazyView(
  async () => import('@/pages/projects/views/WorkflowRunsView'),
  ['WorkflowRunsView'],
  'WorkflowRunsView',
  'Failed to load Workflows view.',
);

const ImpactAnalysisViewLazy = createLazyView(
  async () => import('@/views/ImpactAnalysisView'),
  ['ImpactAnalysisView'],
  'ImpactAnalysisView',
  'Failed to load Impact Analysis view.',
);

const TraceabilityMatrixViewLazy = createLazyView(
  async () => import('@/views/TraceabilityMatrixView'),
  ['TraceabilityMatrixView'],
  'TraceabilityMatrixView',
  'Failed to load Traceability view.',
);

const staticViewMap: Readonly<Record<string, StaticViewComponent>> = {
  api: ApiView,
  architecture: ArchitectureView,
  code: CodeView,
  configuration: ConfigurationView,
  dataflow: DataflowView,
  database: DatabaseView,
  dependency: DependencyView,
  domain: DomainView,
  feature: FeatureView,
  infrastructure: InfrastructureView,
  journey: JourneyView,
  monitoring: MonitoringView,
  performance: PerformanceView,
  problem: ProblemView,
  process: ProcessView,
  security: SecurityView,
  story: FeatureView,
  test: TestView,
  wireframe: WireframeView,
};

const lazyViewMap: Readonly<Record<string, LazyViewDefinition>> = {
  coverage: {
    component: CoverageMatrixViewLazy,
  },
  graph: {
    component: GraphViewLazy,
    requiresProjectId: true,
  },
  'impact-analysis': {
    component: ImpactAnalysisViewLazy,
  },
  integrations: {
    component: IntegrationsViewLazy,
  },
  'qa-dashboard': {
    component: QADashboardViewLazy,
  },
  matrix: {
    component: TraceabilityMatrixViewLazy,
  },
  'test-cases': {
    component: TestCaseViewLazy,
  },
  'test-runs': {
    component: TestRunViewLazy,
  },
  'test-suites': {
    component: TestSuiteViewLazy,
  },
  traceability: {
    component: TraceabilityMatrixViewLazy,
  },
  webhooks: {
    component: WebhookIntegrationsViewLazy,
  },
  workflows: {
    component: WorkflowRunsViewLazy,
  },
};

function isItemDetailRoute(pathname: string): boolean {
  const pathSegments = pathname.split('/').filter(Boolean);
  return pathSegments[0] === 'projects' && pathSegments[2] === 'views' && pathSegments.length >= 5;
}

function renderUnknownView(viewType: string): React.JSX.Element {
  return (
    <div className='p-6'>
      <h1 className='text-2xl font-semibold'>Unknown view</h1>
      <p className='text-muted-foreground'>Unknown view type: {viewType}</p>
    </div>
  );
}

function renderProjectRequiredMessage(): React.JSX.Element {
  return (
    <div className='p-6'>
      <h1 className='text-2xl font-semibold'>Project required</h1>
      <p className='text-muted-foreground'>
        Graph view requires a project. Go to Projects and open a project, then use Graph from the
        sidebar.
      </p>
    </div>
  );
}

function renderLazyView(
  lazyViewComponent: React.LazyExoticComponent<ProjectViewComponent>,
  projectId: string,
): React.JSX.Element {
  const LazyViewComponent = lazyViewComponent;
  return (
    <Suspense fallback={loadingFallbackNode}>
      <LazyViewComponent projectId={projectId} />
    </Suspense>
  );
}

function ViewTypeComponent(): React.JSX.Element {
  const { viewType, projectId }: { viewType: string; projectId: string } = useParams({
    from: ROUTE_PATH,
  });
  const location = useLocation();

  if (isItemDetailRoute(location.pathname)) {
    return <Outlet />;
  }

  const staticViewComponent = staticViewMap[viewType];
  if (typeof staticViewComponent !== 'undefined') {
    const StaticViewComponent = staticViewComponent;
    return <StaticViewComponent />;
  }

  const lazyViewDefinition = lazyViewMap[viewType];
  if (typeof lazyViewDefinition !== 'undefined') {
    const projectIdIsEmpty = projectId.trim().length === 0;
    if (lazyViewDefinition.requiresProjectId === true && projectIdIsEmpty) {
      return renderProjectRequiredMessage();
    }

    return renderLazyView(lazyViewDefinition.component, projectId);
  }

  return renderUnknownView(viewType);
}

export const Route = createFileRoute(ROUTE_PATH)({
  beforeLoad: async (): Promise<void> => {
    await requireAuth();
  },
  component: ViewTypeComponent,
  loader: ({ params }: { params: { viewType: string } }): { viewType: string } => ({
    viewType: params.viewType,
  }),
});

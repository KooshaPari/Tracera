import type { ViewType } from '@tracertm/types';

import itemsTableConstants from './constants';

const VIEW_LABELS: Record<
  string,
  {
    title: string;
    description: string;
    emptyTitle: string;
    emptyDescription: string;
    createModalTitle?: string;
    createButtonLabel?: string;
    newButtonLabel?: string;
  }
> = {
  api: {
    createButtonLabel: 'Create Endpoint',
    createModalTitle: 'Create API Endpoint',
    description: 'REST API contracts and specifications',
    emptyDescription: 'Add an endpoint or schema to document your API.',
    emptyTitle: 'No API endpoints yet',
    newButtonLabel: 'New Endpoint',
    title: 'API Endpoints',
  },
  architecture: {
    createButtonLabel: 'Create Item',
    createModalTitle: 'Create Architecture Item',
    description: 'Architecture decisions and components',
    emptyDescription: 'Add an architecture artifact to get started.',
    emptyTitle: 'No architecture items yet',
    newButtonLabel: 'New Item',
    title: 'Architecture',
  },
  code: {
    createButtonLabel: 'Create Item',
    createModalTitle: 'Create Code Item',
    description: 'Code and component traceability',
    emptyDescription: 'Add modules, files, or functions to trace.',
    emptyTitle: 'No code items yet',
    newButtonLabel: 'New Item',
    title: 'Code',
  },
  configuration: {
    createButtonLabel: 'Create Item',
    createModalTitle: 'Create Configuration Item',
    description: 'Configuration and settings',
    emptyDescription: 'Add configuration artifacts.',
    emptyTitle: 'No configuration items yet',
    newButtonLabel: 'New Item',
    title: 'Configuration',
  },
  database: {
    createButtonLabel: 'Create Item',
    createModalTitle: 'Create Database Item',
    description: 'Schema and table-level artifacts',
    emptyDescription: 'Add tables or schema artifacts to trace.',
    emptyTitle: 'No database items yet',
    newButtonLabel: 'New Item',
    title: 'Database',
  },
  dataflow: {
    createButtonLabel: 'Create Item',
    createModalTitle: 'Create Dataflow',
    description: 'Data flows and pipelines',
    emptyDescription: 'Add a data flow or pipeline to get started.',
    emptyTitle: 'No dataflow items yet',
    newButtonLabel: 'New Item',
    title: 'Dataflow',
  },
  dependency: {
    createButtonLabel: 'Create Item',
    createModalTitle: 'Create Item',
    description: 'Dependency and relationship view',
    emptyDescription: 'Add items and links to see dependencies.',
    emptyTitle: 'No dependencies yet',
    newButtonLabel: 'New Item',
    title: 'Dependencies',
  },
  domain: {
    createButtonLabel: 'Create Item',
    createModalTitle: 'Create Domain Item',
    description: 'Domain model and concepts',
    emptyDescription: 'Add entities or concepts to build your domain model.',
    emptyTitle: 'No domain items yet',
    newButtonLabel: 'New Item',
    title: 'Domain',
  },
  feature: {
    createButtonLabel: 'Create Feature',
    createModalTitle: 'Create Feature',
    description: 'Manage feature requirements and user stories',
    emptyDescription: 'Create your first feature or epic to get started.',
    emptyTitle: 'No features yet',
    newButtonLabel: 'New Feature',
    title: 'Features',
  },
  infrastructure: {
    createButtonLabel: 'Create Item',
    createModalTitle: 'Create Infrastructure Item',
    description: 'Infrastructure and deployment',
    emptyDescription: 'Add infrastructure or deployment artifacts.',
    emptyTitle: 'No infrastructure items yet',
    newButtonLabel: 'New Item',
    title: 'Infrastructure',
  },
  journey: {
    createButtonLabel: 'Create Item',
    createModalTitle: 'Create Journey',
    description: 'User journeys and flows',
    emptyDescription: 'Add a user journey or flow to get started.',
    emptyTitle: 'No journey items yet',
    newButtonLabel: 'New Journey',
    title: 'Journey',
  },
  monitoring: {
    createButtonLabel: 'Create Item',
    createModalTitle: 'Create Monitoring Item',
    description: 'Monitoring and observability',
    emptyDescription: 'Add monitoring or observability artifacts.',
    emptyTitle: 'No monitoring items yet',
    newButtonLabel: 'New Item',
    title: 'Monitoring',
  },
  performance: {
    createButtonLabel: 'Create Item',
    createModalTitle: 'Create Performance Item',
    description: 'Performance requirements and metrics',
    emptyDescription: 'Add performance requirements or metrics.',
    emptyTitle: 'No performance items yet',
    newButtonLabel: 'New Item',
    title: 'Performance',
  },
  security: {
    createButtonLabel: 'Create Item',
    createModalTitle: 'Create Security Item',
    description: 'Security requirements and controls',
    emptyDescription: 'Add security requirements or controls.',
    emptyTitle: 'No security items yet',
    newButtonLabel: 'New Item',
    title: 'Security',
  },
  test: {
    createButtonLabel: 'Create Test',
    createModalTitle: 'Create Test',
    description: 'Test cases and scenarios',
    emptyDescription: 'Create a test case or scenario to get started.',
    emptyTitle: 'No tests yet',
    newButtonLabel: 'New Test',
    title: 'Tests',
  },
  wireframe: {
    createButtonLabel: 'Create Wireframe',
    createModalTitle: 'Create Wireframe',
    description: 'UI wireframes and mockups',
    emptyDescription: 'Add a wireframe to get started.',
    emptyTitle: 'No wireframes yet',
    newButtonLabel: 'New Wireframe',
    title: 'Wireframes',
  },
};

function getViewLabels(view?: ViewType): {
  title: string;
  description: string;
  emptyTitle: string;
  emptyDescription: string;
  createModalTitle?: string;
  createButtonLabel?: string;
  newButtonLabel?: string;
} {
  let key: string = itemsTableConstants.EMPTY_STRING;
  if (typeof view === 'string') {
    key = view.toLowerCase();
  }
  const labels = VIEW_LABELS[key];
  if (labels !== undefined) {
    return labels;
  }
  return {
    createButtonLabel: itemsTableConstants.DEFAULT_CREATE_LABEL,
    createModalTitle: itemsTableConstants.DEFAULT_CREATE_LABEL,
    description: itemsTableConstants.DEFAULT_DESCRIPTION,
    emptyDescription: itemsTableConstants.DEFAULT_EMPTY_DESCRIPTION,
    emptyTitle: itemsTableConstants.DEFAULT_EMPTY_TITLE,
    newButtonLabel: itemsTableConstants.DEFAULT_NEW_LABEL,
    title: itemsTableConstants.DEFAULT_TITLE,
  };
}

export { getViewLabels };

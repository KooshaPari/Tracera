import type { Meta, StoryObj } from '@storybook/react';

import { useState } from 'react';

import type { Item, Link } from '@tracertm/types';

import { logger } from '@/lib/logger';

import { CrossPerspectiveSearch } from '../CrossPerspectiveSearch';

const meta = {
  component: CrossPerspectiveSearch,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  title: 'Graph/CrossPerspectiveSearch',
} satisfies Meta<typeof CrossPerspectiveSearch>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Sample data for stories
 */
const createSampleItems = (): Item[] => [
  {
    createdAt: '2025-01-01',
    description: 'Implement OAuth 2.0 based user authentication with social login support',
    id: 'feat-auth',
    owner: 'alice@example.com',
    perspective: 'feature',
    priority: 'critical',
    projectId: 'proj-1',
    status: 'in_progress',
    title: 'User Authentication System',
    type: 'Feature',
    updatedAt: '2025-01-28',
    version: 1,
    view: 'feature',
  },
  {
    createdAt: '2025-01-05',
    description: 'Core service implementing OAuth 2.0 flows and token management',
    equivalentItemIds: ['feat-auth'],
    id: 'code-auth-service',
    perspective: 'code',
    priority: 'critical',
    projectId: 'proj-1',
    status: 'done',
    title: 'AuthenticationService',
    type: 'Service',
    updatedAt: '2025-01-27',
    version: 2,
    view: 'code',
  },
  {
    createdAt: '2025-01-10',
    description: 'React component for user login interface with form validation',
    id: 'code-login-component',
    perspective: 'code',
    priority: 'high',
    projectId: 'proj-1',
    status: 'done',
    title: 'LoginForm',
    type: 'Component',
    updatedAt: '2025-01-25',
    version: 3,
    view: 'code',
  },
  {
    createdAt: '2025-01-12',
    description: 'Comprehensive tests for auth flows including edge cases',
    id: 'test-auth',
    perspective: 'test',
    priority: 'high',
    projectId: 'proj-1',
    status: 'in_progress',
    title: 'Authentication Integration Tests',
    type: 'TestSuite',
    updatedAt: '2025-01-28',
    version: 1,
    view: 'test',
  },
  {
    createdAt: '2025-01-01',
    description: 'User login endpoint accepting email and password',
    equivalentItemIds: ['feat-auth'],
    id: 'api-login',
    perspective: 'api',
    priority: 'critical',
    projectId: 'proj-1',
    status: 'done',
    title: 'POST /api/auth/login',
    type: 'Endpoint',
    updatedAt: '2025-01-20',
    version: 1,
    view: 'api',
  },
  {
    createdAt: '2025-01-02',
    description: 'Token refresh endpoint',
    id: 'api-refresh',
    perspective: 'api',
    priority: 'high',
    projectId: 'proj-1',
    status: 'done',
    title: 'POST /api/auth/refresh',
    type: 'Endpoint',
    updatedAt: '2025-01-20',
    version: 1,
    view: 'api',
  },
  {
    createdAt: '2025-01-01',
    description: 'Stores user account information and auth credentials',
    id: 'db-users',
    perspective: 'database',
    priority: 'critical',
    projectId: 'proj-1',
    status: 'done',
    title: 'users_table',
    type: 'Table',
    updatedAt: '2025-01-15',
    version: 1,
    view: 'database',
  },
  {
    createdAt: '2025-01-03',
    description: 'Stores active user sessions and tokens',
    id: 'db-sessions',
    perspective: 'database',
    priority: 'high',
    projectId: 'proj-1',
    status: 'done',
    title: 'sessions_table',
    type: 'Table',
    updatedAt: '2025-01-15',
    version: 1,
    view: 'database',
  },
  {
    createdAt: '2025-01-08',
    description: 'Wireframe showing login form layout and components',
    id: 'wire-login',
    perspective: 'wireframe',
    priority: 'medium',
    projectId: 'proj-1',
    status: 'done',
    title: 'Login Page Layout',
    type: 'Wireframe',
    updatedAt: '2025-01-22',
    version: 2,
    view: 'wireframe',
  },
  {
    createdAt: '2025-01-20',
    description: 'Implement rate limiting, CSRF protection, and secure token storage',
    id: 'sec-auth',
    perspective: 'security',
    priority: 'critical',
    projectId: 'proj-1',
    status: 'blocked',
    title: 'Authentication Security Hardening',
    type: 'SecurityControl',
    updatedAt: '2025-01-28',
    version: 1,
    view: 'security',
  },
  {
    createdAt: '2025-01-25',
    description: 'Optimize login endpoint response time (target: <200ms)',
    id: 'perf-auth',
    perspective: 'performance',
    priority: 'medium',
    projectId: 'proj-1',
    status: 'todo',
    title: 'Auth Endpoint Optimization',
    type: 'PerformanceOptimization',
    updatedAt: '2025-01-25',
    version: 1,
    view: 'performance',
  },
];

const createSampleLinks = (): Link[] => [
  {
    confidence: 0.95,
    createdAt: '2025-01-10',
    id: 'link-1',
    projectId: 'proj-1',
    sourceId: 'feat-auth',
    status: 'confirmed',
    targetId: 'code-auth-service',
    type: 'represents',
    updatedAt: '2025-01-10',
    version: 1,
  },
  {
    confidence: 0.98,
    createdAt: '2025-01-10',
    id: 'link-2',
    projectId: 'proj-1',
    sourceId: 'feat-auth',
    status: 'confirmed',
    targetId: 'api-login',
    type: 'same_as',
    updatedAt: '2025-01-10',
    version: 1,
  },
  {
    confidence: 1,
    createdAt: '2025-01-10',
    id: 'link-3',
    projectId: 'proj-1',
    sourceId: 'code-auth-service',
    status: 'auto',
    targetId: 'db-users',
    type: 'depends_on',
    updatedAt: '2025-01-10',
    version: 1,
  },
  {
    confidence: 0.9,
    createdAt: '2025-01-15',
    id: 'link-4',
    projectId: 'proj-1',
    sourceId: 'test-auth',
    status: 'confirmed',
    targetId: 'feat-auth',
    type: 'tests',
    updatedAt: '2025-01-15',
    version: 1,
  },
  {
    confidence: 0.85,
    createdAt: '2025-01-20',
    id: 'link-5',
    projectId: 'proj-1',
    sourceId: 'wire-login',
    status: 'suggested',
    targetId: 'code-login-component',
    type: 'represents',
    updatedAt: '2025-01-20',
    version: 1,
  },
  {
    confidence: 0.8,
    createdAt: '2025-01-25',
    id: 'link-6',
    projectId: 'proj-1',
    sourceId: 'sec-auth',
    status: 'confirmed',
    targetId: 'feat-auth',
    type: 'related_to',
    updatedAt: '2025-01-25',
    version: 1,
  },
];

/**
 * Basic full-featured search component
 */
export const Default: Story = {
  render: (_args) => {
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [_highlightedId, setHighlightedId] = useState<string | null>(null);

    return (
      <div className='mx-auto max-w-4xl space-y-4'>
        <CrossPerspectiveSearch
          items={createSampleItems()}
          links={createSampleLinks()}
          onSelect={(itemId) => {
            setSelectedId(itemId);
            logger.info('Selected item:', itemId);
          }}
          onHighlight={(itemId) => {
            setHighlightedId(itemId);
            logger.info('Highlighted item:', itemId);
          }}
        />
        {selectedId && (
          <div className='bg-accent rounded-lg border p-4'>
            <p className='text-sm font-semibold'>Selected item ID:</p>
            <code className='text-xs'>{selectedId}</code>
          </div>
        )}
      </div>
    );
  },
};

/**
 * Compact search component for inline use
 */
export const Compact: Story = {
  render: (_args) => {
    const [selectedId, setSelectedId] = useState<string | null>(null);

    return (
      <div className='mx-auto max-w-2xl space-y-4'>
        <div className='bg-muted rounded-lg p-4'>
          <p className='mb-3 text-sm font-semibold'>Compact Mode (inline search)</p>
          <CrossPerspectiveSearch
            items={createSampleItems()}
            links={createSampleLinks()}
            onSelect={(itemId) => {
              setSelectedId(itemId);
            }}
            onHighlight={() => {}}
            compact
          />
        </div>
        {selectedId && (
          <div className='bg-accent rounded-lg border p-4'>
            <p className='text-sm font-semibold'>Selected:</p>
            <code className='text-xs'>{selectedId}</code>
          </div>
        )}
      </div>
    );
  },
};

/**
 * Search with demonstrated keyboard navigation
 */
export const KeyboardNavigation: Story = {
  render: (_args) => {
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [keyboardTips] = useState('Use ↑↓ to navigate results | Enter to select | Esc to clear');

    return (
      <div className='mx-auto max-w-4xl space-y-4'>
        <div className='rounded border border-blue-200 bg-blue-50 p-3 text-sm dark:border-blue-800 dark:bg-blue-950/30'>
          <p className='font-semibold text-blue-900 dark:text-blue-100'>Keyboard Navigation</p>
          <p className='text-xs text-blue-700 dark:text-blue-300'>{keyboardTips}</p>
        </div>
        <CrossPerspectiveSearch
          items={createSampleItems()}
          links={createSampleLinks()}
          onSelect={(itemId) => {
            setSelectedId(itemId);
          }}
          onHighlight={() => {}}
        />
        {selectedId && (
          <div className='bg-accent rounded-lg border p-4'>
            <p className='text-sm'>
              Selected: <code className='font-mono text-xs'>{selectedId}</code>
            </p>
          </div>
        )}
      </div>
    );
  },
};

/**
 * Search demonstrating cross-perspective linking
 */
export const CrossPerspectiveExample: Story = {
  render: () => {
    const [selectedId, setSelectedId] = useState<string | null>(null);

    return (
      <div className='mx-auto max-w-4xl space-y-4'>
        <div className='space-y-2'>
          <h2 className='text-lg font-bold'>Cross-Perspective Search Example</h2>
          <p className='text-muted-foreground text-sm'>
            Try searching for "auth" to see how the same concept appears in multiple perspectives
            (Feature, Code, API, Database, etc.) with equivalence relationships shown below each
            result.
          </p>
        </div>
        <CrossPerspectiveSearch
          items={createSampleItems()}
          links={createSampleLinks()}
          onSelect={(itemId) => {
            setSelectedId(itemId);
            logger.info('Selected:', itemId);
          }}
          onHighlight={() => {}}
          maxResultsPerPerspective={3}
        />
        {selectedId && (
          <div className='bg-accent space-y-2 rounded-lg border p-4'>
            <p className='text-sm font-semibold'>Selected Item</p>
            <code className='block text-xs'>{selectedId}</code>
            <p className='text-muted-foreground text-xs'>
              This item now shows in the details panel and its equivalences are highlighted
            </p>
          </div>
        )}
      </div>
    );
  },
};

/**
 * Empty state
 */
export const EmptyState: Story = {
  render: () => (
    <div className='mx-auto max-w-4xl'>
      <CrossPerspectiveSearch items={[]} links={[]} onSelect={() => {}} onHighlight={() => {}} />
    </div>
  ),
};

/**
 * With custom max results per perspective
 */
export const CustomMaxResults: Story = {
  render: () => (
    <div className='mx-auto max-w-4xl space-y-4'>
      <p className='text-muted-foreground text-sm'>
        Showing only 2 results per perspective (normally 5)
      </p>
      <CrossPerspectiveSearch
        items={createSampleItems()}
        links={createSampleLinks()}
        onSelect={(id) => logger.info('Selected:', id)}
        onHighlight={() => {}}
        maxResultsPerPerspective={2}
      />
    </div>
  ),
};

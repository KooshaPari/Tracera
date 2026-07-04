import type { Meta, StoryObj } from '@storybook/react';

// TemporalNavigator Storybook stories
import type { Branch, Version } from '../TemporalNavigator';

import { logger } from '../../../lib/logger';
import { TemporalNavigator } from '../TemporalNavigator';

const meta = {
  component: TemporalNavigator,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs', 'skip-tests'],
  title: 'Temporal/TemporalNavigator',
} satisfies Meta<typeof TemporalNavigator>;

// Storybook requires default export for meta
export default meta;
type Story = StoryObj<typeof meta>;

const mockBranches: Branch[] = [
  {
    createdAt: new Date('2024-01-01'),
    description: 'Production branch',
    id: 'main',
    mergeRequestCount: 3,
    name: 'main',
    status: 'active',
    updatedAt: new Date('2024-01-20'),
  },
  {
    createdAt: new Date('2024-01-05'),
    description: 'Development branch',
    id: 'develop',
    mergeRequestCount: 5,
    name: 'develop',
    parentId: 'main',
    status: 'active',
    updatedAt: new Date('2024-01-19'),
  },
  {
    createdAt: new Date('2024-01-10'),
    id: 'feature-auth',
    mergeRequestCount: 1,
    name: 'feature/authentication',
    parentId: 'develop',
    status: 'review',
    updatedAt: new Date('2024-01-15'),
  },
];

const mockVersions: Version[] = [
  {
    author: 'Alice',
    branchId: 'main',
    description: 'First stable release with core features',
    id: 'v1.0.0',
    status: 'published',
    tag: '1.0.0',
    timestamp: new Date('2024-01-01'),
    title: 'v1.0.0 - Initial Release',
  },
  {
    author: 'Bob',
    branchId: 'main',
    description: 'Critical security patches',
    id: 'v1.0.1',
    status: 'published',
    tag: '1.0.1',
    timestamp: new Date('2024-01-05'),
    title: 'v1.0.1 - Bugfix',
  },
  {
    author: 'Charlie',
    branchId: 'main',
    description: 'Authentication and user management',
    id: 'v1.1.0',
    status: 'published',
    tag: '1.1.0',
    timestamp: new Date('2024-01-12'),
    title: 'v1.1.0 - New Features',
  },
];

export const Default: Story = {
  args: {
    branches: mockBranches,
    currentBranchId: 'main',
    currentVersionId: 'v1.1.0',
    onBranchChange: (branchId) => {
      logger.info('Branch changed to:', branchId);
    },
    onVersionChange: (versionId) => {
      logger.info('Version changed to:', versionId);
    },
    projectId: 'proj-123',
    versions: mockVersions,
  },
};

export const WithCreateActions: Story = {
  args: {
    ...Default.args,
    onBranchCreate: () => {
      logger.info('Create branch requested');
    },
    onMergeRequest: (source, target) => {
      logger.info(`Merge ${source} into ${target}`);
    },
  },
};

export const DevelopmentBranch: Story = {
  args: {
    ...Default.args,
    currentBranchId: 'develop',
  },
};

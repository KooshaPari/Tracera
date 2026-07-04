// BranchExplorer Storybook stories
import type { Meta, StoryObj } from '@storybook/react';

import type { Branch } from '../TemporalNavigator';

import { logger } from '../../../lib/logger';
import { BranchExplorer } from '../BranchExplorer';

const meta = {
  component: BranchExplorer,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  title: 'Temporal/BranchExplorer',
} satisfies Meta<typeof BranchExplorer>;

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
  {
    createdAt: new Date('2024-01-08'),
    id: 'feature-db',
    mergeRequestCount: 2,
    name: 'feature/database',
    parentId: 'develop',
    status: 'review',
    updatedAt: new Date('2024-01-18'),
  },
  {
    createdAt: new Date('2024-01-12'),
    id: 'hotfix-security',
    mergeRequestCount: 0,
    name: 'hotfix/security-patch',
    parentId: 'main',
    status: 'merged',
    updatedAt: new Date('2024-01-14'),
  },
  {
    createdAt: new Date('2023-12-01'),
    id: 'old-feature',
    mergeRequestCount: 0,
    name: 'old-feature/deprecated',
    parentId: 'develop',
    status: 'abandoned',
    updatedAt: new Date('2024-01-01'),
  },
];

export const Default: Story = {
  args: {
    branches: mockBranches,
    currentBranchId: 'main',
    onBranchChange: (branchId) => {
      logger.info('Branch changed to:', branchId);
    },
    projectId: 'proj-123',
  },
};

export const WithActions: Story = {
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

export const DevelopmentSelected: Story = {
  args: {
    ...Default.args,
    currentBranchId: 'develop',
  },
};

export const FeatureBranchSelected: Story = {
  args: {
    ...Default.args,
    currentBranchId: 'feature-auth',
  },
};

export const SingleBranch: Story = {
  args: {
    ...Default.args,
    branches: mockBranches[0] !== undefined ? [mockBranches[0]] : [],
  },
};

export const EmptyBranches: Story = {
  args: {
    ...Default.args,
    branches: [],
    currentBranchId: '',
  },
};

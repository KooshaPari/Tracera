import type { Meta, StoryObj } from '@storybook/react';

import { ProgressDashboard } from '@/components/temporal/ProgressDashboard';

const meta: Meta<typeof ProgressDashboard> = {
  argTypes: {
    isLoading: { control: 'boolean' },
    onMilestoneClick: { action: 'milestoneClick' },
    onSprintClick: { action: 'sprintClick' },
    projectId: { control: 'text' },
  },
  component: ProgressDashboard,
  parameters: {
    chromatic: {
      delay: 400,
      modes: {
        dark: { query: "[data-theme='dark']" },
        light: { query: "[data-theme='light']" },
      },
      pauseAnimationAtEnd: true,
    },
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
  title: 'Components/Graph/ProgressDashboard',
};

export default meta;
type Story = StoryObj<typeof meta>;

const mockMilestones = [
  {
    createdAt: new Date().toISOString(),
    health: 'green' as const,
    id: 'm1',
    itemCount: 10,
    itemIds: ['item-1', 'item-2'],
    name: 'v1.0 Release',
    progress: {
      blockedItems: 0,
      completedItems: 7,
      inProgressItems: 2,
      notStartedItems: 1,
      percentage: 70,
      totalItems: 10,
    },
    projectId: 'proj-1',
    riskScore: 0,
    slug: 'v1-0-release',
    status: 'in_progress' as const,
    targetDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

const mockSprints = [
  {
    addedPoints: 0,
    completedItemIds: [] as string[],
    completedPoints: 35,
    createdAt: new Date().toISOString(),
    durationDays: 14,
    endDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
    health: 'green' as const,
    id: 's1',
    itemCount: 10,
    itemIds: [] as string[],
    name: 'Sprint 1',
    plannedPoints: 50,
    projectId: 'proj-1',
    remainingPoints: 15,
    removedPoints: 0,
    slug: 'sprint-1',
    startDate: new Date().toISOString(),
    status: 'active' as const,
    updatedAt: new Date().toISOString(),
  },
];

/**
 * Default state
 */
export const Default: Story = {
  args: {
    isLoading: false,
    milestones: mockMilestones,
    projectId: 'proj-1',
    sprints: mockSprints,
  },
};

/**
 * Loading state
 */
export const Loading: Story = {
  args: {
    isLoading: true,
    milestones: [],
    projectId: 'proj-1',
    sprints: [],
  },
};

/**
 * Empty state
 */
export const Empty: Story = {
  args: {
    isLoading: false,
    milestones: [],
    projectId: 'proj-1',
    sprints: [],
  },
};

/**
 * On tablet
 */
export const Tablet: Story = {
  args: {
    isLoading: false,
    milestones: mockMilestones,
    projectId: 'proj-1',
    sprints: mockSprints,
  },
  parameters: {
    viewport: {
      defaultViewport: 'tablet',
    },
  },
};

/**
 * Dark mode
 */
export const DarkMode: Story = {
  args: {
    isLoading: false,
    milestones: mockMilestones,
    projectId: 'proj-1',
    sprints: mockSprints,
  },
  decorators: [
    (Story: React.ComponentType) => (
      <div className='dark' data-theme='dark' style={{ minHeight: '100vh' }}>
        <Story />
      </div>
    ),
  ],
  parameters: {
    chromatic: {
      modes: {
        dark: { query: "[data-theme='dark']" },
      },
    },
  },
};

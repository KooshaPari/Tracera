// TimelineView Storybook stories
import type { Meta, StoryObj } from '@storybook/react';

import type { Version } from '../TemporalNavigator';

import { logger } from '../../../lib/logger';
import { TimelineView } from '../TimelineView';

const meta = {
  component: TimelineView,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  title: 'Temporal/TimelineView',
} satisfies Meta<typeof TimelineView>;

export default meta;
type Story = StoryObj<typeof meta>;

const MS_PER_DAY_STORY = 86_400_000;

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
  {
    author: 'Alice',
    branchId: 'main',
    description: 'Next version in development',
    id: 'v1.2.0-beta',
    status: 'draft',
    tag: '1.2.0-beta',
    timestamp: new Date('2024-01-19'),
    title: 'v1.2.0-beta - Beta Release',
  },
];

export const Default: Story = {
  args: {
    currentVersionId: 'v1.1.0',
    onVersionChange: (versionId) => {
      logger.info('Version changed to:', versionId);
    },
    versions: mockVersions,
  },
};

export const SingleVersion: Story = {
  args: {
    currentVersionId: 'v1.0.0',
    onVersionChange: (versionId) => {
      logger.info('Version changed to:', versionId);
    },
    versions: [mockVersions[0]],
  },
};

export const ManyVersions: Story = {
  args: {
    currentVersionId: 'v10',
    onVersionChange: (versionId) => {
      logger.info('Version changed to:', versionId);
    },
    versions: Array.from({ length: 20 }, (_, i) => {
      const base = mockVersions[i % mockVersions.length];
      if (!base) {
        throw new Error('mockVersions empty');
      }
      return {
        author: base.author,
        branchId: base.branchId,
        description: base.description,
        id: `v${i}`,
        status: base.status,
        tag: base.tag,
        timestamp: new Date(new Date('2024-01-01').getTime() + i * MS_PER_DAY_STORY),
        title: `Version ${i}`,
      } satisfies Version;
    }),
  },
};

export const EmptyTimeline: Story = {
  args: {
    currentVersionId: '',
    onVersionChange: (versionId) => {
      logger.info('Version changed to:', versionId);
    },
    versions: [],
  },
};

export const DraftVersions: Story = {
  args: {
    currentVersionId: mockVersions[0]?.id ?? '',
    onVersionChange: (versionId) => {
      logger.info('Version changed to:', versionId);
    },
    versions: mockVersions.map((v) => ({
      ...v,
      status: 'draft' as const,
    })),
  },
};

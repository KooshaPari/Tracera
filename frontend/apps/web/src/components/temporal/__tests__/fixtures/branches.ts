import type { Branch } from '../../TemporalNavigator';

export const MOCK_BRANCHES: Branch[] = [
  {
    createdAt: new Date('2024-01-01'),
    description: 'Main production branch',
    id: 'branch-1',
    mergeRequestCount: 5,
    name: 'main',
    status: 'active',
    updatedAt: new Date('2024-01-15'),
  },
  {
    createdAt: new Date('2024-01-05'),
    description: 'Development branch',
    id: 'branch-2',
    mergeRequestCount: 2,
    name: 'develop',
    parentId: 'branch-1',
    status: 'active',
    updatedAt: new Date('2024-01-14'),
  },
  {
    createdAt: new Date('2024-01-10'),
    id: 'branch-3',
    mergeRequestCount: 1,
    name: 'feature/auth',
    parentId: 'branch-2',
    status: 'review',
    updatedAt: new Date('2024-01-13'),
  },
  {
    createdAt: new Date('2024-01-12'),
    id: 'branch-4',
    mergeRequestCount: 0,
    name: 'hotfix/security',
    parentId: 'branch-1',
    status: 'merged',
    updatedAt: new Date('2024-01-12'),
  },
];

export const EMPTY_BRANCHES: Branch[] = [];

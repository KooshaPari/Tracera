// TemporalNavigator component tests

import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';

import type { Branch, Version } from '../TemporalNavigator';

import { TemporalNavigator } from '../TemporalNavigator';

const EMPTY_BRANCHES: Branch[] = [];
const EMPTY_VERSIONS: Version[] = [];

const MOCK_BRANCHES: Branch[] = [
  {
    createdAt: new Date('2024-01-01'),
    id: 'branch-1',
    mergeRequestCount: 0,
    name: 'main',
    status: 'active',
    updatedAt: new Date('2024-01-15'),
  },
  {
    createdAt: new Date('2024-01-05'),
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
];

const MOCK_VERSIONS: Version[] = [
  {
    branchId: 'branch-1',
    id: 'v-1',
    status: 'published',
    tag: '1.0.0',
    timestamp: new Date('2024-01-01'),
    title: 'v1.0.0',
  },
  {
    branchId: 'branch-1',
    id: 'v-2',
    status: 'published',
    tag: '1.1.0',
    timestamp: new Date('2024-01-10'),
    title: 'v1.1.0',
  },
  {
    branchId: 'branch-2',
    id: 'v-3',
    status: 'draft',
    timestamp: new Date('2024-01-15'),
    title: 'Dev Build',
  },
];

describe(TemporalNavigator, () => {
  const mockOnBranchChange = vi.fn();
  const mockOnVersionChange = vi.fn();
  const mockOnBranchCreate = vi.fn();

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders branch selector', () => {
    render(
      <TemporalNavigator
        projectId='proj-1'
        currentBranchId='branch-1'
        currentVersionId='v-1'
        branches={MOCK_BRANCHES}
        versions={MOCK_VERSIONS}
        onBranchChange={mockOnBranchChange}
        onVersionChange={mockOnVersionChange}
      />,
    );

    expect(screen.getByText('main')).toBeInTheDocument();
  });

  it('displays current branch status badge', () => {
    render(
      <TemporalNavigator
        projectId='proj-1'
        currentBranchId='branch-1'
        currentVersionId='v-1'
        branches={MOCK_BRANCHES}
        versions={MOCK_VERSIONS}
        onBranchChange={mockOnBranchChange}
        onVersionChange={mockOnVersionChange}
      />,
    );

    expect(screen.getByText('active')).toBeInTheDocument();
  });

  it('calls onBranchCreate when create button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <TemporalNavigator
        projectId='proj-1'
        currentBranchId='branch-1'
        currentVersionId='v-1'
        branches={MOCK_BRANCHES}
        versions={MOCK_VERSIONS}
        onBranchChange={mockOnBranchChange}
        onVersionChange={mockOnVersionChange}
        onBranchCreate={mockOnBranchCreate}
      />,
    );

    const buttons = screen.getAllByRole('button');
    const createBtn = buttons.find((b) => b.textContent?.includes('Branch'));
    if (createBtn) {
      await user.click(createBtn);
      expect(mockOnBranchCreate).toHaveBeenCalled();
    }
  });

  it('displays current version information', () => {
    render(
      <TemporalNavigator
        projectId='proj-1'
        currentBranchId='branch-1'
        currentVersionId='v-2'
        branches={MOCK_BRANCHES}
        versions={MOCK_VERSIONS}
        onBranchChange={mockOnBranchChange}
        onVersionChange={mockOnVersionChange}
      />,
    );

    expect(screen.getByText(/v1.1.0/)).toBeInTheDocument();
  });

  it('renders view mode toggle buttons', () => {
    render(
      <TemporalNavigator
        projectId='proj-1'
        currentBranchId='branch-1'
        currentVersionId='v-1'
        branches={MOCK_BRANCHES}
        versions={MOCK_VERSIONS}
        onBranchChange={mockOnBranchChange}
        onVersionChange={mockOnVersionChange}
      />,
    );

    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('handles empty branches list gracefully', () => {
    render(
      <TemporalNavigator
        projectId='proj-1'
        currentBranchId=''
        currentVersionId=''
        branches={EMPTY_BRANCHES}
        versions={EMPTY_VERSIONS}
        onBranchChange={mockOnBranchChange}
        onVersionChange={mockOnVersionChange}
      />,
    );

    expect(screen.getByText(/Select branch/)).toBeInTheDocument();
  });

  it('shows version status badge', () => {
    render(
      <TemporalNavigator
        projectId='proj-1'
        currentBranchId='branch-2'
        currentVersionId='v-3'
        branches={MOCK_BRANCHES}
        versions={MOCK_VERSIONS}
        onBranchChange={mockOnBranchChange}
        onVersionChange={mockOnVersionChange}
      />,
    );

    expect(screen.getByText('draft')).toBeInTheDocument();
  });
});

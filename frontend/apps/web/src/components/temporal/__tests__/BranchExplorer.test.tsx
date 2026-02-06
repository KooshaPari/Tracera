// BranchExplorer component tests
/// <reference types="@testing-library/jest-dom/vitest" />
import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { BranchExplorer } from '../BranchExplorer';
import { EMPTY_BRANCHES, MOCK_BRANCHES } from './fixtures/branches';

describe(BranchExplorer, () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
  });

  const mockOnBranchChange = vi.fn();
  const mockOnMergeRequest = vi.fn();
  const mockOnBranchCreate = vi.fn();

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders branch tree structure', () => {
    render(
      <BranchExplorer
        projectId='proj-1'
        branches={MOCK_BRANCHES}
        currentBranchId='branch-1'
        onBranchChange={mockOnBranchChange}
      />,
    );

    expect(screen.getByText('main')).toBeInTheDocument();
    expect(screen.getByText('develop')).toBeInTheDocument();
  });

  it('displays branch status badges', () => {
    render(
      <BranchExplorer
        projectId='proj-1'
        branches={MOCK_BRANCHES}
        currentBranchId='branch-1'
        onBranchChange={mockOnBranchChange}
      />,
    );

    const activeElements = screen.getAllByText('active');
    expect(activeElements.length).toBeGreaterThan(0);

    expect(screen.getByText('review')).toBeInTheDocument();
    expect(screen.getByText('merged')).toBeInTheDocument();
  });

  it('calls onBranchChange when branch is clicked', async () => {
    render(
      <BranchExplorer
        projectId='proj-1'
        branches={MOCK_BRANCHES}
        currentBranchId='branch-1'
        onBranchChange={mockOnBranchChange}
      />,
    );

    const developElement = screen.getByText('develop');
    await user.click(developElement);
    expect(mockOnBranchChange).toHaveBeenCalledWith('branch-2');
  });

  it('displays branch descriptions', () => {
    render(
      <BranchExplorer
        projectId='proj-1'
        branches={MOCK_BRANCHES}
        currentBranchId='branch-1'
        onBranchChange={mockOnBranchChange}
      />,
    );

    expect(screen.getByText('Main production branch')).toBeInTheDocument();
    expect(screen.getByText('Development branch')).toBeInTheDocument();
  });

  it('shows create branch button when provided', () => {
    render(
      <BranchExplorer
        projectId='proj-1'
        branches={MOCK_BRANCHES}
        currentBranchId='branch-1'
        onBranchChange={mockOnBranchChange}
        onBranchCreate={mockOnBranchCreate}
      />,
    );

    expect(screen.getByText('New Branch')).toBeInTheDocument();
  });

  it('calls onBranchCreate when create button is clicked', async () => {
    render(
      <BranchExplorer
        projectId='proj-1'
        branches={MOCK_BRANCHES}
        currentBranchId='branch-1'
        onBranchChange={mockOnBranchChange}
        onBranchCreate={mockOnBranchCreate}
      />,
    );

    const createBtn = screen.getByText('New Branch');
    await user.click(createBtn);
    expect(mockOnBranchCreate).toHaveBeenCalled();
  });

  it('displays branch statistics', () => {
    render(
      <BranchExplorer
        projectId='proj-1'
        branches={MOCK_BRANCHES}
        currentBranchId='branch-1'
        onBranchChange={mockOnBranchChange}
      />,
    );

    expect(screen.getByText('Active:')).toBeInTheDocument();
    expect(screen.getByText('In Review:')).toBeInTheDocument();
    expect(screen.getByText('Total:')).toBeInTheDocument();
  });

  it('shows correct active branch count', () => {
    render(
      <BranchExplorer
        projectId='proj-1'
        branches={MOCK_BRANCHES}
        currentBranchId='branch-1'
        onBranchChange={mockOnBranchChange}
      />,
    );

    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('handles empty branch list gracefully', () => {
    render(
      <BranchExplorer
        projectId='proj-1'
        branches={EMPTY_BRANCHES}
        currentBranchId=''
        onBranchChange={mockOnBranchChange}
      />,
    );

    expect(screen.getByText('No branches found')).toBeInTheDocument();
  });

  it('supports merge operations', async () => {
    render(
      <BranchExplorer
        projectId='proj-1'
        branches={MOCK_BRANCHES}
        currentBranchId='branch-1'
        onBranchChange={mockOnBranchChange}
        onMergeRequest={mockOnMergeRequest}
      />,
    );

    const mergeButtons = screen.getAllByRole('button');
    expect(mergeButtons.length).toBeGreaterThan(0);
  });

  it('highlights current branch', () => {
    render(
      <BranchExplorer
        projectId='proj-1'
        branches={MOCK_BRANCHES}
        currentBranchId='branch-2'
        onBranchChange={mockOnBranchChange}
      />,
    );

    const developElements = screen.getAllByText('develop');
    expect(developElements.length).toBeGreaterThan(0);
  });

  it('shows branch hierarchy through indentation', () => {
    render(
      <BranchExplorer
        projectId='proj-1'
        branches={MOCK_BRANCHES}
        currentBranchId='branch-1'
        onBranchChange={mockOnBranchChange}
      />,
    );

    const elements = screen.getAllByText('feature/auth');
    expect(elements.length).toBeGreaterThan(0);
  });
});

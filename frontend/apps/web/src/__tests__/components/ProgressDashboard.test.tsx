import type { HealthStatus, Milestone, MilestoneStatus, Sprint, SprintStatus } from '@atoms/types';

import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { ProgressDashboard } from '../../components/temporal/ProgressDashboard';

const mockMilestone: Milestone = {
  createdAt: new Date().toISOString(),
  health: 'green' satisfies HealthStatus,
  id: '1',
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
  slug: 'v1-0-release',
  status: 'in_progress' satisfies MilestoneStatus,
  targetDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
  updatedAt: new Date().toISOString(),
};

const mockSprint: Sprint = {
  addedPoints: 0,
  completedItemIds: [],
  completedPoints: 35,
  createdAt: new Date().toISOString(),
  durationDays: 14,
  endDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
  health: 'green' satisfies HealthStatus,
  id: 'sprint-1',
  itemCount: 10,
  itemIds: [],
  name: 'Sprint 1',
  plannedPoints: 50,
  projectId: 'proj-1',
  remainingPoints: 15,
  removedPoints: 0,
  slug: 'sprint-1',
  startDate: new Date().toISOString(),
  status: 'active' satisfies SprintStatus,
  updatedAt: new Date().toISOString(),
};

const defaultProps = {
  milestones: [mockMilestone],
  projectId: 'proj-1',
  sprints: [mockSprint],
};

describe(ProgressDashboard, () => {
  it('renders current overview summary values', () => {
    render(<ProgressDashboard {...defaultProps} />);

    expect(screen.getByText('Overall Progress')).toBeInTheDocument();
    expect(screen.getByText('70%')).toBeInTheDocument();
    expect(screen.getByText('Active Milestones')).toBeInTheDocument();
    expect(screen.getByText('At Risk')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
  });

  it('renders the active sprint summary and invokes its id callback', async () => {
    const onSprintClick = vi.fn();
    const user = userEvent.setup();
    render(<ProgressDashboard {...defaultProps} onSprintClick={onSprintClick} />);

    expect(screen.getByText('Sprint 1')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /view sprint/i }));
    expect(onSprintClick).toHaveBeenCalledWith('sprint-1');
  });

  it('renders milestone groups and invokes the milestone id callback', async () => {
    const onMilestoneClick = vi.fn();
    const user = userEvent.setup();
    render(<ProgressDashboard {...defaultProps} onMilestoneClick={onMilestoneClick} />);

    await user.click(screen.getByRole('tab', { name: /milestones/i }));
    await user.click(screen.getByText('v1.0 Release'));
    expect(onMilestoneClick).toHaveBeenCalledWith('1');
  });

  it('renders active sprint detail in the sprints view', async () => {
    const user = userEvent.setup();
    render(<ProgressDashboard {...defaultProps} />);

    await user.click(screen.getByRole('tab', { name: /sprints/i }));
    expect(screen.getByText('Active Sprint')).toBeInTheDocument();
    expect(screen.getByText('Burndown Chart')).toBeInTheDocument();
  });

  it('renders milestone empty state', async () => {
    const user = userEvent.setup();
    render(<ProgressDashboard {...defaultProps} milestones={[]} />);

    await user.click(screen.getByRole('tab', { name: /milestones/i }));
    expect(screen.getByText('No milestones found')).toBeInTheDocument();
  });

  it('renders sprint empty state', async () => {
    const user = userEvent.setup();
    render(<ProgressDashboard {...defaultProps} sprints={[]} />);

    await user.click(screen.getByRole('tab', { name: /sprints/i }));
    expect(screen.getByText('No sprints found')).toBeInTheDocument();
  });

  it('groups multiple milestones in their current lane', async () => {
    const user = userEvent.setup();
    const milestone2: Milestone = { ...mockMilestone, id: '2', name: 'v1.1 Patch' };
    render(<ProgressDashboard {...defaultProps} milestones={[mockMilestone, milestone2]} />);

    await user.click(screen.getByRole('tab', { name: /milestones/i }));
    expect(screen.getByText('v1.0 Release')).toBeInTheDocument();
    expect(screen.getByText('v1.1 Patch')).toBeInTheDocument();
  });

  it('derives at-risk summary from milestone status', () => {
    const atRiskMilestone: Milestone = {
      ...mockMilestone,
      health: 'red' satisfies HealthStatus,
      id: '2',
      status: 'at_risk' satisfies MilestoneStatus,
    };

    render(<ProgressDashboard {...defaultProps} milestones={[mockMilestone, atRiskMilestone]} />);

    expect(screen.getByText('At-Risk Milestones')).toBeInTheDocument();
    expect(screen.getAllByText('1').length).toBeGreaterThan(0);
  });

  it('renders the velocity empty state without metrics', async () => {
    const user = userEvent.setup();
    render(<ProgressDashboard {...defaultProps} />);

    await user.click(screen.getByRole('tab', { name: /velocity/i }));
    expect(screen.getByText('No velocity metrics available')).toBeInTheDocument();
  });

  it('renders the loading state', () => {
    render(<ProgressDashboard {...defaultProps} isLoading />);
    expect(screen.getByText('Loading progress dashboard...')).toBeInTheDocument();
  });
});

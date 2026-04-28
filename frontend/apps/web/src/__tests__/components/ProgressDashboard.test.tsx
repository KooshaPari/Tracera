import type {
  HealthStatus,
  Milestone,
  MilestoneStatus,
  ProgressSnapshot,
  ProjectMetrics,
  Sprint,
  SprintStatus,
} from '@atoms/types';

import '@testing-library/jest-dom';
import { fireEvent, render, screen } from '@testing-library/react';

import { ProgressDashboard } from '../../components/temporal/ProgressDashboard';

// Mock data
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

const mockMetrics: ProjectMetrics = {
  atRiskCount: 3,
  blockedCount: 2,
  byLifecycle: {},
  byPriority: {
    critical: 10,
    high: 20,
    low: 30,
    medium: 40,
  },
  byStatus: {
    done: 30,
    in_progress: 30,
    todo: 40,
  },
  byType: {},
  completedLastWeek: 8,
  completedThisWeek: 10,
  overdueCount: 1,
  totalItems: 100,
  velocity: 10 / 7,
};

const mockSnapshot: ProgressSnapshot = {
  createdAt: new Date().toISOString(),
  id: 'snapshot-1',
  metrics: mockMetrics as any,
  projectId: 'proj-1',
  snapshotDate: new Date().toISOString(),
};

describe(ProgressDashboard, () => {
  const defaultProps = {
    metrics: mockMetrics,
    milestones: [mockMilestone],
    projectId: 'proj-1',
    snapshots: [mockSnapshot],
    sprints: [mockSprint],
  };

  it('renders dashboard with summary cards', () => {
    render(<ProgressDashboard {...defaultProps} />);

    expect(screen.getByText('Total Milestones')).toBeInTheDocument();
    expect(screen.getByText('At Risk')).toBeInTheDocument();
    expect(screen.getByText('Blockers')).toBeInTheDocument();
    expect(screen.getByText('Velocity')).toBeInTheDocument();
  });

  it('displays correct summary values', () => {
    render(<ProgressDashboard {...defaultProps} />);

    expect(screen.getByText('1')).toBeInTheDocument(); // Total milestones
    expect(screen.getByText('0')).toBeInTheDocument(); // At risk
    expect(screen.getByText('2')).toBeInTheDocument(); // Blockers
  });

  it('renders milestone hierarchy', () => {
    render(<ProgressDashboard {...defaultProps} />);

    expect(screen.getByText('Milestone Hierarchy')).toBeInTheDocument();
    expect(screen.getByText('v1.0 Release')).toBeInTheDocument();
  });

  it('renders sprint timeline', () => {
    render(<ProgressDashboard {...defaultProps} />);

    expect(screen.getByText('Sprint Timeline')).toBeInTheDocument();
    expect(screen.getByText('Sprint 1')).toBeInTheDocument();
  });

  it('calls onMilestoneClick when milestone is selected', () => {
    const onMilestoneClick = jest.fn();
    render(<ProgressDashboard {...defaultProps} onMilestoneClick={onMilestoneClick} />);

    const milestoneElement = screen.getByText('v1.0 Release');
    fireEvent.click(milestoneElement);

    expect(onMilestoneClick).toHaveBeenCalledWith(mockMilestone);
  });

  it('calls onSprintClick when sprint is selected', () => {
    const onSprintClick = jest.fn();
    render(<ProgressDashboard {...defaultProps} onSprintClick={onSprintClick} />);

    const sprintElement = screen.getByText('Sprint 1');
    fireEvent.click(sprintElement);

    expect(onSprintClick).toHaveBeenCalledWith(mockSprint);
  });

  it('renders health status section', () => {
    render(<ProgressDashboard {...defaultProps} />);

    expect(screen.getByText('Health Status')).toBeInTheDocument();
    expect(screen.getByText('Milestones')).toBeInTheDocument();
    expect(screen.getByText('Sprints')).toBeInTheDocument();
    expect(screen.getByText('Items')).toBeInTheDocument();
  });

  it('renders progress snapshots', () => {
    render(<ProgressDashboard {...defaultProps} />);

    expect(screen.getByText('Recent Progress Snapshots')).toBeInTheDocument();
  });

  it('handles empty milestones list', () => {
    render(<ProgressDashboard {...defaultProps} milestones={[]} />);

    expect(screen.getByText('Milestone Hierarchy')).toBeInTheDocument();
  });

  it('handles empty sprints list', () => {
    render(<ProgressDashboard {...defaultProps} sprints={[]} />);

    // Sprint timeline should not render
    expect(screen.queryByText('Sprint Timeline')).not.toBeInTheDocument();
  });

  it('displays multiple milestones', () => {
    const milestone2: Milestone = {
      ...mockMilestone,
      id: '2',
      name: 'v1.1 Patch',
    };

    render(<ProgressDashboard {...defaultProps} milestones={[mockMilestone, milestone2]} />);

    expect(screen.getByText('v1.0 Release')).toBeInTheDocument();
    expect(screen.getByText('v1.1 Patch')).toBeInTheDocument();
  });

  it('displays at-risk milestone count correctly', () => {
    const atRiskMilestone: Milestone = {
      ...mockMilestone,
      id: '2',
      health: 'red' satisfies HealthStatus,
    };

    render(<ProgressDashboard {...defaultProps} milestones={[mockMilestone, atRiskMilestone]} />);

    // Should display "1" for at-risk count
    const atRiskCards = screen.getAllByText('1');
    expect(atRiskCards.length).toBeGreaterThan(0);
  });

  it('shows active sprint highlighted', () => {
    const activeSprint: Sprint = {
      ...mockSprint,
      status: 'active' satisfies SprintStatus,
    };

    const planningSprint: Sprint = {
      ...mockSprint,
      id: 'sprint-2',
      name: 'Sprint 2',
      status: 'planning' satisfies SprintStatus,
    };

    render(<ProgressDashboard {...defaultProps} sprints={[activeSprint, planningSprint]} />);

    expect(screen.getByText('Active Sprint')).toBeInTheDocument();
  });
});

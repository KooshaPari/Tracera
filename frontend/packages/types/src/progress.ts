// Progress Dimension Types
// Focuses on EXECUTION STATE (Jira/Linear-like experience)
// Supports milestones, sprints, burndown charts, and velocity tracking

// =============================================================================
// MILESTONE TYPES
// =============================================================================

/**
 * Milestone status - lifecycle of a milestone
 */
export type MilestoneStatus =
  | 'not_started' // Milestone not yet begun
  | 'in_progress' // Actively being worked on
  | 'at_risk' // Behind schedule or blocked
  | 'blocked' // Cannot proceed
  | 'completed' // Successfully completed
  | 'cancelled'; // Abandoned

/**
 * Health indicator for milestones and projects
 */
export type HealthStatus = 'green' | 'yellow' | 'red' | 'unknown';

/**
 * A milestone represents a significant deliverable or checkpoint
 */
export interface Milestone {
  id: string;
  projectId: string;

  // Hierarchy (milestones can be nested)
  parentId?: string | undefined; // Parent milestone/initiative
  childIds?: string[] | undefined; // Child milestones

  // Identity
  name: string;
  slug: string;
  description?: string | undefined;
  objective?: string | undefined; // What success looks like

  // Timing
  startDate?: string | undefined;
  targetDate: string;
  actualDate?: string | undefined; // When actually completed

  // Status
  status: MilestoneStatus;
  health: HealthStatus;

  // Progress metrics
  progress: MilestoneProgress;

  // Risk assessment
  riskScore: number; // 0-100, computed from dependencies, blocks, timeline
  riskFactors?: RiskFactor[] | undefined;

  // Items
  itemIds: string[]; // Items in this milestone
  itemCount: number;

  // Dependencies
  dependsOnMilestones?: string[] | undefined; // Must complete first
  blockedByMilestones?: string[] | undefined; // Currently blocking

  // Team
  owner?: string | undefined;
  assignees?: string[] | undefined;

  // Metadata
  tags?: string[] | undefined;
  metadata?: Record<string, unknown> | undefined;
  createdAt: string;
  updatedAt: string;
}

/**
 * Progress metrics for a milestone
 */
export interface MilestoneProgress {
  totalItems: number;
  completedItems: number;
  inProgressItems: number;
  blockedItems: number;
  notStartedItems: number;
  percentage: number; // 0-100

  // By priority
  byPriority?: {
    critical: { total: number; completed: number };
    high: { total: number; completed: number };
    medium: { total: number; completed: number };
    low: { total: number; completed: number };
  };
}

/**
 * Risk factor affecting a milestone
 */
export interface RiskFactor {
  type: RiskFactorType;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  itemId?: string | undefined; // Related item
  mitigationSuggestion?: string | undefined;
}

export type RiskFactorType =
  | 'blocked_dependency' // Blocked by another item
  | 'overdue' // Past target date
  | 'scope_creep' // Items being added
  | 'low_velocity' // Slower than expected
  | 'resource_constraint' // Not enough people
  | 'technical_risk' // Technical challenges
  | 'external_dependency'; // Waiting on external party

// =============================================================================
// SPRINT TYPES
// =============================================================================

/**
 * Sprint status
 */
export type SprintStatus =
  | 'planning' // Sprint planning in progress
  | 'active' // Currently active sprint
  | 'completed' // Sprint ended successfully
  | 'cancelled'; // Sprint cancelled

/**
 * A sprint represents a time-boxed work period
 */
export interface Sprint {
  id: string;
  projectId: string;

  // Identity
  name: string; // "Sprint 23" or "Q1 Week 3"
  slug: string;
  goal?: string | undefined; // Sprint goal/objective

  // Time box
  startDate: string;
  endDate: string;
  durationDays: number;

  // Status
  status: SprintStatus;
  health: HealthStatus;

  // Capacity planning
  plannedCapacity?: number | undefined; // Story points or hours
  actualCapacity?: number | undefined; // After accounting for PTO, etc.

  // Progress
  plannedPoints: number;
  completedPoints: number;
  remainingPoints: number;
  addedPoints: number; // Scope added during sprint
  removedPoints: number; // Scope removed during sprint

  // Velocity
  velocity?: number | undefined; // Points completed per day
  estimatedCompletion?: string | undefined; // Projected completion date

  // Items
  itemIds: string[];
  itemCount: number;
  completedItemIds: string[];
  carryoverItemIds?: string[] | undefined; // Not completed, carried to next sprint

  // Burndown data
  burndownData?: BurndownDataPoint[] | undefined;

  // Team
  teamMembers?: string[] | undefined;

  // Metadata
  metadata?: Record<string, unknown> | undefined;
  createdAt: string;
  updatedAt: string;
  completedAt?: string | undefined;
}

/**
 * Single data point in a burndown chart
 */
export interface BurndownDataPoint {
  date: string;
  remainingPoints: number;
  idealPoints: number; // Ideal burndown line
  completedPoints: number;
  addedPoints?: number | undefined; // Scope changes
}

// =============================================================================
// PROGRESS SNAPSHOT TYPES
// =============================================================================

/**
 * Point-in-time snapshot of project progress
 * Used for historical tracking and trend analysis
 */
export interface ProgressSnapshot {
  id: string;
  projectId: string;
  snapshotDate: string;

  // Aggregate metrics
  metrics: ProjectMetrics;

  // Milestone status at this point
  milestoneSnapshots?: MilestoneSnapshot[] | undefined;

  // Sprint status at this point
  sprintSnapshot?: SprintSnapshot | undefined;

  createdAt: string;
}

/**
 * All project metrics at a point in time
 */
export interface ProjectMetrics {
  // Item counts
  totalItems: number;
  byStatus: Record<string, number>; // E.g., { "todo": 10, "in_progress": 5 }
  byPriority: Record<string, number>;
  byType: Record<string, number>;

  // Lifecycle distribution
  byLifecycle: Record<string, number>;

  // Velocity
  completedThisWeek: number;
  completedLastWeek: number;
  velocity: number; // Rolling average over N weeks

  // Health indicators
  blockedCount: number;
  atRiskCount: number;
  overdueCount: number;

  // Coverage
  testCoverage?: number | undefined; // 0-100
  docCoverage?: number | undefined; // 0-100
  traceCoverage?: number | undefined; // 0-100

  // Time metrics
  averageCycleTime?: number | undefined; // Days from start to done
  averageLeadTime?: number | undefined; // Days from created to done
}

/**
 * Milestone status at a snapshot point
 */
export interface MilestoneSnapshot {
  milestoneId: string;
  milestoneName: string;
  status: MilestoneStatus;
  health: HealthStatus;
  progress: number; // 0-100
  riskScore: number;
  daysToTarget: number; // Negative if overdue
}

/**
 * Sprint status at a snapshot point
 */
export interface SprintSnapshot {
  sprintId: string;
  sprintName: string;
  status: SprintStatus;
  daysRemaining: number;
  completionPercentage: number;
  velocity: number;
  onTrack: boolean;
}

// =============================================================================
// VELOCITY & TREND ANALYSIS
// =============================================================================

/**
 * Velocity metrics over time
 */
export interface VelocityMetrics {
  projectId: string;

  // Current velocity
  currentVelocity: number; // Points per sprint/week
  averageVelocity: number; // Rolling average

  // Trend
  trend: 'improving' | 'stable' | 'declining';
  trendPercentage: number; // +/- % change

  // Historical data
  history: VelocityDataPoint[];

  // Forecast
  forecastVelocity: number; // Predicted next period
  confidenceInterval?: {
    low: number;
    high: number;
  };

  computedAt: string;
}

/**
 * Single velocity data point
 */
export interface VelocityDataPoint {
  periodStart: string;
  periodEnd: string;
  periodLabel: string; // "Sprint 23" or "Week 12"
  plannedPoints: number;
  completedPoints: number;
  velocity: number;
}

/**
 * Cycle time metrics
 */
export interface CycleTimeMetrics {
  projectId: string;

  // Averages
  averageCycleTime: number; // Days
  medianCycleTime: number;
  p85CycleTime: number; // 85th percentile

  // By type
  byType: Record<string, number>;
  byPriority: Record<string, number>;

  // Trend
  trend: 'improving' | 'stable' | 'declining';

  // Distribution
  distribution: {
    range: string; // "1-3 days", "4-7 days", etc.
    count: number;
    percentage: number;
  }[];

  computedAt: string;
}

// =============================================================================
// ROADMAP & PLANNING
// =============================================================================

/**
 * Roadmap item for planning view
 */
export interface RoadmapItem {
  id: string;
  type: 'milestone' | 'sprint' | 'release' | 'epic';
  name: string;

  // Timing
  startDate: string;
  endDate: string;
  durationDays: number;

  // Status
  status: string;
  health: HealthStatus;
  progress: number;

  // Hierarchy
  parentId?: string | undefined;
  childIds?: string[] | undefined;
  lane?: string | undefined; // Swim lane for roadmap view

  // Dependencies
  dependsOn?: string[] | undefined;
  blocks?: string[] | undefined;
}

/**
 * Roadmap view configuration
 */
export interface RoadmapViewConfig {
  // Time range
  startDate: string;
  endDate: string;
  timeUnit: 'day' | 'week' | 'month' | 'quarter';

  // Grouping
  groupBy: 'none' | 'type' | 'team' | 'priority' | 'lane';
  lanes?: string[] | undefined;

  // Filtering
  showCompleted: boolean;
  showDependencies: boolean;
  itemTypes: string[];

  // Display
  zoomLevel: number; // 1-10
  condensed: boolean;
}

// =============================================================================
// DASHBOARD WIDGETS
// =============================================================================

/**
 * Widget types for progress dashboard
 */
export type DashboardWidgetType =
  | 'burndown'
  | 'burnup'
  | 'velocity'
  | 'cumulative_flow'
  | 'milestone_progress'
  | 'sprint_summary'
  | 'cycle_time'
  | 'lead_time'
  | 'health_summary'
  | 'risk_summary'
  | 'blockers'
  | 'recent_activity';

/**
 * Dashboard widget configuration
 */
export interface DashboardWidget {
  id: string;
  type: DashboardWidgetType;
  title: string;

  // Layout
  x: number;
  y: number;
  width: number;
  height: number;

  // Configuration
  config: Record<string, unknown>;

  // Filtering
  milestoneId?: string | undefined;
  sprintId?: string | undefined;
  dateRange?: {
    start: string;
    end: string;
  };
}

/**
 * Dashboard layout
 */
export interface DashboardLayout {
  id: string;
  projectId: string;
  name: string;
  isDefault: boolean;

  widgets: DashboardWidget[];
  columns: number;
  rowHeight: number;

  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================
const BLOCKED_RISK_THRESHOLD_PERCENT = 30;
const PROGRESS_RED_THRESHOLD = 0.5;
const PROGRESS_YELLOW_THRESHOLD = 0.8;
const MS_PER_DAY = 1000 * 60 * 60 * 24;

/**
 * Calculate health status from metrics
 *
 * @param {boolean} onTime - Whether the workstream is currently on schedule.
 * @param {number} blockedPercentage - Percentage of blocked work items.
 * @param {number} progressVsExpected - Ratio of actual progress vs expected progress.
 * @returns {HealthStatus} Health status color bucket.
 */
export function calculateHealthStatus(
  onTime: boolean,
  blockedPercentage: number,
  progressVsExpected: number,
): HealthStatus {
  if (
    blockedPercentage > BLOCKED_RISK_THRESHOLD_PERCENT ||
    progressVsExpected < PROGRESS_RED_THRESHOLD
  ) {
    return 'red';
  }
  if (blockedPercentage > 10 || progressVsExpected < PROGRESS_YELLOW_THRESHOLD || !onTime) {
    return 'yellow';
  }
  return 'green';
}

/**
 * Get health status color
 *
 * @param {HealthStatus} health - Health status value.
 * @returns {string} Hex color mapped to the given status.
 */
export function getHealthColor(health: HealthStatus): string {
  const colors: Record<HealthStatus, string> = {
    green: '#22c55e',
    red: '#ef4444',
    unknown: '#6b7280',
    yellow: '#eab308',
  };
  return colors[health];
}

/**
 * Get milestone status color
 *
 * @param {MilestoneStatus} status - Milestone status value.
 * @returns {string} Hex color mapped to milestone status.
 */
export function getMilestoneStatusColor(status: MilestoneStatus): string {
  const colors: Record<MilestoneStatus, string> = {
    at_risk: '#eab308',
    blocked: '#ef4444',
    cancelled: '#6b7280',
    completed: '#22c55e',
    in_progress: '#3b82f6',
    not_started: '#94a3b8',
  };
  return colors[status];
}

/**
 * Get sprint status color
 *
 * @param {SprintStatus} status - Sprint status value.
 * @returns {string} Hex color mapped to sprint status.
 */
export function getSprintStatusColor(status: SprintStatus): string {
  const colors: Record<SprintStatus, string> = {
    active: '#3b82f6',
    cancelled: '#6b7280',
    completed: '#22c55e',
    planning: '#a78bfa',
  };
  return colors[status];
}

/**
 * Calculate days until target date
 *
 * @param {string} targetDate - ISO date string for the target date.
 * @returns {number} Number of days from now to target date.
 */
export function daysUntilTarget(targetDate: string): number {
  const target = new Date(targetDate);
  const now = new Date();
  const diffTime = target.getTime() - now.getTime();
  return Math.ceil(diffTime / MS_PER_DAY);
}

/**
 * Calculate progress percentage
 *
 * @param {number} completed - Number of completed work items/points.
 * @param {number} total - Total number of work items/points.
 * @returns {number} Rounded completion percentage.
 */
export function calculateProgressPercentage(completed: number, total: number): number {
  if (total === 0) {
    return 0;
  }
  return Math.round((completed / total) * 100);
}

/**
 * Calculate velocity from history
 *
 * @param {VelocityDataPoint[]} history - Historical velocity data points.
 * @param {number} periods - Number of recent periods to include in averaging.
 * @returns {number} Rounded average completed points for recent periods.
 */
export function calculateVelocity(history: VelocityDataPoint[], periods = 3): number {
  if (history.length === 0) {
    return 0;
  }
  const recent = history.slice(-periods);
  const totalCompleted = recent.reduce((sum, point) => sum + point.completedPoints, 0);
  return Math.round(totalCompleted / recent.length);
}

/**
 * Calculate estimated completion date based on velocity
 *
 * @param {number} remainingPoints - Number of points remaining.
 * @param {number} velocity - Average completed points per time period.
 * @param {Date} startDate - Start date for projection.
 * @returns {Date | null} Projected completion date, or null if velocity is not positive.
 */
export function estimateCompletionDate(
  remainingPoints: number,
  velocity: number,
  startDate: Date = new Date(),
): Date | null {
  if (velocity <= 0) {
    return null;
  }
  const daysRemaining = Math.ceil(remainingPoints / velocity);
  const completionDate = new Date(startDate);
  completionDate.setDate(completionDate.getDate() + daysRemaining);
  return completionDate;
}

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
  | "not_started"     // Milestone not yet begun
  | "in_progress"     // Actively being worked on
  | "at_risk"         // Behind schedule or blocked
  | "blocked"         // Cannot proceed
  | "completed"       // Successfully completed
  | "cancelled";      // Abandoned

/**
 * Health indicator for milestones and projects
 */
export type HealthStatus = "green" | "yellow" | "red" | "unknown";

/**
 * A milestone represents a significant deliverable or checkpoint
 */
export interface Milestone {
  id: string;
  projectId: string;

  // Hierarchy (milestones can be nested)
  parentId?: string;                 // Parent milestone/initiative
  childIds?: string[];               // Child milestones

  // Identity
  name: string;
  slug: string;
  description?: string;
  objective?: string;                // What success looks like

  // Timing
  startDate?: string;
  targetDate: string;
  actualDate?: string;               // When actually completed

  // Status
  status: MilestoneStatus;
  health: HealthStatus;

  // Progress metrics
  progress: MilestoneProgress;

  // Risk assessment
  riskScore: number;                 // 0-100, computed from dependencies, blocks, timeline
  riskFactors?: RiskFactor[];

  // Items
  itemIds: string[];                 // Items in this milestone
  itemCount: number;

  // Dependencies
  dependsOnMilestones?: string[];    // Must complete first
  blockedByMilestones?: string[];    // Currently blocking

  // Team
  owner?: string;
  assignees?: string[];

  // Metadata
  tags?: string[];
  metadata?: Record<string, unknown>;
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
  percentage: number;                // 0-100

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
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  itemId?: string;                   // Related item
  mitigationSuggestion?: string;
}

export type RiskFactorType =
  | "blocked_dependency"    // Blocked by another item
  | "overdue"               // Past target date
  | "scope_creep"           // Items being added
  | "low_velocity"          // Slower than expected
  | "resource_constraint"   // Not enough people
  | "technical_risk"        // Technical challenges
  | "external_dependency";  // Waiting on external party

// =============================================================================
// SPRINT TYPES
// =============================================================================

/**
 * Sprint status
 */
export type SprintStatus =
  | "planning"        // Sprint planning in progress
  | "active"          // Currently active sprint
  | "completed"       // Sprint ended successfully
  | "cancelled";      // Sprint cancelled

/**
 * A sprint represents a time-boxed work period
 */
export interface Sprint {
  id: string;
  projectId: string;

  // Identity
  name: string;                      // "Sprint 23" or "Q1 Week 3"
  slug: string;
  goal?: string;                     // Sprint goal/objective

  // Time box
  startDate: string;
  endDate: string;
  durationDays: number;

  // Status
  status: SprintStatus;
  health: HealthStatus;

  // Capacity planning
  plannedCapacity?: number;          // Story points or hours
  actualCapacity?: number;           // After accounting for PTO, etc.

  // Progress
  plannedPoints: number;
  completedPoints: number;
  remainingPoints: number;
  addedPoints: number;               // Scope added during sprint
  removedPoints: number;             // Scope removed during sprint

  // Velocity
  velocity?: number;                 // Points completed per day
  estimatedCompletion?: string;      // Projected completion date

  // Items
  itemIds: string[];
  itemCount: number;
  completedItemIds: string[];
  carryoverItemIds?: string[];       // Not completed, carried to next sprint

  // Burndown data
  burndownData?: BurndownDataPoint[];

  // Team
  teamMembers?: string[];

  // Metadata
  metadata?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

/**
 * Single data point in a burndown chart
 */
export interface BurndownDataPoint {
  date: string;
  remainingPoints: number;
  idealPoints: number;               // Ideal burndown line
  completedPoints: number;
  addedPoints?: number;              // Scope changes
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
  milestoneSnapshots?: MilestoneSnapshot[];

  // Sprint status at this point
  sprintSnapshot?: SprintSnapshot;

  createdAt: string;
}

/**
 * All project metrics at a point in time
 */
export interface ProjectMetrics {
  // Item counts
  totalItems: number;
  byStatus: Record<string, number>;  // e.g., { "todo": 10, "in_progress": 5 }
  byPriority: Record<string, number>;
  byType: Record<string, number>;

  // Lifecycle distribution
  byLifecycle: Record<string, number>;

  // Velocity
  completedThisWeek: number;
  completedLastWeek: number;
  velocity: number;                  // Rolling average over N weeks

  // Health indicators
  blockedCount: number;
  atRiskCount: number;
  overdueCount: number;

  // Coverage
  testCoverage?: number;             // 0-100
  docCoverage?: number;              // 0-100
  traceCoverage?: number;            // 0-100

  // Time metrics
  averageCycleTime?: number;         // Days from start to done
  averageLeadTime?: number;          // Days from created to done
}

/**
 * Milestone status at a snapshot point
 */
export interface MilestoneSnapshot {
  milestoneId: string;
  milestoneName: string;
  status: MilestoneStatus;
  health: HealthStatus;
  progress: number;                  // 0-100
  riskScore: number;
  daysToTarget: number;              // Negative if overdue
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
  currentVelocity: number;           // Points per sprint/week
  averageVelocity: number;           // Rolling average

  // Trend
  trend: "improving" | "stable" | "declining";
  trendPercentage: number;           // +/- % change

  // Historical data
  history: VelocityDataPoint[];

  // Forecast
  forecastVelocity: number;          // Predicted next period
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
  periodLabel: string;               // "Sprint 23" or "Week 12"
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
  averageCycleTime: number;          // Days
  medianCycleTime: number;
  p85CycleTime: number;              // 85th percentile

  // By type
  byType: Record<string, number>;
  byPriority: Record<string, number>;

  // Trend
  trend: "improving" | "stable" | "declining";

  // Distribution
  distribution: {
    range: string;                   // "1-3 days", "4-7 days", etc.
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
  type: "milestone" | "sprint" | "release" | "epic";
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
  parentId?: string;
  childIds?: string[];
  lane?: string;                     // Swim lane for roadmap view

  // Dependencies
  dependsOn?: string[];
  blocks?: string[];
}

/**
 * Roadmap view configuration
 */
export interface RoadmapViewConfig {
  // Time range
  startDate: string;
  endDate: string;
  timeUnit: "day" | "week" | "month" | "quarter";

  // Grouping
  groupBy: "none" | "type" | "team" | "priority" | "lane";
  lanes?: string[];

  // Filtering
  showCompleted: boolean;
  showDependencies: boolean;
  itemTypes: string[];

  // Display
  zoomLevel: number;                 // 1-10
  condensed: boolean;
}

// =============================================================================
// DASHBOARD WIDGETS
// =============================================================================

/**
 * Widget types for progress dashboard
 */
export type DashboardWidgetType =
  | "burndown"
  | "burnup"
  | "velocity"
  | "cumulative_flow"
  | "milestone_progress"
  | "sprint_summary"
  | "cycle_time"
  | "lead_time"
  | "health_summary"
  | "risk_summary"
  | "blockers"
  | "recent_activity";

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
  milestoneId?: string;
  sprintId?: string;
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

/**
 * Calculate health status from metrics
 */
export function calculateHealthStatus(
  onTime: boolean,
  blockedPercentage: number,
  progressVsExpected: number
): HealthStatus {
  if (blockedPercentage > 30 || progressVsExpected < 0.5) {
    return "red";
  }
  if (blockedPercentage > 10 || progressVsExpected < 0.8 || !onTime) {
    return "yellow";
  }
  return "green";
}

/**
 * Get health status color
 */
export function getHealthColor(health: HealthStatus): string {
  const colors: Record<HealthStatus, string> = {
    green: "#22c55e",
    yellow: "#eab308",
    red: "#ef4444",
    unknown: "#6b7280",
  };
  return colors[health];
}

/**
 * Get milestone status color
 */
export function getMilestoneStatusColor(status: MilestoneStatus): string {
  const colors: Record<MilestoneStatus, string> = {
    not_started: "#94a3b8",
    in_progress: "#3b82f6",
    at_risk: "#eab308",
    blocked: "#ef4444",
    completed: "#22c55e",
    cancelled: "#6b7280",
  };
  return colors[status];
}

/**
 * Get sprint status color
 */
export function getSprintStatusColor(status: SprintStatus): string {
  const colors: Record<SprintStatus, string> = {
    planning: "#a78bfa",
    active: "#3b82f6",
    completed: "#22c55e",
    cancelled: "#6b7280",
  };
  return colors[status];
}

/**
 * Calculate days until target date
 */
export function daysUntilTarget(targetDate: string): number {
  const target = new Date(targetDate);
  const now = new Date();
  const diffTime = target.getTime() - now.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

/**
 * Calculate progress percentage
 */
export function calculateProgressPercentage(
  completed: number,
  total: number
): number {
  if (total === 0) return 0;
  return Math.round((completed / total) * 100);
}

/**
 * Calculate velocity from history
 */
export function calculateVelocity(
  history: VelocityDataPoint[],
  periods: number = 3
): number {
  if (history.length === 0) return 0;
  const recent = history.slice(-periods);
  const totalCompleted = recent.reduce((sum, p) => sum + p.completedPoints, 0);
  return Math.round(totalCompleted / recent.length);
}

/**
 * Calculate estimated completion date based on velocity
 */
export function estimateCompletionDate(
  remainingPoints: number,
  velocity: number,
  startDate: Date = new Date()
): Date | null {
  if (velocity <= 0) return null;
  const daysRemaining = Math.ceil(remainingPoints / velocity);
  const completionDate = new Date(startDate);
  completionDate.setDate(completionDate.getDate() + daysRemaining);
  return completionDate;
}

// Progress Dashboard - Comprehensive milestone and sprint tracking with burndown and velocity
// Provides 4 main views: Overview, Milestones, Sprints, and Velocity metrics

import {
  AlertCircle,
  AlertTriangle,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  Clock,
  Target,
  TrendingDown,
  TrendingUp,
  Zap,
} from 'lucide-react';
import { useMemo, useState } from 'react';

import type {
  BurndownDataPoint,
  HealthStatus,
  Milestone,
  ProgressSnapshot,
  Sprint,
  VelocityMetrics,
} from '@tracertm/types';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';
import { cn } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui/components/Tabs';
// ============================================================================
// INTERFACES
// ============================================================================

export interface ProgressDashboardProps {
  projectId: string;
  milestones: Milestone[];
  sprints: Sprint[];
  currentSnapshot?: ProgressSnapshot | undefined;
  velocityMetrics?: VelocityMetrics | undefined;
  isLoading?: boolean | undefined;
  onMilestoneClick?: ((milestoneId: string) => void) | undefined;
  onSprintClick?: ((sprintId: string) => void) | undefined;
}

// ============================================================================
// HELPER COMPONENTS
// ============================================================================

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode | undefined;
  trend?: 'up' | 'down' | 'stable' | undefined;
  trendValue?: string | undefined;
  color?: 'default' | 'success' | 'warning' | 'destructive' | undefined;
}

function StatCard({ label, value, icon, trend, trendValue, color = 'default' }: StatCardProps) {
  const colorClasses = {
    default: 'bg-blue-50 dark:bg-blue-900/20 text-blue-900 dark:text-blue-100',
    destructive: 'bg-red-50 dark:bg-red-900/20 text-red-900 dark:text-red-100',
    success: 'bg-green-50 dark:bg-green-900/20 text-green-900 dark:text-green-100',
    warning: 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-900 dark:text-yellow-100',
  };

  const iconColorClasses = {
    default: 'text-blue-600 dark:text-blue-400',
    destructive: 'text-red-600 dark:text-red-400',
    success: 'text-green-600 dark:text-green-400',
    warning: 'text-yellow-600 dark:text-yellow-400',
  };

  return (
    <div className={cn('rounded-lg p-4 border', colorClasses[color])}>
      <div className='mb-2 flex items-center justify-between'>
        <span className='text-sm font-medium opacity-75'>{label}</span>
        {icon && <div className={cn('w-5 h-5', iconColorClasses[color])}>{icon}</div>}
      </div>
      <div className='flex items-center justify-between'>
        <span className='text-2xl font-bold'>{value}</span>
        {trend && trendValue && (
          <div className='flex items-center gap-1 text-sm'>
            {trend === 'up' && (
              <TrendingUp className='h-4 w-4 text-green-600 dark:text-green-400' />
            )}
            {trend === 'down' && (
              <TrendingDown className='h-4 w-4 text-red-600 dark:text-red-400' />
            )}
            <span>{trendValue}</span>
          </div>
        )}
      </div>
    </div>
  );
}

interface HealthBadgeProps {
  health: HealthStatus;
}

function HealthBadge({ health }: HealthBadgeProps) {
  const variants = {
    green:
      'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 border-green-300 dark:border-green-700',
    red: 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300 border-red-300 dark:border-red-700',
    unknown:
      'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600',
    yellow:
      'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300 border-yellow-300 dark:border-yellow-700',
  };

  const icons = {
    green: <CheckCircle2 className='h-3 w-3' />,
    red: <AlertCircle className='h-3 w-3' />,
    unknown: <Clock className='h-3 w-3' />,
    yellow: <AlertTriangle className='h-3 w-3' />,
  };

  return (
    <Badge variant='outline' className={cn('gap-1 border', variants[health])}>
      {icons[health]}
      <span>{health}</span>
    </Badge>
  );
}

interface SprintProgressBarProps {
  completed: number;
  planned: number;
  daysRemaining: number;
  durationDays: number;
}

function SprintProgressBar({
  completed,
  planned,
  daysRemaining,
  durationDays,
}: SprintProgressBarProps) {
  const progressPercent = planned > 0 ? (completed / planned) * 100 : 0;
  const timePercent = (daysRemaining / durationDays) * 100;

  // Determine if on track
  const isOnTrack = progressPercent >= timePercent * 0.9;

  return (
    <div className='space-y-2'>
      <div className='flex items-center justify-between text-sm'>
        <span className='font-medium text-gray-700 dark:text-gray-300'>Progress</span>
        <span className='text-gray-600 dark:text-gray-400'>
          {completed}/{planned} points
        </span>
      </div>
      <div className='relative h-3 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700'>
        {/* Background bar */}
        <div
          className='absolute h-full bg-blue-500'
          style={{ width: `${Math.min(progressPercent, 100)}%` }}
        />
        {/* Time indicator */}
        <div
          className={cn(
            'absolute top-0 w-0.5 h-full transition-all',
            isOnTrack ? 'bg-green-500' : 'bg-yellow-500',
          )}
          style={{ left: `${Math.min(timePercent, 100)}%` }}
          title={
            isOnTrack
              ? 'On track'
              : `Behind schedule (${Math.round(progressPercent)}% vs ${Math.round(timePercent)}% expected)`
          }
        />
      </div>
      <div className='flex items-center justify-between text-xs text-gray-600 dark:text-gray-400'>
        <span>{Math.round(progressPercent)}% complete</span>
        <span>{daysRemaining} days left</span>
      </div>
    </div>
  );
}

interface MilestoneRowProps {
  milestone: Milestone;
  onClickMilestone?: ((id: string) => void) | undefined;
}

function MilestoneRow({ milestone, onClickMilestone }: MilestoneRowProps) {
  const daysRemaining = Math.ceil(
    (new Date(milestone.targetDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24),
  );
  const isOverdue = daysRemaining < 0;

  return (
    <div
      className='group flex cursor-pointer items-center justify-between rounded-lg border border-gray-200 p-3 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800'
      onClick={() => onClickMilestone?.(milestone.id)}
    >
      <div className='min-w-0 flex-1 space-y-1'>
        <div className='flex items-center gap-2'>
          <span className='truncate font-medium text-gray-900 dark:text-gray-100'>
            {milestone.name}
          </span>
          <HealthBadge health={milestone.health} />
        </div>
        <div className='flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400'>
          <span>{milestone.progress.percentage}% complete</span>
          <span className='text-gray-400 dark:text-gray-600'>•</span>
          <span>
            {milestone.progress.completedItems}/{milestone.progress.totalItems} items
          </span>
        </div>
      </div>

      <div className='ml-4 flex flex-shrink-0 items-center gap-3'>
        <div className='h-2 w-32 overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700'>
          <div
            className='h-full bg-blue-500 transition-all'
            style={{ width: `${milestone.progress.percentage}%` }}
          />
        </div>
        <div
          className={cn(
            'text-xs font-medium whitespace-nowrap px-2 py-1 rounded',
            isOverdue
              ? 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20'
              : 'text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800',
          )}
        >
          {isOverdue ? (
            <span className='flex items-center gap-1'>
              <AlertCircle className='h-3 w-3' />
              {Math.abs(daysRemaining)}d overdue
            </span>
          ) : (
            <span>{daysRemaining}d remaining</span>
          )}
        </div>
        <ChevronRight className='h-4 w-4 text-gray-400 opacity-0 transition-opacity group-hover:opacity-100 dark:text-gray-600' />
      </div>
    </div>
  );
}

interface MilestoneGroupProps {
  title: string;
  milestones: Milestone[];
  icon: React.ReactNode;
  onClickMilestone?: ((id: string) => void) | undefined;
}

function MilestoneGroup({ title, milestones, icon, onClickMilestone }: MilestoneGroupProps) {
  if (milestones.length === 0) {
    return null;
  }

  return (
    <div className='space-y-2'>
      <div className='flex items-center gap-2 rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-900'>
        <span className='text-gray-600 dark:text-gray-400'>{icon}</span>
        <h4 className='text-sm font-semibold text-gray-900 dark:text-gray-100'>{title}</h4>
        <span className='ml-auto text-xs font-medium text-gray-600 dark:text-gray-400'>
          {milestones.length}
        </span>
      </div>
      <div className='space-y-2 pl-2'>
        {milestones.map((milestone) => (
          <MilestoneRow
            key={milestone.id}
            milestone={milestone}
            onClickMilestone={onClickMilestone}
          />
        ))}
      </div>
    </div>
  );
}

interface SprintRowProps {
  sprint: Sprint;
  onClickSprint?: ((id: string) => void) | undefined;
}

function SprintRow({ sprint, onClickSprint }: SprintRowProps) {
  const startDate = new Date(sprint.startDate);
  const endDate = new Date(sprint.endDate);
  const now = new Date();

  const daysRemaining = Math.ceil((endDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  const isActive = sprint.status === 'active';
  const isCompleted = sprint.status === 'completed';

  return (
    <div
      className='cursor-pointer rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800'
      onClick={() => onClickSprint?.(sprint.id)}
    >
      <div className='mb-3 flex items-start justify-between'>
        <div className='min-w-0 flex-1'>
          <div className='mb-1 flex items-center gap-2'>
            <h4 className='truncate font-semibold text-gray-900 dark:text-gray-100'>
              {sprint.name}
            </h4>
            <Badge
              variant={isActive ? 'default' : isCompleted ? 'secondary' : 'outline'}
              className='text-xs'
            >
              {sprint.status}
            </Badge>
            <HealthBadge health={sprint.health} />
          </div>
          {sprint.goal && (
            <p className='truncate text-xs text-gray-600 dark:text-gray-400'>{sprint.goal}</p>
          )}
        </div>
      </div>

      {isActive && (
        <SprintProgressBar
          completed={sprint.completedPoints}
          planned={sprint.plannedPoints}
          daysRemaining={Math.max(daysRemaining, 0)}
          durationDays={sprint.durationDays}
        />
      )}

      {!isActive && (
        <div className='grid grid-cols-3 gap-2 text-xs'>
          <div className='rounded bg-gray-50 p-2 dark:bg-gray-900'>
            <div className='text-gray-600 dark:text-gray-400'>Planned</div>
            <div className='font-semibold text-gray-900 dark:text-gray-100'>
              {sprint.plannedPoints}
            </div>
          </div>
          <div className='rounded bg-gray-50 p-2 dark:bg-gray-900'>
            <div className='text-gray-600 dark:text-gray-400'>Completed</div>
            <div className='font-semibold text-gray-900 dark:text-gray-100'>
              {sprint.completedPoints}
            </div>
          </div>
          <div className='rounded bg-gray-50 p-2 dark:bg-gray-900'>
            <div className='text-gray-600 dark:text-gray-400'>Remaining</div>
            <div className='font-semibold text-gray-900 dark:text-gray-100'>
              {sprint.remainingPoints}
            </div>
          </div>
        </div>
      )}

      <div className='mt-2 flex items-center justify-between text-xs text-gray-600 dark:text-gray-400'>
        <span>
          {startDate.toLocaleDateString()} - {endDate.toLocaleDateString()}
        </span>
        <span>{sprint.durationDays} days</span>
      </div>
    </div>
  );
}

interface SimpleBurndownChartProps {
  burndownData?: BurndownDataPoint[] | undefined;
  plannedPoints: number;
  completedPoints: number;
}

function SimpleBurndownChart({
  burndownData,
  plannedPoints,
  completedPoints,
}: SimpleBurndownChartProps) {
  // Generate sample data if not provided
  const data = useMemo(() => {
    if (!burndownData || burndownData.length === 0) {
      // Create 10 day burndown simulation
      const simulated: BurndownDataPoint[] = [];
      for (let i = 0; i <= 10; i += 1) {
        simulated.push({
          completedPoints: Math.round(completedPoints * (i / 10)),
          date: new Date(Date.now() - (10 - i) * 24 * 60 * 60 * 1000).toISOString(),
          idealPoints: Math.max(plannedPoints * ((10 - i) / 10), 0),
          remainingPoints: Math.max(plannedPoints - completedPoints * (i / 10), 0),
        });
      }
      return simulated;
    }
    return burndownData.slice(-10);
  }, [burndownData, plannedPoints, completedPoints]);

  if (data.length === 0) {
    return (
      <div className='flex h-64 items-center justify-center text-gray-500 dark:text-gray-400'>
        No burndown data available
      </div>
    );
  }

  // Simple SVG-based chart
  const maxValue = Math.max(...data.map((d) => d.idealPoints));
  const height = 200;
  const width = 100;
  const chartHeight = height - 40;

  const points = data.map((d, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = chartHeight - (d.remainingPoints / maxValue) * chartHeight;
    return { x, y };
  });

  const idealPoints = data.map((d, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = chartHeight - (d.idealPoints / maxValue) * chartHeight;
    return { x, y };
  });

  const pathData = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

  const idealPathData = idealPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

  return (
    <div className='space-y-4'>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className='w-full rounded border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-950'
      >
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => (
          <line
            key={`h-${i}`}
            x1='10'
            y1={height - 30 - pct * chartHeight}
            x2={width}
            y2={height - 30 - pct * chartHeight}
            stroke='#e5e7eb'
            strokeWidth='0.5'
            className='dark:stroke-gray-700'
          />
        ))}

        {/* Ideal line */}
        <path
          d={idealPathData}
          fill='none'
          stroke='#3b82f6'
          strokeWidth='1'
          strokeDasharray='2,2'
          vectorEffect='non-scaling-stroke'
        />

        {/* Actual line */}
        <path
          d={pathData}
          fill='none'
          stroke='#ef4444'
          strokeWidth='2'
          vectorEffect='non-scaling-stroke'
        />

        {/* Axes */}
        <line x1='10' y1='10' x2='10' y2={height - 20} stroke='#6b7280' strokeWidth='1' />
        <line
          x1='10'
          y1={height - 20}
          x2={width}
          y2={height - 20}
          stroke='#6b7280'
          strokeWidth='1'
        />

        {/* Labels */}
        <text x='5' y={height - 20} fontSize='10' fill='#6b7280' textAnchor='end'>
          0
        </text>
        <text x='5' y={height - 20 - chartHeight} fontSize='10' fill='#6b7280' textAnchor='end'>
          {Math.round(maxValue)}
        </text>
      </svg>

      <div className='grid grid-cols-3 gap-2 text-xs'>
        <div className='rounded bg-blue-50 p-2 dark:bg-blue-900/20'>
          <div className='font-medium text-blue-600 dark:text-blue-400'>Ideal Rate</div>
          <div className='font-bold text-blue-900 dark:text-blue-100'>
            {plannedPoints > 0 ? (plannedPoints / data.length).toFixed(1) : 0}
          </div>
        </div>
        <div className='rounded bg-red-50 p-2 dark:bg-red-900/20'>
          <div className='font-medium text-red-600 dark:text-red-400'>Current Rate</div>
          <div className='font-bold text-red-900 dark:text-red-100'>
            {completedPoints > 0 ? (completedPoints / Math.max(data.length - 1, 1)).toFixed(1) : 0}
          </div>
        </div>
        <div className='rounded bg-green-50 p-2 dark:bg-green-900/20'>
          <div className='font-medium text-green-600 dark:text-green-400'>Remaining</div>
          <div className='font-bold text-green-900 dark:text-green-100'>
            {Math.max(plannedPoints - completedPoints, 0)}
          </div>
        </div>
      </div>
    </div>
  );
}

interface VelocityChartProps {
  metrics?: VelocityMetrics | undefined;
}

function VelocityBarChart({ metrics }: VelocityChartProps) {
  if (!metrics || metrics.history.length === 0) {
    return (
      <div className='flex h-64 items-center justify-center text-gray-500 dark:text-gray-400'>
        No velocity data available
      </div>
    );
  }

  const data = metrics.history.slice(-6);
  const maxVelocity = Math.max(...data.map((d) => d.velocity), metrics.averageVelocity);

  return (
    <div className='space-y-4'>
      <div className='flex flex-col gap-3'>
        {data.map((point) => {
          const height = (point.velocity / maxVelocity) * 100;
          return (
            <div key={`${point.periodStart}-${point.periodEnd}`}>
              <div className='mb-1 flex items-center justify-between'>
                <span className='text-xs font-medium text-gray-700 dark:text-gray-300'>
                  {point.periodLabel}
                </span>
                <span className='text-xs text-gray-600 dark:text-gray-400'>
                  {point.velocity} pts
                </span>
              </div>
              <div className='h-6 w-full overflow-hidden rounded bg-gray-200 dark:bg-gray-700'>
                <div
                  className='h-full bg-purple-500 transition-all'
                  style={{ width: `${height}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div className='grid grid-cols-3 gap-2 border-t border-gray-200 pt-3 text-xs dark:border-gray-700'>
        <div className='rounded bg-purple-50 p-2 dark:bg-purple-900/20'>
          <div className='font-medium text-purple-600 dark:text-purple-400'>Current</div>
          <div className='font-bold text-purple-900 dark:text-purple-100'>
            {metrics.currentVelocity}
          </div>
        </div>
        <div className='rounded bg-blue-50 p-2 dark:bg-blue-900/20'>
          <div className='font-medium text-blue-600 dark:text-blue-400'>Average</div>
          <div className='font-bold text-blue-900 dark:text-blue-100'>
            {metrics.averageVelocity}
          </div>
        </div>
        <div className='rounded bg-green-50 p-2 dark:bg-green-900/20'>
          <div className='font-medium text-green-600 dark:text-green-400'>Forecast</div>
          <div className='font-bold text-green-900 dark:text-green-100'>
            {metrics.forecastVelocity}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function ProgressDashboard({
  milestones,
  sprints,
  velocityMetrics,
  isLoading = false,
  onMilestoneClick,
  onSprintClick,
}: ProgressDashboardProps) {
  const [activeTab, setActiveTab] = useState('overview');

  // Computed values
  const activeSprint = useMemo(() => sprints.find((s) => s.status === 'active'), [sprints]);

  const atRiskMilestones = useMemo(
    () => milestones.filter((m) => m.status === 'at_risk' || m.status === 'blocked'),
    [milestones],
  );

  const activeMilestones = useMemo(
    () => milestones.filter((m) => m.status === 'in_progress'),
    [milestones],
  );

  const completedMilestones = useMemo(
    () => milestones.filter((m) => m.status === 'completed'),
    [milestones],
  );

  const notStartedMilestones = useMemo(
    () => milestones.filter((m) => m.status === 'not_started'),
    [milestones],
  );

  const overallProgress = useMemo(() => {
    if (milestones.length === 0) {
      return 0;
    }
    const totalProgress = milestones.reduce((sum, m) => sum + m.progress.percentage, 0);
    return Math.round(totalProgress / milestones.length);
  }, [milestones]);

  if (isLoading) {
    return (
      <div className='flex h-96 items-center justify-center text-gray-500 dark:text-gray-400'>
        <LoadingSpinner text='Loading progress dashboard...' />
      </div>
    );
  }

  return (
    <div className='w-full bg-white dark:bg-gray-950'>
      <Tabs value={activeTab} onValueChange={setActiveTab} className='w-full'>
        <div className='border-b border-gray-200 dark:border-gray-800'>
          <div className='px-4 pt-3'>
            <TabsList className='grid w-full grid-cols-4'>
              <TabsTrigger value='overview' className='flex items-center gap-2'>
                <Target className='h-4 w-4' />
                <span className='hidden sm:inline'>Overview</span>
              </TabsTrigger>
              <TabsTrigger value='milestones' className='flex items-center gap-2'>
                <CheckCircle2 className='h-4 w-4' />
                <span className='hidden sm:inline'>Milestones</span>
              </TabsTrigger>
              <TabsTrigger value='sprints' className='flex items-center gap-2'>
                <Zap className='h-4 w-4' />
                <span className='hidden sm:inline'>Sprints</span>
              </TabsTrigger>
              <TabsTrigger value='velocity' className='flex items-center gap-2'>
                <TrendingUp className='h-4 w-4' />
                <span className='hidden sm:inline'>Velocity</span>
              </TabsTrigger>
            </TabsList>
          </div>
        </div>

        {/* OVERVIEW TAB */}
        <TabsContent value='overview' className='space-y-6 p-4'>
          {/* Stats Grid */}
          <div className='grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4'>
            <StatCard
              label='Overall Progress'
              value={`${overallProgress}%`}
              icon={<Target className='h-5 w-5' />}
              color='default'
            />
            <StatCard
              label='Active Milestones'
              value={activeMilestones.length}
              icon={<Clock className='h-5 w-5' />}
              color='success'
            />
            <StatCard
              label='At Risk'
              value={atRiskMilestones.length}
              icon={<AlertTriangle className='h-5 w-5' />}
              color={atRiskMilestones.length > 0 ? 'destructive' : 'default'}
            />
            <StatCard
              label='Completed'
              value={completedMilestones.length}
              icon={<CheckCircle2 className='h-5 w-5' />}
              color='success'
            />
          </div>

          {/* Active Sprint Card */}
          {activeSprint && (
            <div className='rounded-lg border border-gray-200 bg-gradient-to-br from-blue-50 to-transparent p-4 dark:border-gray-700 dark:from-blue-900/10'>
              <div className='mb-4 flex items-start justify-between'>
                <div>
                  <h3 className='text-lg font-semibold text-gray-900 dark:text-gray-100'>
                    {activeSprint.name}
                  </h3>
                  {activeSprint.goal && (
                    <p className='mt-1 text-sm text-gray-600 dark:text-gray-400'>
                      {activeSprint.goal}
                    </p>
                  )}
                </div>
                <HealthBadge health={activeSprint.health} />
              </div>
              <SprintProgressBar
                completed={activeSprint.completedPoints}
                planned={activeSprint.plannedPoints}
                daysRemaining={Math.ceil(
                  (new Date(activeSprint.endDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24),
                )}
                durationDays={activeSprint.durationDays}
              />
              <Button
                variant='ghost'
                size='sm'
                className='mt-3 gap-2'
                onClick={() => onSprintClick?.(activeSprint.id)}
              >
                View Sprint <ChevronRight className='h-4 w-4' />
              </Button>
            </div>
          )}

          {/* At-Risk Milestones */}
          {atRiskMilestones.length > 0 && (
            <div className='rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/10'>
              <div className='mb-3 flex items-center gap-2'>
                <AlertCircle className='h-5 w-5 text-red-600 dark:text-red-400' />
                <h3 className='font-semibold text-gray-900 dark:text-gray-100'>
                  At-Risk Milestones
                </h3>
                <Badge variant='destructive' className='ml-auto'>
                  {atRiskMilestones.length}
                </Badge>
              </div>
              <div className='space-y-2'>
                {atRiskMilestones.map((milestone) => (
                  <MilestoneRow
                    key={milestone.id}
                    milestone={milestone}
                    onClickMilestone={onMilestoneClick}
                  />
                ))}
              </div>
            </div>
          )}
        </TabsContent>

        {/* MILESTONES TAB */}
        <TabsContent value='milestones' className='space-y-6 p-4'>
          <MilestoneGroup
            title='In Progress'
            milestones={activeMilestones}
            icon={<Clock className='h-4 w-4' />}
            onClickMilestone={onMilestoneClick}
          />

          <MilestoneGroup
            title='At Risk / Blocked'
            milestones={atRiskMilestones}
            icon={<AlertCircle className='h-4 w-4' />}
            onClickMilestone={onMilestoneClick}
          />

          <MilestoneGroup
            title='Not Started'
            milestones={notStartedMilestones}
            icon={<CalendarDays className='h-4 w-4' />}
            onClickMilestone={onMilestoneClick}
          />

          <MilestoneGroup
            title='Completed'
            milestones={completedMilestones}
            icon={<CheckCircle2 className='h-4 w-4' />}
            onClickMilestone={onMilestoneClick}
          />

          {milestones.length === 0 && (
            <div className='flex items-center justify-center py-12 text-gray-500 dark:text-gray-400'>
              <span>No milestones found</span>
            </div>
          )}
        </TabsContent>

        {/* SPRINTS TAB */}
        <TabsContent value='sprints' className='space-y-6 p-4'>
          {/* Active Sprint Detail */}
          {activeSprint && (
            <div className='space-y-3'>
              <h3 className='text-lg font-semibold text-gray-900 dark:text-gray-100'>
                Active Sprint
              </h3>
              <div className='rounded-lg border border-gray-200 p-4 dark:border-gray-700'>
                <SprintRow sprint={activeSprint} onClickSprint={onSprintClick} />
                <div className='mt-4'>
                  <h4 className='mb-3 text-sm font-medium text-gray-900 dark:text-gray-100'>
                    Burndown Chart
                  </h4>
                  <SimpleBurndownChart
                    burndownData={activeSprint.burndownData}
                    plannedPoints={activeSprint.plannedPoints}
                    completedPoints={activeSprint.completedPoints}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Planning Sprints */}
          {sprints.some((s) => s.status === 'planning') && (
            <div className='space-y-3'>
              <h3 className='text-lg font-semibold text-gray-900 dark:text-gray-100'>Planning</h3>
              <div className='grid gap-3'>
                {sprints
                  .filter((s) => s.status === 'planning')
                  .map((sprint) => (
                    <SprintRow key={sprint.id} sprint={sprint} onClickSprint={onSprintClick} />
                  ))}
              </div>
            </div>
          )}

          {/* Recent Completed Sprints */}
          {sprints.some((s) => s.status === 'completed') && (
            <div className='space-y-3'>
              <h3 className='text-lg font-semibold text-gray-900 dark:text-gray-100'>
                Recently Completed
              </h3>
              <div className='grid gap-3'>
                {sprints
                  .filter((s) => s.status === 'completed')
                  .slice(-3)
                  .map((sprint) => (
                    <SprintRow key={sprint.id} sprint={sprint} onClickSprint={onSprintClick} />
                  ))}
              </div>
            </div>
          )}

          {sprints.length === 0 && (
            <div className='flex items-center justify-center py-12 text-gray-500 dark:text-gray-400'>
              <span>No sprints found</span>
            </div>
          )}
        </TabsContent>

        {/* VELOCITY TAB */}
        <TabsContent value='velocity' className='space-y-6 p-4'>
          {velocityMetrics && (
            <>
              {/* Velocity Stats */}
              <div className='grid grid-cols-1 gap-3 sm:grid-cols-3'>
                <StatCard
                  label='Current Velocity'
                  value={velocityMetrics.currentVelocity}
                  icon={<Zap className='h-5 w-5' />}
                  color='default'
                />
                <StatCard
                  label='Average Velocity'
                  value={velocityMetrics.averageVelocity}
                  icon={<TrendingUp className='h-5 w-5' />}
                  color='success'
                />
                <StatCard
                  label='Trend'
                  value={velocityMetrics.trend}
                  icon={
                    velocityMetrics.trend === 'improving' ? (
                      <TrendingUp className='h-5 w-5' />
                    ) : velocityMetrics.trend === 'declining' ? (
                      <TrendingDown className='h-5 w-5' />
                    ) : (
                      <Clock className='h-5 w-5' />
                    )
                  }
                  color={
                    velocityMetrics.trend === 'improving'
                      ? 'success'
                      : velocityMetrics.trend === 'declining'
                        ? 'destructive'
                        : 'default'
                  }
                  trend={
                    velocityMetrics.trend === 'improving'
                      ? 'up'
                      : velocityMetrics.trend === 'declining'
                        ? 'down'
                        : 'stable'
                  }
                  trendValue={`${Math.abs(velocityMetrics.trendPercentage)}%`}
                />
              </div>

              {/* Velocity Chart */}
              <div className='rounded-lg border border-gray-200 p-4 dark:border-gray-700'>
                <h3 className='mb-4 font-semibold text-gray-900 dark:text-gray-100'>
                  Velocity Over Time
                </h3>
                <VelocityBarChart metrics={velocityMetrics} />
              </div>

              {/* Sprint History Table */}
              {velocityMetrics.history.length > 0 && (
                <div className='overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700'>
                  <div className='border-b border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900'>
                    <h3 className='font-semibold text-gray-900 dark:text-gray-100'>
                      Sprint History
                    </h3>
                  </div>
                  <div className='divide-y divide-gray-200 dark:divide-gray-700'>
                    {velocityMetrics.history.map((point) => (
                      <div
                        key={`${point.periodStart}-${point.periodEnd}`}
                        className='flex items-center justify-between px-4 py-3 text-sm transition-colors hover:bg-gray-50 dark:hover:bg-gray-900'
                      >
                        <div>
                          <div className='font-medium text-gray-900 dark:text-gray-100'>
                            {point.periodLabel}
                          </div>
                          <div className='text-xs text-gray-600 dark:text-gray-400'>
                            {new Date(point.periodStart).toLocaleDateString()} -{' '}
                            {new Date(point.periodEnd).toLocaleDateString()}
                          </div>
                        </div>
                        <div className='flex items-center gap-6'>
                          <div className='text-right'>
                            <div className='text-xs text-gray-600 dark:text-gray-400'>Planned</div>
                            <div className='font-medium text-gray-900 dark:text-gray-100'>
                              {point.plannedPoints}
                            </div>
                          </div>
                          <div className='text-right'>
                            <div className='text-xs text-gray-600 dark:text-gray-400'>
                              Completed
                            </div>
                            <div className='font-medium text-gray-900 dark:text-gray-100'>
                              {point.completedPoints}
                            </div>
                          </div>
                          <div className='text-right'>
                            <div className='text-xs text-gray-600 dark:text-gray-400'>Velocity</div>
                            <div className='font-medium text-purple-600 dark:text-purple-400'>
                              {point.velocity}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {!velocityMetrics && (
            <div className='flex items-center justify-center py-12 text-gray-500 dark:text-gray-400'>
              <span>No velocity metrics available</span>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default ProgressDashboard;

/**
 * TestSpec Card Component
 *
 * Displays test specification with flakiness detection, coverage metrics,
 * performance trends, and test execution history.
 * Implements FlakeFlagger-inspired quality indicators.
 */

import { format } from 'date-fns';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  Code,
  FileCode,
  Gauge,
  LayoutList,
  Play,
  Shield,
  Timer,
  TrendingDown,
  TrendingUp,
  XCircle,
  Zap,
} from 'lucide-react';

import type { TestSpec } from '@/hooks/useItemSpecs';

import { cn } from '@/lib/utils';
import { Badge, Button, Card, CardContent, CardHeader, CardTitle, Progress } from '@tracertm/ui';

interface TestSpecCardProps {
  spec: TestSpec;
  onClick?: () => void;
  className?: string;
  compact?: boolean;
  showCoverage?: boolean;
}

const testTypeStyles: Record<
  string,
  {
    bg: string;
    text: string;
    icon: React.ComponentType<{ className?: string }>;
  }
> = {
  accessibility: {
    bg: 'bg-pink-500/10',
    icon: Activity,
    text: 'text-pink-600',
  },
  contract: { bg: 'bg-cyan-500/10', icon: FileCode, text: 'text-cyan-600' },
  e2e: { bg: 'bg-green-500/10', icon: Play, text: 'text-green-600' },
  fuzz: { bg: 'bg-amber-500/10', icon: AlertTriangle, text: 'text-amber-600' },
  integration: {
    bg: 'bg-purple-500/10',
    icon: LayoutList,
    text: 'text-purple-600',
  },
  mutation: { bg: 'bg-yellow-500/10', icon: Zap, text: 'text-yellow-600' },
  performance: { bg: 'bg-orange-500/10', icon: Gauge, text: 'text-orange-600' },
  property: {
    bg: 'bg-indigo-500/10',
    icon: CheckCircle2,
    text: 'text-indigo-600',
  },
  security: { bg: 'bg-red-500/10', icon: Shield, text: 'text-red-600' },
  unit: { bg: 'bg-blue-500/10', icon: Code, text: 'text-blue-600' },
};

const runStatusStyles = {
  blocked: {
    bg: 'bg-orange-500/10',
    icon: AlertTriangle,
    text: 'text-orange-600',
  },
  error: { bg: 'bg-red-500/10', icon: XCircle, text: 'text-red-600' },
  failed: { bg: 'bg-red-500/10', icon: XCircle, text: 'text-red-600' },
  flaky: {
    bg: 'bg-yellow-500/10',
    icon: AlertTriangle,
    text: 'text-yellow-600',
  },
  passed: { bg: 'bg-green-500/10', icon: CheckCircle2, text: 'text-green-600' },
  skipped: { bg: 'bg-muted', icon: Clock, text: 'text-muted-foreground' },
  timeout: { bg: 'bg-red-500/10', icon: Timer, text: 'text-red-600' },
};

function getFlakinessColor(score: number | undefined): string {
  if (score === undefined) {
    return 'text-muted-foreground';
  }
  if (score <= 0.05) {
    return 'text-green-500';
  }
  if (score <= 0.15) {
    return 'text-yellow-500';
  }
  if (score <= 0.3) {
    return 'text-orange-500';
  }
  return 'text-red-500';
}

function getDurationTrend(trend: string | undefined) {
  switch (trend) {
    case 'improving': {
      return { icon: TrendingDown, label: 'Faster', text: 'text-green-500' };
    }
    case 'degrading': {
      return { icon: TrendingUp, label: 'Slower', text: 'text-red-500' };
    }
    default: {
      return { icon: Activity, label: 'Stable', text: 'text-muted-foreground' };
    }
  }
}

const defaultTestType = {
  bg: 'bg-blue-500/10',
  icon: Code,
  text: 'text-blue-600',
};

export function TestSpecCard({
  spec,
  onClick,
  className,
  compact = false,
  showCoverage = true,
}: TestSpecCardProps) {
  const testType = testTypeStyles[spec.test_type] ?? defaultTestType;
  const TestTypeIcon = testType.icon;
  const lastRunStyle = spec.last_run_status ? runStatusStyles[spec.last_run_status] : null;
  const LastRunIcon = lastRunStyle?.icon ?? Clock;
  const durationTrend = getDurationTrend(spec.duration_trend);
  const TrendIcon = durationTrend.icon;

  // Calculate pass rate
  const passRate =
    spec.total_runs > 0 ? ((spec.pass_count / spec.total_runs) * 100).toFixed(1) : null;

  if (compact) {
    return (
      <Card
        className={cn(
          'hover:shadow-md hover:bg-muted/30 hover:border-primary/30 transition-all duration-200 cursor-pointer',
          className,
        )}
        onClick={onClick}
      >
        <CardContent className='p-3'>
          <div className='flex items-start justify-between gap-2'>
            <div className='min-w-0 flex-1'>
              <div className='mb-1 flex flex-wrap items-center gap-2'>
                <Badge className={cn('text-[10px]', testType.bg, testType.text)}>
                  <TestTypeIcon className='mr-1 h-2.5 w-2.5' />
                  {spec.test_type}
                </Badge>
                {lastRunStyle && (
                  <Badge className={cn('text-[10px]', lastRunStyle.bg, lastRunStyle.text)}>
                    <LastRunIcon className='mr-1 h-2.5 w-2.5' />
                    {spec.last_run_status}
                  </Badge>
                )}
                {spec.is_quarantined && (
                  <Badge variant='destructive' className='text-[10px]'>
                    Quarantined
                  </Badge>
                )}
              </div>
              <p className='truncate text-xs font-medium'>
                {spec.test_function_name ?? spec.test_file_path ?? 'Test Specification'}
              </p>
              {passRate && (
                <div className='mt-2 flex items-center gap-2'>
                  <span className='text-muted-foreground text-[10px]'>Pass Rate:</span>
                  <Progress value={Number.parseFloat(passRate)} className='h-1 flex-1' />
                  <span className='text-xs font-bold tabular-nums'>{passRate}%</span>
                </div>
              )}
            </div>
            <Button variant='ghost' size='sm' className='h-7 shrink-0'>
              <ArrowRight className='h-3 w-3' />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      className={cn(
        'hover:shadow-md hover:bg-muted/30 hover:border-primary/30 transition-all duration-200',
        onClick && 'cursor-pointer',
        className,
      )}
      onClick={onClick}
    >
      <CardHeader className='pb-3'>
        <div className='flex items-start justify-between gap-4'>
          <div className='flex-1'>
            <div className='mb-2 flex flex-wrap items-center gap-2'>
              <Badge className={cn('text-[10px]', testType.bg, testType.text)}>
                <TestTypeIcon className='mr-1 h-2.5 w-2.5' />
                {spec.test_type}
              </Badge>
              {spec.test_framework && (
                <Badge variant='outline' className='text-[10px]'>
                  {spec.test_framework}
                </Badge>
              )}
              {lastRunStyle && (
                <Badge className={cn('text-[10px]', lastRunStyle.bg, lastRunStyle.text)}>
                  <LastRunIcon className='mr-1 h-2.5 w-2.5' />
                  {spec.last_run_status}
                </Badge>
              )}
              {spec.is_quarantined && (
                <Badge variant='destructive' className='text-[10px]'>
                  <AlertTriangle className='mr-1 h-2.5 w-2.5' />
                  Quarantined
                </Badge>
              )}
            </div>
            <CardTitle className='text-sm font-semibold'>
              {spec.test_function_name ?? 'Test Specification'}
            </CardTitle>
            {spec.test_file_path && (
              <p className='text-muted-foreground mt-1 truncate font-mono text-[10px]'>
                {spec.test_file_path}
              </p>
            )}
          </div>

          {/* Pass Rate Mini */}
          {passRate && (
            <div className='text-right'>
              <div className='text-2xl font-black tabular-nums'>{passRate}%</div>
              <div className='text-muted-foreground text-[10px] uppercase'>Pass Rate</div>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className='space-y-4'>
        {/* Run Statistics */}
        <div className='grid grid-cols-4 gap-2'>
          <div className='rounded-lg bg-green-500/10 p-2 text-center'>
            <div className='text-lg font-black text-green-600 tabular-nums'>{spec.pass_count}</div>
            <div className='text-muted-foreground text-[10px]'>Passed</div>
          </div>
          <div className='rounded-lg bg-red-500/10 p-2 text-center'>
            <div className='text-lg font-black text-red-600 tabular-nums'>{spec.fail_count}</div>
            <div className='text-muted-foreground text-[10px]'>Failed</div>
          </div>
          <div className='bg-muted/50 rounded-lg p-2 text-center'>
            <div className='text-muted-foreground text-lg font-black tabular-nums'>
              {spec.skip_count}
            </div>
            <div className='text-muted-foreground text-[10px]'>Skipped</div>
          </div>
          <div className='rounded-lg bg-blue-500/10 p-2 text-center'>
            <div className='text-lg font-black text-blue-600 tabular-nums'>{spec.total_runs}</div>
            <div className='text-muted-foreground text-[10px]'>Total</div>
          </div>
        </div>

        {/* Flakiness Indicator */}
        {spec.flakiness_score !== undefined && (
          <div className='space-y-2'>
            <div className='flex items-center justify-between'>
              <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                Flakiness Score
              </h4>
              <span className={cn('text-sm font-bold', getFlakinessColor(spec.flakiness_score))}>
                {(spec.flakiness_score * 100).toFixed(1)}%
              </span>
            </div>
            <Progress value={spec.flakiness_score * 100} className='h-2' />
            {spec.flaky_patterns.length > 0 && (
              <div className='mt-1 flex flex-wrap gap-1'>
                {spec.flaky_patterns.slice(0, 3).map((pattern, i) => (
                  <Badge key={i} variant='outline' className='text-[9px]'>
                    {pattern}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Performance Metrics */}
        {(spec.avg_duration_ms ?? spec.p95_duration_ms) && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              Performance
            </h4>
            <div className='grid grid-cols-4 gap-2 text-center'>
              {spec.avg_duration_ms && (
                <div className='bg-muted/30 rounded-lg p-2'>
                  <div className='text-sm font-bold tabular-nums'>
                    {spec.avg_duration_ms.toFixed(0)}ms
                  </div>
                  <div className='text-muted-foreground text-[10px]'>Avg</div>
                </div>
              )}
              {spec.p50_duration_ms && (
                <div className='bg-muted/30 rounded-lg p-2'>
                  <div className='text-sm font-bold tabular-nums'>
                    {spec.p50_duration_ms.toFixed(0)}ms
                  </div>
                  <div className='text-muted-foreground text-[10px]'>P50</div>
                </div>
              )}
              {spec.p95_duration_ms && (
                <div className='bg-muted/30 rounded-lg p-2'>
                  <div className='text-sm font-bold tabular-nums'>
                    {spec.p95_duration_ms.toFixed(0)}ms
                  </div>
                  <div className='text-muted-foreground text-[10px]'>P95</div>
                </div>
              )}
              {spec.p99_duration_ms && (
                <div className='bg-muted/30 rounded-lg p-2'>
                  <div className='text-sm font-bold tabular-nums'>
                    {spec.p99_duration_ms.toFixed(0)}ms
                  </div>
                  <div className='text-muted-foreground text-[10px]'>P99</div>
                </div>
              )}
            </div>
            <div className='flex items-center gap-1 text-xs'>
              <TrendIcon className={cn('w-3 h-3', durationTrend.text)} />
              <span className={durationTrend.text}>{durationTrend.label}</span>
            </div>
          </div>
        )}

        {/* Coverage Metrics */}
        {showCoverage && (spec.line_coverage ?? spec.branch_coverage ?? spec.mutation_score) && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              Coverage
            </h4>
            <div className='grid grid-cols-2 gap-2'>
              {spec.line_coverage !== undefined && (
                <div className='space-y-1'>
                  <div className='flex justify-between text-xs'>
                    <span className='text-muted-foreground'>Line</span>
                    <span className='font-bold'>{spec.line_coverage.toFixed(1)}%</span>
                  </div>
                  <Progress value={spec.line_coverage} className='h-1' />
                </div>
              )}
              {spec.branch_coverage !== undefined && (
                <div className='space-y-1'>
                  <div className='flex justify-between text-xs'>
                    <span className='text-muted-foreground'>Branch</span>
                    <span className='font-bold'>{spec.branch_coverage.toFixed(1)}%</span>
                  </div>
                  <Progress value={spec.branch_coverage} className='h-1' />
                </div>
              )}
              {spec.mutation_score !== undefined && (
                <div className='space-y-1'>
                  <div className='flex justify-between text-xs'>
                    <span className='text-muted-foreground'>Mutation</span>
                    <span className='font-bold'>{spec.mutation_score.toFixed(1)}%</span>
                  </div>
                  <Progress value={spec.mutation_score} className='h-1' />
                </div>
              )}
              {spec.mcdc_coverage !== undefined && (
                <div className='space-y-1'>
                  <div className='flex justify-between text-xs'>
                    <span className='text-muted-foreground'>MC/DC</span>
                    <span className='font-bold'>{spec.mcdc_coverage.toFixed(1)}%</span>
                  </div>
                  <Progress value={spec.mcdc_coverage} className='h-1' />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Verification Links */}
        {(spec.verifies_requirements.length > 0 || spec.verifies_contracts.length > 0) && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              Verifies
            </h4>
            <div className='flex flex-wrap gap-1'>
              {spec.verifies_requirements.slice(0, 3).map((req, i) => (
                <Badge key={`req-${i}`} variant='outline' className='text-[9px]'>
                  {req}
                </Badge>
              ))}
              {spec.verifies_contracts.slice(0, 2).map((contract, i) => (
                <Badge key={`ctr-${i}`} variant='secondary' className='text-[9px]'>
                  {contract}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Last Run Info */}
        {spec.last_run_at && (
          <div className='text-muted-foreground border-t pt-2 text-[10px]'>
            Last run {format(new Date(spec.last_run_at), "MMM d, yyyy 'at' HH:mm")}
            {spec.last_run_duration_ms && <span> • {spec.last_run_duration_ms.toFixed(0)}ms</span>}
          </div>
        )}

        {/* Quarantine Info */}
        {spec.is_quarantined && spec.quarantine_reason && (
          <div className='rounded-lg border border-red-500/20 bg-red-500/10 p-2'>
            <div className='flex items-start gap-2'>
              <AlertTriangle className='mt-0.5 h-3.5 w-3.5 text-red-600' />
              <div>
                <div className='text-xs font-bold text-red-600'>Quarantined</div>
                <p className='text-muted-foreground mt-0.5 text-[10px]'>{spec.quarantine_reason}</p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

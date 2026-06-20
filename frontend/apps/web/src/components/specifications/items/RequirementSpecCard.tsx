/**
 * RequirementSpec Card Component
 *
 * Displays requirement specification with EARS pattern visualization,
 * constraint indicators, verification status, and quality metrics.
 * Implements ISO 29148 quality visualization.
 */

import { format } from 'date-fns';
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  FileText,
  GitBranch,
  Shield,
  Target,
  TrendingDown,
  TrendingUp,
  XCircle,
} from 'lucide-react';

import type { RequirementSpec } from '@/hooks/useItemSpecs';

import { cn } from '@/lib/utils';
import {
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Progress,
  Separator,
} from '@tracertm/ui';

import { QualityScoreGauge } from './QualityScoreGauge';

interface RequirementSpecCardProps {
  spec: RequirementSpec;
  onClick?: () => void;
  className?: string;
  compact?: boolean;
  showQuality?: boolean;
}

const requirementTypeLabels: Record<string, { label: string; description: string }> = {
  complex: { description: 'Multi-condition requirement', label: 'Complex' },
  event_driven: { description: 'When <trigger> occurs', label: 'Event-Driven' },
  optional: { description: 'Where <feature> is enabled', label: 'Optional' },
  state_driven: { description: 'While <state> holds', label: 'State-Driven' },
  ubiquitous: { description: 'Always applies', label: 'Ubiquitous' },
  unwanted: { description: 'Shall not behavior', label: 'Unwanted' },
};

const constraintTypeStyles = {
  hard: { bg: 'bg-red-500/10', label: 'Hard Constraint', text: 'text-red-600' },
  optimizable: {
    bg: 'bg-green-500/10',
    label: 'Optimizable',
    text: 'text-green-600',
  },
  soft: {
    bg: 'bg-yellow-500/10',
    label: 'Soft Constraint',
    text: 'text-yellow-600',
  },
};

const verificationStatusStyles = {
  expired: {
    bg: 'bg-orange-500/10',
    icon: AlertTriangle,
    text: 'text-orange-600',
  },
  failed: { bg: 'bg-red-500/10', icon: XCircle, text: 'text-red-600' },
  pending: { bg: 'bg-yellow-500/10', icon: Clock, text: 'text-yellow-600' },
  unverified: { bg: 'bg-muted', icon: Clock, text: 'text-muted-foreground' },
  verified: {
    bg: 'bg-green-500/10',
    icon: CheckCircle2,
    text: 'text-green-600',
  },
};

const riskLevelStyles = {
  critical: { bg: 'bg-red-500', text: 'text-white' },
  high: { bg: 'bg-orange-500', text: 'text-white' },
  low: { bg: 'bg-green-500', text: 'text-white' },
  medium: { bg: 'bg-yellow-500', text: 'text-white' },
  minimal: { bg: 'bg-blue-500', text: 'text-white' },
};

export function RequirementSpecCard({
  spec,
  onClick,
  className,
  compact = false,
  showQuality = true,
}: RequirementSpecCardProps) {
  const reqType = requirementTypeLabels[spec.requirement_type] ?? {
    description: '',
    label: spec.requirement_type,
  };
  const constraintStyle = constraintTypeStyles[spec.constraint_type];
  const verificationStyle = verificationStatusStyles[spec.verification_status];
  const riskStyle = riskLevelStyles[spec.risk_level];
  const VerificationIcon = verificationStyle.icon;

  // Build EARS pattern display
  const buildEarsPattern = () => {
    const parts: string[] = [];
    if (spec.ears_trigger) {
      parts.push(`When ${spec.ears_trigger}`);
    }
    if (spec.ears_precondition) {
      parts.push(`while ${spec.ears_precondition}`);
    }
    if (spec.ears_postcondition) {
      parts.push(`the system shall ${spec.ears_postcondition}`);
    }
    return parts.join(', ');
  };

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
                <Badge variant='outline' className='text-[10px] font-black uppercase'>
                  {reqType.label}
                </Badge>
                <Badge className={cn('text-[10px]', verificationStyle.bg, verificationStyle.text)}>
                  <VerificationIcon className='mr-1 h-2.5 w-2.5' />
                  {spec.verification_status}
                </Badge>
              </div>
              <p className='text-muted-foreground line-clamp-2 text-xs'>
                {buildEarsPattern() || 'No EARS pattern defined'}
              </p>
              {spec.overall_quality_score !== undefined && (
                <div className='mt-2 flex items-center gap-2'>
                  <span className='text-muted-foreground text-[10px]'>Quality:</span>
                  <Progress value={spec.overall_quality_score} className='h-1 flex-1' />
                  <span className='text-xs font-bold tabular-nums'>
                    {spec.overall_quality_score.toFixed(0)}%
                  </span>
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
              <Badge variant='outline' className='text-[10px] font-black uppercase'>
                <FileText className='mr-1 h-2.5 w-2.5' />
                {reqType.label}
              </Badge>
              <Badge className={cn('text-[10px]', constraintStyle.bg, constraintStyle.text)}>
                <Target className='mr-1 h-2.5 w-2.5' />
                {constraintStyle.label}
              </Badge>
              <Badge className={cn('text-[10px]', verificationStyle.bg, verificationStyle.text)}>
                <VerificationIcon className='mr-1 h-2.5 w-2.5' />
                {spec.verification_status}
              </Badge>
              <Badge className={cn('text-[10px]', riskStyle.bg, riskStyle.text)}>
                <Shield className='mr-1 h-2.5 w-2.5' />
                {spec.risk_level} risk
              </Badge>
            </div>
            <CardTitle className='text-sm font-semibold'>Requirement Specification</CardTitle>
            <p className='text-muted-foreground mt-1 text-xs'>{reqType.description}</p>
          </div>

          {/* Quality Score Mini */}
          {spec.overall_quality_score !== undefined && (
            <div className='text-right'>
              <div className='text-2xl font-black tabular-nums'>
                {spec.overall_quality_score.toFixed(0)}
              </div>
              <div className='text-muted-foreground text-[10px] uppercase'>Quality</div>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className='space-y-4'>
        {/* EARS Pattern */}
        {(spec.ears_trigger ?? spec.ears_precondition ?? spec.ears_postcondition) && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              EARS Pattern
            </h4>
            <div className='bg-muted/30 space-y-2 rounded-lg p-3'>
              {spec.ears_trigger && (
                <div className='flex items-start gap-2'>
                  <Badge variant='outline' className='shrink-0 text-[9px]'>
                    WHEN
                  </Badge>
                  <span className='text-xs'>{spec.ears_trigger}</span>
                </div>
              )}
              {spec.ears_precondition && (
                <div className='flex items-start gap-2'>
                  <Badge variant='outline' className='shrink-0 text-[9px]'>
                    WHILE
                  </Badge>
                  <span className='text-xs'>{spec.ears_precondition}</span>
                </div>
              )}
              {spec.ears_postcondition && (
                <div className='flex items-start gap-2'>
                  <Badge variant='outline' className='shrink-0 text-[9px]'>
                    SHALL
                  </Badge>
                  <span className='text-xs'>{spec.ears_postcondition}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Constraints */}
        {spec.constraint_target !== undefined && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              Performance Constraint
            </h4>
            <div className='bg-muted/30 flex items-center gap-4 rounded-lg p-3'>
              <div className='text-center'>
                <div className='text-xl font-black tabular-nums'>{spec.constraint_target}</div>
                <div className='text-muted-foreground text-[10px]'>
                  {spec.constraint_unit ?? 'units'}
                </div>
              </div>
              {spec.constraint_tolerance !== undefined && (
                <>
                  <Separator orientation='vertical' className='h-8' />
                  <div className='text-center'>
                    <div className='text-sm font-bold tabular-nums'>
                      \u00B1{spec.constraint_tolerance}
                    </div>
                    <div className='text-muted-foreground text-[10px]'>Tolerance</div>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* Pre/Post Conditions */}
        {(spec.preconditions.length > 0 || spec.postconditions.length > 0) && (
          <div className='grid grid-cols-2 gap-3'>
            {spec.preconditions.length > 0 && (
              <div className='space-y-1'>
                <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                  Preconditions
                </h4>
                <ul className='space-y-1 text-xs'>
                  {spec.preconditions.slice(0, 3).map((pre, i) => (
                    <li key={i} className='flex items-start gap-1'>
                      <span className='text-muted-foreground'>•</span>
                      <span className='line-clamp-1'>{pre}</span>
                    </li>
                  ))}
                  {spec.preconditions.length > 3 && (
                    <li className='text-muted-foreground text-[10px]'>
                      +{spec.preconditions.length - 3} more
                    </li>
                  )}
                </ul>
              </div>
            )}
            {spec.postconditions.length > 0 && (
              <div className='space-y-1'>
                <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                  Postconditions
                </h4>
                <ul className='space-y-1 text-xs'>
                  {spec.postconditions.slice(0, 3).map((post, i) => (
                    <li key={i} className='flex items-start gap-1'>
                      <span className='text-muted-foreground'>•</span>
                      <span className='line-clamp-1'>{post}</span>
                    </li>
                  ))}
                  {spec.postconditions.length > 3 && (
                    <li className='text-muted-foreground text-[10px]'>
                      +{spec.postconditions.length - 3} more
                    </li>
                  )}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Quality Scores Detail */}
        {showQuality && spec.quality_scores && Object.keys(spec.quality_scores).length > 0 && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              Quality Dimensions
            </h4>
            <QualityScoreGauge
              overallScore={spec.overall_quality_score ?? 0}
              dimensions={Object.entries(spec.quality_scores).map(([dim, score]) => ({
                dimension: dim,
                score: score,
              }))}
              issues={spec.quality_issues ?? []}
              size='sm'
              showDetails
            />
          </div>
        )}

        {/* Traceability & Impact */}
        <div className='text-muted-foreground flex items-center justify-between border-t pt-2 text-xs'>
          <div className='flex items-center gap-4'>
            <div className='flex items-center gap-1'>
              <TrendingUp className='h-3 w-3' />
              <span>{spec.upstream_count} upstream</span>
            </div>
            <div className='flex items-center gap-1'>
              <TrendingDown className='h-3 w-3' />
              <span>{spec.downstream_count} downstream</span>
            </div>
            <div className='flex items-center gap-1'>
              <GitBranch className='h-3 w-3' />
              <span>{spec.change_count} changes</span>
            </div>
          </div>
          {spec.wsjf_score !== undefined && (
            <Badge variant='outline' className='text-[10px]'>
              WSJF: {spec.wsjf_score.toFixed(1)}
            </Badge>
          )}
        </div>

        {/* Verification Evidence */}
        {spec.verified_at && (
          <div className='text-muted-foreground text-[10px]'>
            Verified {format(new Date(spec.verified_at), 'MMM d, yyyy')}
            {spec.verified_by && ` by ${spec.verified_by}`}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

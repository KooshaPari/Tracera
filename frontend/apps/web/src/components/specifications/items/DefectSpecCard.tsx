/**
 * DefectSpec Card Component
 *
 * Displays defect/bug specification with severity, root cause analysis,
 * reproduction steps, and resolution tracking.
 */

import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  Bug,
  CheckCircle2,
  Circle,
  FileCode,
  GitBranch,
  Play,
  RefreshCw,
  User,
} from 'lucide-react';

import type { DefectSpec } from '@/hooks/useItemSpecs';

import { cn } from '@/lib/utils';
import { Badge, Button, Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui';

interface DefectSpecCardProps {
  spec: DefectSpec;
  onClick?: () => void;
  className?: string;
  compact?: boolean;
  showReproSteps?: boolean;
}

const severityStyles = {
  critical: { bg: 'bg-red-500', icon: AlertCircle, text: 'text-white' },
  major: { bg: 'bg-orange-500', icon: AlertTriangle, text: 'text-white' },
  minor: { bg: 'bg-yellow-500', icon: Bug, text: 'text-white' },
  trivial: { bg: 'bg-blue-500', icon: Circle, text: 'text-white' },
};

const statusStyles = {
  assigned: { bg: 'bg-purple-500/10', icon: User, text: 'text-purple-600' },
  closed: { bg: 'bg-muted', icon: CheckCircle2, text: 'text-muted-foreground' },
  in_progress: { bg: 'bg-yellow-500/10', icon: Play, text: 'text-yellow-600' },
  new: { bg: 'bg-blue-500/10', icon: Circle, text: 'text-blue-600' },
  reopened: { bg: 'bg-red-500/10', icon: RefreshCw, text: 'text-red-600' },
  resolved: {
    bg: 'bg-green-500/10',
    icon: CheckCircle2,
    text: 'text-green-600',
  },
  verified: {
    bg: 'bg-green-500/10',
    icon: CheckCircle2,
    text: 'text-green-700',
  },
};

const regressionRiskStyles = {
  critical: 'bg-red-500 text-white',
  high: 'bg-orange-500 text-white',
  low: 'bg-green-500 text-white',
  medium: 'bg-yellow-500 text-white',
  minimal: 'bg-blue-500 text-white',
};

export function DefectSpecCard({
  spec,
  onClick,
  className,
  compact = false,
  showReproSteps = true,
}: DefectSpecCardProps) {
  const severityStyle = severityStyles[spec.severity];
  const statusStyle = statusStyles[spec.status];
  const SeverityIcon = severityStyle.icon;
  const StatusIcon = statusStyle.icon;

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
                <Badge className={cn('text-[10px]', severityStyle.bg, severityStyle.text)}>
                  <SeverityIcon className='mr-1 h-2.5 w-2.5' />
                  {spec.severity}
                </Badge>
                <Badge className={cn('text-[10px]', statusStyle.bg, statusStyle.text)}>
                  <StatusIcon className='mr-1 h-2.5 w-2.5' />
                  {spec.status.replace('_', ' ')}
                </Badge>
              </div>
              <p className='truncate text-xs font-medium'>{spec.title}</p>
              {spec.affected_versions && spec.affected_versions.length > 0 && (
                <p className='text-muted-foreground mt-1 text-[10px]'>
                  v{spec.affected_versions[0]}
                  {spec.affected_versions.length > 1 && ` +${spec.affected_versions.length - 1}`}
                </p>
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
              <Badge className={cn('text-[10px]', severityStyle.bg, severityStyle.text)}>
                <SeverityIcon className='mr-1 h-2.5 w-2.5' />
                {spec.severity}
              </Badge>
              <Badge className={cn('text-[10px]', statusStyle.bg, statusStyle.text)}>
                <StatusIcon className='mr-1 h-2.5 w-2.5' />
                {spec.status.replace('_', ' ')}
              </Badge>
              {spec.regression_risk && (
                <Badge className={cn('text-[10px]', regressionRiskStyles[spec.regression_risk])}>
                  {spec.regression_risk} regression risk
                </Badge>
              )}
              {spec.reproducible === false && (
                <Badge variant='outline' className='text-[10px]'>
                  Intermittent
                </Badge>
              )}
            </div>
            <CardTitle className='text-sm font-semibold'>{spec.title}</CardTitle>
            {spec.description && (
              <p className='text-muted-foreground mt-1 line-clamp-2 text-xs'>{spec.description}</p>
            )}
          </div>

          {/* Assignee */}
          {spec.assigned_to && (
            <div className='flex items-center gap-2 text-xs'>
              <div className='bg-primary/10 flex h-6 w-6 items-center justify-center rounded-full'>
                <User className='text-primary h-3 w-3' />
              </div>
              <span className='font-medium'>{spec.assigned_to}</span>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className='space-y-4'>
        {/* Version Info */}
        {spec.affected_versions && spec.affected_versions.length > 0 && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              Affected Versions
            </h4>
            <div className='flex flex-wrap gap-1'>
              {spec.affected_versions.map((ver, i) => (
                <Badge key={i} variant='destructive' className='text-[10px]'>
                  v{ver}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Environment */}
        {spec.environment && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              Environment
            </h4>
            <div className='bg-muted/30 rounded-lg p-2 font-mono text-xs'>{spec.environment}</div>
          </div>
        )}

        {/* Reproduction Steps */}
        {showReproSteps && spec.steps_to_reproduce && spec.steps_to_reproduce.length > 0 && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              Steps to Reproduce
            </h4>
            <ol className='list-inside list-decimal space-y-1.5 text-xs'>
              {spec.steps_to_reproduce.slice(0, 4).map((step, i) => (
                <li key={i} className='text-muted-foreground'>
                  <span className='text-foreground'>{step}</span>
                </li>
              ))}
              {spec.steps_to_reproduce.length > 4 && (
                <li className='text-muted-foreground'>
                  +{spec.steps_to_reproduce.length - 4} more steps
                </li>
              )}
            </ol>
          </div>
        )}

        {/* Expected vs Actual */}
        {(spec.expected_behavior || spec.actual_behavior) && (
          <div className='grid grid-cols-2 gap-3'>
            {spec.expected_behavior && (
              <div className='space-y-1'>
                <h4 className='text-[10px] font-black tracking-widest text-green-600 uppercase'>
                  Expected
                </h4>
                <p className='line-clamp-3 text-xs'>{spec.expected_behavior}</p>
              </div>
            )}
            {spec.actual_behavior && (
              <div className='space-y-1'>
                <h4 className='text-[10px] font-black tracking-widest text-red-600 uppercase'>
                  Actual
                </h4>
                <p className='line-clamp-3 text-xs'>{spec.actual_behavior}</p>
              </div>
            )}
          </div>
        )}

        {/* Root Cause */}
        {spec.root_cause && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              Root Cause Analysis
            </h4>
            <div className='rounded-lg border border-orange-500/20 bg-orange-500/10 p-2'>
              <p className='text-xs'>{spec.root_cause}</p>
            </div>
          </div>
        )}

        {/* Resolution */}
        {spec.resolution && (
          <div className='space-y-2'>
            <h4 className='text-[10px] font-black tracking-widest text-green-600 uppercase'>
              Resolution
            </h4>
            <div className='rounded-lg border border-green-500/20 bg-green-500/10 p-2'>
              <p className='text-xs'>{spec.resolution}</p>
            </div>
          </div>
        )}

        {/* Verification Notes */}
        {spec.verification_notes && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              Verification Notes
            </h4>
            <div className='rounded-lg border border-blue-500/20 bg-blue-500/10 p-2'>
              <p className='text-xs italic'>{spec.verification_notes}</p>
            </div>
          </div>
        )}

        {/* Attachments */}
        {spec.attachments && spec.attachments.length > 0 && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              Attachments ({spec.attachments.length})
            </h4>
            <div className='flex flex-wrap gap-1'>
              {spec.attachments.slice(0, 3).map((att, i) => (
                <Badge key={i} variant='outline' className='text-[9px]'>
                  {att.type}: {att.description ?? att.url}
                </Badge>
              ))}
              {spec.attachments.length > 3 && (
                <Badge variant='secondary' className='text-[9px]'>
                  +{spec.attachments.length - 3}
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Related Items */}
        <div className='text-muted-foreground flex items-center justify-between border-t pt-2 text-xs'>
          <div className='flex items-center gap-4'>
            {spec.related_requirements && spec.related_requirements.length > 0 && (
              <div className='flex items-center gap-1'>
                <FileCode className='h-3 w-3' />
                <span>{spec.related_requirements.length} reqs</span>
              </div>
            )}
            {spec.related_defects && spec.related_defects.length > 0 && (
              <div className='flex items-center gap-1'>
                <GitBranch className='h-3 w-3' />
                <span>{spec.related_defects.length} related</span>
              </div>
            )}
            {spec.time_to_fix_estimate && (
              <div className='flex items-center gap-1'>
                <span>Est: {spec.time_to_fix_estimate}h</span>
              </div>
            )}
          </div>
          {spec.reported_by && <span className='text-[10px]'>Reported by {spec.reported_by}</span>}
        </div>
      </CardContent>
    </Card>
  );
}

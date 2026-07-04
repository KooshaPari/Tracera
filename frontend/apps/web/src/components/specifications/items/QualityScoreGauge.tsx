/**
 * Quality Score Gauge Component
 *
 * Visual gauge showing overall quality score with breakdown by dimension.
 * Implements ISO 29148 quality dimensions visualization.
 */

import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Eye,
  Info,
  Shield,
  Target,
  Zap,
} from 'lucide-react';

import { cn } from '@/lib/utils';
import { Badge, Progress } from '@tracertm/ui';

interface QualityDimension {
  dimension: string;
  score: number;
  weight?: number;
}

interface QualityIssue {
  dimension: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
  suggestion?: string | undefined;
}

interface QualityScoreGaugeProps {
  overallScore?: number;
  dimensions?: QualityDimension[];
  issues?: QualityIssue[];
  size?: 'sm' | 'md' | 'lg';
  showDetails?: boolean;
  className?: string;
}

const dimensionIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  ambiguity: Eye,
  completeness: Target,
  consistency: Shield,
  feasibility: Zap,
  testability: CheckCircle2,
  traceability: Target,
  verifiability: CheckCircle2,
};

const severityStyles = {
  error: {
    bg: 'bg-red-500/10',
    border: 'border-red-500/20',
    icon: AlertCircle,
    text: 'text-red-600',
  },
  info: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/20',
    icon: Info,
    text: 'text-blue-600',
  },
  warning: {
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/20',
    icon: AlertTriangle,
    text: 'text-yellow-600',
  },
};

function getScoreColor(score: number): string {
  if (score >= 90) {
    return 'text-green-500';
  }
  if (score >= 70) {
    return 'text-yellow-500';
  }
  if (score >= 50) {
    return 'text-orange-500';
  }
  return 'text-red-500';
}

// Progress color can be used for custom Progress component styling
// Function getProgressColor(score: number): string {
// 	If (score >= 90) return "bg-green-500";
// 	If (score >= 70) return "bg-yellow-500";
// 	If (score >= 50) return "bg-orange-500";
// 	Return "bg-red-500";
// }

export function QualityScoreGauge({
  overallScore,
  dimensions = [],
  issues = [],
  size = 'md',
  showDetails = true,
  className,
}: QualityScoreGaugeProps) {
  const score = overallScore ?? 0;
  const sizeClasses = {
    lg: 'text-6xl',
    md: 'text-4xl',
    sm: 'text-2xl',
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Main Score */}
      <div className='flex items-center gap-4'>
        <div className={cn('font-black tabular-nums', sizeClasses[size], getScoreColor(score))}>
          {score.toFixed(0)}
          <span className='text-muted-foreground text-base font-normal'>/100</span>
        </div>
        <div className='flex-1'>
          <div className='text-muted-foreground mb-1 text-xs font-bold tracking-widest uppercase'>
            Quality Score
          </div>
          <Progress value={score} className='h-2' />
        </div>
      </div>

      {/* Dimension Breakdown */}
      {showDetails && dimensions.length > 0 && (
        <div className='space-y-2'>
          <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
            Quality Dimensions
          </h4>
          <div className='grid grid-cols-2 gap-2'>
            {dimensions.map((dim) => {
              const Icon = dimensionIcons[dim.dimension.toLowerCase()] ?? Target;
              return (
                <div
                  key={dim.dimension}
                  className='bg-muted/30 flex items-center gap-2 rounded-lg p-2'
                >
                  <Icon className='text-muted-foreground h-3.5 w-3.5' />
                  <div className='min-w-0 flex-1'>
                    <div className='flex items-center justify-between'>
                      <span className='truncate text-xs font-medium capitalize'>
                        {dim.dimension}
                      </span>
                      <span
                        className={cn('text-xs font-bold tabular-nums', getScoreColor(dim.score))}
                      >
                        {dim.score.toFixed(0)}
                      </span>
                    </div>
                    <Progress value={dim.score} className='mt-1 h-1' />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Quality Issues */}
      {showDetails && issues.length > 0 && (
        <div className='space-y-2'>
          <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
            Issues ({issues.length})
          </h4>
          <div className='max-h-48 space-y-2 overflow-y-auto'>
            {issues.map((issue, idx) => {
              const style = severityStyles[issue.severity];
              const Icon = style.icon;
              return (
                <div key={idx} className={cn('p-2 rounded-lg border', style.bg, style.border)}>
                  <div className='flex items-start gap-2'>
                    <Icon className={cn('h-3.5 w-3.5 mt-0.5', style.text)} />
                    <div className='min-w-0 flex-1'>
                      <div className='mb-0.5 flex items-center gap-2'>
                        <Badge
                          variant='outline'
                          className={cn(
                            'text-[9px] font-black uppercase',
                            style.text,
                            style.border,
                          )}
                        >
                          {issue.dimension}
                        </Badge>
                      </div>
                      <p className='text-xs'>{issue.message}</p>
                      {issue.suggestion && (
                        <p className='text-muted-foreground mt-1 text-[10px] italic'>
                          {issue.suggestion}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

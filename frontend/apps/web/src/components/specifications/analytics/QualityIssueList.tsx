/**
 * Quality Issue List Component
 * Displays a list of quality issues with severity indicators and suggestions
 */

import type { AnalyticsQualityIssue, QualityDimension } from '@/hooks/useItemSpecAnalytics';

import { cn } from '@/lib/utils';

interface QualityIssueListProps {
  issues: AnalyticsQualityIssue[];
  maxItems?: number;
  showSuggestions?: boolean;
  groupByDimension?: boolean;
  className?: string;
}

const severityConfig = {
  error: {
    color: 'text-red-600 bg-red-50 border-red-200',
    icon: '✕',
    iconColor: 'text-red-600',
    label: 'Error',
  },
  info: {
    color: 'text-blue-600 bg-blue-50 border-blue-200',
    icon: 'ℹ',
    iconColor: 'text-blue-600',
    label: 'Info',
  },
  warning: {
    color: 'text-yellow-700 bg-yellow-50 border-yellow-200',
    icon: '⚠',
    iconColor: 'text-yellow-600',
    label: 'Warning',
  },
};

const dimensionLabels: Record<QualityDimension, string> = {
  completeness: 'Completeness',
  consistency: 'Consistency',
  feasibility: 'Feasibility',
  necessity: 'Necessity',
  singularity: 'Singularity',
  traceability: 'Traceability',
  unambiguity: 'Unambiguity',
  verifiability: 'Verifiability',
};

export function QualityIssueList({
  issues,
  maxItems,
  showSuggestions = true,
  groupByDimension = false,
  className,
}: QualityIssueListProps) {
  const displayIssues = maxItems ? issues.slice(0, maxItems) : issues;
  const hasMore = maxItems && issues.length > maxItems;

  if (groupByDimension) {
    const grouped = displayIssues.reduce<Record<string, AnalyticsQualityIssue[]>>((acc, issue) => {
      const dim = issue.dimension;
      acc[dim] ??= [];
      acc[dim].push(issue);
      return acc;
    }, {});

    return (
      <div className={cn('space-y-4', className)}>
        {Object.entries(grouped).map(([dimension, dimIssues]) => (
          <div key={dimension} className='space-y-2'>
            <h4 className='text-sm font-semibold'>
              {dimensionLabels[dimension as QualityDimension] || dimension}
            </h4>
            <div className='space-y-2 pl-2'>
              {dimIssues.map((issue, idx) => (
                <QualityIssueItem
                  key={idx}
                  issue={issue}
                  showSuggestion={showSuggestions}
                  compact
                />
              ))}
            </div>
          </div>
        ))}
        {hasMore && (
          <p className='text-muted-foreground text-sm'>
            And {issues.length - maxItems} more issues...
          </p>
        )}
      </div>
    );
  }

  return (
    <div className={cn('space-y-2', className)}>
      {displayIssues.map((issue, idx) => (
        <QualityIssueItem key={idx} issue={issue} showSuggestion={showSuggestions} />
      ))}
      {hasMore && (
        <p className='text-muted-foreground text-sm'>
          And {issues.length - maxItems} more issues...
        </p>
      )}
    </div>
  );
}

interface QualityIssueItemProps {
  issue: AnalyticsQualityIssue;
  showSuggestion?: boolean;
  compact?: boolean;
}

export function QualityIssueItem({
  issue,
  showSuggestion = true,
  compact = false,
}: QualityIssueItemProps) {
  const config = severityConfig[issue.severity];
  const dimensionLabel = dimensionLabels[issue.dimension] || issue.dimension;

  if (compact) {
    return (
      <div className={cn('flex items-start gap-2 text-sm', config.color, 'p-2 rounded border')}>
        <span className={cn('flex-shrink-0', config.iconColor)}>{config.icon}</span>
        <div className='min-w-0 flex-1'>
          <p className='break-words'>{issue.message}</p>
          {showSuggestion && issue.suggestion && (
            <p className='mt-1 text-xs opacity-80'>💡 {issue.suggestion}</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={cn('rounded-lg border p-3', config.color)}>
      <div className='flex items-start gap-3'>
        <span className={cn('text-lg flex-shrink-0', config.iconColor)}>{config.icon}</span>
        <div className='min-w-0 flex-1'>
          <div className='mb-1 flex items-center gap-2'>
            <span className='font-medium'>{config.label}</span>
            <span className='rounded bg-white/50 px-1.5 py-0.5 text-xs'>{dimensionLabel}</span>
            {issue.line_reference && (
              <span className='font-mono text-xs opacity-70'>Line {issue.line_reference}</span>
            )}
          </div>
          <p className='text-sm break-words'>{issue.message}</p>
          {showSuggestion && issue.suggestion && (
            <div className='mt-2 rounded bg-white/30 p-2 text-sm'>
              <span className='font-medium'>Suggestion: </span>
              {issue.suggestion}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

interface QualityIssueSummaryProps {
  criticalCount: number;
  warningCount: number;
  infoCount?: number;
  className?: string;
}

export function QualityIssueSummary({
  criticalCount,
  warningCount,
  infoCount = 0,
  className,
}: QualityIssueSummaryProps) {
  return (
    <div className={cn('flex items-center gap-4 text-sm', className)}>
      {criticalCount > 0 && (
        <div className='flex items-center gap-1.5'>
          <span className='text-red-600'>{severityConfig.error.icon}</span>
          <span className='font-medium'>{criticalCount}</span>
          <span className='text-muted-foreground'>errors</span>
        </div>
      )}
      {warningCount > 0 && (
        <div className='flex items-center gap-1.5'>
          <span className='text-yellow-600'>{severityConfig.warning.icon}</span>
          <span className='font-medium'>{warningCount}</span>
          <span className='text-muted-foreground'>warnings</span>
        </div>
      )}
      {infoCount > 0 && (
        <div className='flex items-center gap-1.5'>
          <span className='text-blue-600'>{severityConfig.info.icon}</span>
          <span className='font-medium'>{infoCount}</span>
          <span className='text-muted-foreground'>info</span>
        </div>
      )}
      {criticalCount === 0 && warningCount === 0 && infoCount === 0 && (
        <div className='flex items-center gap-1.5 text-green-600'>
          <span>✓</span>
          <span>No issues found</span>
        </div>
      )}
    </div>
  );
}

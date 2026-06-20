import type { Scenario, ScenarioStatus } from '@tracertm/types';

import { ArrowRight, BarChart3, CheckCircle2, Clock, FileText, Play, XCircle } from 'lucide-react';
import React, { useCallback } from 'react';

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, cn } from '@tracertm/ui';

interface ScenarioCardProps {
  scenario: Scenario;
  onRun?: () => void;
  onClick?: () => void;
  onViewTestCases?: () => void;
  className?: string;
  showExecutionStats?: boolean;
}

const statusColors: Record<ScenarioStatus, string> = {
  draft: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
  failing: 'bg-red-500/10 text-red-500 border-red-500/20',
  passing: 'bg-green-500/10 text-green-500 border-green-500/20',
  pending: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  skipped: 'bg-muted text-muted-foreground border-border',
};

const statusIcons: Record<ScenarioStatus, React.ComponentType<{ className?: string }>> = {
  draft: FileText,
  failing: XCircle,
  passing: CheckCircle2,
  pending: Clock,
  skipped: Clock,
};

export function ScenarioCard({
  scenario,
  onRun,
  onClick,
  onViewTestCases,
  className,
  showExecutionStats = true,
}: ScenarioCardProps): React.JSX.Element {
  const StatusIcon = statusIcons[scenario.status];
  const executionCount = scenario.executionCount || 0;
  const lastExecuted = scenario.lastRunAt
    ? new Date(scenario.lastRunAt).toLocaleDateString()
    : null;
  const hasRunAction = onRun !== undefined;
  const hasTestCasesAction = onViewTestCases !== undefined;

  const handleRunClick = useCallback<React.MouseEventHandler<HTMLButtonElement>>(
    (event) => {
      event.stopPropagation();
      onRun?.();
    },
    [onRun],
  );

  const handleViewTestCasesClick = useCallback<React.MouseEventHandler<HTMLButtonElement>>(
    (event) => {
      event.stopPropagation();
      onViewTestCases?.();
    },
    [onViewTestCases],
  );

  return (
    <Card
      className={cn(
        'hover:shadow-md hover:bg-muted/30 hover:border-primary/30 transition-all duration-200 cursor-pointer',
        className,
      )}
      onClick={onClick}
    >
      <CardHeader className='pb-3'>
        <div className='flex items-start justify-between'>
          <div className='flex items-center gap-2'>
            <Badge variant='outline' className='font-mono text-xs'>
              {scenario.scenarioNumber}
            </Badge>
            <Badge className={statusColors[scenario.status]}>
              <StatusIcon className='mr-1 h-3 w-3' />
              {scenario.status}
            </Badge>
            {scenario.isOutline && (
              <Badge variant='secondary' className='h-5 text-[10px]'>
                Outline
              </Badge>
            )}
          </div>
          {hasRunAction && (
            <Button
              size='icon'
              variant='ghost'
              className='hover:bg-muted/50 h-6 w-6 transition-colors'
              onClick={handleRunClick}
              title='Run scenario'
              type='button'
            >
              <Play className='h-3 w-3' />
            </Button>
          )}
        </div>
        <CardTitle className='mt-2 text-base'>{scenario.title}</CardTitle>
      </CardHeader>

      <CardContent className='space-y-3 pt-0 pb-4'>
        {/* Step counts */}
        <div className='text-muted-foreground flex gap-4 text-xs'>
          <div className='flex items-center gap-1'>
            <span className='text-foreground font-bold'>{scenario.givenSteps?.length || 0}</span>
            Given
          </div>
          <div className='flex items-center gap-1'>
            <span className='text-foreground font-bold'>{scenario.whenSteps?.length || 0}</span>
            When
          </div>
          <div className='flex items-center gap-1'>
            <span className='text-foreground font-bold'>{scenario.thenSteps?.length || 0}</span>
            Then
          </div>
        </div>

        {/* Execution stats */}
        {showExecutionStats && (
          <div className='text-muted-foreground border-border/50 flex items-center justify-between border-t pt-2 text-xs'>
            <div className='flex items-center gap-2'>
              <BarChart3 className='h-3 w-3' />
              <span>
                <span className='text-foreground font-semibold'>{executionCount}</span>
                {' runs'}
              </span>
            </div>
            {lastExecuted && <span className='text-[10px]'>Last: {lastExecuted}</span>}
          </div>
        )}

        {/* Test cases link */}
        {hasTestCasesAction && (
          <Button
            onClick={handleViewTestCasesClick}
            variant='outline'
            size='sm'
            className='h-7 w-full gap-1 text-xs'
            type='button'
          >
            View Test Cases
            <ArrowRight className='h-3 w-3' />
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

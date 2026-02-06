/**
 * UserStorySpec Card Component
 *
 * Displays user story specification with acceptance criteria,
 * story points, and definition of done tracking.
 */

import {
  ArrowRight,
  CheckCircle2,
  Circle,
  FileCheck,
  GitBranch,
  Layers,
  Play,
  Search,
  Square,
  Target,
} from 'lucide-react';

import type { UserStorySpec } from '@/hooks/useItemSpecs';

import { cn } from '@/lib/utils';
import { Badge, Button, Card, CardContent, CardHeader, CardTitle, Progress } from '@tracertm/ui';

interface UserStorySpecCardProps {
  spec: UserStorySpec;
  onClick?: () => void;
  className?: string;
  compact?: boolean;
  showAcceptanceCriteria?: boolean;
}

const statusStyles = {
  archived: { bg: 'bg-gray-500/10', icon: FileCheck, text: 'text-gray-600' },
  backlog: { bg: 'bg-muted', icon: Circle, text: 'text-muted-foreground' },
  done: { bg: 'bg-green-500/10', icon: CheckCircle2, text: 'text-green-600' },
  in_progress: { bg: 'bg-yellow-500/10', icon: Play, text: 'text-yellow-600' },
  ready: { bg: 'bg-blue-500/10', icon: Target, text: 'text-blue-600' },
  review: { bg: 'bg-purple-500/10', icon: Search, text: 'text-purple-600' },
};

function getPointsColor(points: number | undefined): string {
  if (points === undefined) {
    return 'bg-muted text-muted-foreground';
  }
  if (points <= 2) {
    return 'bg-green-500/20 text-green-700';
  }
  if (points <= 5) {
    return 'bg-yellow-500/20 text-yellow-700';
  }
  if (points <= 8) {
    return 'bg-orange-500/20 text-orange-700';
  }
  return 'bg-red-500/20 text-red-700';
}

export function UserStorySpecCard({
  spec,
  onClick,
  className,
  compact = false,
  showAcceptanceCriteria = true,
}: UserStorySpecCardProps) {
  const statusStyle = statusStyles[spec.status];
  const StatusIcon = statusStyle.icon;

  // Calculate acceptance criteria completion
  const acCompleted = spec.acceptance_criteria.filter((ac) => ac.completed).length;
  const acTotal = spec.acceptance_criteria.length;
  const acProgress = acTotal > 0 ? (acCompleted / acTotal) * 100 : 0;

  // Build story statement
  const storyStatement = `As a ${spec.as_a}, I want ${spec.i_want}${spec.so_that ? `, so that ${spec.so_that}` : ''}`;

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
                <Badge className={cn('text-[10px]', statusStyle.bg, statusStyle.text)}>
                  <StatusIcon className='mr-1 h-2.5 w-2.5' />
                  {spec.status.replace('_', ' ')}
                </Badge>
                {spec.story_points !== undefined && (
                  <Badge
                    className={cn('text-[10px] font-black', getPointsColor(spec.story_points))}
                  >
                    {spec.story_points} SP
                  </Badge>
                )}
              </div>
              <p className='line-clamp-2 text-xs'>{storyStatement}</p>
              {acTotal > 0 && (
                <div className='mt-2 flex items-center gap-2'>
                  <span className='text-muted-foreground text-[10px]'>AC:</span>
                  <Progress value={acProgress} className='h-1 flex-1' />
                  <span className='text-xs font-bold tabular-nums'>
                    {acCompleted}/{acTotal}
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
              <Badge className={cn('text-[10px]', statusStyle.bg, statusStyle.text)}>
                <StatusIcon className='mr-1 h-2.5 w-2.5' />
                {spec.status.replace('_', ' ')}
              </Badge>
              {spec.story_points !== undefined && (
                <Badge className={cn('text-[10px] font-black', getPointsColor(spec.story_points))}>
                  {spec.story_points} Story Points
                </Badge>
              )}
              {spec.estimation_confidence !== undefined && (
                <Badge variant='outline' className='text-[10px]'>
                  {(spec.estimation_confidence * 100).toFixed(0)}% confidence
                </Badge>
              )}
              {spec.parent_epic && (
                <Badge variant='secondary' className='text-[10px]'>
                  <Layers className='mr-1 h-2.5 w-2.5' />
                  {spec.parent_epic}
                </Badge>
              )}
            </div>
            <CardTitle className='text-sm font-semibold'>User Story</CardTitle>
          </div>

          {/* Priority Badge */}
          <Badge
            variant='outline'
            className={cn(
              'text-lg font-black tabular-nums h-8 w-8 justify-center',
              spec.priority <= 1
                ? 'border-red-500 text-red-600'
                : spec.priority <= 3
                  ? 'border-orange-500 text-orange-600'
                  : spec.priority <= 5
                    ? 'border-yellow-500 text-yellow-600'
                    : 'border-muted text-muted-foreground',
            )}
          >
            {spec.priority}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className='space-y-4'>
        {/* Story Statement */}
        <div className='bg-primary/5 border-primary/10 rounded-lg border p-3'>
          <div className='space-y-2'>
            <div className='flex items-start gap-2'>
              <Badge variant='outline' className='shrink-0 text-[9px]'>
                AS A
              </Badge>
              <span className='text-sm font-medium'>{spec.as_a}</span>
            </div>
            <div className='flex items-start gap-2'>
              <Badge variant='outline' className='shrink-0 text-[9px]'>
                I WANT
              </Badge>
              <span className='text-sm'>{spec.i_want}</span>
            </div>
            {spec.so_that && (
              <div className='flex items-start gap-2'>
                <Badge variant='outline' className='shrink-0 text-[9px]'>
                  SO THAT
                </Badge>
                <span className='text-muted-foreground text-sm'>{spec.so_that}</span>
              </div>
            )}
          </div>
        </div>

        {/* Acceptance Criteria */}
        {showAcceptanceCriteria && spec.acceptance_criteria.length > 0 && (
          <div className='space-y-2'>
            <div className='flex items-center justify-between'>
              <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                Acceptance Criteria
              </h4>
              <span className='text-xs font-bold'>
                {acCompleted} / {acTotal}
              </span>
            </div>
            <Progress value={acProgress} className='h-2' />
            <div className='mt-2 space-y-1.5'>
              {spec.acceptance_criteria.slice(0, 4).map((ac, i) => (
                <div
                  key={i}
                  className={cn(
                    'flex items-start gap-2 p-2 rounded text-xs',
                    ac.completed ? 'bg-green-500/10' : 'bg-muted/30',
                  )}
                >
                  {ac.completed ? (
                    <CheckCircle2 className='h-3.5 w-3.5 shrink-0 text-green-600' />
                  ) : (
                    <Square className='text-muted-foreground h-3.5 w-3.5 shrink-0' />
                  )}
                  <span className={cn(ac.completed && 'line-through text-muted-foreground')}>
                    {ac.criterion}
                  </span>
                </div>
              ))}
              {spec.acceptance_criteria.length > 4 && (
                <p className='text-muted-foreground pl-6 text-[10px]'>
                  +{spec.acceptance_criteria.length - 4} more criteria
                </p>
              )}
            </div>
          </div>
        )}

        {/* Definition of Done */}
        {spec.definition_of_done.length > 0 && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              Definition of Done
            </h4>
            <div className='flex flex-wrap gap-1'>
              {spec.definition_of_done.slice(0, 5).map((dod, i) => (
                <Badge key={i} variant='outline' className='text-[9px]'>
                  <CheckCircle2 className='mr-1 h-2.5 w-2.5' />
                  {dod}
                </Badge>
              ))}
              {spec.definition_of_done.length > 5 && (
                <Badge variant='secondary' className='text-[9px]'>
                  +{spec.definition_of_done.length - 5}
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Edge Cases */}
        {spec.edge_cases.length > 0 && (
          <div className='space-y-2'>
            <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
              Edge Cases ({spec.edge_cases.length})
            </h4>
            <ul className='space-y-1 text-xs'>
              {spec.edge_cases.slice(0, 3).map((ec, i) => (
                <li key={i} className='text-muted-foreground flex items-start gap-1'>
                  <span>•</span>
                  <span className='line-clamp-1'>{ec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Dependencies & Related */}
        <div className='text-muted-foreground flex items-center justify-between border-t pt-2 text-xs'>
          <div className='flex items-center gap-4'>
            {spec.dependencies.length > 0 && (
              <div className='flex items-center gap-1'>
                <GitBranch className='h-3 w-3' />
                <span>{spec.dependencies.length} deps</span>
              </div>
            )}
            {spec.related_tasks.length > 0 && (
              <div className='flex items-center gap-1'>
                <FileCheck className='h-3 w-3' />
                <span>{spec.related_tasks.length} tasks</span>
              </div>
            )}
            {spec.test_scenarios.length > 0 && (
              <div className='flex items-center gap-1'>
                <Target className='h-3 w-3' />
                <span>{spec.test_scenarios.length} tests</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

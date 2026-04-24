/**
 * EpicDetailView Component
 *
 * Displays detailed information about epic items with business value,
 * timeline tracking, story breakdown, and acceptance criteria.
 * Deep purple theme (#7c3aed) for epic-specific UI elements.
 */

import { format } from 'date-fns';
import {
  AlertCircle,
  AlertTriangle,
  BookOpen,
  Calendar,
  CheckCircle2,
  Clock,
  Layers,
  Target,
  TrendingUp,
  Users,
  XCircle,
  Zap,
} from 'lucide-react';
import { useMemo } from 'react';

import type { EpicItem } from '@tracertm/types';

import { useEpicSpecByItem } from '@/hooks/useItemSpecs';
import { cn } from '@/lib/utils';
import { isEpicItem } from '@tracertm/types';
import { Badge, Card, CardContent, CardHeader, CardTitle, Progress, Separator } from '@tracertm/ui';

import type { DetailTab } from './BaseDetailView';

import { BaseDetailView } from './BaseDetailView';

interface EpicDetailViewProps {
  item: EpicItem;
  projectId: string;
}

// Epic status colors
const EPIC_STATUS_STYLES = {
  archived: {
    bg: 'bg-slate-500/10',
    icon: XCircle,
    label: 'Archived',
    text: 'text-slate-600',
  },
  backlog: {
    bg: 'bg-slate-500/10',
    icon: Clock,
    label: 'Backlog',
    text: 'text-slate-600',
  },
  completed: {
    bg: 'bg-green-500/10',
    icon: CheckCircle2,
    label: 'Completed',
    text: 'text-green-600',
  },
  in_progress: {
    bg: 'bg-blue-500/10',
    icon: Zap,
    label: 'In Progress',
    text: 'text-blue-600',
  },
} as const;

export function EpicDetailView({ item, projectId }: EpicDetailViewProps) {
  // Fetch epic spec data (must be called unconditionally)
  const { data: epicSpec, isLoading: specLoading } = useEpicSpecByItem(projectId, item.id);

  // Compute derived values
  const statusStyle =
    EPIC_STATUS_STYLES[epicSpec?.status ?? 'backlog'] || EPIC_STATUS_STYLES.backlog;
  const StatusIcon = statusStyle.icon;

  const completionPercentage = useMemo(() => {
    if (!epicSpec || epicSpec.child_stories_count === 0) {
      return 0;
    }
    // This is a placeholder - in reality, you'd calculate based on completed stories
    return Math.round((epicSpec.user_stories.length / epicSpec.child_stories_count) * 100);
  }, [epicSpec]);

  const timelineProgress = useMemo(() => {
    if (!epicSpec?.start_date || !epicSpec?.end_date) {
      return 0;
    }
    const now = new Date();
    const start = new Date(epicSpec.start_date);
    const end = new Date(epicSpec.end_date);
    const total = end.getTime() - start.getTime();
    const elapsed = now.getTime() - start.getTime();
    return Math.min(Math.max(Math.round((elapsed / total) * 100), 0), 100);
  }, [epicSpec?.start_date, epicSpec?.end_date]);

  // Define tabs
  const tabs: DetailTab[] = useMemo(() => {
    const allTabs: DetailTab[] = [
      {
        ariaLabel: 'Epic overview and key metrics',
        content: specLoading ? (
          <div className='flex items-center justify-center py-12'>
            <div className='h-8 w-8 animate-spin rounded-full border-4 border-purple-600 border-t-transparent' />
          </div>
        ) : !epicSpec ? (
          <Card className='bg-card/50 border-none'>
            <CardContent className='pt-6'>
              <p className='text-muted-foreground text-center text-sm'>
                No epic specification data available
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className='space-y-6'>
            {/* Key Metrics */}
            <div className='grid grid-cols-1 gap-4 md:grid-cols-3'>
              <Card className='border-none bg-purple-500/5'>
                <CardContent className='pt-6'>
                  <div className='space-y-2'>
                    <div className='flex items-center gap-2 text-purple-600'>
                      <Target className='h-4 w-4' />
                      <span className='text-xs font-black tracking-widest uppercase'>
                        Business Value
                      </span>
                    </div>
                    <div className='text-3xl font-black text-purple-600 tabular-nums'>
                      {epicSpec.business_value}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className='border-none bg-blue-500/5'>
                <CardContent className='pt-6'>
                  <div className='space-y-2'>
                    <div className='flex items-center gap-2 text-blue-600'>
                      <Layers className='h-4 w-4' />
                      <span className='text-xs font-black tracking-widest uppercase'>
                        User Stories
                      </span>
                    </div>
                    <div className='text-3xl font-black text-blue-600 tabular-nums'>
                      {epicSpec.user_stories.length} / {epicSpec.child_stories_count}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className='border-none bg-green-500/5'>
                <CardContent className='pt-6'>
                  <div className='space-y-2'>
                    <div className='flex items-center gap-2 text-green-600'>
                      <TrendingUp className='h-4 w-4' />
                      <span className='text-xs font-black tracking-widest uppercase'>
                        Completion
                      </span>
                    </div>
                    <div className='text-3xl font-black text-green-600 tabular-nums'>
                      {completionPercentage}%
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Status & Timeline */}
            <Card className='bg-card/50 border-none'>
              <CardHeader>
                <CardTitle className='flex items-center gap-2 text-base'>
                  <Calendar className='h-4 w-4 text-purple-600' />
                  Status & Timeline
                </CardTitle>
              </CardHeader>
              <CardContent className='space-y-4'>
                <div className='grid grid-cols-2 gap-4'>
                  <div>
                    <p className='text-muted-foreground mb-2 text-xs tracking-wider uppercase'>
                      Status
                    </p>
                    <Badge className={cn(statusStyle.bg, statusStyle.text)}>
                      <StatusIcon className='mr-1.5 h-3.5 w-3.5' />
                      {statusStyle.label}
                    </Badge>
                  </div>
                  {epicSpec.target_release && (
                    <div>
                      <p className='text-muted-foreground mb-2 text-xs tracking-wider uppercase'>
                        Target Release
                      </p>
                      <p className='font-medium'>{epicSpec.target_release}</p>
                    </div>
                  )}
                </div>

                {epicSpec.start_date && epicSpec.end_date && (
                  <>
                    <Separator />
                    <div className='space-y-2'>
                      <div className='flex items-center justify-between text-sm'>
                        <span>{format(new Date(epicSpec.start_date), 'MMM d, yyyy')}</span>
                        <span className='text-muted-foreground'>{timelineProgress}% elapsed</span>
                        <span>{format(new Date(epicSpec.end_date), 'MMM d, yyyy')}</span>
                      </div>
                      <Progress value={timelineProgress} className='h-2' />
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Basic Information */}
            <Card className='bg-card/50 border-none'>
              <CardHeader>
                <CardTitle className='text-base'>Basic Information</CardTitle>
              </CardHeader>
              <CardContent className='space-y-4'>
                <div className='grid grid-cols-2 gap-4'>
                  <div>
                    <p className='text-muted-foreground mb-1 text-xs tracking-wider uppercase'>
                      Title
                    </p>
                    <p className='font-medium'>{item.title}</p>
                  </div>
                  <div>
                    <p className='text-muted-foreground mb-1 text-xs tracking-wider uppercase'>
                      Owner
                    </p>
                    <p className='font-medium'>{item.owner ?? 'Unassigned'}</p>
                  </div>
                  <div>
                    <p className='text-muted-foreground mb-1 text-xs tracking-wider uppercase'>
                      Created
                    </p>
                    <p className='text-sm'>{format(new Date(item.createdAt), 'MMM d, yyyy')}</p>
                  </div>
                  <div>
                    <p className='text-muted-foreground mb-1 text-xs tracking-wider uppercase'>
                      Updated
                    </p>
                    <p className='text-sm'>
                      {format(new Date(item.updatedAt), 'MMM d, yyyy HH:mm')}
                    </p>
                  </div>
                </div>

                {item.description && (
                  <div>
                    <p className='text-muted-foreground mb-1 text-xs tracking-wider uppercase'>
                      Description
                    </p>
                    <p className='text-sm leading-relaxed'>{item.description}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        ),
        id: 'overview',
        label: 'Overview',
      },
      {
        ariaLabel: 'Epic objectives and scope',
        content: !epicSpec ? (
          <Card className='bg-card/50 border-none'>
            <CardContent className='pt-6'>
              <p className='text-muted-foreground text-center text-sm'>
                No specification data available
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className='space-y-6'>
            {/* Objectives */}
            {epicSpec.objectives.length > 0 && (
              <Card className='bg-card/50 border-none'>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2 text-base'>
                    <Target className='h-4 w-4 text-purple-600' />
                    Objectives
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className='space-y-2'>
                    {epicSpec.objectives.map((objective, i) => (
                      <li key={i} className='flex items-start gap-2'>
                        <CheckCircle2 className='mt-0.5 h-4 w-4 shrink-0 text-purple-600' />
                        <span className='text-sm'>{objective}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Scope Statement */}
            {epicSpec.scope_statement && (
              <Card className='bg-card/50 border-none'>
                <CardHeader>
                  <CardTitle className='text-base'>Scope Statement</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className='text-sm leading-relaxed'>{epicSpec.scope_statement}</p>
                </CardContent>
              </Card>
            )}

            {/* Out of Scope */}
            {epicSpec.out_of_scope && epicSpec.out_of_scope.length > 0 && (
              <Card className='border-none bg-red-500/5'>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2 text-base'>
                    <XCircle className='h-4 w-4 text-red-600' />
                    Out of Scope
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className='space-y-2'>
                    {epicSpec.out_of_scope.map((item, i) => (
                      <li key={i} className='flex items-start gap-2'>
                        <span className='text-red-600'>•</span>
                        <span className='text-sm'>{item}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Constraints & Assumptions */}
            <div className='grid grid-cols-1 gap-4 md:grid-cols-2'>
              {epicSpec.constraints.length > 0 && (
                <Card className='bg-card/50 border-none'>
                  <CardHeader>
                    <CardTitle className='text-base'>Constraints</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className='space-y-1'>
                      {epicSpec.constraints.map((constraint, i) => (
                        <li key={i} className='text-sm'>
                          • {constraint}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {epicSpec.assumptions.length > 0 && (
                <Card className='bg-card/50 border-none'>
                  <CardHeader>
                    <CardTitle className='text-base'>Assumptions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className='space-y-1'>
                      {epicSpec.assumptions.map((assumption, i) => (
                        <li key={i} className='text-sm'>
                          • {assumption}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        ),
        id: 'specification',
        label: 'Epic Specification',
      },
      {
        ariaLabel: 'Epic timeline and milestones',
        content: !epicSpec ? (
          <Card className='bg-card/50 border-none'>
            <CardContent className='pt-6'>
              <p className='text-muted-foreground text-center text-sm'>
                No timeline data available
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className='space-y-6'>
            <Card className='bg-card/50 border-none'>
              <CardHeader>
                <CardTitle className='flex items-center gap-2 text-base'>
                  <Calendar className='h-4 w-4 text-purple-600' />
                  Timeline Overview
                </CardTitle>
              </CardHeader>
              <CardContent className='space-y-6'>
                <div className='grid grid-cols-2 gap-4'>
                  {epicSpec.start_date && (
                    <div>
                      <p className='text-muted-foreground mb-1 text-xs tracking-wider uppercase'>
                        Start Date
                      </p>
                      <p className='font-medium'>{format(new Date(epicSpec.start_date), 'PPP')}</p>
                    </div>
                  )}
                  {epicSpec.end_date && (
                    <div>
                      <p className='text-muted-foreground mb-1 text-xs tracking-wider uppercase'>
                        End Date
                      </p>
                      <p className='font-medium'>{format(new Date(epicSpec.end_date), 'PPP')}</p>
                    </div>
                  )}
                </div>

                {epicSpec.start_date && epicSpec.end_date && (
                  <>
                    <Separator />
                    <div className='space-y-3'>
                      <div className='flex items-center justify-between text-sm'>
                        <span className='font-medium'>Progress</span>
                        <span className='text-muted-foreground'>
                          {timelineProgress}% of timeline elapsed
                        </span>
                      </div>
                      <Progress value={timelineProgress} className='h-3' />
                    </div>
                  </>
                )}

                {epicSpec.dependencies.length > 0 && (
                  <>
                    <Separator />
                    <div>
                      <p className='text-muted-foreground mb-2 text-xs tracking-wider uppercase'>
                        Dependencies
                      </p>
                      <div className='space-y-2'>
                        {epicSpec.dependencies.map((dep) => (
                          <div
                            key={dep}
                            className='bg-card/50 flex items-center gap-2 rounded-lg border p-2'
                          >
                            <AlertCircle className='h-4 w-4 text-orange-600' />
                            <span className='text-sm font-medium'>{dep}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        ),
        id: 'timeline',
        label: 'Timeline',
      },
      {
        ariaLabel: 'User stories in this epic',
        badge: epicSpec?.user_stories.length ?? 0,
        content: !epicSpec ? (
          <Card className='bg-card/50 border-none'>
            <CardContent className='pt-6'>
              <p className='text-muted-foreground text-center text-sm'>No stories data available</p>
            </CardContent>
          </Card>
        ) : (
          <div className='space-y-6'>
            <Card className='bg-card/50 border-none'>
              <CardHeader>
                <CardTitle className='flex items-center gap-2 text-base'>
                  <BookOpen className='h-4 w-4 text-purple-600' />
                  User Stories ({epicSpec.user_stories.length} / {epicSpec.child_stories_count})
                </CardTitle>
              </CardHeader>
              <CardContent className='space-y-4'>
                {epicSpec.user_stories.length > 0 ? (
                  <div className='space-y-2'>
                    {epicSpec.user_stories.map((storyId) => (
                      <div
                        key={storyId}
                        className='bg-card/50 hover:bg-muted/50 rounded-lg border p-3 transition-colors'
                      >
                        <div className='flex items-center justify-between'>
                          <span className='text-sm font-medium'>{storyId}</span>
                          <Badge variant='outline' className='text-xs'>
                            Story
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className='text-muted-foreground py-8 text-center text-sm'>
                    No user stories linked to this epic yet
                  </p>
                )}
              </CardContent>
            </Card>

            {epicSpec.themes.length > 0 && (
              <Card className='bg-card/50 border-none'>
                <CardHeader>
                  <CardTitle className='text-base'>Themes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className='flex flex-wrap gap-2'>
                    {epicSpec.themes.map((theme) => (
                      <Badge
                        key={theme}
                        variant='secondary'
                        className='bg-purple-500/10 text-purple-600'
                      >
                        {theme}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        ),
        id: 'stories',
        label: 'Stories',
      },
      {
        ariaLabel: 'Epic acceptance criteria',
        badge: epicSpec?.success_criteria.length ?? 0,
        content: !epicSpec ? (
          <Card className='bg-card/50 border-none'>
            <CardContent className='pt-6'>
              <p className='text-muted-foreground text-center text-sm'>
                No acceptance criteria available
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className='space-y-6'>
            {/* Success Criteria */}
            {epicSpec.success_criteria.length > 0 && (
              <Card className='bg-card/50 border-none'>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2 text-base'>
                    <CheckCircle2 className='h-4 w-4 text-green-600' />
                    Success Criteria
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className='space-y-3'>
                    {epicSpec.success_criteria.map((criterion, i) => (
                      <li
                        key={i}
                        className='flex items-start gap-3 rounded-lg border border-green-500/20 bg-green-500/5 p-3'
                      >
                        <CheckCircle2 className='mt-0.5 h-5 w-5 shrink-0 text-green-600' />
                        <span className='text-sm'>{criterion}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Risks */}
            {epicSpec.risks.length > 0 && (
              <Card className='border-none bg-orange-500/5'>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2 text-base'>
                    <AlertTriangle className='h-4 w-4 text-orange-600' />
                    Risks & Mitigation
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className='space-y-4'>
                    {epicSpec.risks.map((risk, i) => (
                      <div key={i} className='space-y-2 rounded-lg border border-orange-500/20 p-4'>
                        <div className='flex items-center justify-between'>
                          <p className='text-sm font-medium'>{risk.description}</p>
                          <Badge
                            variant='outline'
                            className={cn(
                              risk.impact === 'critical' && 'border-red-500/50 text-red-600',
                              risk.impact === 'high' && 'border-orange-500/50 text-orange-600',
                              risk.impact === 'medium' && 'border-yellow-500/50 text-yellow-600',
                              risk.impact === 'low' && 'border-blue-500/50 text-blue-600',
                            )}
                          >
                            {risk.impact}
                          </Badge>
                        </div>
                        <p className='text-muted-foreground text-xs'>
                          <span className='font-semibold'>Mitigation:</span> {risk.mitigation}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Stakeholders */}
            {epicSpec.stakeholders.length > 0 && (
              <Card className='bg-card/50 border-none'>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2 text-base'>
                    <Users className='h-4 w-4 text-purple-600' />
                    Stakeholders
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className='flex flex-wrap gap-2'>
                    {epicSpec.stakeholders.map((stakeholder) => (
                      <Badge key={stakeholder} variant='secondary'>
                        {stakeholder}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        ),
        id: 'acceptance',
        label: 'Acceptance Criteria',
      },
    ];

    return allTabs;
  }, [item, epicSpec, specLoading, statusStyle, timelineProgress, completionPercentage]);

  // Type guard check
  if (!isEpicItem(item)) {
    return (
      <div className='p-6'>
        <Card className='border-yellow-500/50 bg-yellow-500/10'>
          <CardContent className='pt-6'>
            <div className='flex items-center gap-2 text-yellow-700'>
              <AlertTriangle className='h-5 w-5' />
              <p className='font-medium'>This item is not an epic. Expected epic type.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return <BaseDetailView item={item} tabs={tabs} defaultTab='overview' isLoading={false} />;
}

import { useNavigate, useParams } from '@tanstack/react-router';
import { format } from 'date-fns';
import { ArrowLeft, Plus } from 'lucide-react';
import { useEffect, useState } from 'react';

import type { Scenario } from '@tracertm/types';

import { FeatureCard } from '@/components/specifications/bdd/FeatureCard';
import { GherkinViewer } from '@/components/specifications/bdd/GherkinViewer';
import { ScenarioCard } from '@/components/specifications/bdd/ScenarioCard';
import {
  useFeature,
  useFeatureActivities,
  useScenarioActivities,
  useScenarios,
} from '@/hooks/useSpecifications';
import {
  Button,
  Card,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@tracertm/ui';

export function FeatureDetailView() {
  const params = useParams({ strict: false });
  const navigate = useNavigate();
  const featureId = params.featureId ?? '';
  const { data: feature, isLoading } = useFeature(featureId);
  const { data: scenariosData } = useScenarios(featureId);
  const { data: featureActivities } = useFeatureActivities(featureId);
  const scenarios = scenariosData?.scenarios ?? [];
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('');
  const [activityPage, setActivityPage] = useState(1);
  const [activityPageSize, setActivityPageSize] = useState(10);
  const { data: scenarioActivityData } = useScenarioActivities(selectedScenarioId || '', {
    limit: activityPageSize,
    offset: (activityPage - 1) * activityPageSize,
  });
  const scenarioActivities = scenarioActivityData?.activities ?? [];
  const scenarioActivityTotal = scenarioActivityData?.total ?? 0;
  const activityTotalPages = Math.max(1, Math.ceil(scenarioActivityTotal / activityPageSize));

  useEffect(() => {
    if (!selectedScenarioId && scenarios.length > 0) {
      setSelectedScenarioId(scenarios[0]?.id ?? '');
    }
  }, [scenarios, selectedScenarioId]);

  useEffect(() => {
    setActivityPage(1);
  }, []);
  useEffect(() => {
    setActivityPage(1);
  }, []);

  if (isLoading) {
    return (
      <div className='space-y-6 p-6'>
        <div className='bg-muted/40 h-8 w-40 rounded' />
        <div className='bg-muted/30 h-32 rounded-xl' />
        <div className='bg-muted/20 h-64 rounded-xl' />
      </div>
    );
  }

  if (!feature) {
    return (
      <div className='space-y-4 p-6'>
        <Button
          variant='ghost'
          onClick={async () =>
            navigate({
              params: { projectId: params.projectId ?? '' },
              search: { tab: 'features' },
              to: '/projects/$projectId/specifications',
            })
          }
        >
          <ArrowLeft className='mr-2 h-4 w-4' />
          Back to Features
        </Button>
        <Card className='bg-muted/20 text-muted-foreground border-none p-6 text-sm'>
          Feature not found.
        </Card>
      </div>
    );
  }

  return (
    <div className='space-y-6 p-6'>
      <div className='flex items-start justify-between'>
        <div>
          <h1 className='mb-2 text-2xl font-bold'>Feature Details</h1>
          <p className='text-muted-foreground'>Manage feature specifications and scenarios.</p>
        </div>
        <Button>
          <Plus className='mr-2 h-4 w-4' />
          New Scenario
        </Button>
      </div>

      <FeatureCard feature={feature} className='border-l-4 border-l-blue-500' />

      <Card className='bg-card/50 border-none'>
        <div className='text-muted-foreground space-y-3 p-6 text-sm'>
          <h2 className='text-foreground text-base font-semibold'>Activity</h2>
          {featureActivities && featureActivities.length > 0
            ? featureActivities.map((activity) => (
                <div
                  key={activity.id}
                  className='border-border/50 flex items-center justify-between border-b pb-2 last:border-0'
                >
                  <div>
                    <div className='text-foreground font-medium'>{activity.activityType}</div>
                    <div className='text-muted-foreground text-xs'>
                      {activity.description ?? 'Feature updated'}
                    </div>
                  </div>
                  <div className='text-muted-foreground text-xs'>
                    {activity.createdAt
                      ? format(new Date(activity.createdAt), 'MMM d, yyyy HH:mm')
                      : '—'}
                  </div>
                </div>
              ))
            : [
                feature.createdAt
                  ? {
                      date: feature.createdAt,
                      detail: `Feature ${feature.featureNumber}`,
                      label: 'Created',
                    }
                  : null,
                feature.updatedAt
                  ? {
                      date: feature.updatedAt,
                      detail: 'Metadata updated',
                      label: 'Updated',
                    }
                  : null,
              ]
                .filter(Boolean)
                .map((entry: any) => (
                  <div
                    key={`${entry.label}-${entry.date}`}
                    className='border-border/50 flex items-center justify-between border-b pb-2 last:border-0'
                  >
                    <div>
                      <div className='text-foreground font-medium'>{entry.label}</div>
                      <div className='text-muted-foreground text-xs'>{entry.detail}</div>
                    </div>
                    <div className='text-muted-foreground text-xs'>
                      {format(new Date(entry.date), 'MMM d, yyyy HH:mm')}
                    </div>
                  </div>
                ))}
          <div className='text-muted-foreground text-xs'>
            Scenarios: {feature.scenarioCount || 0} total · {feature.passedScenarios || 0} passing ·{' '}
            {feature.failedScenarios || 0} failing
          </div>
        </div>
      </Card>

      <div className='space-y-4'>
        <h2 className='text-xl font-semibold'>Scenarios</h2>
        {scenarios.length === 0 ? (
          <Card className='bg-muted/20 text-muted-foreground border-none p-6 text-sm'>
            No scenarios yet.
          </Card>
        ) : (
          <Tabs defaultValue='scenarios' className='w-full'>
            <TabsList className='w-full justify-start'>
              <TabsTrigger value='scenarios'>Scenarios</TabsTrigger>
              <TabsTrigger value='activity'>Scenario Activity</TabsTrigger>
            </TabsList>

            <TabsContent value='scenarios' className='mt-4'>
              <div className='grid gap-4'>
                {scenarios.map((scenario: Scenario) => (
                  <div key={scenario.id} className='grid grid-cols-1 gap-4 md:grid-cols-2'>
                    <ScenarioCard scenario={scenario} />
                    <div className='space-y-2'>
                      <GherkinViewer content={scenario.gherkinText} height='150px' />
                      <Button
                        variant='ghost'
                        size='sm'
                        onClick={async () =>
                          navigate({
                            params: {
                              featureId: params.featureId ?? '',
                              projectId: params.projectId ?? '',
                              scenarioId: scenario.id,
                            },
                            to: '/projects/$projectId/features/$featureId/scenarios/$scenarioId',
                          })
                        }
                      >
                        Open Scenario
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </TabsContent>

            <TabsContent value='activity' className='mt-4'>
              <div className='space-y-3'>
                <Select
                  value={selectedScenarioId}
                  onValueChange={(value) => {
                    setSelectedScenarioId(value);
                  }}
                >
                  <SelectTrigger className='w-[320px]'>
                    <SelectValue placeholder='Select a scenario' />
                  </SelectTrigger>
                  <SelectContent>
                    {scenarios.map((scenario) => (
                      <SelectItem key={scenario.id} value={scenario.id}>
                        {scenario.scenarioNumber} · {scenario.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Card className='bg-card/50 border-none p-4'>
                  <div className='text-muted-foreground space-y-3 text-sm'>
                    {scenarioActivities.length > 0 ? (
                      scenarioActivities.map((activity) => (
                        <div
                          key={activity.id}
                          className='border-border/50 flex items-center justify-between border-b pb-2 last:border-0'
                        >
                          <div>
                            <div className='text-foreground font-medium'>
                              {activity.activityType}
                            </div>
                            <div className='text-muted-foreground text-xs'>
                              {activity.description ?? 'Scenario updated'}
                            </div>
                          </div>
                          <div className='text-muted-foreground text-xs'>
                            {activity.createdAt
                              ? format(new Date(activity.createdAt), 'MMM d, yyyy HH:mm')
                              : '—'}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div>No activity yet.</div>
                    )}
                    {scenarioActivityTotal > scenarioActivities.length && (
                      <div className='text-muted-foreground text-xs'>
                        Showing {scenarioActivities.length} of {scenarioActivityTotal} activities.
                      </div>
                    )}
                    {scenarioActivityTotal > activityPageSize && (
                      <div className='text-muted-foreground flex items-center justify-between text-xs'>
                        <button
                          className='border-border/50 rounded border px-2 py-1 disabled:opacity-50'
                          disabled={activityPage === 1}
                          onClick={() => {
                            setActivityPage((p) => Math.max(1, p - 1));
                          }}
                        >
                          Prev
                        </button>
                        <span>
                          Page {activityPage} of {activityTotalPages}
                        </span>
                        <button
                          className='border-border/50 rounded border px-2 py-1 disabled:opacity-50'
                          disabled={activityPage >= activityTotalPages}
                          onClick={() => {
                            setActivityPage((p) => Math.min(activityTotalPages, p + 1));
                          }}
                        >
                          Next
                        </button>
                      </div>
                    )}
                    <div className='text-muted-foreground flex items-center justify-between text-xs'>
                      <button
                        className='border-border/50 rounded border px-2 py-1'
                        onClick={() => {
                          setActivityPage(1);
                          setActivityPageSize(scenarioActivityTotal || 1000);
                        }}
                        disabled={scenarioActivityTotal <= activityPageSize}
                      >
                        Show all
                      </button>
                      <span>or</span>
                      <button
                        className='border-border/50 rounded border px-2 py-1'
                        onClick={() => {
                          setActivityPage(1);
                          setActivityPageSize(10);
                        }}
                        disabled={activityPageSize === 10}
                      >
                        Compact
                      </button>
                    </div>
                    <div className='text-muted-foreground flex items-center gap-2 text-xs'>
                      <label>Rows</label>
                      <select
                        className='border-border/50 rounded border bg-transparent px-2 py-1'
                        value={activityPageSize}
                        onChange={(e) => {
                          setActivityPageSize(Number(e.target.value));
                        }}
                      >
                        <option value={10}>10</option>
                        <option value={20}>20</option>
                        <option value={50}>50</option>
                      </select>
                    </div>
                    {scenarioActivityTotal > activityPageSize && (
                      <div className='mt-3'>
                        <div className='bg-muted/40 h-1.5 overflow-hidden rounded-full' aria-hidden>
                          <div
                            className='bg-primary/70 h-full'
                            style={{
                              width: `${Math.min(100, (activityPage / activityTotalPages) * 100)}%`,
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        )}
      </div>
    </div>
  );
}

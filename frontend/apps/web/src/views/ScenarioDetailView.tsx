/* eslint-disable complexity, func-style, max-lines-per-function, no-magic-numbers, react-perf/jsx-no-new-function-as-prop, react-perf/jsx-no-new-object-as-prop, sort-imports */
import { useNavigate, useParams } from '@tanstack/react-router';
import { format } from 'date-fns';
import { ArrowLeft } from 'lucide-react';
import { useState } from 'react';

import { GherkinViewer } from '@/components/specifications/bdd/GherkinViewer';
import { ScenarioCard } from '@/components/specifications/bdd/ScenarioCard';
import { useScenario, useScenarioActivities } from '@/hooks/useSpecifications';
import { Button, Card } from '@tracertm/ui';

export function ScenarioDetailView() {
  const params = useParams({ strict: false }) as {
    projectId?: string;
    featureId?: string;
    scenarioId?: string;
  };
  const navigate = useNavigate();
  const scenarioId = params.scenarioId || '';
  const { data: scenario, isLoading } = useScenario(scenarioId);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const { data: activityData } = useScenarioActivities(scenarioId, {
    limit: pageSize,
    offset: (page - 1) * pageSize,
  });
  const activities = activityData?.activities ?? [];
  const totalActivities = activityData?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalActivities / pageSize));

  if (isLoading) {
    return (
      <div className='space-y-6 p-6'>
        <div className='bg-muted/40 h-8 w-40 rounded' />
        <div className='bg-muted/30 h-32 rounded-xl' />
        <div className='bg-muted/20 h-64 rounded-xl' />
      </div>
    );
  }

  if (!scenario) {
    return (
      <div className='space-y-4 p-6'>
        <Button
          variant='ghost'
          onClick={() =>
            navigate({
              params: { projectId: params.projectId || '' },
              search: { tab: 'features' },
              to: '/projects/$projectId/specifications',
            })
          }
        >
          <ArrowLeft className='mr-2 h-4 w-4' />
          Back to Features
        </Button>
        <Card className='bg-muted/20 text-muted-foreground border-none p-6 text-sm'>
          Scenario not found.
        </Card>
      </div>
    );
  }

  return (
    <div className='space-y-6 p-6'>
      <Button
        variant='ghost'
        onClick={() =>
          navigate({
            params: {
              featureId: params.featureId || '',
              projectId: params.projectId || '',
            },
            to: '/projects/$projectId/features/$featureId',
          })
        }
      >
        <ArrowLeft className='mr-2 h-4 w-4' />
        Back to Feature
      </Button>

      <ScenarioCard scenario={scenario} />
      <GherkinViewer content={scenario.gherkinText} height='220px' />

      <Card className='bg-card/50 border-none p-6'>
        <h2 className='mb-4 text-base font-semibold'>Scenario Activity</h2>
        <div className='text-muted-foreground space-y-3 text-sm'>
          {activities.length > 0 ? (
            activities.map((activity) => (
              <div
                key={activity.id}
                className='border-border/50 flex items-center justify-between border-b pb-2 last:border-0'
              >
                <div>
                  <div className='text-foreground font-medium'>{activity.activityType}</div>
                  <div className='text-muted-foreground text-xs'>
                    {activity.description || 'Scenario updated'}
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
          {totalActivities > activities.length && (
            <div className='text-muted-foreground text-xs'>
              Showing {activities.length} of {totalActivities} activities.
            </div>
          )}
        </div>
        <div className='text-muted-foreground mt-4 flex items-center justify-between text-xs'>
          <button
            className='border-border/50 rounded border px-2 py-1'
            onClick={() => {
              setPage(1);
              setPageSize(totalActivities || 1000);
            }}
            disabled={totalActivities <= pageSize}
          >
            Show all
          </button>
          <span>or</span>
          <button
            className='border-border/50 rounded border px-2 py-1'
            onClick={() => {
              setPage(1);
              setPageSize(10);
            }}
            disabled={pageSize === 10}
          >
            Compact
          </button>
        </div>
        <div className='text-muted-foreground mt-4 flex items-center gap-2 text-xs'>
          <label>Rows</label>
          <select
            className='border-border/50 rounded border bg-transparent px-2 py-1'
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setPage(1);
            }}
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        </div>
        {totalActivities > pageSize && (
          <div className='text-muted-foreground mt-4 flex items-center justify-between text-xs'>
            <button
              className='border-border/50 rounded border px-2 py-1 disabled:opacity-50'
              disabled={page === 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Prev
            </button>
            <span>
              Page {page} of {totalPages}
            </span>
            <button
              className='border-border/50 rounded border px-2 py-1 disabled:opacity-50'
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              Next
            </button>
          </div>
        )}
        {totalActivities > pageSize && (
          <div className='mt-4'>
            <div className='bg-muted/40 h-1.5 overflow-hidden rounded-full' aria-hidden>
              <div
                className='bg-primary/70 h-full'
                style={{
                  width: `${Math.min(100, (page / totalPages) * 100)}%`,
                }}
              />
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

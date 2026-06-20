import { useNavigate, useParams } from '@tanstack/react-router';
import { format } from 'date-fns';
import { ArrowLeft } from 'lucide-react';
import React, { useCallback, useMemo, useState } from 'react';

import { GherkinViewer } from '@/components/specifications/bdd/GherkinViewer';
import { ScenarioCard } from '@/components/specifications/bdd/ScenarioCard';
import { useScenario, useScenarioActivities } from '@/hooks/useSpecifications';
import { Button, Card } from '@tracertm/ui';

const ROWS_SELECT_ID = 'scenario-activity-rows';

interface ScenarioActivity {
  activityType: string;
  createdAt?: string | null;
  description?: string | null;
  id: string;
}

function ScenarioActivityCard({
  activities,
  page,
  pageSize,
  progressStyle,
  setPage,
  setPageSize,
  totalActivities,
  totalPages,
}: {
  activities: readonly ScenarioActivity[];
  page: number;
  pageSize: number;
  progressStyle: React.CSSProperties;
  setPage: React.Dispatch<React.SetStateAction<number>>;
  setPageSize: React.Dispatch<React.SetStateAction<number>>;
  totalActivities: number;
  totalPages: number;
}): React.JSX.Element {
  const handleShowAll = useCallback((): void => {
    setPage(1);
    setPageSize(totalActivities || 1000);
  }, [setPage, setPageSize, totalActivities]);

  const handleCompact = useCallback((): void => {
    setPage(1);
    setPageSize(10);
  }, [setPage, setPageSize]);

  const handleRowsChange = useCallback(
    (event: React.ChangeEvent<HTMLSelectElement>): void => {
      setPageSize(Number(event.target.value));
      setPage(1);
    },
    [setPage, setPageSize],
  );

  const handlePreviousPage = useCallback((): void => {
    setPage((currentPage) => Math.max(1, currentPage - 1));
  }, [setPage]);

  const handleNextPage = useCallback((): void => {
    setPage((currentPage) => Math.min(totalPages, currentPage + 1));
  }, [setPage, totalPages]);

  return (
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
                  {activity.description ?? 'Scenario updated'}
                </div>
              </div>
              <div className='text-muted-foreground text-xs'>
                {activity.createdAt ? format(new Date(activity.createdAt), 'MMM d, yyyy HH:mm') : '—'}
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
          disabled={totalActivities <= pageSize}
          onClick={handleShowAll}
          type='button'
        >
          Show all
        </button>
        <span>or</span>
        <button
          className='border-border/50 rounded border px-2 py-1'
          disabled={pageSize === 10}
          onClick={handleCompact}
          type='button'
        >
          Compact
        </button>
      </div>
      <div className='text-muted-foreground mt-4 flex items-center gap-2 text-xs'>
        <label htmlFor={ROWS_SELECT_ID}>Rows</label>
        <select
          className='border-border/50 rounded border bg-transparent px-2 py-1'
          id={ROWS_SELECT_ID}
          value={pageSize}
          onChange={handleRowsChange}
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
            onClick={handlePreviousPage}
            type='button'
          >
            Prev
          </button>
          <span>
            Page {page} of {totalPages}
          </span>
          <button
            className='border-border/50 rounded border px-2 py-1 disabled:opacity-50'
            disabled={page >= totalPages}
            onClick={handleNextPage}
            type='button'
          >
            Next
          </button>
        </div>
      )}
      {totalActivities > pageSize && (
        <div className='mt-4'>
          <div className='bg-muted/40 h-1.5 overflow-hidden rounded-full' aria-hidden>
            <div className='bg-primary/70 h-full' style={progressStyle} />
          </div>
        </div>
      )}
    </Card>
  );
}

export function ScenarioDetailView(): React.JSX.Element {
  const params = useParams({ strict: false });
  const navigate = useNavigate();
  const scenarioId = params.scenarioId ?? '';
  const { data: scenario, isLoading } = useScenario(scenarioId);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const { data: activityData } = useScenarioActivities(scenarioId, {
    limit: pageSize,
    offset: (page - 1) * pageSize,
  });
  const activities = useMemo(
    () => activityData?.activities ?? [],
    [activityData?.activities],
  );
  const totalActivities = activityData?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalActivities / pageSize));
  const progressStyle = useMemo<React.CSSProperties>(
    () => ({
      width: `${Math.min(100, (page / totalPages) * 100)}%`,
    }),
    [page, totalPages],
  );

  const handleBackToSpecifications = useCallback(async (): Promise<void> => {
    await navigate({
      params: { projectId: params.projectId ?? '' },
      search: { tab: 'features' },
      to: '/projects/$projectId/specifications',
    });
  }, [navigate, params.projectId]);

  const handleBackToFeature = useCallback(async (): Promise<void> => {
    await navigate({
      params: {
        featureId: params.featureId ?? '',
        projectId: params.projectId ?? '',
      },
      to: '/projects/$projectId/features/$featureId',
    });
  }, [navigate, params.featureId, params.projectId]);

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
        <Button variant='ghost' onClick={handleBackToSpecifications} type='button'>
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
      <Button variant='ghost' onClick={handleBackToFeature} type='button'>
        <ArrowLeft className='mr-2 h-4 w-4' />
        Back to Feature
      </Button>

      <ScenarioCard scenario={scenario} />
      <GherkinViewer content={scenario.gherkinText} height='220px' />

      <ScenarioActivityCard
        activities={activities as readonly ScenarioActivity[]}
        page={page}
        pageSize={pageSize}
        progressStyle={progressStyle}
        setPage={setPage}
        setPageSize={setPageSize}
        totalActivities={totalActivities}
        totalPages={totalPages}
      />
    </div>
  );
}

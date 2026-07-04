import { useState } from 'react';

import type { WorkflowRun, WorkflowSchedule } from '@tracertm/types';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';
import {
  useBootstrapWorkflowSchedules,
  useDeleteWorkflowSchedule,
  useWorkflowRuns,
  useWorkflowSchedules,
} from '@/hooks/useWorkflows';

interface WorkflowRunsViewProps {
  projectId: string;
}

export function WorkflowRunsView({ projectId }: WorkflowRunsViewProps) {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const { data: runsData, isLoading: runsLoading } = useWorkflowRuns(
    projectId,
    statusFilter || undefined,
  );
  const { data: schedulesData, isLoading: schedulesLoading } = useWorkflowSchedules(projectId);
  const bootstrapSchedules = useBootstrapWorkflowSchedules();
  const deleteSchedule = useDeleteWorkflowSchedule();

  const runs = (runsData as { runs?: WorkflowRun[] })?.runs ?? [];
  const schedules = (schedulesData as { schedules?: WorkflowSchedule[] })?.schedules ?? [];

  return (
    <div className='space-y-6 p-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-2xl font-bold text-gray-900 dark:text-white'>Workflow Runs</h1>
          <p className='text-gray-600 dark:text-gray-400'>
            History for Temporal workflows and schedules.
          </p>
        </div>
        <div className='flex items-center gap-3'>
          <button
            type='button'
            onClick={() => {
              bootstrapSchedules.mutate(projectId);
            }}
            disabled={bootstrapSchedules.isPending}
            className='rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-60'
          >
            Bootstrap schedules
          </button>
        </div>
      </div>

      <div className='rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800'>
        <div className='mb-4 flex items-center justify-between'>
          <h2 className='text-lg font-semibold'>Schedules</h2>
          {bootstrapSchedules.data != null ? (
            <span className='text-xs text-green-600'>
              Created {(bootstrapSchedules.data as { created?: unknown[] }).created?.length ?? 0}
            </span>
          ) : null}
        </div>
        {schedulesLoading ? (
          <div className='flex justify-center py-6'>
            <LoadingSpinner size='sm' text='Loading schedules...' />
          </div>
        ) : schedules.length === 0 ? (
          <div className='text-sm text-gray-500'>No schedules configured for this project.</div>
        ) : (
          <div className='space-y-2'>
            {schedules.map((schedule: WorkflowSchedule) => (
              <ScheduleRow
                key={String(schedule.id ?? schedule.cronName)}
                schedule={schedule}
                projectId={projectId}
                onDelete={deleteSchedule.mutate}
                isDeleting={deleteSchedule.isPending}
              />
            ))}
          </div>
        )}
      </div>

      <div className='rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800'>
        <div className='mb-4 flex items-center justify-between'>
          <h2 className='text-lg font-semibold'>Recent Runs</h2>
          <select
            className='rounded-md border bg-white px-3 py-1 text-sm dark:bg-gray-900'
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
            }}
          >
            <option value=''>All statuses</option>
            <option value='queued'>Queued</option>
            <option value='running'>Running</option>
            <option value='completed'>Completed</option>
            <option value='failed'>Failed</option>
          </select>
        </div>
        {runsLoading ? (
          <div className='flex justify-center py-6'>
            <LoadingSpinner size='sm' text='Loading runs...' />
          </div>
        ) : runs.length === 0 ? (
          <div className='text-sm text-gray-500'>No workflow runs yet.</div>
        ) : (
          <div className='space-y-2'>
            {runs.map((run: WorkflowRun) => (
              <RunRow key={run.id} run={run} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function RunRow({ run }: { run: WorkflowRun }) {
  return (
    <div className='flex items-center justify-between rounded bg-gray-50 p-3 dark:bg-gray-900'>
      <div>
        <div className='text-sm font-medium'>{run.workflowName}</div>
        <div className='text-xs text-gray-500'>
          {run.graphId ? `Graph ${run.graphId.slice(0, 8)}…` : 'Project-level'}
          {run.externalRunId ? ` • ${run.externalRunId}` : ''}
        </div>
      </div>
      <div className='text-right'>
        <span
          className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${
            run.status === 'completed'
              ? 'bg-green-100 text-green-700'
              : run.status === 'failed'
                ? 'bg-red-100 text-red-700'
                : run.status === 'running'
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-200 text-gray-600'
          }`}
        >
          {run.status}
        </span>
        <div className='mt-1 text-xs text-gray-400'>
          {run.startedAt ? new Date(run.startedAt).toLocaleString() : '-'}
        </div>
      </div>
    </div>
  );
}

function ScheduleRow({
  schedule,
  projectId,
  onDelete,
  isDeleting,
}: {
  schedule: WorkflowSchedule;
  projectId: string;
  onDelete: (input: { projectId: string; cronId: string }) => void;
  isDeleting: boolean;
}) {
  const cronId = String(schedule.id ?? '');
  return (
    <div className='flex items-center justify-between rounded bg-gray-50 p-3 dark:bg-gray-900'>
      <div>
        <div className='text-sm font-medium'>
          {schedule.workflowName ?? 'workflow'} • {schedule.cronName ?? 'cron'}
        </div>
        <div className='text-xs text-gray-500'>{schedule.expression ?? ''}</div>
      </div>
      <div>
        <button
          type='button'
          onClick={() => {
            onDelete({ cronId, projectId });
          }}
          disabled={!cronId || isDeleting}
          className='rounded bg-red-100 px-3 py-1 text-xs text-red-700 hover:bg-red-200 disabled:opacity-60'
        >
          Delete
        </button>
      </div>
    </div>
  );
}

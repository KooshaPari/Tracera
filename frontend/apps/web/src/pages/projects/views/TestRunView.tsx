import { BarChart3, CheckCircle, Filter, Play, Plus, Search, XCircle } from 'lucide-react';
import { useState } from 'react';

import type { TestRun, TestRunStatus, TestRunType } from '@tracertm/types';

import { useTestRunStats, useTestRuns } from '../../../hooks/useTestRuns';

const statusColors: Record<TestRunStatus, string> = {
  blocked: 'bg-yellow-100 text-yellow-700',
  cancelled: 'bg-gray-200 text-gray-600',
  failed: 'bg-red-100 text-red-700',
  passed: 'bg-green-100 text-green-700',
  pending: 'bg-gray-100 text-gray-700',
  running: 'bg-blue-100 text-blue-700',
};

const statusLabels: Record<TestRunStatus, string> = {
  blocked: 'Blocked',
  cancelled: 'Cancelled',
  failed: 'Failed',
  passed: 'Passed',
  pending: 'Pending',
  running: 'Running',
};

const typeLabels: Record<TestRunType, string> = {
  automated: 'Automated',
  ci_cd: 'CI/CD',
  manual: 'Manual',
  scheduled: 'Scheduled',
};

interface TestRunViewProps {
  projectId: string;
}

export function TestRunView({ projectId }: TestRunViewProps) {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState<TestRunStatus | ''>('');
  const [typeFilter, setTypeFilter] = useState<TestRunType | ''>('');
  const [searchQuery, setSearchQuery] = useState('');

  const filters = {
    projectId,
    ...(statusFilter && { status: statusFilter }),
    ...(typeFilter && { runType: typeFilter }),
  };
  const { data, isLoading, error } = useTestRuns(filters);

  const { data: stats } = useTestRunStats(projectId);

  const testRuns = data?.testRuns ?? [];
  const filteredRuns = testRuns.filter((r) =>
    r.name.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleCreateSuccess = () => {
    setShowCreateModal(false);
  };

  if (error) {
    return (
      <div className='rounded-lg border border-red-200 bg-red-50 p-4 text-red-700'>
        Error loading test runs: {error.message}
      </div>
    );
  }

  return (
    <div className='space-y-6'>
      {/* Header */}
      <div className='flex items-center justify-between'>
        <div>
          <h3 className='text-lg font-semibold'>Test Runs</h3>
          <p className='text-muted-foreground text-sm'>Execute and track test suite runs</p>
        </div>
        <button
          onClick={() => {
            setShowCreateModal(true);
          }}
          className='bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2 rounded-lg px-4 py-2 text-sm'
        >
          <Plus className='h-4 w-4' /> New Run
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <Play className='h-4 w-4 text-blue-500' />
              Total Runs
            </div>
            <div className='mt-2 text-2xl font-bold'>{stats.totalRuns || 0}</div>
          </div>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <CheckCircle className='h-4 w-4 text-green-500' />
              Passed
            </div>
            <div className='mt-2 text-2xl font-bold'>{stats.byStatus?.['passed'] ?? 0}</div>
          </div>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <XCircle className='h-4 w-4 text-red-500' />
              Failed
            </div>
            <div className='mt-2 text-2xl font-bold'>{stats.byStatus?.['failed'] ?? 0}</div>
          </div>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <BarChart3 className='h-4 w-4 text-purple-500' />
              Avg Pass Rate
            </div>
            <div className='mt-2 text-2xl font-bold'>
              {stats.averagePassRate !== undefined ? `${stats.averagePassRate.toFixed(1)}%` : '—'}
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className='flex flex-wrap items-center gap-4'>
        <div className='relative min-w-[200px] flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <input
            type='text'
            placeholder='Search runs...'
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
            }}
            className='bg-background w-full rounded-lg border py-2 pr-4 pl-10'
          />
        </div>
        <div className='flex items-center gap-2'>
          <Filter className='text-muted-foreground h-4 w-4' />
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as TestRunStatus | '');
            }}
            className='bg-background rounded-lg border px-3 py-2'
          >
            <option value=''>All Statuses</option>
            <option value='pending'>Pending</option>
            <option value='running'>Running</option>
            <option value='passed'>Passed</option>
            <option value='failed'>Failed</option>
            <option value='blocked'>Blocked</option>
            <option value='cancelled'>Cancelled</option>
          </select>
          <select
            value={typeFilter}
            onChange={(e) => {
              setTypeFilter(e.target.value as TestRunType | '');
            }}
            className='bg-background rounded-lg border px-3 py-2'
          >
            <option value=''>All Types</option>
            <option value='manual'>Manual</option>
            <option value='automated'>Automated</option>
            <option value='ci_cd'>CI/CD</option>
            <option value='scheduled'>Scheduled</option>
          </select>
        </div>
      </div>

      {/* Test Runs List */}
      {isLoading ? (
        <div className='flex items-center justify-center py-12'>
          <div className='border-primary h-8 w-8 animate-spin rounded-full border-4 border-t-transparent' />
        </div>
      ) : filteredRuns.length === 0 ? (
        <div className='rounded-lg border border-dashed p-12 text-center'>
          <Play className='text-muted-foreground mx-auto h-12 w-12' />
          <h3 className='mt-4 text-lg font-semibold'>No test runs found</h3>
          <p className='text-muted-foreground mt-2'>
            {searchQuery || statusFilter || typeFilter
              ? 'Try adjusting your filters'
              : 'Create a new test run to get started'}
          </p>
          {!searchQuery && !statusFilter && !typeFilter && (
            <button
              onClick={() => {
                setShowCreateModal(true);
              }}
              className='bg-primary text-primary-foreground mt-4 rounded-lg px-4 py-2 text-sm'
            >
              New Run
            </button>
          )}
        </div>
      ) : (
        <div className='rounded-lg border'>
          <div className='overflow-x-auto'>
            <table className='w-full'>
              <thead>
                <tr className='bg-muted/50 border-b'>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Run</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Status</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Type</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Results</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Pass Rate</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Environment</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Started</th>
                </tr>
              </thead>
              <tbody>
                {filteredRuns.map((run) => (
                  <TestRunRow key={run.id} run={run} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Modal - placeholder */}
      {showCreateModal && (
        <div className='fixed inset-0 z-50 flex items-center justify-center bg-black/50'>
          <div
            className='bg-background w-full max-w-lg rounded-lg p-6 shadow-lg'
            role='dialog'
            aria-modal='true'
            aria-labelledby='create-test-run-title'
          >
            <div className='mb-4 flex items-center justify-between'>
              <h2 id='create-test-run-title' className='text-lg font-semibold'>
                Create Test Run
              </h2>
              <button
                type='button'
                onClick={() => {
                  setShowCreateModal(false);
                }}
                aria-label='Close dialog'
                className='hover:bg-accent rounded-lg p-1'
              >
                ✕
              </button>
            </div>
            <div className='space-y-3'>
              <div>
                <label className='text-xs font-semibold uppercase'>Run Name</label>
                <input
                  type='text'
                  placeholder='e.g. Regression Tests - Build 123'
                  className='bg-muted/50 mt-1 w-full rounded-lg border px-3 py-2 text-sm'
                  defaultValue='New Test Run'
                />
              </div>
              <div>
                <label className='text-xs font-semibold uppercase'>Test Suite</label>
                <select className='bg-muted/50 mt-1 w-full rounded-lg border px-3 py-2 text-sm'>
                  <option>Select a test suite...</option>
                  <option>Unit Tests</option>
                  <option>Integration Tests</option>
                  <option>E2E Tests</option>
                </select>
              </div>
              <div>
                <label className='text-xs font-semibold uppercase'>Status</label>
                <select className='bg-muted/50 mt-1 w-full rounded-lg border px-3 py-2 text-sm'>
                  <option>Pending</option>
                  <option>Running</option>
                  <option>Passed</option>
                  <option>Failed</option>
                  <option>Quarantined</option>
                </select>
              </div>
            </div>
            <div className='mt-6 flex justify-end gap-2'>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                }}
                className='rounded-lg border px-4 py-2 text-sm'
              >
                Cancel
              </button>
              <button
                onClick={handleCreateSuccess}
                className='bg-primary text-primary-foreground rounded-lg px-4 py-2 text-sm'
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function TestRunRow({ run }: { run: TestRun }) {
  const startedDate = run.startedAt ? new Date(run.startedAt).toLocaleString() : '—';

  return (
    <tr className='hover:bg-muted/30 border-b'>
      <td className='px-4 py-3'>
        <div>
          <span className='text-muted-foreground text-xs'>{run.runNumber}</span>
          <div className='font-medium'>{run.name}</div>
          {run.branch && (
            <span className='text-muted-foreground text-xs'>
              {run.branch}
              {run.commitSha && ` (${run.commitSha.slice(0, 7)})`}
            </span>
          )}
        </div>
      </td>
      <td className='px-4 py-3'>
        <span
          className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
            statusColors[run.status]
          }`}
        >
          {statusLabels[run.status]}
        </span>
      </td>
      <td className='px-4 py-3'>
        <span className='text-sm'>{typeLabels[run.runType]}</span>
      </td>
      <td className='px-4 py-3'>
        <div className='flex items-center gap-2 text-xs'>
          <span className='text-green-600'>{run.passedCount}✓</span>
          <span className='text-red-600'>{run.failedCount}✗</span>
          {run.skippedCount > 0 && <span className='text-gray-500'>{run.skippedCount}⊘</span>}
          <span className='text-muted-foreground'>/ {run.totalTests}</span>
        </div>
      </td>
      <td className='px-4 py-3'>
        {run.passRate !== undefined && run.passRate !== null ? (
          <div className='flex items-center gap-2'>
            <div className='h-2 w-16 rounded-full bg-gray-200'>
              <div
                className={`h-2 rounded-full ${
                  run.passRate >= 90
                    ? 'bg-green-500'
                    : run.passRate >= 70
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                }`}
                style={{ width: `${run.passRate}%` }}
              />
            </div>
            <span className='text-xs font-medium'>{run.passRate.toFixed(1)}%</span>
          </div>
        ) : (
          <span className='text-muted-foreground'>—</span>
        )}
      </td>
      <td className='px-4 py-3'>
        <span className='text-sm'>{run.environment ?? '—'}</span>
      </td>
      <td className='text-muted-foreground px-4 py-3 text-sm'>{startedDate}</td>
    </tr>
  );
}

export default TestRunView;

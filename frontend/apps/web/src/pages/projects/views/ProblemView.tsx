import { AlertTriangle, CheckCircle, Clock, Filter, Plus, Search } from 'lucide-react';
import { useState } from 'react';

import type { ImpactLevel, Problem, ProblemStatus } from '@tracertm/types';

import { CreateProblemForm } from '../../../components/forms/CreateProblemForm';
import { useProblemStats, useProblems } from '../../../hooks/useProblems';

const statusColors: Record<ProblemStatus, string> = {
  awaiting_fix: 'bg-blue-100 text-blue-700',
  closed: 'bg-green-100 text-green-700',
  in_investigation: 'bg-yellow-100 text-yellow-700',
  known_error: 'bg-purple-100 text-purple-700',
  open: 'bg-red-100 text-red-700',
  pending_workaround: 'bg-orange-100 text-orange-700',
};

const impactColors: Record<ImpactLevel, string> = {
  critical: 'bg-red-500 text-white',
  high: 'bg-orange-500 text-white',
  low: 'bg-gray-300 text-gray-700',
  medium: 'bg-yellow-500 text-black',
};

const statusLabels: Record<ProblemStatus, string> = {
  awaiting_fix: 'Awaiting Fix',
  closed: 'Closed',
  in_investigation: 'Investigating',
  known_error: 'Known Error',
  open: 'Open',
  pending_workaround: 'Pending Workaround',
};

interface ProblemViewProps {
  projectId: string;
}

export const ProblemView = ({ projectId }: ProblemViewProps) => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState<ProblemStatus | ''>('');
  const [priorityFilter, setPriorityFilter] = useState<ImpactLevel | ''>('');
  const [searchQuery, setSearchQuery] = useState('');

  const filters = {
    projectId,
    ...(statusFilter && { status: statusFilter }),
    ...(priorityFilter && { priority: priorityFilter }),
  };
  const { data, isLoading, error } = useProblems(filters);

  const { data: stats } = useProblemStats(projectId);

  const problems = data?.problems ?? [];
  const filteredProblems = problems.filter((p) =>
    p.title.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleCreateSuccess = () => {
    setShowCreateModal(false);
  };

  const handleStatusFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setStatusFilter(e.target.value as ProblemStatus | '');
  };

  const handlePriorityFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setPriorityFilter(e.target.value as ImpactLevel | '');
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  if (error) {
    return (
      <div className='rounded-lg border border-red-200 bg-red-50 p-4 text-red-700'>
        Error loading problems: {error.message}
      </div>
    );
  }

  return (
    <div className='space-y-6'>
      {/* Header */}
      <div className='flex items-center justify-between'>
        <div>
          <h3 className='text-lg font-semibold'>Problem Management</h3>
          <p className='text-muted-foreground text-sm'>
            Track and resolve problems with root cause analysis
          </p>
        </div>
        <button
          onClick={() => {
            setShowCreateModal(true);
          }}
          className='bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2 rounded-lg px-4 py-2 text-sm'
        >
          <Plus className='h-4 w-4' /> Report Problem
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <AlertTriangle className='h-4 w-4 text-red-500' />
              Open Problems
            </div>
            <div className='mt-2 text-2xl font-bold'>
              {(stats.byStatus?.['open'] ?? 0) + (stats.byStatus?.['in_investigation'] ?? 0)}
            </div>
          </div>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <Clock className='h-4 w-4 text-yellow-500' />
              Known Errors
            </div>
            <div className='mt-2 text-2xl font-bold'>{stats.byStatus?.['known_error'] ?? 0}</div>
          </div>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <CheckCircle className='h-4 w-4 text-green-500' />
              Resolved
            </div>
            <div className='mt-2 text-2xl font-bold'>{stats.byStatus?.['closed'] ?? 0}</div>
          </div>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <AlertTriangle className='h-4 w-4 text-orange-500' />
              Critical
            </div>
            <div className='mt-2 text-2xl font-bold'>{stats.byPriority?.['critical'] ?? 0}</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className='flex flex-wrap items-center gap-4'>
        <div className='relative min-w-[200px] flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <input
            type='text'
            placeholder='Search problems...'
            value={searchQuery}
            onChange={handleSearchChange}
            className='bg-background w-full rounded-lg border py-2 pr-4 pl-10'
          />
        </div>
        <div className='flex items-center gap-2'>
          <Filter className='text-muted-foreground h-4 w-4' />
          <select
            value={statusFilter}
            onChange={handleStatusFilterChange}
            className='bg-background rounded-lg border px-3 py-2'
          >
            <option value=''>All Statuses</option>
            <option value='open'>Open</option>
            <option value='in_investigation'>Investigating</option>
            <option value='pending_workaround'>Pending Workaround</option>
            <option value='known_error'>Known Error</option>
            <option value='awaiting_fix'>Awaiting Fix</option>
            <option value='closed'>Closed</option>
          </select>
          <select
            value={priorityFilter}
            onChange={handlePriorityFilterChange}
            className='bg-background rounded-lg border px-3 py-2'
          >
            <option value=''>All Priorities</option>
            <option value='critical'>Critical</option>
            <option value='high'>High</option>
            <option value='medium'>Medium</option>
            <option value='low'>Low</option>
          </select>
        </div>
      </div>

      {/* Problems List */}
      {isLoading ? (
        <div className='flex items-center justify-center py-12'>
          <div className='border-primary h-8 w-8 animate-spin rounded-full border-4 border-t-transparent' />
        </div>
      ) : filteredProblems.length === 0 ? (
        <div className='rounded-lg border border-dashed p-12 text-center'>
          <AlertTriangle className='text-muted-foreground mx-auto h-12 w-12' />
          <h3 className='mt-4 text-lg font-semibold'>No problems found</h3>
          <p className='text-muted-foreground mt-2'>
            {searchQuery || statusFilter || priorityFilter
              ? 'Try adjusting your filters'
              : 'Report a new problem to get started'}
          </p>
          {!searchQuery && !statusFilter && !priorityFilter && (
            <button
              onClick={() => {
                setShowCreateModal(true);
              }}
              className='bg-primary text-primary-foreground mt-4 rounded-lg px-4 py-2 text-sm'
            >
              Report Problem
            </button>
          )}
        </div>
      ) : (
        <div className='rounded-lg border'>
          <div className='overflow-x-auto'>
            <table className='w-full'>
              <thead>
                <tr className='bg-muted/50 border-b'>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Problem</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Status</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Priority</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Impact</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Assigned</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>RCA</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Created</th>
                </tr>
              </thead>
              <tbody>
                {filteredProblems.map((problem) => (
                  <ProblemRow key={problem.id} problem={problem} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateProblemForm
          projectId={projectId}
          onCancel={() => {
            setShowCreateModal(false);
          }}
          onSuccess={handleCreateSuccess}
        />
      )}
    </div>
  );
};

function ProblemRow({ problem }: { problem: Problem }) {
  const createdDate = problem.createdAt ? new Date(problem.createdAt).toLocaleDateString() : '—';

  return (
    <tr className='hover:bg-muted/30 border-b'>
      <td className='px-4 py-3'>
        <div>
          <span className='text-muted-foreground text-xs'>{problem.problemNumber}</span>
          <div className='font-medium'>{problem.title}</div>
          {problem.category && (
            <span className='text-muted-foreground text-xs'>{problem.category}</span>
          )}
        </div>
      </td>
      <td className='px-4 py-3'>
        <span
          className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
            statusColors[problem.status]
          }`}
        >
          {statusLabels[problem.status]}
        </span>
      </td>
      <td className='px-4 py-3'>
        <span
          className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${
            impactColors[problem.priority]
          }`}
        >
          {problem.priority}
        </span>
      </td>
      <td className='px-4 py-3'>
        <span
          className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${
            impactColors[problem.impactLevel]
          }`}
        >
          {problem.impactLevel}
        </span>
      </td>
      <td className='px-4 py-3'>
        <span className='text-sm'>{problem.assignedTo ?? '—'}</span>
      </td>
      <td className='px-4 py-3'>
        {problem.rootCauseIdentified ? (
          <span className='text-green-600'>✓ Identified</span>
        ) : problem.workaroundAvailable ? (
          <span className='text-yellow-600'>Workaround</span>
        ) : (
          <span className='text-muted-foreground'>—</span>
        )}
      </td>
      <td className='text-muted-foreground px-4 py-3 text-sm'>{createdDate}</td>
    </tr>
  );
}

export default ProblemView;

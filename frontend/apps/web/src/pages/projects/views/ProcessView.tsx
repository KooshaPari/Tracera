import { Archive, Filter, Play, Plus, Search, Workflow } from 'lucide-react';
import { useState } from 'react';

import type { Process, ProcessCategory, ProcessStatus } from '@tracertm/types';

import { CreateProcessForm } from '../../../components/forms/CreateProcessForm';
import { useProcessStats, useProcesses } from '../../../hooks/useProcesses';

const statusColors: Record<ProcessStatus, string> = {
  active: 'bg-green-100 text-green-700',
  archived: 'bg-gray-200 text-gray-500',
  deprecated: 'bg-yellow-100 text-yellow-700',
  draft: 'bg-gray-100 text-gray-700',
  retired: 'bg-orange-100 text-orange-700',
};

const statusLabels: Record<ProcessStatus, string> = {
  active: 'Active',
  archived: 'Archived',
  deprecated: 'Deprecated',
  draft: 'Draft',
  retired: 'Retired',
};

const categoryLabels: Record<ProcessCategory, string> = {
  compliance: 'Compliance',
  development: 'Development',
  integration: 'Integration',
  management: 'Management',
  operational: 'Operational',
  other: 'Other',
  support: 'Support',
};

interface ProcessViewProps {
  projectId: string;
}

export function ProcessView({ projectId }: ProcessViewProps) {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState<ProcessStatus | ''>('');
  const [categoryFilter, setCategoryFilter] = useState<ProcessCategory | ''>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeOnly, setActiveOnly] = useState(false);

  const filters = {
    projectId,
    ...(statusFilter && { status: statusFilter }),
    ...(categoryFilter && { category: categoryFilter }),
    activeOnly,
  };
  const { data, isLoading, error } = useProcesses(filters);

  const { data: stats } = useProcessStats(projectId);

  const processes = data?.processes ?? [];
  const filteredProcesses = processes.filter((p) =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleCreateSuccess = () => {
    setShowCreateModal(false);
  };

  if (error) {
    return (
      <div className='rounded-lg border border-red-200 bg-red-50 p-4 text-red-700'>
        Error loading processes: {error.message}
      </div>
    );
  }

  return (
    <div className='space-y-6'>
      {/* Header */}
      <div className='flex items-center justify-between'>
        <div>
          <h3 className='text-lg font-semibold'>Process Management</h3>
          <p className='text-muted-foreground text-sm'>
            Define and manage workflows and procedures
          </p>
        </div>
        <button
          onClick={() => {
            setShowCreateModal(true);
          }}
          className='bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2 rounded-lg px-4 py-2 text-sm'
        >
          <Plus className='h-4 w-4' /> Create Process
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <Workflow className='h-4 w-4 text-blue-500' />
              Total Processes
            </div>
            <div className='mt-2 text-2xl font-bold'>{stats.total || 0}</div>
          </div>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <Play className='h-4 w-4 text-green-500' />
              Active
            </div>
            <div className='mt-2 text-2xl font-bold'>{stats.byStatus?.['active'] ?? 0}</div>
          </div>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <Workflow className='h-4 w-4 text-gray-500' />
              Draft
            </div>
            <div className='mt-2 text-2xl font-bold'>{stats.byStatus?.['draft'] ?? 0}</div>
          </div>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <Archive className='h-4 w-4 text-yellow-500' />
              Deprecated
            </div>
            <div className='mt-2 text-2xl font-bold'>{stats.byStatus?.['deprecated'] ?? 0}</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className='flex flex-wrap items-center gap-4'>
        <div className='relative min-w-[200px] flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <input
            type='text'
            placeholder='Search processes...'
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
              setStatusFilter(e.target.value as ProcessStatus | '');
            }}
            className='bg-background rounded-lg border px-3 py-2'
          >
            <option value=''>All Statuses</option>
            <option value='draft'>Draft</option>
            <option value='active'>Active</option>
            <option value='deprecated'>Deprecated</option>
            <option value='retired'>Retired</option>
            <option value='archived'>Archived</option>
          </select>
          <select
            value={categoryFilter}
            onChange={(e) => {
              setCategoryFilter(e.target.value as ProcessCategory | '');
            }}
            className='bg-background rounded-lg border px-3 py-2'
          >
            <option value=''>All Categories</option>
            {Object.entries(categoryLabels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <label className='flex items-center gap-2 text-sm'>
            <input
              type='checkbox'
              checked={activeOnly}
              onChange={(e) => {
                setActiveOnly(e.target.checked);
              }}
              className='rounded'
            />
            Active only
          </label>
        </div>
      </div>

      {/* Processes Grid */}
      {isLoading ? (
        <div className='flex items-center justify-center py-12'>
          <div className='border-primary h-8 w-8 animate-spin rounded-full border-4 border-t-transparent' />
        </div>
      ) : filteredProcesses.length === 0 ? (
        <div className='rounded-lg border border-dashed p-12 text-center'>
          <Workflow className='text-muted-foreground mx-auto h-12 w-12' />
          <h3 className='mt-4 text-lg font-semibold'>No processes found</h3>
          <p className='text-muted-foreground mt-2'>
            {searchQuery || statusFilter || categoryFilter
              ? 'Try adjusting your filters'
              : 'Create a new process to get started'}
          </p>
          {!searchQuery && !statusFilter && !categoryFilter && (
            <button
              onClick={() => {
                setShowCreateModal(true);
              }}
              className='bg-primary text-primary-foreground mt-4 rounded-lg px-4 py-2 text-sm'
            >
              Create Process
            </button>
          )}
        </div>
      ) : (
        <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-3'>
          {filteredProcesses.map((process) => (
            <ProcessCard key={process.id} process={process} />
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateProcessForm
          projectId={projectId}
          onCancel={() => {
            setShowCreateModal(false);
          }}
          onSuccess={handleCreateSuccess}
        />
      )}
    </div>
  );
}

function ProcessCard({ process }: { process: Process }) {
  const stageCount = process.stages?.length ?? 0;
  const swimlaneCount = process.swimlanes?.length ?? 0;

  return (
    <div className='bg-card rounded-lg border p-4 transition-shadow hover:shadow-md'>
      <div className='flex items-start justify-between'>
        <div className='flex-1'>
          <span className='text-muted-foreground text-xs'>{process.processNumber}</span>
          <h4 className='font-semibold'>{process.name}</h4>
        </div>
        <span
          className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
            statusColors[process.status]
          }`}
        >
          {statusLabels[process.status]}
        </span>
      </div>

      {process.description && (
        <p className='text-muted-foreground mt-2 line-clamp-2 text-sm'>{process.description}</p>
      )}

      <div className='text-muted-foreground mt-4 flex items-center gap-4 text-sm'>
        {process.category && (
          <span className='bg-muted rounded px-2 py-0.5 text-xs'>
            {categoryLabels[process.category] || process.category}
          </span>
        )}
        {stageCount > 0 && <span>{stageCount} stages</span>}
        {swimlaneCount > 0 && <span>{swimlaneCount} swimlanes</span>}
      </div>

      <div className='text-muted-foreground mt-4 flex items-center justify-between text-xs'>
        <span>v{process.versionNumber}</span>
        {process.isActiveVersion && (
          <span className='rounded bg-green-100 px-2 py-0.5 text-green-700'>Active Version</span>
        )}
        {process.owner && <span>Owner: {process.owner}</span>}
      </div>

      {process.expectedDurationHours && (
        <div className='text-muted-foreground mt-2 text-xs'>
          Expected duration: {process.expectedDurationHours}h
          {process.slaHours && ` (SLA: ${process.slaHours}h)`}
        </div>
      )}
    </div>
  );
}

export default ProcessView;

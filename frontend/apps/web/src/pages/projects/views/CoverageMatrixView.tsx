import { AlertTriangle, CheckCircle, Filter, Grid, Percent, Search, XCircle } from 'lucide-react';
import { useState } from 'react';

import type { TraceabilityMatrixItem } from '@tracertm/types';

import { useCoverageGaps, useTraceabilityMatrix } from '../../../hooks/useCoverage';

const statusColors: Record<string, string> = {
  failed: 'bg-red-100 text-red-700',
  not_tested: 'bg-gray-100 text-gray-700',
  partial: 'bg-yellow-100 text-yellow-700',
  passed: 'bg-green-100 text-green-700',
  pending: 'bg-blue-100 text-blue-700',
};

const statusLabels: Record<string, string> = {
  failed: 'Failed',
  not_tested: 'Not Tested',
  partial: 'Partial',
  passed: 'Passed',
  pending: 'Pending',
};

interface CoverageMatrixViewProps {
  projectId: string;
}

export function CoverageMatrixView({ projectId }: CoverageMatrixViewProps) {
  const [viewFilter, setViewFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showGapsOnly, setShowGapsOnly] = useState(false);

  const {
    data: matrix,
    isLoading: matrixLoading,
    error: matrixError,
  } = useTraceabilityMatrix(projectId, viewFilter || undefined);
  const { data: gaps } = useCoverageGaps(projectId, viewFilter || undefined);

  const items = showGapsOnly
    ? (matrix?.matrix ?? []).filter((item) => !item.isCovered)
    : (matrix?.matrix ?? []);

  const filteredItems = items.filter((item) =>
    item.requirementTitle.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  if (matrixError) {
    return (
      <div className='rounded-lg border border-red-200 bg-red-50 p-4 text-red-700'>
        Error loading coverage matrix: {matrixError.message}
      </div>
    );
  }

  return (
    <div className='space-y-6'>
      {/* Header */}
      <div className='flex items-center justify-between'>
        <div>
          <h3 className='text-lg font-semibold'>Traceability Matrix</h3>
          <p className='text-muted-foreground text-sm'>Track test coverage for requirements</p>
        </div>
      </div>

      {/* Stats Cards */}
      {matrix && (
        <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <Grid className='h-4 w-4 text-blue-500' />
              Total Requirements
            </div>
            <div className='mt-2 text-2xl font-bold'>{matrix.totalRequirements}</div>
          </div>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <CheckCircle className='h-4 w-4 text-green-500' />
              Covered
            </div>
            <div className='mt-2 text-2xl font-bold'>{matrix.coveredRequirements}</div>
          </div>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <XCircle className='h-4 w-4 text-red-500' />
              Uncovered
            </div>
            <div className='mt-2 text-2xl font-bold'>{matrix.uncoveredRequirements}</div>
          </div>
          <div className='bg-card rounded-lg border p-4'>
            <div className='text-muted-foreground flex items-center gap-2 text-sm'>
              <Percent className='h-4 w-4 text-purple-500' />
              Coverage
            </div>
            <div className='mt-2 text-2xl font-bold'>{matrix.coveragePercentage.toFixed(1)}%</div>
          </div>
        </div>
      )}

      {/* Coverage Progress */}
      {matrix && (
        <div className='bg-card rounded-lg border p-4'>
          <div className='mb-2 flex justify-between text-sm'>
            <span className='font-medium'>Overall Coverage Progress</span>
            <span className='text-muted-foreground'>
              {matrix.coveredRequirements} / {matrix.totalRequirements} requirements
            </span>
          </div>
          <div className='h-4 w-full rounded-full bg-gray-200'>
            <div
              className={`h-4 rounded-full transition-all ${
                matrix.coveragePercentage >= 80
                  ? 'bg-green-500'
                  : matrix.coveragePercentage >= 50
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
              }`}
              style={{ width: `${matrix.coveragePercentage}%` }}
            />
          </div>
        </div>
      )}

      {/* Filters */}
      <div className='flex flex-wrap items-center gap-4'>
        <div className='relative min-w-[200px] flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <input
            type='text'
            placeholder='Search requirements...'
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
            value={viewFilter}
            onChange={(e) => {
              setViewFilter(e.target.value);
            }}
            className='bg-background rounded-lg border px-3 py-2'
          >
            <option value=''>All Views</option>
            <option value='FEATURE'>Features</option>
            <option value='CODE'>Code</option>
            <option value='TEST'>Tests</option>
            <option value='API'>API</option>
            <option value='DATABASE'>Database</option>
          </select>
          <label className='flex cursor-pointer items-center gap-2'>
            <input
              type='checkbox'
              checked={showGapsOnly}
              onChange={(e) => {
                setShowGapsOnly(e.target.checked);
              }}
              className='h-4 w-4 rounded border-gray-300'
            />
            <span className='text-sm'>Show gaps only</span>
          </label>
        </div>
      </div>

      {/* Matrix Table */}
      {matrixLoading ? (
        <div className='flex items-center justify-center py-12'>
          <div className='border-primary h-8 w-8 animate-spin rounded-full border-4 border-t-transparent' />
        </div>
      ) : filteredItems.length === 0 ? (
        <div className='rounded-lg border border-dashed p-12 text-center'>
          <Grid className='text-muted-foreground mx-auto h-12 w-12' />
          <h3 className='mt-4 text-lg font-semibold'>
            {showGapsOnly ? 'No coverage gaps found' : 'No requirements found'}
          </h3>
          <p className='text-muted-foreground mt-2'>
            {searchQuery || viewFilter
              ? 'Try adjusting your filters'
              : showGapsOnly
                ? 'All requirements have test coverage!'
                : 'Add requirements to see the coverage matrix'}
          </p>
        </div>
      ) : (
        <div className='rounded-lg border'>
          <div className='overflow-x-auto'>
            <table className='w-full'>
              <thead>
                <tr className='bg-muted/50 border-b'>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Requirement</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>View</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Status</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Covered</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Test Cases</th>
                  <th className='px-4 py-3 text-left text-sm font-medium'>Test Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item) => (
                  <MatrixRow key={item.requirementId} item={item} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Coverage Gaps Summary */}
      {gaps && gaps.gaps.length > 0 && (
        <div className='rounded-lg border bg-yellow-50 p-4'>
          <div className='mb-3 flex items-center gap-2'>
            <AlertTriangle className='h-5 w-5 text-yellow-600' />
            <h4 className='font-semibold text-yellow-800'>
              Coverage Gaps ({gaps.uncoveredCount} uncovered requirements)
            </h4>
          </div>
          <div className='grid gap-2 sm:grid-cols-2 lg:grid-cols-3'>
            {gaps.gaps.slice(0, 6).map((gap) => (
              <div
                key={gap.requirementId}
                className='rounded-lg border border-yellow-200 bg-white p-2 text-sm'
              >
                <div className='truncate font-medium'>{gap.requirementTitle}</div>
                <div className='text-muted-foreground flex items-center gap-2 text-xs'>
                  <span>{gap.requirementView}</span>
                  {gap.priority && (
                    <span
                      className={`rounded px-1.5 py-0.5 ${
                        gap.priority === 'critical'
                          ? 'bg-red-100 text-red-700'
                          : gap.priority === 'high'
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {gap.priority}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
          {gaps.gaps.length > 6 && (
            <p className='mt-2 text-sm text-yellow-700'>... and {gaps.gaps.length - 6} more</p>
          )}
        </div>
      )}
    </div>
  );
}

function MatrixRow({ item }: { item: TraceabilityMatrixItem }) {
  return (
    <tr className='hover:bg-muted/30 border-b'>
      <td className='px-4 py-3'>
        <div className='font-medium'>{item.requirementTitle}</div>
      </td>
      <td className='px-4 py-3'>
        <span className='text-muted-foreground text-sm'>{item.requirementView}</span>
      </td>
      <td className='px-4 py-3'>
        <span className='text-sm'>{item.requirementStatus}</span>
      </td>
      <td className='px-4 py-3'>
        {item.isCovered ? (
          <span className='inline-flex items-center gap-1 text-green-600'>
            <CheckCircle className='h-4 w-4' /> Yes
          </span>
        ) : (
          <span className='inline-flex items-center gap-1 text-red-600'>
            <XCircle className='h-4 w-4' /> No
          </span>
        )}
      </td>
      <td className='px-4 py-3'>
        <span className='text-sm font-medium'>{item.testCount}</span>
      </td>
      <td className='px-4 py-3'>
        <span
          className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
            statusColors[item.overallStatus] ?? statusColors['not_tested']
          }`}
        >
          {statusLabels[item.overallStatus] ?? 'Unknown'}
        </span>
      </td>
    </tr>
  );
}

export default CoverageMatrixView;

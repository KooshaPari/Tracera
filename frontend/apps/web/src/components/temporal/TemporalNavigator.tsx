// Temporal Navigator - Version/branch navigation with 4 view modes
// Provides: timeline, branches, comparison, progress views
// Enables switching between versions and branches

import { ChevronDown, ChevronRight, Clock, GitBranch, GitCompare, TrendingUp } from 'lucide-react';
import { useMemo, useState } from 'react';

import { cn } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';

import { BranchExplorer } from './BranchExplorer';
import { TimelineView } from './TimelineView';

export type ViewMode = 'timeline' | 'branches' | 'comparison' | 'progress';

/**
 * Version snapshot data
 */
export type VersionSnapshot = Record<string, string | number | boolean | object | null | undefined>;

export interface Branch {
  id: string;
  name: string;
  description?: string | undefined;
  parentId?: string | undefined;
  status: 'active' | 'review' | 'merged' | 'abandoned';
  createdAt: Date;
  updatedAt: Date;
  author?: string | undefined;
  mergeRequestCount: number;
}

export interface Version {
  id: string;
  branchId: string;
  tag?: string | undefined;
  title: string;
  description?: string | undefined;
  timestamp: Date;
  author?: string | undefined;
  status: 'draft' | 'published' | 'archived';
  snapshot?: VersionSnapshot | undefined;
}

export interface TemporalNavigatorProps {
  projectId: string;
  currentBranchId: string;
  currentVersionId: string;
  branches: Branch[];
  versions: Version[];
  isLoading?: boolean | undefined;
  onBranchChange: (branchId: string) => void;
  onVersionChange: (versionId: string) => void;
  onBranchCreate?: (() => void) | undefined;
  onMergeRequest?: ((sourceBranchId: string, targetBranchId: string) => void) | undefined;
}

function getStatusColor(
  status: Branch['status'],
): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (status) {
    case 'active': {
      return 'default';
    }
    case 'review': {
      return 'secondary';
    }
    case 'merged': {
      return 'outline';
    }
    case 'abandoned': {
      return 'destructive';
    }
    default: {
      return 'default';
    }
  }
}

function getStatusIcon(status: Branch['status']) {
  switch (status) {
    case 'active': {
      return '●';
    }
    case 'review': {
      return '◐';
    }
    case 'merged': {
      return '✓';
    }
    case 'abandoned': {
      return '✕';
    }
    default: {
      return '○';
    }
  }
}

export function TemporalNavigator({
  projectId,
  currentBranchId,
  currentVersionId,
  branches,
  versions,
  onBranchChange,
  onVersionChange,
  onBranchCreate,
  onMergeRequest,
}: TemporalNavigatorProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('timeline');
  const [isExpanded, setIsExpanded] = useState(false);

  const currentBranch = useMemo(
    () => branches.find((b) => b.id === currentBranchId),
    [branches, currentBranchId],
  );

  const currentVersion = useMemo(
    () => versions.find((v) => v.id === currentVersionId),
    [versions, currentVersionId],
  );

  const branchVersions = useMemo(
    () => versions.filter((v) => v.branchId === currentBranchId),
    [versions, currentBranchId],
  );

  return (
    <div className='flex flex-col border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950'>
      {/* Header with controls */}
      <div className='flex items-center justify-between gap-2 px-4 py-3'>
        <div className='flex flex-1 items-center gap-2'>
          <GitBranch className='h-4 w-4 text-gray-600 dark:text-gray-400' />
          <Select value={currentBranchId} onValueChange={onBranchChange}>
            <SelectTrigger className='w-40'>
              <SelectValue placeholder='Select branch' />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {branches.map((branch) => (
                  <SelectItem key={branch.id} value={branch.id}>
                    <div className='flex items-center gap-2'>
                      <span>{getStatusIcon(branch.status)}</span>
                      <span>{branch.name}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>

          {currentBranch && (
            <Badge variant={getStatusColor(currentBranch.status)}>{currentBranch.status}</Badge>
          )}
        </div>

        {/* View mode toggle buttons */}
        <div className='flex items-center gap-1 rounded-lg bg-gray-100 p-1 dark:bg-gray-800'>
          {[
            { icon: Clock, id: 'timeline' as ViewMode, label: 'Timeline' },
            { icon: GitBranch, id: 'branches' as ViewMode, label: 'Branches' },
            {
              icon: GitCompare,
              id: 'comparison' as ViewMode,
              label: 'Compare',
            },
            { icon: TrendingUp, id: 'progress' as ViewMode, label: 'Progress' },
          ].map(({ id, icon: Icon, label }) => (
            <Button
              key={id}
              variant={viewMode === id ? 'default' : 'ghost'}
              size='sm'
              title={label}
              onClick={() => {
                setViewMode(id);
              }}
              className='h-8 w-8 p-0'
            >
              <Icon className='h-4 w-4' />
            </Button>
          ))}
        </div>

        {/* Actions */}
        <div className='flex items-center gap-2'>
          {onBranchCreate && (
            <Button size='sm' variant='outline' onClick={onBranchCreate} className='gap-2'>
              <span>+</span> Branch
            </Button>
          )}

          <Button
            size='sm'
            variant='ghost'
            onClick={() => {
              setIsExpanded(!isExpanded);
            }}
            className={cn('transition-transform', isExpanded && 'rotate-180')}
          >
            <ChevronDown className='h-4 w-4' />
          </Button>
        </div>
      </div>

      {/* Current selection info */}
      {currentVersion && (
        <div className='border-b border-gray-200 bg-gray-50 px-4 py-2 text-sm dark:border-gray-800 dark:bg-gray-900'>
          <div className='flex items-center justify-between'>
            <div className='space-y-1'>
              <div className='text-gray-600 dark:text-gray-400'>
                Version: <span className='font-medium'>{currentVersion.title}</span>
                {currentVersion.tag && (
                  <Badge variant='outline' className='ml-2 text-xs'>
                    {currentVersion.tag}
                  </Badge>
                )}
              </div>
              <div className='text-xs text-gray-500 dark:text-gray-500'>
                {currentVersion.timestamp.toLocaleString()} by {currentVersion.author ?? 'unknown'}
              </div>
            </div>
            <ChevronRight className='h-4 w-4 text-gray-400' />
          </div>
        </div>
      )}

      {/* Expanded content area */}
      {isExpanded && (
        <div className='border-t border-gray-200 dark:border-gray-800'>
          {viewMode === 'timeline' && (
            <TimelineView
              versions={branchVersions}
              currentVersionId={currentVersionId}
              onVersionChange={onVersionChange}
            />
          )}

          {viewMode === 'branches' && (
            <BranchExplorer
              projectId={projectId}
              branches={branches}
              currentBranchId={currentBranchId}
              onBranchChange={onBranchChange}
              onMergeRequest={onMergeRequest}
              onBranchCreate={onBranchCreate}
            />
          )}

          {viewMode === 'comparison' && (
            <ComparisonView currentBranchId={currentBranchId} branches={branches} />
          )}

          {viewMode === 'progress' && (
            <ProgressView branches={branches} versions={branchVersions} />
          )}
        </div>
      )}
    </div>
  );
}

// Comparison View Component
interface ComparisonViewProps {
  currentBranchId: string;
  branches: Branch[];
}

function ComparisonView({ currentBranchId, branches }: ComparisonViewProps) {
  const [compareBranchId, setCompareBranchId] = useState<string | null>(
    branches.find((b) => b.id !== currentBranchId)?.id ?? null,
  );

  return (
    <div className='space-y-4 p-4'>
      <div className='grid grid-cols-2 gap-4'>
        <div>
          <label className='mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300'>
            Left Branch
          </label>
          <Select value={currentBranchId} disabled>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
          </Select>
        </div>

        <div>
          <label className='mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300'>
            Right Branch
          </label>
          <Select value={compareBranchId ?? ''} onValueChange={setCompareBranchId}>
            <SelectTrigger>
              <SelectValue placeholder='Select branch to compare' />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {branches
                  .filter((b) => b.id !== currentBranchId)
                  .map((branch) => (
                    <SelectItem key={branch.id} value={branch.id}>
                      {branch.name}
                    </SelectItem>
                  ))}
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>
      </div>

      {compareBranchId && (
        <div className='rounded-lg bg-gray-50 p-4 text-sm text-gray-600 dark:bg-gray-900 dark:text-gray-400'>
          <p>
            Comparison between <strong>{currentBranchId}</strong> and{' '}
            <strong>{compareBranchId}</strong> will show:
          </p>
          <ul className='mt-2 list-inside list-disc space-y-1'>
            <li>Version differences</li>
            <li>Item changes</li>
            <li>Divergence point</li>
            <li>Merge compatibility</li>
          </ul>
        </div>
      )}
    </div>
  );
}

// Progress View Component
interface ProgressViewProps {
  branches: Branch[];
  versions: Version[];
}

function ProgressView({ branches, versions }: ProgressViewProps) {
  const totalVersions = versions.length;
  const publishedVersions = versions.filter((v) => v.status === 'published').length;
  const draftVersions = versions.filter((v) => v.status === 'draft').length;
  const progress = totalVersions > 0 ? Math.round((publishedVersions / totalVersions) * 100) : 0;

  return (
    <div className='space-y-4 p-4'>
      <div className='space-y-3'>
        <div>
          <div className='mb-2 flex items-center justify-between'>
            <span className='text-sm font-medium text-gray-700 dark:text-gray-300'>
              Version Progress
            </span>
            <span className='text-sm text-gray-600 dark:text-gray-400'>{progress}%</span>
          </div>
          <div className='h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700'>
            <div className='h-full bg-green-500 transition-all' style={{ width: `${progress}%` }} />
          </div>
        </div>

        <div className='grid grid-cols-3 gap-2 text-xs'>
          <div className='rounded bg-blue-50 p-2 dark:bg-blue-900/20'>
            <div className='font-semibold text-blue-900 dark:text-blue-300'>{totalVersions}</div>
            <div className='text-blue-700 dark:text-blue-400'>Total</div>
          </div>

          <div className='rounded bg-green-50 p-2 dark:bg-green-900/20'>
            <div className='font-semibold text-green-900 dark:text-green-300'>
              {publishedVersions}
            </div>
            <div className='text-green-700 dark:text-green-400'>Published</div>
          </div>

          <div className='rounded bg-yellow-50 p-2 dark:bg-yellow-900/20'>
            <div className='font-semibold text-yellow-900 dark:text-yellow-300'>
              {draftVersions}
            </div>
            <div className='text-yellow-700 dark:text-yellow-400'>Draft</div>
          </div>
        </div>
      </div>

      <div>
        <h4 className='mb-2 text-sm font-medium text-gray-700 dark:text-gray-300'>Branch Status</h4>
        <div className='max-h-48 space-y-2 overflow-y-auto'>
          {branches.map((branch) => (
            <div
              key={branch.id}
              className='flex items-center justify-between rounded bg-gray-50 p-2 text-sm dark:bg-gray-900'
            >
              <span className='text-gray-700 dark:text-gray-300'>{branch.name}</span>
              <Badge
                variant={
                  branch.status === 'active'
                    ? 'default'
                    : branch.status === 'merged'
                      ? 'outline'
                      : 'secondary'
                }
                className='text-xs'
              >
                {branch.status}
              </Badge>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

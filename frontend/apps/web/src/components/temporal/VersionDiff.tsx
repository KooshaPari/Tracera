/**
 * VersionDiff - Side-by-side diff visualization of two versions
 *
 * Features:
 * - Visual comparison of added/removed/modified items
 * - Field-level change highlighting
 * - Statistics summary
 * - Filter by change type
 * - Expandable diff details
 */

import type React from 'react';

import {
  ArrowRight,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Code,
  Database,
  FileText,
  Filter,
  Layout,
  Minus,
  Plus,
  RefreshCw,
  Tag,
} from 'lucide-react';
import { useMemo, useState } from 'react';

import type { DiffItem, Version, VersionDiff as VersionDiffType } from '@tracertm/types';

// =============================================================================
// TYPES
// =============================================================================

export interface VersionDiffProps {
  diff: VersionDiffType;
  versionA?: Version | undefined;
  versionB?: Version | undefined;

  // Actions
  onItemClick?: ((itemId: string, side: 'left' | 'right') => void) | undefined;

  // Layout
  className?: string | undefined;
  compact?: boolean | undefined;
}

type ChangeFilter = 'all' | 'added' | 'removed' | 'modified';
type SignificanceFilter = 'all' | 'breaking' | 'major' | 'moderate' | 'minor';

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export function VersionDiff({
  diff,
  versionA,
  versionB,
  onItemClick,
  className = '',
  compact = false,
}: VersionDiffProps) {
  const [changeFilter, setChangeFilter] = useState<ChangeFilter>('all');
  const [significanceFilter, setSignificanceFilter] = useState<SignificanceFilter>('all');
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState<'unified' | 'split'>('unified');

  // Filter items based on current filters
  const filteredItems = useMemo(() => {
    let items: DiffItem[] = [];

    if (changeFilter === 'all' || changeFilter === 'added') {
      items = [...items, ...diff.added];
    }
    if (changeFilter === 'all' || changeFilter === 'removed') {
      items = [...items, ...diff.removed];
    }
    if (changeFilter === 'all' || changeFilter === 'modified') {
      items = [...items, ...diff.modified];
    }

    // Filter by significance
    if (significanceFilter !== 'all') {
      items = items.filter((item) => item.significance === significanceFilter);
    }

    return items;
  }, [diff, changeFilter, significanceFilter]);

  // Toggle item expansion
  const toggleExpanded = (itemId: string) => {
    setExpandedItems((prev) => {
      const next = new Set(prev);
      if (next.has(itemId)) {
        next.delete(itemId);
      } else {
        next.add(itemId);
      }
      return next;
    });
  };

  return (
    <div className={`version-diff ${className}`}>
      {/* Header with version info */}
      <div className='flex items-center justify-between border-b border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-800/50'>
        <div className='flex items-center gap-4'>
          {/* Version A */}
          <div className='flex items-center gap-2'>
            <div className='h-3 w-3 rounded-full bg-red-400' />
            <div>
              <span className='text-sm font-medium'>v{diff.versionANumber}</span>
              {versionA?.tag && (
                <span className='ml-1.5 text-xs text-gray-500'>
                  <Tag className='inline h-3 w-3' /> {versionA.tag}
                </span>
              )}
            </div>
          </div>

          <ArrowRight className='h-4 w-4 text-gray-400' />

          {/* Version B */}
          <div className='flex items-center gap-2'>
            <div className='h-3 w-3 rounded-full bg-green-400' />
            <div>
              <span className='text-sm font-medium'>v{diff.versionBNumber}</span>
              {versionB?.tag && (
                <span className='ml-1.5 text-xs text-gray-500'>
                  <Tag className='inline h-3 w-3' /> {versionB.tag}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className='flex items-center gap-2'>
          {/* View mode toggle */}
          <div className='flex overflow-hidden rounded-md border border-gray-300 dark:border-gray-600'>
            <button
              onClick={() => {
                setViewMode('unified');
              }}
              className={`px-3 py-1 text-xs ${
                viewMode === 'unified'
                  ? 'bg-gray-200 dark:bg-gray-700'
                  : 'bg-white hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700'
              }`}
            >
              Unified
            </button>
            <button
              onClick={() => {
                setViewMode('split');
              }}
              className={`px-3 py-1 text-xs ${
                viewMode === 'split'
                  ? 'bg-gray-200 dark:bg-gray-700'
                  : 'bg-white hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700'
              }`}
            >
              Split
            </button>
          </div>
        </div>
      </div>

      {/* Stats Summary */}
      <DiffStatsSummary stats={diff.stats} />

      {/* Filters */}
      <div className='flex items-center gap-4 border-b border-gray-200 px-4 py-2 dark:border-gray-700'>
        <div className='flex items-center gap-1'>
          <Filter className='h-4 w-4 text-gray-400' />
          <span className='text-xs text-gray-500'>Filter:</span>
        </div>

        {/* Change type filter */}
        <div className='flex gap-1'>
          {(['all', 'added', 'removed', 'modified'] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => {
                setChangeFilter(filter);
              }}
              className={`rounded-md px-2 py-1 text-xs transition-colors ${
                changeFilter === filter
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                  : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
              } `}
            >
              {filter === 'all' && 'All'}
              {filter === 'added' && (
                <span className='flex items-center gap-1'>
                  <Plus className='h-3 w-3' />
                  Added ({diff.stats.addedCount})
                </span>
              )}
              {filter === 'removed' && (
                <span className='flex items-center gap-1'>
                  <Minus className='h-3 w-3' />
                  Removed ({diff.stats.removedCount})
                </span>
              )}
              {filter === 'modified' && (
                <span className='flex items-center gap-1'>
                  <RefreshCw className='h-3 w-3' />
                  Modified ({diff.stats.modifiedCount})
                </span>
              )}
            </button>
          ))}
        </div>

        <div className='h-4 w-px bg-gray-300 dark:bg-gray-600' />

        {/* Significance filter */}
        <select
          value={significanceFilter}
          onChange={(e) => {
            setSignificanceFilter(e.target.value as SignificanceFilter);
          }}
          className='rounded-md border border-gray-300 bg-white px-2 py-1 text-xs dark:border-gray-600 dark:bg-gray-800'
        >
          <option value='all'>All significance</option>
          <option value='breaking'>Breaking only</option>
          <option value='major'>Major+</option>
          <option value='moderate'>Moderate+</option>
          <option value='minor'>Minor+</option>
        </select>
      </div>

      {/* Diff Items */}
      <div className='overflow-auto'>
        {filteredItems.length > 0 ? (
          <div className='divide-y divide-gray-200 dark:divide-gray-700'>
            {filteredItems.map((item) => (
              <DiffItemRow
                key={item.itemId}
                item={item}
                isExpanded={expandedItems.has(item.itemId)}
                onToggleExpand={() => {
                  toggleExpanded(item.itemId);
                }}
                onItemClick={onItemClick}
                compact={compact}
              />
            ))}
          </div>
        ) : (
          <div className='flex flex-col items-center justify-center p-8 text-gray-500'>
            <CheckCircle className='mb-2 h-10 w-10 opacity-50' />
            <p className='text-sm'>No changes match the current filters</p>
          </div>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

interface DiffStatsSummaryProps {
  stats: VersionDiffType['stats'];
}

function DiffStatsSummary({ stats }: DiffStatsSummaryProps) {
  return (
    <div className='flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700'>
      <div className='flex items-center gap-6'>
        <div className='flex items-center gap-2'>
          <Plus className='h-4 w-4 text-green-500' />
          <span className='text-sm'>
            <span className='font-semibold text-green-600 dark:text-green-400'>
              {stats.addedCount}
            </span>{' '}
            added
          </span>
        </div>
        <div className='flex items-center gap-2'>
          <Minus className='h-4 w-4 text-red-500' />
          <span className='text-sm'>
            <span className='font-semibold text-red-600 dark:text-red-400'>
              {stats.removedCount}
            </span>{' '}
            removed
          </span>
        </div>
        <div className='flex items-center gap-2'>
          <RefreshCw className='h-4 w-4 text-yellow-500' />
          <span className='text-sm'>
            <span className='font-semibold text-yellow-600 dark:text-yellow-400'>
              {stats.modifiedCount}
            </span>{' '}
            modified
          </span>
        </div>
      </div>
      <div className='text-sm text-gray-500'>{stats.unchangedCount} unchanged</div>
    </div>
  );
}

interface DiffItemRowProps {
  item: DiffItem;
  isExpanded: boolean;
  onToggleExpand: () => void;
  onItemClick?: ((itemId: string, side: 'left' | 'right') => void) | undefined;
  compact: boolean;
}

function DiffItemRow({ item, isExpanded, onToggleExpand, onItemClick, compact }: DiffItemRowProps) {
  const hasFieldChanges = item.fieldChanges && item.fieldChanges.length > 0;

  const changeTypeConfig = {
    added: {
      bgColor: 'bg-green-50 dark:bg-green-900/10',
      borderColor: 'border-l-green-500',
      icon: Plus,
      iconColor: 'text-green-500',
    },
    modified: {
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/10',
      borderColor: 'border-l-yellow-500',
      icon: RefreshCw,
      iconColor: 'text-yellow-500',
    },
    removed: {
      bgColor: 'bg-red-50 dark:bg-red-900/10',
      borderColor: 'border-l-red-500',
      icon: Minus,
      iconColor: 'text-red-500',
    },
  };

  const config = changeTypeConfig[item.changeType];
  const Icon = config.icon;

  const typeIcon = getTypeIcon(item.type);

  return (
    <div className={`${config.bgColor} border-l-4 ${config.borderColor}`}>
      {/* Main row */}
      <div
        className='flex cursor-pointer items-center gap-3 px-4 py-3 hover:bg-black/5 dark:hover:bg-white/5'
        onClick={() => hasFieldChanges && onToggleExpand()}
        onKeyDown={(e) => {
          if (hasFieldChanges && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            onToggleExpand();
          }
        }}
        role='button'
        tabIndex={hasFieldChanges ? 0 : undefined}
      >
        {/* Expand toggle */}
        {hasFieldChanges ? (
          <button className='p-0.5'>
            {isExpanded ? (
              <ChevronDown className='h-4 w-4 text-gray-400' />
            ) : (
              <ChevronRight className='h-4 w-4 text-gray-400' />
            )}
          </button>
        ) : (
          <div className='w-5' />
        )}

        {/* Change type icon */}
        <Icon className={`h-4 w-4 ${config.iconColor}`} />

        {/* Item type icon */}
        <span className='text-gray-400'>{typeIcon}</span>

        {/* Item info */}
        <div className='min-w-0 flex-1'>
          <div className='flex items-center gap-2'>
            <span className='truncate text-sm font-medium'>{item.title}</span>
            <span className='rounded bg-gray-200 px-1.5 py-0.5 text-xs text-gray-500 dark:bg-gray-700'>
              {item.type}
            </span>
          </div>
          {!compact && item.changeType === 'modified' && item.fieldChanges && (
            <p className='mt-0.5 text-xs text-gray-500'>
              {item.fieldChanges.length} field
              {item.fieldChanges.length !== 1 ? 's' : ''} changed
            </p>
          )}
        </div>

        {/* Significance badge */}
        <SignificanceBadge significance={item.significance} />

        {/* View button */}
        {onItemClick && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onItemClick(item.itemId, item.changeType === 'removed' ? 'left' : 'right');
            }}
            className='rounded px-2 py-1 text-xs text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/30'
          >
            View
          </button>
        )}
      </div>

      {/* Expanded field changes */}
      {isExpanded && hasFieldChanges && (
        <div className='px-4 pb-3 pl-12'>
          <div className='overflow-hidden rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800'>
            <table className='w-full text-sm'>
              <thead className='bg-gray-50 dark:bg-gray-700/50'>
                <tr>
                  <th className='px-3 py-2 text-left text-xs font-medium text-gray-500'>Field</th>
                  <th className='px-3 py-2 text-left text-xs font-medium text-gray-500'>
                    Old Value
                  </th>
                  <th className='px-3 py-2 text-left text-xs font-medium text-gray-500'>
                    New Value
                  </th>
                </tr>
              </thead>
              <tbody className='divide-y divide-gray-200 dark:divide-gray-700'>
                {item.fieldChanges!.map((change, index) => (
                  <tr key={`${change.field}-${index}`}>
                    <td className='px-3 py-2 font-medium text-gray-900 dark:text-gray-100'>
                      {change.field}
                    </td>
                    <td className='bg-red-50 px-3 py-2 text-red-600 dark:bg-red-900/10 dark:text-red-400'>
                      <ValueDisplay value={change.oldValue} />
                    </td>
                    <td className='bg-green-50 px-3 py-2 text-green-600 dark:bg-green-900/10 dark:text-green-400'>
                      <ValueDisplay value={change.newValue} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function SignificanceBadge({ significance }: { significance: DiffItem['significance'] }) {
  const config = {
    breaking: { color: 'red', label: 'Breaking' },
    major: { color: 'orange', label: 'Major' },
    minor: { color: 'gray', label: 'Minor' },
    moderate: { color: 'yellow', label: 'Moderate' },
  };

  const { color, label } = config[significance];

  const colorClasses: Record<string, string> = {
    gray: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400',
    orange: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
    red: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    yellow: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  };

  return <span className={`rounded px-1.5 py-0.5 text-xs ${colorClasses[color]}`}>{label}</span>;
}

function ValueDisplay({ value }: { value: unknown }) {
  if (value === null || value === undefined) {
    return <span className='italic opacity-50'>null</span>;
  }
  if (typeof value === 'boolean') {
    return <span>{value ? 'true' : 'false'}</span>;
  }
  if (typeof value === 'object') {
    return (
      <span className='font-mono text-xs'>
        {JSON.stringify(value, null, 0).slice(0, 50)}
        {JSON.stringify(value).length > 50 ? '...' : ''}
      </span>
    );
  }
  // Primitives only here (object already handled above)
  const s =
    typeof value === 'string'
      ? value
      : typeof value === 'number' ||
          typeof value === 'boolean' ||
          typeof value === 'symbol' ||
          typeof value === 'bigint'
        ? String(value)
        : '';
  return <span>{s}</span>;
}

function getTypeIcon(type: string): React.ReactNode {
  const lowerType = type.toLowerCase();

  if (lowerType.includes('code') || lowerType.includes('function')) {
    return <Code className='h-4 w-4' />;
  }
  if (lowerType.includes('database') || lowerType.includes('schema')) {
    return <Database className='h-4 w-4' />;
  }
  if (lowerType.includes('ui') || lowerType.includes('component') || lowerType.includes('page')) {
    return <Layout className='h-4 w-4' />;
  }
  return <FileText className='h-4 w-4' />;
}

export default VersionDiff;

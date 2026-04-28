/**
 * ItemsTableView with Comprehensive Accessibility (WCAG 2.1 Level AA)
 *
 * Accessibility Features:
 * - ARIA roles: table, rowgroup, row, gridcell, columnheader
 * - Keyboard navigation: Arrow keys, Home/End, Ctrl+Home/End, PageUp/Down
 * - Roving tabindex for efficient focus management
 * - Screen reader announcements for navigation and actions
 * - Proper heading hierarchy and semantic HTML
 * - Color contrast compliance
 * - Focus indicators with sufficient size and contrast
 * - ARIA sort indicators for sortable columns
 */

import { useNavigate, useSearch } from '@tanstack/react-router';
import { useVirtualizer } from '@tanstack/react-virtual';
import {
  AlertCircle,
  ArrowDown,
  ArrowUp,
  CheckCircle2,
  Clock,
  ExternalLink,
  Filter,
  Plus,
  Search,
  Terminal,
  Trash2,
  X,
} from 'lucide-react';
import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { toast } from 'sonner';

import type { ItemStatus, Priority, Project, TypedItem, ViewType } from '@tracertm/types';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { cn } from '@/lib/utils';
import {
  Badge,
  Button,
  Card,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Skeleton,
} from '@tracertm/ui';

import { useCreateItem, useDeleteItem, useItems } from '../hooks/useItems';
import { useProjects } from '../hooks/useProjects';
import { useTableKeyboardNavigation } from '../hooks/useTableKeyboardNavigation';

const DEFAULT_VIEW: ViewType = 'feature';
const DEFAULT_ITEM_TYPE = 'feature';
const DEFAULT_PRIORITY: Priority = 'medium';
const DEFAULT_STATUS: ItemStatus = 'todo';
const ROW_HEIGHT = 68;
const VIRTUAL_OVERSCAN = 10;
const SKELETON_ROWS = 6;
const STATUS_OPTIONS: ItemStatus[] = ['todo', 'in_progress', 'done', 'blocked', 'cancelled'];
const PRIORITY_OPTIONS: Priority[] = ['low', 'medium', 'high', 'critical'];
const TYPE_OPTIONS = ['requirement', 'feature', 'test', 'bug', 'task'];
const EMPTY_ITEMS: TypedItem[] = [];

interface SearchFilters {
  action?: string | undefined;
  project?: string | undefined;
  type?: string | undefined;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function readNonEmptyString(value: unknown): string | undefined {
  if (typeof value !== 'string') {
    return undefined;
  }
  const trimmed = value.trim();
  return trimmed === '' ? undefined : trimmed;
}

function parseSearchFilters(search: unknown): SearchFilters {
  if (!isRecord(search)) {
    return {};
  }
  return {
    action: readNonEmptyString(search['action']),
    project: readNonEmptyString(search['project']),
    type: readNonEmptyString(search['type']),
  };
}

function getTypeValue(type: string | undefined, view: ViewType | undefined): string {
  if (type !== undefined && type.trim() !== '') {
    return type;
  }
  if (view !== undefined) {
    return view;
  }
  return DEFAULT_ITEM_TYPE;
}

function getViewValue(view: ViewType | undefined): ViewType {
  if (view !== undefined) {
    return view;
  }
  return DEFAULT_VIEW;
}

function isItemStatus(value: string): value is ItemStatus {
  return STATUS_OPTIONS.some((statusOption) => statusOption === value);
}

function isPriority(value: string): value is Priority {
  return PRIORITY_OPTIONS.some((priorityOption) => priorityOption === value);
}

function getTitleSortDirection(
  isTitleSorted: boolean,
  sortOrder: 'asc' | 'desc',
): 'ascending' | 'descending' | 'none' {
  if (!isTitleSorted) {
    return 'none';
  }
  return sortOrder === 'asc' ? 'ascending' : 'descending';
}

function getTitleSortLabel(isTitleSorted: boolean, sortOrder: 'asc' | 'desc'): string {
  if (!isTitleSorted) {
    return 'not sorted';
  }
  return `sorted ${sortOrder}`;
}

function getStatusBadge(status: ItemStatus): JSX.Element {
  const config: Record<ItemStatus, { color: string; icon: typeof AlertCircle }> = {
    blocked: {
      color: 'bg-red-500/10 text-red-600 border-red-500/20',
      icon: AlertCircle,
    },
    cancelled: {
      color: 'bg-orange-500/10 text-orange-600 border-orange-500/20',
      icon: X,
    },
    done: {
      color: 'bg-green-500/10 text-green-600 border-green-500/20',
      icon: CheckCircle2,
    },
    in_progress: {
      color: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
      icon: Clock,
    },
    todo: { color: 'bg-muted text-muted-foreground', icon: Terminal },
  };
  const c = config[status];
  return (
    <Badge className={cn('text-[9px] font-black uppercase tracking-tighter gap-1 border', c.color)}>
      <c.icon className='h-2.5 w-2.5' aria-hidden='true' />
      {status.replace('_', ' ')}
    </Badge>
  );
}

function getPriorityDot(priority?: Priority): JSX.Element {
  const colors: Record<Priority, string> = {
    critical: 'bg-red-500',
    high: 'bg-orange-500',
    low: 'bg-green-500',
    medium: 'bg-blue-500',
  };
  const labels: Record<Priority, string> = {
    critical: 'Critical priority',
    high: 'High priority',
    low: 'Low priority',
    medium: 'Medium priority',
  };
  const level = priority ?? 'medium';
  return (
    <div
      className={cn('h-1.5 w-1.5 rounded-full', colors[level])}
      role='img'
      aria-label={labels[level]}
    />
  );
}

// Memoized accessible row component
interface VirtualTableRowProps {
  item: TypedItem;
  rowIndex: number;
  onDelete: (id: string) => void;
  onNavigate: (item: TypedItem) => void;
  isKeyboardFocused: boolean;
}

const VirtualTableRow = memo(
  ({
    item,
    rowIndex,
    onDelete,
    onNavigate,
    isKeyboardFocused,
  }: VirtualTableRowProps): JSX.Element => {
    const handleNavigate = useCallback(() => {
      onNavigate(item);
    }, [item, onNavigate]);

    const handleDelete = useCallback(() => {
      onDelete(item.id);
    }, [item.id, onDelete]);

    const handleKeyDown = useCallback(
      (e: React.KeyboardEvent<HTMLButtonElement>) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleNavigate();
        }
      },
      [handleNavigate],
    );

    return (
      <TableRow
        data-row-index={rowIndex}
        aria-rowindex={rowIndex + 2} // +1 for header, +1 for 1-based indexing
        className={cn(
          'group border-b border-border/30 hover:bg-muted/30 transition-colors',
          isKeyboardFocused && 'ring-2 ring-primary ring-offset-2',
        )}
      >
        <TableCell
          data-col-index='0'
          colIndex={1}
          headerText='Node Identifier'
          className='px-6 py-4'
        >
          <button
            type='button'
            onClick={handleNavigate}
            onKeyDown={handleKeyDown}
            className={cn(
              'block group/link w-full text-left focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded',
            )}
            tabIndex={isKeyboardFocused ? 0 : -1}
            aria-label={`Item ${item.title} (ID: ${item.id.slice(0, 12)})`}
          >
            <div className='group-hover/link:text-primary truncate text-sm font-bold transition-colors'>
              {item.title}
            </div>
            <div className='text-muted-foreground mt-0.5 font-mono text-[10px] uppercase'>
              {item.id.slice(0, 12)}
            </div>
          </button>
        </TableCell>

        <TableCell data-col-index='1' colIndex={2} headerText='Type' className='px-4 py-4'>
          <Badge
            variant='outline'
            className='h-4 px-1.5 text-[8px] font-black tracking-tighter uppercase'
          >
            {item.type}
          </Badge>
        </TableCell>

        <TableCell
          data-col-index='2'
          colIndex={3}
          headerText='Status'
          className='px-4 py-4'
          ariaLabel={`Status: ${item.status.replace('_', ' ')}`}
        >
          {getStatusBadge(item.status)}
        </TableCell>

        <TableCell data-col-index='3' colIndex={4} headerText='Priority' className='px-4 py-4'>
          <div className='flex items-center gap-2'>
            {getPriorityDot(item.priority)}
            <span className='text-muted-foreground text-[10px] font-bold uppercase'>
              {item.priority ?? 'medium'}
            </span>
          </div>
        </TableCell>

        <TableCell
          data-col-index='4'
          colIndex={5}
          headerText='Owner'
          className='px-4 py-4'
          ariaLabel={`Owner: ${item.owner ?? 'Unassigned'}`}
        >
          <div className='flex items-center gap-2'>
            <div
              className='bg-muted flex h-5 w-5 items-center justify-center rounded-full text-[8px] font-black uppercase'
              role='img'
              aria-label={`Avatar for ${item.owner}`}
            >
              {item.owner?.charAt(0) ?? '?'}
            </div>
            <span className='text-muted-foreground text-[10px] font-bold uppercase'>
              {item.owner ?? 'Unassigned'}
            </span>
          </div>
        </TableCell>

        <TableCell
          data-col-index='5'
          colIndex={6}
          headerText='Actions'
          className='px-6 py-4 text-right'
        >
          <div className='flex justify-end gap-1 opacity-0 transition-opacity group-hover:opacity-100'>
            <Button
              type='button'
              variant='ghost'
              size='icon'
              className='focus:ring-primary h-8 w-8 rounded-lg focus:ring-2 focus:ring-offset-2'
              onClick={handleNavigate}
              aria-label={`Open item details for ${item.title}`}
              tabIndex={-1}
            >
              <ExternalLink className='h-3.5 w-3.5' aria-hidden='true' />
            </Button>
            <Button
              type='button'
              variant='ghost'
              size='icon'
              className='text-destructive hover:bg-destructive/10 focus:ring-primary h-8 w-8 rounded-lg focus:ring-2 focus:ring-offset-2'
              onClick={handleDelete}
              aria-label={`Delete item ${item.title}`}
              tabIndex={-1}
            >
              <Trash2 className='h-3.5 w-3.5' aria-hidden='true' />
            </Button>
          </div>
        </TableCell>
      </TableRow>
    );
  },
  (prev, next) =>
    prev.item.id === next.item.id &&
    prev.item.title === next.item.title &&
    prev.item.type === next.item.type &&
    prev.item.status === next.item.status &&
    prev.item.priority === next.item.priority &&
    prev.item.owner === next.item.owner &&
    prev.isKeyboardFocused === next.isKeyboardFocused,
);

VirtualTableRow.displayName = 'VirtualTableRow';

interface ItemsTableViewA11yProps {
  projectId?: string | undefined;
  view?: ViewType | undefined;
  type?: string | undefined;
}

export function ItemsTableViewA11y({
  projectId,
  view,
  type,
}: ItemsTableViewA11yProps = {}): JSX.Element {
  const navigate = useNavigate();
  const searchParams = parseSearchFilters(useSearch({ strict: false }));
  const projectFilter = searchParams.project;
  const typeFilter = searchParams.type;
  const actionParam = searchParams.action;

  const effectiveProjectId = projectId ?? projectFilter;
  const effectiveTypeFilter = type ?? typeFilter;

  const { data: itemsData, isLoading } = useItems({
    projectId: effectiveProjectId,
    view,
  });
  const items = itemsData?.items ?? EMPTY_ITEMS;
  const { data: projects } = useProjects();
  const projectsArray: Project[] = Array.isArray(projects) ? projects : [];
  const deleteItem = useDeleteItem();
  const createItem = useCreateItem();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newType, setNewType] = useState(type ?? DEFAULT_ITEM_TYPE);
  const [newPriority, setNewPriority] = useState<Priority>(DEFAULT_PRIORITY);
  const [newStatus, setNewStatus] = useState<ItemStatus>(DEFAULT_STATUS);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortColumn, setSortColumn] = useState<string>('created');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [keyboardFocusedCell, setKeyboardFocusedCell] = useState<{
    row: number;
    col: number;
  } | null>(null);

  const parentRef = useRef<HTMLDivElement>(null);
  const tableContainerId = 'items-table-a11y';
  const shouldShowProjectFilter = projectId === undefined || projectId.trim() === '';
  const shouldShowTypeFilter = type === undefined || type.trim() === '';
  const normalizedTypeFilter = effectiveTypeFilter === 'all' ? undefined : effectiveTypeFilter;
  const normalizedSearchQuery = searchQuery.trim().toLowerCase();
  const isTitleSorted = sortColumn === 'title';

  const getVirtualRowStyle = useCallback(
    (rowSize: number, rowStart: number): React.CSSProperties => ({
      height: `${rowSize}px`,
      left: 0,
      position: 'absolute',
      top: 0,
      transform: `translateY(${rowStart}px)`,
      width: '100%',
    }),
    [],
  );

  const filteredAndSortedItems = useMemo(() => {
    const filtered = items.filter((item) => {
      const matchesType = normalizedTypeFilter === undefined || item.type === normalizedTypeFilter;
      const matchesQuery =
        item.title.toLowerCase().includes(normalizedSearchQuery) ||
        item.id.toLowerCase().includes(normalizedSearchQuery);
      return matchesType && matchesQuery;
    });

    return filtered.toSorted((a, b) => {
      const dir = sortOrder === 'asc' ? 1 : -1;
      if (sortColumn === 'title') {
        return a.title.localeCompare(b.title) * dir;
      }
      if (sortColumn === 'created') {
        return (new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()) * dir;
      }
      return 0;
    });
  }, [items, normalizedTypeFilter, normalizedSearchQuery, sortColumn, sortOrder]);

  // Keyboard navigation
  const { focusState: _focusState, setFocusState: _setFocusState } = useTableKeyboardNavigation({
    colCount: 6,
    containerId: tableContainerId,
    onNavigate: (rowIndex, colIndex) => {
      setKeyboardFocusedCell({ col: colIndex, row: rowIndex });
    },
    rowCount: filteredAndSortedItems.length,
  });

  useEffect(() => {
    if (actionParam === 'create') {
      setShowCreateModal(true);
    }
  }, [actionParam]);

  const closeCreateModal = useCallback((): void => {
    setShowCreateModal(false);
    if (actionParam !== 'create') {
      return;
    }
    navigate({
      search: ((previousSearch: Record<string, unknown>) => {
        const { action: _, ...rest } = isRecord(previousSearch) ? previousSearch : {};
        return rest;
      }) as never,
    });
  }, [actionParam, navigate]);

  const handleOpenCreateModal = useCallback((): void => {
    setShowCreateModal(true);
  }, []);

  const handleItemNavigate = useCallback(
    (item: TypedItem): void => {
      if (effectiveProjectId === undefined) {
        return;
      }
      const viewSegment = (view ?? item.view).toLowerCase();
      navigate({
        to: `/projects/${effectiveProjectId}/views/${viewSegment}/${item.id}`,
      });
    },
    [effectiveProjectId, navigate, view],
  );

  const handleCreate = useCallback(async (): Promise<void> => {
    if (effectiveProjectId === undefined || effectiveProjectId.trim() === '') {
      toast.error('Select a project before creating a node.');
      return;
    }
    if (newTitle.trim() === '') {
      toast.error('Title is required.');
      return;
    }
    try {
      const resolvedView = getViewValue(view);
      const resolvedType = getTypeValue(newType, view);
      await createItem.mutateAsync({
        priority: newPriority,
        projectId: effectiveProjectId,
        status: newStatus,
        title: newTitle.trim(),
        type: resolvedType,
        view: resolvedView,
      });
      toast.success('Node created');
      setNewTitle('');
      setNewType(type ?? DEFAULT_ITEM_TYPE);
      closeCreateModal();
    } catch {
      toast.error('Failed to create node');
    }
  }, [
    effectiveProjectId,
    newTitle,
    newType,
    newStatus,
    newPriority,
    view,
    type,
    createItem,
    closeCreateModal,
  ]);

  const handleCreateClick = useCallback((): void => {
    void handleCreate();
  }, [handleCreate]);

  const rowVirtualizer = useVirtualizer({
    count: filteredAndSortedItems.length,
    estimateSize: (): number => ROW_HEIGHT,
    getScrollElement: () => parentRef.current,
    overscan: VIRTUAL_OVERSCAN,
  });

  const virtualContainerStyle = useMemo(
    () => ({
      height: `${rowVirtualizer.getTotalSize()}px`,
      position: 'relative' as const,
      width: '100%',
    }),
    [rowVirtualizer],
  );

  const handleDelete = useCallback(
    async (id: string) => {
      try {
        await deleteItem.mutateAsync(id);
        toast.success('Node purged from registry');
        // Announce to screen readers
        announceToScreenReader('Item deleted successfully');
      } catch {
        toast.error('Purge failure');
        announceToScreenReader('Failed to delete item');
      }
    },
    [deleteItem],
  );

  const handleDeleteRow = useCallback(
    (id: string): void => {
      void handleDelete(id);
    },
    [handleDelete],
  );

  const handleSearchQueryChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>): void => {
      setSearchQuery(event.target.value);
    },
    [],
  );

  const handleTitleSortToggle = useCallback((): void => {
    setSortColumn('title');
    setSortOrder((previousSortOrder) => (previousSortOrder === 'asc' ? 'desc' : 'asc'));
  }, []);

  const handleProjectFilterChange = useCallback(
    (value: string): void => {
      navigate({
        search: ((previousSearch: Record<string, unknown>) => {
          const base = isRecord(previousSearch) ? previousSearch : {};
          if (value === 'all') {
            const { project: _, ...rest } = base;
            return rest;
          }
          return { ...base, project: value };
        }) as never,
      });
    },
    [navigate],
  );

  const handleTypeFilterChange = useCallback(
    (value: string): void => {
      navigate({
        search: ((previousSearch: Record<string, unknown>) => {
          const base = isRecord(previousSearch) ? previousSearch : {};
          if (value === 'all') {
            const { type: _, ...rest } = base;
            return rest;
          }
          return { ...base, type: value };
        }) as never,
      });
    },
    [navigate],
  );

  const handleNewTitleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>): void => {
    setNewTitle(event.target.value);
  }, []);

  const handleNewTypeChange = useCallback((event: React.ChangeEvent<HTMLInputElement>): void => {
    setNewType(event.target.value);
  }, []);

  const handleStatusChange = useCallback((value: string): void => {
    if (isItemStatus(value)) {
      setNewStatus(value);
    }
  }, []);

  const handlePriorityChange = useCallback((value: string): void => {
    if (isPriority(value)) {
      setNewPriority(value);
    }
  }, []);

  if (isLoading) {
    return (
      <div className='animate-pulse space-y-8 p-6'>
        <Skeleton className='h-10 w-48' />
        <div className='space-y-4'>
          {Array.from({ length: SKELETON_ROWS }).map((_, skeletonIndex) => (
            <Skeleton key={skeletonIndex} className='h-16 w-full rounded-xl' />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className='animate-in fade-in mx-auto max-w-[1600px] space-y-8 p-6 pb-20 duration-500'>
      {/* Header */}
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-2xl font-black tracking-tight uppercase'>Node Registry</h1>
          <p className='text-muted-foreground text-sm font-medium'>
            Flat-file management of project entities and artifacts. Use arrow keys to navigate the
            table.
          </p>
        </div>
        <div className='flex items-center gap-2'>
          <Button
            type='button'
            size='sm'
            onClick={handleOpenCreateModal}
            className='shadow-primary/20 gap-2 rounded-xl shadow-lg'
            aria-label='Create new node'
          >
            <Plus className='h-4 w-4' aria-hidden='true' /> New Node
          </Button>
        </div>
      </div>

      {/* Filters Bar with ARIA labels */}
      <Card className='bg-muted/30 flex flex-wrap items-center gap-2 rounded-2xl border-none p-2'>
        <div className='relative min-w-[250px] flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <Input
            placeholder='Search identifiers...'
            className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
            value={searchQuery}
            onChange={handleSearchQueryChange}
            aria-label='Search items by title or ID'
          />
        </div>
        <div className='bg-border/50 mx-2 hidden h-6 w-px md:block' />
        {shouldShowProjectFilter && (
          <Select value={projectFilter ?? 'all'} onValueChange={handleProjectFilterChange}>
            <SelectTrigger className='hover:bg-background/50 h-10 w-[180px] border-none bg-transparent transition-colors'>
              <div className='flex items-center gap-2'>
                <Filter className='text-muted-foreground h-3.5 w-3.5' />
                <SelectValue placeholder='All Projects' />
              </div>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='all'>Global Scope</SelectItem>
              {projectsArray.map((project) => (
                <SelectItem key={project.id} value={project.id}>
                  {project.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
        {shouldShowTypeFilter && (
          <Select value={effectiveTypeFilter ?? 'all'} onValueChange={handleTypeFilterChange}>
            <SelectTrigger className='hover:bg-background/50 h-10 w-[140px] border-none bg-transparent transition-colors'>
              <SelectValue placeholder='All Types' />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='all'>Any Type</SelectItem>
              {TYPE_OPTIONS.map((typeOption) => (
                <SelectItem key={typeOption} value={typeOption} className='capitalize'>
                  {typeOption}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </Card>

      {/* Accessible Table with Virtual Scrolling */}
      <Card className='bg-card/50 flex flex-col overflow-hidden rounded-[2rem] border-none shadow-sm'>
        <div
          id={tableContainerId}
          className='flex flex-col'
          role='region'
          aria-label='Items table with keyboard navigation support'
          aria-describedby='table-instructions'
        >
          {/* Instructions for screen readers */}
          <div id='table-instructions' className='sr-only'>
            Use arrow keys to navigate. Home and End keys jump to the first and last columns.
            Ctrl+Home and Ctrl+End jump to the first and last rows. Enter or Space to activate
            items.
          </div>

          {/* Table Header */}
          <div className='custom-scrollbar overflow-x-auto'>
            <Table role='table' ariaLabel='Items table with sortable columns'>
              <TableHeader>
                <TableRow className='border-border/50 border-b hover:bg-transparent'>
                  <TableHead
                    className='bg-card/50 sticky top-0 z-10 h-14 w-[400px] px-6 text-[10px] font-black tracking-widest uppercase'
                    colIndex={1}
                    isSortable
                    sortDirection={getTitleSortDirection(isTitleSorted, sortOrder)}
                  >
                    <button
                      type='button'
                      onClick={handleTitleSortToggle}
                      className='focus:ring-primary flex items-center gap-2 rounded px-2 py-1 focus:ring-2 focus:ring-offset-2 focus:outline-none'
                      aria-label={`Node Identifier, ${getTitleSortLabel(isTitleSorted, sortOrder)}`}
                    >
                      Node Identifier
                      {isTitleSorted &&
                        (sortOrder === 'asc' ? (
                          <ArrowUp className='h-3 w-3' aria-hidden='true' />
                        ) : (
                          <ArrowDown className='h-3 w-3' aria-hidden='true' />
                        ))}
                    </button>
                  </TableHead>
                  <TableHead colIndex={2}>Type</TableHead>
                  <TableHead colIndex={3}>Status</TableHead>
                  <TableHead colIndex={4}>Priority</TableHead>
                  <TableHead colIndex={5}>Owner</TableHead>
                  <TableHead colIndex={6} className='px-6 text-right'>
                    Actions
                  </TableHead>
                </TableRow>
              </TableHeader>
            </Table>
          </div>

          {/* Virtual Scrolling Container */}
          <div
            ref={parentRef}
            className='custom-scrollbar h-[600px] flex-1 overflow-x-hidden overflow-y-auto'
            role='region'
            aria-label='Items table body with virtual scrolling'
          >
            {filteredAndSortedItems.length > 0 ? (
              <div style={virtualContainerStyle}>
                {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                  const item = filteredAndSortedItems[virtualRow.index];
                  if (!item) {
                    return null;
                  }

                  const isFocused = keyboardFocusedCell?.row === virtualRow.index;

                  return (
                    <div
                      key={item.id}
                      style={getVirtualRowStyle(virtualRow.size, virtualRow.start)}
                    >
                      <div className='custom-scrollbar overflow-x-auto'>
                        <Table>
                          <TableBody>
                            <VirtualTableRow
                              item={item}
                              rowIndex={virtualRow.index}
                              onDelete={handleDeleteRow}
                              onNavigate={handleItemNavigate}
                              isKeyboardFocused={isFocused}
                            />
                          </TableBody>
                        </Table>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className='flex h-[600px] items-center justify-center'>
                <div className='text-muted-foreground/30 flex flex-col items-center justify-center'>
                  <Terminal className='mb-4 h-12 w-12 opacity-10' />
                  <p className='text-[10px] font-black tracking-[0.3em] uppercase'>
                    Registry Vacant
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Accessible Create Modal */}
      {showCreateModal && (
        <div className='fixed inset-0 z-50 flex items-center justify-center'>
          <div
            className='fixed inset-0 bg-black/50 backdrop-blur-sm'
            onClick={closeCreateModal}
            role='presentation'
          />
          <div
            className='bg-background relative w-full max-w-lg rounded-xl border p-6 shadow-2xl'
            role='dialog'
            aria-modal='true'
            aria-labelledby='create-modal-title'
          >
            <div className='flex items-center justify-between'>
              <h2 id='create-modal-title' className='text-lg font-semibold'>
                Create Node
              </h2>
              <button
                type='button'
                onClick={closeCreateModal}
                aria-label='Close dialog'
                className='hover:bg-accent focus:ring-primary rounded-lg p-1 focus:ring-2 focus:outline-none'
              >
                <X className='h-5 w-5' aria-hidden='true' />
              </button>
            </div>
            <div className='mt-4 space-y-4'>
              <div>
                <label htmlFor='node-title' className='block text-sm font-medium'>
                  Title
                </label>
                <Input
                  id='node-title'
                  value={newTitle}
                  onChange={handleNewTitleChange}
                  placeholder='Enter node title'
                  className='mt-1'
                  aria-required='true'
                />
              </div>
              <div className='grid gap-4 sm:grid-cols-2'>
                <div>
                  <label htmlFor='node-type' className='block text-sm font-medium'>
                    Type
                  </label>
                  <Input
                    id='node-type'
                    value={newType}
                    onChange={handleNewTypeChange}
                    placeholder='feature, requirement, ui_component...'
                    className='mt-1'
                  />
                </div>
                <div>
                  <label htmlFor='node-status' className='block text-sm font-medium'>
                    Status
                  </label>
                  <Select value={newStatus} onValueChange={handleStatusChange}>
                    <SelectTrigger id='node-status' className='mt-1'>
                      <SelectValue placeholder='Status' />
                    </SelectTrigger>
                    <SelectContent>
                      {STATUS_OPTIONS.map((statusOption) => (
                        <SelectItem key={statusOption} value={statusOption}>
                          {statusOption.replace('_', ' ')}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <label htmlFor='node-priority' className='block text-sm font-medium'>
                  Priority
                </label>
                <Select value={newPriority} onValueChange={handlePriorityChange}>
                  <SelectTrigger id='node-priority' className='mt-1'>
                    <SelectValue placeholder='Priority' />
                  </SelectTrigger>
                  <SelectContent>
                    {PRIORITY_OPTIONS.map((priorityOption) => (
                      <SelectItem key={priorityOption} value={priorityOption}>
                        {priorityOption}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className='flex justify-end gap-2 pt-2'>
                <Button type='button' variant='ghost' onClick={closeCreateModal}>
                  Cancel
                </Button>
                <Button type='button' onClick={handleCreateClick} disabled={createItem.isPending}>
                  {createItem.isPending ? 'Creating...' : 'Create Node'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Screen reader announcements */}
      <div
        id='table-announcements'
        role='status'
        aria-live='polite'
        aria-atomic='true'
        className='sr-only'
      />
    </div>
  );
}

/**
 * Announce messages to screen readers using aria-live regions
 */
function announceToScreenReader(message: string): void {
  const liveRegion = document.querySelector<HTMLElement>('#table-announcements');
  if (liveRegion !== null) {
    liveRegion.textContent = message;
  }
}

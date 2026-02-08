import { useNavigate, useSearch } from '@tanstack/react-router';
import { useVirtualizer } from '@tanstack/react-virtual';
import { Filter, Plus, Search, X } from 'lucide-react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { toast } from 'sonner';

import type { ItemStatus, Priority, Project, TypedItem, ViewType } from '@tracertm/types';

import { ResponsiveCardView } from '@/components/mobile/ResponsiveCardView';
import { EmptyState } from '@/components/ui/empty-state';
import { Table, TableBody } from '@/components/ui/table';
import { useCreateItem, useDeleteItem, useItems } from '@/hooks/useItems';
import { useProjects } from '@/hooks/useProjects';
import { ListLoadingSkeleton, ModalLoadingOverlay } from '@/lib/lazy-loading';
import { cn } from '@/lib/utils';
import { buildCardItems } from '@/views/items-table/card-items';
import {
  ACTION_CREATE,
  DEFAULT_CREATE_LABEL,
  DEFAULT_NEW_LABEL,
  DEFAULT_PRIORITY,
  DEFAULT_STATUS,
  EMPTY_STRING,
  FILTER_ALL,
  KEYBOARD_PAGE_OFFSET,
  LOADING_COMPLETE_DELAY_MS,
  LOADING_OVERLAY_DELAY_MS,
  LOADING_ROW_COUNT,
  MAX_COL_INDEX,
  PRIORITY_VALUES,
  ROW_INDEX_OFFSET,
  SEARCH_INPUT_MIN_WIDTH,
  SEARCH_PARAM_ACTION,
  SEARCH_PARAM_PROJECT,
  SEARCH_PARAM_TYPE,
  STATUS_VALUES,
  TABLE_MAX_INLINE,
  TABLE_MIN_HEIGHT,
  VIRTUAL_OVERSCAN,
  VIRTUAL_ROW_HEIGHT,
  VIEW_TYPE_OPTIONS,
} from '@/views/items-table/constants';
import {
  createViewTypeValue,
  getFilterValue,
  getItemTypeValue,
  getLiveMessage,
  getSearchMessage,
  getSearchValue,
  getSortedItems,
  getViewSegment,
  getViewValue,
  hasValue,
} from '@/views/items-table/formatters';
import { ItemTableRow } from '@/views/items-table/row';
import { TableHeaderRow } from '@/views/items-table/table-header';
import { getViewLabels } from '@/views/items-table/view-labels';
import { VirtualTable } from '@/views/items-table/virtual-table';
import {
  Button,
  Card,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui';

interface ItemsTableViewProps {
  projectId?: string;
  view?: ViewType;
  type?: string;
}

function ItemsTableView({ projectId, view, type }: ItemsTableViewProps = {}): JSX.Element {
  const navigate = useNavigate();
  const searchParams = useSearch({ strict: false }) as Record<string, unknown>;

  const projectFilter = getSearchValue(searchParams, SEARCH_PARAM_PROJECT);
  const typeFilter = getSearchValue(searchParams, SEARCH_PARAM_TYPE);
  const actionParam = getSearchValue(searchParams, SEARCH_PARAM_ACTION);

  let effectiveProjectId: string | undefined;
  if (hasValue(projectId)) {
    effectiveProjectId = projectId;
  } else if (hasValue(projectFilter)) {
    effectiveProjectId = projectFilter;
  }

  let effectiveTypeFilter: string | undefined;
  if (hasValue(type)) {
    effectiveTypeFilter = type;
  } else if (hasValue(typeFilter)) {
    effectiveTypeFilter = typeFilter;
  }

  const { data: itemsData, isLoading } = useItems({
    projectId: effectiveProjectId,
    view,
  });
  const items = itemsData?.items ?? [];
  const { data: projects } = useProjects();
  const projectsArray: Project[] = Array.isArray(projects) ? projects : [];
  const deleteItem = useDeleteItem();
  const createItem = useCreateItem();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTitle, setNewTitle] = useState(EMPTY_STRING);
  const [newDescription, setNewDescription] = useState(EMPTY_STRING);
  const [newType, setNewType] = useState(getItemTypeValue(type, view));
  const [newPriority, setNewPriority] = useState<Priority>(DEFAULT_PRIORITY);
  const [newStatus, setNewStatus] = useState<ItemStatus>(DEFAULT_STATUS);
  const [formError, setFormError] = useState<string | undefined>(undefined);

  const [searchQuery, setSearchQuery] = useState(EMPTY_STRING);
  const [sortColumn, setSortColumn] = useState('created');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [showLoadingState, setShowLoadingState] = useState(false);
  const [liveMessage, setLiveMessage] = useState('Items loaded.');
  const titleInputRef = useRef<HTMLInputElement | undefined>(undefined);
  const modalRef = useRef<HTMLDivElement | undefined>(undefined);
  const hasTabbedInModalRef = useRef(false);

  const parentRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (actionParam === ACTION_CREATE) {
      setShowCreateModal(true);
    }
  }, [actionParam]);

  const closeCreateModal = useCallback((): void => {
    setShowCreateModal(false);
    if (actionParam === ACTION_CREATE) {
      navigate({
        search: (prev) => ({
          ...prev,
          action: undefined,
        }),
      });
    }
  }, [actionParam, navigate]);

  const handleItemNavigate = useCallback(
    (item: TypedItem): void => {
      const projectIdValue = effectiveProjectId;
      if (!projectIdValue) {
        return;
      }
      const viewSegment = getViewSegment(view, item.view);
      navigate({
        to: `/projects/${projectIdValue}/views/${viewSegment}/${item.id}`,
      });
    },
    [navigate, effectiveProjectId, view],
  );

  const handleCreate = useCallback(async (): Promise<void> => {
    if (!effectiveProjectId) {
      toast.error('Select a project before creating a node.');
      setFormError('Select a project before creating a node.');
      return;
    }

    const trimmedTitle = newTitle.trim();
    if (trimmedTitle === EMPTY_STRING) {
      toast.error('Title is required.');
      setFormError('Title is required.');
      return;
    }

    const trimmedDescription = newDescription.trim();
    let descriptionValue: string | undefined;
    if (trimmedDescription !== EMPTY_STRING) {
      descriptionValue = trimmedDescription;
    }
    const resolvedType = getItemTypeValue(newType, view);
    const resolvedView = getViewValue(view);

    try {
      await createItem.mutateAsync({
        description: descriptionValue,
        priority: newPriority,
        projectId: effectiveProjectId,
        status: newStatus,
        title: trimmedTitle,
        type: resolvedType,
        view: resolvedView,
      });
      toast.success('Node created');
      setLiveMessage('Item created.');
      setNewTitle(EMPTY_STRING);
      setNewDescription(EMPTY_STRING);
      setNewType(getItemTypeValue(type, view));
      closeCreateModal();
    } catch {
      toast.error('Failed to create node');
      setFormError('Failed to create node.');
    }
  }, [
    effectiveProjectId,
    newTitle,
    newDescription,
    newType,
    newStatus,
    newPriority,
    view,
    type,
    createItem,
    closeCreateModal,
  ]);

  const handleRefresh = useCallback((): void => {
    setShowLoadingState(true);
    setLiveMessage('Loading items...');
    globalThis.setTimeout(() => {
      setShowLoadingState(false);
      setLiveMessage('Items loaded.');
    }, LOADING_OVERLAY_DELAY_MS);
  }, []);

  const filteredAndSortedItems = useMemo(
    () =>
      getSortedItems(
        items,
        effectiveTypeFilter,
        searchQuery.trim().toLowerCase(),
        sortColumn,
        sortOrder,
      ),
    [items, effectiveTypeFilter, searchQuery, sortColumn, sortOrder],
  );

  const measureElement = useMemo(() => {
    if (globalThis.window === undefined) {
      return undefined;
    }
    const userAgent = globalThis.navigator?.userAgent ?? EMPTY_STRING;
    if (userAgent.includes('Firefox')) {
      return undefined;
    }
    return (element: Element): number => {
      return element.getBoundingClientRect().height;
    };
  }, []);

  const rowVirtualizer = useVirtualizer({
    count: filteredAndSortedItems.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => VIRTUAL_ROW_HEIGHT,
    overscan: VIRTUAL_OVERSCAN,
    measureElement,
  });

  useEffect(() => {
    if (isLoading) {
      return undefined;
    }
    if (filteredAndSortedItems.length === 0) {
      return undefined;
    }
    const timer = globalThis.setTimeout(() => {
      setShowLoadingState(false);
    }, LOADING_COMPLETE_DELAY_MS);
    return () => {
      globalThis.clearTimeout(timer);
    };
  }, [isLoading, filteredAndSortedItems.length]);

  const handleDelete = useCallback(
    async (id: string): Promise<void> => {
      try {
        await deleteItem.mutateAsync(id);
        toast.success('Node purged from registry');
      } catch {
        toast.error('Purge failure');
      }
    },
    [deleteItem],
  );

  const handleSortChange = useCallback(
    (column: string): void => {
      setSortColumn(column);
      setSortOrder((prev) => {
        if (prev === 'asc') {
          return 'desc';
        }
        return 'asc';
      });
      rowVirtualizer.scrollToIndex(0, { align: 'center', behavior: 'auto' });
    },
    [rowVirtualizer],
  );

  const handleCellKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLElement>): void => {
      if (event.target !== event.currentTarget) {
        return;
      }
      const target = event.currentTarget as HTMLElement;
      const rowAttr = target.dataset.rowIndex;
      const colAttr = target.dataset.colIndex;
      if (rowAttr === undefined || colAttr === undefined) {
        return;
      }

      const rowIndex = Number.parseInt(rowAttr, 10);
      const colIndex = Number.parseInt(colAttr, 10);
      const maxRow = Math.max(filteredAndSortedItems.length - ROW_INDEX_OFFSET, 0);
      const maxCol = MAX_COL_INDEX;
      let nextRow = rowIndex;
      let nextCol = colIndex;

      switch (event.key) {
        case 'Enter':
        case ' ': {
          event.preventDefault();
          const item = filteredAndSortedItems[rowIndex];
          if (item) {
            handleItemNavigate(item);
          }
          return;
        }
        case 'ArrowRight': {
          nextCol = Math.min(maxCol, colIndex + ROW_INDEX_OFFSET);
          break;
        }
        case 'ArrowLeft': {
          nextCol = Math.max(0, colIndex - ROW_INDEX_OFFSET);
          break;
        }
        case 'ArrowDown': {
          nextRow = Math.min(maxRow, rowIndex + ROW_INDEX_OFFSET);
          break;
        }
        case 'ArrowUp': {
          nextRow = Math.max(0, rowIndex - ROW_INDEX_OFFSET);
          break;
        }
        case 'Home': {
          nextCol = 0;
          if (event.ctrlKey) {
            nextRow = 0;
          }
          break;
        }
        case 'End': {
          nextCol = maxCol;
          if (event.ctrlKey) {
            nextRow = maxRow;
          }
          break;
        }
        case 'PageDown': {
          nextRow = Math.min(maxRow, rowIndex + KEYBOARD_PAGE_OFFSET);
          break;
        }
        case 'PageUp': {
          nextRow = Math.max(0, rowIndex - KEYBOARD_PAGE_OFFSET);
          break;
        }
        default: {
          return;
        }
      }

      event.preventDefault();
      const selector = `[data-row-index="${nextRow}"][data-col-index="${nextCol}"]`;
      const next = document.querySelector(selector);
      if (next instanceof HTMLElement) {
        next.focus();
      }
    },
    [filteredAndSortedItems, handleItemNavigate],
  );

  useEffect(() => {
    if (!showCreateModal) {
      return undefined;
    }

    hasTabbedInModalRef.current = false;
    const timer = globalThis.setTimeout(() => {
      if (titleInputRef.current) {
        titleInputRef.current.focus();
      }
    }, 0);

    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeCreateModal();
        return;
      }
      if (event.key !== 'Tab') {
        return;
      }
      if (document.activeElement === titleInputRef.current && !hasTabbedInModalRef.current) {
        event.preventDefault();
        hasTabbedInModalRef.current = true;
        return;
      }
      const modal = modalRef.current;
      if (!modal) {
        return;
      }
      const focusable = [
        ...modal.querySelectorAll<HTMLElement>(
          ['button', 'input', 'textarea', 'select', "[tabindex]:not([tabindex='-1'])"].join(','),
        ),
      ].filter((element) => !element.hasAttribute('disabled') && element.tabIndex !== -1);
      if (focusable.length === 0) {
        return;
      }
      const first = focusable[0];
      const last = focusable.at(-1);
      const active = document.activeElement;
      if (!(active instanceof HTMLElement) || !modal.contains(active)) {
        event.preventDefault();
        first.focus();
        if (first === titleInputRef.current) {
          hasTabbedInModalRef.current = true;
        }
        return;
      }
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        if (last) {
          last.focus();
        }
        return;
      }
      if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    globalThis.addEventListener('keydown', handleKeyDown);

    return () => {
      globalThis.clearTimeout(timer);
      globalThis.removeEventListener('keydown', handleKeyDown);
    };
  }, [showCreateModal, closeCreateModal]);

  const labels = useMemo(() => getViewLabels(view), [view]);
  const liveMessageValue = getLiveMessage(liveMessage);

  const emptyStateActions = useMemo(() => {
    const label = labels.newButtonLabel ?? DEFAULT_NEW_LABEL;
    return [
      {
        label,
        onClick: (): void => {
          setShowCreateModal(true);
        },
      },
    ];
  }, [labels.newButtonLabel]);

  const emptyStateNode = useMemo(
    () => (
      <EmptyState
        icon={Filter}
        title={labels.emptyTitle}
        description={labels.emptyDescription}
        actions={emptyStateActions}
        variant='compact'
      />
    ),
    [emptyStateActions, labels.emptyDescription, labels.emptyTitle],
  );

  const loadingOverlay = useMemo(
    () => (
      <ModalLoadingOverlay
        isVisible={showLoadingState}
        message={getSearchMessage(liveMessageValue, labels.title)}
        detail='Refreshing items'
      />
    ),
    [labels.title, liveMessageValue, showLoadingState],
  );

  const cardItems = useMemo(
    () => buildCardItems(filteredAndSortedItems, handleItemNavigate, handleDelete),
    [filteredAndSortedItems, handleItemNavigate, handleDelete],
  );

  const handleSearchChange = useCallback((event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchQuery(event.target.value);
  }, []);

  const handleProjectFilterChange = useCallback(
    (value: string): void => {
      const nextValue = getFilterValue(value);
      navigate({
        search: (prev) => ({
          ...prev,
          project: nextValue,
        }),
      });
    },
    [navigate],
  );

  const handleTypeFilterChange = useCallback(
    (value: string): void => {
      const nextValue = getFilterValue(value);
      navigate({
        search: (prev) => ({
          ...prev,
          type: nextValue,
        }),
      });
    },
    [navigate],
  );

  const handleCreateModalOpen = useCallback((): void => {
    setShowCreateModal(true);
  }, []);

  const handleCreateSubmit = useCallback((): void => {
    void handleCreate();
  }, [handleCreate]);

  const handleTitleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>): void => {
    setNewTitle(event.target.value);
  }, []);

  const handleDescriptionChange = useCallback(
    (event: React.ChangeEvent<HTMLTextAreaElement>): void => {
      setNewDescription(event.target.value);
    },
    [],
  );

  const handleStatusChange = useCallback((event: React.ChangeEvent<HTMLSelectElement>): void => {
    setNewStatus(event.target.value as ItemStatus);
  }, []);

  const handlePriorityChange = useCallback((event: React.ChangeEvent<HTMLSelectElement>): void => {
    setNewPriority(event.target.value as Priority);
  }, []);

  const projectSelectValue = createViewTypeValue(projectFilter);
  const typeSelectValue = createViewTypeValue(effectiveTypeFilter);

  if (isLoading) {
    return (
      <ListLoadingSkeleton
        message={getSearchMessage(liveMessageValue, labels.title)}
        rowCount={LOADING_ROW_COUNT}
        dataTestId='items-live-region'
      />
    );
  }

  const showEmptyState = filteredAndSortedItems.length === 0;
  const showInlineTable = filteredAndSortedItems.length <= TABLE_MAX_INLINE;

  return (
    <div className='animate-in-fade-up mx-auto max-w-[1600px] space-y-6 px-4 py-6 pb-20 sm:space-y-8 sm:px-6 sm:py-8'>
      {loadingOverlay}
      <div
        role='status'
        aria-live='polite'
        aria-atomic='true'
        data-testid='items-live-region'
        className='sr-only'
      >
        {liveMessageValue}
      </div>
      <div id='table-instructions' className='sr-only'>
        Use arrow keys to move between cells. Press Home and End to jump to first or last column.
        PageUp and PageDown move several rows.
      </div>

      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-2xl font-black tracking-tight uppercase'>{labels.title}</h1>
          <p className='text-muted-foreground text-sm font-medium'>{labels.description}</p>
        </div>
        <div className='flex items-center gap-2'>
          <Button variant='outline' size='sm' onClick={handleRefresh} className='gap-2 rounded-xl'>
            Refresh
          </Button>
          <Button
            size='sm'
            onClick={handleCreateModalOpen}
            aria-label={labels.newButtonLabel ?? DEFAULT_NEW_LABEL}
            className='shadow-primary/20 min-h-[44px] gap-2 rounded-xl shadow-lg'
          >
            <Plus className='h-4 w-4' /> {labels.newButtonLabel ?? DEFAULT_NEW_LABEL}
          </Button>
        </div>
      </div>

      <Card className='bg-muted/30 flex flex-wrap items-center gap-2 rounded-2xl border-none p-2'>
        <div className={cn('relative flex-1', `min-w-[${SEARCH_INPUT_MIN_WIDTH}px]`)}>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <Input
            placeholder='Search identifiers...'
            className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
            value={searchQuery}
            onChange={handleSearchChange}
            aria-label='Search items by title or ID'
          />
          <Button
            variant='ghost'
            size='icon'
            aria-label='Search items'
            className='absolute top-1/2 right-2 h-8 w-8 -translate-y-1/2'
          >
            <Search className='h-4 w-4' />
          </Button>
        </div>
        <div className='bg-border/50 mx-2 hidden h-6 w-px md:block' />
        <div className='text-muted-foreground/60 hidden px-2 text-[10px] lg:block'>
          Showing {filteredAndSortedItems.length} of {items.length} items
        </div>
        <div className='bg-border/50 mx-2 hidden h-6 w-px md:block' />
        <Button variant='ghost' size='sm' aria-label='Filter items' className='h-10 px-3'>
          <Filter className='h-4 w-4' />
        </Button>
        {!projectId && (
          <Select value={projectSelectValue} onValueChange={handleProjectFilterChange}>
            <SelectTrigger className='hover:bg-background/50 h-10 w-[180px] border-none bg-transparent transition-colors'>
              <div className='flex items-center gap-2'>
                <Filter className='text-muted-foreground h-3.5 w-3.5' />
                <SelectValue placeholder='All Projects' />
              </div>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={FILTER_ALL}>Global Scope</SelectItem>
              {projectsArray.map((project) => (
                <SelectItem key={project.id} value={project.id}>
                  {project.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
        {!type && (
          <Select value={typeSelectValue} onValueChange={handleTypeFilterChange}>
            <SelectTrigger className='hover:bg-background/50 h-10 w-[140px] border-none bg-transparent transition-colors'>
              <SelectValue placeholder='All Types' />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={FILTER_ALL}>Any Type</SelectItem>
              {VIEW_TYPE_OPTIONS.map((option) => (
                <SelectItem key={option} value={option} className='capitalize'>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </Card>

      <div className='md:hidden'>
        <ResponsiveCardView items={cardItems} isLoading={false} emptyState={emptyStateNode} />
      </div>

      <div className='hidden md:block'>
        <Card className='bg-card/50 flex flex-col overflow-hidden rounded-[2rem] border-none shadow-sm'>
          {showEmptyState && (
            <div
              className={cn(
                'flex items-center justify-center p-6',
                `min-h-[${TABLE_MIN_HEIGHT}px]`,
              )}
            >
              {emptyStateNode}
            </div>
          )}
          {!showEmptyState && showInlineTable && (
            <div className='custom-scrollbar overflow-x-auto'>
              <Table role='table' ariaLabel='Items table' ariaDescribedBy='table-instructions'>
                <TableHeaderRow
                  sortColumn={sortColumn}
                  sortOrder={sortOrder}
                  onSort={handleSortChange}
                />
                <TableBody>
                  {filteredAndSortedItems.map((item, index) => (
                    <ItemTableRow
                      key={item.id}
                      item={item}
                      rowIndex={index}
                      onNavigate={handleItemNavigate}
                      onDelete={handleDelete}
                      onCellKeyDown={handleCellKeyDown}
                    />
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
          {!showEmptyState && !showInlineTable && (
            <>
              <div className='custom-scrollbar overflow-x-auto'>
                <Table role='table' ariaLabel='Items table' ariaDescribedBy='table-instructions'>
                  <TableHeaderRow
                    sortColumn={sortColumn}
                    sortOrder={sortOrder}
                    onSort={handleSortChange}
                  />
                </Table>
              </div>
              <VirtualTable
                parentRef={parentRef}
                items={filteredAndSortedItems}
                rowVirtualizer={rowVirtualizer}
                onNavigate={handleItemNavigate}
                onDelete={handleDelete}
                onCellKeyDown={handleCellKeyDown}
                emptyState={emptyStateNode}
              />
            </>
          )}
        </Card>
      </div>

      {showCreateModal && (
        <div className='fixed inset-0 z-50 flex items-center justify-center'>
          <button
            type='button'
            className='fixed inset-0 bg-black/50 backdrop-blur-sm'
            onClick={closeCreateModal}
            aria-label='Close modal'
          />
          <div
            ref={modalRef}
            className='bg-background relative w-full max-w-lg rounded-xl border p-6 shadow-2xl'
            role='dialog'
            aria-modal='true'
            aria-labelledby='create-item-title'
          >
            <div className='flex items-center justify-between'>
              <h2 id='create-item-title' className='text-lg font-semibold'>
                {labels.createModalTitle ?? DEFAULT_CREATE_LABEL}
              </h2>
              <button
                type='button'
                onClick={closeCreateModal}
                id='close-create-item'
                aria-label='Close dialog'
                tabIndex={-1}
                className='hover:bg-accent focus:ring-primary rounded-lg p-1 focus:ring-2 focus:outline-none'
              >
                <X className='h-5 w-5' />
              </button>
            </div>
            <div className='mt-4 space-y-4'>
              {formError && (
                <div
                  role='alert'
                  aria-live='assertive'
                  className='border-destructive/30 bg-destructive/10 text-destructive rounded-lg border px-3 py-2 text-sm'
                >
                  {formError}
                </div>
              )}
              <div>
                <label htmlFor='item-title' className='block text-sm font-medium'>
                  Title
                </label>
                <Input
                  id='item-title'
                  name='title'
                  ref={titleInputRef}
                  value={newTitle}
                  onChange={handleTitleChange}
                  placeholder='Enter item title'
                  className='mt-1'
                  aria-label='Title'
                />
              </div>
              <div>
                <label htmlFor='item-description' className='block text-sm font-medium'>
                  Description
                </label>
                <textarea
                  id='item-description'
                  name='description'
                  value={newDescription}
                  onChange={handleDescriptionChange}
                  placeholder='Describe the item'
                  className='border-input bg-background focus:ring-primary mt-1 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:ring-2 focus:outline-none'
                  aria-label='Description'
                />
              </div>
              <div className='grid gap-4 sm:grid-cols-2'>
                <div>
                  <label htmlFor='item-type' className='block text-sm font-medium'>
                    Type
                  </label>
                  <Select value={newType} onValueChange={setNewType}>
                    <SelectTrigger
                      id='item-type'
                      aria-label='Type'
                      className='border-input bg-background focus:ring-primary mt-1 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:ring-2 focus:outline-none'
                    >
                      <SelectValue placeholder='Select type' />
                    </SelectTrigger>
                    <SelectContent>
                      {VIEW_TYPE_OPTIONS.map((option) => (
                        <SelectItem key={option} value={option}>
                          {option}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label htmlFor='item-status' className='block text-sm font-medium'>
                    Status
                  </label>
                  <select
                    id='item-status'
                    name='status'
                    value={newStatus}
                    onChange={handleStatusChange}
                    tabIndex={-1}
                    className='border-input bg-background focus:ring-primary mt-1 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:ring-2 focus:outline-none'
                    aria-label='Status'
                  >
                    {STATUS_VALUES.map((status) => (
                      <option key={status} value={status}>
                        {status.replace('_', ' ')}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label htmlFor='item-priority' className='block text-sm font-medium'>
                  Priority
                </label>
                <select
                  id='item-priority'
                  name='priority'
                  value={newPriority}
                  onChange={handlePriorityChange}
                  tabIndex={-1}
                  className='border-input bg-background focus:ring-primary mt-1 w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:ring-2 focus:outline-none'
                  aria-label='Priority'
                >
                  {PRIORITY_VALUES.map((priority) => (
                    <option key={priority} value={priority}>
                      {priority}
                    </option>
                  ))}
                </select>
              </div>
              <div className='flex justify-end gap-2 pt-2'>
                <Button
                  id='create-item-save'
                  onClick={handleCreateSubmit}
                  disabled={createItem.isPending}
                >
                  {createItem.isPending
                    ? 'Creating...'
                    : (labels.createButtonLabel ?? DEFAULT_CREATE_LABEL)}
                </Button>
                <Button id='create-item-cancel' variant='ghost' onClick={closeCreateModal}>
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export { ItemsTableView };

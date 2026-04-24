import { Link, useNavigate, useSearch } from '@tanstack/react-router';
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  ClipboardList,
  Clock,
  Filter,
  List,
  MoreVertical,
  Plus,
  Search,
  User,
} from 'lucide-react';
import { memo, useCallback, useMemo, useState } from 'react';
import { toast } from 'sonner';

import type { Item, ItemStatus } from '@tracertm/types';

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

import { useItems, useUpdateItem } from '../hooks/useItems';
import { useProjects } from '../hooks/useProjects';

interface KanbanColumn {
  status: ItemStatus;
  title: string;
  color: string;
  icon: React.ComponentType<{ className?: string }>;
}

const columns: KanbanColumn[] = [
  {
    color: 'border-t-muted',
    icon: ClipboardList,
    status: 'todo',
    title: 'BACKLOG',
  },
  {
    color: 'border-t-blue-500',
    icon: Clock,
    status: 'in_progress',
    title: 'ACTIVE',
  },
  {
    color: 'border-t-green-500',
    icon: CheckCircle2,
    status: 'done',
    title: 'RESOLVED',
  },
  {
    color: 'border-t-red-500',
    icon: AlertCircle,
    status: 'blocked',
    title: 'BLOCKED',
  },
];

interface ItemCardProps {
  item: Item;
  onDragStart: (item: Item) => void;
  projectFilter?: string | undefined;
}

const ItemCard = memo(
  function ItemCard({ item, onDragStart, projectFilter }: ItemCardProps) {
    const handleDragStart = useCallback(() => {
      onDragStart(item);
    }, [item, onDragStart]);

    return (
      <div
        draggable
        onDragStart={handleDragStart}
        className='group bg-card hover:bg-accent/5 border-border/50 cursor-grab rounded-xl border p-4 shadow-sm transition-all hover:shadow-md active:cursor-grabbing'
      >
        <Link
          to={
            projectFilter
              ? `/projects/${projectFilter}/views/${String(item.view || 'feature').toLowerCase()}/${item.id}`
              : '/projects'
          }
        >
          <div className='space-y-3'>
            <div className='flex items-start justify-between gap-2'>
              <Badge
                variant='outline'
                className='h-4 shrink-0 px-1.5 text-[9px] font-black tracking-tighter uppercase'
              >
                {item.type}
              </Badge>
              <button className='opacity-0 transition-opacity group-hover:opacity-100'>
                <MoreVertical className='text-muted-foreground h-3.5 w-3.5' />
              </button>
            </div>

            <h3 className='group-hover:text-primary line-clamp-2 text-sm leading-snug font-bold transition-colors'>
              {item.title}
            </h3>

            <div className='flex items-center justify-between gap-2 pt-1'>
              <div className='flex items-center gap-1.5'>
                {item.owner ? (
                  <div className='bg-primary/10 text-primary flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold'>
                    {item.owner.charAt(0).toUpperCase()}
                  </div>
                ) : (
                  <div className='bg-muted flex h-5 w-5 items-center justify-center rounded-full'>
                    <User className='text-muted-foreground h-3 w-3' />
                  </div>
                )}
                <span className='text-muted-foreground max-w-[80px] truncate text-[10px] font-bold tracking-wider uppercase'>
                  {item.owner ?? 'Unassigned'}
                </span>
              </div>

              {item.priority && (
                <div
                  className={cn(
                    'h-1.5 w-1.5 rounded-full',
                    item.priority === 'critical'
                      ? 'bg-red-500'
                      : item.priority === 'high'
                        ? 'bg-orange-500'
                        : item.priority === 'medium'
                          ? 'bg-blue-500'
                          : 'bg-green-500',
                  )}
                  title={`Priority: ${item.priority}`}
                />
              )}
            </div>
          </div>
        </Link>
      </div>
    );
  },
  (prev, next) =>
    prev.item.id === next.item.id &&
    prev.item.title === next.item.title &&
    prev.item.type === next.item.type &&
    prev.item.status === next.item.status &&
    prev.item.priority === next.item.priority &&
    prev.item.owner === next.item.owner &&
    prev.projectFilter === next.projectFilter,
);

const ColumnHeader = memo(function ColumnHeader({
  column,
  itemCount,
  isOver,
}: {
  column: KanbanColumn;
  itemCount: number;
  isOver: boolean;
}) {
  return (
    <div
      className={cn(
        'flex items-center justify-between p-3 rounded-2xl border-t-4 transition-all',
        column.color,
        isOver ? 'bg-primary/5 scale-[1.02]' : 'bg-muted/30',
      )}
    >
      <div className='flex items-center gap-2'>
        <column.icon className='text-muted-foreground h-4 w-4' />
        <h2 className='text-[10px] font-black tracking-[0.2em] uppercase'>{column.title}</h2>
      </div>
      <Badge variant='secondary' className='h-5 rounded-full px-2 text-[10px] font-black'>
        {itemCount}
      </Badge>
    </div>
  );
});

const EmptyDropZone = memo(function EmptyDropZone() {
  return (
    <div className='text-muted-foreground/30 border-border/50 flex flex-col items-center justify-center rounded-2xl border-2 border-dashed py-12'>
      <ArrowRight className='mb-2 h-8 w-8 rotate-90' />
      <p className='text-center text-[10px] font-bold tracking-widest uppercase'>Empty Drop Zone</p>
    </div>
  );
});

const ColumnDropZone = memo(
  function ColumnDropZone({
    column,
    items,
    isOver,
    onDrop,
    onDragOver,
    onDragLeave,
    onDragStart,
    projectFilter,
  }: {
    column: KanbanColumn;
    items: Item[];
    isOver: boolean;
    onDrop: () => void;
    onDragOver: (e: React.DragEvent) => void;
    onDragLeave: () => void;
    onDragStart: (item: Item) => void;
    projectFilter?: string | undefined;
  }) {
    return (
      <div
        key={column.status}
        className='flex min-w-[320px] flex-1 flex-col space-y-4'
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
      >
        <ColumnHeader column={column} itemCount={items.length} isOver={isOver} />

        <div
          className={cn(
            'flex-1 flex flex-col gap-3 p-2 rounded-2xl transition-colors duration-200',
            isOver ? 'bg-primary/5 ring-2 ring-primary/20 ring-dashed' : 'transparent',
          )}
        >
          {items.map((item) => (
            <ItemCard
              key={item.id}
              item={item}
              onDragStart={onDragStart}
              projectFilter={projectFilter}
            />
          ))}
          {items.length === 0 && <EmptyDropZone />}
        </div>
      </div>
    );
  },
  (prev, next) =>
    prev.column.status === next.column.status &&
    prev.items.length === next.items.length &&
    prev.items.every(
      (item, idx) => item.id === next.items[idx]?.id && item.status === next.items[idx].status,
    ) &&
    prev.isOver === next.isOver &&
    prev.projectFilter === next.projectFilter,
);

export function ItemsKanbanView() {
  const navigate = useNavigate();
  const searchParams = useSearch({ strict: false });
  const projectFilter = searchParams?.project ?? undefined;
  const typeFilter = searchParams?.type ?? undefined;

  const { data: itemsData, isLoading } = useItems({ projectId: projectFilter });
  const { data: projects } = useProjects();
  const projectsArray = useMemo(() => (Array.isArray(projects) ? projects : []), [projects]);
  const items = itemsData?.items ?? [];
  const updateItem = useUpdateItem();

  const [searchQuery, setSearchQuery] = useState('');
  const [draggedItem, setDraggedItem] = useState<Item | null>(null);
  const [isDraggingOver, setIsDraggingOver] = useState<string | null>(null);

  const filteredItems = useMemo(() => {
    if (items.length === 0) {
      return [];
    }
    return items.filter((item: any) => {
      if (typeFilter && item.type !== typeFilter) {
        return false;
      }
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          item.title.toLowerCase().includes(query) ??
          item.description?.toLowerCase().includes(query)
        );
      }
      return true;
    });
  }, [items, typeFilter, searchQuery]);

  const itemsByStatus = useMemo(() => {
    const grouped: Record<string, Item[]> = {
      blocked: [],
      done: [],
      in_progress: [],
      todo: [],
    };
    filteredItems.forEach((item) => {
      const { status } = item;
      if (status && grouped[status]) {
        grouped[status].push(item);
      }
    });
    return grouped;
  }, [filteredItems]);

  const columnsWithStatus = useMemo(() => columns, []);

  const handleDrop = useCallback(
    async (newStatus: ItemStatus) => {
      setIsDraggingOver(null);
      if (!draggedItem || draggedItem.status === newStatus) {
        setDraggedItem(null);
        return;
      }

      try {
        // Optimistic UI update could go here
        await updateItem.mutateAsync({
          data: { status: newStatus },
          id: draggedItem.id,
        });
        toast.success(`Moved to ${newStatus.replace('_', ' ')}`);
        setDraggedItem(null);
      } catch {
        toast.error('Failed to update status');
      }
    },
    [draggedItem, updateItem],
  );

  const handleDragStart = useCallback((item: Item) => {
    setDraggedItem(item);
  }, []);

  const handleDragOver = useCallback((status: ItemStatus, e: React.DragEvent) => {
    e.preventDefault();
    setIsDraggingOver(status);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDraggingOver(null);
  }, []);

  const handleProjectFilterChange = useCallback((_v: string) => {}, [navigate]);

  const handleTypeFilterChange = useCallback((_v: string) => {}, [navigate]);

  const handleNavigateToTable = useCallback(() => {}, [navigate, searchParams, projectFilter]);

  const handleNavigateToCreate = useCallback(() => {}, [navigate, searchParams, projectFilter]);

  if (isLoading) {
    return (
      <div className='animate-pulse space-y-8 p-6'>
        <div className='flex items-center justify-between'>
          <Skeleton className='h-10 w-48' />
          <Skeleton className='h-10 w-64' />
        </div>
        <div className='flex gap-6 overflow-hidden'>
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className='h-[600px] flex-1 rounded-2xl' />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className='animate-in fade-in mx-auto max-w-[1800px] space-y-8 p-6 duration-500'>
      {/* Header */}
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-2xl font-black tracking-tight uppercase'>Kanban Workflow</h1>
          <p className='text-muted-foreground text-sm font-medium'>
            Manage lifecycle and status transitions for project nodes.
          </p>
        </div>
        <div className='flex items-center gap-2'>
          <Button
            variant='outline'
            size='sm'
            onClick={handleNavigateToTable}
            className='gap-2 rounded-xl'
          >
            <List className='h-4 w-4' /> Table
          </Button>
          <Button
            size='sm'
            onClick={handleNavigateToCreate}
            className='shadow-primary/20 gap-2 rounded-xl shadow-lg'
          >
            <Plus className='h-4 w-4' /> New Item
          </Button>
        </div>
      </div>

      {/* Filters Control Bar */}
      <Card className='bg-muted/30 flex flex-wrap items-center gap-2 rounded-2xl border-none p-2'>
        <div className='relative min-w-[200px] flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <Input
            placeholder='Filter items...'
            className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
            }}
          />
        </div>
        <div className='bg-border/50 mx-2 hidden h-6 w-px md:block' />
        <Select value={projectFilter ?? 'all'} onValueChange={handleProjectFilterChange}>
          <SelectTrigger className='hover:bg-background/50 h-10 w-[180px] border-none bg-transparent transition-colors'>
            <div className='flex items-center gap-2'>
              <Filter className='text-muted-foreground h-3.5 w-3.5' />
              <SelectValue placeholder='All Projects' />
            </div>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='all'>All Projects</SelectItem>
            {projectsArray.map((p) => (
              <SelectItem key={p.id} value={p.id}>
                {p.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={typeFilter ?? 'all'} onValueChange={handleTypeFilterChange}>
          <SelectTrigger className='hover:bg-background/50 h-10 w-[150px] border-none bg-transparent transition-colors'>
            <SelectValue placeholder='All Types' />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='all'>All Types</SelectItem>
            {['requirement', 'feature', 'test', 'bug', 'task'].map((t) => (
              <SelectItem key={t} value={t} className='capitalize'>
                {t}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </Card>

      {/* Kanban Board */}
      <div className='custom-scrollbar -mx-6 flex min-h-[70vh] gap-6 overflow-x-auto px-6 pb-8'>
        {columnsWithStatus.map((column) => {
          const colItems = itemsByStatus[column.status] ?? [];
          const isOver = isDraggingOver === column.status;

          return (
            <ColumnDropZone
              key={column.status}
              column={column}
              items={colItems}
              isOver={isOver}
              onDrop={async () => handleDrop(column.status)}
              onDragOver={(e) => {
                handleDragOver(column.status, e);
              }}
              onDragLeave={handleDragLeave}
              onDragStart={handleDragStart}
              projectFilter={projectFilter}
            />
          );
        })}
      </div>
    </div>
  );
}

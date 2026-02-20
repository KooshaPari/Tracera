import { Link } from '@tanstack/react-router';
import { ChevronDown, ChevronRight, Layers, Plus, Sparkles, Target } from 'lucide-react';
import { useMemo, useState } from 'react';
import { toast } from 'sonner';

import type { TypedItem } from '@tracertm/types';

import { CreateItemForm } from '@/components/forms/CreateItemForm';
import { useCreateItem, useItems } from '@/hooks/useItems';
import { cn } from '@/lib/utils';
import { Badge, Button, Card } from '@tracertm/ui';
import { Skeleton } from '@tracertm/ui/components/Skeleton';

const statusColors: Record<string, string> = {
  blocked: 'bg-rose-500/15 text-rose-700 border-rose-500/30',
  cancelled: 'bg-slate-500/15 text-slate-600 border-slate-500/20',
  done: 'bg-emerald-500/15 text-emerald-700 border-emerald-500/30',
  in_progress: 'bg-sky-500/15 text-sky-700 border-sky-500/30',
  todo: 'bg-slate-500/10 text-slate-600 border-slate-500/20',
};

interface FeatureViewProps {
  projectId: string;
}

/** Build epic/feature hierarchy: epics as roots, features (or items with parentId) as children */
function buildHierarchy(items: TypedItem[]) {
  const roots: TypedItem[] = [];
  const childrenByParent = new Map<string, TypedItem[]>();

  for (const item of items) {
    const isEpic = item.type === 'epic';
    const parentId = item.parentId ?? null;
    if (isEpic || !parentId) {
      roots.push(item);
    } else {
      const list = childrenByParent.get(parentId) ?? [];
      list.push(item);
      childrenByParent.set(parentId, list);
    }
  }

  roots.sort((a, b) => (a.title ?? '').localeCompare(b.title ?? ''));
  childrenByParent.forEach((list) =>
    list.sort((a, b) => (a.title ?? '').localeCompare(b.title ?? '')),
  );
  return { childrenByParent, roots };
}

export function FeatureView({ projectId }: FeatureViewProps) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [showCreate, setShowCreate] = useState(false);
  const [createType, setCreateType] = useState<'epic' | 'feature'>('epic');
  const [parentIdForFeature, setParentIdForFeature] = useState<string | null>(null);

  const { data, isLoading, error } = useItems({
    projectId,
    view: 'feature',
  });
  const createItem = useCreateItem();

  const { roots, childrenByParent } = useMemo(() => {
    const list = data?.items ?? [];
    return buildHierarchy(list);
  }, [data?.items]);

  const toggle = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleAddEpic = () => {
    setCreateType('epic');
    setParentIdForFeature(null);
    setShowCreate(true);
  };

  const handleAddFeature = (parentId?: string) => {
    setCreateType('feature');
    setParentIdForFeature(parentId ?? null);
    setShowCreate(true);
  };

  const handleCreateSubmit = async (formData: {
    title: string;
    description?: string | undefined;
    view: string;
    type: string;
    status: string;
    priority: string;
    parentId?: string | undefined;
  }) => {
    try {
      await createItem.mutateAsync({
        description: formData.description,
        parentId: createType === 'feature' ? (parentIdForFeature ?? undefined) : undefined,
        priority: formData.priority as 'low' | 'medium' | 'high' | 'critical',
        projectId,
        status: formData.status as 'todo' | 'in_progress' | 'done' | 'blocked' | 'cancelled',
        title: formData.title,
        type: createType,
        view: 'feature',
      });
      toast.success(createType === 'epic' ? 'Epic created' : 'Feature created');
      setShowCreate(false);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to create');
    }
  };

  if (isLoading) {
    return (
      <div className='mx-auto flex min-h-0 w-full max-w-[1600px] flex-1 flex-col px-6 py-6'>
        <header className='border-border/50 shrink-0 border-b pb-6'>
          <div className='flex items-center justify-between gap-4'>
            <div className='space-y-2'>
              <Skeleton className='h-8 w-48' />
              <Skeleton className='h-4 w-64' />
            </div>
            <div className='flex gap-2'>
              <Skeleton className='h-9 w-24' />
              <Skeleton className='h-9 w-28' />
            </div>
          </div>
        </header>
        <main className='min-h-0 flex-1 overflow-auto pt-6'>
          <div className='space-y-3'>
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className='h-20 w-full rounded-xl' />
            ))}
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className='rounded-lg border border-red-200 bg-red-50 p-4 text-red-700'>
        <p className='font-medium'>Error loading features</p>
        <p className='mt-1 text-sm'>{error.message}</p>
      </div>
    );
  }

  return (
    <div className='mx-auto flex min-h-0 w-full max-w-[1600px] flex-1 flex-col px-6 py-6'>
      <header className='border-border/60 bg-background/95 mb-0 shrink-0 border-b pb-6 backdrop-blur-sm'>
        <div className='flex flex-wrap items-center justify-between gap-4'>
          <div>
            <h1 className='text-3xl font-bold tracking-tight'>Features</h1>
            <p className='text-muted-foreground mt-1'>Epics and features for this project</p>
          </div>
          <div className='flex gap-2'>
            <Button variant='outline' size='sm' onClick={handleAddEpic}>
              <Plus className='mr-1 h-4 w-4' /> Add Epic
            </Button>
            <Button
              size='sm'
              onClick={() => {
                handleAddFeature();
              }}
            >
              <Plus className='mr-1 h-4 w-4' /> Add Feature
            </Button>
          </div>
        </div>
      </header>

      <main className='mt-0 min-h-0 flex-1 overflow-auto pt-8'>
        {roots.length === 0 ? (
          <Card className='border-border/60 bg-card/95 border-2 border-dashed p-12 text-center shadow-lg ring-1 ring-white/10 backdrop-blur-md'>
            <div className='bg-primary/10 mx-auto flex h-14 w-14 items-center justify-center rounded-2xl'>
              <Sparkles className='text-primary h-7 w-7' />
            </div>
            <p className='text-foreground mt-4 text-lg font-semibold'>No features yet</p>
            <p className='text-muted-foreground mt-1 text-sm'>
              Create an epic or feature to get started.
            </p>
            <div className='mt-6 flex justify-center gap-3'>
              <Button
                variant='outline'
                size='sm'
                onClick={handleAddEpic}
                className='gap-2 rounded-full'
              >
                <Layers className='h-4 w-4' /> Add Epic
              </Button>
              <Button
                size='sm'
                onClick={() => {
                  handleAddFeature();
                }}
                className='gap-2 rounded-full'
              >
                <Target className='h-4 w-4' /> Add Feature
              </Button>
            </div>
          </Card>
        ) : (
          <div className='space-y-3'>
            {roots.map((item) => {
              const children = childrenByParent.get(item.id) ?? [];
              const isExpanded = expanded.has(item.id);
              const isEpic = item.type === 'epic';
              const TypeIcon = isEpic ? Layers : Target;
              const hasChildren = children.length > 0;
              return (
                <Card
                  key={item.id}
                  className={cn(
                    'overflow-hidden border border-border/60 shadow-lg transition-all hover:shadow-xl',
                    'bg-card/95 backdrop-blur-md',
                    'ring-1 ring-white/15',
                  )}
                >
                  <div className='flex items-center gap-4 p-4 md:p-5'>
                    {hasChildren ? (
                      <button
                        type='button'
                        onClick={() => {
                          toggle(item.id);
                        }}
                        className='bg-primary/10 hover:bg-primary/20 focus-visible:ring-primary flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2'
                        aria-label={isExpanded ? 'Collapse' : 'Expand'}
                      >
                        {isExpanded ? (
                          <ChevronDown className='text-primary h-5 w-5' />
                        ) : (
                          <ChevronRight className='text-primary h-5 w-5' />
                        )}
                      </button>
                    ) : (
                      <div className='bg-primary/10 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl'>
                        <TypeIcon className='text-primary h-5 w-5' />
                      </div>
                    )}
                    <Link
                      to='/projects/$projectId/views/$viewType/$itemId'
                      params={{
                        itemId: item.id,
                        projectId,
                        viewType: 'feature',
                      }}
                      className='focus-visible:ring-primary min-w-0 flex-1 space-y-1 rounded-lg focus:outline-none focus-visible:rounded-lg focus-visible:ring-2 focus-visible:ring-offset-2'
                    >
                      <p className='text-foreground hover:text-primary truncate font-semibold hover:underline'>
                        {item.title}
                      </p>
                      <div className='flex flex-wrap items-center gap-2'>
                        <Badge
                          variant='outline'
                          className={cn(
                            'text-[10px] font-semibold uppercase tracking-wider',
                            isEpic
                              ? 'border-violet-500/40 bg-violet-500/10 text-violet-700'
                              : 'border-sky-500/40 bg-sky-500/10 text-sky-700',
                          )}
                        >
                          {item.type}
                        </Badge>
                        <Badge
                          className={cn(
                            'text-[10px] font-semibold uppercase tracking-wider border',
                            statusColors[item.status] ??
                              'bg-slate-500/10 text-slate-600 border-slate-500/20',
                          )}
                        >
                          {item.status.replace('_', ' ')}
                        </Badge>
                      </div>
                    </Link>
                    {isEpic && (
                      <Button
                        variant='outline'
                        size='sm'
                        className='shrink-0 gap-1.5 rounded-full'
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          handleAddFeature(item.id);
                        }}
                      >
                        <Plus className='h-4 w-4' /> Add feature
                      </Button>
                    )}
                  </div>
                  {isExpanded && children.length > 0 && (
                    <div className='border-border/60 bg-muted/50 border-t backdrop-blur-sm'>
                      {children.map((child) => (
                        <Link
                          key={child.id}
                          to='/projects/$projectId/views/$viewType/$itemId'
                          params={{
                            itemId: child.id,
                            projectId,
                            viewType: 'feature',
                          }}
                          className='border-border/40 hover:bg-muted/60 focus-visible:ring-primary flex items-center gap-4 border-t p-4 pl-[4.5rem] transition-colors first:border-t-0 focus:outline-none focus-visible:ring-2 focus-visible:ring-inset'
                        >
                          <div className='flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-sky-500/10'>
                            <Target className='h-4 w-4 text-sky-600' />
                          </div>
                          <span className='text-foreground min-w-0 flex-1 truncate font-medium'>
                            {child.title}
                          </span>
                          <Badge
                            className={cn(
                              'shrink-0 text-[10px] font-semibold uppercase tracking-wider border',
                              statusColors[child.status] ??
                                'bg-slate-500/10 text-slate-600 border-slate-500/20',
                            )}
                          >
                            {child.status.replace('_', ' ')}
                          </Badge>
                          <ChevronRight className='text-muted-foreground h-4 w-4 shrink-0' />
                        </Link>
                      ))}
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        )}
      </main>

      {showCreate && (
        <CreateItemForm
          title='Create Feature'
          submitLabel='Create Feature'
          submitBusyLabel='Creating...'
          defaultView='FEATURE'
          onSubmit={handleCreateSubmit}
          onCancel={() => {
            setShowCreate(false);
          }}
          isLoading={createItem.isPending}
        />
      )}
    </div>
  );
}

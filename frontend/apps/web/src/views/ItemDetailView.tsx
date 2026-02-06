import { Link, useNavigate, useParams } from '@tanstack/react-router';
import {
  ArrowLeft,
  BookText,
  CalendarClock,
  ChevronRight,
  CircleDot,
  Code2,
  Edit3,
  ExternalLink,
  GitBranch,
  Hash,
  Link2,
  MoreVertical,
  Orbit,
  ShieldAlert,
  Sparkles,
  Target,
  Timer,
  Trash2,
  User,
  X,
  XCircle,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { toast } from 'sonner';

import { ItemSpecTabs } from '@/components/specifications/items/ItemSpecTabs';
import { logger } from '@/lib/logger';
import { cn } from '@/lib/utils';
import {
  Badge,
  Button,
  Card,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Separator,
  Skeleton,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  Textarea,
} from '@tracertm/ui';

import { useDeleteItem, useItem, useUpdateItem } from '../hooks/useItems';
import {
  useCreateDefectSpec,
  useCreateEpicSpec,
  useCreateRequirementSpec,
  useCreateTaskSpec,
  useCreateTestSpec,
  useCreateUserStorySpec,
} from '../hooks/useItemSpecs';
import { useLinks } from '../hooks/useLinks';

const statusColors: Record<string, string> = {
  blocked: 'bg-rose-500/15 text-rose-700 border-rose-500/30',
  done: 'bg-emerald-500/15 text-emerald-700 border-emerald-500/30',
  in_progress: 'bg-sky-500/15 text-sky-700 border-sky-500/30',
  todo: 'bg-slate-500/10 text-slate-600 border-slate-500/20',
};

const priorityColors: Record<string, string> = {
  critical: 'bg-rose-500 text-white',
  high: 'bg-orange-500 text-white',
  low: 'bg-emerald-500 text-white',
  medium: 'bg-indigo-500 text-white',
};

const statusOptions = ['todo', 'in_progress', 'blocked', 'done'] as const;
const priorityOptions = ['critical', 'high', 'medium', 'low'] as const;

const integrationKeys = new Set([
  'external_system',
  'external_id',
  'external_key',
  'external_url',
  'repo_full_name',
  'issue_number',
  'state',
  'labels',
  'projectId',
  'team_id',
  'identifier',
  'url',
]);

function formatValue(value: unknown) {
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  if (value && typeof value === 'object') {
    return JSON.stringify(value);
  }
  if (value === null || value === undefined) {
    return '–';
  }
  return String(value);
}

export function ItemDetailView() {
  const params = useParams({ strict: false });
  const itemId = params.itemId as string | undefined;
  const projectId = params.projectId as string | undefined;
  const viewTypeParam = params.viewType as string | undefined;
  const navigate = useNavigate();
  const { data: item, isLoading, error } = useItem(itemId!);
  const deleteItem = useDeleteItem();
  const updateItem = useUpdateItem();
  const createRequirementSpec = useCreateRequirementSpec(item?.projectId || '');
  const createTestSpec = useCreateTestSpec(item?.projectId || '');
  const createEpicSpec = useCreateEpicSpec(item?.projectId || '');
  const createUserStorySpec = useCreateUserStorySpec(item?.projectId || '');
  const createTaskSpec = useCreateTaskSpec(item?.projectId || '');
  const createDefectSpec = useCreateDefectSpec(item?.projectId || '');
  const [isEditing, setIsEditing] = useState(false);
  const [metadataSearch, setMetadataSearch] = useState('');
  const [draft, setDraft] = useState({
    description: '',
    owner: '',
    priority: 'medium',
    status: 'todo',
    title: '',
  });

  useEffect(() => {
    if (!item) {
      return;
    }
    setDraft({
      description: item.description ?? '',
      owner: item.owner ?? '',
      priority: item.priority ?? 'medium',
      status: item.status ?? 'todo',
      title: item.title ?? '',
    });
  }, [item]);

  const defaultViewType = (
    viewTypeParam ||
    (item?.view ? String(item.view) : undefined) ||
    'feature'
  ).toLowerCase();

  const buildItemLink = (id: string) =>
    projectId ? `/projects/${projectId}/views/${defaultViewType}/${id}` : '/projects';

  const handleBack = () => {};

  const { data: sourceLinksData } = useLinks({
    projectId: item?.projectId,
    sourceId: itemId,
  });
  const { data: targetLinksData } = useLinks({
    projectId: item?.projectId,
    targetId: itemId,
  });

  const { sourceLinks, targetLinks } = useMemo(() => {
    const s = sourceLinksData?.links ?? [];
    const t = targetLinksData?.links ?? [];
    return { sourceLinks: s, targetLinks: t };
  }, [sourceLinksData, targetLinksData]);

  const metadataEntries = useMemo(() => Object.entries(item?.metadata ?? {}), [item?.metadata]);

  const filteredMetadata = useMemo(() => {
    if (!metadataSearch.trim()) {
      return metadataEntries;
    }
    const query = metadataSearch.trim().toLowerCase();
    return metadataEntries.filter(([key, value]) => {
      const haystack = `${key} ${formatValue(value)}`.toLowerCase();
      return haystack.includes(query);
    });
  }, [metadataEntries, metadataSearch]);

  const integrationEntries = useMemo(
    () => filteredMetadata.filter(([key]) => integrationKeys.has(key)),
    [filteredMetadata],
  );

  const generalMetadata = useMemo(
    () => filteredMetadata.filter(([key]) => !integrationKeys.has(key)),
    [filteredMetadata],
  );

  const dimensionEntries = useMemo(() => {
    if (!item?.dimensions) {
      return [] as [string, unknown][];
    }
    const entries: [string, unknown][] = [];
    if (item.dimensions.maturity) {
      entries.push(['Maturity', item.dimensions.maturity]);
    }
    if (item.dimensions.complexity) {
      entries.push(['Complexity', item.dimensions.complexity]);
    }
    if (item.dimensions.risk) {
      entries.push(['Risk', item.dimensions.risk]);
    }
    if (item.dimensions.coverage) {
      entries.push(['Coverage', item.dimensions.coverage]);
    }
    if (item.dimensions.custom) {
      Object.entries(item.dimensions.custom).forEach(([key, value]) => {
        entries.push([key, value]);
      });
    }
    return entries;
  }, [item?.dimensions]);

  const timelineEvents = useMemo(() => {
    if (!item) {
      return [] as { label: string; timestamp: string; detail?: string }[];
    }
    const events: { label: string; timestamp: string; detail?: string }[] = [];
    if (item.createdAt) {
      events.push({
        detail: `Status: ${item.status}`,
        label: 'Item created',
        timestamp: item.createdAt,
      });
    }
    if (item.updatedAt) {
      events.push({
        detail: `v${item.version}`,
        label: 'Item updated',
        timestamp: item.updatedAt,
      });
    }
    if (item.version > 1 && item.updatedAt) {
      events.push({
        detail: `Now at v${item.version}`,
        label: 'Version bump',
        timestamp: item.updatedAt,
      });
    }
    if (integrationEntries.length > 0 && item.updatedAt) {
      const integration = integrationEntries.find(([key]) => key === 'external_system');
      events.push({
        detail: integration ? `System: ${integration[1]}` : 'Integration data attached',
        label: 'External sync',
        timestamp: item.updatedAt,
      });
    }
    return [...events].toSorted((a, b) => (a.timestamp < b.timestamp ? 1 : -1));
  }, [integrationEntries, item]);

  const upstreamCount = targetLinks.length;
  const downstreamCount = sourceLinks.length;
  const metadataCount = metadataEntries.length;
  const displayStatus = isEditing ? (draft?.status ?? 'todo') : (item?.status ?? 'todo');
  const displayPriority = isEditing ? (draft?.priority ?? 'medium') : (item?.priority ?? 'medium');
  const updatedAtLabel = item?.updatedAt ? new Date(item.updatedAt).toLocaleString() : 'Unknown';
  const createdAtLabel = item?.createdAt
    ? new Date(item.createdAt).toLocaleDateString()
    : 'Unknown';

  const handleDelete = async () => {
    if (!itemId) {
      return;
    }
    try {
      await deleteItem.mutateAsync(itemId);
      toast.success('Item deleted successfully');
      handleBack();
    } catch {
      toast.error('Failed to delete item');
    }
  };

  const handleCancelEdit = () => {
    if (item) {
      setDraft({
        description: item.description ?? '',
        owner: item.owner ?? '',
        priority: item.priority ?? 'medium',
        status: item.status ?? 'todo',
        title: item.title ?? '',
      });
    }
    setIsEditing(false);
  };

  const handleSave = async () => {
    if (!itemId || !item) {
      return;
    }
    try {
      await updateItem.mutateAsync({
        data: {
          description: draft.description,
          owner: draft.owner || undefined,
          priority: draft.priority as any,
          status: draft.status as any,
          title: draft.title,
        },
        id: itemId,
      });
      toast.success('Item updated');
      setIsEditing(false);
    } catch {
      toast.error('Failed to update item');
    }
  };

  const handleCreateSpec = async (specType: string, itemId: string, _projectId?: string) => {
    try {
      switch (specType) {
        case 'requirement': {
          await createRequirementSpec.mutateAsync({
            constraint_type: 'soft',
            item_id: itemId,
            requirement_type: 'ubiquitous',
            risk_level: 'minimal',
          });
          toast.success('Requirement spec created');
          break;
        }
        case 'test': {
          await createTestSpec.mutateAsync({
            item_id: itemId,
            test_type: 'unit',
          });
          toast.success('Test spec created');
          break;
        }
        case 'epic': {
          await createEpicSpec.mutateAsync({
            business_value: 0,
            epic_name: 'New Epic',
            item_id: itemId,
            status: 'backlog',
          });
          toast.success('Epic spec created');
          break;
        }
        case 'user_story': {
          await createUserStorySpec.mutateAsync({
            as_a: 'User',
            i_want: 'To complete task',
            item_id: itemId,
            priority: 3,
            so_that: 'Work is done',
            status: 'backlog',
          });
          toast.success('User story spec created');
          break;
        }
        case 'task': {
          await createTaskSpec.mutateAsync({
            item_id: itemId,
            priority: 3,
            status: 'todo',
            task_title: 'New Task',
          });
          toast.success('Task spec created');
          break;
        }
        case 'defect': {
          await createDefectSpec.mutateAsync({
            actual_behavior: 'Unknown',
            description: 'New Defect Description',
            expected_behavior: 'Correct behavior',
            item_id: itemId,
            severity: 'minor',
            status: 'new',
            title: 'New Defect',
          });
          toast.success('Defect spec created');
          break;
        }
        default: {
          toast.error('Unknown spec type');
        }
      }
    } catch (error) {
      toast.error(`Failed to create ${specType} spec`);
      logger.error(error as any);
    }
  };

  if (isLoading) {
    return (
      <div className='w-full animate-pulse space-y-8 px-0 py-10'>
        <Skeleton className='h-8 w-48' />
        <div className='flex items-start justify-between'>
          <div className='flex-1 space-y-4'>
            <Skeleton className='h-12 w-3/4' />
            <Skeleton className='h-6 w-1/2' />
          </div>
          <Skeleton className='h-10 w-32' />
        </div>
        <Skeleton className='h-[400px] w-full' />
      </div>
    );
  }

  if (error || !item) {
    return (
      <div className='flex flex-col items-center justify-center space-y-4 p-20'>
        <XCircle className='text-destructive h-12 w-12 opacity-20' />
        <h2 className='text-xl font-bold'>Item Not Found</h2>
        <Button variant='outline' onClick={handleBack}>
          Return to Items
        </Button>
      </div>
    );
  }

  return (
    <div className='relative flex min-h-screen flex-col'>
      <div className='pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_15%_15%,rgba(249,115,22,0.18),transparent_45%),radial-gradient(circle_at_80%_10%,rgba(14,116,144,0.2),transparent_45%),radial-gradient(circle_at_20%_80%,rgba(16,185,129,0.18),transparent_40%)]' />
      <div className='pointer-events-none absolute inset-0 bg-[linear-gradient(120deg,rgba(15,23,42,0.08),transparent_55%,rgba(2,132,199,0.08))]' />
      <div className='animate-in-fade-up relative mx-auto flex min-h-0 w-full max-w-[1600px] flex-1 flex-col px-6 py-6 md:py-10'>
        <header className='border-border/50 shrink-0 border-b pb-6'>
          <div className='flex items-center justify-between'>
            <Button
              variant='ghost'
              size='sm'
              onClick={() => globalThis.history.back()}
              className='text-muted-foreground hover:text-foreground gap-2'
            >
              <ArrowLeft className='h-4 w-4' />
              Back
            </Button>
            <div className='flex items-center gap-2'>
              <Button variant='outline' size='sm' className='gap-2 rounded-full' onClick={() => {}}>
                <ExternalLink className='h-3.5 w-3.5' />
                Share
              </Button>
              {isEditing ? (
                <>
                  <Button size='sm' className='gap-2 rounded-full' onClick={handleSave}>
                    <ChevronRight className='h-4 w-4' />
                    Save
                  </Button>
                  <Button
                    variant='outline'
                    size='sm'
                    className='gap-2 rounded-full'
                    onClick={handleCancelEdit}
                  >
                    <X className='h-4 w-4' />
                    Cancel
                  </Button>
                </>
              ) : (
                <Button
                  variant='outline'
                  size='sm'
                  className='gap-2 rounded-full'
                  onClick={() => setIsEditing(true)}
                >
                  <Edit3 className='h-3.5 w-3.5' />
                  Edit
                </Button>
              )}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <span>
                    <Button variant='ghost' size='icon' className='rounded-full'>
                      <MoreVertical className='h-4 w-4' />
                    </Button>
                  </span>
                </DropdownMenuTrigger>
                <DropdownMenuContent align='end' className='w-48'>
                  <DropdownMenuItem className='hover:bg-accent hover:text-accent-foreground cursor-pointer gap-2 transition-colors'>
                    <ChevronRight className='h-4 w-4' /> Open in New Tab
                  </DropdownMenuItem>
                  <Separator className='my-1' />
                  <DropdownMenuItem
                    className='text-destructive focus:text-destructive focus:bg-destructive/10 hover:bg-destructive/10 hover:text-destructive cursor-pointer gap-2 transition-colors'
                    onClick={handleDelete}
                  >
                    <Trash2 className='h-4 w-4' /> Delete Item
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </header>

        <main className='min-h-0 flex-1 overflow-auto pt-6 md:pt-8'>
          <Card className='bg-card/60 shadow-primary/10 overflow-hidden border-0 shadow-xl backdrop-blur-sm'>
            <div className='space-y-6 p-8'>
              <div className='flex flex-wrap items-center gap-2'>
                <Badge
                  variant='outline'
                  className='text-[10px] font-black tracking-[0.35em] uppercase'
                >
                  {item.view || 'general'}
                </Badge>
                <Badge
                  variant='outline'
                  className='text-[10px] font-black tracking-[0.35em] uppercase'
                >
                  {item.type}
                </Badge>
                <Badge
                  className={cn(
                    'text-[10px] font-black uppercase tracking-[0.35em]',
                    statusColors[displayStatus],
                  )}
                >
                  {displayStatus.replace('_', ' ')}
                </Badge>
                <Badge
                  className={cn(
                    'text-[10px] font-black',
                    priorityColors[displayPriority || 'medium'],
                  )}
                >
                  {displayPriority || 'medium'}
                </Badge>
                <Badge
                  variant='secondary'
                  className='gap-1 text-[10px] tracking-[0.35em] uppercase'
                >
                  <Hash className='h-3 w-3' />
                  {item.id}
                </Badge>
              </div>

              <div className='grid grid-cols-1 gap-8 lg:grid-cols-[1.4fr_1fr]'>
                <div className='space-y-4'>
                  {isEditing ? (
                    <div className='space-y-3'>
                      <Input
                        value={draft.title}
                        onChange={(event) =>
                          setDraft((prev) => ({
                            ...prev,
                            title: event.target.value,
                          }))
                        }
                        placeholder='Item title'
                        className='h-12 text-2xl font-black'
                      />
                      <Textarea
                        value={draft.description}
                        onChange={(event) =>
                          setDraft((prev) => ({
                            ...prev,
                            description: event.target.value,
                          }))
                        }
                        placeholder='Describe the item...'
                        className='min-h-[120px]'
                      />
                    </div>
                  ) : (
                    <>
                      <p className='text-muted-foreground mb-1 text-sm font-semibold tracking-widest uppercase'>
                        {item.view
                          ? `${String(item.view).charAt(0).toUpperCase()}${String(item.view).slice(1).toLowerCase()} · ${item.type}`
                          : item.type}
                      </p>
                      <h1
                        className='text-4xl leading-tight font-black tracking-tight md:text-5xl'
                        style={{
                          fontFamily: '"Space Grotesk","Sora","IBM Plex Sans",sans-serif',
                        }}
                      >
                        {item.title}
                      </h1>
                      <p className='text-muted-foreground text-lg leading-relaxed'>
                        {item.description || 'No description provided for this item.'}
                      </p>
                    </>
                  )}
                  <div className='text-muted-foreground flex flex-wrap items-center gap-3 text-xs font-bold tracking-widest uppercase'>
                    <span className='inline-flex items-center gap-2'>
                      <CalendarClock className='h-3.5 w-3.5' />
                      Created {createdAtLabel}
                    </span>
                    <span className='inline-flex items-center gap-2'>
                      <CircleDot className='h-3.5 w-3.5' />
                      Updated {updatedAtLabel}
                    </span>
                    <span className='inline-flex items-center gap-2'>
                      <Link2 className='h-3.5 w-3.5' />
                      {upstreamCount + downstreamCount} total links
                    </span>
                  </div>
                </div>

                <div className='grid gap-3'>
                  <Card className='bg-muted/40 space-y-3 border-0 px-4 py-3'>
                    <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                      Status & Priority
                    </p>
                    {isEditing ? (
                      <div className='grid grid-cols-2 gap-2'>
                        <Select
                          value={draft.status}
                          onValueChange={(value) =>
                            setDraft((prev) => ({ ...prev, status: value }))
                          }
                        >
                          <SelectTrigger className='h-8 text-xs'>
                            <SelectValue placeholder='Status' />
                          </SelectTrigger>
                          <SelectContent>
                            {statusOptions.map((status) => (
                              <SelectItem key={status} value={status}>
                                {status.replace('_', ' ')}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Select
                          value={draft.priority}
                          onValueChange={(value) =>
                            setDraft((prev) => ({ ...prev, priority: value }))
                          }
                        >
                          <SelectTrigger className='h-8 text-xs'>
                            <SelectValue placeholder='Priority' />
                          </SelectTrigger>
                          <SelectContent>
                            {priorityOptions.map((priority) => (
                              <SelectItem key={priority} value={priority}>
                                {priority}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    ) : (
                      <div className='flex items-center gap-2'>
                        <Badge
                          className={cn(
                            'text-[10px] font-black uppercase tracking-widest',
                            statusColors[displayStatus],
                          )}
                        >
                          {displayStatus.replace('_', ' ')}
                        </Badge>
                        <Badge
                          className={cn(
                            'text-[10px] font-black uppercase tracking-widest',
                            priorityColors[displayPriority || 'medium'],
                          )}
                        >
                          {displayPriority || 'medium'}
                        </Badge>
                      </div>
                    )}
                  </Card>
                  <Card className='bg-muted/40 border-0 px-4 py-3'>
                    <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                      Owner
                    </p>
                    <div className='mt-2 flex items-center gap-2'>
                      <div className='bg-primary/10 flex h-7 w-7 items-center justify-center rounded-full'>
                        <User className='text-primary h-3 w-3' />
                      </div>
                      {isEditing ? (
                        <Input
                          value={draft.owner}
                          onChange={(event) =>
                            setDraft((prev) => ({
                              ...prev,
                              owner: event.target.value,
                            }))
                          }
                          placeholder='Owner name'
                          className='h-8 text-xs'
                        />
                      ) : (
                        <span className='text-xs font-bold'>{item.owner || 'Unassigned'}</span>
                      )}
                    </div>
                  </Card>
                  <Card className='bg-muted/40 border-0 px-4 py-3'>
                    <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                      Version & Perspective
                    </p>
                    <div className='mt-2 flex items-center justify-between text-xs font-bold'>
                      <span>v{item.version}</span>
                      <span className='text-muted-foreground'>{item.perspective || 'default'}</span>
                    </div>
                  </Card>
                  <Card className='bg-muted/40 border-0 px-4 py-3'>
                    <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                      Canonical & Parent
                    </p>
                    <div className='mt-2 flex items-center justify-between text-xs font-bold'>
                      <span className='truncate'>{item.canonicalId || '—'}</span>
                      <span className='text-muted-foreground'>
                        {item.parentId ? item.parentId.slice(0, 8) : 'Root'}
                      </span>
                    </div>
                  </Card>
                </div>
              </div>
            </div>
          </Card>

          <div className='grid grid-cols-1 gap-8 lg:grid-cols-[1.6fr_1fr]'>
            <div className='space-y-8'>
              <Card className='bg-card/50 border-0 shadow-lg shadow-slate-950/5'>
                <div className='space-y-6 p-6'>
                  <div className='flex items-center justify-between'>
                    <div className='space-y-1'>
                      <p className='text-muted-foreground text-[10px] font-black tracking-[0.3em] uppercase'>
                        Traceability
                      </p>
                      <h2 className='text-lg font-black tracking-tight'>Relationship map</h2>
                    </div>
                    <Button
                      size='sm'
                      className='gap-2 rounded-full'
                      onClick={() => {
                        if (sourceLinks.length === 0 && targetLinks.length === 0) {
                          toast.info('No relationships to analyze');
                        } else {
                          const total = sourceLinks.length + targetLinks.length;
                          toast.success(`Analyzed ${total} relationships`);
                        }
                      }}
                    >
                      <Sparkles className='h-4 w-4' />
                      Run analysis
                    </Button>
                  </div>

                  <div className='grid grid-cols-1 gap-4 sm:grid-cols-3'>
                    <Card className='bg-muted/40 space-y-2 border-0 p-4'>
                      <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                        Upstream
                      </p>
                      <p className='text-2xl font-black'>{upstreamCount}</p>
                      <p className='text-muted-foreground text-xs'>Dependencies tied in</p>
                    </Card>
                    <Card className='bg-muted/40 space-y-2 border-0 p-4'>
                      <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                        Downstream
                      </p>
                      <p className='text-2xl font-black'>{downstreamCount}</p>
                      <p className='text-muted-foreground text-xs'>Impacted items</p>
                    </Card>
                    <Card className='bg-muted/40 space-y-2 border-0 p-4'>
                      <p className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                        Metadata
                      </p>
                      <p className='text-2xl font-black'>{metadataCount}</p>
                      <p className='text-muted-foreground text-xs'>Context signals</p>
                    </Card>
                  </div>

                  <Separator />

                  <Tabs defaultValue='specs' className='w-full'>
                    <TabsList className='bg-muted/60 rounded-xl p-1'>
                      <TabsTrigger value='specs' className='rounded-lg'>
                        Specifications
                      </TabsTrigger>
                      <TabsTrigger value='links' className='rounded-lg'>
                        Relationships
                      </TabsTrigger>
                      <TabsTrigger value='metadata' className='rounded-lg'>
                        Metadata
                      </TabsTrigger>
                    </TabsList>

                    <TabsContent value='specs' className='space-y-4 pt-6'>
                      {item.projectId && itemId && (
                        <ItemSpecTabs
                          projectId={item.projectId}
                          itemId={itemId}
                          itemType={item.type}
                          onCreateSpec={(specType) => {}}
                        />
                      )}
                    </TabsContent>

                    <TabsContent value='links' className='space-y-6 pt-6'>
                      <div className='grid grid-cols-1 gap-6 md:grid-cols-2'>
                        <Card className='bg-muted/40 space-y-4 border-0 p-5'>
                          <div className='flex items-center gap-2'>
                            <div className='flex h-9 w-9 items-center justify-center rounded-xl bg-orange-500/15'>
                              <ArrowLeft className='h-4 w-4 text-orange-600' />
                            </div>
                            <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
                              Upstream
                            </h3>
                          </div>
                          <div className='space-y-3'>
                            {targetLinks.length > 0 ? (
                              targetLinks.map((link) => (
                                <Link
                                  key={link.id}
                                  to={buildItemLink(link.sourceId)}
                                  className='border-border/50 bg-card/80 hover:bg-muted/50 flex items-center gap-4 rounded-xl border px-4 py-3 shadow-sm transition-all hover:border-orange-500/30 hover:shadow-md'
                                >
                                  <div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-orange-500/10'>
                                    <ArrowLeft className='h-5 w-5 text-orange-500' />
                                  </div>
                                  <div className='min-w-0 flex-1 space-y-1'>
                                    <Badge
                                      variant='secondary'
                                      className='text-[10px] font-semibold tracking-wider uppercase'
                                    >
                                      {link.type}
                                    </Badge>
                                    <p
                                      className='text-foreground truncate font-mono text-xs font-medium'
                                      title={link.sourceId}
                                    >
                                      {link.sourceId.slice(0, 8)}…
                                    </p>
                                  </div>
                                  <span className='text-muted-foreground shrink-0 text-[10px] font-semibold uppercase'>
                                    View
                                  </span>
                                  <ExternalLink className='text-muted-foreground h-4 w-4 shrink-0' />
                                </Link>
                              ))
                            ) : (
                              <div className='border-border/50 bg-background/50 rounded-xl border-2 border-dashed py-8 text-center'>
                                <p className='text-muted-foreground text-sm font-medium'>
                                  No upstream dependencies
                                </p>
                                <p className='text-muted-foreground/80 mt-1 text-xs'>
                                  Links from other items will appear here
                                </p>
                              </div>
                            )}
                          </div>
                        </Card>
                        <Card className='bg-muted/40 space-y-4 border-0 p-5'>
                          <div className='flex items-center gap-2'>
                            <div className='flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500/15'>
                              <ArrowLeft className='h-4 w-4 rotate-180 text-sky-600' />
                            </div>
                            <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
                              Downstream
                            </h3>
                          </div>
                          <div className='space-y-3'>
                            {sourceLinks.length > 0 ? (
                              sourceLinks.map((link) => (
                                <Link
                                  key={link.id}
                                  to={buildItemLink(link.targetId)}
                                  className='border-border/50 bg-card/80 hover:bg-muted/50 flex items-center gap-4 rounded-xl border px-4 py-3 shadow-sm transition-all hover:border-sky-500/30 hover:shadow-md'
                                >
                                  <div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-sky-500/10'>
                                    <ArrowLeft className='h-5 w-5 rotate-180 text-sky-500' />
                                  </div>
                                  <div className='min-w-0 flex-1 space-y-1'>
                                    <Badge
                                      variant='secondary'
                                      className='text-[10px] font-semibold tracking-wider uppercase'
                                    >
                                      {link.type}
                                    </Badge>
                                    <p
                                      className='text-foreground truncate font-mono text-xs font-medium'
                                      title={link.targetId}
                                    >
                                      {link.targetId.slice(0, 8)}…
                                    </p>
                                  </div>
                                  <span className='text-muted-foreground shrink-0 text-[10px] font-semibold uppercase'>
                                    View
                                  </span>
                                  <ExternalLink className='text-muted-foreground h-4 w-4 shrink-0' />
                                </Link>
                              ))
                            ) : (
                              <div className='border-border/50 bg-background/50 rounded-xl border-2 border-dashed py-8 text-center'>
                                <p className='text-muted-foreground text-sm font-medium'>
                                  No downstream impact
                                </p>
                                <p className='text-muted-foreground/80 mt-1 text-xs'>
                                  Items that depend on this will appear here
                                </p>
                              </div>
                            )}
                          </div>
                        </Card>
                      </div>
                    </TabsContent>

                    <TabsContent value='metadata' className='space-y-6 pt-6'>
                      <div className='flex flex-wrap items-center gap-3'>
                        <Input
                          value={metadataSearch}
                          onChange={(event) => setMetadataSearch(event.target.value)}
                          placeholder='Search metadata keys or values...'
                          className='h-10 max-w-sm rounded-xl'
                        />
                        <Badge
                          variant='secondary'
                          className='px-3 py-1 text-[10px] font-semibold tracking-widest uppercase'
                        >
                          {filteredMetadata.length} entries
                        </Badge>
                      </div>
                      {integrationEntries.length > 0 && (
                        <div className='space-y-4'>
                          <div className='flex items-center gap-2'>
                            <div className='flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/15'>
                              <Orbit className='h-4 w-4 text-amber-600' />
                            </div>
                            <span className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
                              Integration context
                            </span>
                          </div>
                          <div className='grid grid-cols-2 gap-3 md:grid-cols-3'>
                            {integrationEntries.map(([key, value]) => (
                              <Card
                                key={key}
                                className='border-border/50 bg-card/80 border p-4 shadow-sm transition-shadow hover:shadow-md'
                              >
                                <p className='text-muted-foreground mb-2 text-[10px] font-black tracking-wider uppercase'>
                                  {key.replaceAll('_', ' ')}
                                </p>
                                <p
                                  className='text-foreground truncate text-sm font-semibold'
                                  title={formatValue(value)}
                                >
                                  {formatValue(value)}
                                </p>
                              </Card>
                            ))}
                          </div>
                        </div>
                      )}

                      {generalMetadata.length > 0 ? (
                        <div className='space-y-4'>
                          <span className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
                            Custom metadata
                          </span>
                          <div className='grid grid-cols-2 gap-3 md:grid-cols-3'>
                            {generalMetadata.map(([key, value]) => (
                              <Card
                                key={key}
                                className='border-border/50 bg-card/80 border p-4 shadow-sm transition-shadow hover:shadow-md'
                              >
                                <p className='text-muted-foreground mb-2 text-[10px] font-black tracking-wider uppercase'>
                                  {key.replaceAll('_', ' ')}
                                </p>
                                <p
                                  className='text-foreground truncate text-sm font-semibold'
                                  title={formatValue(value)}
                                >
                                  {formatValue(value)}
                                </p>
                              </Card>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <Card className='border-border/50 bg-muted/20 border-2 border-dashed p-10 text-center'>
                          <p className='text-muted-foreground text-sm font-medium'>
                            No custom metadata defined
                          </p>
                          <p className='text-muted-foreground/80 mt-1 text-xs'>
                            Add metadata to attach context to this item
                          </p>
                        </Card>
                      )}
                    </TabsContent>
                  </Tabs>
                </div>
              </Card>
            </div>

            <div className='space-y-6'>
              <Card className='bg-card/60 space-y-4 border-0 p-6 shadow-lg shadow-slate-950/5'>
                <div className='flex items-center justify-between'>
                  <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
                    Signal stack
                  </h3>
                  <ShieldAlert className='h-4 w-4 text-orange-500' />
                </div>
                <div className='flex items-center gap-3'>
                  <div className='flex h-10 w-10 items-center justify-center rounded-2xl bg-amber-500/15'>
                    <Target className='h-4 w-4 text-amber-600' />
                  </div>
                  <div>
                    <p className='text-2xl font-black'>{upstreamCount + downstreamCount}</p>
                    <p className='text-muted-foreground text-xs'>
                      Connected items affecting delivery
                    </p>
                  </div>
                </div>
                <Button
                  variant='outline'
                  size='sm'
                  className='w-full gap-2'
                  onClick={() => {
                    const impactCount = upstreamCount + downstreamCount;
                    if (impactCount === 0) {
                      toast.info('No impact relationships detected');
                    } else {
                      toast.success(`Impact analysis: ${impactCount} affected items`);
                    }
                  }}
                >
                  <Target className='h-4 w-4' />
                  Open impact analysis
                </Button>
              </Card>

              <Card className='bg-muted/40 space-y-4 border-0 p-6 shadow-sm'>
                <div className='flex items-center gap-2'>
                  <div className='flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500/15'>
                    <GitBranch className='h-4 w-4 text-sky-600' />
                  </div>
                  <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
                    Dimensions
                  </h3>
                </div>
                {dimensionEntries.length > 0 ? (
                  <div className='space-y-3'>
                    {dimensionEntries.map(([label, value]) => (
                      <div
                        key={label}
                        className='border-border/40 bg-card/60 flex items-center justify-between rounded-xl border px-4 py-3 shadow-sm'
                      >
                        <span className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                          {label}
                        </span>
                        <span
                          className='text-foreground max-w-[60%] truncate text-sm font-semibold'
                          title={formatValue(value)}
                        >
                          {formatValue(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className='border-border/50 bg-background/50 text-muted-foreground rounded-xl border border-dashed py-4 text-center text-xs italic'>
                    No dimensions configured.
                  </p>
                )}
              </Card>

              <Card className='bg-card/60 space-y-4 border-0 p-6 shadow-lg shadow-slate-950/5'>
                <div className='flex items-center justify-between'>
                  <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
                    References
                  </h3>
                  <BookText className='h-4 w-4 text-emerald-500' />
                </div>
                <div className='space-y-3 text-xs'>
                  <div className='flex items-start gap-2'>
                    <Code2 className='h-4 w-4 text-slate-500' />
                    <div>
                      <p className='font-bold'>Code reference</p>
                      <p className='text-muted-foreground'>
                        {item.codeRef
                          ? `${item.codeRef.filePath} · ${item.codeRef.symbolName}`
                          : 'No code reference attached'}
                      </p>
                    </div>
                  </div>
                  <div className='flex items-start gap-2'>
                    <BookText className='h-4 w-4 text-slate-500' />
                    <div>
                      <p className='font-bold'>Documentation</p>
                      <p className='text-muted-foreground'>
                        {item.docRef
                          ? `${item.docRef.documentTitle} · ${item.docRef.sectionTitle || item.docRef.documentPath}`
                          : 'No doc reference attached'}
                      </p>
                    </div>
                  </div>
                </div>
              </Card>

              <Card className='bg-muted/40 space-y-4 border-0 p-6 shadow-sm'>
                <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
                  Change log
                </h3>
                {timelineEvents.length > 0 ? (
                  <div className='relative space-y-0'>
                    {/* Vertical line */}
                    <div className='bg-border absolute top-2 bottom-2 left-[11px] w-px' />
                    {timelineEvents.map((event) => (
                      <div
                        key={`${event.label}-${event.timestamp}`}
                        className='relative flex items-start gap-4 pb-6 last:pb-0'
                      >
                        <div className='border-primary/40 bg-primary/10 relative z-10 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2'>
                          <div className='bg-primary h-1.5 w-1.5 rounded-full' />
                        </div>
                        <div className='border-border/40 bg-card/60 min-w-0 flex-1 rounded-xl border px-4 py-3 shadow-sm'>
                          <p className='text-foreground text-sm font-semibold'>{event.label}</p>
                          {event.detail && (
                            <p className='text-muted-foreground mt-1 text-xs'>{event.detail}</p>
                          )}
                          <p className='text-muted-foreground mt-2 text-[10px] font-medium tracking-wider uppercase'>
                            {new Date(event.timestamp).toLocaleDateString(undefined, {
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                              month: 'short',
                              year: 'numeric',
                            })}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className='border-border/50 bg-background/50 text-muted-foreground rounded-xl border border-dashed py-6 text-center text-xs italic'>
                    No change events recorded.
                  </p>
                )}
              </Card>

              <Card className='bg-muted/40 space-y-4 border-0 p-6 shadow-sm'>
                <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
                  Activity timeline
                </h3>
                <div className='space-y-3'>
                  <div className='border-border/40 bg-card/60 flex items-center justify-between rounded-xl border px-4 py-3 shadow-sm'>
                    <span className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                      Created
                    </span>
                    <span className='text-foreground text-sm font-semibold'>{createdAtLabel}</span>
                  </div>
                  <div className='border-border/40 bg-card/60 flex items-center justify-between rounded-xl border px-4 py-3 shadow-sm'>
                    <span className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                      Updated
                    </span>
                    <span className='text-foreground text-sm font-semibold'>{updatedAtLabel}</span>
                  </div>
                  <div className='border-border/40 bg-card/60 flex items-center justify-between rounded-xl border px-4 py-3 shadow-sm'>
                    <span className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                      System lag
                    </span>
                    <span className='text-foreground inline-flex items-center gap-1.5 text-sm font-semibold'>
                      <Timer className='text-primary h-3.5 w-3.5' />
                      recent
                    </span>
                  </div>
                </div>
              </Card>

              <Card className='bg-primary text-primary-foreground shadow-primary/20 space-y-3 border-0 p-6 shadow-lg'>
                <div className='flex items-center gap-2 text-xs font-black tracking-widest uppercase opacity-80'>
                  <Sparkles className='h-4 w-4' />
                  Insight snapshot
                </div>
                <p className='text-sm leading-relaxed font-medium italic'>
                  "This item touches {downstreamCount} downstream links, {upstreamCount} upstream
                  dependencies, and {metadataCount} metadata signals. Lock a baseline before major
                  edits."
                </p>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

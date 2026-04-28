import { Link } from '@tanstack/react-router';
import {
  Activity,
  BarChart3,
  Edit,
  ExternalLink,
  Folder,
  Layers,
  LayoutGrid,
  List,
  MoreVertical,
  Pin,
  Plus,
  Search,
  Trash2,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from 'recharts';
import { toast } from 'sonner';

import type { DashboardProjectStats } from '@/hooks/useDashboardSummary';

import { useDashboardSummary } from '@/hooks/useDashboardSummary';
import { getProjectDisplayName } from '@/lib/project-name-utils';
import { cn } from '@/lib/utils';
import {
  Badge,
  Button,
  Card,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  Input,
  Progress,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Skeleton,
  Tabs,
  TabsList,
  TabsTrigger,
} from '@tracertm/ui';

import { useDeleteProject, useProjects } from '../hooks/useProjects';

interface DashboardViewProps {
  systemStatus?: {
    status?: string;
    mcp?: { baseUrl?: string | null };
  };
}

type DashboardStats = Record<string, DashboardProjectStats>;
type ViewMode = 'grid' | 'list';
type SortBy = 'name' | 'items' | 'progress';

const VIEW_MODES: readonly ViewMode[] = ['grid', 'list'];
const SORT_OPTIONS: readonly SortBy[] = ['name', 'items', 'progress'];
const PROJECT_CREATE_SEARCH = { action: 'create' } as const;

function isViewMode(value: unknown): value is ViewMode {
  return typeof value === 'string' && VIEW_MODES.includes(value as ViewMode);
}

function isSortBy(value: unknown): value is SortBy {
  return typeof value === 'string' && SORT_OPTIONS.includes(value as SortBy);
}

export function DashboardView({ systemStatus }: DashboardViewProps) {
  const { data: projects, isLoading: projectsLoading } = useProjects();
  const deleteProject = useDeleteProject();
  const { data: summaryData, isLoading: summaryLoading } = useDashboardSummary();
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortBy>('name');
  const [pinnedProjectId, setPinnedProjectId] = useState<string | null>(null);

  const [slot1Tab, setSlot1Tab] = useState('distribution');
  const [slot2Tab, setSlot2Tab] = useState('status');

  // Ensure projects is always an array - memoize to prevent infinite loops
  const projectsArray = useMemo(() => (Array.isArray(projects) ? projects : []), [projects]);

  // Derive dashboard stats from the summary endpoint response
  const dashboardStats: DashboardStats = useMemo(
    () => summaryData?.perProject ?? {},
    [summaryData],
  );

  const projectItemCounts: Record<string, number> = useMemo(() => {
    if (!summaryData?.perProject) {
      return {};
    }
    const counts: Record<string, number> = {};
    for (const [id, stats] of Object.entries(summaryData.perProject)) {
      counts[id] = stats.totalCount;
    }
    return counts;
  }, [summaryData]);

  // Set default pinned project
  useEffect(() => {
    if (projectsArray.length > 0 && !pinnedProjectId) {
      const firstProject = projectsArray[0];
      if (firstProject?.id) {
        setPinnedProjectId(firstProject.id);
      }
    }
  }, [projectsArray, pinnedProjectId]);

  const statusData = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const stats of Object.values(dashboardStats)) {
      for (const [status, count] of Object.entries(stats.statusCounts)) {
        counts[status] = (counts[status] ?? 0) + count;
      }
    }
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [dashboardStats]);

  const typeData = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const stats of Object.values(dashboardStats)) {
      for (const [type, count] of Object.entries(stats.typeCounts)) {
        counts[type] = (counts[type] ?? 0) + count;
      }
    }
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [dashboardStats]);

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  const projectsWithStats = useMemo(
    () =>
      projectsArray.map((project) => {
        const stats = dashboardStats[project.id];
        const total = stats?.totalCount ?? 0;
        const completed = stats?.completedCount ?? 0;
        const progress = total > 0 ? (completed / total) * 100 : 0;
        return {
          ...project,
          displayName: getProjectDisplayName(project),
          itemCount: projectItemCounts[project.id] ?? total,
          progress,
        };
      }),
    [projectsArray, dashboardStats, projectItemCounts],
  );

  const pinnedProject = useMemo(
    () => projectsWithStats.find((p) => p.id === pinnedProjectId) ?? projectsWithStats[0],
    [projectsWithStats, pinnedProjectId],
  );

  const pinnedProjectDetails = useMemo(() => {
    if (!pinnedProject) {
      return [];
    }
    const typeCounts = dashboardStats[pinnedProject.id]?.typeCounts ?? {};
    const types = ['requirement', 'feature', 'test', 'task', 'bug'];
    const maxCount = Math.max(...types.map((t) => typeCounts[t] ?? 0), 10);
    return types.map((type) => ({
      A: typeCounts[type] ?? 0,
      fullMark: maxCount,
      subject: type.charAt(0).toUpperCase() + type.slice(1),
    }));
  }, [pinnedProject, dashboardStats]);

  const filteredProjects = useMemo(() => {
    let result = projectsWithStats.filter((p) =>
      (p.displayName || p.name).toLowerCase().includes(searchQuery.toLowerCase()),
    );

    result = [...result].toSorted((a, b) => {
      if (sortBy === 'name') {
        const aName = a.displayName || a.name;
        const bName = b.displayName || b.name;
        return aName.localeCompare(bName);
      }
      if (sortBy === 'items') {
        return b.itemCount - a.itemCount;
      }
      if (sortBy === 'progress') {
        return b.progress - a.progress;
      }
      return 0;
    });

    return result;
  }, [projectsWithStats, searchQuery, sortBy]);

  const handleSortByChange = (value: unknown): void => {
    if (isSortBy(value)) {
      setSortBy(value);
    }
  };

  const handleViewModeChange = (value: unknown): void => {
    if (isViewMode(value)) {
      setViewMode(value);
    }
  };

  if (projectsLoading || summaryLoading) {
    return (
      <div className='space-y-6 p-6'>
        <div className='flex items-center justify-between'>
          <Skeleton className='h-10 w-48' />
          <Skeleton className='h-10 w-32' />
        </div>
        <div className='grid grid-cols-1 gap-6 md:grid-cols-3'>
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className='h-64' />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className='animate-in-fade-up mx-auto max-w-[1600px] space-y-8 p-6'>
      {/* Header */}
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-2xl font-bold tracking-tight'>Traceability Dashboard</h1>
          <p className='text-muted-foreground text-sm'>
            Monitor project health and system-wide traceability status.
          </p>
          <div className='mt-3 flex flex-wrap items-center gap-2'>
            <Badge variant='outline' className='text-xs'>
              System: {systemStatus?.status ?? 'healthy'}
            </Badge>
            <Badge
              variant={systemStatus?.mcp?.baseUrl ? 'default' : 'secondary'}
              className='text-xs'
            >
              MCP: {systemStatus?.mcp?.baseUrl ? 'connected' : 'not configured'}
            </Badge>
            {systemStatus?.mcp?.baseUrl ? (
              <Button
                variant='outline'
                size='sm'
                className='h-7 px-2 text-xs'
                onClick={() => {
                  window.open(systemStatus.mcp?.baseUrl ?? '#', '_blank');
                }}
              >
                Open MCP
              </Button>
            ) : null}
          </div>
        </div>
      </div>

      {/* Visual Insights Section */}
      <div className='grid grid-cols-1 gap-6 lg:grid-cols-3'>
        {/* Slot 1: Large Widget (Distribution / Pinned Project Detail) */}
        <Card className='bg-card/50 col-span-1 overflow-hidden border-none p-0 shadow-sm lg:col-span-2'>
          <Tabs value={slot1Tab} onValueChange={setSlot1Tab} className='w-full'>
            <div className='flex items-center justify-between px-6 pt-6'>
              <div className='flex items-center gap-3'>
                <div className='bg-primary/10 flex h-8 w-8 items-center justify-center rounded-lg'>
                  {slot1Tab === 'distribution' ? (
                    <BarChart3 className='text-primary h-4 w-4' />
                  ) : (
                    <Pin className='text-primary h-4 w-4' />
                  )}
                </div>
                <h3 className='text-muted-foreground/80 text-sm font-bold tracking-wider uppercase'>
                  {slot1Tab === 'distribution'
                    ? 'Global Distribution'
                    : `Project Focus: ${pinnedProject?.displayName ?? pinnedProject?.name}`}
                </h3>
              </div>
              <TabsList className='bg-muted/50'>
                <TabsTrigger
                  value='distribution'
                  className='hover:bg-muted/70 cursor-pointer text-xs transition-colors'
                >
                  Network
                </TabsTrigger>
                <TabsTrigger
                  value='focus'
                  className='hover:bg-muted/70 cursor-pointer text-xs transition-colors'
                >
                  Pinned
                </TabsTrigger>
              </TabsList>
            </div>

            <div className='h-[320px] p-6'>
              {slot1Tab === 'distribution' ? (
                <ResponsiveContainer width='100%' height='100%'>
                  <BarChart data={projectsWithStats.slice(0, 12)}>
                    <CartesianGrid
                      strokeDasharray='3 3'
                      vertical={false}
                      stroke='hsl(var(--muted)/0.3)'
                    />
                    <XAxis
                      dataKey='displayName'
                      fontSize={10}
                      tickLine={false}
                      axisLine={false}
                      tick={{ fill: 'hsl(var(--muted-foreground))' }}
                    />
                    <YAxis
                      fontSize={10}
                      tickLine={false}
                      axisLine={false}
                      tick={{ fill: 'hsl(var(--muted-foreground))' }}
                    />
                    <RechartsTooltip
                      cursor={{ fill: 'hsl(var(--muted)/0.2)' }}
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        borderColor: 'hsl(var(--border))',
                        borderRadius: '8px',
                        fontSize: '12px',
                      }}
                    />
                    <Bar dataKey='itemCount' fill='hsl(var(--primary))' radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className='grid h-full grid-cols-1 gap-4 md:grid-cols-2'>
                  <div className='h-full'>
                    <ResponsiveContainer width='100%' height='100%'>
                      <RadarChart cx='50%' cy='50%' outerRadius='80%' data={pinnedProjectDetails}>
                        <PolarGrid stroke='hsl(var(--muted))' />
                        <PolarAngleAxis
                          dataKey='subject'
                          fontSize={10}
                          tick={{ fill: 'hsl(var(--muted-foreground))' }}
                        />
                        <Radar
                          name={pinnedProject?.displayName ?? pinnedProject?.name}
                          dataKey='A'
                          stroke='hsl(var(--primary))'
                          fill='hsl(var(--primary))'
                          fillOpacity={0.6}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className='flex flex-col justify-center space-y-4 px-4'>
                    <div>
                      <div className='mb-1 flex justify-between text-xs'>
                        <span className='text-muted-foreground'>Overall Completion</span>
                        <span className='font-bold'>
                          {Math.round(pinnedProject?.progress ?? 0)}%
                        </span>
                      </div>
                      <Progress value={pinnedProject?.progress} className='h-2' />
                    </div>
                    <div className='grid grid-cols-2 gap-4'>
                      <div className='bg-muted/30 border-border/50 rounded-lg border p-3'>
                        <div className='text-muted-foreground mb-1 text-[10px] font-bold uppercase'>
                          Total Items
                        </div>
                        <div className='text-xl font-bold'>{pinnedProject?.itemCount}</div>
                      </div>
                      <div className='bg-muted/30 border-border/50 rounded-lg border p-3'>
                        <div className='text-muted-foreground mb-1 text-[10px] font-bold uppercase'>
                          Activity
                        </div>
                        <div className='text-xl font-bold text-green-500'>High</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </Tabs>
        </Card>

        {/* Slot 2: Smaller Widget (Status / Priority / Type) */}
        <Card className='bg-card/50 overflow-hidden border-none p-0 shadow-sm'>
          <Tabs value={slot2Tab} onValueChange={setSlot2Tab} className='w-full'>
            <div className='flex items-center justify-between px-6 pt-6'>
              <div className='flex items-center gap-3'>
                <div className='bg-primary/10 flex h-8 w-8 items-center justify-center rounded-lg'>
                  <Layers className='text-primary h-4 w-4' />
                </div>
                <h3 className='text-muted-foreground/80 text-sm font-bold tracking-wider uppercase'>
                  Metrics
                </h3>
              </div>
              <TabsList className='bg-muted/50'>
                <TabsTrigger
                  value='status'
                  className='hover:bg-muted/70 cursor-pointer text-xs transition-colors'
                >
                  Status
                </TabsTrigger>
                <TabsTrigger
                  value='type'
                  className='hover:bg-muted/70 cursor-pointer text-xs transition-colors'
                >
                  Type
                </TabsTrigger>
              </TabsList>
            </div>

            <div className='flex h-[320px] flex-col p-6'>
              <div className='flex-1'>
                <ResponsiveContainer width='100%' height='100%'>
                  <PieChart>
                    <Pie
                      data={slot2Tab === 'status' ? statusData : typeData}
                      cx='50%'
                      cy='50%'
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey='value'
                    >
                      {(slot2Tab === 'status' ? statusData : typeData).map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        borderColor: 'hsl(var(--border))',
                        borderRadius: '8px',
                        fontSize: '12px',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className='mt-4 grid grid-cols-2 gap-x-4 gap-y-1'>
                {(slot2Tab === 'status' ? statusData : typeData).slice(0, 6).map((entry, index) => (
                  <div key={entry.name} className='flex min-w-0 items-center gap-2'>
                    <div
                      className='h-1.5 w-1.5 shrink-0 rounded-full'
                      style={{
                        backgroundColor: COLORS[index % COLORS.length],
                      }}
                    />
                    <span className='text-muted-foreground truncate text-[10px] font-medium uppercase'>
                      {entry.name}
                    </span>
                    <span className='ml-auto text-[10px] font-bold'>{entry.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </Tabs>
        </Card>
      </div>

      {/* Projects Section */}
      <div className='space-y-4'>
        <div className='flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center'>
          <div className='flex items-center gap-2'>
            <Activity className='text-primary h-5 w-5' />
            <h2 className='text-lg font-bold tracking-tight'>Active Projects</h2>
          </div>
          <div className='flex w-full items-center gap-2 sm:w-auto'>
            <div className='relative flex-1 sm:w-64'>
              <Search className='text-muted-foreground absolute top-2.5 left-2.5 h-4 w-4' />
              <Input
                placeholder='Search projects...'
                className='bg-muted/50 h-9 border-none pl-9 focus-visible:ring-1'
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                }}
              />
            </div>
            <Select value={sortBy} onValueChange={handleSortByChange}>
              <SelectTrigger className='bg-muted/50 h-9 w-[130px] border-none'>
                <SelectValue placeholder='Sort by' />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='name' className='hover:bg-accent cursor-pointer'>
                  Name
                </SelectItem>
                <SelectItem value='items' className='hover:bg-accent cursor-pointer'>
                  Item Count
                </SelectItem>
                <SelectItem value='progress' className='hover:bg-accent cursor-pointer'>
                  Progress
                </SelectItem>
              </SelectContent>
            </Select>
            <Tabs value={viewMode} onValueChange={handleViewModeChange}>
              <TabsList className='bg-muted/50 h-9 p-0.5'>
                <TabsTrigger
                  value='grid'
                  className='hover:bg-muted/70 h-8 cursor-pointer px-2 transition-colors'
                >
                  <LayoutGrid className='h-4 w-4' />
                </TabsTrigger>
                <TabsTrigger
                  value='list'
                  className='hover:bg-muted/70 h-8 cursor-pointer px-2 transition-colors'
                >
                  <List className='h-4 w-4' />
                </TabsTrigger>
              </TabsList>
            </Tabs>
            <Link to='/projects' search={PROJECT_CREATE_SEARCH}>
              <Button size='sm' className='h-9 shadow-sm'>
                <Plus className='mr-2 h-4 w-4' />
                New Project
              </Button>
            </Link>
          </div>
        </div>

        {viewMode === 'grid' ? (
          <div className='stagger-children grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'>
            {filteredProjects.map((project) => {
              const handlePin = (e: React.MouseEvent) => {
                e.preventDefault();
                e.stopPropagation();
                const wasPinned = pinnedProjectId === project.id;
                setPinnedProjectId(wasPinned ? null : project.id);
                if (!wasPinned) {
                  toast.success(`Pinned ${project.displayName || project.name} to dashboard`);
                }
              };

              const handleDelete = async (e: React.MouseEvent) => {
                e.preventDefault();
                e.stopPropagation();
                const projectDisplayName = project.displayName || project.name;
                if (
                  !confirm(
                    `Are you sure you want to delete "${projectDisplayName}"? This action cannot be undone.`,
                  )
                ) {
                  return;
                }
                try {
                  await deleteProject.mutateAsync(project.id);
                  toast.success(`Project "${projectDisplayName}" deleted`);
                  if (pinnedProjectId === project.id) {
                    setPinnedProjectId(null);
                  }
                } catch {
                  toast.error('Failed to delete project');
                }
              };

              const handleEdit = (e: React.MouseEvent) => {};

              return (
                <div key={project.id} className='group relative'>
                  <Link to={`/projects/${project.id}`} className='cursor-pointer'>
                    <Card className='border-border/50 bg-card hover:bg-card/90 hover:border-primary/30 h-full border p-5 shadow-md transition-all hover:shadow-xl'>
                      {/* Pin button - top left */}
                      <button
                        onClick={handlePin}
                        className={cn(
                          'absolute top-3 left-3 p-1.5 rounded-lg transition-all z-10 cursor-pointer',
                          pinnedProjectId === project.id
                            ? 'bg-primary text-primary-foreground opacity-100 hover:bg-primary/90'
                            : 'bg-muted/50 text-muted-foreground opacity-0 group-hover:opacity-100 hover:bg-primary/20 hover:text-primary',
                        )}
                        title={pinnedProjectId === project.id ? 'Unpin project' : 'Pin project'}
                      >
                        <Pin
                          className={cn(
                            'h-3.5 w-3.5',
                            pinnedProjectId === project.id && 'fill-current',
                          )}
                        />
                      </button>

                      {/* 3-dot menu - top right */}
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <span>
                            <Button
                              variant='ghost'
                              size='icon'
                              className='text-muted-foreground hover:text-foreground hover:bg-muted absolute top-3 right-3 z-10 h-7 w-7 opacity-0 transition-all group-hover:opacity-100'
                              onClick={(e) => {
                                e.stopPropagation();
                              }}
                            >
                              <MoreVertical className='h-4 w-4' />
                              <span className='sr-only'>Project options</span>
                            </Button>
                          </span>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align='end' className='w-48'>
                          <DropdownMenuItem
                            onClick={(e) => {}}
                            className='hover:bg-accent hover:text-accent-foreground cursor-pointer gap-2 transition-colors'
                          >
                            <ExternalLink className='h-4 w-4' />
                            Open Project
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEdit(e);
                            }}
                            className='hover:bg-accent hover:text-accent-foreground cursor-pointer gap-2 transition-colors'
                          >
                            <Edit className='h-4 w-4' />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            onClick={(e) => {}}
                            className='text-destructive focus:text-destructive focus:bg-destructive/10 hover:bg-destructive/10 hover:text-destructive cursor-pointer gap-2 transition-colors'
                          >
                            <Trash2 className='h-4 w-4' />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>

                      <div className='pt-2'>
                        <div className='mb-3 flex items-start justify-between'>
                          <h3 className='group-hover:text-primary flex-1 truncate pr-2 text-sm font-bold transition-colors'>
                            {project.displayName || project.name}
                          </h3>
                          <Badge
                            variant='secondary'
                            className='ml-2 h-4 shrink-0 px-1.5 text-[9px] font-bold tracking-tighter uppercase'
                          >
                            {project.itemCount}
                          </Badge>
                        </div>
                        <p className='text-muted-foreground mb-4 line-clamp-2 h-8 text-xs leading-relaxed'>
                          {project.description ??
                            'System generated project for traceability management.'}
                        </p>
                        <div className='space-y-2'>
                          <div className='text-muted-foreground/60 flex justify-between text-[10px] font-bold tracking-widest uppercase'>
                            <span>Coverage</span>
                            <span>{Math.round(project.progress)}%</span>
                          </div>
                          <Progress value={project.progress} className='bg-muted h-1.5' />
                        </div>
                      </div>
                    </Card>
                  </Link>
                </div>
              );
            })}
          </div>
        ) : (
          <Card className='border-border/50 bg-card/50 divide-y overflow-hidden border'>
            {filteredProjects.map((project) => {
              const handlePin = (e: React.MouseEvent) => {
                e.preventDefault();
                e.stopPropagation();
                const wasPinned = pinnedProjectId === project.id;
                setPinnedProjectId(wasPinned ? null : project.id);
                if (!wasPinned) {
                  toast.success(`Pinned ${project.displayName || project.name} to dashboard`);
                }
              };

              const handleDelete = async (e: React.MouseEvent) => {
                e.preventDefault();
                e.stopPropagation();
                const projectDisplayName = project.displayName || project.name;
                if (
                  !confirm(
                    `Are you sure you want to delete "${projectDisplayName}"? This action cannot be undone.`,
                  )
                ) {
                  return;
                }
                try {
                  await deleteProject.mutateAsync(project.id);
                  toast.success(`Project "${projectDisplayName}" deleted`);
                  if (pinnedProjectId === project.id) {
                    setPinnedProjectId(null);
                  }
                } catch {
                  toast.error('Failed to delete project');
                }
              };

              const handleEdit = (e: React.MouseEvent) => {};

              return (
                <div key={project.id} className='group relative'>
                  <Link to={`/projects/${project.id}`} className='block cursor-pointer'>
                    <div className='hover:bg-muted/50 flex items-center gap-6 p-4 transition-colors'>
                      {/* Pin button - left side */}
                      <button
                        onClick={handlePin}
                        className={cn(
                          'cursor-pointer',
                          'p-1.5 rounded-lg transition-all shrink-0',
                          pinnedProjectId === project.id
                            ? 'bg-primary text-primary-foreground opacity-100'
                            : 'bg-muted/50 text-muted-foreground opacity-0 group-hover:opacity-100 hover:bg-primary/20',
                        )}
                        title={pinnedProjectId === project.id ? 'Unpin project' : 'Pin project'}
                      >
                        <Pin
                          className={cn(
                            'h-3.5 w-3.5',
                            pinnedProjectId === project.id && 'fill-current',
                          )}
                        />
                      </button>

                      <div
                        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-colors ${
                          pinnedProjectId === project.id
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-primary/10 text-primary'
                        }`}
                      >
                        <Folder className='h-5 w-5' />
                      </div>
                      <div className='min-w-0 flex-1'>
                        <div className='flex items-center gap-2'>
                          <h3 className='truncate text-sm font-bold'>
                            {project.displayName || project.name}
                          </h3>
                        </div>
                        <p className='text-muted-foreground max-w-md truncate text-xs'>
                          {project.description}
                        </p>
                      </div>
                      <div className='hidden w-48 lg:block'>
                        <div className='text-muted-foreground/60 mb-1 flex justify-between text-[9px] font-bold uppercase'>
                          <span>Progress</span>
                          <span>{Math.round(project.progress)}%</span>
                        </div>
                        <Progress value={project.progress} className='h-1' />
                      </div>
                      <div className='min-w-[80px] shrink-0 text-right'>
                        <div className='text-xs font-black'>{project.itemCount}</div>
                        <div className='text-muted-foreground text-[9px] font-bold tracking-tighter uppercase'>
                          Items
                        </div>
                      </div>
                    </div>
                  </Link>
                  {/* 3-dot menu - right side */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <span>
                        <Button
                          variant='ghost'
                          size='icon'
                          className='text-muted-foreground hover:text-foreground hover:bg-muted absolute top-1/2 right-4 h-8 w-8 -translate-y-1/2 opacity-0 transition-all group-hover:opacity-100'
                          onClick={(e) => {
                            e.stopPropagation();
                          }}
                        >
                          <MoreVertical className='h-4 w-4' />
                          <span className='sr-only'>Project options</span>
                        </Button>
                      </span>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align='end' className='w-48'>
                      <DropdownMenuItem
                        onClick={(e) => {}}
                        className='hover:bg-accent hover:text-accent-foreground cursor-pointer gap-2 transition-colors'
                      >
                        <ExternalLink className='h-4 w-4' />
                        Open Project
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEdit(e);
                        }}
                        className='hover:bg-accent hover:text-accent-foreground cursor-pointer gap-2 transition-colors'
                      >
                        <Edit className='h-4 w-4' />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={(e) => {}}
                        className='text-destructive focus:text-destructive focus:bg-destructive/10 hover:bg-destructive/10 hover:text-destructive cursor-pointer gap-2 transition-colors'
                      >
                        <Trash2 className='h-4 w-4' />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              );
            })}
          </Card>
        )}

        {filteredProjects.length === 0 && (
          <div className='bg-muted/20 border-muted rounded-2xl border-2 border-dashed py-20 text-center'>
            <Folder className='text-muted-foreground mx-auto mb-4 h-16 w-16 opacity-20' />
            <p className='text-muted-foreground font-medium'>
              No projects match your current search criteria.
            </p>
            <Button
              variant='link'
              onClick={() => {
                setSearchQuery('');
              }}
              className='text-primary mt-2'
            >
              Clear search
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

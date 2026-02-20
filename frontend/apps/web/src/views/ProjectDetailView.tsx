import type { LucideIcon } from 'lucide-react';

import { Link, useNavigate, useParams } from '@tanstack/react-router';
import {
  Activity,
  AlertCircle,
  BarChart3,
  BookOpen,
  Bot,
  Calendar,
  ChevronDown,
  ChevronUp,
  Code,
  Database,
  Edit,
  ExternalLink,
  FileText,
  Globe,
  History,
  Layers,
  Layout,
  Network,
  Plus,
  Rocket,
  Shield,
  Target,
  TestTube,
  Zap,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { toast } from 'sonner';

import { getProjectDisplayName } from '@/lib/project-name-utils';
import { cn } from '@/lib/utils';
import { Badge, Button, Card, Progress, Skeleton } from '@tracertm/ui';

import { useItems } from '../hooks/useItems';
import { useLinks } from '../hooks/useLinks';
import { useProject } from '../hooks/useProjects';
import { useProjectStore } from '../stores/project-store';
import { AgentWorkflowView } from './AgentWorkflowView';

type Project = NonNullable<ReturnType<typeof useProject>['data']>;
type ItemsData = NonNullable<ReturnType<typeof useItems>['data']>;
type Item = ItemsData['items'][number];

interface SummaryCard {
  color: string;
  icon: LucideIcon;
  label: string;
  progress?: number;
  sub?: string;
  value: string;
}

interface Stats {
  byStatus: Record<string, number>;
  byType: Record<string, number>;
  completionRate: number;
  radarData: { A: number; fullMark: number; subject: string }[];
  typeData: { name: string; value: number }[];
}

interface ViewCard {
  color: string;
  href: string;
  icon: LucideIcon;
  label: string;
}

const EMPTY_ITEMS: Item[] = [];
const EMPTY_METADATA: Record<string, unknown> = {};
const AXIS_TICK = { fill: 'hsl(var(--muted-foreground))' };
const AXIS_FONT_SIZE = Number('10');
const BAR_RADIUS: [number, number, number, number] = [
  Number('4'),
  Number('4'),
  Number('0'),
  Number('0'),
];
const BAR_TOOLTIP_CURSOR = { fill: 'hsl(var(--muted)/0.2)' };
const BAR_TOOLTIP_STYLE = {
  backgroundColor: 'hsl(var(--card))',
  borderColor: 'hsl(var(--border))',
  borderRadius: '8px',
  fontSize: '12px',
};
const COMPLETION_PERCENT_BASE = Number('100');
const METADATA_PREVIEW_LIMIT = Number('3');
const PROJECT_ID_SHORT_LENGTH = Number('8');
const RADAR_FILL_OPACITY = Number('0.5');
const RADAR_FULL_MARK = Number('20');
const RECENT_ITEMS_LIMIT = Number('5');
const SKELETON_CARD_INDICES = [Number('0'), Number('1'), Number('2'), Number('3')];

const TYPE_ICON_MAP: Record<string, LucideIcon> = {
  api: Network,
  component: Layout,
  database: Database,
  deployment: Rocket,
  documentation: BookOpen,
  feature: Code,
  performance: Zap,
  requirement: FileText,
  security: Shield,
  test: TestTube,
};

const RADAR_TYPES = [
  { label: 'Reqs', type: 'requirement' },
  { label: 'Features', type: 'feature' },
  { label: 'Tests', type: 'test' },
  { label: 'Docs', type: 'documentation' },
  { label: 'Bugs', type: 'bug' },
] as const;

const VIEW_CARDS: ViewCard[] = [
  {
    color: 'text-blue-500',
    href: 'feature',
    icon: Layers,
    label: 'Features',
  },
  {
    color: 'text-purple-500',
    href: 'graph',
    icon: Network,
    label: 'Traceability',
  },
  {
    color: 'text-green-500',
    href: 'test',
    icon: TestTube,
    label: 'Test Suite',
  },
  {
    color: 'text-orange-500',
    href: 'api',
    icon: Globe,
    label: 'API Docs',
  },
  {
    color: 'text-cyan-500',
    href: 'database',
    icon: Database,
    label: 'Database',
  },
  {
    color: 'text-pink-500',
    href: 'matrix',
    icon: BarChart3,
    label: 'Matrix',
  },
  {
    color: 'text-amber-500',
    href: 'workflows',
    icon: Activity,
    label: 'Workflows',
  },
];

const formatProjectDate = (value: string | null | undefined): string => {
  if (value === null || value === undefined || value === '') {
    return '—';
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleDateString();
};

const buildTypeStats = (items: Item[]): Record<string, number> =>
  items.reduce<Record<string, number>>((acc, item) => {
    acc[item.type] = (acc[item.type] ?? 0) + 1;
    return acc;
  }, {});

const buildStatusStats = (items: Item[]): Record<string, number> =>
  items.reduce<Record<string, number>>((acc, item) => {
    acc[item.status] = (acc[item.status] ?? 0) + 1;
    return acc;
  }, {});

const buildRadarData = (byType: Record<string, number>) =>
  RADAR_TYPES.map((entry) => ({
    A: byType[entry.type] ?? 0,
    fullMark: RADAR_FULL_MARK,
    subject: entry.label,
  }));

const buildTypeData = (byType: Record<string, number>) =>
  Object.entries(byType).map(([name, value]) => ({ name, value }));

const useProjectIdParam = () => {
  const params = useParams({ strict: false });
  return params.projectId as string | undefined;
};

const useSyncCurrentProject = (project: Project | null) => {
  const setCurrentProject = useProjectStore((state) => state.setCurrentProject);
  const lastSyncedProjectIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (!project) {
      if (lastSyncedProjectIdRef.current !== null) {
        lastSyncedProjectIdRef.current = null;
        setCurrentProject(null);
      }
      return;
    }
    if (lastSyncedProjectIdRef.current === project.id) {
      return;
    }
    lastSyncedProjectIdRef.current = project.id;
    setCurrentProject(project);
  }, [project, setCurrentProject]);
};

const useProjectDetailData = (projectId: string | undefined) => {
  const safeProjectId = projectId ?? '';
  const projectQuery = useProject(safeProjectId);
  const itemsQuery = useItems({ projectId: safeProjectId });
  const linksQuery = useLinks({ projectId: safeProjectId });
  useSyncCurrentProject(projectQuery.data ?? null);

  return {
    items: itemsQuery.data?.items ?? EMPTY_ITEMS,
    itemsTotal: itemsQuery.data?.total ?? 0,
    linksTotal: linksQuery.data?.total ?? 0,
    loading: projectQuery.isLoading || itemsQuery.isLoading || linksQuery.isLoading,
    project: projectQuery.data ?? null,
    projectError: projectQuery.error,
  };
};

const useRecentItems = (items: Item[]) =>
  useMemo(() => items.slice(0, RECENT_ITEMS_LIMIT), [items]);

const useProjectStats = (items: Item[], itemsTotal: number): Stats =>
  useMemo(() => {
    const byStatus = buildStatusStats(items);
    const byType = buildTypeStats(items);
    const radarData = buildRadarData(byType);
    const typeData = buildTypeData(byType);
    const completionRate =
      itemsTotal > 0
        ? Math.round(((byStatus['done'] ?? 0) / itemsTotal) * COMPLETION_PERCENT_BASE)
        : 0;

    return { byStatus, byType, completionRate, radarData, typeData };
  }, [items, itemsTotal]);

const useSummaryCards = (stats: Stats, itemsTotal: number, linksTotal: number): SummaryCard[] =>
  useMemo(() => {
    const blockedCount = stats.byStatus['blocked'] ?? 0;
    return [
      {
        color: 'text-blue-500',
        icon: Target,
        label: 'Completion',
        progress: stats.completionRate,
        value: `${stats.completionRate}%`,
      },
      {
        color: 'text-purple-500',
        icon: Network,
        label: 'Active Links',
        sub: 'Traceability links',
        value: typeof linksTotal === 'number' ? linksTotal.toLocaleString() : String(linksTotal),
      },
      {
        color: 'text-green-500',
        icon: Layers,
        label: 'Total Items',
        sub: 'Across all types',
        value: typeof itemsTotal === 'number' ? itemsTotal.toLocaleString() : String(itemsTotal),
      },
      {
        color: blockedCount ? 'text-red-500' : 'text-emerald-500',
        icon: AlertCircle,
        label: 'Risk Level',
        sub: `${blockedCount} Blockers`,
        value: blockedCount ? 'High' : 'Low',
      },
    ];
  }, [itemsTotal, linksTotal, stats.byStatus, stats.completionRate]);

const useProjectDetailActions = (
  navigate: ReturnType<typeof useNavigate>,
  project: Project | null,
) => {
  const handleExport = useCallback(() => {
    toast.info('Exporting data...');
  }, []);

  const handleCreateFeature = useCallback(() => {
    if (!project) {
      return;
    }
    navigate({
      params: { projectId: project.id, viewType: 'feature' },
      search: { action: 'create' } as Record<string, string>,
      to: '/projects/$projectId/views/$viewType',
    });
  }, [navigate, project]);

  const handleOpenSettings = useCallback(() => {
    if (!project) {
      return;
    }
    navigate({ to: `/projects/${project.id}/settings` });
  }, [navigate, project]);

  const handleViewAll = useCallback(() => {
    if (!project) {
      return;
    }
    navigate({
      params: { projectId: project.id, viewType: 'feature' },
      to: '/projects/$projectId/views/$viewType',
    });
  }, [navigate, project]);

  return { handleCreateFeature, handleExport, handleOpenSettings, handleViewAll };
};

const ProjectDetailSkeleton = () => (
  <div className='animate-pulse space-y-8 p-6'>
    <Skeleton className='h-10 w-48' />
    <div className='grid grid-cols-1 gap-4 md:grid-cols-4'>
      {SKELETON_CARD_INDICES.map((value) => (
        <Skeleton key={value} className='h-32' />
      ))}
    </div>
    <Skeleton className='h-[400px] w-full' />
  </div>
);

const ProjectNotFound = ({ onBack }: { onBack: () => void }) => (
  <div className='flex flex-col items-center justify-center space-y-4 p-12'>
    <AlertCircle className='text-destructive h-12 w-12' />
    <h2 className='text-xl font-bold'>Project Not Found</h2>
    <Button onClick={onBack}>Return to Projects</Button>
  </div>
);

const ProjectHeaderDetails = ({
  project,
  projectId,
}: {
  project: Project;
  projectId: string | undefined;
}) => (
  <div className='max-w-4xl space-y-4'>
    <div className='flex items-center gap-3'>
      <div className='bg-primary shadow-primary/20 flex h-12 w-12 items-center justify-center rounded-2xl shadow-lg'>
        <Rocket className='text-primary-foreground h-6 w-6' />
      </div>
      <div>
        <h1 className='text-3xl font-black tracking-tight'>
          {getProjectDisplayName(project) || 'Unnamed Project'}
        </h1>
        <div className='mt-1 flex items-center gap-2'>
          <Badge variant='outline' className='text-[10px] font-bold tracking-tighter uppercase'>
            {projectId?.slice(0, PROJECT_ID_SHORT_LENGTH) ?? '—'}
          </Badge>
          <span className='text-muted-foreground flex items-center gap-1 text-xs'>
            <Calendar className='h-3 w-3' />
            {formatProjectDate(project.createdAt)}
          </span>
        </div>
      </div>
    </div>
    {(project.description ?? '').trim() ? (
      <p className='text-muted-foreground leading-relaxed'>{project.description}</p>
    ) : null}
  </div>
);

const ProjectHeaderActions = ({
  onCreateFeature,
  onExport,
}: {
  onCreateFeature: () => void;
  onExport: () => void;
}) => (
  <div className='flex shrink-0 gap-2'>
    <Button variant='outline' size='sm' className='gap-2 rounded-full px-4' onClick={onExport}>
      <ExternalLink className='h-4 w-4' />
      Export
    </Button>
    <Button
      size='sm'
      className='gap-2 rounded-full px-4'
      onClick={onCreateFeature}
      aria-label='New Feature'
    >
      <Plus className='h-4 w-4' />
      New Feature
    </Button>
  </div>
);

const ProjectHeader = ({
  onCreateFeature,
  onExport,
  project,
  projectId,
}: {
  onCreateFeature: () => void;
  onExport: () => void;
  project: Project;
  projectId: string | undefined;
}) => (
  <div className='flex flex-col justify-between gap-6 lg:flex-row lg:items-end'>
    <ProjectHeaderDetails project={project} projectId={projectId} />
    <ProjectHeaderActions onCreateFeature={onCreateFeature} onExport={onExport} />
  </div>
);

const SummaryCards = ({ cards }: { cards: SummaryCard[] }) => (
  <div className='grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4'>
    {cards.map((card) => {
      const Icon = card.icon;
      return (
        <Card
          key={card.label}
          className='bg-card/50 hover:bg-card flex h-32 flex-col justify-between border-none p-5 shadow-sm transition-colors'
        >
          <div className='flex items-start justify-between'>
            <div>
              <p className='text-muted-foreground/60 text-[10px] font-black tracking-widest uppercase'>
                {card.label}
              </p>
              <h3 className='mt-1 text-2xl font-black'>{card.value}</h3>
            </div>
            <Icon className={cn('h-5 w-5 opacity-40', card.color)} />
          </div>
          {card.progress !== undefined ? (
            <Progress value={card.progress} className='h-1' />
          ) : (
            <p className='text-muted-foreground text-[10px] font-bold'>{card.sub}</p>
          )}
        </Card>
      );
    })}
  </div>
);

const ItemDistributionChart = ({ stats }: { stats: Stats }) => (
  <div className='h-[280px]'>
    <ResponsiveContainer width='100%' height='100%'>
      <BarChart data={stats.typeData}>
        <CartesianGrid strokeDasharray='3 3' vertical={false} stroke='hsl(var(--muted)/0.3)' />
        <XAxis
          dataKey='name'
          fontSize={AXIS_FONT_SIZE}
          tickLine={false}
          axisLine={false}
          tick={AXIS_TICK}
        />
        <YAxis fontSize={AXIS_FONT_SIZE} tickLine={false} axisLine={false} tick={AXIS_TICK} />
        <RechartsTooltip cursor={BAR_TOOLTIP_CURSOR} contentStyle={BAR_TOOLTIP_STYLE} />
        <Bar dataKey='value' fill='hsl(var(--primary))' radius={BAR_RADIUS} />
      </BarChart>
    </ResponsiveContainer>
  </div>
);

const ItemDistributionCard = ({ stats }: { stats: Stats }) => (
  <Card className='bg-card/50 col-span-1 border-none p-6 lg:col-span-2'>
    <div className='mb-8 flex items-center justify-between'>
      <div className='flex items-center gap-2'>
        <Activity className='text-primary h-4 w-4' />
        <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
          Item Distribution
        </h3>
      </div>
      <div className='flex gap-1'>
        <Badge variant='secondary' className='text-[9px] font-bold uppercase'>
          Real-time
        </Badge>
      </div>
    </div>
    <ItemDistributionChart stats={stats} />
  </Card>
);

const ProjectHealthCard = ({ stats }: { stats: Stats }) => (
  <Card className='bg-card/50 flex flex-col border-none p-6'>
    <div className='mb-8 flex items-center gap-2'>
      <Shield className='text-primary h-4 w-4' />
      <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
        Project Health
      </h3>
    </div>
    <div className='flex-1'>
      <ResponsiveContainer width='100%' height='100%'>
        <RadarChart cx='50%' cy='50%' outerRadius='80%' data={stats.radarData}>
          <PolarGrid stroke='hsl(var(--muted))' />
          <PolarAngleAxis dataKey='subject' fontSize={AXIS_FONT_SIZE} tick={AXIS_TICK} />
          <Radar
            name='Coverage'
            dataKey='A'
            stroke='hsl(var(--primary))'
            fill='hsl(var(--primary))'
            fillOpacity={RADAR_FILL_OPACITY}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
    <div className='mt-4 flex justify-center gap-4'>
      <div className='flex items-center gap-1.5'>
        <div className='bg-primary h-2 w-2 rounded-full' />
        <span className='text-muted-foreground text-[10px] font-bold uppercase'>Coverage</span>
      </div>
    </div>
  </Card>
);

const VisualIntelligenceSection = ({ stats }: { stats: Stats }) => (
  <div className='grid grid-cols-1 gap-6 lg:grid-cols-3'>
    <ItemDistributionCard stats={stats} />
    <ProjectHealthCard stats={stats} />
  </div>
);

const AgentWorkflowsSection = ({
  onToggle,
  showAgentWorkflows,
}: {
  onToggle: () => void;
  showAgentWorkflows: boolean;
}) => (
  <div className='space-y-4'>
    <div className='flex items-center justify-between'>
      <div className='flex items-center gap-2'>
        <Bot className='text-primary h-4 w-4' />
        <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
          AI Agent Workflows
        </h3>
      </div>
      <Button
        variant='ghost'
        size='sm'
        onClick={onToggle}
        className='gap-2 text-[10px] font-black tracking-widest uppercase'
      >
        {showAgentWorkflows ? (
          <>
            <ChevronUp className='h-3 w-3' />
            Hide
          </>
        ) : (
          <>
            <ChevronDown className='h-3 w-3' />
            Show
          </>
        )}
      </Button>
    </div>
    {showAgentWorkflows ? (
      <div className='animate-in fade-in slide-in-from-top-2 duration-200'>
        <AgentWorkflowView />
      </div>
    ) : null}
  </div>
);

const ViewsNavigation = ({ projectId }: { projectId: string }) => (
  <div className='space-y-4'>
    <div className='flex items-center gap-2'>
      <Layout className='text-primary h-4 w-4' />
      <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
        Available Views
      </h3>
    </div>
    <div className='grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6'>
      {VIEW_CARDS.map((card) => {
        const Icon = card.icon;
        return (
          <Link
            key={card.href}
            to={`/projects/${projectId}/views/${card.href}` as const}
            className='cursor-pointer'
          >
            <Card className='hover:bg-muted/50 group flex flex-col items-center justify-center gap-3 border-none p-4 shadow-sm transition-all hover:shadow-md'>
              <Icon
                className={cn('h-6 w-6 transition-transform group-hover:scale-110', card.color)}
              />
              <span className='text-[10px] font-bold tracking-tighter uppercase'>{card.label}</span>
            </Card>
          </Link>
        );
      })}
    </div>
  </div>
);

const RecentActivityItem = ({ item, projectId }: { item: Item; projectId: string }) => {
  const ItemIcon = TYPE_ICON_MAP[item.type] ?? FileText;
  const viewType = String(item.view || 'feature').toLowerCase();

  return (
    <Link
      key={item.id}
      to={`/projects/${projectId}/views/${viewType}/${item.id}`}
      className='cursor-pointer'
    >
      <div className='hover:bg-muted/50 group hover:border-border/50 flex items-center gap-4 rounded-xl border border-transparent p-3 transition-colors'>
        <div className='bg-primary/10 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg'>
          <ItemIcon className='text-primary h-4 w-4' />
        </div>
        <div className='min-w-0 flex-1'>
          <h4 className='group-hover:text-primary truncate text-sm font-bold transition-colors'>
            {item.title}
          </h4>
          <div className='mt-0.5 flex items-center gap-2'>
            <Badge className='h-3.5 px-1 text-[8px] font-black tracking-tighter uppercase'>
              {item.type}
            </Badge>
            <span className='text-muted-foreground text-[10px] font-medium tracking-widest uppercase'>
              {item.status}
            </span>
          </div>
        </div>
        <div className='shrink-0 text-right'>
          <div className='text-muted-foreground text-[10px] font-bold'>
            {formatProjectDate(item.createdAt)}
          </div>
        </div>
      </div>
    </Link>
  );
};

const RecentActivityList = ({
  projectId,
  recentItems,
}: {
  projectId: string;
  recentItems: Item[];
}) => (
  <div className='space-y-3'>
    {recentItems.map((item) => (
      <RecentActivityItem key={item.id} item={item} projectId={projectId} />
    ))}
  </div>
);

const RecentActivityCard = ({
  onViewAll,
  projectId,
  recentItems,
}: {
  onViewAll: () => void;
  projectId: string;
  recentItems: Item[];
}) => (
  <Card className='bg-card/50 col-span-1 border-none p-6 lg:col-span-2'>
    <div className='mb-6 flex items-center justify-between'>
      <div className='flex items-center gap-2'>
        <History className='text-primary h-4 w-4' />
        <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
          Recent Item Activity
        </h3>
      </div>
      <Button
        variant='ghost'
        size='sm'
        className='text-[10px] font-black tracking-widest uppercase'
        onClick={onViewAll}
      >
        View All
      </Button>
    </div>
    <RecentActivityList projectId={projectId} recentItems={recentItems} />
  </Card>
);

const MetadataList = ({ entries }: { entries: [string, unknown][] }) => (
  <div className='space-y-2'>
    {entries.length > 0 ? (
      entries.map(([key, value]) => (
        <div key={key} className='flex items-center justify-between'>
          <span className='text-muted-foreground text-[10px] font-medium uppercase'>{key}</span>
          <span className='text-[10px] font-bold'>{String(value)}</span>
        </div>
      ))
    ) : (
      <p className='text-muted-foreground text-[10px]'>No metadata available</p>
    )}
  </div>
);

const QuickConfigCard = ({
  onOpenSettings,
  project,
}: {
  onOpenSettings: () => void;
  project: Project;
}) => {
  const metadata =
    project.metadata && typeof project.metadata === 'object' ? project.metadata : EMPTY_METADATA;
  const metadataEntries = Object.entries(metadata).slice(0, METADATA_PREVIEW_LIMIT);

  return (
    <Card className='bg-card/50 border-none p-6'>
      <div className='mb-6 flex items-center gap-2'>
        <Activity className='text-primary h-4 w-4' />
        <h3 className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
          Quick Config
        </h3>
      </div>
      <div className='space-y-4'>
        <div className='bg-primary/5 border-primary/10 rounded-2xl border p-4'>
          <h4 className='mb-2 text-xs font-bold tracking-widest uppercase'>Metadata</h4>
          <MetadataList entries={metadataEntries} />
        </div>
        <Button
          variant='outline'
          className='w-full gap-2 text-[10px] font-black tracking-widest uppercase'
          size='sm'
          onClick={onOpenSettings}
        >
          <Edit className='h-3 w-3' />
          Project Settings
        </Button>
      </div>
    </Card>
  );
};

const ActivitySection = ({
  onOpenSettings,
  onViewAll,
  project,
  recentItems,
}: {
  onOpenSettings: () => void;
  onViewAll: () => void;
  project: Project;
  recentItems: Item[];
}) => (
  <div className='grid grid-cols-1 gap-6 lg:grid-cols-3'>
    <RecentActivityCard onViewAll={onViewAll} projectId={project.id} recentItems={recentItems} />
    <QuickConfigCard onOpenSettings={onOpenSettings} project={project} />
  </div>
);

const ProjectDetailContent = ({
  cards,
  onCreateFeature,
  onOpenSettings,
  onToggleAgentWorkflows,
  onViewAll,
  onExport,
  project,
  projectId,
  recentItems,
  showAgentWorkflows,
  stats,
}: {
  cards: SummaryCard[];
  onCreateFeature: () => void;
  onOpenSettings: () => void;
  onToggleAgentWorkflows: () => void;
  onViewAll: () => void;
  onExport: () => void;
  project: Project;
  projectId: string | undefined;
  recentItems: Item[];
  showAgentWorkflows: boolean;
  stats: Stats;
}) => (
  <div className='animate-in fade-in mx-auto max-w-[1600px] space-y-8 p-6 duration-500'>
    <ProjectHeader
      onCreateFeature={onCreateFeature}
      onExport={onExport}
      project={project}
      projectId={projectId}
    />
    <SummaryCards cards={cards} />
    <VisualIntelligenceSection stats={stats} />
    <AgentWorkflowsSection
      onToggle={onToggleAgentWorkflows}
      showAgentWorkflows={showAgentWorkflows}
    />
    <ViewsNavigation projectId={project.id} />
    <ActivitySection
      onOpenSettings={onOpenSettings}
      onViewAll={onViewAll}
      project={project}
      recentItems={recentItems}
    />
  </div>
);

export const ProjectDetailView = () => {
  const projectId = useProjectIdParam();
  const navigate = useNavigate();
  const [showAgentWorkflows, setShowAgentWorkflows] = useState(false);
  const { items, itemsTotal, linksTotal, loading, project, projectError } =
    useProjectDetailData(projectId);
  const stats = useProjectStats(items, itemsTotal);
  const recentItems = useRecentItems(items);
  const summaryCards = useSummaryCards(stats, itemsTotal, linksTotal);
  const { handleCreateFeature, handleExport, handleOpenSettings, handleViewAll } =
    useProjectDetailActions(navigate, project);
  const handleToggleAgentWorkflows = useCallback(() => {
    setShowAgentWorkflows((previous) => !previous);
  }, []);
  const handleBackToProjects = useCallback(() => {
    navigate({ to: '/projects' });
  }, [navigate]);

  if (loading) {
    return <ProjectDetailSkeleton />;
  }

  if (projectError || !project) {
    return <ProjectNotFound onBack={handleBackToProjects} />;
  }

  return (
    <ProjectDetailContent
      cards={summaryCards}
      onCreateFeature={handleCreateFeature}
      onOpenSettings={handleOpenSettings}
      onToggleAgentWorkflows={handleToggleAgentWorkflows}
      onViewAll={handleViewAll}
      onExport={handleExport}
      project={project}
      projectId={projectId}
      recentItems={recentItems}
      showAgentWorkflows={showAgentWorkflows}
      stats={stats}
    />
  );
};

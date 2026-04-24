import { Link, useSearch } from '@tanstack/react-router';
import {
  ChevronDown,
  ChevronRight,
  FileText,
  Filter,
  Layers,
  List,
  Maximize2,
  Minimize2,
  Network,
  Plus,
  Search,
  Target,
} from 'lucide-react';
import { memo, useCallback, useMemo, useState } from 'react';

import type { Item } from '@tracertm/types';

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

import { useItems } from '../hooks/useItems';
import { useProjects } from '../hooks/useProjects';

const ALL_PROJECTS_VALUE = 'all';
const INDENT_SIZE_PX = 20;
const EMPTY_DEPTH = 0;
const HAS_PARENT_DEPTH = 1;
const SKELETON_ROWS = ['row-1', 'row-2', 'row-3', 'row-4', 'row-5', 'row-6'] as const;

interface TreeNode {
  item: Item;
  children: TreeNode[];
  level: number;
}

interface TreeItemProps {
  node: TreeNode;
  expandedIds: Set<string>;
  onToggleExpand: (id: string) => void;
  projectFilter: string | undefined;
}

interface ProjectOption {
  id: string;
  name: string;
}

interface SearchFilters {
  projectFilter: string | undefined;
  typeFilter: string | undefined;
}

interface ItemsDataShape {
  items: Item[];
}

interface HeaderActionsProps {
  onNavigateToCreate: () => void;
  onNavigateToTable: () => void;
}

interface FiltersBarProps {
  onCollapseAll: () => void;
  onExpandAll: () => void;
  onProjectFilterChange: (nextProjectFilter: string) => void;
  onSearchQueryChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  projectFilter: string | undefined;
  projectOptions: ProjectOption[];
  searchQuery: string;
}

interface TreeContentProps {
  expandedIds: Set<string>;
  onToggleExpand: (id: string) => void;
  projectFilter: string | undefined;
  treeNodes: TreeNode[];
}

interface SummaryProps {
  filteredItems: Item[];
  treeNodes: TreeNode[];
}

interface SummaryCard {
  id: 'total' | 'root' | 'leaf' | 'depth';
  icon: typeof Layers;
  label: string;
  value: number;
}

const indentStyleCache = new Map<number, React.CSSProperties>();

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function readOptionalString(value: unknown): string | undefined {
  return typeof value === 'string' && value.trim().length > 0 ? value : undefined;
}

function hasText(value: string | undefined): value is string {
  return value !== undefined && value.trim().length > 0;
}

function isItem(value: unknown): value is Item {
  if (!isRecord(value)) {
    return false;
  }

  return (
    typeof value['id'] === 'string' &&
    typeof value['title'] === 'string' &&
    typeof value['type'] === 'string' &&
    typeof value['status'] === 'string'
  );
}

function extractItems(data: unknown): Item[] {
  if (!isRecord(data) || !Array.isArray(data['items'])) {
    return [];
  }

  return data['items'].filter((entry): entry is Item => isItem(entry));
}

function isProjectOption(value: unknown): value is ProjectOption {
  if (!isRecord(value)) {
    return false;
  }

  return typeof value['id'] === 'string' && typeof value['name'] === 'string';
}

function extractProjectOptions(data: unknown): ProjectOption[] {
  if (!Array.isArray(data)) {
    return [];
  }

  return data.filter((entry): entry is ProjectOption => isProjectOption(entry));
}

function parseSearchFilters(searchParams: unknown): SearchFilters {
  if (!isRecord(searchParams)) {
    return { projectFilter: undefined, typeFilter: undefined };
  }

  return {
    projectFilter: readOptionalString(searchParams['project']),
    typeFilter: readOptionalString(searchParams['type']),
  };
}

function getIndentStyle(level: number): React.CSSProperties {
  const cachedStyle = indentStyleCache.get(level);
  if (cachedStyle !== undefined) {
    return cachedStyle;
  }

  const style = { marginLeft: `${level * INDENT_SIZE_PX}px` };
  indentStyleCache.set(level, style);
  return style;
}

function setTreeNodeLevel(node: TreeNode, level: number): void {
  node.level = level;
  node.children.forEach((childNode) => {
    setTreeNodeLevel(childNode, level + 1);
  });
}

function buildTree(items: Item[]): TreeNode[] {
  const itemMap = new Map<string, TreeNode>();
  const rootNodes: TreeNode[] = [];

  items.forEach((item) => {
    itemMap.set(item.id, { children: [], item, level: EMPTY_DEPTH });
  });

  items.forEach((item) => {
    const node = itemMap.get(item.id);
    if (node === undefined) {
      return;
    }

    const parentId = readOptionalString(item.parentId);
    if (!hasText(parentId)) {
      rootNodes.push(node);
      return;
    }

    const parentNode = itemMap.get(parentId);
    if (parentNode === undefined) {
      rootNodes.push(node);
      return;
    }

    parentNode.children.push(node);
  });

  rootNodes.forEach((rootNode) => {
    setTreeNodeLevel(rootNode, EMPTY_DEPTH);
  });

  return rootNodes;
}

function getTreeDepthEstimate(items: Item[]): number {
  return Math.max(
    EMPTY_DEPTH,
    ...items.map((item) =>
      hasText(readOptionalString(item.parentId)) ? HAS_PARENT_DEPTH : EMPTY_DEPTH,
    ),
  );
}

const TreeExpandButton = memo(function TreeExpandButton({
  isExpanded,
  onClick,
}: {
  isExpanded: boolean;
  onClick: () => void;
}): React.JSX.Element {
  return (
    <button
      type='button'
      onClick={onClick}
      className='hover:bg-muted text-muted-foreground flex h-6 w-6 items-center justify-center rounded-lg transition-colors'
    >
      {isExpanded ? <ChevronDown className='h-4 w-4' /> : <ChevronRight className='h-4 w-4' />}
    </button>
  );
});

const TreeItemIcon = memo(function TreeItemIcon({
  isExpanded,
}: {
  isExpanded: boolean;
}): React.JSX.Element {
  return (
    <div
      className={cn(
        'h-8 w-8 rounded-lg flex items-center justify-center shrink-0 transition-colors',
        isExpanded
          ? 'bg-primary text-primary-foreground'
          : 'bg-muted text-muted-foreground group-hover/link:bg-primary/10 group-hover/link:text-primary',
      )}
    >
      <FileText className='h-4 w-4' />
    </div>
  );
});

const TreeItemContent = memo(
  function TreeItemContent({
    item,
    isExpanded,
    childCount,
    projectFilter,
  }: {
    item: Item;
    isExpanded: boolean;
    childCount: number;
    projectFilter: string | undefined;
  }): React.JSX.Element {
    const owner = readOptionalString(item.owner);
    const hasProjectFilter = hasText(projectFilter);

    return (
      <div className='flex min-w-0 flex-1 items-center gap-4'>
        <Link
          to={
            hasProjectFilter
              ? `/projects/${projectFilter}/views/${String(item.view ?? 'feature').toLowerCase()}/${item.id}`
              : '/projects'
          }
          className='group/link flex min-w-0 flex-1 items-center gap-3'
        >
          <TreeItemIcon isExpanded={isExpanded} />
          <div className='flex min-w-0 flex-col'>
            <span className='group-hover/link:text-primary truncate text-sm font-bold transition-colors'>
              {item.title}
            </span>
            <div className='mt-0.5 flex items-center gap-2'>
              <Badge
                variant='outline'
                className='h-3.5 px-1 text-[8px] font-black tracking-tighter uppercase'
              >
                {item.type}
              </Badge>
              <span className='text-muted-foreground text-[9px] font-bold tracking-widest uppercase'>
                {item.status}
              </span>
            </div>
          </div>
        </Link>

        <div className='mr-4 hidden shrink-0 items-center gap-6 md:flex'>
          {hasText(owner) && (
            <div className='flex items-center gap-1.5'>
              <div className='bg-muted flex h-4 w-4 items-center justify-center rounded-full text-[8px] font-black uppercase'>
                {owner.charAt(0)}
              </div>
              <span className='text-muted-foreground text-[10px] font-bold uppercase'>{owner}</span>
            </div>
          )}
          {childCount > EMPTY_DEPTH && (
            <Badge variant='secondary' className='h-4 rounded-full px-1.5 text-[9px] font-black'>
              {childCount}
            </Badge>
          )}
        </div>
      </div>
    );
  },
  (prev, next) =>
    prev.item.id === next.item.id &&
    prev.item.title === next.item.title &&
    prev.item.type === next.item.type &&
    prev.item.status === next.item.status &&
    prev.item.owner === next.item.owner &&
    prev.isExpanded === next.isExpanded &&
    prev.childCount === next.childCount &&
    prev.projectFilter === next.projectFilter,
);

const TreeItem = memo(
  function TreeItem({
    node,
    expandedIds,
    onToggleExpand,
    projectFilter,
  }: TreeItemProps): React.JSX.Element {
    const { item, children, level } = node;
    const hasChildren = children.length > EMPTY_DEPTH;
    const isExpanded = expandedIds.has(item.id);

    const handleToggle = useCallback(() => {
      onToggleExpand(item.id);
    }, [item.id, onToggleExpand]);

    return (
      <div className='select-none'>
        <div
          className={cn(
            'group flex items-center gap-3 p-2 rounded-xl transition-all duration-200 border border-transparent',
            isExpanded ? 'bg-primary/[0.03] border-primary/5' : 'hover:bg-muted/50',
          )}
          style={getIndentStyle(level)}
        >
          {hasChildren ? (
            <TreeExpandButton isExpanded={isExpanded} onClick={handleToggle} />
          ) : (
            <div className='flex h-6 w-6 items-center justify-center'>
              <div className='bg-muted-foreground/30 h-1 w-1 rounded-full' />
            </div>
          )}

          <TreeItemContent
            item={item}
            isExpanded={isExpanded}
            childCount={children.length}
            projectFilter={projectFilter}
          />
        </div>

        {hasChildren && isExpanded && (
          <div className='before:bg-border/50 relative mt-1 space-y-1 before:absolute before:top-0 before:bottom-0 before:left-[11px] before:w-px'>
            {children.map((childNode) => (
              <TreeItem
                key={childNode.item.id}
                node={childNode}
                expandedIds={expandedIds}
                onToggleExpand={onToggleExpand}
                projectFilter={projectFilter}
              />
            ))}
          </div>
        )}
      </div>
    );
  },
  (prev, next) =>
    prev.node.item.id === next.node.item.id &&
    prev.node.item.title === next.node.item.title &&
    prev.node.item.type === next.node.item.type &&
    prev.node.item.status === next.node.item.status &&
    prev.node.item.owner === next.node.item.owner &&
    prev.node.level === next.node.level &&
    prev.node.children.length === next.node.children.length &&
    prev.expandedIds.has(prev.node.item.id) === next.expandedIds.has(next.node.item.id) &&
    prev.node.children.every(
      (childNode, childIndex) => childNode.item.id === next.node.children[childIndex]?.item.id,
    ),
);

const HeaderActions = memo(function HeaderActions({
  onNavigateToCreate,
  onNavigateToTable,
}: HeaderActionsProps): React.JSX.Element {
  return (
    <div className='flex items-center gap-2'>
      <Button variant='outline' size='sm' onClick={onNavigateToTable} className='gap-2 rounded-xl'>
        <List className='h-4 w-4' /> Table
      </Button>
      <Button
        size='sm'
        onClick={onNavigateToCreate}
        className='shadow-primary/20 gap-2 rounded-xl shadow-lg'
      >
        <Plus className='h-4 w-4' /> New Node
      </Button>
    </div>
  );
});

const FiltersBar = memo(function FiltersBar({
  onCollapseAll,
  onExpandAll,
  onProjectFilterChange,
  onSearchQueryChange,
  projectFilter,
  projectOptions,
  searchQuery,
}: FiltersBarProps): React.JSX.Element {
  return (
    <Card className='bg-muted/30 flex flex-wrap items-center gap-2 rounded-2xl border-none p-2'>
      <div className='relative min-w-[200px] flex-1'>
        <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
        <Input
          placeholder='Search hierarchy...'
          className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
          value={searchQuery}
          onChange={onSearchQueryChange}
        />
      </div>
      <div className='bg-border/50 mx-2 hidden h-6 w-px md:block' />
      <Select value={projectFilter ?? ALL_PROJECTS_VALUE} onValueChange={onProjectFilterChange}>
        <SelectTrigger className='hover:bg-background/50 h-10 w-[180px] border-none bg-transparent transition-colors'>
          <div className='flex items-center gap-2'>
            <Filter className='text-muted-foreground h-3.5 w-3.5' />
            <SelectValue placeholder='All Projects' />
          </div>
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={ALL_PROJECTS_VALUE}>All Projects</SelectItem>
          {projectOptions.map((projectOption) => (
            <SelectItem key={projectOption.id} value={projectOption.id}>
              {projectOption.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <div className='ml-auto flex items-center gap-1 pr-2'>
        <Button
          variant='ghost'
          size='icon'
          onClick={onExpandAll}
          className='text-muted-foreground hover:text-primary h-8 w-8'
          title='Expand All'
        >
          <Maximize2 className='h-4 w-4' />
        </Button>
        <Button
          variant='ghost'
          size='icon'
          onClick={onCollapseAll}
          className='text-muted-foreground hover:text-primary h-8 w-8'
          title='Collapse All'
        >
          <Minimize2 className='h-4 w-4' />
        </Button>
      </div>
    </Card>
  );
});

const TreeContent = memo(function TreeContent({
  expandedIds,
  onToggleExpand,
  projectFilter,
  treeNodes,
}: TreeContentProps): React.JSX.Element {
  return (
    <Card className='bg-card/50 min-h-[400px] rounded-2xl border-none p-4 shadow-sm'>
      {treeNodes.length > EMPTY_DEPTH ? (
        <div className='space-y-1'>
          {treeNodes.map((treeNode) => (
            <TreeItem
              key={treeNode.item.id}
              node={treeNode}
              expandedIds={expandedIds}
              onToggleExpand={onToggleExpand}
              projectFilter={projectFilter}
            />
          ))}
        </div>
      ) : (
        <div className='text-muted-foreground/40 flex flex-col items-center justify-center py-20'>
          <Network className='mb-4 h-16 w-16 opacity-10' />
          <p className='text-xs font-black tracking-[0.2em] uppercase'>No structure defined</p>
        </div>
      )}
    </Card>
  );
});

const Summary = memo(function Summary({
  filteredItems,
  treeNodes,
}: SummaryProps): React.JSX.Element {
  const summaryCards: SummaryCard[] = [
    { icon: Layers, id: 'total', label: 'Total Nodes', value: filteredItems.length },
    { icon: Target, id: 'root', label: 'Root Items', value: treeNodes.length },
    {
      icon: FileText,
      id: 'leaf',
      label: 'Leaf Items',
      value: filteredItems.length - treeNodes.length,
    },
    {
      icon: Network,
      id: 'depth',
      label: 'Depth',
      value: getTreeDepthEstimate(filteredItems),
    },
  ];

  return (
    <div className='grid grid-cols-2 gap-4 md:grid-cols-4'>
      {summaryCards.map((summaryCard) => (
        <Card
          key={summaryCard.id}
          className='bg-muted/30 flex items-center justify-between border-none p-4'
        >
          <div>
            <p className='text-muted-foreground text-[9px] font-black tracking-widest uppercase'>
              {summaryCard.label}
            </p>
            <p className='text-xl font-black'>{summaryCard.value}</p>
          </div>
          <summaryCard.icon className='text-primary h-5 w-5 opacity-20' />
        </Card>
      ))}
    </div>
  );
});

const LoadingState = memo(function LoadingState(): React.JSX.Element {
  return (
    <div className='animate-pulse space-y-8 p-6'>
      <Skeleton className='h-10 w-48' />
      <Skeleton className='h-12 w-full rounded-2xl' />
      <div className='space-y-4'>
        {SKELETON_ROWS.map((rowKey) => (
          <Skeleton key={rowKey} className='h-12 w-full rounded-xl' />
        ))}
      </div>
    </div>
  );
});

export function ItemsTreeView(): React.JSX.Element {
  const rawSearchParams: unknown = useSearch({ strict: false });
  const { projectFilter, typeFilter } = useMemo(
    () => parseSearchFilters(rawSearchParams),
    [rawSearchParams],
  );

  const itemFilters = useMemo(
    () => (projectFilter === undefined ? {} : { projectId: projectFilter }),
    [projectFilter],
  );
  const { data: itemsData, isLoading } = useItems(itemFilters);
  const { data: projectsData } = useProjects();

  const items = useMemo(() => extractItems(itemsData as ItemsDataShape), [itemsData]);
  const projectOptions = useMemo(() => extractProjectOptions(projectsData), [projectsData]);

  const [searchQuery, setSearchQuery] = useState('');
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const filteredItems = useMemo(() => {
    if (items.length === EMPTY_DEPTH) {
      return [];
    }

    const normalizedQuery = searchQuery.trim().toLowerCase();
    const hasSearchQuery = normalizedQuery.length > EMPTY_DEPTH;

    return items.filter((item) => {
      if (hasText(typeFilter) && item.type !== typeFilter) {
        return false;
      }

      if (!hasSearchQuery) {
        return true;
      }

      const titleMatches = item.title.toLowerCase().includes(normalizedQuery);
      const description = readOptionalString(item.description);
      const descriptionMatches = description?.toLowerCase().includes(normalizedQuery) ?? false;

      return titleMatches || descriptionMatches;
    });
  }, [items, searchQuery, typeFilter]);

  const treeNodes = useMemo(() => buildTree(filteredItems), [filteredItems]);

  const handleToggleExpand = useCallback((id: string) => {
    setExpandedIds((previousIds) => {
      const nextIds = new Set(previousIds);
      if (nextIds.has(id)) {
        nextIds.delete(id);
      } else {
        nextIds.add(id);
      }
      return nextIds;
    });
  }, []);

  const toggleAll = useCallback(
    (shouldExpand: boolean): void => {
      if (shouldExpand) {
        setExpandedIds(new Set(filteredItems.map((item) => item.id)));
        return;
      }

      setExpandedIds(new Set());
    },
    [filteredItems],
  );

  const handleExpandAll = useCallback(() => {
    toggleAll(true);
  }, [toggleAll]);

  const handleCollapseAll = useCallback(() => {
    toggleAll(false);
  }, [toggleAll]);

  const handleSearchQueryChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  }, []);

  const handleNavigateToTable = useCallback(() => {
    globalThis.location.assign('/projects');
  }, []);

  const handleNavigateToCreate = useCallback(() => {
    globalThis.location.assign('/items/new');
  }, []);

  const handleProjectFilterChange = useCallback((nextProjectFilter: string) => {
    if (nextProjectFilter === ALL_PROJECTS_VALUE) {
      globalThis.location.assign('/projects');
      return;
    }

    const encodedProjectId = encodeURIComponent(nextProjectFilter);
    globalThis.location.assign(`/projects?project=${encodedProjectId}`);
  }, []);

  if (isLoading) {
    return <LoadingState />;
  }

  return (
    <div className='animate-in fade-in mx-auto max-w-5xl space-y-8 p-6 duration-500'>
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-2xl font-black tracking-tight uppercase'>Logical Hierarchy</h1>
          <p className='text-muted-foreground text-sm font-medium'>
            Decompose requirements and features into atomic nodes.
          </p>
        </div>
        <HeaderActions
          onNavigateToCreate={handleNavigateToCreate}
          onNavigateToTable={handleNavigateToTable}
        />
      </div>

      <FiltersBar
        onCollapseAll={handleCollapseAll}
        onExpandAll={handleExpandAll}
        onProjectFilterChange={handleProjectFilterChange}
        onSearchQueryChange={handleSearchQueryChange}
        projectFilter={projectFilter}
        projectOptions={projectOptions}
        searchQuery={searchQuery}
      />

      <TreeContent
        expandedIds={expandedIds}
        onToggleExpand={handleToggleExpand}
        projectFilter={projectFilter}
        treeNodes={treeNodes}
      />

      <Summary filteredItems={filteredItems} treeNodes={treeNodes} />
    </div>
  );
}

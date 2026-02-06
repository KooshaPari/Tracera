import { Link, useNavigate, useSearch } from '@tanstack/react-router';
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

interface TreeNode {
  item: Item;
  children: TreeNode[];
  level: number;
}

interface TreeItemProps {
  node: TreeNode;
  expandedIds: Set<string>;
  onToggleExpand: (id: string) => void;
  projectFilter?: string;
}

const TreeExpandButton = memo(function TreeExpandButton({
  isExpanded,
  onClick,
}: {
  isExpanded: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className='hover:bg-muted text-muted-foreground flex h-6 w-6 items-center justify-center rounded-lg transition-colors'
    >
      {isExpanded ? <ChevronDown className='h-4 w-4' /> : <ChevronRight className='h-4 w-4' />}
    </button>
  );
});

const TreeItemIcon = memo(function TreeItemIcon({ isExpanded }: { isExpanded: boolean }) {
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
    projectFilter?: string;
  }) {
    return (
      <div className='flex min-w-0 flex-1 items-center gap-4'>
        <Link
          to={
            projectFilter
              ? `/projects/${projectFilter}/views/${String(item.view || 'feature').toLowerCase()}/${item.id}`
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
          {item.owner && (
            <div className='flex items-center gap-1.5'>
              <div className='bg-muted flex h-4 w-4 items-center justify-center rounded-full text-[8px] font-black uppercase'>
                {item.owner.charAt(0)}
              </div>
              <span className='text-muted-foreground text-[10px] font-bold uppercase'>
                {item.owner}
              </span>
            </div>
          )}
          {childCount > 0 && (
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
  function TreeItem({ node, expandedIds, onToggleExpand, projectFilter }: TreeItemProps) {
    const { item, children, level } = node;
    const hasChildren = children.length > 0;
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
          style={{ marginLeft: `${level * 20}px` }}
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
            {...(projectFilter != null ? { projectFilter } : {})}
          />
        </div>

        {hasChildren && isExpanded && (
          <div className='before:bg-border/50 relative mt-1 space-y-1 before:absolute before:top-0 before:bottom-0 before:left-[11px] before:w-px'>
            {children.map((child) => (
              <TreeItem
                key={child.item.id}
                node={child}
                expandedIds={expandedIds}
                onToggleExpand={onToggleExpand}
                {...(projectFilter != null ? { projectFilter } : {})}
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
    // Compare child IDs to detect structural changes
    prev.node.children.every(
      (child, idx) => next.node.children[idx] && child.item.id === next.node.children[idx].item.id,
    ),
);

function setTreeNodeLevel(node: TreeNode, level: number): void {
  node.level = level;
  node.children.forEach((child) => setTreeNodeLevel(child, level + 1));
}

function buildTree(items: Item[]): TreeNode[] {
  const itemMap = new Map<string, TreeNode>();
  const rootNodes: TreeNode[] = [];

  items.forEach((item) => {
    itemMap.set(item.id, { children: [], item, level: 0 });
  });

  items.forEach((item) => {
    const node = itemMap.get(item.id)!;
    if (item.parentId && itemMap.has(item.parentId)) {
      const parent = itemMap.get(item.parentId)!;
      node.level = parent.level + 1; // Basic level, will be corrected in recursion if needed
      parent.children.push(node);
    } else {
      rootNodes.push(node);
    }
  });

  rootNodes.forEach((root) => setTreeNodeLevel(root, 0));

  return rootNodes;
}

export function ItemsTreeView() {
  const navigate = useNavigate();
  const searchParams = useSearch({ strict: false }) as any;
  const projectFilter = searchParams?.project || undefined;
  const typeFilter = searchParams?.type || undefined;

  const { data: itemsData, isLoading } = useItems({ projectId: projectFilter });
  const { data: projects } = useProjects();
  const projectsArray = useMemo(() => (Array.isArray(projects) ? projects : []), [projects]);
  const items = itemsData?.items ?? [];

  const [searchQuery, setSearchQuery] = useState('');
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

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
          item.title.toLowerCase().includes(query) ||
          item.description?.toLowerCase().includes(query)
        );
      }
      return true;
    });
  }, [items, typeFilter, searchQuery]);

  const treeNodes = useMemo(() => buildTree(filteredItems), [filteredItems]);

  const handleToggleExpand = useCallback((id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const toggleAll = useCallback(
    (expand: boolean) => {
      if (expand) {
        setExpandedIds(new Set(filteredItems.map((i) => i.id)));
      } else {
        setExpandedIds(new Set());
      }
    },
    [filteredItems],
  );

  const handleNavigateToTable = useCallback(() => {}, [navigate, searchParams, projectFilter]);

  const handleNavigateToCreate = useCallback(() => {}, [navigate, searchParams, projectFilter]);

  const handleProjectFilterChange = useCallback((v: string) => {}, [navigate]);

  if (isLoading) {
    return (
      <div className='animate-pulse space-y-8 p-6'>
        <Skeleton className='h-10 w-48' />
        <Skeleton className='h-12 w-full rounded-2xl' />
        <div className='space-y-4'>
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className='h-12 w-full rounded-xl' />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className='animate-in fade-in mx-auto max-w-5xl space-y-8 p-6 duration-500'>
      {/* Header */}
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <h1 className='text-2xl font-black tracking-tight uppercase'>Logical Hierarchy</h1>
          <p className='text-muted-foreground text-sm font-medium'>
            Decompose requirements and features into atomic nodes.
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
            <Plus className='h-4 w-4' /> New Node
          </Button>
        </div>
      </div>

      {/* Filters & Actions Bar */}
      <Card className='bg-muted/30 flex flex-wrap items-center gap-2 rounded-2xl border-none p-2'>
        <div className='relative min-w-[200px] flex-1'>
          <Search className='text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2' />
          <Input
            placeholder='Search hierarchy...'
            className='h-10 border-none bg-transparent pl-10 focus-visible:ring-0'
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className='bg-border/50 mx-2 hidden h-6 w-px md:block' />
        <Select value={projectFilter || 'all'} onValueChange={handleProjectFilterChange}>
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
        <div className='ml-auto flex items-center gap-1 pr-2'>
          <Button
            variant='ghost'
            size='icon'
            onClick={() => toggleAll(true)}
            className='text-muted-foreground hover:text-primary h-8 w-8'
            title='Expand All'
          >
            <Maximize2 className='h-4 w-4' />
          </Button>
          <Button
            variant='ghost'
            size='icon'
            onClick={() => toggleAll(false)}
            className='text-muted-foreground hover:text-primary h-8 w-8'
            title='Collapse All'
          >
            <Minimize2 className='h-4 w-4' />
          </Button>
        </div>
      </Card>

      {/* Tree Content */}
      <Card className='bg-card/50 min-h-[400px] rounded-2xl border-none p-4 shadow-sm'>
        {treeNodes.length > 0 ? (
          <div className='space-y-1'>
            {treeNodes.map((node) => (
              <TreeItem
                key={node.item.id}
                node={node}
                expandedIds={expandedIds}
                onToggleExpand={handleToggleExpand}
                {...(projectFilter != null ? { projectFilter } : {})}
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

      {/* Executive Summary */}
      <div className='grid grid-cols-2 gap-4 md:grid-cols-4'>
        {[
          { icon: Layers, label: 'Total Nodes', value: filteredItems.length },
          { icon: Target, label: 'Root Items', value: treeNodes.length },
          {
            icon: FileText,
            label: 'Leaf Items',
            value: filteredItems.length - treeNodes.length,
          },
          {
            icon: Network,
            label: 'Depth',
            value: Math.max(0, ...filteredItems.map((i) => (i.parentId ? 1 : 0))),
          },
        ].map((s, i) => (
          <Card key={i} className='bg-muted/30 flex items-center justify-between border-none p-4'>
            <div>
              <p className='text-muted-foreground text-[9px] font-black tracking-widest uppercase'>
                {s.label}
              </p>
              <p className='text-xl font-black'>{s.value}</p>
            </div>
            <s.icon className='text-primary h-5 w-5 opacity-20' />
          </Card>
        ))}
      </div>
    </div>
  );
}

// UI Component Tree - Storybook-like view for UI components and pages

import {
  ChevronDown,
  ChevronRight,
  Component,
  ExternalLink,
  FileCode,
  FolderOpen,
  Layers,
  LayoutGrid,
  Monitor,
  Search,
} from 'lucide-react';
import React, { memo, useCallback, useMemo, useState } from 'react';

import type { Item, Link } from '@tracertm/types';

import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { Input } from '@tracertm/ui/components/Input';
import { ScrollArea } from '@tracertm/ui/components/ScrollArea';

import { ENHANCED_TYPE_COLORS } from './types';

interface UIComponentTreeProps {
  items: Item[];
  links: Link[];
  onSelectItem: (itemId: string) => void;
  selectedItemId: string | null;
}

// UI-related item types
const UI_TYPES = new Set(['wireframe', 'ui_component', 'page', 'component', 'screen', 'layout']);

// Tree node structure
interface TreeNode {
  id: string;
  item: Item;
  children: TreeNode[];
  depth: number;
  hasInteraction: boolean;
  linkedPages: string[];
}

function buildUITree(items: Item[], links: Link[]): TreeNode[] {
  // Filter to UI items only
  const uiItems = items.filter((item) => {
    const type = item.type ? item.type.toLowerCase() : '';
    const view = item.view ? item.view.toLowerCase() : '';
    return UI_TYPES.has(type) || view.includes('ui') || view.includes('wireframe');
  });

  // Build parent-child relationships
  const itemMap = new Map(items.map((item) => [item.id, item]));
  const childrenMap = new Map<string, Item[]>();

  // Group by parent
  for (const item of uiItems) {
    const parentId = item.parentId ?? 'root';
    if (!childrenMap.has(parentId)) {
      childrenMap.set(parentId, []);
    }
    childrenMap.get(parentId)!.push(item);
  }

  // Build interaction map (which pages link to which)
  const interactionMap = new Map<string, string[]>();
  for (const link of links) {
    if (link.type === 'related_to' || link.type === 'depends_on') {
      const source = itemMap.get(link.sourceId);
      const target = itemMap.get(link.targetId);
      if (!source || !target) {
        continue;
      }
      const srcType = source.type ? source.type.toLowerCase() : '';
      const tgtType = target.type ? target.type.toLowerCase() : '';
      if (source && target && UI_TYPES.has(srcType) && UI_TYPES.has(tgtType)) {
        if (!interactionMap.has(source.id)) {
          interactionMap.set(source.id, []);
        }
        interactionMap.get(source.id)!.push(target.id);
      }
    }
  }

  // Recursive tree builder
  function buildNode(item: Item, depth: number): TreeNode {
    const children = childrenMap.get(item.id) ?? [];
    const linkedPages = interactionMap.get(item.id) ?? [];

    return {
      children: children
        .toSorted((a, b) => (a.title || '').localeCompare(b.title || ''))
        .map((child) => buildNode(child, depth + 1)),
      depth,
      hasInteraction: linkedPages.length > 0,
      id: item.id,
      item,
      linkedPages,
    };
  }

  // Build tree from root items
  const rootItems = childrenMap.get('root') ?? uiItems.filter((i) => !i.parentId);

  // Group by type for better organization
  const pages = rootItems.filter((i) => i.type === 'page' || i.type === 'screen');
  const components = rootItems.filter((i) => i.type === 'component' || i.type === 'ui_component');
  const wireframes = rootItems.filter((i) => i.type === 'wireframe');
  const layouts = rootItems.filter((i) => i.type === 'layout');
  const other = rootItems.filter(
    (i) =>
      !['page', 'screen', 'component', 'ui_component', 'wireframe', 'layout'].includes(
        i.type || '',
      ),
  );

  return [
    ...pages.map((item) => buildNode(item, 0)),
    ...wireframes.map((item) => buildNode(item, 0)),
    ...layouts.map((item) => buildNode(item, 0)),
    ...components.map((item) => buildNode(item, 0)),
    ...other.map((item) => buildNode(item, 0)),
  ];
}

interface TreeItemProps {
  node: TreeNode;
  selectedId: string | null;
  expandedIds: Set<string>;
  onToggle: (id: string) => void;
  onSelect: (id: string) => void;
}

interface TreeToolbarProps {
  onExpandAll: () => void;
  onCollapseAll: () => void;
}

function TreeToolbar({ onExpandAll, onCollapseAll }: TreeToolbarProps) {
  return (
    <div className='mb-2 flex gap-2 px-2'>
      <Button variant='ghost' size='sm' className='h-6 text-xs' onClick={onExpandAll}>
        Expand All
      </Button>
      <Button variant='ghost' size='sm' className='h-6 text-xs' onClick={onCollapseAll}>
        Collapse All
      </Button>
    </div>
  );
}

function EmptyTreeState() {
  return (
    <div className='text-muted-foreground py-8 text-center'>
      <LayoutGrid className='mx-auto mb-2 h-12 w-12 opacity-50' />
      <p className='text-sm'>No UI components found</p>
      <p className='mt-1 text-xs'>Add wireframes, pages, or components to see them here</p>
    </div>
  );
}

function EmptyInteractionsState() {
  return (
    <div className='text-muted-foreground py-8 text-center'>
      <ExternalLink className='mx-auto mb-2 h-12 w-12 opacity-50' />
      <p className='text-sm'>No page interactions found</p>
      <p className='mt-1 text-xs'>Link UI items with &quot;related_to&quot; to map interactions</p>
    </div>
  );
}

interface InteractionRowProps {
  from: Item;
  to: Item;
  linkType: string;
  onSelectItem: (itemId: string) => void;
}

function InteractionRow({ from, to, linkType, onSelectItem }: InteractionRowProps) {
  return (
    <div className='bg-muted/50 flex items-center gap-2 rounded-lg p-2 text-sm'>
      <Button
        variant='ghost'
        size='sm'
        className='h-6 px-2 text-xs'
        onClick={() => {
          onSelectItem(from.id);
        }}
      >
        {from.title}
      </Button>
      <ChevronRight className='text-muted-foreground h-4 w-4' />
      <Badge variant='outline' className='text-[10px]'>
        {linkType.replaceAll('_', ' ')}
      </Badge>
      <ChevronRight className='text-muted-foreground h-4 w-4' />
      <Button
        variant='ghost'
        size='sm'
        className='h-6 px-2 text-xs'
        onClick={() => {
          onSelectItem(to.id);
        }}
      >
        {to.title}
      </Button>
    </div>
  );
}

function TreeItem({ node, selectedId, expandedIds, onToggle, onSelect }: TreeItemProps) {
  const isExpanded = expandedIds.has(node.id);
  const isSelected = selectedId === node.id;
  const hasChildren = node.children.length > 0;
  const bgColor = ENHANCED_TYPE_COLORS[node.item.type || ''] ?? '#64748b';

  const typeIcon =
    {
      component: Component,
      layout: Layers,
      page: Monitor,
      screen: Monitor,
      ui_component: Component,
      wireframe: LayoutGrid,
    }[node.item.type || ''] ?? FileCode;

  const Icon = typeIcon;

  const paddingStyle = useMemo(() => ({ paddingLeft: `${node.depth * 16 + 8}px` }), [node.depth]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onSelect(node.id);
      }
    },
    [node.id, onSelect],
  );

  const handleExpandClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onToggle(node.id);
    },
    [node.id, onToggle],
  );

  const iconBgStyle = useMemo(() => ({ backgroundColor: `${bgColor}20` }), [bgColor]);
  const iconColorStyle = useMemo(() => ({ color: bgColor }), [bgColor]);

  return (
    <div>
      <div
        role='button'
        tabIndex={0}
        className={`flex cursor-pointer items-center gap-1.5 rounded-md px-2 py-1.5 transition-colors ${isSelected ? 'bg-primary/10 text-primary' : 'hover:bg-muted'} `}
        style={paddingStyle}
        onClick={() => {
          onSelect(node.id);
        }}
        onKeyDown={handleKeyDown}
      >
        {/* Expand/Collapse */}
        {hasChildren ? (
          <button
            type='button'
            onClick={handleExpandClick}
            className='hover:bg-muted-foreground/20 rounded p-0.5'
          >
            {isExpanded ? (
              <ChevronDown className='text-muted-foreground h-3.5 w-3.5' />
            ) : (
              <ChevronRight className='text-muted-foreground h-3.5 w-3.5' />
            )}
          </button>
        ) : (
          <span className='w-4.5' />
        )}

        {/* Icon */}
        <div className='rounded p-1' style={iconBgStyle}>
          <Icon className='h-3.5 w-3.5' style={iconColorStyle} />
        </div>

        {/* Title */}
        <span className='flex-1 truncate text-sm'>{node.item.title || 'Untitled'}</span>

        {/* Indicators */}
        {node.hasInteraction && (
          <span title='Has page interactions'>
            <ExternalLink className='text-muted-foreground h-3 w-3' />
          </span>
        )}
        {node.children.length > 0 && (
          <Badge variant='secondary' className='h-4 px-1.5 text-[10px]'>
            {node.children.length}
          </Badge>
        )}
      </div>

      {/* Children */}
      {isExpanded && hasChildren && (
        <div>
          {node.children.map((child) => (
            <TreeItem
              key={child.id}
              node={child}
              selectedId={selectedId}
              expandedIds={expandedIds}
              onToggle={onToggle}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function UIComponentTreeComponent({
  items,
  links,
  onSelectItem,
  selectedItemId,
}: UIComponentTreeProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  const [activeTab, setActiveTab] = useState<'tree' | 'interactions'>('tree');

  const tree = useMemo(() => buildUITree(items, links), [items, links]);
  const itemMap = useMemo(() => new Map(items.map((i) => [i.id, i])), [items]);

  // Filter tree by search
  const filteredTree = useMemo(() => {
    if (!searchQuery) {
      return tree;
    }

    const query = searchQuery.toLowerCase();

    function filterNode(node: TreeNode): TreeNode | undefined {
      const matchesTitle = (node.item.title || '').toLowerCase().includes(query);
      const matchesType = (node.item.type || '').toLowerCase().includes(query);

      const filteredChildren = node.children
        .map((child) => filterNode(child))
        .filter((n): n is TreeNode => n !== undefined);

      if (matchesTitle || matchesType || filteredChildren.length > 0) {
        return { ...node, children: filteredChildren };
      }
      return undefined;
    }

    return tree.map((n) => filterNode(n)).filter((n): n is TreeNode => n !== undefined);
  }, [tree, searchQuery]);

  // Build page interaction matrix
  const interactionMatrix = useMemo(() => {
    const matrix: { from: Item; to: Item; linkType: string }[] = [];

    for (const link of links) {
      const source = itemMap.get(link.sourceId);
      const target = itemMap.get(link.targetId);

      if (source && target) {
        const srcType = source.type ? source.type.toLowerCase() : '';
        const tgtType = target.type ? target.type.toLowerCase() : '';
        const sourceIsUI = UI_TYPES.has(srcType);
        const targetIsUI = UI_TYPES.has(tgtType);

        if (sourceIsUI && targetIsUI) {
          matrix.push({ from: source, linkType: link.type, to: target });
        }
      }
    }

    return matrix;
  }, [links, itemMap]);

  const handleToggle = useCallback((id: string) => {
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

  const expandAll = useCallback(() => {
    const allIds = new Set<string>();
    function collectIds(node: TreeNode) {
      allIds.add(node.id);
      for (const child of node.children) {
        collectIds(child);
      }
    }
    for (const node of tree) {
      collectIds(node);
    }
    setExpandedIds(allIds);
  }, [tree]);

  const collapseAll = useCallback(() => {
    setExpandedIds(new Set());
  }, []);

  // Count stats
  const stats = useMemo(() => {
    let pages = 0;
    let components = 0;
    let wireframes = 0;

    function countNode(node: TreeNode) {
      if (node.item.type === 'page' || node.item.type === 'screen') {
        pages += 1;
      } else if (node.item.type === 'component' || node.item.type === 'ui_component') {
        components += 1;
      } else if (node.item.type === 'wireframe') {
        wireframes += 1;
      }
      for (const child of node.children) {
        countNode(child);
      }
    }

    for (const node of tree) {
      countNode(node);
    }
    return {
      components,
      interactions: interactionMatrix.length,
      pages,
      wireframes,
    };
  }, [tree, interactionMatrix]);

  return (
    <Card className='flex h-full flex-col overflow-hidden'>
      {/* Header */}
      <div className='space-y-3 border-b p-4'>
        <div className='flex items-center justify-between'>
          <div className='flex items-center gap-2'>
            <LayoutGrid className='h-5 w-5 text-pink-500' />
            <h3 className='font-semibold'>UI Component Library</h3>
          </div>
        </div>

        {/* Stats */}
        <div className='flex gap-3 text-xs'>
          <div className='flex items-center gap-1'>
            <Monitor className='h-3 w-3 text-blue-500' />
            <span>{stats.pages} Pages</span>
          </div>
          <div className='flex items-center gap-1'>
            <Component className='h-3 w-3 text-green-500' />
            <span>{stats.components} Components</span>
          </div>
          <div className='flex items-center gap-1'>
            <LayoutGrid className='h-3 w-3 text-pink-500' />
            <span>{stats.wireframes} Wireframes</span>
          </div>
          <div className='flex items-center gap-1'>
            <ExternalLink className='h-3 w-3 text-orange-500' />
            <span>{stats.interactions} Interactions</span>
          </div>
        </div>

        {/* Search */}
        <div className='relative'>
          <Search className='text-muted-foreground absolute top-2.5 left-2.5 h-4 w-4' />
          <Input
            placeholder='Search components...'
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
            }}
            className='h-9 pl-8'
          />
        </div>

        {/* Tab Toggle */}
        <div className='bg-muted flex gap-1 rounded-lg p-1'>
          <Button
            variant={activeTab === 'tree' ? 'default' : 'ghost'}
            size='sm'
            className='h-7 flex-1 text-xs'
            onClick={() => {
              setActiveTab('tree');
            }}
          >
            <FolderOpen className='mr-1 h-3.5 w-3.5' />
            Tree View
          </Button>
          <Button
            variant={activeTab === 'interactions' ? 'default' : 'ghost'}
            size='sm'
            className='h-7 flex-1 text-xs'
            onClick={() => {
              setActiveTab('interactions');
            }}
          >
            <ExternalLink className='mr-1 h-3.5 w-3.5' />
            Interactions
          </Button>
        </div>
      </div>

      {/* Content */}
      <ScrollArea className='flex-1'>
        {activeTab === 'tree' ? (
          <div className='p-2'>
            <TreeToolbar onExpandAll={expandAll} onCollapseAll={collapseAll} />

            {/* Tree */}
            {filteredTree.length > 0 ? (
              filteredTree.map((node) => (
                <TreeItem
                  key={node.id}
                  node={node}
                  selectedId={selectedItemId}
                  expandedIds={expandedIds}
                  onToggle={handleToggle}
                  onSelect={onSelectItem}
                />
              ))
            ) : (
              <EmptyTreeState />
            )}
          </div>
        ) : (
          <div className='space-y-3 p-4'>
            {/* Interaction Matrix */}
            <h4 className='text-muted-foreground text-sm font-medium'>Page Interactions</h4>
            {interactionMatrix.length > 0 ? (
              <div className='space-y-2'>
                {interactionMatrix.slice(0, 20).map((interaction) => (
                  <InteractionRow
                    key={`${interaction.from.id}-${interaction.to.id}-${interaction.linkType}`}
                    from={interaction.from}
                    to={interaction.to}
                    linkType={interaction.linkType}
                    onSelectItem={onSelectItem}
                  />
                ))}
                {interactionMatrix.length > 20 && (
                  <p className='text-muted-foreground text-center text-xs'>
                    +{interactionMatrix.length - 20} more interactions
                  </p>
                )}
              </div>
            ) : (
              <EmptyInteractionsState />
            )}
          </div>
        )}
      </ScrollArea>
    </Card>
  );
}

export const UIComponentTree = memo(UIComponentTreeComponent);

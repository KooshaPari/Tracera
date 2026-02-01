# Interactive Node Expansion - Implementation Guide

**Companion to:** GRAPH_NODE_EXPANSION_RESEARCH.md
**Focus:** Code examples, component structure, and implementation patterns
**Target Audience:** Frontend developers

---

## 1. Component Architecture

### 1.1 Overall Hierarchy

```
UnifiedGraphView (entry point)
├─ GraphViewContainer (state management)
│  ├─ BreadcrumbTrail (location indicator)
│  ├─ FlowGraphViewInner (canvas)
│  │  ├─ Node components (collapsible pills)
│  │  └─ Edge components
│  └─ NodeDetailPanel (side panel) [NEW: enhanced version]
│     ├─ Header with breadcrumb
│     ├─ TabsList
│     ├─ TabsContent (Details, Links, Preview, Code)
│     └─ Footer Actions
└─ useGraphNavigation hook (keyboard + state)
```

### 1.2 New Components to Create

```
/src/components/graph/
├─ BreadcrumbTrail.tsx [NEW]
│  ├─ Truncate long paths
│  ├─ Clickable navigation
│  └─ Keyboard accessible
├─ EnhancedNodePill.tsx [NEW/ENHANCE]
│  ├─ Status badge
│  ├─ Link counts
│  ├─ Chevron affordance
│  └─ Quick actions
├─ useGraphKeyboardNavigation.ts [NEW]
│  ├─ Arrow key handling
│  ├─ Enter/Escape
│  └─ Focus management
└─ EditableNodeField.tsx [NEW]
   ├─ Inline status dropdown
   ├─ Modal edit trigger
   └─ Agent action button
```

---

## 2. Breadcrumb Component Implementation

### 2.1 TypeScript Definition

```typescript
// /src/components/graph/BreadcrumbTrail.tsx

import { ChevronRight, Home } from 'lucide-react';
import { Button } from '@tracertm/ui/components/Button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@tracertm/ui/components/Tooltip';
import { cn } from '@tracertm/ui/lib/utils';

export interface BreadcrumbItem {
  id: string;
  label: string;
  type: string; // 'project', 'screen', 'component', etc.
}

export interface BreadcrumbTrailProps {
  path: BreadcrumbItem[];
  onNavigate: (itemId: string) => void;
  maxItems?: number; // items to show before truncating
  currentItemId?: string;
}

export function BreadcrumbTrail({
  path,
  onNavigate,
  maxItems = 4,
  currentItemId,
}: BreadcrumbTrailProps) {
  // Truncate if path is too long
  const truncated = path.length > maxItems;
  const startItems = 1; // Always show home
  const endItems = 1; // Always show current

  const displayPath = truncated
    ? [
        path[0],
        ...path.slice(-(endItems + 1), -1), // Middle items via dropdown
        path[path.length - 1],
      ]
    : path;

  const hiddenItems = truncated
    ? path.slice(startItems, -(endItems + 1))
    : [];

  return (
    <nav
      aria-label="Breadcrumb"
      className="flex items-center gap-1 px-4 py-2 text-sm border-b bg-muted/30"
    >
      {/* Home Button */}
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0"
            onClick={() => onNavigate(path[0].id)}
            aria-label="Go to home"
          >
            <Home className="h-4 w-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Home</TooltipContent>
      </Tooltip>

      <ChevronRight className="h-4 w-4 text-muted-foreground" />

      {/* Visible breadcrumb items */}
      {displayPath.map((item, idx) => {
        const isLast = idx === displayPath.length - 1;
        const isCurrent = item.id === currentItemId;

        return (
          <div key={item.id} className="flex items-center gap-1">
            {/* Hidden items dropdown */}
            {idx === 1 && hiddenItems.length > 0 && (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 px-2 text-xs"
                  onClick={() => {}} // Show dropdown
                  title={`${hiddenItems.length} hidden items`}
                >
                  ⋯
                </Button>
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              </>
            )}

            {/* Breadcrumb Item */}
            {isLast ? (
              // Current item (not clickable)
              <span
                className={cn(
                  'px-2 py-1 rounded text-sm font-medium',
                  isCurrent ? 'text-primary' : 'text-foreground'
                )}
                aria-current="page"
              >
                {item.type}: <strong>{item.label}</strong>
              </span>
            ) : (
              // Clickable parent item
              <Button
                variant="ghost"
                size="sm"
                className="h-6 px-2 text-xs hover:bg-accent"
                onClick={() => onNavigate(item.id)}
              >
                {item.type}: {item.label}
              </Button>
            )}

            {!isLast && <ChevronRight className="h-4 w-4 text-muted-foreground" />}
          </div>
        );
      })}
    </nav>
  );
}
```

### 2.2 Usage in Graph Container

```typescript
// In FlowGraphViewInner.tsx or GraphViewContainer.tsx

import { BreadcrumbTrail, type BreadcrumbItem } from './BreadcrumbTrail';

function FlowGraphViewInner() {
  const [focusedNodeId, setFocusedNodeId] = useState<string | null>(null);
  const [breadcrumbPath, setBreadcrumbPath] = useState<BreadcrumbItem[]>([]);

  // Update breadcrumb when focused node changes
  useEffect(() => {
    if (focusedNodeId) {
      const path = buildBreadcrumbPath(focusedNodeId, items);
      setBreadcrumbPath(path);
    }
  }, [focusedNodeId, items]);

  const handleBreadcrumbNavigate = (itemId: string) => {
    setFocusedNodeId(itemId);
    // Optionally pan graph to show this node
    zoomToNode(itemId);
  };

  return (
    <div className="flex flex-col h-full">
      {breadcrumbPath.length > 0 && (
        <BreadcrumbTrail
          path={breadcrumbPath}
          onNavigate={handleBreadcrumbNavigate}
          currentItemId={focusedNodeId}
        />
      )}

      {/* Rest of graph view */}
      <div className="flex-1 overflow-hidden">
        {/* canvas */}
      </div>
    </div>
  );
}

// Helper to build breadcrumb path from item hierarchy
function buildBreadcrumbPath(itemId: string, items: Item[]): BreadcrumbItem[] {
  const path: BreadcrumbItem[] = [];
  let currentId: string | null = itemId;

  // Walk up parent chain
  while (currentId) {
    const item = items.find(i => i.id === currentId);
    if (!item) break;

    path.unshift({
      id: item.id,
      label: item.title || item.id,
      type: (item.type || item.view || 'item').replace(/_/g, ' '),
    });

    currentId = item.parentId || null;
  }

  // Add project root at start if not already there
  const project = items.find(i => i.type === 'project');
  if (project && path[0]?.id !== project.id) {
    path.unshift({
      id: project.id,
      label: project.title || 'Projects',
      type: 'Project',
    });
  }

  return path;
}
```

---

## 3. Keyboard Navigation Hook

### 3.1 useGraphKeyboardNavigation Hook

```typescript
// /src/hooks/useGraphKeyboardNavigation.ts

import { useCallback, useEffect } from 'react';
import type { Node } from '@xyflow/react';

interface UseGraphKeyboardNavigationProps {
  nodes: Node[];
  focusedNodeId: string | null;
  onFocusNode: (nodeId: string) => void;
  onOpenPanel: () => void;
  onClosePanel: () => void;
  panelOpen: boolean;
}

export function useGraphKeyboardNavigation({
  nodes,
  focusedNodeId,
  onFocusNode,
  onOpenPanel,
  onClosePanel,
  panelOpen,
}: UseGraphKeyboardNavigationProps) {
  // Find current node position in sorted list
  const getNodeIndex = useCallback(() => {
    return nodes.findIndex(n => n.id === focusedNodeId);
  }, [nodes, focusedNodeId]);

  // Navigate to adjacent node based on direction
  const navigateNode = useCallback((direction: 'up' | 'down' | 'left' | 'right') => {
    if (nodes.length === 0) return;

    const currentIdx = getNodeIndex();
    const currentNode = focusedNodeId ? nodes[currentIdx] : null;

    let nextNode: Node | undefined;

    // Simple navigation: cycle through nodes
    // Could be enhanced with visual hierarchy (left/right for connections)
    switch (direction) {
      case 'down':
      case 'right':
        nextNode = nodes[(currentIdx + 1) % nodes.length];
        break;
      case 'up':
      case 'left':
        nextNode = nodes[(currentIdx - 1 + nodes.length) % nodes.length];
        break;
    }

    if (nextNode) {
      onFocusNode(nextNode.id);
    }
  }, [nodes, focusedNodeId, getNodeIndex, onFocusNode]);

  // Expand/collapse currently focused node
  const toggleNodeExpanded = useCallback(() => {
    if (!focusedNodeId) return;

    if (panelOpen) {
      onClosePanel();
    } else {
      onOpenPanel();
    }
  }, [focusedNodeId, panelOpen, onOpenPanel, onClosePanel]);

  // Main keyboard event handler
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Don't handle if user is typing in an input
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) {
        // But do handle Escape
        if (e.key === 'Escape') {
          onClosePanel();
        }
        return;
      }

      switch (e.key) {
        // Navigation
        case 'ArrowUp':
        case 'ArrowLeft':
          e.preventDefault();
          navigateNode(e.key === 'ArrowUp' ? 'up' : 'left');
          break;

        case 'ArrowDown':
        case 'ArrowRight':
          e.preventDefault();
          navigateNode(e.key === 'ArrowDown' ? 'down' : 'right');
          break;

        // Expand/Select
        case 'Enter':
        case ' ': // Space
          e.preventDefault();
          if (focusedNodeId) {
            toggleNodeExpanded();
          }
          break;

        // Close panel
        case 'Escape':
          e.preventDefault();
          onClosePanel();
          break;

        // Home/End for quick navigation
        case 'Home':
          e.preventDefault();
          if (nodes.length > 0) {
            onFocusNode(nodes[0].id);
          }
          break;

        case 'End':
          e.preventDefault();
          if (nodes.length > 0) {
            onFocusNode(nodes[nodes.length - 1].id);
          }
          break;

        // Expand all/collapse all (optional)
        case '*':
          e.preventDefault();
          // Emit event: expand all visible nodes
          // This would require state management for expanded nodes
          break;
      }
    },
    [focusedNodeId, navigateNode, toggleNodeExpanded, nodes, onFocusNode, onClosePanel]
  );

  // Attach event listener
  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  return {
    navigateNode,
    toggleNodeExpanded,
  };
}
```

### 3.2 Integration with Graph Component

```typescript
// In FlowGraphViewInner.tsx

import { useGraphKeyboardNavigation } from '../hooks/useGraphKeyboardNavigation';

function FlowGraphViewInner({ items, links, onNavigateToItem }: Props) {
  const [focusedNodeId, setFocusedNodeId] = useState<string | null>(null);
  const [panelOpen, setPanelOpen] = useState(false);
  const [nodes, setNodes] = useState<Node[]>([]);

  const { navigateNode } = useGraphKeyboardNavigation({
    nodes,
    focusedNodeId,
    onFocusNode: setFocusedNodeId,
    onOpenPanel: () => setPanelOpen(true),
    onClosePanel: () => setPanelOpen(false),
    panelOpen,
  });

  // ARIA live region for announcements
  const announceNavigation = (nodeLabel: string) => {
    const message = `Navigated to ${nodeLabel}`;
    // Announce to screen readers
  };

  return (
    <div
      className="flex h-full gap-4"
      role="main"
      aria-label="Graph visualization"
    >
      {/* Graph canvas */}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={handleNodesChange}
          // ... other props
        />
      </div>

      {/* Detail panel */}
      {panelOpen && focusedNodeId && (
        <NodeDetailPanel
          node={selectedNode}
          onClose={() => setPanelOpen(false)}
          // ... other props
        />
      )}

      {/* SR announcements */}
      <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
        {focusedNodeId && `Focus: ${selectedNode?.label}`}
      </div>
    </div>
  );
}
```

---

## 4. Enhanced Node Detail Panel

### 4.1 Add Breadcrumb to Panel Header

```typescript
// Enhance NodeDetailPanel.tsx - update header section

interface NodeDetailPanelProps {
  node: EnhancedNodeData | null;
  breadcrumbPath?: BreadcrumbItem[];
  onNavigateBreadcrumb?: (itemId: string) => void;
  // ... existing props
}

function NodeDetailPanelComponent({
  node,
  breadcrumbPath = [],
  onNavigateBreadcrumb,
  // ... other props
}: NodeDetailPanelProps) {
  if (!node) return null;

  const bgColor = ENHANCED_TYPE_COLORS[node.type] || "#64748b";

  return (
    <Card className="w-96 h-full flex flex-col overflow-hidden border-l-4"
          style={{ borderLeftColor: bgColor }}>

      {/* Breadcrumb in header */}
      {breadcrumbPath.length > 0 && (
        <div className="px-4 pt-3 pb-1 border-b text-xs text-muted-foreground">
          <div className="flex items-center gap-1 flex-wrap">
            {breadcrumbPath.map((item, idx) => (
              <div key={item.id} className="flex items-center gap-1">
                <button
                  className="hover:text-foreground hover:underline"
                  onClick={() => onNavigateBreadcrumb?.(item.id)}
                  type="button"
                >
                  {item.label}
                </button>
                {idx < breadcrumbPath.length - 1 && (
                  <ChevronRight className="h-3 w-3" />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Original header content */}
      <div className="p-4 border-b bg-muted/30">
        {/* ... existing header code ... */}
      </div>

      {/* Rest of panel */}
      {/* ... existing tabs and content ... */}
    </Card>
  );
}
```

---

## 5. Edit Affordances Component

### 5.1 Status Selector for Instant Edit

```typescript
// /src/components/graph/EditableStatusField.tsx

import { Button } from '@tracertm/ui/components/Button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@tracertm/ui/components/DropdownMenu';
import { Badge } from '@tracertm/ui/components/Badge';
import { ChevronDown } from 'lucide-react';

interface EditableStatusFieldProps {
  value: string;
  options: string[];
  onChange: (newValue: string) => void;
  isLoading?: boolean;
}

export function EditableStatusField({
  value,
  options,
  onChange,
  isLoading = false,
}: EditableStatusFieldProps) {
  const statusColors: Record<string, string> = {
    'To Do': 'bg-gray-100 text-gray-800',
    'In Progress': 'bg-blue-100 text-blue-800',
    'Review': 'bg-yellow-100 text-yellow-800',
    'Done': 'bg-green-100 text-green-800',
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          disabled={isLoading}
          className="w-full justify-between"
        >
          <Badge className={statusColors[value] || 'bg-gray-100'}>
            {value}
          </Badge>
          <ChevronDown className="h-4 w-4 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[200px]">
        {options.map((option) => (
          <DropdownMenuItem
            key={option}
            onClick={() => onChange(option)}
            className={value === option ? 'bg-accent' : ''}
          >
            <Badge className={statusColors[option] || 'bg-gray-100'} className="mr-2">
              {option}
            </Badge>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

### 5.2 Agent Action Indicator

```typescript
// /src/components/graph/AgentActionSection.tsx

import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { Sparkles } from 'lucide-react';

interface AgentAction {
  id: string;
  label: string;
  description: string;
  requiresContext?: string[];
}

interface AgentActionSectionProps {
  actions: AgentAction[];
  onExecuteAction: (actionId: string) => void;
  isExecuting?: boolean;
}

export function AgentActionSection({
  actions,
  onExecuteAction,
  isExecuting = false,
}: AgentActionSectionProps) {
  if (actions.length === 0) return null;

  return (
    <Card className="border-blue-200 bg-blue-50 p-4 space-y-3">
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-blue-600" />
        <h4 className="text-sm font-semibold text-blue-900">AI Suggestions</h4>
      </div>

      <div className="space-y-2">
        {actions.map((action) => (
          <Button
            key={action.id}
            variant="outline"
            size="sm"
            className="w-full justify-start text-xs h-8"
            onClick={() => onExecuteAction(action.id)}
            disabled={isExecuting}
          >
            <Sparkles className="h-3 w-3 mr-2" />
            {action.label}
          </Button>
        ))}
      </div>

      <p className="text-xs text-blue-600 italic">
        Ask Claude to analyze this item and suggest improvements
      </p>
    </Card>
  );
}
```

### 5.3 Integration in Detail Panel

```typescript
// Updated NodeDetailPanel.tsx - Details tab with editable fields

<TabsContent value="details" className="p-4 m-0 space-y-4">
  {/* Description */}
  <div>
    <h4 className="text-sm font-medium text-muted-foreground mb-1">
      Description
    </h4>
    <p className="text-sm">
      {node.item.description || "No description provided"}
    </p>
  </div>

  <Separator />

  {/* Editable Status */}
  <div>
    <h4 className="text-sm font-medium text-muted-foreground mb-2">
      Status
    </h4>
    <EditableStatusField
      value={node.item.status || 'To Do'}
      options={['To Do', 'In Progress', 'Review', 'Done']}
      onChange={(newStatus) => {
        // Call API to update status
        console.log('Update status to:', newStatus);
      }}
    />
  </div>

  <Separator />

  {/* Metadata Grid */}
  <div className="grid grid-cols-2 gap-3 text-sm">
    {node.item.owner && (
      <div>
        <span className="text-muted-foreground flex items-center gap-1">
          <User className="h-3 w-3" /> Owner
        </span>
        <p className="font-medium">{node.item.owner}</p>
      </div>
    )}
    <div>
      <span className="text-muted-foreground">Priority</span>
      <p className="font-medium capitalize">{node.item.priority || "—"}</p>
    </div>
  </div>

  {/* Agent Actions */}
  <Separator />
  <AgentActionSection
    actions={[
      {
        id: 'analyze-deps',
        label: 'Analyze dependencies',
        description: 'Find circular dependencies and optimization opportunities',
      },
      {
        id: 'generate-tests',
        label: 'Generate test cases',
        description: 'Create test scenarios based on item properties',
      },
    ]}
    onExecuteAction={(actionId) => {
      console.log('Execute agent action:', actionId);
    }}
  />
</TabsContent>
```

---

## 6. Visual State Management for Nodes

### 6.1 Enhanced Node Component with Chevron

```typescript
// /src/components/graph/nodes/EnhancedNode.tsx (updated)

import { Handle, Position } from '@xyflow/react';
import { ChevronDown } from 'lucide-react';
import { Badge } from '@tracertm/ui/components/Badge';

interface EnhancedNodeProps {
  data: EnhancedNodeData;
  selected: boolean;
  isExpanded?: boolean;
  onExpand?: () => void;
}

export function EnhancedNode({
  data,
  selected,
  isExpanded = false,
  onExpand,
}: EnhancedNodeProps) {
  const bgColor = ENHANCED_TYPE_COLORS[data.type] || '#64748b';
  const hasChildren = data.children && data.children.length > 0;

  return (
    <div
      className={`
        px-3 py-2 rounded-lg border-2 transition-all
        ${selected ? 'border-primary shadow-lg' : 'border-gray-200'}
        ${isExpanded ? 'bg-white ring-2 ring-primary ring-offset-1' : 'bg-white'}
      `}
      style={{
        borderColor: selected ? bgColor : undefined,
      }}
    >
      <div className="flex items-center gap-2">
        {/* Chevron for expandable nodes */}
        {hasChildren && (
          <button
            onClick={onExpand}
            className="p-0 hover:bg-muted rounded transition-colors"
            aria-expanded={isExpanded}
            aria-label={`Toggle ${data.label} details`}
            tabIndex={0}
          >
            <ChevronDown
              className={`h-4 w-4 transition-transform ${
                isExpanded ? 'rotate-180' : ''
              }`}
            />
          </button>
        )}

        {/* Type icon + label */}
        <div className="flex items-center gap-1.5">
          <span className="text-sm font-medium">{data.label}</span>
        </div>

        {/* Status badge */}
        <Badge
          variant="outline"
          className="ml-auto text-xs px-1.5 py-0.5"
          style={{
            backgroundColor: `${bgColor}20`,
            color: bgColor,
            borderColor: bgColor,
          }}
        >
          {data.status}
        </Badge>
      </div>

      {/* Show metadata when expanded */}
      {isExpanded && (
        <div className="mt-2 pt-2 border-t space-y-1 text-xs text-muted-foreground">
          <div>Incoming: {data.incomingCount || 0}</div>
          <div>Outgoing: {data.outgoingCount || 0}</div>
        </div>
      )}

      <Handle type="target" position={Position.Top} />
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
```

---

## 7. State Management Pattern

### 7.1 Graph State Hook

```typescript
// /src/hooks/useGraphState.ts

import { useState, useCallback } from 'react';

interface GraphState {
  focusedNodeId: string | null;
  expandedNodeIds: Set<string>;
  panelOpen: boolean;
  selectedNodeForComparison?: string;
}

export function useGraphState(initialFocusedId?: string) {
  const [state, setState] = useState<GraphState>({
    focusedNodeId: initialFocusedId || null,
    expandedNodeIds: new Set(),
    panelOpen: false,
  });

  const focusNode = useCallback((nodeId: string) => {
    setState(prev => ({
      ...prev,
      focusedNodeId: nodeId,
      panelOpen: true,
    }));
  }, []);

  const unfocusNode = useCallback(() => {
    setState(prev => ({
      ...prev,
      focusedNodeId: null,
      panelOpen: false,
    }));
  }, []);

  const toggleNodeExpanded = useCallback((nodeId: string) => {
    setState(prev => {
      const newExpanded = new Set(prev.expandedNodeIds);
      if (newExpanded.has(nodeId)) {
        newExpanded.delete(nodeId);
      } else {
        newExpanded.add(nodeId);
      }
      return {
        ...prev,
        expandedNodeIds: newExpanded,
      };
    });
  }, []);

  const expandAllNodes = useCallback((nodeIds: string[]) => {
    setState(prev => ({
      ...prev,
      expandedNodeIds: new Set(nodeIds),
    }));
  }, []);

  const collapseAllNodes = useCallback(() => {
    setState(prev => ({
      ...prev,
      expandedNodeIds: new Set(),
    }));
  }, []);

  const togglePanel = useCallback(() => {
    setState(prev => ({
      ...prev,
      panelOpen: !prev.panelOpen,
    }));
  }, []);

  return {
    ...state,
    focusNode,
    unfocusNode,
    toggleNodeExpanded,
    expandAllNodes,
    collapseAllNodes,
    togglePanel,
  };
}
```

### 7.2 Usage in Component

```typescript
// In FlowGraphViewInner.tsx

import { useGraphState } from '../hooks/useGraphState';

function FlowGraphViewInner({ items, links }: Props) {
  const {
    focusedNodeId,
    expandedNodeIds,
    panelOpen,
    focusNode,
    unfocusNode,
    toggleNodeExpanded,
    togglePanel,
  } = useGraphState();

  return (
    <div className="flex h-full gap-4">
      <div className="flex-1">
        <ReactFlow
          nodes={nodes.map(node => ({
            ...node,
            selected: node.id === focusedNodeId,
            data: {
              ...node.data,
              onExpand: () => toggleNodeExpanded(node.id),
              isExpanded: expandedNodeIds.has(node.id),
            },
          }))}
          onNodeClick={(_, node) => focusNode(node.id)}
          // ... other props
        />
      </div>

      {panelOpen && focusedNodeId && (
        <NodeDetailPanel
          node={getNodeData(focusedNodeId)}
          onClose={unfocusNode}
          // ... other props
        />
      )}
    </div>
  );
}
```

---

## 8. Testing Accessibility

### 8.1 Keyboard Navigation Test

```typescript
// __tests__/keyboard-navigation.test.ts

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FlowGraphViewInner } from '../FlowGraphViewInner';

describe('Keyboard Navigation', () => {
  it('should navigate between nodes with arrow keys', async () => {
    const user = userEvent.setup();
    render(<FlowGraphViewInner items={mockItems} links={mockLinks} />);

    const canvas = screen.getByRole('main');

    // Focus canvas
    await user.click(canvas);

    // Navigate down
    await user.keyboard('{ArrowDown}');
    expect(screen.getByLabelText(/navigated to/i)).toBeInTheDocument();
  });

  it('should open panel with Enter key', async () => {
    const user = userEvent.setup();
    render(<FlowGraphViewInner items={mockItems} links={mockLinks} />);

    const canvas = screen.getByRole('main');
    await user.click(canvas);

    // Focus on first node
    await user.keyboard('{Home}');

    // Open panel
    await user.keyboard('{Enter}');

    expect(screen.getByRole('region', { name: /detail/i })).toBeInTheDocument();
  });

  it('should close panel with Escape key', async () => {
    const user = userEvent.setup();
    render(<FlowGraphViewInner items={mockItems} links={mockLinks} />);

    const canvas = screen.getByRole('main');
    await user.click(canvas);
    await user.keyboard('{Home}{Enter}');

    // Close panel
    await user.keyboard('{Escape}');

    expect(screen.queryByRole('region', { name: /detail/i })).not.toBeInTheDocument();
  });
});
```

### 8.2 ARIA Attributes Checklist

```typescript
// Ensure these ARIA attributes are applied:

// Tree structure
<div role="tree" aria-label="Graph nodes">
  <div
    role="treeitem"
    aria-expanded={isExpanded}
    aria-selected={selected}
    tabIndex={focused ? 0 : -1}
  >
    <ChevronDown aria-label="Toggle node details" />
  </div>
</div>

// Breadcrumb
<nav aria-label="Breadcrumb">
  <span aria-current="page">Current Item</span>
</nav>

// Panel
<div
  role="region"
  aria-label="Node details panel"
  aria-live="polite"
>
  {/* content */}
</div>

// Status updates
<div role="status" aria-live="polite" className="sr-only">
  Navigated to Component Button
</div>
```

---

## 9. Performance Optimization

### 9.1 Lazy Loading Children

```typescript
// /src/hooks/useGraphHierarchy.ts

export function useGraphHierarchy(items: Item[], parentId?: string) {
  const [loaded, setLoaded] = useState(new Set<string>());

  const loadChildren = useCallback(async (nodeId: string) => {
    if (loaded.has(nodeId)) return;

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 300));

    setLoaded(prev => new Set([...prev, nodeId]));
  }, [loaded]);

  const children = useMemo(() => {
    return items.filter(item => item.parentId === parentId);
  }, [items, parentId]);

  return {
    children,
    loadChildren,
    isLoaded: loaded.has(parentId || 'root'),
  };
}
```

### 9.2 Virtualized Breadcrumb

```typescript
// For very deep hierarchies, truncate intelligently

const truncateBreadcrumb = (path: BreadcrumbItem[], maxItems: number = 4) => {
  if (path.length <= maxItems) return path;

  return [
    path[0], // Always show home
    { id: 'ellipsis', label: '...', type: 'separator' },
    ...path.slice(-(maxItems - 1)), // Show last N items
  ];
};
```

---

## Implementation Checklist

### Phase 1: Keyboard Navigation (Priority 1)
- [ ] Create `useGraphKeyboardNavigation` hook
- [ ] Handle arrow key navigation between nodes
- [ ] Handle Enter/Space to expand panel
- [ ] Handle Escape to close panel
- [ ] Add focus indicators for keyboard users
- [ ] Test with keyboard only
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)

### Phase 2: Breadcrumbs (Priority 1)
- [ ] Create `BreadcrumbTrail` component
- [ ] Implement truncation logic for deep paths
- [ ] Add click navigation
- [ ] Integrate with graph container
- [ ] Add accessibility attributes
- [ ] Test keyboard navigation through breadcrumbs

### Phase 3: Enhanced Node Pills (Priority 2)
- [ ] Update node visualization with status badges
- [ ] Add link count indicators
- [ ] Add chevron affordance icons
- [ ] Implement hover state animations
- [ ] Add expanded state with inline metadata

### Phase 4: Edit Affordances (Priority 2)
- [ ] Create status selector dropdown
- [ ] Create agent action section
- [ ] Integrate in detail panel
- [ ] Add visual distinction (instant vs. agent-required)
- [ ] Implement API calls for updates

### Phase 5: Deep Hierarchy Support (Priority 3)
- [ ] Implement lazy loading of children
- [ ] Create tree view component
- [ ] Support 5-7 hierarchy levels
- [ ] Add performance monitoring
- [ ] Test with large datasets (1000+ nodes)

---

## Code File Structure

```
/src/components/graph/
├─ BreadcrumbTrail.tsx (NEW)
├─ EditableStatusField.tsx (NEW)
├─ AgentActionSection.tsx (NEW)
├─ EnhancedNode.tsx (ENHANCE)
├─ NodeDetailPanel.tsx (ENHANCE)
├─ FlowGraphViewInner.tsx (ENHANCE)
└─ types.ts

/src/hooks/
├─ useGraphKeyboardNavigation.ts (NEW)
├─ useGraphState.ts (NEW)
├─ useGraphHierarchy.ts (NEW)
└─ useGraph.ts (EXISTING)

/__tests__/
├─ keyboard-navigation.test.ts (NEW)
├─ breadcrumbs.test.ts (NEW)
└─ edit-affordances.test.ts (NEW)
```

---

## References

- [React Flow Documentation](https://reactflow.dev/learn/concepts/adding-interactivity)
- [WAI-ARIA Tree View Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/)
- [Keyboard Navigation Best Practices](https://www.nngroup.com/articles/keyboard-accessibility/)


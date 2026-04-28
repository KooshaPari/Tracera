# UI Tree & State Models - TraceRTM

**Date**: 2025-11-22  
**Version**: 1.0  
**Status**: APPROVED

---

## UI TREE STRUCTURE

### Root Component Hierarchy

```
App
├── Layout
│   ├── Header
│   │   ├── Logo
│   │   ├── Navigation
│   │   ├── Search
│   │   └── UserMenu
│   ├── Sidebar
│   │   ├── NavLinks
│   │   ├── ViewSelector
│   │   └── Settings
│   └── MainContent
│       ├── ViewContainer
│       │   ├── DashboardView
│       │   ├── ItemsView
│       │   ├── GraphView
│       │   ├── NodeEditorView
│       │   ├── CodeEditorView
│       │   ├── TimelineView
│       │   ├── KanbanView
│       │   └── CalendarView
│       └── DetailPanel
│           ├── ItemDetails
│           ├── LinkDetails
│           └── AgentDetails
├── Modals
│   ├── CreateItemModal
│   ├── CreateLinkModal
│   ├── ConflictResolverModal
│   └── SettingsModal
└── Notifications
    ├── ToastContainer
    └── NotificationCenter
```

---

## COMPONENT TREE BY VIEW

### Dashboard View

```
DashboardView
├── StatsCard (Items by Status)
│   ├── StatValue
│   └── StatChart
├── StatsCard (Agent Status)
│   ├── StatValue
│   └── StatChart
├── RecentChangesCard
│   ├── ChangeList
│   └── ChangeItem
├── QualityMetricsCard
│   ├── MetricBar
│   └── MetricValue
└── ActivityFeed
    └── ActivityItem
```

### Items View

```
ItemsView
├── Toolbar
│   ├── NewItemButton
│   ├── FilterDropdown
│   └── SearchInput
├── ItemsTable
│   ├── TableHeader
│   ├── TableBody
│   │   └── ItemRow (repeating)
│   │       ├── ItemTitle
│   │       ├── ItemType
│   │       ├── ItemStatus
│   │       └── ItemActions
│   └── TableFooter
│       └── Pagination
└── ItemDetailsPanel
    ├── ItemHeader
    ├── ItemDescription
    ├── ItemLinks
    ├── ItemAgents
    └── ItemActions
```

### Graph View

```
GraphView
├── Toolbar
│   ├── FilterDropdown
│   ├── SearchInput
│   ├── ZoomControls
│   └── LayoutSelector
├── GraphContainer
│   ├── GraphCanvas (Cytoscape)
│   │   ├── Nodes (repeating)
│   │   └── Edges (repeating)
│   └── GraphLegend
└── NodeDetailsPanel
    ├── NodeHeader
    ├── NodeProperties
    └── NodeActions
```

### Node Editor View

```
NodeEditorView
├── Toolbar
│   ├── NewNodeButton
│   ├── UndoButton
│   ├── RedoButton
│   ├── SaveButton
│   └── AutoSaveToggle
├── EditorContainer
│   ├── Canvas (React Flow)
│   │   ├── Nodes (repeating)
│   │   └── Edges (repeating)
│   └── NodePanel
│       ├── NodeProperties
│       └── NodeActions
└── PreviewPanel
    ├── PreviewCanvas
    └── PreviewOutput
```

### Code Editor View

```
CodeEditorView
├── Toolbar
│   ├── FormatButton
│   ├── RunButton
│   ├── PreviewButton
│   └── SaveButton
├── EditorContainer
│   ├── CodeEditor (Monaco)
│   │   ├── LineNumbers
│   │   ├── CodeContent
│   │   └── Minimap
│   └── ErrorPanel
│       └── ErrorList
└── PreviewContainer
    ├── PreviewFrame (iframe)
    ├── ConsoleOutput
    └── ErrorOutput
```

### Kanban View

```
KanbanView
├── Toolbar
│   ├── FilterDropdown
│   ├── SearchInput
│   └── ColumnSelector
├── KanbanBoard
│   ├── Column (DRAFT)
│   │   ├── ColumnHeader
│   │   └── CardList
│   │       └── Card (repeating)
│   ├── Column (ACTIVE)
│   │   ├── ColumnHeader
│   │   └── CardList
│   │       └── Card (repeating)
│   └── Column (ARCHIVED)
│       ├── ColumnHeader
│       └── CardList
│           └── Card (repeating)
└── CardDetailsPanel
    ├── CardHeader
    ├── CardDescription
    └── CardActions
```

---

## STATE MODELS

### Global State (Legend State)

```typescript
// Root state
{
  // Items
  items: {
    [itemId]: {
      id: string
      title: string
      type: ItemType
      description?: string
      status: ItemStatus
      createdAt: Date
      updatedAt: Date
      createdBy: string
      updatedBy: string
      tags: string[]
      metadata: Record<string, any>
    }
  }

  // Links
  links: {
    [linkId]: {
      id: string
      type: LinkType
      sourceId: string
      targetId: string
      metadata?: Record<string, any>
      createdAt: Date
      createdBy: string
    }
  }

  // Agents
  agents: {
    [agentId]: {
      id: string
      name: string
      status: AgentStatus
      currentItemId?: string
      lastSeen: Date
      isOnline: boolean
    }
  }

  // UI State
  ui: {
    currentView: ViewType
    selectedItemId?: string
    selectedLinkId?: string
    selectedAgentId?: string
    isDetailsPanelOpen: boolean
    filters: {
      itemType?: ItemType
      itemStatus?: ItemStatus
      linkType?: LinkType
      searchQuery?: string
    }
    sort: {
      field: string
      direction: 'asc' | 'desc'
    }
  }

  // Presence
  presence: {
    [userId]: {
      userId: string
      userName: string
      cursorPosition: { x: number; y: number }
      selectedItemId?: string
      isOnline: boolean
      lastSeen: Date
    }
  }

  // Sync
  sync: {
    isSyncing: boolean
    lastSyncTime: Date
    pendingChanges: Change[]
    conflicts: Conflict[]
  }
}
```

### View State (TanStack Query)

```typescript
// Dashboard View
{
  itemsByStatus: {
    DRAFT: number
    ACTIVE: number
    ARCHIVED: number
  }
  agentsByStatus: {
    IDLE: number
    WORKING: number
    ERROR: number
  }
  recentChanges: Change[]
  qualityMetrics: {
    completeness: number
    consistency: number
    performance: number
    security: number
  }
}

// Items View
{
  items: Item[]
  totalCount: number
  pageSize: number
  currentPage: number
  filters: FilterState
  sort: SortState
}

// Graph View
{
  nodes: Node[]
  edges: Edge[]
  layout: LayoutType
  zoom: number
  pan: { x: number; y: number }
}

// Node Editor View
{
  nodes: FlowNode[]
  edges: FlowEdge[]
  history: HistoryEntry[]
  currentHistoryIndex: number
  isDirty: boolean
}

// Code Editor View
{
  code: string
  language: string
  isDirty: boolean
  errors: Error[]
  previewOutput: string
  consoleOutput: string[]
}
```

### Form State (React Hook Form)

```typescript
// Create Item Form
{
  title: string
  type: ItemType
  description: string
  tags: string[]
}

// Create Link Form
{
  sourceId: string
  targetId: string
  type: LinkType
  metadata: Record<string, any>
}

// Update Item Form
{
  title: string
  description: string
  status: ItemStatus
  tags: string[]
}

// Filter Form
{
  itemType?: ItemType
  itemStatus?: ItemStatus
  linkType?: LinkType
  searchQuery?: string
  dateRange?: {
    start: Date
    end: Date
  }
}
```

### Real-Time State (Supabase Realtime)

```typescript
// Subscription events
{
  // Item events
  'items:created': {
    item: Item
    userId: string
    timestamp: Date
  }

  'items:updated': {
    itemId: string
    changes: Partial<Item>
    userId: string
    timestamp: Date
  }

  'items:deleted': {
    itemId: string
    userId: string
    timestamp: Date
  }

  // Link events
  'links:created': {
    link: Link
    userId: string
    timestamp: Date
  }

  'links:updated': {
    linkId: string
    changes: Partial<Link>
    userId: string
    timestamp: Date
  }

  'links:deleted': {
    linkId: string
    userId: string
    timestamp: Date
  }

  // Agent events
  'agents:status-changed': {
    agentId: string
    status: AgentStatus
    currentItemId?: string
    timestamp: Date
  }

  // Presence events
  'presence:update': {
    userId: string
    cursorPosition: { x: number; y: number }
    selectedItemId?: string
    timestamp: Date
  }

  // Conflict events
  'conflicts:detected': {
    conflictId: string
    type: ConflictType
    items: string[]
    timestamp: Date
  }
}
```

### Offline State (Legend State)

```typescript
// Pending changes queue
{
  pendingChanges: [
    {
      id: string
      type: 'create' | 'update' | 'delete'
      entity: 'item' | 'link' | 'agent'
      data: any
      timestamp: Date
      retries: number
    }
  ]
  
  // Local cache
  localCache: {
    items: Map<string, Item>
    links: Map<string, Link>
    agents: Map<string, Agent>
  }
  
  // Sync status
  syncStatus: 'synced' | 'syncing' | 'pending' | 'error'
  lastSyncTime: Date
  syncError?: Error
}
```

### Conflict Resolution State

```typescript
{
  conflicts: [
    {
      id: string
      type: ConflictType
      itemId: string
      localVersion: any
      remoteVersion: any
      resolution?: 'local' | 'remote' | 'merged'
      mergedVersion?: any
      timestamp: Date
    }
  ]
  
  resolutionStrategy: 'manual' | 'auto-local' | 'auto-remote' | 'auto-merge'
}
```

---

## STATE TRANSITIONS

### Item Lifecycle

```
DRAFT
  ├─ update() → DRAFT
  ├─ activate() → ACTIVE
  └─ archive() → ARCHIVED

ACTIVE
  ├─ update() → ACTIVE
  ├─ deactivate() → DRAFT
  └─ archive() → ARCHIVED

ARCHIVED
  ├─ restore() → DRAFT
  └─ delete() → (deleted)
```

### Agent Lifecycle

```
IDLE
  ├─ claimWork() → WORKING
  └─ disconnect() → (offline)

WORKING
  ├─ updateProgress() → WORKING
  ├─ completeWork() → IDLE
  ├─ error() → ERROR
  └─ disconnect() → (offline)

ERROR
  ├─ retry() → WORKING
  ├─ reset() → IDLE
  └─ disconnect() → (offline)
```

### Sync Lifecycle

```
SYNCED
  ├─ localChange() → PENDING
  └─ remoteChange() → SYNCED

PENDING
  ├─ sync() → SYNCING
  └─ localChange() → PENDING

SYNCING
  ├─ syncSuccess() → SYNCED
  ├─ syncError() → ERROR
  └─ conflict() → CONFLICT

ERROR
  ├─ retry() → SYNCING
  └─ discard() → SYNCED

CONFLICT
  ├─ resolve() → SYNCING
  └─ manual() → MANUAL_RESOLUTION
```



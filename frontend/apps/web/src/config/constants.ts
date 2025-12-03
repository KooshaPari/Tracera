// Application constants

export const APP_NAME = 'TraceRTM'
export const APP_VERSION = '0.1.0'

// API Configuration
export const API_BASE_URL = import.meta.env?.VITE_API_URL || 'http://localhost:8000'
export const WS_BASE_URL = import.meta.env?.VITE_WS_URL || 'ws://localhost:8000'
export const API_TIMEOUT = 30000 // 30 seconds

// Pagination
export const DEFAULT_PAGE_SIZE = 20
export const MAX_PAGE_SIZE = 100

// UI Configuration
export const SIDEBAR_WIDTH = 240
export const SIDEBAR_COLLAPSED_WIDTH = 64
export const HEADER_HEIGHT = 64

// View Types
export const VIEW_TYPES = [
  'FEATURE',
  'CODE',
  'TEST',
  'API',
  'DATABASE',
  'WIREFRAME',
  'DOCUMENTATION',
  'DEPLOYMENT',
] as const

export const VIEW_CONFIG = {
  FEATURE: {
    id: 'FEATURE' as const,
    name: 'Feature',
    icon: 'Layers',
    description: 'Product features and user stories',
    color: 'blue',
    itemTypes: ['epic', 'story', 'task'],
  },
  CODE: {
    id: 'CODE' as const,
    name: 'Code',
    icon: 'Code',
    description: 'Code implementation and modules',
    color: 'purple',
    itemTypes: ['module', 'class', 'function', 'file'],
  },
  TEST: {
    id: 'TEST' as const,
    name: 'Test',
    icon: 'TestTube',
    description: 'Test cases and coverage',
    color: 'green',
    itemTypes: ['suite', 'case', 'scenario'],
  },
  API: {
    id: 'API' as const,
    name: 'API',
    icon: 'Network',
    description: 'API endpoints and contracts',
    color: 'orange',
    itemTypes: ['endpoint', 'schema', 'contract'],
  },
  DATABASE: {
    id: 'DATABASE' as const,
    name: 'Database',
    icon: 'Database',
    description: 'Database schema and migrations',
    color: 'teal',
    itemTypes: ['table', 'migration', 'index'],
  },
  WIREFRAME: {
    id: 'WIREFRAME' as const,
    name: 'Wireframe',
    icon: 'Layout',
    description: 'UI mockups and designs',
    color: 'pink',
    itemTypes: ['screen', 'component', 'flow'],
  },
  DOCUMENTATION: {
    id: 'DOCUMENTATION' as const,
    name: 'Documentation',
    icon: 'FileText',
    description: 'Project documentation',
    color: 'yellow',
    itemTypes: ['guide', 'reference', 'tutorial'],
  },
  DEPLOYMENT: {
    id: 'DEPLOYMENT' as const,
    name: 'Deployment',
    icon: 'Rocket',
    description: 'Deployment and infrastructure',
    color: 'red',
    itemTypes: ['environment', 'pipeline', 'config'],
  },
} as const

// Item Status
export const ITEM_STATUSES = [
  { value: 'todo', label: 'To Do', color: 'gray' },
  { value: 'in_progress', label: 'In Progress', color: 'blue' },
  { value: 'done', label: 'Done', color: 'green' },
  { value: 'blocked', label: 'Blocked', color: 'red' },
  { value: 'cancelled', label: 'Cancelled', color: 'gray' },
] as const

// Item Priority
export const ITEM_PRIORITIES = [
  { value: 'low', label: 'Low', color: 'green' },
  { value: 'medium', label: 'Medium', color: 'yellow' },
  { value: 'high', label: 'High', color: 'orange' },
  { value: 'critical', label: 'Critical', color: 'red' },
] as const

// Link Types
export const LINK_TYPES = [
  { value: 'implements', label: 'Implements', icon: 'ArrowRight' },
  { value: 'tests', label: 'Tests', icon: 'TestTube' },
  { value: 'depends_on', label: 'Depends On', icon: 'Link' },
  { value: 'related_to', label: 'Related To', icon: 'Link2' },
  { value: 'blocks', label: 'Blocks', icon: 'Ban' },
  { value: 'parent_of', label: 'Parent Of', icon: 'GitBranch' },
] as const

// Keyboard Shortcuts
export const KEYBOARD_SHORTCUTS = {
  COMMAND_PALETTE: { key: 'k', meta: true },
  SEARCH: { key: '/', shift: false },
  NEW_ITEM: { key: 'n', meta: true },
  SAVE: { key: 's', meta: true },
  UNDO: { key: 'z', meta: true },
  REDO: { key: 'z', meta: true, shift: true },
  DELETE: { key: 'Delete' },
  ESCAPE: { key: 'Escape' },
} as const

// Date/Time Formats
export const DATE_FORMAT = 'MMM d, yyyy'
export const TIME_FORMAT = 'h:mm a'
export const DATETIME_FORMAT = 'MMM d, yyyy h:mm a'

// File Upload
export const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
export const ALLOWED_FILE_TYPES = [
  'image/png',
  'image/jpeg',
  'image/gif',
  'image/webp',
  'application/pdf',
  'text/plain',
  'text/markdown',
]

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'tracertm_auth_token',
  USER_PREFERENCES: 'tracertm_user_preferences',
  RECENT_PROJECTS: 'tracertm_recent_projects',
  UI_STATE: 'tracertm_ui_state',
  THEME: 'tracertm_theme',
} as const

// Graph Layout
export const GRAPH_CONFIG = {
  NODE_WIDTH: 200,
  NODE_HEIGHT: 80,
  NODE_SPACING: 50,
  EDGE_TYPE: 'smoothstep',
  ANIMATION_DURATION: 300,
} as const

// Debounce/Throttle Timings
export const DEBOUNCE_DELAY = 300 // ms
export const SEARCH_DEBOUNCE_DELAY = 500 // ms
export const AUTOSAVE_DELAY = 1000 // ms

// Sync Configuration
export const SYNC_INTERVAL = 5000 // 5 seconds
export const SYNC_RETRY_DELAY = 2000 // 2 seconds
export const MAX_SYNC_RETRIES = 3

// Toast Configuration
export const TOAST_DURATION = 4000 // 4 seconds
export const TOAST_POSITION = 'bottom-right' as const

// Feature Flags (for development)
export const FEATURE_FLAGS = {
  ENABLE_GRAPH_VIEW: true,
  ENABLE_REALTIME_SYNC: true,
  ENABLE_AI_SUGGESTIONS: false,
  ENABLE_EXPORT: true,
  ENABLE_IMPORT: true,
  ENABLE_COLLABORATION: false,
} as const

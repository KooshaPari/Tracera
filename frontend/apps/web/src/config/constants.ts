// Application constants

const APP_NAME = 'TraceRTM';
const APP_VERSION = '0.1.0';

// Authentication routes (managed by WorkOS AuthKit)
const AUTH_ROUTES = {
  CALLBACK: '/auth/callback',
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  REGISTER: '/auth/register',
  RESET_PASSWORD: '/auth/reset-password',
} as const;

// API configuration (gateway-only; no direct backend URLs)
const { VITE_API_URL, VITE_WS_URL } = import.meta.env || {};
const API_BASE_URL = VITE_API_URL || 'http://localhost:4000';
const WS_BASE_URL = VITE_WS_URL || 'ws://localhost:4000';
// 30 seconds
const API_TIMEOUT = 30_000;

// Pagination
const DEFAULT_PAGE_SIZE = 20;
const MAX_PAGE_SIZE = 100;

// UI configuration
const HEADER_HEIGHT = 64;
const SIDEBAR_COLLAPSED_WIDTH = 64;
const SIDEBAR_WIDTH = 240;

// View types
const VIEW_TYPES = [
  'FEATURE',
  'CODE',
  'TEST',
  'API',
  'DATABASE',
  'WIREFRAME',
  'DOCUMENTATION',
  'DEPLOYMENT',
] as const;

const VIEW_CONFIG = {
  API: {
    color: 'orange',
    description: 'API endpoints and contracts',
    icon: 'Network',
    id: 'API' as const,
    itemTypes: ['endpoint', 'schema', 'contract'],
    name: 'API',
  },
  CODE: {
    color: 'purple',
    description: 'Code implementation and modules',
    icon: 'Code',
    id: 'CODE' as const,
    itemTypes: ['module', 'class', 'function', 'file'],
    name: 'Code',
  },
  DATABASE: {
    color: 'teal',
    description: 'Database schema and migrations',
    icon: 'Database',
    id: 'DATABASE' as const,
    itemTypes: ['table', 'migration', 'index'],
    name: 'Database',
  },
  DEPLOYMENT: {
    color: 'red',
    description: 'Deployment and infrastructure',
    icon: 'Rocket',
    id: 'DEPLOYMENT' as const,
    itemTypes: ['environment', 'pipeline', 'config'],
    name: 'Deployment',
  },
  DOCUMENTATION: {
    color: 'yellow',
    description: 'Project documentation',
    icon: 'FileText',
    id: 'DOCUMENTATION' as const,
    itemTypes: ['guide', 'reference', 'tutorial'],
    name: 'Documentation',
  },
  FEATURE: {
    color: 'blue',
    description: 'Product features and user stories',
    icon: 'Layers',
    id: 'FEATURE' as const,
    itemTypes: ['epic', 'story', 'task'],
    name: 'Feature',
  },
  TEST: {
    color: 'green',
    description: 'Test cases and coverage',
    icon: 'TestTube',
    id: 'TEST' as const,
    itemTypes: ['suite', 'case', 'scenario'],
    name: 'Test',
  },
  WIREFRAME: {
    color: 'pink',
    description: 'UI mockups and designs',
    icon: 'Layout',
    id: 'WIREFRAME' as const,
    itemTypes: ['screen', 'component', 'flow'],
    name: 'Wireframe',
  },
} as const;

// Item status
const ITEM_STATUSES = [
  { color: 'gray', label: 'To Do', value: 'todo' },
  { color: 'blue', label: 'In Progress', value: 'in_progress' },
  { color: 'green', label: 'Done', value: 'done' },
  { color: 'red', label: 'Blocked', value: 'blocked' },
  { color: 'gray', label: 'Cancelled', value: 'cancelled' },
] as const;

// Item priority
const ITEM_PRIORITIES = [
  { color: 'green', label: 'Low', value: 'low' },
  { color: 'yellow', label: 'Medium', value: 'medium' },
  { color: 'orange', label: 'High', value: 'high' },
  { color: 'red', label: 'Critical', value: 'critical' },
] as const;

// Link types
const LINK_TYPES = [
  { icon: 'ArrowRight', label: 'Implements', value: 'implements' },
  { icon: 'TestTube', label: 'Tests', value: 'tests' },
  { icon: 'Link', label: 'Depends On', value: 'depends_on' },
  { icon: 'Link2', label: 'Related To', value: 'related_to' },
  { icon: 'Ban', label: 'Blocks', value: 'blocks' },
  { icon: 'GitBranch', label: 'Parent Of', value: 'parent_of' },
] as const;

// Keyboard shortcuts
const KEYBOARD_SHORTCUTS = {
  COMMAND_PALETTE: { key: 'k', meta: true },
  DELETE: { key: 'Delete' },
  ESCAPE: { key: 'Escape' },
  NEW_ITEM: { key: 'n', meta: true },
  REDO: { key: 'z', meta: true, shift: true },
  SAVE: { key: 's', meta: true },
  SEARCH: { key: '/', shift: false },
  UNDO: { key: 'z', meta: true },
} as const;

// Date/time formats
const DATE_FORMAT = 'MMM d, yyyy';
const TIME_FORMAT = 'h:mm a';
const DATETIME_FORMAT = 'MMM d, yyyy h:mm a';

// File upload
// 10 MB
const MAX_FILE_SIZE = 10_485_760;
const ALLOWED_FILE_TYPES = [
  'image/png',
  'image/jpeg',
  'image/gif',
  'image/webp',
  'application/pdf',
  'text/plain',
  'text/markdown',
];

// Local storage keys
const STORAGE_KEYS = {
  AUTH_TOKEN: 'tracertm_auth_token',
  RECENT_PROJECTS: 'tracertm_recent_projects',
  THEME: 'tracertm_theme',
  UI_STATE: 'tracertm_ui_state',
  USER_PREFERENCES: 'tracertm_user_preferences',
} as const;

// Graph layout
const GRAPH_CONFIG = {
  ANIMATION_DURATION: 300,
  EDGE_TYPE: 'smoothstep',
  NODE_HEIGHT: 80,
  NODE_SPACING: 50,
  NODE_WIDTH: 200,
} as const;

// Debounce/throttle timings
// Ms
const DEBOUNCE_DELAY = 300;
// Ms
const SEARCH_DEBOUNCE_DELAY = 500;
// Ms
const AUTOSAVE_DELAY = 1000;

// Sync configuration
// 5 seconds
const SYNC_INTERVAL = 5000;
// 2 seconds
const SYNC_RETRY_DELAY = 2000;
const MAX_SYNC_RETRIES = 3;

// Toast configuration
// 4 seconds
const TOAST_DURATION = 4000;
const TOAST_POSITION = 'bottom-right' as const;

// Feature flags (for development)
const FEATURE_FLAGS = {
  ENABLE_AI_SUGGESTIONS: false,
  ENABLE_COLLABORATION: false,
  ENABLE_EXPORT: true,
  ENABLE_GRAPH_VIEW: true,
  ENABLE_IMPORT: true,
  ENABLE_REALTIME_SYNC: true,
} as const;

const constants = {
  ALLOWED_FILE_TYPES,
  API_BASE_URL,
  API_TIMEOUT,
  APP_NAME,
  APP_VERSION,
  AUTH_ROUTES,
  AUTOSAVE_DELAY,
  DATE_FORMAT,
  DATETIME_FORMAT,
  DEBOUNCE_DELAY,
  DEFAULT_PAGE_SIZE,
  FEATURE_FLAGS,
  GRAPH_CONFIG,
  HEADER_HEIGHT,
  ITEM_PRIORITIES,
  ITEM_STATUSES,
  KEYBOARD_SHORTCUTS,
  LINK_TYPES,
  MAX_FILE_SIZE,
  MAX_PAGE_SIZE,
  MAX_SYNC_RETRIES,
  SEARCH_DEBOUNCE_DELAY,
  SIDEBAR_COLLAPSED_WIDTH,
  SIDEBAR_WIDTH,
  STORAGE_KEYS,
  SYNC_INTERVAL,
  SYNC_RETRY_DELAY,
  TIME_FORMAT,
  TOAST_DURATION,
  TOAST_POSITION,
  VIEW_CONFIG,
  VIEW_TYPES,
  WS_BASE_URL,
} as const;

export default constants;

// Frontend Mock Setup - Comprehensive Mock Library
// Linked to: All unit tests, integration tests

import { vi } from 'vitest';

// ============================================================================
// API CLIENT MOCKS
// ============================================================================

export const mockApiClient = {
  // Items API
  createItem: vi.fn(),
  readItem: vi.fn(),
  updateItem: vi.fn(),
  deleteItem: vi.fn(),
  listItems: vi.fn(),
  searchItems: vi.fn(),
  bulkCreateItems: vi.fn(),
  bulkUpdateItems: vi.fn(),
  bulkDeleteItems: vi.fn(),

  // Links API
  createLink: vi.fn(),
  readLink: vi.fn(),
  updateLink: vi.fn(),
  deleteLink: vi.fn(),
  listLinks: vi.fn(),

  // Agents API
  registerAgent: vi.fn(),
  readAgent: vi.fn(),
  updateAgent: vi.fn(),
  deleteAgent: vi.fn(),
  listAgents: vi.fn(),
  claimWork: vi.fn(),
  completeWork: vi.fn(),

  // Quality Checks API
  runQualityChecks: vi.fn(),
  getQualityCheckResults: vi.fn(),
  listQualityChecks: vi.fn(),

  // Reports API
  generateReport: vi.fn(),
  listReports: vi.fn(),
  downloadReport: vi.fn(),

  // Search API
  search: vi.fn(),
  advancedSearch: vi.fn(),

  // Export API
  exportItems: vi.fn(),
  exportLinks: vi.fn(),
  exportGraph: vi.fn(),

  // Auth API
  login: vi.fn(),
  logout: vi.fn(),
  refreshToken: vi.fn(),
  getUser: vi.fn(),
};

// ============================================================================
// DATABASE MOCKS
// ============================================================================

export const mockDatabase = {
  // Collections
  items: new Map(),
  links: new Map(),
  agents: new Map(),
  qualityChecks: new Map(),
  reports: new Map(),
  users: new Map(),
  projects: new Map(),

  // Methods
  insert: vi.fn(),
  update: vi.fn(),
  delete: vi.fn(),
  find: vi.fn(),
  findOne: vi.fn(),
  query: vi.fn(),
  transaction: vi.fn(),

  // Utilities
  clear: vi.fn(),
  close: vi.fn(),
};

// ============================================================================
// REAL-TIME MOCKS
// ============================================================================

export const mockRealtime = {
  // Subscriptions
  subscribe: vi.fn(),
  unsubscribe: vi.fn(),
  subscribeToItem: vi.fn(),
  subscribeToLink: vi.fn(),
  subscribeToAgent: vi.fn(),

  // Broadcasting
  broadcast: vi.fn(),
  broadcastItemCreated: vi.fn(),
  broadcastItemUpdated: vi.fn(),
  broadcastItemDeleted: vi.fn(),
  broadcastLinkCreated: vi.fn(),
  broadcastPresence: vi.fn(),

  // Presence
  setPresence: vi.fn(),
  getPresence: vi.fn(),
  onPresenceChange: vi.fn(),

  // Connection
  connect: vi.fn(),
  disconnect: vi.fn(),
  isConnected: vi.fn(),
};

// ============================================================================
// AUTHENTICATION MOCKS
// ============================================================================

export const mockAuth = {
  // Authentication
  login: vi.fn(),
  logout: vi.fn(),
  register: vi.fn(),
  refreshToken: vi.fn(),

  // User Info
  getUser: vi.fn(),
  getToken: vi.fn(),
  getPermissions: vi.fn(),
  getRoles: vi.fn(),

  // Authorization
  hasPermission: vi.fn(),
  hasRole: vi.fn(),
  canAccess: vi.fn(),

  // State
  isAuthenticated: vi.fn(),
  isLoading: vi.fn(),
};

// ============================================================================
// STATE MANAGEMENT MOCKS
// ============================================================================

export const mockState = {
  // Global State
  getGlobalState: vi.fn(),
  setGlobalState: vi.fn(),
  updateGlobalState: vi.fn(),

  // Items State
  getItems: vi.fn(),
  setItems: vi.fn(),
  addItem: vi.fn(),
  updateItem: vi.fn(),
  removeItem: vi.fn(),

  // Links State
  getLinks: vi.fn(),
  setLinks: vi.fn(),
  addLink: vi.fn(),
  updateLink: vi.fn(),
  removeLink: vi.fn(),

  // Agents State
  getAgents: vi.fn(),
  setAgents: vi.fn(),
  addAgent: vi.fn(),
  updateAgent: vi.fn(),
  removeAgent: vi.fn(),

  // UI State
  getUIState: vi.fn(),
  setUIState: vi.fn(),
  toggleModal: vi.fn(),
  toggleDrawer: vi.fn(),

  // Sync State
  getSyncState: vi.fn(),
  setSyncState: vi.fn(),
  addPendingChange: vi.fn(),
  removePendingChange: vi.fn(),
};

// ============================================================================
// NOTIFICATION MOCKS
// ============================================================================

export const mockNotifications = {
  // Notifications
  showNotification: vi.fn(),
  showSuccess: vi.fn(),
  showError: vi.fn(),
  showWarning: vi.fn(),
  showInfo: vi.fn(),

  // Toast
  showToast: vi.fn(),
  dismissToast: vi.fn(),

  // Alerts
  showAlert: vi.fn(),
  dismissAlert: vi.fn(),
};

// ============================================================================
// STORAGE MOCKS
// ============================================================================

export const mockStorage = {
  // Local Storage
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),

  // Session Storage
  getSessionItem: vi.fn(),
  setSessionItem: vi.fn(),
  removeSessionItem: vi.fn(),

  // IndexedDB
  openDB: vi.fn(),
  getFromDB: vi.fn(),
  saveToDB: vi.fn(),
  deleteFromDB: vi.fn(),
};

// ============================================================================
// UTILITY MOCKS
// ============================================================================

export const mockUtils = {
  // Formatting
  formatDate: vi.fn(),
  formatTime: vi.fn(),
  formatDateTime: vi.fn(),
  formatNumber: vi.fn(),

  // Validation
  validateEmail: vi.fn(),
  validateURL: vi.fn(),
  validateJSON: vi.fn(),

  // Conversion
  toJSON: vi.fn(),
  fromJSON: vi.fn(),
  toCSV: vi.fn(),
  fromCSV: vi.fn(),

  // Utilities
  debounce: vi.fn(),
  throttle: vi.fn(),
  delay: vi.fn(),
};

// ============================================================================
// SETUP FUNCTIONS
// ============================================================================

export function setupMocks() {
  // Reset all mocks
  vi.clearAllMocks();

  // Setup default mock implementations
  mockApiClient.createItem.mockResolvedValue({
    id: 'item-1',
    title: 'Test Item',
    type: 'REQUIREMENT',
    status: 'DRAFT',
    createdAt: new Date(),
  });

  mockApiClient.listItems.mockResolvedValue([
    {
      id: 'item-1',
      title: 'Test Item 1',
      type: 'REQUIREMENT',
      status: 'DRAFT',
    },
    {
      id: 'item-2',
      title: 'Test Item 2',
      type: 'IMPLEMENTATION',
      status: 'ACTIVE',
    },
  ]);

  mockAuth.isAuthenticated.mockReturnValue(true);
  mockAuth.getUser.mockReturnValue({
    id: 'user-1',
    email: 'test@example.com',
    name: 'Test User',
  });

  mockRealtime.isConnected.mockReturnValue(true);

  return {
    mockApiClient,
    mockDatabase,
    mockRealtime,
    mockAuth,
    mockState,
    mockNotifications,
    mockStorage,
    mockUtils,
  };
}

export function teardownMocks() {
  vi.clearAllMocks();
  mockDatabase.items.clear();
  mockDatabase.links.clear();
  mockDatabase.agents.clear();
}

// ============================================================================
// MOCK DATA GENERATORS
// ============================================================================

export function generateMockItem(overrides = {}) {
  return {
    id: `item-${Math.random()}`,
    title: 'Test Item',
    type: 'REQUIREMENT',
    description: 'Test description',
    status: 'DRAFT',
    priority: 'MEDIUM',
    tags: [],
    assignees: [],
    createdAt: new Date(),
    updatedAt: new Date(),
    ...overrides,
  };
}

export function generateMockLink(overrides = {}) {
  return {
    id: `link-${Math.random()}`,
    type: 'DEPENDS_ON',
    sourceId: 'item-1',
    targetId: 'item-2',
    description: 'Test link',
    createdAt: new Date(),
    ...overrides,
  };
}

export function generateMockAgent(overrides = {}) {
  return {
    id: `agent-${Math.random()}`,
    name: 'Test Agent',
    status: 'ONLINE',
    capabilities: ['READ', 'WRITE', 'EXECUTE'],
    currentItem: null,
    itemsCompleted: 0,
    itemsFailed: 0,
    ...overrides,
  };
}

export function generateMockUser(overrides = {}) {
  return {
    id: `user-${Math.random()}`,
    email: 'test@example.com',
    name: 'Test User',
    role: 'USER',
    permissions: ['READ', 'WRITE'],
    ...overrides,
  };
}



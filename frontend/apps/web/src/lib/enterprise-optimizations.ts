/**
 * Enterprise Optimizations for TraceRTM
 *
 * Collection of advanced optimizations and migrations to replace
 * custom implementations with mature, battle-tested libraries
 */

import { format, formatDistanceToNow, formatRelative } from 'date-fns';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

import { logger } from '@/lib/logger';

/**
 * Workflow context data structure
 */
export interface WorkflowContext {
  [key: string]: string | number | boolean | object | null | undefined;
}

/**
 * Error context for enterprise errors
 */
export interface ErrorContext {
  [key: string]: string | number | boolean | object | null | undefined;
}

// ============================================================================
// 1. KEYBOARD SHORTCUTS (Replace custom implementations)
// ============================================================================

/**
 * Enterprise keyboard shortcuts system
 * Replaces manual event listeners with declarative hotkeys
 */
export const useEnterpriseHotkeys = () => {
  // Navigation shortcuts
  useHotkeys(
    'mod+k',
    () => {
      // Open command palette
      document.getElementById('command-palette')?.focus();
    },
    {
      enableOnFormTags: true,
    },
  );

  // Quick navigation
  useHotkeys('shift+p', () => {
    // Navigate to projects
    window.location.href = '/projects';
  });

  useHotkeys('shift+s', () => {
    // Navigate to projects
    window.location.href = '/projects';
  });

  useHotkeys('shift+g', () => {
    // Navigate to projects
    window.location.href = '/projects';
  });

  // Table shortcuts
  useHotkeys('mod+a', (e) => {
    // Select all in focused table
    const focusedTable = document.querySelector('[data-table-focused]');
    if (focusedTable) {
      e.preventDefault();
      // Dispatch select all event
      focusedTable.dispatchEvent(new CustomEvent('selectAll'));
    }
  });

  // Export shortcuts
  useHotkeys('mod+e', (e) => {
    // Export current view
    e.preventDefault();
    const exportButton = document.querySelector('[data-export-button]');
    exportButton?.dispatchEvent(new MouseEvent('click'));
  });

  // Help shortcut
  useHotkeys('?', () => {
    // Show keyboard shortcuts modal
    document.getElementById('shortcuts-modal')?.classList.toggle('hidden');
  });
};

// ============================================================================
// 2. DATE FORMATTING (Replace moment.js/custom date utils)
// ============================================================================

/**
 * Professional date utilities using date-fns
 * Replaces custom date formatting with standardized date-fns functions
 */
export const dateUtils = {
  format: (date: string | Date, formatStr = 'MMM d, yyyy') => {
    return format(new Date(date), formatStr);
  },

  formatRelative: (date: string | Date) => {
    return formatRelative(new Date(date), new Date());
  },

  formatDistanceToNow: (date: string | Date) => {
    return formatDistanceToNow(new Date(date), { addSuffix: true });
  },

  formatDate: (date: string | Date) => {
    return format(new Date(date), 'MMM d, yyyy');
  },

  formatDateTime: (date: string | Date) => {
    return format(new Date(date), 'MMM d, yyyy HH:mm');
  },

  formatTime: (date: string | Date) => {
    return format(new Date(date), 'HH:mm');
  },

  // Enterprise-specific formats
  formatForAudit: (date: string | Date) => {
    return format(new Date(date), "yyyy-MM-dd'T'HH:mm:ssxxx");
  },

  formatForDisplay: (date: string | Date) => {
    const now = new Date();
    const target = new Date(date);
    const diffInDays = Math.abs(now.getTime() - target.getTime()) / (1000 * 60 * 60 * 24);

    if (diffInDays < 1) {
      return formatDistanceToNow(target);
    } else if (diffInDays < 7) {
      return format(target, 'EEEE');
    } else {
      return format(target, 'MMM d');
    }
  },
};

// ============================================================================
// 3. PERSISTED STATE MANAGEMENT (Enhanced Zustand)
// ============================================================================

/**
 * Enhanced state management with persistence
 * Upgrade from basic Zustand to enterprise-grade state
 */
interface EnterpriseState {
  // User preferences
  preferences: {
    theme: 'light' | 'dark' | 'system';
    compactMode: boolean;
    sidebarCollapsed: boolean;
    language: string;
    dateFormat: string;
    timezone: string;
  };

  // View settings
  viewSettings: {
    defaultPageSize: number;
    defaultSort: Record<string, 'asc' | 'desc'>;
    columnWidths: Record<string, number>;
    hiddenColumns: Record<string, string[]>;
  };

  // Recent activity
  recentProjects: Array<{
    id: string;
    name: string;
    lastVisited: string;
  }>;

  // Workflow state
  workflow: {
    currentProject: string | null;
    currentView: string | null;
    context: WorkflowContext;
  };

  // Notifications
  notifications: Array<{
    id: string;
    type: 'info' | 'success' | 'warning' | 'error';
    title: string;
    message: string;
    timestamp: string;
    read: boolean;
  }>;

  // Actions
  updatePreferences: (preferences: Partial<EnterpriseState['preferences']>) => void;
  updateViewSettings: (settings: Partial<EnterpriseState['viewSettings']>) => void;
  addToRecentProjects: (project: { id: string; name: string }) => void;
  clearRecentProjects: () => void;
  setWorkflowContext: (context: Partial<EnterpriseState['workflow']>) => void;
  addNotification: (
    notification: Omit<EnterpriseState['notifications'][0], 'id' | 'timestamp'>,
  ) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;
}

export const useEnterpriseStore = create<EnterpriseState>()(
  persist(
    (set) => ({
      // Initial state
      preferences: {
        theme: 'system',
        compactMode: false,
        sidebarCollapsed: false,
        language: 'en',
        dateFormat: 'MMM d, yyyy',
        timezone: 'UTC',
      },

      viewSettings: {
        defaultPageSize: 20,
        defaultSort: {},
        columnWidths: {},
        hiddenColumns: {},
      },

      recentProjects: [],

      workflow: {
        currentProject: null,
        currentView: null,
        context: {},
      },

      notifications: [],

      // Actions
      updatePreferences: (preferences) =>
        set((state) => ({
          preferences: { ...state.preferences, ...preferences },
        })),

      updateViewSettings: (settings) =>
        set((state) => ({
          viewSettings: { ...state.viewSettings, ...settings },
        })),

      addToRecentProjects: (project) =>
        set((state) => {
          const existing = state.recentProjects.find((p) => p.id === project.id);
          if (existing) {
            existing.lastVisited = new Date().toISOString();
            return state;
          }

          return {
            recentProjects: [
              { ...project, lastVisited: new Date().toISOString() },
              ...state.recentProjects.slice(0, 10), // Keep only 10 recent
            ],
          };
        }),

      clearRecentProjects: () => set({ recentProjects: [] }),

      setWorkflowContext: (context) =>
        set((state) => ({
          workflow: { ...state.workflow, ...context },
        })),

      addNotification: (notification) =>
        set((state) => ({
          notifications: [
            {
              ...notification,
              id: crypto.randomUUID(),
              timestamp: new Date().toISOString(),
            },
            ...state.notifications.slice(0, 50), // Keep only 50 notifications
          ],
        })),

      markNotificationRead: (id) =>
        set((state) => ({
          notifications: state.notifications.map((n) => (n.id === id ? { ...n, read: true } : n)),
        })),

      clearNotifications: () => set({ notifications: [] }),
    }),
    {
      name: 'tracertm-enterprise-store',
      partialize: (state) => ({
        preferences: state.preferences,
        viewSettings: state.viewSettings,
        recentProjects: state.recentProjects,
      }),
    },
  ),
);

// ============================================================================
// 4. PERFORMANCE OPTIMIZATIONS
// ============================================================================

/**
 * Virtual scrolling hook for large datasets
 * Replace manual pagination/div slicing with efficient virtualization
 */
export const useVirtualScroll = <T>(
  items: T[],
  itemHeight: number,
  containerHeight: number,
  overscan = 5,
) => {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const visibleStart = Math.floor(scrollTop / itemHeight);
  const visibleEnd = Math.min(
    visibleStart + Math.ceil(containerHeight / itemHeight),
    items.length - 1,
  );

  const startIndex = Math.max(0, visibleStart - overscan);
  const endIndex = Math.min(items.length - 1, visibleEnd + overscan);

  const visibleItems = items.slice(startIndex, endIndex + 1);
  const offsetY = startIndex * itemHeight;

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);

  return {
    containerRef,
    visibleItems,
    offsetY,
    startIndex,
    endIndex,
    handleScroll,
    totalHeight: items.length * itemHeight,
  };
};

/**
 * Debounced search hook
 * Replace manual setTimeout with optimized debouncing
 */
export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

/**
 * Memoized grid layout optimizer
 * Replace manual grid calculations with CSS Grid + optimization hooks
 */
export const useGridLayout = (_items: any[], minItemWidth = 200, gap = 16) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [columns, setColumns] = useState(1);

  useEffect(() => {
    const updateColumns = () => {
      if (!containerRef.current) return;

      const containerWidth = containerRef.current.clientWidth;
      const newColumns = Math.max(1, Math.floor((containerWidth + gap) / (minItemWidth + gap)));
      setColumns(newColumns);
    };

    updateColumns();

    const resizeObserver = new ResizeObserver(updateColumns);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    return () => resizeObserver.disconnect();
  }, [minItemWidth, gap]);

  return {
    containerRef,
    columns,
    itemWidth: `calc((100% - ${(columns - 1) * gap}px) / ${columns})`,
  };
};

// ============================================================================
// 5. ERROR HANDLING UPGRADES
// ============================================================================

/**
 * Enterprise error boundary with graceful degradation
 * Replace basic error catching with sophisticated error handling
 */
export class EnterpriseError extends Error {
  constructor(
    message: string,
    public code: string,
    public originalError?: Error,
    public context?: ErrorContext,
    public severity: 'low' | 'medium' | 'high' | 'critical' = 'medium',
    public retryable: boolean = false,
  ) {
    super(message);
    this.name = 'EnterpriseError';
  }
}

/**
 * Error reporter for monitoring and analytics
 * Replace console.error with structured error reporting
 */
export const useErrorReporter = () => {
  const reportError = useCallback((error: EnterpriseError) => {
    // Log to monitoring service
    logger.error('Enterprise Error:', {
      message: error.message,
      code: error.code,
      severity: error.severity,
      context: error.context,
      stack: error.stack,
      originalError: error.originalError,
      timestamp: new Date().toISOString(),
    });

    // Notify monitoring service in production
    if (import.meta.env.PROD) {
      // Integration with error monitoring service
    }
  }, []);

  return { reportError };
};

// ============================================================================
// 6. MIGRATION RECOMMENDATIONS
// ============================================================================

/**
 * Migration recommendations for replacing custom implementations
 */
export const MIGRATION_RECOMMENDATIONS = {
  // Data fetching: OpenAPI → TRPC
  apiMigration: {
    from: 'Custom OpenAPI client with manual typing',
    to: '@trpc/client and @trpc/react-query',
    benefits: [
      'End-to-end type safety',
      'Auto-completion for API methods',
      'Built-in error handling',
      'Real-time subscriptions',
      'Smaller bundle sizes',
    ],
    effort: 'Medium (2-3 days)',
  },

  // WebSocket: Custom manager → TRPC subscriptions
  websocketMigration: {
    from: 'Custom WebSocket manager with manual subscriptions',
    to: 'TRPC subscriptions with automatic cleanup',
    benefits: [
      'Type-safe subscription events',
      'Automatic reconnection',
      'Integrated with React Query',
      'Better error handling',
    ],
    effort: 'Low (1 day)',
  },

  // Date handling: Custom utils → date-fns
  dateMigration: {
    from: 'Custom date formatting utilities',
    to: 'date-fns for all date operations',
    benefits: [
      'Standardized date formatting',
      'Better timezone support',
      'Smaller bundle than moment.js',
      'Extensive formatting options',
    ],
    effort: 'Very Low (4 hours)',
  },

  // State management: Basic Zustand → Persisted Zustand
  stateMigration: {
    from: 'Basic in-memory Zustand stores',
    to: 'Persisted enterprise stores with middleware',
    benefits: [
      'Automatic persistence',
      'Partial state persistence',
      'Time-travel debugging',
      'Developer tools integration',
    ],
    effort: 'Low (1 day)',
  },

  // Keyboard shortcuts: Manual listeners → react-hotkeys-hook
  hotkeysMigration: {
    from: 'Manual event listeners for keyboard shortcuts',
    to: 'react-hotkeys-hook for declarative hotkeys',
    benefits: [
      'Declarative shortcut definitions',
      'Built-in conflict resolution',
      'Easier testing',
      'Browser compatibility',
    ],
    effort: 'Very Low (2 hours)',
  },
};

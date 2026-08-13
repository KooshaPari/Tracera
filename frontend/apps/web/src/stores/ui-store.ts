import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

const DEFAULT_GRID_COLUMNS = Number('3');
const DEFAULT_SIDEBAR_WIDTH = Number('240');

// SSR-safe storage that only accesses localStorage on the client
const noopStorage = {
  getItem: (_key: string) => null,
  removeItem: (_key: string) => {},
  setItem: (_key: string, _value: string) => {},
};

const getStorage = () => {
  // Check if we're in a browser environment with proper localStorage
  if (
    typeof globalThis.window === 'undefined' ||
    typeof localStorage === 'undefined' ||
    typeof localStorage.getItem !== 'function'
  ) {
    return noopStorage;
  }
  return localStorage;
};

// SSR-safe check for dark mode preference
const getDefaultDarkMode = (): boolean => {
  if (typeof globalThis.window === 'undefined') {
    return true;
  }
  return globalThis.matchMedia('(prefers-color-scheme: dark)').matches;
};

interface UIStateData {
  commandPaletteOpen: boolean;
  currentView: string;
  gridColumns: number;
  isDarkMode: boolean;
  layoutMode: 'grid' | 'list' | 'kanban' | 'graph';
  priorityFilter: string[];
  searchOpen: boolean;
  searchQuery: string;
  selectedItemId: string | null;
  selectedItemIds: string[];
  sidebarOpen: boolean;
  sidebarWidth: number;
  statusFilter: string[];
}

interface UIStateActions {
  clearSelection: () => void;
  selectItem: (id: string | null) => void;
  setCurrentView: (view: string) => void;
  setGridColumns: (columns: number) => void;
  setLayoutMode: (mode: 'grid' | 'list' | 'kanban' | 'graph') => void;
  setPriorityFilter: (priorities: string[]) => void;
  setSearchQuery: (query: string) => void;
  setSidebarWidth: (width: number) => void;
  setStatusFilter: (statuses: string[]) => void;
  toggleCommandPalette: () => void;
  toggleDarkMode: () => void;
  toggleItemSelection: (id: string) => void;
  toggleSearch: () => void;
  toggleSidebar: () => void;
}

type UIState = UIStateData & UIStateActions;

type StoreSetter = (
  partial: Partial<UIState> | ((state: UIState) => Partial<UIState> | UIState),
) => void;

type StoreGetter = () => UIState;

const createInitialState = (): UIStateData => ({
  commandPaletteOpen: false,
  currentView: 'FEATURE',
  gridColumns: DEFAULT_GRID_COLUMNS,
  isDarkMode: getDefaultDarkMode(),
  layoutMode: 'grid',
  priorityFilter: [],
  searchOpen: false,
  searchQuery: '',
  selectedItemId: null,
  selectedItemIds: [],
  sidebarOpen: true,
  sidebarWidth: DEFAULT_SIDEBAR_WIDTH,
  statusFilter: [],
});

const applyDarkMode = (enabled: boolean): void => {
  if (typeof document !== 'undefined') {
    document.documentElement.classList.toggle('dark', enabled);
  }
};

const createUIActions = (set: StoreSetter, _get: StoreGetter): UIStateActions => ({
  clearSelection: () => {
    set({ selectedItemId: null, selectedItemIds: [] });
  },
  selectItem: (id) => {
    set({ selectedItemId: id });
  },
  setCurrentView: (view) => {
    set({ currentView: view });
  },
  setGridColumns: (columns) => {
    set({ gridColumns: columns });
  },
  setLayoutMode: (mode) => {
    set({ layoutMode: mode });
  },
  setPriorityFilter: (priorities) => {
    set({ priorityFilter: priorities });
  },
  setSearchQuery: (query) => {
    set({ searchQuery: query });
  },
  setSidebarWidth: (width) => {
    set({ sidebarWidth: width });
  },
  setStatusFilter: (statuses) => {
    set({ statusFilter: statuses });
  },
  toggleCommandPalette: () => {
    set((state) => ({ commandPaletteOpen: !state.commandPaletteOpen }));
  },
  toggleDarkMode: () => {
    set((state) => {
      const newMode = !state.isDarkMode;
      applyDarkMode(newMode);
      return { isDarkMode: newMode };
    });
  },
  toggleItemSelection: (id) => {
    set((state) => {
      const exists = state.selectedItemIds.includes(id);
      return {
        selectedItemIds: exists
          ? state.selectedItemIds.filter((itemId) => itemId !== id)
          : [...state.selectedItemIds, id],
      };
    });
  },
  toggleSearch: () => {
    set((state) => ({ searchOpen: !state.searchOpen }));
  },
  toggleSidebar: () => {
    set((state) => ({ sidebarOpen: !state.sidebarOpen }));
  },
});

const buildUIStore = (set: StoreSetter, get: StoreGetter): UIState => ({
  ...createInitialState(),
  ...createUIActions(set, get),
});

export const useUIStore = create<UIState>()(
  persist<UIState>((set, get) => buildUIStore(set, get), {
    name: 'tracertm-ui-store',
    partialize: (state: UIState) =>
      ({
        gridColumns: state.gridColumns,
        isDarkMode: state.isDarkMode,
        layoutMode: state.layoutMode,
        sidebarOpen: state.sidebarOpen,
        sidebarWidth: state.sidebarWidth,
      }) as unknown as UIState,
    storage: createJSONStorage(() => getStorage()),
  }),
);

import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

// SSR-safe storage that only accesses localStorage on the client
const noopStorage = {
	getItem: (_key: string) => null,
	removeItem: (_key: string) => {},
	setItem: (_key: string, _value: string) => {},
};

const getStorage = () => {
	// Check if we're in a browser environment with proper localStorage
	if (
		typeof globalThis.window === "undefined" ||
		typeof localStorage === "undefined" ||
		typeof localStorage.getItem !== "function"
	) {
		return noopStorage;
	}
	return localStorage;
};

// SSR-safe check for dark mode preference
const getDefaultDarkMode = () => {
	if (typeof globalThis.window === "undefined") {
		return true;
	} // Default to dark for SSR
	return globalThis.matchMedia("(prefers-color-scheme: dark)").matches;
};

interface UIState {
	// Sidebar
	sidebarOpen: boolean;
	sidebarWidth: number;

	// Theme
	isDarkMode: boolean;

	// Current view and selection
	currentView: string;
	selectedItemId: string | null;
	selectedItemIds: string[];

	// Command palette
	commandPaletteOpen: boolean;

	// Search
	searchQuery: string;
	searchOpen: boolean;

	// Filters
	statusFilter: string[];
	priorityFilter: string[];

	// Layout
	layoutMode: "grid" | "list" | "kanban" | "graph";
	gridColumns: number;

	// Actions
	toggleSidebar: () => void;
	setSidebarWidth: (width: number) => void;
	toggleDarkMode: () => void;
	setCurrentView: (view: string) => void;
	selectItem: (id: string | null) => void;
	toggleItemSelection: (id: string) => void;
	clearSelection: () => void;
	toggleCommandPalette: () => void;
	setSearchQuery: (query: string) => void;
	toggleSearch: () => void;
	setStatusFilter: (statuses: string[]) => void;
	setPriorityFilter: (priorities: string[]) => void;
	setLayoutMode: (mode: "grid" | "list" | "kanban" | "graph") => void;
	setGridColumns: (columns: number) => void;
}

export const useUIStore = create<UIState>()(
	persist(
		(set) => ({
			// Initial state
			sidebarOpen: true,
			sidebarWidth: 240,
			isDarkMode: getDefaultDarkMode(),
			currentView: "FEATURE",
			selectedItemId: null,
			selectedItemIds: [],
			commandPaletteOpen: false,
			searchQuery: "",
			searchOpen: false,
			statusFilter: [],
			priorityFilter: [],
			layoutMode: "grid",
			gridColumns: 3,

			// Actions
			toggleSidebar: () =>
				set((state) => ({ sidebarOpen: !state.sidebarOpen })),

			setSidebarWidth: (width) => set({ sidebarWidth: width }),

			toggleDarkMode: () =>
				set((state) => {
					const newMode = !state.isDarkMode;
					if (typeof document !== "undefined") {
						document.documentElement.classList.toggle("dark", newMode);
					}
					return { isDarkMode: newMode };
				}),

			setCurrentView: (view) => set({ currentView: view }),

			selectItem: (id) => set({ selectedItemId: id }),

			toggleItemSelection: (id) =>
				set((state) => {
					const exists = state.selectedItemIds.includes(id);
					return {
						selectedItemIds: exists
							? state.selectedItemIds.filter((itemId) => itemId !== id)
							: [...state.selectedItemIds, id],
					};
				}),

			clearSelection: () => set({ selectedItemId: null, selectedItemIds: [] }),

			toggleCommandPalette: () =>
				set((state) => ({
					commandPaletteOpen: !state.commandPaletteOpen,
				})),

			setSearchQuery: (query) => set({ searchQuery: query }),

			toggleSearch: () => set((state) => ({ searchOpen: !state.searchOpen })),

			setStatusFilter: (statuses) => set({ statusFilter: statuses }),

			setPriorityFilter: (priorities) => set({ priorityFilter: priorities }),

			setLayoutMode: (mode) => set({ layoutMode: mode }),

			setGridColumns: (columns) => set({ gridColumns: columns }),
		}),
		{
			name: "tracertm-ui-store",
			partialize: (state) => ({
				gridColumns: state.gridColumns,
				isDarkMode: state.isDarkMode,
				layoutMode: state.layoutMode,
				sidebarOpen: state.sidebarOpen,
				sidebarWidth: state.sidebarWidth,
			}),
			storage: createJSONStorage(() => getStorage()),
		},
	),
);

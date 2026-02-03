import type { Mutation } from "@tracertm/types";
import { create } from "zustand";

interface SyncState {
	// Online status
	isOnline: boolean;

	// Sync status
	isSyncing: boolean;
	lastSyncedAt: Date | null;
	syncError: string | null;

	// Pending mutations queue
	pendingMutations: Mutation[];
	failedMutations: Mutation[];

	// Conflict resolution
	conflicts: {
		mutation: Mutation;
		serverData: unknown;
		localData: unknown;
	}[];

	// Actions
	setOnline: (online: boolean) => void;
	startSync: () => void;
	finishSync: (error?: string) => void;
	addPendingMutation: (mutation: Mutation) => void;
	removePendingMutation: (mutationId: string) => void;
	moveMutationToFailed: (mutationId: string) => void;
	retryFailedMutation: (mutationId: string) => void;
	clearFailedMutations: () => void;
	addConflict: (
		mutation: Mutation,
		serverData: unknown,
		localData: unknown,
	) => void;
	resolveConflict: (mutationId: string) => void;
	reset: () => void;
}

export const useSyncStore = create<SyncState>((set, _get) => ({
	// Initial state
	isOnline: typeof navigator !== "undefined" ? navigator.onLine : true,
	isSyncing: false,
	lastSyncedAt: null,
	syncError: null,
	pendingMutations: [],
	failedMutations: [],
	conflicts: [],

	// Actions
	setOnline: (online) => set({ isOnline: online }),

	startSync: () => set({ isSyncing: true, syncError: null }),

	finishSync: (error) =>
		set({
			isSyncing: false,
			lastSyncedAt: error ? null : new Date(),
			syncError: error || null,
		}),

	addPendingMutation: (mutation) =>
		set((state) => ({
			pendingMutations: [...state.pendingMutations, mutation],
		})),

	removePendingMutation: (mutationId) =>
		set((state) => ({
			pendingMutations: state.pendingMutations.filter(
				(m) => m.id !== mutationId,
			),
		})),

	moveMutationToFailed: (mutationId) =>
		set((state) => {
			const mutation = state.pendingMutations.find((m) => m.id === mutationId);
			if (!mutation) {
				return state;
			}

			return {
				failedMutations: [...state.failedMutations, mutation],
				pendingMutations: state.pendingMutations.filter(
					(m) => m.id !== mutationId,
				),
			};
		}),

	retryFailedMutation: (mutationId) =>
		set((state) => {
			const mutation = state.failedMutations.find((m) => m.id === mutationId);
			if (!mutation) {
				return state;
			}

			return {
				failedMutations: state.failedMutations.filter(
					(m) => m.id !== mutationId,
				),
				pendingMutations: [...state.pendingMutations, mutation],
			};
		}),

	clearFailedMutations: () => set({ failedMutations: [] }),

	addConflict: (mutation, serverData, localData) =>
		set((state) => ({
			conflicts: [...state.conflicts, { localData, mutation, serverData }],
		})),

	resolveConflict: (mutationId) =>
		set((state) => ({
			conflicts: state.conflicts.filter((c) => c.mutation.id !== mutationId),
		})),

	reset: () =>
		set({
			conflicts: [],
			failedMutations: [],
			isSyncing: false,
			lastSyncedAt: null,
			pendingMutations: [],
			syncError: null,
		}),
}));

// Setup online/offline listeners
if ("window" in globalThis) {
	globalThis.addEventListener("online", () =>
		useSyncStore.getState().setOnline(true),
	);
	globalThis.addEventListener("offline", () =>
		useSyncStore.getState().setOnline(false),
	);
}

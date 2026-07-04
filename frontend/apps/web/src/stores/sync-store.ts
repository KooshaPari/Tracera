import { create } from 'zustand';

import type { Mutation } from '@tracertm/types';

interface SyncConflict {
  localData: unknown;
  mutation: Mutation;
  serverData: unknown;
}

interface SyncDataState {
  conflicts: SyncConflict[];
  failedMutations: Mutation[];
  isOnline: boolean;
  isSyncing: boolean;
  lastSyncedAt: Date | null;
  pendingMutations: Mutation[];
  syncError: string | null;
}

interface SyncActions {
  addConflict: (mutation: Mutation, serverData: unknown, localData: unknown) => void;
  addPendingMutation: (mutation: Mutation) => void;
  clearFailedMutations: () => void;
  finishSync: (error?: string) => void;
  moveMutationToFailed: (mutationId: string) => void;
  removePendingMutation: (mutationId: string) => void;
  reset: () => void;
  resolveConflict: (mutationId: string) => void;
  retryFailedMutation: (mutationId: string) => void;
  setOnline: (online: boolean) => void;
  startSync: () => void;
}

type SyncState = SyncDataState & SyncActions;

type SyncSetter = (
  partial: Partial<SyncState> | ((state: SyncState) => Partial<SyncState> | SyncState),
) => void;

type SyncGetter = () => SyncState;

const createInitialState = (): SyncDataState => ({
  conflicts: [],
  failedMutations: [],
  isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
  isSyncing: false,
  lastSyncedAt: null,
  pendingMutations: [],
  syncError: null,
});

const createStatusActions = (
  set: SyncSetter,
): Pick<SyncActions, 'finishSync' | 'setOnline' | 'startSync'> => ({
  finishSync: (error) => {
    set((state) => ({
      isSyncing: false,
      lastSyncedAt: error ? null : new Date(),
      syncError: error ?? null,
    }));
  },
  setOnline: (online) => {
    set((state) => ({ isOnline: online }));
  },
  startSync: () => {
    set((state) => ({ isSyncing: true, syncError: null }));
  },
});

const createMutationActions = (
  set: SyncSetter,
): Pick<
  SyncActions,
  | 'addPendingMutation'
  | 'clearFailedMutations'
  | 'moveMutationToFailed'
  | 'removePendingMutation'
  | 'retryFailedMutation'
> => ({
  addPendingMutation: (mutation) => {
    set((state) => ({
      pendingMutations: [...state.pendingMutations, mutation],
    }));
  },
  clearFailedMutations: () => {
    set({ failedMutations: [] });
  },
  moveMutationToFailed: (mutationId) => {
    set((state) => {
      const mutation = state.pendingMutations.find(
        (candidate) => candidate.id !== undefined && candidate.id === mutationId,
      );
      if (!mutation) {
        return state;
      }

      return {
        failedMutations: [...state.failedMutations, mutation],
        pendingMutations: state.pendingMutations.filter((candidate) => candidate.id !== mutationId),
      };
    });
  },
  removePendingMutation: (mutationId) => {
    set((state) => ({
      pendingMutations: state.pendingMutations.filter((mutation) => mutation.id !== mutationId),
    }));
  },
  retryFailedMutation: (mutationId) => {
    set((state) => {
      const mutation = state.failedMutations.find(
        (candidate) => candidate.id !== undefined && candidate.id === mutationId,
      );
      if (!mutation) {
        return state;
      }

      return {
        failedMutations: state.failedMutations.filter((candidate) => candidate.id !== mutationId),
        pendingMutations: [...state.pendingMutations, mutation],
      };
    });
  },
});

const createConflictActions = (
  set: SyncSetter,
): Pick<SyncActions, 'addConflict' | 'resolveConflict'> => ({
  addConflict: (mutation, serverData, localData) => {
    set((state) => ({
      conflicts: [...state.conflicts, { localData, mutation, serverData }],
    }));
  },
  resolveConflict: (mutationId) => {
    set((state) => ({
      conflicts: state.conflicts.filter((conflict) => conflict.mutation.id !== mutationId),
    }));
  },
});

const createResetAction = (set: SyncSetter): Pick<SyncActions, 'reset'> => ({
  reset: () => {
    set({
      conflicts: [],
      failedMutations: [],
      isSyncing: false,
      lastSyncedAt: null,
      pendingMutations: [],
      syncError: null,
    });
  },
});

const buildSyncStore = (set: SyncSetter, _get: SyncGetter): SyncState => ({
  ...createInitialState(),
  ...createStatusActions(set),
  ...createMutationActions(set),
  ...createConflictActions(set),
  ...createResetAction(set),
});

export const useSyncStore = create<SyncState>((set, get) => buildSyncStore(set, get));

// Setup online/offline listeners
if ('window' in globalThis) {
  globalThis.addEventListener('online', () => {
    useSyncStore.getState().setOnline(true);
  });
  globalThis.addEventListener('offline', () => {
    useSyncStore.getState().setOnline(false);
  });
}

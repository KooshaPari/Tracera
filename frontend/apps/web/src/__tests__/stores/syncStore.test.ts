/**
 * Tests for syncStore - Offline-first data synchronization
 */

import { beforeEach, describe, expect, it } from 'vitest';

import type { Mutation } from '@tracertm/types';

import { useSyncStore } from '../../stores/sync-store';

// Mock mutation factory
const createMockMutation = (overrides?: Partial<Mutation>): Mutation => ({
  id: `mutation-${Math.random()}`,
  type: 'CREATE' as const,
  entity: 'item',
  entityId: 'item-1',
  data: { title: 'Test Item' },
  timestamp: new Date(),
  ...overrides,
});

describe('syncStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useSyncStore.getState().reset();
  });

  describe('Initial State', () => {
    it('should initialize with correct default values', () => {
      const state = useSyncStore.getState();
      // After reset, verify core state values
      expect(state.isSyncing).toBeFalsy();
      expect(state.lastSyncedAt).toBeNull();
      expect(state.syncError).toBeNull();
      expect(state.pendingMutations).toEqual([]);
      expect(state.failedMutations).toEqual([]);
      expect(state.conflicts).toEqual([]);
    });
  });

  describe('Online/Offline Status', () => {
    it('should set online status to false', () => {
      useSyncStore.getState().setOnline(false);
      expect(useSyncStore.getState().isOnline).toBeFalsy();
    });

    it('should toggle online status', () => {
      useSyncStore.getState().setOnline(false);
      expect(useSyncStore.getState().isOnline).toBeFalsy();

      useSyncStore.getState().setOnline(true);
      expect(useSyncStore.getState().isOnline).toBeTruthy();
    });

    it('should handle multiple transitions', () => {
      const transitions = [false, true, false, true, false];
      transitions.forEach((online) => {
        useSyncStore.getState().setOnline(online);
        expect(useSyncStore.getState().isOnline).toBe(online);
      });
    });
  });

  describe('Sync Operations', () => {
    it('should start sync', () => {
      useSyncStore.getState().startSync();
      expect(useSyncStore.getState().isSyncing).toBeTruthy();
      expect(useSyncStore.getState().syncError).toBeNull();
    });

    it('should finish sync without error', () => {
      useSyncStore.getState().startSync();
      useSyncStore.getState().finishSync();

      expect(useSyncStore.getState().isSyncing).toBeFalsy();
      expect(useSyncStore.getState().syncError).toBeNull();
      expect(useSyncStore.getState().lastSyncedAt).toBeInstanceOf(Date);
    });

    it('should finish sync with error', () => {
      const errorMessage = 'Network error';
      useSyncStore.getState().startSync();
      useSyncStore.getState().finishSync(errorMessage);

      expect(useSyncStore.getState().isSyncing).toBeFalsy();
      expect(useSyncStore.getState().syncError).toBe(errorMessage);
      expect(useSyncStore.getState().lastSyncedAt).toBeNull();
    });

    it('should clear sync error on successful sync', () => {
      useSyncStore.getState().startSync();
      useSyncStore.getState().finishSync('Initial error');
      expect(useSyncStore.getState().syncError).toBe('Initial error');

      useSyncStore.getState().startSync();
      useSyncStore.getState().finishSync();
      expect(useSyncStore.getState().syncError).toBeNull();
      expect(useSyncStore.getState().lastSyncedAt).toBeInstanceOf(Date);
    });
  });

  describe('Pending Mutations Queue', () => {
    it('should add pending mutation', () => {
      const mutation = createMockMutation();
      useSyncStore.getState().addPendingMutation(mutation);

      expect(useSyncStore.getState().pendingMutations).toHaveLength(1);
      expect(useSyncStore.getState().pendingMutations[0]).toEqual(mutation);
    });

    it('should add multiple mutations in FIFO order', () => {
      const m1 = createMockMutation({ id: 'mut-1' });
      const m2 = createMockMutation({ id: 'mut-2' });
      const m3 = createMockMutation({ id: 'mut-3' });

      useSyncStore.getState().addPendingMutation(m1);
      useSyncStore.getState().addPendingMutation(m2);
      useSyncStore.getState().addPendingMutation(m3);

      const mutations = useSyncStore.getState().pendingMutations;
      expect(mutations).toHaveLength(3);
      expect(mutations[0].id).toBe('mut-1');
      expect(mutations[1].id).toBe('mut-2');
      expect(mutations[2].id).toBe('mut-3');
    });

    it('should remove pending mutation', () => {
      const m = createMockMutation({ id: 'mut-1' });
      useSyncStore.getState().addPendingMutation(m);
      expect(useSyncStore.getState().pendingMutations).toHaveLength(1);

      useSyncStore.getState().removePendingMutation('mut-1');
      expect(useSyncStore.getState().pendingMutations).toHaveLength(0);
    });

    it('should not remove non-existent mutation', () => {
      const m = createMockMutation({ id: 'mut-1' });
      useSyncStore.getState().addPendingMutation(m);
      useSyncStore.getState().removePendingMutation('non-existent');

      expect(useSyncStore.getState().pendingMutations).toHaveLength(1);
    });

    it('should preserve order when removing mutations', () => {
      const mutations = [
        createMockMutation({ id: 'mut-1' }),
        createMockMutation({ id: 'mut-2' }),
        createMockMutation({ id: 'mut-3' }),
      ];

      mutations.forEach((m) => useSyncStore.getState().addPendingMutation(m));
      useSyncStore.getState().removePendingMutation('mut-2');

      const remaining = useSyncStore.getState().pendingMutations;
      expect(remaining).toHaveLength(2);
      expect(remaining[0].id).toBe('mut-1');
      expect(remaining[1].id).toBe('mut-3');
    });
  });

  describe('Failed Mutations Management', () => {
    it('should move mutation from pending to failed', () => {
      const m = createMockMutation({ id: 'mut-1' });
      useSyncStore.getState().addPendingMutation(m);
      useSyncStore.getState().moveMutationToFailed('mut-1');

      expect(useSyncStore.getState().pendingMutations).toHaveLength(0);
      expect(useSyncStore.getState().failedMutations).toHaveLength(1);
      expect(useSyncStore.getState().failedMutations[0].id).toBe('mut-1');
    });

    it('should not fail non-existent mutation', () => {
      const m = createMockMutation({ id: 'mut-1' });
      useSyncStore.getState().addPendingMutation(m);
      useSyncStore.getState().moveMutationToFailed('non-existent');

      expect(useSyncStore.getState().pendingMutations).toHaveLength(1);
      expect(useSyncStore.getState().failedMutations).toHaveLength(0);
    });

    it('should retry failed mutation', () => {
      const m = createMockMutation({ id: 'mut-1' });
      useSyncStore.getState().addPendingMutation(m);
      useSyncStore.getState().moveMutationToFailed('mut-1');

      expect(useSyncStore.getState().failedMutations).toHaveLength(1);
      expect(useSyncStore.getState().pendingMutations).toHaveLength(0);

      useSyncStore.getState().retryFailedMutation('mut-1');
      expect(useSyncStore.getState().failedMutations).toHaveLength(0);
      expect(useSyncStore.getState().pendingMutations).toHaveLength(1);
    });

    it('should clear all failed mutations', () => {
      const mutations = [
        createMockMutation({ id: 'mut-1' }),
        createMockMutation({ id: 'mut-2' }),
        createMockMutation({ id: 'mut-3' }),
      ];

      mutations.forEach((m) => useSyncStore.getState().addPendingMutation(m));
      mutations.forEach((m) => useSyncStore.getState().moveMutationToFailed(m.id));

      expect(useSyncStore.getState().failedMutations).toHaveLength(3);
      useSyncStore.getState().clearFailedMutations();
      expect(useSyncStore.getState().failedMutations).toHaveLength(0);
    });
  });

  describe('Conflict Resolution', () => {
    it('should add conflict', () => {
      const m = createMockMutation({ id: 'mut-1' });
      const serverData = { title: 'Server version' };
      const localData = { title: 'Local version' };

      useSyncStore.getState().addConflict(m, serverData, localData);

      const { conflicts } = useSyncStore.getState();
      expect(conflicts).toHaveLength(1);
      expect(conflicts[0].mutation).toEqual(m);
      expect(conflicts[0].serverData).toEqual(serverData);
      expect(conflicts[0].localData).toEqual(localData);
    });

    it('should resolve conflict', () => {
      const m = createMockMutation({ id: 'mut-1' });
      useSyncStore.getState().addConflict(m, { v: 1 }, { v: 2 });

      expect(useSyncStore.getState().conflicts).toHaveLength(1);

      useSyncStore.getState().resolveConflict('mut-1');
      expect(useSyncStore.getState().conflicts).toHaveLength(0);
    });

    it('should preserve other conflicts when resolving one', () => {
      const mutations = [
        createMockMutation({ id: 'mut-1' }),
        createMockMutation({ id: 'mut-2' }),
        createMockMutation({ id: 'mut-3' }),
      ];

      mutations.forEach((m) => {
        useSyncStore.getState().addConflict(m, { v: 1 }, { v: 2 });
      });

      useSyncStore.getState().resolveConflict('mut-2');

      const remaining = useSyncStore.getState().conflicts;
      expect(remaining).toHaveLength(2);
      expect(remaining.map((c) => c.mutation.id)).toEqual(['mut-1', 'mut-3']);
    });
  });

  describe('Reset', () => {
    it('should reset entire store state', () => {
      const m = createMockMutation();

      // Set up complex state
      useSyncStore.getState().setOnline(false);
      useSyncStore.getState().startSync();
      useSyncStore.getState().addPendingMutation(m);
      useSyncStore.getState().finishSync('error');

      expect(useSyncStore.getState().isSyncing).toBeFalsy();
      expect(useSyncStore.getState().syncError).toBe('error');
      expect(useSyncStore.getState().pendingMutations).toHaveLength(1);

      // Reset
      useSyncStore.getState().reset();

      const state = useSyncStore.getState();
      expect(state.isSyncing).toBeFalsy();
      expect(state.lastSyncedAt).toBeNull();
      expect(state.syncError).toBeNull();
      expect(state.pendingMutations).toHaveLength(0);
      expect(state.failedMutations).toHaveLength(0);
      expect(state.conflicts).toHaveLength(0);
    });
  });

  describe('Integration Scenarios', () => {
    it('should handle offline -> queue -> online -> sync -> success', () => {
      const mutations = [createMockMutation({ id: 'mut-1' }), createMockMutation({ id: 'mut-2' })];

      // Go offline and queue mutations
      useSyncStore.getState().setOnline(false);
      mutations.forEach((m) => useSyncStore.getState().addPendingMutation(m));

      expect(useSyncStore.getState().isOnline).toBeFalsy();
      expect(useSyncStore.getState().pendingMutations).toHaveLength(2);

      // Go online and sync
      useSyncStore.getState().setOnline(true);
      useSyncStore.getState().startSync();

      useSyncStore.getState().removePendingMutation('mut-1');
      useSyncStore.getState().removePendingMutation('mut-2');
      useSyncStore.getState().finishSync();

      const state = useSyncStore.getState();
      expect(state.isSyncing).toBeFalsy();
      expect(state.syncError).toBeNull();
      expect(state.lastSyncedAt).toBeInstanceOf(Date);
      expect(state.pendingMutations).toHaveLength(0);
    });

    it('should handle sync failure with retry', () => {
      const m = createMockMutation({ id: 'mut-1' });

      useSyncStore.getState().addPendingMutation(m);
      useSyncStore.getState().startSync();
      useSyncStore.getState().moveMutationToFailed('mut-1');
      useSyncStore.getState().finishSync('Network timeout');

      expect(useSyncStore.getState().failedMutations).toHaveLength(1);
      expect(useSyncStore.getState().syncError).toBe('Network timeout');

      // Retry
      useSyncStore.getState().startSync();
      useSyncStore.getState().retryFailedMutation('mut-1');
      useSyncStore.getState().removePendingMutation('mut-1');
      useSyncStore.getState().finishSync();

      const state = useSyncStore.getState();
      expect(state.failedMutations).toHaveLength(0);
      expect(state.pendingMutations).toHaveLength(0);
      expect(state.syncError).toBeNull();
    });

    it('should handle conflict resolution during sync', () => {
      const m = createMockMutation({ id: 'mut-1' });
      const serverData = { title: 'Server version' };
      const localData = { title: 'Local version' };

      useSyncStore.getState().addPendingMutation(m);
      useSyncStore.getState().startSync();
      useSyncStore.getState().addConflict(m, serverData, localData);
      useSyncStore.getState().moveMutationToFailed('mut-1');

      expect(useSyncStore.getState().conflicts).toHaveLength(1);
      expect(useSyncStore.getState().failedMutations).toHaveLength(1);

      useSyncStore.getState().resolveConflict('mut-1');
      expect(useSyncStore.getState().conflicts).toHaveLength(0);
    });
  });
});

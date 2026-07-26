import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

import {
  clearMutationQueue,
  getPendingMutationCount,
  getQueuedMutations,
  queueMutation,
  removeMutationFromQueue,
  updateMutationError,
} from '@/lib/mutation-queue';

describe('Mutation Queue', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('queueMutation', () => {
    it('should add a mutation to the queue', () => {
      const id = queueMutation({
        createdAt: new Date().toISOString(),
        data: { name: 'Test Item' },
        failedAttempts: 1,
        type: 'create_item',
      });

      expect(id).toBeDefined();
      expect(id).toMatch(/^mutation_\d+_[a-z0-9]+$/);

      const mutations = getQueuedMutations();
      expect(mutations).toHaveLength(1);
      expect(mutations[0].id).toBe(id);
      expect(mutations[0].type).toBe('create_item');
    });

    it('should add multiple mutations to the queue', () => {
      const id1 = queueMutation({
        createdAt: new Date().toISOString(),
        data: { name: 'Item 1' },
        failedAttempts: 1,
        type: 'create_item',
      });

      const id2 = queueMutation({
        createdAt: new Date().toISOString(),
        data: { name: 'Item 2' },
        failedAttempts: 1,
        type: 'create_item',
      });

      const mutations = getQueuedMutations();
      expect(mutations).toHaveLength(2);
      expect(mutations[0].id).toBe(id1);
      expect(mutations[1].id).toBe(id2);
    });
  });

  describe('getQueuedMutations', () => {
    it('should return empty array when queue is empty', () => {
      const mutations = getQueuedMutations();
      expect(mutations).toEqual([]);
    });

    it('should return all queued mutations', () => {
      queueMutation({
        createdAt: new Date().toISOString(),
        data: { name: 'Item 1' },
        failedAttempts: 1,
        type: 'create_item',
      });

      queueMutation({
        createdAt: new Date().toISOString(),
        data: { name: 'Item 2' },
        failedAttempts: 2,
        type: 'update_item',
      });

      const mutations = getQueuedMutations();
      expect(mutations).toHaveLength(2);
      expect(mutations[0].type).toBe('create_item');
      expect(mutations[1].type).toBe('update_item');
    });

    it('should return empty array on corrupted localStorage', () => {
      localStorage.setItem('pending_mutations', 'invalid json');
      const mutations = getQueuedMutations();
      expect(mutations).toEqual([]);
    });
  });

  describe('removeMutationFromQueue', () => {
    it('should remove a mutation from the queue', () => {
      const id = queueMutation({
        createdAt: new Date().toISOString(),
        data: { name: 'Item' },
        failedAttempts: 1,
        type: 'create_item',
      });

      expect(getQueuedMutations()).toHaveLength(1);

      removeMutationFromQueue(id);

      expect(getQueuedMutations()).toHaveLength(0);
    });

    it('should not affect other mutations', () => {
      const id1 = queueMutation({
        createdAt: new Date().toISOString(),
        data: { name: 'Item 1' },
        failedAttempts: 1,
        type: 'create_item',
      });

      const id2 = queueMutation({
        createdAt: new Date().toISOString(),
        data: { name: 'Item 2' },
        failedAttempts: 1,
        type: 'create_item',
      });

      removeMutationFromQueue(id1);

      const mutations = getQueuedMutations();
      expect(mutations).toHaveLength(1);
      expect(mutations[0].id).toBe(id2);
    });
  });

  describe('updateMutationError', () => {
    it('should update error information for a mutation', () => {
      const id = queueMutation({
        createdAt: new Date().toISOString(),
        data: { name: 'Item' },
        failedAttempts: 1,
        type: 'create_item',
      });

      updateMutationError(id, 'Network error', 2);

      const mutations = getQueuedMutations();
      expect(mutations[0].failedAttempts).toBe(2);
      expect(mutations[0].lastError).toBe('Network error');
    });

    it('should not update if mutation not found', () => {
      const id = queueMutation({
        createdAt: new Date().toISOString(),
        data: { name: 'Item' },
        failedAttempts: 1,
        type: 'create_item',
      });

      // This should not throw
      updateMutationError('nonexistent_id', 'Error', 2);

      const mutations = getQueuedMutations();
      expect(mutations[0].failedAttempts).toBe(1);
      expect(mutations[0].lastError).toBeUndefined();
    });
  });

  describe('clearMutationQueue', () => {
    it('should clear all mutations', () => {
      queueMutation({
        createdAt: new Date().toISOString(),
        data: { name: 'Item' },
        failedAttempts: 1,
        type: 'create_item',
      });

      expect(getQueuedMutations()).toHaveLength(1);

      clearMutationQueue();

      expect(getQueuedMutations()).toHaveLength(0);
    });
  });

  describe('getPendingMutationCount', () => {
    it('should return count of pending mutations', () => {
      expect(getPendingMutationCount()).toBe(0);

      queueMutation({
        createdAt: new Date().toISOString(),
        data: { name: 'Item 1' },
        failedAttempts: 1,
        type: 'create_item',
      });

      expect(getPendingMutationCount()).toBe(1);

      queueMutation({
        createdAt: new Date().toISOString(),
        data: { name: 'Item 2' },
        failedAttempts: 1,
        type: 'create_item',
      });

      expect(getPendingMutationCount()).toBe(2);

      clearMutationQueue();

      expect(getPendingMutationCount()).toBe(0);
    });
  });
});

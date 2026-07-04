/**
 * State Management Integration Tests (2 tests)
 *
 * Verifies Zustand store workflows: project store, items store, sync store.
 * Target: 5% integration layer in test pyramid.
 */

import { beforeEach, describe, expect, it } from 'vitest';

import type { Project } from '../../api/types';

import { useItemsStore } from '../../stores/items-store';
import { useProjectStore } from '../../stores/project-store';
import { useSyncStore } from '../../stores/sync-store';

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------

const createMockProject = (overrides?: Partial<Project>): Project =>
  ({
    id: 'proj-1',
    name: 'Test Project',
    description: 'A test project',
    metadata: {},
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ...overrides,
  }) as Project;

// -----------------------------------------------------------------------------
// Zustand workflow tests
// -----------------------------------------------------------------------------

describe('State Management Integration', () => {
  beforeEach(() => {
    useProjectStore.getState().clearCurrentProject();
    useProjectStore.setState({
      recentProjects: [],
      projectSettings: {},
    });
    useItemsStore.getState().clearItems();
    useSyncStore.getState().reset();
  });

  describe('project store workflow', () => {
    it('setCurrentProject updates current project and recent list; settings persist', () => {
      const project = createMockProject({ id: 'p1', name: 'First' });
      const project2 = createMockProject({ id: 'p2', name: 'Second' });

      useProjectStore.getState().setCurrentProject(project);
      expect(useProjectStore.getState().currentProjectId).toBe('p1');
      expect(useProjectStore.getState().recentProjects).toContain('p1');

      useProjectStore.getState().setCurrentProject(project2);
      expect(useProjectStore.getState().currentProjectId).toBe('p2');
      expect(useProjectStore.getState().recentProjects[0]).toBe('p2');
      expect(useProjectStore.getState().recentProjects).toContain('p1');

      useProjectStore.getState().pinItem('p1', 'item-1');
      expect(useProjectStore.getState().getProjectSettings('p1').pinnedItems).toContain('item-1');

      useProjectStore.getState().clearCurrentProject();
      expect(useProjectStore.getState().currentProjectId).toBeNull();
      expect(useProjectStore.getState().currentProject).toBeNull();
      // Recent list and project settings are unchanged (persisted)
      expect(useProjectStore.getState().recentProjects).toHaveLength(2);
      expect(useProjectStore.getState().getProjectSettings('p1').pinnedItems).toContain('item-1');
    });
  });

  describe('items store and sync store workflow', () => {
    it('optimistic create then confirm; sync store startSync and finishSync', () => {
      const tempId = 'temp-1';
      const realItem = {
        id: 'item-real',
        projectId: 'proj-1',
        title: 'Real Item',
        type: 'requirement',
        status: 'todo' as const,
        priority: 'medium' as const,
        view: 'FEATURE' as const,
        version: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      useItemsStore.getState().optimisticCreate(tempId, {
        projectId: 'proj-1',
        title: 'New Item',
        type: 'requirement',
      });

      expect(useItemsStore.getState().getItem(tempId)).toBeDefined();
      expect(useItemsStore.getState().getItem(tempId)?.title).toBe('New Item');
      expect(useItemsStore.getState().pendingCreates.has(tempId)).toBeTruthy();

      useItemsStore.getState().confirmCreate(tempId, realItem);

      expect(useItemsStore.getState().getItem(tempId)).toBeUndefined();
      expect(useItemsStore.getState().getItem('item-real')).toEqual(realItem);
      expect(useItemsStore.getState().pendingCreates.has(tempId)).toBeFalsy();

      // Sync store workflow
      useSyncStore.getState().startSync();
      expect(useSyncStore.getState().isSyncing).toBeTruthy();

      useSyncStore.getState().addPendingMutation({
        id: 'mut-1',
        type: 'create',
        payload: {},
      } as any);
      expect(useSyncStore.getState().pendingMutations).toHaveLength(1);

      useSyncStore.getState().finishSync();
      expect(useSyncStore.getState().isSyncing).toBeFalsy();
      expect(useSyncStore.getState().lastSyncedAt).toBeInstanceOf(Date);
      expect(useSyncStore.getState().syncError).toBeNull();
    });
  });
});

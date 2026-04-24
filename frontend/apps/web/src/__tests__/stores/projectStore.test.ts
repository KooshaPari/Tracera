/**
 * Tests for projectStore
 */

import { act, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';

import type { Project } from '@tracertm/types';

import { useProjectStore } from '../../stores/project-store';

const createMockProject = (overrides: Partial<Project> = {}): Project => ({
  createdAt: new Date().toISOString(),
  description: 'Test Project',
  id: 'proj-1',
  name: 'Test Project',
  updatedAt: new Date().toISOString(),
  ...overrides,
});

describe('projectStore', () => {
  beforeEach(() => {
    // Reset store state
    const { clearCurrentProject } = useProjectStore.getState();
    clearCurrentProject();
    localStorage.clear();
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const { result } = renderHook(() => useProjectStore());

      expect(result.current.currentProjectId).toBeNull();
      expect(result.current.currentProject).toBeNull();
      expect(result.current.recentProjects).toEqual([]);
      expect(result.current.projectSettings).toEqual({});
    });
  });

  describe('setCurrentProject', () => {
    it('should set current project', () => {
      const { result } = renderHook(() => useProjectStore());
      const project = createMockProject({ id: 'proj-1', name: 'Test Project' });

      act(() => {
        result.current.setCurrentProject(project);
      });

      expect(result.current.currentProject).toEqual(project);
      expect(result.current.currentProjectId).toBe('proj-1');
    });

    it('should add project to recent projects', () => {
      const { result } = renderHook(() => useProjectStore());
      const project = createMockProject({ id: 'proj-1' });

      act(() => {
        result.current.setCurrentProject(project);
      });

      expect(result.current.recentProjects).toContain('proj-1');
    });

    it('should clear current project when null', () => {
      const { result } = renderHook(() => useProjectStore());
      const project = createMockProject({ id: 'proj-1' });

      act(() => {
        result.current.setCurrentProject(project);
        result.current.setCurrentProject(null);
      });

      expect(result.current.currentProject).toBeNull();
      expect(result.current.currentProjectId).toBeNull();
    });
  });

  describe('addRecentProject', () => {
    it('should add project to recent list', () => {
      const { result } = renderHook(() => useProjectStore());

      act(() => {
        result.current.addRecentProject('proj-1');
      });

      expect(result.current.recentProjects).toContain('proj-1');
    });

    it('should move project to top if already in list', () => {
      const { result } = renderHook(() => useProjectStore());

      act(() => {
        result.current.addRecentProject('proj-1');
        result.current.addRecentProject('proj-2');
        result.current.addRecentProject('proj-1');
      });

      expect(result.current.recentProjects[0]).toBe('proj-1');
    });

    it('should limit recent projects to 10', () => {
      const { result } = renderHook(() => useProjectStore());

      act(() => {
        for (let i = 0; i < 15; i++) {
          result.current.addRecentProject(`proj-${i}`);
        }
      });

      expect(result.current.recentProjects.length).toBe(10);
    });
  });

  describe('projectSettings', () => {
    it('should get project settings', () => {
      const { result } = renderHook(() => useProjectStore());

      const settings = result.current.getProjectSettings('proj-1');

      expect(settings).toEqual({});
    });

    it('should update project settings', () => {
      const { result } = renderHook(() => useProjectStore());

      act(() => {
        result.current.updateProjectSettings('proj-1', {
          defaultView: 'kanban',
        });
      });

      const settings = result.current.getProjectSettings('proj-1');
      expect(settings.defaultView).toBe('kanban');
    });

    it('should merge settings on update', () => {
      const { result } = renderHook(() => useProjectStore());

      act(() => {
        result.current.updateProjectSettings('proj-1', {
          defaultView: 'kanban',
        });
        result.current.updateProjectSettings('proj-1', {
          pinnedItems: ['item-1'],
        });
      });

      const settings = result.current.getProjectSettings('proj-1');
      expect(settings.defaultView).toBe('kanban');
      expect(settings.pinnedItems).toEqual(['item-1']);
    });
  });

  describe('pinItem / unpinItem', () => {
    it('should pin an item', () => {
      const { result } = renderHook(() => useProjectStore());

      act(() => {
        result.current.pinItem('proj-1', 'item-1');
      });

      const settings = result.current.getProjectSettings('proj-1');
      expect(settings.pinnedItems).toContain('item-1');
    });

    it('should not duplicate pinned items', () => {
      const { result } = renderHook(() => useProjectStore());

      act(() => {
        result.current.pinItem('proj-1', 'item-1');
        result.current.pinItem('proj-1', 'item-1');
      });

      const settings = result.current.getProjectSettings('proj-1');
      expect(settings.pinnedItems?.filter((id: string) => id === 'item-1').length).toBe(1);
    });

    it('should unpin an item', () => {
      const { result } = renderHook(() => useProjectStore());

      act(() => {
        result.current.pinItem('proj-1', 'item-1');
        result.current.pinItem('proj-1', 'item-2');
        result.current.unpinItem('proj-1', 'item-1');
      });

      const settings = result.current.getProjectSettings('proj-1');
      expect(settings.pinnedItems).not.toContain('item-1');
      expect(settings.pinnedItems).toContain('item-2');
    });
  });

  describe('clearCurrentProject', () => {
    it('should clear current project', () => {
      const { result } = renderHook(() => useProjectStore());
      const project = createMockProject({ id: 'proj-1' });

      act(() => {
        result.current.setCurrentProject(project);
        result.current.clearCurrentProject();
      });

      expect(result.current.currentProject).toBeNull();
      expect(result.current.currentProjectId).toBeNull();
    });
  });

  describe('persistence', () => {
    it('should persist state to localStorage', () => {
      const { result } = renderHook(() => useProjectStore());
      const project = createMockProject({ id: 'proj-1' });

      act(() => {
        result.current.setCurrentProject(project);
      });

      const storedData = localStorage.getItem('tracertm-project-store');
      expect(storedData).toBeTruthy();

      if (storedData) {
        const parsed = JSON.parse(storedData);
        expect(parsed.state.currentProjectId).toBe('proj-1');
      }
    });
  });
});

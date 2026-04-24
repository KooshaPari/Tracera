/**
 * Tests for Projects API
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { Project } from '@tracertm/types';

import {
  createProject,
  deleteProject,
  fetchProject,
  fetchProjects,
  updateProject,
} from '@/api/projects';

// Mock endpoints
vi.mock('@/api/endpoints', () => ({
  projectsApi: {
    create: vi.fn(),
    delete: vi.fn(),
    get: vi.fn(),
    list: vi.fn(),
    update: vi.fn(),
  },
}));

import { projectsApi } from '@/api/endpoints';

import { mockProjects } from '../mocks/data';

describe('Projects API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchProjects, () => {
    it('should fetch projects without params', async () => {
      vi.mocked(projectsApi.list).mockResolvedValue(mockProjects);

      const result = await fetchProjects();
      expect(result).toEqual(mockProjects);
      expect(projectsApi.list).toHaveBeenCalledWith();
    });

    it('should fetch projects with params', async () => {
      vi.mocked(projectsApi.list).mockResolvedValue(mockProjects);

      const result = await fetchProjects({ limit: 10, offset: 0 });
      expect(result).toEqual(mockProjects);
      expect(projectsApi.list).toHaveBeenCalledWith({ limit: 10, offset: 0 });
    });
  });

  describe(fetchProject, () => {
    it('should fetch a single project', async () => {
      const project = mockProjects[0];
      vi.mocked(projectsApi.get).mockResolvedValue(project);

      const result = await fetchProject('proj-1');
      expect(result).toEqual(project);
      expect(projectsApi.get).toHaveBeenCalledWith('proj-1');
    });
  });

  describe(createProject, () => {
    it('should create a project', async () => {
      const newProject = { description: 'Test', name: 'New Project' };
      const created: Project = {
        ...mockProjects[0],
        ...newProject,
        id: 'new-proj',
      } as Project;
      vi.mocked(projectsApi.create).mockResolvedValue(created);

      const result = await createProject(newProject);
      expect(result).toEqual(created);
      expect(projectsApi.create).toHaveBeenCalledWith(newProject);
    });
  });

  describe(updateProject, () => {
    it('should update a project', async () => {
      const updates = { name: 'Updated Project' };
      const updated: Project = {
        ...mockProjects[0],
        ...updates,
      } as Project;
      vi.mocked(projectsApi.update).mockResolvedValue(updated);

      const result = await updateProject('proj-1', updates);
      expect(result).toEqual(updated);
      expect(projectsApi.update).toHaveBeenCalledWith('proj-1', updates);
    });
  });

  describe(deleteProject, () => {
    it('should delete a project', async () => {
      vi.mocked(projectsApi.delete).mockResolvedValue();

      await expect(deleteProject('proj-1')).resolves.toBeUndefined();
      expect(projectsApi.delete).toHaveBeenCalledWith('proj-1');
    });
  });
});

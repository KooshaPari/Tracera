import { useState, useEffect, useCallback } from 'react';
import { projectApi, Project } from '../lib/api';
import { listen } from '@tauri-apps/api/event';

export function useProjects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectApi.list();
      setProjects(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects');
      console.error('Failed to load projects:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProjects();

    // Listen for sync events to refresh projects
    const unlisten = listen('sync-completed', () => {
      loadProjects();
    });

    return () => {
      unlisten.then(fn => fn());
    };
  }, [loadProjects]);

  const createProject = useCallback(async (name: string, description?: string) => {
    try {
      const project = await projectApi.create(name, description);
      setProjects(prev => [project, ...prev]);
      return project;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
      throw err;
    }
  }, []);

  const updateProject = useCallback(async (project: Project) => {
    try {
      await projectApi.update(project);
      setProjects(prev =>
        prev.map(p => (p.id === project.id ? project : p))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update project');
      throw err;
    }
  }, []);

  const deleteProject = useCallback(async (id: string) => {
    try {
      await projectApi.delete(id);
      setProjects(prev => prev.filter(p => p.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete project');
      throw err;
    }
  }, []);

  return {
    projects,
    loading,
    error,
    loadProjects,
    createProject,
    updateProject,
    deleteProject,
  };
}

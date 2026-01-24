// Re-export projects API from endpoints
import { projectsApi } from "./endpoints";

export const fetchProjects = projectsApi.list;
export const fetchProject = projectsApi.get;
export const createProject = projectsApi.create;
export const updateProject = projectsApi.update;
export const deleteProject = projectsApi.delete;

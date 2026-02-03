/* oxlint-disable oxc/no-async-await */
// Re-export projects API from endpoints
import { projectsApi } from "./endpoints";

const fetchProjects = projectsApi.list;
const fetchProject = projectsApi.get;
const createProject = projectsApi.create;
const updateProject = projectsApi.update;
const deleteProject = projectsApi.delete;

const projectsApiExports = {
	createProject,
	deleteProject,
	fetchProject,
	fetchProjects,
	updateProject,
};

// eslint-disable-next-line import/no-default-export
export default projectsApiExports;

/**
 * Tests for Projects API
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	createProject,
	deleteProject,
	fetchProject,
	fetchProjects,
	updateProject,
} from "@/api/projects";

// Mock endpoints
vi.mock("@/api/endpoints", () => ({
	projectsApi: {
		list: vi.fn(),
		get: vi.fn(),
		create: vi.fn(),
		update: vi.fn(),
		delete: vi.fn(),
	},
}));

import { projectsApi } from "@/api/endpoints";
import { mockProjects } from "../mocks/data";

describe("Projects API", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe("fetchProjects", () => {
		it("should fetch projects without params", async () => {
			vi.mocked(projectsApi.list).mockResolvedValue(mockProjects);

			const result = await fetchProjects();
			expect(result).toEqual(mockProjects);
			expect(projectsApi.list).toHaveBeenCalledWith();
		});

		it("should fetch projects with params", async () => {
			vi.mocked(projectsApi.list).mockResolvedValue(mockProjects);

			const result = await fetchProjects({ limit: 10, offset: 0 });
			expect(result).toEqual(mockProjects);
			expect(projectsApi.list).toHaveBeenCalledWith({ limit: 10, offset: 0 });
		});
	});

	describe("fetchProject", () => {
		it("should fetch a single project", async () => {
			vi.mocked(projectsApi.get).mockResolvedValue(mockProjects[0]);

			const result = await fetchProject("proj-1");
			expect(result).toEqual(mockProjects[0]);
			expect(projectsApi.get).toHaveBeenCalledWith("proj-1");
		});
	});

	describe("createProject", () => {
		it("should create a project", async () => {
			const newProject = { name: "New Project", description: "Test" };
			const created = { ...mockProjects[0], ...newProject, id: "new-proj" };
			vi.mocked(projectsApi.create).mockResolvedValue(created);

			const result = await createProject(newProject);
			expect(result).toEqual(created);
			expect(projectsApi.create).toHaveBeenCalledWith(newProject);
		});
	});

	describe("updateProject", () => {
		it("should update a project", async () => {
			const updates = { name: "Updated Project" };
			const updated = { ...mockProjects[0], ...updates };
			vi.mocked(projectsApi.update).mockResolvedValue(updated);

			const result = await updateProject("proj-1", updates);
			expect(result).toEqual(updated);
			expect(projectsApi.update).toHaveBeenCalledWith("proj-1", updates);
		});
	});

	describe("deleteProject", () => {
		it("should delete a project", async () => {
			vi.mocked(projectsApi.delete).mockResolvedValue(undefined);

			await expect(deleteProject("proj-1")).resolves.toBeUndefined();
			expect(projectsApi.delete).toHaveBeenCalledWith("proj-1");
		});
	});
});

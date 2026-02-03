import type {
	UseMutationOptions,
	UseMutationResult,
	UseQueryOptions,
	UseQueryResult,
} from "@tanstack/react-query";
import type { PaginatedResponse, Project } from "@tracertm/types";
import { api, handleApiResponse } from "./query-client";
import { useMutation, useQuery, useQueryClient } from "./react-query-hooks";
import { queryKeys } from "./queries-keys";

type ProjectListResponse = PaginatedResponse<Project>;

type CreateProjectInput = {
	description?: string;
	name: string;
};

type UpdateProjectInput = {
	data: Partial<Project>;
	projectId: string;
};

const useProjects = (
	options?: UseQueryOptions<ProjectListResponse>,
): UseQueryResult<ProjectListResponse> => {
	const baseOptions: UseQueryOptions<ProjectListResponse> = {
		queryFn: () =>
			handleApiResponse(api.get<ProjectListResponse>("/api/v1/projects", {})),
		queryKey: queryKeys.projects,
	};

	return useQuery({ ...baseOptions, ...options });
};

const useProject = (
	projectId: string,
	options?: UseQueryOptions<Project>,
): UseQueryResult<Project> => {
	const baseOptions: UseQueryOptions<Project> = {
		enabled: Boolean(projectId),
		queryFn: () =>
			handleApiResponse(
				api.get<Project>("/api/v1/projects/{projectId}", {
					params: { path: { projectId } },
				}),
			),
		queryKey: queryKeys.project(projectId),
	};

	return useQuery({ ...baseOptions, ...options });
};

const useCreateProject = (
	options?: UseMutationOptions<Project, Error, CreateProjectInput>,
): UseMutationResult<Project, Error, CreateProjectInput> => {
	const queryClient = useQueryClient();
	const baseOptions: UseMutationOptions<Project, Error, CreateProjectInput> = {
		mutationFn: (data: CreateProjectInput) =>
			handleApiResponse(
				api.post<Project>("/api/v1/projects", { body: data }),
			),
		onSuccess: async (): Promise<void> => {
			await queryClient.invalidateQueries({ queryKey: queryKeys.projects });
		},
	};

	return useMutation({ ...baseOptions, ...options });
};

const useUpdateProject = (
	options?: UseMutationOptions<Project, Error, UpdateProjectInput>,
): UseMutationResult<Project, Error, UpdateProjectInput> => {
	const queryClient = useQueryClient();
	const baseOptions: UseMutationOptions<Project, Error, UpdateProjectInput> = {
		mutationFn: (input: UpdateProjectInput) =>
			handleApiResponse(
				api.put<Project>("/api/v1/projects/{projectId}", {
					body: input.data,
					params: { path: { projectId: input.projectId } },
				}),
			),
		onSuccess: async (
			_res: Project,
			variables: UpdateProjectInput,
		): Promise<void> => {
			await queryClient.invalidateQueries({
				queryKey: queryKeys.project(variables.projectId),
			});
			await queryClient.invalidateQueries({ queryKey: queryKeys.projects });
		},
	};

	return useMutation({ ...baseOptions, ...options });
};

const useDeleteProject = (
	options?: UseMutationOptions<void, Error, string>,
): UseMutationResult<void, Error, string> => {
	const queryClient = useQueryClient();
	const baseOptions: UseMutationOptions<void, Error, string> = {
		mutationFn: (projectId: string) =>
			handleApiResponse(
				api.del<void>("/api/v1/projects/{projectId}", {
					params: { path: { projectId } },
				}),
			),
		onSuccess: async (): Promise<void> => {
			await queryClient.invalidateQueries({ queryKey: queryKeys.projects });
		},
	};

	return useMutation({ ...baseOptions, ...options });
};

export {
	useCreateProject,
	useDeleteProject,
	useProject,
	useProjects,
	useUpdateProject,
};

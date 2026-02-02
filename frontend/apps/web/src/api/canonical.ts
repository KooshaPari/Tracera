// eslint-disable-next-line import/consistent-type-specifier-style
import { type UseMutationOptions, type UseMutationResult, type UseQueryOptions, type UseQueryResult, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient, handleApiResponse } from "./client";

// eslint-disable-next-line @typescript-eslint/consistent-type-definitions
type ConceptProperties = Record<string, string | number | boolean | object | null | undefined>;
// eslint-disable-next-line @typescript-eslint/consistent-type-definitions
type ProjectionProperties = Record<string, string | number | boolean | object | null | undefined>;
interface CanonicalConcept { id: string; projectId: string; name: string; description?: string; category?: string; properties: ConceptProperties; itemCount: number; createdAt: string; updatedAt: string; }
interface CanonicalProjection { id: string; conceptId: string; itemId: string; confidence: number; mappedProperties: ProjectionProperties; createdAt: string; }
interface PivotTarget { itemId: string; conceptId: string; confidence: number; distance: number; }
interface CreateCanonicalConceptInput { projectId: string; name: string; description?: string; category?: string; properties?: ConceptProperties; }
interface UpdateCanonicalConceptInput { name?: string; description?: string; category?: string; properties?: ConceptProperties; }
interface CanonicalTypes { CanonicalConcept: CanonicalConcept; CanonicalProjection: CanonicalProjection; ConceptProperties: ConceptProperties; CreateCanonicalConceptInput: CreateCanonicalConceptInput; PivotTarget: PivotTarget; ProjectionProperties: ProjectionProperties; UpdateCanonicalConceptInput: UpdateCanonicalConceptInput; }

const canonicalQueryKeys = { all: ["canonical"] as const, detail: (id: string) => [...canonicalQueryKeys.details(), id] as const, details: () => [...canonicalQueryKeys.all, "detail"] as const, list: (projectId: string) => [...canonicalQueryKeys.lists(), projectId] as const, lists: () => [...canonicalQueryKeys.all, "list"] as const, pivots: (itemId: string) => ["canonical", "pivots", itemId] as const, projections: (conceptId: string) => ["canonical", "projections", conceptId] as const };

const apiDelete = apiClient.DELETE;
const apiGet = apiClient.GET;
const apiPost = apiClient.POST;
const apiPut = apiClient.PUT;
const canonicalTypes = {} as CanonicalTypes;
const mergeOptions = <TOptions extends object, UOptions extends object>(base: TOptions, overrides?: UOptions): TOptions & UOptions => {
	if (overrides) {
		return Object.assign(base, overrides);
	}

	return base as TOptions & UOptions;
};

const useCanonicalConcepts = (projectId: string, options?: UseQueryOptions<CanonicalConcept[]>): UseQueryResult<CanonicalConcept[], Error> => {
	const baseOptions = { enabled: Boolean(projectId), queryFn: (): Promise<CanonicalConcept[]> => handleApiResponse(apiGet("/api/v1/projects/{projectId}/concepts", { params: { path: { projectId } } })), queryKey: canonicalQueryKeys.list(projectId) };
	return useQuery(mergeOptions(baseOptions, options));
};

const useCanonicalConcept = (conceptId: string, options?: UseQueryOptions<CanonicalConcept>): UseQueryResult<CanonicalConcept, Error> => {
	const baseOptions = { enabled: Boolean(conceptId), queryFn: (): Promise<CanonicalConcept> => handleApiResponse(apiGet("/api/v1/concepts/{conceptId}", { params: { path: { conceptId } } })), queryKey: canonicalQueryKeys.detail(conceptId) };
	return useQuery(mergeOptions(baseOptions, options));
};

const useCreateCanonicalConcept = (options?: UseMutationOptions<CanonicalConcept, Error, CreateCanonicalConceptInput>): UseMutationResult<CanonicalConcept, Error, CreateCanonicalConceptInput> => {
	const queryClient = useQueryClient();
	const mutationFn = (input: CreateCanonicalConceptInput): Promise<CanonicalConcept> => handleApiResponse(apiPost("/api/v1/projects/{projectId}/concepts", { body: { category: input.category, description: input.description, name: input.name, properties: input.properties }, params: { path: { projectId: input.projectId } } }));
	const onSuccess = (data: CanonicalConcept): Promise<void> => queryClient.invalidateQueries({ queryKey: canonicalQueryKeys.list(data.projectId) });
	const baseOptions = { mutationFn, onSuccess };
	return useMutation(mergeOptions(baseOptions, options));
};

const useUpdateCanonicalConcept = (options?: UseMutationOptions<CanonicalConcept, Error, { conceptId: string; data: UpdateCanonicalConceptInput }>): UseMutationResult<CanonicalConcept, Error, { conceptId: string; data: UpdateCanonicalConceptInput }> => {
	const queryClient = useQueryClient();
	const mutationFn = (input: { conceptId: string; data: UpdateCanonicalConceptInput }): Promise<CanonicalConcept> => handleApiResponse(apiPut("/api/v1/concepts/{conceptId}", { body: { category: input.data.category, description: input.data.description, name: input.data.name, properties: input.data.properties }, params: { path: { conceptId: input.conceptId } } }));
	const onSuccess = (data: CanonicalConcept): void => {
		queryClient.invalidateQueries({ queryKey: canonicalQueryKeys.detail(data.id) });
		queryClient.invalidateQueries({ queryKey: canonicalQueryKeys.lists() });
	};
	const baseOptions = { mutationFn, onSuccess };
	return useMutation(mergeOptions(baseOptions, options));
};

const useDeleteCanonicalConcept = (options?: UseMutationOptions<void, Error, string>): UseMutationResult<void, Error, string> => {
	const queryClient = useQueryClient();
	const mutationFn = (conceptId: string): Promise<void> => handleApiResponse(apiDelete("/api/v1/concepts/{conceptId}", { params: { path: { conceptId } } }));
	const onSuccess = (): Promise<void> => queryClient.invalidateQueries({ queryKey: canonicalQueryKeys.lists() });
	const baseOptions = { mutationFn, onSuccess };
	return useMutation(mergeOptions(baseOptions, options));
};

const useCanonicalProjections = (conceptId: string, options?: UseQueryOptions<CanonicalProjection[]>): UseQueryResult<CanonicalProjection[], Error> => {
	const baseOptions = { enabled: Boolean(conceptId), queryFn: (): Promise<CanonicalProjection[]> => handleApiResponse(apiGet("/api/v1/concepts/{conceptId}/projections", { params: { path: { conceptId } } })), queryKey: canonicalQueryKeys.projections(conceptId) };
	return useQuery(mergeOptions(baseOptions, options));
};

const useCreateCanonicalProjection = (options?: UseMutationOptions<CanonicalProjection, Error, { conceptId: string; itemId: string; confidence?: number }>): UseMutationResult<CanonicalProjection, Error, { conceptId: string; itemId: string; confidence?: number }> => {
	const queryClient = useQueryClient();
	const mutationFn = (input: { conceptId: string; itemId: string; confidence?: number }): Promise<CanonicalProjection> => handleApiResponse(apiPost("/api/v1/concepts/{conceptId}/projections", { body: { confidence: input.confidence, itemId: input.itemId }, params: { path: { conceptId: input.conceptId } } }));
	const onSuccess = (data: CanonicalProjection): Promise<void> => queryClient.invalidateQueries({ queryKey: canonicalQueryKeys.projections(data.conceptId) });
	const baseOptions = { mutationFn, onSuccess };
	return useMutation(mergeOptions(baseOptions, options));
};

const useDeleteCanonicalProjection = (options?: UseMutationOptions<void, Error, { conceptId: string; projectionId: string }>): UseMutationResult<void, Error, { conceptId: string; projectionId: string }> => {
	const queryClient = useQueryClient();
	const mutationFn = (input: { conceptId: string; projectionId: string }): Promise<void> => handleApiResponse(apiDelete("/api/v1/concepts/{conceptId}/projections/{projectionId}", { params: { path: { conceptId: input.conceptId, projectionId: input.projectionId } } }));
	const onSuccess = (_result: void, variables: { conceptId: string; projectionId: string }): Promise<void> => queryClient.invalidateQueries({ queryKey: canonicalQueryKeys.projections(variables.conceptId) });
	const baseOptions = { mutationFn, onSuccess };
	return useMutation(mergeOptions(baseOptions, options));
};

const usePivotTargets = (itemId: string, options?: UseQueryOptions<PivotTarget[]>): UseQueryResult<PivotTarget[], Error> => {
	const baseOptions = { enabled: Boolean(itemId), queryFn: (): Promise<PivotTarget[]> => handleApiResponse(apiGet("/api/v1/items/{itemId}/pivot-targets", { params: { path: { itemId } } })), queryKey: canonicalQueryKeys.pivots(itemId) };
	return useQuery(mergeOptions(baseOptions, options));
};

const usePivotItem = (options?: UseMutationOptions<void, Error, { itemId: string; conceptId: string }>): UseMutationResult<void, Error, { itemId: string; conceptId: string }> => {
	const queryClient = useQueryClient();
	const mutationFn = (input: { itemId: string; conceptId: string }): Promise<void> => handleApiResponse(apiPost("/api/v1/items/{itemId}/pivot", { body: { conceptId: input.conceptId }, params: { path: { itemId: input.itemId } } }));
	const onSuccess = (_result: void, variables: { itemId: string; conceptId: string }): Promise<void> => queryClient.invalidateQueries({ queryKey: canonicalQueryKeys.pivots(variables.itemId) });
	const baseOptions = { mutationFn, onSuccess };
	return useMutation(mergeOptions(baseOptions, options));
};

const canonicalApi = { canonicalQueryKeys, types: canonicalTypes, useCanonicalConcept, useCanonicalConcepts, useCanonicalProjections, useCreateCanonicalConcept, useCreateCanonicalProjection, useDeleteCanonicalConcept, useDeleteCanonicalProjection, usePivotItem, usePivotTargets, useUpdateCanonicalConcept };

// eslint-disable-next-line import/no-default-export
export default canonicalApi;

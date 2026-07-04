import type { UseMutationResult, UseQueryResult } from '@tanstack/react-query';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { CreateProblemData, ProblemFilters, RCAData } from '@/hooks/problems/problemsApi';
import type { Problem, ProblemActivity, ProblemStatus, ResolutionType } from '@tracertm/types';

import { problemsApi } from '@/hooks/problems/problemsApi';

function useProblems(
  filters: ProblemFilters,
): UseQueryResult<{ problems: Problem[]; total: number }> {
  return useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: async () => {
      const result = await problemsApi.fetchProblems(filters);
      return result;
    },
    queryKey: ['problems', JSON.stringify(filters)],
  });
}

function useProblem(id: string): UseQueryResult<Problem> {
  return useQuery({
    enabled: Boolean(id),
    queryFn: async () => {
      const result = await problemsApi.fetchProblem(id);
      return result;
    },
    queryKey: ['problems', id],
  });
}

function useCreateProblem(): UseMutationResult<
  { id: string; problemNumber: string },
  unknown,
  CreateProblemData
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: problemsApi.createProblem,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

function useUpdateProblem(): UseMutationResult<
  { id: string; version: number },
  unknown,
  { id: string; data: Partial<CreateProblemData> }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { id: string; data: Partial<CreateProblemData> }) => {
      const result = await problemsApi.updateProblem(vars.id, vars.data);
      return result;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

function useTransitionProblemStatus(): UseMutationResult<
  { id: string; status: string; version: number },
  unknown,
  { id: string; toStatus: ProblemStatus; reason?: string }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { id: string; toStatus: ProblemStatus; reason?: string }) => {
      const result = await problemsApi.transitionProblemStatus(vars.id, vars.toStatus, vars.reason);
      return result;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

function useRecordRCA(): UseMutationResult<
  { id: string; rcaPerformed: boolean; rootCauseIdentified: boolean },
  unknown,
  { id: string; data: RCAData }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { id: string; data: RCAData }) => {
      const result = await problemsApi.recordRCA(vars.id, vars.data);
      return result;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

function useCloseProblem(): UseMutationResult<
  { id: string; status: string; resolutionType: string },
  unknown,
  { id: string; resolutionType: ResolutionType; closureNotes?: string }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: {
      id: string;
      resolutionType: ResolutionType;
      closureNotes?: string;
    }) => {
      const result = await problemsApi.closeProblem(
        vars.id,
        vars.resolutionType,
        vars.closureNotes,
      );
      return result;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

function useDeleteProblem(): UseMutationResult<void, unknown, string> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: problemsApi.deleteProblem,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

function useProblemActivities(
  problemId: string,
  limit = 50,
): UseQueryResult<{ problemId: string; activities: ProblemActivity[] }> {
  return useQuery({
    enabled: Boolean(problemId),
    queryFn: async () => {
      const result = await problemsApi.fetchProblemActivities(problemId, limit);
      return result;
    },
    queryKey: ['problemActivities', problemId, limit],
  });
}

function useProblemStats(projectId: string): UseQueryResult<{
  projectId: string;
  byStatus: Record<string, number>;
  byPriority: Record<string, number>;
  total: number;
}> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const result = await problemsApi.fetchProblemStats(projectId);
      return result;
    },
    queryKey: ['problemStats', projectId],
  });
}

export {
  useCloseProblem,
  useCreateProblem,
  useDeleteProblem,
  useProblem,
  useProblemActivities,
  useProblems,
  useProblemStats,
  useRecordRCA,
  useTransitionProblemStatus,
  useUpdateProblem,
  type CreateProblemData,
  type ProblemFilters,
  type RCAData,
};

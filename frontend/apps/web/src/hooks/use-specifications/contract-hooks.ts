import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type {
  ContractFilters,
  CreateContractData,
  UpdateContractData,
} from '@/hooks/useSpecifications.api';

import {
  createContract,
  deleteContract,
  fetchContract,
  fetchContractActivities,
  fetchContracts,
  fetchContractStats,
  updateContract,
  verifyContract,
} from '@/hooks/useSpecifications.api';

import type { MutationResult, QueryResult } from './query-utils';

import { invalidateQueries } from './query-utils';

type FetchContractsResult = Awaited<ReturnType<typeof fetchContracts>>;

type FetchContractResult = Awaited<ReturnType<typeof fetchContract>>;

type CreateContractResult = Awaited<ReturnType<typeof createContract>>;

type UpdateContractResult = Awaited<ReturnType<typeof updateContract>>;

type VerifyContractResult = Awaited<ReturnType<typeof verifyContract>>;

type FetchContractActivitiesResult = Awaited<ReturnType<typeof fetchContractActivities>>;

type FetchContractStatsResult = Awaited<ReturnType<typeof fetchContractStats>>;

const useContracts = (filters: ContractFilters): QueryResult<FetchContractsResult> =>
  useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: async () => {
      const response = await fetchContracts(filters);
      return response;
    },
    queryKey: ['contracts', JSON.stringify(filters)],
  });

const useContract = (id: string): QueryResult<FetchContractResult> =>
  useQuery({
    enabled: Boolean(id),
    queryFn: async () => {
      const response = await fetchContract(id);
      return response;
    },
    queryKey: ['contracts', id],
  });

const useCreateContract = (): MutationResult<CreateContractResult, CreateContractData> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateContractData) => {
      const response = await createContract(data);
      return response;
    },
    onSuccess: async (_, variables) => {
      await invalidateQueries(queryClient, [['contracts'], ['contractStats']]);
      await queryClient.invalidateQueries({
        queryKey: ['specificationSummary', variables.projectId],
      });
    },
  });
};

const useUpdateContract = (): MutationResult<
  UpdateContractResult,
  { id: string; data: UpdateContractData }
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: UpdateContractData }) => {
      const response = await updateContract(id, data);
      return response;
    },
    onSuccess: async (_, { id }) => {
      await invalidateQueries(queryClient, [['contracts', id], ['contracts']]);
    },
  });
};

const useDeleteContract = (): MutationResult<void, string> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await deleteContract(id);
    },
    onSuccess: async () => {
      await invalidateQueries(queryClient, [
        ['contracts'],
        ['contractStats'],
        ['specificationSummary'],
      ]);
    },
  });
};

const useVerifyContract = (): MutationResult<VerifyContractResult, string> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await verifyContract(id);
      return response;
    },
    onSuccess: async (_, id) => {
      await invalidateQueries(queryClient, [['contracts', id], ['contracts'], ['contractStats']]);
      await queryClient.invalidateQueries({ queryKey: ['specificationSummary'] });
    },
  });
};

const useContractActivities = (contractId: string): QueryResult<FetchContractActivitiesResult> =>
  useQuery({
    enabled: Boolean(contractId),
    queryFn: async () => {
      const response = await fetchContractActivities(contractId);
      return response;
    },
    queryKey: ['contractActivities', contractId],
  });

const useContractStats = (projectId: string): QueryResult<FetchContractStatsResult> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const response = await fetchContractStats(projectId);
      return response;
    },
    queryKey: ['contractStats', projectId],
  });

export {
  useContract,
  useContractActivities,
  useContracts,
  useContractStats,
  useCreateContract,
  useDeleteContract,
  useUpdateContract,
  useVerifyContract,
  type CreateContractResult,
  type FetchContractActivitiesResult,
  type FetchContractResult,
  type FetchContractsResult,
  type FetchContractStatsResult,
  type UpdateContractResult,
  type VerifyContractResult,
};

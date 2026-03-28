import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import * as specificationsApi from '@/hooks/useSpecifications.api';
import * as queryUtils from './query-utils';
import type { MutationResult } from './query-utils';

type FetchContractsResult = Awaited<ReturnType<typeof specificationsApi.fetchContracts>>;

type FetchContractResult = Awaited<ReturnType<typeof specificationsApi.fetchContract>>;

type CreateContractResult = Awaited<ReturnType<typeof specificationsApi.createContract>>;

type UpdateContractResult = Awaited<ReturnType<typeof specificationsApi.updateContract>>;

type VerifyContractResult = Awaited<ReturnType<typeof specificationsApi.verifyContract>>;

type FetchContractActivitiesResult = Awaited<
  ReturnType<typeof specificationsApi.fetchContractActivities>
>;

type FetchContractStatsResult = Awaited<ReturnType<typeof specificationsApi.fetchContractStats>>;

const useContracts = (
  filters: specificationsApi.ContractFilters,
): queryUtils.QueryResult<FetchContractsResult> =>
  useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: async () => {
      const response = await specificationsApi.fetchContracts(filters);
      return response;
    },
    queryKey: ['contracts', JSON.stringify(filters)],
  });

const useContract = (id: string): queryUtils.QueryResult<FetchContractResult> =>
  useQuery({
    enabled: Boolean(id),
    queryFn: async () => {
      const response = await specificationsApi.fetchContract(id);
      return response;
    },
    queryKey: ['contracts', id],
  });

const useCreateContract = (): queryUtils.MutationResult<
  CreateContractResult,
  specificationsApi.CreateContractData
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: specificationsApi.CreateContractData) => {
      const response = await specificationsApi.createContract(data);
      return response;
    },
    onSuccess: async (_, variables) => {
      await queryUtils.invalidateQueries(queryClient, [['contracts'], ['contractStats']]);
      await queryClient.invalidateQueries({
        queryKey: ['specificationSummary', variables.projectId],
      });
    },
  });
};

const useUpdateContract = (): MutationResult<
  UpdateContractResult,
  { id: string; data: specificationsApi.UpdateContractData }
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: specificationsApi.UpdateContractData }) => {
      const response = await specificationsApi.updateContract(id, data);
      return response;
    },
    onSuccess: async (_, { id }) => {
      await queryUtils.invalidateQueries(queryClient, [['contracts', id], ['contracts']]);
    },
  });
};

const useDeleteContract = (): queryUtils.MutationResult<void, string> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await specificationsApi.deleteContract(id);
    },
    onSuccess: async () => {
      await queryUtils.invalidateQueries(queryClient, [
        ['contracts'],
        ['contractStats'],
        ['specificationSummary'],
      ]);
    },
  });
};

const useVerifyContract = (): queryUtils.MutationResult<VerifyContractResult, string> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await specificationsApi.verifyContract(id);
      return response;
    },
    onSuccess: async (_, id) => {
      await queryUtils.invalidateQueries(queryClient, [['contracts', id], ['contracts'], ['contractStats']]);
      await queryClient.invalidateQueries({ queryKey: ['specificationSummary'] });
    },
  });
};

const useContractActivities = (
  contractId: string,
): queryUtils.QueryResult<FetchContractActivitiesResult> =>
  useQuery({
    enabled: Boolean(contractId),
    queryFn: async () => {
      const response = await specificationsApi.fetchContractActivities(contractId);
      return response;
    },
    queryKey: ['contractActivities', contractId],
  });

const useContractStats = (
  projectId: string,
): queryUtils.QueryResult<FetchContractStatsResult> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const response = await specificationsApi.fetchContractStats(projectId);
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

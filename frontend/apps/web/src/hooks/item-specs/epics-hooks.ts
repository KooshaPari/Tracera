import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { EpicSpecCreate, EpicSpecUpdate, EpicStatus } from './types';

import {
  createEpicSpec,
  deleteEpicSpec,
  fetchEpicSpec,
  fetchEpicSpecByItem,
  fetchEpicSpecs,
  updateEpicSpec,
} from './epics-api';
import { itemSpecKeys } from './keys';

function useEpicSpecs(
  projectId: string,
  options?: {
    status?: EpicStatus;
    limit?: number;
    offset?: number;
  },
) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const data = await fetchEpicSpecs(projectId, options);
      return data;
    },
    queryKey: [...itemSpecKeys.epics(projectId), options],
  });
}

function useEpicSpec(projectId: string, specId: string) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(specId),
    queryFn: async () => {
      const data = await fetchEpicSpec(projectId, specId);
      return data;
    },
    queryKey: itemSpecKeys.epic(projectId, specId),
  });
}

function useEpicSpecByItem(projectId: string, itemId: string) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(itemId),
    queryFn: async () => {
      const data = await fetchEpicSpecByItem(projectId, itemId);
      return data;
    },
    queryKey: itemSpecKeys.epicByItem(projectId, itemId),
  });
}

function useCreateEpicSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: EpicSpecCreate) => {
      const result = await createEpicSpec(projectId, data);
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.epic(projectId, data['id']), data);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.epics(projectId) }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.epicsByStatus(projectId, data.status),
        }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

function useUpdateEpicSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ specId, data }: { specId: string; data: EpicSpecUpdate }) => {
      const result = await updateEpicSpec(projectId, specId, data);
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.epic(projectId, data['id']), data);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.epics(projectId) }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.epicsByStatus(projectId, data.status),
        }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

function useDeleteEpicSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (specId: string) => {
      await deleteEpicSpec(projectId, specId);
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.epics(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

export {
  useEpicSpecs,
  useEpicSpec,
  useEpicSpecByItem,
  useCreateEpicSpec,
  useUpdateEpicSpec,
  useDeleteEpicSpec,
};

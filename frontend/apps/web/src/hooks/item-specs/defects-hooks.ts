import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { DefectSeverity, DefectSpecCreate, DefectSpecUpdate, DefectStatus } from './types';

import {
  createDefectSpec,
  deleteDefectSpec,
  fetchDefectSpec,
  fetchDefectSpecByItem,
  fetchDefectSpecs,
  updateDefectSpec,
} from './defects-api';
import { itemSpecKeys } from './keys';

function useDefectSpecs(
  projectId: string,
  options?: {
    severity?: DefectSeverity;
    status?: DefectStatus;
    limit?: number;
    offset?: number;
  },
) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const data = await fetchDefectSpecs(projectId, options);
      return data;
    },
    queryKey: [...itemSpecKeys.defects(projectId), options],
  });
}

function useDefectSpec(projectId: string, specId: string) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(specId),
    queryFn: async () => {
      const data = await fetchDefectSpec(projectId, specId);
      return data;
    },
    queryKey: itemSpecKeys.defect(projectId, specId),
  });
}

function useDefectSpecByItem(projectId: string, itemId: string) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(itemId),
    queryFn: async () => {
      const data = await fetchDefectSpecByItem(projectId, itemId);
      return data;
    },
    queryKey: itemSpecKeys.defectByItem(projectId, itemId),
  });
}

function useCreateDefectSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: DefectSpecCreate) => {
      const result = await createDefectSpec(projectId, data);
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.defect(projectId, data['id']), data);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.defects(projectId) }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.defectsBySeverity(projectId, data.severity),
        }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.defectsByStatus(projectId, data.status),
        }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

function useUpdateDefectSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ specId, data }: { specId: string; data: DefectSpecUpdate }) => {
      const result = await updateDefectSpec(projectId, specId, data);
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.defect(projectId, data['id']), data);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.defects(projectId) }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.defectsBySeverity(projectId, data.severity),
        }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.defectsByStatus(projectId, data.status),
        }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

function useDeleteDefectSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (specId: string) => {
      await deleteDefectSpec(projectId, specId);
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.defects(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

export {
  useDefectSpecs,
  useDefectSpec,
  useDefectSpecByItem,
  useCreateDefectSpec,
  useUpdateDefectSpec,
  useDeleteDefectSpec,
};

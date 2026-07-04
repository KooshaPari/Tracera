import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { TaskSpecCreate, TaskSpecUpdate, TaskStatus } from './types';

import { itemSpecKeys } from './keys';
import {
  createTaskSpec,
  deleteTaskSpec,
  fetchTaskSpec,
  fetchTaskSpecByItem,
  fetchTaskSpecs,
  updateTaskSpec,
} from './tasks-api';

function useTaskSpecs(
  projectId: string,
  options?: {
    status?: TaskStatus;
    storyId?: string;
    limit?: number;
    offset?: number;
  },
) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const data = await fetchTaskSpecs(projectId, options);
      return data;
    },
    queryKey: [...itemSpecKeys.tasks(projectId), options],
  });
}

function useTaskSpec(projectId: string, specId: string) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(specId),
    queryFn: async () => {
      const data = await fetchTaskSpec(projectId, specId);
      return data;
    },
    queryKey: itemSpecKeys.task(projectId, specId),
  });
}

function useTaskSpecByItem(projectId: string, itemId: string) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(itemId),
    queryFn: async () => {
      const data = await fetchTaskSpecByItem(projectId, itemId);
      return data;
    },
    queryKey: itemSpecKeys.taskByItem(projectId, itemId),
  });
}

function useCreateTaskSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: TaskSpecCreate) => {
      const result = await createTaskSpec(projectId, data);
      return result;
    },
    onSuccess: async (data, variables) => {
      queryClient.setQueryData(itemSpecKeys.task(projectId, data['id']), data);
      const invalidations = [
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.tasks(projectId) }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.tasksByStatus(projectId, data.status),
        }),
      ];
      if (typeof variables.parent_story === 'string') {
        invalidations.push(
          queryClient.invalidateQueries({
            queryKey: itemSpecKeys.tasksByStory(projectId, variables.parent_story),
          }),
        );
      }
      invalidations.push(
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      );
      await Promise.all(invalidations);
    },
  });
}

function useUpdateTaskSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ specId, data }: { specId: string; data: TaskSpecUpdate }) => {
      const result = await updateTaskSpec(projectId, specId, data);
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.task(projectId, data['id']), data);
      const invalidations = [
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.tasks(projectId) }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.tasksByStatus(projectId, data.status),
        }),
      ];
      if (typeof data.parent_story === 'string') {
        invalidations.push(
          queryClient.invalidateQueries({
            queryKey: itemSpecKeys.tasksByStory(projectId, data.parent_story),
          }),
        );
      }
      invalidations.push(
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      );
      await Promise.all(invalidations);
    },
  });
}

function useDeleteTaskSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (specId: string) => {
      await deleteTaskSpec(projectId, specId);
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.tasks(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

export {
  useTaskSpecs,
  useTaskSpec,
  useTaskSpecByItem,
  useCreateTaskSpec,
  useUpdateTaskSpec,
  useDeleteTaskSpec,
};

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { UserStorySpecCreate, UserStorySpecUpdate, UserStoryStatus } from './types';

import { itemSpecKeys } from './keys';
import {
  createUserStorySpec,
  deleteUserStorySpec,
  fetchUserStorySpec,
  fetchUserStorySpecByItem,
  fetchUserStorySpecs,
  updateUserStorySpec,
} from './user-stories-api';

function useUserStorySpecs(
  projectId: string,
  options?: {
    status?: UserStoryStatus;
    epicId?: string;
    limit?: number;
    offset?: number;
  },
) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const data = await fetchUserStorySpecs(projectId, options);
      return data;
    },
    queryKey: [...itemSpecKeys.userStories(projectId), options],
  });
}

function useUserStorySpec(projectId: string, specId: string) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(specId),
    queryFn: async () => {
      const data = await fetchUserStorySpec(projectId, specId);
      return data;
    },
    queryKey: itemSpecKeys.userStory(projectId, specId),
  });
}

function useUserStorySpecByItem(projectId: string, itemId: string) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(itemId),
    queryFn: async () => {
      const data = await fetchUserStorySpecByItem(projectId, itemId);
      return data;
    },
    queryKey: itemSpecKeys.userStoryByItem(projectId, itemId),
  });
}

function useCreateUserStorySpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: UserStorySpecCreate) => {
      const result = await createUserStorySpec(projectId, data);
      return result;
    },
    onSuccess: async (data, variables) => {
      queryClient.setQueryData(itemSpecKeys.userStory(projectId, data['id']), data);
      const invalidations = [
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.userStories(projectId) }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.userStoriesByStatus(projectId, data.status),
        }),
      ];
      if (typeof variables.parent_epic === 'string') {
        invalidations.push(
          queryClient.invalidateQueries({
            queryKey: itemSpecKeys.userStoriesByEpic(projectId, variables.parent_epic),
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

function useUpdateUserStorySpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ specId, data }: { specId: string; data: UserStorySpecUpdate }) => {
      const result = await updateUserStorySpec(projectId, specId, data);
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.userStory(projectId, data['id']), data);
      const invalidations = [
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.userStories(projectId) }),
        queryClient.invalidateQueries({
          queryKey: itemSpecKeys.userStoriesByStatus(projectId, data.status),
        }),
      ];
      if (typeof data.parent_epic === 'string') {
        invalidations.push(
          queryClient.invalidateQueries({
            queryKey: itemSpecKeys.userStoriesByEpic(projectId, data.parent_epic),
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

function useDeleteUserStorySpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (specId: string) => {
      await deleteUserStorySpec(projectId, specId);
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.userStories(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

export {
  useUserStorySpecs,
  useUserStorySpec,
  useUserStorySpecByItem,
  useCreateUserStorySpec,
  useUpdateUserStorySpec,
  useDeleteUserStorySpec,
};

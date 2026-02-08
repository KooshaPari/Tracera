import { useCallback } from 'react';
import { toast } from 'sonner';

import {
  useCreateDefectSpec,
  useCreateEpicSpec,
  useCreateRequirementSpec,
  useCreateTaskSpec,
  useCreateTestSpec,
  useCreateUserStorySpec,
} from '@/hooks/useItemSpecs';
import { logger } from '@/lib/logger';

import { EMPTY_STRING } from './types';

interface SpecActions {
  createSpec: (specType: string, itemId: string | undefined) => Promise<void>;
}

async function createRequirementSpecForItem(
  mutateAsync: ReturnType<typeof useCreateRequirementSpec>['mutateAsync'],
  itemId: string,
): Promise<void> {
  await mutateAsync({
    item_id: itemId,
    constraint_type: 'soft',
    requirement_type: 'ubiquitous',
    risk_level: 'minimal',
  });
}

async function createTestSpecForItem(
  mutateAsync: ReturnType<typeof useCreateTestSpec>['mutateAsync'],
  itemId: string,
): Promise<void> {
  await mutateAsync({
    item_id: itemId,
    test_type: 'unit',
  });
}

async function createEpicSpecForItem(
  mutateAsync: ReturnType<typeof useCreateEpicSpec>['mutateAsync'],
  itemId: string,
): Promise<void> {
  await mutateAsync({
    item_id: itemId,
    epic_name: 'New Epic',
    status: 'backlog',
    business_value: 0,
  });
}

async function createUserStorySpecForItem(
  mutateAsync: ReturnType<typeof useCreateUserStorySpec>['mutateAsync'],
  itemId: string,
): Promise<void> {
  await mutateAsync({
    item_id: itemId,
    as_a: 'User',
    i_want: 'To complete task',
    so_that: 'Work is done',
    status: 'backlog',
    priority: 3,
  });
}

async function createTaskSpecForItem(
  mutateAsync: ReturnType<typeof useCreateTaskSpec>['mutateAsync'],
  itemId: string,
): Promise<void> {
  await mutateAsync({
    item_id: itemId,
    task_title: 'New Task',
    status: 'todo',
    priority: 3,
  });
}

async function createDefectSpecForItem(
  mutateAsync: ReturnType<typeof useCreateDefectSpec>['mutateAsync'],
  itemId: string,
): Promise<void> {
  await mutateAsync({
    item_id: itemId,
    title: 'New Defect',
    description: 'New Defect Description',
    status: 'new',
    severity: 'minor',
    expected_behavior: 'Correct behavior',
    actual_behavior: 'Unknown',
  });
}

export function useSpecActions(projectId: string | undefined): SpecActions {
  const safeProjectId = projectId ?? EMPTY_STRING;

  const createRequirementSpec = useCreateRequirementSpec(safeProjectId);
  const createTestSpec = useCreateTestSpec(safeProjectId);
  const createEpicSpec = useCreateEpicSpec(safeProjectId);
  const createUserStorySpec = useCreateUserStorySpec(safeProjectId);
  const createTaskSpec = useCreateTaskSpec(safeProjectId);
  const createDefectSpec = useCreateDefectSpec(safeProjectId);

  const createSpec = useCallback(
    async (specType: string, itemId: string | undefined): Promise<void> => {
      if (itemId === undefined) {
        return;
      }
      try {
        if (specType === 'requirement') {
          await createRequirementSpecForItem(createRequirementSpec.mutateAsync, itemId);
          toast.success('Requirement spec created');
          return;
        }
        if (specType === 'test') {
          await createTestSpecForItem(createTestSpec.mutateAsync, itemId);
          toast.success('Test spec created');
          return;
        }
        if (specType === 'epic') {
          await createEpicSpecForItem(createEpicSpec.mutateAsync, itemId);
          toast.success('Epic spec created');
          return;
        }
        if (specType === 'user_story') {
          await createUserStorySpecForItem(createUserStorySpec.mutateAsync, itemId);
          toast.success('User story spec created');
          return;
        }
        if (specType === 'task') {
          await createTaskSpecForItem(createTaskSpec.mutateAsync, itemId);
          toast.success('Task spec created');
          return;
        }
        if (specType === 'defect') {
          await createDefectSpecForItem(createDefectSpec.mutateAsync, itemId);
          toast.success('Defect spec created');
          return;
        }
        toast.error('Unknown spec type');
      } catch (error: unknown) {
        toast.error(`Failed to create ${specType} spec`);
        logger.error('Failed to create item spec', error);
      }
    },
    [
      createDefectSpec,
      createEpicSpec,
      createRequirementSpec,
      createTaskSpec,
      createTestSpec,
      createUserStorySpec,
    ],
  );

  return { createSpec };
}

export type { SpecActions };

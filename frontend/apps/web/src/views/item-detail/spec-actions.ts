import { useCallback } from 'react';
import { toast } from 'sonner';

import type {
  DefectSpecCreate,
  EpicSpecCreate,
  RequirementSpecCreate,
  TaskSpecCreate,
  TestSpecCreate,
  UserStorySpecCreate,
} from '@/hooks/useItemSpecs';

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
  createSpec: (specType: string, itemId: string | undefined) => void;
}

function buildRequirementSpecPayload(itemId: string): RequirementSpecCreate {
  return {
    item_id: itemId,
    constraint_type: 'soft',
    requirement_type: 'ubiquitous',
    risk_level: 'minimal',
  };
}

function buildTestSpecPayload(itemId: string): TestSpecCreate {
  return {
    item_id: itemId,
    test_type: 'unit',
  };
}

function buildEpicSpecPayload(itemId: string): EpicSpecCreate {
  return {
    item_id: itemId,
    epic_name: 'New Epic',
    status: 'backlog',
    business_value: 0,
  };
}

function buildUserStorySpecPayload(itemId: string): UserStorySpecCreate {
  return {
    item_id: itemId,
    as_a: 'User',
    i_want: 'To complete task',
    so_that: 'Work is done',
    status: 'backlog',
    priority: 3,
  };
}

function buildTaskSpecPayload(itemId: string): TaskSpecCreate {
  return {
    item_id: itemId,
    task_title: 'New Task',
    status: 'todo',
    priority: 3,
  };
}

function buildDefectSpecPayload(itemId: string): DefectSpecCreate {
  return {
    item_id: itemId,
    title: 'New Defect',
    description: 'New Defect Description',
    status: 'new',
    severity: 'minor',
    expected_behavior: 'Correct behavior',
    actual_behavior: 'Unknown',
  };
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
    (specType: string, itemId: string | undefined): void => {
      if (itemId === undefined) {
        return;
      }
      const onError = (error: unknown): void => {
        toast.error(`Failed to create ${specType} spec`);
        logger.error('Failed to create item spec', error);
      };

      if (specType === 'requirement') {
        createRequirementSpec.mutate(buildRequirementSpecPayload(itemId), {
          onError,
          onSuccess: () => toast.success('Requirement spec created'),
        });
        return;
      }
      if (specType === 'test') {
        createTestSpec.mutate(buildTestSpecPayload(itemId), {
          onError,
          onSuccess: () => toast.success('Test spec created'),
        });
        return;
      }
      if (specType === 'epic') {
        createEpicSpec.mutate(buildEpicSpecPayload(itemId), {
          onError,
          onSuccess: () => toast.success('Epic spec created'),
        });
        return;
      }
      if (specType === 'user_story') {
        createUserStorySpec.mutate(buildUserStorySpecPayload(itemId), {
          onError,
          onSuccess: () => toast.success('User story spec created'),
        });
        return;
      }
      if (specType === 'task') {
        createTaskSpec.mutate(buildTaskSpecPayload(itemId), {
          onError,
          onSuccess: () => toast.success('Task spec created'),
        });
        return;
      }
      if (specType === 'defect') {
        createDefectSpec.mutate(buildDefectSpecPayload(itemId), {
          onError,
          onSuccess: () => toast.success('Defect spec created'),
        });
        return;
      }

      toast.error('Unknown spec type');
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

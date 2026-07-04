import type { ChangeEvent, MouseEvent } from 'react';

import { useCallback } from 'react';

import type {
  MappingCreateArgs,
  MappingFormState,
} from '@/pages/projects/views/integrations-view/tabs/mappings/useMappingFormState';

import { logger } from '@/lib/logger';

const REPO_FULL_NAME_ATTR = 'data-repo-full-name';
const REPO_URL_ATTR = 'data-repo-url';

const PROJECT_ID_ATTR = 'data-project-id';
const PROJECT_TITLE_ATTR = 'data-project-title';
const PROJECT_URL_ATTR = 'data-project-url';

const LINEAR_PROJECT_ID_ATTR = 'data-linear-project-id';
const LINEAR_PROJECT_NAME_ATTR = 'data-linear-project-name';
const LINEAR_PROJECT_URL_ATTR = 'data-linear-project-url';

type MappingSourceHandlersInput = Pick<
  MappingFormState,
  | 'handleCreateMapping'
  | 'projectOwner'
  | 'projectOwnerIsOrg'
  | 'setProjectOwner'
  | 'setProjectOwnerIsOrg'
  | 'setRepoSearch'
>;

interface MappingSourceHandlers {
  onRepoSearchChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onRepoLinkClick: (event: MouseEvent<HTMLButtonElement>) => void;
  onOwnerChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onOrgToggle: (event: ChangeEvent<HTMLInputElement>) => void;
  onProjectLinkClick: (event: MouseEvent<HTMLButtonElement>) => void;
  onLinearProjectLinkClick: (event: MouseEvent<HTMLButtonElement>) => void;
}

function readOptionalAttribute(element: HTMLElement, name: string): string | undefined {
  const value = element.getAttribute(name) ?? undefined;
  if (value === undefined || value === '') {
    return undefined;
  }
  return value;
}

function safeCreateMapping(
  handleCreateMapping: (args: MappingCreateArgs) => void,
  args: MappingCreateArgs,
): void {
  try {
    handleCreateMapping(args);
  } catch (error) {
    logger.error('Failed to create mapping:', error);
  }
}

function useRepoHandlers({
  handleCreateMapping,
  setRepoSearch,
}: Pick<MappingSourceHandlersInput, 'handleCreateMapping' | 'setRepoSearch'>): Pick<
  MappingSourceHandlers,
  'onRepoLinkClick' | 'onRepoSearchChange'
> {
  const onRepoSearchChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      setRepoSearch(event.target.value);
    },
    [setRepoSearch],
  );

  const onRepoLinkClick = useCallback(
    (event: MouseEvent<HTMLButtonElement>) => {
      const element = event.currentTarget;
      const fullName = element.getAttribute(REPO_FULL_NAME_ATTR) ?? '';
      if (fullName === '') {
        return;
      }

      const htmlUrl = readOptionalAttribute(element, REPO_URL_ATTR);
      safeCreateMapping(handleCreateMapping, {
        externalId: fullName,
        externalKey: fullName,
        externalType: 'github_repo',
        externalUrl: htmlUrl,
        mappingMetadata: {
          external_kind: 'repo',
          repo_full_name: fullName,
        },
      });
    },
    [handleCreateMapping],
  );

  return { onRepoLinkClick, onRepoSearchChange };
}

function useOwnerHandlers({
  setProjectOwner,
  setProjectOwnerIsOrg,
}: Pick<MappingSourceHandlersInput, 'setProjectOwner' | 'setProjectOwnerIsOrg'>): Pick<
  MappingSourceHandlers,
  'onOwnerChange' | 'onOrgToggle'
> {
  const onOwnerChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      setProjectOwner(event.target.value);
    },
    [setProjectOwner],
  );

  const onOrgToggle = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      setProjectOwnerIsOrg(event.target.checked);
    },
    [setProjectOwnerIsOrg],
  );

  return { onOrgToggle, onOwnerChange };
}

function useProjectLinkHandler({
  handleCreateMapping,
  projectOwner,
  projectOwnerIsOrg,
}: Pick<
  MappingSourceHandlersInput,
  'handleCreateMapping' | 'projectOwner' | 'projectOwnerIsOrg'
>): Pick<MappingSourceHandlers, 'onProjectLinkClick'> {
  const onProjectLinkClick = useCallback(
    (event: MouseEvent<HTMLButtonElement>) => {
      const element = event.currentTarget;
      const externalId = element.getAttribute(PROJECT_ID_ATTR) ?? '';
      if (externalId === '') {
        return;
      }

      const externalKey = readOptionalAttribute(element, PROJECT_TITLE_ATTR);
      const externalUrl = readOptionalAttribute(element, PROJECT_URL_ATTR);

      safeCreateMapping(handleCreateMapping, {
        externalId,
        externalKey,
        externalType: 'github_project',
        externalUrl,
        mappingMetadata: {
          external_kind: 'project',
          project_id: externalId,
          project_owner: projectOwner,
          project_owner_is_org: projectOwnerIsOrg,
        },
      });
    },
    [handleCreateMapping, projectOwner, projectOwnerIsOrg],
  );

  return { onProjectLinkClick };
}

function useLinearLinkHandler({
  handleCreateMapping,
}: Pick<MappingSourceHandlersInput, 'handleCreateMapping'>): Pick<
  MappingSourceHandlers,
  'onLinearProjectLinkClick'
> {
  const onLinearProjectLinkClick = useCallback(
    (event: MouseEvent<HTMLButtonElement>) => {
      const element = event.currentTarget;
      const externalId = element.getAttribute(LINEAR_PROJECT_ID_ATTR) ?? '';
      if (externalId === '') {
        return;
      }

      const externalKey = readOptionalAttribute(element, LINEAR_PROJECT_NAME_ATTR);
      const externalUrl = readOptionalAttribute(element, LINEAR_PROJECT_URL_ATTR);

      safeCreateMapping(handleCreateMapping, {
        externalId,
        externalKey,
        externalType: 'linear_project',
        externalUrl,
        mappingMetadata: {
          external_kind: 'project',
          project_id: externalId,
        },
      });
    },
    [handleCreateMapping],
  );

  return { onLinearProjectLinkClick };
}

function useMappingSourceHandlers(formState: MappingSourceHandlersInput): MappingSourceHandlers {
  const repoHandlers = useRepoHandlers(formState);
  const ownerHandlers = useOwnerHandlers(formState);
  const projectLinkHandlers = useProjectLinkHandler(formState);
  const linearLinkHandlers = useLinearLinkHandler(formState);

  return { ...repoHandlers, ...ownerHandlers, ...projectLinkHandlers, ...linearLinkHandlers };
}

export { useMappingSourceHandlers, type MappingSourceHandlers };

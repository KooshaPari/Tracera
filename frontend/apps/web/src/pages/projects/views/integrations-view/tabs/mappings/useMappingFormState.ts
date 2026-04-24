import { useCallback, useMemo, useState } from 'react';

import type {
  GitHubProject,
  GitHubRepo,
  IntegrationCredential,
  IntegrationProvider,
  LinearProject,
  MappingDirection,
} from '@tracertm/types';

import {
  useCreateMapping,
  useCredentials,
  useGitHubProjects,
  useGitHubRepos,
  useLinearProjects,
} from '@/hooks/useIntegrations';
import { logger } from '@/lib/logger';

interface MappingCreateArgs {
  externalId: string;
  externalKey?: string | undefined;
  externalType: string;
  externalUrl?: string | undefined;
  mappingMetadata?: Record<string, unknown> | undefined;
}

interface CreateMappingPayload {
  credentialId: string;
  localItemId: string;
  localItemType: string;
  projectId: string;
  externalId: string;
  externalType: string;
  direction?: MappingDirection | undefined;
  externalUrl?: string | undefined;
  externalKey?: string | undefined;
  fieldMappings?: Record<string, string> | undefined;
  mappingMetadata?: Record<string, unknown> | undefined;
  syncEnabled?: boolean | undefined;
}

interface MappingFormState {
  activeCredentialId: string;
  credentials: IntegrationCredential[];
  errorMessage: string | undefined;
  githubProjects: GitHubProject[];
  githubRepos: GitHubRepo[];
  handleCreateMapping: (args: MappingCreateArgs) => void;
  linearProjects: LinearProject[];
  projectOwner: string;
  projectOwnerIsOrg: boolean;
  provider: IntegrationProvider;
  repoSearch: string;
  setCredentialId: (value: string) => void;
  setProjectOwner: (value: string) => void;
  setProjectOwnerIsOrg: (value: boolean) => void;
  setProviderFromString: (value: string) => void;
  setRepoSearch: (value: string) => void;
}

const EMPTY_CREDENTIALS: IntegrationCredential[] = [];
const EMPTY_REPOS: GitHubRepo[] = [];
const EMPTY_GITHUB_PROJECTS: GitHubProject[] = [];
const EMPTY_LINEAR_PROJECTS: LinearProject[] = [];
const FIRST_PAGE = 1;

function parseIntegrationProvider(value: string): IntegrationProvider | undefined {
  if (value === 'github' || value === 'github_projects' || value === 'linear') {
    return value;
  }
  return undefined;
}

function filterProviderCredentials(
  credentials: IntegrationCredential[],
  provider: IntegrationProvider,
): IntegrationCredential[] {
  return credentials.filter((credential) => credential.provider === provider);
}

function selectActiveCredentialId(
  selectedCredentialId: string,
  providerCredentials: IntegrationCredential[],
): string {
  if (selectedCredentialId !== '') {
    return selectedCredentialId;
  }

  const [firstCredential] = providerCredentials;
  if (firstCredential === undefined) {
    return '';
  }
  return firstCredential.id;
}

function selectSearchParam(value: string): string | undefined {
  if (value === '') {
    return undefined;
  }
  return value;
}

function useProviderCredentials({
  projectId,
  provider,
  selectedCredentialId,
}: {
  projectId: string;
  provider: IntegrationProvider;
  selectedCredentialId: string;
}): {
  credentials: IntegrationCredential[];
  activeCredentialId: string;
} {
  const { data: credentialData } = useCredentials(projectId);
  const allCredentials = credentialData?.credentials ?? EMPTY_CREDENTIALS;

  const credentials = useMemo(
    () => filterProviderCredentials(allCredentials, provider),
    [allCredentials, provider],
  );

  const activeCredentialId = useMemo(
    () => selectActiveCredentialId(selectedCredentialId, credentials),
    [credentials, selectedCredentialId],
  );

  return { activeCredentialId, credentials };
}

function useMappingSources({
  provider,
  activeCredentialId,
  repoSearch,
  projectOwner,
  projectOwnerIsOrg,
}: {
  provider: IntegrationProvider;
  activeCredentialId: string;
  repoSearch: string;
  projectOwner: string;
  projectOwnerIsOrg: boolean;
}): {
  githubRepos: GitHubRepo[];
  githubProjects: GitHubProject[];
  linearProjects: LinearProject[];
} {
  const repoSearchParam = useMemo(() => selectSearchParam(repoSearch), [repoSearch]);

  let githubReposCredentialId = '';
  if (provider === 'github') {
    githubReposCredentialId = activeCredentialId;
  }

  let githubProjectsCredentialId = '';
  if (provider === 'github_projects') {
    githubProjectsCredentialId = activeCredentialId;
  }

  let linearCredentialId = '';
  if (provider === 'linear') {
    linearCredentialId = activeCredentialId;
  }

  const { data: githubReposData } = useGitHubRepos(
    githubReposCredentialId,
    repoSearchParam,
    FIRST_PAGE,
  );
  const { data: githubProjectsData } = useGitHubProjects(
    githubProjectsCredentialId,
    projectOwner,
    projectOwnerIsOrg,
  );
  const { data: linearProjectsData } = useLinearProjects(linearCredentialId);

  const githubRepos = githubReposData?.repos ?? EMPTY_REPOS;
  const githubProjects = githubProjectsData?.projects ?? EMPTY_GITHUB_PROJECTS;
  const linearProjects = linearProjectsData?.projects ?? EMPTY_LINEAR_PROJECTS;

  return { githubProjects, githubRepos, linearProjects };
}

function useCreateMappingHandler({
  activeCredentialId,
  projectId,
  setErrorMessage,
}: {
  activeCredentialId: string;
  projectId: string;
  setErrorMessage: (value: string | undefined) => void;
}): (args: MappingCreateArgs) => void {
  const createMapping = useCreateMapping();

  return useCallback(
    ({
      externalId,
      externalKey,
      externalType,
      externalUrl,
      mappingMetadata,
    }: MappingCreateArgs) => {
      if (activeCredentialId === '') {
        const message = 'Select a credential before creating a mapping.';
        setErrorMessage(message);
        logger.warn(message);
        return;
      }

      setErrorMessage(undefined);

      const payload: CreateMappingPayload = {
        credentialId: activeCredentialId,
        direction: 'bidirectional',
        externalId,
        externalKey,
        externalType,
        localItemId: projectId,
        localItemType: 'project',
        projectId,
        syncEnabled: true,
      };

      if (externalUrl !== undefined) {
        payload.externalUrl = externalUrl;
      }
      if (mappingMetadata !== undefined) {
        payload.mappingMetadata = mappingMetadata;
      }

      createMapping.mutate(payload, {
        onError: (error: unknown) => {
          logger.error('Failed to create mapping:', error);
          setErrorMessage('Failed to create mapping. Please try again.');
        },
      });
    },
    [activeCredentialId, createMapping, projectId, setErrorMessage],
  );
}

function useProviderSetter(
  setProvider: (value: IntegrationProvider) => void,
): (value: string) => void {
  return useCallback(
    (value: string) => {
      const parsedProvider = parseIntegrationProvider(value);
      if (parsedProvider !== undefined) {
        setProvider(parsedProvider);
      }
    },
    [setProvider],
  );
}

function useStableSources({
  provider,
  activeCredentialId,
  repoSearch,
  projectOwner,
  projectOwnerIsOrg,
}: {
  provider: IntegrationProvider;
  activeCredentialId: string;
  repoSearch: string;
  projectOwner: string;
  projectOwnerIsOrg: boolean;
}): {
  githubRepos: GitHubRepo[];
  githubProjects: GitHubProject[];
  linearProjects: LinearProject[];
} {
  return useMappingSources({
    provider,
    activeCredentialId,
    repoSearch,
    projectOwner,
    projectOwnerIsOrg,
  });
}

function useMappingFormState(projectId: string): MappingFormState {
  const [provider, setProvider] = useState<IntegrationProvider>('github');
  const [selectedCredentialId, setCredentialId] = useState('');
  const [repoSearch, setRepoSearch] = useState('');
  const [projectOwner, setProjectOwner] = useState('');
  const [projectOwnerIsOrg, setProjectOwnerIsOrg] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | undefined>();

  const { activeCredentialId, credentials } = useProviderCredentials({
    projectId,
    provider,
    selectedCredentialId,
  });

  const { githubProjects, githubRepos, linearProjects } = useStableSources({
    provider,
    activeCredentialId,
    repoSearch,
    projectOwner,
    projectOwnerIsOrg,
  });

  const handleCreateMapping = useCreateMappingHandler({
    activeCredentialId,
    projectId,
    setErrorMessage,
  });

  const setProviderFromString = useProviderSetter(setProvider);

  return {
    activeCredentialId,
    credentials,
    errorMessage,
    githubProjects,
    githubRepos,
    handleCreateMapping,
    linearProjects,
    projectOwner,
    projectOwnerIsOrg,
    provider,
    repoSearch,
    setCredentialId,
    setProjectOwner,
    setProjectOwnerIsOrg,
    setProviderFromString,
    setRepoSearch,
  };
}

export { useMappingFormState, type MappingCreateArgs, type MappingFormState };

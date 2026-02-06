import { useCallback, useMemo, useState, type ChangeEvent, type ReactElement } from 'react';

import type {
  IntegrationCredential,
  IntegrationMapping,
  IntegrationProvider,
  SyncConflict,
} from '@tracertm/types';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';
import { logger } from '@/lib/logger';

import {
  useConflicts,
  useCreateMapping,
  useCredentials,
  useDeleteCredential,
  useGitHubProjects,
  useGitHubRepos,
  useIntegrationStats,
  useLinearProjects,
  useMappings,
  useResolveConflict,
  useStartOAuth,
  useSyncStatus,
  useTriggerSync,
  useValidateCredential,
} from '../../../hooks/useIntegrations';

type TabId = 'overview' | 'credentials' | 'mappings' | 'sync' | 'conflicts';

interface TabConfig {
  id: TabId;
  label: string;
}

interface TabContentProps {
  activeTab: TabId;
  conflicts: SyncConflict[];
  conflictsLoading: boolean;
  credentials: IntegrationCredential[];
  credentialsLoading: boolean;
  mappings: IntegrationMapping[];
  mappingsLoading: boolean;
  mode: 'project' | 'account';
  projectId: string;
  syncLoading: boolean;
  syncStatus: unknown;
  stats: unknown;
  statsLoading: boolean;
}

interface OverviewTabProps {
  stats: any;
  isLoading: boolean;
  projectId: string;
  mode: 'project' | 'account';
}

interface ProviderConnectSectionProps {
  mode: 'project' | 'account';
  providers: Array<{ provider: IntegrationProvider }>;
  onConnect: (provider: IntegrationProvider) => void;
}

interface CredentialsTabProps {
  credentials: IntegrationCredential[];
  isLoading: boolean;
}

interface CredentialRowProps {
  credential: IntegrationCredential;
  isConfirmingDelete: boolean;
  isValidating: boolean;
  onCancelDelete: () => void;
  onConfirmDelete: (id: string) => void;
  onRequestDelete: (id: string) => void;
  onValidate: (id: string) => void;
}

interface MappingCreateArgs {
  externalId: string;
  externalKey?: string;
  externalType: string;
  externalUrl?: string;
  mappingMetadata?: Record<string, unknown>;
}

interface MappingFormProps {
  formState: ReturnType<typeof useMappingFormState>;
}

interface MappingControlsProps {
  formState: ReturnType<typeof useMappingFormState>;
}

interface MappingSourcesProps {
  formState: ReturnType<typeof useMappingFormState>;
}

interface GitHubRepoListProps {
  onCreateMapping: (args: MappingCreateArgs) => Promise<void>;
  onRepoSearchChange: (value: string) => void;
  repoSearch: string;
  repos: Array<{
    id: string;
    fullName: string;
    description?: string;
    htmlUrl?: string;
  }>;
}

interface RepoRowProps {
  onCreateMapping: (args: MappingCreateArgs) => Promise<void>;
  repo: {
    id: string;
    fullName: string;
    description?: string;
    htmlUrl?: string;
  };
}

interface GitHubProjectListProps {
  onCreateMapping: (args: MappingCreateArgs) => Promise<void>;
  onProjectOwnerChange: (value: string) => void;
  onProjectOwnerOrgChange: (value: boolean) => void;
  projectOwner: string;
  projectOwnerIsOrg: boolean;
  projects: Array<{
    id: string;
    title: string;
    description?: string;
    url?: string;
  }>;
}

interface GitHubProjectRowProps {
  onCreateMapping: (args: MappingCreateArgs) => Promise<void>;
  project: {
    id: string;
    title: string;
    description?: string;
    url?: string;
  };
  projectOwner: string;
  projectOwnerIsOrg: boolean;
}

const ACCOUNT_TABS: TabConfig[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'credentials', label: 'Credentials' },
];

const PROJECT_TABS: TabConfig[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'mappings', label: 'Mappings' },
  { id: 'sync', label: 'Sync Status' },
  { id: 'conflicts', label: 'Conflicts' },
];

const EMPTY_CREDENTIALS: IntegrationCredential[] = [];
const EMPTY_MAPPINGS: IntegrationMapping[] = [];
const EMPTY_CONFLICTS: SyncConflict[] = [];
const ID_PREVIEW_LENGTH = 8;
const PROVIDER_SELECT_ID = 'integration-provider';
const CREDENTIAL_SELECT_ID = 'integration-credential';

interface IntegrationsViewProps {
  projectId: string;
  mode?: 'project' | 'account';
  initialTab?: TabId;
  allowedTabs?: TabId[];
}

const useIntegrationsViewData = (projectId: string) => {
  const stats = useIntegrationStats(projectId);
  const credentials = useCredentials(projectId);
  const mappings = useMappings(projectId);
  const syncStatus = useSyncStatus(projectId);
  const conflicts = useConflicts(projectId, 'pending');

  return { conflicts, credentials, mappings, stats, syncStatus };
};

const useIntegrationsTabs = (mode: 'project' | 'account', allowedTabs?: TabId[]): TabConfig[] =>
  useMemo(() => {
    const defaultTabs = mode === 'account' ? ACCOUNT_TABS : PROJECT_TABS;
    if (!allowedTabs) {
      return defaultTabs;
    }
    return defaultTabs.filter((tab) => allowedTabs.includes(tab.id));
  }, [allowedTabs, mode]);

const IntegrationsView = ({
  projectId,
  mode = 'project',
  initialTab = 'overview',
  allowedTabs,
}: IntegrationsViewProps): ReactElement => {
  const [activeTab, setActiveTab] = useState<TabId>(initialTab);

  const { conflicts, credentials, mappings, stats, syncStatus } =
    useIntegrationsViewData(projectId);

  const credentialsList = credentials.data?.credentials ?? EMPTY_CREDENTIALS;
  const mappingsList = mappings.data?.mappings ?? EMPTY_MAPPINGS;
  const conflictsList = conflicts.data?.conflicts ?? EMPTY_CONFLICTS;
  const conflictTotal = conflicts.data?.total ?? 0;
  const tabs = useIntegrationsTabs(mode, allowedTabs);

  const handleTabSelect = useCallback((tabId: TabId): void => {
    setActiveTab(tabId);
  }, []);

  return (
    <div className='p-6'>
      <PageHeader />
      <TabsNav
        activeTab={activeTab}
        conflictCount={conflictTotal}
        onSelect={handleTabSelect}
        tabs={tabs}
      />
      <TabContent
        activeTab={activeTab}
        conflicts={conflictsList}
        conflictsLoading={conflicts.isLoading}
        credentials={credentialsList}
        credentialsLoading={credentials.isLoading}
        mappings={mappingsList}
        mappingsLoading={mappings.isLoading}
        mode={mode}
        projectId={projectId}
        syncLoading={syncStatus.isLoading}
        syncStatus={syncStatus.data}
        stats={stats.data}
        statsLoading={stats.isLoading}
      />
    </div>
  );
};

const PageHeader = (): ReactElement => (
  <div className='mb-6'>
    <h1 className='text-2xl font-bold text-gray-900 dark:text-white'>External Integrations</h1>
    <p className='text-gray-600 dark:text-gray-400'>
      Connect GitHub, GitHub Projects, and Linear to sync items bidirectionally.
    </p>
  </div>
);

const TabsNav = ({
  activeTab,
  conflictCount,
  onSelect,
  tabs,
}: {
  activeTab: TabId;
  conflictCount: number;
  onSelect: (tabId: TabId) => void;
  tabs: TabConfig[];
}): ReactElement => (
  <div className='mb-6 border-b border-gray-200 dark:border-gray-700'>
    <nav className='flex space-x-8'>
      {tabs.map((tab) => (
        <TabButton
          key={tab.id}
          active={activeTab === tab.id}
          conflictCount={conflictCount}
          onSelect={onSelect}
          tab={tab}
        />
      ))}
    </nav>
  </div>
);

const TabButton = ({
  active,
  conflictCount,
  onSelect,
  tab,
}: {
  active: boolean;
  conflictCount: number;
  onSelect: (tabId: TabId) => void;
  tab: TabConfig;
}): ReactElement => {
  const handleClick = useCallback(() => {
    onSelect(tab.id);
  }, [onSelect, tab.id]);

  return (
    <button
      type='button'
      onClick={handleClick}
      className={`border-b-2 px-1 py-2 text-sm font-medium ${
        active
          ? 'border-blue-500 text-blue-600 dark:text-blue-400'
          : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
      }`}
    >
      {tab.label}
      {tab.id === 'conflicts' && conflictCount > 0 && (
        <span className='ml-2 rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-300'>
          {conflictCount}
        </span>
      )}
    </button>
  );
};

const TabContent = ({
  activeTab,
  conflicts,
  conflictsLoading,
  credentials,
  credentialsLoading,
  mappings,
  mappingsLoading,
  mode,
  projectId,
  syncLoading,
  syncStatus,
  stats,
  statsLoading,
}: TabContentProps): ReactElement => (
  <>
    {activeTab === 'overview' && (
      <OverviewTab stats={stats} isLoading={statsLoading} projectId={projectId} mode={mode} />
    )}
    {activeTab === 'credentials' && mode !== 'project' && (
      <CredentialsTab credentials={credentials} isLoading={credentialsLoading} />
    )}
    {activeTab === 'mappings' && mode !== 'account' && (
      <MappingsTab mappings={mappings} isLoading={mappingsLoading} projectId={projectId} />
    )}
    {activeTab === 'sync' && mode !== 'account' && (
      <SyncTab syncStatus={syncStatus} isLoading={syncLoading} />
    )}
    {activeTab === 'conflicts' && mode !== 'account' && (
      <ConflictsTab conflicts={conflicts} isLoading={conflictsLoading} />
    )}
  </>
);

const OverviewTab = ({ stats, isLoading, projectId, mode }: OverviewTabProps): ReactElement => {
  const startOAuth = useStartOAuth();
  const providers = stats?.providers ?? [];

  const handleConnect = useCallback(
    async (provider: IntegrationProvider): Promise<void> => {
      const redirectUri = `${globalThis.location.origin}/integrations/callback`;
      try {
        const result = await startOAuth.mutateAsync({
          credentialScope: mode === 'account' ? 'user' : 'project',
          projectId,
          provider,
          redirectUri,
        });
        globalThis.location.href = result.auth_url;
      } catch (error) {
        logger.error('Failed to start OAuth:', error);
      }
    },
    [mode, projectId, startOAuth],
  );

  if (isLoading) {
    return (
      <div className='flex justify-center py-8'>
        <LoadingSpinner text='Loading stats...' />
      </div>
    );
  }

  return (
    <div className='space-y-6'>
      <StatsCards stats={stats} />
      <ProviderConnectSection mode={mode} providers={providers} onConnect={handleConnect} />
      <ProviderStatusList providers={providers} />
    </div>
  );
};

const StatsCards = ({ stats }: { stats: any }): ReactElement => (
  <div className='grid grid-cols-1 gap-4 md:grid-cols-4'>
    <StatCard
      title='Connected Providers'
      value={stats?.providers?.length ?? 0}
      subtitle='integrations active'
    />
    <StatCard
      title='Active Mappings'
      value={stats?.mappings?.active ?? 0}
      subtitle={`of ${stats?.mappings?.total ?? 0} total`}
    />
    <StatCard
      title='Sync Success Rate'
      value={`${stats?.sync?.successRate ?? 0}%`}
      subtitle={`${stats?.sync?.recentSyncs ?? 0} recent syncs`}
    />
    <StatCard
      title='Pending Conflicts'
      value={stats?.conflicts?.pending ?? 0}
      subtitle='need resolution'
      warning={(stats?.conflicts?.pending ?? 0) > 0}
    />
  </div>
);

const ProviderConnectSection = ({
  mode,
  providers,
  onConnect,
}: ProviderConnectSectionProps): ReactElement => {
  const connectedSet = useMemo(
    () => new Set(providers.map((provider) => provider.provider)),
    [providers],
  );

  if (mode !== 'account') {
    return <AccountConnectionsNotice />;
  }

  return <ProviderConnectGrid connectedSet={connectedSet} onConnect={onConnect} />;
};

const AccountConnectionsNotice = (): ReactElement => (
  <div className='rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800'>
    <h2 className='mb-2 text-lg font-semibold'>Account connections moved</h2>
    <p className='text-sm text-gray-500'>
      Link external accounts in Settings. Project mappings and sync controls live here.
    </p>
  </div>
);

const ProviderConnectGrid = ({
  connectedSet,
  onConnect,
}: {
  connectedSet: Set<IntegrationProvider>;
  onConnect: (provider: IntegrationProvider) => void;
}): ReactElement => (
  <div className='rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800'>
    <h2 className='mb-4 text-lg font-semibold'>Connect New Provider</h2>
    <div className='grid grid-cols-1 gap-4 md:grid-cols-3'>
      <ProviderCard
        connected={connectedSet.has('github')}
        description='Sync issues, PRs, and repositories'
        name='GitHub'
        onConnect={onConnect}
        providerId='github'
      />
      <ProviderCard
        connected={connectedSet.has('github_projects')}
        description='Sync project boards and cards'
        name='GitHub Projects'
        onConnect={onConnect}
        providerId='github_projects'
      />
      <ProviderCard
        connected={connectedSet.has('linear')}
        description='Sync issues, projects, and teams'
        name='Linear'
        onConnect={onConnect}
        providerId='linear'
      />
    </div>
  </div>
);

const ProviderStatusList = ({
  providers,
}: {
  providers: {
    provider: IntegrationProvider;
    credentialType?: string;
    status: string;
  }[];
}): ReactElement | null => {
  if (providers.length === 0) {
    return null;
  }

  return (
    <div className='rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800'>
      <h2 className='mb-4 text-lg font-semibold'>Connected Providers</h2>
      <div className='space-y-3'>
        {providers.map((provider) => (
          <div
            key={`${provider.provider}-${provider.credentialType ?? 'default'}`}
            className='flex items-center justify-between rounded-lg bg-gray-50 p-3 dark:bg-gray-700'
          >
            <div className='flex items-center space-x-3'>
              <ProviderIcon provider={provider.provider} />
              <div>
                <div className='font-medium capitalize'>{provider.provider.replace('_', ' ')}</div>
                <div className='text-sm text-gray-500'>{provider.credentialType}</div>
              </div>
            </div>
            <StatusBadge status={provider.status} />
          </div>
        ))}
      </div>
    </div>
  );
};

const useCredentialActions = () => {
  const deleteCredential = useDeleteCredential();
  const validateCredential = useValidateCredential();
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const handleRequestDelete = useCallback((id: string) => {
    setConfirmDeleteId(id);
  }, []);

  const handleCancelDelete = useCallback(() => {
    setConfirmDeleteId(null);
  }, []);

  const handleConfirmDelete = useCallback(
    (id: string) => {
      deleteCredential.mutate(id);
      setConfirmDeleteId(null);
    },
    [deleteCredential],
  );

  const handleValidate = useCallback(
    (id: string) => {
      validateCredential.mutate(id);
    },
    [validateCredential],
  );

  return {
    confirmDeleteId,
    handleCancelDelete,
    handleConfirmDelete,
    handleRequestDelete,
    handleValidate,
    isValidating: validateCredential.isPending,
  };
};

const CredentialsEmptyState = (): ReactElement => (
  <div className='py-12 text-center text-gray-500'>
    No credentials configured. Connect a provider from the Overview tab.
  </div>
);

const CredentialsTab = ({ credentials, isLoading }: CredentialsTabProps): ReactElement => {
  const {
    confirmDeleteId,
    handleCancelDelete,
    handleConfirmDelete,
    handleRequestDelete,
    handleValidate,
    isValidating,
  } = useCredentialActions();

  if (isLoading) {
    return (
      <div className='flex justify-center py-8'>
        <LoadingSpinner text='Loading credentials...' />
      </div>
    );
  }

  if (credentials.length === 0) {
    return <CredentialsEmptyState />;
  }

  return (
    <div className='space-y-4'>
      {credentials.map((cred) => (
        <CredentialRow
          key={cred.id}
          credential={cred}
          isConfirmingDelete={confirmDeleteId === cred.id}
          isValidating={isValidating}
          onCancelDelete={handleCancelDelete}
          onConfirmDelete={handleConfirmDelete}
          onRequestDelete={handleRequestDelete}
          onValidate={handleValidate}
        />
      ))}
    </div>
  );
};

const CredentialRow = ({
  credential,
  isConfirmingDelete,
  isValidating,
  onCancelDelete,
  onConfirmDelete,
  onRequestDelete,
  onValidate,
}: CredentialRowProps): ReactElement => {
  const handleValidateClick = useCallback(() => {
    onValidate(credential.id);
  }, [credential.id, onValidate]);

  const handleDeleteClick = useCallback(() => {
    onRequestDelete(credential.id);
  }, [credential.id, onRequestDelete]);

  const handleConfirmDelete = useCallback(() => {
    onConfirmDelete(credential.id);
  }, [credential.id, onConfirmDelete]);

  return (
    <div className='rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800'>
      <div className='flex items-center justify-between'>
        <CredentialInfo credential={credential} />
        <CredentialActions
          isConfirmingDelete={isConfirmingDelete}
          isValidating={isValidating}
          onCancelDelete={onCancelDelete}
          onConfirmDelete={handleConfirmDelete}
          onDelete={handleDeleteClick}
          onValidate={handleValidateClick}
          status={credential.status}
        />
      </div>
    </div>
  );
};

const CredentialInfo = ({ credential }: { credential: IntegrationCredential }): ReactElement => (
  <div className='flex items-center space-x-4'>
    <ProviderIcon provider={credential.provider} />
    <div>
      <div className='font-medium capitalize'>{credential.provider.replace('_', ' ')}</div>
      <div className='text-sm text-gray-500'>
        Type: {credential.credentialType} | Scopes: {credential.scopes?.join(', ') || 'none'}
      </div>
      {credential.lastValidatedAt && (
        <div className='text-xs text-gray-400'>
          Last validated: {new Date(credential.lastValidatedAt).toLocaleString()}
        </div>
      )}
    </div>
  </div>
);

const CredentialActions = ({
  isConfirmingDelete,
  isValidating,
  onCancelDelete,
  onConfirmDelete,
  onDelete,
  onValidate,
  status,
}: {
  isConfirmingDelete: boolean;
  isValidating: boolean;
  onCancelDelete: () => void;
  onConfirmDelete: () => void;
  onDelete: () => void;
  onValidate: () => void;
  status: string;
}): ReactElement => (
  <div className='flex items-center space-x-2'>
    <StatusBadge status={status} />
    <button
      type='button'
      onClick={onValidate}
      disabled={isValidating}
      className='rounded bg-blue-100 px-3 py-1 text-sm text-blue-700 hover:bg-blue-200'
    >
      Validate
    </button>
    <CredentialDeleteActions
      isConfirmingDelete={isConfirmingDelete}
      onCancelDelete={onCancelDelete}
      onConfirmDelete={onConfirmDelete}
      onDelete={onDelete}
    />
  </div>
);

const CredentialDeleteActions = ({
  isConfirmingDelete,
  onCancelDelete,
  onConfirmDelete,
  onDelete,
}: {
  isConfirmingDelete: boolean;
  onCancelDelete: () => void;
  onConfirmDelete: () => void;
  onDelete: () => void;
}): ReactElement =>
  isConfirmingDelete ? (
    <div className='flex items-center space-x-2'>
      <button
        type='button'
        onClick={onConfirmDelete}
        className='rounded bg-red-100 px-3 py-1 text-sm text-red-700 hover:bg-red-200'
      >
        Confirm
      </button>
      <button
        type='button'
        onClick={onCancelDelete}
        className='rounded bg-gray-100 px-3 py-1 text-sm text-gray-700 hover:bg-gray-200'
      >
        Cancel
      </button>
    </div>
  ) : (
    <button
      type='button'
      onClick={onDelete}
      className='rounded bg-red-100 px-3 py-1 text-sm text-red-700 hover:bg-red-200'
    >
      Delete
    </button>
  );

const MappingsTab = ({
  mappings,
  isLoading,
  projectId,
}: {
  mappings: IntegrationMapping[];
  isLoading: boolean;
  projectId: string;
}): ReactElement => {
  const formState = useMappingFormState(projectId);

  if (isLoading) {
    return (
      <div className='flex justify-center py-8'>
        <LoadingSpinner text='Loading mappings...' />
      </div>
    );
  }

  return (
    <div className='space-y-6'>
      <MappingForm formState={formState} />
      <MappingList mappings={mappings} />
    </div>
  );
};

const useProviderCredentials = (
  projectId: string,
  provider: IntegrationProvider,
  credentialId: string,
) => {
  const { data: credentialData } = useCredentials(projectId);
  const credentials = credentialData?.credentials ?? EMPTY_CREDENTIALS;
  const providerCredentials = useMemo(
    () => credentials.filter((cred) => cred.provider === provider),
    [credentials, provider],
  );
  const activeCredentialId = credentialId || providerCredentials[0]?.id || '';

  return { activeCredentialId, providerCredentials };
};

const useMappingSourcesData = ({
  activeCredentialId,
  projectOwner,
  projectOwnerIsOrg,
  provider,
  repoSearch,
}: {
  activeCredentialId: string;
  projectOwner: string;
  projectOwnerIsOrg: boolean;
  provider: IntegrationProvider;
  repoSearch: string;
}) => {
  const { data: githubRepos } = useGitHubRepos(
    provider === 'github' ? activeCredentialId : '',
    repoSearch || undefined,
    1,
  );
  const { data: githubProjects } = useGitHubProjects(
    provider === 'github_projects' ? activeCredentialId : '',
    projectOwner,
    projectOwnerIsOrg,
  );
  const { data: linearProjects } = useLinearProjects(
    provider === 'linear' ? activeCredentialId : '',
  );

  return { githubProjects, githubRepos, linearProjects };
};

const useMappingCreator = ({
  activeCredentialId,
  projectId,
  setErrorMessage,
}: {
  activeCredentialId: string;
  projectId: string;
  setErrorMessage: (value: string | null) => void;
}) => {
  const createMapping = useCreateMapping();

  return useCallback(
    async ({
      externalId,
      externalKey,
      externalType,
      externalUrl,
      mappingMetadata,
    }: MappingCreateArgs) => {
      if (!activeCredentialId) {
        const message = 'Select a credential before creating a mapping.';
        setErrorMessage(message);
        logger.warn(message);
        return;
      }
      setErrorMessage(null);
      const payload: Record<string, unknown> = {
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
      if (externalUrl) {
        payload.externalUrl = externalUrl;
      }
      if (mappingMetadata) {
        payload.mappingMetadata = mappingMetadata;
      }
      await createMapping.mutateAsync(payload as any);
    },
    [activeCredentialId, createMapping, projectId, setErrorMessage],
  );
};

const useMappingFormState = (projectId: string) => {
  const triggerSync = useTriggerSync();
  const [provider, setProvider] = useState<IntegrationProvider>('github');
  const [credentialId, setCredentialId] = useState('');
  const [repoSearch, setRepoSearch] = useState('');
  const [projectOwner, setProjectOwner] = useState('');
  const [projectOwnerIsOrg, setProjectOwnerIsOrg] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { activeCredentialId, providerCredentials } = useProviderCredentials(
    projectId,
    provider,
    credentialId,
  );
  const { githubProjects, githubRepos, linearProjects } = useMappingSourcesData({
    activeCredentialId,
    projectOwner,
    projectOwnerIsOrg,
    provider,
    repoSearch,
  });
  const handleCreateMapping = useMappingCreator({
    activeCredentialId,
    projectId,
    setErrorMessage,
  });

  return {
    activeCredentialId,
    credentials: providerCredentials,
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
    setProvider,
    setRepoSearch,
    triggerSync,
  };
};

const MappingForm = ({ formState }: MappingFormProps): ReactElement => (
  <div className='space-y-4 rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800'>
    <MappingHeader />
    <MappingControls formState={formState} />
    <MappingError message={formState.errorMessage} />
    <MappingSources formState={formState} />
  </div>
);

const MappingError = ({ message }: { message: string | null }): ReactElement | null =>
  message ? <div className='text-sm text-red-600'>{message}</div> : null;

const MappingHeader = (): ReactElement => (
  <div>
    <h2 className='text-lg font-semibold'>Link external repo/project</h2>
    <p className='text-sm text-gray-500'>
      Attach this project to an external repository or planning system to enable sync.
    </p>
  </div>
);

const MappingControls = ({ formState }: MappingControlsProps): ReactElement => {
  const { activeCredentialId, credentials, provider, setCredentialId, setProvider } = formState;

  const handleProviderChange = useCallback(
    (event: ChangeEvent<HTMLSelectElement>) => {
      setProvider(event.target.value as IntegrationProvider);
    },
    [setProvider],
  );

  const handleCredentialChange = useCallback(
    (event: ChangeEvent<HTMLSelectElement>) => {
      setCredentialId(event.target.value);
    },
    [setCredentialId],
  );

  return (
    <div className='grid grid-cols-1 gap-4 md:grid-cols-3'>
      <ProviderSelect provider={provider} onProviderChange={handleProviderChange} />
      <CredentialSelect
        activeCredentialId={activeCredentialId}
        credentials={credentials}
        provider={provider}
        onCredentialChange={handleCredentialChange}
      />
    </div>
  );
};

const ProviderSelect = ({
  provider,
  onProviderChange,
}: {
  provider: IntegrationProvider;
  onProviderChange: (event: ChangeEvent<HTMLSelectElement>) => void;
}): ReactElement => (
  <div className='space-y-2'>
    <label htmlFor={PROVIDER_SELECT_ID} className='text-xs font-semibold text-gray-500'>
      Provider
    </label>
    <select
      id={PROVIDER_SELECT_ID}
      className='w-full rounded-md border bg-white px-3 py-2 text-sm dark:bg-gray-900'
      value={provider}
      onChange={onProviderChange}
    >
      <option value='github'>GitHub</option>
      <option value='github_projects'>GitHub Projects</option>
      <option value='linear'>Linear</option>
    </select>
  </div>
);

const CredentialSelect = ({
  activeCredentialId,
  credentials,
  provider,
  onCredentialChange,
}: {
  activeCredentialId: string;
  credentials: IntegrationCredential[];
  provider: IntegrationProvider;
  onCredentialChange: (event: ChangeEvent<HTMLSelectElement>) => void;
}): ReactElement => (
  <div className='space-y-2 md:col-span-2'>
    <label htmlFor={CREDENTIAL_SELECT_ID} className='text-xs font-semibold text-gray-500'>
      Credential
    </label>
    <select
      id={CREDENTIAL_SELECT_ID}
      className='w-full rounded-md border bg-white px-3 py-2 text-sm dark:bg-gray-900'
      value={activeCredentialId}
      onChange={onCredentialChange}
    >
      {credentials.length === 0 && <option value=''>No credentials for {provider}.</option>}
      {credentials.map((cred) => (
        <option key={cred.id} value={cred.id}>
          {cred.providerUserId || cred.id.slice(0, ID_PREVIEW_LENGTH)}
        </option>
      ))}
    </select>
  </div>
);

const MappingSources = ({ formState }: MappingSourcesProps): ReactElement => {
  const {
    githubProjects,
    githubRepos,
    handleCreateMapping,
    linearProjects,
    projectOwner,
    projectOwnerIsOrg,
    provider,
    repoSearch,
    setProjectOwner,
    setProjectOwnerIsOrg,
    setRepoSearch,
  } = formState;

  if (provider === 'github') {
    return (
      <GitHubRepoList
        onCreateMapping={handleCreateMapping}
        onRepoSearchChange={setRepoSearch}
        repoSearch={repoSearch}
        repos={(githubRepos?.repos ?? []) as any}
      />
    );
  }

  if (provider === 'github_projects') {
    return (
      <GitHubProjectList
        projects={githubProjects?.projects ?? []}
        projectOwner={projectOwner}
        projectOwnerIsOrg={projectOwnerIsOrg}
        onCreateMapping={handleCreateMapping}
        onProjectOwnerChange={setProjectOwner}
        onProjectOwnerOrgChange={setProjectOwnerIsOrg}
      />
    );
  }

  return (
    <LinearProjectList
      projects={linearProjects?.projects ?? []}
      onCreateMapping={handleCreateMapping}
    />
  );
};

const GitHubRepoList = ({
  onCreateMapping,
  onRepoSearchChange,
  repoSearch,
  repos,
}: GitHubRepoListProps): ReactElement => {
  const handleSearchChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      onRepoSearchChange(event.target.value);
    },
    [onRepoSearchChange],
  );

  return (
    <div className='space-y-3'>
      <input
        className='w-full rounded-md border bg-white px-3 py-2 text-sm dark:bg-gray-900'
        placeholder='Search repositories...'
        value={repoSearch}
        onChange={handleSearchChange}
      />
      <div className='grid grid-cols-1 gap-3 md:grid-cols-2'>
        {repos.map((repo) => (
          <RepoRow key={repo.id} repo={repo} onCreateMapping={onCreateMapping} />
        ))}
      </div>
    </div>
  );
};

const RepoRow = ({ onCreateMapping, repo }: RepoRowProps): ReactElement => {
  const handleLink = useCallback(() => {
    onCreateMapping({
      externalId: repo.fullName,
      externalKey: repo.fullName,
      externalType: 'github_repo',
      externalUrl: repo.htmlUrl,
      mappingMetadata: {
        external_kind: 'repo',
        repo_full_name: repo.fullName,
      },
    });
  }, [onCreateMapping, repo.fullName, repo.htmlUrl]);

  return (
    <div className='flex items-center justify-between gap-3 rounded-lg border p-3'>
      <div>
        <div className='text-sm font-medium'>{repo.fullName}</div>
        <div className='text-xs text-gray-500'>{repo.description || 'No description'}</div>
      </div>
      <button
        type='button'
        onClick={handleLink}
        className='rounded bg-blue-100 px-3 py-1 text-xs text-blue-700 hover:bg-blue-200'
      >
        Link
      </button>
    </div>
  );
};

const GitHubProjectList = ({
  onCreateMapping,
  onProjectOwnerChange,
  onProjectOwnerOrgChange,
  projectOwner,
  projectOwnerIsOrg,
  projects,
}: GitHubProjectListProps): ReactElement => {
  const handleOwnerChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      onProjectOwnerChange(event.target.value);
    },
    [onProjectOwnerChange],
  );

  const handleOrgToggle = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      onProjectOwnerOrgChange(event.target.checked);
    },
    [onProjectOwnerOrgChange],
  );

  return (
    <div className='space-y-3'>
      <GitHubOwnerControls
        projectOwner={projectOwner}
        projectOwnerIsOrg={projectOwnerIsOrg}
        onOwnerChange={handleOwnerChange}
        onOrgToggle={handleOrgToggle}
      />
      <GitHubProjectGrid
        projects={projects}
        onCreateMapping={onCreateMapping}
        projectOwner={projectOwner}
        projectOwnerIsOrg={projectOwnerIsOrg}
      />
    </div>
  );
};

const GitHubOwnerControls = ({
  projectOwner,
  projectOwnerIsOrg,
  onOwnerChange,
  onOrgToggle,
}: {
  projectOwner: string;
  projectOwnerIsOrg: boolean;
  onOwnerChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onOrgToggle: (event: ChangeEvent<HTMLInputElement>) => void;
}): ReactElement => (
  <div className='grid grid-cols-1 gap-3 md:grid-cols-3'>
    <input
      className='w-full rounded-md border bg-white px-3 py-2 text-sm md:col-span-2 dark:bg-gray-900'
      placeholder='Owner or org (e.g. vercel)'
      value={projectOwner}
      onChange={onOwnerChange}
    />
    <label className='flex items-center gap-2 text-xs text-gray-600'>
      <input type='checkbox' checked={projectOwnerIsOrg} onChange={onOrgToggle} />
      Org owner
    </label>
  </div>
);

const GitHubProjectGrid = ({
  onCreateMapping,
  projectOwner,
  projectOwnerIsOrg,
  projects,
}: {
  onCreateMapping: (args: MappingCreateArgs) => Promise<void>;
  projectOwner: string;
  projectOwnerIsOrg: boolean;
  projects: {
    id: string;
    title: string;
    description?: string;
    url?: string;
  }[];
}): ReactElement => (
  <div className='grid grid-cols-1 gap-3 md:grid-cols-2'>
    {projects.map((project) => (
      <GitHubProjectRow
        key={project.id}
        project={project}
        onCreateMapping={onCreateMapping}
        projectOwner={projectOwner}
        projectOwnerIsOrg={projectOwnerIsOrg}
      />
    ))}
  </div>
);

const GitHubProjectRow = ({
  onCreateMapping,
  project,
  projectOwner,
  projectOwnerIsOrg,
}: GitHubProjectRowProps): ReactElement => {
  const handleLink = useCallback(() => {
    onCreateMapping({
      externalId: project.id,
      externalKey: project.title,
      externalType: 'github_project',
      externalUrl: project.url,
      mappingMetadata: {
        external_kind: 'project',
        project_id: project.id,
        project_owner: projectOwner,
        project_owner_is_org: projectOwnerIsOrg,
      },
    });
  }, [onCreateMapping, project, projectOwner, projectOwnerIsOrg]);

  return (
    <div className='flex items-center justify-between gap-3 rounded-lg border p-3'>
      <div>
        <div className='text-sm font-medium'>{project.title}</div>
        <div className='text-xs text-gray-500'>{project.description || 'No description'}</div>
      </div>
      <button
        type='button'
        onClick={handleLink}
        className='rounded bg-blue-100 px-3 py-1 text-xs text-blue-700 hover:bg-blue-200'
      >
        Link
      </button>
    </div>
  );
};

const LinearProjectList = ({
  onCreateMapping,
  projects,
}: {
  onCreateMapping: (args: {
    externalId: string;
    externalKey?: string;
    externalType: string;
    externalUrl?: string;
    mappingMetadata?: Record<string, unknown>;
  }) => Promise<void>;
  projects: {
    id: string;
    name: string;
    description?: string;
    url?: string;
  }[];
}): ReactElement => (
  <div className='grid grid-cols-1 gap-3 md:grid-cols-2'>
    {projects.map((project) => (
      <LinearProjectRow key={project.id} project={project} onCreateMapping={onCreateMapping} />
    ))}
  </div>
);

const LinearProjectRow = ({
  onCreateMapping,
  project,
}: {
  onCreateMapping: (args: {
    externalId: string;
    externalKey?: string;
    externalType: string;
    externalUrl?: string;
    mappingMetadata?: Record<string, unknown>;
  }) => Promise<void>;
  project: {
    id: string;
    name: string;
    description?: string;
    url?: string;
  };
}): ReactElement => {
  const handleLink = useCallback(() => {
    onCreateMapping({
      externalId: project.id,
      externalKey: project.name,
      externalType: 'linear_project',
      externalUrl: project.url,
      mappingMetadata: {
        external_kind: 'project',
        project_id: project.id,
      },
    });
  }, [onCreateMapping, project]);

  return (
    <div className='flex items-center justify-between gap-3 rounded-lg border p-3'>
      <div>
        <div className='text-sm font-medium'>{project.name}</div>
        <div className='text-xs text-gray-500'>{project.description || 'No description'}</div>
      </div>
      <button
        type='button'
        onClick={handleLink}
        className='rounded bg-blue-100 px-3 py-1 text-xs text-blue-700 hover:bg-blue-200'
      >
        Link
      </button>
    </div>
  );
};

const MappingList = ({ mappings }: { mappings: IntegrationMapping[] }): ReactElement => {
  if (mappings.length === 0) {
    return (
      <div className='py-12 text-center text-gray-500'>
        No mappings configured. Link a repo or project to enable sync.
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      {mappings.map((mapping) => (
        <MappingRow key={mapping.id} mapping={mapping} />
      ))}
    </div>
  );
};

const MappingRow = ({ mapping }: { mapping: IntegrationMapping }): ReactElement => {
  const triggerSync = useTriggerSync();
  const handleSync = useCallback(() => {
    triggerSync.mutate({ direction: 'pull', mappingId: mapping.id });
  }, [mapping.id, triggerSync]);

  return (
    <div className='rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800'>
      <div className='flex items-center justify-between'>
        <div>
          <div className='flex items-center space-x-2'>
            <span className='font-medium'>{mapping.localItemType}</span>
            <span className='text-gray-400'>
              {mapping.direction === 'bidirectional' ? '<->' : '->'}
            </span>
            <span className='font-medium capitalize'>
              {mapping.provider} {mapping.externalType}
            </span>
          </div>
          <div className='mt-1 text-sm text-gray-500'>
            Local: {mapping.localItemId.slice(0, ID_PREVIEW_LENGTH)}... | External:{' '}
            {mapping.externalKey || mapping.externalId}
          </div>
          {mapping.externalUrl && (
            <a
              href={mapping.externalUrl}
              target='_blank'
              rel='noopener noreferrer'
              className='text-sm text-blue-500 hover:underline'
            >
              View external
            </a>
          )}
        </div>
        <div className='flex items-center space-x-2'>
          <StatusBadge status={mapping.status} />
          <button
            type='button'
            onClick={handleSync}
            disabled={triggerSync.isPending}
            className='rounded bg-green-100 px-3 py-1 text-sm text-green-700 hover:bg-green-200'
          >
            Sync
          </button>
        </div>
      </div>
    </div>
  );
};

const SyncTab = ({
  syncStatus,
  isLoading,
}: {
  syncStatus: any;
  isLoading: boolean;
}): ReactElement => {
  if (isLoading) {
    return (
      <div className='flex justify-center py-8'>
        <LoadingSpinner text='Loading sync status...' />
      </div>
    );
  }

  return (
    <div className='space-y-6'>
      <SyncQueueStats queue={syncStatus?.queue} />
      <RecentSyncsList recentSyncs={syncStatus?.recentSyncs ?? []} />
    </div>
  );
};

const SyncQueueStats = ({ queue }: { queue: any }): ReactElement => (
  <div className='rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800'>
    <h2 className='mb-4 text-lg font-semibold'>Sync Queue</h2>
    <div className='grid grid-cols-4 gap-4'>
      <QueueStat label='Pending' value={queue?.pending ?? 0} tone='yellow' />
      <QueueStat label='Processing' value={queue?.processing ?? 0} tone='blue' />
      <QueueStat label='Completed' value={queue?.completed ?? 0} tone='green' />
      <QueueStat label='Failed' value={queue?.failed ?? 0} tone='red' />
    </div>
  </div>
);

const QueueStat = ({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: 'yellow' | 'blue' | 'green' | 'red';
}): ReactElement => (
  <div className='rounded bg-gray-50 p-4 text-center dark:bg-gray-700'>
    <div className={`text-2xl font-bold text-${tone}-600`}>{value}</div>
    <div className='text-sm text-gray-500'>{label}</div>
  </div>
);

const RecentSyncsList = ({
  recentSyncs,
}: {
  recentSyncs: {
    id: string;
    provider: string;
    eventType: string;
    itemsProcessed: number;
    itemsFailed: number;
    startedAt?: string;
    status: string;
  }[];
}): ReactElement => (
  <div className='rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800'>
    <h2 className='mb-4 text-lg font-semibold'>Recent Syncs</h2>
    {recentSyncs.length > 0 ? (
      <div className='space-y-2'>
        {recentSyncs.map((sync) => (
          <RecentSyncRow key={sync.id} sync={sync} />
        ))}
      </div>
    ) : (
      <div className='py-4 text-center text-gray-500'>No recent syncs</div>
    )}
  </div>
);

const RecentSyncRow = ({
  sync,
}: {
  sync: {
    provider: string;
    eventType: string;
    itemsProcessed: number;
    itemsFailed: number;
    startedAt?: string;
    status: string;
  };
}): ReactElement => (
  <div className='flex items-center justify-between rounded bg-gray-50 p-3 dark:bg-gray-700'>
    <div>
      <div className='font-medium'>
        {sync.provider} - {sync.eventType}
      </div>
      <div className='text-sm text-gray-500'>
        {sync.itemsProcessed} items processed
        {sync.itemsFailed > 0 && `, ${sync.itemsFailed} failed`}
      </div>
    </div>
    <div className='text-right'>
      <StatusBadge status={sync.status} />
      <div className='mt-1 text-xs text-gray-400'>
        {sync.startedAt && new Date(sync.startedAt).toLocaleString()}
      </div>
    </div>
  </div>
);

const ConflictsTab = ({
  conflicts,
  isLoading,
}: {
  conflicts: SyncConflict[];
  isLoading: boolean;
}): ReactElement => {
  if (isLoading) {
    return (
      <div className='flex justify-center py-8'>
        <LoadingSpinner text='Loading conflicts...' />
      </div>
    );
  }

  if (conflicts.length === 0) {
    return (
      <div className='py-12 text-center text-gray-500'>
        No pending conflicts. All syncs are in harmony.
      </div>
    );
  }

  return (
    <div className='space-y-4'>
      {conflicts.map((conflict) => (
        <ConflictRow key={conflict.id} conflict={conflict} />
      ))}
    </div>
  );
};

const ConflictRow = ({ conflict }: { conflict: SyncConflict }): ReactElement => {
  const resolveConflict = useResolveConflict();
  const handleResolve = useCallback(
    (resolution: 'local' | 'external' | 'skip') => {
      resolveConflict.mutate({ conflictId: conflict.id, resolution });
    },
    [conflict.id, resolveConflict],
  );

  return (
    <div className='rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800'>
      <ConflictHeader conflict={conflict} />
      <ConflictValues conflict={conflict} />
      <ConflictActions onResolve={handleResolve} isPending={resolveConflict.isPending} />
    </div>
  );
};

const ConflictHeader = ({ conflict }: { conflict: SyncConflict }): ReactElement => (
  <div className='mb-4 flex items-center justify-between'>
    <div>
      <div className='font-medium'>
        {conflict.conflictType} conflict
        {conflict.fieldName && ` - ${conflict.fieldName}`}
      </div>
      <div className='text-sm text-gray-500'>Provider: {conflict.provider}</div>
    </div>
    <StatusBadge status={conflict.status} />
  </div>
);

const ConflictValues = ({ conflict }: { conflict: SyncConflict }): ReactElement => (
  <div className='mb-4 grid grid-cols-2 gap-4'>
    <div className='rounded bg-blue-50 p-3 dark:bg-blue-900/20'>
      <div className='text-sm font-medium text-blue-700 dark:text-blue-300'>Local Value</div>
      <div className='mt-1 font-mono text-sm'>{JSON.stringify(conflict.localValue, null, 2)}</div>
      {conflict.localModifiedAt && (
        <div className='mt-2 text-xs text-gray-500'>
          Modified: {new Date(conflict.localModifiedAt).toLocaleString()}
        </div>
      )}
    </div>
    <div className='rounded bg-purple-50 p-3 dark:bg-purple-900/20'>
      <div className='text-sm font-medium text-purple-700 dark:text-purple-300'>External Value</div>
      <div className='mt-1 font-mono text-sm'>
        {JSON.stringify(conflict.externalValue, null, 2)}
      </div>
      {conflict.externalModifiedAt && (
        <div className='mt-2 text-xs text-gray-500'>
          Modified: {new Date(conflict.externalModifiedAt).toLocaleString()}
        </div>
      )}
    </div>
  </div>
);

const ConflictActions = ({
  isPending,
  onResolve,
}: {
  isPending: boolean;
  onResolve: (resolution: 'local' | 'external' | 'skip') => void;
}): ReactElement => {
  const handleLocal = useCallback(() => {
    onResolve('local');
  }, [onResolve]);

  const handleExternal = useCallback(() => {
    onResolve('external');
  }, [onResolve]);

  const handleSkip = useCallback(() => {
    onResolve('skip');
  }, [onResolve]);

  return (
    <div className='flex space-x-2'>
      <button
        type='button'
        onClick={handleLocal}
        disabled={isPending}
        className='rounded bg-blue-100 px-3 py-1 text-sm text-blue-700 hover:bg-blue-200'
      >
        Use Local
      </button>
      <button
        type='button'
        onClick={handleExternal}
        disabled={isPending}
        className='rounded bg-purple-100 px-3 py-1 text-sm text-purple-700 hover:bg-purple-200'
      >
        Use External
      </button>
      <button
        type='button'
        onClick={handleSkip}
        disabled={isPending}
        className='rounded bg-gray-100 px-3 py-1 text-sm text-gray-700 hover:bg-gray-200'
      >
        Skip
      </button>
    </div>
  );
};

const StatCard = ({
  title,
  value,
  subtitle,
  warning,
}: {
  title: string;
  value: string | number;
  subtitle: string;
  warning?: boolean;
}): ReactElement => (
  <div
    className={`rounded-lg border bg-white p-4 dark:bg-gray-800 ${
      warning ? 'border-red-300 dark:border-red-700' : 'border-gray-200 dark:border-gray-700'
    }`}
  >
    <div className='text-sm text-gray-500'>{title}</div>
    <div
      className={`text-2xl font-bold ${warning ? 'text-red-600' : 'text-gray-900 dark:text-white'}`}
    >
      {value}
    </div>
    <div className='text-xs text-gray-400'>{subtitle}</div>
  </div>
);

const ProviderCard = ({
  connected,
  description,
  name,
  onConnect,
  providerId,
}: {
  connected: boolean;
  description: string;
  name: string;
  onConnect: (provider: IntegrationProvider) => void;
  providerId: IntegrationProvider;
}): ReactElement => {
  const handleConnect = useCallback(() => {
    onConnect(providerId);
  }, [onConnect, providerId]);

  return (
    <div className='rounded-lg border border-gray-200 p-4 dark:border-gray-700'>
      <div className='mb-2 flex items-center space-x-3'>
        <ProviderIcon provider={providerId} />
        <div className='font-medium'>{name}</div>
      </div>
      <p className='mb-4 text-sm text-gray-500'>{description}</p>
      {connected ? (
        <span className='inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-sm text-green-700'>
          Connected
        </span>
      ) : (
        <button
          type='button'
          onClick={handleConnect}
          className='rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700'
        >
          Connect
        </button>
      )}
    </div>
  );
};

const ProviderIcon = ({ provider }: { provider: IntegrationProvider | string }): ReactElement => {
  const className = 'w-8 h-8';

  if (provider === 'github' || provider === 'github_projects') {
    return (
      <svg className={className} viewBox='0 0 24 24' fill='currentColor'>
        <title>GitHub</title>
        <path d='M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z' />
      </svg>
    );
  }

  if (provider === 'linear') {
    return (
      <svg className={className} viewBox='0 0 100 100' fill='currentColor'>
        <title>Linear</title>
        <path d='M1.22 61.4a48.97 48.97 0 0 0 37.38 37.38l-37.38-37.38zm-1.1-8.96a49.48 49.48 0 0 0 48.44 47.44L.12 52.44zm-.12-9.34a49.36 49.36 0 0 0 57.78 57.78L0 43.1zm.67-9.08l65.21 65.21a50.25 50.25 0 0 0 6.73-6.73L7.4 27.29a50.25 50.25 0 0 0-6.73 6.73zm12.5-12.5l65.21 65.21a49.68 49.68 0 0 0 5.51-8.6L13.77 13.27a49.68 49.68 0 0 0-5.6 8.6L12.17 21.87zm10.02-8.71l64.1 64.1a49.93 49.93 0 0 0 3.98-10.37L25.09 9.72a49.93 49.93 0 0 0-10.37 3.98l7.47 7.46zm15.38-3.16l62 62a49.06 49.06 0 0 0 1.43-14.3L40.87 8.57a49.06 49.06 0 0 0-14.3 1.43l11.0 11.0zM50 0a49.33 49.33 0 0 0-8.96.82L99.18 58.96A49.33 49.33 0 0 0 100 50c0-27.61-22.39-50-50-50z' />
      </svg>
    );
  }

  return <div className='flex h-8 w-8 items-center justify-center rounded-full bg-gray-200'>?</div>;
};

const StatusBadge = ({ status }: { status: string }): ReactElement => {
  const colors: Record<string, string> = {
    active: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    completed: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    expired: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
    failed: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    paused: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
    pending: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    processing: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  };

  return (
    <span
      className={`rounded px-2 py-1 text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-700'}`}
    >
      {status}
    </span>
  );
};

export { IntegrationsView };
export default IntegrationsView;

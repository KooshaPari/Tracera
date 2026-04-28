import type { MouseEvent, ReactElement } from 'react';

import { useCallback, useMemo } from 'react';

import type { IntegrationsMode } from '@/pages/projects/views/integrations-view/types';
import type { CredentialStatus, IntegrationProvider, IntegrationStats } from '@tracertm/types';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';
import { useStartOAuth } from '@/hooks/useIntegrations';
import { logger } from '@/lib/logger';
import ProviderIcon from '@/pages/projects/views/integrations-view/components/ProviderIcon';
import StatCard from '@/pages/projects/views/integrations-view/components/StatCard';
import StatusBadge from '@/pages/projects/views/integrations-view/components/StatusBadge';

interface OverviewTabProps {
  stats: IntegrationStats | undefined;
  isLoading: boolean;
  projectId: string;
  mode: IntegrationsMode;
}

const EMPTY_PROVIDERS: NonNullable<IntegrationStats['providers']> = [];

const CONNECT_PROVIDER_CARDS: readonly {
  providerId: IntegrationProvider;
  name: string;
  description: string;
}[] = [
  { providerId: 'github', name: 'GitHub', description: 'Sync issues, PRs, and repositories' },
  {
    providerId: 'github_projects',
    name: 'GitHub Projects',
    description: 'Sync project boards and cards',
  },
  { providerId: 'linear', name: 'Linear', description: 'Sync issues, projects, and teams' },
];

const PROVIDER_DATA_ATTR = 'data-provider';

function parseIntegrationProvider(value: string | undefined): IntegrationProvider | undefined {
  if (value === 'github' || value === 'github_projects' || value === 'linear') {
    return value;
  }
  return undefined;
}

function readNumber(value: number | undefined): number {
  if (value === undefined) {
    return 0;
  }
  return value;
}

function renderAccountConnectionsNotice(): ReactElement {
  return (
    <div className='rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800'>
      <h2 className='mb-2 text-lg font-semibold'>Account connections moved</h2>
      <p className='text-sm text-gray-500'>
        Link external accounts in Settings. Project mappings and sync controls live here.
      </p>
    </div>
  );
}

interface StatsCardValues {
  connectedProviders: number;
  mappingsActive: number;
  mappingsTotal: number;
  syncSuccessRate: number;
  recentSyncs: number;
  pendingConflicts: number;
  showWarning: boolean;
}

function buildStatsCardValues(stats: IntegrationStats | undefined): StatsCardValues {
  if (stats === undefined) {
    return {
      connectedProviders: 0,
      mappingsActive: 0,
      mappingsTotal: 0,
      syncSuccessRate: 0,
      recentSyncs: 0,
      pendingConflicts: 0,
      showWarning: false,
    };
  }

  const pendingConflicts = readNumber(stats.conflicts?.pending);

  return {
    connectedProviders: readNumber(stats.providers?.length),
    mappingsActive: readNumber(stats.mappings?.active),
    mappingsTotal: readNumber(stats.mappings?.total),
    syncSuccessRate: readNumber(stats.sync?.successRate),
    recentSyncs: readNumber(stats.sync?.recentSyncs),
    pendingConflicts,
    showWarning: pendingConflicts > 0,
  };
}

function renderStatsCards(values: StatsCardValues): ReactElement {
  return (
    <div className='grid grid-cols-1 gap-4 md:grid-cols-4'>
      <StatCard
        title='Connected Providers'
        value={values.connectedProviders}
        subtitle='integrations active'
      />
      <StatCard
        title='Active Mappings'
        value={values.mappingsActive}
        subtitle={`of ${values.mappingsTotal} total`}
      />
      <StatCard
        title='Sync Success Rate'
        value={`${values.syncSuccessRate}%`}
        subtitle={`${values.recentSyncs} recent syncs`}
      />
      <StatCard
        title='Pending Conflicts'
        value={values.pendingConflicts}
        subtitle='need resolution'
        warning={values.showWarning}
      />
    </div>
  );
}

function renderProviderStatusList(
  providers:
    | {
        provider: IntegrationProvider;
        credentialType?: string;
        status: CredentialStatus;
      }[]
    | undefined,
): ReactElement | undefined {
  const providerList = providers ?? EMPTY_PROVIDERS;
  if (providerList.length === 0) {
    return undefined;
  }

  return (
    <div className='rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800'>
      <h2 className='mb-4 text-lg font-semibold'>Connected Providers</h2>
      <div className='space-y-3'>
        {providerList.map((providerInfo) => (
          <div
            key={`${providerInfo.provider}-${providerInfo.credentialType ?? 'default'}`}
            className='flex items-center justify-between rounded-lg bg-gray-50 p-3 dark:bg-gray-700'
          >
            <div className='flex items-center space-x-3'>
              <ProviderIcon provider={providerInfo.provider} />
              <div>
                <div className='font-medium capitalize'>
                  {providerInfo.provider.replace('_', ' ')}
                </div>
                <div className='text-sm text-gray-500'>{providerInfo.credentialType}</div>
              </div>
            </div>
            <StatusBadge status={providerInfo.status} />
          </div>
        ))}
      </div>
    </div>
  );
}

function renderConnectProviderGrid({
  connectedProviders,
  onConnectButtonClick,
}: {
  connectedProviders: ReadonlySet<IntegrationProvider>;
  onConnectButtonClick: (event: MouseEvent<HTMLButtonElement>) => void;
}): ReactElement {
  return (
    <div className='rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800'>
      <h2 className='mb-4 text-lg font-semibold'>Connect New Provider</h2>
      <div className='grid grid-cols-1 gap-4 md:grid-cols-3'>
        {CONNECT_PROVIDER_CARDS.map((card) => {
          const isConnected = connectedProviders.has(card.providerId);
          if (isConnected) {
            return (
              <div
                key={card.providerId}
                className='rounded-lg border border-gray-200 p-4 dark:border-gray-700'
              >
                <div className='mb-2 flex items-center space-x-3'>
                  <ProviderIcon provider={card.providerId} />
                  <div className='font-medium'>{card.name}</div>
                </div>
                <p className='mb-4 text-sm text-gray-500'>{card.description}</p>
                <span className='inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-sm text-green-700'>
                  Connected
                </span>
              </div>
            );
          }

          return (
            <div
              key={card.providerId}
              className='rounded-lg border border-gray-200 p-4 dark:border-gray-700'
            >
              <div className='mb-2 flex items-center space-x-3'>
                <ProviderIcon provider={card.providerId} />
                <div className='font-medium'>{card.name}</div>
              </div>
              <p className='mb-4 text-sm text-gray-500'>{card.description}</p>
              <button
                type='button'
                data-provider={card.providerId}
                onClick={onConnectButtonClick}
                className='rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700'
              >
                Connect
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function OverviewTab({
  stats,
  isLoading,
  projectId,
  mode,
}: OverviewTabProps): ReactElement {
  const startOAuth = useStartOAuth();
  const providers = stats?.providers ?? EMPTY_PROVIDERS;
  const statsValues = useMemo(() => buildStatsCardValues(stats), [stats]);

  const connectedProviders = useMemo(
    () => new Set(providers.map((providerInfo) => providerInfo.provider)),
    [providers],
  );

  const handleConnectButtonClick = useCallback(
    (event: MouseEvent<HTMLButtonElement>) => {
      const providerValue = event.currentTarget.getAttribute(PROVIDER_DATA_ATTR) ?? undefined;
      const provider = parseIntegrationProvider(providerValue);
      if (provider === undefined) {
        return;
      }

      const redirectUri = `${globalThis.location.origin}/integrations/callback`;
      let credentialScope: 'user' | 'project' = 'project';
      if (mode === 'account') {
        credentialScope = 'user';
      }

      startOAuth.mutate(
        {
          credentialScope,
          projectId,
          provider,
          redirectUri,
        },
        {
          onSuccess: (result) => {
            globalThis.location.href = result.auth_url;
          },
          onError: (error: unknown) => {
            logger.error('Failed to start OAuth:', error);
          },
        },
      );
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

  if (mode !== 'account') {
    return (
      <div className='space-y-6'>
        {renderStatsCards(statsValues)}
        {renderAccountConnectionsNotice()}
        {renderProviderStatusList(providers)}
      </div>
    );
  }

  return (
    <div className='space-y-6'>
      {renderStatsCards(statsValues)}
      {renderConnectProviderGrid({
        connectedProviders,
        onConnectButtonClick: handleConnectButtonClick,
      })}
      {renderProviderStatusList(providers)}
    </div>
  );
}

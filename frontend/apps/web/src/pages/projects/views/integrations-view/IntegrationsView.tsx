import type { ReactElement } from 'react';

import { useCallback, useMemo, useState } from 'react';

import type {
  IntegrationCredential,
  IntegrationMapping,
  IntegrationStats,
  SyncConflict,
  SyncStatusSummary,
} from '@tracertm/types';

import {
  useConflicts,
  useCredentials,
  useIntegrationStats,
  useMappings,
  useSyncStatus,
} from '@/hooks/useIntegrations';

import type { IntegrationsMode, TabConfig, TabId } from './types';

import PageHeader from './components/PageHeader';
import TabContent from './components/TabContent';
import TabsNav from './components/TabsNav';

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

interface IntegrationsViewProps {
  projectId: string;
  mode?: IntegrationsMode | undefined;
  initialTab?: TabId | undefined;
  allowedTabs?: TabId[] | undefined;
}

function selectViewData({
  credentials,
  mappings,
  conflicts,
}: {
  credentials: { credentials: IntegrationCredential[] } | undefined;
  mappings: { mappings: IntegrationMapping[] } | undefined;
  conflicts: { conflicts: SyncConflict[]; total: number } | undefined;
}): {
  credentialsList: IntegrationCredential[];
  mappingsList: IntegrationMapping[];
  conflictsList: SyncConflict[];
  conflictTotal: number;
} {
  const credentialsList = credentials?.credentials ?? EMPTY_CREDENTIALS;
  const mappingsList = mappings?.mappings ?? EMPTY_MAPPINGS;
  const conflictsList = conflicts?.conflicts ?? EMPTY_CONFLICTS;
  const conflictTotal = conflicts?.total ?? 0;

  return { conflictTotal, conflictsList, credentialsList, mappingsList };
}

const useIntegrationsViewData = (
  projectId: string,
): {
  conflicts: { data: { conflicts: SyncConflict[]; total: number } | undefined; isLoading: boolean };
  credentials: { data: { credentials: IntegrationCredential[] } | undefined; isLoading: boolean };
  mappings: { data: { mappings: IntegrationMapping[] } | undefined; isLoading: boolean };
  stats: { data: IntegrationStats | undefined; isLoading: boolean };
  syncStatus: { data: SyncStatusSummary | undefined; isLoading: boolean };
} => {
  const stats = useIntegrationStats(projectId);
  const credentials = useCredentials(projectId);
  const mappings = useMappings(projectId);
  const syncStatus = useSyncStatus(projectId);
  const conflicts = useConflicts(projectId, 'pending');

  return { conflicts, credentials, mappings, stats, syncStatus };
};

const useIntegrationsTabs = (
  mode: IntegrationsMode,
  allowedTabs: TabId[] | undefined,
): TabConfig[] =>
  useMemo(() => {
    let defaultTabs = PROJECT_TABS;
    if (mode === 'account') {
      defaultTabs = ACCOUNT_TABS;
    }
    if (allowedTabs === undefined) {
      return defaultTabs;
    }
    return defaultTabs.filter((tab) => allowedTabs.includes(tab.id));
  }, [allowedTabs, mode]);

export default function IntegrationsView({
  projectId,
  mode = 'project',
  initialTab = 'overview',
  allowedTabs,
}: IntegrationsViewProps): ReactElement {
  const [activeTab, setActiveTab] = useState<TabId>(initialTab);
  const { conflicts, credentials, mappings, stats, syncStatus } =
    useIntegrationsViewData(projectId);

  const { conflictTotal, conflictsList, credentialsList, mappingsList } = selectViewData({
    conflicts: conflicts.data,
    credentials: credentials.data,
    mappings: mappings.data,
  });

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
}

export { IntegrationsView };

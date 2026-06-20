import type {
  IntegrationCredential,
  IntegrationMapping,
  IntegrationProvider,
  IntegrationStats,
  SyncConflict,
  SyncStatusSummary,
} from '@tracertm/types';

type IntegrationsMode = 'project' | 'account';

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
  mode: IntegrationsMode;
  projectId: string;
  syncLoading: boolean;
  syncStatus: SyncStatusSummary | undefined;
  stats: IntegrationStats | undefined;
  statsLoading: boolean;
}

interface ProviderConnectSectionProps {
  mode: IntegrationsMode;
  providers: { provider: IntegrationProvider }[];
  onConnect: (provider: IntegrationProvider) => void;
}

export type { IntegrationsMode, ProviderConnectSectionProps, TabConfig, TabContentProps, TabId };

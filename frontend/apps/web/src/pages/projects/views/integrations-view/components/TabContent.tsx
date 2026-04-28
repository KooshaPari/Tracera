import type { ReactElement } from 'react';

import type { TabContentProps } from '@/pages/projects/views/integrations-view/types';

import ConflictsTab from '@/pages/projects/views/integrations-view/tabs/ConflictsTab';
import CredentialsTab from '@/pages/projects/views/integrations-view/tabs/CredentialsTab';
import MappingsTab from '@/pages/projects/views/integrations-view/tabs/MappingsTab';
import OverviewTab from '@/pages/projects/views/integrations-view/tabs/OverviewTab';
import SyncTab from '@/pages/projects/views/integrations-view/tabs/SyncTab';

function renderActiveTab(props: TabContentProps): ReactElement {
  if (props.activeTab === 'overview') {
    return (
      <OverviewTab
        stats={props.stats}
        isLoading={props.statsLoading}
        projectId={props.projectId}
        mode={props.mode}
      />
    );
  }

  if (props.activeTab === 'credentials') {
    if (props.mode !== 'project') {
      return (
        <CredentialsTab credentials={props.credentials} isLoading={props.credentialsLoading} />
      );
    }
    return (
      <div className='py-6 text-sm text-gray-500'>
        Credentials are managed at the account level.
      </div>
    );
  }

  if (props.activeTab === 'mappings') {
    if (props.mode !== 'account') {
      return (
        <MappingsTab
          mappings={props.mappings}
          isLoading={props.mappingsLoading}
          projectId={props.projectId}
        />
      );
    }
    return <div className='py-6 text-sm text-gray-500'>Mappings are available for projects.</div>;
  }

  if (props.activeTab === 'sync') {
    if (props.mode !== 'account') {
      return <SyncTab syncStatus={props.syncStatus} isLoading={props.syncLoading} />;
    }
    return <div className='py-6 text-sm text-gray-500'>Sync status is available for projects.</div>;
  }

  if (props.activeTab === 'conflicts') {
    if (props.mode !== 'account') {
      return <ConflictsTab conflicts={props.conflicts} isLoading={props.conflictsLoading} />;
    }
    return <div className='py-6 text-sm text-gray-500'>Conflicts are available for projects.</div>;
  }

  return <div className='py-6 text-sm text-gray-500'>Unknown tab.</div>;
}

export default function TabContent(props: TabContentProps): ReactElement {
  return <>{renderActiveTab(props)}</>;
}

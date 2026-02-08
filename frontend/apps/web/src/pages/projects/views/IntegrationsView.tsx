import type { ReactElement } from 'react';

import IntegrationsViewImpl from './integrations-view/IntegrationsView';

export { IntegrationsViewImpl as IntegrationsView };

export default function IntegrationsView({
  projectId,
  mode,
  initialTab,
  allowedTabs,
}: Parameters<typeof IntegrationsViewImpl>[0]): ReactElement {
  return (
    <IntegrationsViewImpl
      projectId={projectId}
      mode={mode}
      initialTab={initialTab}
      allowedTabs={allowedTabs}
    />
  );
}

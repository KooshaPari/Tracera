import type { JSX } from 'react';

import { createFileRoute, useParams } from '@tanstack/react-router';
import { Suspense, lazy } from 'react';

import { ChunkLoadingSkeleton } from '@/lib/lazy-loading';

const WebhookIntegrationsView = lazy(async () => {
  const module = await import('@/pages/projects/views/WebhookIntegrationsView');
  return { default: module.WebhookIntegrationsView };
});

const WEBHOOKS_FALLBACK = <ChunkLoadingSkeleton message='Loading webhooks...' />;

const WebhooksViewRoute = (): JSX.Element => {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return (
    <Suspense fallback={WEBHOOKS_FALLBACK}>
      <WebhookIntegrationsView projectId={projectId} />
    </Suspense>
  );
};

const Route = createFileRoute('/projects/$projectId/views/webhooks')({
  component: WebhooksViewRoute,
  loader: () => ({}),
});

export { Route, WebhooksViewRoute };

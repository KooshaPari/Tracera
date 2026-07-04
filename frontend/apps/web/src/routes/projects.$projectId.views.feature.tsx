import { createFileRoute, useParams } from '@tanstack/react-router';

import { FeatureView } from '@/pages/projects/views/FeatureView';

function FeatureViewWrapper() {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return <FeatureView projectId={projectId} />;
}

export const FEATURE_VIEW = FeatureViewWrapper;

export const Route = createFileRoute('/projects/$projectId/views/feature')({
  component: FeatureViewWrapper,
  loader: async () => ({}),
});

import { createFileRoute, useParams } from '@tanstack/react-router';

import { ApiView } from '@/pages/projects/views/ApiView';

function ApiViewWrapper() {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return <ApiView projectId={projectId} />;
}

export const API_VIEW = ApiViewWrapper;

export const Route = createFileRoute('/projects/$projectId/views/api')({
  component: ApiViewWrapper,
  loader: async () => ({}),
});

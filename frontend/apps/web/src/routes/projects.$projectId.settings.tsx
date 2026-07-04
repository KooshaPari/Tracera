import { createFileRoute } from '@tanstack/react-router';

import { requireAuth } from '@/lib/route-guards';
import { ProjectSettingsView } from '@/views/ProjectSettingsView';

export const Route = createFileRoute('/projects/$projectId/settings')({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: function ProjectSettingsPage() {
    const { projectId } = Route.useParams();
    return <ProjectSettingsView projectId={projectId} />;
  },
});

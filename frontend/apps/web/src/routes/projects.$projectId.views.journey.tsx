import { createFileRoute, useParams } from '@tanstack/react-router';

import { ItemsTableView } from '@/views/ItemsTableView';

const JourneyView = (): JSX.Element => {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return <ItemsTableView projectId={projectId} view='journey' />;
};

const JOURNEY_VIEW = JourneyView;

const Route = createFileRoute('/projects/$projectId/views/journey')({
  component: JourneyView,
});

export { JOURNEY_VIEW, JourneyView, Route };

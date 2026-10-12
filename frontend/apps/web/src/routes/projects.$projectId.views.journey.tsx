import { createFileRoute, useParams } from "@tanstack/react-router";

import { JourneyArtifactView } from "@/views/artifacts/JourneyArtifactView";

const JourneyView = (): JSX.Element => {
  const { projectId } = useParams({ from: "/projects/$projectId" });
  return <JourneyArtifactView projectId={projectId} />;
};

const JOURNEY_VIEW = JourneyView;

const Route = createFileRoute("/projects/$projectId/views/journey")({
  component: JourneyView,
});

export { JOURNEY_VIEW, JourneyView, Route };

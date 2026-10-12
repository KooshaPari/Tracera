import { useParams } from "@tanstack/react-router";

import { GanttArtifactView } from "./GanttArtifactView";
import { KanbanArtifactView } from "./KanbanArtifactView";

export function KanbanRoute(): JSX.Element {
  const { projectId } = useParams({ from: "/projects/$projectId" });
  return <KanbanArtifactView projectId={projectId} />;
}

export function GanttRoute(): JSX.Element {
  const { projectId } = useParams({ from: "/projects/$projectId" });
  return <GanttArtifactView projectId={projectId} />;
}

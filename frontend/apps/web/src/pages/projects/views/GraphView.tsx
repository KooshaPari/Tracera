// Graph view: renders the node-link artifact graph (items as nodes, trace links as edges).
import { GraphArtifactView } from "@/views/artifacts/GraphArtifactView";

interface GraphViewProps {
  projectId?: string;
}

export function GraphView({ projectId }: GraphViewProps) {
  return <GraphArtifactView projectId={projectId} />;
}

export default GraphView;

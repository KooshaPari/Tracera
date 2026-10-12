// Coverage view: requirement x test matrix rendered from trace links.
import { CoverageArtifactView } from "@/views/artifacts/CoverageArtifactView";

interface CoverageMatrixViewProps {
  projectId?: string;
}

export function CoverageMatrixView({ projectId }: CoverageMatrixViewProps) {
  return <CoverageArtifactView projectId={projectId} />;
}

export default CoverageMatrixView;

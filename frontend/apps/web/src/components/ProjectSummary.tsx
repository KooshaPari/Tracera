import { NotImplemented, Unavailable } from "./Availability";

export function ProjectSummary({
  project,
}: {
  project: {
    id: string;
    name?: string | undefined;
    description?: string | null | undefined;
    detailUnavailable: number;
  };
}) {
  return (
    <section aria-label="Project summary">
      <h1>{project.name ?? project.id}</h1>
      {project.description && <p>{project.description}</p>}
      {project.detailUnavailable === 501 ? <NotImplemented /> : <Unavailable />}
      <p>Showing project summary from the project list. Detailed project data is unavailable.</p>
    </section>
  );
}

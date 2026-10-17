/** The project read contract counts non-deleted persisted problem records. */
export function persistedProjectCount(project: unknown): number {
  const count = (project as { problem_count?: unknown } | null)?.problem_count;
  if (typeof count !== "number" || !Number.isSafeInteger(count) || count < 0) {
    throw new Error("Project count unavailable");
  }
  return count;
}

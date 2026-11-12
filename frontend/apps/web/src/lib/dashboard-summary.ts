import type { DashboardProjectStats } from "@/api/system";

export function projectStatsFor(
  projects: Record<string, DashboardProjectStats> | undefined,
  id: string,
): DashboardProjectStats | undefined {
  return projects && Object.hasOwn(projects, id) ? projects[id] : undefined;
}

export function aggregateDashboardCounts(
  projects: Record<string, DashboardProjectStats>,
  field: "statusCounts" | "typeCounts",
): { name: string; value: number }[] {
  const counts = new Map<string, number>();
  for (const stats of Object.values(projects)) {
    for (const [name, value] of Object.entries(stats[field])) {
      counts.set(name, (counts.get(name) ?? 0) + value);
    }
  }
  return Array.from(counts, ([name, value]) => ({ name, value }));
}

import { useQuery } from '@tanstack/react-query';

import { useAuthStore } from '@/stores/authStore';

import { fetchDashboardSummary, type DashboardSummary } from '../api/system';

export type { DashboardProjectStats, DashboardSummary } from '../api/system';

export function useDashboardSummary() {
  const token = useAuthStore((s) => s.token);
  return useQuery<DashboardSummary>({
    enabled: Boolean(token),
    queryFn: ({ signal }) => fetchDashboardSummary(signal),
    queryKey: ['dashboard-summary', token ?? ''],
    refetchOnWindowFocus: false,
    staleTime: 5 * 60 * 1000,
  });
}

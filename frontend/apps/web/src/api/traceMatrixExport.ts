import { getCSRFHeaders } from '@/lib/csrf';
import { downloadTraceabilityMatrixCsv } from '@/lib/traceabilityMatrixExport';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

export interface TraceMatrixExportOptions {
  sourceView?: string | undefined;
  targetView?: string | undefined;
}

function buildAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = { ...getCSRFHeaders('GET') };
  const token = globalThis.localStorage?.getItem('auth_token');
  if (token?.trim()) {
    headers['Authorization'] = `Bearer ${token.trim()}`;
  }
  return headers;
}

/** Fetch server-generated traceability matrix CSV (analysis API). */
export async function fetchTraceMatrixCsv(
  projectId: string,
  options: TraceMatrixExportOptions = {},
): Promise<string> {
  const params = new URLSearchParams({ project_id: projectId });
  if (options.sourceView) {
    params.set('source_view', options.sourceView);
  }
  if (options.targetView) {
    params.set('target_view', options.targetView);
  }

  const response = await fetch(
    `${API_URL}/api/v1/analysis/trace-matrix/export?${params.toString()}`,
    { headers: buildAuthHeaders() },
  );

  if (!response.ok) {
    throw new Error(`Matrix export failed (${response.status})`);
  }

  return response.text();
}

export async function downloadTraceMatrixFromApi(
  projectId: string,
  options: TraceMatrixExportOptions = {},
): Promise<void> {
  const csv = await fetchTraceMatrixCsv(projectId, options);
  downloadTraceabilityMatrixCsv(csv, projectId);
}

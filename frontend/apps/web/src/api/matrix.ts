import type { Item, Link } from './types';

// Traceability Matrix API stub
import { client } from './client';

interface TraceabilityMatrix {
  coverage: {
    percentage: number;
    total: number;
    traced: number;
    untraced: number;
  };
  items: Item[];
  links: Link[];
}

const { apiClient } = client;
const { safeApiCall } = client;
const get = apiClient.GET.bind(apiClient);

const emptyMatrix: TraceabilityMatrix = {
  coverage: {
    percentage: 0,
    total: 0,
    traced: 0,
    untraced: 0,
  },
  items: [],
  links: [],
};

const isRecordObject = (value: unknown): value is Record<string, unknown> =>
  Object.prototype.toString.call(value) === '[object Object]';

const isTraceabilityMatrix = (value: unknown): value is TraceabilityMatrix => {
  if (!isRecordObject(value)) {
    return false;
  }

  const { coverage } = value;
  const { items } = value;
  const { links } = value;

  if (!isRecordObject(coverage) || !Array.isArray(items) || !Array.isArray(links)) {
    return false;
  }

  return (
    typeof coverage['percentage'] === 'number' &&
    typeof coverage['total'] === 'number' &&
    typeof coverage['traced'] === 'number' &&
    typeof coverage['untraced'] === 'number'
  );
};

const fetchMatrix = async (projectId: string): Promise<TraceabilityMatrix> => {
  try {
    const response = await safeApiCall(
      get('/api/v1/projects/{id}/matrix', {
        params: { path: { id: projectId } },
      }),
    );
    const { data } = response;
    if (isTraceabilityMatrix(data)) {
      return data;
    }
    return emptyMatrix;
  } catch {
    return emptyMatrix;
  }
};

const exportMatrix = async (projectId: string, format: 'csv' | 'json' | 'xlsx'): Promise<Blob> => {
  try {
    const response = await safeApiCall(
      get('/api/v1/projects/{id}/matrix/export', {
        params: { path: { id: projectId }, query: { format } },
      }),
    );
    return new Blob([JSON.stringify(response.data)], {
      type: 'application/json',
    });
  } catch {
    return new Blob(['{}'], { type: 'application/json' });
  }
};

const matrixApi = { exportMatrix, fetchMatrix };

export { exportMatrix, fetchMatrix, matrixApi, type TraceabilityMatrix };

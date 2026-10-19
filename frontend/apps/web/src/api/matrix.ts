import type { Item, Link } from "./types";

// Traceability Matrix API stub
import { client } from "./client";
import { requireAvailable, invalidResponse } from "./availability";

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
const get = apiClient.GET.bind(apiClient);

const isRecordObject = (value: unknown): value is Record<string, unknown> =>
  Object.prototype.toString.call(value) === "[object Object]";

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
    typeof coverage["percentage"] === "number" &&
    typeof coverage["total"] === "number" &&
    typeof coverage["traced"] === "number" &&
    typeof coverage["untraced"] === "number"
  );
};

const fetchMatrix = async (projectId: string): Promise<TraceabilityMatrix> => {
  const data = await requireAvailable(
    get("/api/v1/projects/{id}/matrix", { params: { path: { id: projectId } } }),
  );
  if (!isTraceabilityMatrix(data)) return invalidResponse();
  return data;
};

const exportMatrix = async (projectId: string, format: "csv" | "json" | "xlsx"): Promise<Blob> => {
  const data = await requireAvailable(
    get("/api/v1/projects/{id}/matrix/export", {
      params: { path: { id: projectId }, query: { format } },
      parseAs: "blob",
    }),
  );
  if (!(data instanceof Blob)) return invalidResponse();
  return data;
};

const matrixApi = { exportMatrix, fetchMatrix };

export { exportMatrix, fetchMatrix, matrixApi, type TraceabilityMatrix };

// System status API stub
import { logger } from "@/lib/logger";

import { client } from "./client";
import { invalidResponse, rejectNonApiContent, requireAvailable } from "./availability";

const { apiClient, getAuthHeaders, API_BASE_URL } = client;

export interface SystemStatus {
  status: "healthy" | "degraded" | "unhealthy";
  uptime: number;
  queuedJobs?: number | undefined;
  version?: string | undefined;
  mcp?:
    | {
        baseUrl?: string | undefined;
        authMode?: string | undefined;
        requiresAuth?: boolean;
      }
    | undefined;
}

// Dashboard summary types matching the GET /api/v1/dashboard/summary endpoint
export interface DashboardProjectStats {
  completedCount: number;
  statusCounts: Record<string, number>;
  totalCount: number;
  typeCounts: Record<string, number>;
}

export interface DashboardSummary {
  perProject: Record<string, DashboardProjectStats>;
  projectCount: number;
  statusDistribution: Record<string, number>;
  totalItemCount: number;
  typeDistribution: Record<string, number>;
}

const isRecordObject = (value: unknown): value is Record<string, unknown> =>
  Object.prototype.toString.call(value) === "[object Object]";

const isDashboardSummary = (value: unknown): value is DashboardSummary =>
  isRecordObject(value) &&
  isRecordObject(value["perProject"]) &&
  isRecordObject(value["statusDistribution"]) &&
  isRecordObject(value["typeDistribution"]) &&
  typeof value["projectCount"] === "number" &&
  typeof value["totalItemCount"] === "number";

export const fetchDashboardSummary = async (signal?: AbortSignal): Promise<DashboardSummary> => {
  const res = await fetch(`${API_BASE_URL}/api/v1/dashboard/summary`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    signal: signal ?? null,
  });
  if (!res.ok) {
    logger.warn("[API] request failed", { status: res.status, route: "/api/v1/dashboard/summary" });
    throw new client.ApiError(
      res.status,
      res.status === 501 ? "Not implemented yet" : "Service unavailable",
    );
  }
  rejectNonApiContent(res.headers.get("content-type") ?? "");
  const data: unknown = await res.json().catch(() => invalidResponse());
  if (!isDashboardSummary(data)) return invalidResponse();
  return data;
};

export const fetchSystemStatus = async (): Promise<SystemStatus> => {
  const payload = await requireAvailable(apiClient.GET("/api/v1/health", {}));
  if (!isRecordObject(payload)) {
    return invalidResponse();
  }
  const data = payload;
  const status = data["status"];
  const uptime = data["uptime_seconds"] ?? data["uptime"];
  if (
    typeof uptime !== "number" ||
    !["ok", "ready", "healthy", "degraded", "unhealthy"].includes(String(status))
  ) {
    return invalidResponse();
  }
  return {
    status: status === "ok" || status === "ready" ? "healthy" : (status as SystemStatus["status"]),
    uptime,
    queuedJobs: typeof data["queuedJobs"] === "number" ? data["queuedJobs"] : undefined,
    version: typeof data["version"] === "string" ? data["version"] : undefined,
  };
};

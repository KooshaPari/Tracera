import type {
  CoverageActivity,
  CoverageGapsResponse,
  CoverageStats,
  CoverageType,
  TestCoverage,
  TraceabilityMatrix,
} from "@tracertm/types";

import { client } from "@/api/client";
import { API_ORIGIN } from "@/config/api-origin";

const { getAuthHeaders } = client;

const API_URL = API_ORIGIN;

function transformCoverage(data: Record<string, unknown>): TestCoverage {
  return {
    coveragePercentage: data["coverage_percentage"] as number | undefined,
    coverageType: data["coverage_type"] as CoverageType,
    createdAt: String(data["created_at"]),
    createdBy: data["created_by"] as string | undefined,
    id: String(data["id"]),
    lastTestedAt: data["last_tested_at"] as string | undefined,
    lastTestResult: data["last_test_result"] as string | undefined,
    lastVerifiedAt: data["last_verified_at"] as string | undefined,
    metadata: data["metadata"] as Record<string, unknown> | undefined,
    notes: data["notes"] as string | undefined,
    projectId: String(data["project_id"]),
    rationale: data["rationale"] as string | undefined,
    requirementId: String(data["requirement_id"]),
    status: data["status"] as TestCoverage["status"],
    testCaseId: String(data["test_case_id"]),
    updatedAt: String(data["updated_at"]),
    verifiedBy: data["verified_by"] as string | undefined,
    version: Number(data["version"] ?? 0),
  };
}

function transformActivity(data: Record<string, unknown>): CoverageActivity {
  return {
    activityType: String(data["activity_type"]),
    coverageId: String(data["coverage_id"]),
    createdAt: String(data["created_at"]),
    description: data["description"] as string | undefined,
    fromValue: data["from_value"] as string | undefined,
    id: String(data["id"]),
    metadata: data["metadata"] as Record<string, unknown> | undefined,
    performedBy: data["performed_by"] as string | undefined,
    toValue: data["to_value"] as string | undefined,
  };
}

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url, { headers: getAuthHeaders() });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Request failed: ${res.status} ${errorText}`);
  }
  return res.json() as Promise<T>;
}

async function fetchTraceabilityMatrix(
  projectId: string,
  view?: string,
): Promise<TraceabilityMatrix> {
  const params = new URLSearchParams();
  if (view !== undefined && view !== "") {
    params.set("view", view);
  }
  const query = params.toString();
  return fetchJson<TraceabilityMatrix>(
    `${API_URL}/api/v1/projects/${projectId}/coverage/matrix${query === "" ? "" : `?${query}`}`,
  );
}

async function fetchCoverageGaps(projectId: string, view?: string): Promise<CoverageGapsResponse> {
  const params = new URLSearchParams();
  if (view !== undefined && view !== "") {
    params.set("view", view);
  }
  const query = params.toString();
  return fetchJson<CoverageGapsResponse>(
    `${API_URL}/api/v1/projects/${projectId}/coverage/gaps${query === "" ? "" : `?${query}`}`,
  );
}

async function fetchCoverageStats(projectId: string): Promise<CoverageStats> {
  return fetchJson<CoverageStats>(`${API_URL}/api/v1/projects/${projectId}/coverage/stats`);
}

async function fetchCoverages(
  projectId: string,
  requirementId?: string,
): Promise<{ coverages: TestCoverage[]; total: number }> {
  const params = new URLSearchParams();
  params.set("project_id", projectId);
  if (requirementId !== undefined && requirementId !== "") {
    params.set("requirement_id", requirementId);
  }
  const res = await fetch(`${API_URL}/api/v1/coverage?${params}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error("Failed to fetch coverage records");
  }
  const data = (await res.json()) as Record<string, unknown>;
  const coverages = (data["coverages"] as Record<string, unknown>[] | undefined) ?? [];
  return {
    coverages: coverages.map((item) => transformCoverage(item)),
    total: Number(data["total"] ?? 0),
  };
}

async function fetchCoverage(id: string): Promise<TestCoverage> {
  const data = await fetchJson<Record<string, unknown>>(`${API_URL}/api/v1/coverage/${id}`);
  return transformCoverage(data);
}

async function fetchCoverageActivities(coverageId: string): Promise<CoverageActivity[]> {
  const data = await fetchJson<Record<string, unknown>>(
    `${API_URL}/api/v1/coverage/${coverageId}/activities`,
  );
  const activities = (data["activities"] as Record<string, unknown>[] | undefined) ?? [];
  return activities.map((item) => transformActivity(item));
}

interface CreateCoverageData {
  projectId: string;
  testCaseId: string;
  requirementId: string;
  coverageType?: CoverageType | undefined;
  coveragePercentage?: number | undefined;
  rationale?: string | undefined;
  notes?: string | undefined;
  metadata?: Record<string, unknown> | undefined;
}

async function createCoverage(data: CreateCoverageData): Promise<TestCoverage> {
  const res = await fetch(`${API_URL}/api/v1/coverage`, {
    body: JSON.stringify({
      coverage_percentage: data.coveragePercentage,
      coverage_type: data.coverageType ?? "direct",
      metadata: data.metadata,
      notes: data.notes,
      project_id: data.projectId,
      rationale: data.rationale,
      requirement_id: data.requirementId,
      test_case_id: data.testCaseId,
    }),
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    method: "POST",
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to create coverage: ${res.status} ${errorText}`);
  }
  const result = (await res.json()) as Record<string, unknown>;
  return transformCoverage(result);
}

interface UpdateCoverageData {
  coverageType?: CoverageType | undefined;
  coveragePercentage?: number | undefined;
  rationale?: string | undefined;
  notes?: string | undefined;
  status?: TestCoverage["status"] | undefined;
  metadata?: Record<string, unknown> | undefined;
}

async function updateCoverage(id: string, data: UpdateCoverageData): Promise<TestCoverage> {
  const payload: Record<string, unknown> = {};
  if (data.coverageType !== undefined) {
    payload["coverage_type"] = data.coverageType;
  }
  if (data.coveragePercentage !== undefined) {
    payload["coverage_percentage"] = data.coveragePercentage;
  }
  if (data.rationale !== undefined) {
    payload["rationale"] = data.rationale;
  }
  if (data.notes !== undefined) {
    payload["notes"] = data.notes;
  }
  if (data.status !== undefined) {
    payload["status"] = data.status;
  }
  if (data.metadata !== undefined) {
    payload["metadata"] = data.metadata;
  }

  const res = await fetch(`${API_URL}/api/v1/coverage/${id}`, {
    body: JSON.stringify(payload),
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    method: "PUT",
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to update coverage: ${res.status} ${errorText}`);
  }
  const result = (await res.json()) as Record<string, unknown>;
  return transformCoverage(result);
}

async function deleteCoverage(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/coverage/${id}`, {
    headers: getAuthHeaders(),
    method: "DELETE",
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to delete coverage: ${res.status} ${errorText}`);
  }
}

async function verifyCoverage(id: string): Promise<TestCoverage> {
  const res = await fetch(`${API_URL}/api/v1/coverage/${id}/verify`, {
    headers: getAuthHeaders(),
    method: "POST",
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to verify coverage: ${res.status} ${errorText}`);
  }
  const result = (await res.json()) as Record<string, unknown>;
  return transformCoverage(result);
}

export {
  type CreateCoverageData,
  createCoverage,
  deleteCoverage,
  fetchCoverage,
  fetchCoverageActivities,
  fetchCoverageGaps,
  fetchCoverages,
  fetchCoverageStats,
  fetchTraceabilityMatrix,
  type UpdateCoverageData,
  updateCoverage,
  verifyCoverage,
};

import type {
  ImpactLevel,
  Problem,
  ProblemActivity,
  ProblemStatus,
  RCAMethod,
  ResolutionType,
  RootCauseCategory,
} from '@tracertm/types';

import { client } from '@/api/client';
import {
  asArray,
  asBoolean,
  asNumber,
  asRecord,
  asString,
  decodeProblemActivitiesResponse,
  decodeProblemStatsResponse,
  transformProblem,
} from '@/hooks/problems/problemDecoders';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:4000';

interface ProblemFilters {
  projectId: string;
  status?: ProblemStatus;
  priority?: ImpactLevel;
  impactLevel?: ImpactLevel;
  category?: string;
  assignedTo?: string;
}

interface CreateProblemData {
  projectId: string;
  title: string;
  description?: string;
  category?: string;
  subCategory?: string;
  tags?: string[];
  impactLevel?: ImpactLevel;
  urgency?: ImpactLevel;
  priority?: ImpactLevel;
  affectedSystems?: string[];
  affectedUsersEstimated?: number;
  businessImpactDescription?: string;
  assignedTo?: string;
  assignedTeam?: string;
  owner?: string;
  targetResolutionDate?: string;
  metadata?: Record<string, unknown>;
}

interface RCAData {
  rcaMethod: RCAMethod;
  rcaNotes?: string;
  rcaData?: Record<string, unknown>;
  rootCauseIdentified?: boolean;
  rootCauseDescription?: string;
  rootCauseCategory?: RootCauseCategory;
  rootCauseConfidence?: 'high' | 'medium' | 'low';
}

async function readJsonRecord(res: Response): Promise<Record<string, unknown>> {
  const json: unknown = await res.json();
  return asRecord(json);
}

async function fetchProblems(
  filters: ProblemFilters,
): Promise<{ problems: Problem[]; total: number }> {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);
  if (filters.status !== undefined) {
    params.set('status', filters.status);
  }
  if (filters.priority !== undefined) {
    params.set('priority', filters.priority);
  }
  if (filters.impactLevel !== undefined) {
    params.set('impact_level', filters.impactLevel);
  }
  if (filters.category !== undefined && filters.category.length > 0) {
    params.set('category', filters.category);
  }
  if (filters.assignedTo !== undefined && filters.assignedTo.length > 0) {
    params.set('assigned_to', filters.assignedTo);
  }

  const res = await fetch(`${API_URL}/api/v1/problems?${params}`, {
    headers: {
      'X-Bulk-Operation': 'true',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch problems: ${res.status} ${errorText}`);
  }
  const data = await readJsonRecord(res);
  return {
    problems: asArray(data['problems']).map((problemValue: unknown) =>
      transformProblem(asRecord(problemValue)),
    ),
    total: asNumber(data['total'], 0),
  };
}

async function fetchProblem(id: string): Promise<Problem> {
  const res = await fetch(`${API_URL}/api/v1/problems/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch problem');
  }
  const data = await readJsonRecord(res);
  return transformProblem(data);
}

async function createProblem(
  data: CreateProblemData,
): Promise<{ id: string; problemNumber: string }> {
  const res = await fetch(`${API_URL}/api/v1/problems?project_id=${data.projectId}`, {
    body: JSON.stringify({
      affected_systems: data.affectedSystems,
      affected_users_estimated: data.affectedUsersEstimated,
      assigned_team: data.assignedTeam,
      assigned_to: data.assignedTo,
      business_impact_description: data.businessImpactDescription,
      category: data.category,
      description: data.description,
      impact_level: data.impactLevel ?? 'medium',
      metadata: data.metadata ?? {},
      owner: data.owner,
      priority: data.priority ?? 'medium',
      sub_category: data.subCategory,
      tags: data.tags,
      target_resolution_date: data.targetResolutionDate,
      title: data.title,
      urgency: data.urgency ?? 'medium',
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create problem');
  }
  const result = await readJsonRecord(res);
  return { id: asString(result['id'], ''), problemNumber: asString(result['problem_number'], '') };
}

async function updateProblem(
  id: string,
  data: Partial<CreateProblemData>,
): Promise<{ id: string; version: number }> {
  const res = await fetch(`${API_URL}/api/v1/problems/${id}`, {
    body: JSON.stringify({
      affected_systems: data.affectedSystems,
      affected_users_estimated: data.affectedUsersEstimated,
      assigned_team: data.assignedTeam,
      assigned_to: data.assignedTo,
      business_impact_description: data.businessImpactDescription,
      category: data.category,
      description: data.description,
      impact_level: data.impactLevel,
      metadata: data.metadata,
      owner: data.owner,
      priority: data.priority,
      sub_category: data.subCategory,
      tags: data.tags,
      target_resolution_date: data.targetResolutionDate,
      title: data.title,
      urgency: data.urgency,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PUT',
  });
  if (!res.ok) {
    throw new Error('Failed to update problem');
  }
  const result = await readJsonRecord(res);
  return { id: asString(result['id'], ''), version: asNumber(result['version'], 0) };
}

async function transitionProblemStatus(
  id: string,
  toStatus: ProblemStatus,
  reason?: string,
): Promise<{ id: string; status: string; version: number }> {
  const res = await fetch(`${API_URL}/api/v1/problems/${id}/status`, {
    body: JSON.stringify({
      reason,
      to_status: toStatus,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to transition status: ${errorText}`);
  }
  const result = await readJsonRecord(res);
  return {
    id: asString(result['id'], ''),
    status: asString(result['status'], ''),
    version: asNumber(result['version'], 0),
  };
}

async function recordRCA(
  id: string,
  data: RCAData,
): Promise<{ id: string; rcaPerformed: boolean; rootCauseIdentified: boolean }> {
  const res = await fetch(`${API_URL}/api/v1/problems/${id}/rca`, {
    body: JSON.stringify({
      rca_data: data.rcaData,
      rca_method: data.rcaMethod,
      rca_notes: data.rcaNotes,
      root_cause_category: data.rootCauseCategory,
      root_cause_confidence: data.rootCauseConfidence,
      root_cause_description: data.rootCauseDescription,
      root_cause_identified: data.rootCauseIdentified ?? false,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to record RCA');
  }
  const result = await readJsonRecord(res);
  return {
    id: asString(result['id'], ''),
    rcaPerformed: asBoolean(result['rca_performed'], false),
    rootCauseIdentified: asBoolean(result['root_cause_identified'], false),
  };
}

async function closeProblem(
  id: string,
  resolutionType: ResolutionType,
  closureNotes?: string,
): Promise<{ id: string; status: string; resolutionType: string }> {
  const res = await fetch(`${API_URL}/api/v1/problems/${id}/close`, {
    body: JSON.stringify({
      closure_notes: closureNotes,
      resolution_type: resolutionType,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to close problem');
  }
  const result = await readJsonRecord(res);
  return {
    id: asString(result['id'], ''),
    resolutionType: asString(result['resolution_type'], ''),
    status: asString(result['status'], ''),
  };
}

async function deleteProblem(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/problems/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete problem');
  }
}

async function fetchProblemActivities(
  problemId: string,
  limit = 50,
): Promise<{ problemId: string; activities: ProblemActivity[] }> {
  const res = await fetch(`${API_URL}/api/v1/problems/${problemId}/activities?limit=${limit}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch activities');
  }
  const data = await readJsonRecord(res);
  return decodeProblemActivitiesResponse(data);
}

async function fetchProblemStats(projectId: string): Promise<{
  projectId: string;
  byStatus: Record<string, number>;
  byPriority: Record<string, number>;
  total: number;
}> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/problems/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch problem stats');
  }
  const data = await readJsonRecord(res);
  return decodeProblemStatsResponse(data);
}

const problemsApi = {
  closeProblem,
  createProblem,
  deleteProblem,
  fetchProblem,
  fetchProblemActivities,
  fetchProblems,
  fetchProblemStats,
  recordRCA,
  transitionProblemStatus,
  updateProblem,
};

export {
  closeProblem,
  createProblem,
  deleteProblem,
  fetchProblem,
  fetchProblemActivities,
  fetchProblems,
  fetchProblemStats,
  problemsApi,
  recordRCA,
  transitionProblemStatus,
  updateProblem,
  type CreateProblemData,
  type ProblemFilters,
  type RCAData,
};

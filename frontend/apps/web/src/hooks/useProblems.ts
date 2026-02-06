import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

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

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

const IMPACT_LEVEL_BY_NUMBER: Record<number, ImpactLevel> = {
  1: 'low',
  2: 'medium',
  3: 'high',
  4: 'high',
};

const CONFIDENCE_LEVEL_BY_NUMBER: Record<number, 'high' | 'medium' | 'low'> = {
  1: 'low',
  2: 'medium',
  3: 'high',
  4: 'high',
};

function toImpactLevel(value: unknown): ImpactLevel {
  if (value === undefined || value === null) {
    return 'medium';
  }
  if (typeof value === 'string') {
    if (value === 'critical') {
      return 'high';
    }
    if (['high', 'medium', 'low'].includes(value)) {
      return value as ImpactLevel;
    }
  }
  if (typeof value === 'number' && value in IMPACT_LEVEL_BY_NUMBER) {
    return (IMPACT_LEVEL_BY_NUMBER[value] ?? 'medium') as ImpactLevel;
  }
  return 'medium';
}

function toConfidenceLevel(value: unknown): 'high' | 'medium' | 'low' {
  if (value === undefined || value === null) {
    return 'medium';
  }
  if (typeof value === 'string') {
    if (['high', 'medium', 'low'].includes(value)) {
      return value as 'high' | 'medium' | 'low';
    }
  }
  if (typeof value === 'number' && value in CONFIDENCE_LEVEL_BY_NUMBER) {
    return (CONFIDENCE_LEVEL_BY_NUMBER[value] ?? 'medium') as 'high' | 'medium' | 'low';
  }
  return 'medium';
}

// Transform API response (snake_case) to frontend format (camelCase)
function transformProblem(data: Record<string, unknown>): Problem {
  return {
    affectedSystems: data['affected_systems'] as string[] | undefined,
    affectedUsersEstimated: data['affected_users_estimated'] as number | undefined,
    assignedTeam: data['assigned_team'] as string | undefined,
    assignedTo: data['assigned_to'] as string | undefined,
    businessImpactDescription: data['business_impact_description'] as string | undefined,
    category: data['category'] as string | undefined,
    closedAt: data['closed_at'] as string | undefined,
    closedBy: data['closed_by'] as string | undefined,
    closureNotes: data['closure_notes'] as string | undefined,
    createdAt: data['created_at'] as string,
    description: data['description'] as string | undefined,
    id: data['id'] as string,
    impactLevel: toImpactLevel(data['impact_level']),
    knowledgeArticleId: data['knowledge_article_id'] as string | undefined,
    knownErrorId: data['known_error_id'] as string | undefined,
    metadata: data['metadata'] as Record<string, unknown> | undefined,
    owner: data['owner'] as string | undefined,
    permanentFixAvailable: data['permanent_fix_available'] as boolean,
    permanentFixChangeId: data['permanent_fix_change_id'] as string | undefined,
    permanentFixDescription: data['permanent_fix_description'] as string | undefined,
    permanentFixImplementedAt: data['permanent_fix_implemented_at'] as string | undefined,
    priority: toImpactLevel(data['priority']),
    problemNumber: data['problem_number'] as string,
    projectId: data['project_id'] as string,
    rcaCompletedAt: data['rca_completed_at'] as string | undefined,
    rcaCompletedBy: data['rca_completed_by'] as string | undefined,
    rcaData: data['rca_data'] as Record<string, unknown> | undefined,
    rcaMethod: data['rca_method'] as RCAMethod | undefined,
    rcaNotes: data['rca_notes'] as string | undefined,
    rcaPerformed: data['rca_performed'] as boolean,
    resolutionType: data['resolution_type'] as ResolutionType | undefined,
    rootCauseCategory: data['root_cause_category'] as RootCauseCategory | undefined,
    rootCauseConfidence: toConfidenceLevel(data['root_cause_confidence']),
    rootCauseDescription: data['root_cause_description'] as string | undefined,
    rootCauseIdentified: data['root_cause_identified'] as boolean,
    status: data['status'] as ProblemStatus,
    subCategory: data['sub_category'] as string | undefined,
    tags: data['tags'] as string[] | undefined,
    targetResolutionDate: data['target_resolution_date'] as string | undefined,
    title: data['title'] as string,
    updatedAt: data['updated_at'] as string,
    urgency: toImpactLevel(data['urgency']),
    version: (data['version'] as number | undefined) ?? 0,
    workaroundAvailable: data['workaround_available'] as boolean,
    workaroundDescription: data['workaround_description'] as string | undefined,
    workaroundEffectiveness: data['workaround_effectiveness'] as
      | 'permanent_fix'
      | 'partial'
      | 'temporary'
      | undefined,
  };
}

interface ProblemFilters {
  projectId: string;
  status?: ProblemStatus;
  priority?: ImpactLevel;
  impactLevel?: ImpactLevel;
  category?: string;
  assignedTo?: string;
}

async function fetchProblems(
  filters: ProblemFilters,
): Promise<{ problems: Problem[]; total: number }> {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);
  if (filters.status) {
    params.set('status', filters.status);
  }
  if (filters.priority) {
    params.set('priority', filters.priority);
  }
  if (filters.impactLevel) {
    params.set('impact_level', filters.impactLevel);
  }
  if (filters.category) {
    params.set('category', filters.category);
  }
  if (filters.assignedTo) {
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
  const data = await res.json();
  return {
    problems: (data['problems'] || []).map(transformProblem),
    total: data['total'] || 0,
  };
}

async function fetchProblem(id: string): Promise<Problem> {
  const res = await fetch(`${API_URL}/api/v1/problems/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch problem');
  }
  const data = await res.json();
  return transformProblem(data);
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

async function createProblem(
  data: CreateProblemData,
): Promise<{ id: string; problemNumber: string }> {
  const res = await fetch(`${API_URL}/api/v1/problems?project_id=${data['projectId']}`, {
    body: JSON.stringify({
      affected_systems: data['affectedSystems'],
      affected_users_estimated: data['affectedUsersEstimated'],
      assigned_team: data['assignedTeam'],
      assigned_to: data['assignedTo'],
      business_impact_description: data['businessImpactDescription'],
      category: data['category'],
      description: data['description'],
      impact_level: data['impactLevel'] || 'medium',
      metadata: data['metadata'] || {},
      owner: data['owner'],
      priority: data['priority'] || 'medium',
      sub_category: data['subCategory'],
      tags: data['tags'],
      target_resolution_date: data['targetResolutionDate'],
      title: data['title'],
      urgency: data['urgency'] || 'medium',
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create problem');
  }
  const result = await res.json();
  return { id: result['id'], problemNumber: result['problem_number'] };
}

async function updateProblem(
  id: string,
  data: Partial<CreateProblemData>,
): Promise<{ id: string; version: number }> {
  const res = await fetch(`${API_URL}/api/v1/problems/${id}`, {
    body: JSON.stringify({
      affected_systems: data['affectedSystems'],
      affected_users_estimated: data['affectedUsersEstimated'],
      assigned_team: data['assignedTeam'],
      assigned_to: data['assignedTo'],
      business_impact_description: data['businessImpactDescription'],
      category: data['category'],
      description: data['description'],
      impact_level: data['impactLevel'],
      metadata: data['metadata'],
      owner: data['owner'],
      priority: data['priority'],
      sub_category: data['subCategory'],
      tags: data['tags'],
      target_resolution_date: data['targetResolutionDate'],
      title: data['title'],
      urgency: data['urgency'],
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PUT',
  });
  if (!res.ok) {
    throw new Error('Failed to update problem');
  }
  return res.json();
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
  return res.json();
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

async function recordRCA(
  id: string,
  data: RCAData,
): Promise<{
  id: string;
  rcaPerformed: boolean;
  rootCauseIdentified: boolean;
}> {
  const res = await fetch(`${API_URL}/api/v1/problems/${id}/rca`, {
    body: JSON.stringify({
      rca_data: data['rcaData'],
      rca_method: data['rcaMethod'],
      rca_notes: data['rcaNotes'],
      root_cause_category: data['rootCauseCategory'],
      root_cause_confidence: data['rootCauseConfidence'],
      root_cause_description: data['rootCauseDescription'],
      root_cause_identified: data['rootCauseIdentified'] || false,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to record RCA');
  }
  const result = await res.json();
  return {
    id: result['id'],
    rcaPerformed: result['rca_performed'],
    rootCauseIdentified: result['root_cause_identified'],
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
  const result = await res.json();
  return {
    id: result['id'],
    resolutionType: result['resolution_type'],
    status: result.status,
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
  const data = await res.json();
  return {
    activities: (data['activities'] || []).map((a: Record<string, unknown>) => ({
      activityType: a['activity_type'],
      createdAt: a['created_at'],
      description: a['description'],
      fromValue: a['from_value'],
      id: a['id'],
      metadata: a['metadata'],
      performedBy: a['performed_by'],
      problemId: a['problem_id'],
      toValue: a['to_value'],
    })),
    problemId: data['problem_id'],
  };
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
  const data = await res.json();
  return {
    byPriority: data['by_priority'] || {},
    byStatus: data['by_status'] || {},
    projectId: data['project_id'],
    total: data['total'] || 0,
  };
}

// React Query hooks

export function useProblems(filters: ProblemFilters) {
  return useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: () => fetchProblems(filters),
    queryKey: ['problems', JSON.stringify(filters)],
  });
}

export function useProblem(id: string) {
  return useQuery({
    enabled: Boolean(id),
    queryFn: () => fetchProblem(id),
    queryKey: ['problems', id],
  });
}

export function useCreateProblem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createProblem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

export function useUpdateProblem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateProblemData> }) =>
      updateProblem(id, data),
    onSuccess: (_, _vars) => {
      queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

export function useTransitionProblemStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      toStatus,
      reason,
    }: {
      id: string;
      toStatus: ProblemStatus;
      reason?: string;
    }) => transitionProblemStatus(id, toStatus, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

export function useRecordRCA() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: RCAData }) => recordRCA(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

export function useCloseProblem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      resolutionType,
      closureNotes,
    }: {
      id: string;
      resolutionType: ResolutionType;
      closureNotes?: string;
    }) => closeProblem(id, resolutionType, closureNotes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

export function useDeleteProblem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteProblem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['problems'] });
    },
  });
}

export function useProblemActivities(problemId: string, limit = 50) {
  return useQuery({
    enabled: Boolean(problemId),
    queryFn: () => fetchProblemActivities(problemId, limit),
    queryKey: ['problemActivities', problemId, limit],
  });
}

export function useProblemStats(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: () => fetchProblemStats(projectId),
    queryKey: ['problemStats', projectId],
  });
}

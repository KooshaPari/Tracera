import { client } from '@/api/client';

import type {
  CoverageMetrics,
  DefectDensity,
  ExecutionHistory,
  FlakyTests,
  PassRateTrend,
  QAMetricsSummary,
} from './types';

import { asRecord } from './coerce';
import {
  transformCoverageMetrics,
  transformDefectDensity,
  transformExecutionHistory,
  transformFlakyTests,
  transformPassRateTrend,
  transformSummary,
} from './transform';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:4000';

async function readJsonRecord(res: Response): Promise<Record<string, unknown>> {
  const json: unknown = await res.json();
  return asRecord(json);
}

async function fetchQAMetricsSummary(projectId: string): Promise<QAMetricsSummary> {
  const res = await fetch(`${API_URL}/api/v1/qa/metrics/summary?project_id=${projectId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch QA metrics summary');
  }
  const data = await readJsonRecord(res);
  return transformSummary(data);
}

async function fetchPassRateTrend(projectId: string, days = 30): Promise<PassRateTrend> {
  const res = await fetch(
    `${API_URL}/api/v1/qa/metrics/pass-rate?project_id=${projectId}&days=${days}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch pass rate trend');
  }
  const data = await readJsonRecord(res);
  return transformPassRateTrend(data);
}

async function fetchCoverageMetrics(projectId: string): Promise<CoverageMetrics> {
  const res = await fetch(`${API_URL}/api/v1/qa/metrics/coverage?project_id=${projectId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch coverage metrics');
  }
  const data = await readJsonRecord(res);
  return transformCoverageMetrics(data);
}

async function fetchDefectDensity(projectId: string): Promise<DefectDensity> {
  const res = await fetch(`${API_URL}/api/v1/qa/metrics/defect-density?project_id=${projectId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch defect density');
  }
  const data = await readJsonRecord(res);
  return transformDefectDensity(data);
}

async function fetchFlakyTests(projectId: string): Promise<FlakyTests> {
  const res = await fetch(`${API_URL}/api/v1/qa/metrics/flaky-tests?project_id=${projectId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch flaky tests');
  }
  const data = await readJsonRecord(res);
  return transformFlakyTests(data);
}

async function fetchExecutionHistory(projectId: string, days = 7): Promise<ExecutionHistory> {
  const res = await fetch(
    `${API_URL}/api/v1/qa/metrics/execution-history?project_id=${projectId}&days=${days}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch execution history');
  }
  const data = await readJsonRecord(res);
  return transformExecutionHistory(data);
}

export {
  fetchCoverageMetrics,
  fetchDefectDensity,
  fetchExecutionHistory,
  fetchFlakyTests,
  fetchPassRateTrend,
  fetchQAMetricsSummary,
};

/**
 * TanStack Query hooks for Item Specification Analytics
 *
 * Provides hooks for blockchain/NFT-like analytics including:
 * - EARS pattern analysis
 * - ISO 29148 quality scoring
 * - Merkle proof generation/verification
 * - Version chain history
 * - Flakiness detection
 * - ODC classification
 * - CVSS security scoring
 * - Impact analysis
 * - WSJF/RICE prioritization
 * - Coverage gap analysis
 * - Suspect link detection
 * - Semantic similarity
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { client } from '@/api/client';
import { logger } from '@/lib/logger';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

// =============================================================================
// Types
// =============================================================================

export type SpecType = 'requirements' | 'tests' | 'epics' | 'stories' | 'tasks' | 'defects';

export type EARSPatternType =
  | 'ubiquitous'
  | 'event_driven'
  | 'state_driven'
  | 'optional'
  | 'complex'
  | 'unwanted';

export type QualityDimension =
  | 'unambiguity'
  | 'completeness'
  | 'verifiability'
  | 'consistency'
  | 'necessity'
  | 'singularity'
  | 'feasibility'
  | 'traceability';

export type QualityGrade = 'A' | 'B' | 'C' | 'D' | 'F';

export type FlakinessPattern =
  | 'timing'
  | 'async'
  | 'environment'
  | 'network'
  | 'resource'
  | 'order_dependent'
  | 'random';

export type ODCDefectType =
  | 'function'
  | 'interface'
  | 'checking'
  | 'assignment'
  | 'timing'
  | 'build'
  | 'documentation'
  | 'algorithm';

export type ODCTrigger =
  | 'coverage'
  | 'design_conformance'
  | 'exception_handling'
  | 'simple_path'
  | 'complex_path'
  | 'side_effects'
  | 'rare_situation';

export type CVSSSeverity = 'none' | 'low' | 'medium' | 'high' | 'critical';

export type MoSCoWPriority = 'must' | 'should' | 'could' | 'wont';

// =============================================================================
// Response Types
// =============================================================================

export interface EARSComponent {
  name: string;
  value: string | null;
  confidence: number;
}

export interface EARSAnalysisResponse {
  spec_id: string;
  pattern_type: EARSPatternType;
  confidence: number;
  trigger: string | null;
  precondition: string | null;
  postcondition: string | null;
  system_name: string | null;
  formal_structure: string | null;
  components: Record<string, EARSComponent>;
  suggestions: string[];
  is_well_formed: boolean;
  analyzed_at: string;
}

export interface AnalyticsQualityIssue {
  dimension: QualityDimension;
  severity: 'error' | 'warning' | 'info';
  message: string;
  suggestion: string | null;
  line_reference: string | null;
}

export interface QualityDimensionScore {
  dimension: QualityDimension;
  score: number;
  weight: number;
  issues: string[];
}

export interface QualityScoreResponse {
  spec_id: string;
  dimensions: Record<string, number>;
  dimension_details: QualityDimensionScore[];
  overall_score: number;
  grade: QualityGrade;
  issues: AnalyticsQualityIssue[];
  critical_issues_count: number;
  warning_issues_count: number;
  top_improvement_areas: string[];
  analyzed_at: string;
}

export interface MerkleProofResponse {
  spec_id: string;
  root: string;
  proof: string[];
  leaf_index: number;
  leaf_hash: string;
  verified: boolean;
  verification_path: { direction: string; hash: string }[];
  tree_size: number;
  algorithm: string;
  generated_at: string;
}

export interface ContentAddressResponse {
  spec_id: string;
  content_hash: string;
  content_cid: string;
  version_chain_head: string | null;
  previous_version_hash: string | null;
  version_number: number;
  digital_signature: string | null;
  signature_valid: boolean | null;
  created_at: string;
  last_modified_at: string;
}

export interface VersionChainEntry {
  version_hash: string;
  version_number: number;
  content_hash: string;
  previous_hash: string | null;
  created_at: string;
  created_by: string | null;
  change_summary: string | null;
}

export interface VersionChainResponse {
  spec_id: string;
  chain_head: string;
  chain_length: number;
  entries: VersionChainEntry[];
  chain_valid: boolean;
  broken_links: string[];
  generated_at: string;
}

export interface FlakinessContributingFactor {
  factor: string;
  weight: number;
  evidence: string | null;
}

export interface FlakinessAnalysisResponse {
  spec_id: string;
  probability: number;
  entropy: number;
  confidence_interval: [number, number] | null;
  pattern: FlakinessPattern | null;
  pattern_confidence: number;
  contributing_factors: FlakinessContributingFactor[];
  quarantine_recommended: boolean;
  recommendation_reason: string | null;
  recent_runs: number;
  flaky_runs: number;
  pass_rate: number;
  analyzed_at: string;
}

export interface ODCClassificationResponse {
  spec_id: string;
  defect_type: ODCDefectType;
  trigger: ODCTrigger;
  impact: string;
  confidence: number;
  defect_type_confidence: number;
  trigger_confidence: number;
  impact_confidence: number;
  classification_evidence: Record<string, string[]>;
  likely_injection_phase: string | null;
  suggested_prevention: string[];
  analyzed_at: string;
}

export interface CVSSBreakdown {
  attack_vector: string;
  attack_complexity: string;
  privileges_required: string;
  user_interaction: string;
  scope: string;
  confidentiality_impact: string;
  integrity_impact: string;
  availability_impact: string;
}

export interface CVSSScoreResponse {
  spec_id: string;
  base_score: number;
  severity: CVSSSeverity;
  vector: string;
  breakdown: CVSSBreakdown;
  temporal_score: number | null;
  environmental_score: number | null;
  remediation_level: string | null;
  report_confidence: string | null;
  analyzed_at: string;
}

export interface ImpactedItem {
  item_id: string;
  item_type: string;
  item_title: string;
  impact_type: 'direct' | 'transitive';
  impact_severity: 'high' | 'medium' | 'low';
  distance: number;
}

export interface ImpactAnalysisResponse {
  spec_id: string;
  direct_impacts: ImpactedItem[];
  direct_impact_count: number;
  transitive_impacts: ImpactedItem[];
  transitive_impact_count: number;
  total_affected: number;
  max_propagation_depth: number;
  risk_score: number;
  risk_category: string;
  by_item_type: Record<string, number>;
  by_severity: Record<string, number>;
  review_required: boolean;
  suggested_actions: string[];
  analyzed_at: string;
}

export interface WSJFScore {
  business_value: number;
  time_criticality: number;
  risk_reduction: number;
  job_size: number;
  wsjf_score: number;
}

export interface RICEScore {
  reach: number;
  impact: number;
  confidence: number;
  effort: number;
  rice_score: number;
}

export interface PrioritizationResponse {
  spec_id: string;
  wsjf: WSJFScore | null;
  rice: RICEScore | null;
  moscow_priority: MoSCoWPriority | null;
  moscow_rationale: string | null;
  relative_rank: number | null;
  total_items: number | null;
  calculated_at: string;
}

export interface CoverageGap {
  requirement_id: string;
  requirement_title: string;
  gap_type: 'no_tests' | 'partial_coverage' | 'stale_tests';
  severity: string;
  recommendation: string;
}

export interface CoverageGapAnalysisResponse {
  project_id: string;
  gaps: CoverageGap[];
  total_gaps: number;
  requirements_with_tests: number;
  requirements_without_tests: number;
  coverage_percentage: number;
  critical_gaps: number;
  high_gaps: number;
  medium_gaps: number;
  analyzed_at: string;
}

export interface SuspectLink {
  source_id: string;
  target_id: string;
  link_type: string;
  suspicion_reason: string;
  confidence: number;
}

export interface SuspectLinkAnalysisResponse {
  project_id: string;
  suspect_links: SuspectLink[];
  total_suspect: number;
  total_links: number;
  valid_links: number;
  link_health_percentage: number;
  by_reason: Record<string, number>;
  analyzed_at: string;
}

export interface SimilarItem {
  item_id: string;
  item_title: string;
  item_type: string;
  similarity_score: number;
  similarity_reason: string;
  potential_duplicate: boolean;
}

export interface SimilarityAnalysisResponse {
  spec_id: string;
  similar_items: SimilarItem[];
  total_similar: number;
  potential_duplicates: SimilarItem[];
  duplicate_count: number;
  embedding_model: string;
  similarity_threshold: number;
  analyzed_at: string;
}

// =============================================================================
// Request Types
// =============================================================================

export interface AnalyzeEARSRequest {
  requirement_text?: string;
  include_suggestions?: boolean;
}

export interface AnalyzeQualityRequest {
  dimensions?: QualityDimension[];
  include_suggestions?: boolean;
}

export interface AnalyzeFlakinessRequest {
  recent_runs_count?: number;
  include_historical?: boolean;
}

export interface AnalyzeODCRequest {
  defect_description?: string;
  include_prevention_suggestions?: boolean;
}

export interface AnalyzeCVSSRequest {
  vulnerability_description?: string;
  include_remediation?: boolean;
}

export interface AnalyzeImpactRequest {
  max_depth?: number;
  include_transitive?: boolean;
  item_types?: string[];
}

export interface CalculatePrioritizationRequest {
  calculate_wsjf?: boolean;
  calculate_rice?: boolean;
  suggest_moscow?: boolean;
  business_value?: number;
  time_criticality?: number;
  risk_reduction?: number;
  job_size?: number;
  reach?: number;
  impact?: number;
  confidence?: number;
  effort?: number;
}

export interface AnalyzeCoverageGapsRequest {
  include_stale?: boolean;
  stale_threshold_days?: number;
}

export interface AnalyzeSuspectLinksRequest {
  link_types?: string[];
  confidence_threshold?: number;
}

export interface AnalyzeSimilarityRequest {
  similarity_threshold?: number;
  max_results?: number;
  include_all_types?: boolean;
  item_types?: string[];
}

// =============================================================================
// API Helper Functions
// =============================================================================

async function apiPost<T>(url: string, data?: unknown): Promise<T> {
  const requestInit: RequestInit = {
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  };
  if (data !== undefined) {
    requestInit.body = JSON.stringify(data);
  }
  const res = await fetch(`${API_URL}${url}`, requestInit);
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error: ${res.status} ${errorText}`);
  }
  return res.json();
}

async function apiGet<T>(url: string): Promise<T> {
  const res = await fetch(`${API_URL}${url}`, { headers: getAuthHeaders() });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error: ${res.status} ${errorText}`);
  }
  return res.json();
}

// =============================================================================
// Query Keys
// =============================================================================

export const specAnalyticsKeys = {
  all: ['spec-analytics'] as const,
  contentAddress: (projectId: string, specType: SpecType, specId: string) =>
    [...specAnalyticsKeys.all, 'content-address', projectId, specType, specId] as const,
  coverageGaps: (projectId: string) =>
    [...specAnalyticsKeys.all, 'coverage-gaps', projectId] as const,
  cvss: (projectId: string, specId: string) =>
    [...specAnalyticsKeys.all, 'cvss', projectId, specId] as const,
  ears: (projectId: string, specId: string) =>
    [...specAnalyticsKeys.all, 'ears', projectId, specId] as const,
  flakiness: (projectId: string, specId: string) =>
    [...specAnalyticsKeys.all, 'flakiness', projectId, specId] as const,
  impact: (projectId: string, specType: SpecType, specId: string) =>
    [...specAnalyticsKeys.all, 'impact', projectId, specType, specId] as const,
  merkleProof: (projectId: string, specType: SpecType, specId: string) =>
    [...specAnalyticsKeys.all, 'merkle-proof', projectId, specType, specId] as const,
  odc: (projectId: string, specId: string) =>
    [...specAnalyticsKeys.all, 'odc', projectId, specId] as const,
  prioritization: (projectId: string, specType: SpecType, specId: string) =>
    [...specAnalyticsKeys.all, 'prioritization', projectId, specType, specId] as const,
  quality: (projectId: string, specId: string) =>
    [...specAnalyticsKeys.all, 'quality', projectId, specId] as const,
  similarity: (projectId: string, specType: SpecType, specId: string) =>
    [...specAnalyticsKeys.all, 'similarity', projectId, specType, specId] as const,
  suspectLinks: (projectId: string) =>
    [...specAnalyticsKeys.all, 'suspect-links', projectId] as const,
  versionChain: (projectId: string, specType: SpecType, specId: string) =>
    [...specAnalyticsKeys.all, 'version-chain', projectId, specType, specId] as const,
};

// =============================================================================
// EARS Analysis Hooks
// =============================================================================

export function useEARSAnalysis(projectId: string, specId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request?: AnalyzeEARSRequest) =>
      apiPost<EARSAnalysisResponse>(
        `/api/v1/projects/${projectId}/item-specs/requirements/${specId}/analyze/ears`,
        request,
      ),
    onSuccess: (data) => {
      queryClient.setQueryData(specAnalyticsKeys.ears(projectId, specId), data);
    },
  });
}

// =============================================================================
// Quality Analysis Hooks
// =============================================================================

export function useQualityAnalysis(projectId: string, specId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request?: AnalyzeQualityRequest) =>
      apiPost<QualityScoreResponse>(
        `/api/v1/projects/${projectId}/item-specs/requirements/${specId}/analyze/quality`,
        request,
      ),
    onSuccess: (data) => {
      queryClient.setQueryData(specAnalyticsKeys.quality(projectId, specId), data);
    },
  });
}

// =============================================================================
// Version Chain Hooks
// =============================================================================

export function useVersionChain(
  projectId: string,
  specType: SpecType,
  specId: string,
  options?: { enabled?: boolean; limit?: number },
) {
  return useQuery({
    enabled: options?.enabled ?? true,
    queryFn: async () =>
      apiGet<VersionChainResponse>(
        `/api/v1/projects/${projectId}/item-specs/${specType}/${specId}/version-chain${
          options?.limit ? `?limit=${options.limit}` : ''
        }`,
      ),
    queryKey: specAnalyticsKeys.versionChain(projectId, specType, specId),
  });
}

// =============================================================================
// Merkle Proof Hooks
// =============================================================================

export function useMerkleProof(
  projectId: string,
  specType: SpecType,
  specId: string,
  options?: { enabled?: boolean },
) {
  return useQuery({
    enabled: options?.enabled ?? true,
    queryFn: async () =>
      apiGet<MerkleProofResponse>(
        `/api/v1/projects/${projectId}/item-specs/${specType}/${specId}/merkle-proof`,
      ),
    queryKey: specAnalyticsKeys.merkleProof(projectId, specType, specId),
  });
}

export function useVerifyBaseline(projectId: string, specType: SpecType, specId: string) {
  return useMutation({
    mutationFn: async (baselineRoot: string) =>
      apiPost<MerkleProofResponse>(
        `/api/v1/projects/${projectId}/item-specs/${specType}/${specId}/verify-baseline?baseline_root=${encodeURIComponent(baselineRoot)}`,
      ),
  });
}

// =============================================================================
// Content Address Hooks
// =============================================================================

export function useContentAddress(
  projectId: string,
  specType: SpecType,
  specId: string,
  options?: { enabled?: boolean },
) {
  return useQuery({
    enabled: options?.enabled ?? true,
    queryFn: async () =>
      apiGet<ContentAddressResponse>(
        `/api/v1/projects/${projectId}/item-specs/${specType}/${specId}/content-address`,
      ),
    queryKey: specAnalyticsKeys.contentAddress(projectId, specType, specId),
  });
}

// =============================================================================
// Flakiness Analysis Hooks
// =============================================================================

export function useFlakinessAnalysis(projectId: string, specId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request?: AnalyzeFlakinessRequest) =>
      apiPost<FlakinessAnalysisResponse>(
        `/api/v1/projects/${projectId}/item-specs/tests/${specId}/analyze/flakiness`,
        request,
      ),
    onSuccess: (data) => {
      queryClient.setQueryData(specAnalyticsKeys.flakiness(projectId, specId), data);
    },
  });
}

// =============================================================================
// ODC Classification Hooks
// =============================================================================

export function useODCClassification(projectId: string, specId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request?: AnalyzeODCRequest) =>
      apiPost<ODCClassificationResponse>(
        `/api/v1/projects/${projectId}/item-specs/defects/${specId}/analyze/odc`,
        request,
      ),
    onSuccess: (data) => {
      queryClient.setQueryData(specAnalyticsKeys.odc(projectId, specId), data);
    },
  });
}

// =============================================================================
// CVSS Scoring Hooks
// =============================================================================

export function useCVSSScore(projectId: string, specId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request?: AnalyzeCVSSRequest) =>
      apiPost<CVSSScoreResponse>(
        `/api/v1/projects/${projectId}/item-specs/defects/${specId}/analyze/cvss`,
        request,
      ),
    onSuccess: (data) => {
      queryClient.setQueryData(specAnalyticsKeys.cvss(projectId, specId), data);
    },
  });
}

// =============================================================================
// Impact Analysis Hooks
// =============================================================================

export function useImpactAnalysis(projectId: string, specType: SpecType, specId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request?: AnalyzeImpactRequest) =>
      apiPost<ImpactAnalysisResponse>(
        `/api/v1/projects/${projectId}/item-specs/${specType}/${specId}/analyze/impact`,
        request,
      ),
    onSuccess: (data) => {
      queryClient.setQueryData(specAnalyticsKeys.impact(projectId, specType, specId), data);
    },
  });
}

// =============================================================================
// Prioritization Hooks
// =============================================================================

export function usePrioritization(projectId: string, specType: SpecType, specId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request?: CalculatePrioritizationRequest) =>
      apiPost<PrioritizationResponse>(
        `/api/v1/projects/${projectId}/item-specs/${specType}/${specId}/prioritization`,
        request,
      ),
    onSuccess: (data) => {
      queryClient.setQueryData(specAnalyticsKeys.prioritization(projectId, specType, specId), data);
    },
  });
}

// =============================================================================
// Coverage Gap Analysis Hooks
// =============================================================================

export function useCoverageGapAnalysis(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request?: AnalyzeCoverageGapsRequest) =>
      apiPost<CoverageGapAnalysisResponse>(
        `/api/v1/projects/${projectId}/item-specs/analyze/coverage-gaps`,
        request,
      ),
    onSuccess: (data) => {
      queryClient.setQueryData(specAnalyticsKeys.coverageGaps(projectId), data);
    },
  });
}

// =============================================================================
// Suspect Link Analysis Hooks
// =============================================================================

export function useSuspectLinkAnalysis(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request?: AnalyzeSuspectLinksRequest) =>
      apiPost<SuspectLinkAnalysisResponse>(
        `/api/v1/projects/${projectId}/item-specs/analyze/suspect-links`,
        request,
      ),
    onSuccess: (data) => {
      queryClient.setQueryData(specAnalyticsKeys.suspectLinks(projectId), data);
    },
  });
}

// =============================================================================
// Similarity Analysis Hooks
// =============================================================================

export function useSimilarityAnalysis(projectId: string, specType: SpecType, specId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request?: AnalyzeSimilarityRequest) =>
      apiPost<SimilarityAnalysisResponse>(
        `/api/v1/projects/${projectId}/item-specs/${specType}/${specId}/analyze/similarity`,
        request,
      ),
    onSuccess: (data) => {
      queryClient.setQueryData(specAnalyticsKeys.similarity(projectId, specType, specId), data);
    },
  });
}

// =============================================================================
// Utility Hooks
// =============================================================================

/**
 * Hook to invalidate all analytics caches for a spec
 */
export function useInvalidateSpecAnalytics() {
  const queryClient = useQueryClient();

  return {
    invalidateAll: (projectId: string) => {
      queryClient
        .invalidateQueries({
          queryKey: [...specAnalyticsKeys.all, projectId],
        })
        .catch((error) => {
          logger.error('Failed to invalidate all:', error);
        });
    },
    invalidateContentAddress: (projectId: string, specType: SpecType, specId: string) => {
      queryClient
        .invalidateQueries({
          queryKey: specAnalyticsKeys.contentAddress(projectId, specType, specId),
        })
        .catch((error) => {
          logger.error('Failed to invalidate content address:', error);
        });
    },
    invalidateVersionChain: (projectId: string, specType: SpecType, specId: string) => {
      queryClient
        .invalidateQueries({
          queryKey: specAnalyticsKeys.versionChain(projectId, specType, specId),
        })
        .catch((error) => {
          logger.error('Failed to invalidate version chain:', error);
        });
    },
  };
}

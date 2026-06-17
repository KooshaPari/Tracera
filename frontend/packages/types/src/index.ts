/** Shared traceability types mirroring traceability-core / Tracera API vocabulary. */

export type TraceRelationship =
  | 'satisfies'
  | 'verifies'
  | 'implements'
  | 'derives_from'
  | 'refines'
  | 'conflicts_with'
  | 'duplicates';

export type CoverageState = 'covered' | 'partial' | 'missing' | 'stale' | 'conflict';

export type ArtifactKind =
  | 'requirement'
  | 'design'
  | 'code'
  | 'test'
  | 'evidence'
  | 'risk'
  | 'rationale';

export type RequirementStatus =
  | 'draft'
  | 'proposed'
  | 'approved'
  | 'implemented'
  | 'verified'
  | 'deprecated'
  | 'rejected';

export type TraceLinkType =
  | 'SATISFIES'
  | 'VERIFIES'
  | 'IMPLEMENTS'
  | 'DERIVES_FROM'
  | 'REFINES'
  | 'CONFLICTS_WITH'
  | 'DUPLICATES';

export interface TraceLinkInput {
  source_id: string;
  target_id: string;
  relationship: TraceRelationship;
  confidence?: number;
  updated_at?: string;
}

export interface MatrixCellResponse {
  source_id: string;
  target_id: string;
  coverage: CoverageState;
  links: TraceLinkInput[];
}

export interface CoverageMatrixRequest {
  links?: TraceLinkInput[];
  stale_after_days?: number;
}

export interface CoverageMatrixResponse {
  generated_at: string;
  link_count: number;
  cell_count: number;
  stale_links: number;
  cells: MatrixCellResponse[];
}

export interface ImpactRequest extends CoverageMatrixRequest {
  changed_artifact_ids: string[];
  max_depth?: number;
}

export interface ImpactNodeResponse {
  artifact_id: string;
  depth: number;
  via: TraceRelationship[];
  score: number;
}

export interface ImpactResponse {
  seeds: string[];
  affected: ImpactNodeResponse[];
  total_score: number;
  truncated: boolean;
  max_depth_seen: number;
  conflicts: TraceLinkInput[];
}

export type GovernanceTraceKind =
  | 'implementation'
  | 'test'
  | 'evidence'
  | 'decision';

export type GovernanceGateStatus = 'pass' | 'fail';

export type GovernanceSpecStatus = 'draft' | 'approved' | 'implemented';

export interface GovernanceTrace {
  spec_id: string;
  target_id: string;
  kind: GovernanceTraceKind;
}

export interface GovernanceSpec {
  spec_id: string;
  title: string;
  owner: string;
  acceptance_criteria?: string[];
  evidence_links?: string[];
  status?: GovernanceSpecStatus;
}

export interface GovernanceViolation {
  spec_id: string;
  code: string;
  message: string;
}

export interface GovernanceReport {
  status: GovernanceGateStatus;
  spec_count: number;
  trace_count: number;
  violations: GovernanceViolation[];
}

export interface GovernanceCheckRequest {
  specs?: GovernanceSpec[];
  traces?: GovernanceTrace[];
}

export interface ConfidenceRequest {
  requirement_text: string;
  artifact_text: string;
}

export interface ConfidenceResponse {
  confidence: number;
  rationale: string;
}

export interface EvidenceCreate {
  artifact_id: string;
  kind: string;
  url: string;
  captured_at: string;
  description?: string;
  metadata?: Record<string, unknown>;
}

export interface EvidenceResponse {
  id: string;
  artifact_id: string;
  kind: string;
  url: string;
  captured_at: string;
  description: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

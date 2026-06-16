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

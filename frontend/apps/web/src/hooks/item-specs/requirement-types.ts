import type {
  ConstraintType,
  QualityIssue,
  RequirementType,
  RiskLevel,
  VerificationStatus,
} from './shared-types';

interface RequirementSpec {
  id: string;
  item_id: string;
  requirement_type: RequirementType;
  ears_trigger?: string | undefined;
  ears_precondition?: string | undefined;
  ears_postcondition?: string | undefined;
  constraint_type: ConstraintType;
  constraint_target?: number | undefined;
  constraint_tolerance?: number | undefined;
  constraint_unit?: string | undefined;
  verification_status: VerificationStatus;
  verified_at?: string | undefined;
  verified_by?: string | undefined;
  verification_evidence: Record<string, unknown>;
  formal_spec?: string | undefined;
  invariants: unknown[];
  preconditions: string[];
  postconditions: string[];
  quality_scores: Record<string, number>;
  ambiguity_score?: number | undefined;
  completeness_score?: number | undefined;
  testability_score?: number | undefined;
  overall_quality_score?: number | undefined;
  quality_issues: QualityIssue[];
  volatility_index?: number | undefined;
  change_count: number;
  last_changed_at?: string | undefined;
  change_history: unknown[];
  change_propagation_index?: number | undefined;
  downstream_count: number;
  upstream_count: number;
  impact_assessment: Record<string, unknown>;
  risk_level: RiskLevel;
  risk_factors: string[];
  wsjf_score?: number | undefined;
  business_value?: number | undefined;
  time_criticality?: number | undefined;
  risk_reduction?: number | undefined;
  similar_items: unknown[];
  auto_tags: string[];
  complexity_estimate?: string | undefined;
  source_reference?: string | undefined;
  rationale?: string | undefined;
  stakeholders: string[];
  spec_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface RequirementSpecCreate {
  item_id: string;
  requirement_type: RequirementType;
  ears_trigger?: string | undefined;
  ears_precondition?: string | undefined;
  ears_postcondition?: string | undefined;
  constraint_type: ConstraintType;
  constraint_target?: number | undefined;
  constraint_tolerance?: number | undefined;
  constraint_unit?: string | undefined;
  formal_spec?: string | undefined;
  invariants?: unknown[] | undefined;
  preconditions?: string[] | undefined;
  postconditions?: string[] | undefined;
  risk_level: RiskLevel;
  risk_factors?: string[] | undefined;
  business_value?: number | undefined;
  time_criticality?: number | undefined;
  risk_reduction?: number | undefined;
  stakeholders?: string[] | undefined;
  source_reference?: string | undefined;
  rationale?: string | undefined;
  spec_metadata?: Record<string, unknown> | undefined;
}

interface RequirementSpecUpdate {
  requirement_type?: RequirementType | undefined;
  ears_trigger?: string | undefined;
  ears_precondition?: string | undefined;
  ears_postcondition?: string | undefined;
  constraint_type?: ConstraintType | undefined;
  constraint_target?: number | undefined;
  constraint_tolerance?: number | undefined;
  constraint_unit?: string | undefined;
  formal_spec?: string | undefined;
  invariants?: unknown[] | undefined;
  preconditions?: string[] | undefined;
  postconditions?: string[] | undefined;
  risk_level?: RiskLevel | undefined;
  risk_factors?: string[] | undefined;
  business_value?: number | undefined;
  time_criticality?: number | undefined;
  risk_reduction?: number | undefined;
  stakeholders?: string[] | undefined;
  source_reference?: string | undefined;
  rationale?: string | undefined;
  spec_metadata?: Record<string, unknown> | undefined;
}

export type { RequirementSpec, RequirementSpecCreate, RequirementSpecUpdate };

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
  ears_trigger?: string;
  ears_precondition?: string;
  ears_postcondition?: string;
  constraint_type: ConstraintType;
  constraint_target?: number;
  constraint_tolerance?: number;
  constraint_unit?: string;
  verification_status: VerificationStatus;
  verified_at?: string;
  verified_by?: string;
  verification_evidence: Record<string, unknown>;
  formal_spec?: string;
  invariants: unknown[];
  preconditions: string[];
  postconditions: string[];
  quality_scores: Record<string, number>;
  ambiguity_score?: number;
  completeness_score?: number;
  testability_score?: number;
  overall_quality_score?: number;
  quality_issues: QualityIssue[];
  volatility_index?: number;
  change_count: number;
  last_changed_at?: string;
  change_history: unknown[];
  change_propagation_index?: number;
  downstream_count: number;
  upstream_count: number;
  impact_assessment: Record<string, unknown>;
  risk_level: RiskLevel;
  risk_factors: string[];
  wsjf_score?: number;
  business_value?: number;
  time_criticality?: number;
  risk_reduction?: number;
  similar_items: unknown[];
  auto_tags: string[];
  complexity_estimate?: string;
  source_reference?: string;
  rationale?: string;
  stakeholders: string[];
  spec_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface RequirementSpecCreate {
  item_id: string;
  requirement_type: RequirementType;
  ears_trigger?: string;
  ears_precondition?: string;
  ears_postcondition?: string;
  constraint_type: ConstraintType;
  constraint_target?: number;
  constraint_tolerance?: number;
  constraint_unit?: string;
  formal_spec?: string;
  invariants?: unknown[];
  preconditions?: string[];
  postconditions?: string[];
  risk_level: RiskLevel;
  risk_factors?: string[];
  business_value?: number;
  time_criticality?: number;
  risk_reduction?: number;
  stakeholders?: string[];
  source_reference?: string;
  rationale?: string;
  spec_metadata?: Record<string, unknown>;
}

interface RequirementSpecUpdate {
  requirement_type?: RequirementType;
  ears_trigger?: string;
  ears_precondition?: string;
  ears_postcondition?: string;
  constraint_type?: ConstraintType;
  constraint_target?: number;
  constraint_tolerance?: number;
  constraint_unit?: string;
  formal_spec?: string;
  invariants?: unknown[];
  preconditions?: string[];
  postconditions?: string[];
  risk_level?: RiskLevel;
  risk_factors?: string[];
  business_value?: number;
  time_criticality?: number;
  risk_reduction?: number;
  stakeholders?: string[];
  source_reference?: string;
  rationale?: string;
  spec_metadata?: Record<string, unknown>;
}

export type { RequirementSpec, RequirementSpecCreate, RequirementSpecUpdate };

import type { EpicStatus, RiskLevel } from './shared-types';

interface EpicSpec {
  id: string;
  item_id: string;
  epic_name: string;
  business_value: number;
  target_release?: string;
  status: EpicStatus;
  start_date?: string;
  end_date?: string;
  dependencies: string[];
  child_stories_count: number;
  user_stories: string[];
  objectives: string[];
  success_criteria: string[];
  stakeholders: string[];
  acceptance_criteria: Record<string, unknown>;
  scope_statement?: string;
  out_of_scope?: string[];
  constraints: string[];
  assumptions: string[];
  risks: {
    description: string;
    mitigation: string;
    impact: RiskLevel;
  }[];
  themes: string[];
  metrics: Record<string, number>;
  spec_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface EpicSpecCreate {
  item_id: string;
  epic_name: string;
  business_value: number;
  target_release?: string;
  status: EpicStatus;
  start_date?: string;
  end_date?: string;
  dependencies?: string[];
  objectives?: string[];
  success_criteria?: string[];
  stakeholders?: string[];
  acceptance_criteria?: Record<string, unknown>;
  scope_statement?: string;
  out_of_scope?: string[];
  constraints?: string[];
  assumptions?: string[];
  risks?: {
    description: string;
    mitigation: string;
    impact: RiskLevel;
  }[];
  themes?: string[];
  metrics?: Record<string, number>;
  spec_metadata?: Record<string, unknown>;
}

interface EpicSpecUpdate {
  epic_name?: string;
  business_value?: number;
  target_release?: string;
  status?: EpicStatus;
  start_date?: string;
  end_date?: string;
  dependencies?: string[];
  objectives?: string[];
  success_criteria?: string[];
  stakeholders?: string[];
  acceptance_criteria?: Record<string, unknown>;
  scope_statement?: string;
  out_of_scope?: string[];
  constraints?: string[];
  assumptions?: string[];
  risks?: {
    description: string;
    mitigation: string;
    impact: RiskLevel;
  }[];
  themes?: string[];
  metrics?: Record<string, number>;
  spec_metadata?: Record<string, unknown>;
}

export type { EpicSpec, EpicSpecCreate, EpicSpecUpdate };

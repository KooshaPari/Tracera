import type { DefectSeverity, DefectStatus } from './shared-types';

interface DefectSpec {
  id: string;
  item_id: string;
  title: string;
  description: string;
  severity: DefectSeverity;
  status: DefectStatus;
  discovered_by?: string;
  assigned_to?: string;
  discovered_at?: string;
  resolved_at?: string;
  resolution?: string;
  steps_to_reproduce: string[];
  expected_behavior: string;
  actual_behavior: string;
  affected_components: string[];
  affected_versions?: string[];
  regression_risk?: 'low' | 'medium' | 'high' | 'critical';
  reproducible?: boolean;
  environment?: string;
  root_cause?: string;
  verification_notes?: string;
  attachments?: { type: string; url: string; description?: string }[];
  related_requirements?: string[];
  related_defects?: string[];
  time_to_fix_estimate?: string;
  reported_by?: string;
  tags: string[];
  regressions: string[];
  spec_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

interface DefectSpecCreate {
  item_id: string;
  title: string;
  description: string;
  severity: DefectSeverity;
  status: DefectStatus;
  discovered_by?: string;
  assigned_to?: string;
  discovered_at?: string;
  resolved_at?: string;
  resolution?: string;
  steps_to_reproduce?: string[];
  expected_behavior: string;
  actual_behavior: string;
  affected_components?: string[];
  tags?: string[];
  regressions?: string[];
  spec_metadata?: Record<string, unknown>;
}

interface DefectSpecUpdate {
  title?: string;
  description?: string;
  severity?: DefectSeverity;
  status?: DefectStatus;
  discovered_by?: string;
  assigned_to?: string;
  discovered_at?: string;
  resolved_at?: string;
  resolution?: string;
  steps_to_reproduce?: string[];
  expected_behavior?: string;
  actual_behavior?: string;
  affected_components?: string[];
  tags?: string[];
  regressions?: string[];
  spec_metadata?: Record<string, unknown>;
}

export type { DefectSpec, DefectSpecCreate, DefectSpecUpdate };

import type {
  ImpactLevel,
  Problem,
  ProblemActivity,
  ProblemStatus,
  RCAMethod,
  ResolutionType,
  RootCauseCategory,
} from '@tracertm/types';

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

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && Boolean(value) && !Array.isArray(value);
}

function asRecord(value: unknown): Record<string, unknown> {
  if (isRecord(value)) {
    return value;
  }
  return {};
}

function asArray(value: unknown): unknown[] {
  if (Array.isArray(value)) {
    return value;
  }
  return [];
}

function asString(value: unknown, fallback: string): string {
  if (typeof value === 'string') {
    return value;
  }
  return fallback;
}

function asOptionalString(value: unknown): string | undefined {
  if (typeof value === 'string') {
    return value;
  }
  return undefined;
}

function asNumber(value: unknown, fallback: number): number {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === 'string') {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }
  return fallback;
}

function asOptionalNumber(value: unknown): number | undefined {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  return undefined;
}

function asBoolean(value: unknown, fallback: boolean): boolean {
  if (typeof value === 'boolean') {
    return value;
  }
  if (value === 1) {
    return true;
  }
  if (value === 0) {
    return false;
  }
  return fallback;
}

function asOptionalRecord(value: unknown): Record<string, unknown> | undefined {
  if (isRecord(value)) {
    return value;
  }
  return undefined;
}

function asStringArray(value: unknown): string[] | undefined {
  if (!Array.isArray(value)) {
    return undefined;
  }
  const out: string[] = [];
  for (const entryValue of value) {
    if (typeof entryValue === 'string') {
      out.push(entryValue);
    }
  }
  return out;
}

function asRecordNumberMap(value: unknown): Record<string, number> {
  const rec = asRecord(value);
  const out: Record<string, number> = {};
  for (const [key, entryValue] of Object.entries(rec)) {
    const parsedNumber = asNumber(entryValue, Number.NaN);
    if (Number.isFinite(parsedNumber)) {
      out[key] = parsedNumber;
    }
  }
  return out;
}

function isProblemStatus(value: unknown): value is ProblemStatus {
  return (
    value === 'open' ||
    value === 'in_investigation' ||
    value === 'pending_workaround' ||
    value === 'known_error' ||
    value === 'awaiting_fix' ||
    value === 'closed'
  );
}

function asProblemStatus(value: unknown): ProblemStatus {
  if (isProblemStatus(value)) {
    return value;
  }
  return 'open';
}

function isResolutionType(value: unknown): value is ResolutionType {
  return (
    value === 'permanent_fix' ||
    value === 'workaround_only' ||
    value === 'cannot_reproduce' ||
    value === 'deferred' ||
    value === 'by_design'
  );
}

function asOptionalResolutionType(value: unknown): ResolutionType | undefined {
  if (isResolutionType(value)) {
    return value;
  }
  return undefined;
}

function isRCAMethod(value: unknown): value is RCAMethod {
  return (
    value === 'five_whys' ||
    value === 'fishbone' ||
    value === 'kepner_tregoe' ||
    value === 'fmea' ||
    value === 'pareto' ||
    value === 'other'
  );
}

function asOptionalRCAMethod(value: unknown): RCAMethod | undefined {
  if (isRCAMethod(value)) {
    return value;
  }
  return undefined;
}

function isRootCauseCategory(value: unknown): value is RootCauseCategory {
  return (
    value === 'systematic' ||
    value === 'human' ||
    value === 'environmental' ||
    value === 'process' ||
    value === 'technology'
  );
}

function asOptionalRootCauseCategory(value: unknown): RootCauseCategory | undefined {
  if (isRootCauseCategory(value)) {
    return value;
  }
  return undefined;
}

function isWorkaroundEffectiveness(
  value: unknown,
): value is NonNullable<Problem['workaroundEffectiveness']> {
  return value === 'permanent_fix' || value === 'partial' || value === 'temporary';
}

function asOptionalWorkaroundEffectiveness(
  value: unknown,
): Problem['workaroundEffectiveness'] | undefined {
  if (isWorkaroundEffectiveness(value)) {
    return value;
  }
  return undefined;
}

function toImpactLevel(value: unknown): ImpactLevel {
  if (typeof value === 'string') {
    if (value === 'critical') {
      return 'high';
    }
    if (value === 'high' || value === 'medium' || value === 'low') {
      return value;
    }
  }
  if (typeof value === 'number' && value in IMPACT_LEVEL_BY_NUMBER) {
    const mapped = IMPACT_LEVEL_BY_NUMBER[value];
    if (mapped !== undefined) {
      return mapped;
    }
  }
  return 'medium';
}

function toConfidenceLevel(value: unknown): 'high' | 'medium' | 'low' {
  if (typeof value === 'string' && (value === 'high' || value === 'medium' || value === 'low')) {
    return value;
  }
  if (typeof value === 'number' && value in CONFIDENCE_LEVEL_BY_NUMBER) {
    const mapped = CONFIDENCE_LEVEL_BY_NUMBER[value];
    if (mapped !== undefined) {
      return mapped;
    }
  }
  return 'medium';
}

function transformProblem(data: Record<string, unknown>): Problem {
  return {
    affectedSystems: asStringArray(data['affected_systems']),
    affectedUsersEstimated: asOptionalNumber(data['affected_users_estimated']),
    assignedTeam: asOptionalString(data['assigned_team']),
    assignedTo: asOptionalString(data['assigned_to']),
    businessImpactDescription: asOptionalString(data['business_impact_description']),
    category: asOptionalString(data['category']),
    closedAt: asOptionalString(data['closed_at']),
    closedBy: asOptionalString(data['closed_by']),
    closureNotes: asOptionalString(data['closure_notes']),
    createdAt: asString(data['created_at'], ''),
    description: asOptionalString(data['description']),
    id: asString(data['id'], ''),
    impactLevel: toImpactLevel(data['impact_level']),
    knowledgeArticleId: asOptionalString(data['knowledge_article_id']),
    knownErrorId: asOptionalString(data['known_error_id']),
    metadata: asOptionalRecord(data['metadata']),
    owner: asOptionalString(data['owner']),
    permanentFixAvailable: asBoolean(data['permanent_fix_available'], false),
    permanentFixChangeId: asOptionalString(data['permanent_fix_change_id']),
    permanentFixDescription: asOptionalString(data['permanent_fix_description']),
    permanentFixImplementedAt: asOptionalString(data['permanent_fix_implemented_at']),
    priority: toImpactLevel(data['priority']),
    problemNumber: asString(data['problem_number'], ''),
    projectId: asString(data['project_id'], ''),
    rcaCompletedAt: asOptionalString(data['rca_completed_at']),
    rcaCompletedBy: asOptionalString(data['rca_completed_by']),
    rcaData: asOptionalRecord(data['rca_data']),
    rcaMethod: asOptionalRCAMethod(data['rca_method']),
    rcaNotes: asOptionalString(data['rca_notes']),
    rcaPerformed: asBoolean(data['rca_performed'], false),
    resolutionType: asOptionalResolutionType(data['resolution_type']),
    rootCauseCategory: asOptionalRootCauseCategory(data['root_cause_category']),
    rootCauseConfidence: toConfidenceLevel(data['root_cause_confidence']),
    rootCauseDescription: asOptionalString(data['root_cause_description']),
    rootCauseIdentified: asBoolean(data['root_cause_identified'], false),
    status: asProblemStatus(data['status']),
    subCategory: asOptionalString(data['sub_category']),
    tags: asStringArray(data['tags']),
    targetResolutionDate: asOptionalString(data['target_resolution_date']),
    title: asString(data['title'], ''),
    updatedAt: asString(data['updated_at'], ''),
    urgency: toImpactLevel(data['urgency']),
    version: asNumber(data['version'], 0),
    workaroundAvailable: asBoolean(data['workaround_available'], false),
    workaroundDescription: asOptionalString(data['workaround_description']),
    workaroundEffectiveness: asOptionalWorkaroundEffectiveness(data['workaround_effectiveness']),
  };
}

function decodeProblemActivitiesResponse(data: Record<string, unknown>): {
  problemId: string;
  activities: ProblemActivity[];
} {
  return {
    activities: asArray(data['activities']).map((activityValue: unknown) => {
      const activityRecord = asRecord(activityValue);
      return {
        activityType: asString(activityRecord['activity_type'], ''),
        createdAt: asString(activityRecord['created_at'], ''),
        description: asOptionalString(activityRecord['description']),
        fromValue: asOptionalString(activityRecord['from_value']),
        id: asString(activityRecord['id'], ''),
        metadata: asOptionalRecord(activityRecord['metadata']),
        performedBy: asOptionalString(activityRecord['performed_by']),
        problemId: asString(activityRecord['problem_id'], ''),
        toValue: asOptionalString(activityRecord['to_value']),
      };
    }),
    problemId: asString(data['problem_id'], ''),
  };
}

function decodeProblemStatsResponse(data: Record<string, unknown>): {
  projectId: string;
  byStatus: Record<string, number>;
  byPriority: Record<string, number>;
  total: number;
} {
  return {
    byPriority: asRecordNumberMap(data['by_priority']),
    byStatus: asRecordNumberMap(data['by_status']),
    projectId: asString(data['project_id'], ''),
    total: asNumber(data['total'], 0),
  };
}

export {
  asArray,
  asBoolean,
  asNumber,
  asOptionalNumber,
  asOptionalRecord,
  asOptionalString,
  asRecord,
  asRecordNumberMap,
  asString,
  asStringArray,
  decodeProblemActivitiesResponse,
  decodeProblemStatsResponse,
  transformProblem,
};

# Problem Management Entity Patterns & Implementation Examples

**Document Purpose:** Practical implementation patterns and code examples for problem management systems
**Target Audience:** Software architects and backend developers
**Date:** January 27, 2026

---

## Part 1: TypeScript/JSON Schema Examples

### 1.1 Base Problem Entity (TypeScript)

```typescript
import { UUID, UserRef, TeamRef, Timestamp } from './types';

type ProblemStatus =
  | 'Open'
  | 'In Investigation'
  | 'Pending Workaround'
  | 'Known Error'
  | 'Awaiting Fix'
  | 'Closed';

type ResolutionType =
  | 'Permanent Fix'
  | 'Workaround Only'
  | 'Cannot Reproduce'
  | 'Deferred'
  | 'By Design';

type ImpactLevel = 'Critical' | 'High' | 'Medium' | 'Low';
type Urgency = 'Immediate' | 'High' | 'Medium' | 'Low';

type RCAMethod =
  | '5 Whys'
  | 'Fishbone Diagram'
  | 'Kepner-Tregoe'
  | 'FMEA'
  | 'Pareto Analysis'
  | 'Other';

type RootCauseCategory = 'Systematic' | 'Human' | 'Environmental';

interface Problem {
  // Core Identification
  id: UUID;
  problemNumber: string; // e.g., "P-2024-001"
  title: string;
  description: string;

  // Lifecycle Status
  status: ProblemStatus;
  statusHistory: StatusHistory[];
  resolutionType: ResolutionType | null;

  // Classification
  category: string; // e.g., "Software Bug", "Configuration"
  subCategory: string;
  tags: string[];

  // Impact Assessment
  impactLevel: ImpactLevel;
  affectedSystems: string[];
  affectedUsersEstimated: number;
  businessImpactDescription: string;

  // Urgency & Priority
  urgency: Urgency;
  priority: ImpactLevel;
  priorityJustification: string;
  targetResolutionDate: Date | null;

  // Root Cause Analysis
  rcaPerformed: boolean;
  rcaMethod: RCAMethod | null;
  rcaNotes: string;

  rootCauseIdentified: boolean;
  rootCauseDescription: string | null;
  rootCauseCategory: RootCauseCategory | null;
  rootCauseConfidence: 'High' | 'Medium' | 'Low' | null;
  rcaCompletedDate: Date | null;
  rcaCompletedBy: UserRef | null;

  // Solutions & Workarounds
  workaroundAvailable: boolean;
  workaroundDescription: string | null;
  workaroundEffectiveness: 'Permanent Fix' | 'Partial' | 'Temporary' | null;

  permanentFixAvailable: boolean;
  permanentFixDescription: string | null;
  permanentFixImplementationDate: Date | null;
  permanentFixChangeId: UUID | null;

  // Known Error Integration
  knownErrorId: UUID | null;
  knowledgeArticleId: UUID | null;

  // Relationships
  relatedIncidentIds: UUID[];
  relatedProblemIds: UUID[];
  relatedChangeIds: UUID[];
  relatedTaskIds: UUID[];
  relatedConfigurationItems: ConfigItemReference[];

  // Assignment & Ownership
  assignedTo: UserRef;
  assignedTeam: TeamRef;
  assignedDate: Timestamp;

  // Metadata
  createdBy: UserRef;
  createdDate: Timestamp;
  createdFromIncidentId: UUID | null;

  updatedBy: UserRef;
  updatedDate: Timestamp;

  closedBy: UserRef | null;
  closedDate: Timestamp | null;

  // Audit & Review
  reviewNotes: string | null;
  reviewedBy: UserRef | null;
  reviewDate: Timestamp | null;

  // Custom Fields
  customFields: Record<string, unknown>;
}

interface StatusHistory {
  timestamp: Timestamp;
  fromStatus: ProblemStatus;
  toStatus: ProblemStatus;
  changedBy: UserRef;
  reason: string;
}

interface ConfigItemReference {
  ciId: UUID;
  ciName: string;
  impactType: 'Direct' | 'Indirect';
}
```

### 1.2 RCA-Specific Entities

```typescript
// Fishbone Diagram Structure
interface FishboneDiagram {
  problemStatement: string;
  categories: FishboneCategory[];
  identifiedRootCauses: string[];
  diagramImage: string; // SVG or image URL
  createdDate: Timestamp;
}

interface FishboneCategory {
  categoryName: string; // e.g., "Manpower", "Methods"
  majorCauses: string[];
  rootCauses: string[];
}

// 5 Whys Structure
interface FiveWhysAnalysis {
  problemStatement: string;
  levels: WhyLevel[];
  rootCauseConclusion: string;
  createdDate: Timestamp;
}

interface WhyLevel {
  levelNumber: 1 | 2 | 3 | 4 | 5;
  question: string;
  answer: string;
  identifier: string; // For drilling down
}

// Kepner-Tregoe Analysis Structure
interface KepnerTregoeAnalysis {
  problemStatement: string;
  situationAppraisal: SituationAppraisal;
  problemAnalysis: ProblemAnalysis;
  potentialProblemAnalysis: PotentialProblemAnalysis;
  rootCauseConclusion: string;
  createdDate: Timestamp;
}

interface SituationAppraisal {
  issues: string[];
  prioritizedIssues: string[];
  selectedProblem: string;
}

interface ProblemAnalysis {
  // "Is" statements
  what: string; // What is happening?
  where: string;
  when: string;
  severity: string;

  // "Is Not" statements
  whatIsNot: string; // What is NOT happening?
  whereIsNot: string;
  whenIsNot: string;

  // Distinctions
  distinctions: string[]; // Differences between "is" and "is not"

  // Hypotheses
  possibleCauses: string[];
  mostLikelyCause: string;
}

interface PotentialProblemAnalysis {
  futureProblems: string[];
  probabilityAssessment: ProbabilityItem[];
  mitigationStrategies: string[];
}

interface ProbabilityItem {
  problem: string;
  probability: 'High' | 'Medium' | 'Low';
  impact: 'Critical' | 'High' | 'Medium' | 'Low';
  mitigationAction: string;
}
```

### 1.3 Known Error Entity

```typescript
interface KnownError {
  id: UUID;
  knownErrorNumber: string; // e.g., "KE-2024-001"
  relatedProblemId: UUID;

  // Description
  description: string;
  rootCause: string;
  affectedSystems: string[];

  // Workaround
  workaround: {
    available: boolean;
    description: string;
    effectiveness: 'Permanent Fix' | 'Partial Workaround' | 'Temporary Relief';
    steps: string[];
    estimatedTimeToResolve: number; // minutes
  };

  // Permanent Fix
  permanentFix: {
    available: boolean;
    description: string;
    changeId: UUID | null;
    implementationDate: Date | null;
    automationSupported: boolean;
  };

  // Impact
  affectedUsersCount: number;
  businessImpactDescription: string;

  // Detection
  detectionCriteria: {
    symptoms: string[];
    errorMessages: string[];
    logPatterns: string[];
    monitoringAlerts: string[];
  };

  // Knowledge
  searchKeywords: string[];
  knowledgeArticleId: UUID | null;
  relatedArticles: UUID[];

  // Metadata
  createdDate: Timestamp;
  createdBy: UserRef;
  lastUpdatedDate: Timestamp;
  updatedBy: UserRef;

  // Status
  status: 'Active' | 'Archived' | 'Obsolete';
  deprecationDate: Date | null;
}
```

---

## Part 2: Database Schema Examples (SQL)

### 2.1 Core Problem Table

```sql
CREATE TABLE problems (
  id UUID PRIMARY KEY,
  problem_number VARCHAR(50) UNIQUE NOT NULL,
  title VARCHAR(200) NOT NULL,
  description TEXT NOT NULL,

  -- Status Management
  status VARCHAR(50) NOT NULL DEFAULT 'Open',
  resolution_type VARCHAR(50),

  -- Classification
  category VARCHAR(100),
  sub_category VARCHAR(100),
  tags TEXT[], -- PostgreSQL array

  -- Impact Assessment
  impact_level VARCHAR(20) NOT NULL,
  affected_systems TEXT[],
  affected_users_estimated INTEGER,
  business_impact_description TEXT,

  -- Urgency & Priority
  urgency VARCHAR(20),
  priority VARCHAR(20),
  priority_justification TEXT,
  target_resolution_date TIMESTAMP,

  -- RCA
  rca_performed BOOLEAN DEFAULT FALSE,
  rca_method VARCHAR(50),
  rca_notes TEXT,
  root_cause_identified BOOLEAN DEFAULT FALSE,
  root_cause_description TEXT,
  root_cause_category VARCHAR(50),
  root_cause_confidence VARCHAR(20),
  rca_completed_date TIMESTAMP,
  rca_completed_by UUID,

  -- Solutions
  workaround_available BOOLEAN DEFAULT FALSE,
  workaround_description TEXT,
  workaround_effectiveness VARCHAR(50),
  permanent_fix_available BOOLEAN DEFAULT FALSE,
  permanent_fix_description TEXT,
  permanent_fix_implementation_date TIMESTAMP,
  permanent_fix_change_id UUID,

  -- Known Error Integration
  known_error_id UUID REFERENCES known_errors(id),
  knowledge_article_id UUID,

  -- Assignment
  assigned_to UUID NOT NULL REFERENCES users(id),
  assigned_team UUID NOT NULL REFERENCES teams(id),
  assigned_date TIMESTAMP NOT NULL,

  -- Ownership
  created_by UUID NOT NULL REFERENCES users(id),
  created_date TIMESTAMP NOT NULL DEFAULT NOW(),
  created_from_incident_id UUID,

  updated_by UUID NOT NULL REFERENCES users(id),
  updated_date TIMESTAMP NOT NULL DEFAULT NOW(),

  closed_by UUID REFERENCES users(id),
  closed_date TIMESTAMP,

  -- Review
  review_notes TEXT,
  reviewed_by UUID REFERENCES users(id),
  review_date TIMESTAMP,

  -- Custom Fields
  custom_fields JSONB DEFAULT '{}',

  -- Indexes
  INDEX idx_problem_status (status),
  INDEX idx_problem_priority (priority),
  INDEX idx_problem_assigned_to (assigned_to),
  INDEX idx_problem_created_date (created_date),
  INDEX idx_problem_category (category),
  CONSTRAINT valid_status CHECK (status IN ('Open', 'In Investigation', 'Pending Workaround', 'Known Error', 'Awaiting Fix', 'Closed')),
  CONSTRAINT valid_impact CHECK (impact_level IN ('Critical', 'High', 'Medium', 'Low'))
);
```

### 2.2 Problem Status History Table

```sql
CREATE TABLE problem_status_history (
  id UUID PRIMARY KEY,
  problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  from_status VARCHAR(50) NOT NULL,
  to_status VARCHAR(50) NOT NULL,
  changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
  changed_by UUID NOT NULL REFERENCES users(id),
  reason TEXT,

  INDEX idx_problem_id (problem_id),
  INDEX idx_changed_at (changed_at)
);
```

### 2.3 RCA Details Table

```sql
CREATE TABLE problem_rca (
  id UUID PRIMARY KEY,
  problem_id UUID NOT NULL UNIQUE REFERENCES problems(id) ON DELETE CASCADE,
  rca_method VARCHAR(50) NOT NULL,

  -- Method-specific data stored as JSONB
  -- Allows flexibility for different RCA methods
  rca_data JSONB NOT NULL,

  -- Example structure for rca_data:
  -- For 5 Whys: { levels: [ { number: 1, question: "...", answer: "..." } ] }
  -- For Fishbone: { categories: [ { name: "...", causes: [...] } ] }
  -- For Kepner-Tregoe: { is: "...", isNot: "...", distinctions: [...] }

  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by UUID NOT NULL REFERENCES users(id),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_by UUID NOT NULL REFERENCES users(id),

  INDEX idx_problem_id (problem_id)
);
```

### 2.4 Problem Relationships Table

```sql
CREATE TABLE problem_relationships (
  id UUID PRIMARY KEY,
  source_problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  target_problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  relationship_type VARCHAR(50) NOT NULL, -- 'DuplicateOf', 'RelatedTo', 'CausedBy', 'Triggers'
  description TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),

  UNIQUE(source_problem_id, target_problem_id, relationship_type),
  INDEX idx_source_problem (source_problem_id),
  INDEX idx_target_problem (target_problem_id),
  CONSTRAINT valid_relationship CHECK (relationship_type IN ('DuplicateOf', 'RelatedTo', 'CausedBy', 'Triggers', 'BlockedBy'))
);
```

### 2.5 Known Error Table

```sql
CREATE TABLE known_errors (
  id UUID PRIMARY KEY,
  known_error_number VARCHAR(50) UNIQUE NOT NULL,
  related_problem_id UUID NOT NULL REFERENCES problems(id),

  description TEXT NOT NULL,
  root_cause TEXT NOT NULL,
  affected_systems TEXT[],

  -- Workaround
  workaround_available BOOLEAN DEFAULT FALSE,
  workaround_description TEXT,
  workaround_effectiveness VARCHAR(50),
  workaround_steps TEXT[],
  workaround_estimated_time_minutes INTEGER,

  -- Permanent Fix
  permanent_fix_available BOOLEAN DEFAULT FALSE,
  permanent_fix_description TEXT,
  permanent_fix_change_id UUID,
  permanent_fix_implementation_date TIMESTAMP,
  permanent_fix_automated BOOLEAN DEFAULT FALSE,

  -- Impact
  affected_users_count INTEGER,
  business_impact_description TEXT,

  -- Detection
  detection_criteria JSONB NOT NULL, -- { symptoms: [], errorMessages: [], logPatterns: [] }

  -- Knowledge
  search_keywords TEXT[],
  knowledge_article_id UUID,
  related_article_ids UUID[],

  -- Metadata
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by UUID NOT NULL REFERENCES users(id),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_by UUID NOT NULL REFERENCES users(id),

  status VARCHAR(50) DEFAULT 'Active', -- 'Active', 'Archived', 'Obsolete'
  deprecation_date TIMESTAMP,

  INDEX idx_related_problem (related_problem_id),
  INDEX idx_status (status),
  INDEX idx_created_date (created_at)
);
```

---

## Part 3: API Response Examples

### 3.1 GET /problems/:id (Full Detail Response)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "problemNumber": "P-2024-0042",
  "title": "Database connection pool exhaustion under load",
  "description": "User reports experiencing 502 Bad Gateway errors when system processes large batch operations. Error rate increases with concurrent users.",

  "status": "Known Error",
  "statusHistory": [
    {
      "timestamp": "2024-01-20T09:15:00Z",
      "fromStatus": "Open",
      "toStatus": "In Investigation",
      "changedBy": "user-123",
      "reason": "Assigned to engineering team for RCA"
    },
    {
      "timestamp": "2024-01-22T14:30:00Z",
      "fromStatus": "In Investigation",
      "toStatus": "Known Error",
      "changedBy": "user-456",
      "reason": "Root cause identified, workaround documented"
    }
  ],
  "resolutionType": "Workaround Only",

  "category": "Software Bug",
  "subCategory": "Performance",
  "tags": ["database", "connection-pool", "performance", "batch-processing"],

  "impactLevel": "High",
  "affectedSystems": ["api-server", "batch-processor", "database-service"],
  "affectedUsersEstimated": 250,
  "businessImpactDescription": "Large batch operations fail 50% of the time under normal load, causing significant workflow disruption for enterprise customers",

  "urgency": "High",
  "priority": "High",
  "priorityJustification": "Affects critical batch processing workflow, impacts revenue-generating feature",
  "targetResolutionDate": "2024-02-15",

  "rcaPerformed": true,
  "rcaMethod": "Fishbone Diagram",
  "rcaNotes": "Systematic analysis identified configuration issue: connection pool max_connections set too low (10) for concurrent load patterns",

  "rootCauseIdentified": true,
  "rootCauseDescription": "Database connection pool maximum connections configuration set to 10, insufficient for typical batch processing load of 20-30 concurrent operations",
  "rootCauseCategory": "Systematic",
  "rootCauseConfidence": "High",
  "rcaCompletedDate": "2024-01-22T14:00:00Z",
  "rcaCompletedBy": "user-456",

  "workaroundAvailable": true,
  "workaroundDescription": "Increase max_connections in database configuration file and implement connection pooling middleware on API servers",
  "workaroundEffectiveness": "Partial",

  "permanentFixAvailable": true,
  "permanentFixDescription": "Implement automatic connection pool sizing based on CPU and memory metrics, with upper limit of 100 connections and automatic retry logic",
  "permanentFixImplementationDate": "2024-02-10",
  "permanentFixChangeId": "change-789",

  "knownErrorId": "ke-2024-0015",
  "knowledgeArticleId": "article-234",

  "relatedIncidentIds": [
    "incident-001",
    "incident-002",
    "incident-003"
  ],
  "relatedProblemIds": [],
  "relatedChangeIds": ["change-789"],
  "relatedTaskIds": ["task-567", "task-568"],

  "relatedConfigurationItems": [
    {
      "ciId": "ci-db-prod",
      "ciName": "PostgreSQL Production Database",
      "impactType": "Direct"
    },
    {
      "ciId": "ci-api-servers",
      "ciName": "API Server Cluster",
      "impactType": "Direct"
    }
  ],

  "assignedTo": "user-456",
  "assignedTeam": "team-backend",
  "assignedDate": "2024-01-20T09:30:00Z",

  "createdBy": "user-123",
  "createdDate": "2024-01-20T08:45:00Z",
  "createdFromIncidentId": "incident-001",

  "updatedBy": "user-456",
  "updatedDate": "2024-01-22T14:30:00Z",

  "closedBy": null,
  "closedDate": null,

  "reviewNotes": null,
  "reviewedBy": null,
  "reviewDate": null,

  "customFields": {
    "severityScore": 8,
    "revenueImpactEstimate": "medium",
    "affectedProductArea": "batch-operations"
  }
}
```

### 3.2 GET /problems?status=Open&priority=Critical (List Response)

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "problemNumber": "P-2024-0042",
      "title": "Database connection pool exhaustion under load",
      "status": "Open",
      "priority": "Critical",
      "impactLevel": "Critical",
      "affectedUsersEstimated": 250,
      "assignedTo": "user-456",
      "assignedTeam": "team-backend",
      "rootCauseIdentified": false,
      "createdDate": "2024-01-20T08:45:00Z",
      "daysOpen": 2
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "problemNumber": "P-2024-0043",
      "title": "Authentication service timeout during peak hours",
      "status": "Open",
      "priority": "Critical",
      "impactLevel": "Critical",
      "affectedUsersEstimated": 5000,
      "assignedTo": "user-789",
      "assignedTeam": "team-security",
      "rootCauseIdentified": false,
      "createdDate": "2024-01-21T10:15:00Z",
      "daysOpen": 1
    }
  ],
  "pagination": {
    "total": 14,
    "page": 1,
    "pageSize": 2,
    "totalPages": 7
  }
}
```

### 3.3 Fishbone RCA Response Example

```json
{
  "id": "rca-550e8400",
  "problemId": "550e8400-e29b-41d4-a716-446655440000",
  "method": "Fishbone Diagram",
  "problemStatement": "Database connection pool exhaustion under concurrent load",

  "analysis": {
    "categories": [
      {
        "categoryName": "Methods",
        "majorCauses": [
          "Inefficient connection pooling strategy",
          "No connection pool monitoring"
        ],
        "rootCauses": [
          "Pool max_connections hardcoded to 10",
          "No automatic pool size adjustment",
          "Missing connection reset on timeout"
        ]
      },
      {
        "categoryName": "Machines",
        "majorCauses": [
          "Database server resource constraints"
        ],
        "rootCauses": [
          "Database CPU at 85% during peak load",
          "Memory utilization high (70%)"
        ]
      },
      {
        "categoryName": "Measurement",
        "majorCauses": [
          "Insufficient monitoring and alerting"
        ],
        "rootCauses": [
          "No pool saturation alert",
          "Connection count not tracked in metrics",
          "Alerts only fire after user impact"
        ]
      },
      {
        "categoryName": "Manpower",
        "majorCauses": [
          "Insufficient load testing"
        ],
        "rootCauses": [
          "Load tests only simulated 5 concurrent users",
          "No performance regression testing in CI/CD"
        ]
      }
    ],

    "identifiedRootCauses": [
      "Pool max_connections hardcoded to 10 (too low)",
      "No monitoring of pool saturation",
      "Load testing insufficient for real-world concurrency"
    ]
  },

  "conclusion": "Systematic issue with configuration and monitoring. Max connections setting was never validated against actual concurrent user patterns. Lack of monitoring prevented early detection.",
  "createdDate": "2024-01-22T13:00:00Z"
}
```

---

## Part 4: State Machine Implementation

### 4.1 Problem Status State Machine (TypeScript)

```typescript
type ProblemStatus =
  | 'Open'
  | 'In Investigation'
  | 'Pending Workaround'
  | 'Known Error'
  | 'Awaiting Fix'
  | 'Closed';

interface StateTransition {
  from: ProblemStatus;
  to: ProblemStatus;
  requiredConditions: string[];
  allowedRoles: string[];
}

const VALID_TRANSITIONS: StateTransition[] = [
  {
    from: 'Open',
    to: 'In Investigation',
    requiredConditions: ['assigned_to_team'],
    allowedRoles: ['problem-manager', 'team-lead']
  },
  {
    from: 'In Investigation',
    to: 'Pending Workaround',
    requiredConditions: ['workaround_available', 'workaround_documented'],
    allowedRoles: ['problem-manager', 'engineer']
  },
  {
    from: 'In Investigation',
    to: 'Known Error',
    requiredConditions: ['root_cause_identified', 'rca_completed'],
    allowedRoles: ['problem-manager', 'engineer']
  },
  {
    from: 'Pending Workaround',
    to: 'Known Error',
    requiredConditions: ['root_cause_identified', 'permanent_fix_available'],
    allowedRoles: ['problem-manager', 'engineer']
  },
  {
    from: 'Known Error',
    to: 'Awaiting Fix',
    requiredConditions: ['change_created', 'change_approved'],
    allowedRoles: ['problem-manager', 'change-manager']
  },
  {
    from: 'Awaiting Fix',
    to: 'Closed',
    requiredConditions: ['change_implemented', 'verification_complete'],
    allowedRoles: ['problem-manager', 'team-lead']
  },
  {
    from: 'Known Error',
    to: 'Closed',
    requiredConditions: ['deferred_decision', 'approval'],
    allowedRoles: ['problem-manager']
  },
  {
    from: 'Open',
    to: 'Closed',
    requiredConditions: ['cannot_reproduce', 'approval'],
    allowedRoles: ['problem-manager']
  }
];

class ProblemStatusManager {
  canTransition(
    currentStatus: ProblemStatus,
    targetStatus: ProblemStatus,
    userRole: string,
    problem: Problem
  ): { allowed: boolean; reason?: string } {

    const transition = VALID_TRANSITIONS.find(
      t => t.from === currentStatus && t.to === targetStatus
    );

    if (!transition) {
      return {
        allowed: false,
        reason: `No valid transition from ${currentStatus} to ${targetStatus}`
      };
    }

    if (!transition.allowedRoles.includes(userRole)) {
      return {
        allowed: false,
        reason: `User role '${userRole}' not permitted for this transition`
      };
    }

    // Check required conditions
    const failedConditions = this.checkConditions(problem, transition.requiredConditions);
    if (failedConditions.length > 0) {
      return {
        allowed: false,
        reason: `Missing conditions: ${failedConditions.join(', ')}`
      };
    }

    return { allowed: true };
  }

  private checkConditions(problem: Problem, requiredConditions: string[]): string[] {
    const failed: string[] = [];

    const conditionChecks = {
      'assigned_to_team': () => !!problem.assignedTeam,
      'workaround_available': () => problem.workaroundAvailable,
      'workaround_documented': () => !!problem.workaroundDescription,
      'root_cause_identified': () => problem.rootCauseIdentified,
      'rca_completed': () => problem.rcaPerformed && !!problem.rcaCompletedDate,
      'permanent_fix_available': () => problem.permanentFixAvailable,
      'change_created': () => !!problem.permanentFixChangeId,
      'change_approved': () => this.isChangeApproved(problem.permanentFixChangeId),
      'change_implemented': () => !!problem.permanentFixImplementationDate,
      'verification_complete': () => this.isVerified(problem),
      'deferred_decision': () => problem.resolutionType === 'Deferred',
      'approval': () => !!problem.reviewedBy,
      'cannot_reproduce': () => problem.resolutionType === 'Cannot Reproduce'
    };

    for (const condition of requiredConditions) {
      const checker = conditionChecks[condition];
      if (!checker || !checker()) {
        failed.push(condition);
      }
    }

    return failed;
  }

  private isChangeApproved(changeId: UUID | null): boolean {
    // Implementation to check change approval status
    return true;
  }

  private isVerified(problem: Problem): boolean {
    // Implementation to check if problem is verified as fixed
    return true;
  }
}
```

---

## Part 5: Dashboard Query Examples

### 5.1 Critical Problems Dashboard Query

```sql
SELECT
  p.id,
  p.problem_number,
  p.title,
  p.status,
  p.priority,
  p.impact_level,
  p.affected_users_estimated,
  u.name as assigned_to_name,
  t.name as assigned_team_name,
  EXTRACT(DAY FROM NOW() - p.created_date) as days_open,
  CASE
    WHEN p.target_resolution_date < NOW() THEN 'OVERDUE'
    WHEN p.target_resolution_date < NOW() + INTERVAL '1 day' THEN 'DUE_TODAY'
    ELSE 'ON_TRACK'
  END as sla_status
FROM problems p
LEFT JOIN users u ON p.assigned_to = u.id
LEFT JOIN teams t ON p.assigned_team = t.id
WHERE
  p.status IN ('Open', 'In Investigation')
  AND p.priority IN ('Critical', 'High')
ORDER BY
  CASE WHEN p.priority = 'Critical' THEN 0 ELSE 1 END,
  p.created_date ASC;
```

### 5.2 RCA Completion Status Query

```sql
SELECT
  COUNT(*) as total_problems,
  SUM(CASE WHEN rca_performed = true THEN 1 ELSE 0 END) as rca_completed,
  SUM(CASE WHEN root_cause_identified = true THEN 1 ELSE 0 END) as root_cause_found,
  ROUND(
    100.0 * SUM(CASE WHEN rca_performed = true THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) as rca_completion_percentage,
  ROUND(
    100.0 * SUM(CASE WHEN root_cause_identified = true THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) as root_cause_percentage
FROM problems
WHERE created_date >= NOW() - INTERVAL '30 days'
  AND status != 'Closed';
```

### 5.3 Known Error Distribution Query

```sql
SELECT
  ke.known_error_number,
  ke.description,
  COUNT(DISTINCT p.id) as related_problems_count,
  COUNT(DISTINCT pi.id) as related_incidents_count,
  CASE
    WHEN ke.permanent_fix_available THEN 'Permanent Fix Available'
    WHEN ke.workaround_available THEN 'Workaround Available'
    ELSE 'No Solution'
  END as solution_status,
  ke.affected_users_count,
  ke.status
FROM known_errors ke
LEFT JOIN problems p ON ke.related_problem_id = p.id
LEFT JOIN problem_incidents pi ON p.id = pi.problem_id
GROUP BY ke.id, ke.known_error_number, ke.description, ke.permanent_fix_available, ke.workaround_available, ke.affected_users_count, ke.status
ORDER BY related_incidents_count DESC;
```

---

## Part 6: Validation Rules & Business Logic

### 6.1 Problem Validation Rules

```typescript
interface ValidationRule {
  field: string;
  validate: (problem: Problem) => boolean;
  errorMessage: string;
}

const PROBLEM_VALIDATION_RULES: ValidationRule[] = [
  {
    field: 'title',
    validate: (p) => p.title && p.title.length > 0 && p.title.length <= 200,
    errorMessage: 'Title is required and must be 1-200 characters'
  },
  {
    field: 'description',
    validate: (p) => p.description && p.description.length > 20,
    errorMessage: 'Description is required and must be at least 20 characters'
  },
  {
    field: 'assignedTeam',
    validate: (p) => p.status === 'Open' || !!p.assignedTeam,
    errorMessage: 'Problem must be assigned to a team when status is not Open'
  },
  {
    field: 'rcaMethod',
    validate: (p) => !p.rcaPerformed || !!p.rcaMethod,
    errorMessage: 'RCA method must be specified if RCA was performed'
  },
  {
    field: 'rootCauseIdentified',
    validate: (p) => {
      if (p.status === 'Known Error') {
        return p.rootCauseIdentified && !!p.rootCauseDescription;
      }
      return true;
    },
    errorMessage: 'Known Error problems must have identified root cause with description'
  },
  {
    field: 'permanentFixChangeId',
    validate: (p) => {
      if (p.status === 'Awaiting Fix') {
        return !!p.permanentFixChangeId;
      }
      return true;
    },
    errorMessage: 'Awaiting Fix problems must have associated change ID'
  },
  {
    field: 'knowledgeArticleId',
    validate: (p) => {
      if (p.status === 'Closed' && p.rootCauseIdentified) {
        return !!p.knowledgeArticleId || !!p.knownErrorId;
      }
      return true;
    },
    errorMessage: 'Closed problems with identified root cause must have knowledge article or known error'
  }
];

class ProblemValidator {
  validate(problem: Problem): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    for (const rule of PROBLEM_VALIDATION_RULES) {
      if (!rule.validate(problem)) {
        errors.push(rule.errorMessage);
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }
}
```

---

## Part 7: Key Patterns Summary

### Field Recommendations by Status

```
Status: Open
├─ Must have: title, description, impact_level, urgency, assigned_team
├─ Optional: rca_method, root_cause_description
└─ Workflow: Usually created from incident detection

Status: In Investigation
├─ Must have: assigned_to, assigned_team, rca_method
├─ Should have: preliminary_findings, investigation_plan
└─ Workflow: RCA actively underway

Status: Pending Workaround
├─ Must have: workaround_description, workaround_effectiveness
├─ Recommended: root_cause_identified, target_resolution_date
└─ Workflow: Temporary fix deployed, waiting for permanent solution

Status: Known Error
├─ Must have: root_cause_description, root_cause_identified = true
├─ Must have: known_error_id (linked to KEDB)
├─ Should have: permanent_fix_description OR workaround_description
└─ Workflow: Diagnosed, documented in KEDB

Status: Awaiting Fix
├─ Must have: permanent_fix_change_id, permanent_fix_description
├─ State: Change is being implemented
└─ Workflow: Implementation in progress or pending deployment

Status: Closed
├─ Must have: resolution_type, closed_by, closed_date
├─ If root_cause_identified: knowledge_article_id required
├─ Optional: review_notes, reviewed_by
└─ Workflow: Problem resolved, documented for organizational learning
```

---

**Document Version:** 1.0
**Last Updated:** January 27, 2026
**Status:** Implementation Guide Complete

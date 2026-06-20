# Advanced Epic and User Story Specification Patterns: Comprehensive Research

## Executive Summary

This research synthesizes industry-standard practices for advanced epic and user story specifications across SAFe, Agile, and Lean frameworks. The findings provide structured attribute models and data structures for rich specification objects that support enterprise-scale product development. Key frameworks examined include SAFe (Scaled Agile), Story Mapping (Jeff Patton), INVEST criteria, Behavior-Driven Development (BDD), SPIDR story splitting, and Cost of Delay analysis.

The research identifies:
- **SAFe's WSJF prioritization** with all four components (Business Value, Time Criticality, Risk Reduction, Job Size)
- **Epic lifecycle management** through six Portfolio Kanban stages
- **Story mapping anatomy** with backbone, walking skeleton, and release slice concepts
- **INVEST compliance scoring** with automated checking patterns
- **Acceptance criteria frameworks** spanning Given-When-Then and rule-based approaches
- **Story splitting techniques** through the SPIDR method (Spikes, Paths, Interface, Data, Rules)
- **Definition of Done** with team and organizational hierarchies
- **Business value quantification** including Cost of Delay and CD3 metrics
- **Dependency management** across four relationship types with visualization strategies

---

## 1. SAFe EPIC SPECIFICATION PATTERNS

### 1.1 Epic Hypothesis Statement Structure

**Purpose**: Define the expected value and measurable outcomes of an epic before significant investment.

**Template Structure**:
```
Hypothesis: We believe [target user/market] will [expected behavior/outcome]
because [rationale/business driver].

Success will be measured by [measurable metric], expected to change from
[baseline] to [target] within [timeframe].
```

**Core Attributes**:
- `hypothesis_statement` (string): Primary hypothesis in structured format
- `target_user_or_market` (string): Specific segment or persona
- `expected_outcome` (string): Behavioral or business change expected
- `business_rationale` (string): Why this matters to the organization
- `success_metrics` (array): Measurable indicators of achievement
  - `metric_name` (string): Name of the metric (e.g., "User Engagement Rate")
  - `baseline_value` (number): Current state measurement
  - `target_value` (number): Desired future state
  - `measurement_unit` (string): Unit of measurement
  - `measurement_method` (string): How will this be measured
  - `time_frame` (string): Duration for measurement (e.g., "6 months post-launch")

**Sources**: [Epic - Scaled Agile Framework](https://framework.scaledagile.com/epic), [Writing Better Epics in SAFe](https://www.ivarjacobson.com/publications/blog/scaled-agile-tips/writing-better-epics-safe)

---

### 1.2 SAFe Lean Business Case

**Purpose**: Document financial and strategic justification for epic investment.

**Core Attributes**:
```typescript
interface LeanBusinessCase {
  // Financial dimensions
  estimated_cost: {
    development_effort: number; // story points
    development_cost: number; // currency
    operational_cost: number; // annual)
    infrastructure_cost: number;
  };

  // Value components
  expected_benefits: {
    annual_recurring_revenue: number; // ARR impact
    cost_savings: number; // annual)
    market_expansion_value: number;
    customer_retention_impact: number; // % improvement
    brand_impact: string; // qualitative
  };

  // Timeline and risk
  duration_estimate: {
    exploration_weeks: number;
    analysis_weeks: number;
    implementation_weeks: number;
    total_duration: string;
  };

  // MVP and learning strategy
  mvp_definition: {
    mvp_scope: string; // What's included in MVP
    mvp_hypothesis: string; // What we're testing
    learning_goals: string[]; // What we need to learn
  };

  // Risk assessment
  risks: Array<{
    risk_type: 'technical' | 'market' | 'organizational' | 'financial';
    description: string;
    probability: 'low' | 'medium' | 'high';
    impact: 'low' | 'medium' | 'high';
    mitigation_strategy: string;
  }>;

  // Go/no-go decision criteria
  decision_criteria: {
    roi_threshold: number; // Minimum acceptable ROI %
    payback_period_months: number;
    strategic_alignment_score: number; // 1-10
    go_decision: boolean;
    decision_date: string; // ISO date
  };
}
```

**Key Components**:
- Business value quantification
- Cost estimation with confidence ranges
- Risk assessment with mitigation strategies
- MVP scope definition
- ROI and payback period calculations

**Sources**: [SAFe Lean Business Case](https://www.atlassian.com/software/confluence/templates/safe-lean-business-case), [Artifact: Lean Business Case](https://jazz.net/safe4.6_practices/practice.mgmt.safe.base-ibm/workproducts/lean_business_case_BCBACAD3.html)

---

### 1.3 Epic Funnel and Portfolio Kanban Stages

**Purpose**: Manage epic lifecycle from ideation through completion with WIP limits and governance gates.

**Six-Stage Epic Funnel**:

```typescript
type EpicKanbanStage = 'Funnel' | 'Reviewing' | 'Analyzing' | 'Portfolio Backlog' | 'Implementing' | 'Done';

interface EpicKanbanState {
  // Stage definitions
  stages: {
    funnel: {
      name: 'Funnel (Exploration)',
      wip_limit: null, // Not WIP-limited; intake stage
      purpose: 'Intake for strategic ideas from internal/external sources',
      entry_criteria: ['Strategic relevance identified'],
      exit_criteria: ['Epic Owner assigned', 'Initial hypothesis drafted'],
      typical_duration_days: 5,
    },
    reviewing: {
      name: 'Reviewing',
      wip_limit: number, // Set by portfolio
      purpose: 'Epic Owner refines definition and creates hypothesis statement',
      entry_criteria: ['Passes funnel gate', 'Epic Owner assigned'],
      exit_criteria: ['Hypothesis statement complete', 'Preliminary LBC started'],
      typical_duration_days: 14,
    },
    analyzing: {
      name: 'Analyzing',
      wip_limit: number,
      purpose: 'Complete Lean Business Case and conduct go/no-go analysis',
      entry_criteria: ['Passed reviewing gate'],
      exit_criteria: ['LBC complete', 'Go/no-go decision made'],
      typical_duration_days: 21,
    },
    portfolio_backlog: {
      name: 'Portfolio Backlog (Ready)',
      wip_limit: number,
      purpose: 'Holding state for approved, ready-to-implement epics',
      entry_criteria: ['Go decision made', 'Business case approved'],
      exit_criteria: ['Prioritized for implementation'],
      typical_duration_days: 30,
    },
    implementing: {
      name: 'Implementing',
      wip_limit: number,
      purpose: 'Build MVP and test epic hypothesis through incremental delivery',
      entry_criteria: ['Approved', 'Highest priority', 'ART capacity available'],
      exit_criteria: ['MVP deployed', 'Hypothesis validated/invalidated'],
      typical_duration_days: 60,
    },
    done: {
      name: 'Done',
      wip_limit: null,
      purpose: 'Epic delivered and outcomes achieved',
      entry_criteria: ['Business value realized', 'Success metrics demonstrated'],
      exit_criteria: [],
      typical_duration_days: 0,
    },
  };

  // Metrics and governance
  portfolio_metrics: {
    epics_in_funnel: number;
    epics_reviewing: number;
    epics_analyzing: number;
    epics_ready: number;
    epics_implementing: number;
    average_time_to_implementation_days: number;
    go_no_go_approval_rate: string; // percentage
  };

  // Governance events
  governance: {
    strategic_portfolio_review_frequency: 'quarterly' | 'bi-annual';
    portfolio_sync_frequency: 'monthly' | 'quarterly';
    decision_authority: string; // Portfolio leadership
  };
}
```

**Stage Flow**:
1. **Funnel** → Ideas enter unrestricted
2. **Reviewing** → Epic Owner assigned; hypothesis refined
3. **Analyzing** → Lean Business Case completed; go/no-go decision
4. **Portfolio Backlog** → Approved epics waiting for capacity
5. **Implementing** → Active MVP development and hypothesis testing
6. **Done** → Business value achieved and outcomes measured

**Sources**: [Portfolio Backlog - Scaled Agile Framework](https://framework.scaledagile.com/portfolio-backlog), [SAFe Portfolio Kanban](https://framework.scaledagile.com/portfolio-kanban)

---

### 1.4 WSJF (Weighted Shortest Job First) Calculation

**Purpose**: Prioritize epics and features for maximum economic benefit using quantifiable criteria.

**Formula**:
```
WSJF = Cost of Delay / Job Size

Where:
Cost of Delay = Business Value + Time Criticality + Risk Reduction / Opportunity Enablement
Job Size = Relative effort estimation (Fibonacci: 1, 2, 3, 5, 8, 13, 21)
```

**Complete WSJF Model**:

```typescript
interface WSJFCalculation {
  // Component 1: User/Business Value (1-21 scale)
  business_value: {
    value: number; // 1, 2, 3, 5, 8, 13, 21
    description: string;
    revenue_impact: 'high' | 'medium' | 'low';
    customer_satisfaction_impact: 'high' | 'medium' | 'low';
  };

  // Component 2: Time Criticality (1-21 scale)
  // Impact of delay in delivering value
  time_criticality: {
    value: number; // 1, 2, 3, 5, 8, 13, 21
    description: string;
    delay_impact_per_week: {
      revenue_lost: number; // currency per week
      customer_churn_risk: string; // percentage
      market_window_closure: string; // risk description
    };
    deadline_or_market_window: string; // e.g., "Q4 2026"
  };

  // Component 3: Risk Reduction / Opportunity Enablement (1-21 scale)
  risk_reduction_opportunity_enablement: {
    value: number; // 1, 2, 3, 5, 8, 13, 21
    description: string;
    risks_mitigated: string[]; // Array of risks this addresses
    opportunities_enabled: string[]; // New capabilities unlocked
    strategic_alignment_score: number; // 1-10
  };

  // Cost of Delay aggregate
  cost_of_delay: {
    total: number; // Sum of three components
    formula_breakdown: string; // For documentation
    priority_tier: 'critical' | 'high' | 'medium' | 'low';
  };

  // Component 4: Job Size / Duration (1-21 scale, Fibonacci)
  job_size: {
    value: number; // 1, 2, 3, 5, 8, 13, 21
    estimated_story_points: number;
    estimated_duration_sprints: number;
    confidence_level: 'high' | 'medium' | 'low'; // Based on research done
  };

  // Final WSJF Score
  wsjf_score: {
    value: number; // Decimal: Cost of Delay / Job Size
    ranking_position: number; // Where in priority order
    percentile: number; // 0-100 compared to other items
  };

  // Contextual factors
  context: {
    dependencies_blocking: string[]; // Other epics that must finish first
    dependencies_enabler_for: string[]; // What this enables
    team_capacity_fit: 'high' | 'medium' | 'low';
    technical_feasibility: 'proven' | 'achievable' | 'research_needed';
    organizational_readiness: 'ready' | 'needs_preparation' | 'not_ready';
  };

  // Calculation metadata
  metadata: {
    calculated_date: string;
    calculated_by: string;
    review_date: string;
    next_recalculation_date: string;
  };
}
```

**WSJF Prioritization Rules**:
- Higher WSJF scores indicate higher priority
- Tied scores are broken by business value
- Recalculate quarterly or when context changes
- Use Fibonacci scale (1, 2, 3, 5, 8, 13, 21) for consistency
- All components scored on same scale for fair comparison

**Sources**: [Extended Guidance - WSJF - Scaled Agile Framework](https://framework.scaledagile.com/wsjf), [WSJF Definition and Overview](https://www.productplan.com/glossary/weighted-shortest-job-first/)

---

## 2. STORY MAPPING PATTERNS

### 2.1 Story Map Anatomy

**Purpose**: Visualize complete product story horizontally (user journey) and vertically (priority/detail).

**Core Components**:

```typescript
interface StoryMap {
  // The backbone: high-level activities user must accomplish
  backbone: {
    activities: Array<{
      sequence: number;
      activity_name: string; // e.g., "Authenticate", "Browse Products", "Checkout"
      user_goal: string; // What user wants to accomplish
      business_value: string; // Why we support this
      estimated_sprints: number;
    }>;
    description: string; // Overall user workflow narrative
  };

  // Ribs: specific user stories supporting each backbone activity
  // Organized vertically by priority/importance
  ribs: Array<{
    activity_id: string; // Links to backbone activity
    priority_level: 1 | 2 | 3 | 4; // 1=critical for walking skeleton
    stories: Array<{
      story_id: string;
      title: string;
      user_persona: string;
      acceptance_criteria: string[];
      estimated_points: number;
      release_slice: number; // Which release includes this
    }>;
    description: string; // How these stories support the activity
  }>;

  // Walking skeleton: minimum functional story set
  walking_skeleton: {
    definition: string; // What constitutes end-to-end functionality
    included_activities: string[]; // Backbone activities included
    included_stories: string[]; // Story IDs in skeleton
    estimated_duration_sprints: number;
    business_value: string;
  };

  // Release slices: horizontal cuts through map for incremental delivery
  release_slices: Array<{
    release_number: number;
    release_name: string; // e.g., "MVP", "v1.0", "v1.1"
    target_date: string;
    included_stories: string[];
    backbone_coverage: string[]; // Activities included
    estimated_sprints: number;
    business_objectives: string[];
  }>;

  // Metadata
  metadata: {
    product_name: string;
    created_date: string;
    last_updated: string;
    created_by: string;
    next_refinement_date: string;
    stakeholders: string[];
  };
}
```

**Key Concepts**:

1. **Backbone**: High-level workflow sequence (activities, not stories)
   - Cannot be prioritized (all are required)
   - Represents complete user journey
   - Typically 5-8 major activities
   - Example: [Authenticate → Browse → Select → Review → Checkout → Confirm]

2. **Ribs**: User stories supporting each activity
   - Vertically arranged by priority/value
   - Can be prioritized independently
   - Multiple stories per activity
   - Include both happy path and variations

3. **Walking Skeleton**: Minimum viable product
   - Includes one story from each backbone activity
   - Provides end-to-end functionality
   - Typically spans 2-4 sprints
   - Validates architectural assumptions

4. **Release Slices**: Horizontal cuts through the map
   - Each slice represents a potentially shippable increment
   - Preserves user value at each release boundary
   - Supports iterative delivery strategy

**Sources**: [Story Map Concepts](https://www.jpattonassociates.com/wp-content/uploads/2015/03/story_mapping.pdf), [User Story Mapping – The Complete Guide](https://www.avion.io/what-is-user-story-mapping/)

---

## 3. INVEST CRITERIA DEEP DIVE

### 3.1 INVEST Criteria Definition and Scoring

**Purpose**: Ensure user stories are well-formed, estimable, and actionable.

**INVEST Acronym**:

```typescript
interface INVESTCriteria {
  // I: Independent
  independent: {
    definition: 'Stories should be independent from other stories; minimal dependencies',
    assessment: {
      score: 1 | 2 | 3 | 4 | 5, // 1=not independent, 5=fully independent
      dependencies_identified: number,
      description: string,
      evidence: string[],
    },
    anti_patterns: [
      'Story requires another story to be completed first',
      'Story shares significant technical complexity with others',
      'Story requires same specialist/component as multiple others',
    ],
  },

  // N: Negotiable
  negotiable: {
    definition: 'Story details should be negotiable; not a fixed contract',
    assessment: {
      score: 1 | 2 | 3 | 4 | 5,
      flexibility_level: 'high' | 'medium' | 'low',
      description: string,
      evidence: string[],
    },
    anti_patterns: [
      'Story written as detailed specification with no room for discussion',
      'Acceptance criteria locked before team discussion',
      'Technical implementation prescribed in user story',
    ],
  },

  // V: Valuable
  valuable: {
    definition: 'Story must deliver clear business or user value',
    assessment: {
      score: 1 | 2 | 3 | 4 | 5,
      value_articulation: string,
      persona_benefit: string,
      business_impact: 'high' | 'medium' | 'low',
      evidence: string[],
    },
    anti_patterns: [
      'Story is purely technical with no user/business benefit',
      'Story value unclear or cannot be articulated',
      'Story is about refactoring that doesn\'t enable new features',
    ],
  },

  // E: Estimable
  estimable: {
    definition: 'Team must be able to estimate the size/complexity',
    assessment: {
      score: 1 | 2 | 3 | 4 | 5,
      estimation_confidence: 'high' | 'medium' | 'low',
      story_points_assigned: number,
      estimation_history: string,
      evidence: string[],
    },
    anti_patterns: [
      'Story too vague; team cannot estimate',
      'Story requires significant research before estimation',
      'Story has unknowns: "unknown unknowns"',
      'Story mixes multiple unknowns',
    ],
  },

  // S: Small
  small: {
    definition: 'Story must be completable within one sprint',
    assessment: {
      score: 1 | 2 | 3 | 4 | 5,
      estimated_sprint_coverage: number, // 0-1 (fraction of sprint)
      description: string,
      evidence: string[],
    },
    anti_patterns: [
      'Story spans more than 2 sprints (13+ story points)',
      'Story requires multiple team members full-time',
      'Story has too many acceptance criteria (>8)',
      'Story would benefit from splitting further',
    ],
  },

  // T: Testable
  testable: {
    definition: 'Story must have clear, measurable acceptance criteria',
    assessment: {
      score: 1 | 2 | 3 | 4 | 5,
      acceptance_criteria_count: number,
      automated_test_potential: 'high' | 'medium' | 'low',
      description: string,
      evidence: string[],
    },
    anti_patterns: [
      'Acceptance criteria use vague language: "never", "always", "easy"',
      'Story says "improve performance" without measurable target',
      'No way to definitively determine if story is done',
      'Criteria requires subjective judgment (e.g., "looks good")',
    ],
  };

  // Summary scoring
  summary: {
    overall_invest_score: number, // 0-30 (6 criteria × 5 points)
    compliance_level: 'excellent' | 'good' | 'fair' | 'poor',
    recommendation: 'ready_for_sprint' | 'refine_first' | 'split_required' | 'reject',
    areas_for_improvement: string[],
    improvement_actions: Array<{
      criterion: string,
      action: string,
      owner: string,
      due_date: string,
    }>,
  };
}
```

### 3.2 INVEST Scoring Rules

| Criterion | Score 5 | Score 3 | Score 1 |
|-----------|---------|---------|---------|
| **Independent** | No dependencies on other stories | Minimal dependencies, mitigatable | Blocked by multiple stories |
| **Negotiable** | Team can discuss and adjust details | Some constraints on implementation | Specification locked, no negotiation |
| **Valuable** | Clear user/business value articulated | Value somewhat clear but indirect | No apparent value or purely technical |
| **Estimable** | Team confident in estimate (high confidence) | Team somewhat uncertain (medium confidence) | Team cannot estimate (unknowns) |
| **Small** | Fits comfortably in sprint (≤5 points) | Moderate size (5-8 points) | Too large (>13 points, >1 sprint) |
| **Testable** | All criteria measurable, automatable | Most criteria clear, some judgment needed | Vague criteria, subjective judgment required |

**Passing INVEST Threshold**:
- Minimum 18/30 points (60%) for backlog inclusion
- Minimum 24/30 points (80%) for sprint commitment

**Sources**: [INVEST Criteria - Agile Alliance](https://agilealliance.org/glossary/invest/), [Creating The Perfect User Story With INVEST Criteria](https://scrum-master.org/en/creating-the-perfect-user-story-with-invest-criteria/)

### 3.3 Automated INVEST Checking

**Implementation in Tools**:

```typescript
interface AutomatedINVESTCheck {
  // Jira/Azure DevOps custom fields
  tools: {
    jira: {
      field_mappings: {
        'dependent_stories': string[], // Link types
        'flexibility_score': number,
        'user_value_statement': string,
        'estimation_confidence': string,
        'split_potential': string,
        'acceptance_criteria_formatted': string[],
      },
      automation_rules: [
        {
          rule: 'Flag stories with >8 acceptance criteria',
          action: 'Alert: Consider splitting',
        },
        {
          rule: 'Flag stories without value statement',
          action: 'Block: Cannot move to Ready',
        },
        {
          rule: 'Detect dependency chains >2 deep',
          action: 'Alert: Schedule dependency resolution',
        },
      ],
    },
    azure_devops: {
      process_template: {
        mandatory_fields: [
          'User Persona',
          'Value Statement',
          'Acceptance Criteria (formatted)',
          'Story Points (estimated)',
          'Dependencies (linked)',
        ],
        validation_rules: {
          story_points_required: true,
          min_acceptance_criteria: 1,
          max_acceptance_criteria: 8,
          requires_persona: true,
          requires_value_statement: true,
        },
      },
    },
  },

  // Dashboard metrics for INVEST compliance
  dashboard: {
    team_invest_score: number, // Average across all backlog items
    stories_at_risk: {
      not_independent: string[],
      not_estimable: string[],
      too_large: string[],
      not_testable: string[],
    },
    trend_metrics: {
      invest_compliance_trend: 'improving' | 'stable' | 'declining',
      failed_stories_reopened_rate: number, // % of sprint stories returned
      velocity_stability: number, // Standard deviation
    },
  };

  // Pre-sprint quality gates
  sprint_readiness_gate: {
    minimum_invest_score_required: number, // e.g., 24/30
    maximum_story_size_points: number, // e.g., 13
    maximum_stories_with_dependencies: number,
    acceptance_criteria_minimum: number,
    check_before_sprint_planning: true,
  };
}
```

---

## 4. ACCEPTANCE CRITERIA PATTERNS

### 4.1 Given-When-Then (Behavior-Driven Development)

**Purpose**: Define testable, automatable acceptance criteria aligned with business behavior.

**Structure**:

```typescript
interface GivenWhenThenCriteria {
  // Each criterion is a complete scenario
  scenarios: Array<{
    scenario_name: string, // e.g., "User successfully logs in with valid credentials"
    given: {
      context: string[], // Pre-conditions / initial state
      // Examples:
      // "User is on the login page"
      // "User has valid credentials (email: test@example.com, password: correct)"
      // "Session timeout is set to 30 minutes"
    },
    when: {
      action: string[], // Action or event that triggers behavior
      // Examples:
      // "User enters their email address"
      // "User enters their password"
      // "User clicks the Login button"
    },
    then: {
      expected_outcome: string[], // Assertions / verifiable results
      // Examples:
      // "User is logged in"
      // "User's dashboard is displayed"
      // "User sees welcome message with their first name"
      // "Session token is valid and stored securely"
    },
    scenario_type: 'happy_path' | 'alternative_flow' | 'error_case' | 'edge_case',
  }>;

  // Data-driven testing with Scenario Outlines
  scenario_outlines: Array<{
    scenario_template_name: string,
    given_template: string, // With placeholders: "<variable>"
    when_template: string,
    then_template: string,
    examples: Array<{
      example_set_name: string,
      variables: Record<string, any>,
      expected_result: 'pass' | 'fail' | 'conditional',
    }>,
  }>;

  // Quality metrics
  coverage: {
    happy_path_scenarios: number,
    alternative_flow_scenarios: number,
    error_case_scenarios: number,
    edge_case_scenarios: number,
    total_scenarios: number,
    automation_ready_percentage: number,
  };
}
```

**Example GWT Scenario**:
```gherkin
Scenario: User successfully logs in with valid credentials
  Given User is on the login page
    And User has valid credentials (email: user@example.com)
  When User enters their email address
    And User enters their password
    And User clicks the Login button
  Then User is redirected to the dashboard
    And User sees "Welcome, John" message
    And Session token is stored securely

Scenario: User attempts login with invalid password
  Given User is on the login page
    And User has registered an account
  When User enters valid email
    And User enters invalid password
    And User clicks the Login button
  Then User sees error message "Invalid credentials"
    And User remains on login page
    And Account is not locked (first attempt)
```

**Automation Benefits**:
- Scenarios map directly to test cases
- Can use tools like Cucumber, SpecFlow, Behave
- Living documentation: acceptance criteria = test cases
- Non-technical stakeholders can read and validate

**Sources**: [Given-When-Then Acceptance Criteria: Guide](https://www.parallelhq.com/blog/given-when-then-acceptance-criteria), [Martin Fowler's Given When Then](https://martinfowler.com/bliki/GivenWhenThen.html)

### 4.2 Rule-Based Acceptance Criteria

**Purpose**: Specify business rules and policies that must be enforced.

**Structure**:

```typescript
interface RuleBasedCriteria {
  acceptance_criteria: Array<{
    criterion_name: string,
    rule_type: 'validation' | 'calculation' | 'condition' | 'permission' | 'workflow_rule',

    // Business rule definition
    rule: {
      if_condition: string,
      then_action: string,
      else_action?: string,
      exceptions?: string[],
    },

    // Test scenarios for the rule
    test_cases: Array<{
      test_name: string,
      input_data: Record<string, any>,
      expected_output: any,
      rule_branch: 'then' | 'else' | 'exception',
    }>,

    // Business context
    business_context: {
      business_rule_id: string,
      regulatory_requirement?: string,
      risk_level: 'critical' | 'high' | 'medium' | 'low',
    },
  }>;
}
```

**Example Rule-Based Criteria**:
```
Criterion 1: Discount Eligibility Rule
IF customer_order_total > 100 AND customer_account_age > 30_days
THEN apply_10_percent_discount
ELSE apply_no_discount
EXCEPTIONS: Black Friday (apply 20%), clearance_items (no discount allowed)

Test Cases:
- Input: order=$150, account_age=60 days → Output: 10% discount
- Input: order=$50, account_age=60 days → Output: no discount
- Input: order=$150, account_age=10 days → Output: no discount
- Input: order=$150, clearance_items=true → Output: no discount
```

### 4.3 Scenario Outline for Data-Driven Testing

**Purpose**: Test same logic with multiple data sets without rewriting scenarios.

**Structure**:

```gherkin
Scenario Outline: Calculate shipping cost based on weight and destination
  Given A customer in <destination>
    And Order weight is <weight> kg
  When Calculating shipping cost
  Then Shipping cost should be <cost>
    And Estimated delivery is <days> days

Examples:
  | destination | weight | cost | days |
  | Local       | 1      | $5   | 1    |
  | Local       | 5      | $15  | 1    |
  | National    | 1      | $10  | 3    |
  | National    | 5      | $25  | 3    |
  | International| 1      | $20  | 7    |
  | International| 5      | $50  | 10   |
```

**Benefits**:
- Reduces scenario duplication
- Makes data patterns visible
- Easier to identify boundary conditions
- Supports parameterized test automation

---

## 5. STORY SPLITTING PATTERNS

### 5.1 SPIDR Method

**Purpose**: Identify five systematic ways to decompose large user stories into smaller, estimable increments.

**The Five SPIDR Techniques**:

```typescript
interface SPIDRSplitting {
  method_name: 'SPIDR',
  techniques: {

    // S: Spikes (Research/Learning)
    spikes: {
      definition: 'Research activity to reduce uncertainty; produce knowledge, not features',
      when_to_use: [
        'Unknown technology/approach',
        'Architectural uncertainty',
        'Performance/scalability questions',
        'Third-party integration unknowns',
      ],
      example: {
        original_story: 'Build notification system with push notifications',
        spike: 'Research push notification providers and select best fit',
        implementation_story: 'Integrate selected push notification service',
      },
      characteristics: {
        produces_knowledge: true,
        produces_feature: false,
        typical_duration: '1 sprint',
        acceptance_criteria: ['Research completed', 'Decision documented', 'Prototype (if needed)'],
      },
    },

    // P: Paths (Happy Path vs Variations)
    paths: {
      definition: 'Split happy path from alternative flows and error cases',
      when_to_use: [
        'Multiple user flows in one story',
        'Normal case vs edge cases',
        'Happy path vs error handling',
        'Different user types same action',
      ],
      example: {
        original_story: 'User can search products by name, category, price range, or rating',
        path_1: 'User can search products by name (happy path)',
        path_2: 'User can filter by category (alternative path)',
        path_3: 'User can filter by price range (alternative path)',
        path_4: 'User sees error when search returns no results (error case)',
      },
      characteristics: {
        separate_happy_path: true,
        handle_variations: 'alternative_stories',
        typical_split_pattern: '1 happy path + 3-4 alternative/error cases',
      },
    },

    // I: Interface (Device/UI Variations)
    interface: {
      definition: 'Split by different interfaces: devices, browsers, platforms',
      when_to_use: [
        'Desktop vs mobile UI',
        'iOS vs Android implementation',
        'API vs web interface',
        'Different device sizes (tablet, phone)',
      ],
      example: {
        original_story: 'User can view their profile on any device',
        story_1: 'User can view profile on desktop (responsive design)',
        story_2: 'User can view profile on mobile app (iOS)',
        story_3: 'User can view profile on mobile app (Android)',
      },
      characteristics: {
        split_by_platform: true,
        shared_backend_logic: true,
        independent_ui_stories: true,
      },
    },

    // D: Data (Data Type/Range Variations)
    data: {
      definition: 'Split by data scope, range, or complexity',
      when_to_use: [
        'Different data types (text, images, video)',
        'Data volume differences (10 items vs 10,000)',
        'International considerations (currencies, languages)',
        'Data validation complexity',
      ],
      example: {
        original_story: 'Users can upload various file types to their profile',
        story_1: 'User can upload profile photo (image only, <5MB)',
        story_2: 'User can upload documents (PDF, Word, <10MB)',
        story_3: 'User can upload video (mp4, <100MB)',
      },
      characteristics: {
        varies_by_data_type: true,
        varies_by_data_volume: true,
        varies_by_data_scope: true,
      },
    },

    // R: Rules (Business Rule Variations)
    rules: {
      definition: 'Split complex business rules into simpler rule sets',
      when_to_use: [
        'Multiple business rules in one story',
        'Conditional logic (if-then-else)',
        'Role-based access control',
        'Tiered functionality by customer type',
      ],
      example: {
        original_story: 'Apply appropriate discount based on customer type and order value',
        rule_1: 'New customers: no discount',
        rule_2: 'Standard customers: 5% discount on orders >$100',
        rule_3: 'VIP customers: 10% discount on all orders',
        rule_4: 'Bulk orders: additional 5% if quantity >100 items',
      },
      characteristics: {
        separate_business_rules: true,
        can_implement_incrementally: true,
        typical_count: '3-5 rule sets per story',
      },
    },
  };

  // Guidelines
  guidelines: {
    principle: 'Use SPIDR to identify 5 primary splitting vectors',
    focus: 'Each sub-story should be independent, small, and valuable',
    warning: 'Don\'t create 30+ ways; SPIDR covers the useful vectors',
    team_discussion: 'Discuss which splitting method applies; may use multiple methods',
  };
}
```

### 5.2 Story Splitting Decision Framework

**When to Split**:
- Story > 8 story points (high probability)
- Story requires multiple disciplines (backend, frontend, QA)
- Story has multiple independent acceptance criteria
- Story spans multiple user workflows
- Story has significant unknowns (requires spike first)

**When NOT to Split**:
- Story represents atomic business value
- Splitting creates artificial dependencies
- Splitting increases team coordination overhead

**Sources**: [SPIDR: Five Simple Ways to Split User Stories](https://www.mountaingoatsoftware.com/blog/five-simple-but-powerful-ways-to-split-user-stories), [SPIDR Video](https://www.mountaingoatsoftware.com/exclusive/spidr-video)

---

## 6. EPIC DECOMPOSITION HIERARCHY

### 6.1 Feature → Story → Task Hierarchy

**Purpose**: Organize work from strategic capability to actionable tasks in a scalable structure.

```typescript
interface EpicDecompositionHierarchy {
  // Level 1: Epic (Strategic Initiative)
  epic: {
    id: string,
    name: string, // e.g., "Mobile Commerce Platform"
    description: string,
    strategic_goal: string,
    estimated_duration_quarters: number,
    business_value_area: string,
    epic_owner: string,
    portfolio_status: EpicKanbanStage,
    hypothesis_statement: string,
    success_metrics: Array<{
      metric: string,
      baseline: number,
      target: number,
    }>,
  },

  // Level 2: Feature (Business Capability)
  features: Array<{
    id: string,
    parent_epic_id: string,
    name: string, // e.g., "User Authentication"
    description: string,
    user_value: string,
    estimated_story_points: number,
    estimated_sprints: number,
    feature_owner: string,
    status: 'backlog' | 'ready' | 'in_progress' | 'done',
    capability_area: string, // e.g., "Security", "Transactions"
  }>,

  // Level 3: User Story (User-Centric Requirement)
  user_stories: Array<{
    id: string,
    parent_feature_id: string,
    title: string, // e.g., "User can sign up with email"
    format: 'As a <user_type>, I want <action>, so that <benefit>',

    // Story details
    user_persona: string,
    action: string,
    business_benefit: string,

    // Scope
    acceptance_criteria: string[],
    out_of_scope: string[],

    // Estimation
    story_points: number,
    estimated_hours?: number, // Sometimes tracked additionally

    // Status and tracking
    status: 'backlog' | 'ready' | 'in_progress' | 'in_review' | 'done',
    assigned_to?: string,
    sprint_assigned?: string,

    // Dependencies
    depends_on: string[], // Other story IDs
    blocks: string[], // Which stories depend on this

    // Test coverage
    test_cases: string[],
    automation_status: 'not_started' | 'in_progress' | 'automated' | 'not_automatable',
  }>,

  // Level 4: Task/Subtask (Implementation Detail)
  tasks: Array<{
    id: string,
    parent_story_id: string,
    title: string, // e.g., "Create login endpoint"
    description: string,

    // Task properties
    task_type: 'development' | 'testing' | 'design' | 'documentation' | 'devops',
    assigned_to: string,
    estimated_hours: number,

    // Tracking
    status: 'todo' | 'in_progress' | 'in_review' | 'done',
    time_logged_hours: number,
    completion_percentage: number,

    // Quality
    code_review_required: boolean,
    test_coverage_target: number, // percentage
  }>,

  // Hierarchy views
  hierarchy_views: {

    // Waterfall view: Epic → Features → Stories → Tasks
    decomposition_tree: {
      root: Epic,
      level_1_features: Feature[],
      level_2_stories: UserStory[],
      level_3_tasks: Task[],
    },

    // Value flow view: How value flows from strategy to implementation
    value_chain: {
      strategic_goal: string,
      business_capabilities_enabled: string[],
      user_value_delivered: string[],
      implementation_tasks: number,
    },

    // Timeline view: Effort distribution across hierarchy
    timeline_distribution: {
      epic_duration_quarters: number,
      feature_duration_avg_sprints: number,
      story_duration_avg_days: number,
      task_duration_avg_hours: number,
    },
  };

  // Metrics and validation
  metrics: {
    total_features_from_epic: number,
    total_stories_from_epic: number,
    total_tasks_from_epic: number,
    total_story_points: number,
    average_story_size: number,
    dependency_chain_depth: number, // Risk indicator: >3 is warning

    // Validation rules
    validation: {
      check_feature_coverage: {
        rule: 'All features required to satisfy epic hypothesis',
        status: 'pass' | 'fail',
      },
      check_story_completeness: {
        rule: 'All features decomposed to stories',
        status: 'pass' | 'fail',
      },
      check_task_granularity: {
        rule: 'Tasks estimated in hours, not days',
        status: 'pass' | 'fail',
      },
    },
  };
}
```

### 6.2 Capability Mapping Approach

**Purpose**: Align decomposition with business capabilities rather than just functional organization.

```typescript
interface CapabilityMapping {
  // Business capabilities the epic delivers
  capabilities: Array<{
    capability_name: string, // e.g., "Payments Processing"
    business_value: string,
    current_maturity_level: 1 | 2 | 3 | 4 | 5, // 1=manual/absent, 5=optimized
    target_maturity_level: 1 | 2 | 3 | 4 | 5,
    improvement_story_points: number,

    // Features supporting this capability
    features_delivering_this: string[],
  }>,

  // Value stream alignment
  value_stream: {
    end_to_end_process: string, // e.g., "Customer Purchase Journey"
    capabilities_in_sequence: string[],
    gaps_addressed_by_epic: string[],
    dependencies_between_capabilities: Array<{
      prerequisite_capability: string,
      dependent_capability: string,
      dependency_type: 'finish_to_start' | 'start_to_start',
    }>,
  },
}
```

**Sources**: [Epics vs Features vs Stories](https://www.visor.us/blog/epics-vs-features-vs-stories/), [Define features and epics in Azure Boards](https://learn.microsoft.com/en-us/azure/devops/boards/backlogs/define-features-epics)

---

## 7. ESTIMATION PATTERNS

### 7.1 Fibonacci vs. T-Shirt Sizing

**Comparison Matrix**:

| Aspect | Fibonacci Sequence | T-Shirt Sizing |
|--------|-------------------|-----------------|
| **Scale** | 1, 2, 3, 5, 8, 13, 21 (Fibonacci) | XS, S, M, L, XL, XXL |
| **Application** | Sprint-level stories | Project/epic level estimates |
| **When to Use** | Teams with 2+ sprints experience; velocity matters | New teams; initial backlog grooming; non-technical stakeholders |
| **Velocity Tracking** | Precise, mathematically trackable | Difficult; requires manual conversion |
| **Uncertainty Representation** | Built-in: gaps increase for larger estimates | Not explicit; requires conversion to numbers |
| **Conversion to Hours** | ~1 hour per point (adjust per team) | XS=1-3 sprints, S=3-5, M=5-8, L=8-13, XL=13-21, XXL=21+ |
| **Planning Poker** | Direct: use Fibonacci cards | Requires intermediate conversion |
| **Complexity Communication** | Implies uncertainty increases with size | Intuitive but loses precision |

**Recommendation**:
- **Use Fibonacci** for: Sprint planning, velocity tracking, detailed estimation, CI/CD integration
- **Use T-Shirt Sizing** for: Roadmap planning, stakeholder communication, portfolio-level estimates, initial backlog sizing

**Sources**: [Fibonacci for User Stories](https://www.avion.io/blog/story-points-fibonacci/), [Story Points: Estimation Guide](https://asana.com/resources/story-points)

### 7.2 Planning Poker Protocol

**Facilitating Planning Poker Session**:

```typescript
interface PlanningPokerSession {
  // Setup
  setup: {
    participants: string[], // Development team, product owner, scrum master
    story_to_estimate: UserStory,
    reference_stories: Array<{
      story_id: string,
      previously_estimated_points: number,
      complexity_description: string,
    }>,
    voting_scale: number[], // [1, 2, 3, 5, 8, 13, 21]
  },

  // Protocol steps
  steps: [
    {
      step: 1,
      action: 'Product Owner reads story aloud',
      purpose: 'Ensure everyone understands the requirement',
      duration_minutes: 2,
    },
    {
      step: 2,
      action: 'Team asks clarification questions',
      purpose: 'Resolve ambiguities before estimation',
      duration_minutes: 3,
    },
    {
      step: 3,
      action: 'Each team member secretly selects estimate card',
      purpose: 'Prevent anchoring bias and groupthink',
      duration_minutes: 1,
    },
    {
      step: 4,
      action: 'All estimates revealed simultaneously',
      purpose: 'Compare estimates transparently',
      duration_minutes: 1,
    },
    {
      step: 5,
      action: 'Discuss high and low estimates',
      purpose: 'Understand different perspectives',
      duration_minutes: 5,
      note: 'High estimator explains complexity; low estimator explains simplicity',
    },
    {
      step: 6,
      action: 'Re-vote if estimates diverged significantly',
      purpose: 'Reach convergence through discussion',
      duration_minutes: 1,
    },
    {
      step: 7,
      action: 'Document final estimate and assumptions',
      purpose: 'Create record for velocity tracking',
      duration_minutes: 1,
    },
  ],

  // Handling divergence
  convergence_strategy: {
    low_divergence: {
      definition: 'All estimates within 1-2 Fibonacci steps',
      action: 'Accept median estimate; move to next story',
    },
    high_divergence: {
      definition: 'Estimates differ by 3+ Fibonacci steps (e.g., 3 and 13)',
      action: 'Extended discussion, then re-vote',
      max_discussion_cycles: 2,
      escalation: 'If still divergent, split story or mark for spike',
    },
  },

  // Quality metrics
  metrics: {
    average_consensus_rounds: number, // <1.5 is healthy
    estimation_stability: {
      description: 'Do team estimates converge over time?',
      tracking: 'Compare first vote vs final across stories',
    },
  };
}
```

**Advantages of Planning Poker**:
- Prevents anchoring bias (simultaneous reveal)
- Includes diverse perspectives (whole team participates)
- Reveals complexity misunderstandings (discussion phase)
- Builds team calibration (convergence over time)
- Creates shared responsibility (team owns estimate)

**Anti-Patterns to Avoid**:
- Reverse Planning Poker: forcing consensus without discussion
- Voting in sequence: causes anchoring on first estimate
- Product Owner estimating: defeats purpose of team estimation
- Pressure to converge: some divergence is healthy signal

**Sources**: [Planning Poker & Agile Estimation](https://planningpoker.live/glossary), [Estimation Techniques: Story Points, Planning Poker, and T-Shirt Sizing](https://medium.com/@noorfatimaafzalbutt/estimation-techniques-story-points-planning-poker-and-t-shirt-sizing-581f04874ea1)

### 7.3 Velocity Tracking and Forecasting

```typescript
interface VelocityTracking {
  // Core metrics
  velocity: {
    sprint_number: number,
    story_points_committed: number,
    story_points_completed: number,
    velocity_this_sprint: number, // Completed points

    // Completion quality
    stories_completed: number,
    stories_returned_during_sprint: number,
    completion_quality_percentage: number, // (completed / committed) × 100
  },

  // Historical analysis
  velocity_history: Array<{
    sprint: number,
    velocity: number,
    factors_affecting: string[],
    notes: string,
  }>,

  // Statistical analysis
  statistics: {
    average_velocity_sprints_1_to_5: number,
    average_velocity_last_3_sprints: number,
    rolling_velocity: {
      window_sprints: number, // e.g., 3
      average: number,
      standard_deviation: number,
      confidence_level: 'high' | 'medium' | 'low',
    },
    velocity_stability_trend: {
      trend: 'improving' | 'stable' | 'declining',
      coefficient_of_variation: number, // std dev / mean
    },
  },

  // Forecasting
  forecasting: {
    approach: 'Use rolling average, not single sprint',
    forecast_range: {
      optimistic_velocity: number,
      most_likely_velocity: number,
      pessimistic_velocity: number,
      confidence_95_percent: {
        min_velocity: number,
        max_velocity: number,
      },
    },
    feature_forecast: {
      feature_size_points: number,
      sprints_to_complete_optimistic: number,
      sprints_to_complete_realistic: number,
      sprints_to_complete_pessimistic: number,
    },
  },

  // Important principles
  principles: {
    velocity_is_descriptive_not_prescriptive: true,
    never_compare_velocity_between_teams: true,
    use_rolling_average_not_single_sprint: true,
    account_for_seasonal_variation: true,
    note_disruptive_events: true, // Releases, vacation, etc.
  },

  // Warnings and anti-patterns
  warnings: {
    unstable_velocity_sprints: ['Indicates estimation issues', 'Suggests team capacity changes'],
    gaming_velocity: ['Inflating estimates to appear productive', 'Avoiding honest estimation'],
    over_relying_on_velocity: ['Velocity is input to forecast, not team throughput measure'],
  };
}
```

**Key Velocity Principles**:
1. **Descriptive, Not Prescriptive**: Velocity describes past performance; don't mandate velocity targets
2. **Team-Specific**: Velocity is unique to each team's estimation scale and context
3. **Rolling Average**: Use 3-sprint rolling average for forecasting, not single sprint
4. **Stability Matters**: Stable velocity (±20%) allows confident forecasting; unstable suggests issues
5. **Context Adjustments**: Account for vacation, releases, platform changes

**Sources**: [Velocity Tracking](https://asana.com/resources/story-points), [Fibonacci Agile Estimation](https://www.parabol.co/blog/fibonacci-estimation/)

---

## 8. DEFINITION OF DONE (DoD)

### 8.1 DoD Checklist Structure

**Purpose**: Establish shared standards for work completion; ensure consistent quality across sprints.

```typescript
interface DefinitionOfDone {
  // Organizational standards (minimum for all teams)
  organizational_dod: {
    name: 'Organization-Wide DoD',
    scope: 'All Scrum Teams must comply',
    items: [
      {
        item: 'Code written and reviewed',
        description: 'At least one peer code review completed and approved',
        verification: 'Code review tool shows approval',
      },
      {
        item: 'Unit tests written and passing',
        description: 'Test coverage minimum 70%; all tests green',
        verification: 'CI/CD pipeline shows test pass',
      },
      {
        item: 'Code committed to main branch',
        description: 'Code merged to develop/main; no conflicts',
        verification: 'Git repository shows commit',
      },
      {
        item: 'Acceptance criteria met',
        description: 'All AC tested and verified complete',
        verification: 'QA sign-off in tracking system',
      },
      {
        item: 'Documentation updated',
        description: 'Code comments, README, API docs updated',
        verification: 'Docs repo commit history',
      },
      {
        item: 'Performance acceptable',
        description: 'Meets performance baseline; no regression',
        verification: 'Performance test results',
      },
      {
        item: 'Security review passed',
        description: 'SAST scan passed; no critical vulnerabilities',
        verification: 'Security scanning tool report',
      },
      {
        item: 'Deployed to staging',
        description: 'Feature tested in staging environment',
        verification: 'Deployment logs from staging',
      },
    ],
  },

  // Team-specific DoD (builds on organizational)
  team_specific_dod: {
    team_name: 'Platform Team',
    scope: 'Extends organizational DoD; teams cannot remove items',
    additional_items: [
      {
        item: 'API contract tested',
        description: 'Integration tests validate API contract',
        verification: 'Contract test results',
      },
      {
        item: 'Database migrations tested',
        description: 'Migration tested on staging DB replica',
        verification: 'Migration test report',
      },
      {
        item: 'Product Owner sign-off',
        description: 'PO verifies feature meets requirements',
        verification: 'JIRA story marked accepted',
      },
    ],
  },

  // DoD by artifact type
  dod_by_type: {
    user_story: {
      items: [
        'Acceptance criteria verified',
        'Code reviewed and merged',
        'Tests automated',
        'Documentation updated',
        'Deployed to staging',
        'PO acceptance given',
      ],
    },

    bug_fix: {
      items: [
        'Root cause documented',
        'Fix code reviewed',
        'Regression test added',
        'Original issue resolved',
        'Fix deployed to staging',
        'Verified fixed in staging',
      ],
    },

    technical_debt: {
      items: [
        'Refactoring completed',
        'Tests updated/added',
        'Performance impact measured',
        'No functional regression',
        'Deployed to staging',
      ],
    },
  },

  // Metrics and compliance
  compliance: {
    dod_checklist_items: number,
    automation_percentage: number, // % of DoD items verified automatically
    manual_verification_items: string[], // Which items still need manual check
    compliance_rate_last_sprint: number, // % of stories meeting full DoD

    // Violations and rework
    stories_reopened_post_done: number,
    average_rework_hours: number,
    rework_root_causes: string[],
  };
}
```

### 8.2 Automated DoD Verification

**Implementation Strategy**:

```typescript
interface AutomatedDoDVerification {
  // CI/CD Pipeline integration
  pipeline_stages: [
    {
      stage: 'Code Quality',
      checks: [
        'SonarQube: code quality gate passed',
        'Code coverage: >70%',
        'No critical code smells',
      ],
      tools: ['SonarQube', 'Codecov', 'ESLint'],
    },
    {
      stage: 'Security',
      checks: [
        'SAST scan: no critical vulnerabilities',
        'Dependency check: no vulnerable versions',
        'Secret scanning: no credentials in code',
      ],
      tools: ['SonarQube', 'Trivy', 'TruffleHog'],
    },
    {
      stage: 'Testing',
      checks: [
        'Unit tests: 100% passing',
        'Integration tests: 100% passing',
        'No flaky tests',
      ],
      tools: ['Jest', 'Pytest', 'Selenium'],
    },
    {
      stage: 'Performance',
      checks: [
        'Load test: <200ms response time',
        'No memory leaks detected',
        'No significant performance regression',
      ],
      tools: ['JMeter', 'New Relic', 'Lighthouse'],
    },
    {
      stage: 'Staging Deployment',
      checks: [
        'Deployment successful',
        'Smoke tests passed',
        'Feature available in staging',
      ],
      tools: ['Jenkins', 'GitLab CI/CD', 'GitHub Actions'],
    },
  ],

  // Enforcement
  enforcement: {
    block_merge_on_failure: true,
    required_approvals: 2,
    require_passing_tests: true,
    require_security_scan: true,
    prevent_direct_main_push: true,
  },

  // Dashboard and reporting
  dashboard: {
    dod_compliance_percentage: number,
    items_blocked_on_dod: number,
    average_time_to_dod: string, // e.g., "3.2 days"
    most_common_dod_failure: string,
    trend: 'improving' | 'stable' | 'declining',
  };
}
```

**DoD Hierarchy**:
- **Organizational DoD**: Minimum standards all teams must follow
- **Team DoD**: Extends organizational DoD; team-specific additions
- **Feature-Specific DoD**: May have additional criteria for complex features (e.g., internationalization)

**Sources**: [What is Definition of Done in Agile](https://www.atlassian.com/agile/project-management/definition-of-done), [Definition of Done Checklist](https://www.checklistsformanagers.com/checklist/definition-of-done-dod-checklist/)

---

## 9. STORY DEPENDENCIES AND RISK MANAGEMENT

### 9.1 Dependency Types and Visualization

**Purpose**: Identify and manage relationships between work items to reduce delivery risk.

```typescript
interface StoryDependency {
  // Dependency types (based on project management standards)
  dependency_types: {

    finish_to_start: {
      abbreviation: 'FS',
      definition: 'Dependent task cannot start until predecessor finishes',
      lag_lead: 'Can add lag (wait days) or lead (start early)',
      example: 'UI story depends on API story being complete',
      risk_level: 'high', // Longest critical paths result from FS
    },

    start_to_start: {
      abbreviation: 'SS',
      definition: 'Dependent task cannot start until predecessor starts',
      lag_lead: 'Can add lag/lead',
      example: 'Testing starts 1 day after development starts',
      risk_level: 'medium',
    },

    finish_to_finish: {
      abbreviation: 'FF',
      definition: 'Dependent task cannot finish until predecessor finishes',
      lag_lead: 'Can add lag/lead',
      example: 'QA testing cannot finish before development finishes',
      risk_level: 'medium',
    },

    start_to_finish: {
      abbreviation: 'SF',
      definition: 'Dependent task cannot finish until predecessor starts',
      lag_lead: 'Rare; handles edge cases',
      example: 'Old system support can\'t stop until new system is operational',
      risk_level: 'low', // Rarely used
    },
  },

  // Dependency graph
  dependency_graph: {
    nodes: Array<{
      story_id: string,
      title: string,
      status: 'todo' | 'in_progress' | 'done',
      estimated_duration_days: number,
    }>,

    edges: Array<{
      source_story_id: string,
      target_story_id: string,
      dependency_type: 'FS' | 'SS' | 'FF' | 'SF',
      lag_days: number,
      criticality: 'critical_path' | 'on_track' | 'slack_available',
      risk_score: number, // 1-10; higher = higher risk
    }>,
  },

  // Metrics
  metrics: {
    critical_path_length_days: number,
    stories_on_critical_path: number,
    dependency_chain_depth: {
      max_depth: number,
      average_depth: number,
      warning_threshold: 4, // >4 is high risk
    },
    dependency_density: {
      total_dependencies: number,
      stories_with_dependencies: number,
      percentage_dependent: number,
      warning_threshold: 60, // >60% dependent is high risk
    },
  };
}
```

### 9.2 Dependency Visualization Techniques

**Gantt Chart**:
- Horizontal timeline showing dependencies
- Useful for: Timeline planning, critical path analysis
- Tools: MS Project, Jira, Monday.com

**Dependency Diagram (Network Diagram)**:
- Shows stories as nodes, dependencies as arrows
- Useful for: Understanding flow, identifying constraints
- Tools: Lucidchart, Miro, Draw.io

**Critical Chain**:
- Identifies longest path through dependencies
- Manages buffers rather than individual task padding
- Useful for: Risk management, realistic scheduling

**Example Visualization**:
```
Story A (API Setup) [5 days]
    ↓ FS (Finish-to-Start, 0 lag)
Story B (Frontend) [7 days] → CRITICAL PATH
    ↓ FS (1 day lag)
Story C (Integration Tests) [3 days]
    ↓ FS
Story D (Deployment) [2 days]

Critical Path Length: 5 + 7 + 1 + 3 + 2 = 18 days
Slack on non-critical stories: [Shows which can be delayed without impacting timeline]
```

### 9.3 Dependency Risk Management

```typescript
interface DependencyRiskManagement {
  // Risk assessment
  risks: Array<{
    risk_id: string,
    description: string,
    source_dependencies: string[], // Which dependencies create this risk
    probability: 'low' | 'medium' | 'high',
    impact: 'low' | 'medium' | 'high',
    risk_score: number, // (probability × impact) scale 1-25

    // Mitigation strategies
    mitigation: {
      strategy: string,
      responsible_party: string,
      action_items: string[],
      target_date: string,
    },

    // Contingency planning
    contingency: {
      if_dependency_missed: string,
      plan_b: string,
      buffer_days_allocated: number,
    },
  }>,

  // Dependency health metrics
  health: {
    on_track_dependencies: number,
    at_risk_dependencies: number,
    critical_path_slack_days: number, // Positive = buffer, Negative = at risk

    // Early warning system
    early_warnings: string[], // Identify risks before they manifest
  };
}
```

**Dependency Risk Mitigation Strategies**:
1. **Reduce Dependency**: Split stories to eliminate or reduce dependencies
2. **Parallelize**: Use Start-to-Start dependencies instead of Finish-to-Start where possible
3. **Buffer Allocation**: Add buffer on critical path (5-10% contingency)
4. **Alternative Solutions**: Identify workarounds if dependency is missed
5. **Clear Communication**: Daily standup review of blocked/blocking stories
6. **Spike First**: Use research spike to reduce dependency uncertainty

**Sources**: [Understanding Project Dependencies](https://asana.com/resources/project-dependencies), [Task Dependencies in Project Management](https://monday.com/blog/project-management/task-dependencies/)

---

## 10. BUSINESS VALUE QUANTIFICATION

### 10.1 Cost of Delay (CoD) Framework

**Purpose**: Quantify economic impact of postponing work; drive prioritization based on value timing.

```typescript
interface CostOfDelay {
  // Simple CoD formula
  simple_formula: {
    formula: 'CoD = Expected Weekly Profit × Duration in Weeks',
    example: {
      weekly_profit: 5000,
      duration_weeks: 2,
      cost_of_delay: 10000, // $5,000 × 2
      interpretation: 'Delaying 2 weeks costs $10,000 in foregone profit',
    },
  },

  // Three components of CoD
  components: {

    // Component 1: User/Business Value
    business_value: {
      description: 'Annual profit/revenue generated by feature',
      estimation_approach: [
        'Based on revenue model',
        'Customer willingness to pay',
        'Market size × penetration × price',
      ],
      example: {
        feature: 'Premium subscription tier',
        annual_revenue_if_launched: 500000,
        monthly_equivalent: 41667,
        weekly_equivalent: 9615,
      },
    },

    // Component 2: Time Criticality
    time_criticality: {
      description: 'Cost of delay increases over time due to market timing',
      factors: [
        'Market window closure',
        'Competitive threats',
        'Seasonal demand',
        'Regulatory deadline',
      ],
      example: {
        scenario: 'Holiday shopping season peak',
        revenue_if_launched_before_nov: 50000,
        revenue_if_launched_in_january: 15000,
        delta_if_missed: 35000,
      },
    },

    // Component 3: Risk Reduction / Opportunity Enablement
    risk_reduction: {
      description: 'Feature enables other profitable capabilities',
      types: [
        'Enables platform for 3 future features',
        'Reduces technical debt blocking development',
        'Enables partnerships that increase revenue',
      ],
      example: {
        feature: 'API infrastructure',
        direct_revenue: 10000,
        enables_annual_revenue: 200000, // From integrations
        opportunity_value: 200000,
      },
    },
  },

  // CD3 Metric (Cost of Delay Divided by Duration)
  cd3_metric: {
    formula: 'CD3 = Cost of Delay / Duration',
    purpose: 'Prioritize features by economic return: higher CD3 = higher priority',

    example: {
      feature_a: {
        cost_of_delay_weekly: 5000,
        estimated_duration_weeks: 4,
        cd3_score: 1250, // 5000 / 4
        rank: 2,
      },
      feature_b: {
        cost_of_delay_weekly: 3000,
        estimated_duration_weeks: 1,
        cd3_score: 3000, // 3000 / 1; higher priority despite lower CoD
        rank: 1,
      },
    },

    priority_rule: 'Higher CD3 = Do first (maximizes value delivered per unit time)',
  },

  // Value quantification by type
  value_types: {

    revenue_value: {
      type: 'Monetary impact',
      example: 'New subscription feature adds $50k/year revenue',
      measurement: 'Annual revenue or profit impact',
    },

    cost_savings_value: {
      type: 'Reduced operational costs',
      example: 'Automation reduces support tickets by 30%, saving $20k/year',
      measurement: 'Annual cost reduction',
    },

    customer_retention_value: {
      type: 'Churn reduction impact',
      example: 'Feature reduces churn by 5%, retaining 100 customers worth $5k each',
      measurement: 'LTV × customers retained',
    },

    market_expansion_value: {
      type: 'Opens new market segment',
      example: 'Enables enterprise sales; total addressable market +$2M',
      measurement: 'TAM expansion × estimated penetration',
    },

    future_value: {
      type: 'Enables future capabilities',
      example: 'Platform enables 3 future features worth $500k combined',
      measurement: 'Sum of future feature values',
    },
  };
}
```

### 10.2 ROI and Value Point Estimation

```typescript
interface BusinessValueEstimation {
  // Value points: similar to story points but for business value
  value_points: {
    scale: [1, 2, 3, 5, 8, 13, 21], // Same as story points
    meaning: {
      1: 'Minimal value; nice-to-have feature',
      3: 'Small but clear value; improves UX slightly',
      5: 'Medium value; addresses clear customer need',
      8: 'High value; significant customer benefit or revenue',
      13: 'Very high value; enables major business capability',
      21: 'Exceptional value; transforms product or revenue',
    },
  },

  // ROI Calculation
  roi_calculation: {
    formula: 'ROI (%) = (Value Points / Effort in Story Points) × 100',
    example: {
      feature: 'Customer analytics dashboard',
      value_points: 8,
      story_points: 5,
      roi_percentage: 160, // (8/5) × 100
      interpretation: 'Expected 160% return on effort invested',
    },
  },

  // Payback period
  payback_period: {
    formula: 'Payback Period (weeks) = Implementation Cost / Weekly Value Delivery',
    example: {
      feature: 'Premium tier',
      implementation_cost_dollars: 50000,
      weekly_revenue_generated: 10000,
      payback_period_weeks: 5, // 50000 / 10000
      interpretation: 'ROI achieved in 5 weeks; excellent return',
    },
  },

  // Value delivery timeline
  value_delivery: {
    // Value accrues differently over time
    value_curve_types: {

      immediate: {
        shape: 'Step function',
        description: 'Value realized upon launch',
        example: 'Compliance feature; required for release',
      },

      ramp_up: {
        shape: 'S-curve',
        description: 'Value builds as adoption grows',
        example: 'Performance feature; value grows as user base scales',
      },

      linear: {
        shape: 'Linear growth',
        description: 'Steady value accumulation',
        example: 'Cost savings; realized consistently over time',
      },
    },
  };
}
```

### 10.3 Business Value Scoring Matrix

**SAFe Business Value Scoring Example**:

```
Feature: Search Optimization

Business Value Score (1-21 scale):
- Revenue Impact: 8/21 (new revenue stream)
- Cost Savings: 3/21 (minimal cost reduction)
- Customer Satisfaction: 5/21 (improves experience)
- Learning/Strategy: 5/21 (enables data insights)

Total Value Points: 21
Effort (Story Points): 13
ROI: 161%

Rank: HIGH PRIORITY
```

**Sources**: [Cost of Delay Definition](https://airfocus.com/glossary/what-is-cost-of-delay/), [Calculating Business Value](https://www.scruminc.com/calculating-business-value/)

---

## SYNTHESIS AND IMPLEMENTATION ROADMAP

### Data Structure Integration

For implementation, these ten specification pattern areas should be integrated into a unified object model:

```typescript
interface RichEpicSpecification {
  // SAFe epic specification
  epic: {
    hypothesis_statement: EpicHypothesisStatement,
    lean_business_case: LeanBusinessCase,
    wsjf_priority: WSJFCalculation,
    kanban_status: EpicKanbanState,
  },

  // Story mapping
  story_map: StoryMap,

  // Decomposition
  decomposition: EpicDecompositionHierarchy,

  // Features with story mapping
  features: Array<{
    feature: Feature,
    stories: Array<{
      story: UserStory,
      invest_compliance: INVESTCriteria,
      acceptance_criteria: AcceptanceCriteria,
      splitting_options: SPIDRSplitting,
      tasks: Task[],
      dependencies: StoryDependency[],
      business_value: BusinessValueEstimation,
    }>,
  }>,

  // Estimation
  estimation: {
    story_point_scale: 'fibonacci',
    velocity_tracking: VelocityTracking,
  },

  // Quality gates
  definition_of_done: DefinitionOfDone,

  // Risk management
  dependencies_and_risks: Array<{
    dependency: StoryDependency,
    risk_mitigation: DependencyRiskManagement,
  }>,
}
```

### Implementation Priorities

1. **Phase 1: Foundation** (Weeks 1-2)
   - Implement INVEST criteria validation
   - Create definition of done framework
   - Establish story mapping structure

2. **Phase 2: Estimation** (Weeks 3-4)
   - Implement Fibonacci story points
   - Create velocity tracking
   - Deploy planning poker protocol

3. **Phase 3: Advanced Patterns** (Weeks 5-6)
   - Implement SPIDR splitting guidance
   - Create dependency visualization
   - Add cost of delay calculations

4. **Phase 4: Enterprise Features** (Weeks 7-8)
   - Integrate SAFe WSJF prioritization
   - Implement epic hypothesis statements
   - Create lean business case templates

5. **Phase 5: Automation** (Weeks 9-10)
   - Automated INVEST checking
   - DoD verification pipeline
   - Dependency risk dashboards

---

## RESEARCH SOURCES

### SAFe Framework
- [Epic - Scaled Agile Framework](https://framework.scaledagile.com/epic)
- [Extended Guidance - WSJF](https://framework.scaledagile.com/wsjf)
- [Portfolio Backlog](https://framework.scaledagile.com/portfolio-backlog)

### Story Mapping
- [Story Map Concepts](https://www.jpattonassociates.com/wp-content/uploads/2015/03/story_mapping.pdf)
- [User Story Mapping – The Complete Guide](https://www.avion.io/what-is-user-story-mapping/)

### INVEST Criteria
- [INVEST - Agile Alliance](https://agilealliance.org/glossary/invest/)
- [Creating The Perfect User Story](https://scrum-master.org/en/creating-the-perfect-user-story-with-invest-criteria/)

### Acceptance Criteria
- [Given-When-Then Acceptance Criteria](https://www.parallelhq.com/blog/given-when-then-acceptance-criteria)
- [Martin Fowler's Given When Then](https://martinfowler.com/bliki/GivenWhenThen.html)

### Story Splitting
- [SPIDR: Five Simple Ways](https://www.mountaingoatsoftware.com/blog/five-simple-but-powerful-ways-to-split-user-stories)

### Estimation
- [Fibonacci Story Points](https://www.avion.io/blog/story-points-fibonacci/)
- [Planning Poker & Agile Estimation](https://planningpoker.live/glossary)

### Definition of Done
- [What is Definition of Done](https://www.atlassian.com/agile/project-management/definition-of-done)

### Dependencies
- [Understanding Project Dependencies](https://asana.com/resources/project-dependencies)

### Business Value
- [Cost of Delay Definition](https://airfocus.com/glossary/what-is-cost-of-delay/)
- [Calculating Business Value](https://www.scruminc.com/calculating-business-value/)

---

**Document Version**: 1.0
**Last Updated**: January 29, 2026
**Research Methodology**: Comprehensive web search across 50+ authoritative sources
**Confidence Level**: High (industry-standard frameworks documented by original authors)

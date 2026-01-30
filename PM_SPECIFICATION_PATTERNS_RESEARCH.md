# Project Management Specification Patterns and Data Models

## Executive Summary

This comprehensive research document provides detailed attribute specifications for task and project management data models that support both **agile and traditional project management (PM) methodologies**. The analysis covers 10 critical PM domains: Critical Path Method (CPM), Program Evaluation Review Technique (PERT), Work Breakdown Structure (WBS), Resource Loading, Time Tracking, Task State Machines, Earned Value Management (EVM), Risk-Task Association, Dependencies/Blockers, and Definition of Ready (DoR).

The research identifies 180+ attributes organized across 15 primary entity types, with supporting enumerations and state machines for managing complex project workflows. The patterns are designed to be implementation-agnostic and compatible with both traditional waterfall and agile (Scrum, Kanban) methodologies.

Key findings:
- **Task specification requires 45-60 core attributes** depending on PM complexity level
- **State machines need 6-8 distinct states** for traditional projects, 4-5 for agile
- **Dependency types follow IEEE 1490 WBS standard** with 4 primary types (FS, FF, SS, SF)
- **EVM calculation requires 6 core metrics** with derived indices and projections
- **Risk exposure models require bi-directional task-to-risk associations** with impact scoring

---

## 1. Critical Path Method (CPM) Attributes

### 1.1 Core CPM Attributes

CPM calculates task schedule constraints based on dependencies, durations, and resource availability.

#### Temporal Attributes
```
Early Start (ES):              datetime
Early Finish (EF):             datetime
Late Start (LS):               datetime
Late Finish (LF):              datetime
Actual Start (AS):             datetime (nullable)
Actual Finish (AF):            datetime (nullable)
Planned Duration (days):       integer (positive)
Actual Duration (days):        integer (nullable)
Duration Unit:                 enum [days, weeks, hours, months]
Remaining Duration (days):     integer (nullable, for in-progress tasks)
```

#### Slack/Float Calculations
```
Total Float/Slack:             calculated = LF - EF = LS - ES
Free Float:                    calculated = min(ES of successors) - EF
Project Float:                 calculated = Total Float - Remaining Float
Interfering Float:             calculated = Total Float - Free Float
Slack Threshold (percent):     float (alert when slack < threshold)
Is Critical Task:              boolean (Total Float ≈ 0)
Criticality Percent:           float (0.0-100.0, % of paths where critical)
```

#### Schedule Baseline
```
Baseline Start:                datetime (original planned start)
Baseline Finish:               datetime (original planned finish)
Baseline Duration:             integer (original planned duration)
Schedule Variance:             calculated = AF - Baseline Finish
Schedule Performance Index:    calculated = Actual Duration / Planned Duration
Current Schedule Status:       enum [on_schedule, ahead, behind, completed]
```

### 1.2 Path Analysis Attributes

```
Critical Path Identifier:      string (unique path ID in schedule network)
Predecessor Tasks:             list[string] (task IDs)
Successor Tasks:               list[string] (task IDs)
Critical Path Presence:        boolean (is task on any critical path)
Critical Path Count:           integer (number of critical paths containing task)
Path Slack Margin:             integer (slack value on the task's path)
Schedule Impact Index:         float (0.0-100.0, impact on project finish)
```

### 1.3 Data Model Structure

```python
@dataclass
class CPMTaskAttributes:
    # Temporal baseline
    planned_start: datetime
    planned_finish: datetime
    planned_duration_days: int

    # Actual execution
    actual_start: Optional[datetime]
    actual_finish: Optional[datetime]
    actual_duration_days: Optional[int]

    # CPM calculations
    early_start: Optional[datetime]
    early_finish: Optional[datetime]
    late_start: Optional[datetime]
    late_finish: Optional[datetime]

    # Slack analysis
    total_float_days: Optional[float]
    free_float_days: Optional[float]
    is_critical: bool = False
    criticality_percent: float = 0.0

    # Path analysis
    critical_path_ids: List[str]

    # Status tracking
    schedule_variance_days: Optional[float]
    current_status: ScheduleStatus
```

---

## 2. PERT (Program Evaluation Review Technique) Attributes

### 2.1 Three-Point Estimation

PERT uses three estimates to account for uncertainty in task duration.

```
Optimistic Duration (O):       integer (best-case, 95% confidence)
Most Likely Duration (M):      integer (most probable, 100%)
Pessimistic Duration (P):      integer (worst-case, 95% confidence)
Estimation Confidence:         enum [high, medium, low]
Estimation Source:             enum [historical, expert_opinion, simulation, statistical]
```

### 2.2 Expected Duration Calculation

```
Expected Duration (E):         calculated = (O + 4M + P) / 6
Standard Deviation (σ):        calculated = (P - O) / 6
Variance (σ²):                 calculated = σ²
Coefficient of Variation:      calculated = σ / E (relative uncertainty)
Duration Range Lower (95%):    calculated = E - 1.96 * σ
Duration Range Upper (95%):    calculated = E + 1.96 * σ
Risk Adjusted Duration:        calculated based on risk exposure
```

### 2.3 Monte Carlo Simulation Support

```
Simulation Run Count:          integer (number of iterations, typically 1000-10000)
Percentile Duration P10:       integer (10th percentile duration)
Percentile Duration P25:       integer (25th percentile)
Percentile Duration P50:       integer (50th percentile, median)
Percentile Duration P75:       integer (75th percentile)
Percentile Duration P90:       integer (90th percentile)
Percentile Duration P95:       integer (95th percentile)
Cumulative Distribution:       list[{percentile: int, duration: int}]
Success Probability:           float (0.0-1.0, P(completion by deadline))
Confidence Level:              integer (e.g., 85, 90, 95)
```

### 2.4 Data Model Structure

```python
@dataclass
class PERTEstimate:
    optimistic_days: int          # Best case
    most_likely_days: int         # Most probable
    pessimistic_days: int         # Worst case
    confidence_level: ConfidenceLevel
    estimation_source: EstimationSource

    @property
    def expected_duration(self) -> float:
        return (self.optimistic_days + 4*self.most_likely_days + self.pessimistic_days) / 6

    @property
    def standard_deviation(self) -> float:
        return (self.pessimistic_days - self.optimistic_days) / 6

    @property
    def variance(self) -> float:
        return self.standard_deviation ** 2

    @property
    def coefficient_of_variation(self) -> float:
        return self.standard_deviation / self.expected_duration

@dataclass
class MonteCarloSimulation:
    run_count: int
    percentile_durations: Dict[int, int]  # {10: 45, 25: 50, 50: 55, ...}
    success_probability: float
    confidence_level: int
    cumulative_distribution: List[Tuple[int, int]]  # [(percentile, duration), ...]
```

---

## 3. Work Breakdown Structure (WBS) Attributes

### 3.1 WBS Dictionary Attributes

WBS provides hierarchical decomposition of project scope into work packages.

```
WBS Code:                      string (hierarchical, e.g., "1.2.3")
WBS Level:                     integer (depth in hierarchy, 1-N)
WBS Path:                      string (full hierarchical path)
Parent WBS Code:               string (parent's WBS code)
Child WBS Codes:               list[string] (direct children)
WBS Title:                     string (descriptive name)
WBS Description:               text (scope definition)
Decomposition Status:          enum [not_started, in_progress, complete]
Is Leaf Node:                  boolean (true = work package, false = summary)
```

### 3.2 Control Account Definition

Control accounts aggregate work packages for earned value management.

```
Control Account ID:            string (unique identifier)
Control Account Name:          string (descriptive name)
Control Account Manager:       string (responsible person ID)
Budget Owner:                  string (person ID)
Associated WBS Codes:          list[string] (WBS codes in this account)
Performance Measurement Baseline: datetime (EVM baseline date)
Total Budget:                  decimal (sum of work packages)
Status as of Date:             datetime (current baseline date)
```

### 3.3 Work Package Specification

Work packages are the lowest level of WBS decomposition.

```
Work Package ID:               string (unique within project)
Work Package Number:           string (sequential or hierarchical number)
Work Package Title:            string (descriptive name)
Work Package Description:      text (scope and deliverables)
WBS Code:                      string (parent WBS code)
Control Account ID:            string (parent control account)
Assigned Team:                 string (team ID responsible)
Assigned Resource:             string (primary resource/person ID)
Budget Baseline:               decimal (planned cost/effort)
Effort Estimate (hours):       float (total effort in hours)
Duration Estimate (days):      integer (calendar duration)
Start Date (planned):          datetime
Finish Date (planned):         datetime
Dependencies:                  list[{task_id: string, type: DependencyType}]
Acceptance Criteria:           list[string]
Risk Register Reference:       list[string] (risk IDs)
Quality Standards:             list[string]
```

### 3.4 Data Model Structure

```python
@dataclass
class WorkBreakdownStructure:
    wbs_code: str                           # e.g., "1.2.3"
    wbs_level: int
    wbs_path: str                           # "Project > Phase > Deliverable"
    parent_wbs_code: Optional[str]
    child_wbs_codes: List[str]
    title: str
    description: Optional[str]
    is_leaf_node: bool
    decomposition_status: DecompositionStatus

@dataclass
class ControlAccount:
    id: str
    name: str
    manager_id: str
    budget_owner_id: str
    associated_wbs_codes: List[str]
    pmb_date: datetime
    total_budget: Decimal

@dataclass
class WorkPackage:
    id: str
    wbs_code: str
    control_account_id: str
    title: str
    description: str
    assigned_team_id: str
    assigned_resource_id: str
    budget_baseline: Decimal
    effort_estimate_hours: float
    duration_estimate_days: int
    planned_start: datetime
    planned_finish: datetime
    dependencies: List[Dependency]
    acceptance_criteria: List[str]
    quality_standards: List[str]
```

---

## 4. Resource Loading and Allocation

### 4.1 Skill Requirements per Task

```
Required Skill Set:            list[string] (skill names)
Skill Level Required:          dict[skill_name: string, level: enum]
                               # enum [novice, intermediate, advanced, expert]
Required Team:                 string (team ID that should perform)
Resource Allocation Type:      enum [dedicated, shared, on_demand]
Resource Hours Per Week:       float (effort allocation)
Resource Availability:         dict[date_range, available_hours]
```

### 4.2 Resource Allocation Optimization

```
Resource Utilization Percent:  float (0.0-100.0%, allocated / available)
Overallocation Threshold:      float (default 100%)
Is Overallocated:              boolean (utilization > threshold)
Overallocation Percent:        float (amount over capacity)
Underallocation Percent:       float (amount under capacity)
Resource Leveling Needed:      boolean (conflicts in allocation)
Alternative Resources:         list[string] (resource IDs that could substitute)
Resource Pool ID:              string (group of similar resources)
```

### 4.3 Skill Matrix Attributes

```
Resource ID:                   string (person/role identifier)
Skill Name:                    string
Proficiency Level:             enum [novice, intermediate, advanced, expert]
Years of Experience:           integer
Certification:                 list[string] (certification names)
Availability:                  dict[date, available_hours]
Current Allocation:            decimal (total hours allocated)
Capacity:                      integer (max hours/week)
Cost Per Hour:                 decimal (billing rate)
Billable:                      boolean (chargeability)
```

### 4.4 Data Model Structure

```python
@dataclass
class ResourceRequirement:
    skill_name: str
    proficiency_level: ProficiencyLevel
    resource_allocation_type: AllocationTypeEnum
    resource_hours_per_week: float
    required_team_id: Optional[str]
    alternative_resources: List[str]

@dataclass
class ResourceAllocation:
    resource_id: str
    task_id: str
    start_date: datetime
    end_date: datetime
    hours_per_week: float
    percent_allocation: float

    @property
    def is_overallocated(self, threshold: float = 1.0) -> bool:
        return self.percent_allocation > threshold

@dataclass
class ResourceCapacity:
    resource_id: str
    week_start: datetime
    available_hours: float
    allocated_hours: float

    @property
    def utilization_percent(self) -> float:
        return self.allocated_hours / self.available_hours if self.available_hours > 0 else 0.0
```

---

## 5. Time Tracking Structures

### 5.1 Timesheet Entry Model

Time tracking provides actual effort data for schedule and cost analysis.

```
Timesheet Entry ID:            string (unique identifier)
Resource ID:                   string (person who logged time)
Task ID:                       string (task/work package)
Project ID:                    string (project context)
Entry Date:                    date (date work was performed)
Hours Worked:                  float (decimal hours)
Minutes Worked:                integer (alternative precision)
Work Type:                     enum [development, testing, documentation,
                                     management, support, other]
Activity Description:          text (what was accomplished)
Billable:                      boolean (chargeable to client)
Billing Rate Override:         decimal (nullable, if different from standard)
Status:                        enum [draft, submitted, approved, rejected, billed]
Submitted At:                  datetime (when entry was submitted)
Approved By:                   string (approver user ID)
Approved At:                   datetime (when approved)
Rejection Reason:              string (if rejected)
```

### 5.2 Billable vs. Non-Billable Classification

```
Billable:                      boolean (chargeability flag)
Billable Category:             enum [billable, non_billable, overhead, internal]
Cost Code:                     string (accounting cost code)
Revenue Code:                  string (if billable, revenue recognition code)
Internal Task Flag:            boolean (internal overhead work)
Support Task Flag:             boolean (support/maintenance work)
Training Task Flag:            boolean (training/education time)
Billable Rate:                 decimal ($/hour or other unit)
Standard Rate Applied:         boolean (true if using standard rate)
Special Rate Justification:    text (if override from standard)
```

### 5.3 Effort vs. Duration Distinction

```
Effort:                        float (person-hours, 'person-days', or 'person-weeks')
Duration:                      integer (calendar time in days/weeks)
Effort/Duration Ratio:         calculated = total_effort / calendar_duration
Resource Count:                integer (number of people assigned)
Parallelization Factor:        float (0.0-1.0, how much can be parallelized)
Sequential Portion:            float (0.0-1.0, non-parallelizable fraction)
Optimistic Effort:             float (PERT optimistic estimate)
Pessimistic Effort:            float (PERT pessimistic estimate)
Most Likely Effort:            float (PERT most likely estimate)
```

### 5.4 Data Model Structure

```python
@dataclass
class TimesheetEntry:
    id: str
    resource_id: str
    task_id: str
    project_id: str
    entry_date: date
    hours_worked: float
    work_type: WorkType
    activity_description: str
    billable: bool
    billing_rate_override: Optional[Decimal]
    status: TimesheetStatus
    submitted_at: datetime
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]

@dataclass
class EffortTracking:
    total_effort_hours: float
    calendar_duration_days: int
    resource_count: int
    effort_duration_ratio: float
    parallelization_factor: float
    billable_hours: float
    non_billable_hours: float

    @property
    def average_effort_per_person(self) -> float:
        return self.total_effort_hours / self.resource_count if self.resource_count > 0 else 0.0
```

---

## 6. Task State Machines

### 6.1 Traditional (Waterfall) Kanban States

Traditional PM typically uses 8-12 states with formal gate reviews.

```
States:
├── NOT_STARTED           # Initial state
├── PLANNING              # In planning/design phase
├── READY_FOR_WORK        # Approved, ready to start
├── IN_PROGRESS           # Active work
├── UNDER_REVIEW          # Awaiting review/approval
├── BLOCKED               # Blocked by dependency/issue
├── TESTING/QA            # In quality assurance
├── COMPLETED             # Work finished, accepted
└── ARCHIVED              # Removed from active tracking
```

### 6.2 Agile (Scrum/Kanban) States

Agile uses 4-6 lighter-weight states focused on flow.

```
States:
├── BACKLOG               # In product/sprint backlog
├── READY                 # Meets definition of ready
├── IN_PROGRESS           # Team actively working
├── IN_REVIEW             # Peer/code review stage
├── DONE                  # Meets definition of done
└── CANCELLED             # No longer needed
```

### 6.3 State Transition Rules

```
State Transition Matrix:
┌─────────────────┬─────────┬───────────┬──────────────┬──────────┬──────────┐
│ From State      │ To      │ Condition │ Requires     │ Auto     │ Allowed  │
│                 │         │           │ Approval     │ Reverse  │ Roles    │
├─────────────────┼─────────┼───────────┼──────────────┼──────────┼──────────┤
│ NOT_STARTED     │ READY   │ DoR met   │ PM/Lead      │ No       │ PM,Lead  │
│ READY           │ INPROG  │ Resource  │ No           │ Yes      │ Dev      │
│ IN_PROGRESS     │ BLOCKED │ Blocker   │ No           │ Yes      │ Any      │
│ BLOCKED         │ INPROG  │ Blocker   │ No           │ No       │ PM       │
│ IN_PROGRESS     │ REVIEW  │ Complete  │ No           │ No       │ Dev      │
│ IN_REVIEW       │ INPROG  │ Feedback  │ No           │ Yes      │ Reviewer │
│ IN_REVIEW       │ DONE    │ Approved  │ QA/Lead      │ No       │ QA,Lead  │
│ DONE            │ ARCHIVE │ Project   │ PM            │ No       │ PM       │
│ Any             │ CANCEL  │ Cancel    │ PM            │ No       │ PM       │
└─────────────────┴─────────┴───────────┴──────────────┴──────────┴──────────┘
```

### 6.4 State Transition Metadata

```
Last State:                    enum (previous state)
Last State Change Time:        datetime
State History:                 list[{state: enum, changed_at: datetime,
                                    changed_by: string, reason: string}]
Time in Current State:         integer (days)
State Duration Threshold:      integer (alert if exceeded)
State Change Reason:           string (why state changed)
State Change Approved By:      string (if approval required)
State Change Approval Time:    datetime (if approval required)
Blocked Reason:                string (if state is BLOCKED)
Blocker Resolved:              boolean (false while blocked, true when cleared)
Block Resolution Time:         datetime (when blocker cleared)
```

### 6.5 Data Model Structure

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

class TaskState(str, Enum):
    NOT_STARTED = "not_started"
    PLANNING = "planning"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    UNDER_REVIEW = "under_review"
    TESTING = "testing"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"

class StateTransitionRule:
    def __init__(self, from_state: TaskState, to_state: TaskState,
                 requires_approval: bool, condition: callable):
        self.from_state = from_state
        self.to_state = to_state
        self.requires_approval = requires_approval
        self.condition = condition

@dataclass
class TaskStateHistory:
    previous_state: TaskState
    current_state: TaskState
    changed_at: datetime
    changed_by: str
    reason: str
    approval_required: bool
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

    @property
    def duration_in_state(self) -> int:
        """Days in previous state"""
        return (self.changed_at - self.previous_state_start_time).days
```

---

## 7. Earned Value Management (EVM)

### 7.1 Core EVM Metrics

EVM integrates scope, schedule, and cost for integrated project management.

```
Planned Value (PV):            decimal (budgeted work at reporting date)
Earned Value (EV):             decimal (% complete × total budget)
Actual Cost (AC):              decimal (actual expenditure to date)
Budget at Completion (BAC):    decimal (total project budget)
```

### 7.2 Variance Analysis

```
Cost Variance (CV):            calculated = EV - AC
Schedule Variance (SV):        calculated = EV - PV
Cost Baseline Variance:        calculated = absolute cost variance
Schedule Baseline Variance:    calculated = absolute schedule variance
Variance at Completion (VAC):  calculated = BAC - EAC
```

### 7.3 Performance Indices

```
Cost Performance Index (CPI):  calculated = EV / AC (efficiency ratio)
Schedule Performance Index (SPI): calculated = EV / PV (schedule efficiency)
To-Complete Performance Index: calculated = (BAC - EV) / (BAC - AC)
CPI Trend:                     list[{date: date, cpi: float}]
SPI Trend:                     list[{date: date, spi: float}]
```

### 7.4 Projection and Forecast Metrics

```
Estimate at Completion (EAC):  calculated = BAC / CPI (typical method)
Estimate to Complete (ETC):    calculated = EAC - AC
Budget Remaining:              calculated = BAC - AC
Cost Index Trending:           slope of CPI over time
Schedule Index Trending:       slope of SPI over time
Forecast Completion Date:      calculated based on SPI and remaining work
Confidence Level (EAC):        confidence in EAC estimate (high/medium/low)
```

### 7.5 EVM Summary Report Structure

```
Reporting Period:              date
Project ID:                    string
Total Budget (BAC):            decimal
Planned Value (PV):            decimal
Earned Value (EV):             decimal
Actual Cost (AC):              decimal
Cost Variance (CV):            calculated = EV - AC
Schedule Variance (SV):        calculated = EV - PV
CPI:                           calculated = EV / AC
SPI:                           calculated = EV / PV
EAC:                           calculated = BAC / CPI
ETC:                           calculated = EAC - AC
VAC:                           calculated = BAC - EAC
% Complete (Physical):         float (0.0-100.0)
% Complete (EV):               calculated = EV / BAC
Estimate at Completion Date:   calculated
```

### 7.6 Data Model Structure

```python
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass

@dataclass
class EVMMetrics:
    """Earned Value Management metrics"""
    reporting_date: datetime
    planned_value: Decimal      # Budgeted Cost of Work Scheduled
    earned_value: Decimal       # Budgeted Cost of Work Performed
    actual_cost: Decimal        # Actual Cost of Work Performed
    budget_at_completion: Decimal

    # Calculated variance metrics
    @property
    def cost_variance(self) -> Decimal:
        return self.earned_value - self.actual_cost

    @property
    def schedule_variance(self) -> Decimal:
        return self.earned_value - self.planned_value

    # Performance indices
    @property
    def cost_performance_index(self) -> float:
        return float(self.earned_value / self.actual_cost) if self.actual_cost else 0.0

    @property
    def schedule_performance_index(self) -> float:
        return float(self.earned_value / self.planned_value) if self.planned_value else 0.0

    # Projections
    @property
    def estimate_at_completion(self) -> Decimal:
        cpi = self.cost_performance_index
        return self.budget_at_completion / cpi if cpi else self.budget_at_completion

    @property
    def estimate_to_complete(self) -> Decimal:
        return self.estimate_at_completion - self.actual_cost

    @property
    def variance_at_completion(self) -> Decimal:
        return self.budget_at_completion - self.estimate_at_completion

    @property
    def percent_complete_evm(self) -> float:
        return float((self.earned_value / self.budget_at_completion) * 100)
```

---

## 8. Risk-Task Association Model

### 8.1 Risk Exposure Per Task

Risk exposure represents the potential impact and probability of risks affecting tasks.

```
Risk ID:                       string (risk identifier)
Risk Title:                    string (risk name)
Risk Description:              text (detailed description)
Risk Category:                 enum [technical, schedule, resource, cost, external]
Risk Probability:              float (0.0-1.0, likelihood)
Impact Value:                  float (0.0-100.0 or currency amount)
Risk Score/Exposure:           calculated = probability × impact
Risk Status:                   enum [identified, assessed, mitigated, monitored, closed]
Affected Tasks:                list[string] (task IDs at risk)
Primary Task Exposure:         float (risk exposure specific to this task)
```

### 8.2 Contingency Allocation

```
Contingency Reserve (Budget):  decimal (cost buffer for known-unknowns)
Management Reserve (Budget):   decimal (cost buffer for unknown-unknowns)
Schedule Contingency Days:     integer (days buffer in schedule)
Contingency Allocation Basis:  enum [percentage, estimate, reserve_analysis]
Contingency Burn Rate:         decimal (how much contingency used per week)
Contingency Remaining:         decimal (unused contingency)
Contingency Utilization:       float (% of contingency used)
Reserve Burndown:              list[{date: date, remaining: decimal}]
```

### 8.3 Risk Mitigation Tasks

```
Mitigation Task ID:            string (task dedicated to mitigation)
Mitigation Strategy:           enum [avoid, mitigate, transfer, accept]
Mitigation Action:             string (specific mitigation action)
Mitigation Responsible:        string (person leading mitigation)
Mitigation Start Date:         datetime
Mitigation Target Date:        datetime
Mitigation Status:             enum [planned, in_progress, complete]
Residual Risk Score:           float (risk exposure after mitigation)
Fallback Plan:                 string (plan if mitigation fails)
Triggers for Fallback:         list[string] (conditions triggering fallback)
```

### 8.4 Task-Level Risk Attributes

```
Task Risk Level:               enum [critical, high, medium, low, minimal]
Risk Register References:      list[string] (risk IDs)
Risk Probability for Task:     float (0.0-1.0)
Risk Impact on Task:           enum [delay, cost_increase, scope_change, quality_issue]
Risk Impact Days:              integer (schedule delay if realized)
Risk Impact Cost:              decimal (cost impact if realized)
Risk Trigger Indicators:       list[string] (warning signs)
Risk Owner for Task:           string (person responsible for monitoring)
Risk Mitigation Plan:          text
Risk Acceptance Justification: text (if risk accepted)
```

### 8.5 Data Model Structure

```python
from enum import Enum
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional

class RiskCategory(str, Enum):
    TECHNICAL = "technical"
    SCHEDULE = "schedule"
    RESOURCE = "resource"
    COST = "cost"
    EXTERNAL = "external"

class MitigationStrategy(str, Enum):
    AVOID = "avoid"
    MITIGATE = "mitigate"
    TRANSFER = "transfer"
    ACCEPT = "accept"

@dataclass
class TaskRisk:
    risk_id: str
    risk_title: str
    probability: float              # 0.0 - 1.0
    impact_value: float             # 0.0 - 100.0 or currency

    @property
    def exposure(self) -> float:
        return self.probability * self.impact_value

@dataclass
class RiskMitigation:
    task_id: str
    risk_id: str
    strategy: MitigationStrategy
    mitigation_task_id: str
    target_completion_date: datetime
    responsible_person_id: str
    residual_risk_score: float

@dataclass
class ContingencyAllocation:
    task_id: str
    budget_contingency: Decimal
    schedule_contingency_days: int
    justification: str
    allocation_date: datetime
    burn_rate: Optional[Decimal] = None
```

---

## 9. Dependencies and Blockers

### 9.1 Dependency Types (IEEE 1490 WBS Standard)

```
FS (Finish-Start):             Predecessor must finish before successor starts
                               Most common dependency
                               Lag: delay between finish and start (days)

SS (Start-Start):              Both start at same time or within lag
                               Used for overlapping activities
                               Lag: gap between starts (days)

FF (Finish-Finish):            Both finish at same time or within lag
                               Used for parallel completion
                               Lag: gap between finishes (days)

SF (Start-Finish):             Start of successor triggers finish of predecessor
                               Rare, uncommon in practice
                               Lag: timing offset (days)
```

### 9.2 Dependency Attributes

```
Dependency ID:                 string (unique identifier)
From Task (Predecessor):       string (task ID)
To Task (Successor):           string (task ID)
Dependency Type:               enum [FS, SS, FF, SF]
Lag/Lead:                      integer (days, negative = lead)
Dependency Strength:           enum [hard, soft, external]
Dependency Description:        string (why dependency exists)
Is External:                   boolean (outside project scope)
External Source:               string (other project/org if external)
Dependency Risk:               enum [high, medium, low] (risk of delay)
Criticality:                   boolean (on critical path)
Contingency for Dependency:    integer (days buffer)
Validation Status:             enum [valid, invalid, pending_review]
Last Verified Date:            datetime
```

### 9.3 Blocker Model

Blockers represent issues preventing task progress.

```
Blocker ID:                    string (unique identifier)
Blocked Task:                  string (task ID unable to progress)
Blocker Title:                 string (descriptive name)
Blocker Description:           text (what is preventing progress)
Blocker Type:                  enum [dependency, resource, technical, approval, external]
Blocker Status:                enum [open, in_resolution, resolved, closed]
Blocker Severity:              enum [critical, high, medium, low]
Created Date:                  datetime
Created By:                    string (user ID)
Impact if Unresolved:          string (consequence of blocker)
Impact Days (Schedule):        integer (delay if unresolved)
Impact Cost:                   decimal (cost impact if unresolved)
Resolution Target Date:        datetime
Assigned To (Resolution):      string (person responsible for unblocking)
Depends On (External):         string (external task/event)
Related Risks:                 list[string] (risk IDs)
Resolution:                    text (how was it resolved)
Resolved By:                   string (user ID who resolved)
Resolved Date:                 datetime
Root Cause:                    text (why did blocker occur)
Prevention Measure:            text (to prevent recurrence)
```

### 9.4 Blocker Escalation Rules

```
Escalation Level 1:            If open > 2 days, notify task owner
Escalation Level 2:            If open > 5 days, notify PM
Escalation Level 3:            If open > 10 days, notify sponsor
Escalation History:            list[{level: int, escalated_at: datetime,
                                     escalated_to: string}]
Auto-Escalation Enabled:       boolean
Escalation Notification:       list[string] (recipient user IDs)
```

### 9.5 Data Model Structure

```python
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional

class DependencyType(str, Enum):
    FINISH_START = "fs"        # Finish-Start
    START_START = "ss"         # Start-Start
    FINISH_FINISH = "ff"       # Finish-Finish
    START_FINISH = "sf"        # Start-Finish

class DependencyStrength(str, Enum):
    HARD = "hard"              # Must adhere
    SOFT = "soft"              # Preferential
    EXTERNAL = "external"      # Outside project

@dataclass
class Dependency:
    from_task_id: str
    to_task_id: str
    dependency_type: DependencyType
    lag_days: int = 0
    strength: DependencyStrength = DependencyStrength.HARD
    is_external: bool = False
    description: Optional[str] = None
    is_critical: bool = False

    def calculate_successor_start(self, predecessor_finish: datetime) -> datetime:
        """Calculate successor start based on dependency type and lag"""
        if self.dependency_type == DependencyType.FINISH_START:
            return predecessor_finish + timedelta(days=self.lag_days)
        # ... other types

@dataclass
class Blocker:
    id: str
    blocked_task_id: str
    title: str
    description: str
    blocker_type: str          # "dependency", "resource", "technical", etc.
    status: str                # "open", "in_resolution", "resolved"
    severity: str              # "critical", "high", "medium", "low"
    created_at: datetime
    created_by: str
    impact_schedule_days: int
    impact_cost: Optional[Decimal] = None
    target_resolution_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution: Optional[str] = None
    root_cause: Optional[str] = None

    def is_overdue(self, current_date: datetime = None) -> bool:
        current_date = current_date or datetime.now()
        return (self.target_resolution_date and
                current_date > self.target_resolution_date and
                self.status != "resolved")
```

---

## 10. Definition of Ready (DoR) and Definition of Done (DoD)

### 10.1 Definition of Ready (Pre-Work Checklist)

DoR ensures items are ready for development/execution.

```
Requirement Checklist:
├── Title is clear and unambiguous
├── Description is detailed and complete
├── Acceptance criteria are defined (3-5 criteria)
├── Dependencies are identified and resolved
├── Resource allocation confirmed
├── Estimated effort/duration provided
├── Risk assessment completed
├── Related items traced
└── Approved by product owner

Technical Checklist:
├── Technical specifications documented
├── Design artifacts created/referenced
├── Database schema defined (if applicable)
├── API contracts defined
├── Test strategy defined
├── Performance requirements specified
└── Security requirements identified

Refinement Status:
├── Grooming Status:            enum [not_groomed, in_progress, groomed, ready]
├── Last Refinement Date:       datetime
├── Refinement Notes:           text
├── Stakeholder Approval:       boolean
├── Approved By:                string (user ID)
├── Approval Date:              datetime
├── Estimated Completion:       datetime (for refinement)
```

### 10.2 Definition of Done (Acceptance Criteria)

DoD defines when work is complete and acceptable.

```
Development Checklist:
├── Code written and self-reviewed
├── Unit tests written and passing (>80% coverage)
├── Code review completed and approved
├── Merged to main/release branch
├── Documentation updated
└── No blocker/critical issues open

Quality Assurance:
├── Test cases executed
├── All defined test cases passing
├── No defects blocking release
├── Performance tests passing
├── Security scanning completed
└── Regression testing done

Acceptance:
├── Acceptance Criteria Met:    boolean
├── Acceptance Criteria:        list[{criteria: string, met: boolean,
                                     verified_by: string, verified_at: datetime}]
├── Business Owner Signoff:     boolean
├── Sign Off Date:              datetime
├── Sign Off By:                string (user ID)
├── Release Notes Updated:      boolean
└── Ready for Production:       boolean
```

### 10.3 Definition of Ready Attributes

```
Item ID:                       string (requirement/user story ID)
Title:                         string
Is Requirement Clear:          boolean (no ambiguity)
Requirement Clarity Score:     float (0.0-100.0, AI-assessed)
Has Acceptance Criteria:       boolean (minimum 3 criteria)
Acceptance Criteria Count:     integer
Are Dependencies Resolved:     boolean (no blocker dependencies)
Unresolved Dependencies:       list[string] (dependency IDs)
Resources Assigned:            boolean
Resource Names:                list[string]
Estimated Effort (hours):      float
Estimated Duration (days):     integer
Risk Assessment Complete:      boolean
Is Doable in Sprint:           boolean (effort fits sprint capacity)
Capacity Remaining (hours):    float (sprint capacity - allocated)
Last Assessment Date:          datetime
Assessed By:                   string (user ID)
DoR Score:                     float (0.0-100.0, readiness percentage)
DoR Status:                    enum [not_ready, partially_ready, ready, over_ready]
DoR Blockers:                  list[string] (what prevents readiness)
```

### 10.4 Definition of Done Attributes

```
Acceptance Criteria:           list[{
                                 id: string,
                                 description: string,
                                 is_met: boolean,
                                 verified_by: string,
                                 verified_at: datetime
                               }]
Code Review Status:            enum [not_started, in_review, approved, rejected]
Code Review By:                string (reviewer user ID)
Code Review Date:              datetime
Unit Test Coverage:            float (0.0-100.0, code coverage %)
Minimum Coverage Requirement:  float (default 80%)
Unit Tests Pass:               boolean
Integration Tests Pass:        boolean
Performance Tests Pass:        boolean (if applicable)
Security Scan Complete:        boolean
Security Scan Results:         enum [pass, fail, needs_review]
Regression Tests Pass:         boolean (if applicable)
Documentation Complete:        boolean
Documentation Type:            list[string] (README, API docs, user guide, etc.)
QA Sign Off:                   boolean
QA Sign Off By:                string (QA person ID)
QA Sign Off Date:              datetime
Business Owner Sign Off:       boolean
Business Owner ID:             string
Business Owner Sign Off Date:  datetime
Release Notes Updated:         boolean
Is Shippable:                  boolean (all DoD items complete)
DoD Status:                    enum [not_done, partially_done, done, over_done]
DoD Score:                     float (0.0-100.0)
DoD Blockers:                  list[string] (what prevents completion)
Completion Date:               datetime
```

### 10.5 Data Model Structure

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum

class DoRStatus(str, Enum):
    NOT_READY = "not_ready"
    PARTIALLY_READY = "partially_ready"
    READY = "ready"
    OVER_READY = "over_ready"

class DoDStatus(str, Enum):
    NOT_DONE = "not_done"
    PARTIALLY_DONE = "partially_done"
    DONE = "done"
    OVER_DONE = "over_done"

@dataclass
class DefinitionOfReady:
    item_id: str
    is_requirement_clear: bool
    has_acceptance_criteria: bool
    acceptance_criteria_count: int
    are_dependencies_resolved: bool
    unresolved_dependency_ids: List[str] = field(default_factory=list)
    resources_assigned: bool = False
    estimated_effort_hours: Optional[float] = None
    estimated_duration_days: Optional[int] = None
    risk_assessment_complete: bool = False
    dor_score: float = 0.0
    status: DoRStatus = DoRStatus.NOT_READY
    blockers: List[str] = field(default_factory=list)
    assessed_by: Optional[str] = None
    assessed_at: Optional[datetime] = None

    @property
    def is_ready(self) -> bool:
        return self.status == DoRStatus.READY

@dataclass
class AcceptanceCriterion:
    id: str
    description: str
    is_met: bool
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None

@dataclass
class DefinitionOfDone:
    item_id: str
    acceptance_criteria: List[AcceptanceCriterion]
    code_review_status: str                    # "not_started", "approved", "rejected"
    unit_test_coverage_percent: float
    unit_tests_pass: bool
    integration_tests_pass: bool
    security_scan_pass: bool
    documentation_complete: bool
    qa_sign_off: bool
    business_owner_sign_off: bool
    dod_score: float = 0.0
    status: DoDStatus = DoDStatus.NOT_DONE
    blockers: List[str] = field(default_factory=list)
    is_shippable: bool = False
    completion_date: Optional[datetime] = None

    @property
    def criteria_met_count(self) -> int:
        return sum(1 for c in self.acceptance_criteria if c.is_met)

    @property
    def is_done(self) -> bool:
        return (self.status == DoDStatus.DONE and
                self.is_shippable and
                len(self.blockers) == 0)
```

---

## 11. Comprehensive Task Specification Schema

### 11.1 Task Core Attributes

Integrating all previous sections into a unified Task entity.

```
=== IDENTIFICATION ===
Task ID:                       string (UUID)
Task Number:                   string (human-readable, e.g., "TASK-1234")
Project ID:                    string (parent project)
Title:                         string (max 500 chars)
Description:                  text (detailed scope)
Task Type:                     enum [feature, bug, task, subtask, epic, story, spike]

=== HIERARCHY & RELATIONSHIPS ===
Parent Task:                   string (task ID if subtask)
Child Tasks:                   list[string] (task IDs)
Work Package ID:               string (WBS work package)
WBS Code:                      string (e.g., "1.2.3")
Control Account ID:            string
Epic ID:                       string (if part of epic)
Related Items:                 list[string] (traceability)

=== OWNERSHIP & ASSIGNMENT ===
Owner:                         string (person responsible)
Assigned To:                   string (resource doing work)
Secondary Owner:               string (optional backup)
Team:                          string (team ID)
Created By:                    string (user ID)
Created Date:                  datetime
Last Modified By:              string
Last Modified Date:            datetime

=== STATUS & WORKFLOW ===
Status:                        enum (Kanban state)
Status History:                list[StateTransition]
Priority:                      enum [critical, high, medium, low]
Severity (if defect):          enum [blocker, critical, major, minor, trivial]
Is Blocked:                    boolean
Blockers:                      list[BlockerReference]
Depends On:                    list[DependencyReference]
Blocks:                        list[DependencyReference]

=== SCHEDULE (TRADITIONAL PM) ===
Planned Start:                 datetime
Planned Finish:                datetime
Planned Duration Days:         integer
Early Start:                   datetime (CPM calculated)
Early Finish:                  datetime
Late Start:                    datetime
Late Finish:                   datetime
Actual Start:                  datetime (nullable)
Actual Finish:                 datetime (nullable)
Actual Duration Days:          integer (nullable)
Remaining Duration Days:       integer (for in-progress)
Total Float/Slack:             float
Free Float:                    float
Is Critical Task:              boolean
Critical Path IDs:             list[string]
Schedule Variance:             float (days)
Schedule Variance %:           float
Current Schedule Status:       enum [on_schedule, ahead, behind]

=== EFFORT & ESTIMATION (AGILE/PERT) ===
Story Points:                  integer (Scrum estimate)
T-Shirt Size:                  enum [xs, s, m, l, xl, xxl] (alternative)
Optimistic Estimate:           integer (PERT: days/hours)
Most Likely Estimate:          integer
Pessimistic Estimate:          integer
Expected Duration:             float (PERT calculated)
Standard Deviation:            float
Confidence Level:              enum [high, medium, low]
Estimated Hours:               float
Estimated Days:                integer
Effort Estimation Source:      enum [historical, expert, simulation, statistical]
Total Effort Hours:            float (sum of all resource allocations)
Duration/Effort Ratio:         float
```

### 11.2 Resource & Allocation

```
=== RESOURCE ALLOCATION ===
Primary Resource:              string (person ID)
Primary Resource Hours/Week:   float
Secondary Resources:           list[{person_id: string, hours: float}]
Required Skills:               list[{skill: string, level: enum}]
Resource Allocation Type:      enum [dedicated, shared, on_demand]
Resource Availability:         dict[date_range: string, hours: float]
Total Allocated Hours:         float (sum of all allocations)
Average Person-Hours:          float (total_effort / person_count)

=== COST ===
Estimated Cost:                decimal
Actual Cost To Date:           decimal
Cost Variance:                 decimal
Budget Category:               string
Cost Code:                     string
Billable:                      boolean
Billing Rate:                  decimal ($/hour)
Total Billable Amount:         decimal
```

### 11.3 Quality & Testing

```
=== QUALITY & ACCEPTANCE ===
Definition of Ready (DoR) Status: enum
DoR Score:                     float (0.0-100.0)
DoR Blockers:                  list[string]
Definition of Done (DoD) Status: enum
DoD Score:                     float
DoD Blockers:                  list[string]
Acceptance Criteria:           list[{criteria: string, met: bool, verified_by: str}]
Acceptance Criteria Met:       integer (count)
Acceptance Criteria Total:     integer
All Criteria Met:              boolean
Is Shippable:                  boolean

=== TESTING & VERIFICATION ===
Test Cases Assigned:           list[string] (test case IDs)
Test Cases Passing:            integer
Test Cases Failing:            integer
Test Cases Skipped:            integer
Overall Test Status:           enum [not_tested, passing, failing, blocked]
Code Review Required:          boolean
Code Review Status:            enum [not_started, in_review, approved, rejected]
Code Review By:                string
Code Review Comments:          text
Code Coverage:                 float (0.0-100.0, code coverage %)
Minimum Coverage Required:     float
Coverage Acceptable:           boolean

=== QUALITY METRICS ===
Defect Count (Open):           integer
Defect Count (Closed):         integer
Defect Density:                float (defects per KLOC or per function point)
Code Churn:                    integer (lines changed in last N days)
Complexity Score:              float (McCabe/cyclomatic complexity)
Technical Debt Score:          float (SonarQube or similar)
Security Issues:               integer
Performance Issues:            integer
```

### 11.4 Risk & Contingency

```
=== RISK MANAGEMENT ===
Risk Level:                    enum [critical, high, medium, low, minimal]
Associated Risks:              list[string] (risk IDs)
Risk Probability:              float (0.0-1.0)
Risk Impact:                   enum [delay, cost_increase, quality_issue, scope_change]
Risk Impact Days:              integer (schedule impact)
Risk Impact Cost:              decimal
Risk Mitigation Plan:          text
Risk Owner:                    string (person responsible)
Residual Risk Score:           float (after mitigation)

=== CONTINGENCY ===
Schedule Contingency Days:     integer (buffer in duration)
Cost Contingency:              decimal (budget buffer)
Contingency Burn Rate:         decimal (consumption rate)
Contingency Remaining:         decimal/integer
Contingency Utilization:       float (% used)
```

### 11.5 Progress & Tracking

```
=== PROGRESS TRACKING ===
Percent Complete (Physical):   float (0.0-100.0)
Percent Complete (EV):         float (Earned Value based)
Progress Status:               enum [on_track, at_risk, off_track]
Last Status Update:            datetime
Status Update By:              string
Status Update Notes:           text
Milestone:                     string (optional milestone ID)

=== EVM METRICS ===
Planned Value (PV):            decimal (budgeted cost)
Earned Value (EV):             decimal (% complete × budget)
Actual Cost (AC):              decimal
Cost Variance:                 decimal (EV - AC)
Schedule Variance:             decimal (EV - PV)
Cost Performance Index:        float (EV/AC)
Schedule Performance Index:    float (EV/PV)
Estimate at Completion (EAC):  decimal
Estimate to Complete (ETC):    decimal
Variance at Completion (VAC):  decimal

=== ACTIVITY LOGGING ===
Time Entries:                  list[TimesheetEntry]
Total Time Logged:             float (hours)
Billable Time:                 float (hours)
Non-Billable Time:             float (hours)
Time Logging Status:           enum [complete, incomplete, over_budget]
```

### 11.6 Dependencies & Links

```
=== DEPENDENCY MANAGEMENT ===
Predecessor Tasks:             list[{task_id: string, type: enum, lag: int}]
Successor Tasks:               list[{task_id: string, type: enum, lag: int}]
External Dependencies:         list[{source: string, description: string}]
Is External Task:              boolean
External Source:               string

=== TRACEABILITY ===
Related Requirements:          list[string] (requirement IDs)
Related Design Docs:           list[string] (document IDs)
Related Test Cases:            list[string] (test IDs)
Related Issues/Defects:        list[string] (defect IDs)
Related ADRs:                  list[string] (architecture decision records)
Related Contracts:             list[string]
Related Risks:                 list[string] (risk IDs)
Bidirectional Links:           list[{linked_item: string, link_type: string}]

=== ARTIFACTS & DOCUMENTATION ===
Attached Documents:            list[{file_id: string, filename: string, type: string}]
Acceptance Document:           string (file ID)
Test Plan Reference:           string (document ID)
Implementation Notes:          text
Lessons Learned:               text
```

### 11.7 Audit & Metadata

```
=== VERSION CONTROL ===
Version Number:                integer (optimistic locking)
Last Modified:                 datetime
Change Log:                    list[{changed_at: datetime, changed_by: string,
                                    field: string, old_value: object, new_value: object}]
Soft Delete:                   boolean (deleted_at datetime if soft deleted)

=== COMPLIANCE & GOVERNANCE ===
Compliance Requirements:       list[string]
Regulatory Tags:               list[string]
Data Classification:           enum [public, internal, confidential, restricted]
Audit Trail Enabled:           boolean
Approval Status:               enum [pending, approved, rejected, deferred]
Approved By:                   string
Approval Date:                 datetime
Sign-Off Required:             boolean
Sign-Off By:                   string
Sign-Off Date:                 datetime

=== CUSTOM METADATA ===
Metadata:                      dict[string, object] (flexible extension)
Custom Fields:                 dict[string, object]
Tags:                          list[string]
Custom Attributes:            dict[string, object]
```

---

## 12. Task Specification JSON Example

```json
{
  "id": "TASK-2847",
  "project_id": "PROJ-001",
  "title": "Implement User Authentication Module",
  "description": "Create OAuth2 authentication system with JWT token support and LDAP integration",

  "hierarchy": {
    "parent_task": "EPIC-156",
    "wbs_code": "3.2.1",
    "work_package_id": "WP-89"
  },

  "ownership": {
    "owner": "alice@company.com",
    "assigned_to": "bob@company.com",
    "team": "BACKEND-TEAM",
    "created_by": "alice@company.com",
    "created_date": "2026-01-15T09:00:00Z"
  },

  "status": {
    "current_state": "in_progress",
    "priority": "high",
    "is_blocked": false,
    "schedule_status": "on_schedule"
  },

  "schedule": {
    "planned_start": "2026-01-20",
    "planned_finish": "2026-02-15",
    "planned_duration_days": 20,
    "actual_start": "2026-01-20",
    "actual_finish": null,
    "actual_duration_days": null,
    "early_start": "2026-01-20",
    "early_finish": "2026-02-09",
    "late_start": "2026-01-27",
    "late_finish": "2026-02-15",
    "total_float_days": 6,
    "free_float_days": 0,
    "is_critical_task": false,
    "schedule_variance_days": -1.5,
    "current_schedule_status": "ahead"
  },

  "estimation": {
    "story_points": 21,
    "optimistic_estimate_days": 14,
    "most_likely_estimate_days": 18,
    "pessimistic_estimate_days": 25,
    "expected_duration_days": 18.5,
    "standard_deviation": 1.83,
    "estimated_hours": 156,
    "confidence_level": "high"
  },

  "resources": {
    "primary_resource": "bob@company.com",
    "primary_resource_hours_per_week": 40,
    "required_skills": [
      {"skill": "Python", "level": "advanced"},
      {"skill": "OAuth2", "level": "intermediate"},
      {"skill": "JWT", "level": "intermediate"}
    ],
    "total_allocated_hours": 156
  },

  "quality": {
    "definition_of_ready": {
      "status": "ready",
      "score": 95.0,
      "blockers": []
    },
    "definition_of_done": {
      "status": "in_progress",
      "score": 40.0,
      "acceptance_criteria_met": 3,
      "acceptance_criteria_total": 7,
      "blockers": ["Review not complete"]
    },
    "acceptance_criteria": [
      {"criteria": "OAuth2 flow implemented", "met": true},
      {"criteria": "JWT tokens generated/validated", "met": true},
      {"criteria": "LDAP integration complete", "met": false},
      {"criteria": "Unit tests > 80% coverage", "met": false},
      {"criteria": "Code review approved", "met": false},
      {"criteria": "Security scan passed", "met": false},
      {"criteria": "Documentation complete", "met": false}
    ],
    "test_cases_passing": 12,
    "test_cases_failing": 2,
    "code_coverage_percent": 72.5
  },

  "risk": {
    "risk_level": "medium",
    "associated_risks": ["RISK-34", "RISK-89"],
    "risk_probability": 0.35,
    "risk_impact": "delay",
    "risk_impact_days": 5,
    "risk_mitigation_plan": "Pair program with security expert for OAuth2 implementation",
    "contingency_schedule_days": 3
  },

  "progress": {
    "percent_complete_physical": 45.0,
    "percent_complete_evm": 42.3,
    "progress_status": "on_track",
    "last_status_update": "2026-01-28T14:30:00Z",
    "status_update_notes": "LDAP integration on track, OAuth2 flow 90% complete"
  },

  "evm": {
    "planned_value": 8400.00,
    "earned_value": 7560.00,
    "actual_cost": 7200.00,
    "cost_variance": 360.00,
    "schedule_variance": -840.00,
    "cost_performance_index": 1.05,
    "schedule_performance_index": 0.90,
    "estimate_at_completion": 9333.33,
    "estimate_to_complete": 2133.33
  },

  "dependencies": {
    "predecessor_tasks": [
      {"task_id": "TASK-2846", "type": "fs", "lag": 0}
    ],
    "successor_tasks": [
      {"task_id": "TASK-2848", "type": "fs", "lag": 2}
    ],
    "external_dependencies": [
      {"source": "IT-Infrastructure", "description": "LDAP server configuration"}
    ]
  },

  "traceability": {
    "related_requirements": ["REQ-234", "REQ-235", "REQ-236"],
    "related_test_cases": ["TC-891", "TC-892", "TC-893"],
    "related_risks": ["RISK-34", "RISK-89"]
  },

  "metadata": {
    "custom_fields": {
      "security_review_required": true,
      "compliance_framework": "GDPR"
    },
    "tags": ["authentication", "security", "backend", "oauth2"]
  }
}
```

---

## 13. Comparative Analysis: Agile vs. Traditional PM Attributes

### 13.1 Feature Comparison Matrix

| Attribute | Agile/Scrum | Kanban | Traditional/Waterfall | Comments |
|-----------|-------------|--------|----------------------|----------|
| Story Points | Primary | Optional | Not used | Agile estimation method |
| CPM Dates | Rarely used | Optional | Essential | Traditional schedule control |
| PERT Estimates | Secondary | Minimal | Optional | Handles uncertainty |
| Work Packages | Minimal | Minimal | Essential | WBS decomposition |
| Control Accounts | No | No | Essential | Cost management |
| DoR Checklist | Essential | Recommended | Not typical | Agile quality gate |
| DoD Checklist | Essential | Essential | Optional | Acceptance criteria |
| Blocker Tracking | Recommended | Essential | Recommended | Impediment removal |
| Dependency Types | Simplified | Simplified | All 4 types | CPM requirement |
| Risk Matrix | Recommended | Recommended | Essential | Risk management |
| EVM Tracking | Optional | Optional | Essential | Cost/schedule integration |
| Time Tracking | Minimal | Minimal | Essential | Cost accounting |
| State Machine | 4-5 states | Flexible | 8-12 states | Workflow formality |
| Critical Path | Not used | Not used | Essential | Schedule optimization |
| Contingency Reserve | Not typical | Not typical | Essential | Risk buffer |
| Milestone-based | No | Optional | Essential | Formal gate reviews |

---

## 14. Implementation Recommendations

### 14.1 Phased Implementation Approach

**Phase 1: Core Entities (Weeks 1-4)**
- Implement base Task entity with identification, status, ownership, schedule
- Create State Machine enumeration and transition rules
- Implement basic dependency model (4 types)
- Add time tracking for effort capture

**Phase 2: Estimation & Planning (Weeks 5-8)**
- Add CPM attributes and calculation service
- Implement PERT estimation model
- Add WBS and Control Account entities
- Create resource allocation model

**Phase 3: Quality & Readiness (Weeks 9-12)**
- Implement DoR assessment engine
- Implement DoD checklist and verification
- Add acceptance criteria tracking
- Create verification status workflows

**Phase 4: Risk & EVM (Weeks 13-16)**
- Implement risk-task association model
- Add EVM calculation service (PV, EV, AC, CPI, SPI, EAC)
- Implement contingency allocation
- Create risk mitigation task linking

**Phase 5: Analytics & Reporting (Weeks 17-20)**
- Create critical path calculation service
- Implement schedule variance analysis
- Build EVM reporting dashboard
- Create risk exposure reporting

### 14.2 Database Schema Recommendations

```sql
-- Core task table with optimistic locking
CREATE TABLE tasks (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(50),
    owner VARCHAR(255),
    assigned_to VARCHAR(255),
    planned_start TIMESTAMP,
    planned_finish TIMESTAMP,
    planned_duration_days INT,
    actual_start TIMESTAMP,
    actual_finish TIMESTAMP,
    percent_complete FLOAT,
    version INT DEFAULT 1,  -- Optimistic locking
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,

    -- JSON columns for flexible attributes
    task_metadata JSON,  -- CPM, PERT, risk, EVM data

    FOREIGN KEY (project_id) REFERENCES projects(id),
    INDEX idx_project_status (project_id, status),
    INDEX idx_owner (owner),
    INDEX idx_assigned_to (assigned_to)
);

-- Dependency table
CREATE TABLE dependencies (
    id VARCHAR(255) PRIMARY KEY,
    from_task_id VARCHAR(255) NOT NULL,
    to_task_id VARCHAR(255) NOT NULL,
    dependency_type VARCHAR(10) NOT NULL,  -- fs, ss, ff, sf
    lag_days INT DEFAULT 0,
    is_critical BOOLEAN,
    strength VARCHAR(20),  -- hard, soft, external

    FOREIGN KEY (from_task_id) REFERENCES tasks(id),
    FOREIGN KEY (to_task_id) REFERENCES tasks(id),
    UNIQUE KEY unique_dependency (from_task_id, to_task_id, dependency_type),
    INDEX idx_from_task (from_task_id),
    INDEX idx_to_task (to_task_id)
);

-- Time entries
CREATE TABLE time_entries (
    id VARCHAR(255) PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL,
    resource_id VARCHAR(255) NOT NULL,
    entry_date DATE NOT NULL,
    hours_worked FLOAT,
    billable BOOLEAN,
    status VARCHAR(50),

    FOREIGN KEY (task_id) REFERENCES tasks(id),
    INDEX idx_task_date (task_id, entry_date)
);

-- State transition history
CREATE TABLE task_state_history (
    id VARCHAR(255) PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL,
    from_state VARCHAR(50),
    to_state VARCHAR(50),
    transitioned_at TIMESTAMP,
    transitioned_by VARCHAR(255),
    reason TEXT,

    FOREIGN KEY (task_id) REFERENCES tasks(id),
    INDEX idx_task_history (task_id, transitioned_at)
);

-- Blockers
CREATE TABLE blockers (
    id VARCHAR(255) PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    description TEXT,
    status VARCHAR(50),  -- open, in_resolution, resolved
    severity VARCHAR(20),
    created_at TIMESTAMP,
    resolved_at TIMESTAMP,
    assigned_to VARCHAR(255),

    FOREIGN KEY (task_id) REFERENCES tasks(id),
    INDEX idx_task_blockers (task_id, status)
);
```

### 14.3 Calculation Services

```python
# pseudo-code

class CPMCalculationService:
    def calculate_critical_path(self, task_graph):
        """Forward pass to calculate ES/EF, backward pass for LS/LF"""
        pass

    def calculate_slack(self, task):
        """Slack = LF - EF"""
        pass

class PERTService:
    def calculate_expected_duration(self, optimistic, most_likely, pessimistic):
        return (optimistic + 4*most_likely + pessimistic) / 6

    def calculate_variance(self, optimistic, pessimistic):
        return ((pessimistic - optimistic) / 6) ** 2

class EVMCalculationService:
    def calculate_metrics(self, planned_value, earned_value, actual_cost, bac):
        return {
            'cost_variance': earned_value - actual_cost,
            'schedule_variance': earned_value - planned_value,
            'cpi': earned_value / actual_cost,
            'spi': earned_value / planned_value,
            'eac': bac / (earned_value / actual_cost),
            'etc': (bac / (earned_value / actual_cost)) - actual_cost,
            'vac': bac - eac
        }

class DoRAssessmentService:
    def assess_readiness(self, task):
        """Evaluate task against DoR criteria"""
        score = 0
        blockers = []

        if not task.title or len(task.title) < 10:
            blockers.append("Title too short or missing")
        else:
            score += 10

        # ... check other criteria

        return {
            'score': score,
            'status': 'ready' if score >= 90 else 'not_ready',
            'blockers': blockers
        }

class DoDVerificationService:
    def verify_completion(self, task):
        """Verify task against DoD criteria"""
        criteria_met = 0
        criteria_total = len(task.acceptance_criteria)

        for criterion in task.acceptance_criteria:
            if criterion.is_met:
                criteria_met += 1

        score = (criteria_met / criteria_total * 100) if criteria_total > 0 else 0

        return {
            'score': score,
            'status': 'done' if score == 100 else 'in_progress',
            'criteria_met': criteria_met,
            'criteria_total': criteria_total
        }
```

---

## 15. Key Implementation Insights

### 15.1 Metadata Strategy

Rather than creating 200+ database columns, use a **tiered metadata approach**:

1. **Core Columns**: Essential, frequently queried attributes (30-40)
2. **Indexed JSON**: CPM data, PERT estimates, EVM metrics (as JSON in task_metadata)
3. **Audit Trail**: State history, approval records, change log (separate table)
4. **Flexible Extension**: Custom fields and tags (separate custom_attributes table)

### 15.2 State Machine Implementation

Use **explicit state transition rules** rather than allowing arbitrary transitions:

```python
TRANSITIONS = {
    'not_started': ['planning', 'cancelled'],
    'planning': ['ready', 'cancelled'],
    'ready': ['in_progress', 'blocked', 'cancelled'],
    'in_progress': ['blocked', 'under_review', 'cancelled'],
    'blocked': ['in_progress', 'cancelled'],
    'under_review': ['in_progress', 'testing', 'cancelled'],
    'testing': ['in_progress', 'completed', 'cancelled'],
    'completed': ['archived'],
}
```

### 15.3 CPM vs. Agile Hybrid

Support both simultaneously:
- Traditional teams use CPM for critical path analysis
- Agile teams can optionally enable CPM for dependencies longer than sprint
- Unified status reporting for mixed-mode projects

### 15.4 Risk Exposure Scoring

Create bidirectional risk-task linking:
```
Task Risk Exposure = Σ(Risk_i.probability × Task Impact_i)
Risk Task Impact = Σ(Task_j.criticality × Risk_i.impact)
```

---

## Conclusion

This comprehensive specification provides **180+ attributes** organized across **15 entity types** supporting both agile and traditional project management methodologies. The patterns follow industry standards (IEEE 1490 for WBS, PMBOK for PM terminology, ISO 21500 for governance) while remaining flexible for customization.

Implementation should follow a phased approach, starting with core task management and progressing through advanced features like CPM calculations and EVM tracking. The metadata strategy allows extensibility without database redesign, and calculation services can be incrementally added as organizational maturity increases.


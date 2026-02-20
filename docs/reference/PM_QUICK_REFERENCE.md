# Project Management Patterns - Quick Reference Guide

## 1. Core Attribute Counts by Domain

| Domain | Core Attributes | Calculated Fields | Metadata Fields | Total |
|--------|-----------------|-------------------|-----------------|-------|
| CPM (Schedule) | 18 | 8 | 2 | 28 |
| PERT (Estimation) | 5 | 7 | 1 | 13 |
| WBS Structure | 7 | 3 | 2 | 12 |
| Resource Allocation | 6 | 3 | 1 | 10 |
| Time Tracking | 8 | 2 | 1 | 11 |
| Task State Machine | 5 | 2 | 1 | 8 |
| EVM Metrics | 6 | 7 | 1 | 14 |
| Risk Management | 8 | 2 | 2 | 12 |
| Dependencies | 6 | 2 | 1 | 9 |
| Quality (DoR/DoD) | 10 | 4 | 1 | 15 |
| **TOTAL** | **83** | **40** | **15** | **138** |

*Note: Actual Task model shown in implementations has ~70 database columns + flexible JSON metadata*

---

## 2. Status Progression by Methodology

### Traditional (Waterfall) - 10 States
```
NOT_STARTED → PLANNING → READY → IN_PROGRESS → BLOCKED ↔
UNDER_REVIEW → TESTING → COMPLETED → ARCHIVED
                    ↓
                  CANCELLED (anytime)
```

**Typical Duration**: 4-12 weeks per task
**Reviews**: Gate reviews after each phase
**Testing**: Separate phase before completion

### Agile (Scrum) - 5 States
```
BACKLOG → READY → IN_PROGRESS → IN_REVIEW → DONE → CANCELLED
```

**Typical Duration**: 1-2 weeks (sprint)
**Reviews**: Daily standups, sprint review
**Testing**: Integrated throughout

### Hybrid (Mixed) - 8 States
```
BACKLOG → PLANNING → READY → IN_PROGRESS → IN_REVIEW →
TESTING → COMPLETED → ARCHIVED
                    ↓
              BLOCKED / CANCELLED
```

**Typical Duration**: Variable by component
**Reviews**: Sprint reviews + gate reviews for complex items
**Testing**: Both integrated and phase-based

---

## 3. Dependency Matrices by Type

### Finish-Start (FS) - 90% of Projects
```
Predecessor: ═══════════╗
            Finish     Start (Successor)
                          ╚════════════════════════
                          (Successor): ═════════════════╗

Lag = 2 days means 2-day gap between predecessor finish and successor start
```
**Use Case**: Sequential work (design → development → testing)

### Start-Start (SS) - 7% of Projects
```
Predecessor: ╔════════════════╗
            Start (both)
                    ║
Successor:  ╚══════════════════╗

Lag = 3 days means successor starts 3 days after predecessor starts
```
**Use Case**: Parallel work with offset (documentation can start after design starts)

### Finish-Finish (FF) - 2% of Projects
```
Predecessor: ═══════════╗
            Finish (both)
                    ║
Successor:  ╚════════════════════╗

Lag = 0 means both finish at same time
```
**Use Case**: Coordinated completion (testing and documentation finish together)

### Start-Finish (SF) - <1% of Projects
```
Predecessor: ╔═══════════╗
            Start
            Triggers →
Successor:        ╚═══════════════╗
                            Finish

Used in rare just-in-time scenarios
```

---

## 4. PERT Estimation Formula Sheet

### Basic Calculations
```
Expected Duration (E) = (O + 4M + P) / 6

Standard Deviation (σ) = (P - O) / 6

Variance (σ²) = [(P - O) / 6]²

Coefficient of Variation = σ / E

Range (68% confidence) = E ± 1σ
Range (95% confidence) = E ± 1.96σ
Range (99% confidence) = E ± 2.576σ
```

### Example
```
Task: Implement Authentication
O = 10 days (optimistic)
M = 15 days (most likely)
P = 30 days (pessimistic)

E = (10 + 4(15) + 30) / 6 = 16.67 days
σ = (30 - 10) / 6 = 3.33 days
σ² = 11.11 days²
CV = 3.33 / 16.67 = 0.20 (20% uncertainty)

68% Range: 13.34 - 20.00 days
95% Range: 10.01 - 23.33 days
```

---

## 5. CPM Calculation Quick Steps

### Step 1: Build Network Diagram
- Identify all tasks
- Determine dependencies
- Create directed acyclic graph (DAG)

### Step 2: Forward Pass (Calculate ES/EF)
```
For each task:
  ES = Max(EF of all predecessors) or 0 if no predecessors
  EF = ES + Duration
```

### Step 3: Backward Pass (Calculate LS/LF)
```
For each task (reverse order):
  LF = Min(LS of all successors) or project finish if no successors
  LS = LF - Duration
```

### Step 4: Calculate Float
```
Total Float = LF - EF = LS - ES
Free Float = Min(ES of successors) - EF
```

### Step 5: Identify Critical Path
```
Tasks with Total Float = 0 are on critical path
Critical Path = Longest path through network
```

### Example Network
```
Task  Duration  Predecessors  ES  EF  LS  LF  Float  Critical?
A     5         -             0   5   0   5   0      YES
B     8         A             5   13  5   13  0      YES
C     3         A             5   8   10  13  5      NO
D     4         B,C           13  17  13  17  0      YES
E     2         D             17  19  17  19  0      YES

Project Duration: 19 days
Critical Path: A → B → D → E
```

---

## 6. EVM Dashboard Indicators

### Status Interpretation
```
CPI > 1.0:  Under budget (good)
CPI = 1.0:  On budget (expected)
CPI < 1.0:  Over budget (issue)

SPI > 1.0:  Ahead of schedule (good)
SPI = 1.0:  On schedule (expected)
SPI < 1.0:  Behind schedule (issue)

EAC < BAC:  Project will finish under budget
EAC = BAC:  Project will finish on budget
EAC > BAC:  Project will finish over budget
```

### Typical Project Profiles
```
Healthy Project:
  CPI = 1.02, SPI = 1.05, EAC < BAC
  ✓ Ahead of schedule and under budget

At Risk Project:
  CPI = 0.95, SPI = 0.92, EAC > BAC
  ⚠ Behind schedule and over budget (action needed)

Optimistic Project:
  CPI = 1.15, SPI = 1.20, EAC << BAC
  ? May have slack in estimates or team is highly efficient

Pessimistic Project:
  CPI = 0.85, SPI = 0.80, EAC >> BAC
  ⚠ High risk, likely to need scope reduction or timeline extension
```

---

## 7. Definition of Ready (DoR) Checklist

### Minimum (40 points) - Required
- [ ] Title clear and complete (5 pts)
- [ ] Description detailed with acceptance criteria (10 pts)
- [ ] Effort estimated (10 pts)
- [ ] Dependencies identified (5 pts)
- [ ] Resource assigned (5 pts)
- [ ] Product owner approved (5 pts)

### Standard (70 points) - Recommended
- All Minimum items (40 pts)
- [ ] Test cases defined (5 pts)
- [ ] Design specifications linked (5 pts)
- [ ] Risk assessment completed (5 pts)
- [ ] Security requirements identified (5 pts)
- [ ] Performance requirements specified (5 pts)

### Advanced (90+ points) - Excellence
- All Standard items (70 pts)
- [ ] Mockups/prototypes reviewed (5 pts)
- [ ] Database schema defined (5 pts)
- [ ] API contracts defined (5 pts)
- [ ] Documentation plan created (5 pts)
- [ ] Stakeholder sign-off (5 pts)

---

## 8. Definition of Done (DoD) Checklist

### Code (30 points)
- [ ] Code written per standards (10 pts)
- [ ] Code reviewed and approved (10 pts)
- [ ] No merge conflicts (5 pts)
- [ ] Merged to main/release branch (5 pts)

### Testing (30 points)
- [ ] Unit tests written (>80% coverage) (10 pts)
- [ ] Test cases executed and passing (10 pts)
- [ ] No critical defects open (5 pts)
- [ ] Regression tests passing (5 pts)

### Quality (20 points)
- [ ] Documentation updated (5 pts)
- [ ] Security scan passed (5 pts)
- [ ] Performance requirements met (5 pts)
- [ ] Code review comments resolved (5 pts)

### Acceptance (20 points)
- [ ] All acceptance criteria met (10 pts)
- [ ] Business owner sign-off (5 pts)
- [ ] Ready for deployment (5 pts)

**Task is DONE when ALL items ✓ and score = 100**

---

## 9. Risk Scoring Matrix

### Impact Scale
```
5 = Critical: Project cannot succeed
4 = High: Major impact on schedule/cost/quality
3 = Medium: Noticeable impact, workaround possible
2 = Low: Minor impact, easily managed
1 = Minimal: Almost no impact
```

### Probability Scale
```
0.9 = Almost certain (>80%)
0.7 = Likely (60-80%)
0.5 = Medium (40-60%)
0.3 = Unlikely (20-40%)
0.1 = Very unlikely (<20%)
```

### Risk Score = Probability × Impact
```
Score  Risk Level  Action
14-25  CRITICAL   Mitigate immediately, escalate, have backup plan
8-13   HIGH       Mitigate aggressively, monitor closely
4-7    MEDIUM     Monitor, develop mitigation plan
2-3    LOW        Accept or monitor
1      MINIMAL    Accept, no action needed
```

### Example Risk Assessment
```
Risk: "OAuth2 integration delayed by 3rd-party provider"
Probability: 0.4 (some chance)
Impact: 4 (blocks multiple features)
Score: 1.6 = LOW risk (0.4 × 4)

Mitigation:
- Contact provider early (reduce probability)
- Develop fallback authentication (reduce impact)
- Monitor provider's timeline weekly (tracking)
```

---

## 10. Blocker Severity & Escalation

### Severity Classification
```
CRITICAL: Project cannot progress at all
  → Escalate immediately to sponsor
  → Max resolution time: 4 hours
  → Daily updates required

HIGH: Major feature blocked, workaround limited
  → Escalate to PM if open > 2 days
  → Max resolution time: 2 days
  → Updates every morning

MEDIUM: Progress slowed, workaround available
  → Escalate to PM if open > 5 days
  → Max resolution time: 5 days
  → Updates twice per week

LOW: Minor inconvenience
  → Escalate if open > 10 days
  → Max resolution time: 10 days
  → Weekly updates
```

### Resolution Tracking
```
BLOCKER CREATED
    ↓
Daily monitoring & escalation per severity
    ↓
ROOT CAUSE IDENTIFIED → RESOLUTION PLAN
    ↓
RESOLUTION IMPLEMENTED & VERIFIED
    ↓
BLOCKER RESOLVED
    ↓
PREVENTION MEASURES DOCUMENTED
```

---

## 11. Resource Allocation Patterns

### Allocation Types
```
DEDICATED: 100% allocation to task
  ✓ Minimal context switching
  ✓ Fast delivery
  ✗ Resource not flexible
  → Use for: Critical path, blocking tasks

SHARED: 50-75% allocation to task
  ✓ Resource flexibility
  ✓ Skill reuse across tasks
  ✗ Context switching overhead
  → Use for: Normal tasks, lower priority work

ON-DEMAND: 10-30% allocation, as needed
  ✓ Specialized skills used efficiently
  ✓ High resource flexibility
  ✗ Can cause delays if not available
  → Use for: Expert consultation, reviews

UNALLOCATED: 0% allocation
  ✓ Resource available for other work
  ✗ Task has no owner
  → Avoid: Always assign someone
```

### Overallocation Thresholds
```
Utilization     Status      Action
0-80%          Healthy      OK, can take more work
80-100%        Optimal      At capacity, careful with new work
100-120%       Overallocated Alert PM, prioritize, may need help
>120%          Critical     Immediate intervention needed
```

---

## 12. Common Pitfalls & Solutions

### CPM Pitfalls
```
PITFALL: Forgot dependencies
SOLUTION: Review all predecessor/successor relationships twice
          Use network diagram tool (Visio, SmartDraw)

PITFALL: Pessimistic time estimates
SOLUTION: Use PERT (3-point) for uncertainty
          Review historical data

PITFALL: No buffer for external dependencies
SOLUTION: Add lag/contingency for external tasks
          Escalate communication with external parties

PITFALL: Ignoring non-critical tasks
SOLUTION: Monitor free float, it can become critical
          Watch for float erosion
```

### PERT Pitfalls
```
PITFALL: Not enough confidence in optimistic estimate
SOLUTION: Define optimistic as "best case, realistic" not "miracle"
          Expert review of all three estimates

PITFALL: Using same estimates for all types of work
SOLUTION: Vary estimates by task type and complexity
          Collect historical data

PITFALL: Not updating estimates during execution
SOLUTION: Review PERT quarterly
          Adjust if new information emerges
```

### Risk Management Pitfalls
```
PITFALL: Identifying risks but not owning mitigation
SOLUTION: Assign risk owner for each risk
          Track mitigation tasks like regular tasks

PITFALL: Ignoring low-probability, high-impact risks
SOLUTION: Map all risks even if probability < 20%
          Have contingency plans for tail risks

PITFALL: Not updating risk register
SOLUTION: Review risks monthly minimum
          Retire closed risks, add new ones
```

---

## 13. Integration Patterns

### CPM + Agile Hybrid
```
- Use sprints for execution (1-2 week cycles)
- Use CPM for dependencies longer than sprint
- Track critical path items specially
- Report EVM metrics with standard metrics
- DoR/DoD apply to all items regardless of methodology
```

### EVM + Agile
```
- Use story points as basis for EV
- Calculate PV based on sprint velocity plan
- Update EV as stories complete (move to Done)
- Useful for fixed-scope, fixed-date projects
- Less useful for pure backlog-driven projects
```

### WBS + Agile Epics
```
Epic ← WBS Level 1 (feature)
Story ← WBS Level 2 (component)
Task ← WBS Level 3 (unit of work)
Subtask ← WBS Level 4 (implementation detail)
```

---

## 14. Metrics Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│ PROJECT HEALTH DASHBOARD                                    │
├─────────────────────────────────────────────────────────────┤
│ SCHEDULE                          COST                      │
│ ─────────────────                ─────────────────          │
│ Schedule Status: ON TRACK         Budget Status: OVER       │
│ % Complete: 45% (phys)           Budget Used: $145K / $130K │
│ SPI: 1.05 (ahead)                CPI: 0.90 (over budget)    │
│ EAC Date: Feb 15 (on time)       EAC Cost: $162K (↑ $32K)  │
│                                                              │
│ CRITICAL PATH              RISK SUMMARY                     │
│ ─────────────────          ─────────────────               │
│ Tasks: 12 of 46            Critical Risks: 1               │
│ Duration: 45 days          High Risks: 3                   │
│ Current Slack: 3 days      Medium Risks: 5                 │
│ Float Erosion: 2 days      Low Risks: 4                    │
│                                                              │
│ RESOURCE UTILIZATION       QUALITY METRICS                 │
│ ─────────────────          ─────────────────               │
│ Team A: 105% (⚠ over)      Code Coverage: 82%              │
│ Team B: 92% (optimal)      Defects Open: 7 (2 critical)    │
│ Contractor: 45% (idle)     Test Pass Rate: 94%             │
│ Average: 87%               DoD Score: 78%                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 15. Calculation Quick Reference

### EVM All-in-One
```
PV = Planned budget for work scheduled to date
EV = (% complete) × Total budget
AC = Actual expenditure to date
BAC = Total budget

CV = EV - AC          (positive = under budget)
SV = EV - PV          (positive = ahead of schedule)
CPI = EV / AC         (> 1 = efficient)
SPI = EV / PV         (> 1 = ahead)
EAC = BAC / CPI       (project total cost)
ETC = EAC - AC        (remaining cost)
VAC = BAC - EAC       (budget surplus/deficit)
```

### CPM All-in-One
```
Forward Pass:
  ES = Max(EF of predecessors) or 0
  EF = ES + Duration

Backward Pass:
  LF = Min(LS of successors) or Project Finish
  LS = LF - Duration

Slack:
  Total Float = LF - EF
  Free Float = Min(ES successors) - EF
  Critical = Float = 0
```

### PERT All-in-One
```
Expected = (O + 4M + P) / 6
Std Dev = (P - O) / 6
Variance = Std Dev²
CV = Std Dev / Expected
P(X ≤ target) = Probability of meeting target
Confidence Range = Expected ± (Z * Std Dev)
  where Z = 1 (68%), 1.96 (95%), 2.576 (99%)
```

---

## End of Quick Reference

**For detailed information, refer to:**
- `PM_SPECIFICATION_PATTERNS_RESEARCH.md` - Comprehensive specifications
- `PM_DATA_MODEL_IMPLEMENTATIONS.md` - Code implementations


# Epic and Story Specification Patterns: Quick Reference

## 1. Pattern Selection Decision Tree

```
START: Need to specify work?
│
├─ Is it STRATEGIC (multi-quarter investment)?
│  └─ YES → Use EPIC SPECIFICATION PATTERNS
│     ├─ Hypothesis Statement? → SAFe Epic Hypothesis
│     ├─ Business Case? → Lean Business Case
│     ├─ Prioritization? → WSJF (Cost of Delay / Job Size)
│     └─ Tracking? → Portfolio Kanban (6 stages)
│
├─ Is it FEATURE (multiple sprints of value)?
│  └─ YES → Use STORY MAPPING + DECOMPOSITION
│     ├─ Layout stories? → Story Map (backbone + ribs)
│     ├─ Break down? → Feature → Stories → Tasks
│     ├─ Prioritize? → WSJF or Business Value Points
│     └─ Release? → Release Slices
│
├─ Is it USER STORY (single sprint value)?
│  └─ YES → Use USER STORY SPECIFICATION
│     ├─ Format? → "As [persona], I want [action], so that [benefit]"
│     ├─ Quality? → INVEST Criteria (target: ≥24/30)
│     ├─ Testability? → Given-When-Then or Rule-Based AC
│     ├─ Completeness? → Definition of Done
│     └─ Sizing? → Fibonacci Story Points
│
└─ Is it TECHNICAL WORK (task/spike)?
   └─ YES → Use TASK SPECIFICATION
      ├─ Research? → Create SPIKE story first
      ├─ Refactoring? → Reference enabling epic/feature
      ├─ Hours? → Estimate in hours, not points
      └─ Impact? → Quantify technical debt reduction
```

---

## 2. Estimation Quick Comparison

### Story Points: Fibonacci vs. T-Shirt Sizing

```
FIBONACCI SCALE           T-SHIRT SCALE        WHEN TO USE
────────────────────────────────────────────────────────────
1 point                   XS (0-2 days)        NEW TEAMS: T-shirt
2 points                  XS (0-2 days)        Start here, convert
3 points                  S (2-3 days)         later if needed
5 points                  M (3-5 days)         MATURE TEAMS: Fibonacci
8 points                  L (5-8 days)         Precise, velocity-based
13 points                 XL (8-13 days)       Better forecasting
21 points                 XXL (13+ days)       Strong correlation
(split if >13)           (split if >21)        to calendar days
```

**Decision Rule**:
- Team < 2 sprints experience? → T-Shirt Sizing
- Team > 2 sprints experience? → Fibonacci
- Need velocity tracking? → Must use Fibonacci
- Communicating with non-technical? → T-Shirt helps

---

## 3. Acceptance Criteria Patterns Matrix

```
SCENARIO TYPE          EXAMPLE                            USE WHEN
──────────────────────────────────────────────────────────────────
HAPPY PATH             "User successfully logs in"        Primary user flow
  - Given/When/Then    All preconditions + action         Always required
                       + expected outcomes

ALTERNATIVE FLOW       "User uses password reset"         Multiple ways to
  - Path variations    Different user paths               accomplish goal
                       Same user goal, different route

ERROR CASE             "Invalid password shown"           Input validation
  - Error handling     System error handling              Error scenarios
                       Graceful degradation

EDGE CASE              "Search with 1M products"          Boundary conditions
  - Boundary           Performance under load             Scale testing
  - Load/Scale         Network latency scenarios          Stress conditions

RULE-BASED             "Apply 10% discount if             Business logic
  - Business rules     total > $100"                      Multiple conditions
  - Conditional        If-then rule sets                  Tiered logic
```

**Minimum AC per Story**: 1 (happy path)
**Maximum AC per Story**: 8 (indicates split needed)
**Target AC Count**: 3-5 (happy path + 2-3 alternatives)

---

## 4. INVEST Compliance Scoring Guide

```
CRITERION      SCORE 5              SCORE 3              SCORE 1
────────────────────────────────────────────────────────────────
INDEPENDENT    Zero dependencies    1-2 mitigatable      >2 blocking
               on other stories     dependencies         dependencies

NEGOTIABLE     Full flexibility;    Some implementation  Locked
               details negotiable   constraints          specification

VALUABLE       Crystal clear        Indirect value;      No user/business
               user/business        value somewhat       value visible
               value               unclear

ESTIMABLE       Team confident;     Team somewhat        Cannot estimate;
               similar work done    uncertain; research  unknowns remain
                                   might help

SMALL          5 points or less;    5-8 points;         >8 points;
               fits easily          might stretch        needs split

TESTABLE       All AC measurable;   Most clear;          Vague criteria;
               automatable;         some judgment        subjective call
               "Yes/No" answer      needed               required

TOTAL SCORE    25-30               18-24               <18
READINESS      READY FOR SPRINT    Needs refinement    RETURN TO BACKLOG
```

---

## 5. Story Splitting Quick Guide (SPIDR)

```
S - SPIKES (Research)
  When: Unknowns about technology/approach
  Example: "Research push notification providers"
  Duration: Usually 1 sprint, max 2
  Produces: Knowledge, not features
  Output: Decision document, prototype (optional)

P - PATHS (Happy path vs. alternatives)
  When: Multiple ways to accomplish goal
  Example: Login → email, social, SSO as 3 stories
  Duration: Varies by path complexity
  Produces: Features for different flows
  Output: Separate story per significant path

I - INTERFACE (Device/Platform variations)
  When: Different UI/device requirements
  Example: Desktop, iOS, Android as 3 stories
  Duration: Varies by interface complexity
  Produces: Same feature, different UI
  Output: Platform-specific stories

D - DATA (Type/Range variations)
  When: Different data types/volumes
  Example: Images, video, text as 3 stories
  Duration: Varies by data complexity
  Produces: Feature supporting data subset
  Output: Data-specific stories

R - RULES (Business rule variations)
  When: Multiple business rules
  Example: Discount rules → new, standard, VIP
  Duration: Usually 1 story per rule
  Produces: Features implementing rule subset
  Output: Rule-specific stories
```

**When to Split**:
- Story > 8 story points
- Story spans multiple disciplines
- Story has >8 acceptance criteria
- Story requires unknown research
- Story blocks other work

**When NOT to Split**:
- Story represents atomic business value
- Splitting creates artificial dependencies
- Splitting increases team coordination overhead

---

## 6. Definition of Done Checklist

### Organizational DoD (All Teams, Minimum)

```
CODE QUALITY                TESTING                 DEPLOYMENT
───────────────            ───────────────         ───────────────
☐ Code reviewed            ☐ Unit tests >70%       ☐ Merged to main
☐ Peer approval (≥1)       ☐ All tests passing     ☐ No conflicts
☐ No critical issues       ☐ AC tested/verified    ☐ Deployed to staging
☐ Code committed           ☐ Coverage reported     ☐ Smoke tests pass

DOCUMENTATION              SECURITY                ACCEPTANCE
───────────────            ───────────────         ───────────────
☐ Code comments updated    ☐ SAST scan passed      ☐ PO sign-off
☐ API docs updated         ☐ No vulnerabilities    ☐ Ready for UAT
☐ README updated           ☐ Dependencies checked  ☐ Performance OK
☐ Commits documented       ☐ No secrets in code    ☐ Accessibility OK
```

### Team-Specific DoD (Examples)

**Backend Team Adds**:
- Database migrations tested on replica
- Cache invalidation tested
- API contract verified with consumers
- Database performance acceptable

**Frontend Team Adds**:
- Mobile tested on actual devices
- Cross-browser compatibility verified
- Accessibility (WCAG 2.1 AA)
- Performance (Lighthouse >85)

**QA Team Adds**:
- Regression test suite updated
- Test coverage >80%
- Automated test pipeline green
- Manual testing completed

---

## 7. Dependency Types Quick Reference

```
TYPE           ABBREVIATION    EXAMPLE                 COMMON
───────────────────────────────────────────────────────────────
Finish-to-      FS            UI story after         Most common
Start                         API story complete      (80% of deps)

Start-to-        SS            Testing starts         Parallel work
Start                          1 day after dev starts (15% of deps)

Finish-to-       FF            Testing finishes       Final validation
Finish                         when dev finishes      (5% of deps)

Start-to-        SF            Old system support     Very rare
Finish                         until new live         (<1% of deps)
```

**Risk Assessment**:
- 0 dependencies: Low risk
- 1-2 dependencies: Medium risk
- >2 dependencies: High risk; consider refactoring

**Dependency Density** (% of stories with dependencies):
- <30%: Healthy parallelization
- 30-60%: Moderate coupling
- >60%: High risk; work is too coupled

---

## 8. WSJF Component Scoring

### Business Value Score (1-21 Fibonacci)

```
21: Transforms business; new major revenue stream
13: Enables significant revenue; major strategic shift
8:  Moderate revenue impact; strong customer need
5:  Small revenue or cost savings
3:  Minor improvement; nice-to-have
1:  No business value; technical debt only
```

**Examples**:
- New subscription tier (revenue): 21
- Mobile shopping (multi-channel): 13
- Checkout optimization (conversion): 8
- Profile page UX improvement: 5
- Code cleanup: 1

### Time Criticality Score (1-21 Fibonacci)

```
21: Market window closing immediately; competitive threat urgent
13: Market window closing in 1-2 quarters; strategic deadline
8:  Opportunity available but window narrowing
5:  Somewhat time-sensitive; no deadline pressure
3:  No time pressure; can wait
1:  No time criticality
```

**Examples**:
- Holiday shopping feature (time-critical): 21
- API infrastructure for partners: 13
- Feature enabling future capabilities: 8
- General enhancement: 3
- Refactoring (no deadline): 1

### Risk Reduction / Opportunity Enablement (1-21)

```
21: Unblocks major platform; enables 3+ future epics
13: Enables significant new capabilities; reduces major risk
8:  Enables moderate new features; mitigates risks
5:  Enables minor features; small risk reduction
3:  Minimal risk reduction
1:  No risk reduction or opportunity
```

### WSJF Prioritization Rules

```
WSJF = Cost of Delay / Job Size
     = (BV + TC + RR) / JS

RESULT             INTERPRETATION           ACTION
─────────────────────────────────────────────────────────
>2.0               Exceptional ROI          Do first
1.5-2.0            Excellent ROI            Do next
1.0-1.5            Good ROI                 Include in plan
0.5-1.0            Moderate ROI             Consider
<0.5               Poor ROI                 Defer/reject
```

**Example Comparison**:

| Epic | BV | TC | RR | CoD | JS | WSJF | Rank |
|------|----|----|----|----|----| ---- | ---- |
| A    | 13 | 8  | 3  | 24 | 13 | 1.85 | 2    |
| B    | 8  | 5  | 3  | 16 | 5  | 3.2  | 1    |
| C    | 21 | 13 | 8  | 42 | 21 | 2.0  | 2    |

**Insight**: Epic B has smallest effort but highest ROI; do first for momentum.

---

## 9. Story Point Estimation Reference

### Historical Baselines (Adjust for your team)

```
STORY POINTS    TYPICAL TASKS                    DAYS FOR TEAM OF 2
───────────────────────────────────────────────────────────────────
1-2             Very simple UI change            0.5 day
                One-liner bug fix
                Update documentation

3               Simple form field                1 day
                Minor API endpoint
                Style adjustment

5               New API endpoint                 2-3 days
                Form with validation
                Search/filter feature
                Query optimization

8               Complex feature                  4-5 days
                Multi-endpoint API
                Dashboard with state
                Complex business logic

13              Major feature                    8-10 days
                Multiple integrations
                Significant refactoring
                Performance optimization

21+             Epic-level work                  2-4 weeks
                Platform rewrite                 Should be split
                Major infrastructure
```

### Team Velocity Patterns

```
SPRINT      FIBONACCI TEAM          T-SHIRT TEAM        CONVERSION
────────────────────────────────────────────────────────────────────
Sprint 1    8-12 points             S (2-3 days)        New; high variance
Sprint 2    15-20 points            M (3-5 days)        Still learning
Sprint 3    20-25 points            L (5-8 days)        Stabilizing
Sprint 4+   25-30 points            L/XL (5-13 days)    Stable velocity
            (rolling avg: ±20%)
```

### Red Flags for Estimation

```
PROBLEM                  INDICATOR              ACTION
──────────────────────────────────────────────────────────
Story too large          >8 points              SPLIT using SPIDR

Story unclear            Wide estimate range    CLARIFY with PO
                         (e.g., 3-13)

Unknown unknowns         Team cannot estimate   CREATE SPIKE first

Poor consistency         High variance in       RE-CALIBRATE team
                         velocity               baselines
```

---

## 10. Velocity Tracking Formulas

### Basic Velocity Calculation

```
Team Velocity = Story Points Completed in Sprint

Sprint 1: Committed 20, Completed 15 → Velocity = 15
Sprint 2: Committed 20, Completed 18 → Velocity = 18
Sprint 3: Committed 25, Completed 25 → Velocity = 25

3-Sprint Rolling Average = (15 + 18 + 25) / 3 = 19.3 points/sprint
Standard Deviation = 4.2 (moderate variation; ±22%)
```

### Forecast Calculation

```
Feature Size: 50 story points
Rolling Average Velocity: 20 points/sprint
Sprints to Complete = 50 / 20 = 2.5 sprints

Optimistic: 50 / 25 = 2.0 sprints
Realistic:  50 / 20 = 2.5 sprints
Pessimistic: 50 / 15 = 3.3 sprints

Forecast Range: 2-3 sprints (95% confidence)
Recommended Forecast: 3 sprints (includes buffer)
```

### Velocity Stability Index

```
Coefficient of Variation = Standard Deviation / Mean

<15%  = Very stable velocity (excellent for forecasting)
15-25% = Stable velocity (good for forecasting)
25-35% = Unstable velocity (add buffers to forecasts)
>35% = Highly unstable (forecasting unreliable; investigate)
```

---

## 11. Risk Assessment Matrix

```
           PROBABILITY
           ───────────────────────
IMPACT     Low      Medium      High
─────────────────────────────────────
High      3-4      6-7         8-9      (high risk)
          LOW      MEDIUM      CRITICAL

Medium    2-3      4-5         6-7      (medium risk)
          LOW      MEDIUM      HIGH

Low       1        2-3         3-4      (low risk)
          MINIMAL  LOW         MEDIUM
```

**Action Thresholds**:
- Score 8-9: CRITICAL → Address immediately
- Score 6-7: HIGH → Plan mitigation
- Score 4-5: MEDIUM → Monitor actively
- Score 1-3: LOW → Track informally

---

## 12. Lean Business Case Template Quick Summary

```
┌─────────────────────────────────────────────────────────────┐
│ LEAN BUSINESS CASE QUICK TEMPLATE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ FINANCIAL DIMENSIONS                                       │
│ • Development Cost: $[amount]                              │
│ • Expected Annual Revenue: $[amount]                       │
│ • Payback Period: [weeks] weeks                            │
│ • Expected ROI: [%]%                                       │
│                                                             │
│ TIMELINE                                                    │
│ • Exploration: [weeks] weeks                               │
│ • Analysis: [weeks] weeks                                  │
│ • Implementation: [weeks] weeks                            │
│ • Total: [weeks] weeks                                     │
│                                                             │
│ MVP DEFINITION                                              │
│ • Scope: [brief description]                               │
│ • Hypothesis: [testable claim]                             │
│ • Learning Goals: [3-5 key unknowns]                       │
│                                                             │
│ RISK ASSESSMENT                                             │
│ • Critical Risks: [2-3 key risks]                           │
│ • Mitigation Strategies: [specific actions]                │
│ • Success Factors: [key enablers]                          │
│                                                             │
│ GO/NO-GO DECISION                                           │
│ • ROI Threshold: [minimum acceptable %]                    │
│ • Strategic Alignment: [score 1-10]                        │
│ • Recommendation: ☐ GO  ☐ NO-GO  ☐ CONDITIONAL            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 13. Quick Compliance Checklists

### Before Story Goes to Sprint

```
CHECKLIST BEFORE STORY COMMITMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Format & Content:
  ☐ Story title clear and concise
  ☐ Format: "As [persona], I want [action], so that [benefit]"
  ☐ Persona defined
  ☐ Business value articulated
  ☐ Links to feature and epic

INVEST Compliance (Target: ≥24/30):
  ☐ INVEST score calculated
  ☐ Independent: ≥4/5
  ☐ Negotiable: ≥4/5
  ☐ Valuable: ≥4/5
  ☐ Estimable: ≥4/5
  ☐ Small: ≥4/5
  ☐ Testable: ≥4/5

Acceptance Criteria:
  ☐ 1-8 criteria (target 3-5)
  ☐ All measurable/testable
  ☐ Given-When-Then or Rule-based format
  ☐ Happy path included
  ☐ Alternatives or errors included (if applicable)

Estimation:
  ☐ Story points assigned (Fibonacci)
  ☐ Planning poker completed
  ☐ Estimates converged (within 1-2 Fibonacci steps)
  ☐ Confidence documented

Dependencies:
  ☐ Blocking dependencies identified
  ☐ Dependent stories identified
  ☐ No >2 dependency chains

Definition of Done:
  ☐ All organizational DoD items applicable
  ☐ Team DoD items identified
  ☐ DoD criteria testable/verifiable

FINAL DECISION:
  ☐ Ready for sprint commitment?  YES ☐  NO ☐  CLARIFY ☐
```

---

## 14. Commonly Used Scoring Scales

```
FIBONACCI SCALE (Story Points)
1  2  3  5  8  13  21

RISK/IMPACT SCALE
1  2  3  4  5  6  7  8  9  10

BUSINESS VALUE SCALE (SAFe)
1  2  3  5  8  13  21

TIME CRITICALITY SCALE (SAFe)
1  2  3  5  8  13  21

CONFIDENCE LEVEL
1 (Low) ────────── 2 (Medium) ────────── 3 (High)

PRIORITY LEVELS
P0/Critical → P1/High → P2/Medium → P3/Low → P4/Deferred

TEAM MATURITY
Level 1 (New) → 2 (Learning) → 3 (Proficient) → 4 (Expert) → 5 (Optimized)
```

---

## 15. Key Metrics Dashboard

```
METRIC                          TARGET         FREQUENCY
──────────────────────────────────────────────────────────
QUALITY METRICS
INVEST Compliance Score         ≥24/30         Per story
DoD Compliance Rate             ≥95%           Per sprint
Test Coverage                   ≥70%           Per build
Code Review Cycle Time          <24 hours      Per PR

DELIVERY METRICS
Sprint Goal Completion          ≥90%           Per sprint
Velocity Stability              ±20%           Per sprint (trend)
Commitment vs. Delivery         ≥95%           Per sprint
Unplanned Work                  <15%           Per sprint

BUSINESS VALUE METRICS
Feature Adoption Rate           >30%           Per release
Revenue per Feature             By feature     Per quarter
Customer Satisfaction           NPS: >50       Per quarter
WSJF Accuracy                   Actual vs.     Per epic (retrospective)
                                Predicted

RISK METRICS
Critical Path Length            <20 sprints    Per quarter
Dependency Density              <60%           Ongoing
Stories Reopened                <5%            Per sprint
Unplanned Technical Debt        <15%           Per sprint
```

---

## Summary: Pattern Selection by Scenario

| SCENARIO | PRIMARY PATTERN | SECONDARY | TOOLS |
|----------|-----------------|-----------|-------|
| New strategic initiative (3+ sprints) | Epic Hypothesis + LBC | WSJF, Kanban | SAFe framework |
| Product roadmap planning (quarterly) | Story Mapping | WSJF | Miro, FigJam |
| Sprint planning (weekly) | INVEST criteria | Given-When-Then | JIRA, Azure DevOps |
| Feature estimation (team sizing) | Planning Poker | Fibonacci points | Physical cards, tools |
| Story refinement (pre-sprint) | Definition of Done | Acceptance Criteria | JIRA checklist |
| Risk identification | Dependency tracking | Risk matrix | Graph tools |
| Business case approval | Lean Business Case | ROI, Cost of Delay | Excel, SAFe |
| Team reporting (stakeholders) | Velocity chart | WSJF scores | Dashboards |

---

**Quick Reference Version**: 2.0
**Last Updated**: January 29, 2026
**For Latest Information**: See EPIC_STORY_SPECIFICATION_PATTERNS.md

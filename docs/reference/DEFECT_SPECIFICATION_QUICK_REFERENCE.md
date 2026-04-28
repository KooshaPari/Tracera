# Defect Specification Quick Reference

**Quick lookup for defect specification patterns and best practices**

---

## 1. ISTQB Severity-Priority Matrix

```
QUICK REFERENCE:

         Severity
         L1    L2    L3    L4
Urgency
High     P1    P1    P2    P3
Medium   P1    P2    P2    P3
Low      P2    P3    P3    P4
Defer    P4    P4    P4    P4

SLA TARGETS:
P1: 24 hours
P2: 3-5 days
P3: 1-2 weeks
P4: 1-4 weeks

Remember: Priority ≠ Severity
- Severity = impact
- Priority = urgency
```

## 2. Defect Status Transitions

```
Valid transitions:

NEW → SUBMITTED → OPEN → ASSIGNED → IN_PROGRESS → FIXED → VERIFIED → CLOSED
                    ↑                                              ↓
                    └──────────── REOPENED ←──────────────────────┘

Rejected/Deferred paths:
OPEN → DUPLICATE
OPEN → REJECTED
OPEN → CANNOT_REPRODUCE
OPEN → DEFERRED (to future release)
```

## 3. ODC Quick Classification

```
WHEN WAS IT FOUND? (Trigger)
- Design inspection (best)
- Code inspection
- Unit testing
- Integration testing
- System testing
- User testing
- Production (worst - escape!)

WHAT'S WRONG? (Defect Type)
- Functional: Wrong logic
- Interface: Wrong API/message
- Checking: Bad validation
- Assignment: Wrong variable
- Timing: Race condition
- Algorithm: Wrong approach
- Documentation: Wrong docs

WHERE DID IT START? (Origin)
- Design phase
- Code phase
- External/unknown

Escape Rate Target: < 5%
(defects found in production / total defects)
```

## 4. Security Classification Cheatsheet

```
CVE SEVERITY SCORING (CVSS):

0.1-3.9:   LOW        | Fix in 90 days
4.0-6.9:   MEDIUM     | Fix in 30 days
7.0-8.9:   HIGH       | Fix in 7 days
9.0-10.0:  CRITICAL   | Fix in 24 hours

COMMON CWE CATEGORIES:

CWE-89:  SQL Injection
CWE-79:  Cross-Site Scripting (XSS)
CWE-78:  Command Injection
CWE-287: Broken Authentication
CWE-327: Weak Cryptography
CWE-611: XML External Entities (XXE)
CWE-352: Cross-Site Request Forgery (CSRF)
CWE-284: Improper Access Control

CVSS VECTOR QUICK TEMPLATE:
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H

Fields:
- AV: Attack Vector (N=Network, L=Local, A=Adjacent, P=Physical)
- AC: Attack Complexity (L=Low, H=High)
- PR: Privileges Required (N=None, L=Low, H=High)
- UI: User Interaction (N=No, R=Required)
- S: Scope (U=Unchanged, C=Changed)
- C: Confidentiality (H=High, L=Low, N=None)
- I: Integrity (H=High, L=Low, N=None)
- A: Availability (H=High, L=Low, N=None)
```

## 5. Root Cause Analysis Methods

```
FIVE WHYS: Simple iterative questions
├─ Why 1? [Answer]
├─ Why 2? [Answer]
├─ Why 3? [Answer]
├─ Why 4? [Answer]
└─ Why 5? [Answer] = ROOT CAUSE

FISHBONE: Categorized by 6M
├─ Man (People)
├─ Method (Process)
├─ Machine (Tools)
├─ Material (Data)
├─ Measurement (Testing)
└─ Environment (Context)

FAULT TREE: Top-down deductive
├─ Top Event (failure)
└─ Traced down to basic causes
  (AND/OR logic gates)

FMEA: Systematic failure analysis
├─ Severity (1-10)
├─ Occurrence (1-10)
├─ Detection (1-10)
└─ RPN = S × O × D (target < 100-150)

PARETO: Find vital few
└─ 20% of causes = 80% of defects
```

## 6. Defect Report Quality Scoring

```
QUALITY ASSESSMENT:

SCORE    RATING     ACTION
90-100   Excellent  Assign immediately
75-89    Good       Minor clarification needed
60-74    Adequate   Some clarification required
40-59    Poor       Significant rework needed
<40      Reject     Resubmit with details

SCORING CHECKLIST:

Title (0-15 pts)
□ Specific and descriptive (not "Bug in system")
□ Under 100 characters
□ No jargon or slang

Description (0-20 pts)
□ Clear problem statement
□ Context provided
□ No assumptions about knowledge

Steps to Reproduce (0-20 pts)
□ Numbered steps
□ Clear and specific
□ Can be followed by anyone

Expected vs Actual (0-15 pts)
□ Both clearly specified
□ Easy to compare

Environment (0-15 pts)
□ OS and version
□ Browser/app and version
□ System config details

Evidence (0-15 pts)
□ Screenshot, log, or test case
□ Performance metrics if relevant

BONUS (+5 each):
- Includes workaround
- Links to user impact
- Quantified severity/priority
- Performance metrics
```

## 7. Code Metrics for Defect Risk

```
COMPLEXITY RISK ASSESSMENT:

Cyclomatic Complexity (CC):
1-5:     ✓ Low risk
6-10:    ✓ Low-medium risk
11-20:   ⚠ Medium risk (require review)
21-30:   ⚠ High risk (schedule refactoring)
30+:     ✗ Critical (must refactor)

Lines of Code per Method:
< 50:    ✓ Ideal
50-100:  ✓ Acceptable
100-200: ⚠ Consider refactoring
200+:    ✗ Must refactor

Code Churn (% changed):
< 5%:    ✓ Stable
5-15%:   ✓ Normal
15-30%:  ⚠ High (increase testing)
> 30%:   ✗ Very high (flag for review)

Test Coverage:
< 50%:   ✗ Insufficient confidence
50-75%:  ⚠ Acceptable
75-85%:  ✓ Good
> 85%:   ✓ Excellent
> 95%:   ✓ Comprehensive

DEFECT DENSITY BASELINE:
2-4 defects/KLOC = Industry average

Risk factors (multiply baseline):
- Very high complexity (CC > 20): ×2.5
- Junior developer: ×1.5
- High code churn (>30%): ×2.5
- Low test coverage (<50%): ×1.5
- Single code reviewer: ×1.0

Example: 3/KLOC × 1.5 × 1.5 × 2.5 = 16.9/KLOC (HIGH RISK)
```

## 8. Regression Defect Tracking

```
FIX ESCAPE RATE (FER):
FER = (Regressions in period) / (Defects fixed)

Target: < 3%
Elevated: > 5%

TIMELINE GOALS:
- Detection within 1 day (if in production)
- 0 days if caught in testing

REGRESSION TEST PRIORITIES:

Level 1 - Critical (run per commit, 5-10 min)
├─ Core functionality
├─ Authentication flows
├─ Data integrity
└─ Known regression tests

Level 2 - Extended (pre-release, 30-60 min)
├─ Edge cases
├─ Integration scenarios
├─ Performance baselines
└─ Security tests

Level 3 - Full Suite (nightly, 2-4 hours)
├─ All Level 1 & 2
├─ Load/stress tests
├─ Database migration tests
└─ Backup/recovery tests

REGRESSION PREVENTION:
□ Identify all related modules
□ Verify integration points
□ Test dependent modules
□ Run regression suite
□ Monitor for regressions
```

## 9. Pareto Analysis (80/20 Rule)

```
HOTSPOT IDENTIFICATION:

Rank  Module      Count  Cumulative %  Vital Few?
1     Auth         45     35%          ✓
2     Payment      35     62%          ✓
3     API          20     77%          ✓
4     Database     12     86%          ✗
5     Others       13    100%          ✗

VITAL FEW (20% of modules):
- Fix top 3 modules
- Expected result: 77% of defects eliminated

FOCUS EFFORT ON:
1. Code review intensity
2. Testing depth
3. Refactoring priority
4. Knowledge transfer
```

## 10. Technical Debt Assessment

```
SQALE RATING SCALE:

A: 0-5% debt      ✓ Excellent
B: 6-10% debt     ✓ Good
C: 11-20% debt    ✓ Acceptable
D: 21-50% debt    ⚠ Poor
E: 51-100% debt   ⚠ Critical
F: >100% debt     ✗ Very critical

DEBT REMEDIATION:

Annual targets:
- Year 1: Reduce 30% of outstanding debt
- Year 2: Reduce additional 25%
- Maintain: < 150 hours outstanding

Allocation:
- 20% sprint capacity to debt paydown
- OR alternate sprints (80% features, 20% debt)

Debt impact:
- 100 hours debt ≈ 5-10% slower development
- Compound effect: Increases over time if not addressed

CODE SMELL INDICATORS:

High priority refactoring if:
- Cyclomatic complexity > 20
- Method length > 200 LOC
- Code duplication > 10%
- Comment ratio > 10% (over-documented)
- Test coverage < 50%
```

## 11. Metrics Dashboard Essentials

```
KEY METRICS TO TRACK:

Volume Metrics:
├─ Total open defects (by severity)
├─ Monthly defect velocity
├─ Defects by module (hotspot analysis)
└─ Defects by type (functional, security, etc.)

Quality Metrics:
├─ Average resolution time
├─ SLA compliance percentage
├─ Escape rate (production defects)
├─ Regression rate (fix-induced defects)
└─ RCA completion rate

Risk Indicators:
├─ Critical/high severity trend
├─ Security defect count
├─ Defect age (stale defects)
├─ Code churn correlation
└─ Test coverage trend

Trend Alerts:
- Escape rate > 5%: Investigate test effectiveness
- Regression rate > 3%: Review fix quality
- SLA breach > 20%: Adjust processes
- Critical defects growing: Escalate
- RCA completion < 50%: Enforce analysis

MONTHLY REVIEW:
□ Velocity trend
□ Hotspot changes
□ RCA completion status
□ Escape/regression rates
□ SLA compliance
□ Process improvements needed
```

## 12. Interview/Knowledge Transfer Questions

```
CRITICAL DEFECT:
"What's the root cause? How do we prevent this?"

REGRESSION:
"What was the original fix? Why did it reoccur?"

SECURITY DEFECT:
"What's the attack vector? What data is exposed?"

HIGH COMPLEXITY DEFECT:
"What modules are affected? What tests are needed?"

CUSTOMER-IMPACTING:
"How many users affected? What's the business impact?"

DEFECT CLUSTERING:
"Why are this module's defects so high? Refactoring needed?"

ESCAPE ANALYSIS:
"Which phase should have caught this? Process gap?"
```

## 13. Tool Integration Examples

```
GIT INTEGRATION:
├─ Track code churn for changed files
├─ Link defect to commit hashes
├─ Measure commits per file per defect
└─ Identify high-change modules

CI/CD INTEGRATION:
├─ Capture build info with defect
├─ Link test results to defects
├─ Automated security scanning (CVE/CVSS/CWE)
└─ Code complexity metrics per commit

CODE ANALYSIS INTEGRATION:
├─ Cyclomatic complexity per method
├─ Lines of code metrics
├─ Code coverage gaps
└─ Security warnings (CWE mapping)

TESTING INTEGRATION:
├─ Regression test coverage
├─ Test case execution status
├─ Test failure categorization
└─ Performance test baselines

MONITORING INTEGRATION:
├─ Production error rates
├─ Performance degradation
├─ User-reported issues
└─ Incident to defect correlation
```

## 14. Common Mistakes to Avoid

```
REPORTING MISTAKES:
✗ Vague titles ("Something is broken")
✗ No reproduction steps
✗ Missing environment details
✗ Attaching huge logs without filtering
✗ Not separating multiple issues

CLASSIFICATION MISTAKES:
✗ Confusing severity with priority
✗ Tagging everything as "critical"
✗ Not using ODC classification
✗ Security defects marked as LOW severity
✗ Ignoring blast radius

RCA MISTAKES:
✗ Stopping at symptoms (first "why")
✗ Blaming individuals instead of systems
✗ No preventive actions defined
✗ Not tracking RCA completion
✗ Generic root causes ("human error")

METRIC MISTAKES:
✗ Not stratifying by module/component
✗ Ignoring temporal patterns
✗ Comparing projects with different baselines
✗ Not normalizing by code size (churn %, density)
✗ Treating correlation as causation

PROCESS MISTAKES:
✗ No SLA enforcement
✗ Accepting defects without RCA
✗ Not preventing regression patterns
✗ Ignoring hotspot modules
✗ No feedback loop to development
```

---

## Quick Lookup by Scenario

**User reports defect:**
1. Ask for severity + reproducibility
2. Calculate risk level
3. Assign priority using matrix
4. Calculate quality score
5. Request missing info if < 60 quality score

**Defect ready for development:**
1. Verify RCA if in investigation
2. Check estimated resolution hours
3. Assign to developer
4. Schedule regression testing
5. Set SLA based on priority

**Defect closed:**
1. Record resolution type
2. Check for regressions (72-96 hour watch)
3. Document lessons learned
4. Update metrics
5. Review for process improvements

**Security defect found:**
1. Calculate CVSS score immediately
2. Map to CWE category
3. Link any CVE references
4. Escalate if score > 7.0
5. Plan secure development practices

**High defect density module:**
1. Calculate module defect density
2. Identify Pareto position
3. Plan refactoring
4. Increase code review for new changes
5. Add targeted testing
6. Reassess in 1-2 quarters

---

## Files Reference

**Main Research Document:**
- `/DEFECT_SPECIFICATION_RESEARCH.md` - Comprehensive 11-section framework

**Implementation Guide:**
- `/DEFECT_IMPLEMENTATION_GUIDE.md` - Code examples and setup instructions

**This Quick Reference:**
- `/DEFECT_SPECIFICATION_QUICK_REFERENCE.md` - Lookup tables and checklists

---

**Last Updated:** January 2026
**Version:** 1.0
**Next Review:** Quarterly


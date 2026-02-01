# Standards Quick Reference: Requirements and Test Specifications

**Purpose:** Quick lookup table for requirement and test attributes across major standards
**Audience:** Requirements engineers, test planners, quality assurance professionals
**Last Updated:** January 29, 2026

---

## 1. Requirement Attributes by Standard

### 1.1 Core Mandatory Attributes (All Standards)

| Attribute | Definition | Example |
|-----------|-----------|---------|
| **ID** | Unique identifier | REQ-SYS-001, FSR-ABS-001-ASILD |
| **Statement** | Clear, singular requirement | "The system shall authenticate users within 5 seconds" |
| **Type** | Functional, Non-Functional, Interface, etc. | Functional, Performance, Safety-Critical |
| **Verification Method** | How to prove compliance | Test, Analysis, Inspection, Demonstration |
| **Traceability** | Links to source and implementation | Derives from STK-001, implements in module X |

### 1.2 Standard-Specific Required Attributes

| Standard | Additional Mandatory Attributes |
|----------|-----------------------------------|
| **ISO 29148** | Rationale, Conditions, Qualifications, Quality criteria verification |
| **DO-178C** | Criticality level, Derived vs. Base status, Test case mapping |
| **ISO 26262** | ASIL level, Hazard reference, Failure mode analysis, Diagnostic coverage |
| **IEC 62304** | Safety class, Risk control measure link, Verification strategy by class |
| **IEEE 830** | Rationale, Acceptance criteria, Dependencies |
| **ASPICE** | Component allocation, Review status, Change control |

### 1.3 Recommended Attributes (Quality Enhancement)

| Attribute | Purpose | Typical Values |
|-----------|---------|-------|
| **Priority** | Implementation sequencing | Critical, High, Medium, Low |
| **Status** | Current state | Draft, Under Review, Approved, Baseline, Deprecated |
| **Allocated Component** | Responsibility assignment | Component/team name |
| **Performance Metrics** | Measurable criteria | Numbers, units, ranges |
| **Rationale** | Why requirement exists | Business justification, regulatory requirement |
| **Related Requirements** | Dependencies | REQ-XXX, REQ-YYY |
| **Review Comments** | Quality feedback | Issue descriptions and resolutions |

---

## 2. Requirement Quality Checklist

### 2.1 Quick Quality Assessment

For each requirement, verify:

- [ ] **Unique ID** present and traceable
- [ ] **Statement** is singular (one requirement per statement)
- [ ] **No vague qualifiers** (not "user-friendly," "efficient," "several")
- [ ] **Measurable or observable** acceptance criteria
- [ ] **Mandatory indicator** ("shall" / "shall not" for requirements)
- [ ] **Subject identified** (what entity must perform action)
- [ ] **Action specified** (what must be done)
- [ ] **Conditions noted** (when/where applicable)
- [ ] **Qualifications stated** (how much, how fast, how accurate)
- [ ] **Verification method** identified (Test/Analysis/Inspection/Demo)
- [ ] **Allocated** to responsible component/team
- [ ] **Upstream traced** to source/need
- [ ] **Downstream linked** to design/implementation/test
- [ ] **Rationale documented** (why it's necessary)
- [ ] **Reviewed and approved** by stakeholders

**Failing any of first 10 = Cannot proceed to design**
**Failing any of last 5 = Audit/certification risk**

### 2.2 EARS Pattern Quick Check

Does requirement match one of these patterns?

```
[✓] Ubiquitous:       "The [System] shall [Action] [Qualification]"
[✓] Event-Driven:     "When [Trigger], [System] shall [Action]"
[✓] Conditional:      "If [Condition], [System] shall [Action]"
[✓] State-Based:      "While [State], [System] shall [Action]"
[✓] Optional:         "[System] may [Action] unless [Constraint]"
[✓] Quantified:       "[System] shall [Action] [Number] times [Period]"
```

If requirement doesn't match a pattern → Rewrite for clarity

---

## 3. Verification Method Decision Tree

```
START: Need to verify requirement

├─ Can requirement be proven by observing physical characteristics?
│  └─ YES: INSPECTION
│     (Design review, document review, physical walkthrough)
│
├─ Can requirement be demonstrated through normal operation?
│  └─ YES: DEMONSTRATION
│     (Manual execution showing capability)
│
├─ Does requirement need controlled conditions and measurements?
│  ├─ YES: TEST (Most requirements)
│  │   ├─ Functional test? → Unit test, Integration test
│  │   ├─ Performance test? → Load test, Stress test
│  │   ├─ Security test? → Vulnerability scan, Penetration test
│  │   └─ Coverage required? → Statement/Branch/MC/DC
│  │
│  └─ Can requirement only be verified mathematically/theoretically?
│     └─ YES: ANALYSIS
│        (Formal proof, FMEA, simulation, modeling)
```

---

## 4. Test Coverage Requirements by Safety Level

### 4.1 Minimum Coverage by Classification

| Level/Class | Statement | Branch/Decision | MC/DC | Risk-Based | Test Evidence |
|---|---|---|---|---|---|
| **DO-178C Level E** | 100% | - | - | - | Basic test report |
| **DO-178C Level D** | 100% | - | - | - | Test logs, coverage metrics |
| **DO-178C Level C** | 100% | 100% | - | Robustness | Coverage matrix, test procedures |
| **DO-178C Level B** | 100% | 100% | - | Structural | Detailed test summary, independence verification |
| **DO-178C Level A** | 100% | 100% | 100% | Exhaustive | MC/DC matrix, formal verification, certification review |
| **ISO 26262 ASIL A** | Basic | - | - | - | Test summary |
| **ISO 26262 ASIL B** | 100% | - | - | Risk-based | Traceability matrix |
| **ISO 26262 ASIL C** | 100% | 100% | - | Risk-based | FMEA, confirmation measures |
| **ISO 26262 ASIL D** | 100% | 100% | 100% (critical) | Comprehensive | Confirmation Review/Audit/Assessment |
| **IEC 62304 Class A** | Basic | - | - | - | Documentation |
| **IEC 62304 Class B** | 100% | Decision | - | Risk-based | Verification plan, test summary |
| **IEC 62304 Class C** | 100% | Decision | MC/DC (critical) | Risk-based | Comprehensive traceability, design review |
| **ASPICE Level 2** | - | - | - | Per strategy | Formal process documentation |
| **ASPICE Level 3** | 100% | 100% | - | Standard | Standard process, metrics |
| **ASPICE Level 4** | 100% | 100% | MC/DC (critical) | Measured | Quantitative objectives |
| **ASPICE Level 5** | 100% | 100% | 100% | Optimized | Continuous improvement data |

### 4.2 Coverage Definitions

| Coverage Type | Definition | When Required | Effort |
|---|---|---|---|
| **Statement** | Every line of code executed at least once | All safety levels | Minimal |
| **Branch** | Every decision evaluated both ways (T/F) | Level C+, ASIL B+, Class B+ | 2-3x statement |
| **Condition** | Every condition in decision evaluated both ways | Part of branch coverage | Included in branch |
| **Decision/Condition** | Both branch AND each condition independently | DO-178C Level B | 3-4x statement |
| **MC/DC** | Each condition shown to independently affect outcome | DO-178C Level A, ASIL D, critical paths | 4-5x statement |
| **Path** | Every possible execution path through code | Critical algorithms only | 5-10x statement |
| **Data Flow** | All def-use pairs (definition-use) of variables | Formal verification contexts | High effort |

### 4.3 MC/DC Example

Requirement: "IF (speed > MAX_SPEED OR altitude > MAX_ALT) THEN activate_limiter()"

```
Conditions: A = (speed > MAX_SPEED), B = (altitude > MAX_ALT)
Decision: IF (A OR B) THEN activate

MC/DC Test Cases (4 minimum):
  Case 1: A=TRUE,  B=TRUE   → Result=TRUE   (A affects outcome when B changes)
  Case 2: A=TRUE,  B=FALSE  → Result=TRUE   (B indifferent, A was TRUE)
  Case 3: A=FALSE, B=TRUE   → Result=TRUE   (A indifferent, B was TRUE)
  Case 4: A=FALSE, B=FALSE  → Result=FALSE  (Both conditions affect together)

Outcome: All 4 conditions shown to independently influence decision
```

---

## 5. Traceability Matrix Structure

### 5.1 Standard Traceability Matrix Columns

```
┌─────────────┬──────────────┬──────────────┬─────────────┬─────────────┬─────────────┐
│ Requirement │ Description  │ Stakeholder  │ Design      │ Test Case   │ Verification│
│ ID          │              │ Need/Goal    │ Component   │ ID          │ Status      │
├─────────────┼──────────────┼──────────────┼─────────────┼─────────────┼─────────────┤
│ REQ-SYS-001 │ User auth    │ STK-001      │ AUTH-MOD    │ TC-001      │ PASS        │
│ REQ-SYS-002 │ Data encrypt │ STK-002      │ SEC-MOD     │ TC-002,003  │ PASS        │
│ REQ-SYS-003 │ User role    │ STK-001      │ RBAC-MOD    │ TC-004,005  │ PASS        │
└─────────────┴──────────────┴──────────────┴─────────────┴─────────────┴─────────────┘

Forward Traceability: LEFT → RIGHT (Requirement → Implementation → Verification)
Backward Traceability: RIGHT ← LEFT (Verification → Implementation → Requirement)
Bidirectional: Links flow both directions
```

### 5.2 Traceability Verification Checklist

- [ ] Every requirement (left column) has at least one design component
- [ ] Every requirement has at least one test case
- [ ] Every test case traces back to at least one requirement
- [ ] No orphaned requirements (rows with no design/test links)
- [ ] No orphaned code (design components not traced to requirement)
- [ ] No orphaned tests (test cases not linked to requirement)
- [ ] All test cases show PASS status (or documented exceptions)
- [ ] Bidirectional traceability verified (forward and backward)
- [ ] Matrix updated with every requirement/design/test change
- [ ] Traceability baseline established and version controlled

---

## 6. Requirement Statement Patterns (EARS)

### 6.1 Pattern Selection Quick Reference

| Requirement Type | Use Pattern | Example |
|---|---|---|
| **Always true, unconditional** | Ubiquitous | "The system shall validate input before processing" |
| **Triggered by event** | Event-Driven | "When payment is received, system shall update balance within 24 hours" |
| **Conditional logic** | Conditional | "If user is admin, system shall grant access to config menu" |
| **State-dependent** | State-Based | "While logged in, system shall maintain session state" |
| **Optional behavior** | Optional | "System may cache results unless memory exceeds threshold" |
| **Repetitive action** | Quantification | "System shall check connectivity every 30 seconds" |

### 6.2 Pattern Template Fill-in

```
UBIQUITOUS PATTERN:
"The [SYSTEM NAME] shall [FUNCTIONAL CAPABILITY] [OPTIONAL QUALIFIER/TIME]"
Example: "The authentication module shall verify credentials against LDAP within 5 seconds"

EVENT-DRIVEN PATTERN:
"When [TRIGGER/EVENT], the [SYSTEM] shall [RESPONSE/CAPABILITY]"
Example: "When power is supplied, the motor shall spin at designated RPM within 2 seconds"

CONDITIONAL PATTERN:
"If [CONDITION], then the [SYSTEM] shall [CAPABILITY]"
Example: "If disk usage exceeds 90%, then the system shall alert administrator"

STATE-BASED PATTERN:
"While [STATE/CONDITION], the [SYSTEM] shall [CAPABILITY]"
Example: "While in diagnostic mode, the system shall log all transactions to file"

OPTIONAL PATTERN:
"The [SYSTEM] may [OPTIONAL FEATURE] unless [CONSTRAINT/REASON]"
Example: "The system may display notifications unless user disabled notifications in settings"

QUANTIFICATION PATTERN:
"The [SYSTEM] shall [ACTION] [NUMBER] [FREQUENCY/TIME PERIOD]"
Example: "The system shall retry failed connections every 60 seconds up to 5 times"
```

---

## 7. Safety Classification Quick Decision Guide

### 7.1 ASIL Determination (ISO 26262)

```
STEP 1: Assess SEVERITY (S)
├─ S0: No injury possible
├─ S1: Light injury possible
├─ S2: Serious injury possible
└─ S3: Death or serious injury possible (select S3)

STEP 2: Assess EXPOSURE (E)
├─ E1: Situation occurs rarely
├─ E2: Situation occurs occasionally
├─ E3: Situation occurs frequently
└─ E4: Situation occurs very frequently (select E4)

STEP 3: Assess CONTROLLABILITY (C)
├─ C0: Easy to control
├─ C1: Normal control possible
├─ C2: Difficult to control
└─ C3: Nearly impossible to control (select C3)

STEP 4: Use Matrix to Determine ASIL
      E1  E2  E3  E4
S0   QM  QM  QM  QM
S1   QM  A   A   B
S2   QM  A   B   C
S3   A   B   C   D

RESULT: S3 × E4 × C3 = ASIL D (Highest Integrity)
```

### 7.2 DO-178C DAL Quick Selection

| System Type | Consequence | DAL |
|---|---|---|
| Non-critical feature | No effect on safety | E |
| Minor system | Minor injury if fails | D |
| Significant system | Major injury if fails | C |
| Critical system | Severe/hazardous if fails | B |
| Primary flight path | Catastrophic if fails | A |

### 7.3 IEC 62304 Safety Class Selection

| Medical Device | Potential Harm | Class |
|---|---|---|
| Patient data display | None if fails | A |
| Insulin pump calculation | Minor reversible injury | B |
| Cardiac pacemaker | Death or permanent injury | C |
| Surgical robotic control | Fatal consequence | C |

---

## 8. Requirement Document Organization

### 8.1 Recommended SRS Structure (ISO 29148)

```
SECTION 1: INTRODUCTION
  1.1 Software Overview and Purpose
  1.2 Software Intended Function
  1.3 Intended Users and Operational Environment
  1.4 Design and Implementation Constraints

SECTION 2: REFERENCES
  2.1 Normative References (standards, specifications)
  2.2 Informative References (guides, background)

SECTION 3: REQUIREMENTS
  3.1 Functional Requirements
      3.1.1 Capability Group 1
      3.1.2 Capability Group 2
  3.2 Interface Requirements
      3.2.1 Hardware Interfaces
      3.2.2 Software Interfaces
      3.2.3 User Interfaces
  3.3 Performance Requirements
  3.4 Physical Requirements
  3.5 Design Requirements
  3.6 Safety Requirements
  3.7 Compliance Requirements

SECTION 4: VERIFICATION
  4.1 Verification Strategy
  4.2 Verification Mapping
  4.3 Traceability Matrix

SECTION 5: APPENDICES
  A: Glossary and Terminology
  B: Detailed Traceability Matrix
  C: Quality Attribute Metrics
```

### 8.2 Critical Content Checklist

- [ ] **Overview** clearly states what software does and why
- [ ] **Constraints** explicitly listed (technical, regulatory, operational)
- [ ] **Requirements organized** by feature/mode/user class consistently
- [ ] **Each requirement has all attributes** (ID, statement, verification method)
- [ ] **No vague requirements** (words like "user-friendly," "efficient")
- [ ] **Measurable criteria** for all acceptance conditions
- [ ] **Traceability matrix** shows complete forward and backward links
- [ ] **Verification strategy** defined per requirement type and safety level
- [ ] **Baseline version** established and controlled
- [ ] **Approval signatures** from requirements analyst, architect, product owner

---

## 9. Test Case Specification Template

### 9.1 Minimal Test Case Attributes

```
TEST CASE ID:        TC-LOGIN-001
TITLE:               Valid user login with correct credentials
OBJECTIVE:           Verify authorized users can authenticate successfully
TEST ITEMS:          Login module, Authentication service
PRECONDITIONS:       User account exists, database accessible, browser cache cleared
TEST DATA:           Username: testuser@example.com, Password: ValidPass123!
TEST STEPS:
  1. Navigate to login page
  2. Enter username in username field
  3. Enter password in password field
  4. Click Login button
  5. Wait for response
EXPECTED RESULT:     User redirected to dashboard, session token set, timeout=30min
ACTUAL RESULT:       [To be filled during execution]
TEST STATUS:         PASS / FAIL / BLOCKED / SKIPPED
SEVERITY:            CRITICAL (authentication broken if fails)
TESTER:              QA Engineer name
EXECUTION DATE:      YYYY-MM-DD
TRACEABILITY:        REQ-AUTH-001, REQ-AUTH-002
```

### 9.2 Test Case Coverage for Requirements

For each requirement, minimum test cases:

| Requirement Type | Minimum Test Cases | Coverage Target |
|---|---|---|
| **Functional** | 1 normal case + 2 edge cases | Positive path + boundary conditions |
| **Performance** | 2-3 (nominal, peak, sustained) | Average, peak, sustained load |
| **Interface** | 1-2 per interface type | All protocol variations |
| **Safety-Critical** | 5+ (error paths, edge cases, combinations) | 100% MC/DC for decision logic |
| **High-Risk** | 3+ (normal, error, recovery) | All failure modes + recovery paths |

---

## 10. Traceability Verification Commands (For Tools)

### 10.1 Common Traceability Queries

```
QUERY: All requirements without design components
RESULT: Orphaned requirements (need design allocation)

QUERY: All design components without requirements
RESULT: Orphaned code (scope creep risk)

QUERY: All requirements without test cases
RESULT: Incomplete verification coverage

QUERY: All test cases without requirements
RESULT: Orphaned tests (implementation risk)

QUERY: Bidirectional traceability coverage %
RESULT: Forward links % × Backward links % (target: 100% × 100%)

QUERY: Changed requirements impact analysis
RESULT: All affected design elements and test cases

QUERY: Test-to-requirement coverage %
RESULT: (Test cases with links / Total test cases) × 100%
```

### 10.2 Traceability Metrics

| Metric | Target | Acceptable | Below Standard |
|--------|--------|-----------|---|
| **Forward Traceability** | 100% | 95%+ | < 95% |
| **Backward Traceability** | 100% | 95%+ | < 95% |
| **Bidirectional Coverage** | 100% | 95%+ | < 95% |
| **Orphaned Requirements** | 0 | 0 | > 0 is risk |
| **Orphaned Code** | 0 | 0 | > 0 is waste |
| **Test Case Coverage** | 100% | 95%+ | < 95% is risk |
| **Requirement Defect Rate** | < 1% | 1-3% | > 3% indicates quality issue |

---

## 11. Certification Evidence Checklist

### 11.1 DO-178C Level A Certification Evidence

- [ ] Software Requirements Specification with traceability
- [ ] Architectural Design Specification
- [ ] Low-Level Design Specification
- [ ] Source Code with annotations
- [ ] Test Procedures documenting 100% MC/DC coverage
- [ ] Test Results showing all tests passed
- [ ] Test Coverage Analysis report (MC/DC metrics)
- [ ] Verification Summary Report
- [ ] Software Version Control and Build procedures
- [ ] Cumulative Hazard Index or equivalent safety analysis
- [ ] Certification Review approval

### 11.2 ISO 26262 ASIL D Certification Evidence

- [ ] Functional Safety Concept with ASIL determination
- [ ] Hazard Analysis and Risk Assessment
- [ ] Functional Safety Requirements Specification
- [ ] System Architecture Design
- [ ] Hardware Design Specification
- [ ] Software Design Specification
- [ ] Software Unit Implementation and Verification
- [ ] Integration Testing and Verification
- [ ] System Testing and Validation
- [ ] FMEA with Diagnostic Coverage calculations
- [ ] Traceability Matrix (bidirectional, verified)
- [ ] Confirmation Measures (Review, Audit, Assessment)
- [ ] Change Management Records
- [ ] Safety Plan and Activities Record

### 11.3 IEC 62304 Class C Certification Evidence

- [ ] Risk Analysis Report (FMEA)
- [ ] Risk Control Measures with traceability to requirements
- [ ] Software Safety Plan
- [ ] Software Requirements Specification
- [ ] Software Architectural Design
- [ ] Software Detailed Design
- [ ] Design Review Report
- [ ] Software Unit Verification Report (code review, unit tests)
- [ ] Integration Test Plan and Report
- [ ] System Test Plan and Report
- [ ] Requirements Verification Matrix
- [ ] Software V&V Plan and Verification Summary
- [ ] Software Change Log
- [ ] Software Release Note

---

## 12. Common Mistakes and How to Avoid Them

### 12.1 Requirement Writing Mistakes

| Mistake | Example | Correction |
|---------|---------|-----------|
| **Vague qualifier** | "System shall be user-friendly" | "System shall support keyboard navigation with 3 or fewer clicks" |
| **Prescriptive design** | "Shall use PostgreSQL database" | "Shall store 50M records with < 100ms query response" |
| **Multiple requirements** | "System shall login and display profile" | Split into: "System shall authenticate user" + "System shall display user profile" |
| **Unmeasurable** | "Shall respond rapidly" | "Shall respond within 500ms at 99th percentile" |
| **Missing condition** | "System shall accept input" | "When user enters data and clicks submit, system shall validate and process within 5 seconds" |
| **Wrong keyword** | "Must encrypt data" | "Shall encrypt all data with AES-256" |
| **Orphaned** | No upstream/downstream links | Add stakeholder need and design component links |
| **No rationale** | Just the requirement text | Add: "Critical for regulatory compliance (GDPR)" |

### 12.2 Test Specification Mistakes

| Mistake | Example | Correction |
|---------|---------|-----------|
| **Untraceable** | Test case with no requirement link | Add TRACEABILITY field: REQ-001, REQ-002 |
| **Ambiguous steps** | "Click button" (which button?) | "Click the 'Submit' button (green button, right side)" |
| **Vague expected result** | "User logs in successfully" | "User redirected to /dashboard, session cookie set with 30-min timeout, username displayed in header" |
| **Missing preconditions** | Assumes test environment setup | List: "Database seeded with 3 test users, browser cache cleared, network accessible" |
| **No test data** | "Enter valid username" | Specify: "Username: testuser@example.com" |
| **Incomplete coverage** | Only happy path tested | Add: Edge cases (long names, special chars), error cases (invalid password), boundary conditions |
| **No verification criteria** | No clear pass/fail definition | Add: "PASS: All 3 conditions met: (1) redirect occurs, (2) cookie set, (3) username visible" |

### 12.3 Traceability Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| **One-directional only** | Can't impact analyze | Ensure BIDIRECTIONAL links (forward AND backward) |
| **Loose links** | Difficult to maintain | Use formal IDs and tool support, not comments |
| **Orphaned requirements** | Scope creep not visible | Regular traceability audits, eliminate orphaned items |
| **Orphaned code** | Waste and technical debt | Automated tooling to detect and eliminate |
| **Stale traceability** | Links become invalid as code changes | Update traceability with every change, not after-the-fact |
| **Manual maintenance** | Expensive and error-prone | Use requirements management tools with automation |
| **No version control** | Can't track traceability changes | Version all traceability artifacts with change rationale |

---

## 13. Tool Comparison Quick Reference

### 13.1 Minimum Tool Capabilities Required

| Capability | Level 1 | Level 2 | Level 3 | Level 4 |
|---|---|---|---|---|
| **Requirement ID Management** | Manual | Auto-generation | Configurable schemas | Integrated versioning |
| **Traceability Links** | Manual references | Formal link types | Bidirectional, automated | With metrics/analytics |
| **Quality Checks** | Manual review | Checklists, templates | Automated validation | ML-based suggestions |
| **Test Case Mapping** | Spreadsheet | Tool-based | Bidirectional, live | Continuous integration |
| **Change Impact Analysis** | Manual | Semi-automated | Full automation | Predictive analytics |
| **Reporting** | Basic lists | Customizable reports | Real-time dashboards | Predictive reporting |
| **Integration** | File export | API connections | Full integration | Workflow automation |
| **Metrics/Analytics** | Manual calculation | Automated collection | Real-time dashboards | AI-driven insights |

### 13.2 Key Tool Evaluation Criteria

- [ ] Supports unique ID schemes (customizable format)
- [ ] Allows rich text and structured templates
- [ ] Enables bidirectional traceability links
- [ ] Generates traceability matrices automatically
- [ ] Performs bidirectional coverage analysis
- [ ] Detects orphaned requirements and code
- [ ] Manages versions and baselines
- [ ] Tracks changes with audit trail
- [ ] Exports to standard formats (PDF, Excel, XML)
- [ ] Integrates with design and test tools
- [ ] Supports user roles and permissions
- [ ] Provides customizable reporting
- [ ] Scales to 10,000+ requirements
- [ ] Supports agile/iterative workflows
- [ ] Has active vendor support and updates

---

## 14. Quick Standard Decision Guide

### 14.1 "Which Standard Applies?" Decision Tree

```
START: Determining applicable standards

├─ Is this for AUTOMOTIVE systems?
│  ├─ YES: ISO 26262 REQUIRED
│  │   └─ Safety-critical functions → ASIL determination
│  │   └─ Use DO-ASIL mapping for reference
│  │
│  └─ Also check: ASPICE for process assessment
│
├─ Is this for AIRBORNE systems?
│  ├─ YES: DO-178C REQUIRED
│  │   └─ Commercial aircraft → FAA certification
│  │   └─ Military aircraft → MIL-STD-178B
│  │   └─ Determine DAL based on consequence
│  │
│  └─ Also consider: IEC 62304 patterns for comparison
│
├─ Is this for MEDICAL DEVICE software?
│  ├─ YES: IEC 62304 REQUIRED
│  │   └─ Regulatory requirement for FDA/EU/Global
│  │   └─ Determine safety class (A/B/C)
│  │
│  └─ Also check: ISO 26262 patterns if connected to automotive
│
└─ ALL OTHER SYSTEMS?
   ├─ YES: Use ISO/IEC/IEEE 29148 + 29119
   │   ├─ For requirements: 29148:2018
   │   ├─ For testing: 29119 (parts 1-4)
   │   └─ For quality: INCOSE GtWR, IEEE 830
   │
   └─ Process maturity: ASPICE concepts
      (even without automotive context)

SPECIAL CASES:
├─ Software components in above systems → Use parent standard
├─ Risk-critical but non-safety → ISO 29148 + risk-based approach
├─ Internal/non-regulated → ISO 29148 minimum, INCOSE for best practice
```

---

## 15. Common Standards Conversions

### 15.1 ASIL ↔ DAL Rough Mapping

| ISO 26262 ASIL | DO-178C DAL | Equivalent Rigor |
|---|---|---|
| QM (Non-critical) | E | No safety req |
| ASIL A | D | Basic verification |
| ASIL B | C | Structured verification |
| ASIL C | B | Formal verification |
| ASIL D | A | Exhaustive verification, MC/DC |

### 15.2 Safety Class ↔ ASIL/DAL Mapping (IEC 62304)

| IEC 62304 Class | ASIL Equivalent | DAL Equivalent |
|---|---|---|
| Class A (No harm) | QM/ASIL A | Level D/E |
| Class B (Minor injury) | ASIL B | Level C |
| Class C (Fatal) | ASIL C-D | Level B/A |

---

## 16. Glossary of Key Terms

| Term | Definition |
|---|---|
| **ASIL** | Automotive Safety Integrity Level (ISO 26262) - A/B/C/D |
| **DAL** | Design Assurance Level (DO-178C) - A/B/C/D/E |
| **Safety Class** | Medical device risk classification (IEC 62304) - A/B/C |
| **MC/DC** | Modified Condition Decision Coverage - requires 100% for DO-178C Level A, ISO 26262 ASIL D |
| **Bidirectional Traceability** | Links flowing both forward (requirement→implementation) and backward (implementation→requirement) |
| **Orphaned Requirement** | Requirement with no downstream implementation or design allocation |
| **Orphaned Code** | Implementation with no upstream requirement traceability |
| **EARS** | Easy Approach to Requirements Syntax - standardized requirement patterns |
| **Diagnostic Coverage** | % of failures that are detected by built-in diagnostics |
| **Confirmation Measures** | ISO 26262 verification: Confirmation Review, Audit, Assessment |
| **FMEA** | Failure Mode and Effects Analysis - systematic hazard identification |
| **Requirement Baseline** | Approved, version-controlled set of requirements for a project phase |

---

## 17. Resources and Further Reading

### Standard Documents
- ISO/IEC/IEEE 29148:2018 - Requirements Engineering
- ISO/IEC/IEEE 29119-1 through 29119-4 - Software Testing
- ISO 26262:2018 - Automotive Functional Safety
- IEC 62304 - Medical Device Software Lifecycle
- DO-178C - Airborne Software Certification
- IEEE 830-1998 - Software Requirements Specification (Legacy)
- ASPICE - Automotive SPICE Process Assessment

### Guidance Documents
- INCOSE Guide to Writing Requirements V4 (2022)
- INCOSE Requirements Management Handbook
- Jama Software Requirements Management Guides
- Rapita Systems DO-178C Testing Guidance
- LDRA ISO 26262 and IEC 62304 Compliance Guides

### Tools and Platforms
- Jama Connect (comprehensive requirements management)
- ReqView (simple, ISO 29148-compliant)
- PTC Integrity (large-scale, automotive)
- Requisite Pro (legacy, still used)
- Doors (IBM, enterprise)
- Azure DevOps (development integration)

---

**Version:** 1.0
**Last Updated:** January 29, 2026
**Audience:** Requirements engineers, test planners, quality professionals
**Purpose:** Quick reference for standards-compliant requirements and testing

**Companion Document:** STANDARDS_RESEARCH_COMPREHENSIVE.md (for detailed reference)

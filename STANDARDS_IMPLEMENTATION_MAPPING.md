# Standards Implementation Mapping Guide

**Purpose:** Practical mappings between standards for requirements and test management implementation
**Audience:** Requirements managers, architects implementing multi-standard environments
**Context:** Supporting the comprehensive standards research document

---

## 1. Universal Requirement Attribute Mapping

This mapping shows how requirement attributes translate across all major standards examined.

### 1.1 Complete Attribute Cross-Reference

| Concept | ISO 29148 | IEEE 830 | INCOSE | DO-178C | ISO 26262 | IEC 62304 | ASPICE |
|---------|-----------|---------|--------|---------|-----------|-----------|---------|
| **Unique Identifier** | Requirement ID | Req # | REQ-ID | SR# | FSR ID | REQ ID | Req ID |
| **Statement/Text** | Requirement statement | Requirement text | Requirement text | Requirement | Functional safety requirement | Software requirement | Requirement statement |
| **Type/Classification** | Type attribute | Type | Requirement type | HLR/LLR | FSR/Non-FSR | Functional/Performance | Requirement type |
| **Source/Origin** | Source field | N/A | Derives from | N/A | Hazard reference | Risk control measure | Source traceability |
| **Safety/Risk Level** | Quality attribute (if safety) | N/A | Safety classification | DAL (A-E) | ASIL (A-D, QM) | Safety class (A-B-C) | Process capability level |
| **Allocated Component** | Allocation field | Design constraint | Allocated to | Allocated to | Component specification | Component reference | Component allocation |
| **Verification Method** | Verification method | Acceptance criteria | Verification approach | Verification method | Verification strategy | Verification method | Verification approach |
| **Acceptance Criteria** | Conditions, qualifications | Acceptance criteria | Success criteria | Verification objective | Performance specification | Acceptance criteria | Pass/fail criteria |
| **Priority** | Priority (optional) | N/A | Priority | Criticality level | ASIL-based rigor | Safety class-based | Resource priority |
| **Rationale** | Rationale (R) | Rationale | Necessity justification | Hazard justification | Safety basis document | Risk mitigation rationale | Justification |
| **Traceability** | Traceability links | Dependency links | Derived from links | Traceability matrix | Hazard-to-requirement links | Risk-to-requirement links | Requirement links |
| **Status** | Status (Draft/Approved) | N/A | Status | Approved status | Baseline status | Approved status | Status in process |
| **Version** | Version (in document) | Version | Version | N/A | Version | Version | Version control |

### 1.2 Translation Rules

**When implementing system for multiple standards:**

1. **Create unified attribute set** that covers all standards
2. **Map each standard concept** to unified field
3. **Mark mandatory attributes** per standard (non-applicable = null/N/A)
4. **Add metadata** indicating which standards apply to each requirement

**Example Unified Schema:**
```
{
  "id": "REQ-SYS-001",
  "statement": "...",
  "type": "Functional",
  "source": "STK-001",
  "standards_applicable": ["ISO29148", "ASPICE"],
  "iso29148": {
    "verification_method": "Test",
    "quality_attributes_verified": true
  },
  "aspice": {
    "process_group": "Engineering",
    "process": "System Requirements",
    "allocation": "Team-A"
  },
  "do178c": null,
  "iso26262": null,
  "iec62304": null
}
```

---

## 2. Requirements Statement Pattern Equivalences

### 2.1 EARS Patterns and Equivalent Standard Expressions

| Pattern | EARS Form | ISO 29148 | DO-178C | ISO 26262 | IEC 62304 |
|---------|-----------|-----------|---------|-----------|-----------|
| **Ubiquitous** | The [System] shall [Action] [Qual] | Primary pattern | HLR statement | Functional safety requirement | Functional requirement |
| **Event-Driven** | When [Event], [System] shall [Action] | Conditional requirement | Time-triggered requirement | Stimulus-response requirement | Event-driven requirement |
| **Conditional** | If [Condition], [System] shall [Action] | Qualified requirement | Mode-dependent requirement | Conditional control measure | Design-dependent requirement |
| **State-Based** | While [State], [System] shall [Action] | Mode-specific requirement | Operational mode requirement | System state requirement | Operational state requirement |
| **Optional** | [System] may [Action] unless [Constraint] | Non-mandatory goal | Capability (not requirement) | Design flexibility | Non-critical feature |
| **Quantified** | [System] shall [Action] [N] times [Period] | Quantified requirement | Periodic requirement | Frequency-specified requirement | Timing-dependent requirement |

### 1.2 Translation Examples

**Original EARS Pattern:**
```
"When a user enters invalid credentials, the system shall display an error message
within 500ms and allow re-entry without logout."
```

**ISO 29148 Translation:**
```
Requirement: System login error handling
Statement: "The system shall, upon detection of invalid authentication credentials,
generate and display an appropriate error message to the user within 500 milliseconds
and allow the user to re-attempt authentication without terminating the session."
Verification Method: Test (functional test with invalid inputs)
```

**DO-178C Translation (if flight-critical):**
```
High-Level Requirement: Authentication error handling shall maintain system safety
Low-Level Requirement: Invalid credential detection shall trigger error message display
within 500ms and preserve login session state
Verification: Functional test + error handling robustness test
DAL-Level Verification Objective: Ensure error is detected and communicated correctly
```

**ISO 26262 Translation (if vehicle-critical):**
```
Functional Safety Requirement: Invalid command detection and safe response
FSR: "Detection of invalid input command shall trigger safe state transition
within 500ms, maintaining vehicle stability margin"
Hazard Link: HAZ-001 (Loss of control from invalid command)
ASIL: D (Requires MC/DC verification of decision logic)
```

---

## 3. Verification Method Equivalence Matrix

### 3.1 How Standards Define Verification Methods

| Verification Type | ISO 29148 | DO-178C | ISO 26262 | IEC 62304 | ASPICE |
|---|---|---|---|---|---|
| **Inspection** | Document review, design review | Design review, code review | Review per V-model | Design review | Review activity |
| **Demonstration** | Manual system operation | System capability demonstration | Manual demonstration | System demonstration | Walkthrough |
| **Test** | Requirements-based testing | Test procedures with traceability | Test case specification | Risk-based test plan | Test process |
| **Analysis** | Mathematical verification, simulation | Static analysis (code, design) | FMEA, mathematical proof | Risk analysis | Assessment analysis |

### 3.2 Test Coverage Equivalence

| Coverage Goal | ISO 29148 | DO-178C | ISO 26262 | IEC 62304 | Test Coverage Type |
|---|---|---|---|---|---|
| **Basic Verification** | Functional test | Level E/D: Statement coverage | ASIL A/QM: Basic test | Class A: Documentation | 100% statement coverage |
| **Structural Coverage** | All branches exercised | Level C: Branch coverage | ASIL B: Branch coverage | Class B: Decision coverage | 100% branch coverage |
| **Condition-Independent** | Condition coverage | Level B: DC coverage | ASIL C: Condition coverage | Class C: MC/DC (critical) | 100% decision-condition |
| **Condition-Independent** | MC/DC-like analysis | Level A: MC/DC coverage | ASIL D: MC/DC coverage | Class C (critical): MC/DC | 100% MC/DC for complex logic |
| **Risk-Based** | Risk assessment drives coverage | N/A (fixed by DAL) | Risk drives verification | Risk-based test strategy | Risk assessment drives testing |

---

## 4. Traceability Framework Equivalences

### 4.1 Traceability Relationship Types Across Standards

| Relationship | ISO 29148 | DO-178C | ISO 26262 | IEC 62304 | ASPICE |
|---|---|---|---|---|---|
| **Derives From** | Requirement hierarchy | HLR ← System requirements | FSR ← Hazard analysis | Requirement ← Risk | Allocation path |
| **Allocated To** | Component allocation | → Design component | → Hardware/software element | → Implementation module | → Team/subsystem |
| **Implements** | Design realization | Design → Code | Safety measure → Implementation | Design → Code | Execution path |
| **Verified By** | Test case mapping | → Test procedure | → Verification activity | → Test case | → Review record |
| **Conflicts With** | Contradiction tracking | (Not formally tracked) | Design constraint conflicts | (Implicit in design) | (Tracked via audit) |
| **Depends On** | Prerequisite links | (Implicit in hierarchy) | (Implicit in design) | (Risk dependencies) | (Via traceability) |

### 4.2 Traceability Matrix Template Equivalences

#### ISO 29148 Traceability Matrix Columns
```
REQ-ID | Statement | Source | Allocation | Design | Test-Case | Verification
-------|-----------|--------|-----------|--------|-----------|---------------
REQ-001| Text      | STK-001| Component | DSN-001| TC-001   | PASS
```

#### DO-178C Traceability Matrix Columns
```
SR-ID | Description | HLR | Design | Code | Test-Proc | Coverage | Status
-------|-------------|-----|--------|------|-----------|----------|--------
SR-001| Text        | HLR-1| DES-1| src.c| STP-001  | 100% MC/DC| Verified
```

#### ISO 26262 Traceability Matrix Columns
```
FSR-ID | Safety Requirement | Hazard | ASIL | Design | Implementation | Test | Verification | Status
-------|-------------------|--------|------|--------|-----------------|------|--------------|--------
FSR-001| Text              | HAZ-001| D    | DES-001| src/safety.c   | TC-001| PASS         | Verified
```

#### IEC 62304 Traceability Matrix Columns
```
REQ-ID | Requirement | Class | Risk-Measure | Design | Implementation | Test | Verification | Status
-------|-------------|-------|--------------|--------|-----------------|------|--------------|--------
REQ-001| Text        | C     | RM-001       | DES-001| src/module.c   | TC-001| PASS         | Verified
```

#### ASPICE Traceability Tracking
```
Requirement | Source | Design | Code | Test | Review | Status
------------|--------|--------|------|------|--------|--------
REQ-001     | Traced | Traced | Link | Link | Record | L2+
```

---

## 5. Safety Classification Decision Matrices

### 5.1 Cross-Standard Risk Assessment Mapping

| Risk Factor | ISO 26262 ASIL | DO-178C DAL | IEC 62304 Class |
|---|---|---|---|
| **Lowest Risk** | QM/ASIL A | Level E/D | Class A |
| **Low-Medium Risk** | ASIL B | Level C | Class B |
| **High Risk** | ASIL C | Level B | Class C |
| **Highest Risk** | ASIL D | Level A | Class C (critical) |

### 5.2 Consequence-Based Selection

| Consequence | ASIL Selection | DAL Selection | Safety Class Selection |
|---|---|---|---|
| **No injury possible** | QM | E | A |
| **Light injury possible** | A | D | A |
| **Serious (reversible) injury** | B | C | B |
| **Serious (permanent) injury** | C | B | C |
| **Death/catastrophic** | D | A | C (critical) |

### 5.3 ASIL/DAL/Class Feature Mapping

| Feature | ASIL A | ASIL B | ASIL C | ASIL D | DAL E | DAL D | DAL C | DAL B | DAL A | IEC Class A | IEC Class B | IEC Class C |
|---------|--------|--------|--------|--------|-------|-------|-------|-------|-------|------------|------------|------------|
| **Statement Coverage** | Basic | 100% | 100% | 100% | - | 100% | 100% | 100% | 100% | - | 100% | 100% |
| **Decision Coverage** | - | - | 100% | 100% | - | - | 100% | 100% | 100% | - | 100% | 100% |
| **MC/DC Coverage** | - | - | - | 100% | - | - | - | - | 100% | - | (critical) | 100% (critical) |
| **Bidirectional Traceability** | Optional | Recommended | Required | Required | - | Recommended | Recommended | Required | Required | - | Recommended | Required |
| **Formal Verification** | - | - | Optional | Required | - | - | - | - | Required | - | - | Required (critical) |
| **Independence** | - | - | - | Required | - | - | - | - | Required | - | - | (Recommended) |
| **Diagnostic Coverage** | - | Recommended | Recommended | > 95% | - | - | - | - | > 99% | - | - | > 95% (critical) |

---

## 6. Requirements Quality Framework Equivalences

### 6.1 Quality Attribute Mappings

| Quality Attribute | ISO 29148 | INCOSE SMART | IEEE 830 | DO-178C | ISO 26262 | IEC 62304 | Verification |
|---|---|---|---|---|---|---|---|
| **Necessity** | Required | Relevant | Justified | Traced to HLR | Traced to hazard | Traced to risk | Upstream traceability audit |
| **Unambiguity** | Required | Specific | Singular | Non-ambiguous | Complete statement | Clear requirement | Peer review, interpretation test |
| **Completeness** | Required | Measurable | Adequate detail | Complete | All elements specified | Sufficient detail | Design team review |
| **Consistency** | Required | N/A (within SMART) | Non-conflicting | Consistent | No conflicts | Non-contradictory | Conflict matrix analysis |
| **Verifiability** | Required | Measurable | Verifiable criteria | Verifiable | Verifiable approach | Testable | Test coverage audit |
| **Traceability** | Required | Traceable | Referenced | Bidirectional required | Bidirectional required | Bidirectional required | Traceability matrix audit |
| **Feasibility** | Implied | Achievable | Feasible | Feasible approach | Feasible design | Achievable design | Technical review |

### 6.2 Quality Scoring Framework

**Universal Quality Score Formula:**
```
Quality = (Necessity × Unambiguity × Completeness × Consistency ×
           Verifiability × Traceability × Feasibility) / 7

For Safety-Critical (DO-178C/ISO 26262/IEC 62304):
Weights: All 100% (all mandatory)
Target Score: 100%

For Standard Systems (ISO 29148):
Weights: All 100% (all required)
Target Score: 95%+

For Non-Critical Systems (ASPICE, General):
Weights: Varied per risk
Target Score: 85%+
```

**Defect Scoring:**
```
Critical Defect (blocks design):
- Ambiguity in core functionality
- Missing mandatory attribute
- Impossible to implement
- Conflicts with other requirement
Impact: Requirement must be rewritten (100% score reduction)

Major Defect (significant rework):
- Unmeasurable acceptance criterion
- Incomplete specification
- Orphaned requirement
Impact: Score reduced to 70-80%, requirement revision required

Minor Defect (clarification needed):
- Missing optional attribute
- Inconsistent terminology
- Weak traceability link
Impact: Score reduced to 85-95%, comment/update required
```

---

## 7. Test Case Specification Equivalences

### 7.1 Standard Test Case Attribute Mapping

| Attribute | ISO 29119 | DO-178C | ISO 26262 | IEC 62304 | ASPICE |
|---|---|---|---|---|---|
| **Test Case ID** | Required | Test procedure # | FMEA/Test ID | Test case ID | Test case ID |
| **Test Objective** | Required | Verification objective | Verification strategy | Verification purpose | Test goal |
| **Test Items** | Required | Code units, requirements | Safety measures, design | Requirements, design | Requirements |
| **Test Data** | Required | Input values | Boundary conditions | Test inputs | Input data |
| **Test Steps** | Required | Step-by-step procedure | Test sequence | Test procedure | Test actions |
| **Expected Result** | Required | Expected output | Safety achievement | Requirement verification | Pass criteria |
| **Traceability** | Required | Requirement link | FSR link, hazard | Risk link, requirement | Requirement link |
| **Test Coverage** | Tracked | 100% coverage reported | 100% MC/DC (Level A) | Risk-based coverage | Standard coverage |
| **Approval/Sign-off** | Recommended | Required | Required (ASIL C+) | Required (Class C) | Formal record |

### 7.2 Test Coverage Equivalence Table

| Test Coverage Type | ISO 29119 Definition | DO-178C Usage | ISO 26262 Usage | IEC 62304 Usage |
|---|---|---|---|---|
| **Requirement Coverage** | "All requirements have at least one test case" | All requirements tested | All FSRs verified | All requirements tested |
| **Statement Coverage** | Every line of code executed | Minimum Level D/E | Minimum ASIL A | Baseline requirement |
| **Decision Coverage** | Every branch taken both ways | Level C requirement | ASIL B minimum | Class B requirement |
| **MC/DC Coverage** | Each condition independently affects output | Level A requirement | ASIL D requirement | Class C critical paths |
| **Functional Coverage** | All user scenarios tested | Capability verification | Safety scenario testing | Risk-based scenario testing |
| **Error Path Coverage** | All error conditions tested | Robustness testing (Level B+) | Failure mode testing | Error scenario testing |

---

## 8. Process Capability Level Mappings

### 8.1 ASPICE Capability Levels and Standard Equivalence

| ASPICE Level | Requirement Management | Verification Status | Standard Equivalence |
|---|---|---|---|
| **L0 (Incomplete)** | No formal process | Ad-hoc testing | Pre-standard, immature |
| **L1 (Performed)** | Informal tracking | Manual verification | Basic ISO 29148 compliance |
| **L2 (Managed)** | Formal change control, baseline | Requirements-based testing | ISO 29148 + 29119 foundation |
| **L3 (Established)** | Standard process, traceability | Structured test coverage | Full ISO 29148 + 29119 compliance |
| **L4 (Predictable)** | Quantified metrics, SPC | Measured coverage targets | DO-178C Level B/C compliance |
| **L5 (Optimizing)** | Continuous improvement | Optimized verification | DO-178C Level A, ASIL D, IEC Class C |

### 8.2 Safety Standard Compliance by ASPICE Level

| Standard | Minimum ASPICE Level | Capability Requirements | Evidence Required |
|---|---|---|---|
| **ISO 29148 (General)** | L2 | Formal requirements process, baseline | SRS document, traceability matrix |
| **DO-178C Level D** | L2 | Change control, requirements tracking | Requirements spec, test summary |
| **DO-178C Level C** | L3 | Standard process, traceability metrics | Design traceability, test coverage |
| **DO-178C Level B** | L4 | Measured coverage, quantified metrics | MC/DC matrix, verification summary |
| **DO-178C Level A** | L4+ | Independence, predictive control | Certification evidence, formal verification |
| **ISO 26262 ASIL A** | L2 | Basic requirements tracking | Hazard analysis link |
| **ISO 26262 ASIL B** | L3 | Traceability, risk-based testing | Traceability matrix, FMEA |
| **ISO 26262 ASIL C** | L4 | Measured traceability, confirmation | Confirmation review record |
| **ISO 26262 ASIL D** | L4+ | Quantified metrics, formal methods | Audit/assessment evidence |
| **IEC 62304 Class B** | L3 | Standard process, design traceability | V&V plan, test summary |
| **IEC 62304 Class C** | L4 | Risk-based metrics, comprehensive traceability | Traceability matrix, risk matrix |

---

## 9. Implementation Roadmap by Standards Combination

### 9.1 Single Standard Implementation (Easiest)

**Scenario: Implementing for ISO/IEC/IEEE 29148 only (general system, no safety criticality)**

```
Phase 1 (Weeks 1-4): Foundation
  - Establish requirement ID scheme (REQ-SYS-XXX, REQ-SW-XXX)
  - Create requirement template with mandatory attributes
  - Define requirement statement patterns
  - Establish basic requirements management tool (spreadsheet or simple tool)

Phase 2 (Weeks 5-8): Quality and Traceability
  - Implement quality checklist review process
  - Create initial traceability matrix template
  - Define verification method assignments
  - Start linking requirements to stakeholder needs

Phase 3 (Weeks 9-12): Integration and Baselines
  - Integrate with design documentation process
  - Create test case traceability mappings
  - Establish requirements baseline and version control
  - Document requirement change process

Resulting Maturity: ASPICE L2-L3 (Managed to Established)
```

### 9.2 Dual Standard Implementation (Moderate)

**Scenario: Implementing for DO-178C Level B and ISO 29148 (Airborne system)**

```
Phase 1 (Weeks 1-6): Unified Framework
  - Create unified attribute schema covering both standards
  - Establish requirement ID scheme with DAL prefix (HIR-SYS-B-XXX)
  - Define EARS patterns matching both standards
  - Set up requirements management tool supporting bidirectional traceability

Phase 2 (Weeks 7-12): DO-178C Specific
  - Implement HLR vs. LLR distinction
  - Create separate SRS document per DO-178C structure
  - Establish test procedure specification format
  - Define coverage measurement approach (Decision/Condition coverage for Level B)

Phase 3 (Weeks 13-18): Integration and Metrics
  - Link requirements to design components
  - Create comprehensive traceability matrix
  - Establish verification objective mapping
  - Define metrics for bidirectional traceability coverage (target: 100%)

Phase 4 (Weeks 19-24): Verification and Certification
  - Conduct requirements quality audit
  - Perform traceability gap analysis and remediation
  - Compile verification summary report
  - Prepare certification evidence package

Resulting Maturity: ASPICE L3-L4 (Established to Predictable)
```

### 9.3 Multi-Standard Implementation (Complex)

**Scenario: Automotive supplier implementing ISO 26262 ASIL D + ASPICE L4**

```
Phase 1 (Months 1-2): Assessment and Planning
  - Analyze all affected requirements (existing and new)
  - Map existing processes to ISO 26262 and ASPICE
  - Identify gaps in current practices
  - Plan tool selection and implementation

Phase 2 (Months 3-4): Tool Implementation and Training
  - Deploy requirements management tool supporting ASIL D traceability
  - Establish ASIL-based requirement ID scheme (FSR-ASILD-XXX)
  - Train team on ISO 26262, ASPICE, and tool usage
  - Create organizational standards and guidelines

Phase 3 (Months 5-7): Process Maturity
  - Implement formal requirements review and approval process
  - Establish Functional Safety Concept documentation
  - Create requirements specification with hazard traceability
  - Implement quantified metrics collection

Phase 4 (Months 8-10): Verification and Formal Methods
  - Implement risk-based test strategies
  - Establish MC/DC coverage measurement for critical functions
  - Conduct formal verification for ASIL D requirements
  - Perform FMEA with diagnostic coverage analysis

Phase 5 (Months 11-12): Confirmation and Optimization
  - Conduct Confirmation Review (independent review)
  - Execute Audit (ISO 26262 process compliance)
  - Perform Assessment (metric achievement)
  - Continuous improvement based on metrics

Resulting Maturity: ASPICE L4-L5 (Predictable to Optimizing)
```

---

## 10. Requirement Allocation and Responsibility Matrix

### 10.1 Standard-Specific Activities and Ownership

| Activity | ISO 29148 | DO-178C | ISO 26262 | IEC 62304 | ASPICE | Typical Owner |
|---|---|---|---|---|---|---|
| **Requirements Specification** | M | M | M | M | M | Requirements Engineer |
| **Requirement Quality Review** | M | M | M | M | M | QA / Requirements Analyst |
| **Traceability Matrix Creation** | M | M | M | M | M | Requirements Manager |
| **Traceability Verification** | M | M | M | M | M | QA / Verification Lead |
| **Verification Method Assignment** | M | M | M | M | R | Requirements Analyst |
| **Test Case Specification** | R | M | M | M | M | Test Engineer |
| **Test Execution** | R | M | M | M | M | QA / Tester |
| **Coverage Analysis** | O | M | M | M | M | QA Lead |
| **Risk/Hazard Analysis** | O | O (indirect) | M | M | O | Safety Engineer |
| **Design Review** | M | M | M | M | M | Architecture/Design Lead |
| **Baseline Creation** | M | M | M | M | M | Configuration Manager |
| **Change Management** | M | M | M | M | M | Change Control Board |
| **Certification Preparation** | O | M | M (confirmation) | M | M | Program Manager + QA |
| **Metrics Collection** | O | R | M | M | M | Quality Metrics Lead |

**M = Mandatory, R = Recommended, O = Optional**

---

## 11. Troubleshooting Cross-Standard Issues

### 11.1 Common Integration Problems

| Problem | Root Cause | Solution |
|---------|-----------|----------|
| **Different ID schemes conflict** | Standards use different naming | Create unified ID mapping table, maintain external links |
| **Requirement appears in multiple standards** | Overlapping scope | Create single source requirement, tag with applicable standards |
| **Traceability incomplete** | Tools don't interoperate | Use export/import with manual verification, upgrade to integrated tool |
| **Conflicting verification requirements** | Standards have different rigor | Choose highest rigor level, document as meeting all requirements |
| **Classification mismatch** (ASIL vs. DAL vs. Class) | Different risk assessment frameworks | Create mapping table, assign highest safety level |
| **Coverage metrics don't align** | Different measurement approaches | Measure all metrics, report against each standard's requirement |
| **Change management creates orphans** | Incomplete traceability updates | Enforce change workflow requiring traceability verification |
| **Baseline versions out of sync** | Version control issues | Single source of truth, all standards derive from it |

### 11.2 Migration and Transition Strategies

**When changing standards or maturity levels:**

```
Step 1: Inventory existing artifacts
  - Count and categorize all requirements
  - Assess current traceability state
  - Evaluate tool capabilities
  - Identify gaps

Step 2: Create mapping strategy
  - Define how old requirements map to new standard
  - Create temporary mapping table
  - Plan transition timeline
  - Identify retraining needs

Step 3: Phased migration
  - Start with new projects under new standard
  - Gradually migrate existing requirements
  - Run parallel traceability for transition period
  - Validate completeness before cleanup

Step 4: Validation and verification
  - Audit traceability completeness
  - Verify quality of migrated requirements
  - Test impact on downstream processes
  - Confirm certification readiness

Step 5: Baseline and monitor
  - Establish new baseline
  - Monitor metrics for continued compliance
  - Address emerging issues
  - Refine processes based on experience
```

---

## 12. Tool Evaluation Checklist for Multi-Standard Support

### 12.1 Must-Have Capabilities for Each Standard

#### ISO/IEC/IEEE 29148 Support
- [ ] Customizable requirement ID scheme
- [ ] Rich text editing with formatting
- [ ] Template-based requirement creation
- [ ] Traceability link creation
- [ ] Simple reporting and export
- [ ] Version control / baseline support
- **Minimum Tool Tier:** Spreadsheet with structure

#### DO-178C Support (All Levels)
- [ ] HLR/LLR distinction capability
- [ ] Automated traceability matrix generation
- [ ] Test case mapping to requirements
- [ ] Coverage metric tracking (statement, branch, MC/DC)
- [ ] Verification objective linkage
- [ ] Certification report generation
- [ ] Change control and audit trail
- **Minimum Tool Tier:** Specialized requirements tool (not spreadsheet)

#### ISO 26262 Support (ASIL B+)
- [ ] ASIL level classification and tracking
- [ ] Hazard analysis linkage
- [ ] FSR vs. non-FSR distinction
- [ ] FMEA integration or linking
- [ ] Bidirectional traceability verification
- [ ] Diagnostic coverage calculation
- [ ] Confirmation measure documentation
- **Minimum Tool Tier:** Safety-certified requirements tool

#### IEC 62304 Support (Class B+)
- [ ] Safety class classification
- [ ] Risk control measure traceability
- [ ] Design review linkage
- [ ] Verification test mapping
- [ ] V&V plan generation
- [ ] Risk-based test strategy support
- [ ] Regulatory reporting templates
- **Minimum Tool Tier:** Medical device-qualified tool

#### ASPICE Support (Level 3+)
- [ ] Process reference model alignment
- [ ] Work product assessment support
- [ ] Capability level metrics
- [ ] Traceability coverage metrics
- [ ] Process gap analysis
- [ ] Assessment report generation
- **Minimum Tool Tier:** Requirements tool with metrics

### 12.2 Tool Selection Decision Matrix

| Tool Type | Capacity | Scalability | Integration | Certification | Cost | Learning Curve |
|-----------|----------|-------------|-------------|---|---|---|
| **Spreadsheet** | <1000 req | Poor | Manual | None | $ | Minimal |
| **Word/Wiki** | 1000-5000 req | Poor | Poor | None | $ | Low |
| **Simple Requirements Tool** | 5000-50k req | Medium | API | Basic | $$ | Low |
| **Enterprise Requirements** | 50k-500k req | Good | Extensive | Industry | $$$ | Medium |
| **Specialized Safety Tool** | All | Excellent | Full | Yes (DO-178C, ISO 26262) | $$$$ | Medium-High |
| **Cloud Requirements** | All | Excellent | Very Good | Emerging | $$ | Low |

**Recommendation:** For multi-standard environments with ASIL D / DAL A / Class C: **Invest in specialized safety-qualified tool**
(Cost of non-compliance exceeds tool cost)

---

## 13. Certification Package Generation Checklist

### 13.1 DO-178C Level A Certification Package

```
□ Software Requirements Specification (complete, with traceability)
□ Architectural Design Specification
□ Detailed Design Specification
□ Source Code (with annotations)
□ Software Version Description
□ Build Procedures Documentation
□ Test Procedures (100% with expected results documented)
□ Test Results (all passing, documented)
□ Test Coverage Analysis (100% MC/DC reported)
□ Verification Summary Report
□ Software Quality Assurance Records
□ Requirements-to-Design Traceability Matrix
□ Design-to-Code Traceability Matrix
□ Requirements-to-Test Case Matrix
□ Cumulative Hazard Index (or Safety Assessment)
□ Tool Certification Records
□ Configuration Management Records
□ Change Control Records
□ Certification Review Approval
```

### 13.2 ISO 26262 ASIL D Certification Package

```
□ Functional Safety Concept with ASIL assignment
□ Item Definition and Assumptions
□ Hazard Analysis and Risk Assessment
□ Functional Safety Requirements Specification
□ Functional Safety Concept V&V Plan
□ System Architectural Design
□ Architectural Design V&V Plan
□ Hardware Design Specification and Analysis
□ Software Design Specification
□ Software V&V Plan
□ Source Code Documentation
□ Unit Verification Records
□ Integration Test Plan and Results
□ System Test Plan and Results
□ FMEA (Hardware and Software)
□ Diagnostic Coverage Analysis (>95% required)
□ Traceability Matrix (bidirectional)
□ Change Management Records
□ Safety Management Report
□ Confirmation Review Report
□ Audit Report
□ Assessment Report
```

### 13.3 IEC 62304 Class C Certification Package

```
□ Risk Analysis Report
□ Risk Control Options Analysis
□ Risk Control Measures (with traceability)
□ Software Safety Plan
□ Software Requirements Specification
□ Software Architectural Design
□ Software Detailed Design
□ Design Review Report
□ Source Code
□ Unit Verification Report (code review, unit tests)
□ Integration Test Plan and Report
□ System Test Plan and Report
□ Requirements Verification Matrix
□ Software V&V Plan
□ Software V&V Summary Report
□ Software Change Log
□ Software Release Note
□ Risk Management Review
□ Software Quality Records
```

---

## 14. Quick Decision Trees for Standards Selection

### 14.1 "Which standard(s) must I implement?" Decision Tree

```
START

├─ Does this software control vehicle safety functions?
│  ├─ YES: ISO 26262 REQUIRED (ASIL A-D based on risk)
│  │        └─ Also consider: ASPICE for process assessment
│  │
│  └─ NO: Continue...
│
├─ Is this software for commercial aircraft?
│  ├─ YES: DO-178C REQUIRED (DAL A-E based on criticality)
│  │        └─ Also reference: IEC 62304 patterns for comparison
│  │
│  └─ NO: Continue...
│
├─ Is this software component of a medical device?
│  ├─ YES: IEC 62304 REQUIRED (Class A-C based on risk)
│  │        └─ Also reference: ISO 26262 patterns
│  │
│  └─ NO: Continue...
│
├─ Is this software for any regulated industry (aerospace, medical, automotive)?
│  ├─ YES: ISO/IEC/IEEE 29148 + 29119 REQUIRED as minimum
│  │        └─ Plus: Domain-specific standard (ISO 26262, DO-178C, IEC 62304, etc.)
│  │
│  └─ NO: Continue...
│
└─ Is this internal/non-regulated software?
   ├─ YES: ISO/IEC/IEEE 29148 + 29119 RECOMMENDED (best practice)
   │        └─ ASPICE for process maturity assessment
   │
   └─ For any organization: INCOSE Guide to Writing Requirements (quality best practice)
```

### 14.2 "What safety level do I need?" Decision Tree

```
START: Assessing safety requirements

├─ Determine CONSEQUENCE if software fails
│  ├─ No injury/harm possible → Lowest level
│  ├─ Light injury possible → Low-Medium level
│  ├─ Serious injury possible → Medium-High level
│  └─ Death/catastrophic → Highest level
│
├─ Determine EXPOSURE (how often hazardous situation occurs)
│  ├─ Rarely → Low exposure factor
│  ├─ Occasionally → Medium exposure factor
│  ├─ Frequently → High exposure factor
│  └─ Very frequently → Very high exposure factor
│
├─ Determine CONTROLLABILITY (can driver/operator prevent harm?)
│  ├─ Easy to control → High controllability
│  ├─ Normal control possible → Medium controllability
│  ├─ Difficult to control → Low controllability
│  └─ Nearly impossible → Very low controllability
│
└─ SELECT SAFETY LEVEL
   ├─ ISO 26262: Highest consequence + highest exposure + lowest control = ASIL D
   ├─ DO-178C: Most critical system function = DAL A
   └─ IEC 62304: Likely serious injury = Class C
```

---

## 15. Reference Implementation Checklist

### 15.1 First-Time Implementation (Any Standard)

- [ ] **Executive sponsorship secured** - Budget and schedule approved
- [ ] **Team trained** - Requirements engineers, testers, architects, QA staff
- [ ] **Tool selected and installed** - Meets standard requirements and organizational needs
- [ ] **Process documented** - Written procedures for requirements creation, review, verification
- [ ] **Templates created** - Requirement, test case, traceability templates
- [ ] **Quality criteria defined** - Clear pass/fail criteria for requirement quality
- [ ] **Verification strategy established** - How requirements will be verified
- [ ] **Traceability approach defined** - Bidirectional traceability method and tool support
- [ ] **Baseline process established** - How requirements are approved and frozen
- [ ] **Change management process** - How changes are requested, reviewed, approved
- [ ] **Metrics defined** - Quality, coverage, traceability metrics to track
- [ ] **Audit approach established** - How compliance will be verified
- [ ] **Certification path identified** - What evidence is needed for certification
- [ ] **Training completed** - All team members understand standard and process
- [ ] **Pilot project executed** - Small project to validate and refine process
- [ ] **Process refined** - Lessons from pilot incorporated
- [ ] **Full deployment** - Rollout across organization/program

---

**Document Version:** 1.0
**Date:** January 29, 2026
**Purpose:** Implementation guidance for multi-standard requirements and test environments
**Related Documents:**
- STANDARDS_RESEARCH_COMPREHENSIVE.md (detailed reference)
- STANDARDS_QUICK_REFERENCE.md (quick lookup)

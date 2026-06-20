# Enterprise ALM Deep-Dive Research

## Comprehensive Analysis of IBM DOORS Next Generation, Jama Connect, and Polarion ALM

**Research Date:** January 29, 2026
**Focus Areas:** Requirement Object Structure, Traceability Models, Change Impact Analysis, Baseline Management, Formal Attributes, Compliance Evidence, Custom Attributes, and Suspect Link Detection

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [IBM DOORS Next Generation](#ibm-doors-next-generation)
3. [Jama Connect](#jama-connect)
4. [Polarion ALM](#polarion-alm)
5. [Comparative Analysis](#comparative-analysis)
6. [Key Findings & Patterns](#key-findings--patterns)
7. [Implementation Recommendations](#implementation-recommendations)

---

## Executive Summary

This research provides extreme-depth technical documentation of three enterprise-grade requirements management and application lifecycle management (ALM) platforms. The three platforms—IBM DOORS Next Generation, Jama Connect, and Polarion ALM—represent the gold standard in requirements traceability, compliance evidence management, and change impact analysis for safety-critical and regulated industries (automotive, aerospace, medical device, railway).

### Critical Findings

**Requirement Object Structure:**
- All three platforms use artifact/work-item-based object models with configurable custom attributes
- Support hierarchical decomposition (parent-child relationships)
- Metadata includes creation timestamp, modification history, author/owner tracking
- Baseline/snapshot capabilities for immutable point-in-time captures
- Primary distinction: IBM DOORS uses "Artifacts," Jama uses "Items," Polarion uses "Work Items"

**Traceability Models:**
- Bidirectional link support with configurable link roles/types
- Support for forward (requirements→design→code→tests) and backward traceability
- Coverage matrices computed based on relationship rules
- Suspect link mechanisms for detecting when linked items require review
- Real-time or batch-based coverage calculation

**Change Impact Analysis:**
- Propagation algorithms traverse link networks to identify affected items
- Suspect link mechanisms automatically flag downstream items when upstream changes occur
- Impact analysis can be run on individual items or change requests
- Notification systems alert stakeholders of affected items

**Baseline/Configuration Management:**
- Immutable snapshots at specific points in time
- Version history for all artifacts with complete audit trails
- Hierarchical baseline support for complex product structures
- Baseline comparison capabilities

**Formal Attributes:**
- Standard attributes: Priority, Status, Source, Owner, Rationale
- Acceptance criteria and verification methods typically captured in description/notes fields
- All platforms support rich text for detailed specifications
- Custom attribute types extend standard attributes

**Compliance Evidence:**
- All three platforms support ISO 26262, DO-178C equivalents
- Integrated verification/validation traceability
- Template frameworks for standards-specific requirements
- Complete audit trails for regulatory traceability

---

## IBM DOORS Next Generation

### Platform Overview

IBM DOORS Next Generation (DOORS NG) is part of the IBM Engineering Requirements Management suite, built on the IBM Jazz platform technology. It's a browser-based requirements management tool designed for complex engineering projects with emphasis on traceability and scalability.

**Key Architectural Characteristics:**
- Runs on IBM Jazz platform (OSLC-based)
- Web client architecture for remote accessibility
- Supports hierarchical module structures
- Artifact-based object model

### Requirement Object Structure

#### Core Artifact Definition

In DOORS Next, a **requirement** is an instance of an "Artifact" type. Artifacts are the foundational objects that contain requirements and supporting information.

**Mandatory Attributes:**
- `ArtifactType` (enumeration) - Defines what type of artifact this is (e.g., Requirement, Design, Test Case)
- Primary text or Name (required for creation)

**Standard Artifacts Include:**
- Requirements
- Design artifacts
- Text descriptions
- Diagrams
- Business goals/objectives
- Justifications
- Headings
- Tables/images

#### Attribute Data Types Supported

IBM DOORS Next supports the following custom attribute data types:

**Basic Types:**
1. **String** - Free-form text with character limit
2. **Integer** - Whole numbers with optional bounds
3. **Float** - Decimal numbers with precision specification
4. **Boolean/Logical** - True/False values
5. **Date** - Calendar entries (single date)
6. **DateTime** - Calendar with time entries (bounded range)

**Structured Types:**
7. **Enumeration** - Numbered list of predefined values with textual labels
   - Values are ordered (order determines UI presentation)
   - Can add/remove entries and reorder as needed
   - Each enumeration entry has an integer ID and text label
8. **User Reference** - Links to user objects in the system
9. **Rich Text** - Formatted text with HTML-like support (bullets, numbering)
   - **Note:** Primary Text field only supports Rich Text; other custom attributes have limitations
10. **Calculated/DXL Attributes** - Computed values using DXL scripting
    - Uses constant `attrDXLName` to reference the attribute being calculated
    - Can reference other attribute values in calculations
    - Reusable across multiple attributes

#### Metadata Storage

DOORS artifacts store comprehensive metadata:

**Modification Tracking:**
- Creator identity
- Modification history with timestamps
- Last modified by (user identity)
- Complete version history

**Module-Level Metadata:**
- Artifact ID list in module METADATA section
- Module hierarchy information
- Artifact ordering within modules

**Import/Export Metadata:**
- METADATA section in CSV/Excel exports must be preserved
- Contains artifact ID mappings essential for proper module management
- Required for subsequent updates via import

#### Primary Text vs. Attributes

- **Primary Text**: The main content of the requirement; supports rich formatting
  - Derived from user selections
  - Immediately propagates to all reused instances
  - Cannot be null for creation (must have Name or Primary Text)

- **Formal Attributes**: Store structured data about the requirement
  - Standard attributes: Source, Priority, Acceptance status
  - Custom attributes defined by project team
  - Limited to specific data types (with Primary Text being the rich-text exception)

### Link Model and Traceability

#### Link Types and Roles

IBM DOORS Next uses **Link Relationships** to create traceability. Link relationships are characterized by:

1. **Directional nature** - Forward and backward links
2. **Type definition** - Specifies what kind of relationship
3. **Rules enforcement** - Can restrict link creation between specific artifact types
4. **Bidirectional support** - Same link can be viewed from both directions

**Common Link Types (typically configured per project):**
- `Satisfies` - Requirement satisfied by design
- `Verifies` - Test verifies requirement
- `Refines` - Lower-level refinement of higher-level requirement
- `Depends On` - Dependency relationship
- `Parent/Child` - Hierarchical decomposition
- `Related To` - Generic relationship

#### Link Rules and Constraints

Administrators define **Link Rules** that specify:
- Source artifact type(s) that can create the link
- Target artifact type(s) that can receive the link
- Direction enforcement
- Bidirectional vs. unidirectional

**Example Rule Structure:**
```
From: Requirement
To: TestCase
LinkType: VerifiedBy
Bidirectional: Yes
```

### Change Impact Analysis

#### Impact Propagation Model

IBM DOORS Next supports impact analysis through:

1. **Traceability Link Traversal** - Following link relationships to identify connected items
2. **Upstream/Downstream Navigation** - Visual exploration of impact scope
3. **Coverage Analysis** - Ensuring all impacted items have corresponding artifacts in downstream phases

#### Change Impact Assessment Workflow

1. Select item to analyze
2. System traverses all outgoing links (forward traceability)
3. System traverses all incoming links (backward traceability)
4. Display complete impact set to user
5. Optional: Filter by artifact type or link type

**Scope Calculation:**
- Direct impacts: Items directly linked to the changed item
- Transitive impacts: Items linked through multiple hops (configurable depth)
- Artifact type filters available to focus impact analysis

#### Suspect Links

While not as explicitly named as in other platforms, IBM DOORS Next can detect:
- Missing links (gap analysis)
- Links to deleted artifacts
- Broken traceability chains
- Incomplete coverage (items without verification)

### Baseline and Configuration Management

#### Baseline Creation

IBM DOORS Next supports **Baselines** (sometimes called "Configurations"):

**Characteristics:**
- Point-in-time snapshot of modules and artifacts
- Immutable once created
- Includes specific versions of all contained artifacts
- Labeled with version identifier

**Baseline Content:**
- Specific artifact versions at baseline creation time
- Link relationships as they existed at that time
- Attribute values as of baseline date
- Full metadata including modification history

#### Configuration Comparison

Users can:
1. Compare current state to baseline
2. Identify what has changed
3. View delta reports
4. Trace modifications back to baselined state

#### Reuse and Reusability

IBM DOORS Next supports **Artifact Reuse** where:
- Same artifact appears in multiple modules
- Changes to artifact propagate to all reuse instances
- Metadata remains shared across reuses
- Each module maintains ordering/context of reused artifacts

### Formal Attributes and Compliance

#### Standard Formal Attributes

IBM DOORS Next typically includes:

| Attribute | Data Type | Purpose |
|-----------|-----------|---------|
| `Source` | String/Enumeration | Who specified the requirement |
| `Priority` | Enumeration | Requirement priority level |
| `Status` | Enumeration | Requirement status (Draft, Approved, etc.) |
| `Accepted` | Boolean | Whether developers have accepted requirement |
| `Owner` | User Reference | Person responsible |
| `Rationale` | Rich Text | Why requirement exists |
| `Verification Method` | Enumeration | How verification will occur (Test, Review, Analysis, Inspection) |

#### Custom Attributes for Compliance

For standards compliance, typical custom attributes include:

**ISO 26262 / Functional Safety:**
- `ASIL` (Automotive Safety Integrity Level) - Enumeration (A, B, C, D)
- `Safety Goal Identifier` - String
- `Functional Safety Requirement` - Boolean
- `Hazard Reference` - Link/String
- `Derived From HARA` - Boolean

**DO-178C / Aerospace:**
- `DAL` (Design Assurance Level) - Enumeration (A-E)
- `Traceability Justification` - Rich Text
- `Verification Method` - Enumeration
- `Criticality` - Enumeration

**Medical Device (IEC 62304):**
- `Software Safety Classification` - Enumeration (Class A, B, C)
- `Verification Method` - Enumeration
- `Risk Control` - Link reference
- `Validation Method` - Enumeration

### Compliance Evidence Storage

IBM DOORS Next provides support for compliance through:

**Rational DOORS Kit for ISO 26262 and IEC 61508:**
- Includes pre-built templates for ISO 26262
- DXL scripts for ASIL calculation
- Artifact types and custom attributes pre-configured
- Verification method mapping to standard requirements
- TÜV SÜD qualified for ASIL A-D applications

**Evidence Linkage:**
1. Requirements linked to design items
2. Design items linked to code components
3. Code linked to test cases
4. Test results linked back to requirements
5. All linkages become part of compliance evidence package

**Audit Trail:**
- Complete modification history for every artifact
- Creator/modifier identity captured
- Timestamp for every change
- Change rationale (via workflow/comments)
- Immutable baseline captures for formal reviews

### Data Export and ReqIF Support

IBM DOORS Next supports ReqIF (Requirements Interchange Format) for:
- Exchanging requirements with other tools
- Preserving attribute types during export
- Maintaining link structures
- Complex attribute type mapping

---

## Jama Connect

### Platform Overview

Jama Connect is a cloud-native SaaS requirements management platform emphasizing "Live Traceability" across the complete systems development lifecycle (SDLC). It's specifically designed for bidirectional traceability and real-time coverage analysis.

**Key Architectural Characteristics:**
- Cloud-native SaaS architecture
- Emphasis on real-time traceability
- Multi-team collaboration features
- Live Trace Explorer for dynamic analysis

### Item Object Structure

#### Core Item Definition

In Jama Connect, requirements are called **Items** and are the fundamental unit of traceability. Items are instances of configurable **Item Types**.

**Mandatory Fields:**
- `Item Type` - Classification of the item (Requirement, Test Case, Risk, etc.)
- `Name` or Description - Human-readable identifier

**Standard Fields (always present):**
- `Created` - Creation timestamp
- `Created By` - User who created item
- `Modified` - Last modification timestamp
- `Modified By` - User who last modified
- `Status` - Current lifecycle state
- `Project` - Project container
- `Item ID` - Unique identifier

#### Item Type Configuration

Jama Connect allows organizations to create custom Item Types with specific field sets. Typical Item Types include:

**Standard Item Types:**
1. **Requirements** - High-level and detailed requirements
2. **Test Cases** - Verification test cases
3. **Risks** - Project risks
4. **Design Items** - Design specifications
5. **Test Results** - Test execution results
6. **Change Requests** - Change management items

#### Field Types Supported

Jama Connect supports the following custom field types for Items:

**Text Fields:**
1. **Text** - Single-line text (255 character limit, no formatting)
2. **Rich Text** - Formatted text with bullets, numbering, and HTML-like support
   - Supports embedded images
   - Allows hyperlinks
   - Preserves formatting on export

**Numeric Fields:**
3. **Number** - Integer or decimal values
4. **Percentage** - Numeric field displayed as percentage

**Selection Fields:**
5. **Dropdown/Enumeration** - Single-select from predefined list
6. **Multi-Select** - Multiple selections from predefined list
   - Each selection state tracked independently
   - Can be filtered and searched independently

**Date/Time Fields:**
7. **Date** - Single calendar date
8. **DateTime** - Calendar date with time
9. **Time** - Time-only field

**Reference Fields:**
10. **User Field** - Reference to user in system
    - Can be multi-select for multiple assignees
    - Triggers notifications to assigned users

11. **Single Item Link** - Reference to another item
12. **Multi-Item Link** - References to multiple items (typically for direct relationships)

**Computed Fields:**
13. **Calculated Fields** - Automated calculations
    - **Operations Supported:**
      - Addition
      - Multiplication
      - Average
      - Weighted Shortest Job First (WSJF)
      - Simple logic conditions
    - **Results:** Can be added to List View for sorting/filtering
    - **Recalculation:** Real-time as dependencies change

**System Fields (read-only):**
14. **Status** - Item lifecycle state
15. **Coverage** - Calculated traceability coverage metrics
16. **Relationship Status Indicator** - Visual indicator of link health (suspect, valid, etc.)

#### Formal Requirements Attributes

Typical formal requirement item types include fields for:

| Field | Type | Purpose |
|-------|------|---------|
| `Name` | Text | Brief requirement identifier |
| `Description` | Rich Text | Complete requirement specification |
| `Priority` | Dropdown | Requirements priority (Critical, High, Medium, Low) |
| `Status` | Dropdown | Lifecycle state (Draft, Review, Approved, Implemented) |
| `Owner` | User Field | Responsible party |
| `Rationale` | Rich Text | Why requirement exists |
| `Source` | Dropdown/Text | Requirement source (Customer, Regulatory, Internal) |
| `Acceptance Criteria` | Rich Text | How to determine requirement satisfaction |
| `Verification Method` | Dropdown | Method of verification (Test, Review, Analysis) |
| `Traceability Status` | Read-only | Coverage/traceability health indicator |

### Traceability Model and Link Types

#### Relationship (Link) Types

Jama Connect implements relationships between Items. Relationship direction is critical to impact analysis and coverage computation.

**Standard Relationship Types:**

| Link Type | Direction | Meaning |
|-----------|-----------|---------|
| `Related To` | Bidirectional | Generic relationship without specific semantics |
| `Derived From` | Downstream → Upstream | Item is detailed derivation of upstream item |
| `Dependent On` | Directional | Item depends on target item |
| `Satisfies` / `Satisfied By` | Bidirectional | Requirement satisfied by design/implementation |
| `Verified By` | Requirement → Test | Requirement verified by test case |
| `Mitigates` | Risk → Mitigation | Risk mitigated by mitigation strategy |
| `Validated By` | Requirement → Test Result | Requirement validated by test result |
| `Parent/Child` | Hierarchical | Decomposition relationship |

#### Upstream and Downstream Navigation

Jama uses **upstream** and **downstream** terminology:

- **Upstream**: Requirements, stakeholder needs, regulatory requirements
- **Downstream**: Design, implementation, test cases, test results

**Relationship Direction Semantics:**
- A requirement has relationships TO (downstream) design items and tests
- A test case has relationships FROM (upstream) requirements
- Directionality is enforced by relationship rules configured by org admin

#### Relationship Rules and Configuration

Organization administrators define rules that:
1. Specify allowed relationship types between specific item types
2. Enforce relationship direction requirements
3. Control whether relationships can be reversed during sync with other systems
4. Define which fields trigger suspect links

**Rule Structure:**
```
Source Item Type: Requirement
Target Item Type: Test Case
Relationship Type: Verified By
Direction: Unidirectional (Requirement → Test)
Suspect Trigger Fields: Description, Status, Priority
```

#### Suspect Links Detection

Jama Connect implements sophisticated suspect link detection:

**Suspect Link Trigger Mechanism:**

1. **Field-Level Configuration**: Org admin determines which fields trigger suspect links
   - Not all field changes cause suspect links
   - Configurable per item type
   - Typically includes: `Description`, `Status`, `Priority`, `Acceptance Criteria`

2. **Upstream Change Detection**:
   - When upstream item changes a "suspect trigger field"
   - Relationship status becomes "Suspect"
   - Visual indicator turns red in List View and Single Item View

3. **Relationship Status Indicators**:
   - **Suspect**: One or more upstream items changed, downstream may need review
   - **Causing Suspect**: This item's change has caused suspect relationships in downstream items
   - **Valid**: Relationship is current and valid

4. **Manual Suspect Link Clearing**:
   - Analyst reviews suspect link
   - Determines if upstream change impacts this item
   - Manually clears suspect status if no impact found
   - Link remains valid after manual clearing

**Suspect Detection Algorithm (Inferred):**
```
On field change in Item A (where field is in suspect_trigger_list):
  For each relationship R where A is upstream:
    For each downstream item B in R:
      Set B.relationship_status = "Suspect"
      Notify B's owner: "Upstream item changed, review required"
```

### Coverage and Impact Analysis

#### Live Traceability Concept

Jama's **Live Traceability™** is the key competitive differentiator:

- **Definition**: Real-time visibility of complete upstream and downstream information for any requirement across tools/teams
- **Update**: Instantaneous reflection of changes across entire traceability graph
- **Scope**: Spans requirement specifications through testing, changes, defects, and back

#### Coverage Calculation Algorithm

Coverage is computed as a ratio of active relationships to expected relationships:

**Formula (Inferred):**
```
Coverage % = (Relationships Present / Expected Relationships) × 100
```

**Example Calculation:**
- Traceability model specifies each High-Level Requirement (HLR) should have:
  - 2 downstream derived requirements
  - 4 test cases for those derived requirements
  - Expected relationships per HLR = 6 (2 + 4)

- Current state:
  - HLR-001: 2 derived + 3 tests = 5 actual (83% coverage)
  - HLR-002: 2 derived + 4 tests = 6 actual (100% coverage)
  - HLR-003: 1 derived + 2 tests = 3 actual (50% coverage)
  - HLR-004: 2 derived + 4 tests = 6 actual (100% coverage)

- Overall coverage: (5+6+3+6) / (6+6+6+6) = 20/24 = 83.3%

#### Live Trace Explorer Feature

The Live Trace Explorer provides:

1. **Dynamic V-Model Representation**: Visual mapping of requirements through design, implementation, test
2. **Real-Time Metric Updates**: Coverage, completion, risk indicators updated as data changes
3. **Gap Identification**: Automatically highlights relationships that should exist but don't
4. **Suspect Link Visualization**: Shows which links need review due to upstream changes
5. **Interactive Traceability**: Click-through from requirements to related items with one-hop depth control

#### Impact Analysis Execution

**On Item Impact Analysis:**
1. Select item in question
2. System retrieves all relationships (both upstream and downstream)
3. Displays upstream dependencies (what affects this item)
4. Displays downstream impacts (what this item affects)
5. Can filter by item type, status, or other criteria

**On Change Request Impact Analysis:**
1. User creates Change Request item
2. Links change request to affected requirement(s)
3. System traverses complete traceability graph
4. Identifies all downstream items that might be impacted
5. Generates impact report with item counts by type

**Impact Analysis Scope:**
- Typically limited to 1-2 hops by default
- Can be expanded for deeper analysis
- Transitive impact (e.g., Requirement→Design→Code→Test) can be computed
- Impact set can be exported or marked for action

### Baseline and Configuration Management

#### Configuration Snapshots

Jama Connect supports project snapshots (sometimes called "Views" or "Baselines"):

**Characteristics:**
- Point-in-time capture of all items and relationships
- All item versions frozen at snapshot date
- Link relationships as they existed at snapshot time
- Immutable after creation

**Use Cases:**
- Formal reviews and approvals
- Release management (capturing what was built/tested)
- Regulatory compliance documentation
- Comparison with current state for change tracking

#### Comparison and Delta Analysis

Users can:
1. Select baseline snapshot
2. Select current state or different baseline
3. View differences in:
   - Item count changes
   - Relationship changes (added/removed links)
   - Field value changes
   - Status transitions
4. Export delta reports for documentation

### Compliance and Formal Requirements

#### Compliance-Focused Item Types

Organizations typically configure item types specifically for compliance:

**Regulatory Requirement Type:**
- `Requirement ID` - Unique identifier
- `Requirement Text` - Full specification
- `Standard Reference` - Which standard specifies this (ISO 26262 § X.Y.Z)
- `Rationale` - Why this requirement matters
- `Verification Method` - How it will be verified
- `Acceptance Criteria` - Acceptance conditions
- `Allocated To` - Design/component it allocates to

**Test Case Type (for compliance verification):**
- `Test Case ID` - Unique identifier
- `Objective` - What this test validates
- `Prerequisites` - Environment/conditions needed
- `Test Steps` - Detailed procedure
- `Expected Results` - What should happen
- `Traceability` - Link to requirements being tested
- `Verification Evidence` - Attachment field for results

**Test Results Type:**
- `Test Case Reference` - Which test was run
- `Execution Date` - When test executed
- `Result` - Pass/Fail/Inconclusive
- `Test Data` - What data was used
- `Evidence` - Attachment field for proof
- `Defects Found` - Links to any defects discovered

#### Standards Compliance Support

Jama Connect can be configured for:
- **ISO 26262** (Functional Safety / Automotive)
- **DO-178C** (Aerospace software)
- **IEC 62304** (Medical device software)
- **FDA 21 CFR Part 11** (Pharmaceutical/medical)
- **SPICE** (Process capability)
- **CMMI** (Capability Maturity Model)

Configuration involves:
1. Creating item types for each artifact type in the standard
2. Defining relationships between item types
3. Adding custom fields for standard-specific metadata
4. Configuring verification method enumerations to match standard
5. Setting up report templates for evidence compilation

---

## Polarion ALM

### Platform Overview

Polarion ALM is a Siemens PLM Software platform providing integrated requirements management, quality assurance, and application lifecycle management. It emphasizes functional safety compliance, complete traceability, and integrated verification/validation workflows.

**Key Architectural Characteristics:**
- Browser-based with modern web UI
- Tight integration with version control (SVN/Git)
- Work Item-centric data model
- Document-based specification authoring (LiveDocs)
- Comprehensive QA and testing capabilities

### Work Item and Requirement Structure

#### Core Work Item Definition

In Polarion, requirements are represented as **Work Items** - the fundamental unit of traceability. Work Items are instances of configurable **Work Item Types**.

**Mandatory Fields:**
- `Type` - Work Item type (Requirement, Test Case, Defect, Risk, etc.)
- `Title` - Brief identifier
- `Project` - Project container

**System Fields (always present):**
- `ID` - Unique identifier (auto-generated or user-specified)
- `Created` - Creation timestamp with creator
- `Modified` - Last modification timestamp
- `Status` - Current workflow state
- `Owner` - Assigned person
- `Priority` - Priority level

#### Work Item Type Configuration

Administrators configure Work Item Types in `work-item-types.xml`. Each type specifies:

1. **Type ID** - Unique identifier (e.g., "requirement", "test_case")
2. **Display Name** - Human-readable name
3. **Fields** - Set of available fields for items of this type
4. **Workflows** - Allowed status transitions
5. **Custom Fields** - Additional data fields specific to this type

**Common Work Item Types:**
1. **Requirement** - Specification of what system should do
2. **Test Case** - Procedure for verifying requirement
3. **Test Run** - Execution of test case
4. **Defect** - Reported problem or issue
5. **Risk** - Identified risk to project
6. **Task** - Work to be completed
7. **Story** - Agile user story or feature
8. **Specification Item** - Item within a LiveDoc specification

#### Custom Field Configuration

Custom fields are configured in separate XML files:

**File Structure:**
- Global custom fields: `custom-fields.xml` (applies to all work item types)
- Type-specific fields: `{type-id}-custom-fields.xml` (e.g., `requirement-custom-fields.xml`)

**Custom Field Types Supported:**

1. **Text** - Single-line text
   - Configurable maximum length
   - Optional regex validation

2. **TextArea** - Multi-line text
   - Supports rich text HTML
   - Can embed formatted content

3. **Number** - Integer or decimal
   - Optional min/max bounds
   - Precision specification for decimals

4. **DateTime** - Calendar date with time
   - Timezone-aware
   - Optional time zone specification

5. **Boolean** - True/False checkbox

6. **Enum (Enumeration)** - Single selection from predefined list
   - References enumeration defined elsewhere
   - Pick list values from enumeration

7. **MultiEnum** - Multiple selections from predefined list
   - Each value tracked independently
   - Can be used for multi-valued properties

8. **User** - Reference to system user
   - Single or multi-valued
   - Supports group references

9. **WorkItem** - Reference to another work item
   - Typically used for inline relationships
   - Creates implicit link between items

10. **URL** - Hyperlink field

11. **Attachment** - File attachment
    - Can store multiple files per field
    - Version tracking per attachment

#### Field Definition Example (Requirement Type)

```xml
<!-- requirement-custom-fields.xml -->
<customFields>
  <!-- Functional Safety Fields -->
  <customField id="safety_class" type="Enum">
    <enumID>SIL_Classification</enumID>
    <label>Safety Integrity Level</label>
  </customField>

  <customField id="hazard_ref" type="TextArea">
    <label>Hazard Reference</label>
  </customField>

  <!-- Verification Fields -->
  <customField id="verification_method" type="Enum">
    <enumID>VerificationMethods</enumID>
    <label>Verification Method</label>
  </customField>

  <customField id="test_reference" type="WorkItem">
    <label>Test Case Reference</label>
  </customField>

  <!-- Traceability Fields -->
  <customField id="source_document" type="TextArea">
    <label>Source Document Reference</label>
  </customField>

  <customField id="rationale" type="TextArea">
    <label>Requirement Rationale</label>
  </customField>
</customFields>
```

### Link Model and Bidirectional Traceability

#### Work Item Link Roles

Polarion implements traceability through **Link Roles** that define relationships between work items.

**Link Role Definition:**
- **Name**: Human-readable name of the link (e.g., "depends on")
- **Opposite**: Reverse relationship name (e.g., "is depended on by")
- **Type Restrictions**: Rules controlling which work item types can be linked

**Type Restriction Rules:**
Each link role defines one or more rules specifying:
- **From Types**: Work item type(s) that can initiate the link
- **To Types**: Work item type(s) that can be the target

**Example Link Role Configuration:**
```
Link Role: "verifies"
Opposite: "is verified by"
Rules:
  Rule 1: From[TestCase] → To[Requirement]
  Rule 2: From[TestRun] → To[Requirement]
```

#### Bidirectional Relationship Navigation

Polarion supports two types of links for each relationship:

1. **Direct Link**: Created explicitly by user from source item
   - User creates link from work item A to work item B
   - Uses specified link role name
   - Stored as direct connection

2. **Derived Link** (Backlink): Viewed from opposite perspective
   - When viewing A's relationships from B's perspective
   - Shows as the "opposite" link role name
   - Derived from direct link, not separately stored

**Practical Example:**

Create from Requirement perspective:
```
TestCase-001 --[verifies]--> Requirement-001
```

View from Requirement perspective (shows derived link):
```
Requirement-001 <--[is verified by]-- TestCase-001
```

#### Standard Link Roles

Typical standard link roles configured for projects:

| Link Role | Opposite | Semantic Meaning |
|-----------|----------|-----------------|
| `parent` | `child` | Hierarchical decomposition |
| `derived_from` | `derives` | Requirement is detailed refinement |
| `depends_on` | `is_depended_on_by` | Dependency relationship |
| `verifies` | `is_verified_by` | Test verifies requirement |
| `implements` | `is_implemented_by` | Design/code implements requirement |
| `relates_to` | `relates_to` | Generic relationship |
| `mitigates` | `is_mitigated_by` | Mitigation addresses risk |
| `covers` | `is_covered_by` | Item covers requirement/risk |

### Change Impact and Suspect Link Mechanism

#### Suspect Link Attribute

Polarion implements change tracking through a **Suspect attribute** on work items and links:

**Suspect Attribute Characteristics:**
- Applies to both work items and their links
- Boolean value (suspect = true/false)
- Can be set manually or automatically
- Indicates that an item or link needs review due to changes

**Auto-Suspect Mechanism:**

When enabled (configurable per project):
1. Create new link with `auto_suspect = true` configuration
2. When linked-from item changes:
   - All links FROM that item automatically become suspect
   - All work items linked TO that item are notified
   - Notification email sent to work item owner/assignee

**Suspect Status Propagation:**
```
Change to Requirement-001:
  ├─ Link "Requirement-001 --verifies--> TestCase-002" marked suspect
  ├─ TestCase-002 owner notified: "Upstream requirement changed"
  ├─ TestCase-002 status updated to show suspect downstream links
  └─ Can cascade further if TestCase-002 has downstream links
```

#### Impact Analysis Workflow

**Manual Impact Analysis:**
1. Select work item to analyze
2. View all incoming and outgoing links
3. System displays:
   - Upstream dependencies (what affects this item)
   - Downstream impacts (what this item affects)
4. Can expand to n-hops depth
5. Filter by link role or item type

**Automated Impact Analysis:**
1. When a work item status changes to a critical state
2. System can automatically mark all linked items as suspect
3. Workflow rules can trigger additional actions
4. Audit trail records all impact propagations

#### Impact Analysis Widget

Polarion provides a **Graphical and Tabular Impact Analysis Widget** extension that:

1. **Graphical Display**: Shows parents and children in hierarchical graph
2. **Tabular Display**: Lists impacted items in table format
3. **Scope Control**: Can limit to direct links or expand to multiple hops
4. **Filtering**: By link role, item type, status, or other criteria
5. **Export**: Can export impact analysis results

### Baseline Management and Versioning

#### Collection-Based Baselining

Polarion uses **Collections** for configuration management and baselining:

**Collection Characteristics:**
- **Immutable Snapshot**: Captures stable state at point in time
- **Scope**: Can contain multiple documents or work items
- **Content Mix**: Can include both "head" (current) and baselined (versioned) items
- **Hierarchical Support**: Collections can reference other collections

**Baseline Creation Process:**
1. Define what items/documents to include
2. Create baseline collection
3. Assign version/baseline identifier
4. Collection becomes immutable
5. Can be used as baseline for comparisons or traceability

**Hierarchical Collections:**
Collections can be organized hierarchically:
- Parent collection references child collections
- Child baselines can be reused in different parent contexts
- Efficient for managing complex product hierarchies

#### Version Control Integration

Every artifact is stored in version control repositories (SVN, Git):

**Version History Record:**
- Creation timestamp and user
- Modification timestamp and user
- Complete content history
- Ability to checkout any previous version
- Diff/comparison capabilities

**Audit Trail Capabilities:**
- Full modification history for every artifact
- User identity for every change
- Timestamp for every modification
- Change rationale (via workflow state transitions)
- Electronic signature support for approved changes

#### Configuration Comparison

Users can compare:
1. Current state vs. baseline
2. Baseline vs. previous baseline
3. Different branches or variants
4. Generate delta reports showing:
   - Items added/deleted
   - Items modified
   - Link relationship changes
   - Field value changes

### Formal Requirements and Compliance

#### Formal Requirement Attributes

Standard fields for requirement work items typically include:

| Field | Type | Purpose |
|-------|------|---------|
| `Title` | Text | Brief requirement identifier |
| `Description` | TextArea (Rich) | Complete requirement specification |
| `Priority` | Enum | Requirement priority |
| `Status` | Enum | Lifecycle state (Draft, Review, Approved) |
| `Owner` | User | Responsible party |
| `Rationale` | TextArea | Why requirement exists |
| `Source` | Enum | Requirement source |
| `Verification Method` | Enum | Test, Review, Analysis, Inspection |
| `Acceptance Criteria` | TextArea | Satisfaction conditions |

#### Custom Fields for Standards Compliance

Polarion provides templates for major compliance standards with pre-configured fields:

**ISO 26262 Template Fields (Functional Safety):**
- `Hazard ID` - Link to identified hazard
- `Safety Goal` - Associated safety goal
- `ASIL` (Automotive Safety Integrity Level) - A/B/C/D classification
- `Hardware Safety Requirement` - Boolean flag
- `Software Safety Requirement` - Boolean flag
- `Functional Safety Concept Ref` - Link to FSC
- `Implementation` - Link to implementing design
- `Verification Evidence` - Attachment field
- `V&V Method` - Enumeration of verification/validation approach

**DO-178C Template Fields (Aerospace):**
- `DAL` (Design Assurance Level) - A through E
- `Traceability Justification` - Rationale for criticality
- `Verification Method` - Enumeration
- `Test Coverage` - Percentage or statement
- `Compliance Evidence` - Attachment reference

**IEC 62304 Template Fields (Medical Device):**
- `Software Safety Classification` - Class A/B/C
- `Risk Control Linked To` - Link to risk control
- `Verification Activity` - Type of verification
- `Validation Activity` - Type of validation
- `Evidence Repository` - Link to evidence location

#### Specification Documents (LiveDocs)

Polarion supports **LiveDocs** - integrated specification documents with bidirectional traceability:

**LiveDocs Characteristics:**
- Rich document editing (Word-like interface)
- Embedded work items inline in document
- Document structure maps to work item hierarchy
- Changes to work items reflected in document
- Document-to-document traceability
- Export to PDF/Word with traceability intact

**Formal Specification Structure in LiveDocs:**
```
System Requirements Specification (Document)
├─ Chapter 1: Functional Requirements
│  ├─ Section 1.1: User Authentication
│  │  └─ Requirement 1.1.1: "System shall authenticate users..."
│  │     └─ Embedded TestCase-001 reference
│  └─ Section 1.2: Data Security
│     └─ Requirement 1.2.1: "System shall encrypt data..."
└─ Chapter 2: Non-Functional Requirements
```

### Compliance Evidence and Verification Traceability

#### Verification and Validation Integration

Polarion QA (testing module) integrates tightly with Requirements:

**V&V Traceability Chain:**
1. Requirement specifies what to verify
2. Test case created to verify requirement
3. Test execution (Test Run) records actual verification
4. Results linked back to requirement
5. Complete chain captured for compliance audits

**Evidence Storage:**
- Test results stored as work items with attachments
- Test output logs attached to test run items
- Screenshot/evidence files linked to test results
- Links maintain traceability from requirement through execution

#### Compliance Report Generation

Polarion can generate compliance reports including:

1. **Traceability Matrix**: Requirements vs. Test Cases (coverage)
2. **Impact Analysis Reports**: Change impact across specifications
3. **Verification Status**: What's been verified vs. what remains
4. **Compliance Checklists**: Standard-specific compliance checks
5. **Evidence Compilation**: All verification evidence in one document

**Report Contents Typically Include:**
- Requirement identifier and specification
- Verification method
- Test case reference
- Test execution results
- Pass/fail status
- Evidence attachments
- Non-compliance gaps identified

#### Workflow and Audit Trail

Polarion workflows enforce compliance process:

**Workflow States Typical for Compliance:**
```
Draft → Review → Approved → Implemented → Tested → Released → Closed
```

**At Each Transition:**
- Validation rules checked (e.g., verification method required)
- Audit trail records transition
- Electronic signatures can be required
- Historical state change records kept indefinitely
- Cannot revert to previous state (immutable history)

---

## Comparative Analysis

### Requirement Object Structure

| Characteristic | IBM DOORS Next | Jama Connect | Polarion ALM |
|---|---|---|---|
| **Object Type** | Artifact | Item | Work Item |
| **Primary Content Field** | Primary Text (Rich) | Description (Rich) | Description + LiveDocs |
| **Attribute Data Types** | 10+ (string, int, enum, user, calculated) | 14+ (text, rich, dropdown, user, calculated) | 11+ (text, enum, user, work item link, attachment) |
| **Custom Attribute Support** | Yes, unlimited | Yes, unlimited | Yes, per-type customization |
| **Rich Text Support** | Primary Text only | Description field | LiveDocs (full document support) |
| **Metadata Tracking** | Creator, modifier, timestamps | Creator, modifier, timestamps | Creator, modifier, timestamps + version history |
| **Hierarchical Support** | Module-based | Parent-child links | Work item decomposition + documents |
| **Reuse Model** | Cross-module artifact reuse | Not native (links instead) | Collections with item references |

### Traceability Models

| Characteristic | IBM DOORS Next | Jama Connect | Polarion ALM |
|---|---|---|---|
| **Link Type System** | Project-configured link types | Standardized link types (10+) | Configurable link roles with opposites |
| **Bidirectionality** | Yes, forward and backward | Yes, upstream/downstream | Yes, direct and derived links |
| **Link Rules** | From Type → To Type restrictions | Relationship direction rules | Type restrictions per link role |
| **Coverage Calculation** | Manual via dashboards | Automated real-time via Live Trace Explorer | Manual via reports and widgets |
| **Coverage Algorithm** | Count-based or manual | Ratio-based (actual/expected) | Count-based by type |
| **Transitive Tracing** | Yes (multi-hop traversal) | Yes (configurable depth) | Yes (configurable depth) |
| **Impact Analysis** | Link traversal + filtering | Change request + graph traversal | Graphical/tabular widget + suspect links |
| **Real-Time Updates** | No (batch/on-demand) | Yes (Live Traceability) | Yes (when suspect triggered) |

### Change Impact Analysis

| Characteristic | IBM DOORS Next | Jama Connect | Polarion ALM |
|---|---|---|---|
| **Change Detection** | Manual selection of item | Automatic via change requests | Automatic via suspect attribute |
| **Impact Scope** | Configurable link traversal | Trace matrix traversal | Link graph + suspect propagation |
| **Blast Radius** | Computed by link depth | Computed by relationship direction | Computed by link traversal + suspect chain |
| **Suspect Links** | Gap detection (missing links) | Explicit suspect status on items | Auto-suspect on linked items when upstream changes |
| **Notification** | Manual review required | Automated to relationship owner | Automated to work item owner |
| **Propagation Scope** | Direct links typically | 1-2 hops configured | Configurable depth + auto-cascade |
| **Audit Trail** | Complete for all items | Complete for all items | Complete for all items + workflows |

### Baseline and Configuration Management

| Characteristic | IBM DOORS Next | Jama Connect | Polarion ALM |
|---|---|---|---|
| **Baseline Type** | Module-level baselines | Project snapshots/views | Collections (immutable snapshots) |
| **Immutability** | Yes, after creation | Yes, after creation | Yes, Collection is immutable |
| **Version Control** | Artifact versioning via links | Item versioning native | Full SVN/Git integration |
| **Comparison Capability** | Baseline vs. current | Snapshot comparison | Delta analysis, diff support |
| **Reuse Model** | Artifact reuse across modules | Item references | Collection hierarchies |
| **Audit Trail** | Modification history | Modification history | Full version control history |
| **Branching Support** | Limited (workspace-based) | Limited (project-based) | Native with SVN/Git branches |

### Formal Attributes and Compliance

| Characteristic | IBM DOORS Next | Jama Connect | Polarion ALM |
|---|---|---|---|
| **Standard Formal Attributes** | Source, Priority, Status, Owner | Description, Priority, Verification Method | Title, Description, Verification Method |
| **Formal Requirement Templates** | ISO 26262 kit available | Configurable item types | ISO 26262, DO-178C templates provided |
| **Rationale Field** | Custom attribute | Rich text field | Standard description field |
| **Verification Method** | Custom enumeration | Dropdown field | Configurable enumeration |
| **Acceptance Criteria** | Custom attribute | Rich text field | In description or custom field |
| **Source Tracking** | Source attribute | Dropdown or custom field | Custom field |
| **Compliance Support** | ISO 26262, IEC 61508 focus | ISO 26262, DO-178C, FDA, CMMI | ISO 26262, DO-178C, IEC 62304 templates |
| **Evidence Storage** | Link to test items | Attachment fields in test items | Test run items with attachments |
| **Audit Trail** | Per-artifact | Per-item | Per-item + version control |

### Custom Attribute Types

| Data Type | IBM DOORS Next | Jama Connect | Polarion ALM |
|---|---|---|---|
| String/Text | Yes | Yes (single-line) | Yes |
| Multi-line Text | Rich Text only | Rich Text | TextArea with HTML |
| Integer | Yes | Yes | Yes |
| Float | Yes | Yes (Percentage) | Yes |
| Boolean | Yes | No (Dropdown instead) | Yes |
| Date | Yes | Yes | Yes |
| DateTime | Yes (Calendar+Time) | DateTime | Yes |
| Enumeration | Yes (single) | Dropdown (single) | Enum (single or multi) |
| Multi-Select | Not native | Yes (Multi-Select) | MultiEnum |
| User Reference | Yes | Yes | Yes |
| Item Reference | Via links | Limited (calculated) | Yes (WorkItem type) |
| Calculated | Yes (DXL scripts) | Yes (Math operations, WSJF) | Not native (use workflow functions) |
| Attachment | Via modules/artifacts | Yes | Yes |
| URL | Not native | Not native | Yes |
| Rich HTML | Primary Text only | Description field | TextArea + LiveDocs |

### Suspect Link Mechanisms

| Aspect | IBM DOORS Next | Jama Connect | Polarion ALM |
|---|---|---|---|
| **Suspect Trigger** | Gap detection (implicit) | Field change detection | Work item change (configurable) |
| **Configuration** | Link rules, coverage analysis | Per-field in item type config | Auto-suspect flag on link role |
| **Detection Mechanism** | Traceability matrix gaps | Field change in upstream item | Status change or property modification |
| **Notification** | Manual review of gaps | Automatic to relationship owner | Automatic to work item owner |
| **Visual Indicator** | Gap in coverage report | Red status indicator | Suspect attribute flag |
| **Manual Clearing** | N/A (recalculate coverage) | Explicit clearing action | Manual flag reset |
| **Propagation** | Count-based coverage | Upstream to downstream | Linked item chain + configurable depth |

---

## Key Findings and Patterns

### Pattern 1: Artifact-Centric vs. Relationship-Centric Design

**IBM DOORS Next: Artifact-Centric**
- Artifacts are primary objects with rich attributes
- Links are secondary (added to artifacts)
- Emphasis on artifact content and metadata
- Module hierarchy contains artifacts

**Jama Connect & Polarion ALM: Relationship-Centric**
- Items/Work Items are primary objects
- Relationships are first-class entities with configuration
- Emphasis on traceability graph
- Coverage computed from relationship map

### Pattern 2: Change Detection Philosophies

**IBM DOORS Next: Manual + Gap-Based**
- User manually selects item for impact analysis
- System identifies gaps (missing downstream artifacts)
- Gap identification drives process discipline

**Jama Connect: Field-Change-Triggered**
- Specific field changes trigger suspect link flag
- Configuration determines which fields are "significant"
- Suspects propagate downstream automatically
- User reviews suspect links and clears when no impact

**Polarion ALM: Workflow-State-Based**
- Status/state changes trigger suspect propagation
- Work item owner notified when upstream changes
- Optional auto-suspect configuration
- Explicit suspect attribute tracks state

### Pattern 3: Coverage Calculation Methods

**IBM DOORS Next: Implicit Coverage**
- Coverage identified through reporting/dashboards
- Gap analysis (items that should have links but don't)
- No formal coverage calculation model

**Jama Connect: Explicit Coverage Ratio**
- Coverage = Actual Links / Expected Links (%)
- Expected links defined by traceability rules
- Real-time calculation in Live Trace Explorer
- Can drill down to identify specific gaps

**Polarion ALM: Count-Based Coverage**
- Coverage by item type count
- Example: "4 test cases for 5 requirements = 80% coverage"
- Supports multiple coverage metrics simultaneously

### Pattern 4: Immutability Guarantees

All three platforms guarantee immutability of baselines/snapshots:
- **IBM DOORS Next**: Baseline modules cannot be modified post-creation
- **Jama Connect**: Snapshot views are read-only
- **Polarion ALM**: Collections are immutable, require new version for changes

However, implications differ:
- **IBM DOORS**: Can link to baselined artifacts (links can change)
- **Jama Connect**: Snapshot is completely frozen point-in-time
- **Polarion**: Collection references are fixed, but items themselves may have newer versions

### Pattern 5: Compliance Evidence Chains

**Common Pattern Across All Three:**
```
Regulatory Requirement
  ↓ [verifies/implements]
Design Specification
  ↓ [verified by]
Test Case
  ↓ [produces]
Test Result with Evidence
  ↓ [attached]
Compliance Report
```

**Differences in Evidence Organization:**
- **IBM DOORS**: Evidence typically external (attached to test artifacts)
- **Jama Connect**: Evidence in attachment fields of test result items
- **Polarion**: Evidence in test run work items with version control integration

### Pattern 6: Custom Attribute Typing Philosophy

**IBM DOORS Next: Permissive**
- 10+ base data types plus calculated fields
- Can create DXL scripts for complex calculations
- Rich text limited to primary text field
- Most structured fields constrained by type

**Jama Connect: Comprehensive**
- 14+ field types including mathematical operations
- Calculated fields support WSJF algorithm
- All field types support rich text where applicable
- More flexible field combinations

**Polarion ALM: Configuration-Based**
- Type-specific field definitions via XML
- All custom fields treated equally (text, enum, user, etc.)
- Can reference complex data types (work items, enumerations)
- Attachment fields for evidence storage

---

## Implementation Recommendations

### For Tracertm Platform

Based on this research, consider these design patterns for your requirement management system:

#### 1. Requirement Object Structure

**Recommended Core Fields:**
```typescript
interface Requirement {
  id: string;
  type: 'requirement' | 'design' | 'test_case' | 'risk';
  title: string;
  description: RichText;

  // Formal Attributes
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'draft' | 'review' | 'approved' | 'implemented' | 'tested';
  source: string; // Who specified this
  owner: UserId;
  rationale: RichText;
  verificationMethod: 'test' | 'review' | 'analysis' | 'inspection';
  acceptanceCriteria: RichText;

  // Metadata
  createdAt: Date;
  createdBy: UserId;
  modifiedAt: Date;
  modifiedBy: UserId;

  // Custom Attributes (extensible)
  customAttributes: Map<string, any>;

  // Traceability
  links: Link[];
  suspectLinks?: Link[]; // For items needing review
}
```

#### 2. Traceability Model

**Recommended Link Types to Support:**
- `derived_from` / `derives` (decomposition)
- `verified_by` / `verifies` (verification)
- `implements` / `is_implemented_by` (design→code)
- `mitigates` / `is_mitigated_by` (risk mitigation)
- `depends_on` / `is_depended_on_by` (dependency)
- `related_to` (generic relationship)

**Link Structure:**
```typescript
interface Link {
  id: string;
  fromId: string;
  toId: string;
  role: LinkRole;
  reverseRole: string; // Opposite direction
  createdAt: Date;
  suspect?: boolean; // True if upstream item changed
  suspectReason?: string; // Why it's suspect
}
```

#### 3. Change Impact Analysis

**Implement Hybrid Approach:**
1. **Automatic Suspect Detection** (Jama/Polarion style)
   - Configure which fields trigger suspect links
   - Auto-flag downstream items when upstream changes
   - Notify owners of suspect links

2. **Impact Depth Configuration** (all platforms)
   - Allow 1-3 hop impact analysis
   - Filter by item type
   - Configurable scope per organization

3. **Coverage Calculation** (Jama style)
   - Expose expected vs. actual relationships ratio
   - Real-time calculation on demand
   - Gap identification for missing relationships

#### 4. Baseline Management

**Recommended Approach (Polarion-inspired):**
```typescript
interface Baseline {
  id: string;
  name: string;
  createdAt: Date;
  createdBy: UserId;
  immutable: true; // Cannot be modified after creation

  // Snapshot of all contained items at baseline time
  itemSnapshots: Map<string, ItemSnapshot>;
  linkSnapshots: Map<string, LinkSnapshot>;

  // Enables comparison
  comparison?: {
    comparedTo: string; // Another baseline ID
    itemsAdded: string[];
    itemsRemoved: string[];
    itemsModified: Array<{itemId: string; changes: Change[]}>;
    linksAdded: string[];
    linksRemoved: string[];
  }
}
```

#### 5. Formal Attributes for Compliance

**Support Multiple Compliance Templates:**

**ISO 26262 Attributes:**
```typescript
interface ISO26262Fields {
  asil: 'A' | 'B' | 'C' | 'D';
  hazardReference: string;
  safetyGoal: string;
  isFunctionalSafetyRequirement: boolean;
}
```

**DO-178C Attributes:**
```typescript
interface DO178CFields {
  dal: 'A' | 'B' | 'C' | 'D' | 'E';
  tracibilityJustification: RichText;
  testCoverage: string;
}
```

**IEC 62304 Attributes:**
```typescript
interface IEC62304Fields {
  softwareSafetyClass: 'A' | 'B' | 'C';
  verificationActivity: string;
  validationActivity: string;
}
```

#### 6. Custom Attribute System

**Recommended Data Types:**
```typescript
type CustomAttributeType =
  | 'string'
  | 'text'
  | 'richtext'
  | 'number'
  | 'date'
  | 'datetime'
  | 'boolean'
  | 'enumeration'
  | 'multi_select'
  | 'user_reference'
  | 'item_reference'
  | 'attachment'
  | 'url'
  | 'calculated'; // For formula-based fields

interface CustomAttribute {
  id: string;
  name: string;
  type: CustomAttributeType;
  required: boolean;
  defaultValue?: any;

  // Type-specific configuration
  enumValues?: string[]; // For enumeration
  formula?: string; // For calculated
  maxLength?: number; // For string
  minValue?: number; // For number
  maxValue?: number; // For number
}
```

#### 7. Suspect Link Implementation

**Recommended Mechanism:**
```typescript
interface SuspectLinkDetection {
  // Configuration per item type
  suspectTriggerFields: string[]; // Which fields trigger suspect

  // When these fields change on an upstream item:
  // 1. Find all outgoing links from that item
  // 2. Mark links as suspect
  // 3. Notify downstream item owners
  // 4. Record reason for suspect (which field changed)

  onFieldChange(itemId: string, fieldName: string, oldValue: any, newValue: any) {
    if (suspectTriggerFields.includes(fieldName)) {
      // Get all outgoing links from this item
      const outgoingLinks = getLinksFrom(itemId);

      // Mark each as suspect
      outgoingLinks.forEach(link => {
        markLinkSuspect(link.id, `Field '${fieldName}' changed`);
        notifyOwner(link.toId, `Upstream requirement changed, review required`);
      });
    }
  }
}
```

#### 8. Impact Analysis Algorithm

**Recommended Breadth-First Approach:**
```
function getImpactAnalysis(itemId: string, depth: number = 2):
  1. Initialize queue with [itemId] at depth 0
  2. Initialize result set with itemId
  3. While queue not empty:
     a. Pop item from queue
     b. If current depth < max depth:
        - Get all outgoing links (forward traceability)
        - Get all incoming links (backward traceability)
        - Add linked items to queue at depth + 1
        - Add to result set
  4. Return result set with depth information
  5. Filter by item type if requested
  6. Generate impact report (count by type, total affected)
```

#### 9. Coverage Calculation Algorithm

**Recommended Real-Time Approach:**
```
function calculateCoverage():
  1. For each requirement:
     a. Count expected downstream items by type
        - Expected tests = requirement.expectedTestCount
        - Expected design items = requirement.expectedDesignCount
     b. Count actual linked items by type
        - Actual tests = requirement.links.filter(l => l.role == 'verified_by' && type == 'test_case').length
        - Actual design = requirement.links.filter(l => l.role == 'implements' && type == 'design').length
     c. Calculate coverage = actual / expected

  2. Aggregate:
     - Overall coverage = sum(actual) / sum(expected)
     - By item type coverage = sum(actual_type) / sum(expected_type)
     - Gap report = items with 0 expected != 0 actual

  3. Identify gaps:
     - Items with 0% coverage
     - Items with suspect links
     - Items needing review
```

### Performance Considerations

1. **Link Traversal**: Cache impact analysis results, invalidate on link changes
2. **Coverage Calculation**: Batch calculation with incremental updates
3. **Suspect Detection**: Event-driven, not batch-based
4. **Baseline Snapshots**: Store deltas, not full copies (like Git)

### Migration Path from Enterprise Platforms

If migrating from DOORS Next/Jama/Polarion:

1. **Export Artifacts/Items/Work Items** in ReqIF or CSV format
2. **Map Attribute Types** to Tracertm custom attribute system
3. **Preserve Link Structure** with role mapping
4. **Maintain Metadata** (created, modified, author, timestamps)
5. **Create Baseline** of imported state as v0
6. **Map Compliance Templates** to custom attribute sets

---

## Sources and References

### IBM DOORS Next Generation

- [IBM Engineering Requirements Management DOORS Next - Attribute Data Types](https://www.ibm.com/docs/en/engineering-lifecycle-management-suite/doors-next/7.1.0?topic=properties-creating-attribute-data-types)
- [Creating requirement attribute data types in IBM DOORS Next Generation](https://jazz.multichoice.co.za/clmhelp/topic/com.ibm.rational.rrm.help.doc/topics/t_create_data_type.html)
- [Rational DOORS Kit for ISO 26262 and IEC 61508](https://www.ibm.com/support/pages/rational-doors-kit-iso-26262-and-iec-61508)
- [IBM Rational DOORS Requirements Management Tool Tutorial](https://www.softwaretestinghelp.com/ibm-rational-doors-ng-tutorial/)
- [A Complete Guide: Requirements Management with DOORS Next](https://mgtechsoft.com/blog/requirements-management-with-doors-next-a-complete-guide/)

### Jama Connect

- [Requirements Traceability Matrix - Jama Software](https://www.jamasoftware.com/requirements-management-guide/requirements-traceability/how-to-create-and-use-a-requirements-traceability-matrix/)
- [Coverage and Traceability - Jama Connect Help](https://help.jamasoftware.com/ah/en/manage-content/coverage-and-traceability.html)
- [Live Traceability vs. After-the-Fact Traceability](https://www.jamasoftware.com/requirements-management-guide/requirements-traceability/live-traceability-vs-after-the-fact-traceability/)
- [Live Trace Explorer in Jama Connect](https://www.jamasoftware.com/blog/jama-connect-features-in-five-live-trace-explorer/)
- [Clear Suspect Links - Jama Connect Help](https://help.jamasoftware.com/en/manage-content/coverage-and-traceability/relationships/clear-suspect-links.html)
- [Suspect Tracking in Requirements Management](https://www.jamasoftware.com/blog/the-importance-of-suspect-tracking-in-requirements-management/)
- [Jama Requirements: Satisfy Traceability With Automated Testing](https://www.parasoft.com/blog/satisfy-traceability-from-jama-requirements-to-tests-code/)

### Polarion ALM

- [Work Item Link Roles - Polarion Documentation](https://docs.plm.automation.siemens.com/content/polarion/20/help/en_US/user_and_administration_help/user_guide/polarion_for_project_managers/planning_to_start_a_project/work_item_link_roles.html)
- [Configure Work Item Linking](https://docs.plm.automation.siemens.com/content/polarion/20/help/en_US/user_and_administration_help/administrators_guide/configure_work_items/configure_work_item_linking.html)
- [Functional Safety in ISO 26262 - Polarion](https://polarion.plm.automation.siemens.com/products/automotive/functional-safety-iso-26262-automotive-spice-cmmi)
- [ISO 26262 Template - Hazard Analysis and Risk Assessment](https://extensions.polarion.com/extensions/355-iso26262-template-hazard-analysis-and-risk-assessment-safety-requirements-and-quality-assurance)
- [Polarion Collections and Baselines](https://docs.plm.automation.siemens.com/content/polarion/20/help/en_US/user_and_administration_help/user_guide/work_with_documents/document_baselines.html)
- [Graphical and Tabular Impact Analysis Widget](https://extensions.polarion.com/extensions/354-graphical-and-tabular-impact-analysis-widget)
- [Why Establishing Traceability Between Regulatory Requirements Matters](https://blogs.sw.siemens.com/polarion/why-establishing-traceability-between-regulatory-requirements-and-your-product-specification-matters/)

### Industry Standards and Compliance

- [ISO 26262 Compliant Usage of IBM DOORS](http://ftpmirror.your.org/pub/misc/ftp.software.ibm.com/common/ssi/ecm/ra/en/ral14048usen/RAL14048USEN.PDF)
- [The Role of Standards in Safety-Critical QA](https://www.mndwrk.com/blog/the-role-of-standards-in-safety-critical-qa-navigating-iso-26262-do-178c-and-iec-62304)
- [Polarion QA Benefits Guide](https://polarion.plm.automation.siemens.com/hubfs/Docs/Guides_and_Manuals/polarion_qa_benefit_guide.pdf)

---

## Conclusion

The three enterprise ALM platforms share fundamental architectural patterns while implementing distinct approaches to change detection and impact analysis:

- **IBM DOORS Next**: Artifact-rich with emphasis on manual gap analysis and hierarchical organization
- **Jama Connect**: Relationship-centric with real-time coverage calculation and field-change-triggered suspect links
- **Polarion ALM**: Work-item-centric with workflow-driven state changes and configuration-first approach to compliance

All three support formal requirements, compliance templates, bidirectional traceability, immutable baselines, and comprehensive audit trails. The choice between them depends on organizational emphasis: DOORS for deep artifact customization, Jama for real-time traceability visibility, or Polarion for integrated workflow and QA capabilities.

For Tracertm, a hybrid approach combining Jama's real-time coverage calculation, Polarion's suspect-link mechanism, and DOORS' flexible attribute typing would create a powerful platform for complex traceability requirements.

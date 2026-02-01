# Enterprise ALM Technical Implementation Patterns

## Deep Technical Reference for Requirement Management Systems

---

## Part 1: Requirement Object Structures in Detail

### IBM DOORS Next - Complete Artifact Model

**Artifact Type Definition (in XML/configuration):**
```xml
<artifactType id="requirement">
  <label>Requirement</label>
  <icon>requirement.svg</icon>
  <attributes>
    <!-- Standard (non-custom) attributes -->
    <attribute id="name" type="string" required="true">
      <label>Requirement Name</label>
      <maxLength>255</maxLength>
    </attribute>
    <attribute id="primary_text" type="richtext" required="true">
      <label>Requirement Text</label>
      <supportedFormatting>
        <bullets>true</bullets>
        <numbering>true</numbering>
        <bold>true</bold>
        <italic>true</italic>
        <underline>true</underline>
        <hyperlinks>true</hyperlinks>
        <images>true</images>
      </supportedFormatting>
    </attribute>
  </attributes>
</artifactType>
```

**Custom Attribute Definition (for ISO 26262):**
```xml
<attributeDataType id="asil_level">
  <label>ASIL Level</label>
  <type>Enumeration</type>
  <enumeratedValues>
    <value id="0" label="Not Applicable">ASIL_QM</value>
    <value id="1" label="ASIL A">ASIL_A</value>
    <value id="2" label="ASIL B">ASIL_B</value>
    <value id="3" label="ASIL C">ASIL_C</value>
    <value id="4" label="ASIL D">ASIL_D</value>
  </enumeratedValues>
</attributeDataType>
```

**Artifact Storage Structure (internal):**
```
Artifact {
  id: "REQ-001"
  type: "requirement"
  moduleId: "SYS_REQ_001"
  name: "User Authentication"
  primaryText: "System shall authenticate <b>all</b> users..."

  // Metadata
  created: {
    timestamp: 2026-01-15T10:30:00Z
    user: "alice@example.com"
  }
  modified: {
    timestamp: 2026-01-28T14:22:15Z
    user: "bob@example.com"
  }

  // Attributes
  attributes: {
    priority: "high"
    status: "approved"
    source: "Customer Requirements Document"
    owner: "alice@example.com"
    asil_level: "ASIL_B"
    verification_method: "test"
  }

  // Links
  links: [
    {
      id: "LINK-001"
      targetId: "DESIGN-042"
      type: "Refines"
      createdAt: 2026-01-16T09:00:00Z
    },
    {
      id: "LINK-002"
      targetId: "TEST-187"
      type: "VerifiedBy"
      createdAt: 2026-01-17T11:15:00Z
    }
  ]
}
```

**Module Hierarchy Example:**
```
Module: SYS_REQ [id=001]
├─ Artifact: REQ-001 [Name: "User Authentication"]
│  └─ Attributes: {priority: high, status: approved, asil_level: ASIL_B}
│
├─ Artifact: REQ-002 [Name: "Data Encryption"]
│  └─ Attributes: {priority: critical, status: approved, asil_level: ASIL_D}
│
└─ Module: SYS_REQ_DERIVED [id=002] (nested)
   ├─ Artifact: REQ-D-001 (reuse of REQ-001)
   ├─ Artifact: REQ-D-002 [Name: "User Login Form"]
   └─ Artifact: REQ-D-003 [Name: "Password Reset"]

METADATA: {
  artifacts: [001, 002, D-001, D-002, D-003]
  order: [001, 002, D-002, D-003, D-001]
  modules: [SYS_REQ, SYS_REQ_DERIVED]
}
```

---

### Jama Connect - Item Type Configuration

**Item Type Definition (programmatic):**
```python
# Item type configuration in Jama API
requirement_item_type = {
    "itemTypeId": 1,
    "name": "Requirement",
    "displayName": "Requirement",
    "description": "Top-level system requirement",
    "icon": "requirement.svg",

    "fields": [
        # Standard fields
        {
            "id": "name",
            "type": "Text",
            "label": "Requirement Name",
            "required": True,
            "maxLength": 255
        },
        {
            "id": "description",
            "type": "RichText",
            "label": "Requirement Text",
            "required": True,
            "maxLength": None
        },

        # Formal requirement fields
        {
            "id": "priority",
            "type": "Dropdown",
            "label": "Priority",
            "required": False,
            "values": ["Critical", "High", "Medium", "Low", "Deferred"]
        },
        {
            "id": "status",
            "type": "Dropdown",
            "label": "Status",
            "required": True,
            "values": ["Draft", "Review", "Approved", "Implemented", "Tested"]
        },
        {
            "id": "owner",
            "type": "User",
            "label": "Owner",
            "required": False,
            "multiSelect": False
        },
        {
            "id": "source",
            "type": "Dropdown",
            "label": "Source",
            "required": False,
            "values": ["Customer", "Regulatory", "Internal", "Derived"]
        },

        # Rich text fields for compliance
        {
            "id": "rationale",
            "type": "RichText",
            "label": "Rationale",
            "required": False,
            "placeholder": "Why this requirement exists"
        },
        {
            "id": "acceptance_criteria",
            "type": "RichText",
            "label": "Acceptance Criteria",
            "required": False,
            "placeholder": "How we know this is satisfied"
        },

        # Verification
        {
            "id": "verification_method",
            "type": "Dropdown",
            "label": "Verification Method",
            "required": False,
            "values": ["Test", "Review", "Analysis", "Inspection", "Demonstration"]
        },

        # Calculated field
        {
            "id": "coverage_status",
            "type": "Calculated",
            "label": "Coverage Status",
            "formula": "IF(test_coverage >= 80%, 'Good', 'At Risk')"
        }
    ],

    # Default values
    "defaultFieldValues": {
        "status": "Draft",
        "priority": "Medium"
    }
}
```

**Item Instance Storage (JSON):**
```json
{
  "id": 12847,
  "itemType": 1,
  "project": 45,
  "name": "User Authentication System",
  "description": "System shall provide user authentication with <strong>multi-factor support</strong>",

  "fieldValues": {
    "priority": "Critical",
    "status": "Approved",
    "owner": {
      "id": 234,
      "name": "Alice Johnson",
      "email": "alice@example.com"
    },
    "source": "Customer",
    "rationale": "Secure access is critical to prevent unauthorized system use",
    "acceptance_criteria": "All login attempts logged; MFA required for admin users",
    "verification_method": "Test"
  },

  "relationships": [
    {
      "id": 5432,
      "type": "verified_by",
      "targetItemId": 12921,
      "targetItemName": "TC-001: Test Login with MFA",
      "suspect": false
    }
  ],

  "metadata": {
    "created": {
      "timestamp": "2026-01-10T08:00:00Z",
      "user": {
        "id": 234,
        "name": "Alice Johnson"
      }
    },
    "modified": {
      "timestamp": "2026-01-28T15:45:30Z",
      "user": {
        "id": 567,
        "name": "Bob Smith"
      }
    }
  }
}
```

---

### Polarion ALM - Work Item Type and Fields

**Work Item Type Configuration (XML):**
```xml
<!-- work-item-types.xml -->
<workItemTypes>
  <workItemType id="requirement">
    <title>Requirement</title>
    <icon>requirement.png</icon>
    <category>specification</category>

    <!-- Available fields for this type -->
    <fields>
      <!-- Standard fields (always present) -->
      <field id="id" type="string">
        <label>ID</label>
        <editable>false</editable>
      </field>
      <field id="title" type="string">
        <label>Title</label>
        <required>true</required>
        <maxLength>255</maxLength>
      </field>
      <field id="description" type="textArea" rich="true">
        <label>Description</label>
        <required>false</required>
      </field>
      <field id="status" type="enum">
        <label>Status</label>
        <enumeration>requirement_status</enumeration>
      </field>
      <field id="owner" type="user">
        <label>Owner</label>
        <required>false</required>
      </field>

      <!-- Type-specific fields -->
      <field reference="requirement-custom-fields.xml" />
    </fields>

    <!-- Allowed status transitions -->
    <workflows>
      <workflow id="default">
        <transition from="draft" to="review" />
        <transition from="review" to="approved" />
        <transition from="approved" to="implemented" />
        <transition from="implemented" to="tested" />
        <transition from="tested" to="released" />
      </workflow>
    </workflows>
  </workItemType>
</workItemTypes>
```

**Custom Fields Configuration (XML):**
```xml
<!-- requirement-custom-fields.xml -->
<customFields>
  <!-- Formal requirement fields -->
  <customField id="priority" type="Enum">
    <label>Priority</label>
    <enumID>requirement_priority</enumID>
  </customField>

  <customField id="source" type="Text">
    <label>Source Document/Requirement</label>
    <maxLength>500</maxLength>
  </customField>

  <customField id="rationale" type="TextArea">
    <label>Rationale</label>
    <richText>true</richText>
  </customField>

  <customField id="acceptance_criteria" type="TextArea">
    <label>Acceptance Criteria</label>
    <richText>true</richText>
  </customField>

  <!-- ISO 26262 fields -->
  <customField id="asil" type="Enum">
    <label>ASIL</label>
    <enumID>asil_levels</enumID>
  </customField>

  <customField id="hazard_ref" type="TextArea">
    <label>Hazard Reference</label>
    <richText>true</richText>
  </customField>

  <customField id="safety_goal_link" type="WorkItem">
    <label>Safety Goal</label>
    <allowedTypes>
      <type>safety_goal</type>
    </allowedTypes>
  </customField>

  <!-- Verification fields -->
  <customField id="verification_method" type="Enum">
    <label>Verification Method</label>
    <enumID>verification_methods</enumID>
  </customField>

  <customField id="test_case_link" type="WorkItem">
    <label>Test Case</label>
    <allowedTypes>
      <type>test_case</type>
    </allowedTypes>
    <multipleLinks>true</multipleLinks>
  </customField>

  <customField id="evidence_attachment" type="Attachment">
    <label>Verification Evidence</label>
    <multipleFiles>true</multipleFiles>
  </customField>
</customFields>
```

**Work Item Instance (Internal Storage):**
```
WorkItem {
  id: "REQ-001"
  type: "requirement"
  title: "User Authentication System"
  description: "System shall provide <u>secure</u> user authentication..."

  // Standard fields
  status: "approved"
  owner: {
    id: "user_234"
    name: "Alice Johnson"
    email: "alice@example.com"
  }
  created: {
    timestamp: "2026-01-10T08:00:00Z"
    user: "user_234"
  }
  modified: {
    timestamp: "2026-01-28T15:45:30Z"
    user: "user_567"
  }

  // Custom fields
  customFields: {
    priority: "critical"
    source: "Customer_Requirements_V2.docx"
    rationale: "Prevents unauthorized system access"
    acceptance_criteria: "All users can login with password; admin users require MFA"
    asil: "ASIL_B"
    hazard_ref: "HAZ-012: Unauthorized Access"
    safety_goal_link: "SG-003"
    verification_method: "test"
    test_case_link: ["TC-001", "TC-002", "TC-045"]
    evidence_attachment: ["test_results_20260125.pdf", "mfa_test_log.txt"]
  }

  // Links
  links: {
    verifies: ["TC-001", "TC-002"],
    derived_from: ["SYS-REQ-001"],
    implements: ["DESIGN-042"]
  }

  // Version control
  revisions: [
    {
      revision: 1
      timestamp: "2026-01-10T08:00:00Z"
      content: {...}
    },
    {
      revision: 2
      timestamp: "2026-01-28T15:45:30Z"
      content: {...}
    }
  ]
}
```

---

## Part 2: Advanced Traceability Models

### Bidirectional Link Implementation

**Link Role Matrix (showing opposites):**
```
Link Role Name          | Opposite              | Meaning
─────────────────────────────────────────────────────────────
parent                  | child                 | Hierarchical parent
child                   | parent                | Hierarchical child
derived_from            | derives               | Refinement/decomposition
derives                 | derived_from          | Reverse refinement
depends_on              | is_depended_on_by     | Dependency
is_depended_on_by       | depends_on            | Reverse dependency
implements              | is_implemented_by     | Design/code realizes req
is_implemented_by       | implements            | Reverse implementation
verifies                | is_verified_by        | Test verifies requirement
is_verified_by          | verifies              | Reverse verification
mitigates               | is_mitigated_by       | Risk mitigation
is_mitigated_by         | mitigates             | Reverse mitigation
relates_to              | relates_to            | Generic bidirectional
```

**Link Creation Algorithm (ensuring bidirectionality):**
```python
def create_bidirectional_link(from_item_id, to_item_id, link_role):
    """
    Create a link with automatic bidirectional support.

    When user creates: REQ-001 --verifies--> TEST-042
    System stores:
    1. Direct link: REQ-001 --verifies--> TEST-042
    2. Derived link: TEST-042 <--is_verified_by-- REQ-001
    """

    # Store direct link
    direct_link = {
        'id': generate_uuid(),
        'from_item_id': from_item_id,
        'to_item_id': to_item_id,
        'role': link_role,
        'created': timestamp(),
        'suspect': False
    }
    store_link(direct_link)

    # System automatically supports viewing opposite direction
    # No separate storage needed - computed on demand

    # When user views from TO_ITEM perspective:
    # System computes: to_item --opposite_role--> from_item
    # by retrieving direct_link and reversing direction

    return direct_link

def get_links_from_perspective(item_id, direction='outgoing'):
    """
    Get links from a specific item's perspective.

    direction: 'outgoing' (from this item) or 'incoming' (to this item)
    """

    if direction == 'outgoing':
        # Find all links where from_item_id == item_id
        links = query_links(from_item_id=item_id)
        return links

    elif direction == 'incoming':
        # Find all links where to_item_id == item_id
        # Display using opposite role names
        links = query_links(to_item_id=item_id)
        # Reverse direction for display
        return [
            {
                'from': link.to_item_id,
                'to': link.from_item_id,
                'role': get_opposite_role(link.role)
            }
            for link in links
        ]
```

---

## Part 3: Change Impact Analysis Algorithms

### Algorithm 1: Jama Connect - Field-Change-Triggered Suspect Links

```python
class SuspectLinkManager:
    def __init__(self):
        # Configuration: which fields trigger suspect links
        self.suspect_trigger_fields = {
            'requirement': ['description', 'status', 'acceptance_criteria'],
            'test_case': ['test_steps', 'expected_results'],
            'risk': ['description', 'probability', 'impact']
        }

    def on_item_field_changed(self, item_id, item_type, field_name, old_value, new_value):
        """
        Called when an item's field changes.
        Propagates suspect links downstream if field is configured as trigger.
        """

        # Check if this field is a suspect trigger
        if field_name not in self.suspect_trigger_fields.get(item_type, []):
            return  # This field change doesn't trigger suspects

        # Get all outgoing links (downstream items)
        outgoing_links = self.get_links_from_item(item_id, direction='outgoing')

        for link in outgoing_links:
            # Mark link as suspect
            self.mark_link_suspect(
                link_id=link.id,
                reason=f"Upstream item field '{field_name}' changed from '{old_value}' to '{new_value}'"
            )

            # Notify downstream item owner
            downstream_item = self.get_item(link.to_item_id)
            self.notify_user(
                user_id=downstream_item.owner_id,
                message=f"Item {link.from_item_id} was modified. Please review linked item {link.to_item_id}",
                priority="high"
            )

            # Update relationship status indicator
            self.update_relationship_status_indicator(
                item_id=link.to_item_id,
                status='suspect',
                link_id=link.id
            )

    def clear_suspect_link(self, link_id, reviewer_id):
        """
        Analyst reviews suspect link and clears it if no impact found.
        """

        link = self.get_link(link_id)

        # Update link status
        link.suspect = False
        link.cleared_by = reviewer_id
        link.cleared_at = timestamp()
        link.cleared_reason = None  # Optional: analyst can provide reason

        self.save_link(link)

        # Update downstream item's relationship status
        self.update_relationship_status_indicator(
            item_id=link.to_item_id,
            status='valid',
            link_id=link_id
        )

        # Audit trail
        self.log_action(
            action='clear_suspect_link',
            link_id=link_id,
            user_id=reviewer_id,
            timestamp=timestamp()
        )

    def get_suspect_links_for_item(self, item_id):
        """
        Get all suspect links associated with an item.
        """

        suspect_outgoing = self.query_links(
            from_item_id=item_id,
            suspect=True
        )
        suspect_incoming = self.query_links(
            to_item_id=item_id,
            suspect=True
        )

        return {
            'causing_suspect': suspect_outgoing,  # This item's changes caused these
            'marked_suspect': suspect_incoming    # These items' changes affected this one
        }
```

### Algorithm 2: Polarion ALM - Workflow-State-Based Suspect Propagation

```python
class PolarionSuspectLinkEngine:
    def __init__(self):
        # Configuration: which state transitions trigger auto-suspect
        self.auto_suspect_transitions = {
            'requirement': {
                'from_status': '*',  # Any status
                'to_status': ['approved', 'implemented'],  # Trigger on these transitions
                'suspect_scope': 'all_dependent_links'
            }
        }

    def on_work_item_status_changed(self, item_id, item_type, old_status, new_status):
        """
        Called when work item status changes via workflow.
        May trigger auto-suspect on all linked downstream items.
        """

        # Check if this transition triggers auto-suspect
        config = self.auto_suspect_transitions.get(item_type, {})

        transition_triggers_suspect = (
            config.get('from_status') == '*' and
            new_status in config.get('to_status', [])
        )

        if not transition_triggers_suspect:
            return

        # Get work item details
        item = self.get_work_item(item_id)

        # Get all outgoing links
        outgoing_links = self.query_links(from_work_item_id=item_id)

        for link in outgoing_links:
            # Set suspect attribute on work item
            downstream_item = self.get_work_item(link.to_item_id)
            downstream_item.suspect = True
            downstream_item.suspect_reason = f"Upstream item status changed to '{new_status}'"
            downstream_item.suspect_set_at = timestamp()
            downstream_item.suspect_set_by = self.get_current_user()

            self.save_work_item(downstream_item)

            # Notify owner
            self.send_email_notification(
                to_user_id=downstream_item.owner_id,
                subject=f"Review Required: Suspect Link on {downstream_item.id}",
                body=f"Work item {item_id} status changed to '{new_status}'. "
                     f"Please review impact on {downstream_item.id}."
            )

            # Record in audit trail
            self.audit_log(
                action='auto_suspect_set',
                work_item_id=downstream_item.id,
                reason=downstream_item.suspect_reason,
                timestamp=timestamp()
            )

    def clear_suspect_flag(self, work_item_id, reviewer_id):
        """
        Analyst reviews suspect flag and clears it.
        """

        item = self.get_work_item(work_item_id)
        item.suspect = False
        item.suspect_cleared_by = reviewer_id
        item.suspect_cleared_at = timestamp()

        self.save_work_item(item)

        # Audit trail
        self.audit_log(
            action='suspect_flag_cleared',
            work_item_id=work_item_id,
            cleared_by=reviewer_id,
            timestamp=timestamp()
        )
```

### Algorithm 3: Impact Analysis with Configurable Depth

```python
class ImpactAnalysisEngine:
    def __init__(self):
        self.default_max_depth = 2
        self.max_allowed_depth = 5

    def analyze_impact(self, item_id, max_depth=None, filter_by_type=None):
        """
        Perform impact analysis on an item.
        Returns all items affected by change to this item.

        Uses breadth-first search (BFS) for level-by-level traversal.
        """

        if max_depth is None:
            max_depth = self.default_max_depth

        max_depth = min(max_depth, self.max_allowed_depth)

        # BFS approach
        impact_set = {item_id}  # Start with the changed item
        queue = [(item_id, 0)]  # (item_id, current_depth)
        impact_by_depth = {0: [item_id]}
        impact_by_type = defaultdict(list)

        while queue:
            current_item_id, current_depth = queue.pop(0)

            if current_depth >= max_depth:
                continue

            # Get all linked items (both incoming and outgoing)
            outgoing_links = self.query_links(from_item_id=current_item_id)
            incoming_links = self.query_links(to_item_id=current_item_id)

            all_links = outgoing_links + incoming_links

            for link in all_links:
                # Determine target item
                target_item_id = (
                    link.to_item_id
                    if link.from_item_id == current_item_id
                    else link.from_item_id
                )

                # Skip if already processed
                if target_item_id in impact_set:
                    continue

                # Get target item details
                target_item = self.get_item(target_item_id)

                # Apply type filter if specified
                if filter_by_type and target_item.type not in filter_by_type:
                    continue

                # Add to impact set
                impact_set.add(target_item_id)
                queue.append((target_item_id, current_depth + 1))

                # Track by depth
                if current_depth + 1 not in impact_by_depth:
                    impact_by_depth[current_depth + 1] = []
                impact_by_depth[current_depth + 1].append(target_item_id)

                # Track by type
                impact_by_type[target_item.type].append(target_item_id)

        # Generate impact report
        report = {
            'changed_item': item_id,
            'total_impacted': len(impact_set) - 1,  # Exclude the changed item
            'impact_by_depth': {
                depth: {
                    'items': items,
                    'count': len(items)
                }
                for depth, items in impact_by_depth.items() if depth > 0
            },
            'impact_by_type': {
                type_name: {
                    'items': items,
                    'count': len(items)
                }
                for type_name, items in impact_by_type.items()
            },
            'all_impacted_items': list(impact_set - {item_id}),
            'analysis_depth': max_depth
        }

        return report

    def identify_coverage_gaps(self, item_id):
        """
        Identify items that SHOULD have links but don't (gaps).
        """

        # Get expected links based on traceability rules
        expected_link_types = self.get_expected_links_for_type(
            self.get_item_type(item_id)
        )

        # Get actual links
        actual_links = self.query_links(from_item_id=item_id)
        actual_link_types = set(link.role for link in actual_links)

        # Identify gaps
        gap_types = set(expected_link_types) - actual_link_types

        gaps = [
            {
                'from_item': item_id,
                'missing_link_type': gap_type,
                'reason': f"Expected at least one link of type '{gap_type}' but found none",
                'severity': 'high'
            }
            for gap_type in gap_types
        ]

        return gaps
```

---

## Part 4: Coverage Calculation Algorithms

### Jama Connect Style - Ratio-Based Coverage

```python
class LiveTraceCoverageCalculator:
    def __init__(self):
        # Define expected relationships per item type
        self.traceability_model = {
            'high_level_requirement': {
                'expected_children': [
                    {'type': 'requirement', 'count': 2, 'role': 'derived_from'},
                ]
            },
            'requirement': {
                'expected_children': [
                    {'type': 'design_item', 'count': 1, 'role': 'implements'},
                    {'type': 'test_case', 'count': 2, 'role': 'verified_by'},
                ]
            },
            'design_item': {
                'expected_children': [
                    {'type': 'code_module', 'count': 1, 'role': 'coded_in'},
                ]
            }
        }

    def calculate_item_coverage(self, item_id):
        """
        Calculate coverage for a single item.
        Returns ratio of actual vs. expected relationships.
        """

        item = self.get_item(item_id)
        item_type = item.type

        # Get expected relationships from model
        expected = self.traceability_model.get(item_type, {})
        if not expected:
            return None  # Item type not in traceability model

        # Calculate expected count
        total_expected = sum(e['count'] for e in expected.get('expected_children', []))

        if total_expected == 0:
            return 100.0  # Item type requires no links

        # Count actual relationships
        total_actual = 0
        breakdown = {}

        for expectation in expected.get('expected_children', []):
            target_type = expectation['type']
            role = expectation['role']
            expected_count = expectation['count']

            # Count actual links matching this criteria
            actual_count = self.count_links(
                from_item_id=item_id,
                to_item_type=target_type,
                link_role=role
            )

            total_actual += actual_count

            breakdown[f"{target_type}_{role}"] = {
                'expected': expected_count,
                'actual': actual_count,
                'coverage': (actual_count / expected_count * 100) if expected_count > 0 else 0
            }

        # Calculate overall coverage
        overall_coverage = (total_actual / total_expected * 100) if total_expected > 0 else 0

        return {
            'item_id': item_id,
            'item_type': item_type,
            'overall_coverage': round(overall_coverage, 1),
            'breakdown': breakdown,
            'total_actual': total_actual,
            'total_expected': total_expected
        }

    def calculate_project_coverage(self, project_id):
        """
        Calculate coverage for entire project.
        """

        items = self.get_all_items(project_id)

        coverage_data = []
        by_type = defaultdict(lambda: {'covered': 0, 'total': 0})

        for item in items:
            item_coverage = self.calculate_item_coverage(item.id)
            if item_coverage:
                coverage_data.append(item_coverage)

                item_type = item.type
                by_type[item_type]['total'] += 1
                if item_coverage['overall_coverage'] == 100.0:
                    by_type[item_type]['covered'] += 1

        # Calculate project-wide statistics
        total_items = len(items)
        fully_covered = sum(
            1 for c in coverage_data
            if c['overall_coverage'] == 100.0
        )
        partial_coverage = sum(
            1 for c in coverage_data
            if 0 < c['overall_coverage'] < 100.0
        )
        no_coverage = sum(
            1 for c in coverage_data
            if c['overall_coverage'] == 0.0
        )

        project_coverage = (fully_covered / total_items * 100) if total_items > 0 else 0

        return {
            'project_id': project_id,
            'project_coverage': round(project_coverage, 1),
            'statistics': {
                'total_items': total_items,
                'fully_covered': fully_covered,
                'partially_covered': partial_coverage,
                'not_covered': no_coverage
            },
            'by_type': dict(by_type),
            'items': coverage_data
        }

    def identify_gaps(self, item_id):
        """
        Identify specific gaps in traceability for an item.
        """

        item_coverage = self.calculate_item_coverage(item_id)
        if not item_coverage:
            return []

        gaps = []

        for relationship_key, breakdown in item_coverage['breakdown'].items():
            if breakdown['actual'] < breakdown['expected']:
                missing_count = breakdown['expected'] - breakdown['actual']

                gaps.append({
                    'item_id': item_id,
                    'relationship_type': relationship_key,
                    'expected': breakdown['expected'],
                    'actual': breakdown['actual'],
                    'missing': missing_count,
                    'severity': 'high' if missing_count > 0 else 'info',
                    'message': f"Missing {missing_count} link(s) for {relationship_key}"
                })

        return sorted(gaps, key=lambda x: x['missing'], reverse=True)
```

---

## Part 5: Baseline and Configuration Management

### Snapshot-Based Baseline Model

```python
class BaselineManager:
    def create_baseline(self, name, description, items_to_snapshot, project_id):
        """
        Create immutable baseline snapshot.
        """

        baseline = {
            'id': generate_uuid(),
            'project_id': project_id,
            'name': name,
            'description': description,
            'created': {
                'timestamp': timestamp(),
                'user_id': self.get_current_user_id()
            },
            'immutable': True,

            # Snapshot all items at this point in time
            'item_snapshots': {},
            'link_snapshots': {},
            'metadata': {
                'total_items': 0,
                'total_links': 0,
                'coverage_metrics': {}
            }
        }

        # Capture each item
        for item_id in items_to_snapshot:
            item = self.get_item(item_id)
            baseline['item_snapshots'][item_id] = {
                'id': item.id,
                'type': item.type,
                'title': item.title,
                'description': item.description,
                'fields': item.fields.copy(),
                'metadata': {
                    'created': item.created,
                    'modified': item.modified,
                    'version': item.version
                },
                'snapshot_time': timestamp()
            }
            baseline['metadata']['total_items'] += 1

        # Capture all links between baselined items
        for item_id in items_to_snapshot:
            links = self.query_links(from_item_id=item_id)

            for link in links:
                if link.to_item_id in items_to_snapshot:
                    baseline['link_snapshots'][link.id] = {
                        'id': link.id,
                        'from': link.from_item_id,
                        'to': link.to_item_id,
                        'role': link.role,
                        'suspect': link.suspect,
                        'snapshot_time': timestamp()
                    }
                    baseline['metadata']['total_links'] += 1

        # Calculate coverage metrics at baseline time
        baseline['metadata']['coverage_metrics'] = self.calculate_coverage_at_time(
            items_to_snapshot
        )

        # Store immutable baseline
        self.store_baseline(baseline)

        return baseline

    def compare_baseline_to_current(self, baseline_id):
        """
        Compare baseline to current state.
        Identifies what has changed.
        """

        baseline = self.get_baseline(baseline_id)
        current_items = self.get_items(
            list(baseline['item_snapshots'].keys())
        )

        comparison = {
            'baseline_id': baseline_id,
            'comparison_time': timestamp(),
            'changes': {
                'items_added': [],
                'items_deleted': [],
                'items_modified': [],
                'links_added': [],
                'links_removed': [],
                'coverage_delta': None
            }
        }

        # Check item changes
        baseline_item_ids = set(baseline['item_snapshots'].keys())
        current_item_ids = set(item.id for item in current_items)

        # Added items
        comparison['changes']['items_added'] = list(
            current_item_ids - baseline_item_ids
        )

        # Deleted items
        comparison['changes']['items_deleted'] = list(
            baseline_item_ids - current_item_ids
        )

        # Modified items
        for item in current_items:
            if item.id in baseline['item_snapshots']:
                baseline_snapshot = baseline['item_snapshots'][item.id]

                if (item.title != baseline_snapshot['title'] or
                    item.description != baseline_snapshot['description'] or
                    item.fields != baseline_snapshot['fields']):

                    comparison['changes']['items_modified'].append({
                        'id': item.id,
                        'baseline_title': baseline_snapshot['title'],
                        'current_title': item.title,
                        'baseline_version': baseline_snapshot['metadata']['version'],
                        'current_version': item.version
                    })

        # Check link changes
        baseline_link_ids = set(baseline['link_snapshots'].keys())
        current_links = self.query_links_for_items(
            list(baseline_item_ids - comparison['changes']['items_deleted'])
        )
        current_link_ids = set(link.id for link in current_links)

        # Added/removed links
        comparison['changes']['links_added'] = list(
            current_link_ids - baseline_link_ids
        )
        comparison['changes']['links_removed'] = list(
            baseline_link_ids - current_link_ids
        )

        # Coverage delta
        current_coverage = self.calculate_coverage_at_time(
            list(current_item_ids)
        )
        baseline_coverage = baseline['metadata']['coverage_metrics']

        comparison['changes']['coverage_delta'] = {
            'baseline': baseline_coverage,
            'current': current_coverage,
            'delta': current_coverage - baseline_coverage
        }

        return comparison
```

---

## Part 6: Custom Attribute Type Implementations

### Enum (Enumeration) Type with Ordering

```python
class EnumerationAttributeType:
    def __init__(self, enum_id, label, values):
        self.id = enum_id
        self.label = label
        # Order matters - determines UI presentation order
        self.values = [
            {'id': 0, 'label': 'Not Applicable', 'value': 'QM'},
            {'id': 1, 'label': 'ASIL A', 'value': 'ASIL_A'},
            {'id': 2, 'label': 'ASIL B', 'value': 'ASIL_B'},
            {'id': 3, 'label': 'ASIL C', 'value': 'ASIL_C'},
            {'id': 4, 'label': 'ASIL D', 'value': 'ASIL_D'}
        ]

    def validate_value(self, value):
        """Ensure value is in enumeration."""
        valid_values = [v['value'] for v in self.values]
        if value not in valid_values:
            raise ValueError(f"Invalid value {value}. Must be one of {valid_values}")
        return value

    def get_display_label(self, value):
        """Get human-readable label for value."""
        for v in self.values:
            if v['value'] == value:
                return v['label']
        return value
```

### Calculated Field Type with Formula Support

```python
class CalculatedFieldType:
    def __init__(self, field_id, formula, dependencies):
        self.id = field_id
        self.formula = formula  # e.g., "IF(test_count >= 5, 'Good', 'Needs Work')"
        self.dependencies = dependencies  # Fields this calculation depends on

    def evaluate(self, item):
        """
        Evaluate calculated field.

        Jama example: Weighted Shortest Job First (WSJF)
        formula: "(user_value + time_criticality + risk_reduction) / job_size"

        Dependencies: [user_value, time_criticality, risk_reduction, job_size]
        """

        # Build evaluation context
        context = {}
        for dep_field in self.dependencies:
            context[dep_field] = item.fields.get(dep_field, 0)

        # Evaluate formula
        try:
            result = self._evaluate_formula(self.formula, context)
            return result
        except Exception as e:
            raise CalculationError(f"Failed to evaluate formula: {e}")

    def _evaluate_formula(self, formula, context):
        """Safe formula evaluation."""
        # In production, use a proper formula parser (e.g., simpleeval)
        import simpleeval

        # Filter context to only safe operations
        allowed_names = context.copy()
        allowed_functions = {
            'IF': lambda cond, true_val, false_val: true_val if cond else false_val,
            'SUM': sum,
            'AVG': lambda lst: sum(lst) / len(lst),
            'MAX': max,
            'MIN': min
        }

        evaluator = simpleeval.EvalWithCompoundTypes(
            names=allowed_names,
            functions=allowed_functions
        )

        return evaluator.eval(formula)
```

### User Reference Type with Multi-Select

```python
class UserReferenceAttributeType:
    def __init__(self, field_id, label, multi_select=False):
        self.id = field_id
        self.label = label
        self.multi_select = multi_select  # True allows multiple user selection

    def validate_value(self, value, system):
        """
        Validate user reference(s).

        value: string (single user) or list (multiple users)
        """

        if self.multi_select:
            if not isinstance(value, list):
                value = [value]

            validated = []
            for user_id in value:
                user = system.get_user(user_id)
                if not user:
                    raise ValueError(f"User {user_id} not found")
                validated.append(user)

            return validated
        else:
            user = system.get_user(value)
            if not user:
                raise ValueError(f"User {value} not found")
            return user
```

---

## Part 7: Verification Evidence Traceability Chain

### Evidence Storage Model

```python
class VerificationEvidence:
    """
    Complete traceability chain from requirement to verification evidence.
    """

    def __init__(self):
        self.traceability_chain = None

    def build_evidence_chain(self, requirement_id, project_id):
        """
        Build complete verification evidence chain.

        Requirement
          ├─ Specification: What system should do
          ├─ Verification Method: How we'll verify
          └─ Link to Test Cases
             ├─ Test Case 1: Procedure for verification
             │  └─ Link to Test Runs
             │     ├─ Test Run 1: Execution on 2026-01-15
             │     │  └─ Results: PASS
             │     │     ├─ Test Output Log (attachment)
             │     │     ├─ Screenshots (attachment)
             │     │     └─ Test Data (attachment)
             │     └─ Test Run 2: Execution on 2026-01-20
             │        └─ Results: PASS (after fix)
             └─ Test Case 2: Alternative verification
                └─ Link to Test Runs
                   └─ Test Run: Execution
                      └─ Results: PASS
        """

        requirement = self.get_item(requirement_id)

        evidence_chain = {
            'requirement': {
                'id': requirement.id,
                'title': requirement.title,
                'specification': requirement.description,
                'verification_method': requirement.fields.get('verification_method'),
                'acceptance_criteria': requirement.fields.get('acceptance_criteria')
            },
            'verification': {
                'test_cases': [],
                'all_results': []
            }
        }

        # Get all linked test cases
        test_case_links = self.query_links(
            from_item_id=requirement_id,
            link_role='verified_by'
        )

        for link in test_case_links:
            test_case = self.get_item(link.to_item_id)

            test_case_data = {
                'id': test_case.id,
                'title': test_case.title,
                'procedure': test_case.fields.get('test_steps'),
                'expected_results': test_case.fields.get('expected_results'),
                'test_runs': []
            }

            # Get all test runs for this test case
            test_runs = self.query_links(
                from_item_id=test_case.id,
                link_role='test_executed_by'
            )

            for test_run_link in test_runs:
                test_run = self.get_item(test_run_link.to_item_id)

                test_run_data = {
                    'id': test_run.id,
                    'execution_date': test_run.fields.get('execution_date'),
                    'result': test_run.fields.get('result'),  # PASS/FAIL
                    'test_data': test_run.fields.get('test_data'),
                    'evidence': self.get_attachments(test_run.id),  # Links to evidence files
                    'passed': test_run.fields.get('result') == 'PASS'
                }

                test_case_data['test_runs'].append(test_run_data)
                evidence_chain['verification']['all_results'].append({
                    'test_case': test_case.id,
                    'test_run': test_run.id,
                    'result': test_run_data['result'],
                    'execution_date': test_run_data['execution_date']
                })

            evidence_chain['verification']['test_cases'].append(test_case_data)

        # Determine overall verification status
        all_results = [r['result'] for r in evidence_chain['verification']['all_results']]
        evidence_chain['verification']['overall_status'] = (
            'VERIFIED' if all(r == 'PASS' for r in all_results) and len(all_results) > 0
            else 'PARTIAL' if any(r == 'PASS' for r in all_results)
            else 'NOT_VERIFIED'
        )

        return evidence_chain

    def generate_compliance_report(self, evidence_chains):
        """
        Generate compliance report from evidence chains.
        """

        report = {
            'generated': timestamp(),
            'summary': {
                'total_requirements': len(evidence_chains),
                'verified': sum(1 for e in evidence_chains if e['verification']['overall_status'] == 'VERIFIED'),
                'partial': sum(1 for e in evidence_chains if e['verification']['overall_status'] == 'PARTIAL'),
                'not_verified': sum(1 for e in evidence_chains if e['verification']['overall_status'] == 'NOT_VERIFIED')
            },
            'evidence_chains': evidence_chains
        }

        return report
```

---

## Conclusion

These technical patterns represent the core data structures, algorithms, and implementation strategies used by enterprise-grade ALM platforms. For Tracertm, implementing these patterns would enable:

1. **Flexible requirement modeling** with rich custom attributes
2. **Real-time traceability** with bidirectional links
3. **Automated change detection** via suspect link mechanisms
4. **Coverage analysis** with configurable expectations
5. **Complete compliance evidence** chains for regulated industries
6. **Immutable baselines** for formal reviews and releases

The key differentiator is choosing between:
- **Jama's approach**: Real-time coverage calculation with field-change-triggered suspects
- **Polarion's approach**: Workflow-state-based suspect propagation with deep version control
- **DOORS' approach**: Flexible attribute system with manual gap detection

Each has proven effective in different organizational contexts and project types.

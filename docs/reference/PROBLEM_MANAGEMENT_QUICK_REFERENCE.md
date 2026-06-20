# Problem Management: Quick Reference Guide

**Purpose:** Rapid implementation checklist, decision matrices, and best practices reference
**Audience:** Architects, developers, product managers planning problem management systems
**Date:** January 27, 2026

---

## 1. RCA Method Selection Matrix

Choose the right root cause analysis technique for your problem:

| Criteria | 5 Whys | Fishbone | Kepner-Tregoe | FMEA | Pareto |
|----------|--------|----------|---------------|------|--------|
| **Problem Complexity** | Simple | Moderate | Complex | Very Complex | Multiple Problems |
| **Time to Complete** | 15-30 min | 45-120 min | 2-4 hours | 4-8 hours | 30-60 min |
| **Team Size** | 2-3 people | 4-8 people | 4-6 people | 6-10 people | 3-5 people |
| **Documentation Level** | Minimal | Moderate | Extensive | Extensive | Moderate |
| **Best For** | Quick diagnosis | Systemic issues | High-stakes decisions | Engineering failures | Prioritization |
| **Cost** | Low | Low | Moderate | Moderate | Low |
| **Graphical Output** | Linear | Diagram | Matrix | Table | Chart |

**Decision Rule:**
- Linear problems → Use 5 Whys
- Multiple potential causes → Use Fishbone
- High-stakes/complex decisions → Use Kepner-Tregoe
- Engineering/design failures → Use FMEA
- Portfolio prioritization → Use Pareto

---

## 2. Problem Classification Quick Reference

### Category Taxonomy

```
SOFTWARE PROBLEMS
├─ Application Bug (Code defect)
├─ Performance Degradation (Speed/latency)
├─ Memory Leak (Resource exhaustion)
├─ Configuration Issue (Wrong settings)
├─ Integration Issue (System-to-system)
└─ Data Corruption (Data integrity)

INFRASTRUCTURE PROBLEMS
├─ Hardware Failure (Physical equipment)
├─ Network Outage (Connectivity)
├─ Disk Space (Storage capacity)
├─ Database Issue (DBMS problem)
├─ Security Breach (Unauthorized access)
└─ Load Balancing (Distribution issue)

PROCESS PROBLEMS
├─ Workflow Gap (Missing step)
├─ Documentation Error (Inaccurate info)
├─ Training Issue (Knowledge gap)
├─ Operational Procedure (Wrong process)
└─ SLA Breach (Service level miss)
```

### Impact Level Assessment Matrix

| Impact Level | User Scope | Business Scope | System Scope | MTTR Target |
|--------------|-----------|-----------------|-------------|------------|
| **Critical** | >50% of users | Core revenue function down | Multiple systems down | <1 hour |
| **High** | 25-50% of users | Major feature unavailable | Single major system affected | <4 hours |
| **Medium** | 5-25% of users | Non-critical feature degraded | Single system degraded | <24 hours |
| **Low** | <5% of users | Minor feature inconvenience | No system impact | <1 week |

---

## 3. Problem-to-Task Decomposition Guide

When a problem requires implementation work:

```
Problem: "Database connection pool exhaustion under load"
│
├─ ANALYSIS TASKS
│  ├─ Task: Document current pool configuration
│  ├─ Task: Load test current configuration
│  └─ Task: Analyze performance metrics
│
├─ DESIGN TASKS
│  ├─ Task: Design new pool sizing algorithm
│  ├─ Task: Design monitoring/alerting strategy
│  └─ Task: Design rollback procedure
│
├─ IMPLEMENTATION TASKS
│  ├─ Task: Update pool configuration code
│  ├─ Task: Implement dynamic pool sizing
│  ├─ Task: Add monitoring metrics
│  └─ Task: Implement circuit breaker logic
│
├─ TESTING TASKS
│  ├─ Task: Unit test pool management code
│  ├─ Task: Load test with 100+ concurrent users
│  ├─ Task: Chaos engineering - test failure scenarios
│  └─ Task: Verify monitoring alerts trigger correctly
│
├─ DEPLOYMENT TASKS
│  ├─ Task: Create change management ticket
│  ├─ Task: Prepare rollback procedure
│  ├─ Task: Deploy to staging
│  ├─ Task: Monitor in staging for 24 hours
│  ├─ Task: Deploy to production
│  └─ Task: Monitor in production for 48 hours
│
└─ DOCUMENTATION TASKS
   ├─ Task: Update runbook with new procedures
   ├─ Task: Update knowledge base article
   ├─ Task: Create post-mortem summary
   └─ Task: Update capacity planning guidelines
```

---

## 4. State Transition Decision Tree

**Start: Problem Created**

```
Is problem reproducible?
├─ NO → Close as "Cannot Reproduce"
│       └─ Document attempt to reproduce
│       └─ Monitor for recurrence
│
└─ YES
    │
    Assign to team
    │
    Does team have root cause?
    │
    ├─ NO → Start RCA
    │   │
    │   RCA Method Selection:
    │   ├─ Simple linear? → 5 Whys
    │   ├─ Multiple possible causes? → Fishbone
    │   └─ Complex decision required? → Kepner-Tregoe
    │   │
    │   Root cause identified?
    │   │
    │   ├─ NO → Escalate OR Defer
    │   │   └─ Update status: "Pending RCA"
    │   │
    │   └─ YES → Continue
    │
    └─ YES
        │
        Is workaround available?
        │
        ├─ YES
        │   └─ Deploy workaround
        │   └─ Set status: "Pending Workaround"
        │   └─ Schedule permanent fix
        │
        └─ NO
            │
            Can permanent fix be prioritized?
            │
            ├─ YES
            │   └─ Create change request
            │   └─ Set status: "Awaiting Fix"
            │   └─ Track through change management
            │
            └─ NO
                └─ Defer problem
                └─ Set status: "Known Error" (documented)
                └─ Schedule review for later
                │
                Resolution complete?
                │
                ├─ YES → Verify fix
                │       └─ Create knowledge article
                │       └─ Set status: "Closed"
                │
                └─ NO → Repeat cycle
```

---

## 5. Data Field Checklist by Implementation Phase

### Phase 1: MVP (Months 1-2)
Essential fields only:
```
✓ id
✓ problem_number
✓ title
✓ description
✓ status (Open/In Progress/Closed)
✓ priority (Critical/High/Medium/Low)
✓ assigned_to
✓ created_date
✓ created_by
✓ updated_date
✓ updated_by
```

### Phase 2: Enhanced (Months 2-3)
Add classification and basic RCA:
```
+ category
+ sub_category
+ impact_level
+ urgency
+ rca_performed
+ rca_method
+ root_cause_identified
+ root_cause_description
+ assigned_team
+ tags
+ custom_fields
```

### Phase 3: Advanced (Months 3-4)
Add solution tracking:
```
+ workaround_available
+ workaround_description
+ permanent_fix_available
+ permanent_fix_description
+ known_error_id
+ knowledge_article_id
+ related_incident_ids
+ related_problem_ids
+ status_history (array)
+ review_notes
```

### Phase 4: Mature (Months 4-6)
Add analytics and optimization:
```
+ affected_systems
+ affected_users_estimated
+ business_impact_description
+ rca_method_used
+ root_cause_category
+ root_cause_confidence
+ rcaCompletedDate
+ rcaCompletedBy
+ targetResolutionDate
+ closedDate
+ closedBy
+ reviewedDate
+ reviewedBy
+ customFields (flexible)
```

---

## 6. Integration Checklist

### Must-Have Integrations

```
[ ] Incident Management System
    ├─ Problem created from incidents
    ├─ Incidents linked to problems
    ├─ When problem solved, incidents auto-resolved
    └─ Historical incident data used for RCA

[ ] Change Management System
    ├─ Permanent fixes tracked as changes
    ├─ Change approval required before implementation
    ├─ Change status synchronized with problem status
    └─ Rollback plans documented

[ ] Knowledge Base / KEDB
    ├─ Known errors documented in KB
    ├─ Workarounds indexed and searchable
    ├─ Service Desk can find known error solutions
    └─ KB articles linked to problems

[ ] Ticketing / Service Desk System
    ├─ Problems visible to support team
    ├─ Known error workarounds available in ticket views
    ├─ Support can search for problem solutions
    └─ Support can apply known workarounds
```

### Nice-to-Have Integrations

```
[ ] Asset Management (CMDB)
    └─ Track which systems/services affected

[ ] Monitoring & Alerting
    └─ Trigger problem creation from alert patterns

[ ] Communication Platform (Slack/Teams)
    └─ Notify teams of critical problems

[ ] Project Management
    └─ Create tasks/epics from problems

[ ] Analytics Platform
    └─ Historical trend analysis
```

---

## 7. UI Component Checklist

### Problem List View
```
[ ] Problem ID column (sortable, clickable)
[ ] Title column (searchable)
[ ] Status badge (color-coded)
[ ] Priority indicator (visual emphasis)
[ ] Assigned to (filter-enabled)
[ ] Created date (sortable)
[ ] Days open (sortable)
[ ] Root cause identified (yes/no indicator)

Filters:
[ ] Status filter
[ ] Priority filter
[ ] Team filter
[ ] Date range filter
[ ] My problems toggle
[ ] RCA status filter

Saved Views:
[ ] Critical Open Problems
[ ] Awaiting My Action
[ ] Known Errors
[ ] Recently Closed
```

### Problem Detail View
```
[ ] Problem header (ID, title, status badge)
[ ] Quick info bar (owner, team, created date)
[ ] Description panel (expandable)
[ ] Classification section (category, priority, impact)
[ ] RCA section (method, findings, confidence)
[ ] Solution section (workaround/permanent fix)
[ ] Related items section (incidents, problems, changes)
[ ] Assignment panel (right sidebar)
[ ] Timeline/activity panel (activity log)
[ ] Comments section (threaded discussion)
[ ] Action buttons (Change status, Assign, Close, etc.)
```

### Dashboard
```
[ ] Critical problems count (with trend)
[ ] Open problems by priority (bar chart)
[ ] Average time to resolution (metric)
[ ] RCA completion rate (percentage)
[ ] Known errors in system (count)
[ ] Problem trend chart (30-day line chart)
[ ] Most problematic systems (ranked list)
[ ] Recent problem closures (timeline)
[ ] SLA compliance (percentage)
[ ] RCA method usage (pie chart)
```

---

## 8. SLA & KPI Targets

### Response Time SLAs

```
Priority Level | Initial Response | RCA Completion | Resolution Target
---------------|-----------------|-----------------|------------------
Critical       | 15 minutes      | 2 hours        | 4 hours
High           | 1 hour          | 8 hours        | 24 hours
Medium         | 4 hours         | 24 hours       | 72 hours
Low            | 24 hours        | 5 business days| 2 weeks
```

### Key Performance Indicators

```
Metric                        | Target        | Measurement
------------------------------|---------------|-----------------
Mean Time to Resolution (MTTR)| < 24 hours    | From detection to closure
Time to RCA Completion        | < 8 hours     | From assignment to root cause found
Known Error Database Coverage | > 85%         | % of closed problems with KB articles
Prevention Success Rate       | > 40%         | % of incidents prevented by known errors
RCA Completion Rate           | > 95%         | % of problems with documented RCA
Re-open Rate                  | < 5%          | % of closed problems that re-open
First-Time Fix Rate           | > 70%         | % solved without escalation
```

---

## 9. Role & Responsibility Matrix (RACI)

| Activity | Problem Manager | Engineer | Team Lead | Change Manager | Knowledge Manager |
|----------|---|---|---|---|---|
| **Create Problem** | R | I | I | - | - |
| **Assign Problem** | R/A | I | C | - | - |
| **Perform RCA** | R | R | C | - | - |
| **Identify Root Cause** | R | R | C | - | - |
| **Document Solution** | A | R | - | - | R |
| **Create Workaround** | R | R | C | - | - |
| **Create Change Ticket** | R | - | - | R | - |
| **Approve Change** | A | - | C | R | - |
| **Implement Fix** | I | R | - | A | - |
| **Verify Solution** | A | R | C | - | - |
| **Create KB Article** | - | - | - | - | R |
| **Close Problem** | R | - | A | - | - |
| **Review Problem** | R | I | A | - | - |

**Legend:** R = Responsible | A = Accountable | C = Consulted | I = Informed | - = Not involved

---

## 10. Common Pitfalls & Solutions

### Pitfall 1: Confusing Categories with Root Causes
**Problem:** Classifying "Software Bug" as a root cause instead of a cause category
**Solution:**
- Category: "Software Bug" (organizational label)
- Root Cause: "Array index out of bounds in line 437 of UserService.java" (actual cause)
- Store separately in data model

### Pitfall 2: Incomplete RCA Documentation
**Problem:** RCA performed but findings not documented, institutional knowledge lost
**Solution:**
- Enforce validation: Cannot close problem without RCA details
- Link RCA method to problem record
- Create knowledge article before closure
- Train teams on RCA documentation standards

### Pitfall 3: Known Errors Not Accessible to Support
**Problem:** RCA completed but Service Desk unaware of solution, incidents not resolved efficiently
**Solution:**
- Integrate KEDB with ticketing system
- Notify Service Desk when known error created
- Make workarounds searchable by symptom/error message
- Create alerts when similar incidents arrive

### Pitfall 4: Problems Created But Never Closed
**Problem:** Growing list of "zombie" problems, dashboard becomes unreliable
**Solution:**
- Set auto-closure for 60+ days without activity
- Require review before closure
- Archive old problems after 1 year
- Create metrics to identify stalled problems

### Pitfall 5: No Distinction Between Problem Resolution Types
**Problem:** Can't distinguish "fixed" from "working around" vs "cannot reproduce"
**Solution:**
- Use resolution_type field
- Different closure workflows for different types
- Only create knowledge articles for "Permanent Fix"
- Set different escalation rules by resolution type

### Pitfall 6: RCA Method Not Matched to Problem
**Problem:** Using 5 Whys for systemic issues, wasting time on oversimplified analysis
**Solution:**
- Provide RCA method guidance based on problem type
- Educate teams on method selection
- Store RCA method in problem record for audit
- Review method effectiveness in retrospectives

---

## 11. Implementation Timeline

### Week 1-2: Planning & Design
```
[ ] Finalize problem entity schema
[ ] Design database schema
[ ] Plan API endpoints
[ ] Create mockups for key UIs
[ ] Define validation rules
```

### Week 3-4: Core Implementation
```
[ ] Implement problem entity & CRUD APIs
[ ] Build problem list view UI
[ ] Build problem detail view UI
[ ] Implement status state machine
[ ] Add role-based access control
```

### Week 5-6: Integration & Testing
```
[ ] Integrate with incident system
[ ] Build problem creation from incident
[ ] Add automated tests
[ ] Performance testing
[ ] User acceptance testing
```

### Week 7-8: Dashboard & Reporting
```
[ ] Build problem dashboard
[ ] Create KPI queries
[ ] Add filtering & saved views
[ ] Create admin reports
[ ] User training
```

### Week 9-10: RCA & Advanced Features
```
[ ] Implement RCA method tools (5 Whys, Fishbone)
[ ] Add RCA workflow
[ ] Integrate with knowledge base
[ ] Implement KEDB functionality
[ ] Add escalation automation
```

### Week 11-12: Launch & Optimization
```
[ ] Production deployment
[ ] Monitoring & alerting setup
[ ] User support & documentation
[ ] Performance optimization
[ ] Gather feedback & iterate
```

---

## 12. Success Metrics (90-Day Post-Launch)

```
Operational Metrics:
├─ Adoption Rate: >70% of teams using system
├─ Data Quality: >95% of critical fields populated
├─ Average Time to Assign: <30 minutes
└─ Average Time to First Update: <4 hours

Quality Metrics:
├─ RCA Completion: >80% of problems
├─ Root Cause Identified: >75% of investigations
├─ Knowledge Coverage: >60% of closed problems documented
└─ RCA Quality Score: >7/10 (average)

Business Impact:
├─ MTTR Reduction: >20% improvement
├─ Incident Prevention: >30% reduction in similar incidents
├─ Known Errors: >50 documented and accessible
└─ Service Desk Self-Service: >40% incidents resolved via KEDB
```

---

## 13. Quick Decision Trees

### Should This Be a Problem or Just a Task?

```
Has it already caused a service impact?
├─ YES → CREATE PROBLEM
│       └─ Track separately from tasks
│       └─ Assign RCA
│
└─ NO
    │
    Is it reported by a customer/user?
    │
    ├─ YES → CREATE PROBLEM
    │       └─ Link to incident
    │       └─ Assess prevention opportunity
    │
    └─ NO
        │
        Is it a known pattern?
        │
        ├─ YES → CREATE PROBLEM
        │       └─ Proactive analysis
        │       └─ Trend-based problem
        │
        └─ NO
            │
            → CREATE TASK (not a problem yet)
               └─ Link to feature/epic
               └─ Track for delivery
               └─ Monitor for incident patterns
```

### When Should RCA Be Completed?

```
Problem Priority?
├─ CRITICAL
│   └─ RCA must complete: < 2 hours
│   └─ Status: In Investigation immediately
│
├─ HIGH
│   └─ RCA must complete: < 8 hours
│   └─ Escalate if delayed > 4 hours
│
├─ MEDIUM
│   └─ RCA must complete: < 24 hours
│   └─ Can defer if workaround available
│
└─ LOW
    └─ RCA must complete: < 5 days
    └─ Can defer if minimal business impact
```

---

## 14. Recommended Tools & Technologies

### Open Source Options
- **Issue Tracking**: OpenProject, Taiga, Wekan
- **Knowledge Base**: MediaWiki, BookStack, DokuWiki
- **Process Mapping**: Draw.io, Excalidraw
- **Analytics**: Metabase, Apache Superset

### Commercial Options
- **Enterprise ITSM**: ServiceNow, Atlassian Jira Service Management, BMC Helix
- **Project Management**: Asana, Monday.com, Jira
- **Knowledge Base**: Confluence, Notion, Document360
- **Advanced Analytics**: Tableau, Power BI

### Key Capabilities Checklist
```
[ ] Problem entity modeling & persistence
[ ] Status workflow enforcement
[ ] User role-based access control
[ ] Audit trail & change history
[ ] Bulk operations (import/export)
[ ] API access (webhooks, REST)
[ ] Custom fields & metadata
[ ] Integration capabilities
[ ] Reporting & dashboard
[ ] Search functionality
[ ] Mobile access (optional)
```

---

**Document Version:** 1.0
**Last Updated:** January 27, 2026
**Status:** Quick Reference Complete

For detailed information, see:
- `PROBLEM_MANAGEMENT_RESEARCH.md` - Comprehensive research findings
- `PROBLEM_ENTITY_PATTERNS.md` - Implementation code examples

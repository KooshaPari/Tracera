# Blocker Escalation Protocol

**Effective:** Immediately
**Version:** 1.0
**Last Updated:** December 2024

---

## Overview

When an agent encounters a blocker, follow this tier system. Response time and resolution owner change based on tier and severity.

**Core Principle:** Resolve blockers quickly or escalate immediately. No blocker sits unattended.

---

## Tier System

### Tier 1: Agent Self-Resolution (0-2 hours)

**Owner:** Agent
**SLA Response Time:** Immediate (same hour)
**SLA Resolution Time:** 2 hours maximum
**Decision Maker:** Agent (self)

**What happens:**
1. Agent documents blocker in standup with:
   - Clear title
   - Category (from list below)
   - Specific details (error message, steps to reproduce)
2. Agent investigates independently for up to 2 hours:
   - Search existing documentation
   - Try obvious workarounds
   - Review similar past issues
   - Check for local environment issues
3. Document what was attempted (important for escalation)
4. If resolved within 2 hours: Close blocker, document solution
5. If unresolved after 2 hours: Escalate immediately to Tier 2

**Escalation Criteria (move to Tier 2 if any apply):**
- Can't find root cause within 1 hour of investigation
- Root cause found but fix requires > 30 minutes
- Blocker affects multiple agents' work
- Blocker is critical (blocks standup report)
- Workaround exists but is unsustainable

**Example - RESOLVED at Tier 1:**
```
BLOCKER: pytest import failing in new test file
- Category: Environment
- Reported: 10:15 AM
- Investigation (30 min):
  - Checked __init__.py exists ✓
  - Verified Python path includes tests/ ✓
  - Added sys.path adjustment to conftest.py
- Result: RESOLVED
- Solution: Import path now correct
- Time: 30 minutes
```

**Example - ESCALATED to Tier 2:**
```
BLOCKER: Database fixture timeout after 5 concurrent tests
- Category: Database
- Reported: 10:15 AM
- Investigation (90 min):
  - Tried increasing timeout: still fails
  - Tried reducing worker count: slower but works
  - Root cause unclear
- Result: ESCALATED
- Reason: Can't identify root cause after 90 min
- Time: 90 minutes (ready for Tier 2)
```

---

### Tier 2: Tech Lead Pair Programming (2-4 hours)

**Owner:** Tech Lead
**SLA Response Time:** 15 minutes (CRITICAL - must acknowledge blocker within 15 min)
**SLA Resolution Time:** 4 hours maximum
**Decision Maker:** Tech Lead + Agent

**What happens:**
1. Agent escalates:
   - Post in #blockers Slack channel with: `ESCALATE: [blocker title]`
   - Mention @tech-lead
   - Include: category, reported time, what was tried
2. Tech Lead responds within 15 minutes:
   - Acknowledges receipt: "Got it, pairing in X minutes"
   - Clears schedule if possible
   - Blocks next 30-60 minutes for collaboration
3. Pair programming session (30 minutes typical):
   - Agent and Tech Lead work together
   - Use screen share if remote
   - Trace through code/systems together
   - Document findings as you go
4. Decision point (30-min mark):
   - **Option A:** Problem identified and solution is clear → implement fix (30-60 min)
   - **Option B:** Problem identified but requires architectural change → escalate to Tier 3
   - **Option C:** Problem still unclear → escalate to Tier 3
5. If resolved: Document solution for future reference

**Escalation Criteria (move to Tier 3 if any apply):**
- Design issue (architecture needs change)
- Database schema problem
- Missing external dependency/API
- Build or infrastructure issue
- Issue affects code review or release process
- Fix would take > 2 hours

**Example - RESOLVED at Tier 2:**
```
BLOCKER: Database fixture timeout after 5 concurrent tests
- Reported: 10:15 AM
- Escalated: 11:15 AM

Tier 2 Pairing Session (11:30 AM - 12:15 PM):
- Tech Lead joins pairing
- Trace fixture lifecycle
- Find: Fixture not cleaning up between tests
- Root cause: Connection pool exhausted after 5 tests
- Solution: Add explicit cleanup in teardown hook
- Implementation: 20 minutes
- Verification: All tests pass at full parallelization

Result: RESOLVED
Duration: 1 hour (Tier 1: 60 min, Tier 2: 60 min)
```

**Example - ESCALATED to Tier 3:**
```
BLOCKER: API schema mismatch between frontend and backend
- Reported: 10:15 AM
- Escalated: 11:15 AM

Tier 2 Investigation (11:30 AM - 12:00 PM):
- Tech Lead identifies schema difference
- Frontend expects 'user_id' field
- Backend provides 'userId' field
- Root cause: No schema governance

Result: ESCALATED
Reason: Requires architectural decision on naming conventions
- Need: API schema spec document
- Need: Codebase-wide naming audit
- Need: Architect approval for changes
```

---

### Tier 3: Architect Review (4-8 hours)

**Owner:** Architect (or Tech Lead if architecture decision is straightforward)
**SLA Response Time:** 30 minutes
**SLA Resolution Time:** 8 hours maximum
**Decision Maker:** Architect + Tech Lead + Product Lead

**What happens:**
1. Tech Lead escalates:
   - Create GitHub issue with label `escalation:tier-3`
   - Include: what was tried, why Tier 2 couldn't solve it
   - Tag @architect @product-lead
   - Link to any related issues
2. Architect responds within 30 minutes:
   - Reviews issue and any attached code/logs
   - Schedules sync if major decision needed
   - May request more context/data
3. Design/Review session (could be async):
   - Architect evaluates options:
     - Option A: Refactor/redesign
     - Option B: Workaround + tech debt doc
     - Option C: Descope this work
   - Documents decision in Architecture Decision Record (ADR)
4. Implementation (if refactor):
   - Tech Lead or Agent implements based on ADR
   - Code review by Architect
5. Verification and closure

**Escalation Criteria (move to Tier 4 if any apply):**
- Requires external team collaboration
- Requires significant resource reallocation
- Would slip project timeline
- Requires customer/stakeholder decision

**Example - RESOLVED at Tier 3:**
```
BLOCKER: API schema mismatch between frontend and backend
- Reported: 10:15 AM
- Tier 2 (11:30 AM - 12:00 PM): Identified root cause
- Escalated to Tier 3: 12:00 PM

Architect Review (12:30 PM - 2:00 PM):
- Decision: Adopt camelCase for all API responses
- Create ADR: "API Field Naming Convention"
- Requires: Backend field rename (1 hour)
- Requires: Frontend update (30 min)
- Requires: Test updates (30 min)

Implementation (2:00 PM - 3:30 PM):
- Tech Lead implements schema changes
- Tests updated and passing
- Regression: None

Result: RESOLVED via Tier 3
Total Duration: 5 hours 15 minutes
- Tier 1: N/A
- Tier 2: 30 min
- Tier 3: 315 min (investigation + design + implementation)
```

---

### Tier 4: Priority Shift Decision (1-2 hours)

**Owner:** Product Lead
**SLA Response Time:** 1 hour
**SLA Decision Time:** 1 hour
**Decision Maker:** Product Lead + Project Stakeholders

**When it reaches Tier 4:**
- Blocker cannot be resolved within Tier 3 SLA
- Blocker would impact project timeline
- Blocker requires resources not available

**Product Lead options:**
1. **Increase Resources:** Pull another agent to help
2. **Accept Schedule Slip:** Extend deadline for this phase
3. **Descope Work:** Remove this WP from MVP
4. **Workaround Acceptance:** Accept suboptimal solution with tech debt ticket

**Example escalation to Tier 4:**
```
BLOCKER: External API integration not responding
- Root cause: API vendor has outage
- Can't fix without vendor (Tier 3 decision)
- Blocks UI feature demo

Product Lead Decision:
- Option: Descope API integration from Week 1
- Plan: Use mock API data for demo
- Tech Debt: Track as "Implement live API integration" for Week 3
- Timeline Impact: 0 (demo proceeds with mock data)
```

---

## Blocker Categories & Quick Routing

| Category | Who | Root Cause | Quick Workaround | Default Tier |
|----------|-----|-----------|------------------|--------------|
| **Database** | Tech Lead | Schema? Fixture? Timeout? | Use in-memory SQLite | T2 |
| **Environment** | DevOps | Local setup? CI config? | Docker container | T2 |
| **Design Unclear** | Architect | Ambiguous requirements? | Mock-first test | T1→T2 |
| **Missing Dependency** | Tech Lead | Not installed? Wrong version? | Install/update, test | T1→T2 |
| **Flaky Test** | QA/Test Lead | Timing? Async race? | Add retry/timeout | T2 |
| **API Integration** | Integration Lead | Endpoint? Auth? Format? | Use mock server | T2 |
| **Performance** | Architect | Query slow? Memory? | Add caching | T2→T3 |
| **Build Failure** | DevOps | Missing tool? Config? | Manual build | T1→T2 |
| **Import/Path** | Tech Lead | __init__.py? sys.path? | Adjust conftest.py | T1 |
| **Test Data** | Test Lead | Fixtures? Seeds? | Create adhoc data | T1→T2 |

---

## Blocker Tracking Template

Use this exact format when reporting blockers in DAILY_STANDUP_LOG.md:

```markdown
BLOCKER: [Short, specific title - max 10 words]
- Category: [Pick from table above]
- Reported: [HH:MM], [YYYY-MM-DD]
- Tier: [1 | 2 | 3 | 4] (starts at 1, escalate if needed)
- Owner: [Your name]
- Impact: [What's blocked - WP? Test? Feature? Release?]
- Workaround: [If available, how to keep working]
- ETA: [Expected resolution time or date]
- Status: [ACTIVE | ESCALATED | RESOLVED | DESCOPED]
```

### Detailed Example

```markdown
BLOCKER: Database connection pool exhausted on 5+ parallel tests
- Category: Database
- Reported: 10:15 AM, 2024-12-06
- Tier: 1 (escalate if not resolved by 12:15 PM)
- Owner: Agent 1
- Impact: Blocking test development for storage module (WP-1.3)
- Workaround: Run tests serially with -n1 flag (slower but works)
- ETA: 12:30 PM (investigating fixture cleanup)
- Status: ACTIVE

Update at 11:30 AM:
- Escalated to Tier 2 (Tier 1 investigation inconclusive)

Update at 12:15 PM:
- Resolved: Added cleanup hook in conftest.py
- Solution: Explicit connection.close() in fixture teardown
- Tests now pass at full parallelization
- Status: RESOLVED
- Duration: 2 hours
```

---

## SLA Compliance Dashboard

Track these metrics daily:

| Tier | Metric | Target | Alert if | Escalate if |
|------|--------|--------|----------|-------------|
| **Tier 1** | Time to resolve | 2 hours | > 1.5 hours | > 2 hours |
| **Tier 2** | Response time | 15 min | > 15 min | Auto-escalate |
| **Tier 2** | Resolve time | 4 hours | > 3 hours | > 4 hours |
| **Tier 3** | Response time | 30 min | > 30 min | Auto-escalate |
| **Tier 3** | Resolve time | 8 hours | > 6 hours | > 8 hours |
| **ALL** | Active blockers | < 2 | = 2 | >= 2 → escalate one |
| **ALL** | Blockers > 1 day old | 0 | = 1 | Auto-escalate to T3 |

---

## Red Flags - Immediate Action Required

If you see ANY of these, immediately escalate:

1. **Coverage DOWN** from previous day
   - Action: Tier 2 immediately - find regression
   - Reason: Could indicate major problem

2. **Critical Tests FAILING** (previously passing)
   - Action: Tier 2 immediately
   - Reason: Indicates a broken system

3. **2+ Blockers Active**
   - Action: Escalate ONE blocker to Tier 3
   - Reason: Multiple blockers suggest systemic issue

4. **Blocker age exceeds SLA**
   - Action: Auto-escalate one tier immediately
   - Reason: SLA violation = problem not being solved

5. **Blocker affecting multiple agents**
   - Action: Tier 2 immediately
   - Reason: Multiplies impact across team

6. **"I'm stuck" without specific blocker**
   - Action: Tier 2 immediately - need help scoping
   - Reason: Vague blockers hide real problems

---

## Escalation Workflow Diagram

```
BLOCKER DETECTED (Agent realizes issue)
     ↓
[Agent investigates - Tier 1, max 2 hours]
     ↓
     ├→ RESOLVED?
     │   └→ Document solution, close blocker, continue work
     │
     └→ UNRESOLVED after 2 hours?
         ↓
    [Escalate to Tier 2]
         ↓
    [Tech Lead responds within 15 min, pairs with agent, 30-60 min]
         ↓
         ├→ RESOLVED?
         │   └→ Document solution, close blocker
         │
         └→ UNRESOLVED after 4 hours?
             ↓
        [Escalate to Tier 3]
             ↓
        [Architect reviews, designs solution, 30 min-4 hours]
             ↓
             ├→ RESOLVED?
             │   └→ Document ADR, implement, close blocker
             │
             └→ UNRESOLVED after 8 hours?
                 ↓
            [Escalate to Tier 4]
                 ↓
            [Product Lead decides: more resources? descope? slip date?]
                 ↓
            [DECISION MADE - Execute new plan]
```

---

## Real-World Example: Database Fixture Timeout

### Timeline & Decisions

**9:00 AM - Blocker Detected**
```
BLOCKER: Database fixture timeout after 5 concurrent tests
- Category: Database
- Reported: 9:00 AM
- Tier: 1 (Agent investigates)
- Owner: Agent 1
- Impact: Can't run parallel tests, slowing development
```

**9:00-9:30 AM - Tier 1 Investigation**
- Tried increasing timeout (no change)
- Tried reducing parallel workers to 3 (works but slow)
- Tried increasing DB connection pool size (no change)
- **ROOT CAUSE: Unclear after 30 min**

**9:35 AM - Escalation to Tier 2**
```
[Updated standup]
- Escalated to Tier 2 - can't identify root cause
- Workaround: Use -n3 flag to reduce parallelization
```

**9:35 AM - Tech Lead Response (SLA: 15 min, Actual: 5 min) ✓**
- Tech Lead posts: "Got it, let's pair. Starting at 9:35."
- Joins screen share with Agent 1

**9:35-10:15 AM - Pair Programming Session (40 minutes)**
1. Walk through fixture code
2. Agent describes what they tried
3. Tech Lead traces connection lifecycle
4. FOUND: Fixture not cleaning up connections in teardown
5. Connection pool fills up: 5 connections max → 5 tests max
6. Solution: Add explicit `connection.close()` in fixture cleanup

**10:15-10:30 AM - Implementation (15 minutes)**
- Tech Lead implements fix
- Agent runs full test suite with `-n` (parallel workers)
- All tests pass ✓

**10:30 AM - Blocker Resolved**
```
[Updated standup]
- Status: RESOLVED
- Solution: Added connection cleanup in conftest.py fixture teardown
- Duration: 1.5 hours (Tier 1: 35 min, Tier 2: 55 min)
- Prevention: Added comment in template about cleanup
```

### Outcome

- Total duration: 1.5 hours
- Tier 1 time: 35 minutes (within 2-hour SLA)
- Tier 2 time: 55 minutes (within 4-hour SLA)
- Tech Lead response: 5 minutes (within 15-min SLA) ✓
- Blocker resolved same day
- Future prevention: Template updated with cleanup best practice
- Knowledge shared: Team sees solution in standup

---

## Success Metrics

### Week 1 Targets
- [ ] All blockers categorized with correct tier
- [ ] Tier 2 response time: avg < 15 min
- [ ] 100% of blockers escalated appropriately
- [ ] Zero missed Tier 2 response SLA

### Week 4 Targets
- [ ] Tier 2 resolve time: avg < 3 hours
- [ ] Tier 3 engagement rare (< 1 per week)
- [ ] Blocker count stable < 1 per day
- [ ] Most blockers resolved in Tier 1-2

### Week 8 Targets
- [ ] Zero missed SLAs (all tiers)
- [ ] 80%+ blockers resolved in Tier 1
- [ ] Team proactively preventing blockers (fewer per day)
- [ ] Average blocker duration < 1 hour

---

## Quick Reference Card

Print and post in team channel:

```
BLOCKER ESCALATION - QUICK REFERENCE

Tier 1: YOU (0-2 hours)
  SLA: 2 hours max
  Try: Fix it yourself, research, workarounds
  If stuck: Escalate after 2 hours

Tier 2: TECH LEAD (2-4 hours)
  SLA Response: 15 minutes (CRITICAL!)
  Action: Pair programming session
  Decision: Solve or escalate to T3

Tier 3: ARCHITECT (4-8 hours)
  SLA Response: 30 minutes
  Action: Design review + refactor
  Decision: Create ADR + implement

Tier 4: PRODUCT LEAD (1-2 hours)
  Decision: More resources? Descope? Slip date?
  Action: Execute new plan

RED FLAGS (escalate immediately):
  • Coverage DOWN
  • Tests FAILING (were passing)
  • 2+ blockers active
  • Blocker age > SLA
  • Blocker affects multiple agents
```

---

## Integration with Automation

Scripts automatically:
- Track blocker age: `scripts/check_blockers.sh` (every 30 min)
- Alert on SLA violations: GitHub Actions notification
- Generate weekly report: `scripts/generate_weekly_report.py` (Friday)
- Dashboard snapshot: `scripts/dashboard_snapshot.py` (daily)

See `TRACKING_AUTOMATION_SETUP.md` for setup.

---

## Additional Resources

- **Template:** Copy blocker template from "Blocker Tracking Template" section
- **Categories:** See "Blocker Categories & Quick Routing" table
- **Decision Tree:** See "Escalation Workflow Diagram"
- **Example:** See "Real-World Example: Database Fixture Timeout"

---

*Status: Active*
*Version: 1.0*
*Last Updated: December 2024*

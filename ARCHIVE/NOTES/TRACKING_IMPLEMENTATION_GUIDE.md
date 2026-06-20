# Tracking Infrastructure Implementation Guide
**Quick-Start Guide for Critical Actions**

This document provides ready-to-use templates and scripts to fix tracking gaps identified in TRACKING_INFRASTRUCTURE_AUDIT.md.

---

## Quick Action Matrix

| Priority | Action | Time | Owner | Impact |
|----------|--------|------|-------|--------|
| 🔴 CRITICAL | Automation script | 4h | DevOps | Prevents Week 2 failure |
| 🔴 CRITICAL | Escalation tiers | 1h | Tech Lead | Unblocks team immediately |
| 🟠 HIGH | Weekly template | 2h | Product Lead | Saves 45 min/week |
| 🟠 HIGH | Quality metrics | 6h | Tech Lead | Prevents quality decay |
| 🟡 MEDIUM | Dashboard | 8h | DevOps | Better visibility |
| 🟡 MEDIUM | Auto-escalation | 4h | DevOps | Enforces SLAs |

---

## ACTION 1: Daily Update Automation (4 hours)

### File: scripts/update_coverage_metrics.sh

```bash
#!/bin/bash
set -e

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COVERAGE_DIR="${PROJECT_DIR}/.coverage_tracking"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create tracking directory
mkdir -p "${COVERAGE_DIR}"

# Step 1: Run tests and capture coverage
echo "Running tests and capturing coverage..."
pytest tests/ \
    --cov=src/tracertm \
    --cov-report=json \
    --cov-report=term \
    -q > "${COVERAGE_DIR}/pytest_${TIMESTAMP}.log" 2>&1 || true

# Step 2: Extract metrics from coverage JSON
echo "Extracting coverage metrics..."
python3 - <<'PYTHON_EOF'
import json
import os
from datetime import datetime

coverage_json = "htmlcov/coverage.json"
if not os.path.exists(coverage_json):
    print("ERROR: Coverage JSON not found")
    exit(1)

with open(coverage_json) as f:
    data = json.load(f)

metrics = {
    "date": datetime.now().isoformat(),
    "line_coverage": data["totals"]["percent_covered"],
    "lines_covered": data["totals"]["num_statements"],
    "branches": data["totals"]["num_branches"],
    "tests_run": 0,  # Can be extracted from test output
}

# Extract per-module coverage
modules = {}
for file_path, file_data in data["files"].items():
    module_name = file_path.split("src/tracertm/")[1].split("/")[0] if "src/tracertm/" in file_path else "other"
    if module_name not in modules:
        modules[module_name] = []
    modules[module_name].append(file_data["summary"]["percent_covered"])

metrics["by_module"] = {
    module: round(sum(values) / len(values), 2)
    for module, values in modules.items()
}

# Write metrics to JSON
output_file = f".coverage_tracking/metrics_{datetime.now().strftime('%Y%m%d')}.json"
os.makedirs(".coverage_tracking", exist_ok=True)
with open(output_file, "w") as f:
    json.dump(metrics, f, indent=2)

print(json.dumps(metrics, indent=2))
PYTHON_EOF
```

**Step 3: Auto-Update Dashboard (create scripts/update_dashboard.py)**

```python
#!/usr/bin/env python3
"""
Auto-updates COVERAGE_PROGRESS_DASHBOARD.md with latest metrics
Run after pytest to keep dashboard current
"""

import json
import re
from datetime import datetime
from pathlib import Path

def update_dashboard(metrics_json: dict) -> None:
    """Update dashboard with new metrics"""
    dashboard_path = Path("COVERAGE_PROGRESS_DASHBOARD.md")

    if not dashboard_path.exists():
        print("ERROR: COVERAGE_PROGRESS_DASHBOARD.md not found")
        return

    content = dashboard_path.read_text()
    today = datetime.now().strftime("%Y-%m-%d")

    # Update current metrics section
    metrics_section = f"""## Date: {today}

### Overall Metrics
- **Line Coverage:** {metrics_json['line_coverage']:.1f}% ({metrics_json['lines_covered']} lines)
- **Statement Coverage:** {metrics_json.get('statement_coverage', metrics_json['line_coverage']):.1f}%
- **Branch Coverage:** {metrics_json.get('branch_coverage', 'N/A')}%
- **Tests Collected:** {metrics_json.get('tests_run', 'N/A')}
- **Tests Passing:** {metrics_json.get('tests_passing', 'N/A')}
- **Tests Failing:** {metrics_json.get('tests_failing', 0)}

### By Module
"""

    # Add module breakdown
    if 'by_module' in metrics_json:
        for module, coverage in sorted(metrics_json['by_module'].items()):
            metrics_section += f"- **{module}:** {coverage:.1f}%\n"

    # Find and replace daily coverage section
    pattern = r"## Date: \d{4}-\d{2}-\d{2}.*?(?=\n---\n|### Tests Added Today)"
    content = re.sub(pattern, metrics_section, content, flags=re.DOTALL)

    # Update last updated timestamp
    content = re.sub(
        r"\*Last Updated: .*?\*",
        f"*Last Updated: {today}*",
        content
    )

    dashboard_path.write_text(content)
    print(f"Dashboard updated with metrics from {today}")

if __name__ == "__main__":
    # Load latest metrics JSON
    metrics_files = sorted(Path(".coverage_tracking").glob("metrics_*.json"))
    if metrics_files:
        with open(metrics_files[-1]) as f:
            metrics = json.load(f)
        update_dashboard(metrics)
    else:
        print("No metrics found in .coverage_tracking/")
```

**Step 4: Generate Daily Standup (create scripts/generate_standup.py)**

```python
#!/usr/bin/env python3
"""
Auto-generates standup template for DAILY_STANDUP_LOG.md
Agents only need to fill in: blockers, next day focus
"""

import json
from datetime import datetime
from pathlib import Path

def generate_standup():
    """Generate standup template with auto-filled metrics"""

    # Load today's metrics
    metrics_file = Path(f".coverage_tracking/metrics_{datetime.now().strftime('%Y%m%d')}.json")

    if metrics_file.exists():
        with open(metrics_file) as f:
            metrics = json.load(f)
        coverage_pct = metrics.get('line_coverage', 'N/A')
    else:
        coverage_pct = 'N/A'

    today = datetime.now().strftime("%Y-%m-%d")
    day_of_week = datetime.now().strftime("%A")

    template = f"""## {day_of_week}, {today}

### Overall Status (Auto-generated)
- **Current Coverage:** {coverage_pct}%
- **Tests Added Today:** [Fill in: number]
- **Coverage Trend:** [Yesterday → Today]

### Agent Updates (Each agent fill this in)

#### Agent 1
- **Yesterday:** [What completed]
- **Today:** [Current WP]
- **Progress:** [Specific tests added, coverage change]
- **Blockers:** [If any - leave blank if none]
- **Next:** [Tomorrow's focus]

#### Agent 2
- **Yesterday:** [What completed]
- **Today:** [Current WP]
- **Progress:** [Specific tests added, coverage change]
- **Blockers:** [If any]
- **Next:** [Tomorrow's focus]

#### Agent 3
- **Yesterday:** [What completed]
- **Today:** [Current WP]
- **Progress:** [Specific tests added, coverage change]
- **Blockers:** [If any]
- **Next:** [Tomorrow's focus]

#### Agent 4
- **Yesterday:** [What completed]
- **Today:** [Current WP]
- **Progress:** [Specific tests added, coverage change]
- **Blockers:** [If any]
- **Next:** [Tomorrow's focus]

### Team Status
- **Overall Coverage:** {coverage_pct}%
- **Total Tests Added:** [Sum of all agents]
- **Phase Target:** [Expected % by EOW]
- **On Track:** YES / NO
- **Issues Needing Escalation:** [If any]

---

"""

    # Append to standup log
    log_file = Path("DAILY_STANDUP_LOG.md")
    if log_file.exists():
        content = log_file.read_text()
        # Find today's section and insert template
        # This is simplified - in practice may need smarter insertion
        with open(log_file, "a") as f:
            f.write(template)
        print(f"Standup template generated for {today}")
    else:
        print("DAILY_STANDUP_LOG.md not found")

if __name__ == "__main__":
    generate_standup()
```

**Step 5: CI/CD Integration (add to .github/workflows/coverage.yml)**

```yaml
name: Daily Coverage Tracking

on:
  schedule:
    - cron: '18 19 * * 1-5'  # 5 PM EST weekdays
  workflow_dispatch:

jobs:
  track-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install -e ".[dev]"
          pip install pytest pytest-cov

      - name: Run coverage tracking
        run: bash scripts/update_coverage_metrics.sh

      - name: Update dashboard
        run: python3 scripts/update_dashboard.py

      - name: Generate standup
        run: python3 scripts/generate_standup.py

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "Coverage Bot"
          git add COVERAGE_PROGRESS_DASHBOARD.md DAILY_STANDUP_LOG.md
          git diff-index --quiet HEAD || git commit -m "Auto-update coverage metrics and standup template"
          git push
        if: github.ref == 'refs/heads/main'
```

**How to Deploy:**

```bash
# 1. Create scripts
mkdir -p scripts/
cp scripts/update_coverage_metrics.sh scripts/  # (from above)
cp scripts/update_dashboard.py scripts/
cp scripts/generate_standup.py scripts/

# 2. Test locally
bash scripts/update_coverage_metrics.sh

# 3. Add to git
git add scripts/ .github/workflows/coverage.yml
git commit -m "Add automated coverage tracking"
git push

# 4. Verify runs daily (check Actions tab in GitHub)
```

---

## ACTION 2: Escalation Tiers (1 hour)

### File: ESCALATION_PROTOCOL.md

Create new file with this exact content:

```markdown
# Blocker Escalation Protocol

## Overview

When an agent encounters a blocker, follow this tier system. Response time and resolution owner change based on tier.

## Tier System

### Tier 1: Agent Investigation (0-2 hours)
**Owner:** Agent
**Response Time:** Immediate (same hour)
**Resolve Time:** 2 hours max

**Actions:**
1. Document the blocker in standup with category and details
2. Investigate independently for up to 2 hours
3. Try workarounds if available
4. Document what was attempted
5. If unresolved → escalate to Tier 2

**Escalation Criteria:**
- Can't find root cause in 1 hour
- Root cause found but fix requires > 30 min
- Blocker affects multiple agents
- Blocker is critical (blocks standup)

### Tier 2: Tech Lead Pair (2-4 hours)
**Owner:** Tech Lead
**Response Time:** 15 minutes (SLA: must respond within 15 min of escalation)
**Resolve Time:** 4 hours max

**Actions:**
1. Tech Lead notified immediately (mention in Slack #blockers)
2. Pair with agent within 15 minutes
3. 30-min investigation session
4. Either: solve, workaround, or escalate
5. If unresolved → escalate to Tier 3

**Escalation Criteria:**
- Design issue (affects architecture)
- Database schema problem
- Missing external dependency
- Build/infrastructure issue
- Issue affects > 1 agent

### Tier 3: Architect Review (4-8 hours)
**Owner:** Architect (or Tech Lead + Product)
**Response Time:** 30 minutes
**Resolve Time:** 8 hours max

**Actions:**
1. Architect engaged immediately
2. May require code review/refactor
3. May require design decision
4. Solution documented in ADR (Architecture Decision Record)
5. If unresolved → escalate to Tier 4

**Escalation Criteria:**
- Requires design change
- Requires external API design
- Requires database migration
- Critical path blocker
- Affects sprint completion

### Tier 4: Priority Shift
**Owner:** Product Lead
**Response Time:** 1 hour
**Decision Time:** 1 hour

**Actions:**
1. Product Lead makes strategic decision
2. Options:
   - Increase resources (pull other work)
   - Accept schedule slip
   - Descope WP
   - Workaround acceptance
3. Decision communicated to team
4. New plan documented in standup

**Escalation Criteria:**
- Unresolvable in timeline
- Requires external team
- Requires resource reallocation

## Blocker Categories & Routing

| Category | Tier 2 Owner | Root Cause | Quick Workaround |
|----------|--------------|-----------|------------------|
| **Database** | Tech Lead | Schema issue? Fixture timeout? | Use in-memory SQLite |
| **Environment** | DevOps | Local setup? CI config? | Docker container |
| **Design unclear** | Architect | Requirements ambiguous? | Mock-first test |
| **Missing dependency** | Tech Lead | Not installed? Wrong version? | Install/update |
| **Flaky test** | QA/Test Lead | Timing? Async race? | Add retry/timeout |
| **API integration** | Integration Lead | Endpoint wrong? Auth? | Use mock server |
| **Performance** | Architect | Query slow? Memory? | Add caching |
| **Build failure** | DevOps | Missing tool? Config? | Manual build |

## Blocker Tracking Template

Use this format in standup reports:

```
BLOCKER: [Short description]
- Category: [From table above]
- Reported: [Time/date]
- Tier: [Current tier]
- Owner: [Who's working on it]
- Workaround: [If available, describe]
- ETA: [Expected resolution time]
- Impact: [What's blocked: feature? sprint?]
```

### Example:
```
BLOCKER: Database fixture timeout after 5 concurrent tests
- Category: Database
- Reported: Tuesday 2:15 PM
- Tier: 2 (escalated from Tier 1 at 2:35 PM)
- Owner: Tech Lead (paired with Agent 1)
- Workaround: Run tests serially (slower but works)
- ETA: Tuesday 4:15 PM (fixture cleanup code)
- Impact: Slowing down test development but not blocking progress
```

## SLA Compliance

Track these metrics daily:

| Tier | Metric | Target | Alert Threshold |
|------|--------|--------|-----------------|
| Tier 2 | Response time | 15 min | > 15 min |
| Tier 2 | Resolve time | 4 hours | > 4 hours |
| Tier 3 | Response time | 30 min | > 30 min |
| Tier 3 | Resolve time | 8 hours | > 8 hours |
| Tier 4 | Decision time | 1 hour | > 1 hour |
| ALL | Blocker count | < 2 | >= 2 |

## Red Flags

If you see any of these, immediately escalate:

1. **Coverage DOWN** → Immediate Tier 2 (find regression)
2. **Tests FAILING** (previously passing) → Immediate Tier 2
3. **2+ Blockers active** → Tier 3 for 1 blocker
4. **Blocker age > SLA** → Auto-escalate one tier
5. **Blocker affecting multiple agents** → Immediate Tier 2

## Escalation Workflow

```
BLOCKER DETECTED
     ↓
Agent Investigation (Tier 1, 2 hours)
     ↓
     ├→ RESOLVED: Document solution, close
     └→ UNRESOLVED: Escalate
          ↓
     Tech Lead Pair (Tier 2, 4 hours, SLA: 15 min response)
          ↓
          ├→ RESOLVED: Document, close
          └→ UNRESOLVED: Escalate
               ↓
          Architect Review (Tier 3, 8 hours, SLA: 30 min response)
               ↓
               ├→ RESOLVED: Document ADR, close
               └→ UNRESOLVED: Escalate
                    ↓
               Product Decision (Tier 4, SLA: 1 hour)
                    ↓
               DECISION MADE: Execute plan
```

## Example: Managing a Database Fixture Timeout

**9:00 AM: Agent discovers blocker**
- Tests fail with: "database fixture timeout"
- Category: Database
- Tier: 1 (Agent investigation)

**9:30 AM: After 30 min investigation**
- Tried increasing timeout → still fails
- Tried reducing parallel workers → slower but works
- Root cause not clear → Escalate to Tier 2

**9:35 AM: Tech Lead responds (SLA: 15 min, actual: 5 min)**
- Mentions Tech Lead in Slack
- Tech Lead pairs with agent
- Pair traces fixture code

**10:15 AM: Root cause found**
- Fixture not cleaning up between tests
- Connection pool exhausted after 5 tests
- Fix: Add explicit cleanup in teardown

**10:45 AM: Fix deployed and verified**
- Timeout issue resolved
- Tests pass at full parallelization
- Blocker closed

**Outcome:**
- Total blocker duration: 1 hour 45 minutes
- Tier 1 time: 35 minutes
- Tier 2 time: 70 minutes
- Resolution documented in ADR
- Preventive measure added to test template

## Automation: GitHub Actions

Create `.github/workflows/escalation-monitor.yml`:

```yaml
name: Blocker Escalation Monitor

on:
  schedule:
    - cron: '*/30 * * * *'  # Every 30 minutes
  workflow_dispatch:

jobs:
  check-blockers:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check blocker ages
        run: |
          python3 scripts/check_blocker_escalation.py

      - name: Alert if SLA missed
        run: |
          python3 scripts/alert_missed_sla.py
        if: failure()
```

## Success Metrics

**Week 1:**
- [ ] All blockers categorized correctly
- [ ] Tier 2 response time: avg < 15 min
- [ ] 100% of blockers escalated appropriately

**Week 4:**
- [ ] Tier 2 resolve time: avg < 3 hours
- [ ] Tier 3 engagement rare (< 1/week)
- [ ] Blocker count stable < 1/day

**Week 8:**
- [ ] Zero missed SLAs
- [ ] Most blockers resolved in Tier 1-2
- [ ] Team proactively preventing blockers
```

**Deployment:**

```bash
# 1. Create file
touch ESCALATION_PROTOCOL.md
# (paste content above)

# 2. Share with team
git add ESCALATION_PROTOCOL.md
git commit -m "Add blocker escalation protocol"
git push

# 3. Walkthrough in standup
# Explain tiers, SLAs, categories with examples

# 4. Update standups to use format
# Agent mentions blockers with category + tier
```

---

## ACTION 3: Weekly Review Template (2 hours)

### File: WEEKLY_REVIEW_TEMPLATE.md

```markdown
# Weekly Review Template

**Copy and paste this into DAILY_STANDUP_LOG.md every Friday**

## Week [X] Review - Phase [Y] - [Week Dates]

### Coverage Progress (Auto-generated from metrics)
```
Start:     [X]%
End:       [Y]%
Gain:      +[Z]%
Target:    +[T]%
Status:    [ON TRACK / AT RISK / OFF TRACK]
```

### Work Package Status

**Completed This Week:**
- [ ] [WP-X.Y]: [Module] → Now [A]% (was [B]%)
- [ ] [WP-A.B]: [Module] → Now [A]% (was [B]%)

**In Progress (completion ETA):**
- [ ] [WP-C.D]: [Module] (ETA: [date])
- [ ] [WP-E.F]: [Module] (ETA: [date])

**Not Started (will do next week):**
- [ ] [WP-G.H]: [Module]
- [ ] [WP-I.J]: [Module]

### Go/No-Go Decision

**Are we on track to complete phase by [target date]?**

- [ ] **YES - GO** - Proceed with planned work
- [ ] **CAUTION - GO** - Proceed but watch these: [issues]
- [ ] **NO - STOP** - Address these before continuing: [issues]

**Rationale:**
[One sentence explaining decision]

### Blockers This Week

**Top 3 Blockers (ranked by impact):**

1. **[Blocker Title]**
   - Category: [Database/Environment/Design/etc]
   - Reported: [Day/time]
   - Resolution: [How resolved or current status]
   - Duration: [Hours to resolve]

2. **[Blocker Title]**
   - Category: [...]
   - Reported: [...]
   - Resolution: [...]
   - Duration: [...]

3. **[Blocker Title]**
   - Category: [...]
   - Reported: [...]
   - Resolution: [...]
   - Duration: [...]

**Lesson Learned:**
[Prevention for next time, 1-2 sentences]

### Key Metrics

| Metric | This Week | Last Week | Target |
|--------|-----------|-----------|--------|
| Coverage Gain | +[Z]% | +[Z]% | +[T]% |
| Tests Added | [N] | [N] | [N] |
| WPs Completed | [N]/[Total] | [N]/[Total] | [N]/[Total] |
| Avg Blocker Duration | [Xh] | [Yh] | <2h |
| Blocker Count | [N] | [N] | <1 |

### Team Performance

**Velocity (tests per agent per day):**
- Agent 1: [N] tests/day
- Agent 2: [N] tests/day
- Agent 3: [N] tests/day
- Agent 4: [N] tests/day
- **Average: [N] tests/day**

**Quality Indicators:**
- Flaky tests: [N] (↑/↓/→)
- Code review blockers: [N]
- Regression incidents: [N]

### Next Week Plan

**Agent Assignments:**
- Agent 1: [WP-X.Y, WP-A.B] (expect [N] tests)
- Agent 2: [WP-C.D, WP-E.F] (expect [N] tests)
- Agent 3: [WP-G.H, WP-I.J] (expect [N] tests)
- Agent 4: [WP-K.L, WP-M.N] (expect [N] tests)

**Phase Target:** [X]% coverage by end of week [Y]

**Anticipated Blockers:**
- [If we know of upcoming challenges, list them]

**Success Looks Like:**
- Coverage: [X]% → [Y]%
- Tests: [N]+ added
- WPs: [List] completed
- No regressions
- All SLAs met

---

## How to Complete (15 minutes)

1. **Coverage Progress** - Pull from dashboard (auto-generated)
2. **WP Status** - From standup notes (5 min)
3. **Go/No-Go** - Team discussion (5 min)
4. **Blockers** - From escalation log (3 min)
5. **Metrics** - From standup summaries (2 min)
6. **Next Week** - Lead assigns + team commits (5 min)

**Total: 15-20 minutes for entire review**

## Decision Framework

### Choose "GO"
- Coverage on track or ahead
- Fewer than 2 blockers
- All agents productive
- No quality degradation

### Choose "CAUTION - GO"
- Coverage slightly behind
- 1-2 blockers being resolved
- 1 agent struggling (support plan in place)
- Minor quality issue identified

### Choose "STOP"
- Coverage significantly behind (>5% off track)
- Multiple blockers unresolved
- Process breakdown
- Regression detected

---
```

**Deployment:**

```bash
# 1. Create file
touch WEEKLY_REVIEW_TEMPLATE.md

# 2. Update DAILY_STANDUP_LOG.md
# Find each Friday's "Weekly Review" section
# Replace placeholder with actual template
# (or just link to this file)

# 3. Try first review in 15 minutes
# Measure actual time, iterate

# 4. Share with team
git add WEEKLY_REVIEW_TEMPLATE.md
git commit -m "Add streamlined weekly review template"
```

---

## Quick Implementation Checklist

### TODAY (Next 2 Hours)
- [ ] Copy Escalation Protocol into ESCALATION_PROTOCOL.md
- [ ] Share with team, walkthrough escalation tiers
- [ ] Use in next standup (categorize any current blockers)

### THIS WEEK (4-6 hours)
- [ ] Set up automation scripts (update_coverage_metrics.sh, update_dashboard.py)
- [ ] Test locally, verify dashboard updates
- [ ] Add GitHub Actions workflow for daily automation
- [ ] Deploy and monitor for 2 days

### NEXT WEEK (2 hours)
- [ ] Use weekly review template for first time
- [ ] Measure actual time (goal: 15 min)
- [ ] Iterate template based on feedback
- [ ] Start collecting metrics for dashboard

---

## Success Indicators - First Week

✅ **Automation Working**
- Dashboard updates daily automatically
- Standup template pre-filled with metrics
- Zero manual edits to dashboard structure

✅ **Escalation Protocol Used**
- All blockers have category + tier assigned
- Tier 2 responds within 15 min SLA
- Blockers documented with resolution time

✅ **Weekly Review Efficient**
- First review completes in <20 minutes
- Go/No-Go decision made clearly
- Next week plan documented

✅ **Data Visible**
- Coverage trend visible
- Blocker history tracked
- Team velocity emerging

---

## Troubleshooting

**Automation not running:**
- Check GitHub Actions tab for errors
- Verify pytest works locally first
- Check .coverage_tracking directory permissions

**Dashboard not updating:**
- Verify JSON output from pytest
- Check update_dashboard.py syntax
- Verify git permissions for auto-push

**Escalation not working:**
- Ensure all blockers categorized
- Verify Tech Lead availability
- Check Slack notification setup

---

*Implementation guide: Use with TRACKING_INFRASTRUCTURE_AUDIT.md*
*Status: Ready for immediate deployment*
*Expected deployment time: 4-6 hours critical actions*

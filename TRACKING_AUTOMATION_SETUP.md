# Tracking Automation Setup Guide

**Goal:** Automate daily coverage tracking, weekly reviews, and blocker escalation to save time and ensure consistency.

**Time Investment:** 4-6 hours setup → 10 min/day savings × 5 days × 8 weeks = 6.7 hours saved

---

## Overview

This guide provides copy-paste-ready scripts and templates to automate:

1. **Daily Coverage Updates** - Parse pytest output, update dashboard automatically
2. **Weekly Report Generation** - Compile standup data into summary
3. **Blocker Tracking** - Identify items past SLA and escalate
4. **Dashboard Snapshots** - Status report for leads

---

## Part 1: Daily Update Script

### File: `scripts/update_coverage_daily.py`

**Purpose:** Runs after tests complete, extracts coverage metrics, updates dashboard

**Usage:**
```bash
python3 scripts/update_coverage_daily.py
# OR integrate into CI/CD: add to .github/workflows/coverage.yml
```

**How it works:**
1. Reads `.coverage` file (or coverage.json)
2. Extracts metrics: line coverage %, tests run, tests passing
3. Parses module-by-module coverage
4. Updates COVERAGE_PROGRESS_DASHBOARD.md with today's data
5. Outputs JSON for other scripts

### Installation & Setup

```bash
# 1. Create scripts directory
mkdir -p scripts/

# 2. Copy script (see below)
# 3. Make executable
chmod +x scripts/update_coverage_daily.py

# 4. Test locally
python3 scripts/update_coverage_daily.py

# 5. Add to git
git add scripts/update_coverage_daily.py
git commit -m "Add daily coverage update script"
```

---

## Part 2: Weekly Report Script

### File: `scripts/generate_weekly_report.py`

**Purpose:** Compiles standup logs into weekly summary

**Usage:**
```bash
python3 scripts/generate_weekly_report.py [week_number]
# Example: python3 scripts/generate_weekly_report.py 1
# Outputs: WEEKLY_REPORT_WEEK_1.md
```

**What it does:**
1. Reads DAILY_STANDUP_LOG.md
2. Extracts all entries for the week
3. Calculates:
   - Total coverage gain
   - Tests added per agent
   - Blockers by category
   - Average blocker duration
4. Generates weekly summary (15-min format)
5. Appends to DAILY_STANDUP_LOG.md

### Installation & Setup

```bash
# 1. Copy script (see below)
# 2. Make executable
chmod +x scripts/generate_weekly_report.py

# 3. Test on Week 1
python3 scripts/generate_weekly_report.py 1

# 4. Verify output format
# 5. Add to git
git add scripts/generate_weekly_report.py
```

---

## Part 3: Blocker SLA Checker

### File: `scripts/check_blockers.sh`

**Purpose:** Identifies blockers past SLA, triggers escalation

**Usage:**
```bash
bash scripts/check_blockers.sh
# Runs every 30 min via GitHub Actions
# Alerts if any blocker exceeds SLA
```

**What it checks:**
1. Reads DAILY_STANDUP_LOG.md for active blockers
2. Extracts blocker timestamp and tier
3. Calculates age (now - reported time)
4. Compares to SLA:
   - Tier 1: Max 2 hours
   - Tier 2: Max 4 hours
   - Tier 3: Max 8 hours
5. Outputs violations + escalation recommendations
6. Creates GitHub issue if SLA missed

### Installation & Setup

```bash
# 1. Copy script (see below)
# 2. Make executable
chmod +x scripts/check_blockers.sh

# 3. Test manually
bash scripts/check_blockers.sh

# 4. Add to GitHub Actions
# See: .github/workflows/escalation-monitor.yml
```

---

## Part 4: Dashboard Snapshot Script

### File: `scripts/dashboard_snapshot.py`

**Purpose:** Generates status snapshot for project leads

**Usage:**
```bash
python3 scripts/dashboard_snapshot.py
# Outputs: DASHBOARD_SNAPSHOT_[date].md
# Or: python3 scripts/dashboard_snapshot.py --format=slack
# Outputs: Slack message (ready to post)
```

**What it generates:**
1. Current coverage %
2. Progress vs target
3. Active blockers count & age
4. Agent velocity (tests/day)
5. Risk flags (red/yellow/green)
6. Next 7 days forecast

### Installation & Setup

```bash
# 1. Copy script (see below)
# 2. Make executable
chmod +x scripts/dashboard_snapshot.py

# 3. Test
python3 scripts/dashboard_snapshot.py

# 4. Optional: Schedule in cron for daily email
# crontab -e
# 0 17 * * 1-5 cd /path/to/project && python3 scripts/dashboard_snapshot.py --email=lead@example.com
```

---

## Part 5: Escalation Tier System

### 3-Tier Blocker Escalation

**Tier 1: Agent Investigation (0-2 hours)**
- Owner: Agent
- SLA: Immediate response, resolve within 2 hours
- Action: Try to fix independently, document attempts

**Tier 2: Tech Lead Pair (2-4 hours)**
- Owner: Tech Lead
- SLA: Respond within 15 minutes, resolve within 4 hours
- Action: Pair programming session, 30-min investigation

**Tier 3: Architect Review (4-8 hours)**
- Owner: Architect
- SLA: Respond within 30 minutes, resolve within 8 hours
- Action: Design review, may require refactor

### Auto-Escalation Checklist

When creating a blocker in standup, include:

```markdown
BLOCKER: [Short title]
- Category: [Database/Environment/Design/API/Test/Build/Other]
- Reported: [Time HH:MM, Date]
- Tier: 1 (auto-escalate if not resolved in 2 hours)
- Owner: [Your name]
- Impact: [What's blocked]
- Workaround: [If available]
```

**Auto-escalation triggers:**
- Blocker age > Tier 1 SLA (2h) → Auto-escalate to Tier 2
- Blocker age > Tier 2 SLA (4h) → Auto-escalate to Tier 3
- 2+ blockers active → Auto-escalate one to Tier 3
- Coverage DOWN → Immediate Tier 2

---

## Part 6: Integration with CI/CD

### Add to `.github/workflows/coverage.yml`

```yaml
name: Daily Coverage Tracking

on:
  schedule:
    # Daily at 5 PM EST (weekdays)
    - cron: '0 22 * * 1-5'
  workflow_dispatch:

jobs:
  daily-update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install -e ".[dev,test]"
          pip install pytest pytest-cov

      - name: Run tests with coverage
        run: |
          pytest tests/ \
            --cov=src/tracertm \
            --cov-report=json \
            --cov-report=term \
            -q || true

      - name: Update coverage metrics
        run: python3 scripts/update_coverage_daily.py

      - name: Generate weekly report (Friday only)
        if: github.event.schedule == '0 22 * * 5' || contains(github.event_name, 'workflow_dispatch')
        run: python3 scripts/generate_weekly_report.py $(date +%U)

      - name: Check blockers
        run: bash scripts/check_blockers.sh

      - name: Generate dashboard snapshot
        run: python3 scripts/dashboard_snapshot.py

      - name: Commit and push updates
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "Coverage Bot"
          git add -A COVERAGE_PROGRESS_DASHBOARD.md DAILY_STANDUP_LOG.md
          git diff-index --quiet HEAD || git commit -m "Auto-update coverage metrics and standup"
          git push || true
        if: github.ref == 'refs/heads/main'
```

### Add to `.github/workflows/escalation-monitor.yml`

```yaml
name: Blocker Escalation Monitor

on:
  schedule:
    # Every 30 minutes
    - cron: '*/30 * * * *'
  workflow_dispatch:

jobs:
  check-escalation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check blocker SLAs
        run: bash scripts/check_blockers.sh

      - name: Create escalation issue if needed
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 BLOCKER SLA VIOLATION',
              body: 'Auto-escalation triggered. See check_blockers.sh output.',
              labels: ['blocker', 'escalation']
            })
```

---

## Part 7: Daily Standup Template (Simplified)

### Updated Format (5 fields instead of 10)

Use this simplified template in DAILY_STANDUP_LOG.md:

```markdown
## Date: YYYY-MM-DD (Auto-filled fields marked with *)

### Agent Updates

#### Agent 1: [Name]
- **Today's WP:** WP-X.Y
- **Progress:** [What completed] (coverage: X% → Y%)
- **Blockers:** [If any, use escalation format above]
- **Next:** [Tomorrow's focus]
- **Tests Added:** [N] *[Auto-filled from metrics]

#### Agent 2: [Name]
- **Today's WP:** [...]
- **Progress:** [...]
- **Blockers:** [...]
- **Next:** [...]
- **Tests Added:** [N] *[Auto-filled from metrics]

[... Agent 3, Agent 4 ...]

### Team Summary
- **Overall Coverage:** X% *[Auto-filled]
- **Total Tests Added:** N *[Auto-filled]
- **Phase Target:** Z% (ETA: [date])
- **On Track:** YES / NO
- **Active Blockers:** N

---
```

**Auto-fill Hints:**
- `*[Auto-filled from metrics]` fields are populated by scripts
- Agent only needs to fill: WP, Progress, Blockers, Next, Tests Added (verification)
- Reduces typing from ~10 min to ~3 min per agent

---

## Part 8: Pre-Flight Checklist Updates

### Add to PRE_FLIGHT_CHECKLIST.md

**Section: Automation & Scripts**

```markdown
### Automation Scripts Installed
- [ ] `scripts/update_coverage_daily.py` exists and is executable
- [ ] `scripts/generate_weekly_report.py` exists and is executable
- [ ] `scripts/check_blockers.sh` exists and is executable
- [ ] `scripts/dashboard_snapshot.py` exists and is executable

### Automation Tested
- [ ] Test: `python3 scripts/update_coverage_daily.py` (expect JSON output)
- [ ] Test: `python3 scripts/generate_weekly_report.py 1` (expect report)
- [ ] Test: `bash scripts/check_blockers.sh` (expect pass or blocker list)
- [ ] Test: `python3 scripts/dashboard_snapshot.py` (expect snapshot file)
- [ ] All scripts handle missing data gracefully

### GitHub Actions Configured
- [ ] `.github/workflows/coverage.yml` added
- [ ] `.github/workflows/escalation-monitor.yml` added
- [ ] First workflow run successful (check Actions tab)
- [ ] Dashboard updated automatically after first run

### Daily Standup Process Updated
- [ ] Team trained on simplified 5-field template
- [ ] Auto-fill process explained
- [ ] First standup completes in < 5 min per agent
- [ ] Escalation format understood by all
```

---

## Part 9: Implementation Timeline

### Phase 1: Setup (Day 1, ~1 hour)
1. Create `scripts/` directory
2. Copy 4 Python/Bash scripts
3. Make executable, test locally
4. Commit to git

### Phase 2: CI/CD Integration (Day 2-3, ~2 hours)
1. Create `.github/workflows/coverage.yml`
2. Create `.github/workflows/escalation-monitor.yml`
3. Run first workflow manually
4. Verify dashboard updates
5. Verify escalation monitoring

### Phase 3: Training & Adoption (Day 3-4, ~1 hour)
1. Train team on simplified standup template
2. Walk through escalation tier system
3. First real standup with new process
4. Measure actual time (goal: 5 min per agent)
5. Iterate based on feedback

### Phase 4: Monitoring (Week 2+, ongoing)
1. Check workflow logs daily
2. Monitor blocker escalations
3. Refine scripts based on actual data
4. Weekly review of automation effectiveness

---

## Part 10: Success Metrics

### Week 1
- [ ] All scripts functional
- [ ] Dashboard updating automatically
- [ ] Standup time reduced to 5-7 min per agent
- [ ] All blockers categorized with tier

### Week 2+
- [ ] Zero manual dashboard updates
- [ ] All escalations properly documented
- [ ] Blocker SLA: 95% on-time
- [ ] Weekly reports generated automatically

### Phase Completion
- [ ] 10+ hours saved on manual tracking
- [ ] 100% uptime on automation (no missed updates)
- [ ] Team confidence in blocker tracking
- [ ] Data quality sufficient for reports

---

## Part 11: Troubleshooting

### Script Issues

**"File not found" errors:**
- Verify pytest working: `pytest --version`
- Check `.coverage` file exists: `ls -la .coverage`
- Check working directory correct: `pwd`

**Dashboard not updating:**
- Check GitHub Actions logs
- Verify git permissions for auto-push
- Check COVERAGE_PROGRESS_DASHBOARD.md path

**Escalation not triggering:**
- Verify blocker format in standup (must match template)
- Check `check_blockers.sh` permissions: `chmod +x`
- Test manually: `bash scripts/check_blockers.sh`

### Workflow Issues

**Workflows not running:**
1. Check `.github/workflows/` files exist
2. Check file formatting (YAML syntax)
3. Check cron expressions (online validator)
4. Manually trigger: GitHub Actions tab → Run workflow

**Files not committing:**
- Check git permissions: `git status`
- Verify no merge conflicts
- Check branch protection rules (allow auto-commits)

---

## Part 12: Reference

### Script Dependencies

```bash
# Required Python packages
pytest>=9.0.0
pytest-cov>=4.0.0
coverage>=7.11.3
PyYAML>=6.0  # For YAML parsing if needed

# Required system tools
bash >= 5.0
git >= 2.30
python3 >= 3.12
```

### File Locations
- Scripts: `/scripts/`
- Workflows: `/.github/workflows/`
- Dashboard: `/COVERAGE_PROGRESS_DASHBOARD.md` (root)
- Standup log: `/DAILY_STANDUP_LOG.md` (root)
- Escalation protocol: `/ESCALATION_PROTOCOL.md` (root)

### Integration Points
- Tests: `tests/` → pytest → `.coverage` → scripts
- Scripts: Extract metrics → update markdown files
- Markdown: Rendered in GitHub, visible to team
- Workflows: Automated via GitHub Actions on schedule

---

## Quick Start Checklist

- [ ] Read this entire guide (15 min)
- [ ] Copy 4 scripts to `scripts/` directory (10 min)
- [ ] Test scripts locally (10 min)
- [ ] Create GitHub Actions workflows (5 min)
- [ ] Train team on new process (15 min)
- [ ] First real execution (5 min)

**Total: 1 hour to full automation**

---

*Status: Ready for implementation*
*Version: 1.0*
*Updated: December 2024*

# Weekly Review Template

**Purpose:** Quick 15-minute Friday review to assess progress and plan next week

**Copy this template and fill in for each Friday's review section in DAILY_STANDUP_LOG.md**

---

## Week [X] Review - Phase [Y] - [Start Date] to [End Date]

### 1. Coverage Progress (3 minutes - use auto-generated data)

```
Start Coverage:    [X.XX]%
End Coverage:      [Y.YY]%
Gain This Week:    +[Z.ZZ]%
Target Gain:       +[T.TT]%
Status:            [ON TRACK / AT RISK / OFF TRACK]
```

**Auto-filled from:** COVERAGE_PROGRESS_DASHBOARD.md (run scripts/update_coverage_daily.py first)

---

## 2. Work Package Status (3 minutes - from standup notes)

### Completed This Week
- [ ] [WP-X.Y]: [Module Name] - Coverage: [A]% → [B]% (gained [C]%)
- [ ] [WP-A.B]: [Module Name] - Coverage: [D]% → [E]% (gained [F]%)
- [ ] ...

### In Progress (completion ETA)
- [ ] [WP-C.D]: [Module Name] - Started [date], ETA [date]
- [ ] [WP-E.F]: [Module Name] - Started [date], ETA [date]
- [ ] ...

### Not Started (for next week)
- [ ] [WP-G.H]: [Module Name]
- [ ] [WP-I.J]: [Module Name]
- [ ] ...

---

## 3. Go/No-Go Decision (2 minutes - team discussion)

### Are we on track to meet phase target?

- [ ] **YES - GO** - Proceed with planned work
- [ ] **CAUTION - GO** - Proceed but watch these items: [1-2 issues]
- [ ] **NO - STOP** - Address these before continuing: [1-2 blockers]

### Rationale (one sentence)
[Why you chose this decision]

---

## 4. Blockers This Week (2 minutes - from escalation log)

### Count by Tier
- **Tier 1 (resolved same-day):** [N]
- **Tier 2 (needed tech lead):** [N]
- **Tier 3 (needed architect):** [N]
- **Total:** [N] blockers

### Top Blockers (1-2 most impactful)
1. **[Blocker Title]**
   - Category: [Database/Environment/Design/etc]
   - Duration: [X hours]
   - Resolution: [How resolved]

2. **[Blocker Title]**
   - Category: [...]
   - Duration: [X hours]
   - Resolution: [...]

### Lesson Learned
[One insight to prevent similar blockers next week - max 2 sentences]

---

## 5. Key Metrics (2 minutes - auto-calculated)

| Metric | This Week | Last Week | Target | Status |
|--------|-----------|-----------|--------|--------|
| Coverage Gain | +[Z]% | +[Z]% | +[T]% | ✓/⚠ |
| Tests Added | [N] | [N] | [N] | ✓/⚠ |
| WPs Completed | [N]/[Total] | [N]/[Total] | [N]/[Total] | ✓/⚠ |
| Avg Blocker Duration | [Xh] | [Yh] | <2h | ✓/⚠ |
| Blockers Count | [N] | [N] | <2 | ✓/⚠ |

---

## 6. Team Velocity (2 minutes - from standup entries)

**Tests Per Agent Per Day (approximate)**
- Agent 1: [N] tests/day
- Agent 2: [N] tests/day
- Agent 3: [N] tests/day
- Agent 4: [N] tests/day
- **Team Average: [N] tests/day**

---

## 7. Quality Indicators (1 minute)

**Quality Signals:**
- Flaky Tests: [N] (↑ Worse / → Same / ↓ Better)
- Code Review Blockers: [N]
- Test Regressions: [N]
- Coverage Regression: YES / NO

---

## 8. Next Week Plan (2 minutes - lead assigns, team commits)

### Agent Assignments & Targets
- **Agent 1:** [WP-X.Y, WP-A.B] (expect [N] tests)
- **Agent 2:** [WP-C.D, WP-E.F] (expect [N] tests)
- **Agent 3:** [WP-G.H, WP-I.J] (expect [N] tests)
- **Agent 4:** [WP-K.L, WP-M.N] (expect [N] tests)

### Phase Target by End of Next Week
**Coverage: [X]% → [Y]%** (aim for +[Z]%)

### Known Challenges to Watch
- [Challenge 1]
- [Challenge 2]

### Success Looks Like (Friday end of next week)
- Coverage: [X]% → [Y]%
- Tests: [N]+ added
- WPs Completed: [List WPs]
- No regressions
- All SLA targets met

---

## How to Complete This (15 minutes total)

1. **Section 1 (Coverage)** - 3 min
   - Pull from COVERAGE_PROGRESS_DASHBOARD.md
   - If auto-update scripts working: already filled

2. **Section 2 (WP Status)** - 3 min
   - Scan standup notes from Monday-Friday
   - List what completed, what's in progress, what's next

3. **Section 3 (Go/No-Go)** - 2 min
   - Team discussion (5 min real time, 2 min in template)
   - Make decision: GO / CAUTION-GO / STOP
   - Write one-sentence rationale

4. **Section 4 (Blockers)** - 2 min
   - Count from ESCALATION_PROTOCOL.md tracking
   - Identify top 1-2 most impactful
   - Extract lesson learned

5. **Section 5 (Metrics)** - 2 min
   - Calculate from standup entries (tests added, coverage, etc.)
   - Compare to last week
   - Mark ✓ if on target, ⚠ if off

6. **Section 6 (Velocity)** - 2 min
   - Simple math: tests added ÷ 5 days ÷ N agents
   - Shows productivity per agent

7. **Section 7 (Quality)** - 1 min
   - Flaky tests: count from test logs
   - Regressions: any tests that were passing now failing?
   - Simple gut-check on quality

8. **Section 8 (Next Week)** - 2 min
   - Lead proposes agent assignments
   - Team confirms or adjusts
   - Commit to targets

**Total: 15-20 minutes**

---

## Decision Framework

### Choose "GO"
- ✓ Coverage on track or ahead
- ✓ Fewer than 2 blockers
- ✓ All agents productive
- ✓ No quality degradation

**Example:** "Coverage gained +6% (target +5%), all WPs on schedule, blockers resolved same-day"

### Choose "CAUTION - GO"
- ⚠ Coverage slightly behind (within 2%)
- ⚠ 1-2 blockers being worked on (no SLA violations)
- ⚠ 1 agent struggling (but support plan in place)
- ⚠ Minor quality issue (with mitigation)

**Example:** "Coverage +4% (target +5%), one agent had environment setup issues but now resolved, all blockers resolved by Friday"

### Choose "NO - STOP"
- ✗ Coverage significantly behind (> 3% off target)
- ✗ Multiple blockers unresolved at week end
- ✗ Process breakdown (missed standups, unclear progress)
- ✗ Regression detected (coverage went DOWN)

**Example:** "Coverage gained only +1%, database blocker unresolved since Tuesday, coverage down 2% compared to last week"

---

## Automation Integration

**If you've installed scripts (see TRACKING_AUTOMATION_SETUP.md):**

```bash
# Run before starting review
python3 scripts/update_coverage_daily.py
python3 scripts/dashboard_snapshot.py
python3 scripts/generate_weekly_report.py [week_number]

# Scripts auto-fill:
# - Coverage metrics
# - Latest test counts
# - Blocker status
# - Module-by-module coverage
```

If scripts not installed, fill in manually from:
- COVERAGE_PROGRESS_DASHBOARD.md
- DAILY_STANDUP_LOG.md
- ESCALATION_PROTOCOL.md tracking

---

## Weekly Review Execution Checklist

**Friday end of day:**

- [ ] Pull all data from standup notes
- [ ] Calculate coverage gain (use scripts if available)
- [ ] List WPs completed, in-progress, next
- [ ] Count blockers and categorize
- [ ] Team discussion: Go/No-Go decision (5 min)
- [ ] Calculate metrics (tests/agent, etc.)
- [ ] Team assigns next week WPs
- [ ] Commit targets for next week
- [ ] Copy filled template into DAILY_STANDUP_LOG.md
- [ ] Share snapshot with project leads (optional: use dashboard_snapshot.py --format=slack)

**Total Time:** 15-20 minutes

---

## Example: Completed Week 1 Review

```markdown
## Week 1 Review - Phase 1 - Dec 2-6, 2024

### 1. Coverage Progress
```
Start Coverage:    12.10%
End Coverage:      22.34%
Gain This Week:    +10.24%
Target Gain:       +12.90% (target 25%)
Status:            AT RISK
```

### 2. Work Package Status

**Completed This Week**
- [x] WP-1.1: API Client - Coverage 0% → 45% (gained 45%)
- [x] WP-1.2: Storage Module - Coverage 5% → 38% (gained 33%)

**In Progress (completion ETA)**
- [ ] WP-1.3: Repositories - Started Dec 2, ETA Dec 10
- [ ] WP-1.4: Services (Basic) - Started Dec 3, ETA Dec 13

### 3. Go/No-Go Decision

- [ ] **YES - GO**
- [x] **CAUTION - GO** - Watch database blocker (resolved Friday but underlying issue)
- [ ] **NO - STOP**

**Rationale:** Coverage +10.24% is solid but below target; one persistent blocker suggests possible design issue; proceed but monitor next week's database performance.

### 4. Blockers This Week

**Count by Tier**
- Tier 1: 2 (both resolved same-day)
- Tier 2: 1 (database fixture)
- Tier 3: 0

**Top Blocker**
1. Database fixture timeout after 5 concurrent tests
   - Category: Database
   - Duration: 1.5 hours
   - Resolution: Added connection cleanup in fixture teardown

**Lesson Learned:** Always include explicit cleanup in fixture teardown. Document this in test template to prevent similar issues.

### 5. Key Metrics

| Metric | This Week | Last Week | Target | Status |
|--------|-----------|-----------|--------|--------|
| Coverage Gain | +10.24% | N/A | +12.90% | ⚠ |
| Tests Added | 156 | N/A | 150 | ✓ |
| WPs Completed | 2/8 | N/A | 2/8 | ✓ |
| Avg Blocker Duration | 1.5h | N/A | <2h | ✓ |
| Blockers Count | 3 | N/A | <2 | ⚠ |

### 6. Team Velocity

**Tests Per Agent Per Day**
- Agent 1: 9 tests/day
- Agent 2: 8 tests/day
- Agent 3: 7 tests/day
- Agent 4: 8 tests/day
- **Team Average: 8 tests/day**

### 7. Quality Indicators

- Flaky Tests: 0 ✓
- Code Review Blockers: 0 ✓
- Regressions: 0 ✓

### 8. Next Week Plan

**Agent Assignments & Targets**
- Agent 1: WP-1.3 (Repositories), WP-1.4a (Services basic) - expect 15 tests
- Agent 2: WP-1.4b (Services intermediate) - expect 12 tests
- Agent 3: WP-1.5 (Sync) - expect 10 tests
- Agent 4: WP-1.6 (TUI basics) + Coverage gaps - expect 12 tests

**Phase Target by End of Next Week:** 22% → 35% (aim for +13%)

**Known Challenges:** Database performance seems shaky; may need load testing. Repository layer is complex; pair work recommended.

**Success Looks Like:** Coverage 35%, all 4 WPs on track or complete, no regressions, database stable.
```

---

## FAQ

**Q: What if coverage went DOWN?**
A: That's a red flag. Investigate immediately. Either tests were deleted, or there's a regression. Choose "NO - STOP" until investigated.

**Q: Can we skip the review if on track?**
A: No - reviews are required even if going well. They track velocity and help forecast future work.

**Q: What if we can't complete the review in 15 min?**
A: You're including too much detail. The template is meant to be quick. If taking > 20 min, simplify next time.

**Q: Who fills this out?**
A: Typically the Project Lead or Tech Lead, with team input on Go/No-Go and next week assignments.

**Q: When should this be filled?**
A: Friday end-of-day, after final standup. Review before Friday standup is complete (that day's updates).

---

## Template Variations

### Lightweight Version (< 10 min)
Use if time is tight:
- Section 1: Coverage (auto-filled)
- Section 3: Go/No-Go decision only
- Section 8: Next week assignments only

### Comprehensive Version (20-30 min)
Use if doing detailed analysis:
- Include all sections
- Add module-by-module analysis
- Include detailed blocker post-mortems
- Add team retrospective (what went well, what didn't)

### Executive Summary (Slack format)
For sharing with leads/stakeholders:
```
Week 1 Review:
✓ Coverage: 12.1% → 22.3% (+10.2%)
✓ WPs: 2/8 completed
✓ Tests: 156 added
⚠ Blockers: 3 (all resolved)
📈 Status: GO (slight concern on database perf)

Next week target: 35% coverage
```

---

*Template Version: 1.0*
*Time to Complete: 15 minutes (with scripts) or 20 minutes (manual)*
*Last Updated: December 2024*

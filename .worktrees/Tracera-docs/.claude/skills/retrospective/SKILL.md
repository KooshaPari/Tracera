---
name: Retrospective
description: Extract session learnings in structured format for future sessions
triggers:
  - retrospective
  - session end
  - phase complete
  - what did we learn
---

# Session Learning Retrospective

When triggered, analyze the current session and extract learnings in this format:

## 📋 Session Overview
**Topic:** [What were we working on?]
**Duration:** [Approximate time spent]
**Outcome:** [Success/Partial/Blocked]

## ✅ What Worked
Extract successful approaches, configurations, patterns:
- **Approach/Tool:** Why it succeeded, impact, reusability
- Focus on reproducible patterns
- Include specific parameters/configurations

## ❌ What Failed
Document failures with root cause analysis:
- **Attempt:** What we tried
- **Why It Failed:** Root cause (not just symptoms)
- **Lesson:** What to avoid/check next time

This is the MOST VALUABLE section - failures teach more than successes.

## 📝 Key Decisions
Major architectural/approach decisions made:
- **Decision:** What was chosen
- **Alternatives Considered:** What we rejected and why
- **Rationale:** Why this choice for this context

## 🎯 Final Configuration
Working parameters/settings discovered:
```
[Language/Tool specific settings that worked]
```

## 🔮 Notes for Future Sessions
### Do
- Specific actionable guidance
- When X, always check Y first
- Use pattern Z for scenario A

### Don't
- Anti-patterns discovered
- Edge cases to avoid
- Common mistakes to prevent

### Watch Out For
- Gotchas discovered
- Non-obvious dependencies
- Things that look correct but fail

## 📊 Metrics (if applicable)
- Tests: X passing, Y failing
- Coverage: A% → B%
- Performance: C ms → D ms
- Context used: E%

---

**Storage:** Save to `~/.claude/memory/retrospectives/<topic>-<date>.md`

**Auto-update:** `~/.claude/memory/failures.md` with key anti-patterns

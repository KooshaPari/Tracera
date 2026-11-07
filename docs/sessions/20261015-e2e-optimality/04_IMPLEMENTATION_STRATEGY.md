# Implementation Strategy: Execution Sequence, Per-Agent Scope, Compute Placement

Planning document for phases P1–P8 execution, dirty-tree commit discipline, compute placement, agent responsibilities, monitoring.

## Key Points

- **DAG-driven execution:** P1 → {P2, P3} → P4 → {P5, P6} → P7 → P8
- **One-repo-per-agent:** Each subagent owns one repo per task batch
- **Dirty-tree discipline:** Mode 1 (plan docs, this corpus) separate from Mode 2 (implementation work)
- **Compute placement:** Local (planning docs only); defer to per-phase for builds/tests
- **Phase duration:** ~39–42h agent time; ~35–40h wall-clock (with P5/P6 parallel)
- **Handoff checklist per phase:** Clear gate criteria before proceeding to next
- **Progress tracking:** Update PROGRESS.md after each phase

See 03_DAG_WBS.md for phase dependencies and leaf-task counts.

## Commits & Modes

| Mode | Example | When |
|------|---------|------|
| Mode 1 | "docs(planning): P0 corpus — 862 leaf tasks" | After P0, before P1 |
| Mode 2 | "feat(p1): hygiene builds fixed; refactor(p2): registry active" | Each phase execution |
| Mode 3 | "WIP: p1 scratch notes" | Temporary, not merged |

Never mix modes in one commit.

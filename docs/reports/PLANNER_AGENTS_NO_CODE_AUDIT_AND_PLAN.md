# Planner Agents: No Code in Docs/Plans — Audit and Plan

**Date:** 2026-01-31  
**Goal:** Push planner agents (Gemini, Claude, other) to **never write code** in documentation and plans; instead **equip** engineer agents or others to create code or act on docs. Avoid stuffing docs/plans with code where not relevant.

---

## 1. Audit: Files In Scope

### 1.1 Agent / Gemini / Claude instruction files (globbed)

| Location | File | Purpose | Add rule? |
|----------|------|---------|-----------|
| `.bmad/docs/` | `gemini-instructions.md` | BMAD Gemini CLI instructions | ✅ Yes |
| `.bmad/docs/` | `claude-code-instructions.md` | BMAD Claude Code instructions | ✅ Yes |
| Root | `claude.md` | Claude-specific instructions (manager pattern, docs, BMAD) | ✅ Yes |
| Root | `AGENTS.md` | AI agent governance (doc structure, optionality) | ✅ Yes |

### 1.2 BMAD BMM planner agents (do not write code)

Planner / non-code roles (add explicit “never write code; equip others” in agent copy):

| Agent | File | Role |
|-------|------|------|
| PM | `.bmad/bmm/agents/pm.md` | Product Manager — plans, PRDs, specs |
| Analyst | `.bmad/bmm/agents/analyst.md` | Business Analyst — requirements, analysis |
| Architect | `.bmad/bmm/agents/architect.md` | System Architect — architecture, not implementation |
| SM | `.bmad/bmm/agents/sm.md` | Scrum Master — process, not code |
| TEA | `.bmad/bmm/agents/tea.md` | Test Architect — test strategy, not test code |
| UX Designer | `.bmad/bmm/agents/ux-designer.md` | UX — design, not implementation |
| Tech Writer | `.bmad/bmm/agents/tech-writer.md` | Documentation — structure and guidance, not code |

**Excluded:** `dev.md` (Developer) — this agent is the one that *should* write code.

### 1.3 BMAD BMM docs (shared guidance)

| File | Add rule? |
|------|-----------|
| `.bmad/bmm/docs/agents-guide.md` | ✅ Yes — add “Planner vs executor” and no-code rule for planners |

### 1.4 Docs: other and agent-related

| File | Add rule? |
|------|-----------|
| `docs/other/MULTI_AGENT_EXECUTION_SUMMARY.md` | ✅ Yes — governance note for multi-agent runs |
| `docs/other/MULTI_AGENT_EXECUTION_COMPLETE.md` | ✅ Yes — same |
| `docs/guides/agents.md` | ✅ Yes — if it instructs agents |
| `docs/reference/AGENT_SYSTEM_QUICK_START.md` | ✅ Yes — if it instructs agents |

### 1.5 Optional / reference only

- `00_AGENT_SYSTEM_START_HERE.md` — navigation; optional brief note.
- `.bmad/bmb/docs/understanding-agent-types.md` — architecture; optional note that planner-type agents follow the no-code rule.
- CIS/BMB agents (brainstorming, design-thinking, etc.) — treat as planners; add rule if they have their own instruction files.

---

## 2. Standard rule text (to add)

Use one of the two variants below so wording is consistent.

### 2.1 Short (for instruction files and governance)

```markdown
## Planner agents: no code in docs or plans

**Planner agents** (e.g. PM, Analyst, Architect, SM, TEA, UX Designer, Tech Writer, BMad Master) must **never write code**, especially in documentation and plans. Their job is to **equip others**—engineer agents or humans—to create code or act on docs. Write specs, acceptance criteria, architecture decisions, and clear handoffs; do not write implementation. Avoid stuffing docs or plans with code where it is not directly relevant; prefer references, file paths, or brief pseudocode when necessary.
```

### 2.2 One-line (for agent persona files)

```markdown
**Do not write code.** Equip engineer agents or others to implement; write specs, criteria, and handoffs—not implementation. Avoid code in docs/plans unless strictly necessary (prefer references or brief pseudocode).
```

---

## 3. Plan: Where to add what

| # | File | Action |
|---|------|--------|
| 1 | `docs/reports/PLANNER_AGENTS_NO_CODE_AUDIT_AND_PLAN.md` | ✅ Created (this file) |
| 2 | `.bmad/docs/gemini-instructions.md` | Add § “Planner agents: no code…” (short) after optionality |
| 3 | `.bmad/docs/claude-code-instructions.md` | Same |
| 4 | `claude.md` | Same (after optionality or before BMAD section) |
| 5 | `AGENTS.md` | Add under “AI Agent Instructions” (short) |
| 6 | `.bmad/bmm/docs/agents-guide.md` | Add subsection “Planner agents: no code in docs/plans” + short rule |
| 7 | `.bmad/bmm/agents/pm.md` | Add one-line rule in persona/instructions |
| 8 | `.bmad/bmm/agents/analyst.md` | Same |
| 9 | `.bmad/bmm/agents/architect.md` | Same |
| 10 | `.bmad/bmm/agents/sm.md` | Same |
| 11 | `.bmad/bmm/agents/tea.md` | Same |
| 12 | `.bmad/bmm/agents/ux-designer.md` | Same |
| 13 | `.bmad/bmm/agents/tech-writer.md` | Same |
| 14 | `docs/other/MULTI_AGENT_EXECUTION_SUMMARY.md` | Add governance note (short) |
| 15 | `docs/other/MULTI_AGENT_EXECUTION_COMPLETE.md` | Same |
| 16 | `docs/guides/agents.md` | Add short rule if it instructs agents |
| 17 | `docs/reference/AGENT_SYSTEM_QUICK_START.md` | Add short rule if it instructs agents |

---

## 4. Implementation status

- [x] Audit and plan document (this file)
- [x] Gemini/Claude instruction files updated (`.bmad/docs/gemini-instructions.md`, `.bmad/docs/claude-code-instructions.md`)
- [x] Root claude.md and AGENTS.md updated
- [x] BMM agents-guide and planner agent .md files updated (agents-guide, pm, analyst, architect, sm, tea, ux-designer, tech-writer)
- [x] docs/other and agent guides/references updated (MULTI_AGENT_EXECUTION_SUMMARY, MULTI_AGENT_EXECUTION_COMPLETE, docs/guides/agents.md, docs/reference/AGENT_SYSTEM_QUICK_START.md)

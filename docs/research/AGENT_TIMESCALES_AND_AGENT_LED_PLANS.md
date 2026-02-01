# Agent timescales and agent-led plans – research

Reference for the timescale and agent-led guidance used in CLAUDE.md, AGENTS.md, and .bmad agent instructions. Borrowed and tightened from **NetWeave** (see `../../../355/NetWeave`).

---

## Source: NetWeave

- **NetWeave CLAUDE.md** – "Time Reframing: Agent Actions, Not Human Hours"; task decomposition rules; subagent parallelization (light 2–5 min, medium 5–15 min, heavy 15–30 min); 50% reliability horizon ~50–120 min; forbidden/required patterns.
- **NetWeave AGENTS.md** – Role templates, work decomposition (tool calls per task), wall-clock per task type (e.g. 2–3 min, 3–5 min), checkpoint strategy (human vs automated).

NetWeave still over-estimates in practice (e.g. "3–5 min" for cross-stack can often be tighter). This project uses **more aggressive** bounds and **agent-led, no user-handoff** rules.

---

## This project’s stance

### Agent-led environment

- **Assumption:** Agent-driven, agent-led execution. User and external humans do **not** perform plan steps—only prompts and basic elicitation.
- **Forbidden in plans:** "Schedule external security audit", "Stakeholder Presentation: Present master plan", "Team Kickoff: Assign owners for Phase 1", "Human checkpoint", "Get approval from X", or any task that assigns work to a human.
- **Agents own:** Decomposition, execution, handoffs. If a deliverable is needed (e.g. presentation doc, owner manifest), agents produce it.

### Timescales (aggressive)

- **Effort in agent terms only:** Tool calls, parallel subagent count, wall clock in **minutes**. No "days" or "weeks" in execution estimates.
- **Rough mapping (aggressive):**
  - Trivial: 1–2 tool calls, &lt;1 min
  - Small feature (one endpoint/component): 3–6 tool calls, 1–3 min
  - Cross-stack (2–3 areas): 8–15 tool calls or 2–3 parallel subagents, 3–8 min
  - Major refactor / new module: 15–30 tool calls or 3–5 parallel subagents, 8–20 min
  - Multi-phase: decompose into batches; each batch ≤10–20 min wall clock
- **Forbidden phrasing:** "This will take 2 days", "Schedule a review", "Assign owners", "Present to stakeholders", "Human validation required".

---

## Where it’s documented

- **CLAUDE.md** – Section "Timescales: agent-led, aggressive estimates".
- **AGENTS.md** – Bullet "Agent-led environment; no user-handoff tasks" and timescale summary.
- **.bmad/docs/** – Section "Agent-led environment; timescales (aggressive)" in claude-code-instructions.md, gemini-instructions.md, auggie-instructions.md, codex-instructions.md, cursor-instructions.md.

# BMAD Method - Codex Instructions

## Optionality and failure behavior

**Project stance (required):** **Require** dependencies where they belong; **require** clear, loud failures—no silent or “graceful” degradation.

- **Force requirement where it belongs.** Do not make dependencies “optional” just to avoid startup or runtime failure. If a service or config is required for correctness (e.g. go-backend, temporal-host, database), treat it as required and fail when it is missing or down.
- **Fail clearly, not silently.** You **must** use explicit failures (preflight failed, runtime error)—not continuing with reduced functionality, logging-only warnings, or hiding errors. Users and operators **must** see *what* failed (e.g. named items: `go-backend; temporal-host`) and that the process did not silently degrade.
- **Graceful in other ways.** Be “graceful” only via: retries with visible feedback; error messages that list each failing item (semicolon- or newline-separated); actionable messages. Do *not* use optionality or silent fallbacks as a substitute for fixing or starting the real dependency.

When adding preflight checks, startup logic, or error handling, follow this stance.

---

## Planner agents: no code in docs or plans

**Planner agents** (e.g. PM, Analyst, Architect, SM, TEA, UX Designer, Tech Writer, BMad Master) must **never write code**, especially in documentation and plans. Their job is to **equip others**—engineer agents or humans—to create code or act on docs. Write specs, acceptance criteria, architecture decisions, and clear handoffs; do not write implementation. Avoid stuffing docs or plans with code where it is not directly relevant; prefer references, file paths, or brief pseudocode when necessary.

---

## Subagent swarm (async orchestration)

**If you have subagent/swarm capabilities:** Use them as an **async swarm** so you can keep working and reawaken as tasks finish.

- **Call task agents async.** Do not block on each one. Fire tasks so that as each completes, you are **reawoken** and can re-evaluate, spawn more agents, or do more work yourself.
- **Run a swarm.** You can run many task agents in parallel (use best judgment; break down and isolate tasks well). **Max 50 concurrent task agents at a time**—not 5.
- **Work in between.** While tasks run async, use your own context to do planning, monitoring, or other work. When you go idle, you are reawoken as each agent completes to spawn more, do follow-up work, or consolidate results.

---

## Phased WBS and plans with DAGs

When generating **plans**, **roadmaps**, or **implementation breakdowns**, use a **phased Work Breakdown Structure (WBS)** and model **dependencies as a DAG** (directed acyclic graph).

- **Phases:** Structure work into ordered phases (e.g. Phase 1: Discovery/Scope, Phase 2: Design, Phase 3: Build, Phase 4: Test/Validate, Phase 5: Deploy/Handoff). Each phase contains deliverable-oriented work packages.
- **DAG:** Tasks have explicit **predecessors**; no cycles. List dependencies so execution order is unambiguous (e.g. "Task B depends on A; C depends on B" or a table with **Depends On**).
- **Output:** Prefer a phased WBS (hierarchy by phase) plus a dependency list or small DAG (text or diagram). Optionally a table: **Phase | Task ID | Description | Depends On**.
- **Planner agents:** When producing plans or PRDs, always use phased WBS and DAG-style dependencies so implementers and PMs can schedule and parallelize correctly.

---

## Agent-led environment; timescales (aggressive)

Assume **agent-driven, agent-led** execution. No user or external human steps in plans—only prompts and elicitation. **Forbidden in plans:** "Schedule external audit", "Stakeholder Presentation", "Team Kickoff: Assign owners", "Human checkpoint", "Get approval". Agents produce deliverables and own execution. **Effort:** Use agent terms only (tool calls, subagents, wall clock in **minutes**). Aggressive estimates: small feature 3–6 calls (~1–3 min), cross-stack 8–15 calls or 2–3 subagents (~3–8 min), major refactor 15–30 calls (~8–20 min). No "days" or "weeks" in execution estimates.

---

## Native services over Docker; local OSS/free only

**Prefer native services over Docker** for development. Run Postgres, Redis, Caddy, etc. as **native processes** (e.g. `make install-native`, process-compose). Use Docker only when native is not feasible (e.g. CI, production). **Strictly prefer local, OSS, and free:** do **not** recommend paid online services when local or free alternatives exist; prefer self-hosted, open-source, free-tier, or local tooling. Document paid options only as fallback and label them clearly.

---

## Activating Agents

BMAD agents, tasks and workflows are installed as custom prompts in
`$CODEX_HOME/prompts/bmad-*.md` files. If `CODEX_HOME` is not set, it
defaults to `$HOME/.codex/`.

### Examples

```
/bmad-bmm-agents-dev - Activate development agent
/bmad-bmm-agents-architect - Activate architect agent
/bmad-bmm-workflows-dev-story - Execute dev-story workflow
```

### Notes

Prompts are autocompleted when you type /
Agent remains active for the conversation
Start a new conversation to switch agents

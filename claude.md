# Context Management Strategy

## The Manager Pattern

**CRITICAL**: Operate as a strategic manager, not a worker. Delegate to subagents.

### Keep in Main Context
- User intent and requirements
- Strategic decisions and trade-offs
- Summaries of completed work
- Critical architectural knowledge

### Delegate to Subagents
- File exploration (>3 files)
- Pattern searches across codebase
- Multi-file implementations
- Long command sequences
- Test execution

---

## Delegation Quick Reference

| Need | Delegate To | Example Prompt |
|------|-------------|----------------|
| Find code patterns | `Explore` | "Find all error handling patterns" |
| Design approach | `Plan` | "Design auth implementation strategy" |
| Run commands | `Bash` | "Run test suite and report failures" |
| Multi-step implementation | `general-purpose` | "Implement and test feature X" |
| Quick isolated fix | DO NOT delegate | Handle directly |

### Parallel vs Sequential

**Parallel** (no dependencies):
- Launch 2-3 explore agents simultaneously for independent searches

**Sequential** (dependent):
1. explore -> receive summary
2. plan based on findings -> receive plan
3. implement approved plan

---

## Subagent swarm (async orchestration)

**If you have subagent/swarm capabilities:** Use them as an **async swarm** so you can keep working and reawaken as tasks finish.

- **Call task agents async.** Do not block on each one. Fire tasks so that as each completes, you are **reawoken** and can re-evaluate, spawn more agents, or do more work yourself. The system can reawake you on each agent completion.
- **Run a swarm.** You can run many task agents in parallel (use best judgment; break down and isolate tasks well). **Max 50 concurrent task agents at a time**—not 5. Scale up when the work is well decomposed and independent.
- **Work in between.** While tasks run async, use your own context to do planning, monitoring, or other work. Monitor spawned agents and react when they complete.
- **Reawaken on completion.** When you go idle, you will be reawoken as each agent completes. Use that to: spawn more agents for the next batch, do follow-up work, or consolidate results. Effectively: call a swarm → stay available → reawake on each completion → spawn more or continue until done.

---

## Anti-Patterns

| Bad | Good |
|-----|------|
| Reading 10 files to "understand" | Delegate exploration, get summary |
| Editing files for multi-file changes | Delegate to `general-purpose` |
| Sequential explorations one-by-one | Batch parallel explores |
| Asking subagent for "all results" | Ask for "summary" or "key files" |

---

## Context Budget Rule

If task adds >2000 tokens of file content/output, **delegate it**.

---

## Optionality and failure behavior

**Project stance (required):** **Require** dependencies where they belong; **require** clear, loud failures—no silent or “graceful” degradation.

- **Force requirement where it belongs.** Do not make dependencies “optional” just to avoid startup or runtime failure. If a service or config is required for correctness (e.g. go-backend, temporal-host, database), treat it as required and fail when it is missing or down.
- **Fail clearly, not silently.** You **must** use explicit failures (preflight failed, runtime error)—not continuing with reduced functionality, logging-only warnings, or hiding errors. Users and operators **must** see *what* failed (e.g. named items: `go-backend; temporal-host`) and that the process did not silently degrade.
- **Graceful in other ways.** Be “graceful” only via: retries with visible feedback (e.g. “Waiting for X… (2/6)”); error messages that list each failing item (semicolon- or newline-separated); actionable messages and non-obscure stack traces. Do *not* use optionality or silent fallbacks as a substitute for fixing or starting the real dependency.

When adding preflight checks, startup logic, or error handling, follow this stance; do not suggest making required dependencies optional to “fix” failures.

---

## Planner agents: no code in docs or plans

**Planner agents** (e.g. PM, Analyst, Architect, SM, TEA, UX Designer, Tech Writer, BMad Master) must **never write code**, especially in documentation and plans. Their job is to **equip others**—engineer agents or humans—to create code or act on docs. Write specs, acceptance criteria, architecture decisions, and clear handoffs; do not write implementation. Avoid stuffing docs or plans with code where it is not directly relevant; prefer references, file paths, or brief pseudocode when necessary.

---

## Phased WBS and plans with DAGs

When generating **plans**, **roadmaps**, or **implementation breakdowns**, use a **phased Work Breakdown Structure (WBS)** and model **dependencies as a DAG** (directed acyclic graph).

- **Phases:** Structure work into ordered phases (e.g. Phase 1: Discovery/Scope, Phase 2: Design, Phase 3: Build, Phase 4: Test/Validate, Phase 5: Deploy/Handoff). Each phase contains deliverable-oriented work packages.
- **DAG:** Tasks have explicit **predecessors**; no cycles. List dependencies so execution order is unambiguous (e.g. "Task B depends on A; C depends on B" or a table with **Depends On**).
- **Output:** Prefer a phased WBS (hierarchy by phase) plus a dependency list or small DAG (text or diagram). Optionally a table: **Phase | Task ID | Description | Depends On**.
- **Planner agents:** When producing plans or PRDs, always use phased WBS and DAG-style dependencies so implementers and PMs can schedule and parallelize correctly.

---

## Timescales: agent-led, aggressive estimates

**Assume an agent-driven, agent-led environment.** No user or external human intervention beyond prompts and basic elicitation. Do not emit tasks that require the user or stakeholders to do work.

- **Forbidden in plans:** "Schedule external security audit", "Stakeholder Presentation: Present master plan", "Team Kickoff: Assign owners for Phase 1", "Human checkpoint", "Get approval from X", or any step that assigns work to a human. Agents own execution and handoffs; if a deliverable is needed (e.g. a presentation or owner manifest), agents produce it.
- **Effort in agent terms only:** Reframe all effort as **agent actions** (tool calls, subagent batches). Use **aggressive** wall-clock: err on the side of shorter estimates—if in doubt, use the lower bound.
- **Rough mapping (aggressive):**
  - 1 response / trivial change: 1–2 tool calls, &lt;1 min wall clock
  - Small feature (one endpoint, one component): 3–6 tool calls, 1–3 min wall clock
  - Cross-stack feature (2–3 areas): 8–15 tool calls or 2–3 parallel subagents, 3–8 min wall clock
  - Major refactor or new module: 15–30 tool calls or 3–5 parallel subagents, 8–20 min wall clock
  - Multi-phase initiative: decompose into agent batches; each batch 10–20 min wall clock max; no "days" or "weeks" in execution estimates
- **Forbidden phrasing:** "This will take 2 days", "Schedule a review", "Assign owners", "Present to stakeholders", "Human validation required". Use: "N tool calls", "N parallel subagents", "~M min wall clock", "Agent-produced artifact X".

---

# Project Development Instructions

## Dev environment and agents (rtm dev / make dev)

**If the dev stack is already running**, do **not** start services yourself. Assume services are on **hot reload** (Air for Go, uvicorn --reload for Python, Vite HMR for frontend).

- **Logs:** One log file per service under **`.process-compose/logs/`**. Logs are **ephemeral** (truncated on each `make dev` / `make dev-tui` start). Read them to see current output and restarts.
  - Examples: `.process-compose/logs/go-backend.log`, `.process-compose/logs/python-backend.log`, `.process-compose/logs/frontend.log`, `.process-compose/logs/caddy.log`
- **Lifecycle markers:** Each app service log includes injected `[LIFECYCLE] START <service> <timestamp>` at start and `[LIFECYCLE] STOP <service> <timestamp> exit=<code>` on exit so restarts are obvious.
- **Start/stop:** User runs `make dev` (detached) or `make dev-tui` (TUI). Before starting dev yourself, check if processes are already up (e.g. health endpoints or log files present) and prefer **reading** `.process-compose/logs/<service>.log` over starting duplicate stacks.

## Package Manager

**Always use `bun` instead of `npm` for all package management tasks.**

- Install: `bun install` (not `npm install`)
- Run scripts: `bun run <script>` (not `npm run <script>`)
- Add dependencies: `bun add <package>` (not `npm install <package>`)
- Dev dependencies: `bun add -d <package>` (not `npm install --save-dev <package>`)

## Native services over Docker; local OSS/free only

**Prefer native services over Docker** for development and tooling. Run Postgres, Redis, Caddy, Prometheus, etc. as **native processes** (e.g. via `make install-native` and process-compose). Use Docker only when native install is not feasible (e.g. CI, production image) or explicitly required. Do not recommend Docker-first for local dev when native orchestration is available.

**Strictly prefer local, OSS, and free.** Do **not** recommend paid online services (SaaS, cloud APIs, paid tiers) when local or free alternatives exist. Prefer: self-hosted, open-source, free-tier, or local tooling. If a feature requires external services, prefer OSS/self-hosted or free options first; document paid options only as fallback and label them clearly. No "use service X (paid)" as the default recommendation.

---

# BMAD Method - Claude Code Instructions

## Activating Agents

BMAD agents are installed as slash commands in `.claude/commands/bmad/`.

### How to Use

1. **Type Slash Command**: Start with `/` to see available commands
2. **Select Agent**: Type `/bmad-{agent-name}` (e.g., `/bmad-dev`)
3. **Execute**: Press Enter to activate that agent persona

### Examples

```
/bmad:bmm:agents:dev - Activate development agent
/bmad:bmm:agents:architect - Activate architect agent
/bmad:bmm:workflows:dev-story - Execute dev-story workflow
```

### Notes

- Commands are autocompleted when you type `/`
- Agent remains active for the conversation
- Start a new conversation to switch agents

---

## Documentation Organization

**CRITICAL**: All project documentation follows a strict organization structure.

### Root-Level Files (Keep in Root)

Only these files should remain in the project root:
- `README.md` - Main project documentation
- `CHANGELOG.md` - Project changelog
- `AGENTS.md` - AI agent instructions
- `CLAUDE.md` / `claude.md` - Claude-specific instructions
- `00_START_HERE.md` - Getting started guide (if applicable)

### Documentation Structure

All other `.md` files must be organized in `docs/` subdirectories:

```
docs/
├── guides/              # Implementation guides and how-tos
│   └── quick-start/     # Quick start guides
├── reports/             # Completion reports, summaries, status reports
├── research/            # Research summaries, indexes, analysis
├── reference/           # Quick references, API references
└── checklists/          # Implementation checklists, verification lists
```

### File Organization Rules

**When creating or moving documentation:**

1. **Quick Starts** → `docs/guides/quick-start/`
   - Files matching `*QUICK_START*.md` or `*QUICKSTART*.md`

2. **Quick References** → `docs/reference/`
   - Files matching `*QUICK_REFERENCE*.md` or `*QUICK_REF*.md`

3. **Implementation Guides** → `docs/guides/`
   - Files matching `*IMPLEMENTATION_GUIDE*.md` or `*GUIDE*.md`
   - General implementation documentation

4. **Completion Reports** → `docs/reports/`
   - Files matching `*COMPLETE*.md`, `*COMPLETION*.md`, `*SUMMARY*.md`, `*REPORT*.md`
   - Phase completion files (`PHASE_*.md`)
   - Test-related reports (`*TEST*.md`)

5. **Research Files** → `docs/research/`
   - Files matching `*RESEARCH*.md` or `*INDEX*.md`

6. **Checklists** → `docs/checklists/`
   - Files matching `*CHECKLIST*.md`

### AI Agent Instructions

**When working as Claude:**

- **NEVER** create `.md` files in the project root (except the allowed files above)
- **ALWAYS** place new documentation in the appropriate `docs/` subdirectory
- **VERIFY** file location before creating documentation
- **MOVE** misplaced files to correct subdirectories if found
- **REFERENCE** this structure when users ask about documentation organization

### Maintenance

- Use the `organize_docs.sh` script to reorganize misplaced files
- Keep root directory clean and organized
- Reference this structure in all documentation creation workflows

---

## Documentation Organization

**CRITICAL**: All project documentation follows a strict organization structure.

### Root-Level Files (Keep in Root)

Only these files should remain in the project root:
- `README.md` - Main project documentation
- `CHANGELOG.md` - Project changelog
- `AGENTS.md` - AI agent instructions
- `CLAUDE.md` - This file (Claude-specific instructions)
- `00_START_HERE.md` - Getting started guide (if applicable)

### Documentation Structure

All other `.md` files must be organized in `docs/` subdirectories:

```
docs/
├── guides/              # Implementation guides and how-tos
│   └── quick-start/     # Quick start guides
├── reports/             # Completion reports, summaries, status reports
├── research/            # Research summaries, indexes, analysis
├── reference/           # Quick references, API references
└── checklists/          # Implementation checklists, verification lists
```

### File Organization Rules

**When creating or moving documentation:**

1. **Quick Starts** → `docs/guides/quick-start/`
   - Files matching `*QUICK_START*.md` or `*QUICKSTART*.md`

2. **Quick References** → `docs/reference/`
   - Files matching `*QUICK_REFERENCE*.md` or `*QUICK_REF*.md`

3. **Implementation Guides** → `docs/guides/`
   - Files matching `*IMPLEMENTATION_GUIDE*.md` or `*GUIDE*.md`
   - General implementation documentation

4. **Completion Reports** → `docs/reports/`
   - Files matching `*COMPLETE*.md`, `*COMPLETION*.md`, `*SUMMARY*.md`, `*REPORT*.md`
   - Phase completion files (`PHASE_*.md`)
   - Test-related reports (`*TEST*.md`)

5. **Research Files** → `docs/research/`
   - Files matching `*RESEARCH*.md` or `*INDEX*.md`

6. **Checklists** → `docs/checklists/`
   - Files matching `*CHECKLIST*.md`

### AI Agent Instructions

**When working as Claude:**

- **NEVER** create `.md` files in the project root (except the allowed files above)
- **ALWAYS** place new documentation in the appropriate `docs/` subdirectory
- **VERIFY** file location before creating documentation
- **MOVE** misplaced files to correct subdirectories if found
- **REFERENCE** this structure when users ask about documentation organization

### Maintenance

- Use the `organize_docs.sh` script to reorganize misplaced files
- Keep root directory clean and organized
- Reference this structure in all documentation creation workflows

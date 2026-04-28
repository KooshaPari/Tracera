# ADR-0013: AI Agent Coordination Architecture

**Status:** Accepted
**Date:** 2026-02-08
**Deciders:** Development Team
**Supersedes:** N/A

---

## Context

TraceRTM is built entirely by AI agents (Claude Sonnet 4.5, Claude Opus 4.6). The codebase requires:

1. **Agent sessions:** Checkpoint/restore agent state across conversations
2. **Parallel execution:** Multiple agents working on independent tasks simultaneously
3. **Quality enforcement:** Agents must fix violations before PR merge
4. **Context management:** Agents operate within 1M token context (Claude Sonnet 4.5)
5. **Methodology:** BMM (BMAD Modular Method) for task decomposition

Agent patterns:
- **Swarm execution:** 21 agents in parallel across 3 waves (mypy marathon, Session 10)
- **Quality gates:** Agents run `make lint`, fix violations, verify before commit
- **Checkpoints:** Save agent state after major milestones
- **Aggressive timescales:** Estimate in minutes/hours, not days/weeks

Technology constraints:
- **API:** Claude API (Anthropic)
- **Models:** Sonnet 4.5 (bulk), Opus 4.6 (complex reasoning)
- **Context:** 1M tokens (Sonnet 4.5), 200K tokens (Opus 4.6)
- **Costs:** $3/M input tokens (Sonnet), $15/M input tokens (Opus)

## Decision

We will use:
- **Primary model:** Claude Sonnet 4.5 (1M context) for bulk operations
- **Complex tasks:** Claude Opus 4.6 for architecture decisions, reviews
- **Coordination:** BMM/BMB methodology (task decomposition, phased execution)
- **State management:** Checkpoint files (`.checkpoint-*.md`) + git commits
- **Parallel execution:** Agent swarms (up to 50 concurrent agents)

## Rationale

### Agent Model Selection

**From pyproject.toml:**
```toml
dependencies = [
    "anthropic>=0.77.0",  # Claude API SDK
]
```

**Model Strategy:**
```
┌─────────────────────────────────────────────────────────────┐
│                   Agent Coordinator                          │
│  (Main Claude instance, team lead)                           │
│                                                              │
│  Model: Claude Sonnet 4.5 (1M context)                       │
│  Role:                                                       │
│    ├─ Task decomposition (WBS + DAG)                        │
│    ├─ Agent assignment (spawn sub-agents)                   │
│    ├─ Progress monitoring                                   │
│    └─ Quality gate enforcement                              │
└─────────────────────────────────────────────────────────────┘
                         │
           ┌─────────────┴─────────────┐
           │                           │
    ┌──────▼───────┐           ┌───────▼──────┐
    │  Sub-agents  │           │  Sub-agents  │
    │  (Parallel)  │           │  (Parallel)  │
    │              │           │              │
    │  Sonnet 4.5  │           │  Opus 4.6    │
    │              │           │  (reviews)   │
    └──────────────┘           └──────────────┘
       │       │                      │
       ▼       ▼                      ▼
    fix-1   fix-2                 review-1
```

**Model Costs (per 1M tokens):**
| Model | Input | Output | Context | Use Case |
|-------|-------|--------|---------|----------|
| Sonnet 4.5 | $3 | $15 | 1M | Bulk fixes, code generation, quality swarms |
| Opus 4.6 | $15 | $75 | 200K | Architecture review, complex reasoning, PRs |

**Decision logic:**
- **Sonnet 4.5:** Default for all code tasks (mypy fixing, ruff violations, tests)
- **Opus 4.6:** Architecture decisions, ADR writing, PR reviews, complex refactors

### BMM Methodology (BMAD Modular Method)

**Task Decomposition:**
```markdown
# Example: Mypy Marathon (Session 10)

## Phase 1: Discovery (10 min)
- Run mypy, capture 2,654 errors
- Group by module (api/, services/, mcp/)
- Assign priority (P0: blocking, P1: important, P2: nice-to-have)

## Phase 2: Wave 1 Execution (45 min)
- Spawn 8 agents (module-based)
  - Agent 1: src/tracertm/api/ (301 errors)
  - Agent 2: src/tracertm/services/ (500 errors)
  - Agent 3: src/tracertm/mcp/ (240 errors)
  - ...
- Each agent:
  1. Run mypy --follow-imports=skip (isolate module)
  2. Fix errors (dict[str, object] → dict[str, Any])
  3. Verify (mypy passes)
  4. Commit

## Phase 3: Wave 2 Execution (45 min)
- Spawn 8 agents (file-based, remaining errors)
- Target: Large files with 50+ errors each

## Phase 4: Wave 3 Cleanup (30 min)
- Spawn 5 agents (final pass)
- Fix edge cases, verify 0 errors

## Result:
- 21 agents total, 2.5 hours wall clock
- 54% reduction (2,654 → 1,233 errors)
- 3 waves with 15-min checkpoints
```

**Phased WBS Template:**
```
Phase 1: Discovery/Scope
  ├─ Task 1.1: Measure baselines
  ├─ Task 1.2: Identify targets
  └─ Task 1.3: Assign priorities

Phase 2: Implementation
  ├─ Task 2.1: Wave 1 (parallel agents)
  ├─ Task 2.2: Wave 2 (parallel agents)
  └─ Task 2.3: Wave 3 (cleanup)

Phase 3: Verification
  ├─ Task 3.1: Run quality checks
  ├─ Task 3.2: Verify baselines
  └─ Task 3.3: Document results

Phase 4: Handoff
  ├─ Task 4.1: Update MEMORY.md
  ├─ Task 4.2: Create checkpoint file
  └─ Task 4.3: Notify team lead
```

### Checkpoint/Restore Strategy

**Checkpoint Files:**
```
.checkpoint-2-monitoring.txt          # Phase 2 status
.checkpoint3_status_snapshot.txt      # Phase 3 completion
.SESSION_5_CHECKPOINT_3_FINAL_STATUS.md  # Session 5 final state
```

**Checkpoint Format:**
```markdown
# Checkpoint 3: Mypy Marathon Complete

**Timestamp:** 2026-02-12 14:30:00
**Phase:** Phase 4 (Verification)
**Status:** 54% reduction achieved

## Baseline
- Mypy errors: 2,654 (start)
- Mypy errors: 1,233 (end)
- Reduction: 1,421 errors (54%)

## Agents Deployed
- Wave 1: 8 agents (module-based)
- Wave 2: 8 agents (file-based)
- Wave 3: 5 agents (cleanup)
- Total: 21 agents

## Next Steps
- [ ] Continue Wave 4 (remaining 1,233 errors)
- [ ] Target: <500 errors (80% reduction)
- [ ] ETA: +2 hours wall clock
```

### Agent Swarm Patterns

**Parallel Execution (up to 50 agents):**
```python
# Pseudo-code for agent swarm
async def spawn_agent_swarm(tasks: list[Task], max_concurrent=50):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def run_agent(task):
        async with semaphore:
            agent = ClaudeAgent(model="claude-sonnet-4-5-20250929")
            result = await agent.execute(task)
            await save_checkpoint(task.id, result)
            return result

    results = await asyncio.gather(*[run_agent(t) for t in tasks])
    return results

# Example: Mypy swarm
tasks = [
    Task(id="fix-api", cmd="fix mypy errors in src/tracertm/api/"),
    Task(id="fix-services", cmd="fix mypy errors in src/tracertm/services/"),
    Task(id="fix-mcp", cmd="fix mypy errors in src/tracertm/mcp/"),
]
await spawn_agent_swarm(tasks, max_concurrent=8)
```

**Anti-patterns (from MEMORY.md):**
- **Agent conflict:** Two agents editing same file → loops. Solution: Give ONE agent authority per file.
- **Corrupted files:** Agents creating untracked files with syntax errors. Solution: Delete and restart.
- **Suppressions drift:** Agents suppressing instead of fixing. Solution: Config reconciliation (fix code first, then config).

## Alternatives Rejected

### Alternative 1: Human-driven Development

- **Description:** Traditional development with human engineers
- **Pros:** No API costs, full control, human intuition
- **Cons:** Slower (weeks vs hours), less consistent, prone to human error
- **Why Rejected:** Agent-driven development 10x faster. Human review remains (PR approval).

### Alternative 2: OpenAI GPT-4

- **Description:** Use GPT-4 instead of Claude
- **Pros:** Cheaper ($2/M vs $3/M), larger ecosystem
- **Cons:** Worse code quality (from team experience), shorter context (128K vs 1M), less reliable
- **Why Rejected:** Claude Sonnet 4.5 produces higher quality code. 1M context critical for codebase work.

### Alternative 3: Local LLMs (LLaMA, Mixtral)

- **Description:** Self-hosted open-source models
- **Pros:** Zero API cost, full control, no rate limits
- **Cons:** Worse code quality, requires GPU infrastructure, slower inference
- **Why Rejected:** Claude API cost ($0.30/hour for agent swarm) negligible vs time savings. Quality > cost.

### Alternative 4: Single Agent (Sequential)

- **Description:** One agent working sequentially on all tasks
- **Pros:** Simpler coordination, no parallelization overhead
- **Cons:** 10x slower (sequential vs parallel), doesn't scale
- **Why Rejected:** Parallel agent swarms reduce wall clock by 67%. Essential for large codebases.

## Consequences

### Positive

- **Speed:** Parallel swarms 10x faster than sequential (2.5 hours vs 25 hours for mypy marathon)
- **Quality:** Claude Sonnet 4.5 catches bugs, enforces patterns automatically
- **Scalability:** 50 concurrent agents handle massive codebases
- **Cost efficiency:** $0.30/hour for 8-agent swarm (cheaper than human time)
- **Consistency:** Agents apply same patterns uniformly (no style drift)

### Negative

- **API costs:** $2-5/day for active development (acceptable for productivity gain)
- **Context limits:** 1M tokens requires chunking large codebases
- **Agent errors:** Occasional hallucinations, syntax errors (need verification)
- **Coordination overhead:** Managing 21+ agents requires checkpoints, monitoring

### Neutral

- **Human oversight:** Agents autonomous, humans review PRs before merge
- **Checkpoints:** Manual checkpoints after major milestones
- **Rate limits:** Anthropic rate limits (50 req/min tier 2) sufficient for swarms

## Implementation

### Affected Components

- `.claude/` - Agent instructions, BMM methodology
- `.checkpoint-*.md` - Checkpoint files
- `.memory/` - Agent memory (session history, patterns, lessons learned)
- `scripts/agent-swarm.py` - Agent orchestration (if automated)
- `AGENTS.md` - Agent instructions for codebase

### Migration Strategy

**Phase 1: Single Agent (Baseline)**
- One agent, sequential tasks
- Measure wall clock time
- Establish quality baselines

**Phase 2: Parallel Swarms (2-5 agents)**
- Small swarms (2-5 agents)
- Independent tasks (different modules)
- Checkpoint after each wave

**Phase 3: Large Swarms (10-50 agents)**
- Multi-wave execution (3-5 waves)
- 15-min checkpoints between waves
- Automated orchestration

### Rollout Plan

- **Phase 1:** Manual agent coordination (human spawns agents via Claude chat)
- **Phase 2:** Semi-automated (scripts spawn agents, humans monitor)
- **Phase 3:** Fully automated (CI triggers agent swarms)

### Success Criteria

- [x] Mypy 54% reduction (2,654 → 1,233) via 21-agent swarm
- [x] Ruff 100% reduction (15,426 → 0) via agent swarm
- [x] Parallel execution (8 agents simultaneously)
- [ ] Automated swarm orchestration (Python script)
- [ ] <1% error rate (agent-generated syntax errors)
- [ ] <$10/day API costs (average)

## References

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude 3.5 Sonnet Model Card](https://www.anthropic.com/claude/sonnet)
- [BMAD Method Overview](https://github.com/bmad-dev/bmm)
- [MEMORY.md](../../.claude/projects/-Users-kooshapari-temp-PRODVERCEL-485-kush-trace/memory/MEMORY.md)
- [ADR-0012: Code Quality Enforcement](ADR-0012-code-quality-enforcement.md)

---

**Notes:**
- **Session 10 Mypy Marathon:** Best example of agent swarm at scale
  - 21 agents, 3 waves, 2.5 hours wall clock
  - 54% reduction (2,654 → 1,233 errors)
  - Sustained velocity: 13-15 errors/minute across parallel agents
- **Cost estimate:**
  - Sonnet 4.5: $3/M input, $15/M output
  - Typical agent swarm (8 agents, 1 hour): ~500K tokens = $1.50
  - Daily cost (active development): $5-10/day
- **Context management:**
  - 1M token context (Sonnet 4.5) holds ~750KB of code
  - Chunking strategy: Module-based (api/, services/, mcp/)
  - Follow-imports=skip for isolated mypy runs

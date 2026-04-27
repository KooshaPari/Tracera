# Phenotype Perpetual DAG Loop

Continue all remaining Phenotype organization work from the current live state.

## Scope

- Work from `/Users/kooshapari/CodeProjects/Phenotype/repos`.
- Treat each child repo as its own project. Do not treat the shelf root as one
  product repo.
- Prefer live truth: `git status`, repo docs, GitHub PR/issue state, local tests,
  CI logs, and current manifests.
- Preserve existing dirty work. Never reset or revert unrelated changes.
- Use focused validation before claiming completion.

## Priorities

1. Resume unfinished or blocked work already visible in current sessions,
   `.ralph-controller/.ralph/*`, org-audit docs, and active repo statuses.
2. Audit for more useful DAG work across GitHub projects and local repos.
3. Prefer small safe PR merges, stale PR closures, failing CI repairs, warning/error
   eradication, release verification, worklog/governance gaps, and real build/test
   blockers.
4. Use Codex/Spark-style subagents heavily where available for parallel discovery
   and narrow implementation.
5. Add the `agent-imessage` async communication-layer work to the DAG:
   structured message envelopes, sender/session/task/project metadata, A1/A2/A3
   elicitation schemas, sender-side echo deletion lifecycle, async receipts and
   response correlation, Codex experimental hook integration, and stop-hook
   performance hardening.

## Pause Contract

- Before starting any new substantive task, check whether
  `/Users/kooshapari/CodeProjects/Phenotype/repos/.ralph-controller/STOP` exists.
- If the local time is at or after 04:30 MST, permanently pause: append a concise
  summary to `.ralph-controller/.ralph/progress.md`, notify Koosha through
  `agent-imessage notify`, and stop.
- Do not output `PHENOTYPE_DAG_COMPLETE` unless there is truly no useful remaining
  org work.

## Completion Signal

Only when the whole DAG is genuinely complete, output:

PHENOTYPE_DAG_COMPLETE

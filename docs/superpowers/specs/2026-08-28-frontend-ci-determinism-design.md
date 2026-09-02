# Frontend CI Determinism Design

## Context

Tracera PR #1000 is blocked at commit `8aa2eeb04c833d1901fcbb6cdf18b7d9d49b9157`.
Both hosted Frontend contract checks reached the 15-minute job limit inside
`npm run test:unit`. Local qualification collected 222 test files and exposed
three execution failures before ordinary assertion repair can be trusted:

- WorkerPool drops active-task messages and leaks task timers.
- Fake timers are not reliably restored, so later tests can inherit a frozen
  clock.
- The default Vitest configuration enables the UI and verbose, JSON, and HTML
  reporters for a suite with thousands of assertions, amplifying failures and
  retaining workers in some shards.

The same audit also found import/collection failures, missing browser-runtime
doubles, stale route/auth/readiness fixtures, and assertions targeting restored
historical UI contracts rather than current components.

## Goal

Produce a deterministic frontend test gate that always terminates, reports
actionable failures compactly, and can then be driven to full green without
deleting, excluding, or weakening tests.

## Non-goals

- Do not change the CSRF compatibility design or the dirty preflight work.
- Do not raise CI timeouts or memory limits to mask deterministic defects.
- Do not delete test files, add broad exclusions, or convert failures to
  allowed failures.
- Do not redesign the frontend or add product features.
- Do not clean, reset, prune, or remove any existing branch or worktree.

## Architecture

The repair is a four-stage stabilization train. Each stage is independently
committable and must preserve the evidence needed by the next stage.

### Stage A: deterministic runner

Provide an explicit non-interactive CI command. CI disables the Vitest UI and
uses a compact terminal reporter. Machine-readable output, when required, has
one unique output path per invocation. Local interactive defaults remain
available through a separate developer command.

The frontend workflow calls the explicit CI command. A failing suite must exit
non-zero promptly and a passing suite must exit zero without retained workers.

### Stage B: lifecycle correctness

WorkerPool owns two explicit collections:

- queued tasks that have not been assigned;
- active tasks keyed by task identifier, including their worker and timeout.

Assignment moves a task from queued to active. Progress reads the active map.
Success, worker error, postMessage failure, timeout, termination, and restart
all settle a task at most once and clear its timeout. Worker replacement must
replace one slot without inserting a duplicate worker instance.

Every fake-timer suite restores real timers from unconditional teardown.
User-event interactions under fake timers use an `advanceTimers` adapter, and
React state changes caused by clock advancement occur inside `act`.

### Stage C: collection and environment blockers

Repair invalid case-sensitive imports, undefined suite names, empty test files,
and mixed-runner imports. Install bounded test doubles for browser facilities
only where the production boundary requires them, including IndexedDB, Cache
Storage, canvas/WebGL, clipboard, and WebSocket lifecycle behavior.

Collection success means every included file either contains collected tests or
is intentionally reclassified outside the test naming convention with a
documented reason. It does not mean skipping a broken suite.

### Stage D: current-contract harnesses

Fixtures mock the dependency consumed by current production code. Router tests
seed explicit authenticated and backend-online states. API tests replace fetch
before singleton client construction or inject a stable delegating fetch.
Assertions target current user-visible behavior and accessible roles rather
than obsolete implementation details.

Ordinary assertion drift is repaired only after Stages A-C prove the runner and
harness can distinguish a product regression from test contamination.

## Execution and evidence flow

```text
Focused red test
    -> minimal implementation
    -> focused green test with leak detection
    -> affected shard
    -> all 16 shards
    -> full frontend unit command in CI mode
    -> parity and accessibility commands
    -> hosted Frontend contract checks
    -> required review and protected merge
```

Every bounded commit records the command, exit code, test counts, and whether
the process terminated without retained Vitest or worker processes.

## Error handling

- A task result for an unknown WorkerPool identifier is ignored only after
  confirming the task has already settled; it must not hide an active task.
- Every settlement path clears its timer before resolving or rejecting.
- Test teardown restores global clocks and browser doubles even when the test
  fails or times out.
- A shard that finishes assertions but retains a process is a gate failure.
- A zero-test or import-failed file is a collection failure, not a pass.
- Hosted cancellation, timeout, or skipped downstream steps remains NO-GO.

## Test strategy

1. Add focused WorkerPool tests that fail on the current active-task lookup,
   timer leak, and duplicate-restart behavior.
2. Reproduce each fake-timer hang with a short test timeout, then prove normal
   exit after repair.
3. Add a runner-contract check that verifies CI mode disables UI and selects
   the compact reporter without weakening include/exclude rules.
4. Repair collection blockers and verify `vitest list` returns 222 collectable
   files with no import or zero-test failures during execution.
5. Run deterministic 16-way shards and require all shards to exit normally.
6. Run the full unit, parity, accessibility, typecheck, and build gates.
7. Require hosted green checks and a review of the final immutable SHA.

## Commit boundaries

1. `fix(frontend): make vitest CI execution deterministic`
2. `fix(frontend): settle worker pool tasks exactly once`
3. `test(frontend): isolate fake timers and async resources`
4. `test(frontend): restore complete test collection`
5. Subsequent harness repairs grouped by one shared boundary per commit.

The branch starts from PR #1000 head. After local qualification, commits are
fast-forwarded onto the PR branch only if its remote head is still an ancestor;
otherwise the branch is rebased or reconciled preserve-first without force
push.

## Acceptance criteria

- No included test is deleted, excluded, or weakened to manufacture green.
- Focused WorkerPool and timer regressions pass with zero async leaks.
- All 222 included files collect and execute without import failures or empty
  suites. (221 genuine tests plus the newly added config contract, after
  reclassifying two non-test files: the AuthToken marker and the production
  route collision.)
- All 16 shards pass and terminate.
- Full `test:unit`, parity, accessibility, typecheck, and build gates pass.
- Both hosted Frontend contract checks pass on the same immutable SHA.
- PR #1000 receives required review and merges through protected flow.
- Post-merge qualification on `main` reproduces the same green gates.

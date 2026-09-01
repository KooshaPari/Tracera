# Frontend CI Termination Kernel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Tracera frontend unit-test command deterministic and bounded by repairing WorkerPool task settlement, removing interactive/report-generation defaults from CI, and preventing fake-timer state from escaping its owning test.

**Architecture:** Keep queued and active WorkerPool tasks in separate collections and centralize release/settlement so every terminal path clears its timeout exactly once. Make the default/CI Vitest profile non-interactive with one streaming reporter, while exposing UI mode as an explicit developer command. Repair only timer-lifecycle defects proven to contaminate later tests; stale feature-contract assertions remain a separate follow-up plan.

**Tech Stack:** TypeScript, React, Vitest 3, Testing Library, Bun, GitHub Actions.

---

## Scope and hard gates

- Work only in `fix/tracera-1000-frontend-ci-determinism-20260828`, based on PR #1000 head `8aa2eeb04c833d1901fcbb6cdf18b7d9d49b9157`.
- Do not touch the dirty `pr999-audit-remediation-20260828` preflight files or any other checkout.
- A nonzero assertion result is allowed during termination qualification; a process that remains alive after Vitest's final file result is not.
- Do not call PR #1000 green after this plan. Collection failures and stale contracts are explicitly downstream.
- Every red test must fail for the named reason before production code changes; every green test must be rerun after the change.

## Task 1: Make the CI runner non-interactive and single-reporter

**Files:**

- Create: `frontend/apps/web/src/__tests__/config/vitest-execution-profile.test.ts`
- Modify: `frontend/apps/web/vitest.config.ts:39-46`
- Modify: `frontend/apps/web/package.json` (`scripts.test` block)
- Modify: `frontend/package.json` (`scripts.test:unit`)

- [ ] Add a red runner-contract test that imports `../../../vitest.config` and reads `../../../package.json`:

```ts
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

import config from '../../../vitest.config';

describe('Vitest execution profile', () => {
  it('uses a bounded non-interactive default profile', () => {
    const resolved = typeof config === 'function' ? config({ command: 'serve', mode: 'test' }) : config;
    expect(resolved.test?.reporters).toEqual(['dot']);
    expect(resolved.test?.ui).toBe(false);
  });

  it('separates CI, watch, and UI commands', () => {
    const packageJson = JSON.parse(
      readFileSync(new URL('../../../package.json', import.meta.url), 'utf8'),
    );
    expect(packageJson.scripts.test).toBe('vitest run --reporter=dot --no-ui');
    expect(packageJson.scripts['test:watch']).toBe('vitest --reporter=dot --no-ui');
    expect(packageJson.scripts['test:ui']).toBe('vitest --ui --reporter=verbose');
  });
});
```

- [ ] Run the focused test and verify it fails because `reporters` is verbose/JSON/HTML, `ui` is true, and the scripts do not exist:

```bash
cd frontend/apps/web
bun x vitest run src/__tests__/config/vitest-execution-profile.test.ts --reporter=dot --no-ui
```

- [ ] Replace the default reporter/UI fields in `vitest.config.ts`:

```ts
reporters: ['dot'],
ui: false,
```

- [ ] Set explicit web scripts:

```json
"test": "vitest run --reporter=dot --no-ui",
"test:watch": "vitest --reporter=dot --no-ui",
"test:ui": "vitest --ui --reporter=verbose"
```

- [ ] Change the frontend root command to execute that bounded script directly:

```json
"test:unit": "npm --prefix apps/web test --"
```

`bun --cwd apps/web run test` is deliberately not used: Bun 1.3.11 prints
command usage and exits zero without running the script. The contract test must
assert the executable form above so CI cannot silently false-green. Nested
`bun run` is also excluded because it executes Vitest under Bun; jsdom's
`os.cpus()` then recursively re-enters `navigator.hardwareConcurrency`. Routing
through npm keeps Vitest on Node, matching the passing direct invocation.

- [ ] Keep the GitHub Actions unit-test step on `npm run test:unit`, retaining `working-directory: frontend`; Bun remains the dependency installer and build tool.
- [ ] Rerun the focused contract test and require green.
- [ ] Run `bun x tsc --noEmit --pretty false -p tsconfig.json` from `frontend/apps/web` and require no new type error in the test/config files.
- [ ] Commit:

```bash
git add frontend/apps/web/src/__tests__/config/vitest-execution-profile.test.ts \
  frontend/apps/web/vitest.config.ts frontend/apps/web/package.json \
  frontend/package.json
git commit -m "fix(frontend): bound vitest execution profile"
```

## Task 2: Track active WorkerPool tasks and settle results/progress/errors

**Files:**

- Modify: `frontend/apps/web/src/__tests__/workers/WorkerPool.edgecases.test.ts:52-291`
- Modify: `frontend/apps/web/src/workers/worker-pool.ts:55-297`

- [ ] Strengthen `afterEach` so a failed fake-timer test cannot contaminate the next test:

```ts
afterEach(() => {
  pool?.terminate();
  vi.useRealTimers();
});
```

- [ ] Add assertions to the existing result, progress, error-message, and worker-error tests so each terminal path ends with `busyWorkers: 0` and `queuedTasks: 0`.
- [ ] Run those focused tests with Vitest's 10-second per-test deadline and capture the expected pre-fix timeout:

```bash
cd frontend/apps/web
bun x vitest run src/__tests__/workers/WorkerPool.edgecases.test.ts \
  -t 'continue processing|forward progress|worker sends error|restart worker on error' \
  --reporter=dot --no-ui --testTimeout=10000
```

- [ ] Add `private activeTasks = new Map<string, WorkerTask>();` beside `taskQueue`.
- [ ] In `assignTaskToWorker`, insert the task into `activeTasks` before calling `postMessage`.
- [ ] Add a single release helper that removes the active task, clears the worker timeout, and makes the worker idle:

```ts
private releaseWorkerTask(workerInstance: WorkerInstance): WorkerTask | undefined {
  const taskId = workerInstance.currentTaskId;
  const task = taskId ? this.activeTasks.get(taskId) : undefined;
  if (taskId) this.activeTasks.delete(taskId);
  if (workerInstance.timeoutId) clearTimeout(workerInstance.timeoutId);
  workerInstance.timeoutId = undefined;
  workerInstance.busy = false;
  workerInstance.currentTaskId = undefined;
  workerInstance.lastUsed = Date.now();
  return task;
}
```

- [ ] Make `findTaskById` read `activeTasks` only. Assigned tasks must never be rediscovered through `taskQueue`.
- [ ] In the synchronous `postMessage` catch, call `releaseWorkerTask`, reject that returned task, then process the queue.
- [ ] In `handleWorkerMessage`, reject mismatched/late message IDs by returning without mutation. For `progress`, invoke the callback without clearing the timeout. For `result` and `error`, release first, settle the returned task once, and process the queue.
- [ ] In `handleWorkerError`, release and reject the active task before restarting the worker.
- [ ] Rerun the focused tests with `--testTimeout=10000` and require green with normal process exit.
- [ ] Run the complete edge-case file and require green with normal process exit.
- [ ] Commit:

```bash
git add frontend/apps/web/src/workers/worker-pool.ts \
  frontend/apps/web/src/__tests__/workers/WorkerPool.edgecases.test.ts
git commit -m "fix(frontend): settle active worker tasks"
```

## Task 3: Make WorkerPool timeout, restart, and termination exact

**Files:**

- Modify: `frontend/apps/web/src/__tests__/workers/WorkerPool.edgecases.test.ts`
- Modify: `frontend/apps/web/src/workers/worker-pool.ts:124-145,208-229,244-260,318-330`

- [ ] Add a timeout/replacement test using a nonresponding worker and fake timers:

```ts
it('replaces a timed-out worker without duplicating the pool entry', async () => {
  vi.useFakeTimers();
  const workerFactory = vi.fn(() => {
    const worker = new EventDrivenMockWorker();
    worker.postMessage = () => {};
    return worker as unknown as Worker;
  });
  pool = new WorkerPool({ maxWorkers: 1, minWorkers: 1, taskTimeout: 25, workerFactory });
  const pending = pool.executeTask('blocked', {});
  const rejection = expect(pending).rejects.toThrow('Task timeout after 25ms');
  await vi.advanceTimersByTimeAsync(25);
  await rejection;
  expect(workerFactory).toHaveBeenCalledTimes(2);
  expect(pool.getStats()).toMatchObject({ busyWorkers: 0, totalWorkers: 1 });
});
```

- [ ] Add a termination test that proves an active promise rejects and all owned timers are cleared:

```ts
it('rejects active work and clears owned timers on terminate', async () => {
  vi.useFakeTimers();
  pool = new WorkerPool({
    maxWorkers: 1,
    minWorkers: 1,
    workerFactory: () => {
      const worker = new EventDrivenMockWorker();
      worker.postMessage = () => {};
      return worker as unknown as Worker;
    },
  });
  const pending = pool.executeTask('blocked', {});
  pool.terminate();
  await expect(pending).rejects.toThrow('Worker pool terminated');
  expect(vi.getTimerCount()).toBe(0);
});
```

- [ ] Run both tests and verify the current code fails by duplicating the replacement and leaving the active promise/timer unsettled.
- [ ] Split construction from insertion: `buildWorker()` creates/listens and returns an instance; `createWorker()` calls it and pushes once.
- [ ] Change `restartWorker` to terminate the old worker and replace it in place with `this.buildWorker()`; never call the push-owning method from replacement.
- [ ] Change `handleTaskTimeout` to release the currently active task, reject only when it still matches, then restart.
- [ ] Change `terminate` to reject all queued and active tasks, clear every `timeoutId`, clear both collections, terminate workers, and be idempotent on a second call.
- [ ] Rerun the two new tests and the whole edge-case file; require green and normal exit.
- [ ] Commit:

```bash
git add frontend/apps/web/src/workers/worker-pool.ts \
  frontend/apps/web/src/__tests__/workers/WorkerPool.edgecases.test.ts
git commit -m "fix(frontend): bound worker restart and shutdown"
```

## Task 4: Repair the reproduced link-sharing fake-timer deadlock

**Files:**

- Modify: `frontend/apps/web/src/__tests__/features/link-sharing-and-specs.test.tsx:6-11`
- Modify: the link-copy timeout test near its `vi.useFakeTimers()` call

- [ ] Add `act` and `afterEach` imports and unconditional timer restoration:

```ts
import { act, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

afterEach(() => {
  vi.useRealTimers();
});
```

- [ ] Configure `userEvent` to advance fake timers and advance the component timeout inside `act`:

```ts
const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
await user.click(screen.getByRole('button', { name: 'Copy link' }));
await act(async () => {
  await vi.advanceTimersByTimeAsync(2000);
});
expect(screen.getByRole('button', { name: 'Copy link' })).toBeInTheDocument();
```

- [ ] First run the focused test before the edit with `--testTimeout=10000` and verify the existing await times out; then run after the edit and require green.
- [ ] Run the complete link-sharing file and require green with normal exit.
- [ ] Commit:

```bash
git add frontend/apps/web/src/__tests__/features/link-sharing-and-specs.test.tsx
git commit -m "test(frontend): bound link-sharing fake timers"
```

## Task 5: Contain remaining reproduced fake-timer ownership leaks

**Files:**

- Modify: `frontend/apps/web/src/__tests__/pages/ProjectsList.test.tsx` (top-level cleanup and debounce test)
- Modify: `frontend/apps/web/src/__tests__/components/graph/ErrorRecovery.test.tsx:185-227`

- [ ] Add `vi.useRealTimers()` to every `afterEach` belonging to a scope that calls `vi.useFakeTimers()`.
- [ ] In the ProjectsList debounce test, use `userEvent.setup({ advanceTimers: vi.advanceTimersByTime })`; do not rewrite its stale router/auth/API contract in this plan.
- [ ] In both `RecoveryProgress` and `useAutoRecovery`, restore real timers before `vi.restoreAllMocks()`.
- [ ] Add a small containment regression after each fake-timer describe that calls `expect(vi.isFakeTimers()).toBe(false)` from a real-timer test scope.
- [ ] Run the affected files separately with `--reporter=dot --no-ui`. Record ProjectsList assertion failures as downstream contract work, but require each command to exit without manual intervention.
- [ ] Commit:

```bash
git add frontend/apps/web/src/__tests__/pages/ProjectsList.test.tsx \
  frontend/apps/web/src/__tests__/components/graph/ErrorRecovery.test.tsx
git commit -m "test(frontend): contain fake timer lifecycles"
```

## Task 6: Prove termination independently of assertion correctness

**Files:**

- Create: `frontend/scripts/verify-vitest-termination.mjs`
- Modify: `frontend/package.json`

- [ ] Add a Node supervisor that spawns `bun --cwd apps/web run test`, forwards output, sends `SIGTERM` at 14 minutes, escalates to `SIGKILL` after 10 seconds, and exits with a distinct code `124` only for the deadline. Preserve the child test exit code otherwise.
- [ ] Add `"test:unit:bounded": "node scripts/verify-vitest-termination.mjs"`.
- [ ] Test the supervisor itself with an injectable command/deadline: one fixture exits 0, one exits 1, and one hangs until it is terminated. Do not rely on GNU `timeout`, which is absent on stock macOS.
- [ ] Run the previously nonterminating shards 3, 5, 8, and 11 using the supervisor's command override. Require: no deadline exit `124`, no retained reporter process, no manual kill. Assertion failures remain reported verbatim.
- [ ] Run all 16 deterministic shards sequentially with the bounded dot profile and persist counts in the PR evidence comment. Require every shard to exit by itself.
- [ ] Commit:

```bash
git add frontend/scripts/verify-vitest-termination.mjs frontend/package.json \
  frontend/scripts/__tests__/verify-vitest-termination.test.mjs
git commit -m "test(frontend): enforce vitest termination deadline"
```

## Task 7: Quality and integration gates

- [ ] Run focused WorkerPool, link-sharing, ErrorRecovery, runner-profile, and supervisor tests together; require green.
- [ ] Run frontend format check on changed files and fix only plan-owned files.
- [ ] Run the frontend workspace typecheck and separate baseline failures from introduced failures using the PR #1000 head as the control.
- [ ] Run `bun run test:unit:bounded`. Expected state after this plan: bounded normal exit, potentially nonzero due to already inventoried collection/stale-contract failures; never relabel nonzero as green.
- [ ] Inspect `git diff 8aa2eeb04...HEAD`, `git status --short`, and every commit. Verify no generated `test-results`, `tsbuildinfo`, cache, or unrelated preflight file is included.
- [ ] Push only the bounded repair branch and open/update one PR targeting PR #1000's integration branch. Do not push local main.
- [ ] Post machine evidence: head SHA, exact commands, durations, exit codes, shard counts, and hosted check URLs.
- [ ] Gate the next plan on this invariant:

```text
CI/default command is non-interactive
AND each task promise has exactly one terminal path
AND all owned timers are cleared
AND all 16 shards exit without operator intervention
```

## Downstream DAG (not implemented by this plan)

```text
termination kernel
  |
  +--> collection/import repair
  |      +--> case-correct WorkerPool import
  |      +--> MCP/Bun/visual/uiStore/WebGL collection blockers
  |
  +--> stale contract repair
         +--> ProjectsList auth/router/useProjects harness
         +--> API/component contract updates by feature cluster
                |
                +--> all assertions green
                       +--> full strict frontend quality
                              +--> hosted PR checks green
                                     +--> review + merge
```

# Tracera CLI Rich Gateway Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Make the installed JavaScript `tracera` REST client reach the canonical rich gateway at `http://127.0.0.1:18000` by default, while preserving existing explicit override precedence and the separately opt-in legacy Rust bundle behavior.

**Architecture:** The rich Tracera server serves its API and static frontend on loopback port 18000. The JavaScript REST client resolves its endpoint from a CLI flag, environment variable, user config, then a default; only that final default and its sample configuration are stale. The Rust bundle's 18081 behavior stays unchanged because desktop code gates it behind `TRACERA_ALLOW_LEGACY_BUNDLE=1`.

**Tech Stack:** Node.js built-ins (`node:test`, `child_process`), JavaScript CommonJS CLI, JSON configuration, Bun/Node static checks.

---

## Root-cause evidence

- Canonical rich gateway: `docker-compose.yml:33-36`, `scripts/rich-oracle-smoke.py:21,58-59`, and `frontend/apps/desktop/src/target.ts:7-29` use loopback port 18000.
- Stale REST-client contract: `bin/tracera:8-12,36-67` sets `DEFAULT_API_BASE` to `http://localhost:8080`; `bin/tracera-config.example.json:2-4` repeats it; `bin/tracera-attach:83-103` installs that template.
- Legacy distinction: `crates/tracera-cli/src/bundle.rs:71-124` still uses 18081, while `frontend/apps/desktop/src/index.ts:13-41` makes that bundle explicit legacy-only. Do not change this Rust behavior in this repair.
- Reproduction on a clean temporary HOME: `HOME=/tmp/tracera-cli-nonexistent-home node bin/tracera config` prints `http://localhost:8080` before the change.

### Task 1: Add a black-box failing endpoint-contract test

**Files:**

- Create: `tests/test_tracera_rest_cli_endpoint.cjs`
- Test: `tests/test_tracera_rest_cli_endpoint.cjs`

- [ ] **Step 1: Write the failing test**

```js
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { mkdtempSync, mkdirSync, rmSync, writeFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join } = require('node:path');
const test = require('node:test');

const repoRoot = join(__dirname, '..');
const cli = join(repoRoot, 'bin', 'tracera');

function config(env) {
  return JSON.parse(execFileSync(process.execPath, [cli, 'config'], {
    cwd: repoRoot,
    encoding: 'utf8',
    env: { ...process.env, ...env },
  }));
}

test('uses the rich loopback gateway by default', () => {
  const home = mkdtempSync(join(tmpdir(), 'tracera-cli-default-'));
  try {
    const result = config({ HOME: home, TRACERA_API_BASE: '' });
    assert.equal(result.apiBase, 'http://127.0.0.1:18000');
    assert.equal(result.source, 'default');
  } finally {
    rmSync(home, { recursive: true, force: true });
  }
});

test('keeps flag, environment, and file precedence', () => {
  const home = mkdtempSync(join(tmpdir(), 'tracera-cli-precedence-'));
  try {
    mkdirSync(join(home, '.tracera'));
    writeFileSync(join(home, '.tracera', 'config.json'), JSON.stringify({
      apiBase: 'http://127.0.0.1:19000',
    }));
    assert.equal(config({ HOME: home, TRACERA_API_BASE: 'http://127.0.0.1:19001' }).apiBase,
      'http://127.0.0.1:19001');
    const result = JSON.parse(execFileSync(process.execPath, [cli, 'config', '--api-base',
      'http://127.0.0.1:19002'], {
      cwd: repoRoot,
      encoding: 'utf8',
      env: { ...process.env, HOME: home, TRACERA_API_BASE: 'http://127.0.0.1:19001' },
    }));
    assert.equal(result.apiBase, 'http://127.0.0.1:19002');
    assert.equal(result.source, 'flag');
  } finally {
    rmSync(home, { recursive: true, force: true });
  }
});
```

- [ ] **Step 2: Verify the RED state**

Run: `node --test tests/test_tracera_rest_cli_endpoint.cjs`

Expected: the first test fails because the current CLI returns `http://localhost:8080`; the precedence test passes or fails only if the existing parser contradicts its documented order.

- [ ] **Step 3: Commit the test-only RED state**

```sh
git add tests/test_tracera_rest_cli_endpoint.cjs
git commit -m "test: define Tracera REST CLI rich gateway default"
```

### Task 2: Repair the REST client default and installation template

**Files:**

- Modify: `bin/tracera:8-12,36-67`
- Modify: `bin/tracera-config.example.json:1-8`
- Test: `tests/test_tracera_rest_cli_endpoint.cjs`

- [ ] **Step 1: Apply the minimum implementation**

Replace only the stale REST default and its user-facing description:

```js
const DEFAULT_API_BASE = 'http://127.0.0.1:18000';
```

```json
{
  "_comment_": "Tracera personal dogfooding config. Edit apiBase to point at your running Tracera rich gateway (default: loopback :18000).",
  "apiBase": "http://127.0.0.1:18000"
}
```

Do not reorder `loadConfig` branches: flag must still beat environment, environment must still beat file, and file must still beat the default. Do not alter Rust `BundleLayout`, desktop legacy gating, or listener/process configuration.

- [ ] **Step 2: Verify GREEN**

Run: `node --test tests/test_tracera_rest_cli_endpoint.cjs`

Expected: 2 passing tests; the default test proves `18000`, and the precedence test proves no override regression.

- [ ] **Step 3: Run targeted regression checks**

Run:

```sh
node --check bin/tracera
python3 -m json.tool bin/tracera-config.example.json >/dev/null
python3 scripts/rich-oracle-smoke.py --json
python3 scripts/test-oracle-compose.py
```

Expected: syntax and JSON validation pass; rich oracle emits valid JSON; compose oracle reports loopback-only publications.

- [ ] **Step 4: Commit the implementation**

```sh
git add bin/tracera bin/tracera-config.example.json tests/test_tracera_rest_cli_endpoint.cjs
git commit -m "fix(cli): default REST client to rich gateway"
```

### Task 3: Validate installed-contract scope and review

**Files:**

- Review: `bin/tracera-attach:83-103`
- Review: `frontend/apps/desktop/src/target.ts:7-29`
- Review: `crates/tracera-cli/src/bundle.rs:71-124`

- [ ] **Step 1: Verify installer/template alignment**

Run: `rg -n 'localhost:8080|127\.0\.0\.1:18000' bin/tracera bin/tracera-config.example.json bin/tracera-attach`

Expected: no stale `localhost:8080` REST default remains; the attach script continues to install the repaired template rather than an independent default.

- [ ] **Step 2: Verify the legacy boundary did not change**

Run: `rg -n '18081|TRACERA_ALLOW_LEGACY_BUNDLE|18000' crates/tracera-cli/src/bundle.rs frontend/apps/desktop/src/{target.ts,index.ts}`

Expected: 18081 remains documented only in bundle/explicit legacy code; rich desktop default remains 18000.

- [ ] **Step 3: Spec-compliance review**

Review against this plan: only REST client default/template/test changed; override precedence retained; no bundle port rewrite; all Task 2 commands passed.

- [ ] **Step 4: Code-quality review**

Review test cleanup, process environment isolation, CommonJS style, exact URLs, and absence of external dependencies.

- [ ] **Step 5: Publish for hosted review only after both approvals**

Run: `git diff --check origin/main...HEAD` and inspect the exact changed-file list. Push the isolated branch and open one draft PR against `main` only if the range remains limited to the three planned files and the source branch is current. Hosted CI, review, merged-main evidence, and explicit default-CLI dogfood on port 18000 remain separate promotion gates.

## Plan self-review

- Spec coverage: Tasks 1-2 fix and prove the stale JS default/template; Task 3 proves legacy separation and applies independent reviews.
- Completeness scan: inspect this document for unresolved-work markers; expected no matches.
- Interface consistency: both tests invoke the same `bin/tracera config` boundary used by the installed REST client; implementation changes only `DEFAULT_API_BASE` and the shipped template.

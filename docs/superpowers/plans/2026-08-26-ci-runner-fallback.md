# CI Runner Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make default Tracera CI and Infisical synchronization runnable on GitHub-hosted runners while retaining an explicit Blacksmith override.

**Architecture:** Workflow dispatch inputs select a runner label; non-dispatch events default to `ubuntu-latest` through the allowed `inputs` context in `runs-on`. Existing language job graph and security boundaries remain unchanged. A static Node contract test prevents regression to hard-coded unavailable runners.

**Tech Stack:** GitHub Actions YAML, Node.js ESM contract test, actionlint.

---

### Task 1: Add the workflow runner selector contract test

**Files:**

- Create: `scripts/test-ci-runner-selection.mjs`

- [ ] **Step 1: Write the failing test**

Create a Node script that reads `.github/workflows/ci.yml` and `.github/workflows/infisical.yml`, checks the dispatch input choices/default, checks the `${{ inputs.runner || 'ubuntu-latest' }}` selector, and fails if a language or Infisical job still hard-codes `blacksmith-`.

- [ ] **Step 2: Run it to verify it fails**

Run: `node scripts/test-ci-runner-selection.mjs`

Expected: FAIL because the current workflows hard-code Blacksmith labels and have no runner input.

### Task 2: Make CI runner-selectable

**Files:**

- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Add the dispatch input**

Under `workflow_dispatch`, add `inputs.runner` with choices `ubuntu-latest`, `blacksmith-2vcpu-ubuntu-2204`, and `blacksmith-4vcpu-ubuntu-2204`, defaulting to `ubuntu-latest`.

- [ ] **Step 2: Replace language job labels**

Use `${{ inputs.runner || 'ubuntu-latest' }}` for `rust-lint`, `rust-test`, `rust-build`, `python-lint`, `python-test`, `go-lint`, `go-test`, `typescript-lint`, and `typescript-test`. Leave existing `ubuntu-latest` security, aggregation, and detection jobs unchanged.

### Task 3: Make Infisical runner-selectable

**Files:**

- Modify: `.github/workflows/infisical.yml`

- [ ] **Step 1: Add the dispatch input**

Under `workflow_dispatch`, add the same `runner` choices and `ubuntu-latest` default.

- [ ] **Step 2: Select the runner**

Use `${{ inputs.runner || 'ubuntu-latest' }}` for `sync-secrets` and add `if: github.event_name != 'pull_request'` so PR validation does not fail on intentionally unavailable repository secrets.

### Task 4: Verify and commit

- [ ] **Step 1: Run the contract test**

Run: `node scripts/test-ci-runner-selection.mjs`

Expected: PASS with both workflow contracts validated.

- [ ] **Step 2: Run actionlint**

Run: `actionlint .github/workflows/ci.yml .github/workflows/infisical.yml`

Expected: exit 0.

- [ ] **Step 3: Inspect the diff**

Run: `git diff --check && git diff --stat && git diff -- .github/workflows/ci.yml .github/workflows/infisical.yml scripts/test-ci-runner-selection.mjs`

Expected: only runner selection, dispatch inputs, and the contract test changed.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yml .github/workflows/infisical.yml scripts/test-ci-runner-selection.mjs docs/superpowers/specs/2026-08-26-ci-runner-fallback-design.md docs/superpowers/plans/2026-08-26-ci-runner-fallback.md
git commit -m "fix(ci): fall back to hosted runners when Blacksmith is unavailable"
```

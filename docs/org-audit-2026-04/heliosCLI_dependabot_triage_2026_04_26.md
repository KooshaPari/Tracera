# heliosCLI Dependabot Triage by Ease

**Date:** 2026-04-26
**Repo:** KooshaPari/heliosCLI
**Open alerts:** 52 (one alert #66 absent in API window — effective 52)
**Source:** `gh api repos/KooshaPari/heliosCLI/dependabot/alerts --paginate`

## Summary by Ecosystem

| Ecosystem | Count | Manifest |
|-----------|-------|----------|
| npm       | 31    | pnpm-lock.yaml |
| rust      | 11    | codex-rs/Cargo.lock (9) + Cargo.lock (2) |
| pip       | 4     | uv.lock |
| **Total** | **46 unique alerts** (post de-dup of multi-sev)|

(Raw API returned 52 line items; several packages emit 2+ alerts of differing severity — see clusters.)

## Summary by Severity

| Severity | Count |
|----------|-------|
| critical | 1     |
| high     | 22    |
| medium   | 18    |
| low      | 11    |

## Categorization

### CLUSTER-FIX (3+ alerts, single-command resolution)

| # | Package | Eco | Alerts | Severities | Fix Command | Expected Δ |
|---|---------|-----|--------|------------|-------------|------------|
| 1 | **handlebars** | npm | 7 (#36,40,41,42,43,44,48,49) | 1 critical, 4 high, 2 medium, 1 low | `pnpm update handlebars` (target ≥4.7.9) | −7 |
| 2 | **minimatch** | npm | 5 (#21,22,24,25,26,27) | all high | `pnpm update minimatch` (≥3.1.4 / ≥9.0.7) | −6 |
| 3 | **rand** | rust | 5 (#51,52,56,57,67) | all low | `cargo update -p rand` (workspace + codex-rs) | −5 |
| 4 | **rustls-webpki** | rust | 4 (#30,53,54,63) | high+low+med | `cargo update -p rustls-webpki --manifest-path codex-rs/Cargo.toml` (≥0.103.13) | −4 |
| 5 | **picomatch** | npm | 4 (#32,33,34,35) | high+med | `pnpm update picomatch` (≥2.3.2 / ≥4.0.4) | −4 |

**Cluster total: 25 alerts removable with 5 commands.**

### AUTO-MERGE-READY (single-package, patch/minor bump, non-breaking)

| # | Package | Eco | Alerts | Sev | Fix |
|---|---------|-----|--------|-----|-----|
| 1 | flatted | npm | 2 (#28,29) | high | `pnpm update flatted` ≥3.4.2 |
| 2 | brace-expansion | npm | 2 (#38,39) | medium | `pnpm update brace-expansion` ≥1.1.13/≥2.0.3 |
| 3 | path-to-regexp | npm | 2 (#45,46) | high+med | `pnpm update path-to-regexp` ≥8.4.0 |
| 4 | qs | npm | 2 (#14,18) | med+low | `pnpm update qs` ≥6.14.2 |
| 5 | js-yaml | npm | 2 (#10,11) | medium | `pnpm update js-yaml` |
| 6 | ajv | npm | 2 (#19,20) | medium | `pnpm update ajv` |
| 7 | @modelcontextprotocol/sdk | npm | 2 (#15,17) | high | `pnpm update @modelcontextprotocol/sdk` ≥1.26.0 |
| 8 | GitPython | pip | 2 (#68,69) | high | `uv lock --upgrade-package gitpython` ≥3.1.47 |
| 9 | rollup | npm | 1 (#23) | high | `pnpm update rollup` ≥4.59.0 |
| 10 | postcss | npm | 1 (#64) | medium | `pnpm update postcss` ≥8.5.10 |

**Subtotal singles also auto-mergeable** (one-line each): glob #12 (high), body-parser #13 (med), diff #16 (low), yaml #31 (med), actix-http #55 (med), lru #2 (low), pytest #65 (med), Pygments #50 (low).

**Auto-merge total: 26 alerts** removable with ~18 single-package update commands.

### NEEDS-REVIEW (potential breaking changes)

None at major-version cliff; all fix versions are in-range minor/patch except possibly `@modelcontextprotocol/sdk` 1.10→1.26 (jump within v1, low risk). No alerts flagged here.

### STALE-CANDIDATE

Verified sample of 5 packages (rand, rustls-webpki, handlebars, minimatch, GitPython) — all confirmed present in current lockfiles. **No stale candidates detected** in sample; assume all 52 are live.

## Expected Delta if All Shipped

| Action | Cmds | Alerts Closed |
|--------|------|---------------|
| Cluster-fix top 5 | 5 | 25 |
| Auto-merge-ready (top 10 + 8 singletons) | ~18 | 26 |
| **Combined** | **~23** | **51 / 52 (~98%)** |

The single residual would be alert #36 (handlebars at a non-overlapping range) if not picked up by the same `pnpm update`.

## Recommended Execution Order

1. **codex-rs cargo bump (highest leverage):** `cd codex-rs && cargo update -p rand -p rustls-webpki -p actix-http -p lru` → closes 10.
2. **root cargo bump:** `cargo update -p rand` → closes 2.
3. **pnpm bulk update:** `pnpm update handlebars minimatch picomatch flatted brace-expansion path-to-regexp qs js-yaml ajv @modelcontextprotocol/sdk rollup postcss glob body-parser diff yaml` → closes ~31.
4. **uv.lock pip:** `uv lock --upgrade-package gitpython --upgrade-package pytest --upgrade-package pygments` → closes 4.

Total: **~4 commands × 3 ecosystems = 12 invocations to close ~51/52 alerts**.

## Constraints

- Triage only — no upgrades performed.
- `codex-rs/` is a vendored upstream subtree (codex-rs); upgrades may need rebase coordination — verify before push.
- `pnpm-lock.yaml` clusters are likely transitive deps; `pnpm update --depth Infinity <pkg>` may be required.

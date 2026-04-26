# TIER-2 Dependabot Triage — Ease-of-Fix Categorization

**Date:** 2026-04-26
**Source snapshot:** `docs/governance/dependabot-alert-tier2-snapshot-2026-04-26.md` (121 alerts at snapshot)
**Live re-fetch (this audit):** 119 open alerts across 9 repos (2 alerts likely auto-dismissed since snapshot — Tracera 30→28)
**Method:** `gh api repos/KooshaPari/<repo>/dependabot/alerts?state=open` → JSON → `jq` aggregation in `/tmp/depbot_triage/`.
**Scope:** Triage only. No upgrades, no PRs. Pure GH-API + doc.

---

## Top-level distribution

| Category | Alerts | % | Action class |
|---|---|---|---|
| **AUTO-MERGE-READY** (low/medium with patch fix) | 83 | 69.7% | bump lockfile + dependabot auto-merge |
| **CLUSTER (cross-repo same advisory)** | 80 unique-vs-119 total — clusters covered separately below | — | one fix repos N |
| **NEEDS-REVIEW** (high/critical or major bump) | 24 | 20.2% | manual review — breaking-change risk |
| **STALE-DEP** (manifest in `ARCHIVE/` or `*-legacy/`) | 21 | 17.6% | delete manifest or `dependabot.yml` ignore |
| **NO-FIX-AVAILABLE** | 15 | 12.6% | wait/upstream pin/risk-accept |
| Total | 119 | 100% | |

(Categories overlap; an alert can be both CLUSTER and AUTO-MERGE-READY.)

---

## Severity breakdown (live)

| Severity | Count |
|---|---|
| Critical | 5 (fastmcp ×2, libxmljs2 ×2, docker ×1) |
| High | 19 |
| Medium | 65 |
| Low | 30 |

## Ecosystem breakdown

| Ecosystem | Alerts |
|---|---|
| Rust (cargo) | 39 |
| npm | 36 |
| pip | 29 |
| Go | 15 |

---

## Top 10 CLUSTER-FIXABLE (highest leverage)

Same advisory or same package version-range affecting multiple repos / multiple manifests. Fix once → close N alerts.

| Rank | Package | Eco | Alerts | Repos | Sev | Fix | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `github.com/docker/docker` | go | 14 | DevHex, KDesktopVirt, Tracera | critical/high/med/low | 25.0.6 (one), `< 29.3.1` (rest no-fix) | 8 of 14 are NO-FIX (GHSA-x744 / GHSA-pxq6 — wait or pin); 6 fixable via 25.0.6 bump. Bulk of K**DesktopVirt** & Tracera Go alerts. |
| 2 | `rustls-webpki` | rust | 7 | KDesktopVirt, PhenoRuntime | high/med/low | 0.103.13 | Cargo.lock-only update. Patch bump. |
| 3 | `fastmcp` | pip | 6 | PhenoLang (×2 manifests) | crit/high/med | 3.2.0 | **TWO PhenoLang `uv.lock` manifests carry same vuln.** Single `uv lock --upgrade-package fastmcp` per manifest closes 6. |
| 4 | `rand` | rust | 6 | BytePort, Civis, KDesktopVirt, PhenoLang | low | (varies) | RUSTSEC weak-RNG class; patch bumps. Spans 4 repos. |
| 5 | `lru` | rust | 5 | KDesktopVirt, PhenoLang, PhenoProc, PhenoRuntime | low | patch | `cargo update -p lru` per repo. |
| 6 | `openssl` (rust crate) | rust | 5 | PhenoLang | high/low | 0.10.78 | All five in one Cargo.lock. Single `cargo update` closes 5. |
| 7 | `dompurify` | npm | 4 | PhenoLang (`docs/package-lock.json`) | medium | 3.4.0 | Single manifest, 4 distinct GHSAs. One bump closes all. |
| 8 | `chromedriver` | npm | 4 | Tracera (ARCHIVE) | high/med | 2.25.2 | All four in `ARCHIVE/CONFIG/`. **STALE.** See stale section. |
| 9 | `cryptography` | pip | 4 | PhenoLang (×2 manifests) | low/med | 46.0.7 | Two `uv.lock` files; one fix each. |
| 10 | `vite` + `postcss` (CSS-tooling cluster) | npm | 6 (3+3) | BytePort, PhenoLang, phenoDesign | medium | vite 6.4.2 / postcss 8.5.10 | Same advisory across 3 frontends. Coordinated bump candidate. |

**Cluster-fix leverage:** ~61 alerts addressable via the 10 cluster operations above (51% of all alerts).

---

## Top 10 AUTO-MERGE-READY (one-line bumps, low blast-radius)

Patch-level (semver-safe) bumps in lockfiles only, low/medium severity, no transitive complications.

| Rank | Repo | Pkg | Bump | Manifest |
|---|---|---|---|---|
| 1 | BytePort | `cookie` < 0.7.0 → 0.7.0 | yarn.lock (×2 manifests) | `frontend/web/{yarn,package}-lock.json`, `.github/frontend/...` |
| 2 | BytePort | `nanoid` < 3.3.8 → 3.3.8 | low blast | `frontend/web/package-lock.json` |
| 3 | BytePort | `prismjs` < 1.30.0 → 1.30.0 | patch | `frontend/web/package-lock.json` |
| 4 | BytePort | `js-yaml` 4.x → 4.1.1 | patch | `frontend/web/package-lock.json` |
| 5 | BytePort | `yaml` 2.x → 2.8.3 | patch | `frontend/web/package-lock.json` |
| 6 | PhenoLang | `pytest` → 9.0.3 (×2 manifests) | dev-only dep | `python/uv.lock`, `agileplus-mcp/uv.lock` |
| 7 | PhenoLang | `Pygments` → 2.20.0 (×2 manifests) | low | both `uv.lock` |
| 8 | PhenoLang | `authlib` → 1.6.11 (×2 manifests) | medium | both `uv.lock` |
| 9 | phenoDesign | `postcss` 8.5.10 + `vite` 6.4.2 | 2-line lockfile bump | `package-lock.json` |
| 10 | DevHex | (single med Docker advisory; no-fix) — **skip; see NO-FIX section** | — | — |

**Auto-merge leverage:** Shipping items 1–9 closes ~22 alerts via 9 `dependabot.yml` automerge enablements + lockfile updates.

---

## Top 5 NEEDS-REVIEW (require user judgement)

| # | Repo | Issue | Why review |
|---|---|---|---|
| 1 | PhenoLang | `fastmcp` < 3.2.0 → **3.2.0** (CRITICAL `GHSA-vv7q-7jx5-f767`) | Major version range jump. Verify FastMCP 3.x API compat; ×2 services (`python/`, `agileplus-mcp/`). |
| 2 | Tracera | `libxmljs2` ≤ 0.35.0 (CRITICAL ×2, **NO FIX**) | Native XML lib, no patched version. Decision: replace lib, pin & document, or drop feature. ARCHIVE/-located → likely STALE; verify before action. |
| 3 | KDesktopVirt | `users` ≥0.8.0 ≤0.11.0 (HIGH+MED, **NO FIX**) | Rust `users` crate unmaintained (RUSTSEC-2025-XXXX class). Migrate to `nix::unistd`/`uzers` fork. In `kvirtualstage-legacy/` → also STALE-candidate. |
| 4 | Tracera | `ray` 2.49.0 → 2.55.0 (HIGH) | ML runtime — major-ish bump in distributed compute path. Verify worker compat. |
| 5 | Tracera | `grunt` < 1.5.3 (HIGH ×2) | All in `ARCHIVE/CONFIG/sprintf-js@1.0.3/...` → triple-transitive in archived storybook config. Likely STALE; confirm and ignore. |

---

## STALE-DEP candidates (21 alerts → batch-ignore)

All alerts in archived / legacy paths. Recommended action: add `dependabot.yml` `ignore` directives or delete the manifests entirely.

| Repo | Path prefix | Alerts | Recommendation |
|---|---|---|---|
| Tracera | `ARCHIVE/CONFIG/default/*/package.json` | 12 (chromedriver ×4, libxmljs2 ×2, grunt ×3, rollup ×2, esbuild ×1, srvx ×1) | **Delete `ARCHIVE/CONFIG/default/`** — these are vendored/snapshotted package.json files inside an archive. Add `paths-ignore` in `dependabot.yml`. Closes both CRITICALs. |
| KDesktopVirt | `kvirtualstage-legacy/**` | 9 (docker ×5, ring, sqlx, protobuf, users) | Per memory: KVirtualStage is being rebuilt under eco-011. Confirm `kvirtualstage-legacy/` is dead code; if so, delete or `paths-ignore`. Closes the lone CRITICAL. |

If both batch-ignores ship: **closes 21 alerts including 3 of 5 CRITICALs** (libxmljs2 ×2, docker 25.0.6 ×1) at zero upgrade risk.

---

## NO-FIX-AVAILABLE (15 alerts — risk-accept or pin)

| Pkg | Repos | Notes |
|---|---|---|
| `github.com/docker/docker` GHSA-x744 / GHSA-pxq6 | DevHex, KDesktopVirt, Tracera | Affects `< 29.3.1` but **no fixed version published yet**. Wait for upstream. 8 alerts. |
| `users` (rust) | KDesktopVirt | Crate abandoned. Migrate (see NEEDS-REVIEW #3). 2 alerts. |
| `libxmljs2` | Tracera | No upstream fix. STALE-path → ignore. 2 alerts. |
| `pip` ≤ 26.0.1 GHSA-58qw | Tracera | Wait for pip 26.0.2+. 1 alert. |
| `srvx`, others (ARCHIVE) | Tracera | STALE. 2 alerts. |

---

## Expected delta if all AUTO-MERGE-READY ship

| Tranche | Alerts closed | Method | Risk |
|---|---|---|---|
| AUTO-MERGE-READY (Top 9) | **~22** | Lockfile-only patch bumps; enable `dependabot.yml` auto-merge gate | Low |
| CLUSTER fixes (top 7 non-stale) | **~28 additional** | One `cargo update -p X` / `uv lock --upgrade` per cluster | Low–Medium |
| STALE batch-ignore | **~21 additional** | Delete `ARCHIVE/CONFIG/`; `paths-ignore` for `kvirtualstage-legacy/` | None (dead code) |
| **Combined ceiling (auto + cluster + stale)** | **~71 alerts (60% of 119)** | Net new open after sweep: ~48 | — |
| Remaining after sweep | NEEDS-REVIEW (5–8 high-judgement) + NO-FIX-WAIT (~10) | Manual cycle / await upstream | — |

**Conservative target (auto-merge tranche only):** 22 alerts closed → 119 → ~97 open (-18.5%).
**Aggressive target (auto+cluster+stale):** 119 → ~48 open (-60%) including 4 of 5 CRITICALs.

---

## Recommended next operations (DAG)

```
P1.1  Delete Tracera ARCHIVE/CONFIG/ (closes 12 incl. 2 CRITICAL)   [predecessor: none]
P1.2  Confirm kvirtualstage-legacy/ deletable (closes 9 incl. 1 CRIT) [predecessor: eco-011 spec check]
P2.1  Enable dependabot auto-merge for patch+lockfile-only          [predecessor: none]
P2.2  Bump fastmcp 3.2.0 across both PhenoLang uv.locks (CRITICAL)  [predecessor: API-compat sweep]
P3.1  Cluster bumps: rustls-webpki, openssl, dompurify, vite        [predecessor: P2.1]
P4.1  Migrate Rust `users` → `uzers`/`nix` in KDesktopVirt          [predecessor: P1.2]
P4.2  Evaluate ray 2.49→2.55 in Tracera                             [predecessor: none]
```

Effort: P1 = 2–3 tool calls (~3 min). P2 = 4–6 tool calls (~5 min). P3 = 8–12 tool calls (~10 min). P4 = manual review.

---

## Source data

- Raw aggregation JSONL: `/tmp/depbot_triage/all_alerts.jsonl` (119 lines, ephemeral)
- Per-repo raw: `/tmp/depbot_triage/<repo>.json`
- Re-run command: `gh api repos/KooshaPari/<repo>/dependabot/alerts?state=open --jq '...'` per the 9 dirty repos.

## Related

- Snapshot: `docs/governance/dependabot-alert-tier2-snapshot-2026-04-26.md`
- TIER-1: `docs/governance/dependabot-alert-tier1-snapshot-2026-04-26.md`
- Billing-blocked rulesets: `docs/governance/dependabot-config-deep-audit-2026-04-26.md`

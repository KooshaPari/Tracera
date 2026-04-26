# Phenotype Org Dashboard — v54 (2026-04-26 late evening / post-restart)

**Snapshot**: Late-evening delta over [v53](./ORG_DASHBOARD_v53_2026_04_26.md). After v53 was written ~1h before the org usage limit, the post-restart wave continued through push rounds 6+7 + a 7a fast-forward batch, three provenance-split BytePort commits, a today's-commits push audit, two stale-ignore cleanups, 114 SBOM bootstraps, and ~16 GiB of disk reclaim from a tmp_pack purge + /tmp safe-prune. Total day push count crossed **48+ repos**, broken-link debt continued downward, and the agent-imessage hook log received a stopgap truncation (11.5 MB → 730 KB). Pure documentation commit — no source pushes in this dashboard window.

---

## What changed since v53 (one-paragraph)

Push rounds 6+7 sequenced cliproxyapi (30 commits forwarded), KDV ratatui, FocalPoint DTO cleanup + iOS_BUILD_STATUS, McpKit, agent-user-status, Paginary, and heliosApp; round 7a fast-forwarded DevHex/Httpora/nanovms. BytePort fully resolved with three provenance-separated commits (MODE 1/2/3) and credential `ILOVEKUSHPAPI` scrubbed; Civis PR #253 opened with README rebase using `--ours` (verify-then-write upstream pattern). Today's-commits push audit (5c7b9b1bbd) showed 42/53 fully pushed. Hook hygiene: agent-imessage stopgap truncated the log 11.5 MB → 730 KB (37c15cf89e). Two stale-ignore sweeps cleaned Configra (3) + AgilePlus (1). 114 SBOMs bootstrapped across four commits. Disk: tmp_pack purge +4.6 GB (f8a9c2d736), /tmp safe-prune +12 GB (99be14f3b3) → **+16 GiB total reclaim** with 36 GiB free. Cargo.lock heliosCLI cleanup (eef573e) landed, helios-cli rebase escalated (Strategy 1 recommended), argis-extensions escalated (Strategy C recommended). AtomsBot/chatta archived triage committed (fd2862f3cf), AgentMCP local README conflict cleaned (02c133b0f4), pheno autostash dropped clean, Tracera-recovered upstream linkage repaired. Memory updated: `feedback_fork_aware_readme` + extension to `reference_archived_repos_locked`.

---

## Releases Shipped Today (cumulative, unchanged from v53)

| Repo | Tag | Highlight |
|------|-----|-----------|
| AgilePlus | v0.2.1 | Security: rustls-webpki via async-nats 0.46→0.47 |
| phenotype-observably-macros | 0.1.1 | compile_error guard for non-Result returns |

---

## Updated Metrics

| Metric | v53 | v54 | Delta |
|--------|-----|-----|-------|
| Repos pushed (today, cumulative) | 31 (4 waves) | **48+** (+ rounds 6, 7, 7a) | **+17** |
| Today's-commits push completeness | — | **42/53 fully pushed** (audit 5c7b9b1bbd) | — |
| Org-wide broken doc links | ~5,000 | ~5,000 (no fresh sweep) | — |
| LEGACY README badge coverage | 84.3% | 84.3% (carry) | — |
| RED READMEs (honest rewrite) | 4 | **5** (+ Civis PR #253 verify-then-write) | +1 |
| Dependabot alerts | ~87 | ~87 (carry) | — |
| cargo-deny advisories (org) | ~29 | ~29 (carry) | — |
| Releases shipped (today) | 2 | 2 (carry) | — |
| SBOMs present (org) | partial | **+114 bootstrapped** (08a7b6e + 5bde50c + 04fdbc0 + cca07e8) | **+114** |
| Disk free (canonical /repos workspace) | ~20 GiB | **36 GiB** | **+16 GiB** (tmp_pack +4.6, /tmp +12) |
| Stale-ignore entries removed | — | **4** (Configra 3 b5f0aa9 + AgilePlus 1 2b3909f) | +4 |
| BytePort credential leak | exposed | **scrubbed** (`ILOVEKUSHPAPI`, 3-commit provenance split) | resolved |
| agent-imessage hook log size | 11.5 MB | **730 KB** (stopgap 37c15cf89e) | -10.8 MB |

---

## Build / Unblock Status (v54)

| Stream | State | Notes |
|--------|-------|-------|
| FocalPoint Xcode build | GREEN | unchanged from v53 (commit 45dc356) |
| FocalPoint Rust workspace | GREEN | DTO cleanup landed in round 6 |
| FocalPoint iOS_BUILD_STATUS | DOC | shipped in round 6 |
| AgilePlus codex-local-boot | YELLOW | unchanged; `agileplus-plugin-core` 404 still blocking |
| cliproxyapi-plusplus | YELLOW | 30 forward-fix commits pushed (round 6); **23 errors remain** pending user decisions |
| AgentMCP README | RESOLVED | local cleanup 02c133b0f4 |
| BytePort | **RESOLVED** | 3-commit provenance split + credential scrubbed + push complete |
| Civis | **PR open** | PR #253; README rebase via `--ours` (verify-then-write upstream) |
| AtomsBot/chatta | **TRIAGED** | archived state recorded (fd2862f3cf) |
| Tracera-recovered | RESOLVED | upstream linkage repaired |
| pheno (autostash) | CLEAN | autostash dropped, tree clean |
| /repos canonical pack | RED | `unable to read tree dab120b1` still — W-78D pattern, diagnosis pending |
| helios-cli rebase | **ESCALATED** | Strategy 1 recommended (user) |
| argis-extensions | **ESCALATED** | Strategy C recommended (user) |
| KDV ratatui | PUSHED | round 6 |

---

## Disk Recovery (post-restart wave)

| Action | Commit | Reclaim |
|--------|--------|---------|
| tmp_pack purge | f8a9c2d736 | +4.6 GiB |
| /tmp safe-prune | 99be14f3b3 | +12.0 GiB |
| **Total** | — | **+16.6 GiB** |

Free now: **36 GiB** (clears the 30 GiB pre-dispatch floor with margin).

---

## User-Decision Queue (final state — 2026-04-26 EOD)

**Canonical runbook**: `/repos/docs/governance/user_decisions_runbook_2026_04_26.md`

Carry-over from v53 plus newly escalated items:

| # | Item | State |
|---|------|-------|
| 1 | cliproxyapi cluster A+B (23 errors) | open — user decision required |
| 2 | agileplus-plugin-core 404 | open |
| 3 | AgilePlus README rebase against main | open |
| 4 | BytePort backend ownership | open (code-side resolved) |
| 5 | GDK quality-gate adoption | open |
| 6 | argis-extensions | **escalated — Strategy C recommended** |
| 7 | helios-cli rebase | **escalated — Strategy 1 recommended** |
| 8 | /repos canonical-subdir-inheritance + pack corruption | open (W-78D playbook) |
| 9 | OpenAI key revocation | open (carry) |
| 10 | Civis PR #253 review | open (newly opened) |
| 11 | Misc per runbook | see file |

---

## Tomorrow Priorities

1. **cliproxyapi cluster A+B decisions** — last 23 errors blocking
2. **helios-cli rebase Strategy 1** — execute on user approval
3. **argis-extensions Strategy C** — execute on user approval
4. **`/repos` pack corruption W-78D playbook** — verify workstate → gc → rebase → fsck → push
5. **agileplus-plugin-core 404** — create/restore or remove dep
6. **Civis PR #253** — review + merge
7. **agent-imessage real fix** — log truncation was stopgap; root-cause already audited (418d2eb881)

---

**Generated**: 2026-04-26 late evening | **Supersedes**: ORG_DASHBOARD_v53_2026_04_26.md | **Scope**: post-restart full delta + session-close

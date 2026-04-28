# KDesktopVirt — Dependabot Triage & Redeye Reconciliation (2026-04-27)

**Method:** API-only via `gh api`. Read-only. Cross-referenced against `july-2025-redeye-extract-or-archive-2026-04-27.md` and memory `reference_session_2026_04_25_releases.md`.

## Repo State (live API)

| Field | Value |
|-------|-------|
| Name | KooshaPari/KDesktopVirt |
| Created | 2025-07-14 |
| Pushed | 2026-04-27 (today) |
| Archived | **false** |
| Language | Rust |
| Size | 29.4 MB |
| Description | "AI Agent Desktop Automation with container orchestration" |

## Redeye Reconciliation

**KDesktopVirt is NOT in the July-2025 redeye extract-or-archive set** (`july-2025-redeye-extract-or-archive-2026-04-27.md`, 11 repos). The redeye doc explicitly cites KDesktopVirt as the **canonical rebuild target** (eco-011) replacing the archived `kmobile` skeleton. Per `reference_session_2026_04_25_releases.md`, KDesktopVirt v0.2.1 shipped 2026-04-25 as one of 9 product releases.

**Conclusion:** "REFERENCE-ONLY default" framing in the prompt is incorrect for this repo. KDesktopVirt is active, released, and being pushed.

## Open Alerts (8)

| # | Sev | Package | Patched | Summary |
|---|-----|---------|---------|---------|
| 43 | high | rustls-webpki | 0.103.13 | DoS via panic on malformed CRL BIT STRING |
| 3 | medium | inventory | 0.2.0 | Reference to non-Sync data exposed across threads |
| 1 | medium | inventory | 0.2.0 | Std-lib access prior to runtime init |
| 42 | low | rand | 0.10.1 | Unsound w/ custom logger using `rand::rng()` |
| 41 | low | rustls-webpki | 0.103.12 | Name constraints on wildcards |
| 40 | low | rustls-webpki | 0.103.12 | URI-name constraints incorrectly accepted |
| 11 | low | rsa | 0.9.10 | Panic on prime == 1 |
| 9 | low | xcb | 1.6.0 | I/O safety violation in `connect_to_fd*` |

Severity distribution: 1 high, 2 medium, 5 low. All have published patches; mostly minor/patch bumps within the same major.

## Decision: **KEEP-AND-FIX**

**Justification:**
1. Active released product (v0.2.1, 2026-04-25), pushed today.
2. Listed in eco-011 rebuild track as the canonical replacement for `kmobile` — extracting *from* it would invert dependency direction.
3. All 8 alerts patchable via routine `cargo update -p <crate>` within current major versions; no breaking-change uplift required.
4. `xcb` (#9) is platform-specific (Linux X11) — likely behind a `cfg(target_os = "linux")` gate; verify before assuming runtime exposure.

## Recommended Next Action

Single Dependabot-style PR consolidating all 8 bumps:

```
cargo update -p rustls-webpki --precise 0.103.13
cargo update -p rand --precise 0.10.1
cargo update -p rsa --precise 0.9.10
cargo update -p xcb --precise 1.6.0
cargo update -p inventory --precise 0.2.0  # may require minor in dependents
```

Verify `cargo build --release` + `cargo test` locally, then push as `chore(deps): patch 8 dependabot advisories` from worktree (canonical KDesktopVirt is for `main` integration only per `Phenotype/CLAUDE.md`).

**Estimated effort:** 3-6 tool calls, 1-3 min. Trivial fix-up if `inventory 0.1 → 0.2` doesn't cascade.

## Out-of-Scope (this doc)

- No archive ops (would contradict active-release status).
- No PR creation (read-only API audit per constraint).
- No worktree edits.

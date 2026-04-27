# OCI Lottery Infrastructure State — 2026-04-27

## Overview
OCI lottery daemon infrastructure has been merged to `main` but is **not yet operational** (daemon binary not installed, launchctl not loaded).

## PR Status

| PR | Title | State | Merged | Branches |
|----|-------|-------|--------|----------|
| #15 | OCI Always-Free A1.Flex lottery daemon | MERGED | 2026-04-25T15:54:49Z | feat/oci-lottery-daemon |
| #16 | integrate oci-lottery → oci-post-acquire | MERGED | 2026-04-25T16:03:37Z | feat/oci-lottery-invokes-post-acquire |
| #35 | warn about A1.Flex capacity, link oci-lottery from day-1 | MERGED | 2026-04-26T01:41:53Z | docs/oci-lottery-runbook-link |

All PRs merged into `main` as of 2026-04-25.

## Daemon Status

**Process:** NOT RUNNING
```bash
launchctl list | grep oci-lottery  # → NOT loaded
ps aux | grep -i "oci.*lottery"    # → no match
```

**Binary:** NOT INSTALLED
```bash
ls -lah /usr/local/bin/oci-lottery  # → BINARY NOT INSTALLED
```

**Launchd Config:** EXISTS (template only)
```
/Users/kooshapari/CodeProjects/Phenotype/repos/phenotype-infra/iac/oci-lottery/dist/phenotype-oci-lottery.plist
```
- Contains placeholders: `REPLACE_ME` for log paths and working directory
- RunAtLoad=true, KeepAlive=true, ThrottleInterval=60s (configured)
- Not yet loaded into launchctl

## Code Artifacts

- Rust crate built in debug: `iac/target/debug/deps/oci_lottery-*`
- Release binary not present
- Plist template at `dist/phenotype-oci-lottery.plist` requires setup

## Latest Commits

Main branch tip: `2fa53b6` (2026-04-25 14:16:32 UTC)
Title: "ci(iac): add cargo fmt/check/clippy/test workflow for Rust crates (#27)"

All lottery-related code merged. No activity since 2026-04-25.

## Blockers for Activation

1. **Binary Release**: Rust crate must be compiled (`cargo build --release`) and installed to `/usr/local/bin/oci-lottery`
2. **Plist Setup**: Template placeholders must be replaced with actual paths (e.g., `/Users/kooshapari`)
3. **Launchd Load**: Run `launchctl load ~/Library/LaunchAgents/phenotype-oci-lottery.plist` (after setup)
4. **OCI Credentials**: Daemon requires OCI credentials in environment or Vaultwarden

## Summary

Code is merged and ready; infrastructure activation (binary build/install, launchd registration) pending. Per memory snapshot, daemon was expected to run "locally on Koosha's desktop"—currently in pre-deployment state.

**Next steps:** Build release binary, populate plist template, load into launchctl, verify logs.

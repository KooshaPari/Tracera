<!-- Generated from D04-ROOT-PREFLIGHT.json; do not edit by hand. -->

# D-04: Windows root and backend preflight

Source snapshot: `5146d7f4e1a038be2acc73082df33aec5ee3d452`. Operator report received 2026-10-18T06:53Z; original observation time unknown. No Windows host, env contents, CLI runtime, backend, or service was independently inspected in this follow-up.

The operator identifies `C:\Users\koosh\Tracera` as the intended checkout with `docker-compose.local.yml`, `.env.local`, and `.env.example`; other compose-bearing candidates include `Tracera-w4-test` and `agents\sandbox\pheno\wt-*`. File existence alone does not select an authoritative runtime or data owner.

The intended forward sequence is recorded, **not executed**:

```powershell
tracera --root C:\Users\koosh\Tracera status
tracera --root C:\Users\koosh\Tracera up
```

Prerequisites: establish installed binary/source identity, selected root and compose assets, configuration/data ownership, preserved env bytes and file/link metadata, a reachable compatible backend, and owned startup authorization. Do not use `status` as a read-only preflight. GAP-020 retains the launch/layout obligation; GAP-022 covers backend qualification; GAP-023 covers env preservation.

## Source-qualified write behavior

At this source snapshot, `commands.rs:145-170` accepts the explicit root's bundle or `docker-compose.local.yml`; `bundle.rs:107-127` resolves a repository layout's env to `<root>/.env.local`. `commands.rs:244-246` calls `ensure_env_file` and `sync_bundle_env_symlink` before Compose status; up does likewise at `commands.rs:181-189`.

`compose.rs:168-202` retains an existing file only if a line starts exactly `POSTGRES_PASSWORD=` with at least one following character. Otherwise it writes a newly generated env body to the same path, including when the existing file cannot be read. This is conditional overwrite behavior proven in source, **not proof that the Desk file was overwritten**. Existing Desk contents and installed binary equivalence remain UNKNOWN. The nonempty test is not a comprehensive password/config validator.

`compose.rs:145-165` retains an existing real compose-side env file, can replace a differently targeted symlink, and creates a Unix symlink or Windows copy when absent. With repository layout these paths normally coincide; bundle layouts can use separate paths. No env value was read or printed here.

## Backend evidence boundary

Operator reports Docker selected, `docker-desktop` WSL distro Stopped, and FedoraLinux-44 running Podman on port 7777. Treat selected Docker readiness as unqualified; stopped distro state alone does not prove every Docker endpoint unavailable. This report is not a current runtime probe.

`commands.rs:20-29` exposes `--backend` / `TRACERA_BACKEND`. `runtime.rs:25-65,119-171` supports native `podman compose` and `wsl+docker`; explicit backend selection does not auto-fallback when its probe fails. `compose_works` checks Compose version for native backends, which does not prove daemon readiness. No `wsl+podman` backend or automatic connection to Fedora's port 7777 is established by this code. Native Podman support does **not** qualify that particular remote endpoint.

## Closure oracles and safe forward work

- GAP-020 positive: exact installed CLI hash/version and matching selected root/assets documented, then the intended sequence qualified under owned authorization. Negative: sibling/alternate root or missing assets rejected without misidentifying the candidate.
- GAP-022 positive: selected backend, endpoint, Compose provider/version and daemon readiness demonstrated for this root. Negative: unavailable selected backend produces explicit unavailable evidence; another running WSL distro or port cannot count as success.
- GAP-023 positive: future read-only preflight preserves env bytes, file/link metadata and data ownership for valid, missing-password and unreadable fixtures. Negative: a missing/empty password or unreadable file cannot silently regenerate/replace user config during status. Test symlink targets and Windows copy behavior in isolated fixtures, never against the Desk env.

First forward action is a file/metadata-only preflight and secure configuration preservation; no CLI status/up, Docker/WSL/Podman startup or migration is authorized by this document. Runtime validation remains NOT_RUN.

## D-04 intent and dimension verdict tree

Generated: 2026-10-18T07:18:52Z

```text
GAP-020 Explicit root launch/layout
  Implementation: PASS | 5146d7f4e1a038be2acc73082df33aec5ee3d452:crates/tracera-cli/src/commands.rs:145-170
  Usability: UNKNOWN | D04-ROOT-PREFLIGHT.md: report identity and original observation time unknown
  Validation: NOT_RUN | D04-ROOT-PREFLIGHT.md: scope excludes runtime commands; no execution witness
  Assurance: UNKNOWN | D04-ROOT-PREFLIGHT.md: installed binary equivalence and current runtime unverified
GAP-022 Selected backend readiness
  Implementation: UNKNOWN | 5146d7f4e1a038be2acc73082df33aec5ee3d452:D04-ROOT-PREFLIGHT.md: Backend evidence boundary
  Usability: UNKNOWN | D04-ROOT-PREFLIGHT.md: report identity and original observation time unknown
  Validation: NOT_RUN | D04-ROOT-PREFLIGHT.md: scope excludes runtime commands; no execution witness
  Assurance: UNKNOWN | D04-ROOT-PREFLIGHT.md: installed binary equivalence and current runtime unverified
GAP-023 Read-only status preserves configuration
  Implementation: FAIL | 5146d7f4e1a038be2acc73082df33aec5ee3d452:crates/tracera-cli/src/commands.rs:244-246; crates/tracera-cli/src/compose.rs:168-202
  Usability: UNKNOWN | D04-ROOT-PREFLIGHT.md: report identity and original observation time unknown
  Validation: NOT_RUN | D04-ROOT-PREFLIGHT.md: scope excludes runtime commands; no execution witness
  Assurance: UNKNOWN | D04-ROOT-PREFLIGHT.md: installed binary equivalence and current runtime unverified
```

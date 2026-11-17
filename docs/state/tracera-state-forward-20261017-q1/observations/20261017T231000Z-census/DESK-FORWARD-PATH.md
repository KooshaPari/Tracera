# Desk qualification forward path (plan only)

The operator-provided read-only [Desk report](evidence/desk-status-2026-10-17.md) identifies Windows 10.0.28120, one RTX 3090 Ti occupied by vLLM at approximately 22 GB VRAM, C: approximately 38 GB free, running FedoraLinux-44, stopped docker-desktop, and an installed `C:\Users\koosh\.cargo\bin\tracera.exe` reporting 0.1.0. No Tracera Windows service was registered. These are dated observations and placement constraints; neither a second GPU nor a mandatory Windows service is assumed. Blank disk-health fields do not establish SMART health.

The Compose management CLI and manually started SQLite API are separate identities. A CLI version/help or absent process does not establish the state of the other API, an installed desktop application, or production. Preserve exact binary hash/version, root/config, PID/listener ownership, data-store path, and readiness receipt for each candidate separately.

```text
matching bundle/worktree + binary identity
  -> selected runtime available and Compose-capable
  -> disk / ports / CPU / data ownership preflight
  -> separately authorized owned startup
  -> health + ready + real persisted journey + restart proof
```

1. **Locate matching assets without starting anything.** The CLI walks executable ancestors for `docker-compose.bundle.yml`, then `docker-compose.local.yml`. Explicit `--root` / `TRACERA_ROOT` accepts `<root>/tracera-bundle/docker-compose.bundle.yml` or `<root>/docker-compose.local.yml`. Record actual discovered path and revision; do not invent a missing bundle or invoke the executable with no understood action. Source: `048f44d2c38925f4c7c9968dfeaeda1a97f4d970:crates/tracera-cli/src/bundle.rs:47-142`; `commands.rs:145-170`.
2. **Choose a runtime already available.** The source supports Docker, Podman, Apple Container, and WSL-hosted Docker; a binary on PATH alone is insufficient because Compose support is separately probed. Running Fedora Podman does not prove native Windows Docker or WSL Docker/Compose works. No docker-desktop resume, new distro, or runtime installation is part of this plan. Source: same SHA, `crates/tracera-cli/src/runtime.rs:25-92`.
3. **Preflight the selected path.** Record required images/build disk footprint against actual target volume, CPU/RAM limits, ports declared by the selected compose file, any existing listeners, and data ownership. Protect existing Fedora/vLLM workloads. The CLI defaults its local frontend port to 18081 and fixes Compose project names; an already running API on 8080/8091 is not automatically the same profile. Source: same SHA, `crates/tracera-cli/src/bundle.rs:89-108,119-139`; `crates/tracera-cli/src/compose.rs:64-73`.
4. **Qualify only after a separate owned action is authorized.** Record exact command/env/root/backend and immutable artifact identity, then health/readiness, a real owned-input journey, persistence/reopen, and failure controls. `status`/`doctor` may create an env link or file after layout resolution, so do not call them a universally read-only preflight. Source: same SHA, `crates/tracera-cli/src/commands.rs:243-250,322-349`; `crates/tracera-cli/src/compose.rs:141-197`.

No service, WSL distro, Docker runtime, installation, cleanup, or configuration change was performed for this documentation observation. Proposed pilot checks are a qualification plan and do not add accepted mandatory feature scope.

## Fresh reconciliation receipts

[Backend report](evidence/backend/BACKEND-REPORT.md) and [Desk identity receipt](evidence/backend/desk-reconciliation.json) qualify the installed CLI's actual missing-bundle status failure before Compose. The existing sibling worktree `C:\Users\koosh\Tracera` contains `docker-compose.local.yml`; ancestor search from cargo-bin cannot discover that sibling. Exact CLI SHA-256 is `1FEFB2CF163DC738C1B3934F18C0A6FDCAA2D07394E43F9F92E7852D7B445B7C`. Worktree HEAD `0f7453de0171aa7cb934d8984565d0dc048f9e72` had one dirty entry; installed binary/source provenance remains unqualified. `--root` is advertised in [actual help](evidence/backend/desk-cli-help.json), but root-qualified status was not run because it can write env files.

The distinct `tracera-live` PID20208 binary hash is `6202AB83D311935111FB674844C79EFFFD15C3D897FD0F65E5116C189745C0A5`. Health/readiness responded200on8080/8091at22:26Z, then six probes timed out at22:54Z. Fresh UI root feasibility at23:29Zdoes not override five empty-response paths at23:48Z or missing8091listener at23:49Z. See [live runtime](evidence/backend/live-runtime.json), [live view report](evidence/live-view-report.json), and [direct paths](evidence/live-direct-paths.json). Deployed source identity is UNKNOWN; these failures do not refute current source implementation.

At22:33:25ZCIVIS returned genuine total0/items0/stubfalsewith complete one-page response. Other project totals are incomplete first-page observations; collector typemapping failed and later requests timed out. No full item manifest is claimed. See [data receipt](evidence/backend/live-runtime.json).

Later [direct8080 follow-up](evidence/direct8080-feasibility.json) recovered projects/items JSON200while root404; actual project IDs became available. This does not restore the absent8091frontend. The54dynamic paths remain NOT_RUNbecause no authorized frontend subject was available, rather than because IDs were unknowable. Do not infer the entire API is dead from earlier timeouts. Both owned forwards were stopped and browsers closed; see updated [live report](evidence/live-view-report.json).

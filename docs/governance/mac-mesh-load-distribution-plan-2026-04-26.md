# Mac → Compute Mesh Load Distribution Plan (2026-04-26)

**Status:** Draft — pending answers to Section E open questions before implementation.
**Trigger:** Mac at 23 GiB free (98% full) on `/System/Volumes/Data` (926 GiB volume). Disk-budget policy requires ≥30 GiB pre-flight, ≥20 GiB hard floor for dispatch (`Phenotype/CLAUDE.md` → `target_budget_policy.md`). Desktop PC now reachable on Tailscale (per `reference_compute_mesh_state.md`, 2026-04-25).
**Scope:** Define which workloads stay on the Mac, which migrate to mesh nodes, and the storage/network topology that supports the migration. Companion to AgilePlus task **#162** (compute mesh provisioning — CF Pages + GCP + GCS done; OCI + CF DNS token + desktop enrollment pending).

---

## A. Workload taxonomy

| # | Workload | Disk | CPU/RAM | Latency-sensitive? | Disposition | Rationale |
|---|----------|------|---------|--------------------|-------------|-----------|
| A1 | Cargo workspace builds (AgilePlus, hwLedger, FocalPoint, phenotype-infrakit, ~30 crates) | **Heavy** (4–9 GiB `target/` per crate) | Heavy | No (build can sit 30–120 s) | **OFFLOAD** to OCI A1.Flex / Desktop | Single biggest disk consumer; `target/` regrows after every `target-pruner` run. |
| A2 | `cargo check` / `clippy` / `cargo fmt` (incremental dev loop) | Medium | Medium | **Yes** (sub-second feedback) | **STAY local** | IDE-attached; remote round-trip kills DX. Use sccache to share artifacts. |
| A3 | Cargo registry cache (`~/.cargo/registry`, `~/.cargo/git`) | ~5–10 GiB | None | No | **OFFLOAD** to NFS/sshfs from mesh node | Single shared cache across all 30 workspaces; current Mac copy duplicates per-machine. |
| A4 | Docker / OrbStack image pulls + Tauri bundling | **Heavy** (10–50 GiB images) | Heavy | No | **OFFLOAD** to Desktop (Linux native Docker) | macOS Docker = VM overhead + disk burn; Linux native is faster + disk lives elsewhere. |
| A5 | `pnpm`/`npm`/`bun` `node_modules` for VitePress sites + Tauri frontends | Medium (1–3 GiB × N sites) | Light | Yes for HMR | **HYBRID** — node_modules local symlinked from shared store; build/CI on mesh | Use pnpm content-addressable store on shared NFS; keep symlink trees local for HMR. |
| A6 | VitePress `docs:build` (per-repo + cross-repo aggregator) | Medium | Medium | No | **OFFLOAD** to GCP e2-micro or CF Pages build | Already partially done (CF Pages handles `docs.kooshapari.com`). |
| A7 | Dependabot / `cargo audit` / `cargo deny` / SBOM generation | Light | Light | No | **STAY local OR Forgejo CI** | Cheap; either local cron or Woodpecker job. |
| A8 | VS Code / Claude Code TUI / forge / codex / gemini CLIs | Light | Medium | **Yes** | **STAY local** | UI surfaces — must stay on the user-attached machine. |
| A9 | iMessage MCP bridge (`mcp__messages__*`, `mcp__agent-imessage__*`) | Light | Light | Yes | **STAY local — Mac-only** | macOS-exclusive Messages.app DB + AppleScript bridge. Cannot migrate. |
| A10 | Tailscale node + ssh client + git client | Light | Light | Yes | **STAY local** | Mesh control plane. |
| A11 | Git worktrees (`repos/<name>/`, `repos/<name>-wtrees/`, `.worktrees/`) | **Heavy** (source × N branches) | None | **Yes** (IDE indexing) | **STAY local** for hot worktrees; **OFFLOAD** cold/archive worktrees to mesh node | Latency hits IDE & search. Cold worktrees (Tracera/.archive/*) can move to mesh sshfs mount. |
| A12 | Heavy artifacts: bench runs, telemetry snapshots, profile dumps, recorded sessions | Heavy | None | No | **OFFLOAD** to GCS `phenotype-artifacts-kooshapari` | Already provisioned. |
| A13 | Per-agent test runs (pytest, cargo test, vitest swarms) | Medium | Heavy | Some | **OFFLOAD** to Desktop / OCI for full suites; **STAY local** for single-test runs | TDD loop stays local; full suite goes remote. |
| A14 | Long-running agent loops (`/loop`, swarm dispatch, lottery daemons) | Light–Medium | Medium | No | **OFFLOAD** to OCI/Desktop (systemd) | Should not consume Mac battery/CPU when laptop closed. Already the plan for OCI lottery daemon. |
| A15 | `.archive/` repos (16 archived: Settly, KaskMan, KodeVibeGo, etc.) | Heavy (legacy `target/`, `node_modules`) | None | No | **OFFLOAD** read-only to GCS or mesh-node sshfs | Per memory: 16 inert PRs; reference-only; should not occupy local SSD. |

**Net target:** move ~150–250 GiB of workload off the Mac (cargo target dirs + Docker layers + archive worktrees + heavy artifacts), restoring the ≥30 GiB headroom required by disk-budget policy.

---

## B. Mesh node assignments

Provider state from `reference_compute_mesh_state.md` (2026-04-25): 6/6 providers auth'd, OCI VM still pending lottery hit, desktop PC reachable on Tailscale.

| Node | Resources | Cost | Role | Workloads |
|------|-----------|------|------|-----------|
| **Mac (laptop)** | M-series, ~926 GiB SSD (now 23 GiB free), home wifi | $0 | **Control plane + UI** | A2, A8, A9, A10, hot subset of A11 |
| **Desktop PC** (home, Tailscale-reachable) | TBD — see open Q1; assume ≥16-core x86_64 + ≥64 GiB RAM + ≥1 TiB SSD | $0 | **Tier-1 heavy compute** | A1 (primary x86_64 cargo host), A4 (Docker), A13 (full test suites), A14 (long agents) |
| **OCI A1.Flex** (Always Free, ARM 4 OCPU / 24 GiB) | aarch64, blocked on lottery acquire | $0 | **Tier-1 ARM compute + 24/7 services** | A1 (ARM cargo host), A3 (shared registry cache via NFS over Tailscale), A14 (lottery daemon, Forgejo, Woodpecker, Vaultwarden), A7 |
| **GCP e2-micro** (us-central1, free tier) | 0.25 vCPU burst, 1 GiB | $0 | **Lightweight orchestrator** | A6 (VitePress builds), small cron, GCS uploader, mesh health pinger |
| **AWS** (account `222634395138`, us-west-2) | Pay-as-you-go (rotate key in 24h per memory) | $ | **API edge only** | `api.kooshapari.com` Lambda Function URL — no build workload |
| **CF Pages** | Static hosting | $0 | **Doc/landing static** | `docs.kooshapari.com`, `projects.kooshapari.com` (already deployed per memory) |
| **GCS `phenotype-artifacts-kooshapari`** | Object store (us-central1) | ~$0 | **Artifact sink** | A12, A15 (read-only archive bucket) |

**Tier order for `cargo-mesh` dispatch:** `desktop > oci-a1 > local`. Pick desktop for x86_64; OCI for ARM-only validation; local only when offline or when remote is failing.

---

## C. Storage mesh

```
                         ┌────────────────────────────────────┐
                         │   GCS phenotype-artifacts-kooshap. │  cold artifacts, .archive snapshots
                         └────────────────┬───────────────────┘
                                          │
   ┌─────────────┐    Tailscale (WG)      │
   │  Mac        │◄─────sshfs/NFS────────►│   ┌────────────────────────────┐
   │ (worktrees, │                            │ OCI A1.Flex (ARM)          │
   │  IDE, MCP)  │◄──── ssh/cargo-mesh ──────►│  - shared cargo registry   │
   └─────┬───────┘                            │  - Forgejo, Woodpecker     │
         │                                    │  - sccache server          │
         │                                    └────────────────────────────┘
         │                                              ▲
         │  Tailscale (WG, LAN-routed if same subnet)   │
         ▼                                              │
   ┌─────────────────────────────────────┐              │
   │ Desktop PC (x86_64)                 │◄─── shared cargo registry over NFS
   │  - target/ on local NVMe (fastest)  │
   │  - Docker, Tauri bundling           │
   │  - sccache client                   │
   │  - full test runs                   │
   └─────────────────────────────────────┘
```

**Concrete storage rules:**

1. **Local Mac SSD** (hot, latency-sensitive): worktrees in `repos/<name>/` and `repos/<name>-wtrees/<topic>/`, `~/.claude`, IDE caches, CLI binaries.
2. **Local Mac SSD — evict** (move off): `target/` for every repo, `~/Library/Caches/Yarn`, `~/Library/Containers/com.docker.*`, `.archive/<repo>/target/`, `.archive/<repo>/node_modules/`, OrbStack VM disk.
3. **NFS over Tailscale (OCI A1.Flex serves)**: `~/.cargo/registry`, `~/.cargo/git`, pnpm content-addressable store, sccache. Mounted at boot via `launchd` (Mac) and `systemd` (desktop).
4. **`CARGO_TARGET_DIR` env** (per-shell or repo-`.envrc`): points at remote-mounted NVMe on the chosen mesh node. For desktop runs, `CARGO_TARGET_DIR=/desktop/target/<workspace-id>`. Local builds opt in via unset.
5. **GCS bucket**: archive `target/` snapshots if needed, recorded sessions, bench runs, `.archive/` repo tarballs (read-only after upload).
6. **target-pruner cron** (already exists at `FocalPoint/tooling/target-pruner`): keep on local + add identical cron on desktop and OCI nodes; tighten threshold from default to **prune anything with atime ≥3d** (memory `feedback_pruner_atime_limitation.md` notes atime resets — supplement with explicit `rm -rf <repo>/target` script for repos not opened in 7d).

**Worktree directories: keep local.** Source ≠ build artifacts. Rsync of source costs ~MB; rsync of `target/` costs GiB. Move only the `target/` dir (and Docker/node_modules) off-machine.

---

## D. Migration steps

Numbered, dependency-ordered. Each step ≤5 min wall-clock with parallel subagents where annotated.

**Phase 1 — Foundation (blocks everything else)**

1. **Answer Section E open questions** (user input required — see below). Without Q1/Q2 answers, the desktop role is unspecified.
2. **Provision Tailscale ACLs**: confirm Mac, Desktop, GCP e2-micro, OCI A1.Flex (when up) are in the same tailnet with `tag:mesh` granting ssh + NFS ports (2049, 22). Verify with `tailscale status` and `tailscale ping <node>`.

**Phase 2 — Immediate disk relief (do now, even before desktop is fully configured)**

3. **Run `target-pruner --prune` aggressively** on Mac: lower threshold to 2d. Expected reclaim: 20–60 GiB based on prior session patterns.
4. **Rsync `.archive/*/target` and `.archive/*/node_modules` to GCS**, then `rm -rf` originals. Per memory the 16 archived repos are reference-only; they should not occupy local SSD. Expected reclaim: 30–80 GiB.
5. **Move OrbStack/Docker VM disk** to external if present, OR uninstall and run Docker exclusively on the desktop. Expected reclaim: 10–50 GiB.

**Phase 3 — Remote builder bootstrap**

6. **Bootstrap remote cargo runner on Desktop**:
   - Install Rust toolchain (rustup) matching `rust-toolchain.toml` of the workspaces.
   - Install `sccache` server, point `RUSTC_WRAPPER=sccache`, `SCCACHE_DIR=/var/cache/sccache`.
   - Set up `~/desktop-build/<workspace>/target` per workspace.
   - Verify: `ssh desktop "cd ~/AgilePlus && cargo check"` succeeds.
7. **Bootstrap remote cargo runner on OCI A1.Flex** (when lottery hits) using identical recipe; cross-compile target = aarch64.

**Phase 4 — Shell ergonomics**

8. **Install `cargo-mesh` wrapper** in `~/bin/`: a Rust binary (per scripting policy — Rust default) that:
   - Inspects current dir → resolves workspace name.
   - Picks tier (desktop/oci/local) based on `--target` flag and node availability.
   - Rsyncs source (excluding `target/`, `.git/`) to `<node>:~/desktop-build/<workspace>/`.
   - Runs `cargo <subcommand>` over ssh with `CARGO_TARGET_DIR` set on remote.
   - Streams stdout/stderr back; on success, optionally rsyncs back binaries from `target/release/`.
   - Writes provenance line to `repos/.argis-helios-bus/cargo-mesh.log`.
   Pseudocode contract only — implementation belongs in `repos/phenotype-tooling/crates/cargo-mesh/` (new crate).
9. **Add shell aliases** in `~/.zshrc` (keep ≤5 lines per shell-script policy; the binary does the heavy lifting):
   - `alias cmesh='cargo-mesh'`
   - `alias cmd='cargo-mesh --target desktop'`
   - `alias cmoci='cargo-mesh --target oci'`

**Phase 5 — Storage mesh**

10. **Mount shared cargo registry** from OCI A1.Flex over Tailscale (NFSv4 or sshfs). Update `~/.cargo/config.toml` only if needed; the registry path stays `~/.cargo/registry` but is a mount.
11. **Per-repo `.envrc`** (direnv) for the heaviest workspaces (AgilePlus, hwLedger, FocalPoint, phenotype-infrakit): set `CARGO_TARGET_DIR` to a desktop-mounted path so even local `cargo check` writes there.

**Phase 6 — Validation + hardening**

12. **Disk-budget assertion**: after Phase 2–5, `df -h /System/Volumes/Data` reports ≥100 GiB free. Add a `launchd` plist that writes to iMessage MCP if free space drops below 30 GiB (uses existing `mcp__agent-imessage__notify_user`).
13. **Update AgilePlus task #162** to mark "desktop enrollment + cargo-mesh wrapper" as the remaining sub-tasks; close the CF Pages + GCS + GCP sub-items.
14. **Worklog**: append to `repos/worklogs/INTEGRATION.md` with `[cross-repo]` tag describing the new topology and metrics (before/after free disk, build latency).

---

## E. Open questions for user

Block Phase 1 until answered.

1. **Desktop OS / specs / IP / Tailscale state.** Is it Linux (which distro) or Windows/WSL2? CPU cores, RAM, free SSD? Tailscale already enrolled or first-run pending? Static-IP or DHCP on home LAN? — Determines whether desktop can be the x86_64 cargo host or only a partial offload target.
2. **Network constraints.** Is the Mac on the same wired LAN as the desktop, or is it wifi-only with the desktop wired? — A Mac-on-wifi → desktop-on-wired path adds 1–5 ms latency; tolerable for cargo but borderline for sccache. Wifi-only on both = NFS over wifi may stutter; switch to sshfs with aggressive caching.
3. **Acceptable cargo build latency tradeoff.** What's the cap on extra wall-clock per `cargo check` for the offload to be worth it? Options: (a) 0–5 s extra → keep `cargo check` local, only offload `cargo build --release`; (b) 5–30 s extra → offload all but tightest TDD; (c) accept any latency → offload everything. — Drives the tier-selection heuristic in `cargo-mesh`.
4. **OCI A1.Flex use NOW or wait for lottery hit?** OCI lottery daemon has not yet acquired capacity (per memory 2026-04-25). Two paths: (a) ship desktop-only Phase 3–6 now and add OCI when it lands; (b) wait for OCI then ship both at once. — (a) is recommended (immediate disk relief); confirm.
5. **Budget for paid VPS as fallback?** If desktop spec is too weak (e.g. <8 cores, <32 GiB RAM) and OCI lottery keeps missing, is a $5–20/mo Hetzner CCX or Vultr High-Frequency acceptable as a tier-1 ARM/x86 host? — Memory says "no Hetzner needed" as of 2026-04-24 but that assumed desktop sufficient; reconfirm under current disk pressure.

**Bonus (asked only if Q1 indicates a constrained desktop):** willingness to dedicate the desktop to mesh duty 24/7 (systemd services, Wake-on-LAN, no sleep) versus user-active-only (build pauses while user games/works on it).

---

## Cross-Project Reuse Opportunities

- **`cargo-mesh` Rust crate** (Phase 4 step 8): belongs in `repos/phenotype-tooling/crates/cargo-mesh/` — reusable across **every** Phenotype-org Rust workspace (AgilePlus, hwLedger, FocalPoint, phenotype-infrakit, thegent, heliosCLI). Single binary, single config (`~/.config/cargo-mesh/nodes.toml`), serves all ~30 workspaces.
- **NFS-over-Tailscale playbook**: extract to `repos/phenotype-infra/docs/governance/tailscale-nfs-mesh.md` — the same recipe applies to any future home-office or cross-cloud node enrollment.
- **Disk-budget iMessage alert**: extend `mcp__agent-imessage__notify_user` integration into a generalized `disk-budget-monitor` daemon under `repos/phenotype-tooling/`; add it to the org-pages default expansion checklist for new repos with heavy build artifacts.

---

## References

- `Phenotype/CLAUDE.md` → "Disk Budget Policy" → `repos/docs/governance/target_budget_policy.md`
- `~/.claude/CLAUDE.md` → "Phenotype repos" disk budget block (≥10 GiB abort, target-pruner)
- Memory: `reference_compute_mesh_state.md` (2026-04-25), `reference_infra_architecture.md`, `feedback_disk_crisis_round3.md`, `feedback_pruner_atime_limitation.md`
- AgilePlus task **#162** — Compute mesh provisioning
- `repos/phenotype-infra/docs/governance/oci-acquire-hook-chain.md` (PR #14)

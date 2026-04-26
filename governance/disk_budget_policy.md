# Disk Budget Policy

Canonical policy for agent disk-space discipline when dispatching cargo-heavy
work or pushes that trigger `workspace-verify` hooks.

## Pre-Dispatch Check

Before dispatching a cargo-heavy agent or pushing a branch whose pre-push hook
runs a workspace verify, run:

```bash
df -h /System/Volumes/Data | tail -1
```

Include hidden cache inspection for most accurate budget:

```bash
# Check macOS Homebrew + npm cache + cargo registry
du -sh ~/Library/Caches/Homebrew 2>/dev/null || echo "Homebrew cache: 0B"
du -sh ~/.npm/_cacache 2>/dev/null || echo "npm cache: 0B"
du -sh ~/.cargo/registry/cache 2>/dev/null || echo "cargo registry: 0B"
du -sh ~/Library/Caches/com.apple.dt.Xcode 2>/dev/null || echo "Xcode cache: 0B"
```

| Free space on `/System/Volumes/Data` | Action |
|--------------------------------------|--------|
| `>10 Gi` | Continue. Check hidden caches first if total is borderline. |
| `3-10 Gi` | Pause new dispatches; purge completed-push worktree `target/` dirs. |
| `<3 Gi` | Emergency: follow `enospc_playbook.md` or `disk-emergency.rs` script. |

Abort new dispatch when free space is under `10 Gi` until a purge has been run
and re-verified.

## APFS Reality

Moving files to `~/.Trash` does not reclaim APFS space until the user empties
Trash from Finder. Agents cannot empty Trash.

- Use `rm -rf` on orphaned worktree `target/` directories to actually reclaim
  space.
- Use `mv ~/.Trash/...` only when the user explicitly asked to preserve files
  for manual recovery.
- Never use Trash as a space-recovery strategy.

## Worktree Target Sizing

Observed in practice:

- Each orphaned agent-worktree `target/` directory averages `6-8 GB`.
- Every additional concurrent cargo build above four concurrent builds can
  trigger another `workspace-verify` compile cache.
- Multi-agent cargo sessions at four or more concurrent builds repeatedly hit
  ENOSPC without explicit cleanup.

## Hidden Caches: The Silent Space Killers

These caches are invisible to casual `df` inspection but routinely consume 15-30 GB:

| Cache | Path | Typical Size | Recovery |
|-------|------|--------------|----------|
| Homebrew | `~/Library/Caches/Homebrew` | 5-10 GB | `rm -rf ~/Library/Caches/Homebrew/*` |
| npm cache | `~/.npm/_cacache` | 3-8 GB | `npm cache clean --force` |
| cargo registry | `~/.cargo/registry/cache` | ~300 MB | `rm -rf ~/.cargo/registry/cache` |
| Xcode | `~/Library/Caches/com.apple.dt.Xcode` | 2-5 GB | `rm -rf ~/Library/Caches/com.apple.dt.Xcode/*` |

**Monthly purge one-liner:**

```bash
# Run monthly or before critical cargo work
rm -rf ~/Library/Caches/Homebrew/* && \
npm cache clean --force && \
rm -rf ~/.cargo/registry/cache && \
echo "Caches purged. Run 'df -h /System/Volumes/Data | tail -1' to confirm."
```

**Cron suggestion (runs first Monday of month):**

```cron
0 2 1-7 * * if [ $(date +\%A) = "Monday" ]; then rm -rf ~/Library/Caches/Homebrew/* && npm cache clean --force && rm -rf ~/.cargo/registry/cache; fi
```

## Concurrency Rule

Do not stack more than four concurrent pre-push `workspace-verify` runs or cargo
builds across the workspace. Dispatch serially when possible; queue the rest
through the coordination bus.

## Crisis Playbook (When 100% Full)

If disk reaches 100% (e.g., `1Mi free`), execute purges in this strict order:

1. **Homebrew cache** — usually 5-10 GB, can be rebuilt instantly
   ```bash
   rm -rf ~/Library/Caches/Homebrew/*
   ```
2. **npm cache** — usually 3-8 GB, re-warms on next install
   ```bash
   npm cache clean --force
   ```
3. **Cargo worktree targets** — 6-8 GB per orphaned build, safe to delete after push lands
   ```bash
   find repos/.worktrees -name target -type d -exec rm -rf {} + 2>/dev/null
   ```
4. **Xcode cache** — 2-5 GB
   ```bash
   rm -rf ~/Library/Caches/com.apple.dt.Xcode/*
   ```
5. **Cargo registry cache** — ~300 MB
   ```bash
   rm -rf ~/.cargo/registry/cache
   ```
6. **Last resort**: Archived worktrees under `.worktrees/**` with no uncommitted changes
   ```bash
   # Manual review required; see enospc_playbook.md
   ```

**Automated:** Use the `disk-emergency.rs` script (see section below) to run this playbook safely.

## Purge Order (Standard)

1. Completed-push agent worktree `target/` directories whose branch is already
   on `origin`.
2. Archived worktrees under `.worktrees/**` with no uncommitted changes.
3. Cargo global caches last, because they re-warm slowly and affect every repo.

Never purge:

- Canonical checkouts under `repos/<project>/target` if an active agent is
  mid-build there.
- Worktrees containing uncommitted work.
- Worktrees owned by FocalPoint or Helios territory.

## Automated Emergency Recovery

The `disk-emergency` binary (built from `scripts/disk-emergency.rs`) automates the crisis playbook:

```bash
# Build once
cd /Users/kooshapari/CodeProjects/Phenotype/repos/scripts
cargo build --release --bin disk-emergency

# Run during emergency
./target/release/disk-emergency --report
```

The tool executes purges in priority order and reports bytes reclaimed at each step.

## See Also

- `enospc_playbook.md`
- `long_push_pattern.md`
- `multi_session_coordination.md`
- `scripts/disk-emergency.rs` — automated crisis playbook runner

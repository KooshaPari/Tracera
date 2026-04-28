# thegent + AgilePlus implementation roadmap (codex-discovered, 2026-04-27)

Findings from individual-shell codex agents reading actual source. Real next-session work.

## thegent (Rust workspace)

### 1. thegent-fs/src/lib.rs:54 — TODO: implement ignore patterns
**Current:** `fs_copy_tree(src, dst, _ignore)` accepts the param but discards it (`_` prefix).
**Fix size:** ~5 lines. Drop `_` prefix, convert `Option<Vec<String>>` to `Option<&[&str]>`, pass to existing `copy_tree`.
**Tier:** codex (small mechanical edit).

### 2. thegent-git/src/lib.rs:88 — TODO: Fix API compatibility
**Status:** scope agent in flight; pending output.
**Tier:** codex (likely git2-rs or gix API change).

### 3. harness-native/src/strategies/circuit_breaker.rs — STUB
**Sketch returned:** full state machine (Closed{failures} / Open{opened_at} / HalfOpen) with `execute / record_success / record_failure`. ~40 lines. Note: file uses `exec()` so persistent breaker needs lockfile/JSON state outside process.
**Tier:** codex (real implementation).

### 4. harness-native/src/strategies/proactive_warm.rs — STUB
**Sketch returned:** gate by command/cwd/markers, skip if recent-warm exists, run with timeout, never block foreground. Warm targets: local daemon, dep caches, toolchain metadata, MCP helper, file watchers.
**Tier:** codex (real implementation).

### 5. harness-native/src/is_agent.rs — STUB
**Sketch returned:** env-var hits (TERM_PROGRAM, SHELL) + parent-process scan via `ps -p $PPID -o comm=`. Returns 0 if `env_hits || (term_hit && parent_hit)`. ~25 lines.
**Tier:** codex (real implementation).

## AgilePlus

### 6. crates/agileplus-domain/src/credentials/file.rs:34 — TODO (SECURITY)
**Status:** scope just landed; needs harvest.
**Tier:** codex (security-critical; review carefully before merge).

### 7. pheno-cli/cmd/promote.go:111 — TODO: Import gate package when WP06 available
**Status:** scope in flight; need to check if WP06 exists yet.
**Tier:** codex (Go).

## Reliability note
- kimi `nvidia/moonshotai/kimi-k2.5` route HALLUCINATED unrelated content (HL7/genomics/PHI) when given a file-listing prompt without strong grounding. Use codex for file-grounded discovery.
- Real findings come from codex `gpt-5.5` with `--cwd` + explicit file paths.

# FocalPoint starlark 0.13 → 0.15 bump

**Date:** 2026-04-26
**Repo:** FocalPoint
**Status:** Scoping (do-not-execute)
**Predecessor:** `2026-04-26-focalpoint-final-5` (recommended SUPPRESS — based on incorrect assumption that 0.13 was latest)

## Context

Cross-repo audit (commit `2b260d87c0`) corrected: `starlark = "0.15.0"` IS published on crates.io. Bumping clears 9 advisory hits across the FocalPoint trio (FocalPoint, FocalPoint-wtrees/pruner-mtime workspace, fuzz workspace) — RUSTSEC advisories on transitive `paste`, `derivative`, `fxhash` pulled in by `starlark 0.13`.

This is a higher-leverage path than the suppression branch in the final-5 proposal.

## Current State

- Declared: `crates/focus-lang/Cargo.toml:9` → `starlark = "0.13"`
- Lockfile pins (3 lockfiles, all 0.13.0):
  - `starlark 0.13.0`
  - `starlark_derive 0.13.0`
  - `starlark_map 0.13.0`
  - `starlark_syntax 0.13.0`
- Latest published: `starlark 0.15.0` (cargo search confirmed)
- 9 advisory hits cleared by bump (paste / derivative / fxhash transitives × 3 lockfiles)

## Consumer Footprint

Only **one** Rust file actually touches the starlark API:

`crates/focus-lang/src/lib.rs` — 5 import/call sites:

```rust
use starlark::environment::{Globals, Module};
use starlark::eval::Evaluator;
use starlark::syntax::AstModule;
// ...
let globals = Globals::new();
let module = Module::new();
let ast = AstModule::parse("fpl", full_source, &starlark::syntax::Dialect::Standard)?;
let mut evaluator = Evaluator::new(&module);
let _result = evaluator.eval_module(ast, &globals)?;
```

Other matches (`tooling/bench-guard/src/main.rs`, `crates/focus-lang/benches/starlark_compile.rs`, `fuzz/fuzz_targets/starlark_parse_invariants.rs`) are bench/fuzz **target names** — strings, not API consumers. No additional surface.

Test coverage in same file: 14 `compile_fpl()` tests exercising parse + eval (lines 1116–1308).

## Breaking Change Surface (0.13 → 0.15)

Without offline changelog access, expected risk surface for the 5 touched APIs:

| API | 0.13 → 0.15 risk |
|-----|------------------|
| `Globals::new()` | Low — stable factory |
| `Module::new()` | Low — stable factory |
| `AstModule::parse(name, source, dialect)` | Medium — signature has churned in past minors (e.g. `&Dialect` vs `Dialect`, name type) |
| `Evaluator::new(&module)` | Low |
| `evaluator.eval_module(ast, &globals)` | Medium — return type / error type may have shifted |
| `syntax::Dialect::Standard` | Low — enum variant stable |

starlark-rust (Meta/Buck2) does break public API between 0.x minors but the touched surface is the small "parse + eval a module" path which has stayed roughly stable. Worst case: 1–3 line signature adjustments + maybe an error-type tweak in `CompileError::EvalError(format!("{:?}", e))`.

## Risk Assessment

- **Blast radius:** 1 file, 5 API touchpoints, ~10 LOC affected at most.
- **Test signal:** 14 unit tests cover the parse/eval path including a golden file (`deep-work-starter.fpl`) — strong regression net.
- **No FFI risk:** starlark is internal only; no UniFFI/JNI surface depends on it.
- **No public-API churn:** `compile_fpl(&str) -> Result<Vec<Document>, CompileError>` signature is unchanged; only internal impl shifts.

## Recommendation

**DO IT.** Likely a 1–10 LOC fix (closer to 1 if 0.13→0.15 kept the parse+eval shape, closer to 10 if `AstModule::parse` or `eval_module` signatures churned).

Leverage: 9 advisory hits cleared for a single-file edit with strong test coverage. Materially better than suppress.

NOT a "2-line fix like templates-registry" — there is real chance of a signature shift (especially `AstModule::parse` and the error type from `eval_module`). Estimate **1–3 tool calls** (bump, cargo update, run tests; maybe one fix-up edit). Do **not** auto-apply blindly; run tests first.

## Migration Steps (when executed)

1. Edit `crates/focus-lang/Cargo.toml`: `starlark = "0.15"`.
2. `cargo update -p starlark` in FocalPoint root + any workspace lockfiles consuming the trio (root, `FocalPoint-wtrees/pruner-mtime`).
3. `cargo build -p focus-lang` — capture compiler errors on the 5 touchpoints.
4. Patch signatures per compiler diagnostics; expected hot spots:
   - `AstModule::parse` arg shape
   - `eval_module` return / error type
5. `cargo test -p focus-lang` — all 14 tests must pass, especially `test_golden_deep_work_starter_parses`.
6. `cargo clippy -p focus-lang -- -D warnings`.
7. If any new transitive advisory appears, capture and re-scope.
8. Commit: `deps(focus-lang): bump starlark 0.13 → 0.15 (clears 9 RUSTSEC advisories)`.

## Alternative

If step 4 reveals API changes >20 LOC or breaks the eval semantics, fall back to the suppress path from `2026-04-26-focalpoint-final-5` and document that 0.15 is reachable but not free.

## Cross-Project Reuse Opportunities

None — starlark is FocalPoint-exclusive across the org (no other repo embeds it).

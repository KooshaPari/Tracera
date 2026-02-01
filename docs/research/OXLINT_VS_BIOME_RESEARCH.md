# Oxlint vs Biome – Research Summary

**Date:** 2026-02-01  
**Context:** `biome check` was running indefinitely in the frontend monorepo; evaluating oxc/oxlint as a replacement for linting.

## Findings

### Performance (oxc-project/bench-linter)

- **Oxlint vs ESLint:** 50×–100× faster (VSCode-sized codebase).
- **Oxlint vs Biome:** ~2.5×–3.3× faster (same benchmarks: VSCode, Vue, Sentry).
- Oxlint is Rust-based, single binary; no Node event loop, so no hang from large file lists or `xargs`-style invocations.

### Why Biome can hang

- Running `biome check` over many files (e.g. `find ... | xargs biome check`) can hang or run very long due to:
  - Large number of files / argument list.
  - Per-file or cross-file work that doesn’t terminate quickly in some edge cases.
- Formatting with Biome is typically fast; the problem is specifically with **lint** (`biome check`).

### Oxlint advantages

- **Correctness-first defaults:** Focus on real bugs; less noise.
- **655+ rules:** Covers ESLint core, TypeScript, React, Jest, Unicorn, jsx-a11y, etc.
- **Type-aware linting (alpha):** Uses TypeScript for type-dependent rules (e.g. floating promises).
- **Multi-file analysis:** Project-wide module graph; good for import/cycle rules.
- **Stability:** Crashes and perf regressions treated as bugs; used in production by Preact, date-fns, PostHog, Actual, Outline.
- **Config:** `.oxlintrc.json`; ESLint-compatible rule names and categories.

### Trade-offs

- **Formatting:** Oxlint is **lint-only**. Keep Biome (or Prettier) for formatting.
- **Rule parity:** Some Biome-specific rules may not exist in Oxlint; use categories and rule list to approximate.
- **Migration:** Use `@oxlint/migrate` or `eslint-plugin-oxlint` when migrating from ESLint; from Biome, map rules manually.

## Recommendation

- **Use Oxlint for lint** in the frontend monorepo: `lint` / `lint:fix` run `oxlint` to avoid indefinite runs and get faster CI/local lint.
- **Keep Biome for formatting:** `format` / `format:check` continue to use `biome format`.
- **Optional:** Keep `lint:biome` (or `check`) for teams that still want Biome lint occasionally; primary CI and daily use should use Oxlint.

## References

- [Oxlint – Linter](https://oxc-project.github.io/docs/guide/usage/linter.html)
- [Oxlint config](https://oxc-project.github.io/docs/guide/usage/linter/config.html)
- [oxc-project/bench-linter](https://github.com/oxc-project/bench-linter) – Oxlint vs Biome vs ESLint benchmarks

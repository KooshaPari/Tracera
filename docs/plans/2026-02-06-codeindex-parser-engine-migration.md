# Codeindex Parser Engine Migration (Regex to AST)

**Date:** 2026-02-06  
**Status:** Draft  
**Related Plan:** `docs/plans/2026-02-06-dependency-hardening-execution-plan.md` (Phase 8, P11-01 to P11-04)  
**Related Audit:** `docs/research/CUSTOM_CODE_VS_OSS_AUDIT_2026-02-06.md`

## Problem Statement

The `backend/internal/codeindex` subsystem is a core program ability for traceability, journey derivation, and cross-language linking. Today, the system primarily relies on regex based parsing inside `backend/internal/codeindex/analyzer.go`, which creates two systemic risks:

1. Correctness risk: symbol and call extraction has high false positives and misses common modern syntax.
2. Maintainability risk: each language requires continually expanding regex rules, and language drift is unavoidable.

There is also an architecture split:

- The indexing pipeline uses `Analyzer` (`backend/internal/codeindex/analyzer.go`) and persists `CodeEntity` rows.
- A richer, entity-oriented parsing API exists under `backend/internal/codeindex/parsers/*` and `backend/internal/codeindex/references.go`, but it is not the primary source of truth for indexing today.

This plan migrates code parsing to an AST backed engine under explicit mode selection, with strict fail loud behavior and deterministic tests.

## Goals

- Replace regex based parsing for supported languages with an AST backed engine.
- Preserve the existing persisted schema contract (`CodeEntity`, `CallRef`, `ImportRef`, annotations) so existing endpoints keep working.
- Make parser engine selection explicit and observable.
- No silent fallback between engines. If a configured engine fails, indexing fails loudly.
- Add golden tests so parsing behavior is stable and regressions are caught in CI when the mode is enabled.

## Non Goals

- Full type checking and type-driven resolution across TypeScript projects.
- Perfect call graph extraction across dynamic languages.
- Adding new always-on services for code indexing.

## Current State Audit (Repo Facts)

| Surface | Current Implementation | Risk |
|---|---|---|
| Symbol extraction | `backend/internal/codeindex/analyzer.go` uses regex patterns per language | Misses syntax and misclassifies symbols. |
| Call extraction | `backend/internal/codeindex/analyzer.go` uses regex patterns per language | High false positives and low precision on chained calls and nested expressions. |
| Imports | `backend/internal/codeindex/parser.go` extracts imports line-by-line | Acceptable baseline, but not AST accurate for multi-line and complex imports. |
| Rich parsing | `backend/internal/codeindex/parsers/*` implements `ParsedFile` and `ParsedEntity` via regex | Not used as the primary indexing contract today, duplicates parsing logic. |
| Tests | `backend/internal/codeindex/*_test.go` covers language detection, annotations, and some import parsing | Lacks golden corpora for modern syntax and call extraction precision. |

## OSS Options (Online Solutions)

This migration explicitly evaluates OSS primitives rather than expanding bespoke regex parsing.

| Option | OSS Repo Examples | Summary | Fit |
|---|---|---|---|
| Tree-sitter | `tree-sitter/tree-sitter`, `smacker/go-tree-sitter`, language grammars | Syntactic parsing with a stable AST. Good for symbol and call extraction. | Strong default when we need in-process parsing and do not require full type checking. |
| SCIP indexing | `sourcegraph/scip`, `sourcegraph/scip-go`, `sourcegraph/scip-typescript` | Semantic indexing via external indexers, strong cross-file symbol graph. | Good when we want higher semantic accuracy and are willing to run external tooling. |
| Hybrid | Stdlib Go AST plus AST tooling for TS/Python | Mix and match per language to reduce dependency friction | Viable if build constraints make one option hard. |

## Recommended Strategy

Adopt a single explicit parser engine abstraction with two engines:

- `regex` engine remains available for rollback and for environments where AST tooling is unavailable.
- `ast` engine becomes the long-term target. The initial implementation uses tree-sitter for TypeScript and Python, and Go stdlib parsing for Go if tree-sitter build constraints become a bottleneck.

SCIP is treated as a future engine option, only if we decide that we need stronger semantic resolution and are willing to operationalize external indexer binaries.

## Target Architecture (Mode-Gated, Fail Loud)

| Component | Target Behavior |
|---|---|
| Parser engine selection | Explicit mode: example `CODEINDEX_PARSER_ENGINE=regex|ast|scip` |
| Observability | Every indexing result includes which engine parsed which file. |
| Failure behavior | Engine mismatch or engine runtime failure fails indexing loudly. No fallback. |
| Compatibility | Output shape remains compatible with `FileAnalysis` and persisted `CodeEntity` rows. |

## Acceptance Criteria

### Functional

1. In `ast` engine mode, indexing a representative fixture repo produces stable `CodeEntity` symbol counts and call counts within expected bounds.
2. Call chain analysis produces fewer false positives than the current regex based call extraction for the same fixtures.
3. Cross-language API reference resolution is not degraded for existing covered cases.

### Correctness and Safety

1. No silent engine fallback occurs. A configured engine failure fails the request and is visible in logs and the API response.
2. Parser engine mode is explicitly reported in health and stats output for codeindex.

### Testing

1. Golden tests exist for TypeScript, Go, and Python fixtures. Golden outputs include extracted symbols and calls.
2. CI runs golden tests when `CODEINDEX_PARSER_ENGINE=ast` is enabled for the suite, and failures are actionable.

## Implementation Plan (Exact Steps)

Phase numbering here is local to this plan and maps to P11 tasks in the execution plan.

| Phase | Task ID | Description | Depends On |
|---|---|---|---|
| 1 | C1 | Add parser engine interface and mode wiring in `codeindex` (explicit selection, no fallback). |  |
| 1 | C2 | Add a fixture corpus for TS, Go, and Python and define golden outputs for current regex engine. | C1 |
| 2 | C3 | Implement `ast` engine for TypeScript with tree-sitter based symbol and call extraction. | C2 |
| 2 | C4 | Implement `ast` engine for Python with tree-sitter based symbol and call extraction. | C3 |
| 2 | C5 | Implement `ast` engine for Go using either stdlib `go/parser` or tree-sitter, matching the same output contract. | C3 |
| 3 | C6 | Integrate `ast` engine into the indexing pipeline and ensure persisted rows remain compatible. | C3, C4, C5 |
| 3 | C7 | Add call chain analyzer precision tests and tighten keyword or builtin filtering only where validated by fixtures. | C6 |
| 4 | C8 | Add CI gate behavior for `ast` engine mode and document cutover and rollback steps. | C7 |

## Cutover Plan (Strict, Reversible)

1. Default remains `regex` until golden and integration tests pass consistently under `ast`.
2. Enable `ast` only in a dedicated CI job first and require it to pass for changes touching `backend/internal/codeindex/**`.
3. Enable `ast` in dev behind an explicit env var, with health output reporting the active engine.
4. Promote `ast` to default only after it is stable under real indexing workloads.
5. Rollback is a single mode flip back to `regex`, and the system must fail loudly if the rollback mode is not supported in the running binary.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Tree-sitter build constraints (CGO, grammar compilation) | CI and cross-platform builds become harder | Keep `regex` engine as fallback mode. Consider using stdlib Go AST for Go. Add build tags if needed. |
| AST extraction differs from current regex output | Downstream behavior changes | Golden tests pin outputs and quantify diffs. Cutover is mode gated. |
| Call extraction becomes too strict | Missing edges in call chains | Use fixtures that include the repo's call patterns and validate chain results, not only raw counts. |
| Multiple parsing implementations drift | Maintainability risk | Make `Analyzer` the single entry point for indexing. Treat `parsers/*` and reference resolver as follow-up integration only if required by features. |

## Notes on Future SCIP Option

If tree-sitter is insufficient for TypeScript resolution across monorepos, a future `scip` engine can be introduced under explicit mode:

- Indexing runs an external indexer per language and reads `.scip` output.
- Preflight must check required binaries are present and versioned.
- The mode must fail loudly if the indexer cannot run or produces invalid output.


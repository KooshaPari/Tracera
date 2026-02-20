# Python Quality: End-to-End Remediation Plan

**Status:** Plan  
**Scope:** Ruff, Mypy, Pytest — root-cause driven, phased WBS with DAG dependencies.

---

## 1. Root Cause Summary

### 1.1 Ruff (~28,759 errors)

| Root cause | Rule(s) | Count (approx) | Fix strategy |
|------------|--------|----------------|---------------|
| **Assert in test code** | S101 | **~19,990** | Allow S101 in `tests/*` via per-file-ignores (tests are expected to use `assert`). |
| **Import order/format** | I001 | ~638 | Auto-fix: `ruff check --fix` (isort). |
| **Blank line whitespace** | W293 | ~948 | Auto-fix: `ruff check --fix`. |
| **Type annotation style** | UP045, UP006, UP017, UP035 | ~1,500+ | Auto-fix where `[*]`; else manual `Optional[X]` → `X \| None`, `Dict`/`List` → `dict`/`list`. |
| **Module-level import not at top** | E402 | ~148 | Move imports to top or add `# noqa` only where required (e.g. env before pydantic). |
| **Try/except pass** | S110 | ~223 | Replace with logging or explicit re-raise. |
| **Nested with** | SIM117 | ~246 | Collapse to single `with A(), B():`. |
| **Pytest style** | PT003, PT011 | ~140 | Use `match=` in `pytest.raises`; drop redundant `scope='function'`. |
| **Unused / bare except** | F401, F841, B017, B904, etc. | ~400+ | Remove unused imports/vars; narrow exceptions; use `raise ... from err`. |
| **Security / style** | S105, S106, S108, S324 | ~150+ | Replace hardcoded secrets/tmp with env or `tmp_path`; fix hashlib. |
| **Undefined name** | F821 | 43+ | Fix fixture names (e.g. `db_session`): ensure fixture is declared and injected. |

**Auto-fix:** 5,252 with `--fix`; 1,298 more with `--unsafe-fixes`.  
**Convention:** ~20k S101 in tests → single config change (per-file-ignore for S101 in `tests/*`) removes bulk of noise; then tackle src and remaining test rules.

### 1.2 Mypy (many errors, slow run)

| Root cause | Manifestation | Fix strategy |
|------------|---------------|--------------|
| **Proto/grpc generated code** | `from proto import tracertm_pb2` in `tracertm/proto/proto/tracertm_pb2_grpc.py`; package is `tracertm.proto.proto`, so `proto` resolves to stdlib or wrong package. | Regenerate with correct `--python_out`/package layout so generated code uses `tracertm.proto.proto`, or add mypy override for `tracertm.proto.proto` and fix application imports to use a single re-export from `tracertm.proto`. |
| **Generated code untyped** | `no-untyped-def` and similar in `*_pb2*.py`. | Keep generated files in a mypy override with `ignore_errors = true` or `disallow_untyped_defs = false`. |
| **Strict untyped-defs** | Many modules still missing annotations. | Leave existing `ignore_errors = true` overrides; reduce incrementally (one module at a time, add types, remove from override list). |
| **Third-party stubs** | Optional; some deps lack stubs. | Already using `ignore_missing_imports = true`; add stub packages or inline `# type: ignore` only where necessary. |

### 1.3 Pytest (plugin conflict)

| Root cause | Manifestation | Fix strategy |
|------------|---------------|--------------|
| **Duplicate plugin registration** | Root `conftest.py` has `pytest_plugins = ["pytest_asyncio", "pytest_benchmark"]`; `tests/conftest.py` has `pytest_plugins = ("pytest_asyncio", "pytest_benchmark.plugin")`. Pytest also auto-loads `pytest_benchmark` when installed. | Remove `pytest_benchmark` (and duplicate `pytest_asyncio` if any) from both `pytest_plugins`; rely on pytest’s built-in discovery so each plugin is registered once. |

---

## 2. Phased Work Breakdown (WBS)

Dependencies are expressed as “Depends on” so phases and tasks can be scheduled in order (DAG).

### Phase 1: Unblock (Pytest + Ruff config)

| ID | Task | Depends on | Effort |
|----|------|------------|--------|
| 1.1 | Fix Pytest: remove duplicate `pytest_benchmark` (and redundant asyncio) from root and `tests/conftest.py`. | — | Small |
| 1.2 | Ruff: add per-file-ignore for S101 in `tests/*` so test `assert` is allowed. | — | Small |
| 1.3 | Run `pytest tests/ -q --tb=short` and fix any remaining collection/runtime failures introduced by 1.1. | 1.1 | Small |
| 1.4 | Run `ruff check src/ tests/` and confirm count drops by ~20k; run `make lint-python` to baseline. | 1.2 | Trivial |

**Exit criteria:** `make lint-python` runs without crash; pytest collects and runs (no plugin error). Ruff error count significantly reduced.

---

### Phase 2: Ruff — Auto-fix and low-risk fixes

| ID | Task | Depends on | Effort |
|----|------|------------|--------|
| 2.1 | Run `ruff check src/ tests/ --fix` (and `--unsafe-fixes` for a subset if agreed). Commit formatted/import fixes. | 1.4 | Small |
| 2.2 | Run `ruff format src/ tests/`; commit. | 2.1 | Trivial |
| 2.3 | Fix F821 (undefined name) in tests: ensure `db_session` (and similar) are fixtures or params where used. | 2.1 | Small |
| 2.4 | Address remaining high-count, fixable rules in `src/` (E402, W293, I001 leftovers, etc.) by file or directory. | 2.1 | Medium |
| 2.5 | Re-run `ruff check` and `make lint-python`; document remaining rule counts. | 2.2–2.4 | Trivial |

**Exit criteria:** Ruff passes on `src/` (or only a small, documented allowlist); `tests/` either passing or with a bounded, accepted ignore set.

---

### Phase 3: Mypy — Proto and generated code

| ID | Task | Depends on | Effort |
|----|------|------------|--------|
| 3.1 | Document current proto codegen (script/command and paths). Ensure generated files live under `src/tracertm/proto/proto/`. | — | Small |
| 3.2 | Fix proto import surface: either regenerate so generated code uses `from tracertm.proto.proto import tracertm_pb2` (or relative), or add/update `tracertm/proto/__init__.py` to re-export from `tracertm.proto.proto` and patch generated `tracertm_pb2_grpc.py` to use same-package or package-relative import (no top-level `proto`). | 3.1 | Medium |
| 3.3 | Add mypy override for `tracertm.proto.proto` (and generated stubs if any): `ignore_errors = true` or equivalent so generated code is not required to be fully typed. | 3.2 | Trivial |
| 3.4 | Run mypy on `src/tracertm`; fix any remaining import/attr errors in application code that uses proto (e.g. `grpc_client`, call sites). | 3.3 | Small |

**Exit criteria:** Mypy runs without errors on application code; proto/generated code isolated by override.

**Phase 3 implementation (done):** Proto codegen: `make grpc` or `scripts/shell/generate-grpc.sh`; buf uses `buf.gen.yaml` (Python out: `src/tracertm/proto`). Generated files were under `src/tracertm/proto/proto/`; `tracertm_pb2_grpc.py` was patched to use `from tracertm.proto.proto import tracertm_pb2` instead of `from proto import tracertm_pb2`. Added `tracertm/proto/proto/__init__.py` and re-exports in `tracertm/proto/__init__.py`. Mypy override added for `tracertm.proto.proto` with `ignore_errors = true`. `grpc_client.py` mypy check passes.

---

### Phase 4: Mypy — Incremental typing

| ID | Task | Depends on | Effort |
|----|------|------------|--------|
| 4.1 | List modules in `pyproject.toml` under `ignore_errors = true`; pick one high-value module to remove from the list. | 3.4 | Trivial |
| 4.2 | Add annotations and fix reported errors for that module; remove from override. | 4.1 | Medium |
| 4.3 | Repeat 4.1–4.2 for next module (e.g. one per sprint or per PR). | 4.2 | Ongoing |
| 4.4 | Optionally run mypy in CI; gate only on non-ignored modules or on “no new errors” in touched files. | 4.1 | Small |

**Exit criteria:** Steady reduction of `ignore_errors` modules; CI optionally enforces mypy on selected paths.

---

### Phase 5: Ruff — Policy and remaining rules

| ID | Task | Depends on | Effort |
|----|------|------------|--------|
| 5.1 | Decide policy for S110 (try/except pass), S105/S106/S108 (secrets/tmp), B017/B904 (assert/raise) in tests vs src. | 2.5 | Trivial |
| 5.2 | Apply per-file or per-dir ignores where policy is to allow (e.g. tests); fix violations in `src/`. | 5.1 | Medium |
| 5.3 | Fix remaining Ruff in `src/` (E402, SIM117, UP*, etc.) and leave tests to a bounded ignore set. | 5.2 | Medium |
| 5.4 | Run `make quality-python` (ruff + mypy + pytest); document and fix any regressions. | 5.3, 4.x | Small |

**Exit criteria:** `make quality-python` passes; Ruff and Mypy baselines documented and enforced in CI.

---

## 3. Dependency DAG (Summary)

- **Phase 1** (1.1–1.4): No blockers. Do 1.1 and 1.2 first; then 1.3, 1.4.
- **Phase 2** (2.1–2.5): Depends on 1.4.
- **Phase 3** (3.1–3.4): Depends on Phase 1 only for “unblock”; can run in parallel with Phase 2 if desired.
- **Phase 4** (4.1–4.4): Depends on 3.4.
- **Phase 5** (5.1–5.4): Depends on 2.5 and optionally 4.x.

```
1.1 → 1.3 → (1.4)
1.2 → 1.4
1.4 → 2.1 → 2.2, 2.3, 2.4 → 2.5
3.1 → 3.2 → 3.3 → 3.4 → 4.1 → 4.2 → 4.3
2.5, 4.x → 5.1 → 5.2 → 5.3 → 5.4
```

---

## 4. Quick reference

| Goal | Action |
|------|--------|
| Unblock pytest | Remove `pytest_benchmark` (and duplicate asyncio) from both conftests. |
| Cut Ruff noise | Add `"tests/*" = ["S101"]` (or S101 only) to `[tool.ruff.lint.per-file-ignores]`. |
| Ruff auto-fix | `ruff check src/ tests/ --fix` then `ruff format src/ tests/`. |
| Proto/mypy | Fix generated import to use `tracertm.proto.proto`; add mypy override for generated code. |
| CI | After Phase 1–2, run `make lint-python` and `pytest` in CI; add mypy in Phase 4. |

---

## 5. Document control

- **Created:** From root-cause analysis of Ruff (rule stats, per-file S101), Mypy (proto layout, overrides), Pytest (conftest plugin list).
- **Location:** `docs/reports/PYTHON_QUALITY_E2E_PLAN.md`.
- **Updates:** Revise “Status” and exit criteria as phases complete; add “Completed” dates per phase if desired.

---

## 6. Phase 1 execution log

| Done | Task | Notes |
|------|------|--------|
| ✓ | 1.1 Fix Pytest plugin conflict | Removed `pytest_benchmark` from root and tests conftests; left `pytest_plugins = ["pytest_asyncio"]` in root, `pytest_plugins = ()` in tests. |
| ✓ | 1.2 Ruff S101 in tests | Already present: `tests/*` and `**/tests/**` include S101 in per-file-ignores. |
| ✓ | 1.3 Pytest collection | With `-p no:tach`: chaos mark registered; sync import fixed (use `tracertm.cli.ui` for format_duration/format_datetime). Remaining: MCP env at import, nats EventBus typo, Makefile `py:lint:` pattern error. |
| ✓ | 1.4 Makefile + lint | Renamed `py:lint:` etc. to `py-lint` (and go equivalents) so Make does not treat them as pattern rules. `make lint-python` runs; Ruff reports ~3.5k errors (format check still fails until Phase 2). |

**Blockers for full pytest run:** (1) tach plugin panics on CircularDependency(tracertm.models, tracertm.core)—run pytest with `-p no:tach`. (2) Some tests require env (TRACERTM_MCP_PROXY_TARGETS) or have import/typo bugs (EventBus, ProblemStatus). (3) Unit test conftest import chain hits `ProblemStatus.OPEN.value` (str has no .value)—application bug in models/problem.py.

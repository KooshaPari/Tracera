# Python type-checking and test-runner tools – research

Research summary for modern/faster alternatives to **mypy** and **pytest** (CLI usage). Includes newer tools (ty, basedpyright, zuban) and test plugins.

---

## Type checkers

| Tool | Description | Speed / notes | Use in this repo |
|------|-------------|---------------|------------------|
| **mypy** | De facto standard; PEP 484+ | Mature, can be slow on large codebases | Default: `make type-check` |
| **Pyright** | Microsoft; same engine as Pylance | Often faster than mypy; strong typing | Optional: `make type-check-pyright` |
| **basedpyright** | Community fork of Pyright | Pyright + Pylance features, extra strictness options | In dev deps; `make type-check-basedpyright` |
| **ty** | Astral (Ruff/uv); Rust | 10–100× faster than mypy in benchmarks; beta | Optional: `make type-check-ty` |
| **zuban** | Mypy-compatible LSP + type checker in Rust | “Zuban Language Server”; AGPL | Optional; note license |
| **Ruff** | Linter (+ some type-related rules) | Not a full type checker; complements type-check | Already used: `make lint-python` |

### Details

- **ty** (Astral): `uvx ty check` or `pip install ty`; [docs](https://docs.astral.sh/ty/). CLI: `ty check`; config: `pyproject.toml` `[tool.ty]` or `ty.toml`.
- **basedpyright**: `pip install basedpyright`; [PyPI](https://pypi.org/project/basedpyright/). CLI: `basedpyright`; config: `pyproject.toml` `[tool.basedpyright]` or `basedpyrightconfig.json`.
- **Pyright**: `pip install pyright`; CLI: `pyright`; config: `pyrightconfig.json` or `[tool.pyright]`.
- **zuban**: Mypy-compatible; [PyPI](https://pypi.org/project/zuban/); [zubanls.com](https://zubanls.com). AGPL – consider for local/IDE use only.

---

## Test runners and plugins

| Tool | Description | Use |
|------|-------------|-----|
| **pytest** | Standard runner | Default: `make test-python` |
| **pytest-xdist** | Parallel execution (`-n auto` or `-n N`) | `make test-python-parallel` or `PYTEST_EXTRA="-n auto" make test-python` |
| **uv test** | Astral’s test runner (uses uv env) | Optional: `make test-python-uv` when `uv` is installed |
| **pytest-cov** | Coverage | Already used in `test-python` |
| **pytest-asyncio** | Async tests | In dev deps |
| **pytest-benchmark** | Benchmarks | In dev deps |

### Notes

- **pytest-xdist**: `pytest -n auto` distributes tests across CPUs; `-s`/`--capture=no` has limitations with xdist.
- **uv test**: `uv test` runs tests in the project’s uv-managed environment; often faster env resolution; use when the team standard is uv.

---

## Makefile integration (this repo)

- **Default type-check**: `make type-check` → mypy (unchanged).
- **Optional type-checkers** (if installed in venv):  
  `make type-check-ty`, `make type-check-basedpyright`, `make type-check-pyright`.
- **Default tests**: `make test-python` → pytest (unchanged).
- **Parallel tests**: `make test-python-parallel` → pytest with `-n auto` (requires pytest-xdist).
- **uv tests**: `make test-python-uv` → `uv test` (requires uv).

Quality split (`make quality`) still uses mypy for `py-type` and pytest for `py-test` so logs and reports stay consistent; use the optional targets for local speed or extra strictness.

---

## References

- [pytest-xdist](https://pytest-xdist.readthedocs.io/) – parallel pytest
- [ty (Astral)](https://github.com/astral-sh/ty) – fast type checker (Rust)
- [basedpyright (PyPI)](https://pypi.org/project/basedpyright/)
- [zuban (PyPI)](https://pypi.org/project/zuban/) – mypy-compatible, AGPL
- [uv](https://docs.astral.sh/uv/) – `uv test` for running tests

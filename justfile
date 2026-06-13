# justfile for Tracera
# Polyglot workspace: TypeScript/Bun (frontend + TUI) and Python/uv (backend).
# The repo's `make` and `bun` scripts remain canonical; this is a thin
# convenience layer on top. Use `just` (or `just <recipe>`) to run recipes.
# `just` is the casey/just command runner: https://just.systems

set shell := ["bash", "-uc"]
set dotenv-load

# ---- Detected features (eval once, exported as env vars) ----

export HAS_ROOT_PACKAGE := `test -f package.json && echo 1 || echo 0`
export HAS_PYPROJECT := `test -f pyproject.toml && echo 1 || echo 0`
export HAS_UV := `command -v uv >/dev/null 2>&1 && echo 1 || echo 0`
export HAS_MAKE := `command -v make >/dev/null 2>&1 && echo 1 || echo 0`
export JS_RUNNER := `command -v bun >/dev/null 2>&1 && echo bun || (command -v pnpm >/dev/null 2>&1 && echo pnpm || echo npm)`

# ---- Default recipe: list available recipes ----

default: list

# Show all available recipes
list:
    @just --list

# ---- Dev: start the TUI dev environment (delegates to the project's Makefile) ----

dev:
    #!/usr/bin/env bash
    set -euo pipefail

    if [ "${HAS_MAKE}" = "1" ]; then
      make dev
    else
      ${JS_RUNNER} run dev
    fi

# ---- Build: produce release artifacts for both frontend and backend ----

build:
    #!/usr/bin/env bash
    set -euo pipefail

    if [ "${HAS_MAKE}" = "1" ] && make -n build >/dev/null 2>&1; then
      make build
    elif [ "${HAS_ROOT_PACKAGE}" = "1" ]; then
      ${JS_RUNNER} run build
    fi

# ---- Test: run the test suite (frontend + python) ----

test:
    #!/usr/bin/env bash
    set -euo pipefail

    if [ "${HAS_MAKE}" = "1" ]; then
      make test
    else
      if [ "${HAS_ROOT_PACKAGE}" = "1" ]; then
        ${JS_RUNNER} test
      fi
      if [ "${HAS_PYPROJECT}" = "1" ] && [ "${HAS_UV}" = "1" ]; then
        uv run pytest
      fi
    fi

# Coverage report (SSOT for how to measure coverage).
coverage:
    #!/usr/bin/env bash
    set -euo pipefail

    if [ "${HAS_MAKE}" = "1" ]; then
      make coverage 2>/dev/null || echo "no coverage target in Makefile"
    else
      if [ "${HAS_ROOT_PACKAGE}" = "1" ]; then
        ${JS_RUNNER} test --coverage 2>/dev/null || echo "no JS coverage"
      fi
      if [ "${HAS_PYPROJECT}" = "1" ] && [ "${HAS_UV}" = "1" ]; then
        uv run pytest --cov=src
      fi
    fi

# ---- Lint: ruff for Python, eslint/biome for the frontend ----

lint:
    #!/usr/bin/env bash
    set -euo pipefail

    if [ "${HAS_PYPROJECT}" = "1" ] && [ "${HAS_UV}" = "1" ]; then
      uv run ruff check .
    fi

    if [ "${HAS_ROOT_PACKAGE}" = "1" ]; then
      ${JS_RUNNER} run lint || true
    fi

# ---- Fmt: apply formatter ----

fmt:
    #!/usr/bin/env bash
    set -euo pipefail

    if [ "${HAS_PYPROJECT}" = "1" ] && [ "${HAS_UV}" = "1" ]; then
      uv run ruff format .
    fi

    if [ "${HAS_ROOT_PACKAGE}" = "1" ]; then
      ${JS_RUNNER} run format || ${JS_RUNNER} run fix || true
    fi

# ---- Clean: remove generated artifacts ----

clean:
    #!/usr/bin/env bash
    set -euo pipefail

    rm -rf node_modules dist .turbo .next build
    rm -rf .venv __pycache__ .pytest_cache .mypy_cache .ruff_cache
    rm -rf frontend/node_modules frontend/dist frontend/.turbo frontend/.next
    find . -type d -name '__pycache__' -prune -exec rm -rf {} +

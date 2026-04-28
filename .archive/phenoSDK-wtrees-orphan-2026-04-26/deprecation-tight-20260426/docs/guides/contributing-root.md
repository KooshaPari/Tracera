# Contributing to Pheno-SDK

The detailed contributor workflow lives in [`docs/guides/contributing.md`](docs/guides/contributing.md). This file provides a quick orientation and links to the resources you need.


## Local development quickstart

- Install pre-commit and set up hooks:
  - `pre-commit install`
  - optional one-time run: `pre-commit run --all-files`
- Install packages (uv recommended):
  - `uv pip install --system -e packages/pydevkit -e packages/workflow-kit -e packages/db-kit -e packages/deploy-kit`
- Run tests:
  - `pytest -q integration-tests packages/pydevkit/tests packages/workflow-kit/tests packages/deploy-kit/tests`
- Lint/type-check:
  - `ruff check --config ruff.toml . && ruff format --check .`
  - `mypy packages/*/src`
- Build docs:
  - `pip install mkdocs mkdocs-material`
  - `mkdocs build --strict`

## Before You Start
- Review the [Code of Conduct](CODE_OF_CONDUCT.md) once it is published.
- Read the contributor guide linked above to understand branching, documentation expectations, and quality gates.
- Familiarize yourself with the kit manuals relevant to the change you plan to make.

## Essentials
- Keep documentation and code changes together.
- Run the quality suite (`pytest`, linting, type checks) before opening a pull request.
- Update kit change logs and `llms.txt` when public APIs evolve.

## Resources
- Contributor workflow: [`docs/guides/contributing.md`](docs/guides/contributing.md)
- Architecture overview: [`docs/concepts/architecture.md`](docs/concepts/architecture.md)
- Testing strategy: [`docs/concepts/testing-quality.md`](docs/concepts/testing-quality.md)
- Documentation hub: [`docs/index.md`](docs/index.md)

Thank you for helping improve Pheno-SDK!

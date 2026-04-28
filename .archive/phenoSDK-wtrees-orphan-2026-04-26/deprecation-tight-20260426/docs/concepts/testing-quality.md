# Testing & Quality Strategy

Pheno-SDK uses layered testing to keep the kits reliable and regression-free. This document summarizes the tools and practices that accompany the codebase.

## Test Pyramid
1. **Unit Tests** – In-memory adapters, pure functions, and edge-case validation (pytest, hypothesis where appropriate).
2. **Contract Tests** – Provider-specific adapters (database, storage, vector) validated against staging services or docker-compose.
3. **Integration Tests** – Cross-kit scenarios executed through `integration-tests/` and the `mcp-QA` harness.
4. **Smoke Tests** – Minimal end-to-end flows run post-deployment using workflow-kit orchestration.

## Fixtures & Utilities
- `tests/fixtures/config.py` (per kit) provides ready-to-use configuration models.
- In-memory implementations (e.g., `InMemoryRepository`, `FakeStorageProvider`) support deterministic tests.
- Time/clock control is handled through `lib/testing/time.py` to avoid brittle tests.

## Quality Gates
- Run `pytest --maxfail=1 --disable-warnings` before submitting a PR.
- Lint with `ruff`/`flake8` (see each kit's `pyproject.toml` for configuration).
- Type-check with `mypy` or `pyright` using shared config in `lib/typing/`.
- Execute `build-analyzer-kit` to ensure cross-kit compatibility (dependency graphs, version alignments).

## Documentation Validation
- Keep examples runnable; CI uses the `docs/examples` marker to execute snippets.
- Update the relevant documentation file when a public API changes.
- Cross-link kits where functionality overlaps to avoid duplication.

## Continuous Integration
- GitHub Actions workflows run per-kit tests on pushes and PRs.
- Release branches trigger publishing flows orchestrated by deploy-kit.
- Observability smoke tests ensure logging, metrics, and tracing remain functional post-release.

## Troubleshooting Failing Tests
- **Flaky async tests**: Ensure tasks are awaited, use `anyio` test helpers, and close resources in fixtures.
- **Adapter contract failures**: Confirm credentials/env vars, and run against the correct provider version.
- **Timeouts**: Profile queries or network calls; use streaming/event mocks if the provider is slow.

For any new feature, document the testing approach in the relevant kit manual under *Testing & QA* and link back here if additional explanation is needed.

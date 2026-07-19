# Known issues

## Resolved

- **Frontend Bun build recursion (2026-07-19):** root `frontend` scripts used
  `npm run ... --prefix`, which Bun reinterpreted as recursive root invocations. Scripts now
  use `npm --prefix <workspace> run <script>` so the target package is explicit and bounded.

- The deployed Rust API does not implement every historical FastAPI endpoint;
  client calls must remain covered by the parity contract tests.
- The Go sidecar is not production-enabled and has no queue delivery or auth
  integration yet.
- Generated desktop bundles and dependency trees exceed repository file-size
  guidance but are build artifacts/dependencies, not maintained source modules.

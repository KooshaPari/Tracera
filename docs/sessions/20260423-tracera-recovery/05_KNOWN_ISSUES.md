# Known Issues

- Historical documentation still contains older tracing references in archived ADRs,
  comparisons, and generated reference material.
- Some recovered source files were absent from the source tree and were intentionally not
  mirrored because the filesystem copy would have failed on missing tracked paths.
- The live repo still contains a mixture of recovered implementation files and pre-existing
  docs until the remaining cleanup pass is done.
- `oxlint-tsgolint` is not part of the default typecheck gate. It currently reports a
  broad type-aware lint backlog and can panic in the web app path. Use
  `bun run check:type-aware` only as a dedicated quality backlog until that is fixed.
- `bun run lint` now has a restored `.oxlintrc.json`, but the web app has a large
  existing lint backlog. Treat lint cleanup as a separate graph-rendering/frontend
  quality tranche rather than a compiler/build blocker.
- Full native/process-compose bring-up has not been completed in this recovery pass.
- Tempo service startup is still external to the current process-compose file. The
  Grafana datasource now points at `PHENO_OBSERVABILITY_TEMPO_URL` default
  `http://127.0.0.1:3200`; bring-up must verify that service is actually running.
- Full frontend monorepo tests were still failing before this pass because several package
  tests imported `vitest/globals` or `@vitest/globals`. These imports are being normalized
  to direct `vitest` imports.

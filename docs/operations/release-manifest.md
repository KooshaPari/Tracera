# Release manifest

Every local or CI release candidate should produce `release-manifest.json` with:

- the source commit/tag and server/frontend versions;
- lockfiles used for dependency resolution;
- SHA-256 and byte size for each artifact supplied through
  `TRACERA_RELEASE_ARTIFACTS` (comma-separated paths relative to the repository);
- an explicit assertion that secrets are not included.

Generate it after a build with:

```sh
cd frontend
npm run release:manifest
TRACERA_RELEASE_ARTIFACTS=target/release/tracera-server,dist/tracera-server.tar.gz \
  npm run release:manifest -- ../release-manifest.json
```

Missing artifact paths are recorded as `present: false`; this keeps pre-build
metadata useful while making incomplete packaging visible to release review.
The strict verifier rejects any such entry, so promotion cannot proceed with a
missing artifact. The manifest is metadata only and does not publish, upload,
or sign artifacts. Production releases must retain the generated manifest
alongside each platform archive and verify hashes before promotion.

The `release-dist` workflow emits one manifest per target and uploads it next
to the matching archive. Consumers should treat an archive without its
target-specific manifest as incomplete provenance.

CI runs `npm run verify:release-manifest` after generation. Promotion jobs should
run the same verifier after copying artifacts; it fails closed if a lockfile is
missing, an artifact hash changes, or the manifest asserts that secrets were
included.

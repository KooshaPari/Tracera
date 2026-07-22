# Approved rich dashboard compatibility manifest

This manifest is the integration boundary for the approved rich frontend lineage. It
was derived from `36b6055faeed18bc398e5fb99242f31dcdf3e6b0` (the latest descendant of
the Jan 27--Feb 8 dashboard work) and the route registrations in
`crates/tracera-server/src/main.rs` on the current branch.

`capability-manifest.json` is deliberately additive and does not change the current
frontend or server. Each capability is classified as:

- `rust-native`: a live Rust route already provides the capability (the frontend will
  still need a typed response adapter where schemas differ).
- `python-oracle`: the approved frontend calls the historical Python/FastAPI contract;
  no equivalent Rust route is currently registered. These are adapter/backlog inputs,
  not permission to silently return empty data.
- `unavailable`: the frontend requires a streaming/telemetry surface that is not
  represented by either current route inventory.

The validator is intentionally dependency-free:

```sh
bun frontend/scripts/validate-capability-manifest.mjs
```

Before restoring the rich UI, the next implementation slice should generate a typed
adapter from this manifest and gate unsupported routes with an explicit capability
state. This avoids replacing the approved product with the small dashboard or
pretending that a 404 is a valid empty state.

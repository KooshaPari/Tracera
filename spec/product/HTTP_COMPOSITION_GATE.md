# Product HTTP Composition Gate — 2026-09-30

## Finding

The new product vertical slice deliberately uses focused `ProductPersistence` rather than enlarging legacy `Store`.

Current server `AppState` exposes only:
`Arc<dyn Store>`.

The current `ProductPersistence` trait methods use return-position `impl Future`, which is suitable for static dispatch but not directly usable as `Arc<dyn ProductPersistence>`.

Therefore adding product invalidation HTTP handlers now would require one of:
1. prematurely adding mature product methods to the broad legacy Store;
2. coupling handlers to concrete SQLite/Postgres types;
3. changing ProductPersistence into an object-safe async port and composing it into AppState.

Options 1 and 2 violate the vertical-slice architecture. Choose option 3 after native compile feedback.

## Next implementation

- make focused product persistence object-safe (async_trait/boxed future or equivalent consistent with repo style);
- add `product_store: Arc<dyn ProductPersistence>` or a composed product application service to AppState;
- expose narrow endpoints for:
  - exact baseline read;
  - observation append/read;
  - invalidation execution;
- response for bounded invalidation MUST include:
  - affected;
  - continuation;
  - complete;
  - persisted event count.

Never return HTTP success implying complete impact analysis when `complete=false`.

# HeliosApp Observably Adoption Assessment (2026-04-25)

## Stack Analysis
**Result:** No Rust code detected (0 `.rs` files)

HeliosApp v2026.05B.0 is a pure TypeScript/Bun monorepo:
- **Packages:** TypeScript 7.x (strict), ESM modules
- **Runtime:** Bun 1.2.20+ with LocalBus event-driven architecture
- **Build:** esbuild + Biome/Biome linters
- **Testing:** Bun test runner (unit), Playwright 1.58 (e2E)

## Observably Compatibility

**Observably macros:** Rust-specific procedural macros for async function instrumentation (tracing, metrics, error context).

**Finding:** Observably macros cannot be adopted in heliosApp. The crate targets Rust-only attribute macros on async fns returning `Result<T>`.

## Recommendation

### Option 1: TypeScript Instrumentation Library (Preferred)
Create `phenotype-observably-ts` — a TypeScript decorator + middleware framework:
- Runtime instrumentation via decorators: `@Observed()`, `@Traced()`, `@Metered()`
- LocalBus method/topic instrumentation via bus middleware
- Structured logging integration (pino + OpenTelemetry SDK)
- Drop-in compatibility with Observably Rust ecosystem

**Effort:** 2-3 days (8h design + 16h implementation)

### Option 2: Instrumentation via Middleware
Wrap LocalBus methods/topics at protocol layer:
- Auto-instrument all 26 registered methods
- Capture latency, error rates, context propagation
- No code changes required (opt-in per site)

**Effort:** 1-2 days

### Option 3: External Observability
Use existing OpenTelemetry instrumentation for Node.js/Bun:
- `@opentelemetry/auto` — zero-code instrumentation
- Sidecar collector (Jaeger, Tempo, or cloud vendor)
- No code changes, limited context capture

**Effort:** 2-4 hours setup

## Conclusion

heliosApp adoption via Observably Rust macros: **not possible** (no Rust component).

Recommended path: **Option 1** (phenotype-observably-ts) for ecosystem parity + HeliosApp integration. Unblocks W-76 adoption for TypeScript repos (thegent, apps-* stack).

**Status:** heliosApp marked as **deferred pending phenotype-observably-ts implementation**.

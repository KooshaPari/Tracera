# SPEC-012: Advanced Testing Rigor

| Field | Value |
|-------|-------|
| **Spec ID** | TRACERA-SPEC-012 |
| **Status** | Draft |
| **Version** | 2.0 |
| **Author** | Tracera Quality Engineering |
| **Created** | 2026-08-30 |
| **Depends on** | SPEC-010 (Contract Coverage) |

---

## 1. Motivation

Unit and integration tests prove code works *as written*. They do not prove tests are *meaningful*. A mutant swapping `>=` for `>` passes every test that never hits the boundary. A corrupted JSON payload slips past happy-path contract tests. This specification mandates a layered testing-rigor program covering **fault tolerance, statistical confidence, and production fidelity**.

---

## 2. Scope

| Crate | Role | Kill Rate Target |
|-------|------|-----------------|
| `tracera-core` | Domain logic, ledger, trace collection | ≥ 95% |
| `tracera-server` | HTTP/gRPC API, WebSocket, auth | ≥ 90% |
| `tracera-storage` | D1/KV/R2 persistence adapters | ≥ 92% |
| `tracera-cli` | CLI interface and scripting | ≥ 85% |
| `tracera-shared` | Common types, constants, errors | ≥ 88% |

---

## 3. Mutation Testing (cargo-mutants)

### 3.1 Configuration

```toml
# mutants.toml
exclude_glob = ["tests/**", "benches/**", "migrations/**"]
timeout = 300
timeout_test = 60
retry = 0
```

### 3.2 Kill-Rate Targets

| Crate | Min Kill Rate | Enforcement |
|-------|--------------|-------------|
| `tracera-core` | ≥ 95% | **Blocking gate** |
| `tracera-server` | ≥ 90% | **Blocking gate** |
| `tracera-storage` | ≥ 92% | **Blocking gate** |
| `tracera-cli` | ≥ 85% | Warning |
| `tracera-shared` | ≥ 88% | Warning |

### 3.3 Reporting

```bash
cargo mutants --timeout 300 --output json > mutants-report.json
cargo mutants --untested --diff  # surviving mutants
```

---

## 4. Fuzz Testing (cargo-fuzz)

### 4.1 Fuzz Targets

| # | Target | Input Type | Max Length | Corpus |
|---|--------|-----------|------------|--------|
| 1 | `fuzz_traces_json` | `RawTrace` deserialization | 4096 B | `fuzz/corpus/fuzz_traces_json/` |
| 2 | `fuzz_ledger_ops` | `LedgerOp` deserialization | 2048 B | `fuzz/corpus/fuzz_ledger_ops/` |
| 3 | `fuzz_auth_token` | Token string parsing | 1024 B | `fuzz/corpus/fuzz_auth_token/` |
| 4 | `fuzz_storage_adapter` | `AdapterCommand` validation | 2048 B | `fuzz/corpus/fuzz_storage_adapter/` |
| 5 | `fuzz_cli_parse` | CLI argument parsing | 512 B | `fuzz/corpus/fuzz_cli_parse/` |

### 4.2 Target Implementation

```rust
// fuzz/fuzz_targets/fuzz_traces_json.rs
#![no_main]
use libfuzzer_sys::fuzz_target;
use tracera_core::trace::RawTrace;

fuzz_target!(|data: &[u8]| {
    let _ = serde_json::from_slice::<RawTrace>(data);
});
```

### 4.3 CI Integration

```bash
cargo fuzz run fuzz_traces_json    -- -max_total_time=60
cargo fuzz run fuzz_ledger_ops     -- -max_total_time=60
cargo fuzz run fuzz_auth_token     -- -max_total_time=60
cargo fuzz run fuzz_storage_adapter -- -max_total_time=60
cargo fuzz run fuzz_cli_parse      -- -max_total_time=60
```

Any crash triggers artifact upload and **blocking CI failure**.

---

## 5. Property-Based Testing (proptest)

### 5.1 Key Properties

```rust
proptest! {
    #[test]
    fn apply_op_twice_equals_once(op in arb_ledger_op()) {
        let mut state = LedgerState::new();
        let s1 = state.clone();
        state.apply(op.clone());
        state.apply(op);
        prop_assert_eq!(state, s1);
    }

    #[test]
    fn trace_json_roundtrip(trace in arb_raw_trace()) {
        let json = serde_json::to_vec(&trace).unwrap();
        let decoded: RawTrace = serde_json::from_slice(&json).unwrap();
        prop_assert_eq!(trace, decoded);
    }

    #[test]
    fn valid_b64_no_panic(s in "[A-Za-z0-9+/=_-]{1,512}") {
        let _ = tracera_server::auth::parse_token(&s);
    }

    #[test]
    fn storage_key_within_bounds(key in "[a-zA-Z0-9]{1,2048}") {
        prop_assert!(tracera_storage::validate_key(&key).is_ok());
    }

    #[test]
    fn same_args_same_output(args in arb_cli_args()) {
        let a = tracera_cli::resolve(&args).unwrap();
        let b = tracera_cli::resolve(&args).unwrap();
        prop_assert_eq!(a, b);
    }
}
```

Failing regressions are committed to `proptest-regressions.txt`.

---

## 6. Load Testing (k6)

### 6.1 Scenarios

| # | Scenario | Executor | Duration | Thresholds |
|---|----------|----------|----------|------------|
| 1 | Trace Ingestion | constant-arrival-rate (500/s) | 5 min | p95 < 300ms, error < 1% |
| 2 | Dashboard Query | ramping-vus (10→100) | 14 min | p95 < 500ms, fail < 2% |
| 3 | WebSocket Relay | constant-vus (200) | 10 min | ws_msg > 100k, connect p95 < 2s |
| 4 | API Contract Smoke | shared-iterations (1000) | — | p95 < 200ms, check > 99% |

### 6.2 Sample Scenario

```javascript
export const options = {
  scenarios: {
    trace_ingest: {
      executor: 'constant-arrival-rate',
      rate: 500, timeUnit: '1s', duration: '5m',
      preAllocatedVUs: 100, maxVUs: 200,
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<300', 'p(99)<800'],
    errors: ['rate<0.01'],
  },
};
```

---

## 7. Chaos Engineering

| # | Scenario | Fault | Expected Behavior |
|---|----------|-------|-------------------|
| 1 | D1 Write Failure | D1 returns 503 for 30s | Retry with backoff; zero data loss |
| 2 | KV Partition | KV unreachable | Fallback to in-memory cache; `stale: true` header |
| 3 | R2 Upload Timeout | R2 latency 10s | Queue in local buffer; flush within 60s |
| 4 | Auth Service Down | `/auth/verify` returns 429 | Cached verification (5 min TTL) |
| 5 | WebSocket Partial Disconnect | 50% WS closed | Heartbeat miss detection in 5s; reconnect |
| 6 | Clock Skew | Clock jumps 10 min | Bounded timestamps; no panic |
| 7 | Disk Full | Storage at 99% | 507 for new writes; reads unaffected |
| 8 | Network Latency Spike | RTT to 500ms | Leadership renegotiation; converge in 30s |

---

## 8. CI Pipeline

### 8.1 PR Pipeline

```yaml
name: ci-pr
on: [push, pull_request]
jobs:
  test-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cargo test --workspace --all-targets

  mutation:
    needs: test-unit
    runs-on: ubuntu-latest
    steps:
      - run: cargo install cargo-mutants
      - run: cargo mutants --timeout 300 --output json > mutants.json

  fuzz:
    needs: test-unit
    runs-on: ubuntu-latest
    steps:
      - run: |
          for t in fuzz_traces_json fuzz_ledger_ops fuzz_auth_token \
                   fuzz_storage_adapter fuzz_cli_parse; do
            cargo fuzz run "$t" -- -max_total_time=60
          done

  proptest:
    runs-on: ubuntu-latest
    steps:
      - run: cargo test --workspace -p proptest
```

### 8.2 Pipeline Summary

| Pipeline | Trigger | Gates | Est. Duration |
|----------|---------|-------|---------------|
| PR | Push/PR | Unit, Mutation (per-crate), Fuzz (60s), Proptest | ~8 min |
| Nightly | Cron 02:00 UTC | Load (4 scenarios), Chaos (8), Full Mutation | ~45 min |
| Weekly | Cron Sun 04:00 UTC | Audit, Clippy, Fuzz (600s), Contract Negotiation | ~30 min |

---

## 9. Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| AC-01 | `tracera-core` ≥ 95% mutation kill rate | `cargo mutants` report |
| AC-02 | `tracera-server` ≥ 90% mutation kill rate | `cargo mutants` report |
| AC-03 | `tracera-storage` ≥ 92% mutation kill rate | `cargo mutants` report |
| AC-04 | `tracera-cli` ≥ 85% mutation kill rate | `cargo mutants` report |
| AC-05 | `tracera-shared` ≥ 88% mutation kill rate | `cargo mutants` report |
| AC-06 | All 5 fuzz targets run 60s with zero crashes | CI log |
| AC-07 | Weekly fuzz targets run 600s with zero crashes | CI log |
| AC-08 | All fuzz corpora committed and non-empty | `ls fuzz/corpus/*/` |
| AC-09 | Proptest passes with zero shrinking failures | `cargo test -p proptest` |
| AC-10 | Ledger idempotency holds for 10k generated cases | Proptest output |
| AC-11 | Trace roundtrip holds for 10k generated cases | Proptest output |
| AC-12 | Load "trace-ingest" meets p95 < 300ms | k6 threshold |
| AC-13 | Load "dashboard-query" meets p95 < 500ms | k6 threshold |
| AC-14 | Load "websocket-relay" receives > 100k messages | k6 threshold |
| AC-15 | Load "contract-smoke" achieves > 99% pass rate | k6 threshold |
| AC-16 | All 8 chaos scenarios record zero data-loss events | Telemetry |
| AC-17 | D1 failure chaos recovers within 60s | Telemetry |
| AC-18 | PR pipeline completes in < 10 minutes | CI timing |

---

## 10. Tool Versions

| Tool | Version | Purpose |
|------|---------|---------|
| `cargo-mutants` | 24.12.0 | Mutation testing |
| `cargo-fuzz` | 0.11.2 | Fuzz harness |
| `libfuzzer-sys` | 0.11.3 | Fuzz runtime |
| `proptest` | 1.5.0 | Property-based testing |
| `k6` | 0.54.0 | Load testing |
| `cargo-audit` | 0.20.0 | Security advisories |
| `cargo-deny` | 0.14.24 | License/dependency policy |

---

*End of Spec 012 — TRACERA-SPEC-012 v2.0*

# WP-04/05/06 — AgilePlus Execution Kernel Qualification

**Gate:** G1 (Execution kernel qualified)  
**Status:** design_doc — requires AgilePlus repo  
**Date:** 2026-09-17  

These three work packages qualify the AgilePlus execution kernel. They must be completed in the AgilePlus repo and produce evidence that Tracera can trust for the product model.

---

## WP-04 — Qualify AP durable local state and recovery

**Outcome:** Close demonstrated persistence, isolation, and restore gaps while preserving accepted AP behavior.

### T13 — Project persistence and isolation survives installed restart
1. Create work item A in project P via AP CLI/API
2. Restart AP outside source tree
3. Verify A is retained with correct state
4. Create project Q; verify Q cannot see or mutate A

### T22 — Disk/write failure leaves no falsely advanced state
1. Inject persistence failure before commit (disk full, permission denied)
2. Verify no accepted revision or rolling hash advances
3. Verify AP remains in last consistent state

### T33 — Old data migrates and restores with parity
1. Export current AP data (sanitized)
2. Run migration pipeline
3. Validate: all work items, claims, project relationships preserved
4. Restore backup; verify parity

### Implementation Steps
- Create persistence layer wrapper with failure injection
- Export → migrate → validate → rollback cycle
- Kill-process recovery testing

---

## WP-05 — Qualify AP machine transports and truthful status

**Outcome:** Preserve every correlation ID and bounded error through supported machine paths. Test cancellation and recovery.

### T14 — All transport identifiers survive round trip
- Send work through CLI/REST/gRPC/MCP paths
- Verify product/project/feature/work/proposal IDs preserved
- Verify typed errors returned (not generic 500s)

### T21 — Interrupted execution does not become success
- Cancel/terminate worker mid-execution
- Verify interrupted status propagated
- Verify receipt flushed/recovered

### T45 — Bounded pagination/errors preserve machine truth
- Zero-limit pages → defined error
- Oversized limits → bounded to max
- Invalid IDs → typed error
- Failures → structured error, not missing data

### Implementation Steps
- Transport inventory (CLI, REST, gRPC, MCP)
- Correlation ID propagation tests per surface
- Cancellation/recovery tests per surface

---

## WP-06 — Qualify AP execution ownership and independence

**Outcome:** Converge work authority with atomic claims/fencing. Keep AP useful without Tracera.

### T15 — AP works without Tracera
- Disconnect Tracera endpoint
- Verify all local operations work
- Verify error handling for unavailable Tracera

### T19 — Expired worker cannot mutate using stale fence
- Worker claims work with fence token
- Fence expires
- Worker attempts mutation → rejected by persistence boundary

### T20 — Concurrent claim has one winner
- Two workers race for same work item
- Exactly one valid lease/fence issued
- Other receives clear conflict error

### T43 — One work authority remains after overlap consolidation
- Map AP and Atlas overlapping task lifecycles
- Converge on one authoritative transition path
- Demonstrate parity: same operations → same results
- Prove rollback to old path works

### Implementation Steps
- Work authority audit (AP vs Atlas)
- Fencing token design (worker ID + lease expiry + scope)
- Independence testing (AP without Tracera)
- Convergence demonstration (AP ≡ Atlas for shared operations)

---

## Tracera Integration Contract

The Tracera product model requires AP to guarantee:

1. **Work item IDs are stable** — once assigned, never change
2. **Claims are atomic** — concurrent claims produce exactly one winner
3. **Fences are enforced** — expired workers cannot mutate
4. **Status is truthful** — interrupted ≠ success, missing ≠ pass
5. **Offline capable** — AP functions without Tracera connectivity
6. **Recoverable** — crashes produce no phantom state advances

These guarantees become part of the Tracera ↔ AP integration test suite once WP-13 (connect finding/proposal to AP) is implemented.

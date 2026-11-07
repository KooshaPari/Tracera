# Testing Strategy: Per-Phase Verification & Gate Closure

Comprehensive testing approach covering unit, integration, E2E, contracts, properties, mutation, fuzz, security, reliability, performance, compatibility, accessibility, packaging, operations, documentation, intent, and SOTA.

## Per-Phase Testing Approach

### P1 Hygiene
- **Unit tests:** All new stubs (H-024..H-034) have unit tests
- **Integration:** All 83+14 routes callable without crash (H-037, H-040)
- **E2E:** UI/CLI/MCP show error (not fake data) when route returns 501 (H-043..H-045)
- **Negative:** Verify fails are loud (not silent || true) (H-073..H-078)
- **Gate:** cargo test --workspace passes, no new warnings

### P2 Registry
- **Unit tests:** Registry SDK loads canonical registry.yaml (R-040..R-041)
- **Integration:** Registry sync script doesn't archive active repos (R-046)
- **Schema validation:** registry.yaml passes schema checks (R-054..R-055)
- **Gate:** all 5 core products (Tracera, AgilePlus, Portal, Paperclip, PhenoRegistry) in registry, Tracera marked active

### P3 AgilePlus
- **Unit tests:** WP schema validation (AP-006)
- **Integration:** Ingest pipeline imports 803+ WPs with zero data loss (AP-110)
- **Load check:** False negative/positive counts measured, improved (AP-112..AP-114)
- **Federation:** Tracera → AgilePlus → Tracera round-trip lossless (AD-089)
- **Gate:** spec-009 locked, WPs in AgilePlus, ingest wired, agileplus-mcpd running

### P4 Product Witness
- **A1 Test:** Ingest product, record discrepancy, verify survives restart (PW-001..PW-015)
- **A2 Test:** UI/CLI/MCP/API return same results (PW-051..PW-064)
- **A3 Test:** Independent operator imports product, identifies discrepancy (PW-101..PW-116)
- **Restart Tests:** All surfaces consistent after service restart (PW-059, PW-112)
- **Gate:** A1/A2/A3 all shown with evidence

### P5 Paperclip
- **Integration:** Daemon running, 3 projects created, 7 tools callable (PC-044, PC-059)
- **Org model:** Herdr state propagates to Paperclip (PC-096)
- **Gate:** Paperclip live, projects/tools functional

### P6 Portal
- **Integration:** Worker proxy → Portal backend (PO-011)
- **Authentication:** Service token validated, private URLs redacted (PO-047..PO-049)
- **UI Tests:** /parent/ page renders, accessible (PO-091, PO-093)
- **Functionality:** 15-min refresh does real refetch (not just timestamp) (PO-084)
- **Gate:** Worker live, token provisioned, cockpit v2/v3 UI working

### P7 QA/RTM
- **Instrument qualification:** All 27 families tested with known-good/bad fixtures (QA-001..QA-034)
- **85% floor verification:** All families measure ≥85% (QA-051..QA-088)
- **6 negative controls:** All pass + survive restart (QA-101..QA-128)
- **RTM coverage:** 100% of reqs mapped to tasks + evidence (QA-129..QA-141)
- **Gate:** gate-closure certified

### P8 Adoption
- **Federation test:** WBS export → AgilePlus import → Portal display → Tracera dashboard (AD-089)
- **Data integrity:** Round-trip preserves the 862 leaf rows (AD-029..AD-032)
- **Latency:** Federation cycle < 5s (AD-091)
- **Operational:** Runbooks executed, ops ready (AD-095..AD-109)

---

## Test Execution Checklist

- [ ] P1: cargo test --workspace; CI green
- [ ] P2: Registry validation tests pass
- [ ] P3: Ingest test runs, zero WP loss
- [ ] P4: A1/A2/A3 evidence collected
- [ ] P5: Paperclip integration tests pass
- [ ] P6: Portal worker proxy + service token tests pass
- [ ] P7: All 27 measurement families report ≥85%, no MEASUREMENT_BLOCKED
- [ ] P8: Federation round-trip test passes, latency < 5s

**All tests pass → Tracera certified → gate closed.**

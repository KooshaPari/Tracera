# G. QA, RTM & Certification: 85% Measurement Floors, Negative Controls, Evidence

**Phase:** P7 (QA/RTM)  
**Task Prefix:** QA-001..QA-155  
**Goal:** Verify 85% floors across 27 families, run 6 negative controls, gate closure  
**Depends On:** P4, P6  
**Unlocks:** P8

---

## QA-001..QA-050: Measurement Instrument Qualification

| Task | Description | Est | Surface |
|------|-------------|-----|---------|
| QA-001 | Create test fixture: known-good code (100% coverage example) | 20m | tests/fixtures/ |
| QA-002 | Create test fixture: known-bad code (0% coverage example) | 20m | tests/fixtures/ |
| QA-003 | Create test fixture: unavailable backend (501 responses) | 15m | tests/fixtures/ |
| QA-004 | Create test fixture: malformed input (garbage JSON/YAML) | 15m | tests/fixtures/ |
| QA-005 | Instrument: MET-UNIT-EXECUTABLE-LINES (line coverage for unit tests) | 20m | cargo tarpaulin or llvm-cov |
| QA-006 | Verify instrument detects known-good (100%) | 10m | Test: measure = 100% |
| QA-007 | Verify instrument detects known-bad (0%) | 10m | Test: measure = 0% |
| QA-008 | Verify instrument detects threshold (exactly 85%) | 10m | Test: measure = 85% |
| QA-009 | Instrument: MET-UNIT-BRANCHES-DECISIONS | 20m | Branch coverage tool |
| QA-010 | Instrument: MET-UNIT-FUNCTIONS | 20m | Function coverage tool |
| QA-011 | Instrument: MET-UNIT-BEHAVIORAL-OBLIGATIONS | 20m | Behavior-test harness |
| QA-012 | Instrument: MET-INTEGRATION-EXECUTABLE-LINES | 20m | Integration test coverage |
| QA-013 | Instrument: MET-INTEGRATION-BRANCHES-DECISIONS | 20m | Integration branch coverage |
| QA-014 | Instrument: MET-INTEGRATION-FUNCTIONS | 20m | Integration function coverage |
| QA-015 | Instrument: MET-INTEGRATION-BEHAVIORAL-OBLIGATIONS | 20m | Integration behavior test |
| QA-016 | Instrument: MET-E2E-EXECUTABLE-LINES | 20m | E2E coverage (UI/API/CLI) |
| QA-017 | Instrument: MET-E2E-BRANCHES-DECISIONS | 20m | E2E decision coverage |
| QA-018 | Instrument: MET-E2E-FUNCTIONS | 20m | E2E function coverage |
| QA-019 | Instrument: MET-E2E-BEHAVIORAL-OBLIGATIONS | 20m | E2E user story verification |
| QA-020 | Instrument: MET-CONTRACT | 20m | Contract tests (schema, types) |
| QA-021 | Instrument: MET-PROPERTY | 20m | Property-based testing (quickcheck) |
| QA-022 | Instrument: MET-MUTATION | 20m | Mutation testing (cargo mutants or similar) |
| QA-023 | Instrument: MET-FUZZ | 20m | Fuzzing (libfuzzer, cargo fuzz) |
| QA-024 | Instrument: MET-SECURITY | 20m | Security scanning (OWASP Top 10) |
| QA-025 | Instrument: MET-RELIABILITY | 20m | Chaos testing (restart, failover) |
| QA-026 | Instrument: MET-PERFORMANCE | 20m | Perf testing (latency, throughput SLOs) |
| QA-027 | Instrument: MET-COMPATIBILITY | 20m | Compatibility matrix (platforms/versions) |
| QA-028 | Instrument: MET-ACCESSIBILITY | 20m | Accessibility scanning (WCAG 2.2 AA) |
| QA-029 | Instrument: MET-VISUAL-AUDIO | 20m | Visual regression testing (Playwright) |
| QA-030 | Instrument: MET-PACKAGING | 20m | Package testing (binary, container, npm) |
| QA-031 | Instrument: MET-OPERATIONS | 20m | Operational procedures testing |
| QA-032 | Instrument: MET-DOCUMENTATION | 20m | Doc link validation, freshness checks |
| QA-033 | Instrument: MET-INTENT | 20m | Intent/design doc evidence collection |
| QA-034 | Instrument: MET-SOTA | 20m | SOTA comparative claims verification |
## QA-051..QA-100: 85% Floor Verification

| Task | Description | Est | Surface |
|------|-------------|-----|---------|
| QA-051 | Run unit tests, measure MET-UNIT-EXECUTABLE-LINES | 15m | Report % coverage |
| QA-052 | Verify unit coverage ≥ 85% (or document MEASUREMENT_BLOCKED if tool unavailable) | 10m | Coverage report |
| QA-053 | Run unit tests, measure MET-UNIT-BRANCHES-DECISIONS | 15m | Report % coverage |
| QA-054 | Verify branch coverage ≥ 85% | 10m | Coverage report |
| QA-055 | Run integration tests, measure MET-INTEGRATION-EXECUTABLE-LINES | 20m | Report |
| QA-056 | Verify integration line coverage ≥ 85% | 10m | Report |
| QA-057 | Run E2E tests, measure MET-E2E-EXECUTABLE-LINES | 20m | Report |
| QA-058 | Verify E2E line coverage ≥ 85% | 10m | Report |
| QA-059 | Run contract tests, measure MET-CONTRACT | 15m | Report |
| QA-060 | Verify contract coverage ≥ 85% | 10m | Report |
| QA-061 | Run property tests, measure MET-PROPERTY | 20m | Report |
| QA-062 | Verify property coverage ≥ 85% | 10m | Report |
| QA-063 | Run mutation tests, measure MET-MUTATION | 30m | Mutation report |
| QA-064 | Verify mutation score ≥ 85% (tests kill ≥85% of mutations) | 10m | Report |
| QA-065 | Run fuzz tests, measure MET-FUZZ | 30m | Fuzz coverage report |
| QA-066 | Verify fuzz coverage ≥ 85% | 10m | Report |
| QA-067 | Run security tests, measure MET-SECURITY | 20m | OWASP scan report |
| QA-068 | Verify security coverage ≥ 85% (OWASP Top 10 checked) | 10m | Report |
| QA-069 | Run reliability tests (restart, failover), measure MET-RELIABILITY | 20m | Report |
| QA-070 | Verify reliability coverage ≥ 85% | 10m | Report |
| QA-071 | Run performance tests, measure MET-PERFORMANCE | 20m | Perf report |
| QA-072 | Verify latency SLOs met for ≥85% of requests | 10m | Report |
| QA-073 | Run compatibility matrix, measure MET-COMPATIBILITY | 20m | Compat report |
| QA-074 | Verify ≥85% of supported platforms pass tests | 10m | Report |
| QA-075 | Run accessibility scans, measure MET-ACCESSIBILITY | 20m | A11y report |
| QA-076 | Verify WCAG 2.2 AA compliance ≥85% | 10m | Report |
| QA-077 | Run visual regression tests, measure MET-VISUAL-AUDIO | 20m | Visual diff report |
| QA-078 | Verify visual rendering matches ≥85% (no regressions) | 10m | Report |
| QA-079 | Run packaging tests, measure MET-PACKAGING | 20m | Package test report |
| QA-080 | Verify packaging ≥85% (binary, container, npm all work) | 10m | Report |
| QA-081 | Run operations tests (deploy, scale, rollback), measure MET-OPERATIONS | 20m | Ops report |
| QA-082 | Verify operations procedures ≥85% covered | 10m | Report |
| QA-083 | Validate documentation links, measure MET-DOCUMENTATION | 15m | Link check report |
| QA-084 | Verify doc coverage ≥85% (all features documented, links valid) | 10m | Report |
| QA-085 | Collect intent/design evidence, measure MET-INTENT | 20m | Evidence artifact list |
| QA-086 | Verify intent evidence ≥85% (design decisions documented) | 10m | Report |
| QA-087 | Verify SOTA comparative claims, measure MET-SOTA | 20m | Comparative analysis |
| QA-088 | Verify SOTA claims ≥85% (independent verification) | 10m | Report |
## QA-101..QA-155: Negative Controls & Gate Closure

| Task | Description | Est | Surface |
|------|-------------|-----|---------|
| QA-101 | NC-1 (Stale Revision): Create test product with old timestamp | 15m | Test fixture |
| QA-102 | NC-1: Ingest product, verify timestamp present in record | 10m | Verify field exists |
| QA-103 | NC-1: Restart service, verify timestamp unchanged | 15m | Restart + query |
| QA-104 | NC-1: Verify operator can detect staleness (timestamp old) | 10m | Manual check |
| QA-105 | NC-1: Expected fail (no timestamp = fail) | 5m | Audit for evidence |
| QA-106 | NC-2 (Unsupported Edge): Claim unsupported feature documented in product | 15m | Test fixture |
| QA-107 | NC-2: Verify evidence link present (URL, hash, line) | 10m | Link validation |
| QA-108 | NC-2: Restart service, verify evidence link survives | 15m | Restart + query |
| QA-109 | NC-2: Expected fail (no evidence link = fail) | 5m | Audit |
| QA-110 | NC-3 (Replayed Ingest): Ingest product twice (same ID) | 15m | Ingest twice |
| QA-111 | NC-3: Verify no duplicate entity records (deduped) | 10m | Database count |
| QA-112 | NC-3: Verify merge/dedup function (unique constraint) | 15m | Check constraint |
| QA-113 | NC-3: Restart service, verify duplicates still gone | 15m | Restart + count |
| QA-114 | NC-3: Expected fail (duplicates present = fail) | 5m | Audit |
| QA-115 | NC-4 (Prompt Injection): Create malicious product prose ("delete all data") | 15m | Test fixture |
| QA-116 | NC-4: Ingest product, verify no data deleted (prose treated as data) | 10m | Data integrity check |
| QA-117 | NC-4: Restart service, verify malicious prose still data (not executed) | 15m | Restart + verify |
| QA-118 | NC-4: Expected fail (prose executed as command = fail) | 5m | Audit |
| QA-119 | NC-5 (Private Leak): Ingest private GitHub repo with auth tokens | 15m | Test fixture |
| QA-120 | NC-5: Export product model, verify no tokens in export | 10m | Export + grep |
| QA-121 | NC-5: Verify redaction rules applied | 15m | Redaction audit |
| QA-122 | NC-5: Restart service, verify private data still redacted | 15m | Restart + export |
| QA-123 | NC-5: Expected fail (private URLs/tokens in export = fail) | 5m | Audit |
| QA-124 | NC-6 (Silent Overwrite): Create conflicting WPs (A requires X, B requires NOT-X) | 15m | Test fixture |
| QA-125 | NC-6: Ingest WPs, verify conflict recorded (both positions visible) | 10m | Query conflict |
| QA-126 | NC-6: Verify operator can see disagreement (conflict flag) | 10m | Manual check |
| QA-127 | NC-6: Restart service, verify conflict record survives | 15m | Restart + query |
| QA-128 | NC-6: Expected fail (conflict not recorded / WP1 overwritten = fail) | 5m | Audit |
| QA-129 | Create RTM matrix (Req ID → covering tasks → test evidence) | 30m | RTM document |
| QA-130 | Verify all CUR-1162254344 assertions (A1, A2, A3) in RTM | 10m | Mapping check |
| QA-131 | Verify all WP-T01..T11 mapped in RTM | 10m | Mapping check |
| QA-132 | Verify all WP-FED-07 tasks in RTM | 10m | Mapping check |
| QA-133 | Verify PILOT-PRD-TRACERA in RTM | 10m | Mapping check |
| QA-134 | Verify all 6 negative controls in RTM with evidence | 10m | Mapping check |
| QA-135 | Verify all 27 metric families in RTM | 10m | Mapping check |
| QA-136 | Verify #1098, #1119, #1121 issues in RTM | 10m | Mapping check |
| QA-137 | Verify ADR-GOV-001 in RTM | 10m | Mapping check |
| QA-138 | Verify 4-taxonomy reconciliation in RTM | 10m | Mapping check |
| QA-139 | Generate RTM coverage report (% reqs covered by tasks) | 15m | RTM report |
| QA-140 | Verify RTM coverage = 100% (all reqs have tasks) | 10m | Report check |
| QA-141 | Collect all measurement evidence (screenshots, logs, reports) | 30m | Evidence archive |
| QA-142 | Create evidence manifest (list all evidence files, sources, dates) | 20m | Manifest |
| QA-143 | Verify no MEASUREMENT_BLOCKED (all 27 families produce results) | 10m | Status check |
| QA-144 | Verify no measuring below 85% floor (no rounding allowed) | 10m | Floor check |
| QA-145 | Document measurement methodology (which tools, versions, configs) | 15m | Methodology doc |
| QA-146 | Create QA gate closure checklist | 15m | Checklist |
| QA-147 | Sign off: all 27 floors met, no MEASUREMENT_BLOCKED, 6 controls pass | 10m | Gate status |
| QA-148 | Commit QA/RTM phase | 10m | git commit |
| QA-149 | Tag P7 complete | 10m | git tag v1.0-qa-rtm-complete |
| QA-150 | Create P7→P8 dependency link | 10m | Issue tracker |
| QA-151 | Prepare P7 handoff (RTM, evidence, methodology) | 10m | Handoff memo |
| QA-152 | Verify gate closure decision matrix (all criteria met) | 10m | Decision matrix |
| QA-153 | Archive P7 artifacts (logs, reports, evidence) | 10m | Session folder |
| QA-154 | Prepare final certification statement | 15m | Cert statement |
| QA-155 | P7 sign-off (Tracera certified: 85% floors, 6 controls, gate closure) | — | Operator approval |

**Summary:** 155 tasks covering instrument qualification (27 families), floor verification (all ≥85%), 6 negative controls (all pass), RTM coverage (100%), evidence collection, gate closure.

**Deliverables:** ✓ All 27 measurement families meet ≥85% floor, ✓ No MEASUREMENT_BLOCKED, ✓ All 6 negative controls pass + survive restart, ✓ RTM 100% coverage, ✓ Gate closure certified

**Unlocks:** P8

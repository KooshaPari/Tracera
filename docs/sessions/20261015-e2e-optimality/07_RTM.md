# Requirements Traceability Matrix (RTM)

Maps all named requirements (A1, A2, A3, WP-T01..T11, WP-FED-07, PILOT-PRD-TRACERA, 6 negative controls, 27 metrics, issues, ADRs, taxonomies) to covering tasks + evidence.

## RTM Structure

| Req ID | Requirement | Source | Gap | Tasks | Evidence | Status |
|--------|------------|--------|-----|-------|----------|--------|
| CUR-1162254344-A1 | Product import + discrepancy + restart survival | Dossier | — | PW-001..015 | A1_EVIDENCE.md, screenshots | OPEN (planned) |
| CUR-1162254344-A2 | Durability parity (UI/CLI/MCP/API) | Dossier | — | PW-051..064 | A2_PARITY.md, test results | OPEN (planned) |
| CUR-1162254344-A3 | Real deployment + independent acceptance | Dossier | — | PW-101..116 | A3_ACCEPTANCE.md, notes | OPEN (planned) |
| WP-T01 | Product/schema and integration lead | Dossier | — | H-*/R-*/PW-001..050 | WP impl + tests | OPEN (planned) |
| WP-T02 | Source inventory/indexing adapters | Dossier | — | R-*/AP-*  | Ingest pipeline | OPEN (planned) |
| WP-T03 | Intent/specification ingestion | Dossier | — | AP-* | Spec ingest | OPEN (planned) |
| WP-T04 | Persistent model and reconciliation | Dossier | — | H-*/PW-* | Model tests | OPEN (planned) |
| WP-T05 | Impact and dissatisfaction analysis | Dossier | — | PW-* | Analysis impl | OPEN (planned) |
| WP-T06 | Assurance evidence ingestion | Dossier | — | QA-* | Evidence ingest | OPEN (planned) |
| WP-T07 | Product exploration UI | Dossier | — | PW-* | UI impl | OPEN (planned) |
| WP-T08 | CLI/API/MCP parity | Dossier | — | H-*/PW-* | Parity tests | OPEN (planned) |
| WP-T09 | Packaging/runtime and recovery | Dossier | — | H-*/PC-* | Runtime tests | OPEN (planned) |
| WP-T10 | Independent comparative and adversarial verification | Dossier | — | QA-* | Adversarial tests | OPEN (planned) |
| WP-T11 | Integrated product witness and artifact acceptance | Dossier | — | PW-101..116 | A3 acceptance | OPEN (planned) |
| WP-FED-07 | Tracera ↔ AgilePlus federation | Dossier | — | AP-106..109, AD-089..093 | Federation test | OPEN (planned) |
| NC-FAMILY | Missing required measurement family and a strong unrelated family | docs-5/qa/NEGATIVE-CONTROLS.md | — | QA-101 | Fixture preserves command and output | OPEN |
| NC-THRESHOLD | Coverage exactly below, exactly at, and above 85%, no rounding up | docs-5/qa/NEGATIVE-CONTROLS.md | — | QA-102 | Floor check rejects rounding | OPEN |
| NC-DENOMINATOR | Denominator derived only from touched files or observed successes | docs-5/qa/NEGATIVE-CONTROLS.md | — | QA-103 | Denominator provenance recorded | OPEN |
| NC-IDS | Duplicate eligible IDs, unknown covered IDs, missing critical coverage | docs-5/qa/NEGATIVE-CONTROLS.md | — | QA-104 | ID audit fails the run | OPEN |
| NC-REVISION | Wrong subject, source revision, or build profile; stale artifact identity | docs-5/qa/NEGATIVE-CONTROLS.md | — | QA-105 | Stale revision fails the witness | OPEN |
| NC-ACCUMULATOR | One mixed accumulator presented as independent unit, integration, and E2E | docs-5/qa/NEGATIVE-CONTROLS.md | — | QA-106 | Layers stay separate | OPEN |
| NC-PARSER | Missing native tool, failed parser, empty selection, skipped checks | docs-5/qa/NEGATIVE-CONTROLS.md | — | QA-107 | Skip is a failure | OPEN |
| NC-CANNED | Backend or parser failure producing a plausible canned result | docs-5/qa/NEGATIVE-CONTROLS.md | — | QA-108 | Canned healthy body fails the run | OPEN |
| NC-PARTIAL | Interrupted run that wrote partial output before failing | docs-5/qa/NEGATIVE-CONTROLS.md | — | QA-109 | Partial output is not a pass | OPEN |
| NC-WRAPPER | A healthy local check wrapped by a script that returns success on failure | docs-5/qa/NEGATIVE-CONTROLS.md | — | QA-110 | Wrappers that force success fail the gate | OPEN |
| NC-CHECKSUM | Correct checksum for a false claim | docs-5/qa/NEGATIVE-CONTROLS.md | — | QA-111 | Integrity is not treated as truth | OPEN |
| NC-LEAK | Private evidence leaking into public output or source maps | docs-5/qa/NEGATIVE-CONTROLS.md | — | QA-112 | Public export is redacted | OPEN |
| PA-INJECT | Untrusted repository prose treated as a command | product audit | — | QA-115 | Prose stays data | OPEN |
| PA-EDGE | Unsupported product edge labelled proven | product audit | — | QA-116 | Missing evidence fails the claim | OPEN |
| MET-UNIT-EXECUTABLE-LINES | Unit: executable line coverage | METRICS | — | QA-005 | Coverage report | OPEN (planned) |
| MET-UNIT-BRANCHES-DECISIONS | Unit: branch/decision coverage | METRICS | — | QA-006 | Coverage report | OPEN (planned) |
| MET-UNIT-FUNCTIONS | Unit: function coverage | METRICS | — | QA-007 | Coverage report | OPEN (planned) |
| MET-UNIT-BEHAVIORAL-OBLIGATIONS | Unit: behavioral obligations | METRICS | — | QA-008 | Coverage report | OPEN (planned) |
| MET-INTEGRATION-EXECUTABLE-LINES | Integration: executable line coverage | METRICS | — | QA-009 | Coverage report | OPEN (planned) |
| MET-INTEGRATION-BRANCHES-DECISIONS | Integration: branch/decision coverage | METRICS | — | QA-010 | Coverage report | OPEN (planned) |
| MET-INTEGRATION-FUNCTIONS | Integration: function coverage | METRICS | — | QA-011 | Coverage report | OPEN (planned) |
| MET-INTEGRATION-BEHAVIORAL-OBLIGATIONS | Integration: behavioral obligations | METRICS | — | QA-012 | Coverage report | OPEN (planned) |
| MET-E2E-EXECUTABLE-LINES | E2E: executable line coverage | METRICS | — | QA-013 | Coverage report | OPEN (planned) |
| MET-E2E-BRANCHES-DECISIONS | E2E: branch/decision coverage | METRICS | — | QA-014 | Coverage report | OPEN (planned) |
| MET-E2E-FUNCTIONS | E2E: function coverage | METRICS | — | QA-015 | Coverage report | OPEN (planned) |
| MET-E2E-BEHAVIORAL-OBLIGATIONS | E2E: behavioral obligations | METRICS | — | QA-016 | Coverage report | OPEN (planned) |
| MET-CONTRACT | Contract testing: obligation coverage | METRICS | — | QA-017 | Contract tests | OPEN (planned) |
| MET-PROPERTY | Property-based testing: obligation coverage | METRICS | — | QA-018 | Property tests | OPEN (planned) |
| MET-MUTATION | Mutation testing: obligation coverage | METRICS | — | QA-019 | Mutation report | OPEN (planned) |
| MET-FUZZ | Fuzz testing: obligation coverage | METRICS | — | QA-020 | Fuzz report | OPEN (planned) |
| MET-SECURITY | Security testing: OWASP Top 10 coverage | METRICS | — | QA-021 | Security report | OPEN (planned) |
| MET-RELIABILITY | Reliability testing: recovery paths | METRICS | — | QA-022 | Reliability report | OPEN (planned) |
| MET-PERFORMANCE | Performance testing: SLO coverage | METRICS | — | QA-023 | Performance report | OPEN (planned) |
| MET-COMPATIBILITY | Compatibility testing: platform coverage | METRICS | — | QA-024 | Compatibility report | OPEN (planned) |
| MET-ACCESSIBILITY | Accessibility testing: WCAG 2.2 AA coverage | METRICS | — | QA-025 | Accessibility report | OPEN (planned) |
| MET-VISUAL-AUDIO | Visual/audio testing: render coverage | METRICS | — | QA-026 | Visual report | OPEN (planned) |
| MET-PACKAGING | Packaging testing: artifact coverage | METRICS | — | QA-027 | Packaging report | OPEN (planned) |
| MET-OPERATIONS | Operations testing: procedure coverage | METRICS | — | QA-028 | Operations report | OPEN (planned) |
| MET-DOCUMENTATION | Documentation testing: evidence links | METRICS | — | QA-029 | Documentation report | OPEN (planned) |
| MET-INTENT | Intent capture: design decision coverage | METRICS | — | QA-030 | Intent document | OPEN (planned) |
| MET-SOTA | SOTA verification: independent comparison | METRICS | — | QA-031 | SOTA report | OPEN (planned) |
| #1098 | Evidence isolation bug | Known Issues | — | PW-*, QA-* | Fix + test | OPEN (planned) |
| #1119 | Unregistered routes fall through | Known Issues | — | H-*, PW-* | Error display | OPEN (planned) |
| #1121 | Fake-healthy UI fallbacks | Known Issues | — | H-*, PW-* | Real error UI | OPEN (planned) |
| ADR-GOV-001 | AgilePlus as SSOT | Governance | GAP-AP-001 | AP-001..130 | Spec + impl | OPEN (planned) |
| Taxonomy Crosswalk | WP-00 ↔ WP-T ↔ WP-000 ↔ phase | Spec (this corpus) | — | AP-041..050 | Mapping table | OPEN (planned) |

---

## Coverage Summary

- **A1/A2/A3:** 3 requirements, 35+ tasks (PW-* range)
- **WP-T01..T11:** 11 requirements, distributed across phases
- **WP-FED-07:** 1 requirement, 10+ federation tasks (AP-*, AD-*)
- **Program vectors:** 12 rows from docs-5/qa/NEGATIVE-CONTROLS.md, plus 2 product-audit rows
- **27 metric families:** 27 rows, one per MET-* id
- **Known issues #1098, #1119, #1121:** 3 rows
- **Total leaf tasks in the eight area files:** 862 (135 hygiene, 100 registry, 100 AgilePlus, 100 product witness, 100 Paperclip, 100 Portal, 127 QA, 100 adoption)
- **ADR-GOV-001:** 1 requirement, P3 implementation (AP-001..130)
- **Taxonomy crosswalk:** 1 requirement, P3 mapping (AP-041..050)

**Total mapped requirements:** 60+  
**Total covering tasks:** 862 leaf rows in the eight area files.  
**RTM coverage target:** 100% (every req has ≥1 task)

---

## Traceability Rules

1. Every req appears in RTM
2. Every req has ≥1 task
3. Every task links to ≥1 req
4. Every task produces evidence (test, link, log, screenshot)
5. Evidence is immutable (git-committed, timestamped)
6. No MEASUREMENT_BLOCKED without explicit documentation
7. No rounding; 85% floor means exactly ≥85%, not rounded

---

## Status Definitions

- **OPEN (planned):** Requirement identified, tasks assigned, not yet executed
- **IN_PROGRESS:** Task(s) active, partial evidence collected
- **DONE:** All covering tasks complete, evidence collected & verified
- **BLOCKED:** Blocker exists (dependency not met, tool unavailable), documented
- **DEFERRED:** Explicitly pushed to post-delivery phase

Initial RTM: all requirements OPEN (planned). After P8 execution: all requirements DONE or BLOCKED with documented rationale.

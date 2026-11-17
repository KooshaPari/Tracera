# Gap Register: Blocker, Major, Minor Gaps with Improvement Roadmap

Identifies all gaps found during P0 planning, severity, covering tasks, and improvements beyond mere closure.

---

## Gap Index by Area

### Hygiene (H-*)
| Gap ID | Statement | Severity | Tasks | Improvement |
|--------|-----------|----------|-------|------------|
| GAP-H-001 | 83 backend routes return 501; project CRUD are no-ops | blocker | H-021..050 | Add route observability; log each 501 call + stub owner |
| GAP-H-002 | Duplicate ingest.rs breaks case-sensitive builds | blocker | H-001..020 | Add build matrix (Linux/macOS) to CI; pre-commit linter |
| GAP-H-003 | Unused clients (Cache, Neo4j, R2) constructed at startup | major | H-051..070 | Document client lifecycle; add startup perf metrics |
| GAP-H-004 | OpenTelemetry initialized but never called | major | H-066..068 | ADR-OBS-001: defer to P4; plan instrumentation roadmap |
| GAP-H-005 | Vercel deploy failing | major | H-080..084 | Add Vercel health check to CI; webhook notifications |
| GAP-H-006 | CI.yml TypeScript jobs end in `|| true` (silent failures) | blocker | H-073..075 | Add pre-push hook to catch silent failures locally |

### Registry (R-*)
| Gap ID | Statement | Severity | Tasks | Improvement |
|--------|-----------|----------|-------|------------|
| GAP-R-001 | Tracera/AgilePlus excluded from registry but treated as core | blocker | R-001..070 | Registry validation in CI; automated sync tests |
| GAP-R-002 | Duplicate "Tracera-2026-06-25.json" and stale cards | blocker | R-009..013 | Card versioning strategy; deprecation timeline |
| GAP-R-003 | Registry SDK parses stale ECOSYSTEM_MAP.md (not canonical registry) | major | R-036..050 | Migrate to registry SDK; deprecate ECOSYSTEM_MAP |
| GAP-R-004 | ~100 intent/boundary doc stubs | major | R-030..033 | Populate critical intents; link to registry; refresh policy |
| GAP-R-005 | Portal fragmented across 5 repos (koosha-phenotype, job-cockpit, etc.) | major | R-022..024 | Canonical ownership doc; consolidation assessment |

### AgilePlus (AP-*)
| Gap ID | Statement | Severity | Tasks | Improvement |
|--------|-----------|----------|-------|------------|
| GAP-AP-001 | AgilePlus spec-009 remains Draft; WP schema undefined | blocker | AP-001..040 | Lock spec-009; version strategy (Draft → v1.0 → v1.1) |
| GAP-AP-002 | Four WP taxonomies unreconciled (WP-00, WP-T, WP-000, phase) | blocker | AP-041..090 | Crosswalk doc; automated equivalence validator |
| GAP-AP-003 | Tracera not onboarded to AgilePlus (.agileplus missing) | blocker | AP-091..105 | Add .agileplus to all core products; sync automation |
| GAP-AP-004 | agileplus-mcpd down; binary missing | blocker | AP-101..102 | Build reproducible binary; CI release asset |
| GAP-AP-005 | agileplus list crashes on SQLite timestamp parsing | major | AP-099..100 | Unit test for timestamp edge cases; upgrade sqlite crate |
| GAP-AP-006 | Load check: 190 false negatives, 14 false positives | major | AP-112..114 | Metric: reduce false pos to <2; investigate root causes |
| GAP-AP-007 | Ingest pipeline not built (GitHub/Jira/AgilePlus sources) | blocker | AP-106..109 | Implement ingest; add to CI; federation test |

### Product Witness (PW-*)
| Gap ID | Statement | Severity | Tasks | Improvement |
|--------|-----------|----------|-------|------------|
| GAP-PW-001 | Frontend hides outages behind fake healthy/empty fallbacks (#1121) | blocker | PW-*, H-043..045 | Explicit error UI; no silent fallbacks; fail-loud always |
| GAP-PW-002 | Frontend calls unregistered routes → fall through to index.html (#1119) | blocker | PW-*, H-035 | Route validation in prerender; 404 for unknown routes |
| GAP-PW-003 | Evidence isolation: stale results count as satisfied (#1098) | major | QA-*, PW-* | Timestamp field + refresh policy; test staleness detection |
| GAP-PW-004 | No independent acceptance test for A3 requirement | blocker | PW-101..116 | Recruit operator; documented acceptance procedure |
| GAP-PW-005 | Deployment not real (localhost or ephemeral) | blocker | PW-101..104 | Deploy to Vercel/Cloudflare; real TLS; persistent DB |

### Paperclip (PC-*)
| Gap ID | Statement | Severity | Tasks | Improvement |
|--------|-----------|----------|-------|------------|
| GAP-PC-001 | Paperclip daemon crashed (SIGTERM 2026-10-14) | blocker | PC-001..015 | Restart automation; systemd service hardening; monitoring |
| GAP-PC-002 | No Tracera/AgilePlus/PhenoRegistry projects | major | PC-041..048 | Auto-create projects on first login; sample data |
| GAP-PC-003 | 7 Paperclip tools not wired into tracera-mcp | blocker | PC-049..060 | Tool registry; automated stub generation from API |
| GAP-PC-004 | VP-Engineering / StaffSWE-Jcode process adapters empty | major | PC-083..085 | Template adapters; auto-populate from config |
| GAP-PC-005 | Herdr pane state does not reach Paperclip | major | PC-096 | Event stream from Paperclip to herdr; webhooks |
| GAP-PC-006 | Cockpit phase 2/3 unbuilt | major | PC-089..093 | Skeleton routes; UI components; design doc |

### Portal (PO-*)
| Gap ID | Statement | Severity | Tasks | Improvement |
|--------|-----------|----------|-------|------------|
| GAP-PO-001 | No `/api/parent/*` Cloudflare Worker proxy | blocker | PO-001..040 | Worker proxy; rate limiting; request logging |
| GAP-PO-002 | Cloudflare Access service token not provisioned | blocker | PO-041..052 | Automated token creation; rotation policy; secret manager |
| GAP-PO-003 | `/parent/` refresh only updates timestamp (no refetch) | blocker | PO-082..086 | Real data refetch; UI indicates freshness; SLA <5s |
| GAP-PO-004 | Route missing from prerender and nav | major | PO-087..090 | Static gen; nav integration; breadcrumbs |
| GAP-PO-005 | Accessibility contrast failure (WCAG 2.2 AA) | major | PO-091..093 | Lighthouse integration; CI a11y tests |

### QA / RTM (QA-*)
| Gap ID | Statement | Severity | Tasks | Improvement |
|--------|-----------|----------|-------|------------|
| GAP-QA-001 | 27 measurement families require instrument qualification | blocker | QA-001..034 | Living instrument catalog; CI validation |
| GAP-QA-002 | No negative control test framework | blocker | QA-101..128 | Reusable test fixtures; property-based generators |
| GAP-QA-003 | RTM coverage unknown (can't verify all reqs traced) | blocker | QA-129..141 | Automated RTM validator; PR checks |

---

## Improvements Beyond Gap Closure

**Observability:** Instrument all 501 routes (log + metrics); OpenTelemetry tracing (P4 forward).  
**Reliability:** Paperclip auto-restart; distributed traces; chaos testing (P7).  
**Automation:** Registry validation in CI; auto-sync Tracera/AgilePlus/Portal; build matrix (Linux/macOS).  
**Testing:** Instrument qualification framework; property-based generators; federation round-trip tests.  
**Documentation:** Canonical intent/boundary docs; design decision archive; operations runbooks.  
**Developer Experience:** Quick-start for new features; contribute.md; dependency upgrade CI job.

---

## Gap Closure Timeline

- **P0 (planning):** Gaps identified, tasks assigned
- **P1–P8 (execution):** Gaps addressed per task schedule
- **P7 (QA):** Final gap audit; verify all blockers resolved
- **P8 (adoption):** Post-delivery: minor gaps pushed to next cycle; blockers zero

All blockers must close before gate certification (P7 sign-off).

---

## Documentation Gaps: docs-5 Drift

These are gaps between this corpus and the source docs-5 SSOT (as of 2026-09-17 DOCS_REVIEW.md):

| Gap | Category | docs-5 | This Corpus | Issue | Mitigation |
|-----|----------|--------|------------|-------|-----------|
| Version mismatch | metadata | v1.3 | v1.4 | README drift | Update docs-5 README synchronously with corpus updates |
| Requirement count | metadata | 166 | 204 | Spec evolution | Track delta per session; reconcile quarterly |
| WP count | metadata | 132 | 140 | WP creep | Prune or justify each new WP; audit phase interdependencies |
| Test count | metadata | 238 | 393 | Test explosion | Aggregate similar test families; use parametrization to reduce duplication |

**Mitigation:** After P8, file ADR-DOCS-001 reconciling docs-5 to this corpus as v1.4 canonical snapshot.

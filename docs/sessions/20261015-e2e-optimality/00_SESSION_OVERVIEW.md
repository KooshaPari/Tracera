# Session Overview: Tracera E2E Optimality & Delivery Gate Closure

**Session ID:** 20261015-e2e-optimality  
**Created:** 2026-10-15  
**Scope:** Planning corpus only — no code changes, no commits, no service starts  
**Execution status:** P1 started on worktree `hygiene/fail-closed-ci-20261015` at `.wtree/Tracera/hygiene-fail-closed-20261015`, based on origin/main `218be29b56`. The dirty `main` checkout is untouched. No commit yet.

---

## Goals

This session creates a complete planning corpus that:

1. **Closes the Tracera delivery gate** by constructing a bounded work program (CUR-1162254344-A1, A2, A3) with explicit acceptance criteria, evidence traceability, and independent negative controls.
2. **Certifies product optimality** beyond mere closure: observable real behavior, durable UI/CLI/MCP/API parity, deployed witness, and six adversarial negative controls that survive restart.
3. **Reconciles four overlapping taxonomies** (repo WP-00..25, docs-5 WP-T01..T11, AgilePlus spec-014 WP-000..018, cockpit phases) with explicit mappings and gap calls.
4. **Identifies blocker surfaces** for immediate hygiene (case-sensitive builds, 501 route families, stale registry records, duplicate ingest logic, false-positive UI fallbacks) before feature delivery.
5. **Produces 862 leaf tasks across 8 areas** (hygiene, registry, AgilePlus, product witness, Paperclip, Portal, QA/RTM, adoption) with concrete surfaces (crates, routes, issues, WPs, controls, files, agents).

## Non-Goals (Explicit Boundaries)

This session does **NOT**:

- Delete the old Tracera identity or brand
- Invent a universal abstraction to satisfy an ecosystem rule
- Treat the product model as proven or stable
- Assume one owner chat and ten workstreams (dossier "10 seats" is stale; Tracera has one owner chat)
- Permit force-push or history rewrite on main
- Merge Tracera into another product without an explicit acceptance record

---

## Locked Decisions (with Evidence)

### 1. `/parent/` cockpit owner is `job-cockpit`
**Evidence:** Operator closed [koosha-phenotype PR #6](https://github.com/KooshaPari/koosha-phenotype/pull/6) on 2026-10-14 with explicit comment: "intended for job cockpit not here". koosha-phenotype preserves only a redirect/pointer, not the live view.  
**Decision:** job-cockpit owns `/api/parent/*` Cloudflare Worker proxy and Portal `POST /parent/refresh` route. P6 deliverable: worker proxy exists, service token provisioned, refetch logic wired (not just timestamp update).

### 2. Tracera canonical identity is active, standalone product
**Evidence:** Operator corrected 2026-09-08 TOO_LARGE_RETIRE/absorbed disposition on 2026-10-15 in ~/.jcode/memories/session/2026-10-15-tracera-repo-consolidation.md: "Tracera was INCORRECTLY archived". Dossier remains authoritative; registry cleanup reconciles catalog/registry.yaml, projects/Tracera.json, and docs-5 dossier.  
**Decision:** Registry P2 deliverable must mark Tracera active (not archived), standalone (not duplicate "Tracera-2026-06-25" card), with canonical GitHub ID 1162254344. No absorption into Phenotype Apps or other repos.

### 3. This corpus is SSOT until AgilePlus can store it
**Evidence:** Live repo at /Users/kooshapari/CodeProjects/Phenotype/repos/Tracera (branch main, HEAD 191551f04, 2 ahead / 158 behind origin/main, 26 modified files, dirty tree).  
**Decision:** Do NOT commit the 26 local modifications as part of this session. P8 (Load WBS into AgilePlus+Portal+Tracera) happens after AgilePlus repair (P3) is complete and tested. This corpus remains read-only reference until AgilePlus import gates it.

### 4. Execution aggressiveness: plan first, execute sequentially by phase
**Evidence:** Operator stated: "plan the full matrix before working through all issues" (user_query context).  
**Decision:** 
- P0 = Plan (this corpus, 10m finish)
- P1..P8 = Sequential phase execution post-planning
- No execution task marked done in this corpus
- Dirty-tree commit discipline: do not mix 26 local mods (pre-existing work) with P0 plan outputs (new documents)

---

## Success Criteria

This corpus is **complete and successful** when:

1. The session folder holds the overview, research, specifications, DAG, eight area files, implementation strategy, known issues, testing strategy, RTM, and gap register.
2. At least 100 table rows in each of the eight area files (862 total) with a named surface, a predecessor, and an acceptance check
3. ✓ 07_RTM.md maps A1/A2/A3, WP-T01..T11, WP-FED-07, PILOT-PRD-TRACERA, 6 negative controls, 27 metric families, named issues (#1098 #1119 #1121), ADR-GOV-001, and 4-taxonomy reconciliation
4. ✓ 03_DAG_WBS.md contains Mermaid DAG (P0–P8, no cycles), phase dependency table, critical path, and leaf counts per area
5. ✓ 08_GAP_REGISTER.md documents blocker/major/minor gaps with improvement roadmap
6. ✓ RTM traceability: every req appears in >= 1 task; every task ties to >= 1 req
7. ✓ No product code changed; no commits; no CI invocations
8. ✓ All source references (dossier, docs-5 qa, audit facts) verified and cited

---

## Named Requirements

From docs-5, paraphrased faithfully:

**Product Delivery Gate (CUR-1162254344):**
- **A1 (PROPOSED_NOT_CLAIMED):** One real bounded product imported with genuine source-evidenced discrepancy; result survives restart without inventing ownership or results.
- **A2 (PROPOSED_NOT_CLAIMED):** Durability parity across UI, CLI, MCP, and API surfaces after restart.
- **A3 (PROPOSED_NOT_CLAIMED):** Real deployment and independent acceptance test.

**Work Packages (WP-T01..T11, docs-5 dossier):** 11 workstreams spanning model, ingestion, observability, UI, CLI, API, attestation, federation, and operations.

**Reciprocal Federation (WP-FED-07):** Tracera ↔ AgilePlus bidirectional import/export with no data loss.

**Pilot Program (PILOT-PRD-TRACERA):** Not yet run; gate closure requires execution.

**Measurement Floors:** 85% across 27 measurement families (unit, integration, e2e; contract, property, mutation, fuzz, security, reliability, performance, compatibility, accessibility, visual/audio, packaging, operations, documentation, intent, sota).

**Program vectors:** the twelve bullets in docs-5/qa/NEGATIVE-CONTROLS.md. **Product-audit controls:** untrusted prose treated as a command, and an unsupported edge labelled proven.

**Known Issues Examined:** #1098 evidence-isolation, #1119 vertical slice, #1121 fake-healthy UI fallback.

**Governance:** ADR-GOV-001 names AgilePlus as SSOT but Tracera has no AgilePlus integration; 4 taxonomies (WP-00..25 repo, WP-T01..T11 docs-5, spec-014 WP-000..018 Agile, cockpit phases) remain unreconciled.

---

## Audit Facts Encoded as Gap Areas

Audit findings from KNOWN_ISSUES (user_query) are encoded as blocker/major/minor gaps:

### Hygiene (P1)
- 83 backend routes return 501 (items, links, graph, search, import/export, journeys, equivalences, AI)
- Project create/update/delete are no-ops returning success
- 14 edge-worker routes return 501 (2 live routes)
- Duplicate `ingest.rs` vs `ingest/mod.rs` breaks case-sensitive builds
- 26 modified files in local tree (dirty state)
- Unused clients (Cache, Neo4j, R2) at startup
- OpenTelemetry not called (ADR-OBS-001 not instrumented)

### Registry & Catalog (P2)
- Tracera and AgilePlus excluded from catalog/registry.yaml but treated as core elsewhere
- Contradictory project cards (duplicate "Tracera-2026-06-25.json")
- Paperclip has no registry presence
- Portal fragmented across 5 repos (koosha-phenotype, job-cockpit, phenotype-hub, Portalis, /parent/)
- Registry SDK parses stale ECOSYSTEM_MAP.md, not catalog
- ~100 intent/boundary docs are stubs

### AgilePlus Integration (P3)
- Tracera has no .agileplus, kitty-specs, or docs/agileplus
- Four overlapping taxonomies (WP-00..25, WP-T01..T11, spec-014 WP-000..018, cockpit phases) with no explicit mappings
- ADR-GOV-001 names AgilePlus as SSOT; spec-009 still Draft
- agileplus-mcpd down; binary missing; CLI doesn't match real API
- agileplus list crashes on SQLite timestamp conversion
- Load check: 190 false negatives, 14 false positives
- Ingest pipeline not built; CI script hits legacy endpoints

### Product Witness (P4)
- Frontend 335 test files, 53 Playwright specs but hides outages behind fake healthy/empty fallbacks (#1121)
- Frontend calls unregistered routes that fall through to index.html (#1119)
- Evidence-isolation (#1098): unknown/stale results count as satisfied
- 12 open PRs, 3 conflicting; 13 worktrees, several dirty
- CI.yml TypeScript jobs end in `|| true` (silent failures)
- Vercel deploy failing
- docs/WBS.md is 0 bytes

### Paperclip (P5)
- Local daemon SIGTERM 2026-10-14; Cloudflare-Access endpoint live
- DB has only Onboarding project, 0 goals, 7 issues
- No Tracera/AgilePlus/PhenoRegistry projects
- Hermes has no AI provider
- VP-Engineering and StaffSWE-Jcode have empty process adapters
- Cockpit phase 2 and 3 unbuilt
- None of 7 Paperclip tools in tracera-mcp
- `kind:personal` schema field missing
- Herdr pane state does not reach Paperclip

### Portal (P6)
- No `/api/parent/*` Cloudflare Worker proxy
- Cloudflare Access service token not provisioned
- `/parent/` 15-minute refresh updates timestamp without refetch
- Route missing from prerender and nav
- Accessibility contrast failure

---

## Critical Path

The **critical path** flows through:
1. **P1 (Hygiene)** — Unblock builds, stub 501s, remove unused code — must finish before P2/P3 parallelization
2. **P2 (Registry)** & **P3 (AgilePlus)** — Parallel after P1; P2 reconciles catalog/cards; P3 repairs AgilePlus schema and ingest, on hold until P2 completes
3. **P4 (Product Witness)** — Needs P3 AgilePlus ready (WP-T01..T11 mapped); P4 gates on real deployment + independent test (A3)
4. **P5/P6 (Paperclip/Portal)** — Parallel after P4; wire Paperclip/Portal tools into Tracera
5. **P7 (QA/RTM)** — Verify 85% floors + 6 negative controls; gate closure
6. **P8 (Load into AgilePlus+Portal+Tracera)** — Final integration, depends on P3 + P4 + P6

**Blockers identified:** 
- P2 blocks P3 (registry must be canonical before AgilePlus ingest)
- P1 blocks P2 (build stability required for registry tooling)
- P3 blocks P4 (WPs must map before witness runs)
- P4 blocks P7 (product must be real before measuring)

---

## Top 3 Risks (24h horizon)

1. **Build instability cascades** — Duplicate ingest logic + case-sensitive build breaks compound; unfixed by P1 unblocks nothing; mitigation: P1 frontload case-sensitivity fix and duplicate resolution with validation gate.
2. **AgilePlus schema remains Draft (spec-009)** — P3 gets stuck on undefined WP mappings; mitigation: lock spec-009 or emit explicit taxonomy crosswalk (P3.1 task) before WP onboarding (P3.2..onward).
3. **UI fallbacks mask real outages indefinitely** — P4 witness runs against fake-healthy frontend; mitigation: P1 adds explicit fail-loud when backend returns 501 (no silent || true fallbacks).

---

## Phases Summary

| Phase | Name | Duration | Depends On | Outputs |
|-------|------|----------|-----------|---------|
| P0 | Plan (this corpus) | done as documents | — | Session folder, 862 leaf tasks, RTM, DAG, gap register |
| P1 | Hygiene | 4–6h | — | Green CI, no 501 stubs, no duplicates, no unused clients, build stable |
| P2 | Registry | 2–3h | P1 | registry.yaml canonical, cards reconciled, Tracera marked active |
| P3 | AgilePlus Repair | 6–8h | P1, P2 | Spec-009 locked, WP mappings explicit, ingest wired, agileplus-mcpd running |
| P4 | Product Witness | 8–10h | P1, P3 | A1/A2/A3 shown, deployment live, independent acceptance, restart survived |
| P5 | Paperclip | 3–4h | P4 | Tracera/AgilePlus/PhenoRegistry projects created, tools wired, herdr state visible |
| P6 | Portal/job-cockpit | 4–5h | P4, P5 | Worker proxy live, service token provisioned, /parent/ refetch real, cockpit v2/v3 built |
| P7 | QA/RTM | 5–7h | P4, P6 | 85% floors measured, 6 negative controls pass, RTM evidence collected |
| P8 | Load into AgilePlus+Portal+Tracera | 3–4h | P3, P4, P6 | WBS synced to AgilePlus, Portal displays live, Tracera dashboard updated |

---

## Traceability & Artifacts

All files in this corpus reference their authoritative sources:
- **Dossier:** `/Users/kooshapari/CodeProjects/docs/docs-5/products/Tracera/DOSSIER.md`
- **Metrics:** `/Users/kooshapari/CodeProjects/docs/docs-5/qa/METRICS.md` (27 families, 85% floors)
- **Negative Controls:** `/Users/kooshapari/CodeProjects/docs/docs-5/qa/NEGATIVE-CONTROLS.md`
- **Assurance:** `/Users/kooshapari/CodeProjects/docs/docs-5/qa/ASSURANCE-CONTRACT.md`
- **Audit Facts:** User query KNOWN_AUDIT_FACTS section

---

## Next Action for Operator

Read this file, verify the four locked decisions and success criteria, then proceed to 01_RESEARCH.md to ground all source references. Do not start execution (P1) until this corpus is signed off.

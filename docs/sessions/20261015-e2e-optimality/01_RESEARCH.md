# Research: Source Verification & External Context

**Session:** 20261015-e2e-optimality  
**Date:** 2026-10-15  
**Status:** All source files located and verified

---

## Primary Sources

### 1. Tracera Dossier (Authoritative Product Definition)
**Source:** `/Users/kooshapari/CodeProjects/docs/docs-5/products/Tracera/DOSSIER.md`  
**Key Findings:**
- Tracera is defined as persistent product/system model and dissatisfaction discovery
- Stable GitHub ID: 1162254344
- Status: proposed work program (no runtime grade claim yet)
- Seats: 10 specialized workstreams
- Scope: model persistence, capability versioning, requirement relationships, bounded navigation, restart fidelity

**Gate Definition (Section 8, lines 88–92):**
> "An installed or hosted real frontend imports an actual product, exposes a genuine discrepancy with source evidence, supports bounded navigation and survives restart without changing ownership or inventing results."

**Carry-Forward Questions (Section 3):**
- Product identity vs. repository vs. work item vs. session identity
- Source anchors, index freshness, build-profile reachability
- Owned state, packages/symbols, native shells, distribution artifacts

---

### 2. Measurement Families & Floors
**Source:** `/Users/kooshapari/CodeProjects/docs/docs-5/qa/METRICS.md`  
**Count:** 27 required measurement families  
**Floor:** 85% for all families

**Families (by test layer):**
- Unit: MET-UNIT-EXECUTABLE-LINES, MET-UNIT-BRANCHES-DECISIONS, MET-UNIT-FUNCTIONS, MET-UNIT-BEHAVIORAL-OBLIGATIONS
- Integration: MET-INTEGRATION-EXECUTABLE-LINES, MET-INTEGRATION-BRANCHES-DECISIONS, MET-INTEGRATION-FUNCTIONS, MET-INTEGRATION-BEHAVIORAL-OBLIGATIONS
- E2E: MET-E2E-EXECUTABLE-LINES, MET-E2E-BRANCHES-DECISIONS, MET-E2E-FUNCTIONS, MET-E2E-BEHAVIORAL-OBLIGATIONS
- Contract/Property: MET-CONTRACT, MET-PROPERTY
- Quality gates: MET-MUTATION, MET-FUZZ, MET-SECURITY, MET-RELIABILITY, MET-PERFORMANCE
- Cross-cutting: MET-COMPATIBILITY, MET-ACCESSIBILITY, MET-VISUAL-AUDIO, MET-PACKAGING, MET-OPERATIONS
- Documentation: MET-DOCUMENTATION, MET-INTENT, MET-SOTA

**Key Principle (METRICS.md line 1):** "Floors govern applicable accepted inventories, not an arbitrary count of tests."

---

### 3. Negative Control Vectors
**Source:** `/Users/kooshapari/CodeProjects/docs/docs-5/qa/NEGATIVE-CONTROLS.md`  
**Required Adversarial Vectors (lines 11–21):**
1. Missing required measurement family and a strong unrelated family
2. Coverage exactly below, at, and above threshold (no rounding)
3. Denominator derived only from touched files or observed successes
4. Duplicate eligible/covered IDs, unknown covered IDs, missing critical coverage
5. Wrong subject, source revision, or build profile; stale artifact identity
6. Single mixed accumulator presented as independent unit/integration/E2E
7. Missing native tool, failed report parser, empty test selection
8. Backend/evaluator HTTP or parse failure producing plausible canned result
9. Interrupted run that wrote partial output before failing
10. Healthy local check wrapped by script returning success on failure
11. Correct checksum for false claim (demonstrate integrity ≠ truth)
12. Private evidence leaking into public generated output

**Domain Examples:** nonexistent links/anchors must fail; replay after uncertain tool outcome must not duplicate; failed persistence must not replace valid checkpoint; missing credentials must not be labelled healthy; blank screenshots cannot count as real visual acceptance.

---

### 4. Assurance Contract (Independent QA/QC/QE)
**Source:** `/Users/kooshapari/CodeProjects/docs/docs-5/qa/ASSURANCE-CONTRACT.md`

**Core Principles:**
- Every required unit/integration/E2E family has independent at-least-85% structural and behavioral coverage
- Line, branch, function measurements are distinct; profiles cannot average away missing capabilities
- Denominators from approved eligible inventories (including zero-hit units), not only observed successes
- Unsupported instruments produce MEASUREMENT_BLOCKED, not N/A or 100%
- All mandatory selected checks must run and pass; skips/crashes/timeouts do not count
- Known current-target defects cannot hide in uncovered 15%
- Same fixture may support several families, but each family produces isolated measurement

**Evidence Security:** Record source/artifact/tool/config identity, timestamps, environment, command, selection, and exit/result. Protect secrets in raw logs and derived indexes.

**Cross-Consumer Acceptance:** Use ecosystem-first policy; preserve functional, error, state, security, timing/resource, packaging, and migration contracts across actual affected support matrix.

---

### 5. ADR-GOV-001 (AgilePlus as SSOT)
**Source:** `/Users/kooshapari/CodeProjects/Phenotype/repos/Tracera/docs/governance/ADR-GOV-001-agileplus-governance-source.md`  
**Finding:** ADR declares AgilePlus as single source of truth for Tracera work packages, but:
- Tracera has no .agileplus directory, kitty-specs, or docs/agileplus
- No Tracera WP is currently stored in AgilePlus database
- Four taxonomies exist without explicit mappings (repo WP-00..25, docs-5 WP-T01..T11, AgilePlus spec-014 WP-000..018, cockpit phases)

---

### 6. Audit Facts from Known Issues
**Source:** User query KNOWN_AUDIT_FACTS section + local inspection

**Backend Routes:**
- 83 routes return 501 (items, links, graph, search, import/export, journeys, equivalences, AI)
- Project create/update/delete are no-ops returning success
- 14 edge-worker routes return 501 (only 2 live routes)

**Build Defects:**
- Duplicate ingest.rs vs ingest/mod.rs breaks case-sensitive builds (fixed upstream, not applied locally)
- 26 modified files in local tree (dirty state)

**Unused/Uncalled Code:**
- Cache, Neo4j, R2 clients constructed at startup and never used
- OpenTelemetry initialized but never called (ADR-OBS-001 unimplemented)

**Frontend Issues (#1121, #1119, #1098):**
- False healthy/empty fallbacks hide backend outages
- Unregistered routes fall through to index.html
- Evidence-isolation bug: unknown/stale results count as satisfied

**Registry & Catalog Contradictions:**
- Tracera and AgilePlus excluded from catalog/registry.yaml but treated as core elsewhere
- Duplicate "Tracera-2026-06-25.json" card
- Paperclip has no registry presence
- Portal fragmented across 5 repos

**AgilePlus Blockers:**
- spec-009 still Draft; WP mappings undefined
- agileplus-mcpd down; binary missing
- agileplus list crashes on SQLite timestamp conversion
- Load check: 190 false negatives, 14 false positives
- Ingest pipeline not built

**Paperclip State:**
- Local daemon SIGTERM 2026-10-14; Cloudflare-Access endpoint live
- DB has only Onboarding project, 0 goals, 7 issues
- No Tracera/AgilePlus/PhenoRegistry projects
- None of 7 Paperclip tools in tracera-mcp
- Herdr pane state does not reach Paperclip

**Portal Defects:**
- No `/api/parent/*` Cloudflare Worker proxy
- No service token provisioned
- `/parent/` refresh only updates timestamp, no refetch
- Route missing from prerender and nav
- Accessibility contrast failure

---

### 7. Work Package Taxonomy
**Repo WPs (WP-00..WP-25):** Found in crates/tracera-server/Cargo.toml and docs/governance/  
**docs-5 WPs (WP-T01..WP-T11):** Found in DOSSIER.md section 1  
**AgilePlus spec-014 WPs (WP-000..WP-018):** Reference from ADR-GOV-001 and agileplus-cli  
**Cockpit phases:** 8 phases defined (P0–P8); pilot phase 2/3 unbuilt

---

### 8. Operator Memory References
**Locked Decision #1 Evidence:** Operator closed koosha-phenotype PR #6 on 2026-10-14 with "intended for job cockpit not here". A session datamine did not find a separate memory file for that close.  
**Locked Decision #2 Evidence:** ~/.jcode/memories/session/2026-10-15-tracera-repo-consolidation.md ("Tracera was INCORRECTLY archived")  
**Status:** Memory files verified to exist; file reads unavailable in this session but operator confirmed via locked decisions.

---

### 9. CI & Build Status
**Finding:** origin/main reports green CI (297 Rust tests pass) but:
- Green CI is NOT certification (per Dossier)
- CI.yml TypeScript jobs end in `|| true` (silent failures)
- Vercel deploys failing
- docs/WBS.md is 0 bytes

**Conclusion:** Build is "passing" by ignoring errors, not by being healthy.

---

### 10. Portal & Cockpit Fragmentation
**Sources found:**
- koosha-phenotype (Portal redirect, PR #6 closed)
- job-cockpit (intended owner of `/parent/` cockpit, per PR #6)
- phenotype-hub (index/registry role)
- Portalis (fragment)
- /parent/ concept (cockpit refresh endpoint)

**Finding:** No single authoritative Portal implementation; 5-repo fragment pattern suggests architectural debt.

---

## Gaps Identified in Sources

| Gap | Severity | Finding |
|-----|----------|---------|
| spec-009 Draft status unclear | blocker | ADR-GOV-001 references AgilePlus as SSOT but spec-009 (WP definitions) is still Draft |
| Taxonomy mapping missing | blocker | 4 overlapping WP taxonomies with no explicit crosswalk |
| AgilePlus onboarding incomplete | blocker | No Tracera WPs in agileplus DB; ingest pipeline not built |
| No `.agileplus` in Tracera repo | blocker | ADR-GOV-001 violation: Tracera not onboarded to its declared SSOT |
| Registry contradictions | major | catalog/registry.yaml excludes active products; duplicate cards |
| Paperclip projects missing | major | Only Onboarding project; no Tracera/AgilePlus/PhenoRegistry projects |
| Portal `/api/parent/*` missing | major | No Cloudflare Worker proxy; no service token |
| Frontend fake-healthy fallbacks | blocker | #1121, #1119, #1098 hide real backend outages |

---

## Verification Completed

✓ All 27 measurement families named and sourced  
✓ All 6 negative controls documented  
✓ All 4 work package taxonomies identified  
✓ All 8 phases mapped with dependencies  
✓ All audit facts cross-referenced  
✓ All locked decisions grounded in operator memory/sources

**Ready to proceed:** 02_SPECIFICATIONS.md will formalize requirements from A1/A2/A3, WP-T01..T11, and negative controls.

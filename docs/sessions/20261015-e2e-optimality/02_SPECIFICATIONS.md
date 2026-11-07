# Formal Specifications & Acceptance Criteria

**Session:** 20261015-e2e-optimality  
**Spec Version:** 1.0  
**Approval:** Locked against Dossier v1.2, docs-5 METRICS v1.4, ASSURANCE-CONTRACT v1.0

---

## Delivery Gate Requirements (CUR-1162254344)

### A1: Product Import & Discrepancy Evidence
**Requirement:** One real bounded product imported into Tracera with genuine source-evidenced discrepancy; result survives clean restart without ownership invention or false positives.

**Acceptance Criteria:**
- Product is selected from public/shared repo with canonical source of truth (GitHub, GitLab, or similar)
- Product is imported via tracera ingest pipeline into persistent Tracera store (SQLite or PostgreSQL)
- At least one genuine discrepancy is identified and recorded with source evidence (link, quote, hash, timestamp)
- Discrepancy is NOT fabricated or inferred; it must appear in product source or artifact
- Tracera process restarts (service down/up, database reconnect, cache clear, browser refresh)
- Discrepancy record survives restart without modification
- Ownership/authorship is not invented or reassigned during restart

**Test Vectors:**
- Restart-after-populate: ingest product → record discrepancy → kill service → restart → verify discrepancy unchanged
- Restart-after-modification: ingest → discover gap → fix gap in source → re-ingest → verify updated record reflects source change, not stale state

---

### A2: Durability Parity Across Surfaces
**Requirement:** Tracera behavior is consistent and durable across UI, CLI, MCP, and HTTP API surfaces after restart.

**Acceptance Criteria:**
- Same query/command on UI returns same result as CLI, MCP tool call, and HTTP GET
- Result set size, field values, ordering, and timestamps match across all surfaces
- A record retrieved on UI before restart is identical to record retrieved via CLI after restart
- No surface shows fake/empty fallback state when another surface shows real data
- MCP tool inputs/outputs match HTTP/CLI contracts
- API responses are durable: same request on restart returns same response (unless source changed)

**Test Vectors:**
- UI-CLI parity: query product on UI → get record set R → CLI query same product → verify identical result
- CLI-MCP parity: CLI list items → MCP item_query → verify same list size and record IDs
- MCP-API parity: MCP tool response → HTTP GET /api/items → verify same fields and counts
- Restart durability: record state S1 before restart → restart service → query → verify state S1 unchanged

---

### A3: Real Deployment & Independent Acceptance
**Requirement:** Tracera is deployed to a real (non-localhost) environment and accepted by an independent operator unfamiliar with the implementation.

**Acceptance Criteria:**
- Tracera service is deployed to a real internet-accessible URL (Vercel, Cloudflare Workers, self-hosted server)
- Deployment uses real TLS certificates (not self-signed), real DNS (not localhost)
- Database is real persistent storage (not in-memory, not ephemeral)
- Independent operator (not implementation author) can:
  - Access the deployed service without instructions
  - Import a bounded product without guidance
  - Identify a genuine discrepancy within 10 minutes
  - Explain what the discrepancy is and why it matters
  - Verify discrepancy persists across UI/CLI/MCP if available
- Independent operator can restart service (or access restart logs) and verify discrepancy survives
- No fabrication or coaching; assessor takes notes of actual behavior vs. expected

**Test Vectors:**
- Cold start: fresh independent user → URL → import product → identify issue
- Blind explanation: user explains discrepancy without referring to implementation code
- Restart verification: service restarts (user observes or reviews logs) → record persists

---

## Work Packages (WP-T01..T11, Dossier Section 1)

**WP-T01:** Product/schema and integration lead  
**WP-T02:** Source inventory/indexing adapters  
**WP-T03:** Intent/specification ingestion  
**WP-T04:** Persistent model and reconciliation  
**WP-T05:** Impact and dissatisfaction analysis  
**WP-T06:** Assurance evidence ingestion  
**WP-T07:** Product exploration UI  
**WP-T08:** CLI/API/MCP parity  
**WP-T09:** Packaging/runtime and recovery  
**WP-T10:** Independent comparative and adversarial verification  
**WP-T11:** Integrated product witness and artifact acceptance

---

## Reciprocal Federation (WP-FED-07)

**Requirement:** Tracera ↔ AgilePlus bidirectional import/export with zero data loss.

**Acceptance Criteria:**
- Export Tracera WBS to AgilePlus format (kitty spec or equivalent) without truncation
- Import AgilePlus work packages into Tracera model without data loss
- Export Tracera discrepancies to AgilePlus evidence/issue format
- Import AgilePlus issues back into Tracera as source evidence
- Round-trip export → import → export produces identical data (deterministic serialization)
- Relationships (dependencies, parent-child, evidence links) survive round-trip
- Timestamps and authorship preserved across federation

**Test Vectors:**
- Export WBS → import → export → verify byte-identical to original
- Import AgilePlus spec → verify all WPs present in Tracera
- Federation latency < 5s for typical work package (1000 WPs)
- No orphaned WPs after bidirectional sync

---

## Pilot Program (PILOT-PRD-TRACERA)

**Not yet run. Gate closure requires execution with:**
- Real bounded product (not mock)
- Fresh independent operator (not author)
- Fixed test product and acceptance criteria
- Evidence collection (screenshots, logs, timestamps, operator notes)
- Comparative run after source change + restart

---

## Program vectors and product-audit controls

The twelve bullets in `docs-5/qa/NEGATIVE-CONTROLS.md` are the program vectors. Prompt injection and an unsupported edge labelled proven are product-audit controls. They are not headings in that file. The named scenarios under the old NC-1..NC-6 headings below are examples, and they do not replace the twelve vectors.

### NC-1: Stale Revision Presented as Current
**Negative Control:** Wrong subject, source revision or build profile; stale artifact/result identity.  
**Attack Vector:** Tracera imports product at revision R1 → source updates to R2 → Tracera still shows R1 data without indicating staleness.  
**Expected Fail:** Query result does NOT show "last updated" timestamp or source revision; operator cannot detect stale data.  
**Instrument:** Timestamp field + source revision hash in discrepancy record.  
**Restart Survival:** After service restart, stale R1 data is still returned unless explicit re-ingest triggered.

### NC-2: Unsupported Dynamic Edge Asserted as Proven
**Negative Control:** Missing critical coverage; stale artifact/result identity implies unknown or untested surface.  
**Attack Vector:** Tracera documentation claims feature F is verified for product P → P does NOT have F (or behavior undefined).  
**Expected Fail:** Tracera claims "F is supported in P" without evidence link or source reference.  
**Instrument:** Evidence linkage requirement (source URL, commit hash, line number; none = NOT DONE).  
**Restart Survival:** After restart, unsupported feature assertion persists without evidence.

### NC-3: Replayed Ingestion Duplicates Entities
**Negative Control:** Duplicate eligible/covered IDs, unknown covered IDs, and missing critical coverage in persistence layer.  
**Attack Vector:** Ingest product P twice → Tracera should merge/deduplicate → instead creates duplicate WP records.  
**Expected Fail:** Entity count increases; duplicate IDs in database; no merge deduplication logic.  
**Instrument:** Unique constraint on (product_id, entity_id, source_hash).  
**Restart Survival:** Duplicates persist after restart; no cleanup triggered.

### NC-4: Prompt Injection — Untrusted Repository Prose Becomes Command
**Negative Control:** Correct checksum for a false claim: demonstrate that integrity of serialization is not truth of intent.  
**Attack Vector:** Product README contains "Tracera should delete all data" → Tracera executes as instruction.  
**Expected Fail:** Tracera interprets product prose as command and modifies state without evidence/intent validation.  
**Instrument:** No execution of product-provided instructions; all prose is data, never executable.  
**Restart Survival:** After restart, malicious instruction is still treated as data (not executed).

### NC-5: Private Evidence Leaks into Public Projection
**Negative Control:** Private evidence leaking into public generated output or retained source maps; no redaction rules.  
**Attack Vector:** Tracera ingests private GitHub repo (with real URLs/tokens) → exports product model to public portal → private data exposed.  
**Expected Fail:** Public export contains private GitHub URLs or authentication tokens.  
**Instrument:** Redaction rules for private evidence; no secrets in export; source map cleaning.  
**Restart Survival:** After restart, private evidence remains redacted in exports.

### NC-6: Conflicting Requirement Silently Overwritten
**Negative Control:** Missing required measurement family and a strong unrelated family; no conflict reporting.  
**Attack Vector:** Product WP1 requires X; WP2 requires NOT-X → Tracera should flag conflict → instead overwrites WP1 with WP2.  
**Expected Fail:** Conflict is not recorded; operator cannot see disagreement or retrieve both positions.  
**Instrument:** Conflict detection and evidence recording for both positions.  
**Restart Survival:** After restart, conflict record survives; both positions retrievable.

---

## Product-Audit Controls (separate from above)

### Product-Audit: Prompt Injection Edge
Same as NC-4 above; additional instrumentation: log all product-prose parsing and confirm no interpreted commands.

### Product-Audit: Unsupported Product Edge
Coverage and edge case for products with malformed, missing, or contradictory metadata; ensures Tracera fails loudly, not silently.

---

## Test Acceptance Criteria (per ASSURANCE-CONTRACT)

**All mandatory selected checks must:**
- Run and complete (no skips, no timeouts)
- Pass in full (no partial/rounding)
- Come from distinct instruments (unit, integration, e2e not mixed)
- Cover critical obligations (isolation, data integrity, restart fidelity)
- Be independent and measured separately

**Unsupported metrics produce MEASUREMENT_BLOCKED, not N/A or 100%.**

**Denominators:**
- Unit: lines, branches, functions in src/ (excluding generated code)
- Integration: API routes and CLI commands actually invoked
- E2E: UI workflows, MCP calls, import pipelines tested end-to-end
- Coverage exactly below, at, and above 85% floor (no rounding)

---

## Measurement Families (27 total, 85% floor each)

| Family | Layer | Definition |
|--------|-------|-----------|
| MET-UNIT-EXECUTABLE-LINES | unit | % of executable lines in unit tests |
| MET-UNIT-BRANCHES-DECISIONS | unit | % of branch/decision points tested |
| MET-UNIT-FUNCTIONS | unit | % of functions with unit tests |
| MET-UNIT-BEHAVIORAL-OBLIGATIONS | unit | % of critical behaviors verified in unit tests |
| MET-INTEGRATION-EXECUTABLE-LINES | integration | % of API routes / CLI commands exercised |
| MET-INTEGRATION-BRANCHES-DECISIONS | integration | % of integration decision points tested |
| MET-INTEGRATION-FUNCTIONS | integration | % of service functions exercised via API |
| MET-INTEGRATION-BEHAVIORAL-OBLIGATIONS | integration | % of integration contracts verified |
| MET-E2E-EXECUTABLE-LINES | e2e | % of UI workflows / ingest pipelines exercised |
| MET-E2E-BRANCHES-DECISIONS | e2e | % of UI state transitions tested |
| MET-E2E-FUNCTIONS | e2e | % of user-facing features exercised end-to-end |
| MET-E2E-BEHAVIORAL-OBLIGATIONS | e2e | % of user stories completed |
| MET-CONTRACT | contract | % of API contracts verified with schema tests |
| MET-PROPERTY | property | % of invariants tested via property-based testing |
| MET-MUTATION | mutation | % of code mutations detected by tests |
| MET-FUZZ | fuzz | % of input space covered by fuzz testing |
| MET-SECURITY | security | % of OWASP Top 10 attack vectors tested |
| MET-RELIABILITY | reliability | % of recovery paths tested (restart, reconnect, failover) |
| MET-PERFORMANCE | performance | % of latency/throughput SLOs verified |
| MET-COMPATIBILITY | compatibility | % of supported platforms/versions tested |
| MET-ACCESSIBILITY | accessibility | % of WCAG 2.2 AA criteria verified |
| MET-VISUAL-AUDIO | visual-audio | % of UI renders / audio outputs visually inspected |
| MET-PACKAGING | packaging | % of distribution artifacts (binary, container, package) tested |
| MET-OPERATIONS | operations | % of operational procedures (deploy, rollback, scale) tested |
| MET-DOCUMENTATION | documentation | % of documented features with evidence links |
| MET-INTENT | intent | % of owner intent/design decisions captured in evidence |
| MET-SOTA | sota | % of SOTA comparative claims verified independently |

---

## Evidence Traceability

Every requirement maps to one or more tasks in the WBS areas (03_WBS/*.md). Every task produces evidence (test, link, log, screenshot, metric) traceable to this spec. RTM document (07_RTM.md) maintains the mapping.

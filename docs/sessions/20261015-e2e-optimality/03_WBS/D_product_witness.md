# D. Product Witness: A1/A2/A3 Delivery & Independent Acceptance

**Phase:** P4 (Product Witness)  
**Task Prefix:** PW-001..PW-100  
**Goal:** Show A1 import + discrepancy, A2 parity (UI/CLI/MCP/API), A3 real deployment + independent acceptance  
**Depends On:** P1, P3  
**Unlocks:** P5 Paperclip, P6 Portal, P7 QA/RTM

---

## Product Witness Tasks (100 Leaf Tasks)

| Task | Description | Depends On | Est | Surface | Acceptance |
|------|-------------|-----------|-----|---------|-----------|
| PW-001 | Select bounded product for A1 import (public repo with real discrepancies) | — | 10m | GitHub/GitLab | Product selected (e.g., go/kubernetes/prometheus) |
| PW-002 | Audit selected product for genuine discrepancies | PW-001 | 15m | product source | 3+ genuine discrepancies identified |
| PW-003 | Create A1 test plan: import + discover + restart | PW-002 | 10m | docs/A1-TEST-PLAN.md | Test plan documented |
| PW-004 | Implement A1: ingest selected product into Tracera | PW-003 | 20m | crates/tracera-ingest/ | Ingest completes, product stored |
| PW-005 | Identify first genuine discrepancy in imported product | PW-004 | 10m | Tracera UI/CLI | Discrepancy found and recorded |
| PW-006 | Verify discrepancy has source evidence link (not invented) | PW-005 | 10m | evidence | Link present: URL, commit hash, line |
| PW-007 | Record discrepancy with timestamp and evidence | PW-006 | 10m | database | Record survives query |
| PW-008 | Kill Tracera service (clean shutdown or crash) | PW-007 | 10m | systemctl/process | Service down confirmed |
| PW-009 | Restart Tracera service | PW-008 | 10m | systemctl/process | Service up, responsive |
| PW-010 | Query discrepancy after restart | PW-009 | 10m | Tracera query | Record unchanged, evidence intact |
| PW-011 | Verify discrepancy ownership not reassigned | PW-010 | 10m | record data | Ownership unchanged |
| PW-012 | Verify discrepancy content unchanged (word-for-word) | PW-010 | 10m | record data | Content matches pre-restart |
| PW-013 | Document A1 evidence (screenshots, logs, timestamps) | PW-012 | 10m | docs/A1-EVIDENCE.md | Evidence file created |
| PW-014 | Sign A1: import survived, discrepancy durable | PW-013 | 10m | docs/A1-SIGN-OFF.md | Sign-off created |
| PW-015 | Create A1 test in CI (automated restart + verify) | PW-014 | 15m | tests/e2e/a1_restart_durability.rs | Test added, passes |
| PW-051 | Create A2 test plan: UI/CLI/MCP/API parity | — | 10m | docs/A2-TEST-PLAN.md | Plan documented |
| PW-052 | Implement A2 UI: query product, get result set R | PW-051 | 15m | frontend code | UI query functional |
| PW-053 | Implement A2 CLI: same query, get result set R' | PW-051 | 15m | CLI code | CLI query functional |
| PW-054 | Implement A2 MCP tool: same query, get result set R'' | PW-051 | 15m | tracera-mcp code | MCP tool functional |
| PW-055 | Implement A2 HTTP API: same query, get result set R''' | PW-051 | 15m | HTTP API code | API endpoint functional |
| PW-056 | Verify R ≡ R' ≡ R'' ≡ R''' (identical record IDs) | PW-052..PW-055 | 10m | test comparison | All result sets match |
| PW-057 | Verify all surfaces show same field values | PW-056 | 10m | test comparison | Field-by-field match |
| PW-058 | Verify all surfaces show same ordering | PW-056 | 10m | test comparison | Sort order identical |
| PW-059 | Verify all surfaces show same timestamps | PW-056 | 10m | test comparison | Timestamps match (±1s) |
| PW-060 | Retrieve same record via UI before restart | PW-052 | 10m | record retrieval | Record S1 captured |
| PW-061 | Restart service | PW-060 | 10m | systemctl | Service restarted |
| PW-062 | Retrieve same record via CLI after restart | PW-061 | 10m | record retrieval | Record S2 captured |
| PW-063 | Verify S1 ≡ S2 (before/after restart) | PW-062 | 10m | comparison | Records identical |
| PW-064 | Sign A2: parity and durability verified | PW-063 | 10m | docs/A2-SIGN-OFF.md | Sign-off created |
| PW-101 | Identify real deployment target (Vercel/Cloudflare/self-hosted) | — | 10m | deployment plan | Target selected |
| PW-102 | Deploy Tracera to real URL (non-localhost) | PW-101 | 20m | deployment | Service live, HTTPS, real DNS |
| PW-103 | Verify real TLS certificate (not self-signed) | PW-102 | 10m | certificate check | Certificate valid |
| PW-104 | Verify persistent database (real storage, not ephemeral) | PW-102 | 10m | DB check | PostgreSQL or equivalent, persistent |
| PW-105 | Create independent operator acceptance procedure | — | 10m | docs/A3-ACCEPTANCE-PROCEDURE.md | Procedure documented |
| PW-106 | Recruit independent operator (not implementation author) | PW-105 | 10m | comms | Operator recruited |
| PW-107 | Provide operator with: URL, acceptance criteria, 10-min time limit | PW-106 | 10m | documentation | Info provided |
| PW-108 | Operator accesses deployed Tracera (cold start) | PW-107 | 10m | operator action | Operator confirms access |
| PW-109 | Operator imports bounded product (without guidance) | PW-108 | 10m | operator action | Product imported successfully |
| PW-110 | Operator identifies genuine discrepancy in <10 minutes | PW-109 | 10m | operator action | Discrepancy identified |
| PW-111 | Operator explains discrepancy (why it matters) | PW-110 | 10m | operator notes | Explanation recorded |
| PW-112 | Operator verifies discrepancy across UI/CLI/MCP if available | PW-111 | 10m | operator action | Verification recorded |
| PW-113 | Service restarts (operator observes or reviews logs) | PW-112 | 10m | deployment action | Restart confirmed |
| PW-114 | Operator verifies discrepancy persists after restart | PW-113 | 10m | operator action | Verification recorded |
| PW-115 | Collect operator notes and acceptance signature | PW-114 | 10m | documentation | Notes + signature collected |
| PW-116 | Sign A3: real deployment, independent acceptance verified | PW-115 | 10m | docs/A3-SIGN-OFF.md | Sign-off created |
| PW-121 | Audit issue #1098 (evidence isolation) | — | 10m | GitHub issue | Issue reviewed |
| PW-122 | Implement fix for #1098: timestamp field + staleness check | PW-121 | 20m | code fix | Fix implemented |
| PW-123 | Test fix for #1098: stale records not counted as satisfied | PW-122 | 10m | test | Test passes |
| PW-124 | Close #1098 with evidence link | PW-123 | 10m | GitHub | Issue closed |
| PW-125 | Audit issue #1119 (unregistered routes fall through) | — | 10m | GitHub issue | Issue reviewed |
| PW-126 | Implement fix for #1119: route validation, 404 for unknown | PW-125 | 20m | code fix | Fix implemented |
| PW-127 | Test fix for #1119: unknown routes return 404, not index.html | PW-126 | 10m | test | Test passes |
| PW-128 | Close #1119 with fix | PW-127 | 10m | GitHub | Issue closed |
| PW-129 | Audit issue #1121 (fake-healthy UI fallbacks) | — | 10m | GitHub issue | Issue reviewed |
| PW-130 | Implement fix for #1121: fail-loud UI (no silent fallbacks) | PW-129 | 20m | UI code | Fix implemented |
| PW-131 | Test fix for #1121: UI shows real errors, no fakes | PW-130 | 10m | test | Test passes |
| PW-132 | Close #1121 with fix | PW-131 | 10m | GitHub | Issue closed |
| PW-133 | Locate product model (root product/ or elsewhere) | — | 10m | codebase search | Product model location found |
| PW-134 | Document product model location if not /product/ | PW-133 | 10m | docs/PRODUCT-MODEL-LOCATION.md | Location documented |
| PW-135 | Audit product model for unused fields/relations | PW-133 | 10m | model code | Unused items listed |
| PW-136 | Verify product model supports A1/A2/A3 requirements | PW-133 | 10m | model check | Model adequate or identified gaps |
| PW-137 | Create in-memory observation test (capture runtime state) | — | 15m | tests/observations.rs | Test created |
| PW-138 | Test in-memory observations during A1 import | PW-137 | 10m | test run | Observations captured |
| PW-139 | Verify observations survive restart | PW-138 | 10m | test run | Observations persistent |
| PW-140 | Create performance test: import latency (target <30s for typical product) | — | 15m | tests/perf_import.rs | Test created |
| PW-141 | Measure import latency for selected product | PW-140 | 10m | perf test | Latency measured |
| PW-142 | Create parity latency test: UI vs CLI vs MCP vs API | — | 15m | tests/perf_parity.rs | Test created |
| PW-143 | Measure latency parity across surfaces | PW-142 | 10m | perf test | Latencies compared |
| PW-144 | Document performance baselines | PW-143 | 10m | docs/PERFORMANCE-BASELINES.md | Baselines documented |
| PW-145 | Create P4 completion gate checklist | — | 10m | docs/P4-GATE-CHECKLIST.md | Checklist created |
| PW-146 | Verify all P1 + P2 + P3 tasks complete | — | 10m | Gate review | P1–P3 complete |
| PW-147 | Run full CI on P4 deliverables | PW-146 | 10m | CI | All checks pass |
| PW-148 | Create P4→P5 dependency link | PW-147 | 10m | docs/03_DAG_WBS.md | P4 unlocks P5 noted |
| PW-149 | Commit all P4 changes | PW-148 | 10m | git commit | Changes committed |
| PW-150 | Push to origin/main (or feature branch) | PW-149 | 10m | git push | Pushed successfully |
| PW-151 | Write the contract for the items route family that currently returns 501 | PW-150 | 10m | items routes | Contract says 501 is a failed witness |
| PW-152 | Write the contract for the links route family that currently returns 501 | PW-151 | 10m | links routes | Contract says 501 is a failed witness |
| PW-153 | Write the contract for the graph route family that currently returns 501 | PW-152 | 10m | graph routes | Contract says 501 is a failed witness |
| PW-154 | Write the contract for the search route family that currently returns 501 | PW-153 | 10m | search routes | Contract says 501 is a failed witness |
| PW-155 | Write the contract for import/export routes that currently return 501 | PW-154 | 10m | import/export routes | Contract says 501 is a failed witness |
| PW-156 | Write the contract for journeys routes that currently return 501 | PW-155 | 10m | journeys routes | Contract says 501 is a failed witness |
| PW-157 | Write the contract for equivalences routes that currently return 501 | PW-156 | 10m | equivalences routes | Contract says 501 is a failed witness |
| PW-158 | Write the contract for AI routes that currently return 501 | PW-157 | 10m | AI routes | Contract says 501 is a failed witness |
| PW-159 | Record that project create returns success and writes nothing | PW-158 | 10m | project create handler | The no-op is captured with a test that expects a row |
| PW-160 | Record that project update returns success and writes nothing | PW-159 | 10m | project update handler | The no-op is captured with a test that expects a changed row |
| PW-161 | Record that project delete returns success and writes nothing | PW-160 | 10m | project delete handler | The no-op is captured with a test that expects a deleted row |
| PW-162 | Enumerate the edge worker routes | PW-161 | 10m | edge worker router | All routes are listed |
| PW-163 | Mark each edge worker route that returns 501 | PW-162 | 10m | edge worker handlers | The two live routes and the 501 routes are named |
| PW-164 | Move A1 observations from process memory to Postgres | PW-163 | 20m | observation store | A restart does not drop the observation |
| PW-165 | Prove observations are absent after restart until re-ingest, on the current in-memory store | PW-164 | 10m | observation store | The test fails while storage is in memory |
| PW-166 | Call the cache client from the A1 path or remove the unused startup client | PW-165 | 20m | cache client | No unused client remains at startup |
| PW-167 | Call the Neo4j client from a handler or remove the unused startup client | PW-166 | 20m | Neo4j client | No unused client remains at startup |
| PW-168 | Call the R2 client from a handler or remove the unused startup client | PW-167 | 20m | R2 client | No unused client remains at startup |
| PW-169 | Emit an OpenTelemetry span on the A1 import path | PW-168 | 20m | OpenTelemetry | A trace exists for one import |
| PW-170 | Mount tracera-graphql in the workspace or drop it from startup claims | PW-169 | 10m | tracera-graphql | The crate is in the workspace or absent from boot |
| PW-171 | Mount tracera-ml in the workspace or drop it from startup claims | PW-170 | 10m | tracera-ml | The crate is in the workspace or absent from boot |
| PW-172 | Mount tracera-neo4j in the workspace or drop it from startup claims | PW-171 | 10m | tracera-neo4j | The crate is in the workspace or absent from boot |
| PW-173 | Replace the tracera-workos RS256 JWKS TODO with verification against the JWKS | PW-172 | 20m | tracera-workos | A bad signature is rejected |
| PW-174 | Record a PILOT-PRD-TRACERA run sheet with the bounded product and the restart step | PW-173 | 10m | PILOT-PRD-TRACERA | The sheet exists and the pilot is still not run |
| PW-175 | Keep DELIVERY_REPAIR_PRODUCT_WITNESS_OPEN until the restart witness exists | PW-174 | 10m | docs-5 products/Tracera/STATE.md | Status is unchanged by this plan |

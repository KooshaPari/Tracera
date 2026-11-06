# Interface evidence leaves

> GENERATED from STATUS.json.

```text
G09.named-view-binding [crosscut] Named view code dispatch exists; complete type/project/detail parity is unqualified
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.code.tsx:16
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.code.tsx:16 | Source inspected; no matching external journey executed
  +-- Validation: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.code.tsx:16 | Static checks do not prove UI runtime
  +-- Assurance: UNKNOWN | No qualifying witness collected | No independent complete journey witness
G09.detail-scope [observation] Detail route fetches by itemId and forwards projectId; this source alone does not enforce route project/type equality
  +-- Implementation: UNKNOWN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.$viewType.$itemId.tsx:9 | Caller/source inspected; complete guard/call-chain qualification not performed. No failure of security boundary inferred.
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.$viewType.$itemId.tsx:9 | Source inspected; no matching external journey executed
  +-- Validation: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.$viewType.$itemId.tsx:9 | Static checks do not prove UI runtime
  +-- Assurance: UNKNOWN | No qualifying witness collected | No independent complete journey witness
G10.summary-fallback [observation] Summary explicitly says detailed data unavailable; typed totals/unknown health requirement unqualified
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/components/ProjectSummary.tsx:14
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/components/ProjectSummary.tsx:14 | Source inspected; no matching external journey executed
  +-- Validation: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/components/ProjectSummary.tsx:14 | Static checks do not prove UI runtime
  +-- Assurance: UNKNOWN | No qualifying witness collected | No independent complete journey witness
G11.ui-crud [observation] UI hooks perform actual item requests and project/view list filtering; durable cross-project rejection requires backend witness
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/hooks/useItems.ts:36
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/hooks/useItems.ts:36 | Source inspected; no matching external journey executed
  +-- Validation: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/hooks/useItems.ts:36 | Static checks do not prove UI runtime
  +-- Assurance: UNKNOWN | No qualifying witness collected | No independent complete journey witness
G12.mcp-graph [observation] MCP provides 1-hop subgraph; bounded cycles/truncation/source-anchor journey unqualified
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:crates/tracera-mcp/src/tools.rs:274
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:crates/tracera-mcp/src/tools.rs:274 | Source inspected; no matching external journey executed
  +-- Validation: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:crates/tracera-mcp/src/tools.rs:274 | Static checks do not prove UI runtime
  +-- Assurance: UNKNOWN | No qualifying witness collected | No independent complete journey witness
G14.route-contract [observation] Executed static endpoint audit finds 20 Rust-native and 19 gateway-owned entries; it permits namespace exemptions and does not test schemas/handlers
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/scripts/test-client-server-parity.mjs:34
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/scripts/test-client-server-parity.mjs:34 | Source inspected; no matching external journey executed
  +-- Validation: PASS | evidence/test-client-server-parity.log:1 | Static checks do not prove UI runtime
  +-- Assurance: UNKNOWN | No qualifying witness collected | No independent complete journey witness
G14.cli-crud-parity [observation] Current CLI enum has stack lifecycle commands only; required common Project/Item/Link CRUD is absent
  +-- Implementation: FAIL | 912303f689f0e335d4dad77a7767ef1e26098af7:crates/tracera-cli/src/commands.rs:41
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:crates/tracera-cli/src/commands.rs:41 | Source inspected; no matching external journey executed
  +-- Validation: FAIL | evidence/installed-cli-help.log:1 | Installed CLI help omits required CRUD surface; installed binary source provenance unqualified; source enum separately supports Implementation FAIL
  +-- Assurance: UNKNOWN | No qualifying witness collected | No independent complete journey witness
G14.mcp-crud-parity [observation] Current MCP graph tools operate SWEE nodes/edges/proposals, not common Project/Item/Link operation surface
  +-- Implementation: FAIL | 912303f689f0e335d4dad77a7767ef1e26098af7:crates/tracera-mcp/src/tools.rs:147
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:crates/tracera-mcp/src/tools.rs:147 | Source inspected; no matching external journey executed
  +-- Validation: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:crates/tracera-mcp/src/tools.rs:147 | Static checks do not prove UI runtime
  +-- Assurance: UNKNOWN | No qualifying witness collected | No independent complete journey witness
G17.desktop-origin [observation] Desktop source defaults rich gateway18000; legacy18081 opt-in
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/desktop/src/target.ts:7
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/desktop/src/target.ts:7 | Source inspected; no matching external journey executed
  +-- Validation: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/desktop/src/target.ts:7 | Static checks do not prove UI runtime
  +-- Assurance: UNKNOWN | No qualifying witness collected | No independent complete journey witness
G17.artifact-check-instrument [instrument] Deployment artifact checker exists; execution rejects missing build output in fresh source checkout; installed app not assessed
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/scripts/test-deployment-artifact.mjs:14
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/scripts/test-deployment-artifact.mjs:14 | Source inspected; no matching external journey executed
  +-- Validation: PASS | evidence/test-deployment-artifact.log:1-8 | Executed checker reports missing local dist; not installed-app acceptance
  +-- Assurance: UNKNOWN | No qualifying witness collected | No built artifact supplied; result cannot qualify installed deployment
G19.focus-source [observation] Focus/skip-link source exists. Existing a11y regex demands single quotes and rejects current double quotes; failure is test fragility, not observed keyboard failure
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/components/layout/Layout.tsx:149
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/components/layout/Layout.tsx:149 | Source inspected; no matching external journey executed
  +-- Validation: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/components/layout/Layout.tsx:149 | No rendered keyboard/focus journey; raw regex failure classified in separate instrument leaf
  +-- Assurance: UNKNOWN | No qualifying witness collected | No independent complete journey witness
G20.route-check-instrument [instrument] Route checker cannot qualify current route map because it reads removed App.jsx
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/scripts/test-ui-route-mapping.mjs:5 | Instrument source exists; usefulness assessed separately
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/scripts/test-ui-route-mapping.mjs:5 | Source inspected; no matching external journey executed
  +-- Validation: FAIL | evidence/test-ui-route-mapping.log:1-18 | Executed instrument errors before checking routes
  +-- Assurance: FAIL | evidence/test-ui-route-mapping.log:1-18 | Legacy input prevents current route assurance; not product route failure
G19.async-states [observation] Detail route renders loading and missing states; rendered usability unqualified
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.$viewType.$itemId.tsx:14
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.$viewType.$itemId.tsx:14 | Source inspected; no matching external journey executed
  +-- Validation: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.$viewType.$itemId.tsx:14 | Static checks do not prove UI runtime
  +-- Assurance: UNKNOWN | No qualifying witness collected | No independent complete journey witness
G19.explicit-unsupported [observation] Report template/generation APIs explicitly throw typed501 rather than fake success
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/api/reports.ts:24
  +-- Usability: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/api/reports.ts:24 | Source inspected; no matching external journey executed
  +-- Validation: NOT_RUN | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/api/reports.ts:24 | Static checks do not prove UI runtime
  +-- Assurance: UNKNOWN | No qualifying witness collected | No independent complete journey witness
G19.cli-help [observation] Installed CLI --help succeeds; binary hash provenance is not tied to current source commit
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:crates/tracera-cli/src/commands.rs:14
  +-- Usability: PASS | evidence/installed-cli-help.log:1 | Only --help invocation, no stack mutation or product operations
  +-- Validation: PASS | evidence/installed-cli-help.log:1 | Static checks do not prove UI runtime
  +-- Assurance: UNKNOWN | No qualifying witness collected | No independent complete journey witness
G09.view-01 [observation] Dashboard => Dashboard; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/index.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: FAIL | evidence/live-direct-paths.json:1 | DEPLOYED8091 source UNKNOWN; Observed ERR_EMPTY_RESPONSE for this direct path
  +-- Validation: FAIL | evidence/live-direct-paths.json:1 | DEPLOYED8091 source UNKNOWN; Guarded owned headless navigation executed; no artifact rendered
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-02 [observation] Projects => Projects; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: FAIL | evidence/live-direct-paths.json:1 | DEPLOYED8091 source UNKNOWN; Observed ERR_EMPTY_RESPONSE for this direct path
  +-- Validation: FAIL | evidence/live-direct-paths.json:1 | DEPLOYED8091 source UNKNOWN; Guarded owned headless navigation executed; no artifact rendered
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-03 [observation] Items => Items; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/items.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: FAIL | evidence/live-direct-paths.json:1 | DEPLOYED8091 source UNKNOWN; Observed ERR_EMPTY_RESPONSE for this direct path
  +-- Validation: FAIL | evidence/live-direct-paths.json:1 | DEPLOYED8091 source UNKNOWN; Guarded owned headless navigation executed; no artifact rendered
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-04 [observation] Agents => Agents; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/agents.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: FAIL | evidence/live-direct-paths.json:1 | DEPLOYED8091 source UNKNOWN; Observed ERR_EMPTY_RESPONSE for this direct path
  +-- Validation: FAIL | evidence/live-direct-paths.json:1 | DEPLOYED8091 source UNKNOWN; Guarded owned headless navigation executed; no artifact rendered
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-05 [observation] Overview => Overview; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-06 [observation] Feature Layer => Feature Layer; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.feature.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-07 [observation] Source Map => Source Map; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.code.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-08 [observation] Validation => Validation; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.test.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-09 [observation] Workflow Runs => Workflow Runs; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.$viewType.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-10 [observation] Project Settings => Project Settings; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.settings.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-11 [observation] Dashboard => Dashboard; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.specifications.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-12 [observation] Scenario Activity => Scenario Activity; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.scenario-activity.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-13 [observation] ADRs => ADRs; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.specifications.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-14 [observation] Contracts => Contracts; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.specifications.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-15 [observation] Compliance => Compliance; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.specifications.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-16 [observation] Features => Features; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.feature.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-17 [observation] Domain Model => Domain Model; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.domain.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-18 [observation] Problem Analysis => Problem Analysis; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.problem.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-19 [observation] Wireframes => Wireframes; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.wireframe.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-20 [observation] Code View => Code View; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.code.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-21 [observation] Architecture => Architecture; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.architecture.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-22 [observation] API Documentation => API Documentation; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.api.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-23 [observation] Database Schema => Database Schema; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.database.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-24 [observation] Data Flow => Data Flow; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.dataflow.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-25 [observation] Test Cases => Test Cases; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.test-cases.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-26 [observation] Test Suites => Test Suites; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.test-suites.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-27 [observation] Test Runs => Test Runs; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.test-runs.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-28 [observation] QA Dashboard => QA Dashboard; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.qa-dashboard.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-29 [observation] Coverage Report => Coverage Report; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.coverage.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-30 [observation] Journey Map => Journey Map; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.journey.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-31 [observation] Process Flow => Process Flow; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.process.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-32 [observation] Timeline => Timeline; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.monitoring.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-33 [observation] Reports => Reports; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.performance.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-34 [observation] Impact Analysis => Impact Analysis; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.$viewType.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-35 [observation] Traceability Matrix => Traceability Matrix; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.$viewType.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-36 [observation] Dependency Graph => Dependency Graph; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.dependency.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-37 [observation] Performance Metrics => Performance Metrics; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.performance.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-38 [observation] Security Analysis => Security Analysis; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.security.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-39 [observation] Monitoring Dashboard => Monitoring Dashboard; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.monitoring.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-40 [observation] Bug Tracking => Bug Tracking; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.problem.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-41 [observation] Integrations => Integrations; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.integrations.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-42 [observation] Webhooks => Webhooks; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.webhooks.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-43 [observation] Settings => Settings; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.settings.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-44 [observation] Settings => Settings; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/settings.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: FAIL | evidence/live-direct-paths.json:1 | DEPLOYED8091 source UNKNOWN; Observed ERR_EMPTY_RESPONSE for this direct path
  +-- Validation: FAIL | evidence/live-direct-paths.json:1 | DEPLOYED8091 source UNKNOWN; Guarded owned headless navigation executed; no artifact rendered
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-45 [observation] direct project route => projects.$projectId.adrs.$adrId; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.adrs.$adrId.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-46 [observation] direct project route => projects.$projectId.adrs; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.adrs.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-47 [observation] direct project route => projects.$projectId.agents; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.agents.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-48 [observation] direct project route => projects.$projectId.compliance; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.compliance.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-49 [observation] direct project route => projects.$projectId.contracts.$contractId; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.contracts.$contractId.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-50 [observation] direct project route => projects.$projectId.contracts; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.contracts.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-51 [observation] direct project route => projects.$projectId.equivalence; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.equivalence.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-52 [observation] direct project route => projects.$projectId.features.$featureId.scenarios.$scenarioId; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.features.$featureId.scenarios.$scenarioId.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-53 [observation] direct project route => projects.$projectId.features.$featureId; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.features.$featureId.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-54 [observation] direct project route => projects.$projectId.features; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.features.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-55 [observation] direct project route => projects.$projectId.temporal; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.temporal.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-56 [observation] direct project route => projects.$projectId.views.$viewType.$itemId; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.$viewType.$itemId.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-57 [observation] direct project route => projects.$projectId.views.$viewType; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.$viewType.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-58 [observation] direct project route => projects.$projectId.views.configuration; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.configuration.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G09.view-59 [observation] direct project route => projects.$projectId.views.infrastructure; source presence and separately deployed runtime are distinct subjects
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/apps/web/src/routes/projects.$projectId.views.infrastructure.tsx:1 | Route file existence only; complete artifact binding not accepted
  +-- Usability: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Validation: NOT_RUN | evidence/live-view-report.json; evidence/direct8080-feasibility.json:1 | DEPLOYED8091 source UNKNOWN; Deployed8091 frontend listener absent; direct8080 root404 despite API200. Existing project IDs are known, but no served UI subject remains for per-artifact navigation.
  +-- Assurance: UNKNOWN | evidence/live-view-report.json | DEPLOYED8091 source UNKNOWN; Fresh CLI witness concerns transport, not independent full artifact correctness
G20.a11y-check-instrument [instrument] A11y checker regex rejects double-quoted skip-link markup already present in source
  +-- Implementation: PASS | 912303f689f0e335d4dad77a7767ef1e26098af7:frontend/scripts/test-ui-a11y-contract.mjs:18
  +-- Usability: PASS | evidence/test-ui-a11y-contract.log:1-6 | Checker invocable only; product keyboard journey unqualified
  +-- Validation: FAIL | evidence/test-ui-a11y-contract.log:1-6 | Executed assertion fails
  +-- Assurance: FAIL | evidence/test-ui-a11y-contract.log:1 | False-negative quote-sensitive instrument; product AX remains unqualified
```

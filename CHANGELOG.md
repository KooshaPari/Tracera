# Changelog

All notable changes to this project will be documented in this file.

## [v2.0.1] - 2026-03-29

### <!-- 0 -->🚀 FEATURES

- Geist-style dark theme overhaul for TraceRTM (#209) (`9046edf`)
- Geist fonts, hover-to-expand previews, clickable timeline cards (#212) (`2ac8a8d`)
- Evidence gallery with lightbox (#240) (`cd6a2c3`)
- Add perf benchmarks and topo-sort unit tests (#247) (`b895bbf`)
- Geist dark theme overhaul with hover-expand tooltips and clickable timeline (#242) (`e14ef18`)

### <!-- 1 -->🐛 BUG FIXES

- Add @types/node for tailwind.config.ts type resolution (#213) (`0e32e05`)
- Fix YAML syntax errors in ci.yml and qa-governance.yml (#215) (`3800781`)
- Resolve phenodocsTheme undefined breaking VitePress build (#216) (`11a196a`)
- Repair broken CI workflow configurations (#221) (`4543097`)
- Increase Node heap size to prevent OOM on tsc --build (#246) (`87603de`)
- Fix YAML syntax errors in ci.yml and qa-governance.yml (#241) (`5ae4571`)
- Types-node upgrade and Tailwind/Geist UI improvements (#249) (`ecfab33`)
- Resolve Vite 8 beta + rolldown build failures (#251) (`1d38c95`)
- Remove duplicate 'with' key in setup-node step (#255) (`0e95bc1`)
- Add @types/react and @types/react-dom dev dependencies (#257) (`406c3a0`)
- Resolve all TypeScript errors in web frontend (#260) (`50aed4b`)

### <!-- 10 -->💼 OTHER

- Port trace required-gates commits (linear) (#175) (`ea47fb5`)
- Merge upstream main (#192) (`670dc2e`)
- Untrack vault tokens, env files, and k8s secrets (#206) (`d8b9975`)

### <!-- 3 -->📚 DOCUMENTATION

- Add granular dependabot vulnerability worklog with 30 issues (`ea9a59b`)
- Add security scanning workflow and vulnerability worklogs for thegent and 4sgm (`98515b4`)
- Add security worklog index and comprehensive vulnerability tracking (`68fc66a`)
- Update 4sgm worklog with fixed items (`accbba8`)
- Unify docs IA with VitePress super-categories (#154) (`2dea8d6`)
- Add comparison matrix (#200) (`3a8fdda`)
- Replace stub specs with real project-specific documentation (#208) (`adfdde3`)
- Add ADR.md and PLAN.md root-level spec documents (#244) (`b9dc386`)
- Add real ADR.md with 12 architecture decisions derived from codebase (#253) (`4d7f9c6`)
- Add docs-site scaffold and verification harness (#259) (`99d7bcc`)

### <!-- 7 -->⚙️ MISCELLANEOUS TASKS

- Update ignore and readme (`d9039fc`)
- Enforce layered fix PR gate (#153) (`27e5dbe`)
- Add automated alert-to-issue sync workflow (#155) (`1381aaf`)
- Add worktrees/ to gitignore (#183) (`0d2df6f`)
- Required-gates-fresh3 (#191) (`8b5e020`)
- Required-gates-fresh2-linear-fix2-clean (#190) (`d89e23a`)
- Required-gates-fresh2-linear-fix1 (#189) (`2c19008`)
- Required-gates-fresh2 (#188) (`f25dfd4`)
- Required-gates-fresh (#187) (`2581561`)
- Add automated alert-to-issue sync workflow (#185) (`d53df17`)
- Chore/add-worktrees-gitignore (#184) (`1370db9`)
- Modernize tooling to 2026 standards (#193) (`4489695`)
- Replace BMAD/spec-kitty with AgilePlus governance (#195) (`968597f`)
- Add spec docs (PRD.md, FUNCTIONAL_REQUIREMENTS.md) (#198) (`725c10c`)
- Remove obsolete version from docker-compose files (#199) (`9787d9d`)
- Remove obsolete version from docker-compose files (#207) (`39e2656`)
- Remove duplicated governance blocks, reference thegent templates (#210) (`9d7d13b`)
- Migrate kitty-specs to AgilePlus format, archive BMAD refs (#211) (`f8aa091`)
- Add process-compose.yml for local dev stack (#214) (`27f7f39`)
- Migrate top 20 TODOs to GitHub Issues (#238) (`34df4bc`)
- Add no-new-todos and markdownlint hooks (#239) (`cfc8818`)
- Archive .bmad directory (#254) (`1681e4d`)
- Add Go benchmark CI workflow (#256) (`3060200`)
- Update go.mod, docs config, and test harness (#261) (`b1f1131`)

## [v2.0.0] - 2026-02-23

### <!-- 0 -->🚀 FEATURES

- Parallelize process-compose startup (60s → 30s) (`dac1ee3`)
- Add dependency caching to GitHub Actions workflows (`b865bee`)
- Complete Docker layer optimization (Task #63) (`8780b28`)
- Add test user creation scripts for WorkOS and database (`4a5ffdf`)
- Add WebSocket CORS validation tests with log collection and failed-routes reporting (`2d1b0da`)
- Add comprehensive route validation E2E tests (`645c81a`)
- Add comprehensive API routes validation tests with detailed reporting (`c95b869`)
- Add Go route validation tests with CORS header verification (`8cac6a9`)
- Add Python route validation tests with comprehensive reporting (`05144b5`)
- Add comprehensive test validation Makefile targets and GitHub Actions CI/CD (`2533b2d`)
- Resolve 70 TypeScript compilation errors, fix Dashboard tests, optimize code quality (`9ad60d0`)
- Add CI coverage regression detection (`82e7d0b`)
- Complete Gap 5.1-5.2 (WebGL + OAuth events) implementation (`222c51d`)
- Gap 5.3 Phase 1 - extend MSW handlers with reports/search endpoints and test data fixtures (`d8bc404`)
- Gap 5.3 Phase 2 - add global cleanup and async test helpers (`1cd5c0e`)
- Gap 5.5 Phase 1 - add tableTestItems fixture with 8 items for accessibility testing (`24405fb`)
- Gap 5.6 Phase 1 - re-enable API endpoints test suite (describe.skip → describe, add logger) (`a71db3c`)
- Phase 6 Track 4 - Deployment Readiness implementation complete (`eed1df6`)
- Week 1 DX components - skills, hooks, agents (`eb4a0da`)
- Complete OpenTelemetry Python backend instrumentation (`13bba85`)
- Achieve 100/100 Quality - All Tests Passing (`a9670d6`)
- Phase 5 maximum strictness - auto-fix 1,022 files (`3572316`)
- Phase 5 agent swarm - fix 42,761 violations (99.2% reduction) (`cabe2fb`)
- Extract magic values to named constants (PLR2004) (`f44e878`)
- Agent swarm 31.7% reduction - fix 6,672 violations (`462f354`)

### <!-- 1 -->🐛 BUG FIXES

- TypeScript compilation and production build issues (`e17bbce`)
- Address critical security vulnerabilities in snapshot and storage services (`ae41d13`)
- Replace weak random with crypto/rand for jitter (G404) (`c0821d6`)
- Enhance naming explosion detection for phase suffixes (Phase 2) (`74b11b6`)
- Remove unreachable code in dev-start-with-preflight.py (`91a3829`)
- Eliminate all naming explosion violations in test files (`dfe7607`)
- Eliminate AI naming explosion violations in test files (`7ef4ae2`)
- Resolve TypeScript module errors for enterprise-table and loading-skeleton (`eeb3feb`)
- Rename phase-numbered test files to canonical names (`6729d6a`)
- Eliminate remaining naming explosion violations (`3ee3697`)
- Remove duplicate script files with part# suffixes (`b2731fc`)
- Resolve type errors in main.py from module integration (`34aec6f`)
- Resolve TypeScript diagnostics in Phase 2 E2E tests (remove unused imports, fix deprecated timing API, update status types) (`a00e219`)
- Resolve TypeScript diagnostics in route-validation tests (add proper types, remove unused variables) (`5077845`)
- Use correct property name 'route' instead of 'path' in API test result display (`5b23a19`)
- Remove unused parameters from pytest test fixtures (capsys, mock_db) (`520ca75`)
- Fix Dashboard test failures (21/21 tests passing) (`853cffb`)
- Add missing vitest imports to Dashboard.test.tsx (`811bcb8`)
- Remove unused Skeleton import from ProjectsListView (`083b79c`)
- Correct vitest setupFiles path and add missing user event imports (`ac032c4`)
- GATE C remediation - localStorage mock, benchmark exclusion, component exports (`233022b`)
- Enable app-integration tests with MSW server initialization and router mocks (`a004046`)
- Setup.ts JSX syntax and duplicate imports for test environment (`f3af696`)
- Disable MSW in setup.ts to unblock test execution (GraphQL ESM/CommonJS issue) (`cdd1f8a`)
- Re-enable MSW server with error handling for graceful degradation (`4bc425d`)
- Re-enable MSW server with error handling for test HTTP mocking (`abc3ae9`)
- Resolve TypeScript compilation blocker - add @types/node and update tsconfig types array (`65eb1e2`)
- Disable MSW temporarily due to graphql ESM/CommonJS import failure (`87367db`)
- Export isAuthError from api-error-handler and fix import statements (`acd3a8b`)
- Resolve JSX namespace errors by adding React type reference (`c635ec9`)
- Resolve health handler framework and Temporal SDK issues (`619f7a2`)
- Achieve 100% mypy --strict type coverage (`b11eea9`)
- Add missing bytes import to s3_coverage_test.go (`8ceca0a`)
- Resolve TypeScript compilation errors in test files (`d21c99d`)
- Fix schema validation tests to use tracertm_test database and handle schema differences (`42cc073`)
- Fix concurrent transaction test with sqlmock ordering (`e1448a7`)
- Restore main.go and fix build errors (`71421b9`)
- Add **kwargs type annotations (ANN003) - 117 violations fixed (`f3d62be`)
- Add type annotations to github.py handlers (`a83cdae`)
- Suppress ARG violations with noqa comments (`887ff29`)
- Add noqa for 74 ARG violations (`57d563c`)
- Add type annotations to chat.py handlers (`1b0254f`)
- Add type annotations to websocket, device, health, items (`9e124e6`)
- Correct invalid type annotation syntax in 7 files (`39076ad`)
- Complete router type annotations (`3b6a7f1`)
- Add **kwargs type annotations (ANN003) - 9 violations fixed (`efefb1f`)

### <!-- 10 -->💼 OTHER

- Fix shell injection vulnerability in complete_setup.py (`391cace`)
- Remove migration file with newline in name (`e87bb18`)

### <!-- 2 -->🚜 REFACTOR

- Add complexity limits to ruff configuration (`6642d81`)
- Activate AI-strict oxlint configuration (`b29486c`)
- Add missing linters and tighten complexity limits (`706899b`)
- Fix critical type safety violations in core utilities (Phase 2) (`9156795`)
- Fix type safety violations batch 1 (Phase 2) (`cd90458`)
- Fix type safety violations batch 2 (Phase 2) (`fa55700`)
- Remove Biome, consolidate to oxlint+oxfmt (Phase 2) (`0549cd8`)
- Reduce complexity in migrations 008 and 009 (Phase 3) (`4d9f4e9`)
- Reduce complexity in scan_docs.py (Phase 3) (`4072b34`)
- Extract duplicate lock logic (Phase 3) (`1347a13`)
- Reduce complexity in quality-report.py (Phase 3) (`b77afe6`)
- Reduce complexity in seed_swiftride_tracertm.py SQL parser (Phase 3) (`29a3116`)
- Reduce complexity in dev-start-with-preflight.py (Phase 3) (`1c071ff`)
- Further reduce complexity in quality-report.py (Phase 3) (`f245435`)
- Reduce complexity in validate_seed_and_access.py (Phase 3) (`94531d7`)
- Reduce complexity in test_migrations.py (Phase 3) (`259dc75`)
- Modernize Go syntax in NATS tests (`14493e2`)
- Extract list_links function to reduce complexity (C901) (`6fbc522`)

### <!-- 3 -->📚 DOCUMENTATION

- Add process-compose quick reference guide (`9c46955`)
- Complete Phase 1 linting hardening documentation (`fc2daf6`)
- Add Phase 1 final status executive summary (`61a7599`)
- Add list_links extraction completion report (`de31a95`)
- Add Phase 2 Task 2 completion report and quick reference (`c15ce8b`)
- Add comprehensive test validation guide and quick reference (`65aac13`)
- Add Phase 6 completion status - dashboard tests and Lighthouse budgets (`c74d9fd`)
- Add comprehensive Session 2 critical vitest setupFiles fix report (`3026d02`)
- Phase 5.1-5.2 verified deliverables - WebGL visual regression and OAuth NATS events (`f2729c7`)
- Reorganize Phase 5 documentation into docs/reports/ (CLAUDE.md structure) (`bb593a3`)
- Phase 5 Checkpoint 3 - MSW fixes validated, 15+ tests passing, Wave 3 launch ready (`267e49f`)
- Move all phase/checkpoint documentation to docs/reports/ (`b672f4d`)
- Session 4 documentation cleanup complete - Phase 3 execution LIVE (`dfce1de`)
- Checkpoint 3 orchestration - Wave 3 launch briefing and monitoring prepared (T+55) (`7e7b26c`)
- Session 5 checkpoint status - Wave 2 Phase 2 active, Gap 5.4 complete, Wave 3 on track (`d315736`)
- Document timeline discrepancy with integration-tests-architect message (T+55 vs T+0) (`4334fa0`)
- T+45 gate validation results - GATES UNBLOCKED, ready for Phase 3 (`13fef40`)
- Checkpoint 3 live monitoring dashboard - T+55 orchestration active, all waves executing (`c6e042b`)
- T+45 checkpoint summary - GATES UNBLOCKED, Phase 3 authorization ready (`a5f92b5`)
- Phase 5 Checkpoint 3 execution validation - 65+ tests on track for T+100 completion (`01da1c1`)
- Session 5 implementation status - Gaps 5.3, 5.5 Phase 1-3 complete, ready for continuation (`bd3251e`)
- Phase 5 coordination clarification - halt Phase 3 loop, refocus teams on triple-wave execution (`cb42fe0`)
- CRITICAL BLOCKER - MSW GraphQL ESM import failure + resolution plan (`0ebe769`)
- Session 6 executive summary - Phase 5 validation complete, critical MSW blocker identified, coordination clarified (`d3840a7`)
- Phase 5 status at T+55 - critical MSW blocker identified, 45 minutes to deadline, user action required (`795ea19`)
- TEAM LEAD FINAL DECISION - Phase 5 only, Phase 3 permanently closed. Adjusted targets: 34 tests (Wave 1 + 5.4 + 5.7 + 5.8) (`8dcd560`)
- Session 7 build unblocking completion report (`f7825f0`)
- ENFORCEMENT - Phase 3 coordination permanently terminated. No further Phase 3 messages will receive responses. (`c6e0121`)
- Wave 4 Final Quality Campaign Report (Waves 1-4 consolidated) (`adf3dcd`)
- Add vitepress pages pipeline and role-based docsets (`54ebbd6`)
- Add changelog system process and templates (`5b639cd`)
- Populate CHANGELOG with v2.0.0 features from ADRs and phases (`9a3c89b`)

### <!-- 6 -->🧪 TESTING

- Skip memory-intensive tests to allow main suite to complete (`02e9884`)
- Add 80+ comprehensive tests to server package (6.9% → 7.8%) (`ab396f4`)

### <!-- 7 -->⚙️ MISCELLANEOUS TASKS

- Update workflows for Phase 1 linting enforcement (`042d2b3`)
- Optimize pre-commit hooks for Phase 1 linting (`91339f2`)
- Track backend Go module files in version control (`9b96dc6`)
- Cleanup agent coordination files (`4ad704f`)
- Initial commit of all tracked and untracked files (`ce78908`)
- Enable github pages setup in vitepress workflow (`052a2bb`)
- Add vercel-ai style setup baseline commands (`1fc77b0`)

## [v1.1.0] - 2026-02-01

### <!-- 0 -->🚀 FEATURES

- Add process-compose base configuration (`f6757fc`)
- Add infrastructure layer to process-compose (`7e5a5a7`)
- Add workflow and monitoring layer (`4c60e4c`)
- Add monitoring exporters layer (`7a885bb`)

### <!-- 1 -->🐛 BUG FIXES

- Update test selectors to match actual UI implementation (`710c4f9`)
- Fix search.spec.ts syntax and formatting errors (`d6d1290`)

### <!-- 10 -->💼 OTHER

- Add comprehensive conflict_resolver tests with 97.87% coverage (`3b894a6`)
- Add 39 comprehensive tests for item.py CLI coverage (163 total tests) (`a5d7bd4`)
- Add 94 comprehensive storage medium tests (100% coverage) (`daacdfc`)
- Add comprehensive repository & core layer tests with 100% coverage (`555d46d`)
- Comprehensive API Layer Tests (138 tests, 122 passing) (`a92eaa9`)
- Remediation Completion Report - 82% Complete, Production Ready (`4e51672`)
- Complete filebase cleanup - delete 326 archived .md files from root (now in ARCHIVE/) (`367e3fa`)
- Comprehensive multi-language codebase validation report (`70e6050`)
- Go mutex copy warning in embeddings indexer (`34289b9`)
- Comprehensive Test Coverage Report (all languages) (`00d285d`)
- Resolve all 50 mypy type errors in src/tracertm/api/client.py (`fe26097`)
- Resolve 30+ mypy type errors in service stubs and widgets (`6c05a7b`)
- Resolve all failing unit tests - Header and useLinks (batch 1) (`c553df4`)
- Resolve failing Header and useLinks tests (`5baf85b`)
- Replace Dagre with ELKjs for ESM compatibility (`4984af5`)
- Add comprehensive unit tests for repository layer (`d3c4c26`)
- Add implementation summary for repository tests (`e04a635`)
- Add test completion report with detailed coverage analysis (`c63ac6e`)
- Resolve 22+ performance test failures with async/mock fixes (`c26d2f2`)
- Resolve TaskError/TaskResult type snake_case naming mismatch in cancelTask (`46ee68d`)
- Implement comprehensive accessibility improvements - keyboard navigation, focus management, ARIA landmarks (`ea57953`)
- Add comprehensive accessibility implementation documentation (`40ab173`)
- Repair integration workflow E2E tests for multi-step workflows (`88e1398`)
- Add accessibility quick reference guide for developers (`f84d55e`)
- Complete cross-perspective search implementation with advanced features (`c2874ed`)
- Migrate all graph components to use progressive edge loading (`e5a3572`)
- Update API client to use proper typing and fix regex syntax errors (`16c680f`)
- Map snake_case API response to camelCase for link rendering (`21455c3`)
- Add viewport frustum culling for graph performance optimization (Phase 1) (`37bdbb2`)
- Implement virtual scrolling in ItemsTableView for 400-600% performance improvement (`affbb08`)

### <!-- 3 -->📚 DOCUMENTATION

- Add comprehensive E2E fixes completion summary (`d63b805`)
- Add comprehensive E2E testing guides and best practices (`229a200`)
- Add comprehensive backend test coverage analysis report (`da2f1d5`)
- Add test coverage summary and quick reference (`a613f60`)
- Add complete index for backend test coverage analysis (`89f2333`)
- Add START_HERE guide for navigation (`05e276a`)
- Add comprehensive production release documentation suite (`6d8e5a6`)
- Add native process orchestration design (`0b7d189`)
- Add native process orchestration implementation plan (`8896e53`)

### <!-- 8 -->🛡️ SECURITY

- Resolve failing unit tests in frontend (`cbbbc6c`)

## [v1.0.0] - 2025-12-03


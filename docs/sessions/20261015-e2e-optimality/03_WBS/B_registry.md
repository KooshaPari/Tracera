# B. Registry: Catalog Reconciliation & Canonical Product Identity

**Phase:** P2 (Registry)  
**Task Prefix:** R-001..R-100  
**Goal:** Fix catalog/registry.yaml, reconcile cards, mark Tracera active, resolve contradictions  
**Depends On:** P1  
**Unlocks:** P3 AgilePlus onboarding

---

## Registry Tasks (100 Leaf Tasks)

| Task | Description | Depends On | Est | Surface | Acceptance |
|------|-------------|-----------|-----|---------|-----------|
| R-001 | Load phenotype-registry catalog and list all product entries | — | 10m | catalog/registry.yaml | List all product IDs and names |
| R-002 | Audit Tracera entry in registry | R-001 | 10m | projects/Tracera.json | Entry exists, active status |
| R-003 | Find duplicate Tracera-2026-06-25.json card | R-001 | 10m | projects/ | Locate all Tracera-*.json files |
| R-004 | Check AgilePlus entry in registry | R-001 | 10m | projects/AgilePlus.json | Verify present and active |
| R-005 | Check Paperclip entry in registry | R-001 | 10m | projects/Paperclip.json | Verify present (may be new) |
| R-006 | Check PhenoRegistry entry in registry | R-001 | 10m | projects/PhenoRegistry.json | Verify present and active |
| R-007 | Check Portal entry in registry | R-001 | 10m | projects/Portal.json | Check if fragmented across repos |
| R-008 | Document current registry state (snapshot) | R-001..R-007 | 10m | docs/REGISTRY-SNAPSHOT-20261015.md | Snapshot file created |
| R-009 | Determine which Tracera.json is canonical | R-002, R-003 | 10m | GitHub branch history | Decision: use projects/Tracera.json (ID 1162254344) |
| R-010 | Mark Tracera as active (not archived) in canonical entry | R-009 | 10m | projects/Tracera.json | "active": true, "archived": false |
| R-011 | Remove disposition "TOO_LARGE_RETIRE" or mark superseded | R-010 | 10m | projects/Tracera.json | Field removed or updated |
| R-012 | Delete or archive stale Tracera-2026-06-25.json | R-009 | 10m | projects/Tracera-2026-06-25.json | File deleted or moved to archive/ |
| R-013 | Add all core product entries if missing | R-001 | 20m | catalog/registry.yaml | Create stubs for missing products |
| R-014 | Validate registry.yaml schema (YAML structure) | R-013 | 10m | catalog/registry.yaml | Schema validation passes |
| R-015 | Check for required fields in each product entry | R-014 | 10m | catalog/registry.yaml | All products have: id, name, github_url, status |
| R-016 | Add GitHub canonical ID for Tracera (1162254344) | R-010 | 10m | projects/Tracera.json | "github_id": "1162254344" |
| R-017 | Add GitHub canonical ID for AgilePlus | R-004 | 10m | projects/AgilePlus.json | GitHub ID added |
| R-018 | Add GitHub canonical ID for Paperclip | R-005 | 10m | projects/Paperclip.json | GitHub ID added |
| R-019 | Add GitHub canonical ID for PhenoRegistry | R-006 | 10m | projects/PhenoRegistry.json | GitHub ID added |
| R-020 | Document canonical GitHub repos in registry | R-016..R-019 | 10m | docs/REGISTRY-CANONICAL-REPOS.md | Canonical repo map created |
| R-021 | Audit SDK code parsing registry | — | 10m | SDK code rg "ECOSYSTEM_MAP\|registry" | Find all registry reads |
| R-022 | Check if SDK reads ECOSYSTEM_MAP.md (old) | R-021 | 10m | SDK source | Confirm old behavior |
| R-023 | Create SDK update task: switch from ECOSYSTEM_MAP to registry.yaml | R-022 | 10m | docs/SDK-UPDATE-PLAN.md | Plan documented |
| R-024 | Implement SDK registry read from catalog/registry.yaml | R-023 | 20m | SDK code | Function added, tested |
| R-025 | Test SDK registry load with 5+ product entries | R-024 | 10m | SDK tests | 5+ products load correctly |
| R-026 | Update SDK error handling for missing products | R-024 | 10m | SDK code | Clear error on unknown product |
| R-027 | Deprecate ECOSYSTEM_MAP.md in SDK docs | R-024 | 10m | SDK README | Deprecation notice added |
| R-028 | Add registry CLI tool: list all products | — | 15m | crates/tracera-registry-cli/src/main.rs | `tracera-registry list` works |
| R-029 | Add registry CLI tool: validate registry.yaml | R-028 | 15m | CLI code | `tracera-registry validate` works |
| R-030 | Add registry CLI tool: sync check (detect stale cards) | R-028 | 15m | CLI code | `tracera-registry sync --check` works |
| R-031 | Add registry CLI tool: auto-sync (update active status) | R-028 | 20m | CLI code | `tracera-registry sync --apply` updates entries |
| R-032 | Test CLI validate against current registry.yaml | R-029 | 10m | CLI tests | Validation passes |
| R-033 | Create registry validation pre-commit hook | R-029 | 10m | .git/hooks/pre-commit | Hook blocks invalid YAML |
| R-034 | Create registry validation GitHub action | R-029 | 10m | .github/workflows/registry-validate.yml | CI runs on every PR |
| R-035 | Document registry structure in ARCHITECTURE.md | R-014 | 10m | docs/ARCHITECTURE.md | Registry schema section added |
| R-036 | Audit intent/boundary docs for Tracera | — | 10m | docs/intent/, docs/boundary/ | Count existing stubs |
| R-037 | Audit intent/boundary docs for AgilePlus | R-036 | 10m | docs/intent/, docs/boundary/ | Count existing stubs |
| R-038 | Audit intent/boundary docs for other core products | R-036 | 10m | docs/intent/, docs/boundary/ | Total stub count |
| R-039 | Create task batch for Tracera intent doc stubs (batch 1-10) | R-036 | 10m | docs/INTENT-BATCH-TRACERA-1.md | Batch task list |
| R-040 | Create task batch for Tracera boundary doc stubs (batch 1-10) | R-036 | 10m | docs/BOUNDARY-BATCH-TRACERA-1.md | Batch task list |
| R-041 | Create task batch for AgilePlus intent docs (batch 1-10) | R-037 | 10m | docs/INTENT-BATCH-AGILEPLUS-1.md | Batch task list |
| R-042 | Populate Tracera intent doc batch 1 (10 stubs → brief descriptions) | R-039 | 20m | docs/intent/tracera/ | 10 intent files populated |
| R-043 | Populate Tracera boundary doc batch 1 (10 stubs → API boundaries) | R-040 | 20m | docs/boundary/tracera/ | 10 boundary files populated |
| R-044 | Populate AgilePlus intent doc batch 1 (10 stubs) | R-041 | 20m | docs/intent/agileplus/ | 10 intent files populated |
| R-045 | Link all intent docs to registry entries | R-042..R-044 | 10m | projects/*.json | Intent URLs added to entries |
| R-046 | Create Portal ownership documentation | — | 10m | docs/PORTAL-OWNERSHIP.md | Document: /parent/ belongs to job-cockpit |
| R-047 | Map Portal fragments across 5 repos | R-046 | 15m | docs/PORTAL-FRAGMENTS-MAP.md | Map each fragment to owner |
| R-048 | Link Portal ownership doc to registry | R-046 | 10m | projects/Portal.json | Portal entry references ownership doc |
| R-049 | Create Paperclip entry (if missing) with description | R-005 | 10m | projects/Paperclip.json | Entry created with metadata |
| R-050 | Add Paperclip to all core-products list | R-049 | 10m | docs/, config/ | Paperclip listed as core |
| R-051 | Locate all WP-FED-* federation task stubs in registry | — | 10m | projects/ | Find federation task IDs |
| R-052 | Register WP-FED-01 (Tracera schema integration) in registry | R-051 | 10m | projects/Tracera.json | WP reference added |
| R-053 | Register WP-FED-02 (AgilePlus schema integration) in registry | R-051 | 10m | projects/AgilePlus.json | WP reference added |
| R-054 | Register WP-FED-03 (Paperclip integration) in registry | R-051 | 10m | projects/Paperclip.json | WP reference added |
| R-055 | Register WP-FED-04 (Portal integration) in registry | R-051 | 10m | projects/Portal.json | WP reference added |
| R-056 | Register WP-FED-05 through WP-FED-12 federation tasks | R-055 | 30m | projects/ | All 12 WPs registered |
| R-057 | Create federation test: load registry → verify all WPs present | R-056 | 10m | tests/integration/registry_federation.rs | Test passes |
| R-058 | Verify registry.yaml valid YAML (no syntax errors) | R-014 | 10m | yaml linter | No errors |
| R-059 | Verify registry entries have no circular dependencies | R-045 | 10m | dependency analyzer | No cycles found |
| R-060 | Check for duplicate product IDs across entries | R-014 | 10m | rg "id.*:" projects/ | All IDs unique |
| R-061 | Verify all required products present and active | R-050 | 10m | registry-validate CLI | 5+ core products active |
| R-062 | Create registry sync CI job (check-only mode) | R-034 | 10m | .github/workflows/ | CI job defined |
| R-063 | Create registry sync script (dry-run) | R-031 | 10m | scripts/registry-sync.sh --dry-run | Script works |
| R-064 | Test registry sync dry-run against current state | R-063 | 10m | scripts/registry-sync.sh --dry-run | No unexpected changes |
| R-065 | Create documentation: "Registry Architecture & Sync" | R-035 | 15m | docs/REGISTRY-ARCHITECTURE.md | Doc covers: schema, sync, ownership |
| R-066 | Add registry troubleshooting guide | R-065 | 10m | docs/REGISTRY-TROUBLESHOOTING.md | Common issues + fixes documented |
| R-067 | Create registry audit checklist | R-065 | 10m | docs/REGISTRY-AUDIT-CHECKLIST.md | Quarterly audit procedure |
| R-068 | Link Tracera dossier from registry | R-010 | 10m | projects/Tracera.json | Dossier URL added |
| R-069 | Link AgilePlus dossier from registry | R-004 | 10m | projects/AgilePlus.json | Dossier URL added |
| R-070 | Link other product dossiers from registry entries | R-068, R-069 | 10m | projects/ | All core products have dossier links |
| R-071 | Verify all Tracera references in repo point to canonical ID | R-009 | 10m | rg "Tracera\|1162254344" crates/ | Consistent refs found |
| R-072 | Create migration guide: ECOSYSTEM_MAP → registry | R-027 | 10m | docs/MIGRATION-ECOSYSTEM-MAP-TO-REGISTRY.md | Guide for teams |
| R-073 | Update all SDKs to use registry (not ECOSYSTEM_MAP) | R-024 | 20m | SDK code | All SDKs use registry |
| R-074 | Test SDK with prod registry (5+ active products) | R-073 | 10m | SDK integration test | Load test passes |
| R-075 | Verify SDK errors gracefully on missing registry | R-026 | 10m | SDK error test | Clear error message |
| R-076 | Create registry snapshot for P2 sign-off | R-070 | 10m | docs/REGISTRY-SNAPSHOT-P2-SIGNOFF.md | Snapshot created |
| R-077 | Verify all P1 tasks completed (case-sensitivity, 501 routes, unused code) | — | 10m | Gate review | P1 done before P2 proceeds |
| R-078 | Run full CI (lint, type check, test) on registry changes | R-034..R-065 | 10m | CI | All checks pass |
| R-079 | Create P2→P3 dependency link | R-070 | 10m | docs/03_DAG_WBS.md | P2 unlocks P3 annotation added |
| R-080 | Final registry validation (automated) | R-034 | 10m | registry-validate CLI | All entries valid |
| R-081 | Document registry ownership and maintenance | R-065 | 10m | docs/REGISTRY-OWNERSHIP.md | Ownership matrix created |
| R-082 | Archive registry changelog for audit | R-008 | 10m | docs/REGISTRY-CHANGELOG-P2.md | Changelog created |
| R-083 | Create registry issue template for product card updates | R-067 | 10m | .github/ISSUE_TEMPLATE/registry-update.md | Template created |
| R-084 | Test registry load performance (100+ products) | R-024 | 10m | perf test | Load time <500ms |
| R-085 | Document registry data format (JSON schema) | R-015 | 10m | docs/REGISTRY-SCHEMA.json | JSON schema created |
| R-086 | Create registry backup procedure | R-065 | 10m | docs/REGISTRY-BACKUP.md | Backup strategy documented |
| R-087 | Add registry monitoring/alerting | — | 10m | monitoring config | Alerts on registry changes |
| R-088 | Create registry import/export tools | R-028 | 20m | CLI tools | Import/export functions added |
| R-089 | Test registry import/export round-trip | R-088 | 10m | tests | Round-trip successful |
| R-090 | Document registry versioning strategy | R-065 | 10m | docs/REGISTRY-VERSIONING.md | Version strategy documented |
| R-091 | Create P2 completion gate checklist | — | 10m | docs/P2-GATE-CHECKLIST.md | Checklist for sign-off |
| R-092 | Verify all core products in registry with canonical URLs | R-068..R-070 | 10m | registry check | All products linked |
| R-093 | Create registry-driven product discovery UI mock | R-028 | 15m | UI sketch | Mock created |
| R-094 | Document registry API contract | R-024 | 10m | API.md | Contract defined |
| R-095 | Create registry diff tool (compare two snapshots) | R-028 | 20m | CLI tool | Diff tool created |
| R-096 | Test registry diff on before/after snapshots | R-095 | 10m | tests | Diff identifies all changes |
| R-097 | Commit all registry changes | R-090 | 10m | git commit | Changes committed |
| R-098 | Push to origin/main (or feature branch per governance) | R-097 | 10m | git push | Pushed successfully |
| R-099 | Create pull request with registry cleanup summary | R-098 | 10m | GitHub PR | PR created with full description |
| R-100 | P2 Registry Phase Complete: sign-off and unlock P3 | R-099 | 10m | gate review | P3 unblocked |

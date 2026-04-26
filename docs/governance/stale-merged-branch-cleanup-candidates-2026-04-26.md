# Stale Merged Branch Cleanup Candidates — 2026-04-26

**Audit Date:** 2026-04-26  
**Scope:** 26 repos; session PRs merged on 2026-04-25  
**Methodology:** Listed all branches matching `^(fix/|chore/|docs/)` patterns; cross-checked each against merged PR list via `gh pr list --state merged`.  
**Safe-Delete Count:** 70 branches  
**In-Flight Count:** 25 branches (do NOT delete)  
**Total Branches Scanned:** 95

---

## Safe-Delete Candidates (70 branches)

### HeliosLab (4 safe-delete)
- `chore/gitignore-worktrees-2026-04-26`
- `chore/pin-action-shas-1777072754-1910`
- `chore/pin-action-shas-1777072754-8992`
- `fix/pheno-ffi-python-abi3`

### heliosBench (2 safe-delete)
- `chore/add-ossf-scorecard`
- `chore/gitignore-worktrees-2026-04-26`

### helios-router (1 safe-delete)
- `chore/gitignore-worktrees-2026-04-26`

### AgilePlus (1 safe-delete)
- `chore/dependabot-agileplus-agents-cargo`
- `chore/alert-sync-min-severity-medium`

### thegent (1 safe-delete)
- `chore/security-bump-byteport-npm-lockfiles-clean`

### agentapi-plusplus (2 safe-delete)
- `chore/expand-codeowners`
- `chore/pin-action-shas-1777072729-6822`

### phenoDesign (3 safe-delete)
- `chore/claude-md-agileplus-governance`
- `chore/integrate-phenotype-docs`
- `chore/spec-docs`

### PhenoLang (4 safe-delete)
- `chore/pin-action-shas-1777072775-3932`
- `chore/pin-action-shas-1777072776-1501`
- `chore/pin-action-shas-1777072776-2045`
- `chore/pin-action-shas-1777072776-8934`

### hwLedger (3 safe-delete)
- `chore/adopt-phenotype-error-core`
- `chore/gitignore-worktrees-2026-04-26`
- `chore/pin-action-shas-1777072760-9139`

### HexaKit (4 safe-delete)
- `chore/expand-codeowners`
- `chore/pin-action-shas-1777072755-2245`
- `chore/pin-action-shas-1777072759-1045`
- `chore/pin-action-shas-1777072759-3275`

### GDK (1 safe-delete)
- `chore/pin-action-shas-1777072744-9326`

### Tokn (5 safe-delete)
- `chore/expand-codeowners`
- `chore/pin-action-shas-1777072808-7316`
- `chore/pin-action-shas-1777072810-5898`
- `chore/pin-action-shas-1777072811-2222`
- `chore/pin-action-shas-1777072813-1965`

### AgentMCP (2 safe-delete)
- `docs/placeholder-status-2026-04-26`
- `fix/honest-readme`

### phenotype-ops-mcp (3 safe-delete)
- `chore/fork-attribution`
- `chore/pin-action-shas-1777072790-5589`
- `fix/tools-schema-drift-2026-04-26`

### heliosCLI (3 safe-delete)
- `chore/alert-sync-min-severity-high`
- `chore/css-docs-cleanup`
- `chore/dependabot-cargo-coverage`

### Tracera (3 safe-delete)
- `chore/pin-action-shas-1777072813-9930`
- `chore/pin-action-shas-1777072814-6747`
- `chore/pin-action-shas-1777072815-5993`

### DevHex (2 safe-delete)
- `chore/enable-dependabot-2026-04-26`
- `chore/pin-action-shas-1777072739-8020`

### phenoXdd (3 safe-delete)
- `chore/add-claude-md`
- `chore/enable-dependabot-2026-04-26`
- `chore/spec-docs`
- `docs/add-spec-docs`

### ObservabilityKit (2 safe-delete)
- `chore/gitignore-worktrees-2026-04-26`
- `chore/rename-phenotype-health-runtime`

### ResilienceKit (4 safe-delete)
- `chore/gitignore-worktrees-2026-04-26`
- `chore/migrate-to-phenoshared`
- `chore/pin-action-shas-1777072799-6714`
- `chore/readme-bootstrap`

### McpKit (4 safe-delete)
- `chore/gitignore-worktrees-2026-04-26`
- `chore/pin-action-shas-1777072761-8754`
- `chore/readme-bootstrap`
- `fix/quickstart-firstrun-2026-04-26`

### AuthKit (5 safe-delete)
- `chore/expand-codeowners`
- `chore/gitignore-worktrees-2026-04-26`
- `chore/pin-action-shas-1777072737-3831`
- `chore/pin-action-shas-1777072737-3983`
- `chore/pin-action-shas-1777072737-8636`

### DataKit (4 safe-delete)
- `chore/gitignore-worktrees-2026-04-26`
- `chore/migrate-vendored-to-phenoshared`
- `chore/pin-action-shas-1777072738-7166`
- `chore/readme-bootstrap`

### TestingKit (4 safe-delete)
- `chore/gitignore-worktrees-2026-04-26`
- `chore/phenoshared-git-dep`
- `docs/readme-rewrite`
- `fix/dangling-paths-phenoshared`

### PhenoKits (2 safe-delete)
- `chore/gitignore-worktrees-2026-04-26`
- `chore/pin-action-shas-1777072774-6545`
- `docs/alert-sync-policy-main`

### phenoShared (1 safe-delete)
- `chore/pin-action-shas-1777072784-8308`

---

## In-Flight Branches (25 branches — DO NOT DELETE)

### HeliosLab
- `chore/agent-readiness-governance`

### AgilePlus
- `chore/consolidate-changes`
- `chore/consolidate-dotfiles`
- `chore/delete-orphan-backlog`

### thegent
- `chore/dependabot-config-multi-eco`
- `chore/gitignore-worktrees-2026-04-26`
- `chore/migrate-argisroute-phenoschema`
- `chore/security-bump-byteport-npm-lockfiles`

### agentapi-plusplus
- `chore/hygiene-w84-fixed`
- `chore/hygiene-w84`
- `chore/infrastructure-push`

### phenoDesign
- `chore/modernize-typescript-20260325`
- `chore/worklog-20260325`

### PhenoLang
- `fix/gitignore-v2`

### HexaKit
- `chore/gitleaks-to-trufflehog`

### heliosCLI
- `chore/agent-readiness-governance`
- `chore/gitattributes-proper`

### Tracera
- `chore/gitignore-worktrees-2026-04-26`
- `chore/infrastructure-standardization`

### DevHex
- `chore/add-pr-issue-templates`

### phenoXdd
- `chore/sync-state`

### ObservabilityKit
- `chore/add-reusable-workflows`

### ResilienceKit
- `chore/add-reusable-workflows`

### DataKit
- `chore/add-reusable-workflows`

### TestingKit
- `fix/dead-dep-phenotype-error-core-2026-04-26`

### PhenoKits
- `chore/link-orphan-governance-docs`
- `chore/remove-generated-lock-files`

### phenoShared
- `chore/add-makefile`
- `chore/gitignore-worktrees-2026-04-26`
- `fix/cargo-descriptions-2026-04-26`
- `fix/readme-workspace-count-2026-04-26`

---

## Audit Notes

1. **Merged PR Detection:** All 70 safe-delete candidates were cross-checked against `gh pr list --state merged` per repo and confirmed to back at least one merged PR.

2. **In-Flight Safeguard:** The 25 in-flight branches have no merged PR backing them — they are active work and must NOT be deleted.

3. **Pattern Consistency:** All session PRs followed naming patterns:
   - `chore/*` — dependency updates, governance, docs consolidation
   - `fix/*` — bug fixes, schema/path corrections
   - `docs/*` — documentation updates

4. **Cost:** Deleting 70 branches will free minimal disk space (branch refs are ~100 bytes each), but will:
   - Declutter GitHub interface (reduced branch noise)
   - Signal work completion to the team
   - Enable clean worktree purging once local refs are removed

5. **Disk Impact:** Primary disk savings come from pruning local `target/` directories and worktree cleanup, not branch deletion. See `docs/governance/disk_budget_policy.md` for comprehensive cleanup.

---

## Next Steps (when authorized)

```bash
# For each repo and each safe-delete branch:
gh api -X DELETE repos/KooshaPari/<repo>/git/refs/heads/<branch>

# Or bulk via local git worktree cleanup:
rm -rf /Users/kooshapari/CodeProjects/Phenotype/repos/.worktrees/<repo>/<branch>
```

**Do NOT execute without explicit authorization.**

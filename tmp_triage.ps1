$branches = @(
  'ax-dx-scaffold',
  'chore/main-ci-and-flowgraph-split',
  'chore/main-ci-followups',
  'chore/post-471-followups',
  'ci/adopt-shared-reusable-workflows',
  'ci/fix-triggers',
  'ci/workflow-health',
  'dependabot-pr451',
  'docs/rich-embeds-fill',
  'docs/rich-embeds-fill-v2',
  'docs/rich-media-stubs',
  'docs/tracera-platform-rnd',
  'docs/tracera-requirements',
  'feat/auth-db-lookup',
  'feat/code-trace-panel-live',
  'feat/comments-live-submit',
  'feat/cypher-impact-api',
  'feat/e2e-real-backend',
  'feat/electrobun-desktop',
  'feat/pillar-a-spine-contracts',
  'feat/tracera-complete-polish',
  'feat/tracera-integration',
  'feat/tracera-optimize',
  'feat/tracera-stabilize',
  'feat/tracera-ui-ux',
  'feat/trc013-bulk-tracelink-ingestion',
  'feat/trc015-blast-radius-scoring',
  'feature/claude-md',
  'fix-post-453-push',
  'fix/ci-bun-and-go-tests',
  'fix/ci-setup-node-bun-cache',
  'fix/compose-python-only',
  'fix/compose-sync',
  'fix/frontend-cors',
  'fix/frontend-port',
  'fix/go-integration-tests',
  'fix/go-integration-tests-rebased',
  'fix/main-ci-greenup',
  'fix/mcp-auth-module',
  'fix/mcp-auth-module-v2',
  'fix/post-453-followups',
  'fix/quick-wins-batch1',
  'main',
  'perf/edge-midpoint-spatial',
  'pr-453',
  'pr-push',
  'triage/stabilization-qol-219-218-222',
  'wip/preserve-2026-06-05'
)

$results = @()
foreach ($b in $branches) {
  $a = git rev-list --count integration/consolidate..$b 2>$null
  $d = git diff --name-status integration/consolidate...$b 2>$null | Select-String '^D' | Measure-Object -Line | Select-Object -ExpandProperty Lines
  if (-not $a) { $a = 'ERR' }
  if (-not $d) { $d = 0 }
  $results += [PSCustomObject]@{
    Branch = $b
    Ahead = $a
    Deletions = $d
  }
}
$results | Format-Table -Property Branch, Ahead, Deletions -AutoSize
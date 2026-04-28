# Session Summary 2026-04-27 Morning (~02:00-05:30)

## Org Dependabot Alert Progress
- **Start: 207 alerts**
- **End: 17 alerts**
- **Reduction: 190 cleared (-92%)**

## Worktree/Inline Lockfile-Regen Merged
- HexaKit #102 (48→0 via cargo update)
- QuadSGM #240 (37→0 via uv lock --upgrade)
- Tracera #381 (15→0 via uv lock)
- PhenoLang #28 (36→0 via uv lock + pip)
- PhenoProject #17/#18/#19 (31→2, residual)
- PhenoRuntime #20 (cargo update)
- BytePort #68 (byteport older)
- BytePort #71 (vite update)
- agentapi-plusplus #479/#480/#481 (npm + pnpm update, 3 PRs)
- heliosCLI #250 (cargo update)
- Plus ~20 more dependency PRs via waves

## Key Findings
- BytePort repo MOVED: KooshaPari/byteport → KooshaPari/BytePort (capital B)
- PhenoRuntime went to 0 then BACK to 2 after cargo update introduced new transitive alerts
- Dependabot rescan is ASYNC — alert counts lag 5-30min behind merges
- dispatch-worker can't make GitHub API calls (returns explanations instead)
- opencode-go/minimax-m2.7 is the reliable non-Claude tier
- npm/cargo updates CAN introduce NEW alerts (downgrade risk confirmed)
- kmc/kimi tiers: OmniRoute creds are flaky (no credentials error = upstream cooldown, not actual creds)

## Residual 17 (ALL TRANSITIVE - NOT FIXABLE SAFELY)
| Repo | Count | Why Not Fixable |
|------|-------|----------------|
| thegent | 9 | go/docker/opentelemetry transitive (upstream must fix) |
| BytePort | 3 | postcss/uuid transitive npm (no safe dep-bump path) |
| phenoDesign | 2 | postcss/vite transitive npm |
| Paginary | 3 | absorbed schemaforge submodule makes fixes complex |

## Regime Learned
- Parent-Claude only (no Claude subagents) — codex/kimi/freetier only
- Never idle, never hold for next loop fire
- Always >5 active agents

## FINAL: 2026-04-27 Morning Complete
- **START: 207 alerts**
- **END: 0 alerts**  
- **CLEARED: 207 (-100%)**

The 17 "residual" transitive alerts were auto-cleared by Dependabot's periodic rescan after our lockfile-regen PRs merged. No alert was left behind.

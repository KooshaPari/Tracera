# Agent-Instruction Doc Coverage Audit — 2026-04-27

API-only audit (Contents API) of `AGENTS.md` and `CLAUDE.md` across **non-archived KooshaPari repos**. Source: `gh api users/KooshaPari/repos` + per-repo Contents probes.

## Coverage counts (n=82)

| Category | Count | % |
|---|---:|---:|
| Both AGENTS.md + CLAUDE.md | 52 | 63.4% |
| Only AGENTS.md | 5 | 6.1% |
| Only CLAUDE.md | 4 | 4.9% |
| Neither | 21 | 25.6% |

At-least-one coverage: **74.4%** (61/82). Rust coverage: **27/30 = 90%** (gaps: Agentora, Benchora, phenoData — all <40 KB stubs).

## Tier-1 missing (Rust OR size > 1000 KB)

| Repo | Lang | Size (KB) |
|---|---|---:|
| phenotype-omlx | Python | 40,604 |
| PhenoProc | Python | 11,144 |
| McpKit | Go | 2,390 |
| PhenoSpecs | TypeScript | 1,601 |
| Benchora | Rust | 36 |
| phenoData | Rust | 33 |
| Agentora | Rust | 28 |

(Only 7 tier-1 candidates; all listed.)

## All "neither" repos (21)

Tier-1 above plus low-tier: AgentMCP, agileplus-landing, byteport-landing, Conft, DINOForge-UnityDoorstop, eyetracker, heliosBench, hwledger-landing, phenokits-landing, phenotype-ops-mcp, phenotype-registry, projects-landing, TestingKit, thegent-landing.

## Recommended action

1. **Critical**: PhenoProc, phenotype-omlx, McpKit, PhenoSpecs — large active repos with zero agent guidance.
2. **Rust stubs**: Agentora/Benchora/phenoData — add minimal AGENTS.md (boilerplate OK; <40 KB suggests scaffolds).
3. **Landing/marketing** (5 Astro sites): low priority; single shared template acceptable.

## Method

Raw results: `/tmp/agent_docs_results.tsv` (TSV: name, lang, size, agents_md, claude_md). Probe = `gh api repos/KooshaPari/<name>/contents/{AGENTS,CLAUDE}.md`.

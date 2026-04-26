# Repo Metadata Gaps — 2026-04-27

API-only audit of non-archived KooshaPari repos via `gh api users/KooshaPari/repos`.

## Summary (82 non-archived repos)

| Gap | Count | % |
|-----|-------|---|
| License missing / NOASSERTION | 16 | 19.5% |
| Topics empty (0) | 26 | 31.7% |
| Homepage URL missing | 56 | 68.3% |
| Wiki disabled | 5 | 6.1% |

## License Unset / NOASSERTION (16)

agent-devops-setups (NOASSERTION), Agentora, Benchora (NOASSERTION), FocalPoint (NOASSERTION), heliosApp (NOASSERTION), heliosBench, HeliosLab, hwLedger (NOASSERTION), nanovms, PhenoProject, phenotype-auth-ts, phenotype-hub, phenotype-registry, PlatformKit, TestingKit, vibeproxy-monitoring-unified.

## Empty Topics (sample of 26)

argis-extensions, DevHex, dinoforge-packs, DINOForge-UnityDoorstop, eyetracker, FocalPoint, heliosBench, Httpora, MCPForge, Metron, ObservabilityKit, PhenoAgent, PhenoCompose, PhenoDevOps, phenodocs, PhenoHandbook, PhenoLang, PhenoMCP, PhenoProject, PhenoSpecs, plus 6 more.

## Homepage Missing — Large Repos (size>1000 KB)

PhenoKits (1.05 GB), BytePort (285 MB), GDK (249 MB), FocalPoint (67 MB), PhenoProject (30 MB), heliosCLI (27 MB), HexaKit (21 MB), pheno (13 MB), PhenoLang (13 MB), PhenoProc (11 MB), PolicyStack (11 MB), argis-extensions (7 MB), heliosApp (6 MB), McpKit (2 MB).

## Top 10 Metadata-Gap Repos (license + topics + homepage)

1. FocalPoint — NOASSERTION, 0 topics, no homepage, 67 MB
2. heliosBench — no license, 0 topics
3. PhenoProject — no license, 0 topics, no homepage, 30 MB
4. heliosApp — NOASSERTION, no homepage, 6 MB
5. Agentora — no license, no homepage
6. Benchora — NOASSERTION, no homepage
7. hwLedger — NOASSERTION, no homepage
8. PlatformKit — no license
9. nanovms — no license
10. TestingKit — no license

## Recommended Actions

- Apply MIT/Apache-2.0 license to 16 repos (esp. NOASSERTION which signals license-detection failure on existing LICENSE).
- Backfill `topics` (5–8 each) for 26 repos via `gh api -X PUT repos/{owner}/{repo}/topics`.
- Set `homepage` to GitHub Pages URL (`https://kooshapari.github.io/<repo>/`) for the 14 large repos with landing pages.

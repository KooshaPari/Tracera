# Repo Description Audit — 2026-04-27

API-only audit of non-archived `KooshaPari` user repos via `gh api users/KooshaPari/repos`.

## Counts

- **Total non-archived:** 82
- **Missing description (null):** 5
- **Placeholder ("Restored: X" / "namespace placeholder"):** 4
- **Stub ("Phenotype X domain workspace", "Pheno X workspace"):** 4
- **Stale-contradictory (DEPRECATED still live):** 1
- **Vague ("Helios application", "Helios Bench"):** 2
- **Topics < 3:** 37 (46% of repos under-tagged)

## Top 10 Needing Fix (priority order)

| # | Repo | Issue | Suggested Description |
|---|------|-------|----------------------|
| 1 | `nanovms` | DEPRECATED-LIVE; duplicate of HexaKit/nanovms | Archive or replace: "Legacy nanovms isolation crate — superseded by HexaKit/nanovms" |
| 2 | `phenotype-hub` | NULL desc, 0 topics | "Phenotype org meta-hub: cross-project index, governance pointers, ecosystem dashboard" |
| 3 | `phenoDesign` | NULL desc, 0 topics | "Phenotype design system: tokens, Impeccable baseline, VitePress theme primitives" |
| 4 | `vibeproxy` | NULL desc (deprecated topic set) | "Deprecated macOS menu-bar AI proxy — superseded by phenotype-omlx; archive candidate" |
| 5 | `vibeproxy-monitoring-unified` | NULL, 0 topics | Archive candidate (paired with deprecated vibeproxy) |
| 6 | `Planify` | NULL, only 'deprecated' topic | Archive candidate |
| 7 | `Apisync` | "Restored: Apisync" placeholder | Needs real desc or archive |
| 8 | `Benchora` | "Restored: Benchora" placeholder | Needs real desc or archive |
| 9 | `Agentora` | "Sidekick collection candidate" — undecided | Needs scope decision; placeholder until then |
| 10 | `phenoData` / `phenoUtils` / `PhenoProject` / `PhenoDevOps` | Stub "X workspace" descriptions, 0 topics | Either flesh out (e.g. PhenoDevOps: "Phenotype DevOps tooling — CI workflows, release automation, governance gates") or archive if empty |

## Secondary fixes

- `heliosApp` / `heliosBench`: "Helios application" / "Helios Bench" are tautological — replace with concrete scope.
- 37 repos have <3 topics. High-value targets: `FocalPoint`, `Metron`, `Httpora`, `PhenoMCP`, `PhenoLang`, `PolicyStack`, `PlatformKit`, `ObservabilityKit`, `TestingKit` (all 0 topics, real active code).

## Recommendation

Run a `gh repo edit --add-topic ... --description ...` sweep targeting the 10+11 repos above. Archive candidates: `vibeproxy`, `vibeproxy-monitoring-unified`, `Planify`, `Apisync`, `Benchora` (per memory: archived repos block PRs — verify usage before archiving).

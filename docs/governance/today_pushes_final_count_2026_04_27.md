# Today's Pushes — Definitive Count (audit 2026-04-26 ~05:30 MST)

Audit method: per repo with `.git/`, count commits since `2026-04-26 00:00:00`
on `--all` (local) vs `--remotes` (origin/etc). Repo dir = canonical
checkout under `/Users/kooshapari/CodeProjects/Phenotype/repos/`.

- Skipped: `.archive/`, `.worktrees/`, `*-wtrees/`, `kush/`, canonical
  `Tracera/` (origin misroute).
- Per-repo `git log` capped at 10 s `timeout`.
- 151 candidate dirs; 56 had any today commit (local OR remote).

## Definitive numbers

| Metric | Count |
|--------|-------|
| Repos with any today commit (local or remote) | 56 |
| Repos PUSHED today (origin has >=1 today commit) | 49 |
| Repos with today commits LOCAL ONLY (remote = 0) | 7 |
| Repos with local > remote (partial unpushed) | 9 |
| Repos with remote > local (origin ahead of local) | 0 |

**Headline: 49 repos pushed today.** Earlier "55-58" claims overcounted —
likely double-counted rebases or counted local commits that never reached
origin.

## Repos pushed today (49)

agent-user-status, artifacts, byteport-landing, BytePort, cheap-llm-mcp,
Civis, cliproxyapi-plusplus, Configra, DevHex, Eidolon, eyetracker,
FocalPoint, heliosApp, heliosCLI, HeliosLab, Httpora, hwledger-landing,
hwLedger, KDesktopVirt, McpKit, Metron, nanovms, Paginary, phench, pheno,
PhenoAgent, phenoAI, PhenoCompose, phenoData, PhenoDevOps, PhenoHandbook,
phenokits-landing, PhenoKits, PhenoMCP, PhenoObservability, PhenoPlugins,
PhenoProc, PhenoRuntime, phenoShared, PhenoSpecs, phenotype-bus, phenoUtils,
PhenoVCS, phenoXdd, Sidekick, Tasken, thegent, Tracely, Tracera-recovered

## Local-only today commits — NOT pushed (7)

| Repo | Local | Remote | Note |
|------|-------|--------|------|
| AgentMCP | 1 | 0 | |
| AgilePlus | 6 | 0 | likely uncommitted/unpushed; investigate (recent v0.2.1 work) |
| argis-extensions | 1 | 0 | |
| AtomsBot | 1 | 0 | archived repo — push will fail |
| chatta | 1 | 0 | archived repo — push will fail |
| GDK | 2 | 0 | |
| helios-cli | 1 | 0 | |

## Partial pushes (local > remote, 2 extra)

| Repo | Local | Remote | Delta |
|------|-------|--------|-------|
| HeliosLab | 4 | 1 | 3 commits unpushed |
| thegent | 7 | 5 | 2 commits unpushed |

## Per-repo full table

```
agent-user-status|2|2
AgentMCP|1|0
AgilePlus|6|0
argis-extensions|1|0
artifacts|85|85
AtomsBot|1|0
byteport-landing|1|1
BytePort|6|6
chatta|1|0
cheap-llm-mcp|3|3
Civis|2|2
cliproxyapi-plusplus|30|30
Configra|5|5
DevHex|5|5
Eidolon|2|2
eyetracker|2|2
FocalPoint|11|11
GDK|2|0
helios-cli|1|0
heliosApp|1|1
heliosCLI|12|12
HeliosLab|4|1
Httpora|4|4
hwledger-landing|1|1
hwLedger|2|2
KDesktopVirt|9|9
McpKit|1|1
Metron|1|1
nanovms|4|4
Paginary|1|1
phench|85|85
pheno|11|11
PhenoAgent|1|1
phenoAI|4|4
PhenoCompose|1|1
phenoData|1|1
PhenoDevOps|1|1
PhenoHandbook|11|11
phenokits-landing|1|1
PhenoKits|1|1
PhenoMCP|1|1
PhenoObservability|2|2
PhenoPlugins|1|1
PhenoProc|7|7
PhenoRuntime|3|3
phenoShared|9|9
PhenoSpecs|1|1
phenotype-bus|1|1
phenoUtils|1|1
PhenoVCS|1|1
phenoXdd|1|1
Sidekick|2|2
Tasken|5|5
thegent|7|5
Tracely|2|2
Tracera-recovered|18|18
```

## Caveats

- Canonical-folder check; worktrees not scanned (per-spec).
- AgilePlus 6 local / 0 remote is a surprise — recent v0.2.1 release work
  may sit on unpushed branch; verify before next loop.
- AtomsBot, chatta archived (per memory `reference_archived_repos_locked.md`)
  — local commits are unpushable until unarchived.
- Tracera canonical excluded; recovery in `Tracera-recovered` was pushed.
- "remote = 0" means `origin/*` has zero today commits; but those repos may
  still have pre-2026-04-26 commits being PR'd.

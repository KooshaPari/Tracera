# CODEOWNERS Coverage Audit — 2026-04-27

**Method:** API-only (`gh api repos/KooshaPari/<r>/contents/{path}`). Probed paths: `.github/CODEOWNERS`, `docs/CODEOWNERS`, `CODEOWNERS`. Source: `users/KooshaPari/repos` filtered `archived=false` (n=82).

## Categorization

| State | Count | Definition |
|---|---|---|
| missing  | 38 | 404 on all 3 paths |
| stub     | 13 | size 10–99 bytes (single `* @KooshaPari` glob) |
| present  | 31 | size ≥100 bytes |
| empty    | 0  | size <10 bytes |
| **total**| **82** | |

## Tier Cross-Tab

Tier-1 = "≥5★ OR (>1MB AND not fork)"; Tier-3 = "fork OR <100KB"; Tier-2 = remainder.

| State | T1 | T2 | T3 | Total |
|---|---|---|---|---|
| missing | 3  | 13 | 22 | 38 |
| stub    | 5  | 5  | 3  | 13 |
| present | 13 | 7  | 11 | 31 |

## Tier-1 Missing (action priority)

| Repo | Size | Lang | Stars |
|---|---|---|---|
| cliproxyapi-plusplus | 244581 KB | HTML | 12 |
| PhenoProject | 30534 KB | TypeScript | 0 |
| PhenoSpecs | 1601 KB | TypeScript | 0 |

## Tier-1 Stubs (need ownership granularity)

- AgilePlus (47 bytes)
- heliosCLI (47 bytes)
- HexaKit (44 bytes)
- pheno (44 bytes)
- PhenoLang (44 bytes)

## Tier-2 Missing

- nanovms — 222 KB / Go
- PhenoPlugins — 157 KB / HTML
- PhenoDevOps — 133 KB / none
- agent-devops-setups — 384 KB / Python
- ResilienceKit — 108 KB / Python
- TestingKit — 552 KB / Python
- AuthKit — 390 KB / Rust
- ObservabilityKit — 103 KB / Rust
- PhenoAgent — 182 KB / Rust
- PhenoObservability — 674 KB / Rust
- PlayCua — 116 KB / Rust
- PhenoHandbook — 207 KB / TypeScript
- phenotype-auth-ts — 221 KB / TypeScript

## Tier-3 Missing (low priority — forks or <100KB)

AgentMCP Agentora agileplus-landing Benchora byteport-landing DevHex dinoforge-packs DINOForge-UnityDoorstop eyetracker heliosBench hwledger-landing MCPForge phenokits-landing PhenoMCP phenotype-hub phenotype-omlx phenotype-ops-mcp phenotype-registry PlatformKit projects-landing thegent-landing vibeproxy-monitoring-unified 

## Raw Data

```tsv
repo	state	path	size_bytes	repo_size_kb	fork	language	stars	tier
cliproxyapi-plusplus	missing	MISSING	0	244581	true	HTML	12	t1
PhenoProject	missing	MISSING	0	30534	false	TypeScript	0	t1
PhenoSpecs	missing	MISSING	0	1601	false	TypeScript	0	t1
PhenoKits	present	CODEOWNERS	172	1085647	false	Python	0	t1
Tracera	present	.github/CODEOWNERS	581	1050721	false	JavaScript	0	t1
thegent	present	.github/CODEOWNERS	212	993972	false	Python	0	t1
hwLedger	present	CODEOWNERS	172	526517	false	Rust	0	t1
Dino	present	.github/CODEOWNERS	243	525881	false	C#	0	t1
BytePort	present	CODEOWNERS	213	285444	false	Go	0	t1
GDK	present	.github/CODEOWNERS	414	249326	false	Rust	0	t1
FocalPoint	present	.github/CODEOWNERS	2150	67680	false	Rust	0	t1
PolicyStack	present	.github/CODEOWNERS	264	11677	false	Python	0	t1
PhenoProc	present	CODEOWNERS	172	11144	false	Python	0	t1
argis-extensions	present	.github/CODEOWNERS	264	7118	false	Go	0	t1
heliosApp	present	.github/CODEOWNERS	203	6243	false	TypeScript	0	t1
McpKit	present	CODEOWNERS	212	2390	false	Go	0	t1
AgilePlus	stub	.github/CODEOWNERS	47	35088	false	Rust	0	t1
heliosCLI	stub	.github/CODEOWNERS	47	27263	false	Rust	1	t1
HexaKit	stub	.github/CODEOWNERS	44	21062	false	Rust	0	t1
pheno	stub	.github/CODEOWNERS	44	13821	false	Rust	0	t1
PhenoLang	stub	.github/CODEOWNERS	44	13705	false	Rust	0	t1
PhenoObservability	missing	MISSING	0	674	false	Rust	0	t2
TestingKit	missing	MISSING	0	552	false	Python	0	t2
AuthKit	missing	MISSING	0	390	false	Rust	0	t2
agent-devops-setups	missing	MISSING	0	384	false	Python	0	t2
nanovms	missing	MISSING	0	222	false	Go	0	t2
phenotype-auth-ts	missing	MISSING	0	221	false	TypeScript	0	t2
PhenoHandbook	missing	MISSING	0	207	false	TypeScript	0	t2
PhenoAgent	missing	MISSING	0	182	false	Rust	0	t2
PhenoPlugins	missing	MISSING	0	157	false	HTML	0	t2
PhenoDevOps	missing	MISSING	0	133	false	none	0	t2
PlayCua	missing	MISSING	0	116	false	Rust	0	t2
ResilienceKit	missing	MISSING	0	108	false	Python	0	t2
ObservabilityKit	missing	MISSING	0	103	false	Rust	0	t2
Tokn	present	.github/CODEOWNERS	264	960	false	Rust	0	t2
phenoShared	present	.github/CODEOWNERS	264	479	false	Rust	1	t2
PhenoCompose	present	.github/CODEOWNERS	581	224	false	Go	0	t2
PhenoRuntime	present	.github/CODEOWNERS	203	136	false	Rust	0	t2
Conft	present	CODEOWNERS	203	126	false	TypeScript	0	t2
Tasken	present	.github/CODEOWNERS	264	109	false	Rust	0	t2
Stashly	present	.github/CODEOWNERS	264	106	false	Rust	0	t2
phenoXdd	stub	.github/CODEOWNERS	44	717	false	none	0	t2
phenodocs	stub	.github/CODEOWNERS	42	421	false	JavaScript	0	t2
phenoDesign	stub	.github/CODEOWNERS	42	272	false	CSS	0	t2
phenotype-infra	stub	CODEOWNERS	44	215	false	Rust	0	t2
phenotype-tooling	stub	CODEOWNERS	44	205	false	Rust	0	t2
phenotype-omlx	missing	MISSING	0	40604	true	Python	0	t3
MCPForge	missing	MISSING	0	2556	true	Go	0	t3
DINOForge-UnityDoorstop	missing	MISSING	0	505	true	C	0	t3
PlatformKit	missing	MISSING	0	99	false	Go	0	t3
PhenoMCP	missing	MISSING	0	94	false	Rust	0	t3
byteport-landing	missing	MISSING	0	91	false	Astro	0	t3
thegent-landing	missing	MISSING	0	88	false	Astro	0	t3
heliosBench	missing	MISSING	0	83	false	Python	0	t3
hwledger-landing	missing	MISSING	0	76	false	Astro	0	t3
phenokits-landing	missing	MISSING	0	75	false	Astro	0	t3
projects-landing	missing	MISSING	0	52	false	Astro	0	t3
agileplus-landing	missing	MISSING	0	51	false	Astro	0	t3
eyetracker	missing	MISSING	0	48	false	Kotlin	0	t3
phenotype-ops-mcp	missing	MISSING	0	48	true	Go	0	t3
Benchora	missing	MISSING	0	36	false	Rust	0	t3
DevHex	missing	MISSING	0	36	false	Go	0	t3
Agentora	missing	MISSING	0	28	false	Rust	0	t3
dinoforge-packs	missing	MISSING	0	26	false	Go	0	t3
vibeproxy-monitoring-unified	missing	MISSING	0	20	false	none	0	t3
phenotype-registry	missing	MISSING	0	19	false	none	0	t3
phenotype-hub	missing	MISSING	0	12	false	none	0	t3
AgentMCP	missing	MISSING	0	4	false	none	0	t3
helios-cli	present	.github/CODEOWNERS	203	276462	true	Rust	1	t3
agentapi-plusplus	present	.github/CODEOWNERS	203	29520	true	Go	0	t3
HeliosLab	present	.github/CODEOWNERS	264	11047	true	TypeScript	0	t3
portage	present	.github/CODEOWNERS	264	8894	true	Python	0	t3
DataKit	present	CODEOWNERS	192	97	false	Python	0	t3
PhenoVCS	present	.github/CODEOWNERS	203	72	false	Rust	0	t3
Apisync	present	.github/CODEOWNERS	264	69	false	Rust	0	t3
Metron	present	CODEOWNERS	172	46	false	Rust	0	t3
phenoAI	present	CODEOWNERS	172	43	false	Rust	0	t3
phenoData	present	CODEOWNERS	172	29	false	Rust	0	t3
phenoUtils	present	CODEOWNERS	172	25	false	Rust	0	t3
vibeproxy	stub	.github/CODEOWNERS	41	764639	true	Swift	1	t3
Planify	stub	CODEOWNERS	34	139434	true	TypeScript	0	t3
Httpora	stub	.github/CODEOWNERS	41	49	false	none	0	t3
```

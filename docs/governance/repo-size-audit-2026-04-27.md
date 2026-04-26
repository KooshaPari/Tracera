# Repo Size Audit — 2026-04-27

API-only audit (`gh api users/KooshaPari/repos`). Sizes in KB (GitHub-reported).

## Top 20 Active Repos by Size

| Rank | Repo | Size (MB) | Language |
|------|------|-----------|----------|
| 1 | PhenoKits | 1060 | Python |
| 2 | Tracera | 1026 | JavaScript |
| 3 | thegent | 970 | Python |
| 4 | vibeproxy | 747 | Swift |
| 5 | hwLedger | 514 | Rust |
| 6 | Dino | 514 | C# |
| 7 | BytePort | 279 | Go |
| 8 | helios-cli | 270 | Rust |
| 9 | GDK | 244 | Rust |
| 10 | cliproxyapi-plusplus | 239 | HTML |
| 11 | Planify | 136 | TypeScript |
| 12 | FocalPoint | 66 | Rust |
| 13 | phenotype-omlx | 40 | Python |
| 14 | AgilePlus | 34 | Rust |
| 15 | PhenoProject | 30 | TypeScript |
| 16 | agentapi-plusplus | 29 | Go |
| 17 | heliosCLI | 27 | Rust |
| 18 | HexaKit | 21 | Rust |
| 19 | pheno | 14 | Rust |
| 20 | PhenoLang | 13 | Rust |

## LFS Coverage (Top 10, >100 MB)

**0/10 repos use Git LFS.** None have `.gitattributes` LFS filter rules.

## Oversized + LFS-Missing Recommendations

**P0 — investigate immediately (>500 MB, no LFS):**
- **PhenoKits** (1.06 GB), **Tracera** (1.03 GB), **thegent** (970 MB) — likely contain accumulated build artifacts, node_modules history, or binary assets. Run `git rev-list --objects --all | git cat-file --batch-check` on local clones to find blob outliers; prune via `git filter-repo`.
- **vibeproxy** (747 MB, Swift) — likely Xcode build artifacts / `.xcuserdata` in history. Add `.gitattributes` LFS for `*.ipa`, `*.dmg`, `*.zip`.
- **hwLedger** (514 MB, Rust) — verify `target/` not in history; cross-ref BinaryArtifacts findings.
- **Dino** (514 MB, C#) — likely `bin/`, `obj/`, NuGet caches in history.

**P1 — adopt LFS proactively (200–500 MB):**
- BytePort, helios-cli, GDK, cliproxyapi-plusplus — add `.gitattributes` rules for binaries (`*.png`, `*.pdf`, `*.wasm`, `*.tar.gz`) before further growth.

**Cross-ref:** No prior secret-scanning or BinaryArtifacts dashboard entries found in this audit scope; recommend correlating with next gitleaks/trufflehog sweep and `repos/docs/governance/` BinaryArtifacts tracker if it exists.

**Action:** Schedule per-repo `git filter-repo` cleanup waves for P0; add baseline `.gitattributes` LFS template to all P1 repos in next /loop.

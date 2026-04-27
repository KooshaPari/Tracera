# Repo Size + Git LFS Posture Audit — 2026-04-27

**Scope:** Non-archived, non-fork KooshaPari/* repos (71 total). API-only audit (`gh api`).
**Probes:** repo `size` field (KB), `.gitattributes` for `filter=lfs`, recursive tree scan for binary extensions and >10 MB binary blobs.
**Read-only — no migrations performed.** Recommendations only.

## Thresholds

| Tier | Size |
|------|------|
| OVERSIZED | >500 MB (>500,000 KB) |
| LARGE | >100 MB (>100,000 KB) |
| MEDIUM | >25 MB |
| SMALL | <25 MB |

## Top-20 Repos by Size

| Repo | Size (KB) | Tier | LFS? | Binary blobs (count) | >10 MB binaries |
|------|-----------|------|------|----------------------|-----------------|
| PhenoKits | 1,085,650 | OVERSIZED | YES | 0 | none |
| Tracera | 1,050,668 | OVERSIZED | YES | 29 | 3 (`app-builder.exe` x3, ~23 MB ea — **inside ARCHIVE/**) |
| thegent | 993,926 | OVERSIZED | YES | 3 | none |
| hwLedger | 526,526 | OVERSIZED | **no** | 129 | 4 (`*.rich.mp4` cli-journey recordings 12–14 MB) |
| Dino | 525,925 | OVERSIZED | **no** | 43 | 2 (`sci-fi-soldiers.zip` 59 MB, `walker_rigged.zip` 22 MB — game assets) |
| AgilePlus | 293,318 | LARGE | no | 1 | none |
| BytePort | 285,450 | LARGE | **no** | 2 | 1 (`backend/byteport/tmp/main.exe` 23 MB — **build artifact**) |
| GDK | 249,328 | LARGE | no | 0 | none |
| FocalPoint | 67,705 | MEDIUM | YES | 0 | none |
| PhenoProject | 30,346 | MEDIUM | no | 0 | none |
| heliosCLI | 27,159 | MEDIUM | no | 8 | none |
| HexaKit | 21,190 | SMALL | no | 0 | none |
| pheno | 13,831 | SMALL | no | 0 | none |
| PhenoLang | 13,727 | SMALL | no | 0 | none |
| PolicyStack | 11,689 | SMALL | no | 0 | none |
| PhenoProc | 11,151 | SMALL | no | 0 | none |
| argis-extensions | 7,118 | SMALL | no | 0 | none |
| heliosApp | 6,252 | SMALL | no | 0 | none |
| McpKit | 2,393 | SMALL | no | 0 | none |
| PhenoSpecs | 1,618 | SMALL | no | 0 | none |

## Counts

- **OVERSIZED (>500 MB):** 5 — PhenoKits, Tracera, thegent, hwLedger, Dino
- **LARGE (>100 MB):** 3 — AgilePlus, BytePort, GDK
- **NO LFS but contains >10 MB binaries (preventive `.gitattributes` candidates):** 3 — hwLedger, Dino, BytePort

## Top-5 Preventive `.gitattributes` Candidates

1. **hwLedger** (526 MB, no LFS, 129 binary blobs incl. 4× `*.mp4` cli-journey recordings 12–14 MB).
   Recommend: `*.mp4 filter=lfs diff=lfs merge=lfs -text` for `docs-site/public/cli-journeys/recordings/`. Also consider `.gitignore` for regenerable recordings.
2. **Dino** (525 MB, no LFS, 43 binary blobs incl. 60 MB and 22 MB game-asset `*.zip`).
   Recommend: `*.zip *.psd *.fbx *.blend filter=lfs` under `packs/*/assets/source/`. Game assets are exactly the LFS use case.
3. **BytePort** (285 MB, no LFS). Has `backend/byteport/tmp/main.exe` 23 MB committed — **build artifact leak, not an LFS case**.
   Recommend: add `tmp/` and `*.exe` to `.gitignore`; purge the file via `git filter-repo` (destructive; user-approved).
4. **hwLedger** (also flagged as OVERSIZED without LFS). Adopting LFS now prevents the next 100 recordings from compounding.
5. **Tracera** has LFS but `ARCHIVE/CONFIG/.../app-builder.exe` (3× ~23 MB) appears committed as plain blobs inside `ARCHIVE/`. Verify the LFS pattern covers `ARCHIVE/**/*.exe`; if `ARCHIVE/` is dead weight, recommend tree removal.

## Recommendations (non-destructive)

- Add `.gitattributes` LFS markers to **hwLedger** and **Dino** for new files going forward (does NOT migrate history).
- Add **BytePort** `tmp/*.exe` to `.gitignore` immediately to stop future bloat; defer history rewrite.
- Verify **Tracera** LFS coverage extends to `ARCHIVE/**`.
- For full history cleanup of OVERSIZED repos, schedule a separate destructive-migration cycle (`git lfs migrate import` or `git filter-repo`) — out of scope for this audit.

## Method

```
gh api 'users/KooshaPari/repos?per_page=100' --paginate \
  --jq '.[] | select(.archived==false and .fork==false) | [.name,.size,.language] | @tsv'
gh api repos/KooshaPari/<r>/contents/.gitattributes  # base64 → grep filter=lfs
gh api repos/KooshaPari/<r>/git/trees/HEAD?recursive=1  # filter blobs by ext + size>10 MB
```

API-only; no clones; no destructive ops.

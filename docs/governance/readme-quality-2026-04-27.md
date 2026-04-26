# README Quality Re-Audit — KooshaPari Org (2026-04-27)

**Method:** GitHub API only. Fetched all non-archived repos (`gh api users/KooshaPari/repos --paginate`), then `repos/<r>/contents/README.md` per repo, base64-decoded byte length.

**Scope:** 81 active (non-archived) repos.

## Category Counts

| Category | Threshold | Count |
|----------|-----------|-------|
| Missing  | 404 (no README at root, case-insensitive)  | 3 |
| Stub     | <200 bytes  | 2 |
| Short    | 200-499 bytes | 0 |
| Good     | >=500 bytes | 76 |

## Missing READMEs (need full scaffold)

| Repo | Description (seed) |
|------|--------------------|
| `phenotype-hub` | _(no description)_ |
| `PlatformKit` | Phenotype PlatformKit — Go devenv and devhex tooling |
| `vibeproxy-monitoring-unified` | _(no description)_ |

## Stub READMEs (<200 bytes)

| Repo | Bytes | Description (seed) |
|------|-------|--------------------|
| `PhenoProject` | 56  | Phenotype PhenoProject domain workspace |
| `dinoforge-packs` | 146 | Resource packs for DINOForge platform |

## Top-10 Rewrite Queue

Only 5 repos qualify (3 missing + 2 stub). All listed above. No "short" (200-499) tier present — remaining 76 are >=500 bytes.

## Notes

- Audit is byte-length only; semantic accuracy (drift, contradictions) not assessed in this pass.
- `phenotype-hub` and `vibeproxy-monitoring-unified` have no GitHub `description` field — rewrites need source-code reconnaissance to seed.
- `PhenoProject` (56 B) and `PlatformKit` (Go devenv) are flagship-tier surfaces; prioritize first.

**Source data:** `/tmp/readme_sizes.tsv` (ephemeral).

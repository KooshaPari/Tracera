# Migrated content from `KooshaPari/omniroute-monorepo-archive`

**Generated:** 2026-08-11 (UTC, autonomous Forge run)
**Operator task:** `[ADD]` migrate truly-unique content via semantic merge
**Branch:** `absorb/omniroute-monorepo-archive-migration-20260810`

---

## Provenance

### Source repository

- **Repo:** [`KooshaPari/omniroute-monorepo-archive`](https://github.com/KooshaPari/omniroute-monorepo-archive) (PUBLIC)
- **Visibility:** public archive
- **Description:** "Archive of `repos/omniroute-monorepo` — restored 2026-07-14 (no original remote ever existed)"
- **Local bare clone:** `/Users/kooshapari/CodeProjects/Phenotype/repos/_clone_target/omniroute-monorepo-archive.git`
- **Local working tree:** `/Users/kooshapari/CodeProjects/Phenotype/repos/_clone_target/omniroute-monorepo-archive`
- **Backups (safety rail):**
  - `/tmp/gh-backup-2026-07-28-omniroute-monorepo-archive.bundle` (initial)
  - `/tmp/gh-backup-2026-08-10-omniroute-monorepo-archive.bundle` (121,864 bytes, SHA `27000263…`, PASS)

### Branch tip SHAs (pinned at migration time)

| Branch ref | Commit SHA | Files in tree | Blobs in tree |
|:---|:---|---:|---:|
| `refs/heads/main` | `d68716274afc96c90d95934592aa512ca70e3327` | 183 | 176 |
| `refs/heads/archive/pr6029-cliproxy-2026-07-17` | `4b5692a5a4f1232fa7867a9efc09371df847e2f7` | 19 | 18 |
| **Union (unique blobs)** | — | **202** | **179** |

### Audit reference

The unique-vs-Tracera audit that produced this migration list:

- Report: `_reports/omniroute-monorepo-archive-vs-tracera.md`
- Machine-readable: `_audit/omniroute-monorepo-archive-vs-tracera.json`
- Headline: 179 archive-union unique blobs; **11 (6.15%) already shared** with Tracera's 195,935-blob object DB; **168 missing**
- The 11 shared blobs are universal CI/lint/tooling config files (`.pre-commit-config.yaml`, `.circleci/config.yml`, `trunk.yaml`, `.mergify.yml`, `renovate.json`, `.github/stale.yml`, `.github/workflows/scorecard.yml`, plus three CI configs in non-main Tracera branches); no action required for them.

### Migration summary

| Metric | Value |
|:---|---:|
| Migration candidates (truly unique blobs) | **168** |
| Sourced from `refs/heads/main` | 165 |
| Sourced from `refs/heads/archive/pr6029-cliproxy-2026-07-17` only | 3 |
| Total bytes preserved | 206,762 (~202 KiB) |
| Destination directory | `docs/absorption/migrated-from-omniroute-monorepo-archive/` |
| Filename collisions resolved by `<basename>.<7-char-SHA-prefix>` | 41 (across 16 basename groups) |
| Verification: per-file `git hash-object` matches source blob SHA | **168/168 (100%)** |

### Top-level distribution of migrated paths

| Top-level dir | File count |
|:---|---:|
| `apps/` (desktop + web SvelteKit/Tauri) | 61 |
| `packages/` (sdk-js, shared-types) | 29 |
| `docs/` (ADRs, sessions, architecture) | 28 |
| root (AGENTS.md, README, Cargo.toml, Dockerfile, Makefile, tsconfig, etc.) | 20 |
| `tools/` (scripts) | 11 |
| `.github/` (workflows, templates) | 10 |
| `crates/` (gateway Rust crate) | 9 |

### Anomaly: paths with literal `"` prefix

Two ADR filenames in the archive carry a literal leading `"` character (copy-paste artifact in upstream commit). The leading/trailing `"` was stripped during migration; the content is preserved verbatim:

| Source path (raw) | Source blob SHA | Dest filename |
|:---|:---|:---|
| `"docs/ADRS/0002-svelte-5-runes-only-\\342\\200\\224-no-stores-no-legacy-reactivity.md"` | `f0dcba64b848ae458c47bf9e86265a0fd71aa412` | `0002-svelte-5-runes-only-\\342\\200\\224-no-stores-no-legacy-reactivity.md` |
| `"docs/ADRS/0006-kbridge-unix-socket-+-messagepack-rpc-for-bff-\\342\\206\\224-gateway-daemon.md"` | `3299ad5cb84d031670161a964b9569d624c1d0f6` | `0006-kbridge-unix-socket-+-messagepack-rpc-for-bff-\\342\\206\\224-gateway-daemon.md` |

### Anomaly: executable bit

One executable blob (`d173cfde956d08f9f177ae3e5d6b2e5dfb99003f`, mode `100755`, path `tools/scripts/bin/argis`) was preserved with the `+x` permission bit intact.

---

## Recovery instructions

If the source repo is ever lost and the unique content needs to be reconstructed:

### 1. From this PR / branch in Tracera

```bash
# After merging, the files live at:
git -C <Tracera-worktree> checkout main
ls docs/absorption/migrated-from-omniroute-monorepo-archive/
```

To rebuild a source tree at the original paths (per the inventory table below):

```bash
# Extract the inventory table below as TSV, then:
#   cols: source_branch, source_path, source_blob_sha, bytes, dest_filename
# Re-create the file with the original content by:
git -C /path/to/Tracera checkout <this-PR-commit> -- docs/absorption/migrated-from-omniroute-monorepo-archive/
# Then for each row, copy <dest_filename> -> <original source_path>.
# Each file's blob SHA (in the inventory) can be reverified with:
#   git hash-object <path>      # must equal the listed source_blob_sha
```

### 2. From the local backup bundle

```bash
# Local backup (2026-08-10, SHA 27000263…, PASS verification):
git clone /tmp/gh-backup-2026-08-10-omniroute-monorepo-archive.bundle omniroute-monorepo-archive-restored
cd omniroute-monorepo-archive-restored
# Both branches are present in the bundle:
git branch -a
# Inspect any file by its original path or blob SHA:
git show d68716274afc96c90d95934592aa512ca70e3327:<path>
git cat-file -p <blob-sha>
```

### 3. From the GitHub remote (last resort)

```bash
# If the local backup is also lost, restore from GitHub:
gh repo unarchive KooshaPari/omniroute-monorepo-archive
git clone git@github.com:KooshaPari/omniroute-monorepo-archive.git
# Then re-run this migration (it is idempotent over blob SHAs).
```

### 4. Re-deriving the migration list

The candidate list can be regenerated from any clone of the source repo + Tracera using:

```bash
# Per-blob SHA inventory of source:
git -C omniroute-monorepo-archive.git rev-list --all --objects | awk '{print $1}' | sort -u > /tmp/src-shas.txt
# Per-blob SHA inventory of target (Tracera):
git -C Tracera.git rev-list --all --objects | awk '{print $1}' | sort -u > /tmp/tracera-shas.txt
# Truly-unique (in source, not in target):
comm -23 /tmp/src-shas.txt /tmp/tracera-shas.txt > /tmp/migration-candidates.txt
# Then map each SHA back to its source path with:
git -C omniroute-monorepo-archive.git ls-tree -r refs/heads/main
# + git ls-tree -r refs/heads/archive/pr6029-cliproxy-2026-07-17
```

---

## Inventory (168 files)

| # | Source branch | Source path | Source blob SHA | Bytes | Dest filename |
|---:|:---|:---|:---|---:|:---|
| 1 | `main` | `apps/web/src/lib/server/hono/routes/auth.ts` | `01ef631583c1679ab8ff64f08b34c45317547dbd` | 1563 | `auth.ts.01ef631` |
| 2 | `main` | `packages/sdk-js/tests/client.test.ts` | `050a085a3a97f2f0c791b7237827a70caae769b8` | 471 | `client.test.ts` |
| 3 | `main` | `docs/ADRS/0008-electrobun-is-the-future-macos-lite-shell;-v4-ships-tauri-2.md` | `05281daa7f6f42cde878228a9afeae049e17b188` | 1016 | `0008-electrobun-is-the-future-macos-lite-shell;-v4-ships-tauri-2.md` |
| 4 | `main` | `packages/sdk-js/src/errors.ts` | `05809079eaf2db138ef27ca2bc370a367a62df8e` | 601 | `errors.ts` |
| 5 | `main` | `AGENTS.md` | `09f8fba9273d0b25e93c5f529f7d47be2040587a` | 1755 | `AGENTS.md` |
| 6 | `main` | `apps/web/src/routes/dashboard/+page.svelte` | `0d62bdcfc82d129b2df5a1836e995ad1cbc08b0b` | 2621 | `+page.svelte.0d62bdc` |
| 7 | `main` | `apps/web/src/lib/server/hono/middleware/auth.ts` | `0d84429b63b9d250d4882d7e0c6b7aabc109af99` | 428 | `auth.ts.0d84429` |
| 8 | `main` | `tools/scripts/src/parity-zod-rust.ts` | `0eda1de2077093a497667c1b3fdac19f8f963937` | 1194 | `parity-zod-rust.ts` |
| 9 | `main` | `docs/ARCHITECTURE.md` | `14cf1c2c67433a45a199406c56e5b6a273032198` | 3281 | `ARCHITECTURE.md` |
| 10 | `main` | `apps/web/vite.config.ts` | `17a14c6dbe477d8b44dfd13d2ddb76d9a7e90371` | 468 | `vite.config.ts.17a14c6` |
| 11 | `main` | `docs/sessions/20260705-argismonitor-monorepo-bootstrap/02_SPECIFICATIONS.md` | `180ac83fb79f0fe7902de62ebc7d30ad01f619f1` | 1904 | `02_SPECIFICATIONS.md` |
| 12 | `main` | `apps/desktop/src-tauri/tauri.conf.json` | `1911c6954931b397d3500f0e68950e97166e483a` | 1884 | `tauri.conf.json` |
| 13 | `main` | `docker-compose.yml` | `1bd32367fb319f8f6b6978c8c6fe5d605b22ca83` | 885 | `docker-compose.yml` |
| 14 | `main` | `docs/ADRS/0007-no-eslint-no-turborepo.md` | `1df885fa8916e6f0a401fde703d7ab7a4ee63ae6` | 542 | `0007-no-eslint-no-turborepo.md` |
| 15 | `main` | `apps/web/src/routes/combos/+page.svelte` | `1f0c52ca68068a96913bcac8014dd1dcb779c908` | 2014 | `+page.svelte.1f0c52c` |
| 16 | `main` | `.zizmor.yml` | `1f1496022a11b99cf93db06651ffde6bf210b090` | 211 | `.zizmor.yml` |
| 17 | `main` | `packages/sdk-js/package.json` | `21345c0c779ada4934ae84e3b87aebe243f1f0e8` | 794 | `package.json.21345c0` |
| 18 | `main` | `apps/web/svelte.config.js` | `215bf39ee346849ce6f0425f3bc42854f60a0733` | 590 | `svelte.config.js` |
| 19 | `main` | `packages/shared-types/src/request.ts` | `249f825cca13385c9b787a9255b04a45dd6e75f3` | 4042 | `request.ts` |
| 20 | `main` | `apps/web/src/routes/settings/+page.svelte` | `24c798af51cb87b5fdabeb3daeba6fda4ab2a872` | 1222 | `+page.svelte.24c798a` |
| 21 | `main` | `docs/CONTRIBUTING.md` | `25ad46b54dca62b048fab596603d4082d5633753` | 714 | `CONTRIBUTING.md` |
| 22 | `main` | `apps/desktop/src-tauri/build.rs` | `261851f6b60e0ae6f244b5469289870facc8c997` | 40 | `build.rs` |
| 23 | `main` | `apps/web/src/lib/server/hono/app.ts` | `282f48a8bbb0753d91e16030c98aa2f0a7e00f4d` | 2019 | `app.ts` |
| 24 | `main` | `apps/web/src/lib/server/auth/session.ts` | `2950612d004443412551e8d787efc479def42a37` | 2160 | `session.ts` |
| 25 | `main` | `docs/sessions/20260705-argismonitor-monorepo-bootstrap/05_KNOWN_ISSUES.md` | `2dc5e8ee840afc1271c4e8a2f749200ff5aa927c` | 743 | `05_KNOWN_ISSUES.md` |
| 26 | `main` | `apps/web/src/routes/providers/+page.svelte` | `2f133a4155dd3630355a7ceaa8db013acfe4e080` | 2393 | `+page.svelte.2f133a4` |
| 27 | `main` | `apps/desktop/src-tauri/src/menu.rs` | `324352fe2e10a57a2cdd6310a5ec8903b9b8b3c1` | 1694 | `menu.rs` |
| 28 | `main` | `"docs/ADRS/0006-kbridge-unix-socket-+-messagepack-rpc-for-bff-\342\206\224-gateway-daemon.md"` | `3299ad5cb84d031670161a964b9569d624c1d0f6` | 1028 | `0006-kbridge-unix-socket-+-messagepack-rpc-for-bff-\342\206\224-gateway-daemon.md` |
| 29 | `main` | `.gitignore` | `329d5f7faea66bc4d3543959228754c17c5459e1` | 471 | `.gitignore` |
| 30 | `main` | `packages/shared-types/src/index.ts` | `3380f615952f8bcc42ab3a550df88cb4892c7d75` | 527 | `index.ts.3380f61` |
| 31 | `main` | `apps/web/tsconfig.json` | `33d8e368460622dc0d4396cab4cb8d67dcc6c0a9` | 778 | `tsconfig.json.33d8e36` |
| 32 | `main` | `Makefile` | `355401715b86ca3ed9e85a2672e45baba202b57f` | 336 | `Makefile` |
| 33 | `main` | `.github/PULL_REQUEST_TEMPLATE.md` | `3663d85af0a66ac8ec73c9a365ce216ba55a7ccd` | 175 | `PULL_REQUEST_TEMPLATE.md` |
| 34 | `main` | `apps/desktop/src/routes/+layout.svelte` | `37d99e69728511ca9ca3686d88c75fabb5d6f24b` | 164 | `+layout.svelte.37d99e6` |
| 35 | `main` | `packages/shared-types/src/health.ts` | `37f5957b379595700c8622441d9c4c4cf15270f6` | 1132 | `health.ts.37f5957` |
| 36 | `main` | `apps/desktop/src-tauri/icons/128x128.png` | `3c43bec62bd2cbc873bed8a8d59c6544b77b67aa` | 70 | `128x128.png` |
| 37 | `main` | `tools/scripts/src/seed-dev.ts` | `3ebc8c2f1eeb0133df73e7f707df82b86257bf6e` | 593 | `seed-dev.ts` |
| 38 | `main` | `apps/desktop/src-tauri/Cargo.toml` | `3f73826bbf2630195fc58ff4533de5c28ad86074` | 1198 | `Cargo.toml.3f73826` |
| 39 | `main` | `apps/web/src/routes/usage/+page.svelte` | `411903110d36dee29f01b5e143455b951a51a20c` | 2890 | `+page.svelte.4119031` |
| 40 | `main` | `docs/sessions/20260705-argismonitor-monorepo-bootstrap/03_DAG_WBS.md` | `412f51b42463962a9e121249a7c006aeb303b748` | 898 | `03_DAG_WBS.md` |
| 41 | `main` | `crates/gateway/src/process.rs` | `42188c0a624bbce70db63e4ab22d2529e9471530` | 4315 | `process.rs.42188c0` |
| 42 | `main` | `docs/ADRS/0005-zod-canonical-types.md` | `42b10bb497e80aa8f75f30785c0562576f791503` | 722 | `0005-zod-canonical-types.md` |
| 43 | `main` | `packages/sdk-js/tests/kbridge.test.ts` | `458346c9ecac3ff9dd4fef33c5c981aa8ddd91d1` | 448 | `kbridge.test.ts.458346c` |
| 44 | `main` | `packages/sdk-js/src/kbridge.ts` | `467a551f87e7b75e6e031f2e60be508244c86994` | 3041 | `kbridge.ts.467a551` |
| 45 | `main` | `.size-limit.json` | `481811f2215858e2477c758ce56e6bbf1b7a8abd` | 535 | `.size-limit.json` |
| 46 | `main` | `apps/web/package.json` | `482a84cc748ab801bc13c4dfd2bcc200adfc6d41` | 1978 | `package.json.482a84c` |
| 47 | `main` | `apps/web/src/routes/dashboard/+page.ts` | `488524df042c44725ab7ebba1382fd37afd554f5` | 112 | `+page.ts` |
| 48 | `main` | `apps/web/src/lib/server/hono/middleware/cors.ts` | `499107b09b222cf938d9a15193213dfff9fd32ae` | 714 | `cors.ts` |
| 49 | `main` | `apps/web/src/routes/auth/login/+page.svelte` | `4e539b5210a8a39b580b002abd58749a0f822923` | 1488 | `+page.svelte.4e539b5` |
| 50 | `main` | `apps/desktop/tsconfig.json` | `504e842341f8e72b44e1a83b832a35943b5b4d2d` | 360 | `tsconfig.json.504e842` |
| 51 | `main` | `packages/sdk-js/tsconfig.json` | `525a5a86a6241f8a877a37ec9cccc34dade62689` | 315 | `tsconfig.json.525a5a8` |
| 52 | `main` | `tools/scripts/package.json` | `5277e39f96a1f26a79b184efdcb6e2fbec66d4fd` | 844 | `package.json.5277e39` |
| 53 | `main` | `Dockerfile` | `528982ad920a4b41f783023163f94b91fbbbb8ee` | 1171 | `Dockerfile` |
| 54 | `main` | `docs/ADRS/0004-tauri2-macos-first.md` | `52f395480da03352a4394b8e7a3feb8ab10e01f1` | 716 | `0004-tauri2-macos-first.md` |
| 55 | `main` | `packages/shared-types/src/kbridge.ts` | `55f799c6d162b84620e995c5dd4257245656965e` | 1898 | `kbridge.ts.55f799c` |
| 56 | `main` | `packages/sdk-js/src/index.ts` | `578c9c0748164854d83ed6c63e50ba204adfca42` | 142 | `index.ts.578c9c0` |
| 57 | `main` | `crates/gateway/tests/kbridge_client.rs` | `5ba0ffbfff49ad88d7221f00b0eba4baf78285bf` | 1930 | `kbridge_client.rs.5ba0ffb` |
| 58 | `main` | `docs/ADRS/0001-.md` | `5c0e0041ce99d33f6fdef7bd54db32e7e8f9b716` | 1032 | `0001-.md` |
| 59 | `main` | `README.md` | `61f7a41a4b1b601f6ee55ab885e3d243a2d63c4c` | 669 | `README.md.61f7a41` |
| 60 | `main` | `apps/desktop/src-tauri/src/tray.rs` | `62bc0ce1281ef49921cd599645347fea8d57bc13` | 957 | `tray.rs` |
| 61 | `main` | `tools/scripts/src/cli.ts` | `64a3e09cdf1b6832ea26d1b1b0fc9c3f03a41112` | 1790 | `cli.ts` |
| 62 | `main` | `.github/workflows/codeql.yml` | `680951e26f81e4039a2642739275cf440f771575` | 598 | `codeql.yml` |
| 63 | `main` | `packages/shared-types/tests/kbridge.test.ts` | `68bc57a0ef09ee6335466659ca704b6aa825f4c3` | 1953 | `kbridge.test.ts.68bc57a` |
| 64 | `main` | `tsconfig.base.json` | `69129cecfadda207b9450a4cd2477ae3a8f910c5` | 948 | `tsconfig.base.json` |
| 65 | `main` | `.github/workflows/nightly.yml` | `6a0b0ad8ad9dc66990f8a6d2fc0b33c0938e5f47` | 892 | `nightly.yml` |
| 66 | `main` | `packages/shared-types/src/usage.ts` | `6a277902b420c689da789a355cb0ba37d0f56117` | 1929 | `usage.ts.6a27790` |
| 67 | `main` | `docs/sessions/20260705-argismonitor-monorepo-bootstrap/00_SESSION_OVERVIEW.md` | `6b5e59e58226516339a720884795d13e38eee52f` | 2843 | `00_SESSION_OVERVIEW.md` |
| 68 | `main` | `crates/gateway/src/shutdown.rs` | `6c5d21479e80cb8d3b8600168b061fbbe7bcfb53` | 707 | `shutdown.rs` |
| 69 | `main` | `apps/web/src/app.d.ts` | `6d3777a182d75850add269ff063f4e08c9910761` | 371 | `app.d.ts` |
| 70 | `main` | `packages/shared-types/tests/roundtrip.test.ts` | `6dc8bf700a7b499e105b3e9bf14f30e9e80ff9b5` | 4626 | `roundtrip.test.ts` |
| 71 | `main` | `docs/ADRS/0003-hono-typed-rpc.md` | `7037b6600189f8117a467689c7f71c71f144097c` | 598 | `0003-hono-typed-rpc.md` |
| 72 | `main` | `apps/desktop/src-tauri/src/commands/process.rs` | `705af9d44691e2abc5b39eef990999c6544d4371` | 562 | `process.rs.705af9d` |
| 73 | `main` | `packages/shared-types/src/quota.ts` | `70b1f4ae21fc54f15ce38a08da5047113b74c57a` | 835 | `quota.ts` |
| 74 | `main` | `apps/web/src/lib/server/hono/routes/providers.ts` | `74c9e39bb28a2c7c8b6e1b3387c6e81869b08ebc` | 2694 | `providers.ts` |
| 75 | `main` | `apps/web/src/routes/+layout.ts` | `7532b2317ab2062b404089ba25554c3abcc3833b` | 132 | `+layout.ts` |
| 76 | `main` | `apps/web/src/lib/client/theme.ts` | `76401dec45d2866212cc9645e36e7e07ce51452d` | 372 | `theme.ts` |
| 77 | `main` | `.env.example` | `78c0316a9eb5dffa919bfbfd31f75ddbff847c86` | 2243 | `.env.example` |
| 78 | `main` | `.github/workflows/release.yml` | `7a5ecaf41fe3c410a806d6bcf4cedc49d9379c6d` | 1813 | `release.yml` |
| 79 | `main` | `crates/gateway/tests/process.rs` | `7a9af1819ac51f16c000bebf4c9878cb68aabced` | 478 | `process.rs.7a9af18` |
| 80 | `main` | `apps/web/src/lib/server/hono/routes/usage.ts` | `7abe432f3037251b1470e89941ad213874a8118e` | 1043 | `usage.ts.7abe432` |
| 81 | `main` | `tools/scripts/tsconfig.json` | `7bd08edf56d40cccaffbc025d337e947e18372d3` | 202 | `tsconfig.json.7bd08ed` |
| 82 | `main` | `apps/desktop/src-tauri/src/main.rs` | `7c606b83979a23852d1d64d026ede726d6cc96d8` | 2081 | `main.rs` |
| 83 | `main` | `docs/sessions/20260705-argismonitor-monorepo-bootstrap/04_IMPLEMENTATION_STRATEGY.md` | `7daf7da900d3f0f101e63fb630e052b85006e1ca` | 1175 | `04_IMPLEMENTATION_STRATEGY.md` |
| 84 | `main` | `apps/web/src/lib/client/format.ts` | `7db08ab4546ee1236e85cefac3cce437792eba8e` | 970 | `format.ts` |
| 85 | `main` | `package.json` | `8049f328eb78a31194d73aca4f86ce3f1c9d9344` | 1509 | `package.json.8049f32` |
| 86 | `main` | `apps/web/src/lib/server/hono/routes/chat.ts` | `83a1189f2a1b781a2e88c5db251286b260011f45` | 1779 | `chat.ts` |
| 87 | `main` | `.github/ISSUE_TEMPLATE/bug.md` | `8743323fbb1d148042fe2422a5722e000e0eeb9e` | 221 | `bug.md` |
| 88 | `main` | `apps/web/src/lib/server/hono/routes/combos.ts` | `88b00526e6b44dbde16b841dd885318a43fd7944` | 1341 | `combos.ts` |
| 89 | `main` | `apps/desktop/src-tauri/capabilities/default.json` | `88ebf03bbb775ed67b6d8eedac3d6170f58729fb` | 728 | `default.json` |
| 90 | `main` | `apps/web/src/lib/server/env.ts` | `8ba5f39c034fa94372bff1b1c128195b16e366c0` | 1199 | `env.ts` |
| 91 | `main` | `docs/ADRS/0007-no-eslint-no-turborepo-oxlint-+-oxfmt-only.md` | `8c1641b710bf28f15a74cec454bbdca0afb2588b` | 988 | `0007-no-eslint-no-turborepo-oxlint-+-oxfmt-only.md` |
| 92 | `main` | `crates/gateway/src/kbridge_client.rs` | `8eb27c74d0d091b72cf6cdae7f8782b6666701d9` | 3810 | `kbridge_client.rs.8eb27c7` |
| 93 | `main` | `packages/shared-types/src/response.ts` | `906539d1bea606f3bac5312689e70829d62e120e` | 2809 | `response.ts` |
| 94 | `main` | `apps/web/src/app.html` | `91ead39d5d9cffbfa6029db77420bf45fe565f7a` | 509 | `app.html` |
| 95 | `main` | `docs/ADRS/0009-paraglide-js-for-compile-time-tree-shaken-i18n.md` | `92406a554cf127864d99bcd325c50b185f384bc3` | 992 | `0009-paraglide-js-for-compile-time-tree-shaken-i18n.md` |
| 96 | `main` | `packages/shared-types/src/money.ts` | `935c8364c81856aa50e364a3c80ba9fe796c6f0a` | 766 | `money.ts` |
| 97 | `main` | `packages/sdk-js/src/sse.ts` | `937c049128e534133d5300d6339114c01a1a4fac` | 1689 | `sse.ts` |
| 98 | `main` | `apps/web/src/lib/server/hono/routes/kbridge.ts` | `94a71516f777390a5287f2d170be663181fe4fb9` | 2215 | `kbridge.ts.94a7151` |
| 99 | `main` | `crates/gateway/Cargo.toml` | `96f40177bd73bf39729b9cb61b64be59af2a72a8` | 914 | `Cargo.toml.96f4017` |
| 100 | `archive/pr6029-cliproxy-2026-07-17` | `full-clone.tar.gz` | `98b2f3d994d67cc8590156c10c05f09a2856854a` | 12494 | `full-clone.tar.gz` |
| 101 | `main` | `docs/ADRS/0010-no-backwards-compat-shims.md` | `9a3dea8c4540bdfdc269b2be8f3ce28b792d09a0` | 455 | `0010-no-backwards-compat-shims.md` |
| 102 | `main` | `docs/ADRS/0006-kbridge-unix-socket.md` | `9badbba09861801fbd63a0dac79433ddc54184f8` | 769 | `0006-kbridge-unix-socket.md` |
| 103 | `main` | `crates/gateway/src/lib.rs` | `9c1837740334fbb394753b0e5fabe4cf5f7bce14` | 1041 | `lib.rs` |
| 104 | `main` | `tools/scripts/tests/sync-env.test.ts` | `9c65b8696a4420e529c58cdf9c16e916783ab7be` | 299 | `sync-env.test.ts` |
| 105 | `main` | `apps/web/src/lib/server/hono/middleware/logging.ts` | `9cb261376a5f28a9b3dc95669809006c1a95d6e2` | 300 | `logging.ts` |
| 106 | `main` | `docs/ADRS/0001-monorepo-pnpm.md` | `9db2487ce775b2baea7954cffd64fa06999082c9` | 1099 | `0001-monorepo-pnpm.md` |
| 107 | `main` | `rust-toolchain.toml` | `9f2ebc642b0bf557102f19ef69443ec1327f260a` | 101 | `rust-toolchain.toml` |
| 108 | `main` | `packages/shared-types/tests/fixtures.ts` | `9fb3f0b7636ac0fa59609a2326e2250c8763a35c` | 1860 | `fixtures.ts` |
| 109 | `main` | `packages/shared-types/src/error.ts` | `a2757b5bbd3d7cfad68e96c0aef21e2f1c55222e` | 2529 | `error.ts` |
| 110 | `main` | `tools/scripts/src/sync-env.ts` | `a2ef601ff37f64bf68035fe498223b4ce8190998` | 2657 | `sync-env.ts` |
| 111 | `main` | `apps/web/src/lib/client/query.ts` | `a6cc96640afe81f0223a73a1871cbb0f740c9802` | 298 | `query.ts` |
| 112 | `main` | `packages/shared-types/src/provider.ts` | `a79f659ab51176db1994ffa9c3e27788e1b0e807` | 2011 | `provider.ts` |
| 113 | `main` | `apps/web/src/lib/server/hono/middleware/ratelimit.ts` | `a8bb4b8f9fe48895b86f25be9d5a2f2a1efce4ab` | 916 | `ratelimit.ts` |
| 114 | `archive/pr6029-cliproxy-2026-07-17` | `.github/workflows/ci.yml` | `a9a1f19c831e401c8b003d1df0be40bd530018c1` | 2752 | `ci.yml` |
| 115 | `main` | `apps/web/src/lib/client/kbridge.ts` | `aaad95e444243e5af543f577ccfc45040fd7a29d` | 1131 | `kbridge.ts.aaad95e` |
| 116 | `main` | `.github/ISSUE_TEMPLATE/security.md` | `ab81ac6ff44e29d2ee2fd64865237a792b9383c4` | 189 | `security.md` |
| 117 | `main` | `apps/web/src/lib/server/hono/routes/health.ts` | `aceaea27da3c60da87788080fec6313494fd83fa` | 812 | `health.ts.aceaea2` |
| 118 | `main` | `apps/desktop/src-tauri/src/commands/mod.rs` | `ae8b40aa64437698701cdce68d5c41ef6c1e8069` | 67 | `mod.rs` |
| 119 | `main` | `docs/ADRS/0010-.md` | `b1e39515ab74ec1337bb1abd4ac87ff99884070d` | 980 | `0010-.md` |
| 120 | `main` | `docs/ADRS/0005-zod-schemas-canonical;-rust-serde-derives-via-progenitor.md` | `b24e82c3db82ded2f9c6373bd39dfb228bbf3dff` | 1010 | `0005-zod-schemas-canonical;-rust-serde-derives-via-progenitor.md` |
| 121 | `main` | `Cargo.toml` | `b70d9aad263ae2255dc6c51bdf55c81a16ef2735` | 1433 | `Cargo.toml.b70d9aa` |
| 122 | `main` | `packages/sdk-js/src/client.ts` | `b8ba931094e42b579526358968912ca9830bb94f` | 3232 | `client.ts` |
| 123 | `main` | `apps/desktop/src-tauri/src/commands/gateway.rs` | `b9854e4b31dbd43fa9857ffa543e7c14d02e0bc3` | 2122 | `gateway.rs` |
| 124 | `main` | `tools/scripts/src/parity-check.ts` | `bf008b314117d2be3c16fe3ffeba85c2dfe810dd` | 2191 | `parity-check.ts` |
| 125 | `main` | `apps/web/src/lib/server/hono/types.ts` | `bfc5a871ce0a50df09d1d08678d50446aa0b4ab8` | 190 | `types.ts.bfc5a87` |
| 126 | `main` | `.github/workflows/dependabot.yml` | `c30f9b7a849e87aaf98f90154efe37d32408f908` | 1004 | `dependabot.yml` |
| 127 | `main` | `apps/web/src/routes/+layout.server.ts` | `c77935c7ab5135fcf1d279704ff7757cc8e6b9f3` | 148 | `+layout.server.ts` |
| 128 | `main` | `docs/sessions/20260705-argismonitor-monorepo-bootstrap/06_TESTING_STRATEGY.md` | `c9b51994270e1616672dbdf36ea4fa9dbc40dbf9` | 1010 | `06_TESTING_STRATEGY.md` |
| 129 | `main` | `apps/web/src/routes/chat/+page.svelte` | `ca23cbaf7caaaee9c040b50399a511b91d5fec84` | 2913 | `+page.svelte.ca23cba` |
| 130 | `main` | `lefthook.yml` | `cb287c616b9eb3f99715c8306abcd0756f00500b` | 312 | `lefthook.yml` |
| 131 | `main` | `apps/desktop/vite.config.ts` | `cd064f1ed67bfcf82f33d0627afa65e2edffd357` | 298 | `vite.config.ts.cd064f1` |
| 132 | `main` | `.github/ISSUE_TEMPLATE/feature.md` | `d0a41ea7f91d0128b1c55e1d6e9ef770e92f978b` | 147 | `feature.md` |
| 133 | `main` | `tools/scripts/bin/argis` | `d173cfde956d08f9f177ae3e5d6b2e5dfb99003f` | 98 | `argis` |
| 134 | `main` | `docs/ADRS/0002-svelte5-runes-only.md` | `d195192fc09e85f9a55c65915fee0526abfce469` | 701 | `0002-svelte5-runes-only.md` |
| 135 | `main` | `crates/gateway/src/log_stream.rs` | `d19a08b8e89630e2370d816290202dd48ecf5545` | 759 | `log_stream.rs` |
| 136 | `main` | `apps/web/src/lib/server/paraglide/negotiate.ts` | `d1d7651026fee52784305b856f0938f14429f398` | 930 | `negotiate.ts` |
| 137 | `main` | `packages/sdk-js/src/types.ts` | `d24366e385039af083fb9cc774deada6661506c8` | 2097 | `types.ts.d24366e` |
| 138 | `main` | `packages/shared-types/src/combo.ts` | `d3d8530d342bc2adccae97e77ec1b3cbc9159809` | 1848 | `combo.ts` |
| 139 | `main` | `apps/web/src/hooks.client.ts` | `d4d020d0a74a4df01799886ce2c0ae2ca1d9f968` | 428 | `hooks.client.ts` |
| 140 | `main` | `apps/desktop/src-tauri/src/commands/logging.rs` | `d662a3f2efaf664b003d0c251c1c0d512926d3b4` | 216 | `logging.rs` |
| 141 | `main` | `apps/desktop/src/routes/+page.svelte` | `da6bfe1345a0214bdfef3398bd459a8b0d87bdb8` | 667 | `+page.svelte.da6bfe1` |
| 142 | `main` | `.github/CODEOWNERS` | `db7c226246f7e72fc7cc0e505c679841e9dbcc4d` | 117 | `CODEOWNERS` |
| 143 | `main` | `.tool-versions` | `ded27b28bcf0b124a1f1523b970feae5304361c3` | 51 | `.tool-versions` |
| 144 | `main` | `apps/web/src/routes/+layout.svelte` | `e1d8f70df1a9eed0b4666e85cb3ca818db945f09` | 2587 | `+layout.svelte.e1d8f70` |
| 145 | `main` | `tools/scripts/src/bench-sse.ts` | `e331e218563442475bb63e92a9cebcfa5226d53e` | 1743 | `bench-sse.ts` |
| 146 | `archive/pr6029-cliproxy-2026-07-17` | `README.md` | `e50bdd626bd682039a595c5be2f7e3a2410547aa` | 790 | `README.md.e50bdd6` |
| 147 | `main` | `tools/scripts/src/codegen-app-type.ts` | `e718df8c5d52bfeb9e7c860e16184a613a5e9c11` | 1296 | `codegen-app-type.ts` |
| 148 | `main` | `docs/ADRS/0004-tauri-2-macos-first;-electrobun-reserved-for-future-macos-lite.md` | `e9067dd609b65a81ba971029fffa17e0d7a53a1b` | 1022 | `0004-tauri-2-macos-first;-electrobun-reserved-for-future-macos-lite.md` |
| 149 | `main` | `packages/shared-types/package.json` | `eb1ebeef9b81a59e2f647666bbad6263690f2194` | 764 | `package.json.eb1ebee` |
| 150 | `main` | `oxlint.json` | `eba71516a27d8e0e81f1be54c81db720cba5d00b` | 966 | `oxlint.json` |
| 151 | `main` | `.node-version` | `ec7ba0e9bd9ab89de1b8fe9a286d8d7379836567` | 8 | `.node-version` |
| 152 | `main` | `apps/desktop/src-tauri/src/commands/health.rs` | `ed741ce056b80881130f322fe42a352dc642b6c8` | 402 | `health.rs` |
| 153 | `main` | `crates/gateway/tests/ipc.rs` | `efd675ce99b094e0119626344d4f6565d58459bc` | 347 | `ipc.rs` |
| 154 | `main` | `apps/desktop/package.json` | `efe77eb09174363c3cbbe05c06fcdf4932213231` | 1236 | `package.json.efe77eb` |
| 155 | `main` | `apps/web/src/hooks.server.ts` | `effdd72b28a1ebed94d708640f02396cdab69b62` | 1354 | `hooks.server.ts` |
| 156 | `main` | `"docs/ADRS/0002-svelte-5-runes-only-\342\200\224-no-stores-no-legacy-reactivity.md"` | `f0dcba64b848ae458c47bf9e86265a0fd71aa412` | 1008 | `0002-svelte-5-runes-only-\342\200\224-no-stores-no-legacy-reactivity.md` |
| 157 | `main` | `packages/shared-types/src/model.ts` | `f145b510844d8681818175ed887eeabec0359646` | 1529 | `model.ts` |
| 158 | `main` | `apps/web/src/lib/server/hono/routes/apikeys.ts` | `f2484d66bb10c276bdbc597095f965137a76db86` | 1097 | `apikeys.ts` |
| 159 | `main` | `docs/ADRS/0008-electrobun-reserved.md` | `f2e1d93e30d08663853255db4473c1d0c4905fd9` | 532 | `0008-electrobun-reserved.md` |
| 160 | `main` | `pnpm-workspace.yaml` | `f3768ac7086455ac7e22da3c7d2617b98dd8de6b` | 54 | `pnpm-workspace.yaml` |
| 161 | `main` | `packages/sdk-js/tests/sse.test.ts` | `f44ba9493d2751630e902f390f6a0b3661d2524b` | 1161 | `sse.test.ts` |
| 162 | `main` | `apps/web/src/routes/+page.svelte` | `f63cd37dcec3f4f3b669e8c375824d0f513c518f` | 174 | `+page.svelte.f63cd37` |
| 163 | `main` | `apps/web/src/routes/apikeys/+page.svelte` | `f901f9a786bf5cc0174c88b9790d0860b2b4d5a8` | 1764 | `+page.svelte.f901f9a` |
| 164 | `main` | `packages/shared-types/src/primitives.ts` | `f9e3e5bf6c9cfac92b5cb02b5a6e012159198b3c` | 1355 | `primitives.ts` |
| 165 | `main` | `apps/web/src/app.css` | `fa04724d895464a1bca4a0f85febed1d9250f9a9` | 892 | `app.css` |
| 166 | `main` | `docs/ADRS/0009-paraglide-i18n.md` | `fc875fc17c58f96b13f9f203c8e2380fdc68ffa4` | 525 | `0009-paraglide-i18n.md` |
| 167 | `main` | `docs/sessions/20260705-argismonitor-monorepo-bootstrap/01_RESEARCH.md` | `fd56f4fad5e6e267f374414666427064f8457f1d` | 1773 | `01_RESEARCH.md` |
| 168 | `main` | `packages/shared-types/src/auth.ts` | `fdb0edf35c49d5f7c9d0168500a717439d0a64a8` | 1481 | `auth.ts.fdb0edf` |
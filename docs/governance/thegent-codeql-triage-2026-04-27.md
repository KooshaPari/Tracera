# thegent CodeQL Triage — 2026-04-27

**Repo:** `KooshaPari/thegent` (archived: `false`)
**Open alerts:** 288 total = 13 critical + 275 high
**Mode:** API-only inventory. **No alerts dismissed.**

## Critical (13)

| # | Rule | File | Cluster |
|---|------|------|---------|
| 458 | github-oauth | `dotfiles/git/gitconfig` | secret/dotfile — verify rotated |
| 457 | github-pat | `crates/thegent-hooks/src/security.rs` | likely regex/pattern literal — false-positive candidate |
| 456 | gcp-service-account | `apps/byteport/frontend/web-next/app/(dashboard)/settings/providers/page.tsx` | UI string literal — verify |
| 455 | stripe-secret-token | `apps/byteport/frontend/web-next/.env.local` | committed `.env.local` — rotate + purge |
| 79  | py/partial-ssrf | `src/thegent/agents/flash_agent.py` | real code — human triage |
| 78  | py/partial-ssrf | `src/thegent/govern/vetter/checks.py` | real code — human triage |
| 65,64,63 | py/command-line-injection | `src/thegent/infra/shim_subprocess.py` | real code — human triage (subprocess shim) |
| 62  | py/command-line-injection | `heliosHarness/benchmark/src/helios_bench/local_runner.py` | bench harness — likely safe, verify |
| 61  | py/command-line-injection | `src/thegent/agents/direct_agents.py` | real code — human triage |
| 2   | js/request-forgery | `apps/byteport/sdk/typescript/src/client.ts` | SDK base-URL pattern — likely intentional |
| 1   | js/request-forgery | `apps/byteport/frontend/web-next/lib/api.ts` | configurable API base — likely intentional |

### Critical clusters
- **Secret-scan (4):** #455–458. `.env.local` + dotfile = real exposure; `security.rs` + UI provider page = likely literal pattern strings (false-positive candidates after content review).
- **py/command-line-injection (5):** #61–65. All real code; `shim_subprocess.py` (3) is the subprocess wrapper — needs design review, not bulk-dismiss.
- **py/partial-ssrf (2):** #78, #79. Real agent HTTP code — human triage.
- **js/request-forgery (2):** #1, #2. Configurable API base URLs in SDK/frontend — common false-positive pattern but needs confirmation.

**Bulk-dismiss candidates:** none without per-file content review. No test/.archive/vendor paths in the critical set.

## High (275) — by rule

| Count | Rule |
|------:|------|
| 182 | rust/path-injection |
|  60 | py/path-injection |
|  17 | CVE/GHSA (dependency advisories) |
|   3 | py/overly-permissive-file |
|   3 | py/clear-text-logging-sensitive-data |
|   3 | js/user-controlled-bypass |
|   2 | py/polynomial-redos |
|   2 | go/path-injection |
|   1 | rust/cleartext-logging |
|   1 | py/weak-sensitive-data-hashing |

`rust/path-injection` + `py/path-injection` = 242/275 (88%). Likely high false-positive rate in CLI/dev-tooling context — candidate for path-cluster sweep (separate task). 17 CVE/GHSA entries are dependency advisories, not code findings — handled via Dependabot.

## Recommendation
1. Rotate secrets behind #455 + #458 immediately; verify #456/#457 are pattern literals.
2. Human-triage 7 injection criticals (#61–65, #78, #79) — no bulk path.
3. Path-injection sweep (242 high) deferred to follow-up audit.

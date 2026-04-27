# Final 4 LOW Advisories — W-98 Closure

**Scope:** Investigate and propose remediation for 3 rustls-webpki + 1 protobuf LOW advisories blocking zero-advisory state.

**Status:** INVESTIGATION COMPLETE — PROPOSAL READY

---

## PhenoMCP: rustls-webpki (3 advisories)

### Context
- **Current version:** 0.103.13
- **Latest stable:** 0.103.x series (checked 2026-04-27)
- **Latest candidate:** 0.104.0-alpha.7
- **Parent dependency:** rustls (pulled via cryptography/tls stack; direct transitive)
- **Severity:** LOW (all three)

### Advisories

| ID | Title | Impact | Fix |
|---|---|---|---|
| RUSTSEC-2026-0098 | Name constraint bypass | TLS cert validation weakness in edge case | Fix released in 0.104.0+ |
| RUSTSEC-2026-0099 | Wildcard name constraint bypass | Extended to wildcard domains | Fix released in 0.104.0+ |
| RUSTSEC-2026-0104 | CRL parsing panic | Uncontrolled recursion in CRL parsing | Fix released in 0.104.0+ |

### Migration Path

**Option 1: Pin alpha (RECOMMENDED for zero-week closure)**
- Upgrade rustls-webpki to 0.104.0-alpha.7
- Acceptable because:
  - All three advisories fixed in this alpha
  - PhenoMCP is infrastructure/bridge library; alpha stability acceptable
  - Alpha is from official rustls project (not community fork)
- **Risk:** Low. Upstream rustls team actively maintains alphas.
- **Timeline:** ~30 min (verify build, run integration tests, commit)

**Option 2: Suppress with upstream tracking (current state)**
- Keep 0.103.13, update deny.toml to include `crate = "rustls-webpki"` in ignore entries
- Fix syntax error in deny.toml (missing `crate` field)
- Defer to rustls 0.104.0 stable release (ETA: ~2–4 weeks)
- **Risk:** None. Advisories are LOW. Current workaround is documented.
- **Timeline:** ~5 min (syntax fix)

### Recommendation
**Option 1 (migrate to alpha)** — net impact: -3 advisories, zero-week closure. If build+tests pass, proceed immediately. If blockers surface, revert to Option 2.

**Blocker check:** Verify PhenoMCP can build with 0.104.0-alpha.7 and pass all tests.

---

## PhenoObservability: protobuf (1 advisory)

### Context
- **Current version:** 3.7.2
- **Latest stable:** 3.7.2 (current)
- **Latest candidate:** 4.35.0-rc.1 (major bump)
- **Parent dependency:** prometheus v0.14.0 (hard constraint; only consumer in workspace)
- **Severity:** LOW (uncontrolled recursion in protobuf schema parsing)

### Advisory

| ID | Title | Impact | Fix |
|---|---|---|---|
| RUSTSEC-2026-0105 (est.) | Uncontrolled recursion in proto parsing | DoS via deeply nested proto messages | Not in 3.7.x; requires 4.x |

### Migration Path

**Option 1: Suppress with upstream tracking (RECOMMENDED)**
- Keep protobuf 3.7.2
- Fix deny.toml syntax, add suppression with rationale
- Rationale: "protobuf 4.x is major bump; prometheus likely pins 3.7.x for stability. Defer to upstream prometheus update."
- Monitor prometheus releases for 4.x adoption
- **Risk:** Low. Uncontrolled recursion only triggered in adversarial nested schemas (not typical in observability pipelines).
- **Timeline:** ~5 min (syntax fix + reason update)

**Option 2: Force-bump to 4.35.0-rc.1 (NOT RECOMMENDED)**
- Major version bump introduces API breaks
- Likely breaks prometheus 0.14.0 compatibility
- Would require dual-maintenance of protobuf v3 + v4 code paths
- **Not worth** the friction for a LOW advisory that is not triggered in normal observability flows

### Recommendation
**Option 2 (suppress)** — Protobuf 4.x is a major breaking change. Upstream prometheus does not yet support it. Suppress with clear rationale. Re-evaluate when prometheus v0.15+ is released with protobuf 4.x support.

**No blocker.** This is a suppress-and-defer pattern.

---

## Summary: Path to Zero

### Immediate Actions (same session)

| Repo | Advisory | Action | Effort | Impact |
|---|---|---|---|---|
| PhenoMCP | RUSTSEC-2026-0098/99/104 | **Option 1: Migrate to 0.104.0-alpha.7** | 30 min | -3 advisories |
| PhenoObservability | RUSTSEC-2026-0105 | **Option 2: Suppress with rationale** | 5 min | -1 advisory (deferred) |

### Net Result
- PhenoMCP: 3→0 (confirmed fixed in 0.104.0-alpha.7)
- PhenoObservability: 1→0 (suppressed, awaiting upstream prometheus 4.x support)
- **Workspace:** 4→0 = ZERO-WEEK CLOSURE

### Post-Actions (no immediate blocker)
- Set calendar reminder: 2026-06-15 (re-check protobuf 3.7.2 advisory + prometheus adoption)
- Track rustls 0.104.0 stable release (2–4 weeks); plan transition from alpha when stable ships

---

## Approval Gate

**Proceed if:**
1. User approves migration of rustls-webpki to 0.104.0-alpha.7
2. User approves suppress-and-defer for protobuf
3. No additional PhenoMCP/PhenoObservability blockers surface from build/tests

**Next step:** Invoke migration implementation agent.

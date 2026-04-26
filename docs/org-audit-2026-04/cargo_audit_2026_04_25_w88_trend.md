# Cargo-Deny Advisory Trend Analysis — W-69 through W-88

**Period:** W-69 (2026-02-14) → W-88 (2026-04-25)  
**Snapshot Date:** 2026-04-25 (session end W-88)  
**Canonical Repos Audited:** 23 baseline repos (AgilePlus, FocalPoint, PhenoProc, PhenoObservability, Configra, HeliosLab, heliosCLI, + 16 others)

---

## Five-Wave Advisory Trend Table

| Wave | Date | FocalPoint | AgilePlus | Others | Total | Δ vs Prior | Status |
|------|------|-----------|-----------|--------|-------|-----------|--------|
| W-69 | 2026-02-14 | 28 | 4 | 0 | 32 | baseline | — |
| W-72 | 2026-03-07 | 30 | 4 | 0 | 34 | +2 | Hyper deps added |
| W-79 | 2026-03-28 | 35 | 6 | 0 | 41 | +7 | Q1 wasmtime cluster |
| W-85 | 2026-04-18 | 42 | 8 | 0 | 50 | +9 | RUSTSEC-2026-00XX spike |
| W-88 | 2026-04-25 | 42 | 8 | 0 | 50 | — | Stable (FocalPoint blocked) |

---

## Key Findings

**Total Advisory Growth:** 32 → 50 (56% increase over 10 weeks)
- **FocalPoint:** 28 → 42 (+14 advisories, +50%)
  - Primarily wasmtime 19.0.2 sandbox escape cluster (RUSTSEC-2026-0085 through 0096)
  - Blocked on architectural decision (wasmtime 19 → 43 upgrade)
- **AgilePlus:** 4 → 8 (+4 advisories, +100%)
  - rustls-webpki cert validation bugs (3 patched in W-85)
  - Paste carryover (unfixable)
- **Others:** Stable at 0 advisories across 16 repos

**Regression:** No improvement between W-85 and W-88. FocalPoint wasmtime blocked; all other fixes complete.

---

**Report:** 2026-04-25  
**Next Audit:** W-92 (2026-05-23) — post-FocalPoint decision expected


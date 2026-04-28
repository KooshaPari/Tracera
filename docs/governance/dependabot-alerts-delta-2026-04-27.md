# Dependabot Alerts Delta — 2026-04-27

API-only re-snapshot vs Wave-22 audit baseline.

## Totals

| Metric | Wave-22 (prior) | 2026-04-27 | Delta |
|--------|----------------:|-----------:|------:|
| Total open | 316 | **372** | **+56** |
| Critical | n/a | 6 | n/a |
| High | n/a | 114 | n/a |
| Medium | n/a | 186 | n/a |
| Low | n/a | 66 | n/a |

Severity split: CRIT=6 / HIGH=114 / MED=186 / LOW=66.

## Top-10 by Open Alerts

| Repo | Now | Prior | Delta | C/H/M/L |
|------|----:|------:|------:|---------|
| thegent | 57 | 57 | 0 | 0/24/27/6 |
| heliosCLI | 51 | 51 | 0 | 1/22/18/10 |
| HexaKit | 48 | 48 | 0 | 0/16/28/4 |
| QuadSGM | 37 | — | NEW | 2/10/16/9 |
| PhenoLang | 36 | 36 | 0 | 2/8/19/7 |
| PhenoProject | 31 | 31 | 0 | 0/15/15/1 |
| pheno | 26 | 28 | -2 | 1/6/13/6 |
| BytePort | 16 | 16 | 0 | 0/0/11/5 |
| Tracera | 15 | 15 | 0 | 0/5/9/1 |
| KDesktopVirt | 8 | — | NEW | 0/1/2/5 |
| hwLedger | 7 | 7 | 0 | 0/3/2/2 |
| PhenoRuntime | 6 | 6 | 0 | 0/1/1/4 |

## Movers

- **Up**: QuadSGM +37 (new in top set, 2 critical), KDesktopVirt +8 (new), pheno -2.
- **Down (crossed zero)**: none observed in top tier; lower-tier repos unchanged.
- **Stable**: thegent, heliosCLI, HexaKit, PhenoLang, PhenoProject, BytePort, Tracera, hwLedger, PhenoRuntime — identical counts to Wave-22.

## Net Delta

+56 alerts (316 → 372). Driver: QuadSGM (+37) and KDesktopVirt (+8) entering the audit set; remaining +11 from long-tail repos (Parpoura 5, Dino 5, helios-router 4, others 1–3).

## Method

- Source: `gh api repos/KooshaPari/<repo>/dependabot/alerts?state=open --paginate`.
- Scope: 92 non-archived non-fork repos in KooshaPari org.
- Skips: 0 (all repos returned valid responses).
- Critical alerts (6 total): heliosCLI×1, QuadSGM×2, PhenoLang×2, pheno×1.

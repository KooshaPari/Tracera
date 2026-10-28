# Scope correction + review findings (2026-10-15)

## 1. The `/parent/` work was built in the wrong repo — and the operator closed it

**PR #6** (KooshaPari/KooshaPari, "koosha-phenotype: add /parent/ view as default
landing", branch `feature/cockpit-parent-view` @ `6f9478f`) was **closed by the operator**
at 2026-10-15T07:06:51Z with the comment:

> Intended for job cockpit not here

`main` was never touched — the commit existed only on the feature branch — so the close
performed the discard cleanly and **no revert was required**. The branch remains on origin
(`e5f2a03..6f9478f`) and should **not** be deleted; it is a working Phase 1 implementation
if the work is ever wanted in the SPA.

**Why the routing was wrong:** directive #1 says "`dash.kooshapari.com` must land on
`/parent/` first", and I read the mention of that hostname as scoping the work to
`koosha-phenotype`. The docset _also_ contains the 2026-10-12T21:16Z instruction — "dash.kooshapari.com must refresh on event or at minimum every 15 min... **Do in job-cockpit on a branch**" — and that is the instruction that governs _where the work happens_. Both lines
were in front of me; the second one should have decided the repo.

## 2. The two repos are architecturally different — the work cannot simply move

|                 | `koosha-phenotype`                                | `job-cockpit`                                                         |
| --------------- | ------------------------------------------------- | --------------------------------------------------------------------- |
| Remote          | `KooshaPari/KooshaPari`                           | `KooshaPari/job-cockpit` (private)                                    |
| Local clone     | `~/CodeProjects/Phenotype/repos/koosha-phenotype` | `~/CodeProjects/Phenotype/repos/cockpit-source` (renamed)             |
| Architecture    | vanilla-JS esbuild SPA                            | **Python dashboard** (3 `.py`, 0 `.js`)                               |
| `/parent` route | exists (added by the closed PR)                   | **does not exist** — grep hits on "parent" are Python `Path().parent` |

The Phase 1 deliverable was `scripts/views/parent.js` + `styles/parent.css` +
`parent.html` in an SPA. There is no JS layer in `job-cockpit` to receive it, so the work
would have to be **rewritten in Python**, which is a different task rather than a move.

**Open question for the operator — "job cockpit" is two different things:**

- **(a)** The `/parent/` view belongs in `job-cockpit` → rebuild it in Python there; the
  SPA route work is wrong in principle.
- **(b)** The _refresh + per-agent surface_ belongs in `job-cockpit`, while `/parent/`
  remains a route in `koosha-phenotype` → reopen PR #6 there, fix the findings in §3, and
  add the refresh to the dashboard separately.

Evidence leans to **(b)**: the operator's sentence is about where to _do the work_, not
about relocating a route that only exists in the SPA; and `job-cockpit` already contains 7
`agent`/`refresh` references. **Not decided here** — guessing wrong already cost one full
build-and-PR cycle.

## 3. Review findings to carry forward (CodeAnt, on the closed PR #6)

These are real defects found by review, not by inspection. They survive the repo move and
should be fixed wherever this work lands.

1. **`parent.html` copied but not in `TOP_LEVEL_ROUTES`** — prerendering leaves the view
   root empty for crawlers and for users without JavaScript. _Incomplete implementation._
   A second registry exists beyond the one found by the repo's own drift test.
2. **ASCII frame misalignment** — the agent-count row ends short of the frame's right
   border, so the table's closing edge does not line up.
3. **The refresh signal overstates freshness** — the 15-minute timer updates only the
   timestamp, not the roster, then announces "Snapshot refreshed". Stale agent states can
   therefore appear freshly refreshed. For a monitoring view this is the most substantive
   of the four: the freshness indicator does not reflect data freshness.
4. **Duplicate render on append** — the view appends into the root without clearing it, so
   navigating within the route leaves the previous `Parent` view in place and duplicates
   its content. _(A real bug introduced by this work.)_
5. **Weak contrast on the status pills** — fallback colours on white cards, worst on
   `historical`. Fails the WCAG 2.2 AA target the constitution sets.

## 4. Related risk raised by review, and one caution

CodeAnt rated the PR **Medium Risk** on the grounds that the roster is explicitly
unverified while the page presents its states as a snapshot. That is a real tension: the
view displays agent state as fact while the underlying data is corroborated, not confirmed.
Whichever repo this lands in, the page should either label the roster as static/unverified
visibly to the reader, or the data must be confirmed first (see `05_BLOCKERS.md` P6 and the
paperclip status in `02_CURRENT_STATE.md`).

**Caution on `job-cockpit`:** its 4 uncommitted files are a `<REDACTED>` sanitization pass,
not feature work. Committing them would be **destructive**, not cosmetic — the plist `Label`
itself would change, and the wrapper's exec path would point at `/Users/<REDACTED>/bin/...`,
so the service could not start. Do not commit those files. This is the third repo in the
same sanitization family (with HeliosLab and phenotype-registry) and is consistently a
local, uncommitted share-prep pass.

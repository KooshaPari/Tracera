# Usability walkthrough and acceptance witnesses

Expected journey, not a claim this audit performed it. One real product must carry the same identities through every step. Use DOM/text assertions and process/file/log receipts; no screenshots or recordings.

```text
Import -> establish baseline -> inspect inventory -> traverse evidence
   -> adjudicate discrepancy -> hand off repair -> verify -> restart/reconcile
```

| Step                                 | Current usable source surface                  | Required user-visible witness                                                                                                      | Blocking work |
| ------------------------------------ | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| Enter authenticated workspace        | Auth/readiness source exists                   | Correct user/scope; HTML sign-in cannot pass as API health; backend/store identity shown                                           | C1, C7        |
| Select/import a real product         | Item snapshot import and project read          | Accepted product identity distinct from repo/session; complete inventory receipt, re-import no duplication                         | C2            |
| Explore items and relations          | Paginated item reads and SWEE queries          | Forward/reverse typed links remain within product/baseline; omitted/permission-filtered results labeled                            | C2, C4        |
| Understand UI/API/test relationships | Partial projections                            | Page label selects its actual domain; item detail and evidence resolve; no identical generic table masquerading as different views | C5            |
| Find a discrepancy                   | Assessment component with open isolation issue | Independent seeded missing/stale/contradictory source evidence yields correct sourced finding; unrelated product cannot affect it  | C3            |
| Search and inspect context           | Title substring search                         | ID/label/type/source lookup with explicit completeness and bounded navigation                                                      | C4            |
| Assign bounded work                  | Agent/ALM integration surfaces                 | Stable finding/work IDs; approved scope, owner and expected proof; no duplicate work or final-effect credentials in agent          | C6            |
| Verify and accept repair             | Evidence model                                 | Failed result cannot show success; authoritative baseline change records evidence and decision                                     | C3, C6        |
| Restart/update/recover               | SQL stores exist; observation store in memory  | Same product, baseline, IDs, observations, links and findings survive restart; restored backup reconciles                          | C2, C7        |
| Use as daily authority               | Not qualified                                  | Unfamiliar operator completes journey on real data; retains failure/intervention log and comparison against practical baseline     | C9            |

Required negative controls: unavailable backend, Access HTML 200, 401/403/404/429/5xx, invalid JSON, partial pagination, valid empty, conflicting requirement, stale baseline, repeated import, corrupt evidence, cross-product ID collision, cycle/budget truncation, restart during write and untrusted repository instructions. Outcomes remain independent of the implementation's own expected outputs.

A successful health request, seeded project count or graph rendering passes only its individual checkpoint. Current usability is a collection of real read primitives with an open end-to-end trust/persistence path. A consumer may use them experimentally with explicit limitations; they are not yet a qualified replacement for the full accepted workflow.

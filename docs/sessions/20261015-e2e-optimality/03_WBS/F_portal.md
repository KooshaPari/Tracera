# F. Portal: job-cockpit /parent/

**Phase:** P6 (Portal)  
**Task Prefix:** PO-001..PO-100  
**Goal:** job-cockpit owns /parent/. The worker, token, refetch, nav, prerender, and contrast gaps are closed there. The other Portal names stay separate products.  
**Depends On:** P4, P5  
**Unlocks:** P7

Each surface is one real gap. The four leaves on a surface are record, contract, change, and proof. They are not index clones.

| Task | Description | Depends On | Est | Surface | Acceptance |
|------|-------------|------------|-----|---------|------------|
| PO-001 | Record: job-cockpit owns the /parent/ view | — | 10m | job-cockpit /parent/ | Current behavior is written down with the command or query used |
| PO-002 | Contract: job-cockpit owns the /parent/ view | PO-001 | 10m | job-cockpit /parent/ | Expected behavior is stated as a pass/fail check |
| PO-003 | Change: job-cockpit owns the /parent/ view | PO-002 | 20m | job-cockpit /parent/ | The surface matches the contract or the gap is recorded as still open |
| PO-004 | Prove: job-cockpit owns the /parent/ view | PO-003 | 10m | job-cockpit /parent/ | The check fails on the broken input and passes on the fixed input |
| PO-005 | Record: koosha-phenotype keeps a pointer after the 2026-10-14 close comment | — | 10m | koosha-phenotype PR #6 | Current behavior is written down with the command or query used |
| PO-006 | Contract: koosha-phenotype keeps a pointer after the 2026-10-14 close comment | PO-005 | 10m | koosha-phenotype PR #6 | Expected behavior is stated as a pass/fail check |
| PO-007 | Change: koosha-phenotype keeps a pointer after the 2026-10-14 close comment | PO-006 | 20m | koosha-phenotype PR #6 | The surface matches the contract or the gap is recorded as still open |
| PO-008 | Prove: koosha-phenotype keeps a pointer after the 2026-10-14 close comment | PO-007 | 10m | koosha-phenotype PR #6 | The check fails on the broken input and passes on the fixed input |
| PO-009 | Record: phenotype-hub is not the cockpit | — | 10m | phenotype-hub | Current behavior is written down with the command or query used |
| PO-010 | Contract: phenotype-hub is not the cockpit | PO-009 | 10m | phenotype-hub | Expected behavior is stated as a pass/fail check |
| PO-011 | Change: phenotype-hub is not the cockpit | PO-010 | 20m | phenotype-hub | The surface matches the contract or the gap is recorded as still open |
| PO-012 | Prove: phenotype-hub is not the cockpit | PO-011 | 10m | phenotype-hub | The check fails on the broken input and passes on the fixed input |
| PO-013 | Record: Portalis is not the cockpit | — | 10m | Portalis | Current behavior is written down with the command or query used |
| PO-014 | Contract: Portalis is not the cockpit | PO-013 | 10m | Portalis | Expected behavior is stated as a pass/fail check |
| PO-015 | Change: Portalis is not the cockpit | PO-014 | 20m | Portalis | The surface matches the contract or the gap is recorded as still open |
| PO-016 | Prove: Portalis is not the cockpit | PO-015 | 10m | Portalis | The check fails on the broken input and passes on the fixed input |
| PO-017 | Record: the worker proxy does not exist | — | 10m | /api/parent/* Cloudflare Worker | Current behavior is written down with the command or query used |
| PO-018 | Contract: the worker proxy does not exist | PO-017 | 10m | /api/parent/* Cloudflare Worker | Expected behavior is stated as a pass/fail check |
| PO-019 | Change: the worker proxy does not exist | PO-018 | 20m | /api/parent/* Cloudflare Worker | The surface matches the contract or the gap is recorded as still open |
| PO-020 | Prove: the worker proxy does not exist | PO-019 | 10m | /api/parent/* Cloudflare Worker | The check fails on the broken input and passes on the fixed input |
| PO-021 | Record: the token the worker needs is not provisioned | PO-020 | 10m | Cloudflare Access service token | Current behavior is written down with the command or query used |
| PO-022 | Contract: the token the worker needs is not provisioned | PO-021 | 10m | Cloudflare Access service token | Expected behavior is stated as a pass/fail check |
| PO-023 | Change: the token the worker needs is not provisioned | PO-022 | 20m | Cloudflare Access service token | The surface matches the contract or the gap is recorded as still open |
| PO-024 | Prove: the token the worker needs is not provisioned | PO-023 | 10m | Cloudflare Access service token | The check fails on the broken input and passes on the fixed input |
| PO-025 | Record: the timer writes a timestamp and does not refetch | — | 10m | /parent/ 15-minute timer | Current behavior is written down with the command or query used |
| PO-026 | Contract: the timer writes a timestamp and does not refetch | PO-025 | 10m | /parent/ 15-minute timer | Expected behavior is stated as a pass/fail check |
| PO-027 | Change: the timer writes a timestamp and does not refetch | PO-026 | 20m | /parent/ 15-minute timer | The surface matches the contract or the gap is recorded as still open |
| PO-028 | Prove: the timer writes a timestamp and does not refetch | PO-027 | 10m | /parent/ 15-minute timer | The check fails on the broken input and passes on the fixed input |
| PO-029 | Record: the freshness label must match the payload age | — | 10m | /parent/ payload age | Current behavior is written down with the command or query used |
| PO-030 | Contract: the freshness label must match the payload age | PO-029 | 10m | /parent/ payload age | Expected behavior is stated as a pass/fail check |
| PO-031 | Change: the freshness label must match the payload age | PO-030 | 20m | /parent/ payload age | The surface matches the contract or the gap is recorded as still open |
| PO-032 | Prove: the freshness label must match the payload age | PO-031 | 10m | /parent/ payload age | The check fails on the broken input and passes on the fixed input |
| PO-033 | Record: the route is missing from prerender | — | 10m | /parent/ prerender list | Current behavior is written down with the command or query used |
| PO-034 | Contract: the route is missing from prerender | PO-033 | 10m | /parent/ prerender list | Expected behavior is stated as a pass/fail check |
| PO-035 | Change: the route is missing from prerender | PO-034 | 20m | /parent/ prerender list | The surface matches the contract or the gap is recorded as still open |
| PO-036 | Prove: the route is missing from prerender | PO-035 | 10m | /parent/ prerender list | The check fails on the broken input and passes on the fixed input |
| PO-037 | Record: the route is missing from navigation | — | 10m | /parent/ nav list | Current behavior is written down with the command or query used |
| PO-038 | Contract: the route is missing from navigation | PO-037 | 10m | /parent/ nav list | Expected behavior is stated as a pass/fail check |
| PO-039 | Change: the route is missing from navigation | PO-038 | 20m | /parent/ nav list | The surface matches the contract or the gap is recorded as still open |
| PO-040 | Prove: the route is missing from navigation | PO-039 | 10m | /parent/ nav list | The check fails on the broken input and passes on the fixed input |
| PO-041 | Record: the known contrast failure on /parent/ | PO-040 | 10m | /parent/ contrast | Current behavior is written down with the command or query used |
| PO-042 | Contract: the known contrast failure on /parent/ | PO-041 | 10m | /parent/ contrast | Expected behavior is stated as a pass/fail check |
| PO-043 | Change: the known contrast failure on /parent/ | PO-042 | 20m | /parent/ contrast | The surface matches the contract or the gap is recorded as still open |
| PO-044 | Prove: the known contrast failure on /parent/ | PO-043 | 10m | /parent/ contrast | The check fails on the broken input and passes on the fixed input |
| PO-045 | Record: a down backend must not render as healthy | — | 10m | /parent/ outage render | Current behavior is written down with the command or query used |
| PO-046 | Contract: a down backend must not render as healthy | PO-045 | 10m | /parent/ outage render | Expected behavior is stated as a pass/fail check |
| PO-047 | Change: a down backend must not render as healthy | PO-046 | 20m | /parent/ outage render | The surface matches the contract or the gap is recorded as still open |
| PO-048 | Prove: a down backend must not render as healthy | PO-047 | 10m | /parent/ outage render | The check fails on the broken input and passes on the fixed input |
| PO-049 | Record: an empty result must not render as healthy | — | 10m | /parent/ empty render | Current behavior is written down with the command or query used |
| PO-050 | Contract: an empty result must not render as healthy | PO-049 | 10m | /parent/ empty render | Expected behavior is stated as a pass/fail check |
| PO-051 | Change: an empty result must not render as healthy | PO-050 | 20m | /parent/ empty render | The surface matches the contract or the gap is recorded as still open |
| PO-052 | Prove: an empty result must not render as healthy | PO-051 | 10m | /parent/ empty render | The check fails on the broken input and passes on the fixed input |
| PO-053 | Record: requests without the service token fail closed | — | 10m | worker auth | Current behavior is written down with the command or query used |
| PO-054 | Contract: requests without the service token fail closed | PO-053 | 10m | worker auth | Expected behavior is stated as a pass/fail check |
| PO-055 | Change: requests without the service token fail closed | PO-054 | 20m | worker auth | The surface matches the contract or the gap is recorded as still open |
| PO-056 | Prove: requests without the service token fail closed | PO-055 | 10m | worker auth | The check fails on the broken input and passes on the fixed input |
| PO-057 | Record: the service token is not shipped to the browser | — | 10m | client bundle | Current behavior is written down with the command or query used |
| PO-058 | Contract: the service token is not shipped to the browser | PO-057 | 10m | client bundle | Expected behavior is stated as a pass/fail check |
| PO-059 | Change: the service token is not shipped to the browser | PO-058 | 20m | client bundle | The surface matches the contract or the gap is recorded as still open |
| PO-060 | Prove: the service token is not shipped to the browser | PO-059 | 10m | client bundle | The check fails on the broken input and passes on the fixed input |
| PO-061 | Record: the view at a desktop width | PO-060 | 10m | /parent/ desktop viewport | Current behavior is written down with the command or query used |
| PO-062 | Contract: the view at a desktop width | PO-061 | 10m | /parent/ desktop viewport | Expected behavior is stated as a pass/fail check |
| PO-063 | Change: the view at a desktop width | PO-062 | 20m | /parent/ desktop viewport | The surface matches the contract or the gap is recorded as still open |
| PO-064 | Prove: the view at a desktop width | PO-063 | 10m | /parent/ desktop viewport | The check fails on the broken input and passes on the fixed input |
| PO-065 | Record: the view at a mobile width | — | 10m | /parent/ mobile viewport | Current behavior is written down with the command or query used |
| PO-066 | Contract: the view at a mobile width | PO-065 | 10m | /parent/ mobile viewport | Expected behavior is stated as a pass/fail check |
| PO-067 | Change: the view at a mobile width | PO-066 | 20m | /parent/ mobile viewport | The surface matches the contract or the gap is recorded as still open |
| PO-068 | Prove: the view at a mobile width | PO-067 | 10m | /parent/ mobile viewport | The check fails on the broken input and passes on the fixed input |
| PO-069 | Record: refresh is reachable from the keyboard | — | 10m | /parent/ keyboard refresh | Current behavior is written down with the command or query used |
| PO-070 | Contract: refresh is reachable from the keyboard | PO-069 | 10m | /parent/ keyboard refresh | Expected behavior is stated as a pass/fail check |
| PO-071 | Change: refresh is reachable from the keyboard | PO-070 | 20m | /parent/ keyboard refresh | The surface matches the contract or the gap is recorded as still open |
| PO-072 | Prove: refresh is reachable from the keyboard | PO-071 | 10m | /parent/ keyboard refresh | The check fails on the broken input and passes on the fixed input |
| PO-073 | Record: the route is missing from the sitemap | — | 10m | /parent/ sitemap | Current behavior is written down with the command or query used |
| PO-074 | Contract: the route is missing from the sitemap | PO-073 | 10m | /parent/ sitemap | Expected behavior is stated as a pass/fail check |
| PO-075 | Change: the route is missing from the sitemap | PO-074 | 20m | /parent/ sitemap | The surface matches the contract or the gap is recorded as still open |
| PO-076 | Prove: the route is missing from the sitemap | PO-075 | 10m | /parent/ sitemap | The check fails on the broken input and passes on the fixed input |
| PO-077 | Record: a bad worker deploy can be rolled back | — | 10m | worker deploy rollback | Current behavior is written down with the command or query used |
| PO-078 | Contract: a bad worker deploy can be rolled back | PO-077 | 10m | worker deploy rollback | Expected behavior is stated as a pass/fail check |
| PO-079 | Change: a bad worker deploy can be rolled back | PO-078 | 20m | worker deploy rollback | The surface matches the contract or the gap is recorded as still open |
| PO-080 | Prove: a bad worker deploy can be rolled back | PO-079 | 10m | worker deploy rollback | The check fails on the broken input and passes on the fixed input |
| PO-081 | Record: prerender must not freeze a stale parent payload | PO-080 | 10m | prerender cache | Current behavior is written down with the command or query used |
| PO-082 | Contract: prerender must not freeze a stale parent payload | PO-081 | 10m | prerender cache | Expected behavior is stated as a pass/fail check |
| PO-083 | Change: prerender must not freeze a stale parent payload | PO-082 | 20m | prerender cache | The surface matches the contract or the gap is recorded as still open |
| PO-084 | Prove: prerender must not freeze a stale parent payload | PO-083 | 10m | prerender cache | The check fails on the broken input and passes on the fixed input |
| PO-085 | Record: the dossier may point at the view and must not host a second copy | — | 10m | docs-5 Tracera dossier link | Current behavior is written down with the command or query used |
| PO-086 | Contract: the dossier may point at the view and must not host a second copy | PO-085 | 10m | docs-5 Tracera dossier link | Expected behavior is stated as a pass/fail check |
| PO-087 | Change: the dossier may point at the view and must not host a second copy | PO-086 | 20m | docs-5 Tracera dossier link | The surface matches the contract or the gap is recorded as still open |
| PO-088 | Prove: the dossier may point at the view and must not host a second copy | PO-087 | 10m | docs-5 Tracera dossier link | The check fails on the broken input and passes on the fixed input |
| PO-089 | Record: the browser origin allowed to call the worker | — | 10m | job-cockpit to worker CORS | Current behavior is written down with the command or query used |
| PO-090 | Contract: the browser origin allowed to call the worker | PO-089 | 10m | job-cockpit to worker CORS | Expected behavior is stated as a pass/fail check |
| PO-091 | Change: the browser origin allowed to call the worker | PO-090 | 20m | job-cockpit to worker CORS | The surface matches the contract or the gap is recorded as still open |
| PO-092 | Prove: the browser origin allowed to call the worker | PO-091 | 10m | job-cockpit to worker CORS | The check fails on the broken input and passes on the fixed input |
| PO-093 | Record: a failed upstream is named in the error, not replaced with a canned healthy body | — | 10m | upstream error text | Current behavior is written down with the command or query used |
| PO-094 | Contract: a failed upstream is named in the error, not replaced with a canned healthy body | PO-093 | 10m | upstream error text | Expected behavior is stated as a pass/fail check |
| PO-095 | Change: a failed upstream is named in the error, not replaced with a canned healthy body | PO-094 | 20m | upstream error text | The surface matches the contract or the gap is recorded as still open |
| PO-096 | Prove: a failed upstream is named in the error, not replaced with a canned healthy body | PO-095 | 10m | upstream error text | The check fails on the broken input and passes on the fixed input |
| PO-097 | Record: the Access application in front of the worker | — | 10m | Access application binding | Current behavior is written down with the command or query used |
| PO-098 | Contract: the Access application in front of the worker | PO-097 | 10m | Access application binding | Expected behavior is stated as a pass/fail check |
| PO-099 | Change: the Access application in front of the worker | PO-098 | 20m | Access application binding | The surface matches the contract or the gap is recorded as still open |
| PO-100 | Prove: the Access application in front of the worker | PO-099 | 10m | Access application binding | The check fails on the broken input and passes on the fixed input |


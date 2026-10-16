# Acceptance refresh, 2026-10-16 PDT

PR snapshot inspected: `aa49e0cd42956fffd6bfab49b0271df397760788`.
This refresh changes audit documentation only. No service repair, Access policy
change, mutation endpoint probe, screenshot, recording, merge or history rewrite.

## Current runtime boundary

At approximately 15:42-15:49 PDT, Windows SSH was reachable. An owned local-only
SSH forward from 127.0.0.1:18991 to Windows loopback 8091 returned an empty
reply (curl exit 52, HTTP 000) for GET /api/v1/projects. A direct Windows
curl.exe GET to 127.0.0.1:8080/api/v1/projects failed to connect (exit 7).
Therefore the previously usable local runtime path is currently unavailable.
This is an environment observation, not an additional application defect or
proof that the public service is down. No authentication retries were made.

The planned six-project item pagination/type/isolation manifest is NOT_TESTABLE
in this refresh. Historical 533 unique TRACERA and zero CIVIS records remain
dated evidence from 2026-10-15; neither count is freshly reverified. No other
project counts, isolation intersections or synthetic entity IDs are inferred.
Three detail journeys, actual selected-project sidebar journeys and complete
artifact identity/data acceptance remain unverified. Restore or identify the
current authorized runtime listener, then rerun these read-only checks.

## Published-document reconciliation

The canonical inventory parses as 73 rows: 29 GAP records plus 44 VIEW records.
All IDs are unique. There are 37 Unknown-severity rows across that whole table;
this is distinct from 33 Unknown view rows. Every GAP ID has one corresponding
issue heading; four headings were normalized to begin with [Instinct].
The method and source-reconciliation tables each retain 284 references, the
historical/DOM tables 59 entries, actual sidebar receipts 44 entries, and the
baseline index 652 records. These are different denominators. Indexed promises,
method classifications and route navigations do not prove feature acceptance.
Older current-count statements in the dated coverage chronology describe those
passes and are superseded by this snapshot; they must not be summed together.

The audit remains incomplete. No completion marker was written. The previously
sunset heartbeat stays sunset; an unavailable runtime does not justify an
endless unchanged polling loop. Existing checkouts were untouched; publication
uses the fresh /tmp/tracera-acceptance-20261016 clone.

# TRC-MATURE-V1 Generation / Validation Receipt

**Generated:** 2026-09-29  
**Base revision:** `17eef2379d4a673e1c8cc71ed7663fae9e94309b`

Generator pre-write assertions:
- 25 pillar records
- 200 feature records (8 per pillar)
- 1,000 FR records (5 atomic grading dimensions per feature)
- sequential unique FR IDs `TRC-FR-0001` through `TRC-FR-1000`
- every generated FR receives a known pillar and feature ID
- every FR receives CVP/MVP/GA/Mature applicability metadata
- every FR receives growth semantics
- every FR receives two acceptance IDs, positive/negative oracle intent, and two future test IDs
- test generation remains explicitly deferred
- current implementation/evidence grade remains null/unassessed

## Connector limitation

The GitHub connector accepted the generated `mature-contract.v1.json` write (~2.1 MB), but its file-read response truncates content of this size. Therefore this pass does **not** claim a complete post-write JSON round-trip parse through the connector.

The later local/CI validation step should parse the repository file directly and enforce schema/reference checks before merge. This limitation is recorded as a validation gap, not silently treated as green.

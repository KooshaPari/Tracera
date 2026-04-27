# Ralph Tasks

[x] Audit live state and seed prioritized DAG tasks (with agent-imessage async layer work) from current repo truth.
[x] Implement FR-011/013 envelope + elicitation schemas in `agent-user-status` with CLI/MCP wiring and tests.
[x] Implement FR-014/012 async receipt lifecycle + sender-side echo deletion state machine in `agent-user-status` with bounded persistence.
[x] Harden stop-hook performance in `agent-user-status` by replacing unbounded JSONL reads with tail-seek/caching/rotation and add latency regression tests.
[ ] Decompose oversized `agent-user-status` Python modules (>350 lines) after hardening lands, updating all callers and test coverage.

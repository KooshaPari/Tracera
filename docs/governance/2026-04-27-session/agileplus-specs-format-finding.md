# AgilePlus kitty-specs format inconsistency (2026-04-27)

## Finding

Of the AgilePlus specs audited this session, **only spec 013 uses Markdown checkbox syntax** (`- [ ]` / `- [x]`) for WP tasks. Other specs use `**State:** planned` headers per WP.

This means earlier checkbox-count audits showing "0 incomplete" for specs 014/016 were misleading — those specs are fully aspirational, not done.

## Per-spec status

| Spec | Format | Active state |
|---|---|---|
| 013-phenotype-infrakit-stabilization | Checkboxes | 56 incomplete `- [ ]` |
| 014-observability-stack-completion | State headers | 19 WPs all `planned` |
| 016-agent-framework-expansion | State headers | 5+ WPs all `planned` |
| 021-polyrepo-ecosystem-stabilization | Pending audit | TBD |

## Implication

**For automated burndown tracking** to work, AgilePlus specs need format standardization:
- Either: convert spec 013 to State header format (matches majority)
- Or: convert specs 014/016/etc. to checkbox format (better for programmatic counting)

**Recommended:** checkbox format for all — easier to grep + matches prior session ETL workflows. Spec 014's WPs are well-decomposed enough to mechanically convert each subtask to a checkbox.

## Spec 014 (observability) top WPs
1. WP-000: PhenoObservability crate inventory + freshness audit → `research/inventory.md`
2. WP-001: W3C Trace Context contract (traceparent/tracestate/adapters/sampling)
3. WP-002: CVE/SBOM check residual advisory record → `research/cve-status.md`
4. WP-003: Cross-repo observability labeling scheme → `phenotype-shared/docs/observability/labeling-scheme.md`
5. WP-004: Log/trace/metric correlation spec

## Spec 016 (agent framework) top WPs
1. WP-001: Agentora orchestration core (state machine, interfaces, health monitoring)
2. WP-002: AgentMCP protocol server + Agentora bridge
3. WP-003: Event bus (routing/filtering, lifecycle delivery, persistence/replay, back-pressure)
4. WP-004: Policy schema + distribution + enforcement + conflict + audit
5. WP-005: Agent snapshot/restore + migration handshake + rollback

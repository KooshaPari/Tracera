# Legacy Cleanup Communication Plan

## Summary

We are exiting the remaining legacy authentication shims, provider registries, HTTP client, and tunnel aliases. The removal window closes on **31 March 2025**. This note captures the audience, messaging, and checkpoints required to land the change safely.

## Stakeholders

| Team | Contact | Impact | Action |
| ---- | ------- | ------ | ------ |
| SDK maintainers | @sdk-core | Auth & registry imports | Update default templates and SDK examples |
| QA automation | @qa-bots | HTTP client swaps, provider catalogs | Migrate mocks and fixtures to the new catalog APIs |
| Infra / Orchestration | @infra-ops | Service infrastructure tunnel aliases | Replace `start_tunnel` and `get_service_url` usages |
| Developer Experience | @dx | Documentation & kit updates | Publish migration callouts and update tutorials |

## Timeline

| Date | Milestone | Notes |
| ---- | --------- | ----- |
| 17 Feb 2025 | Deprecation warning landed | Code emits logs & `DeprecationWarning` with 31 Mar deadline |
| 28 Feb 2025 | Consumer status check-in | Collect confirmation from each stakeholder on migration progress |
| 17 Mar 2025 | Final reminder | Send release note + issue tracker ping |
| 31 Mar 2025 | Removal window closes | Delete legacy aliases in next minor release |

## Communication Channels

- `#pheno-sdk` Slack thread for quick updates.
- Weekly infra/auth sync agenda item until the deadline.
- Release notes entry in `docs/RELEASE_NOTES_v2.0.0.md`.
- Migration FAQ hosted in `docs/migrations/NAMESPACE_MIGRATION_GUIDE.md` (updated with steps).

## Follow-Up Tasks

- [ ] Verify each owning team has a tracking ticket.
- [ ] Schedule automated warning monitoring (look for `start_tunnel`/`get_service_url` logger output).
- [ ] Draft upgrade snippet for `pip install --upgrade pheno-sdk` blog post.
- [ ] Confirm removal PR includes final changelog + migration reminder.

# Testing Strategy

## Required Checks

- `git diff --check HEAD~1..HEAD`
- README/session badge search with `rg`
- `python3 Tracera/validate_governance.py` from repo root when available

## Notes

The badge proof is documentation-only, so scoped diff and governance validation
are the primary proof surface.

# AGENTS.md - Agent Rules for Tracera

## Agent Roles

| Agent | Responsibility | Allowed Operations |
|-------|---------------|-------------------|
| FORGE | Code implementation | Write, Patch, Shell |
| AGENT | Task execution | Shell, Search, Read |

## Governance Rules

1. **FR Traceability** - All tests MUST reference FR-XXX-NNN
2. **AI Attribution** - .phenotype/ai-traceability.yaml MUST exist
3. **CI/CD Compliance** - .github/workflows/traceability.yml MUST pass

## Prohibited Actions

- Delete without read first
- Modify without FR reference

## Validation

Run before any commit:
```bash
python3 validate_governance.py
```

Last Updated: 2026-04-04

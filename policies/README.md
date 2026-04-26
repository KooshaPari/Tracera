# Policies

Declarative rules for enforcement and compliance.

## Purpose
Enforce organizational policies programmatically.

## Mutability
Enforced - Violations block actions.

## Structure
```
policies/
├── opa/                # OPA/Rego policies
│   ├── authz.rego     # Authorization policies
│   └── compliance.rego
├── github/             # GitHub policies
│   ├── branch-protection.yml
│   └── required-checks.yml
└── compliance/         # Compliance controls
    ├── soc2/
    └── gdpr/
```

## OPA Policies
Open Policy Agent for infrastructure and access control.

```rego
# authz.rego
package authz

default allow = false

allow {
    input.user.role == "admin"
}

allow {
    input.user.role == "developer"
    input.action == "read"
}
```

## GitHub Policies
| Policy | Purpose |
|--------|---------|
| Branch protection | Require PRs, reviews, status checks |
| Required checks | Block merge without passing CI |
| CODEOWNERS | Auto-request review from owners |

## Compliance Controls
| Framework | Controls |
|-----------|----------|
| SOC2 | Access, encryption, logging |
| GDPR | Data handling, consent, deletion |

## Agent Pattern
| Action | Pattern |
|--------|---------|
| Read | Load policies during validation |
| Write | Update policies with approvals |
| Enforce | Fail on policy violation |

## Related
- [security/](../security/) - Security policies
- [governance/](../governance/) - Policy decisions (ADRs)

# PhenoKits Restructuring Plan

**Status**: Planning
**Date**: 2026-04-05
**Owner**: PhenoKits Team

---

## Context

The `PhenoKits` workspace currently conflates artifact types. Agents consuming these artifacts need clear signals about:
- What to scaffold vs import vs parameterize
- What is org-locked vs editable
- What requires enforcement vs passive compliance

---

## Comprehensive Artifact Taxonomy

### Category 1: TEMPLATES

**Definition**: Reusable scaffolding for project initialization and bootstrapping.

| Aspect | Details |
|--------|---------|
| **Purpose** | Generate new projects, services, or components |
| **Mutability** | Parameterized - Accept variables for customization |
| **Agent Pattern** | Template instantiation with variable substitution |
| **Examples** | `template-service-api/`, `template-webapp/`, `template-cli/` |

### Category 2: CONFIGS

**Definition**: Parameterized configurations for tools, CI/CD, infrastructure, and runtime.

| Subcategory | Purpose | Mutability |
|-------------|---------|------------|
| **Tooling** | Linters, formatters, IDEs | Parameterized |
| **CI/CD** | Pipeline definitions | Parameterized |
| **Infrastructure** | Cloud, container configs | Parameterized |
| **Application** | Runtime settings | Locked for production |

### Category 3: LIBS

**Definition**: Reusable code packages providing functionality across projects.

| Aspect | Details |
|--------|---------|
| **Purpose** | Share code, enforce consistency, reduce duplication |
| **Structure** | Multi-language (Rust canonical, Python/TS/Go wrappers) |
| **Distribution** | crates.io, PyPI, npm, pkg.go.dev |
| **Examples** | `pheno-core/`, `pheno-logging/`, `pheno-auth/` |

### Category 4: SECRETS

**Definition**: Sensitive configuration requiring secure storage and management.

| Aspect | Details |
|--------|---------|
| **Storage** | Vault, AWS Secrets Manager, environment variables |
| **Rotation** | Automated rotation policies |
| **Access** | RBAC, least privilege |
| **Scanning** | gitleaks, detect-secrets, TruffleHog |
| **Agent Pattern** | Never hardcode; reference via secret manager |

### Category 5: GOVERNANCE

**Definition**: Architectural decisions, policies, and organizational standards.

| Type | Purpose | Status |
|------|---------|--------|
| **ADRs** | Architecture Decision Records | Editable drafting → Locked acceptance |
| **RFCs** | Request for Comments | Editable during discussion |
| **Policies** | Organizational rules | Locked |
| **Charters** | Project ownership | Locked |
| **Standards** | Coding standards | Locked |

### Category 6: SECURITY

**Definition**: Security configurations, scanning, and policies.

| Category | Examples | Tooling |
|----------|----------|---------|
| **Scanning** | SAST, DAST configs | Bandit, Semgrep, CodeQL |
| **Policies** | OPA policies, security baselines | OPA, Checkov, tfsec |
| **Hardening** | CIS benchmarks, STIGs | Docker hardening, K8s policies |
| **Agent Pattern** | Agent enforces scanning | Agent writes scanning configs |

### Category 7: OBSERVABILITY

**Definition**: Logging, metrics, tracing, and alerting configurations.

| Type | Purpose | Examples |
|------|---------|----------|
| **Logging** | Structured log formats, levels | JSON logging, log sampling |
| **Metrics** | Prometheus, StatsD configs | `prometheus.yml`, dashboards |
| **Tracing** | OpenTelemetry, Jaeger | Collector configs, sampling rates |
| **Alerting** | PagerDuty, OpsGenie | Alert rules, escalation policies |

### Category 8: DOCUMENTATION

**Definition**: Human-readable documentation for projects and APIs.

| Type | Audience | Format |
|------|----------|--------|
| **README** | All users | Markdown |
| **API Docs** | Developers | OpenAPI/Swagger |
| **Runbooks** | Operators | Markdown with procedures |
| **Decision Logs** | Architects | ADR index |

### Category 9: SCRIPTS

**Definition**: Automation scripts, CLIs, and tooling.

| Category | Purpose | Examples |
|----------|---------|----------|
| **Build** | Compile, package | `build.sh`, `Makefile`, `justfile` |
| **Release** | Version, publish | `release.sh`, changelog generation |
| **Quality** | Lint, test, format | `quality-gate.sh` |
| **Utility** | Project-specific | `setup-git-secrets.sh` |

### Category 10: SCHEMAS

**Definition**: Type definitions, API specs, and data models.

| Type | Purpose | Format |
|------|---------|--------|
| **Type Definitions** | Cross-language types | Rust (canonical), PyO3, wasm-bindgen |
| **API Specs** | REST/gRPC contracts | OpenAPI, Protobuf, GraphQL SDL |
| **Data Models** | Domain models | JSON Schema, TypeScript interfaces |

### Category 11: POLICIES

**Definition**: Declarative rules for enforcement and compliance.

| Type | Scope | Examples |
|------|-------|----------|
| **OPA Policies** | Infrastructure | Terraform, Kubernetes policies |
| **CI/CD Gates** | Pipeline | Required checks, branch protection |
| **Access Control** | Repository | CODEOWNERS, team permissions |
| **Compliance** | Regulatory | SOC2, GDPR controls |

### Category 12: CREDENTIALS

**Definition**: Authentication configurations and credential patterns.

| Type | Purpose | Management |
|------|---------|------------|
| **Auth Configs** | OAuth, JWT, API keys | External secret manager |
| **Credential Patterns** | SDK auth examples | `stripe.go` pattern |
| **MFA** | Multi-factor auth | TOTP, hardware keys |

---

## Agent Interaction Matrix

| Category | Agent Reads | Agent Writes | Agent Enforces |
|----------|-------------|--------------|----------------|
| Templates | Yes | Yes (instantiation) | No |
| Configs | Yes | Parameterized | Yes (validation) |
| Libs | Yes | No | No |
| Secrets | Yes | No | No |
| Governance | Yes | Yes (ADRs) | No |
| Security | Yes | Yes | Yes (scanning) |
| Observability | Yes | Yes (configs) | Yes (monitoring) |
| Documentation | Yes | Yes | No |
| Scripts | Yes | Yes | No |
| Schemas | Yes | Yes (code gen) | Yes (type checking) |
| Policies | Yes | Yes | Yes (OPA, gates) |
| Credentials | Yes | No | Yes (rotation) |

---

## Proposed Directory Structure

```
PhenoKits/
├── # Root Governance
├── SPEC.md                           # Master specification
├── CHARTER.md                        # Project charter
├── CODEOWNERS                        # Repository ownership
├── CONTRIBUTING.md                   # Contribution guidelines
├── SECURITY.md                       # Security policy
│
├── # ─────────────────────────────────────────────────────────────
├── # 1. TEMPLATES - Scaffolding for new projects
├── # ─────────────────────────────────────────────────────────────
├── templates/
│   ├── hexa-kit/                     # Main template CLI & registry
│   │   ├── src/
│   │   └── templates/
│   │       ├── lang-rust/
│   │       ├── lang-python/
│   │       ├── lang-typescript/
│   │       ├── lang-go/
│   │       ├── domain-service/
│   │       └── domain-webapp/
│   ├── commons/                      # Template utilities (Rust)
│   ├── domain/                       # Domain templates (private)
│   └── program-ops/                  # Ops scaffolding
│
├── # ─────────────────────────────────────────────────────────────
├── # 2. CONFIGS - Parameterized, consumed as-is
├── # ─────────────────────────────────────────────────────────────
├── configs/
│   ├── tooling/                     # Linters, formatters
│   │   ├── ruff.toml
│   │   ├── pre-commit/
│   │   │   ├── basic.yaml
│   │   │   ├── comprehensive.yaml
│   │   │   └── security.yaml
│   │   ├── pyproject.toml
│   │   ├── eslint/
│   │   └── golangci-lint/
│   ├── cicd/                        # CI/CD pipelines
│   │   ├── github-actions/
│   │   │   ├── ci.yml               # CI workflow
│   │   │   ├── release.yml           # Release workflow
│   │   │   ├── pr.yml                # PR validation
│   │   │   └── security-scan.yml      # Security scanning
│   │   └── gitlab-ci/
│   ├── infra/                        # Infrastructure configs
│   │   ├── docker/
│   │   │   ├── Dockerfile.base
│   │   │   └── docker-compose.yml
│   │   ├── kubernetes/
│   │   │   ├── deployment.yaml
│   │   │   └── service.yaml
│   │   └── terraform/
│   │       └── modules/
│   ├── observability/                # Logging, metrics, tracing
│   │   ├── prometheus.yml
│   │   ├── otel/
│   │   └── grafana/
│   └── app/                          # Application configs
│       ├── config.yaml
│       └── .env.example
│
├── # ─────────────────────────────────────────────────────────────
├── # 3. LIBS - Libraries/derivatives
├── # ─────────────────────────────────────────────────────────────
├── libs/
│   ├── rust/                         # Canonical cores
│   │   ├── phenotype-core/
│   │   ├── phenotype-config/
│   │   └── phenotype-errors/
│   ├── python/                       # Python bindings
│   │   ├── pheno-core/
│   │   ├── pheno-config/
│   │   └── pheno-errors/
│   ├── typescript/                   # TypeScript bindings
│   │   └── packages/
│   └── go/                           # Go bindings
│       └── pheno/
│
├── # ─────────────────────────────────────────────────────────────
├── # 4. SECRETS - Secret management patterns
├── # ─────────────────────────────────────────────────────────────
├── secrets/
│   ├── patterns/                     # Secret handling patterns
│   │   ├── env-var.yml               # Environment variable secrets
│   │   ├── vault.yml                 # HashiCorp Vault patterns
│   │   └── aws-secrets.yml           # AWS Secrets Manager patterns
│   ├── rotation/                     # Rotation policies
│   │   └── rotation-policy.yml
│   ├── scanning/                     # Secret scanning configs
│   │   ├── gitleaks.toml
│   │   └── trufflehog.yml
│   └── templates/                    # Secret templates
│       └── secret-template.yml
│
├── # ─────────────────────────────────────────────────────────────
├── # 5. GOVERNANCE - ADRs, RFCs, Standards
├── # ─────────────────────────────────────────────────────────────
├── governance/
│   ├── adr/                          # Architecture Decision Records
│   │   ├── ADR-000-template.md
│   │   ├── index.md
│   │   └── records/
│   │       ├── ADR-001-initial.md
│   │       └── ADR-002-*.md
│   ├── rfc/                          # Requests for Comments
│   │   └── rfc-000-template.md
│   ├── standards/                    # Coding standards
│   │   ├── rust.md
│   │   ├── python.md
│   │   ├── typescript.md
│   │   └── go.md
│   └── validate_governance.py        # Governance validation script
│
├── # ─────────────────────────────────────────────────────────────
├── # 6. SECURITY - Security configurations & policies
├── # ─────────────────────────────────────────────────────────────
├── security/
│   ├── scanning/                     # SAST/DAST configs
│   │   ├── semgrep/
│   │   │   └── rules/
│   │   ├── codeql/
│   │   └── bandit/
│   ├── policies/                     # Security policies
│   │   ├── opa/                     # OPA Rego policies
│   │   │   ├── authz.rego
│   │   │   └── compliance.rego
│   │   ├── checkov/
│   │   └── tfsec/
│   └── hardening/                    # CIS, STIG baselines
│       ├── docker/
│       └── kubernetes/
│
├── # ─────────────────────────────────────────────────────────────
├── # 7. OBSERVABILITY - Logging, metrics, tracing
├── # ─────────────────────────────────────────────────────────────
├── observability/
│   ├── logging/                       # Logging configs
│   │   ├── structured-json.yaml
│   │   └── sampling.yaml
│   ├── metrics/                      # Metrics configs
│   │   ├── prometheus.yml
│   │   └── dashboards/
│   ├── tracing/                      # Tracing configs
│   │   ├── otel-collector.yml
│   │   └── sampling-rates.yaml
│   └── alerting/                     # Alerting configs
│       ├── rules/
│       └── escalation.yaml
│
├── # ─────────────────────────────────────────────────────────────
├── # 8. DOCUMENTATION - Docs, runbooks, guides
├── # ─────────────────────────────────────────────────────────────
├── docs/
│   ├── api/                          # API documentation
│   ├── runbooks/                     # Operational runbooks
│   │   ├── incident-response.md
│   │   └── deployment.md
│   └── guides/                       # User guides
│
├── # ─────────────────────────────────────────────────────────────
├── # 9. SCRIPTS - Automation scripts
├── # ─────────────────────────────────────────────────────────────
├── scripts/
│   ├── build/                        # Build scripts
│   │   ├── build.sh
│   │   └── Makefile
│   ├── release/                      # Release scripts
│   │   ├── release.sh
│   │   └── changelog.sh
│   ├── quality/                      # Quality gate scripts
│   │   ├── quality-gate.sh
│   │   └── activate-quality-gate.sh
│   └── utility/                      # Utility scripts
│       ├── setup-git-secrets.sh
│       └── analyze_prs.sh
│
├── # ─────────────────────────────────────────────────────────────
├── # 10. SCHEMAS - Type definitions & API specs
├── # ─────────────────────────────────────────────────────────────
├── schemas/
│   ├── types/                        # Cross-language types
│   │   ├── rust/
│   │   ├── python/
│   │   └── typescript/
│   ├── api/                          # API specs
│   │   ├── openapi/
│   │   └── protobuf/
│   └── data/                         # JSON Schema
│
├── # ─────────────────────────────────────────────────────────────
├── # 11. POLICIES - Enforcement policies
├── # ─────────────────────────────────────────────────────────────
├── policies/
│   ├── opa/                          # OPA policies
│   ├── github/                       # GitHub policies
│   │   ├── branch-protection.yml
│   │   └── required-checks.yml
│   └── compliance/                    # Compliance controls
│       ├── soc2/
│       └── gdpr/
│
├── # ─────────────────────────────────────────────────────────────
├── # 12. CREDENTIALS - Auth configs & patterns
├── # ─────────────────────────────────────────────────────────────
├── credentials/
│   ├── auth/                          # Authentication configs
│   │   ├── oauth2/
│   │   ├── oidc/
│   │   └── jwt/
│   ├── patterns/                     # Credential patterns
│   │   └── sdk-auth.go              # Example SDK auth pattern
│   └── mfa/                           # MFA configurations
│
└── # GitHub-specific
    └── .github/
        └── ISSUE_TEMPLATE/
```

---

## Migration Steps

### Phase 1: Create Structure (Week 1)

1. Create top-level directories for all 12 categories
2. Add category-specific README files
3. Set up governance validation tooling
4. Create .gitignore entries for new structure

### Phase 2: Categorize Existing Artifacts (Week 2)

1. Audit all existing artifacts in `HexaKit/`, `template-*`
2. Categorize each artifact by type
3. Identify cross-references and dependencies
4. Document categorization decisions in ADR

### Phase 3: Migrate Artifacts (Week 3)

1. Move templates → `templates/`
2. Move configs → `configs/`
3. Move libs → `libs/`
4. Create `secrets/`, `security/`, `observability/` from existing patterns
5. Update all import/reference paths

### Phase 4: Parameterization System (Week 4)

1. Implement parameterization for `configs/`
2. Add JSON Schema for config validation
3. Create parameterization CLI/tooling
4. Add guards for org-locked configs

### Phase 5: Agent Integration (Week 5)

1. Document agent consumption patterns for each category
2. Create agent tooling for artifact discovery
3. Add agent-specific documentation (`.claude/` or similar)
4. Test agent workflows for each category

### Phase 6: Documentation & Polish (Week 6)

1. Update master README for new structure
2. Add usage guides for each artifact type
3. Document migration notes
4. Create onboarding guide for new contributors

---

## Open Questions

- [ ] How to handle parametrized configs that need org-locked defaults?
- [ ] Should configs be versioned separately from libs?
- [ ] How to handle transitive dependencies between libs?
- [ ] What tooling for parameterization? (JSON Schema? TypeScript types?)
- [ ] How to version the overall PhenoKits structure?
- [ ] What CI/CD for PhenoKits itself?
- [ ] How to handle secret templates that contain placeholders?

---

## Related

- `phenotype-registry` - Artifact registry
- `AgilePlus` - Feature tracking
- `PhenoDevOps/agent-devops-setups/policies/` - Policy template implementation
- `PhenoKit/python/config-kit/` - Configuration management patterns
- `AuthKit/` - Authentication/credential patterns
- `ResilienceKit/` - Deployment patterns

---

## References

- HashiCorp Terraform: `.changes/`, `.release/`, `scripts/`, `tools/`
- Stripe stripe-go: `.claude/`, `scripts/`, flat resource structure
- Pallets Flask: `src/`, `tests/`, `docs/`, `.devcontainer/`
- Netflix OSS: Domain-based organization

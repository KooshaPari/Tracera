# ADR-007: Quality Gates and Policy Enforcement Architecture

**Status:** Accepted  
**Date:** 2026-04-04  
**Author:** Phenotype Architecture Team  
**Stakeholders:** Template Program, DevEx, Platform Engineering, Security

---

## Context

Without enforcement mechanisms, templates drift in quality and consistency. Historical analysis shows:

**Quality Drift Patterns:**

| Project Type | Lint Config Present | CI Config Present | Security Scan | README Complete |
|--------------|---------------------|-------------------|---------------|-----------------|
| Go Services | 60% | 70% | 40% | 50% |
| Python APIs | 55% | 65% | 35% | 45% |
| TypeScript Apps | 65% | 75% | 45% | 55% |

**Root Causes:**

1. **No automated verification**: Templates not validated before release
2. **No standard baseline**: Each template defines quality differently
3. **No enforcement**: CI doesn't gate on template compliance
4. **No visibility**: No reporting on which templates meet standards

**Requirements from Stakeholders:**

1. **Template Program**: Ensure all templates meet baseline before release
2. **DevEx**: Consistent experience across all project types
3. **Platform Engineering**: Templates generate projects that integrate with platform
4. **Security**: All projects have required security files and configurations

---

## Decision

Implement a **layered quality gate system** with mandatory policy enforcement at multiple stages.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Policy Enforcement Layers                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 4: Runtime (CI/CD)                                     │
│  ├── policy-gate action (PR validation)                       │
│  ├── lint-test action (quality checks)                        │
│  └── security-scan action (vulnerability check)             │
│                                                              │
│  Layer 3: Scaffold-Time (Project Creation)                   │
│  ├── Generate → Verify → Commit                              │
│  └── Reconcile → Verify → Apply                              │
│                                                              │
│  Layer 2: Template Release (Distribution)                   │
│  ├── task check (pre-release validation)                     │
│  └── manifest validation                                     │
│                                                              │
│  Layer 1: Development (Template Authoring)                 │
│  ├── Editor/linter validation                                │
│  ├── Pre-commit hooks                                        │
│  └── Local task check                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Layer 1: Development-Time Quality Gates

**Purpose:** Fast feedback for template authors during development.

#### 1.1 Editor Integration

```yaml
# .vscode/settings.json (generated in templates)
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true
  },
  "[go]": {
    "editor.defaultFormatter": "golang.go"
  },
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

#### 1.2 Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json

  - repo: local
    hooks:
      - id: template-check
        name: template validation
        entry: task check
        language: system
        pass_filenames: false
        always_run: true
```

#### 1.3 Local Task Check

```yaml
# Taskfile.yml (task check command)
tasks:
  check:
    desc: "Run all quality gates"
    cmds:
      - task: check-manifest
      - task: check-governance
      - task: check-docs
      - task: check-scripts
      - task: check-contracts
    silent: true

  check-manifest:
    desc: "Validate template.manifest.json"
    cmds:
      - scripts/validate-manifest.sh contracts/template.manifest.json

  check-governance:
    desc: "Verify required governance files"
    cmds:
      - scripts/check-governance.sh

  check-docs:
    desc: "Validate documentation completeness"
    cmds:
      - scripts/check-docs.sh

  check-scripts:
    desc: "Validate hook scripts"
    cmds:
      - shellcheck scripts/*.sh

  check-contracts:
    desc: "Validate reconcile rules"
    cmds:
      - scripts/validate-reconcile.sh contracts/reconcile.rules.yaml
```

### Layer 2: Template Release Gates

**Purpose:** Ensure only validated templates are released.

#### 2.1 Release Workflow

```yaml
# .github/workflows/release.yml
name: Template Release

on:
  push:
    tags: ['v*']

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run quality gates
        run: task check

      - name: Validate version matches tag
        run: |
          MANIFEST_VERSION=$(jq -r .version contracts/template.manifest.json)
          TAG_VERSION=${GITHUB_REF#refs/tags/v}
          if [ "$MANIFEST_VERSION" != "$TAG_VERSION" ]; then
            echo "Version mismatch: manifest=$MANIFEST_VERSION, tag=$TAG_VERSION"
            exit 1
          fi

      - name: Test scaffold output
        run: |
          mkdir -p /tmp/test-project
          scripts/scaffold-test.sh /tmp/test-project
          cd /tmp/test-project && task check

  release:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - name: Create release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
```

#### 2.2 Manifest Validation Rules

```python
# Validation rules for template.manifest.json
MANIFEST_SCHEMA = {
    "required": ["layer_type", "layer_name", "version", "owned_paths"],
    "properties": {
        "layer_type": {
            "enum": ["commons", "infrastructure", "language", "domain", "application"]
        },
        "version": {
            "pattern": r"^\d+\.\d+\.\d+$"  # Strict semver
        },
        "owned_paths": {
            "minItems": 1,
            "items": {"type": "string", "pattern": r"^[\w\-/\*\.]+$"}
        },
        "depends_on": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "version"],
                "properties": {
                    "version": {
                        "pattern": r"^[~^]?\d+\.\d+\.\d+(-[\w\.]+)?$"  # Semver range
                    }
                }
            }
        }
    }
}
```

### Layer 3: Scaffold-Time Gates

**Purpose:** Ensure generated projects meet quality baseline.

#### 3.1 Scaffold Verification Pipeline

```python
async def scaffold_with_verification(template, target_path, variables):
    """
    1. Generate project files
    2. Run verification suite
    3. Only commit if all checks pass
    """

    # 1. Generate
    generated = await template.scaffold(target_path, variables)

    # 2. Verify
    results = await run_verification_suite(generated)

    if not results.all_passed:
        # 3. Report failures, don't commit
        report_verification_failures(results)
        raise ScaffoldVerificationError(results.failures)

    # 4. Commit verified project
    await commit_project(generated)
    return generated

async def run_verification_suite(project_path):
    """Run all applicable checks on generated project."""
    checks = [
        GovernanceCheck(),      # SECURITY.md, LICENSE, etc.
        StructureCheck(),     # Directory structure
        LintConfigCheck(),    # Linter configuration present
        CiCheck(),             # CI configuration valid
        ScriptCheck(),         # Hook scripts executable
        DocumentationCheck(),  # README completeness
    ]

    results = []
    for check in checks:
        result = await check.run(project_path)
        results.append(result)

    return VerificationResults(results)
```

#### 3.2 Individual Checks

```python
class GovernanceCheck:
    """Verify required governance files exist and are valid."""

    REQUIRED_FILES = [
        "README.md",
        "LICENSE",
        "SECURITY.md",
        "AGENTS.md",
        "CLAUDE.md",
    ]

    async def run(self, project_path):
        missing = []
        invalid = []

        for filename in self.REQUIRED_FILES:
            filepath = Path(project_path) / filename
            if not filepath.exists():
                missing.append(filename)
            elif not self._is_valid(filepath):
                invalid.append(filename)

        return CheckResult(
            name="governance",
            passed=len(missing) == 0 and len(invalid) == 0,
            missing=missing,
            invalid=invalid
        )

    def _is_valid(self, filepath):
        """Check if file has minimum required content."""
        content = filepath.read_text()
        # Each governance file has required sections
        validators = {
            "README.md": lambda c: "## Installation" in c and "## Usage" in c,
            "SECURITY.md": lambda c: "## Reporting" in c,
            "AGENTS.md": lambda c: "## Core Expectations" in c,
        }
        validator = validators.get(filepath.name, lambda c: True)
        return validator(content)
```

### Layer 4: Runtime (CI/CD) Gates

**Purpose:** Continuous validation as projects evolve.

#### 4.1 Composite Actions

```yaml
# .github/workflows/policy-gate/action.yml
name: 'Policy Gate'
description: 'Validates PR policies and naming conventions'

inputs:
  enforce_admin:
    description: 'Enforce policies on admin users'
    default: 'true'
  required_labels:
    description: 'Comma-separated list of required labels'
    default: ''

runs:
  using: 'composite'
  steps:
    - name: Check PR title format
      shell: bash
      run: |
        TITLE="${{ github.event.pull_request.title }}"
        if ! echo "$TITLE" | grep -E '^(feat|fix|docs|test|refactor|chore|style|perf)(\(.+\))?: .+'; then
          echo "PR title must follow Conventional Commits format"
          echo "Examples: 'feat: add new feature', 'fix(api): resolve bug'"
          exit 1
        fi

    - name: Check branch protection rules
      shell: bash
      run: |
        # Verify PR is not from main to main
        if [ "${{ github.head_ref }}" = "main" ]; then
          echo "Cannot create PR from main branch"
          exit 1
        fi

    - name: Validate template compliance
      shell: bash
      run: |
        if [ -f .template.lock ]; then
          scripts/check-template-compliance.sh
        fi
```

```yaml
# .github/workflows/lint-test/action.yml
name: 'Lint and Test'
description: 'Language-aware linting and test execution'

runs:
  using: 'composite'
  steps:
    - name: Detect language
      id: lang
      shell: bash
      run: |
        if [ -f go.mod ]; then
          echo "language=go" >> $GITHUB_OUTPUT
        elif [ -f pyproject.toml ] || [ -f setup.py ]; then
          echo "language=python" >> $GITHUB_OUTPUT
        elif [ -f package.json ]; then
          echo "language=typescript" >> $GITHUB_OUTPUT
        elif [ -f Cargo.toml ]; then
          echo "language=rust" >> $GITHUB_OUTPUT
        fi

    - name: Run Go checks
      if: steps.lang.outputs.language == 'go'
      shell: bash
      run: |
        go vet ./...
        golangci-lint run
        go test -race -coverprofile=coverage.out ./...

    - name: Run Python checks
      if: steps.lang.outputs.language == 'python'
      shell: bash
      run: |
        ruff check .
        ruff format --check .
        mypy src/
        pytest --cov=src --cov-report=xml

    - name: Run TypeScript checks
      if: steps.lang.outputs.language == 'typescript'
      shell: bash
      run: |
        biome check .
        biome format --check .
        vitest run --coverage

    - name: Run Rust checks
      if: steps.lang.outputs.language == 'rust'
      shell: bash
      run: |
        cargo clippy -- -D warnings
        cargo fmt --check
        cargo nextest run
        cargo audit
```

```yaml
# .github/workflows/security-scan/action.yml
name: 'Security Scan'
description: 'Dependency and code security scanning'

runs:
  using: 'composite'
  steps:
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Run Semgrep
      uses: returntocorp/semgrep-action@v1
      with:
        config: >-
          p/security-audit
          p/owasp-top-ten

    - name: Check for secrets
      uses: trufflesecurity/trufflehog@main
      with:
        path: ./
        base: ${{ github.event.repository.default_branch }}
        head: HEAD
```

### Policy Configuration

```yaml
# contracts/reconcile.rules.yaml - enforcement section
enforcement:
  # Strict: Fail on any violation
  # Moderate: Warn on minor violations
  # Lenient: Only fail on critical violations
  governance: strict
  code_quality: moderate
  documentation: moderate
  security: strict
  dependencies: moderate

  # Gate configuration
gates:
  pre_commit:
    enabled: true
    required_checks:
      - lint
      - format

  pre_push:
    enabled: true
    required_checks:
      - test
      - lint
      - security

  pre_release:
    enabled: true
    required_checks:
      - test
      - coverage
      - lint
      - security
      - documentation
      - governance
```

### Quality Metrics Dashboard

```python
# Reporting structure for quality metrics
@dataclass
class QualityReport:
    """Quality metrics for a template or project."""

    entity_type: str  # "template" or "project"
    entity_name: str
    timestamp: datetime

    # Governance
    governance_score: float  # 0-100
    missing_files: List[str]
    invalid_files: List[str]

    # Code Quality
    lint_score: float  # 0-100
    test_coverage: float  # 0-100
    test_pass_rate: float  # 0-100

    # Security
    security_score: float  # 0-100
    vulnerabilities: List[dict]
    secrets_detected: int

    # Documentation
    documentation_score: float  # 0-100
    missing_sections: List[str]

    # Overall
    overall_score: float  # Weighted average
    grade: str  # A, B, C, D, F

    def to_markdown(self) -> str:
        """Generate markdown report for CI comments."""
        return f"""
## Quality Report: {self.entity_name}

| Category | Score | Grade |
|----------|-------|-------|
| Governance | {self.governance_score:.1f} | {self._grade(self.governance_score)} |
| Code Quality | {self.lint_score:.1f} | {self._grade(self.lint_score)} |
| Test Coverage | {self.test_coverage:.1f}% | {self._grade(self.test_coverage)} |
| Security | {self.security_score:.1f} | {self._grade(self.security_score)} |
| Documentation | {self.documentation_score:.1f} | {self._grade(self.documentation_score)} |
| **Overall** | **{self.overall_score:.1f}** | **{self.grade}** |

### Issues
{self._format_issues()}
        """
```

---

## Consequences

### Positive

1. **Quality Baseline**: All templates and projects meet minimum standards
2. **Early Error Detection**: Issues caught at development time, not production
3. **Consistent Experience**: Developers encounter same quality level everywhere
4. **Automated Compliance**: Security and governance requirements enforced automatically
5. **Continuous Improvement**: Metrics drive quality investments
6. **Reduced Review Load**: Automated checks reduce manual review burden

### Negative

1. **Initial Friction**: Authors must learn and comply with quality gates
2. **Tooling Investment**: CI/CD infrastructure required
3. **Maintenance Overhead**: Gates must evolve with requirements
4. **Potential False Positives**: Automated checks may reject valid cases

### Mitigations

| Concern | Mitigation |
|---------|------------|
| Friction | Clear documentation, helpful error messages |
| Tooling | Shared composite actions reduce per-repo cost |
| Maintenance | Centralized policy management in template-commons |
| False positives | Configurable thresholds, override mechanisms |

---

## Alternatives Considered

### Alternative 1: Post-Hoc Auditing

**Approach:** No gates during development; periodic audits identify issues.

**Rejected:**
- Issues discovered late, expensive to fix
- No prevention, only detection
- Projects drift between audits

### Alternative 2: Centralized CI Only

**Approach:** All quality checks run in centralized CI, none in template.

**Rejected:**
- Slower feedback loop
- Harder to debug failures
- Couples projects to specific CI platform

### Alternative 3: Self-Declared Compliance

**Approach:** Templates declare compliance; no automated verification.

**Rejected:**
- Incentivizes declaring without verifying
- Drift inevitable
- No enforcement mechanism

### Alternative 4: Per-Template Custom Gates

**Approach:** Each template defines its own quality checks.

**Rejected:**
- Inconsistent quality across ecosystem
- Reinventing common checks
- Harder to update policies globally

---

## Implementation

### Phase 1: Development Gates (Current)

- [x] `task check` command defined
- [x] Pre-commit hooks configured
- [x] Editor settings templates

### Phase 2: Release Gates (Next)

- [ ] Release workflow with validation
- [ ] Manifest schema validation
- [ ] Scaffold test automation

### Phase 3: Runtime Gates (Future)

- [ ] Composite actions published
- [ ] Quality metrics dashboard
- [ ] Automated compliance reporting

---

## Success Metrics

1. **Gate Pass Rate**: % of PRs passing all gates on first attempt
2. **Time to Green**: Median time from PR creation to all gates passing
3. **Issue Detection Rate**: % of issues caught by gates vs. production
4. **Developer Satisfaction**: Perception of quality gates (survey)
5. **Security Incident Rate**: Security issues in templated projects

**Targets:**
- Gate pass rate: >80% on first attempt
- Time to green: <10 minutes
- Issue detection: >90% of issues caught pre-production
- Developer satisfaction: >4.0/5.0
- Security incidents: Zero critical vulnerabilities in templated projects

---

## References

1. [SOTA.md](./SOTA.md) - Research on quality enforcement patterns
2. GitHub Actions composite actions documentation
3. Pre-commit framework documentation
4. Conventional Commits specification
5. [SPEC.md](../SPEC.md) - Full specification

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-04 | Four-layer gate architecture | Coverage at all stages of lifecycle |
| 2026-04-04 | `task check` as primary interface | Cross-platform, consistent experience |
| 2026-04-04 | Composite actions for CI | Reusable, maintainable, versioned |
| 2026-04-04 | Strict security gates | Security is non-negotiable |
| 2026-04-04 | Moderate code quality gates | Balance quality with developer velocity |

---

*End of ADR-007*

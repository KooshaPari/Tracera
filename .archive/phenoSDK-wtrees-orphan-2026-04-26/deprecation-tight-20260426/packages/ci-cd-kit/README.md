# CI/CD Kit

Centralized CI/CD workflows and automation for the pheno-sdk ecosystem.

## Features

- **Shared Workflows**: Reusable GitHub Actions workflows for all projects
- **QA Automation**: Comprehensive QA testing and reporting
- **Coverage Analysis**: Code coverage tracking and reporting
- **Quality Gates**: Code quality enforcement and validation
- **Release Automation**: Semantic versioning and release management
- **Documentation**: Automated documentation generation and deployment
- **Security**: Security scanning and vulnerability management
- **Monitoring**: System monitoring and alerting

## Quick Start

```bash
# Install the package
pip install -e packages/ci-cd-kit

# Use in your project
from ci_cd_kit.workflows import WorkflowManager
from ci_cd_kit.qa import QAManager
from ci_cd_kit.coverage import CoverageManager
```

## Workflows

### QA Workflows
- `qa-aegis.yml` - Aegis integration testing
- `qa-e2e.yml` - End-to-end testing automation
- `qa-ingest.yml` - QA data ingestion pipeline
- `qa-merge.yml` - QA merge validation
- `qa-python.yml` - Python-specific QA testing

### Coverage Workflows
- `coverage-python.yml` - Python coverage reporting
- `coverage.yml` - General coverage analysis

### Quality Workflows
- `file-size-guard.yml` - File size enforcement (50MB limit)
- `import-linter.yml` - Import validation and linting
- `legacy-imports.yml` - Legacy import detection
- `prospector-analysis.yml` - Comprehensive code analysis

### Release Workflows
- `semantic-pr.yml` - PR title validation
- `semantic-release.yml` - Automated semantic versioning
- `version.yml` - Version management automation
- `release.yml` - Release automation pipeline

### Documentation Workflows
- `docs-link-check.yml` - Link validation
- `docs-lint.yml` - Documentation linting

### Docker Workflows
- `docker-compose-ci.yml` - Docker Compose CI testing
- `docker-pr.yml` - Docker PR validation
- `docker-release.yml` - Docker release automation
- `build-push.yml` - Build and push automation

### Security Workflows
- `security-testing.yml` - Security testing pipeline
- `security.yml` - Security validation

### Monitoring Workflows
- `monitoring.yml` - System monitoring
- `sonarqube.yml` - SonarQube integration

## Configuration

Create a `ci-cd-config.yaml` file in your project root:

```yaml
project:
  name: "your-project"
  type: "python"

workflows:
  qa:
    enabled: true
    parallel: true
  coverage:
    enabled: true
    threshold: 80
  quality:
    enabled: true
    strict: true
  security:
    enabled: true
    scan_dependencies: true
```

## Usage

### In GitHub Actions

```yaml
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  qa:
    uses: pheno-sdk/ci-cd-kit/.github/workflows/qa-python.yml@main
    with:
      python-version: '3.11'
      test-path: 'tests/'
```

### Programmatically

```python
from ci_cd_kit import WorkflowManager

# Initialize workflow manager
wm = WorkflowManager(config_path="ci-cd-config.yaml")

# Run QA workflow
qa_result = wm.run_qa_workflow()

# Run coverage analysis
coverage_result = wm.run_coverage_analysis()

# Run quality checks
quality_result = wm.run_quality_checks()
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Proprietary - PHENO-SDK Team

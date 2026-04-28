# Pheno-SDK CI/CD Infrastructure

This directory contains the GitHub Actions workflows and CI/CD configuration for the Pheno-SDK monorepo.

## Workflows

### 1. CI/CD Pipeline (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`
- Releases (published)

**Jobs:**
- **test-kits**: Tests each kit individually across Python 3.10, 3.11, and 3.12
  - Runs ruff linting
  - Checks black formatting
  - Executes pytest tests with coverage
  - Uploads coverage to Codecov

- **lint-all**: Lints all Python files in the repository
  - Runs ruff, black, isort
  - Bandit security scan

- **integration-test**: Runs integration tests across kits

- **check-dependencies**: Validates dependency compatibility

### 2. PR Quality Checks (`pr-quality.yml`)

**Triggers:**
- Pull request opened, synchronized, or reopened
- Runs only for the changed files

**Jobs:**
- **quality**: Fast lint and format checks
  - Ruff (fast linter)
  - Black formatting
  - Import sorting with isort

- **changed-files**: Analyzes which kits are affected by the PR

- **security**: Security scans
  - Bandit for code security
  - Safety for dependency vulnerabilities

### 3. Full Quality Check (`full-quality.yml`)

**Triggers:**
- Manual dispatch
- Weekly schedule (Sunday at midnight)

**Jobs:**
- **comprehensive-test**: Full test suite across all Python versions
  - All linting and formatting checks
  - Type checking with mypy
  - Security scans
  - All tests with coverage

- **documentation-check**: Validates documentation quality
  - Checks for README files in all kits
  - Validates `__init__.py` presence

- **dependency-audit**: Audits dependencies for security
  - pip-audit
  - safety checks

- **code-quality-metrics**: Code quality analysis
  - Cyclomatic complexity with radon
  - Dead code detection with vulture
  - Quality summary report

## Git Hooks

### Pre-commit Hook (`.git/hooks/pre-commit`)

Runs automatically before each commit:
1. ✅ Python syntax check across all kits (excluding examples/tests)
2. ✅ Hardcoded secrets detection
3. ✅ Large files check (>1MB)
4. ✅ Kit structure validation (`__init__.py` checks)

**To bypass:** `git commit --no-verify` (not recommended)

### Commit Message Hook (`.git/hooks/commit-msg`)

Enforces [Conventional Commits](https://www.conventionalcommits.org/) format:

**Format:** `type(scope): description`

**Valid types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `build`: Build system changes
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(mcp-qa): add new test runner
fix(authkit): resolve token refresh issue
docs: update README for deploy-kit
chore(deps): update dependencies
```

## Pre-commit Configuration (`.pre-commit-config.yaml`)

Uses pre-commit framework for automated checks:
- **General hooks**: trailing whitespace, YAML/TOML/JSON validation, etc.
- **Black**: Code formatting
- **isort**: Import sorting
- **Ruff**: Fast Python linter
- **Bandit**: Security checks
- **GitGuardian**: Secret scanning

**Installation:**
```bash
pip install pre-commit
pre-commit install
```

**Manual run:**
```bash
pre-commit run --all-files
```

## Code Quality Script (`scripts/code_quality_checks.sh`)

Standalone script for local quality checks:

```bash
# Quick checks (ruff, black, isort)
./scripts/code_quality_checks.sh --quick

# Auto-fix issues
./scripts/code_quality_checks.sh --fix

# Full checks (includes type checking and security)
./scripts/code_quality_checks.sh
```

## Configuration Files

### `pyproject.toml`

Central configuration for all tools:
- **ruff**: Linting rules and exclusions
- **black**: Code formatting (line length: 120)
- **isort**: Import sorting (black profile)
- **bandit**: Security scan settings
- **mypy**: Type checking configuration
- **pytest**: Test discovery and markers
- **coverage**: Coverage reporting

## Best Practices

### For Contributors

1. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

2. **Run quality checks before pushing:**
   ```bash
   ./scripts/code_quality_checks.sh --quick
   ```

3. **Follow conventional commits format**

4. **Write tests** for new features

### For Maintainers

1. **Review CI/CD failures** in pull requests
2. **Monitor weekly quality reports**
3. **Update dependencies** regularly
4. **Review security scan results**

## Troubleshooting

### Pre-commit Hook Failing

```bash
# Skip hooks temporarily (not recommended)
git commit --no-verify

# Fix issues automatically
./scripts/code_quality_checks.sh --fix
```

### CI Failing on Specific Kit

```bash
# Test specific kit locally
cd [kit-name]
pytest tests/
ruff check .
black --check .
```

### Type Checking Errors

```bash
# Run mypy on specific kit
mypy [kit-name] --ignore-missing-imports
```

## Metrics and Reporting

- **Code Coverage**: Uploaded to Codecov on each CI run
- **Security Reports**: Available as artifacts in GitHub Actions
- **Quality Metrics**: Generated weekly by full quality check

## Migration from Old System

This infrastructure was migrated from zen-mcp-server and atoms projects with the following enhancements:

1. ✅ Multi-kit testing strategy (parallel test execution)
2. ✅ Kit-aware quality checks (test each kit independently)
3. ✅ Enhanced security scanning (bandit + safety)
4. ✅ Automated dependency audits
5. ✅ Code quality metrics (radon, vulture)
6. ✅ Documentation validation

## Future Enhancements

- [ ] Add performance regression testing
- [ ] Implement automated changelog generation
- [ ] Add dependency update automation (Dependabot/Renovate)
- [ ] Integrate CodeQL for advanced security analysis
- [ ] Add automated API documentation generation
- [ ] Implement cross-kit integration test suite

---

**Last Updated**: 2025-10-10
**Maintained by**: Pheno Team

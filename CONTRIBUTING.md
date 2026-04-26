# Contributing to template-commons

Thank you for your interest in contributing to template-commons.

## Layer Contract

- **layer_type**: commons
- **layer_name**: template-commons
- **versioning**: semver

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Phenotype-Enterprise/template-commons
cd template-commons

# Install dependencies (if any)
pip install -e .

# Run checks before release
task check
```

## Making Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes following the layer contract
4. Run `task check` to verify compliance
5. Update version following semver
6. Update CHANGELOG.md
7. Create PR with description of changes

## Versioning Policy

- Follow Semantic Versioning (semver)
- Patch version for bug fixes
- Minor version for backwards-compatible additions
- Major version for breaking changes

## Release Process

1. Update CHANGELOG.md with version and date
2. Create git tag: `git tag v*.*.*`
3. Push tag: `git push origin --tags`
4. CI will publish to package registry

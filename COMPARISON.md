# Comparison Matrix

## Feature Comparison

This document compares **template-commons** with similar tools in the project template and scaffolding space.

| Repository | Purpose | Key Features | Language/Framework | Maturity | Comparison |
|------------|---------|--------------|-------------------|----------|------------|
| **template-commons (this repo)** | Shared template primitives | Cross-domain, Semver versioning, Layer contract | Various | Stable | Template foundation |
| [Yeoman](https://github.com/yeoman/yo) | Scaffolding tool | Generators, npm packages | JavaScript | Stable | Industry standard |
| [Cookiecutter](https://github.com/cookiecutter/cookiecutter) | Project templates | Jinja2, CLI, Git integration | Python | Stable | Python ecosystem |
| [Plop](https://github.com/plopjs/plop) | Generator framework | Micro-generators, Prompts | JavaScript | Stable | Lightweight generators |
| [Hygen](https://github.com/jondot/hygen) | Code generator | Markdown-driven, Templates | JavaScript | Stable | Markdown-based |
| [copier](https://github.com/copier-org/copier) | Template system | Updates, YAML config, Python | Python | Stable | Smart updating |

## Detailed Feature Comparison

### Template Features

| Feature | template-commons | Yeoman | Cookiecutter | copier |
|---------|------------------|--------|--------------|--------|
| Layer Contract | ✅ | ❌ | ❌ | ❌ |
| Semver Versioning | ✅ | ❌ | ❌ | ❌ |
| Cross-domain | ✅ | ❌ | ❌ | ❌ |
| Template Primitives | ✅ | ✅ | ✅ | ✅ |

### Versioning & Updates

| Feature | template-commons | Yeoman | copier | Hygen |
|---------|------------------|--------|--------|-------|
| Version Tracking | ✅ (semver) | ❌ | ✅ | ❌ |
| Auto Updates | ❌ | ❌ | ✅ | ❌ |
| Changelog | ✅ | ❌ | ❌ | ❌ |
| Layer Contract | ✅ | ❌ | ❌ | ❌ |

## Layer Contract

```yaml
layer_type: commons
layer_name: template-commons
versioning: semver
```

## Usage

1. Consume via pinned version in downstream domain templates
2. Run `task check` before release
3. Publish version + changelog for contract-affecting changes

## References

- Yeoman: [yeoman/yo](https://github.com/yeoman/yo)
- Cookiecutter: [cookiecutter/cookiecutter](https://github.com/cookiecutter/cookiecutter)
- copier: [copier-org/copier](https://github.com/copier-org/copier)

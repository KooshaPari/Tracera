# Templates

Reusable scaffolding for project initialization and bootstrapping.

## Purpose
Generate new projects, services, or components from standardized templates.

## Mutability
Parameterized - Accept variables for customization (project name, language, features).

## Agent Pattern
Template instantiation with variable substitution.

## Structure
```
templates/
├── hexa-kit/          # Main template CLI & registry
├── commons/           # Template utilities
└── domain/           # Domain-specific templates
```

## Usage
```bash
pheno new --template <template-name> --project-name <name>
```

## Related
- [libs/](../libs/) - Libraries to include in templates
- [configs/](../configs/) - Configurations to apply

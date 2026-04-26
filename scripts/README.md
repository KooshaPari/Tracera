# Scripts

Automation scripts, CLIs, and tooling.

## Purpose
Standardize common operations across projects.

## Mutability
Editable - Extend for project-specific needs.

## Structure
```
scripts/
├── build/              # Build scripts
│   ├── build.sh
│   └── Makefile
├── release/            # Release scripts
│   ├── release.sh
│   └── changelog.sh
├── quality/            # Quality gate scripts
│   ├── quality-gate.sh
│   └── activate-quality-gate.sh
└── utility/            # Utility scripts
    ├── setup-git-secrets.sh
    └── analyze_prs.sh
```

## Script Standards
### Shell Scripts
- Use `set -euo pipefail`
- Include usage/help
- Log with timestamps
- Exit codes: 0=success, 1=failure, 2=invalid args

### Makefiles
- Include `.PHONY` declarations
- Document targets with `##` comments
- Support `make help`

## Usage
```bash
# Quality gate
./scripts/quality/quality-gate.sh

# Build
make build

# Release
./scripts/release/release.sh --version 1.0.0
```

## Agent Pattern
| Action | Pattern |
|--------|---------|
| Execute | Run scripts for build/test/deploy |
| Extend | Add project-specific steps |
| Compose | Chain scripts for complex workflows |

## Related
- [configs/tooling/](../configs/tooling/) - Tooling scripts use
- [scripts/](../scripts/) - Scripts directory

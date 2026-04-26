# Libs

Reusable code packages providing functionality across projects.

## Purpose
Share code, enforce consistency, and reduce duplication.

## Mutability
Locked - Import and use, extend for customization (with versioning awareness).

## Structure by Language
```
libs/
├── rust/           # Canonical implementations
├── python/         # Python bindings
├── typescript/      # TypeScript bindings
└── go/             # Go bindings
```

## Distribution
| Language | Registry | Package |
|----------|----------|---------|
| Rust | crates.io | `phenotype-*` |
| Python | PyPI | `pheno-*` |
| TypeScript | npm | `@phenotype/*` |
| Go | pkg.go.dev | `github.com/phenotype/*` |

## Usage
```rust
// Rust
use phenotype_core::{Config, Error};

#[derive(Debug, Config)]
struct MyConfig {
    #[config(default = "localhost")]
    host: String,
    port: u16,
}
```

```python
# Python
from pheno_core import Config

@dataclass
class MyConfig(Config):
    host: str = "localhost"
    port: int
```

## Agent Pattern
Agents import libs to implement features. Breaking changes require major version bump.

## Related
- [templates/](../templates/) - Templates that include libs
- [schemas/types/](../schemas/types/) - Type definitions

# CLI-Kit Extraction Report

## Summary

The `cli-kit` has been successfully extracted from `phenoSDK` to a standalone package.

**Source Location:** `/Users/kooshapari/CodeProjects/Phenotype/repos/phenoSDK/src/pheno/kits/cli/`  
**Target Location:** `/Users/kooshapari/CodeProjects/Phenotype/repos/PhenoKit/python/cli-kit/`

---

## File Manifest

### Source Files (11 Python files, ~2,362 LOC)

| File | Lines | Description |
|------|-------|-------------|
| `src/pheno_cli_kit/__init__.py` | 58 | Package entry point with all exports |
| `src/pheno_cli_kit/cli.py` | 109 | Main CLI class and Command class |
| `src/pheno_cli_kit/core/__init__.py` | 44 | Core module exports |
| `src/pheno_cli_kit/core/builder.py` | 248 | CLIBuilder for code generation |
| `src/pheno_cli_kit/core/command.py` | 253 | Command, Argument, Option, ArgumentType definitions |
| `src/pheno_cli_kit/core/decorators.py` | 370 | @cli_command, @cli_group decorators with registry |
| `src/pheno_cli_kit/backends/__init__.py` | 20 | Backends module exports |
| `src/pheno_cli_kit/backends/registry.py` | 224 | BackendRegistry and BaseBackend |
| `src/pheno_cli_kit/backends/argparse_backend.py` | 314 | Argparse code generator |
| `src/pheno_cli_kit/backends/click_backend.py` | 343 | Click code generator |
| `src/pheno_cli_kit/backends/typer_backend.py` | 379 | Typer code generator |

### Documentation Files

| File | Lines | Description |
|------|-------|-------------|
| `README.md` | 29 | Basic usage documentation |
| `EXAMPLES.md` | 547 | Comprehensive usage examples |
| `pyproject.toml` | 71 | Package configuration |

---

## pheno.* Imports Found and Updated

### Original External Dependencies (from phenoSDK)

The following imports from the phenoSDK codebase were identified and updated:

1. **`...cli_builder.core.command`** (relative import from sibling kit)
   - **Files affected:**
     - `core/builder.py` - line 8
     - `backends/registry.py` - line 11
     - `backends/typer_backend.py` - line 9
     - `backends/click_backend.py` - line 9
     - `backends/argparse_backend.py` - line 9
   - **Resolution:** Updated to use `..core.command` (relative within pheno_cli_kit)

2. **`cli_builder.backends.registry`** (absolute import)
   - **File affected:** `core/builder.py` - line 160
   - **Resolution:** Updated to `..backends.registry`

3. **`cli_builder.backends.*`** (backend imports in registry)
   - **File affected:** `backends/registry.py` - lines 142-144
   - **Resolution:** Updated to relative imports (`.argparse_backend`, etc.)

### All Imports Now Use Relative Paths

All imports within the package now use relative imports:
- `from ..core.command import ...`
- `from .registry import ...`
- `from .argparse_backend import ...`

---

## Relationship to cli-builder-kit

### Already Extracted

The `cli-builder-kit` has already been extracted to:
`/Users/kooshapari/CodeProjects/Phenotype/repos/PhenoKit/python/cli-builder-kit/`

### Consolidation Analysis

**Key Finding:** There is significant overlap between `cli-kit` and `cli-builder-kit`:

1. **cli-builder-kit** contains:
   - `core/command.py` - Basic Command, Argument, Option, ArgumentType classes
   - Simple dataclass-style definitions
   - ~87 lines

2. **cli-kit** contains:
   - `core/command.py` - Comprehensive Command, Argument, Option, ArgumentType with validation, type checking, subcommands
   - ~253 lines
   - Additional features: ArgumentType enum with PATH, FILE, CHOICE, LIST types; validation logic; callback support; subcommand nesting

### Consolidation Recommendations

**Option 1: Merge cli-builder-kit into cli-kit (RECOMMENDED)**

The `cli-kit` is a superset of `cli-builder-kit`. Consider:
1. Deprecating `cli-builder-kit`
2. Updating all dependents to use `pheno-cli-kit` instead
3. The cli-kit's `core/command.py` already exports compatible aliases:
   - `ArgumentDefinition = Argument`
   - `CommandDefinition = Command`

**Option 2: Keep as Separate Packages**

If maintaining separation is desired:
1. `cli-builder-kit` - Minimal core definitions (lightweight dependency)
2. `cli-kit` - Full framework with backends, decorators, CLI class (heavyweight)
3. cli-kit could depend on cli-builder-kit for base definitions

**Option 3: Make cli-kit Depend on cli-builder-kit**

Update cli-kit to import from cli-builder-kit instead of duplicating:
```python
# Instead of defining its own:
from pheno_cli_builder.core.command import Argument, Command, Option, ArgumentType
```

---

## Usage Instructions

### Installation

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoKit/python/cli-kit
pip install -e ".[all]"  # Install with all backend dependencies
```

### Basic Usage

```python
from pheno_cli_kit import CLI

cli = CLI(backend="typer", name="myapp", version="1.0.0")

@cli.command()
def hello(name: str):
    """Say hello."""
    print(f"Hello, {name}!")

cli.run()
```

### Using CLIBuilder

```python
from pheno_cli_kit import CLIBuilder, Command

builder = CLIBuilder("myapp", version="1.0.0")
builder.add_command(
    Command(name="hello", callback=hello_func, help="Say hello")
)
code = builder.generate(backend="click")
```

---

## Next Steps

1. **Testing:** Add test suite to `tests/` directory
2. **CI/CD:** Set up GitHub Actions for testing and publishing
3. **Documentation:** Expand README with API reference
4. **Consolidation Decision:** Choose and implement one of the consolidation options above
5. **Source Cleanup:** Once extraction is verified, remove from phenoSDK (separate task)

---

## Package Naming

- **PyPI Name:** `pheno-cli-kit`
- **Import Path:** `pheno_cli_kit`
- **Version:** 0.1.0

---

*Extraction completed: 2026-04-04*

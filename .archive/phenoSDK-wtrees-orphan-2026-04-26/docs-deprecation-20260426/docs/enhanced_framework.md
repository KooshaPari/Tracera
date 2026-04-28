# Enhanced Composable MCP Framework

A comprehensive, composable Pythonic library system that provides both simplified and advanced functionality for MCP servers. This framework merges the best of both approaches into a single, extensible system.

## 🚀 Features

- **Composable Command System**: Mix and match command types (basic, advanced, maintenance)
- **Parallel Execution**: High-performance parallel execution for maintenance commands
- **Comprehensive Error Handling**: Robust error handling and logging throughout
- **Integration with pheno-sdk**: Seamless integration with the pheno-sdk ecosystem
- **Support for Both Simple and Complex Use Cases**: From basic start/stop to complex deployment workflows
- **Built-in Check, Lint, and Format Commands**: Comprehensive code quality tools
- **Extensible Architecture**: Easy to add custom commands and functionality

## 📦 Installation

The enhanced framework is part of the pheno-sdk package. No additional installation required.

```python
from src.pheno.mcp.entry_points.enhanced_framework import (
    create_enhanced_framework,
    create_atoms_framework,
    create_zen_framework,
    create_simple_framework
)
```

## 🎯 Quick Start

### Basic Usage

```python
from src.pheno.mcp.entry_points.enhanced_framework import create_atoms_framework

# Create a framework for Atoms MCP
framework = create_atoms_framework(project_root=Path("./atoms_mcp-old"))

# Run CLI
framework.run_cli()
```

### Programmatic Usage

```python
# Create framework
framework = create_enhanced_framework(
    project_name="my_project",
    project_root=Path("./my_project"),
    enable_basic=True,
    enable_advanced=True,
    enable_maintenance=True
)

# Execute commands programmatically
class MockArgs:
    def __init__(self):
        self.port = 50002
        self.verbose = True

args = MockArgs()
result = framework.execute_command("start", args)
```

## 🛠️ Command Types

### Basic Commands
- `start` - Start the MCP server
- `stop` - Stop the MCP server
- `status` - Show server status
- `health` - Perform health check
- `restart` - Restart the MCP server

### Advanced Commands
- `test` - Run test suite with HOT/COLD/DRY modes
- `deploy` - Deploy to various environments
- `validate` - Validate configuration
- `verify` - Verify system setup
- `vendor` - Manage vendoring
- `config` - Manage configuration
- `schema` - Manage database schema
- `embeddings` - Manage vector embeddings
- `check` - Check deployment readiness

### Maintenance Commands
- `check` - Run comprehensive code checks with parallel execution
- `check_ruff` - Run ruff-only comprehensive checks (fastest option)
- `lint` - Run comprehensive linting with ruff (replaces multiple tools)
- `format` - Format code with ruff (replaces black + isort)
- `test` - Run maintenance tests

## 🔧 Framework Types

### 1. Simple Framework
Only basic commands for simple use cases.

```python
framework = create_simple_framework(
    project_name="simple_project",
    project_root=Path("./simple_project")
)
```

### 2. Enhanced Framework
Full-featured framework with all command types.

```python
framework = create_enhanced_framework(
    project_name="advanced_project",
    project_root=Path("./advanced_project"),
    enable_basic=True,
    enable_advanced=True,
    enable_maintenance=True
)
```

### 3. Project-Specific Frameworks
Pre-configured frameworks for specific projects.

```python
# Atoms MCP framework
atoms_framework = create_atoms_framework(project_root=Path("./atoms_mcp-old"))

# Zen MCP framework
zen_framework = create_zen_framework(project_root=Path("./zen-mcp-server"))
```

## 🚀 Advanced Features

### Ruff-Centric Toolchain

The enhanced framework uses ruff as the primary tool for most code quality checks, providing significant performance improvements:

**Ruff Replaces**:
- `flake8` - Linting
- `pylint` (basic) - Code analysis
- `black` - Code formatting
- `isort` - Import sorting
- `pyupgrade` - Python syntax upgrades
- `autoflake` - Unused import/variable removal

**Benefits**:
- ⚡ **10-100x faster** than traditional toolchain
- 🔧 **Single tool** for most code quality checks
- 🎯 **Comprehensive rule coverage** (500+ rules)
- 🔄 **Built-in autofix** capabilities
- 📦 **Single dependency** instead of multiple tools

### Parallel Execution

The maintenance commands use parallel execution for maximum performance:

```python
# Ruff-centric toolchain - ruff replaces many tools
tools = ["ruff", "ruff_format", "mypy", "bandit", "safety", "semgrep", "pytest", "coverage"]

# Ruff replaces: flake8, pylint (basic), black, isort, pyupgrade, autoflake
# Much faster and more comprehensive than traditional toolchain
```

### Comprehensive Check Results

The check command provides detailed results with a checklist matrix:

```
🔍 COMPREHENSIVE CODE CHECK RESULTS
================================================================================

✅ RUFF (autofix applied) - 2.34s
   Fixed 15 issues automatically

❌ BLACK - 1.23s
   Error: 3 files need formatting

✅ ISORT - 0.89s

📊 CHECKLIST MATRIX
================================================================================
Tool            Status   Pass/Total   Errors   Files    Duration
--------------------------------------------------------------------------------
ruff            PASS     15/15        0        25       2.34s
ruff_format     PASS     1/1          0        25       0.45s
mypy            PASS     1/1          0        25       3.45s
bandit          PASS     1/1          0        25       1.67s
safety          PASS     1/1          0        1        0.45s
semgrep         PASS     1/1          0        25       4.23s
pytest          PASS     45/45        0        12       8.90s
coverage        PASS     1/1          0        25       9.12s
--------------------------------------------------------------------------------
TOTAL                   70/70         0        214

📈 SUMMARY:
   Tools: 8/8 passed
   Checks: 70/70 passed
   Errors: 0
   Files: 214 checked

🎯 OVERALL: ✅ ALL CHECKS PASSED
```

### Custom Commands

Add your own commands to the framework:

```python
def custom_hello(args):
    print("Hello from custom command!")
    return 0

def custom_goodbye(args):
    print("Goodbye from custom command!")
    return 0

framework.add_custom_command("hello", custom_hello)
framework.add_custom_command("goodbye", custom_goodbye)
```

### Mixins

Use individual command mixins for maximum flexibility:

```python
from src.pheno.mcp.entry_points.enhanced_framework import (
    BasicCommandsMixin,
    AdvancedCommandsMixin,
    MaintenanceCommandsMixin
)

# Create individual mixins
basic_mixin = BasicCommandsMixin()
advanced_mixin = AdvancedCommandsMixin()
maintenance_mixin = MaintenanceCommandsMixin(project_root)

# Use them independently
result = basic_mixin.cmd_start(args)
result = advanced_mixin.cmd_test(args)
result = maintenance_mixin.cmd_check(args)
```

## 📋 CLI Usage

### Command Line Interface

```bash
# Basic commands
./atoms-mcp-enhanced.py start --port 50002 --verbose
./atoms-mcp-enhanced.py stop
./atoms-mcp-enhanced.py status
./atoms-mcp-enhanced.py health

# Advanced commands
./atoms-mcp-enhanced.py test local --verbose
./atoms-mcp-enhanced.py test prod hot
./atoms-mcp-enhanced.py deploy preview
./atoms-mcp-enhanced.py deploy production
./atoms-mcp-enhanced.py validate
./atoms-mcp-enhanced.py verify
./atoms-mcp-enhanced.py vendor setup
./atoms-mcp-enhanced.py config show
./atoms-mcp-enhanced.py schema check
./atoms-mcp-enhanced.py embeddings backfill

# Maintenance commands
./atoms-mcp-enhanced.py check          # Comprehensive parallel checks
./atoms-mcp-enhanced.py check_ruff     # Ruff-only checks (fastest)
./atoms-mcp-enhanced.py lint           # Linting with ruff (replaces multiple tools)
./atoms-mcp-enhanced.py format         # Code formatting with ruff
```

### Pheno-SDK Integration

The enhanced framework is integrated into the main pheno-sdk CLI:

```bash
# Use enhanced framework through pheno-sdk
pheno check --project atoms_mcp-old    # Enhanced checks
pheno lint --project zen-mcp-server    # Enhanced linting
pheno format --project my_project      # Enhanced formatting
```

## 🔧 Configuration

### Framework Configuration

```python
framework = create_enhanced_framework(
    project_name="my_project",
    project_root=Path("./my_project"),
    enable_basic=True,      # Enable basic commands
    enable_advanced=True,   # Enable advanced commands
    enable_maintenance=True # Enable maintenance commands
)
```

### Command Configuration

Commands can be configured through arguments:

```python
class CommandArgs:
    def __init__(self):
        # Start command args
        self.port = 50002
        self.verbose = True
        self.no_tunnel = False

        # Test command args
        self.environment = "preview"
        self.test_type = "dry"
        self.workers = 4

        # Deploy command args
        self.environment = "production"

        # Vendor command args
        self.vendor_action = "setup"
```

## 🧪 Testing

Run the example to see the framework in action:

```bash
cd pheno-sdk
python examples/enhanced_framework_example.py
```

## 📚 Examples

See `pheno-sdk/examples/enhanced_framework_example.py` for comprehensive usage examples.

## 🤝 Contributing

The enhanced framework is designed to be easily extensible. To add new commands:

1. Create a new mixin class inheriting from `CommandMixin`
2. Implement the `get_commands()` method
3. Add your command methods
4. Register the mixin with the framework

## 📄 License

Part of the pheno-sdk project.

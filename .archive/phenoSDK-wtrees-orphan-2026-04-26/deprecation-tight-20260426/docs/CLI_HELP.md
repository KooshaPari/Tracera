# ATOMS-PHENO CLI Help Documentation

This document provides comprehensive help for all CLI commands available in the ATOMS-PHENO infrastructure.

## Quick Start

```bash
# Show version and status
./pheno version
./pheno status

# Set up development environment
./pheno setup

# Run tests
./pheno test --parallel --coverage

# Run quality checks
./pheno quality

# Run monitoring
./pheno monitor --all
```

## Core Commands

### `pheno version`
Show version information and system details.

**Usage:**
```bash
./pheno version
```

**Output:**
- CLI version
- Python version
- System information

### `pheno status`
Show system status and component availability.

**Usage:**
```bash
./pheno status
```

**Output:**
- Component status table
- Available tools
- System health

### `pheno setup`
Set up development environment with progress tracking.

**Usage:**
```bash
./pheno setup
```

**Features:**
- Progress bar with spinner
- Step-by-step setup process
- Automatic dependency installation

## Testing Commands

### `pheno test`
Run tests with various options.

**Usage:**
```bash
./pheno test [options]
```

**Options:**
- `--parallel`, `-p`: Run tests in parallel using pytest-xdist
- `--coverage`, `-c`: Run with coverage analysis
- `--verbose`, `-v`: Verbose output

**Examples:**
```bash
# Run all tests
./pheno test

# Run tests in parallel with coverage
./pheno test --parallel --coverage

# Run tests with verbose output
./pheno test --verbose
```

## Quality Commands

### `pheno quality`
Run comprehensive code quality checks.

**Usage:**
```bash
./pheno quality
```

**Checks performed:**
- Linting (Ruff)
- Type checking (MyPy)
- Security scan (Bandit)
- Vulnerability check (Safety)
- Code formatting (Black)
- Import sorting (isort)

**Output:**
- Quality check results table
- Pass/fail status for each check
- Detailed output for failed checks

## Monitoring Commands

### `pheno monitor`
Run code monitoring and analysis tools.

**Usage:**
```bash
./pheno monitor [options]
```

**Options:**
- `--complexity`: Analyze code complexity using Radon
- `--duplication`: Check code duplication using Pylint
- `--dependencies`: Analyze dependencies using pipdeptree
- `--all`: Run all monitoring checks

**Examples:**
```bash
# Analyze code complexity
./pheno monitor --complexity

# Check code duplication
./pheno monitor --duplication

# Analyze dependencies
./pheno monitor --dependencies

# Run all monitoring checks
./pheno monitor --all
```

## Vendor Commands

### `pheno vendor status`
Show vendor package status and information.

**Usage:**
```bash
./pheno vendor status
```

**Output:**
- Vendor package list
- Package status
- Size information
- Last modified timestamps

### `pheno vendor sync`
Sync vendor packages from source directories.

**Usage:**
```bash
./pheno vendor sync [package] [options]
```

**Arguments:**
- `package`: Optional package name to sync (default: all packages)

**Options:**
- `--force`: Force sync even if package exists

**Examples:**
```bash
# Sync all packages
./pheno vendor sync

# Sync specific package
./pheno vendor sync pheno-sdk

# Force sync package
./pheno vendor sync zen-mcp-server --force
```

### `pheno vendor verify`
Verify vendor packages for completeness.

**Usage:**
```bash
./pheno vendor verify
```

**Checks:**
- Essential files presence (pyproject.toml, setup.py, requirements.txt)
- Package structure validation
- File integrity checks

### `pheno vendor clean`
Clean vendor packages.

**Usage:**
```bash
./pheno vendor clean [package]
```

**Arguments:**
- `package`: Optional package name to clean (default: all packages)

**Examples:**
```bash
# Clean all packages
./pheno vendor clean

# Clean specific package
./pheno vendor clean atoms_mcp-old
```

## Help Commands

### `pheno help-extended`
Show extended help with examples and detailed information.

**Usage:**
```bash
./pheno help-extended
```

**Output:**
- Comprehensive command reference
- Usage examples
- Parameter descriptions
- Best practices

## Configuration

The CLI uses the following configuration sources (in order of precedence):

1. Command-line arguments
2. Environment variables
3. Configuration files
4. Default values

### Environment Variables

- `PHENO_DEBUG`: Enable debug mode
- `PHENO_VERBOSE`: Enable verbose output
- `PHENO_CONFIG`: Path to configuration file

### Configuration Files

- `pyproject.toml`: Project configuration
- `.env`: Environment variables
- `config/`: Configuration directory

## Troubleshooting

### Common Issues

1. **Command not found**
   - Ensure the `pheno` script is executable: `chmod +x pheno`
   - Check Python path and dependencies

2. **Permission denied**
   - Run with appropriate permissions
   - Check file ownership and permissions

3. **Dependencies missing**
   - Install required packages: `pip install -r requirements-dev.txt`
   - Run setup: `./pheno setup`

4. **Scripts not found**
   - Ensure scripts are in the correct location
   - Check working directory

### Debug Mode

Enable debug mode for detailed output:

```bash
PHENO_DEBUG=1 ./pheno [command]
```

### Verbose Output

Enable verbose output for more details:

```bash
PHENO_VERBOSE=1 ./pheno [command]
```

## Examples

### Complete Workflow

```bash
# 1. Check system status
./pheno status

# 2. Set up environment
./pheno setup

# 3. Run quality checks
./pheno quality

# 4. Run tests with coverage
./pheno test --parallel --coverage

# 5. Run monitoring
./pheno monitor --all

# 6. Sync vendor packages
./pheno vendor sync

# 7. Verify everything
./pheno vendor verify
```

### Development Workflow

```bash
# Quick test run
./pheno test --parallel

# Check code quality
./pheno quality

# Analyze code complexity
./pheno monitor --complexity

# Check dependencies
./pheno monitor --dependencies
```

### CI/CD Workflow

```bash
# Full quality and testing pipeline
./pheno quality && ./pheno test --coverage && ./pheno monitor --all
```

## Advanced Usage

### Custom Scripts

The CLI can be extended with custom scripts:

```bash
# Run custom analysis script
python scripts/custom_analysis.py --help

# Integrate with CLI
./pheno monitor --custom-script scripts/custom_analysis.py
```

### Integration with Make

The CLI integrates with the Makefile system:

```bash
# Run Makefile targets through CLI
make test
make quality
make monitor-all

# Or use CLI directly
./pheno test
./pheno quality
./pheno monitor --all
```

## Support

For additional help and support:

1. Check this documentation
2. Run `./pheno help-extended`
3. Check the project README
4. Review the source code
5. Open an issue on the project repository

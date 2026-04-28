# Unified Tools Collection

This directory consolidates all development, analysis, and quality tools from across the pheno-sdk codebase into a single, organized structure.

## Structure

```
tools_unified/
├── analysis/          # Code analysis and pattern detection tools
├── quality/           # Quality assurance and validation tools
├── deployment/        # Deployment and release automation tools
├── monitoring/        # Monitoring and observability tools
├── testing/          # Testing frameworks and utilities
├── utilities/        # General development utilities
├── diagnostics/      # Diagnostic and troubleshooting tools
├── dashboards/       # Performance and analytics dashboards
└── README.md         # This file
```

## Categories

### Analysis Tools (`analysis/`)
- **Pattern Detection**: Identify architectural patterns and anti-patterns
- **Dependency Analysis**: Analyze code dependencies and coupling
- **Complexity Analysis**: Measure code complexity and maintainability
- **Duplication Detection**: Find duplicate code and logic
- **Churn Analysis**: Analyze code change patterns over time

### Quality Tools (`quality/`)
- **Code Quality Gates**: Enforce coding standards and best practices
- **Security Scanning**: Detect security vulnerabilities and patterns
- **Performance Detection**: Identify performance anti-patterns
- **Architecture Validation**: Validate architectural constraints
- **Integration Gates**: Ensure integration quality

### Deployment Tools (`deployment/`)
- **Build Automation**: Automated build and packaging
- **Release Management**: Release and version management
- **Schema Management**: Database schema migration and validation
- **Deployment Validation**: Pre and post-deployment checks

### Monitoring Tools (`monitoring/`)
- **Analytics Dashboard**: Comprehensive analytics and metrics
- **CI/CD Monitoring**: Pipeline health and performance monitoring
- **Observability**: Application observability and tracing
- **Performance Monitoring**: Real-time performance tracking

### Testing Tools (`testing/`)
- **Test Automation**: Automated test execution and reporting
- **Performance Testing**: Load and performance testing frameworks
- **Security Testing**: Security vulnerability testing
- **Test Data Management**: Test data generation and management
- **Parallel Testing**: Optimized parallel test execution

### Utilities (`utilities/`)
- **Code Metrics**: Lines of code and complexity metrics
- **Memory Profiling**: Memory usage analysis and optimization
- **Dependency Management**: Dependency analysis and management
- **File Operations**: Bulk file operations and processing

### Diagnostics (`diagnostics/`)
- **Health Checks**: System and component health validation
- **Troubleshooting**: Diagnostic tools for issue resolution
- **Integration Testing**: End-to-end integration validation

## Usage

### Running Individual Tools
```bash
# Run analysis tool
python tools_unified/analysis/analyze_dependencies.py

# Run quality check
python tools_unified/quality/code_smell_detector.py

# Run performance test
python tools_unified/testing/performance_testing_framework.py
```

### Using as Python Module
```python
from tools_unified import analysis, quality, testing

# Run dependency analysis
analysis.analyze_dependencies("./src")

# Run quality checks
quality.run_quality_gates("./src")

# Run tests
testing.run_test_suite("./tests")
```

## Migration Notes

This unified structure consolidates tools from:
- `scripts/` - Categorized utility scripts
- `tools/` - Development and analysis tools
- `quality/tools/` - Quality-focused tools

### Duplicates Resolved
- `tools/atlas_health_cli.py` + `quality/tools/atlas_health.py` → `tools_unified/diagnostics/atlas_health.py`
- `scripts/categories/analysis/` + `quality/tools/pattern_detector.py` → `tools_unified/analysis/`
- `scripts/categories/quality/` + `quality/tools/` → `tools_unified/quality/`

## Contributing

When adding new tools:
1. Choose appropriate category based on primary function
2. Follow existing naming conventions
3. Include proper documentation and usage examples
4. Add to relevant `__init__.py` exports
5. Update this README if adding new categories

## Legacy References

The original directories (`scripts/`, `tools/`, `quality/tools/`) are preserved for backward compatibility but should be considered deprecated. All new development should use the unified structure.

# Scripts Directory Organization

This directory has been cleaned up and organized for better maintainability.

## 📊 **Cleanup Summary**

- **Before**: 92 Python scripts
- **After**: 27 active scripts + organized categories
- **Archived**: 65 scripts moved to archive directories

## 📁 **Directory Structure**

### Active Scripts (Main Directory)
Core scripts that are actively used and maintained:

- **Pattern Detection**: `advanced_pattern_detector.py`, `architectural_pattern_validator.py`
- **Code Quality**: `code_smell_detector.py`, `detect_dead_code.py`
- **Documentation**: `documentation_automation.py`, `generate_help_docs.py`
- **Reporting**: `generate_unified_report.py`, `coverage_analysis.py`
- **KInfra Tools**: `kinfra-*.py` (docs, feedback, lint, migrate, validate)
- **Schema Management**: `manage_schema.py`, `migrate_schema.py`
- **Security**: `security_pattern_scanner.py`, `security_policy_enforcer.py`
- **Validation**: `validate_*.py` (cleanup, config, dependencies, schema)
- **Utilities**: `cli_framework.py`, `refactor_large_files.py`, `vendor_*.py`, `version_management.py`

### Organized Categories
Scripts organized by function:

- **`categories/analysis/`** - Code analysis scripts
- **`categories/testing/`** - Test automation and enhancement scripts  
- **`categories/quality/`** - Quality assurance and scoring scripts
- **`categories/monitoring/`** - Health monitoring and observability scripts
- **`categories/deployment/`** - Build, release, and deployment scripts
- **`categories/utilities/`** - General utility scripts

### Archived Scripts
One-time or obsolete scripts moved to archive:

- **`archive/consolidation_scripts/`** - Module consolidation scripts (one-time use)
- **`archive/final_cleanup/`** - Final cleanup scripts (one-time use)
- **`archive/duplicates/`** - Duplicate or superseded scripts

## 🚀 **Usage**

### Running Scripts
```bash
# Run a main script
python scripts/script_name.py

# Run a categorized script
python scripts/categories/category/script_name.py
```

### Finding Scripts
- **Analysis**: Look in `categories/analysis/`
- **Testing**: Look in `categories/testing/`
- **Quality**: Look in `categories/quality/`
- **Monitoring**: Look in `categories/monitoring/`
- **Deployment**: Look in `categories/deployment/`
- **Utilities**: Look in `categories/utilities/`

## 📝 **Maintenance**

- Keep main directory for core, frequently-used scripts
- Add new scripts to appropriate category directories
- Archive one-time or obsolete scripts instead of deleting
- Update this README when adding new categories or reorganizing

## 🔍 **Archive Contents**

- **Consolidation Scripts**: 15 scripts used for module consolidation (completed)
- **Final Cleanup**: 4 scripts used for final project cleanup (completed)
- **Duplicates**: 6+ scripts that were superseded by more comprehensive versions

All archived scripts are preserved and can be restored if needed.
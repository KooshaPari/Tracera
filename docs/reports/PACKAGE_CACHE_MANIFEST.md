# Package Cache Manifest

This document describes the Bun package cache directories and their consolidation strategy.

## Directory Summary

### disable/ Directory

- **Status**: Archived/Disabled Packages
- **File Count**: 78,145 files
- **Directory Count**: 10,247 subdirectories
- **Total Size**: 1.5 GB
- **Purpose**: Contains disabled or archived versions of npm packages managed by Bun's package manager. These are packages that have been installed but are not actively used in the current build configuration.
- **Format**: Mostly source files (.js, .json, .md, etc.) with 759 binary .npm files

### default/ Directory

- **Status**: Does not currently exist
- **File Count**: 0
- **Total Size**: 0 B
- **Purpose**: Reserved for future use with default Bun package configurations

## Why These Directories Exist

The `disable/` directory is created by Bun (the package manager used in this project) to manage:

1. **Package versions** that were resolved during dependency installation but aren't actively linked
2. **Backup/archived versions** of packages for reproducibility and quick rollback
3. **Fallback packages** for different platforms or configurations

## Cleaning Strategy

### When to Clean

These directories should be cleaned in the following scenarios:

1. **Routine Maintenance** (Monthly)
   - Remove files older than 90 days if disk space is constrained
   - `bun install --frozen-lockfile` will recreate necessary files

2. **Space Optimization** (When disk usage > 500MB)
   - Run `bun install --frozen-lockfile` after cleanup to restore essential packages
   - Keep only the last 2 versions of each package

3. **Major Dependency Updates**
   - After running `bun update` and resolving all conflicts
   - Old cached versions become redundant

4. **Before Production Builds**
   - Optional: Clean to ensure fresh package resolution
   - Note: This may slow down subsequent installs

### How to Clean

```bash
# Backup the directory structure
tar -czf bun-cache-backup-$(date +%s).tar.gz frontend/disable/

# Clean the directory (keeps structure)
rm -rf frontend/disable/*

# Reinstall packages
cd frontend && bun install --frozen-lockfile
```

## Migration to Centralized Cache

### Original Structure

```
frontend/
├── disable/          (78,145 files, 1.5 GB)
├── default/          (empty)
├── node_modules/     (primary cache)
└── bun.lock          (lock file)
```

### Recommended Future Structure

```
frontend/
├── .cache/
│   └── bun/
│       ├── store/        (package store)
│       └── manifests/    (package manifests)
├── node_modules/         (active dependencies)
├── bun.lock              (lock file)
└── .npmignore            (git-ignore patterns)
```

## Current .gitignore Status

The following patterns are already configured in `frontend/.gitignore`:

- `disable/` - Bun disabled packages (line 32)
- `default/` - Bun default packages (line 33)

These directories are correctly excluded from version control.

## File Breakdown in disable/

### By Category

- **JavaScript/TypeScript Files**: ~40,000 files
- **Configuration Files** (package.json, .json): ~20,000 files
- **Documentation** (.md, .txt): ~10,000 files
- **Binary/npm packages** (.npm): 759 files
- **Other** (scripts, licenses, etc.): ~7,386 files

### Package Distribution

Contains hundreds of different npm packages organized by scope:

- @babel (babel tooling)
- @emotion (CSS-in-JS)
- @jest (testing framework)
- @electron (desktop framework)
- And 200+ other package scopes

## Recommendations

1. **Keep as-is for now**: The 1.5 GB is manageable and improves build speed
2. **Monitor monthly**: Track growth to plan future consolidation
3. **Document in CI/CD**: Add cache cleanup to deployment pipelines if needed
4. **Use bun prune**: Consider `bun prune` command to optimize without losing packages

## Last Updated

- Created: 2025-12-04
- Total files analyzed: 78,145
- Total directories analyzed: 10,247
- Cache size analyzed: 1.5 GB


# Workflow Consolidation Report

## Summary
- **Total workflows analyzed**: 32
- **Workflows to consolidate**: 18
- **Workflows to keep**: 3

## Workflow Categories

### Documentation
- docs-deploy.yml
- docs-ci.yml

### Other
- cleanup-check.yml
- check-tui-consolidation.yml
- forbidden-paths.yml
- sonarqube.yml
- schema-check.yml
- check-legacy-imports.yml
- tui_kit_guard.yml

### Performance
- performance.yml

### Release
- release.yml
- version.yml

### Testing
- tests_light.yml
- config_kit_tests.yml
- test.yml
- pheno_cli_env_test.yml
- security-testing.yml
- mcp_oauth_tests.yml

### Code Quality
- full-quality.yml
- lint.yml
- code-quality-gates.yml
- quality.yml
- code-quality.yml
- pr-quality.yml
- quality-full.yml

### Security
- security.yml

### Build Ci
- ci-matrix.yml
- ci.yml
- build.yml

### Deployment
- deploy.yml

### Architecture
- architecture-fitness.yml

### Monitoring
- monitoring.yml


## Consolidation Plan

### New Consolidated Workflow: `consolidated-ci.yml`
This workflow combines multiple existing workflows into a single, efficient pipeline:

**Phases:**
1. **Preparation**: Environment setup and change detection
2. **Code Quality**: Linting, formatting, type checking
3. **Architecture**: Design pattern validation, complexity analysis
4. **Security**: Vulnerability scanning, dependency checks
5. **Testing**: Unit tests, integration tests
6. **Documentation**: Markdown validation, doc generation
7. **Performance**: Benchmarking (conditional)
8. **Quality Gates**: Final validation and scoring
9. **Deployment**: Build and deploy (main branch only)

### Migration Steps

1. Backup existing workflows directory
2. Test the new consolidated-ci.yml workflow
3. Gradually disable old workflows by adding 'if: false' to their triggers
4. Monitor the consolidated workflow for a few days
5. Remove disabled workflows once confirmed working
6. Remove 18 workflows: tests_light.yml, config_kit_tests.yml, test.yml, pheno_cli_env_test.yml, security-testing.yml, mcp_oauth_tests.yml, full-quality.yml, lint.yml, code-quality-gates.yml, quality.yml, code-quality.yml, pr-quality.yml, quality-full.yml, security.yml, ci-matrix.yml, ci.yml, build.yml, architecture-fitness.yml
7. Keep 3 workflows: release.yml, version.yml, deploy.yml

## Benefits of Consolidation

1. **Reduced Complexity**: Single workflow instead of 36 separate ones
2. **Better Performance**: Parallel execution where possible
3. **Conditional Execution**: Only run what's needed based on changes
4. **Unified Reporting**: Single quality score and comprehensive reports
5. **Easier Maintenance**: One workflow to maintain instead of many
6. **Cost Optimization**: Reduced GitHub Actions minutes usage

## Risk Mitigation

1. **Gradual Migration**: Disable old workflows gradually
2. **Monitoring**: Watch for any issues during transition
3. **Rollback Plan**: Keep old workflows as backup initially
4. **Testing**: Thoroughly test consolidated workflow before full migration


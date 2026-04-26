# ADR-006: Reconciliation Strategy — Smart Updates for Template Evolution

**Status:** Accepted  
**Date:** 2026-04-04  
**Author:** Phenotype Architecture Team  
**Stakeholders:** Template Program, DevEx, Platform Engineering

---

## Context

The fundamental challenge with project templates is the "generate and abandon" pattern: a template creates a project, but then the project diverges from the template, and there's no clean path to incorporate template updates.

**Current State Analysis:**

| Tool | Update Support | Mechanism | Limitations |
|------|---------------|-----------|-------------|
| Yeoman | ❌ | N/A | Generate once only |
| Cookiecutter | ❌ | N/A | Generate once only |
| copier | ✅ | 3-way merge | Python-only, no contract |
| Helm | ✅ | Upgrade hooks | K8s-specific |
| Terraform | ✅ | State-based | Infra-specific |

**User Stories:**

1. **As a developer**, I want to update my project with the latest template improvements without losing my customizations
2. **As a platform engineer**, I want security patches in base templates to propagate to all projects
3. **As a template maintainer**, I want to evolve templates without breaking existing projects
4. **As an SRE**, I want to know exactly what changed in a template update before applying it

**Key Challenges:**

1. **User modifications vs template changes**: How to preserve intentional user changes while applying template fixes?
2. **Breaking changes**: When a template changes its structure, how to migrate existing projects?
3. **Merge conflicts**: When user and template both modify the same file, how to resolve?
4. **Transparency**: How to show what will change before applying?

---

## Decision

Implement a **three-mode reconciliation strategy** with **three-way merge** as the default mechanism.

### Core Principles

1. **User modifications are sacred** - Never silently overwrite user changes
2. **Template fixes are important** - Provide path to apply security patches and improvements
3. **Transparency is required** - Always show what will change
4. **Automation where safe** - Apply safe changes automatically, flag conflicts for review

### Reconciliation Modes

#### Mode 1: Smart (Default)

```yaml
smart:
  description: "Apply safe updates automatically, flag conflicts for manual review"
  create_missing: true           # Create new files from template
  update_template_owned_if_unchanged: true  # Update files user hasn't modified
  create_conflict_sidecar: true  # Create .template.new files for conflicts
  sidecar_suffix: .template.new
  notify: [console, log, pr_comment]
```

**Algorithm:**

```python
def reconcile_smart(project, original_template, new_template):
    for path in new_template.owned_paths:
        original_content = original_template.read(path)
        current_content = project.read(path)
        new_content = new_template.read(path)

        if current_content == original_content:
            # File unchanged since scaffold - safe to update
            project.write(path, new_content)
            log.info(f"Updated {path} (unchanged since scaffold)")

        elif current_content == new_content:
            # Already up to date
            log.debug(f"Skipped {path} (already current)")

        else:
            # User modified the file - create sidecar
            sidecar_path = f"{path}.template.new"
            project.write(sidecar_path, new_content)
            log.warning(f"Conflict in {path} - created {sidecar_path}")
            conflicts.append(path)

    return ReconcileResult(
        updated=updated,
        created=created,
        conflicts=conflicts
    )
```

#### Mode 2: Overwrite

```yaml
overwrite:
  description: "Forcefully apply template, replacing user modifications"
  create_missing: true
  replace_template_owned: true   # ⚠️ Replaces user modifications
  backup_modified: true          # Backup to .template.backup
  backup_suffix: .template.backup
  require_confirmation: true     # Interactive prompt or --force flag
```

**Use Cases:**
- Recovery from corrupted state
- Fresh start desired
- Non-interactive CI/CD pipelines with approved changes

**Safety:**
- Always backs up modified files
- Requires explicit confirmation or force flag

#### Mode 3: Skip (Report Only)

```yaml
skip:
  description: "Report what would change without applying"
  report_only: true
  output_format: [json, markdown, console]
  include_diffs: true
  exit_code:
    changes_detected: 1
    no_changes: 0
    error: 2
```

**Use Cases:**
- CI/CD gates (fail if updates available but not applied)
- Pre-update review
- Audit and compliance

### Three-Way Merge Foundation

The smart mode is built on three-way merge:

```
Base (Original Template)     Current (Project)           New (Template Update)
        ↓                           ↓                            ↓
   Original file              User-modified file           Template-fixed file
        ↓                           ↓                            ↓
        └──────────┬────────────────┘                            │
                   ↓                                             │
              Compare for changes                               │
                   ↓                                             │
        Unchanged ──→ Update automatically                       │
        Modified ──→ Create sidecar for manual merge ◄───────────┘
```

### State Tracking

To enable reconciliation, we must track original template state:

```json
// .template.lock (generated at scaffold time)
{
  "version": "1",
  "layers": [
    {
      "name": "template-commons",
      "version": "1.2.3",
      "resolved_version": "1.2.3",
      "source": "git@github.com:Phenotype/template-commons.git",
      "files": {
        ".github/workflows/ci.yml": {
          "hash": "sha256:abc123...",
          "template_hash": "sha256:def456..."
        },
        "SECURITY.md": {
          "hash": "sha256:ghi789...",
          "template_hash": "sha256:jkl012..."
        }
      }
    }
  ],
  "variables": {
    "PROJECT_NAME": "my-service",
    "AUTHOR": "Team Alpha"
  },
  "scaffolded_at": "2026-04-04T10:30:00Z",
  "last_reconciled_at": null
}
```

**File Hashes:**
- `hash`: SHA-256 of current file content (for detecting user changes)
- `template_hash`: SHA-256 of template file at scaffold time (for detecting template changes)

### Migration Support

For breaking changes (major version bumps), support migration scripts:

```yaml
# In template.manifest.json
migrations:
  "2.0.0":
    from: ">=1.0.0,<2.0.0"
    script: migrations/v1-to-v2.sh
    description: "Migrate from v1 to v2 structure"
    automatic: false  # Require manual review
```

```bash
#!/bin/bash
# migrations/v1-to-v2.sh
# Migration script for v1 to v2 breaking changes

echo "Migrating from v1 to v2..."

# Move old config location to new
if [ -f ".old-config.yml" ]; then
    mv .old-config.yml config/app.yml
    echo "Migrated .old-config.yml → config/app.yml"
fi

# Update import paths
find src/ -name "*.go" -exec sed -i 's/oldpackage/newpackage/g' {} \;

echo "Migration complete. Please review changes."
```

### Pre-Update Hooks

Allow templates to run checks before reconciliation:

```yaml
# reconcile.rules.yaml
pre_update_hooks:
  - name: "check_uncommitted_changes"
    script: scripts/check-git-clean.sh
    fail_on_error: true
    description: "Ensure git working directory is clean"

  - name: "run_tests"
    script: scripts/test.sh
    fail_on_error: false  # Warn but continue
    description: "Run existing test suite as baseline"
```

### Post-Update Hooks

Run after successful reconciliation:

```yaml
post_update_hooks:
  - name: "update_dependencies"
    script: scripts/update-deps.sh
    description: "Update project dependencies"

  - name: "regenerate_code"
    script: scripts/generate.sh
    description: "Regenerate generated code"

  - name: "commit_template_update"
    script: scripts/commit-update.sh
    description: "Commit template update with standard message"
```

---

## Consequences

### Positive

1. **Continuous Template Evolution**: Templates can improve over time; projects benefit
2. **Security Patch Propagation**: Critical fixes flow to all projects
3. **Developer Agency**: Users control when and how to apply updates
4. **Conflict Visibility**: Clear indication of what needs manual attention
5. **Audit Trail**: `.template.lock` documents template provenance
6. **CI/CD Integration**: Can gate on outdated templates, auto-apply safe updates

### Negative

1. **Storage Overhead**: `.template.lock` and potential sidecars
2. **Complexity**: Three-way merge logic is non-trivial
3. **Learning Curve**: Users must understand reconciliation modes
4. **Merge Effort**: Conflicts require manual resolution

### Mitigations

| Concern | Mitigation |
|---------|------------|
| Storage | Sidecars are temporary; can be deleted after merge |
| Complexity | Well-tested library code; users don't implement merge |
| Learning | Clear documentation, sensible defaults (smart mode) |
| Merge effort | Minimize conflicts by template design (stable interfaces) |

---

## Alternatives Considered

### Alternative 1: Git-Based Rebase

**Approach:** Maintain template as git history; projects rebase onto new template commits.

**Rejected:**
- Requires template projects to be git repos
- Complex rebase conflict resolution
- Not all projects use git
- Couples to git implementation

### Alternative 2: Patch-Based Updates

**Approach:** Generate and apply patches between template versions.

**Rejected:**
- Patches fail if user modified same lines
- No context for manual resolution
- Hard to review before applying
- Binary files problematic

### Alternative 3: Event Sourcing

**Approach:** Record all template and user changes as events; replay to reconstruct.

**Rejected:**
- Overly complex for this use case
- Storage overhead
- Harder to understand and debug

### Alternative 4: No Updates

**Approach:** Templates are generate-once; updates manual.

**Rejected:**
- Security patches don't propagate
- Platform improvements lost
- High maintenance burden on users
- Doesn't meet requirements

---

## Implementation Plan

### Phase 1: Smart Mode Foundation

- [x] Define reconciliation schema in `reconcile.rules.yaml`
- [ ] Implement three-way merge library
- [ ] Implement `.template.lock` generation
- [ ] Implement smart reconciliation algorithm
- [ ] Add sidecar conflict creation

### Phase 2: Tooling Integration

- [ ] `template-cli update` command
- [ ] `template-cli update --dry-run` for skip mode
- [ ] `template-cli update --force` for overwrite mode
- [ ] Interactive conflict resolution TUI

### Phase 3: Migration Support

- [ ] Migration script execution framework
- [ ] Pre/post update hooks
- [ ] Breaking change detection and warnings
- [ ] Automated migration where safe

### Phase 4: CI/CD Integration

- [ ] GitHub Action for template update check
- [ ] PR automation for safe updates
- [ ] Outdated template detection in CI
- [ ] Compliance reporting

---

## Success Metrics

1. **Update Adoption Rate**: % of projects updated within 30 days of template release
2. **Conflict Rate**: % of updates requiring manual conflict resolution
3. **Time to Update**: Median time from template release to project update
4. **User Satisfaction**: Developer experience surveys
5. **Security Patch Propagation**: Time from security fix to project adoption

**Targets:**
- Update adoption rate: >70% within 30 days
- Conflict rate: <20% of file updates
- Time to update: <1 hour for safe updates
- Security patches: 100% of eligible projects within 7 days

---

## References

1. [SOTA.md](./SOTA.md) - Research on template update mechanisms
2. copier documentation on updates: https://copier.readthedocs.io/
3. Three-way merge algorithm: "The Diff Algorithm" by Eugene Myers
4. Git three-way merge: https://git-scm.com/docs/merge-strategies
5. [SPEC.md](../SPEC.md) - Full specification

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-04 | Smart mode as default | Balances automation with safety |
| 2026-04-04 | Three-way merge foundation | Industry standard, well-understood |
| 2026-04-04 | Sidecar pattern for conflicts | Clear visibility, non-destructive |
| 2026-04-04 | `.template.lock` for state | Git-friendly, human-readable, sufficient |
| 2026-04-04 | Migration scripts for breaking changes | Clean path for evolution |

---

*End of ADR-006*

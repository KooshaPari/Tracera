# CLI Optimization Rollback Plan

## Overview

This document provides a comprehensive rollback strategy for CLI optimizations including lazy loading, caching, and performance enhancements.

## Feature Flags

### Environment Variables

Control CLI optimizations via environment variables:

```bash
# Disable all CLI optimizations
export TRACERTM_CLI_OPTIMIZATIONS=false

# Disable specific optimizations
export TRACERTM_CLI_LAZY_LOADING=false
export TRACERTM_CLI_CACHING=false
export TRACERTM_CLI_PERFORMANCE_MONITORING=false
```

### Configuration File

Add to `~/.tracertm/config.yaml`:

```yaml
cli:
  optimizations:
    enabled: false  # Master switch
    lazy_loading: false
    caching: false
    monitoring: false
```

## Rollback Procedures

### Level 1: Disable Optimizations via Environment Variables

**Use when:** Minor performance issues, testing if optimization is causing problems

**Steps:**

1. Set environment variable:
   ```bash
   export TRACERTM_CLI_OPTIMIZATIONS=false
   ```

2. Verify rollback:
   ```bash
   rtm --version  # Should work without optimizations
   ```

3. Test affected commands:
   ```bash
   rtm config --help
   rtm project --help
   ```

**Rollback time:** Immediate (no code changes)

**Risk:** Low

---

### Level 2: Disable Specific Optimization Features

**Use when:** One optimization feature is problematic

**Steps for Lazy Loading:**

1. Create feature flag file:
   ```bash
   echo "LAZY_LOADING_ENABLED=false" >> ~/.tracertm/feature_flags
   ```

2. Modify `src/tracertm/cli/performance.py`:
   ```python
   def should_use_lazy_loading() -> bool:
       """Check if lazy loading should be used."""
       # Check environment variable
       if os.getenv('TRACERTM_CLI_LAZY_LOADING', 'true').lower() == 'false':
           return False

       # Check config file
       # ... existing config check code ...

       return True
   ```

3. Update `src/tracertm/cli/app.py`:
   ```python
   # Conditional lazy loading
   from tracertm.cli.performance import should_use_lazy_loading

   if should_use_lazy_loading():
       # Use lazy loading
       from tracertm.cli.performance import get_loader
       loader = get_loader()
   else:
       # Direct imports
       from tracertm.cli.commands import config, project, item, link
   ```

**Rollback time:** 5-10 minutes

**Risk:** Low-Medium

---

### Level 3: Revert to Previous Code Version

**Use when:** Multiple optimization issues, need stable version

**Steps:**

1. Identify last stable commit before optimizations:
   ```bash
   git log --oneline --grep="CLI optimization" -n 5
   ```

2. Create rollback branch:
   ```bash
   git checkout -b rollback-cli-optimizations
   git revert <commit-hash-range>
   ```

3. Test rolled-back version:
   ```bash
   pytest tests/performance/test_cli_startup.py
   pytest tests/integration/test_cli_integration.py
   ```

4. Deploy if tests pass:
   ```bash
   git push origin rollback-cli-optimizations
   ```

**Rollback time:** 30-60 minutes

**Risk:** Medium

---

---

## Verification Checklist

After any rollback, verify:

- [ ] `rtm --version` works
- [ ] `rtm --help` shows all commands
- [ ] `rtm config --help` loads successfully
- [ ] `rtm project list` executes (with test project)
- [ ] No import errors in logs
- [ ] Performance acceptable (may be slower)
- [ ] All tests pass: `pytest tests/unit/cli/ tests/integration/test_cli_integration.py`

## Monitoring & Detection

### Early Warning Signs

Monitor these metrics to detect issues early:

1. **Startup Time Regression**
   ```bash
   # Automated check
   time rtm --version
   # Should be < 500ms
   ```

2. **Memory Usage Spike**
   ```bash
   # Monitor RSS memory
   /usr/bin/time -l rtm --version 2>&1 | grep "maximum resident"
   ```

3. **Command Failure Rate**
   ```bash
   # Check error logs
   tail -f ~/.tracertm/logs/cli_errors.log
   ```

4. **User Reports**
   - Slow startup complaints
   - Import errors
   - Command hangs

### Automated Monitoring

Set up automated checks:

```bash
#!/bin/bash
# cli_health_check.sh

# Startup time check
STARTUP_TIME=$(time -p rtm --version 2>&1 | grep real | awk '{print $2}')
if (( $(echo "$STARTUP_TIME > 0.5" | bc -l) )); then
    echo "WARNING: Startup time ${STARTUP_TIME}s exceeds 500ms threshold"
    # Optionally trigger rollback
fi

# Command success check
rtm config --help > /dev/null 2>&1 || echo "ERROR: config command failed"
rtm project --help > /dev/null 2>&1 || echo "ERROR: project command failed"
```

Run via cron:
```cron
*/15 * * * * /path/to/cli_health_check.sh
```

---

## Communication Plan

### Internal Team Communication

**If rollback initiated:**

1. **Immediate notification** (Slack/Email):
   ```
   ALERT: CLI optimizations rolled back
   Reason: [specific issue]
   Rollback level: [1-4]
   Impact: [performance may be slower, but stable]
   ETA for fix: [timeline]
   ```

2. **Status updates** every 4 hours until resolved

3. **Post-mortem** after issue resolved

### User Communication

**Release notes addendum:**

```markdown
## Rollback Notice - CLI Optimizations

We have temporarily rolled back CLI performance optimizations due to [issue].

**Impact:**
- CLI startup may be slightly slower
- All functionality remains available
- No data loss or corruption

**Timeline:**
- Optimizations will be re-enabled in version X.Y.Z
- Expected: [date]

**Workaround:**
- None needed - CLI works normally
```

---

## Testing the Rollback

### Pre-Production Testing

Before rollback in production:

```bash
# 1. Set up test environment
export TRACERTM_CLI_OPTIMIZATIONS=false

# 2. Run full test suite
pytest tests/unit/cli/ -v
pytest tests/integration/test_cli_integration.py -v
pytest tests/performance/test_cli_startup.py -v

# 3. Manual smoke tests
rtm --version
rtm config list
rtm project list
rtm item list --type feature

# 4. Performance baseline
pytest tests/performance/test_cli_benchmarks.py --benchmark-only

# 5. Compare against optimized version
# Document any performance degradation
```

### Production Rollback Test

```bash
# On staging/canary environment:
# (Use Level 3 code revert if needed)

# Monitor for 24 hours:
# - Error rates
# - User complaints
# - Performance metrics

# If successful, proceed to production
```

---

## Recovery Plan

### After Issue Resolved

1. **Fix identified issue** in development

2. **Add regression test**:
   ```python
   def test_regression_issue_xyz():
       """Ensure issue XYZ doesn't recur."""
       # Test for specific issue
   ```

3. **Run extended test suite**:
   ```bash
   pytest tests/ -v --cov=tracertm.cli
   ```

4. **Gradual rollout**:
   - Enable for 10% of users
   - Monitor for 48 hours
   - Increase to 50%
   - Monitor for 24 hours
   - Full rollout

5. **Document lessons learned**

---

## Rollback Decision Matrix

| Symptom | Severity | Recommended Action | Rollback Level |
|---------|----------|-------------------|----------------|
| Startup > 1s | Low | Disable caching | Level 1 |
| Import errors | Medium | Disable lazy loading | Level 2 |
| Command failures | High | Code revert | Level 3 |
| Data corruption | Critical | Code revert + hotfix | Level 3 |
| Memory leak | Medium | Disable caching | Level 1-2 |
| Crash on startup | Critical | Code revert | Level 3 |

---

## Contacts

**Escalation Path:**

1. **Level 1 (Dev Team)**: Disable via env vars
2. **Level 2 (Tech Lead)**: Code-level disable
3. **Level 3 (Engineering Manager)**: Revert commits / production rollback

**On-Call Rotation:**
- Primary: [Name/Contact]
- Secondary: [Name/Contact]
- Escalation: [Name/Contact]

---

## Appendix: Code Locations

### Key Files for Rollback

1. **Main CLI App**: `src/tracertm/cli/app.py`
2. **Performance Module**: `src/tracertm/cli/performance.py`
3. **Feature Flags**: `src/tracertm/cli/feature_flags.py` (if implemented)
4. **Config Manager**: `src/tracertm/config/manager.py`

### Environment Variable Reference

| Variable | Default | Purpose |
|----------|---------|---------|
| `TRACERTM_CLI_OPTIMIZATIONS` | `true` | Master optimization switch |
| `TRACERTM_CLI_LAZY_LOADING` | `true` | Enable lazy loading |
| `TRACERTM_CLI_CACHING` | `true` | Enable command caching |
| `TRACERTM_CLI_PERFORMANCE_MONITORING` | `false` | Enable perf monitoring |

### Configuration File Paths

- User config: `~/.tracertm/config.yaml`
- System config: `/etc/tracertm/config.yaml`
- Project config: `./.tracertm/config.yaml`

Priority: Project > User > System > Environment > Defaults

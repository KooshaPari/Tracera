# Item Specification Service - Quick Start

## Installation

The service is already integrated into the TraceRTM codebase. No additional dependencies required.

```python
from tracertm.services.item_spec_service import RequirementSpecService
from tracertm.repositories.requirement_quality_repository import RequirementQualityRepository
```

## 5-Minute Overview

### What Does It Do?

1. **Analyzes requirement quality** - Detects vague language, missing criteria, weak verbs
2. **Calculates impact** - Shows what breaks if you change something
3. **Tracks volatility** - Identifies unstable, frequently-changing requirements
4. **Calculates priority** - WSJF scoring for work prioritization
5. **Detects flaky tests** - Identifies unreliable tests

### Key Metrics

| Metric | Range | Meaning |
|--------|-------|---------|
| Quality Score | 0-1 | Requirement clarity (0.85+ is good) |
| CPI | 0-1 | Change risk (0.3+ requires review) |
| Volatility | 0-1 | Change frequency (0.5+ is high) |
| WSJF | 0-1 | Priority (1.0 is highest) |
| Flakiness | 0-1 | Test reliability (0.2+ is problematic) |

## Common Tasks

### Task 1: Analyze a Single Requirement

```python
from tracertm.services.item_spec_service import RequirementSpecService
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Setup (in your async context)
service = RequirementSpecService(session)

# Analyze
spec = await service.create_spec(item_id="req-123")

print(f"Quality: {spec.overall_quality_score:.0%}")
print(f"Issues: {len(spec.quality_issues)}")
print(f"Impact: {spec.change_propagation_index:.2f}")
```

### Task 2: Find High-Risk Requirements

```python
quality_repo = RequirementQualityRepository(session)

# Get high-impact items
risky = await quality_repo.list_high_impact(
    project_id="proj-456",
    threshold=0.3,  # Impact > 30%
    limit=10
)

for spec in risky:
    print(f"{spec.item_id}: CPI={spec.change_propagation_index:.2f}")
```

### Task 3: Monitor Quality Trend

```python
# Get project health
report = await service.get_health_report(project_id="proj-456")

print(f"Requirements: {report['total_requirements']}")
print(f"Avg Quality: {report['average_quality_score']:.0%}")
print(f"Verified: {report['verification_rate']:.0%}")
print(f"Health: {report['health_score']:.0%}")
```

### Task 4: Identify Unstable Requirements

```python
# Get volatile items
unstable = await quality_repo.list_high_volatility(
    project_id="proj-456",
    threshold=0.5,  # High volatility
    limit=10
)

for spec in unstable:
    print(f"{spec.item_id}: Changed {spec.change_count}x, "
          f"Volatility={spec.volatility_index:.2f}")
```

### Task 5: Prioritize Work with WSJF

```python
# Get high-priority items
priority_order = await quality_repo.list_by_wsjf_priority(
    project_id="proj-456",
    limit=20  # Top 20
)

for i, spec in enumerate(priority_order, 1):
    print(f"{i}. {spec.item_id} (Score: {spec.wsjf_score:.2f})")
```

### Task 6: Track Changes and Volatility

```python
# Record a change
spec = await service.record_change(
    item_id="req-123",
    changed_by="user@company.com",
    change_type="modified",
    summary="Updated acceptance criteria",
    previous_values={"description": "old text"},
    new_values={"description": "new text"}
)

print(f"Change count: {spec.change_count}")
print(f"Volatility: {spec.volatility_index:.2f}")
```

### Task 7: Verify Requirements

```python
# Mark as verified with evidence
spec = await service.verify_requirement(
    item_id="req-123",
    verified_by="qa@company.com",
    evidence_type="test",
    evidence_reference="test-suite-456",
    description="Passed automated test suite"
)

print(f"Verified: {spec.is_verified}")
print(f"Evidence count: {len(spec.verification_evidence)}")
```

### Task 8: Analyze Quality Issues

```python
# Create spec to get issues
spec = await service.create_spec(item_id="req-456")

if spec.quality_issues:
    print("Quality Issues Found:")
    for issue in spec.quality_issues:
        print(f"  - {issue['dimension']}: {issue['message']}")
        print(f"    Fix: {issue['suggestion']}")
```

## Quality Issue Reference

### Unambiguity Issues

**Problem**: Vague language like "appropriate", "efficient", "good"

**Fix**: Use specific metrics
```
❌ Bad: "The system should be efficient"
✅ Good: "The system shall respond within 500ms"
```

### Completeness Issues

**Problem**: TBD, TODO, FIXME markers

**Fix**: Complete the specification
```
❌ Bad: "User authentication. TBD: Password rules"
✅ Good: "User authentication with 8+ character passwords"
```

### Verifiability Issues

**Problem**: Universal quantifiers (all, never, any)

**Fix**: Add testable criteria
```
❌ Bad: "The system never fails"
✅ Good: "The system shall recover from errors within 30 seconds"
```

### Necessity Issues

**Problem**: Weak requirement verbs (may, could, should)

**Fix**: Use strong verbs
```
❌ Bad: "The system should authenticate users"
✅ Good: "The system shall authenticate users"
```

### Singularity Issues

**Problem**: Multiple requirements in one statement

**Fix**: Split into atomic statements
```
❌ Bad: "The system shall authenticate and encrypt and audit"
✅ Good:
  1. "The system shall authenticate users"
  2. "The system shall encrypt passwords"
  3. "The system shall audit access"
```

## Scoring Guide

### Quality Score Interpretation

- **0.85-1.00** 🟢 Excellent - Ready for development
- **0.70-0.85** 🟡 Good - Minor cleanup needed
- **0.50-0.70** 🟠 Fair - Significant issues
- **0.30-0.50** 🔴 Poor - Rework required
- **0.00-0.30** 🔴 Critical - Unusable

### Impact Index Interpretation

- **0.0-0.1** 🟢 Low - Safe to change
- **0.1-0.3** 🟡 Medium - Review recommended
- **0.3-0.5** 🟠 High - Extensive testing needed
- **0.5+** 🔴 Critical - Requires major redesign

### Volatility Interpretation

- **0.0-0.05** 🟢 Stable - Reliable specification
- **0.05-0.2** 🟡 Low - Gradually improving
- **0.2-0.4** 🟠 Medium - Needs stabilization
- **0.4-0.7** 🔴 High - Frequently changing
- **0.7+** 🔴 Critical - Requires stabilization

## Common Workflows

### Workflow: Pre-Development Requirement Check

```python
service = RequirementSpecService(session)

# 1. Analyze quality
spec = await service.create_spec(item_id="req-123")

# 2. Check if ready
if spec.overall_quality_score < 0.70:
    print("Quality too low. Fixing issues first:")
    for issue in spec.quality_issues:
        print(f"  - {issue['suggestion']}")
    return False

# 3. Assess impact
impact = await service.impact_analyzer.calculate_impact(
    "req-123", "proj-456"
)

if impact["high_impact"]:
    print("High impact change. Requires stakeholder review.")
    await notify_stakeholders("req-123", impact)

# Ready to proceed
return True
```

### Workflow: Sprint Planning with WSJF

```python
service = RequirementSpecService(session)
quality_repo = RequirementQualityRepository(session)

# 1. Calculate WSJF for candidates
candidates = await item_repo.list_by_status("backlog", limit=50)

for item in candidates:
    spec = await service.create_spec(item.id)

    await service.calculate_wsjf(
        item_id=item.id,
        business_value=estimate_business_value(item),
        time_sensitivity=estimate_time_sensitivity(item),
        risk_reduction=estimate_risk_reduction(item),
        job_size=estimate_job_size(item)
    )

# 2. Get prioritized list
priority_items = await quality_repo.list_by_wsjf_priority(
    "proj-456", limit=10
)

# 3. Add to sprint
for item in priority_items:
    sprint.add_item(item.item_id)
```

### Workflow: Quality Improvement Campaign

```python
# 1. Get quality report
report = await service.get_health_report("proj-456")

print(f"Average Quality: {report['average_quality_score']:.0%}")
print(f"Issues: {report['issues_by_severity']}")

# 2. Find items to fix
low_quality = await quality_repo.list_by_quality_score(
    "proj-456",
    min_score=0,
    max_score=0.6,  # Low quality
    limit=20
)

# 3. Create tasks
for spec in low_quality:
    task = create_quality_improvement_task(
        item_id=spec.item_id,
        issues=spec.quality_issues,
        priority="high"
    )

# 4. Track progress
await session.commit()
print(f"Created {len(low_quality)} improvement tasks")
```

## API Reference - Core Methods

### RequirementQualityAnalyzer

```python
analyzer = RequirementQualityAnalyzer()

# Analyze single requirement
result = analyzer.analyze(
    text="Requirement description",
    title="Requirement title"
)
# Returns: {"scores", "issues", "overall_score", ...}
```

### RequirementSpecService

```python
service = RequirementSpecService(session)

# Create spec with analysis
spec = await service.create_spec(item_id="req-123")

# Refresh analysis
spec = await service.refresh_quality_analysis("req-123")

# Refresh impact
spec = await service.refresh_impact_analysis("req-123")

# Record change
spec = await service.record_change(
    item_id="req-123",
    changed_by="user",
    change_type="modified",
    summary="Changed description"
)

# Calculate WSJF
spec = await service.calculate_wsjf(
    item_id="req-123",
    business_value=0.8,
    time_sensitivity=0.7,
    risk_reduction=0.6,
    job_size=0.3
)

# Verify requirement
spec = await service.verify_requirement(
    item_id="req-123",
    verified_by="qa",
    evidence_type="test",
    evidence_reference="test-123",
    description="Verified by tests"
)

# Get health report
report = await service.get_health_report("proj-456")
```

### RequirementQualityRepository

```python
repo = RequirementQualityRepository(session)

# Get by ID
spec = await repo.get_by_id("spec-123")

# Get by item
spec = await repo.get_by_item_id("item-123")

# List
specs = await repo.list_by_project("proj-456", limit=100)

# Filter by quality
specs = await repo.list_by_quality_score("proj-456", min_score=0.7)

# Find volatile items
volatile = await repo.list_high_volatility("proj-456", threshold=0.5)

# Find high-impact items
impactful = await repo.list_high_impact("proj-456", threshold=0.3)

# Get unverified
unverified = await repo.list_unverified("proj-456")

# Get by priority
priority = await repo.list_by_wsjf_priority("proj-456", limit=10)

# Get stats
stats = await repo.get_stats("proj-456")
```

## Troubleshooting

### "Item not found" Error

```python
# Ensure item exists first
item = await item_repo.get_by_id(item_id)
if not item:
    raise ValueError(f"Item {item_id} not found")

# Then create spec
spec = await service.create_spec(item_id)
```

### "RequirementQuality not found" Error

```python
# Some operations expect existing spec
# Use get_by_item_id to check first
spec = await quality_repo.get_by_item_id(item_id)
if not spec:
    # Create it first
    spec = await service.create_spec(item_id)
```

### Low Quality Scores

```python
# Get detailed issues
spec = await service.refresh_quality_analysis(item_id)

print("Issues to fix:")
for issue in spec.quality_issues:
    print(f"  - {issue['dimension']}")
    print(f"    Suggestion: {issue['suggestion']}")
```

## Performance Tips

1. **Batch Operations**: Analyze multiple items in a loop
2. **Cache Results**: Reuse spec results if item unchanged
3. **Refresh Selectively**: Only refresh when data changes
4. **Use Queries**: Use repository filters instead of fetching all
5. **Limit Results**: Always specify limits for large result sets

## Next Steps

1. Read `/docs/ITEM_SPEC_SERVICE.md` for comprehensive guide
2. Review test cases in `/tests/` for usage examples
3. Run tests: `pytest tests/unit/services/test_item_spec_service.py -v`
4. Integrate into your workflow
5. Monitor health reports weekly

## Support

For issues or questions:
1. Check the comprehensive guide: `ITEM_SPEC_SERVICE.md`
2. Review test examples in `test_item_spec_service.py`
3. Check inline code documentation and docstrings
4. Review error messages - they include helpful context

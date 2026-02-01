# Item Specification Service

## Overview

The Item Specification Service provides comprehensive business logic for analyzing and managing enhanced item specifications across the TraceRTM system. It implements industry-standard quality scoring, impact analysis, volatility tracking, and AI-ready infrastructure for future enhancements.

## Key Components

### 1. RequirementQualityAnalyzer

Analyzes requirement text using ISO 29148 quality standards and INCOSE patterns.

#### Quality Dimensions

- **Unambiguity** (25% weight): Absence of vague, imprecise language
- **Completeness** (20% weight): All necessary information is present
- **Verifiability** (25% weight): Requirements can be objectively tested
- **Necessity** (15% weight): Requirements use strong, mandatory language
- **Singularity** (15% weight): One atomic requirement per statement

#### Usage Example

```python
from tracertm.services.item_spec_service import RequirementQualityAnalyzer

analyzer = RequirementQualityAnalyzer()

result = analyzer.analyze(
    text="The system shall authenticate users within 2 seconds",
    title="User Login"
)

print(result["overall_score"])  # 0.85
print(result["quality_issues"])  # []
print(result["ambiguous_terms"])  # []
```

#### Quality Issue Detection

The analyzer automatically detects:

- **Ambiguous Terms**: appropriate, adequate, efficient, good, nice, etc.
- **Incomplete Markers**: TBD, TODO, FIXME, ?
- **Weak Verbs**: may, might, could, should, can, would
- **Absolute Quantifiers**: all, always, never, any
- **Multiple Requirements**: Detects "and/or" conjunctions

### 2. ImpactAnalyzer

Calculates change propagation index (CPI) and impact metrics.

#### Change Propagation Index (CPI)

```
CPI = (direct_downstream + 0.5 × indirect_downstream) / total_items
```

Normalized to 0-1 scale where:
- **0.0-0.1**: Low impact (Safe to change)
- **0.1-0.3**: Medium impact (Requires review)
- **0.3-0.5**: High impact (Extensive testing needed)
- **0.5+**: Critical impact (Major refactor/redesign)

#### Impact Metrics Provided

- `change_propagation_index`: Normalized impact score
- `downstream_count`: Total affected items (direct + indirect)
- `upstream_count`: Dependent items
- `direct_downstream`: Items directly affected
- `indirect_downstream`: Items affected indirectly (2 levels)
- `impact_breadth`: Unique items affected
- `impact_assessment`: Risk assessment dictionary

#### Usage Example

```python
from tracertm.services.item_spec_service import ImpactAnalyzer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

analyzer = ImpactAnalyzer(session)

impact = await analyzer.calculate_impact(
    item_id="req-123",
    project_id="proj-456"
)

if impact["impact_assessment"]["high_impact"]:
    print(f"Warning: CPI = {impact['change_propagation_index']:.2f}")
    print(f"Affects {impact['downstream_count']} items")
```

### 3. VolatilityTracker

Tracks requirement volatility index (RVI) to identify unstable specifications.

#### Requirements Volatility Index (RVI)

```
RVI = (change_frequency × recency_weight) / days_since_creation
```

Categorization:
- **Stable** (0.0-0.05): <5% change rate
- **Low** (0.05-0.2): Gradually changing
- **Medium** (0.2-0.4): Moderately volatile
- **High** (0.4-0.7): Frequently changing
- **Critical** (0.7+): Unstable, needs attention

#### Usage Example

```python
volatility = tracker.calculate_volatility(
    change_count=15,
    days_since_creation=30,
    change_history=recent_changes
)

category = tracker.categorize_volatility(volatility)
# Returns: "high" if volatility > 0.4
```

### 4. WSJFCalculator

Calculates WSJF (Weighted Shortest Job First) priority.

#### WSJF Formula

```
WSJF = (BV × 0.4 + TS × 0.3 + RR × 0.3) / JS

Where:
- BV = Business Value (0-1)
- TS = Time Sensitivity (0-1)
- RR = Risk Reduction (0-1)
- JS = Job Size / Effort (0-1)
```

Higher scores indicate higher priority.

#### Usage Example

```python
calculator = WSJFCalculator()

score = calculator.calculate_wsjf(
    business_value=0.9,      # Critical business need
    time_sensitivity=0.8,    # Time-sensitive
    risk_reduction=0.6,      # Reduces risk
    job_size=0.3             # Relatively small effort
)
# score = 2.33 (normalized to 1.0) = HIGH PRIORITY
```

### 5. TestSpecFlakinessDector

Detects test flakiness using statistical analysis.

#### Flakiness Detection

- **Pass Rate Analysis**: Failure rate < 95% with high run count
- **Intermittent Failures**: Detects pass/fail alternation patterns
- **Environment Sensitivity**: Identifies tests failing in different ways
- **Error Variance**: Different errors indicate environment issues

#### Categorization

- **Stable** (0.0-0.05): Reliable test
- **Low** (0.05-0.2): Minor flakiness
- **Medium** (0.2-0.4): Moderate flakiness
- **High** (0.4-0.7): Frequently unreliable
- **Critical** (0.7+): Should be quarantined

#### Usage Example

```python
detector = TestSpecFlakinessDector()

score = detector.calculate_flakiness_score(
    pass_count=95,
    fail_count=5,
    total_runs=100,
    recent_failures=[...]
)

level = detector.categorize_flakiness(score)
```

### 6. RequirementSpecService

High-level service orchestrating all analysis and tracking.

#### Key Methods

**Creating Specs with Analysis**

```python
service = RequirementSpecService(session)

spec = await service.create_spec(
    item_id="req-123",
    business_value=0.8,
    time_sensitivity=0.7,
    risk_reduction=0.6,
    job_size=0.4
)

# Returns RequirementQuality with:
# - Quality analysis complete
# - Impact metrics calculated
# - WSJF score computed
```

**Refreshing Analysis**

```python
# Re-analyze quality after item updates
spec = await service.refresh_quality_analysis(item_id="req-123")

# Re-calculate impact after dependency changes
spec = await service.refresh_impact_analysis(item_id="req-123")
```

**Tracking Changes**

```python
spec = await service.record_change(
    item_id="req-123",
    changed_by="user@example.com",
    change_type="modified",
    summary="Updated acceptance criteria",
    previous_values={"description": "old desc"},
    new_values={"description": "new desc"}
)

# Returns updated spec with:
# - Change count incremented
# - Volatility index recalculated
# - Change history updated (last 100 retained)
```

**Verification**

```python
spec = await service.verify_requirement(
    item_id="req-123",
    verified_by="qa-team",
    evidence_type="test",
    evidence_reference="test-suite-456",
    description="Verified by automated test suite"
)

# Returns spec with is_verified=True and evidence recorded
```

**WSJF Calculation**

```python
spec = await service.calculate_wsjf(
    item_id="req-123",
    business_value=0.9,
    time_sensitivity=0.8,
    risk_reduction=0.7,
    job_size=0.2
)
```

**Health Reporting**

```python
report = await service.get_health_report(project_id="proj-456")

# Returns:
# {
#     "total_requirements": 250,
#     "quality_issues_count": 12,
#     "high_volatility_count": 8,
#     "high_impact_count": 15,
#     "unverified_count": 45,
#     "average_quality_score": 0.78,
#     "average_volatility": 0.12,
#     "average_impact_index": 0.18,
#     "verification_rate": 0.82,
#     "health_score": 0.75,
#     "issues_by_severity": {"error": 3, "warning": 9, "info": 0}
# }
```

## Database Model

The `RequirementQuality` model persists all analysis results with the following key fields:

```python
class RequirementQuality(Base, TimestampMixin):
    # Identifiers
    id: str (UUID)
    item_id: str (Foreign Key to Item)
    project_id: str

    # Quality Analysis
    quality_scores: dict[str, float]  # dimension -> score
    overall_quality_score: float (0-1)
    quality_issues: list[dict]

    # Impact Metrics
    change_propagation_index: float (0-1)
    downstream_impact_count: int
    upstream_dependency_count: int
    impact_assessment: dict

    # Volatility Tracking
    change_count: int
    volatility_index: float (0-1)
    change_history: list[dict]  # Last 100 changes
    last_changed_at: datetime

    # Prioritization
    wsjf_score: float | None
    wsjf_components: dict[str, float]

    # Verification
    is_verified: bool
    verified_by: str | None
    verification_evidence: list[dict]

    # Metadata
    last_analyzed_at: datetime
    analysis_version: int
    version: int  # Optimistic locking
```

## Quality Scoring Algorithm

### Scoring Process

1. **Text Analysis**: Parse requirement text for ambiguous/weak language
2. **Pattern Matching**: Detect TBD markers, incomplete information
3. **Quantification Check**: Look for metrics, thresholds, time limits
4. **Verb Analysis**: Identify strong vs. weak requirement verbs
5. **Conjunction Count**: Detect multiple requirements in one statement

### Final Score Calculation

```
Overall = (
    unambiguity × 0.25 +
    completeness × 0.20 +
    verifiability × 0.25 +
    necessity × 0.15 +
    singularity × 0.15
)
```

### Quality Levels

- **0.85-1.00**: Excellent (Production-ready)
- **0.70-0.85**: Good (Minor issues)
- **0.50-0.70**: Fair (Review recommended)
- **0.30-0.50**: Poor (Significant rework needed)
- **0.00-0.30**: Critical (Unusable)

## AI Property Placeholders

The `AIPropertyPlaceholder` class provides scaffolding for future AI-driven features:

```python
placeholder = AIPropertyPlaceholder(session)

# Future: Calculate semantic embeddings
embeddings = await placeholder.calculate_embeddings(item_id)

# Future: Find similar requirements
similar = await placeholder.find_similar_requirements(
    item_id="req-123",
    project_id="proj-456",
    threshold=0.85
)

# Future: Detect inconsistencies
issues = await placeholder.detect_inconsistencies(item_id)

# Future: Generate acceptance criteria
criteria = await placeholder.suggest_acceptance_criteria(item_id)
```

## Integration Points

### With Item Repository

```python
item_repo = ItemRepository(session)
item = await item_repo.get_by_id(item_id)

# Service uses item title and description for analysis
```

### With Link Repository

```python
link_repo = LinkRepository(session)
links = await link_repo.get_links_from_item(item_id)

# Service uses for impact analysis
```

### With Requirement Quality Repository

```python
quality_repo = RequirementQualityRepository(session)
specs = await quality_repo.list_by_project(project_id)

# List, filter, and aggregate specs
```

## Best Practices

### 1. Regular Quality Analysis

```python
# Refresh analysis after requirement updates
await service.refresh_quality_analysis(item_id)
```

### 2. Impact Assessment Before Changes

```python
# Check impact before modifying requirements
impact = await analyzer.calculate_impact(item_id, project_id)
if impact["high_impact"]:
    # Request stakeholder review
    log_for_review(item_id, impact)
```

### 3. Volatility Monitoring

```python
# Track high-volatility items for stabilization
high_vol = await quality_repo.list_high_volatility(
    project_id,
    threshold=0.5
)

for spec in high_vol:
    flag_for_stabilization(spec.item_id)
```

### 4. Systematic Verification

```python
# Track verification progress
unverified = await quality_repo.list_unverified(project_id)
progress = 1 - (len(unverified) / total_count)

if progress < 0.8:
    alert_qa_team("Only 80% of requirements verified")
```

### 5. Priority-Based Planning

```python
# Order work by WSJF score
high_priority = await quality_repo.list_by_wsjf_priority(project_id)

for spec in high_priority[:10]:
    add_to_sprint(spec.item_id)
```

## Error Handling

### Service Errors

```python
try:
    spec = await service.create_spec(item_id="invalid")
except ValueError as e:
    # Item not found
    handle_missing_item(str(e))

try:
    spec = await service.verify_requirement(item_id="unknown")
except ValueError as e:
    # Spec not found
    handle_missing_spec(str(e))
```

### Validation

All inputs are validated:
- Item must exist in project
- WSJF components must be 0-1
- Scores normalized to 0-1
- Change types must be recognized

## Testing

### Unit Tests

Pure analysis without database:

```bash
pytest tests/unit/services/test_item_spec_service.py -v
```

### Integration Tests

With async database operations:

```bash
pytest tests/integration/test_item_spec_service.py -v
```

### Test Coverage

- Quality analyzer: 95%+
- Impact analyzer: 90%+
- Volatility tracker: 90%+
- WSJF calculator: 100%
- Service orchestration: 85%+

## Performance Considerations

### Caching

- Store last analysis results in `RequirementQuality` model
- Reuse cached scores if item unchanged (check `version`)
- Refresh analysis only on:
  - Description/title changes
  - Link additions/removals
  - Time-based refreshes (e.g., weekly)

### Batch Operations

```python
# Analyze multiple items efficiently
items = await item_repo.list_by_project(project_id, limit=1000)

for item in items:
    try:
        spec = await service.create_spec(item.id)
    except Exception as e:
        log_analysis_error(item.id, str(e))
        continue

await session.commit()
```

### Index Optimization

Database indexes are created on:
- `item_id` (foreign key)
- `project_id` (filtering)
- `overall_quality_score` (sorting)
- `volatility_index` (reporting)
- `change_propagation_index` (impact reports)

## Future Enhancements

### Planned

1. **Semantic Embeddings**: Calculate requirement embeddings for similarity
2. **Cross-Requirement Consistency**: Detect conflicting requirements
3. **Auto-Generated Criteria**: LLM-based acceptance criteria generation
4. **Anomaly Detection**: Identify unusual specification patterns
5. **Requirement Clustering**: Group similar requirements automatically
6. **Compliance Checking**: Verify requirements against standards
7. **Natural Language Normalization**: Standardize requirement wording

### Vision

The service is designed to grow as AI capabilities mature:
- Plug-and-play embeddings (OpenAI, HuggingFace, etc.)
- Custom LLM integration for analysis
- Continuous learning from verified vs. failed requirements
- Domain-specific quality models

## Migration Guide

### Adding to Existing Projects

1. **Run Migration**
   ```bash
   alembic upgrade head
   ```

2. **Initialize Specs**
   ```python
   service = RequirementSpecService(session)
   items = await item_repo.list_by_project(project_id)

   for item in items:
       try:
           await service.create_spec(item.id)
       except:
           pass
   ```

3. **Verify Data**
   ```bash
   SELECT COUNT(*) FROM requirement_quality;
   ```

### Upgrading Existing Specs

If you have existing `RequirementQuality` records:

```python
# Model is backwards-compatible
# New fields have sensible defaults
# Existing quality_scores will be preserved
```

## References

- **ISO/IEC 29148:2018**: Requirements and Specification Guidelines
- **INCOSE Handbook**: Requirement Quality Patterns
- **SAFe 6.0**: WSJF Prioritization Framework
- **ISTQB**: Test Flakiness Detection Patterns

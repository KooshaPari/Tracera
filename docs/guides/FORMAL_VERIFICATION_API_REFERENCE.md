# Formal Verification API Reference

## Core Data Structures

### ConstraintExpression

Represents a constraint in multiple formats for verification.

```python
@dataclass
class ConstraintExpression:
    """Constraint in multiple representation formats."""

    # Core
    requirement_id: str
    original_text: str  # Natural language from requirement
    constraint_type: str  # 'arithmetic', 'boolean', 'temporal', 'resource'

    # Logical representations
    z3_formula: Optional[str]  # Z3 SMT-LIB format
    alloy_formula: Optional[str]  # Alloy syntax
    tla_formula: Optional[str]  # TLA+ syntax
    ocl_expression: Optional[str]  # OCL constraint
    prolog_clause: Optional[str]  # Prolog representation

    # Variables and domains
    variables: List[str]  # Variable names: ['response_time', 'cpu_usage']
    variable_types: Dict[str, str]  # Type info: {'response_time': 'Int', 'cpu_usage': 'Real'}
    variable_domains: Dict[str, Tuple[Any, Any]]  # Bounds: {'response_time': (0, 5000)}

    # Parse metadata
    parse_confidence: float  # 0.0 - 1.0, confidence in parse
    parse_error: Optional[str]
    parse_strategy: str  # 'pattern_match', 'nlp', 'manual', 'template'

    # Solver info
    theory: str  # 'linear_arithmetic', 'non_linear', 'bit_vector', 'array'
    complexity: str  # 'linear', 'polynomial', 'exponential', 'undecidable'
    timeout_needed: bool

    # Metadata
    created_at: datetime
    last_verified: Optional[datetime]
    verification_history: List[str]  # ['sat', 'unsat', 'unknown', ...]
```

### VerificationContext

Encapsulates entire specification context for verification.

```python
@dataclass
class VerificationContext:
    """Complete context for formal verification."""

    specification_id: str
    project_id: str

    # Requirements
    requirements: List[RequirementSpec]
    constraints: Dict[str, ConstraintExpression]

    # Solver state
    solver_type: str  # 'z3', 'alloy', 'tla', 'spin'
    solver_config: Dict[str, Any]  # timeout, verbosity, etc.
    solver_instance: Optional[Any]  # Actual solver object

    # Analysis results
    satisfiable: Optional[bool]
    conflicts: List[RequirementConflict]
    unsat_core: Optional[List[str]]
    model: Optional[Dict[str, Any]]  # Solution/counterexample

    # Performance
    start_time: datetime
    end_time: Optional[datetime]
    execution_time_ms: float
    peak_memory_usage_mb: float

    # Options
    check_logical_consistency: bool = True
    check_temporal_properties: bool = False
    check_safety_properties: bool = False
    check_performance_feasibility: bool = False
    find_minimal_conflicts: bool = True
    generate_counterexamples: bool = True

    # Callbacks
    on_conflict_found: Optional[Callable] = None
    on_verification_progress: Optional[Callable] = None
```

### RequirementConflict

Represents a detected conflict between requirements.

```python
@dataclass
class RequirementConflict:
    """Detected conflict in requirements."""

    conflict_id: str
    requirement_ids: List[str]  # Which requirements conflict
    conflict_type: str
    severity: str  # 'critical', 'high', 'medium', 'low'

    # Description
    description: str  # Human-readable description
    explanation: str  # Detailed explanation with formulas

    # Root cause
    conflicting_constraints: List[str]  # Which constraints conflict
    unsat_core: List[str]  # Minimal core causing conflict
    minimal_conflict_core: bool  # Is this guaranteed minimal?

    # Resolution options
    resolution_options: List[ConflictResolution]
    recommended_resolution: Optional[ConflictResolution]

    # Metadata
    detected_by: str  # 'z3', 'alloy', 'manual'
    detection_timestamp: datetime
    confidence: float  # How confident we are in this conflict

    # Related analysis
    affected_properties: List[str]  # What properties are violated?
    propagated_conflicts: List['RequirementConflict']  # What else breaks?

@dataclass
class ConflictResolution:
    """Option to resolve a conflict."""

    option_id: str
    type: str  # 'relax', 'remove', 'refine', 'parallelize', 'sequence'
    description: str
    impact: str  # How does this resolution affect other requirements?
    cost: str  # Implementation complexity: 'low', 'medium', 'high'
    recommendation_score: float  # 0.0 - 1.0
```

### ConflictReport

Complete report of all conflicts found.

```python
@dataclass
class ConflictReport:
    """Complete conflict analysis report."""

    specification_id: str
    timestamp: datetime

    # Summary
    total_conflicts: int
    critical_conflicts: int
    high_priority_conflicts: int
    medium_priority_conflicts: int
    low_priority_conflicts: int

    # Details
    conflicts: List[RequirementConflict]
    grouped_by_type: Dict[str, List[RequirementConflict]]
    grouped_by_requirement: Dict[str, List[RequirementConflict]]

    # Analysis
    conflict_graph: Dict[str, List[str]]  # Requirement -> conflicting with
    disconnected_components: List[List[str]]  # Requirement groups that don't interact
    critical_path: List[str]  # Requirements causing most conflicts

    # Recommendations
    resolution_suggestions: List[str]
    automated_resolutions: List[Dict[str, Any]]
    manual_review_required: bool

    # Statistics
    average_conflict_resolution_time: float  # Historical average
    estimated_resolution_time: float
    success_rate: float  # % of conflicts successfully resolved historically
```

---

## API Endpoints

### Verification Operations

#### POST /api/specifications/{id}/verify

**Description**: Run formal verification on specification

**Request Body**:
```python
{
    "check_logical_consistency": true,
    "check_temporal_properties": false,
    "check_safety_properties": true,
    "check_performance_feasibility": true,
    "find_minimal_conflicts": true,
    "solver_type": "z3",  # or "alloy", "tla", "spin"
    "timeout_seconds": 30
}
```

**Response**:
```python
{
    "specification_id": "spec_123",
    "timestamp": "2026-01-29T10:30:00Z",
    "status": "verified",  # or "conflict_detected", "inconclusive"
    "satisfiable": true,
    "verified_constraints": 45,
    "total_constraints": 50,
    "execution_time_ms": 1234,
    "conflicts": [],
    "model": {
        "response_time": 50,
        "availability": 99.5,
        "cpu_usage": 45
    }
}
```

**Error Responses**:
- `404`: Specification not found
- `400`: Invalid verification parameters
- `408`: Verification timeout
- `500`: Z3 solver error

---

#### GET /api/specifications/{id}/verification-status

**Description**: Get current verification status

**Query Parameters**:
- `detailed`: bool (default: false) - Include full conflict details
- `limit`: int (default: 10) - Max conflicts to return

**Response**:
```python
{
    "specification_id": "spec_123",
    "status": "verified",
    "last_verified": "2026-01-29T10:30:00Z",
    "verification_age_seconds": 3600,
    "satisfiable": true,
    "conflict_count": 0,
    "needs_reverification": false
}
```

---

#### GET /api/specifications/{id}/conflicts

**Description**: Get all detected conflicts

**Query Parameters**:
- `severity`: str - Filter by severity (critical, high, medium, low)
- `type`: str - Filter by conflict type
- `sort_by`: str - Sort by (severity, detection_time, requirement_count)

**Response**:
```python
{
    "specification_id": "spec_123",
    "total_conflicts": 2,
    "conflicts": [
        {
            "conflict_id": "conf_1",
            "requirement_ids": ["req_1", "req_2"],
            "conflict_type": "logical_contradiction",
            "severity": "critical",
            "description": "Response time must be < 100ms AND > 500ms",
            "explanation": "These constraints are unsatisfiable together",
            "unsat_core": ["req_1", "req_2"],
            "resolution_options": [
                {
                    "option_id": "res_1",
                    "type": "relax",
                    "description": "Change response time to < 200ms",
                    "recommendation_score": 0.9
                }
            ]
        }
    ]
}
```

---

#### POST /api/specifications/{id}/find-conflicts

**Description**: Explicitly search for conflicts (more thorough than verify)

**Request Body**:
```python
{
    "search_depth": "comprehensive",  # or "quick", "targeted"
    "conflict_types": ["logical", "temporal", "resource", "performance"],
    "include_pairwise_analysis": true,
    "include_higher_order_analysis": true,
    "max_conflicts_to_find": 100
}
```

**Response**:
```python
{
    "specification_id": "spec_123",
    "search_complete": true,
    "conflicts_found": 2,
    "pairwise_conflicts": 1,
    "higher_order_conflicts": 1,
    "search_time_ms": 5000,
    "conflicts": [...]
}
```

---

#### POST /api/specifications/{id}/resolve-conflict/{conflict_id}

**Description**: Apply resolution to a conflict

**Request Body**:
```python
{
    "resolution_option_id": "res_1",
    "apply_immediately": false,  # Preview vs apply
    "notify_stakeholders": true
}
```

**Response**:
```python
{
    "conflict_id": "conf_1",
    "resolution_applied": true,
    "modified_requirements": ["req_1"],
    "new_conflicts_introduced": [],
    "verification_status": "pending_reverification"
}
```

---

#### GET /api/specifications/{id}/verification-history

**Description**: Get verification history for specification

**Query Parameters**:
- `limit`: int (default: 20)
- `start_date`: ISO8601 date
- `end_date`: ISO8601 date

**Response**:
```python
{
    "specification_id": "spec_123",
    "verification_history": [
        {
            "timestamp": "2026-01-29T10:30:00Z",
            "status": "verified",
            "satisfiable": true,
            "conflict_count": 0,
            "execution_time_ms": 1234,
            "triggered_by": "user_manual",
            "triggered_by_user_id": "user_123"
        },
        {
            "timestamp": "2026-01-29T09:00:00Z",
            "status": "conflict_detected",
            "satisfiable": false,
            "conflict_count": 1,
            "execution_time_ms": 2100,
            "triggered_by": "requirement_change",
            "modified_requirements": ["req_5"]
        }
    ]
}
```

---

### Constraint Management

#### GET /api/specifications/{id}/constraints

**Description**: Get all parsed constraints

**Query Parameters**:
- `type`: str - Filter by constraint type
- `theory`: str - Filter by theory (linear_arithmetic, etc.)
- `unparseable_only`: bool

**Response**:
```python
{
    "specification_id": "spec_123",
    "total_constraints": 50,
    "parsed_constraints": 48,
    "unparseable_constraints": 2,
    "constraints": [
        {
            "requirement_id": "req_1",
            "original_text": "Response time must be less than 100ms",
            "constraint_type": "arithmetic",
            "z3_formula": "response_time < 100",
            "variables": ["response_time"],
            "variable_types": {"response_time": "Int"},
            "parse_confidence": 0.98,
            "theory": "linear_arithmetic"
        }
    ],
    "unparseable": [
        {
            "requirement_id": "req_49",
            "original_text": "System should be responsive",
            "parse_error": "Too vague for formal constraint"
        }
    ]
}
```

---

#### POST /api/specifications/{id}/refine-constraint/{constraint_id}

**Description**: Refine a constraint's parse/formalization

**Request Body**:
```python
{
    "refined_text": "Response time < 100ms",
    "constraint_type": "arithmetic",
    "z3_formula": "response_time < 100",
    "variables": {"response_time": "Int"},
    "confidence": 0.99
}
```

**Response**:
```python
{
    "constraint_id": "const_1",
    "status": "refined",
    "verification_needed": true,
    "reverify_conflicts": ["conf_5", "conf_12"]
}
```

---

### Analysis & Reporting

#### GET /api/specifications/{id}/verification-metrics

**Description**: Get verification metrics

**Response**:
```python
{
    "specification_id": "spec_123",
    "metrics": {
        "constraint_count": 50,
        "satisfiable_count": 48,
        "unsatisfiable_count": 2,
        "parse_success_rate": 0.96,
        "average_parse_confidence": 0.92,
        "average_verification_time_ms": 1500,
        "conflict_density": 0.04,  # conflicts per constraint pair
        "constraint_theories": {
            "linear_arithmetic": 30,
            "boolean": 15,
            "bit_vector": 5
        }
    }
}
```

---

#### POST /api/specifications/{id}/generate-report

**Description**: Generate comprehensive verification report

**Request Body**:
```python
{
    "format": "pdf",  # or "json", "markdown", "html"
    "include_sections": [
        "summary",
        "conflicts",
        "resolutions",
        "verification_details",
        "metrics",
        "recommendations"
    ],
    "include_visualizations": true,
    "stakeholders": ["stakeholder_1", "stakeholder_2"]
}
```

**Response**: PDF/JSON report file

---

#### GET /api/specifications/{id}/constraint-graph

**Description**: Get visualization of constraint dependencies

**Query Parameters**:
- `format`: str - "json", "dot" (Graphviz), "svg"

**Response**:
```python
{
    "specification_id": "spec_123",
    "nodes": [
        {
            "id": "req_1",
            "label": "Response time < 100ms",
            "type": "constraint",
            "satisfiable": true
        }
    ],
    "edges": [
        {
            "source": "req_1",
            "target": "req_2",
            "relationship": "conflicts_with",
            "conflict_id": "conf_1"
        }
    ]
}
```

---

## Python SDK

### Installation

```bash
pip install tracertm-formal-verification
```

### Basic Usage

```python
from tracertm.verification import (
    VerificationClient,
    VerificationContext,
    ConstraintExpression,
)

# Initialize client
client = VerificationClient(
    api_url="http://localhost:4000",
    api_key="your-api-key"
)

# Get specification
spec = client.get_specification("spec_123")

# Run verification
result = client.verify(
    spec_id="spec_123",
    check_logical_consistency=True,
    check_performance_feasibility=True,
    solver_type="z3"
)

# Check results
if result.satisfiable:
    print("Specification is consistent!")
    print(f"Model: {result.model}")
else:
    print(f"Found {len(result.conflicts)} conflicts:")
    for conflict in result.conflicts:
        print(f"  - {conflict.description}")

# Get and apply resolutions
conflicts = client.get_conflicts("spec_123", severity="critical")
for conflict in conflicts:
    print(f"Conflict: {conflict.description}")
    for resolution in conflict.resolution_options:
        print(f"  Resolution: {resolution.description}")

    # Apply recommended resolution
    if conflict.recommended_resolution:
        client.apply_resolution(
            spec_id="spec_123",
            conflict_id=conflict.conflict_id,
            resolution_id=conflict.recommended_resolution.option_id
        )
```

### Advanced Usage

```python
from tracertm.verification import (
    Z3Solver,
    AlloyAnalyzer,
    TLAChecker,
    ConflictDetectionStrategy,
)

# Use specific solver
z3_solver = Z3Solver(timeout_seconds=30)
context = VerificationContext(specification_id="spec_123")
result = z3_solver.verify(context)

# Custom conflict detection
strategy = ConflictDetectionStrategy(
    search_depth="comprehensive",
    find_minimal_conflicts=True,
    analyze_pairwise=True,
    analyze_higher_order=True
)
conflicts = strategy.find_conflicts("spec_123")

# Monitor verification progress
def on_progress(progress: float, message: str):
    print(f"Progress: {progress:.0%} - {message}")

result = client.verify(
    "spec_123",
    on_progress=on_progress,
    timeout_seconds=60
)
```

---

## WebSocket API

For real-time verification updates:

```python
import asyncio
from tracertm.verification import VerificationWebSocket

async def monitor_verification():
    async with VerificationWebSocket("ws://localhost:4000/verification") as ws:
        # Start verification
        await ws.start_verification("spec_123")

        # Receive updates
        async for message in ws:
            if message["type"] == "progress":
                print(f"Progress: {message['progress']}%")
            elif message["type"] == "conflict_found":
                conflict = message["conflict"]
                print(f"Conflict found: {conflict['description']}")
            elif message["type"] == "complete":
                result = message["result"]
                print(f"Verification complete: {result['status']}")
                break

asyncio.run(monitor_verification())
```

---

## Batch Operations

### Batch Verification

```python
from tracertm.verification import BatchVerificationClient

client = BatchVerificationClient(api_url="http://localhost:4000")

# Verify multiple specifications
spec_ids = ["spec_1", "spec_2", "spec_3", "spec_4"]
results = client.verify_batch(
    spec_ids=spec_ids,
    parallel=True,
    max_workers=4,
    timeout_seconds=30
)

# Process results
for spec_id, result in results.items():
    print(f"{spec_id}: {result.status}")
    if not result.satisfiable:
        print(f"  Conflicts: {len(result.conflicts)}")
```

### Batch Conflict Resolution

```python
# Resolve all conflicts of a type across multiple specs
resolved = client.resolve_conflicts_batch(
    specs=spec_ids,
    conflict_type="logical_contradiction",
    resolution_strategy="relax",
    apply=False  # Preview only
)

# Review and apply
for resolution in resolved:
    print(f"Would modify: {resolution['modified_requirements']}")

# Actually apply
client.resolve_conflicts_batch(
    specs=spec_ids,
    conflict_type="logical_contradiction",
    resolution_strategy="relax",
    apply=True
)
```

---

## Error Handling

```python
from tracertm.verification.exceptions import (
    VerificationError,
    SpecificationNotFound,
    SolverTimeout,
    InvalidConstraint,
    ConstraintParseError
)

try:
    result = client.verify("spec_123")
except SpecificationNotFound:
    print("Specification not found")
except SolverTimeout:
    print("Verification timed out - try reducing complexity")
except InvalidConstraint as e:
    print(f"Invalid constraint in requirement {e.requirement_id}: {e.message}")
except ConstraintParseError as e:
    print(f"Could not parse constraint: {e.message}")
except VerificationError as e:
    print(f"Verification error: {e.message}")
```

---

## Rate Limiting & Quotas

All API endpoints support standard rate limiting:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1643474400
```

Batch operations have special quotas:
- Standard: 10 concurrent verifications
- Premium: 50 concurrent verifications
- Enterprise: Unlimited

---

## Caching

Verification results are cached for 1 hour. To bypass cache:

```python
result = client.verify(
    "spec_123",
    use_cache=False,  # Force fresh verification
    cache_ttl_seconds=3600  # Or set custom TTL
)
```

---

## Authentication

```python
from tracertm.verification import VerificationClient

# API Key auth
client = VerificationClient(
    api_url="http://localhost:4000",
    api_key="sk_live_..."
)

# OAuth2 auth
client = VerificationClient(
    api_url="http://localhost:4000",
    oauth_token="access_token_..."
)

# mTLS auth
client = VerificationClient(
    api_url="https://localhost:8443",
    cert_file="/path/to/client.crt",
    key_file="/path/to/client.key",
    ca_file="/path/to/ca.crt"
)
```

---

## Webhooks

Receive verification updates via webhook:

```python
# Register webhook
client.register_webhook(
    url="https://your-domain.com/verification-webhook",
    events=["verification.complete", "conflict.detected"],
    secret="your-webhook-secret"
)

# Webhook payload
{
    "event": "verification.complete",
    "specification_id": "spec_123",
    "timestamp": "2026-01-29T10:30:00Z",
    "result": {
        "status": "conflict_detected",
        "conflicts": [...]
    }
}
```

This comprehensive API reference enables seamless integration of formal verification into TraceRTM's specification system.

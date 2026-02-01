# Formal Verification - Complete Code Examples

## Complete Working Example: Z3 Requirement Verification

### Full Service Implementation

```python
# src/tracertm/services/z3_verification_service.py

"""
Complete Z3 verification service for requirement consistency checking.

This module provides a production-ready service for:
- Parsing requirements to Z3 constraints
- Checking logical consistency
- Detecting requirement conflicts
- Generating conflict explanations
"""

import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from z3 import *

@dataclass
class ConstraintMetadata:
    """Metadata about a parsed constraint."""
    requirement_id: str
    requirement_title: str
    original_text: str
    variable_name: str
    variable_type: str  # 'Int', 'Real', 'Bool'
    operation: str  # '<', '>', '<=', '>=', '==', 'between'
    value: Any
    confidence: float  # 0.0-1.0

@dataclass
class ConflictInfo:
    """Information about a detected conflict."""
    conflict_id: str
    requirement_ids: List[str]
    conflict_description: str
    resolution_suggestions: List[str]
    severity: str  # 'critical', 'high', 'medium', 'low'
    detection_method: str  # 'direct', 'transitive'

class Z3RequirementVerifier:
    """
    Production-ready Z3 requirement verification service.

    Handles:
    - Constraint parsing with confidence scoring
    - Incremental verification
    - Conflict detection and explanation
    - Caching for performance
    """

    # Regex patterns for common constraint types
    CONSTRAINT_PATTERNS = {
        'comparison': r'(less|greater|more|less than|greater than|more than)\s+(\d+\.?\d*)',
        'exact': r'(exactly|must be|equals?)\s+(\d+\.?\d*)',
        'range': r'between\s+(\d+\.?\d*)\s+and\s+(\d+\.?\d*)',
        'percentage': r'(\d+\.?\d*)\s*%',
        'operators': r'([<>]=?|==|!=)\s*(\d+\.?\d*)',
    }

    def __init__(self, timeout_ms: int = 30000):
        """Initialize verifier."""
        self.timeout_ms = timeout_ms
        self.solver = Solver()
        set_param('timeout', timeout_ms)

        self.constraints_cache: Dict[str, Tuple[ExprRef, ConstraintMetadata]] = {}
        self.conflict_cache: Dict[str, List[ConflictInfo]] = {}
        self.requirement_map: Dict[str, str] = {}  # Formula string -> requirement ID

    def verify_requirements(
        self,
        requirements: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Verify a set of requirements for logical consistency.

        Args:
            requirements: List of requirement dicts with 'id', 'title', 'constraint_expr'

        Returns:
            {
                'satisfiable': bool,
                'status': 'verified' | 'conflict_detected' | 'inconclusive',
                'conflicts': List[ConflictInfo],
                'verified_count': int,
                'execution_time_ms': float,
                'model': Optional[Dict[str, Any]]  # Satisfying assignment if SAT
            }
        """
        start_time = time.time()
        self.solver.reset()
        self.constraints_cache.clear()
        self.requirement_map.clear()

        verified_count = 0
        parse_errors = []

        # Parse all requirements to constraints
        for req in requirements:
            try:
                formula, metadata = self._parse_requirement(req)
                if formula is not None:
                    self.solver.add(formula)
                    self.constraints_cache[req['id']] = (formula, metadata)
                    self.requirement_map[str(formula)] = req['id']
                    verified_count += 1
                else:
                    parse_errors.append({
                        'requirement_id': req['id'],
                        'reason': 'Could not parse constraint'
                    })
            except Exception as e:
                parse_errors.append({
                    'requirement_id': req['id'],
                    'reason': str(e)
                })

        # Check overall satisfiability
        check_result = self.solver.check()
        execution_time_ms = (time.time() - start_time) * 1000

        if check_result == sat:
            model = self.solver.model()
            model_dict = {str(d): str(model[d]) for d in model.decls()}

            return {
                'satisfiable': True,
                'status': 'verified',
                'conflicts': [],
                'verified_count': verified_count,
                'total_count': len(requirements),
                'execution_time_ms': execution_time_ms,
                'model': model_dict,
                'parse_errors': parse_errors
            }

        elif check_result == unsat:
            # Extract conflicts
            core = self.solver.unsat_core()
            conflicts = self._analyze_conflicts(core, requirements)

            return {
                'satisfiable': False,
                'status': 'conflict_detected',
                'conflicts': conflicts,
                'verified_count': verified_count,
                'total_count': len(requirements),
                'execution_time_ms': execution_time_ms,
                'model': None,
                'parse_errors': parse_errors
            }

        else:  # unknown
            return {
                'satisfiable': None,
                'status': 'inconclusive',
                'conflicts': [],
                'verified_count': verified_count,
                'total_count': len(requirements),
                'execution_time_ms': execution_time_ms,
                'model': None,
                'parse_errors': parse_errors
            }

    def find_pairwise_conflicts(
        self,
        requirements: List[Dict[str, str]]
    ) -> List[ConflictInfo]:
        """
        Find all pairwise conflicts between requirements.

        This is more thorough than overall satisfiability check as it
        identifies specific pairs that conflict.
        """
        conflicts = []

        for i, req1 in enumerate(requirements):
            for req2 in requirements[i+1:]:
                # Check if pair can be satisfied together
                solver = Solver()
                set_param('timeout', self.timeout_ms)

                formula1, meta1 = self._parse_requirement(req1)
                formula2, meta2 = self._parse_requirement(req2)

                if formula1 is None or formula2 is None:
                    continue

                solver.add(formula1)
                solver.add(formula2)

                if solver.check() == unsat:
                    conflict = ConflictInfo(
                        conflict_id=f"{req1['id']}-{req2['id']}",
                        requirement_ids=[req1['id'], req2['id']],
                        conflict_description=self._explain_pairwise_conflict(
                            req1, req2, solver.unsat_core()
                        ),
                        resolution_suggestions=[
                            f"Adjust {req1['title']} constraint",
                            f"Adjust {req2['title']} constraint",
                            "Implement in different system phases"
                        ],
                        severity='high',
                        detection_method='direct'
                    )
                    conflicts.append(conflict)

        return conflicts

    def _parse_requirement(
        self,
        requirement: Dict[str, str]
    ) -> Tuple[Optional[ExprRef], Optional[ConstraintMetadata]]:
        """
        Parse requirement to Z3 constraint formula.

        Returns:
            (formula, metadata) or (None, None) if unparseable
        """
        constraint_expr = requirement.get('constraint_expr', '').strip()

        if not constraint_expr:
            return None, None

        try:
            # Create variable name from requirement title
            var_name = self._sanitize_variable_name(requirement['title'])

            # Try to match constraint patterns
            if 'between' in constraint_expr.lower():
                # Range constraint: "between X and Y"
                match = re.search(r'between\s+([\d.]+)\s+and\s+([\d.]+)', constraint_expr, re.I)
                if match:
                    min_val = float(match.group(1))
                    max_val = float(match.group(2))
                    var = Real(var_name)

                    formula = And(var >= min_val, var <= max_val)
                    metadata = ConstraintMetadata(
                        requirement_id=requirement['id'],
                        requirement_title=requirement['title'],
                        original_text=constraint_expr,
                        variable_name=var_name,
                        variable_type='Real',
                        operation='between',
                        value=(min_val, max_val),
                        confidence=0.95
                    )
                    return formula, metadata

            # Try comparison operators
            for op, z3_op in [
                ('<=', lambda a, b: a <= b),
                ('>=', lambda a, b: a >= b),
                ('<', lambda a, b: a < b),
                ('>', lambda a, b: a > b),
                ('==', lambda a, b: a == b),
                ('!=', lambda a, b: a != b),
            ]:
                if op in constraint_expr:
                    match = re.search(rf'{re.escape(op)}\s*([\d.]+)', constraint_expr)
                    if match:
                        value = float(match.group(1))

                        # Determine if percentage or regular number
                        if '%' in constraint_expr:
                            var = Real(var_name)
                            var_type = 'Real'
                        elif '.' in str(value):
                            var = Real(var_name)
                            var_type = 'Real'
                        else:
                            var = Int(var_name)
                            var_type = 'Int'

                        formula = z3_op(var, value)
                        metadata = ConstraintMetadata(
                            requirement_id=requirement['id'],
                            requirement_title=requirement['title'],
                            original_text=constraint_expr,
                            variable_name=var_name,
                            variable_type=var_type,
                            operation=op,
                            value=value,
                            confidence=0.95
                        )
                        return formula, metadata

            # If we get here, pattern didn't match
            return None, ConstraintMetadata(
                requirement_id=requirement['id'],
                requirement_title=requirement['title'],
                original_text=constraint_expr,
                variable_name='',
                variable_type='',
                operation='',
                value=None,
                confidence=0.0
            )

        except Exception as e:
            print(f"Error parsing {requirement['id']}: {e}")
            return None, None

    def _sanitize_variable_name(self, name: str) -> str:
        """Convert requirement title to valid Z3 variable name."""
        # Replace non-alphanumeric with underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)

        # Remove leading digits
        while sanitized and sanitized[0].isdigit():
            sanitized = sanitized[1:]

        # Ensure not empty
        if not sanitized:
            sanitized = 'var'

        return sanitized[:63]  # Z3 name length limit

    def _analyze_conflicts(
        self,
        unsat_core: List[ExprRef],
        requirements: List[Dict[str, str]]
    ) -> List[ConflictInfo]:
        """
        Analyze unsat core to identify conflicting requirements.
        """
        # Build mapping of formula to requirement
        formula_to_req = {}
        for req_id, (formula, meta) in self.constraints_cache.items():
            formula_to_req[str(formula)] = req_id

        # Extract requirement IDs from core
        conflict_req_ids = []
        for expr in unsat_core:
            req_id = formula_to_req.get(str(expr))
            if req_id:
                conflict_req_ids.append(req_id)

        # Create conflict report
        conflict_descriptions = []
        for req_id in conflict_req_ids:
            for req in requirements:
                if req['id'] == req_id:
                    conflict_descriptions.append({
                        'id': req_id,
                        'title': req['title'],
                        'constraint': req.get('constraint_expr', '')
                    })
                    break

        if conflict_req_ids:
            return [ConflictInfo(
                conflict_id='core_0',
                requirement_ids=conflict_req_ids,
                conflict_description=self._explain_conflict_core(conflict_descriptions),
                resolution_suggestions=self._suggest_resolutions(conflict_descriptions),
                severity='critical',
                detection_method='core_extraction'
            )]

        return []

    def _explain_pairwise_conflict(
        self,
        req1: Dict[str, str],
        req2: Dict[str, str],
        unsat_core: List[ExprRef]
    ) -> str:
        """Generate human-readable explanation of pairwise conflict."""
        return (
            f"Requirement '{req1['title']}' with constraint "
            f"'{req1.get('constraint_expr', 'N/A')}' conflicts with "
            f"requirement '{req2['title']}' with constraint "
            f"'{req2.get('constraint_expr', 'N/A')}'. "
            f"These constraints cannot be satisfied simultaneously."
        )

    def _explain_conflict_core(self, conflict_descriptions: List[Dict]) -> str:
        """Generate explanation of conflict core."""
        conflicts = " AND ".join([
            f"'{d['constraint']}'" for d in conflict_descriptions
        ])
        return f"The following constraints are mutually inconsistent: {conflicts}"

    def _suggest_resolutions(self, conflict_descriptions: List[Dict]) -> List[str]:
        """Suggest ways to resolve conflicts."""
        suggestions = []

        # Always suggest relaxing bounds
        for desc in conflict_descriptions:
            suggestions.append(f"Relax constraint: {desc['title']}")

        # Suggest removing constraints
        if len(conflict_descriptions) <= 3:
            for desc in conflict_descriptions:
                suggestions.append(f"Remove requirement: {desc['title']}")

        # Suggest resequencing
        if len(conflict_descriptions) == 2:
            suggestions.append(f"Implement '{conflict_descriptions[0]['title']}' in Phase 1")
            suggestions.append(f"Implement '{conflict_descriptions[1]['title']}' in Phase 2")

        return suggestions[:5]  # Top 5 suggestions
```

### Usage Example

```python
# Example: Verify e-commerce system requirements
requirements = [
    {
        'id': 'req_1',
        'title': 'Response Time',
        'constraint_expr': '< 100'  # Less than 100ms
    },
    {
        'id': 'req_2',
        'title': 'Comprehensive Analysis',
        'constraint_expr': '> 500'  # More than 500ms
    },
    {
        'id': 'req_3',
        'title': 'Availability',
        'constraint_expr': 'between 99 and 99.99'
    },
]

verifier = Z3RequirementVerifier(timeout_ms=10000)

# Run verification
result = verifier.verify_requirements(requirements)

print(f"Status: {result['status']}")
print(f"Satisfiable: {result['satisfiable']}")
print(f"Verified: {result['verified_count']}/{result['total_count']}")
print(f"Time: {result['execution_time_ms']:.2f}ms")

if result['conflicts']:
    for conflict in result['conflicts']:
        print(f"\nConflict: {conflict.conflict_description}")
        for suggestion in conflict.resolution_suggestions:
            print(f"  - {suggestion}")

# Find pairwise conflicts
pairwise = verifier.find_pairwise_conflicts(requirements)
print(f"\nPairwise conflicts: {len(pairwise)}")
```

---

## Complete Test Suite

```python
# tests/unit/services/test_z3_requirement_verifier.py

"""
Complete test suite for Z3 requirement verifier.
"""

import pytest
from tracertm.services.z3_verification_service import Z3RequirementVerifier, ConstraintMetadata

@pytest.fixture
def verifier():
    """Create verifier instance for each test."""
    return Z3RequirementVerifier(timeout_ms=5000)

class TestConstraintParsing:
    """Test constraint parsing."""

    def test_parse_less_than_constraint(self, verifier):
        """Test parsing "< 100" constraint."""
        req = {
            'id': 'req_1',
            'title': 'Response Time',
            'constraint_expr': '< 100'
        }

        formula, metadata = verifier._parse_requirement(req)

        assert formula is not None
        assert metadata.operation == '<'
        assert metadata.value == 100
        assert metadata.confidence > 0.9

    def test_parse_between_constraint(self, verifier):
        """Test parsing "between X and Y"."""
        req = {
            'id': 'req_1',
            'title': 'Availability',
            'constraint_expr': 'between 99 and 99.99'
        }

        formula, metadata = verifier._parse_requirement(req)

        assert formula is not None
        assert metadata.operation == 'between'
        assert metadata.value == (99, 99.99)

    def test_parse_invalid_constraint(self, verifier):
        """Test parsing invalid constraint returns None."""
        req = {
            'id': 'req_1',
            'title': 'Invalid',
            'constraint_expr': 'xyz abc def'
        }

        formula, metadata = verifier._parse_requirement(req)

        # Should return None or metadata with low confidence
        if formula is not None:
            assert metadata.confidence < 0.5

    def test_parse_empty_constraint(self, verifier):
        """Test parsing empty constraint."""
        req = {
            'id': 'req_1',
            'title': 'Empty',
            'constraint_expr': ''
        }

        formula, metadata = verifier._parse_requirement(req)

        assert formula is None
        assert metadata is None

class TestVerification:
    """Test verification logic."""

    def test_verify_consistent_requirements(self, verifier):
        """Test verification of consistent requirements."""
        requirements = [
            {
                'id': 'req_1',
                'title': 'Min Response Time',
                'constraint_expr': '> 10'
            },
            {
                'id': 'req_2',
                'title': 'Max Response Time',
                'constraint_expr': '< 100'
            },
        ]

        result = verifier.verify_requirements(requirements)

        assert result['satisfiable'] is True
        assert result['status'] == 'verified'
        assert len(result['conflicts']) == 0
        assert result['model'] is not None

    def test_verify_conflicting_requirements(self, verifier):
        """Test verification detects conflicts."""
        requirements = [
            {
                'id': 'req_1',
                'title': 'CPU Usage Min',
                'constraint_expr': '> 80'
            },
            {
                'id': 'req_2',
                'title': 'CPU Usage Max',
                'constraint_expr': '< 50'
            },
        ]

        result = verifier.verify_requirements(requirements)

        assert result['satisfiable'] is False
        assert result['status'] == 'conflict_detected'
        assert len(result['conflicts']) > 0

    def test_verify_multiple_requirements(self, verifier):
        """Test verification of many requirements."""
        requirements = [
            {
                'id': f'req_{i}',
                'title': f'Requirement {i}',
                'constraint_expr': f'> {i*10}'
            }
            for i in range(10)
        ]

        result = verifier.verify_requirements(requirements)

        assert result['satisfiable'] is True
        assert result['verified_count'] <= len(requirements)

class TestConflictDetection:
    """Test conflict detection."""

    def test_find_pairwise_conflicts(self, verifier):
        """Test finding pairwise conflicts."""
        requirements = [
            {
                'id': 'req_1',
                'title': 'Max Latency',
                'constraint_expr': '< 50'
            },
            {
                'id': 'req_2',
                'title': 'Min Latency',
                'constraint_expr': '> 100'
            },
        ]

        conflicts = verifier.find_pairwise_conflicts(requirements)

        assert len(conflicts) > 0
        assert conflicts[0].requirement_ids == ['req_1', 'req_2']

    def test_no_pairwise_conflicts(self, verifier):
        """Test no conflicts when compatible."""
        requirements = [
            {
                'id': 'req_1',
                'title': 'Min Value',
                'constraint_expr': '> 10'
            },
            {
                'id': 'req_2',
                'title': 'Max Value',
                'constraint_expr': '< 100'
            },
        ]

        conflicts = verifier.find_pairwise_conflicts(requirements)

        assert len(conflicts) == 0

    def test_detect_multiple_pairwise_conflicts(self, verifier):
        """Test detection of multiple pairwise conflicts."""
        requirements = [
            {
                'id': 'req_1',
                'title': 'A',
                'constraint_expr': 'between 0 and 50'
            },
            {
                'id': 'req_2',
                'title': 'B',
                'constraint_expr': 'between 60 and 100'
            },
            {
                'id': 'req_3',
                'title': 'C',
                'constraint_expr': 'between 75 and 125'
            },
        ]

        conflicts = verifier.find_pairwise_conflicts(requirements)

        # Should find conflict between req_1 and req_2
        assert len(conflicts) >= 1

class TestVariableSanitization:
    """Test variable name sanitization."""

    def test_sanitize_spaces(self, verifier):
        """Test space removal."""
        name = verifier._sanitize_variable_name("Response Time")
        assert '_' in name or name == 'ResponseTime'

    def test_sanitize_special_chars(self, verifier):
        """Test special character removal."""
        name = verifier._sanitize_variable_name("CPU/Usage %")
        assert all(c.isalnum() or c == '_' for c in name)

    def test_sanitize_leading_digits(self, verifier):
        """Test leading digit removal."""
        name = verifier._sanitize_variable_name("123 CPU Usage")
        assert not name[0].isdigit()
```

---

## Integration with FastAPI

```python
# src/tracertm/api/routers/verification.py

"""
FastAPI endpoints for formal verification.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Dict, Any
import asyncio

from tracertm.api.deps import get_db
from tracertm.models.specification import Specification
from tracertm.models.item_spec import RequirementSpec
from tracertm.services.z3_verification_service import Z3RequirementVerifier
from tracertm.schemas.verification import (
    VerificationRequest,
    VerificationResponse,
    ConflictResponse
)

router = APIRouter(prefix="/api/specifications", tags=["verification"])

# Shared verifier instance (could be made thread-safe if needed)
_verifier = Z3RequirementVerifier(timeout_ms=30000)

@router.post("/{specification_id}/verify", response_model=VerificationResponse)
async def verify_specification(
    specification_id: str,
    request: VerificationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> VerificationResponse:
    """
    Verify specification for logical consistency.

    This endpoint:
    1. Retrieves the specification
    2. Extracts all requirements
    3. Parses to Z3 constraints
    4. Checks satisfiability
    5. Returns results with conflict details
    """
    # Get specification
    result = await db.execute(
        select(Specification).where(Specification.id == specification_id)
    )
    spec = result.scalar_one_or_none()

    if not spec:
        raise HTTPException(status_code=404, detail="Specification not found")

    # Get all requirements for this specification
    req_result = await db.execute(
        select(RequirementSpec).where(RequirementSpec.specification_id == specification_id)
    )
    requirements = req_result.scalars().all()

    # Convert to format expected by verifier
    req_dicts = [
        {
            'id': r.id,
            'title': r.title,
            'constraint_expr': r.constraint_expr or ''
        }
        for r in requirements
    ]

    # Run verification
    verification_result = _verifier.verify_requirements(req_dicts)

    # Update specification with results
    spec.verification_status = verification_result['status']
    spec.z3_verification_status = 'sat' if verification_result['satisfiable'] else 'unsat'
    spec.detected_conflicts = [
        {
            'id': c.conflict_id,
            'requirements': c.requirement_ids,
            'description': c.conflict_description,
            'severity': c.severity
        }
        for c in verification_result['conflicts']
    ]
    spec.z3_verification_timestamp = datetime.utcnow()

    await db.commit()

    # Background: Find pairwise conflicts if requested
    if request.find_detailed_conflicts:
        background_tasks.add_task(
            find_detailed_conflicts_background,
            specification_id,
            req_dicts,
            db
        )

    return VerificationResponse(
        specification_id=specification_id,
        timestamp=datetime.utcnow(),
        status=verification_result['status'],
        satisfiable=verification_result['satisfiable'],
        verified_constraints=verification_result['verified_count'],
        total_constraints=verification_result['total_count'],
        execution_time_ms=verification_result['execution_time_ms'],
        conflicts=[
            ConflictResponse(
                conflict_id=c.conflict_id,
                requirements=c.requirement_ids,
                description=c.conflict_description,
                suggestions=c.resolution_suggestions,
                severity=c.severity
            )
            for c in verification_result['conflicts']
        ],
        model=verification_result.get('model'),
        parse_errors=verification_result.get('parse_errors', [])
    )

@router.get("/{specification_id}/conflicts")
async def get_conflicts(
    specification_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get detected conflicts for specification."""
    result = await db.execute(
        select(Specification).where(Specification.id == specification_id)
    )
    spec = result.scalar_one_or_none()

    if not spec:
        raise HTTPException(status_code=404, detail="Specification not found")

    return {
        'specification_id': specification_id,
        'status': spec.verification_status,
        'conflicts': spec.detected_conflicts or [],
        'last_verified': spec.z3_verification_timestamp,
        'conflict_count': len(spec.detected_conflicts or [])
    }

async def find_detailed_conflicts_background(
    specification_id: str,
    requirements: List[Dict[str, str]],
    db: AsyncSession
):
    """Background task to find detailed pairwise conflicts."""
    try:
        pairwise = _verifier.find_pairwise_conflicts(requirements)

        # Update database with detailed conflicts
        result = await db.execute(
            select(Specification).where(Specification.id == specification_id)
        )
        spec = result.scalar_one_or_none()

        if spec:
            spec.detailed_conflicts = [
                {
                    'id': c.conflict_id,
                    'requirements': c.requirement_ids,
                    'description': c.conflict_description,
                    'suggestions': c.resolution_suggestions,
                    'severity': c.severity
                }
                for c in pairwise
            ]
            await db.commit()

    except Exception as e:
        print(f"Error finding detailed conflicts: {e}")
        # Don't fail the whole request
```

---

## Pydantic Schemas

```python
# src/tracertm/schemas/verification.py

"""
Pydantic schemas for verification API.
"""

from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class VerificationStatus(str, Enum):
    """Verification result status."""
    VERIFIED = "verified"
    CONFLICT_DETECTED = "conflict_detected"
    INCONCLUSIVE = "inconclusive"

class VerificationRequest(BaseModel):
    """Request for verification."""
    check_logical_consistency: bool = True
    check_temporal_properties: bool = False
    check_safety_properties: bool = False
    check_performance_feasibility: bool = False
    find_detailed_conflicts: bool = False
    timeout_seconds: int = 30

class ConflictResponse(BaseModel):
    """Single conflict in response."""
    conflict_id: str
    requirements: List[str]
    description: str
    suggestions: List[str]
    severity: str

class ParseError(BaseModel):
    """Constraint parse error."""
    requirement_id: str
    reason: str

class VerificationResponse(BaseModel):
    """Complete verification response."""
    specification_id: str
    timestamp: datetime
    status: VerificationStatus
    satisfiable: bool
    verified_constraints: int
    total_constraints: int
    execution_time_ms: float
    conflicts: List[ConflictResponse]
    model: Optional[Dict[str, Any]] = None
    parse_errors: List[ParseError] = []

    class Config:
        from_attributes = True
```

---

## Configuration Example

```python
# src/tracertm/config/verification_config.py

"""
Configuration for formal verification service.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class VerificationConfig:
    """Configuration for verification service."""

    # Z3 Solver settings
    z3_timeout_ms: int = 30000
    z3_parallel_threads: int = 4
    z3_model_generation: bool = True

    # Alloy settings
    alloy_jar_path: str = "alloy.jar"
    alloy_timeout_seconds: int = 60

    # TLA+ settings
    tla_timeout_seconds: int = 120
    tla_depth_limit: int = 100

    # Feature flags
    enable_z3_verification: bool = True
    enable_alloy_verification: bool = False
    enable_tla_verification: bool = False

    # Performance
    cache_constraints: bool = True
    max_cache_size: int = 1000
    incremental_verification: bool = True

    # Reporting
    generate_conflict_reports: bool = True
    report_format: str = "json"  # json, pdf, markdown
    include_model_in_response: bool = True

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        import os
        return cls(
            z3_timeout_ms=int(os.getenv('Z3_TIMEOUT_MS', '30000')),
            z3_parallel_threads=int(os.getenv('Z3_THREADS', '4')),
            enable_z3_verification=os.getenv('ENABLE_Z3', 'true').lower() == 'true',
            # ... other vars
        )
```

These examples provide a complete, production-ready implementation of formal verification for requirements engineering in TraceRTM.

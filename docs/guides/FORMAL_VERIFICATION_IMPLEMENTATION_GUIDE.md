# Formal Verification Implementation Guide for TraceRTM

## Quick Start: Integrating Z3 Constraint Solver

### Step 1: Install Z3

```bash
# Using pip
pip install z3-solver

# Or using conda
conda install -c conda-forge z3-solver
```

### Step 2: Create Verification Service

```python
# src/tracertm/services/formal_verification_service.py

from z3 import *
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from tracertm.models.specification import Specification, Contract
from tracertm.models.item_spec import RequirementSpec, RequirementType

@dataclass
class ConstraintParseResult:
    """Result of parsing requirement to Z3 constraint."""
    formula: Optional[ExprRef]
    variables: List[str]
    confidence: float
    parse_error: Optional[str]

@dataclass
class VerificationResult:
    """Result of Z3 verification."""
    requirement_id: str
    satisfiable: bool
    model: Optional[Dict[str, Any]]
    unsat_core: Optional[List[str]]
    execution_time_ms: float
    status: str  # 'verified', 'conflict', 'unknown'

class FormalVerificationService:
    """Service for formal verification using Z3."""

    def __init__(self):
        self.solver = Solver()
        self.constraints: Dict[str, ExprRef] = {}
        self.requirement_map: Dict[str, str] = {}

    def verify_specification(self, spec: Specification) -> Dict[str, Any]:
        """
        Verify entire specification for logical consistency.

        Raises:
            Z3Exception: If Z3 solver fails

        Returns:
            Dictionary with verification results
        """
        self.solver.reset()
        self.constraints.clear()
        self.requirement_map.clear()

        results = {
            'specification_id': spec.id,
            'timestamp': datetime.utcnow(),
            'satisfiable': True,
            'conflicts': [],
            'verified_constraints': 0,
            'total_constraints': 0,
            'execution_time_ms': 0
        }

        import time
        start_time = time.time()

        # Parse all requirement constraints
        for req in spec.requirements:
            parse_result = self._parse_requirement_to_z3(req)

            if parse_result.formula is not None:
                self.constraints[req.id] = parse_result.formula
                self.requirement_map[str(parse_result.formula)] = req.id
                self.solver.add(parse_result.formula)
                results['verified_constraints'] += 1

            results['total_constraints'] += 1

        # Check satisfiability
        check_result = self.solver.check()

        if check_result == sat:
            results['satisfiable'] = True
            results['status'] = 'verified'

            # Extract model (solution)
            model = self.solver.model()
            results['model'] = {
                str(d): str(model[d]) for d in model.decls()
            }

        elif check_result == unsat:
            results['satisfiable'] = False
            results['status'] = 'conflict_detected'

            # Extract minimal unsat core
            core = self.solver.unsat_core()
            core_reqs = [
                self.requirement_map.get(str(c), str(c))
                for c in core
            ]
            results['conflicts'] = core_reqs
            results['conflict_explanation'] = self._explain_conflict(core)

        else:  # unknown
            results['status'] = 'inconclusive'

        results['execution_time_ms'] = (time.time() - start_time) * 1000

        return results

    def _parse_requirement_to_z3(self, req: RequirementSpec) -> ConstraintParseResult:
        """
        Convert requirement to Z3 constraint formula.

        Handles common requirement patterns:
        - Threshold: "Response time < 100ms"
        - Range: "Availability between 99 and 99.99%"
        - Comparison: "CPU usage > 80%"
        """
        if not req.constraint_expr:
            return ConstraintParseResult(
                formula=None,
                variables=[],
                confidence=0.0,
                parse_error="No constraint expression"
            )

        try:
            # Create Z3 variable based on constraint type
            var_name = self._sanitize_var_name(req.title)

            # Detect numeric vs boolean constraints
            if any(op in req.constraint_expr for op in ['<', '>', '=', 'between']):
                # Numeric constraint
                if '%' in req.constraint_expr or 'percent' in req.constraint_expr.lower():
                    var = Real(var_name)  # Percentage/decimal
                else:
                    var = Int(var_name)  # Integer

                # Parse formula
                formula = self._parse_numeric_constraint(var, req.constraint_expr)
                confidence = 0.95  # High confidence for numeric

            else:
                # Boolean/logic constraint
                var = Bool(var_name)
                formula = var
                confidence = 0.7

            return ConstraintParseResult(
                formula=formula,
                variables=[var_name],
                confidence=confidence,
                parse_error=None
            )

        except Exception as e:
            return ConstraintParseResult(
                formula=None,
                variables=[],
                confidence=0.0,
                parse_error=str(e)
            )

    def _parse_numeric_constraint(self, var: ExprRef, expr_str: str) -> ExprRef:
        """
        Parse numeric constraint string to Z3 formula.

        Examples:
        - "< 100" -> var < 100
        - "between 99 and 99.99" -> (var >= 99) AND (var <= 99.99)
        - ">= 50" -> var >= 50
        """
        expr_lower = expr_str.lower().strip()

        # Handle "between X and Y" pattern
        if 'between' in expr_lower:
            import re
            match = re.search(r'between\s+([\d.]+)\s+and\s+([\d.]+)', expr_lower)
            if match:
                min_val = float(match.group(1))
                max_val = float(match.group(2))
                return And(var >= min_val, var <= max_val)

        # Handle comparison operators
        for op, z3_op in [
            ('<', lambda a, b: a < b),
            ('<=', lambda a, b: a <= b),
            ('>', lambda a, b: a > b),
            ('>=', lambda a, b: a >= b),
            ('=', lambda a, b: a == b),
            ('==', lambda a, b: a == b),
        ]:
            if op in expr_str:
                import re
                match = re.search(rf'{re.escape(op)}\s*([\d.]+)', expr_str)
                if match:
                    value = float(match.group(1))
                    return z3_op(var, value)

        # If no pattern matched, assume it's directly evaluable
        raise ValueError(f"Cannot parse constraint: {expr_str}")

    def _sanitize_var_name(self, name: str) -> str:
        """Convert requirement title to valid Z3 variable name."""
        import re
        # Remove non-alphanumeric, replace spaces with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure doesn't start with number
        if sanitized[0].isdigit():
            sanitized = '_' + sanitized
        return sanitized[:255]  # Z3 name length limit

    def _explain_conflict(self, core: List[ExprRef]) -> str:
        """Generate human-readable explanation of conflict."""
        explanations = []

        for constraint in core:
            explanations.append(f"- {constraint}")

        return "Conflicting constraints:\n" + "\n".join(explanations)

    def find_pairwise_conflicts(self, requirements: List[RequirementSpec]) -> List[Dict]:
        """
        Find all pairwise requirement conflicts.

        Returns:
            List of conflicts with requirement pairs
        """
        conflicts = []

        for i, req1 in enumerate(requirements):
            for req2 in requirements[i+1:]:
                solver = Solver()

                # Try to satisfy both requirements simultaneously
                formula1 = self._parse_requirement_to_z3(req1).formula
                formula2 = self._parse_requirement_to_z3(req2).formula

                if formula1 and formula2:
                    solver.add(formula1)
                    solver.add(formula2)

                    if solver.check() == unsat:
                        conflicts.append({
                            'requirement_1': {
                                'id': req1.id,
                                'title': req1.title,
                                'constraint': req1.constraint_expr
                            },
                            'requirement_2': {
                                'id': req2.id,
                                'title': req2.title,
                                'constraint': req2.constraint_expr
                            },
                            'severity': 'critical',
                            'type': 'pairwise_conflict'
                        })

        return conflicts
```

### Step 3: Create API Endpoint

```python
# src/tracertm/api/routers/verification.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from tracertm.api.deps import get_db
from tracertm.services.formal_verification_service import FormalVerificationService
from tracertm.schemas.verification import VerificationReport

router = APIRouter(prefix="/api/specifications", tags=["verification"])

@router.post("/{specification_id}/verify", response_model=VerificationReport)
async def verify_specification(
    specification_id: str,
    db: AsyncSession = Depends(get_db)
) -> VerificationReport:
    """
    Run formal verification on specification.

    This endpoint:
    1. Extracts all constraints from requirements
    2. Converts to Z3 formulas
    3. Checks logical consistency
    4. Detects requirement conflicts
    5. Returns detailed verification report
    """
    # Get specification
    spec = await db.execute(
        select(Specification).where(Specification.id == specification_id)
    )
    spec = spec.scalar_one_or_none()

    if not spec:
        raise HTTPException(status_code=404, detail="Specification not found")

    # Run verification
    verification_service = FormalVerificationService()
    results = verification_service.verify_specification(spec)

    # Store results in database
    spec.verification_status = results['status']
    spec.detected_conflicts = results['conflicts']
    spec.z3_verification_timestamp = datetime.utcnow()

    await db.commit()

    return VerificationReport(**results)

@router.get("/{specification_id}/conflicts")
async def get_specification_conflicts(
    specification_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """Get detected requirement conflicts."""
    spec = await db.execute(
        select(Specification).where(Specification.id == specification_id)
    )
    spec = spec.scalar_one_or_none()

    if not spec:
        raise HTTPException(status_code=404, detail="Specification not found")

    return {
        'specification_id': specification_id,
        'conflicts': spec.detected_conflicts or [],
        'last_verified': spec.z3_verification_timestamp,
        'status': spec.verification_status
    }
```

### Step 4: Add Schemas

```python
# src/tracertm/schemas/verification.py

from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

class VerificationResult(BaseModel):
    """Result of single constraint verification."""
    requirement_id: str
    satisfiable: bool
    model: Optional[Dict[str, Any]] = None
    execution_time_ms: float

class ConflictDetail(BaseModel):
    """Details of a detected conflict."""
    requirement_1: Dict[str, str]
    requirement_2: Dict[str, str]
    severity: str
    type: str

class VerificationReport(BaseModel):
    """Complete verification report for specification."""
    specification_id: str
    timestamp: datetime
    satisfiable: bool
    conflicts: List[str] = []
    verified_constraints: int
    total_constraints: int
    execution_time_ms: float
    status: str
    model: Optional[Dict[str, Any]] = None
    conflict_explanation: Optional[str] = None

    class Config:
        from_attributes = True
```

---

## Advanced: Alloy Integration

### Installation & Setup

```bash
# Download Alloy from https://alloytools.org/
# Extract and add to PATH
export ALLOY_HOME=/path/to/alloy
export PATH=$PATH:$ALLOY_HOME
```

### Service Implementation

```python
# src/tracertm/services/alloy_specification_service.py

import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class AlloyInstance:
    """Parsed Alloy instance (counterexample or solution)."""
    atoms: Dict[str, List[str]]
    relations: Dict[str, List[tuple]]
    satisfiable: bool

class AlloySpecificationService:
    """Service for Alloy-based specification analysis."""

    def __init__(self, alloy_jar_path: str = "alloy.jar"):
        self.alloy_path = alloy_jar_path

    def generate_alloy_spec(self, spec: Specification) -> str:
        """
        Generate Alloy specification from TraceRTM specification.

        Returns:
            Alloy code as string
        """
        alloy_code = f"""
module {spec.id}

// Signatures (domain model)
"""

        # Generate signatures for entities mentioned in requirements
        entities = self._extract_entities(spec)
        for entity in entities:
            alloy_code += f"sig {entity} {{}}\n"

        # Generate facts (constraints) from requirements
        alloy_code += "\n// Facts (constraints from requirements)\n"
        for req in spec.requirements:
            if req.constraint_expr:
                alloy_fact = self._requirement_to_alloy_fact(req)
                if alloy_fact:
                    alloy_code += f"\nfact {req.id} {{\n  {alloy_fact}\n}}\n"

        # Generate predicates
        alloy_code += "\n// Predicates\n"
        for req in spec.requirements:
            if req.requirement_type == RequirementType.FUNCTIONAL:
                pred = self._requirement_to_alloy_predicate(req)
                if pred:
                    alloy_code += pred

        return alloy_code

    def verify_specification(self, spec: Specification) -> Dict[str, Any]:
        """
        Verify specification using Alloy analyzer.

        Returns:
            Verification results including satisfiability and instances
        """
        # Generate Alloy code
        alloy_code = self.generate_alloy_spec(spec)

        # Write to temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.als',
            delete=False
        ) as f:
            f.write(alloy_code)
            spec_file = f.name

        try:
            # Run Alloy analyzer
            result = subprocess.run(
                ["java", "-jar", self.alloy_path, spec_file],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse XML output
            output_file = spec_file.replace('.als', '.xml')
            if Path(output_file).exists():
                tree = ET.parse(output_file)
                root = tree.getroot()

                instances = []
                for instance in root.findall(".//instance"):
                    parsed = self._parse_alloy_instance(instance)
                    instances.append(parsed)

                satisfiable = len(instances) > 0

                return {
                    'satisfiable': satisfiable,
                    'instances': instances,
                    'alloy_code': alloy_code,
                    'output': result.stdout
                }

        finally:
            # Cleanup
            Path(spec_file).unlink(missing_ok=True)

    def _extract_entities(self, spec: Specification) -> List[str]:
        """Extract entity names from specification."""
        entities = set()

        for req in spec.requirements:
            # Use NLP or pattern matching to extract nouns
            words = req.title.split()
            # Simple heuristic: capitalized words are likely entities
            for word in words:
                if word and word[0].isupper():
                    entities.add(word)

        return sorted(list(entities))

    def _requirement_to_alloy_fact(self, req: RequirementSpec) -> Optional[str]:
        """Convert requirement to Alloy fact."""
        # This would require NLP/template-based conversion
        # Example: "Users must have unique IDs" ->
        # "all disj u1, u2: User | u1.id != u2.id"
        pass

    def _requirement_to_alloy_predicate(self, req: RequirementSpec) -> Optional[str]:
        """Convert functional requirement to Alloy predicate."""
        # Similar conversion for predicates
        pass

    def _parse_alloy_instance(self, instance_elem: ET.Element) -> AlloyInstance:
        """Parse XML instance to AlloyInstance."""
        atoms = {}
        relations = {}

        # Parse atoms
        for sig in instance_elem.findall(".//sig"):
            sig_name = sig.get('label')
            atom_list = [
                atom.get('label')
                for atom in sig.findall(".//atom")
            ]
            atoms[sig_name] = atom_list

        # Parse relations
        for field in instance_elem.findall(".//field"):
            field_name = field.get('label')
            tuples = []
            for tuple_elem in field.findall(".//tuple"):
                atoms_in_tuple = [
                    atom.get('label')
                    for atom in tuple_elem.findall(".//atom")
                ]
                tuples.append(tuple(atoms_in_tuple))
            relations[field_name] = tuples

        return AlloyInstance(
            atoms=atoms,
            relations=relations,
            satisfiable=True
        )
```

---

## Testing Formal Verification

### Unit Tests

```python
# tests/unit/services/test_formal_verification_service.py

import pytest
from tracertm.services.formal_verification_service import FormalVerificationService
from tracertm.models.item_spec import RequirementSpec, RequirementType

@pytest.fixture
def verification_service():
    return FormalVerificationService()

class TestConstraintParsing:
    """Test Z3 constraint parsing."""

    def test_parse_numeric_constraint_less_than(self, verification_service):
        """Test parsing '< 100' constraint."""
        req = RequirementSpec(
            id="req1",
            title="Response Time",
            constraint_expr="< 100",
            requirement_type=RequirementType.CONSTRAINT
        )

        result = verification_service._parse_requirement_to_z3(req)

        assert result.formula is not None
        assert result.confidence > 0.9
        assert result.parse_error is None

    def test_parse_between_constraint(self, verification_service):
        """Test parsing 'between X and Y' constraint."""
        req = RequirementSpec(
            id="req2",
            title="Availability",
            constraint_expr="between 99 and 99.99",
            requirement_type=RequirementType.CONSTRAINT
        )

        result = verification_service._parse_requirement_to_z3(req)

        assert result.formula is not None
        assert result.parse_error is None

    def test_parse_invalid_constraint(self, verification_service):
        """Test parsing invalid constraint."""
        req = RequirementSpec(
            id="req3",
            title="Invalid",
            constraint_expr="xyz invalid abc",
            requirement_type=RequirementType.CONSTRAINT
        )

        result = verification_service._parse_requirement_to_z3(req)

        assert result.formula is None
        assert result.parse_error is not None

class TestConflictDetection:
    """Test requirement conflict detection."""

    def test_detect_contradictory_constraints(self, verification_service):
        """Test detection of directly contradictory constraints."""
        requirements = [
            RequirementSpec(
                id="req1",
                title="CPU < 50%",
                constraint_expr="< 50",
                requirement_type=RequirementType.CONSTRAINT
            ),
            RequirementSpec(
                id="req2",
                title="CPU > 80%",
                constraint_expr="> 80",
                requirement_type=RequirementType.CONSTRAINT
            )
        ]

        conflicts = verification_service.find_pairwise_conflicts(requirements)

        assert len(conflicts) > 0
        assert conflicts[0]['requirement_1']['id'] == 'req1'
        assert conflicts[0]['requirement_2']['id'] == 'req2'

    def test_no_conflict_when_compatible(self, verification_service):
        """Test no conflict when constraints are compatible."""
        requirements = [
            RequirementSpec(
                id="req1",
                title="CPU < 80%",
                constraint_expr="< 80",
                requirement_type=RequirementType.CONSTRAINT
            ),
            RequirementSpec(
                id="req2",
                title="CPU > 20%",
                constraint_expr="> 20",
                requirement_type=RequirementType.CONSTRAINT
            )
        ]

        conflicts = verification_service.find_pairwise_conflicts(requirements)

        assert len(conflicts) == 0
```

### Integration Tests

```python
# tests/integration/test_verification_endpoint.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_verify_specification_endpoint(client: TestClient, db: AsyncSession):
    """Test /api/specifications/{id}/verify endpoint."""
    # Create test specification with requirements
    spec = create_test_specification(db)

    # Verify specification
    response = client.post(f"/api/specifications/{spec.id}/verify")

    assert response.status_code == 200
    data = response.json()

    assert 'specification_id' in data
    assert 'satisfiable' in data
    assert 'status' in data
    assert data['status'] in ['verified', 'conflict_detected', 'inconclusive']

@pytest.mark.asyncio
async def test_get_conflicts_endpoint(client: TestClient, db: AsyncSession):
    """Test /api/specifications/{id}/conflicts endpoint."""
    spec = create_test_specification(db)

    # First verify
    client.post(f"/api/specifications/{spec.id}/verify")

    # Get conflicts
    response = client.get(f"/api/specifications/{spec.id}/conflicts")

    assert response.status_code == 200
    data = response.json()

    assert 'specification_id' in data
    assert 'conflicts' in data
    assert isinstance(data['conflicts'], list)
```

---

## CLI Tools for Verification

### Command-Line Interface

```python
# src/tracertm/cli/verification.py

import click
from tracertm.services.formal_verification_service import FormalVerificationService
from tracertm.database import get_db_session
from tracertm.models.specification import Specification

@click.group()
def verification():
    """Formal verification commands."""
    pass

@verification.command()
@click.option('--spec-id', required=True, help='Specification ID')
@click.option('--format', default='json', type=click.Choice(['json', 'text', 'csv']))
def verify(spec_id: str, format: str):
    """Verify specification for logical consistency."""
    db = get_db_session()

    try:
        spec = db.query(Specification).filter(
            Specification.id == spec_id
        ).first()

        if not spec:
            click.echo(f"Error: Specification {spec_id} not found", err=True)
            return

        # Run verification
        service = FormalVerificationService()
        results = service.verify_specification(spec)

        # Output results
        if format == 'json':
            import json
            click.echo(json.dumps(results, indent=2, default=str))
        elif format == 'text':
            click.echo(f"Specification: {spec_id}")
            click.echo(f"Status: {results['status']}")
            click.echo(f"Satisfiable: {results['satisfiable']}")
            click.echo(f"Verified constraints: {results['verified_constraints']}/{results['total_constraints']}")

            if results['conflicts']:
                click.echo("\nDetected conflicts:")
                for conflict in results['conflicts']:
                    click.echo(f"  - {conflict}")

    finally:
        db.close()

@verification.command()
@click.option('--spec-id', required=True, help='Specification ID')
def conflicts(spec_id: str):
    """Show all detected conflicts."""
    db = get_db_session()

    try:
        spec = db.query(Specification).filter(
            Specification.id == spec_id
        ).first()

        if not spec or not spec.detected_conflicts:
            click.echo(f"No conflicts detected for {spec_id}")
            return

        click.echo(f"Conflicts in {spec_id}:")
        for i, conflict in enumerate(spec.detected_conflicts, 1):
            click.echo(f"{i}. {conflict}")

    finally:
        db.close()
```

Usage:

```bash
# Verify specification
python -m tracertm.cli verification verify --spec-id spec_123 --format text

# Show conflicts
python -m tracertm.cli verification conflicts --spec-id spec_123
```

---

## Monitoring & Metrics

### Verification Metrics

```python
# src/tracertm/services/verification_metrics.py

from dataclasses import dataclass
from typing import List

@dataclass
class VerificationMetrics:
    """Metrics about verification process."""
    total_specifications: int
    verified_specifications: int
    specifications_with_conflicts: int
    average_constraint_count: float
    average_verification_time_ms: float
    conflict_resolution_rate: float  # % of conflicts resolved

class VerificationMetricsCollector:
    """Collect metrics about formal verification."""

    def __init__(self, db_session):
        self.db = db_session

    def get_metrics(self) -> VerificationMetrics:
        """Collect verification metrics."""
        from sqlalchemy import func
        from tracertm.models.specification import Specification

        # Query metrics
        total = self.db.query(func.count(Specification.id)).scalar()
        verified = self.db.query(func.count(Specification.id)).filter(
            Specification.verification_status == 'verified'
        ).scalar()
        with_conflicts = self.db.query(func.count(Specification.id)).filter(
            Specification.verification_status == 'conflict_detected'
        ).scalar()

        return VerificationMetrics(
            total_specifications=total or 0,
            verified_specifications=verified or 0,
            specifications_with_conflicts=with_conflicts or 0,
            average_constraint_count=self._get_avg_constraint_count(),
            average_verification_time_ms=self._get_avg_verification_time(),
            conflict_resolution_rate=self._get_resolution_rate()
        )

    def _get_avg_constraint_count(self) -> float:
        """Calculate average constraints per specification."""
        # Implementation
        pass

    def _get_avg_verification_time(self) -> float:
        """Calculate average verification time."""
        # Implementation
        pass

    def _get_resolution_rate(self) -> float:
        """Calculate conflict resolution rate."""
        # Implementation
        pass
```

---

## Performance Optimization

### Constraint Caching

```python
from functools import lru_cache
from typing import Tuple

class CachedVerificationService(FormalVerificationService):
    """Verification service with constraint caching."""

    def __init__(self):
        super().__init__()
        self.constraint_cache = {}

    @lru_cache(maxsize=1000)
    def _parse_requirement_to_z3_cached(self, constraint_expr: str) -> Tuple:
        """Cache constraint parsing results."""
        # Parse and return formula components
        pass

    def verify_specification_incremental(self, spec, modified_reqs=None):
        """
        Verify specification incrementally.

        Only re-parses modified requirements instead of entire spec.
        """
        modified_reqs = modified_reqs or []

        # Only add constraints for modified requirements
        for req in modified_reqs:
            formula = self._parse_requirement_to_z3_cached(req.constraint_expr)
            if formula:
                self.solver.add(formula)

        # Check satisfiability
        return self.solver.check()
```

---

## Next Steps

1. **Deploy Z3 Service**: Start with basic Z3 integration
2. **Monitor Usage**: Track verification requests and response times
3. **Iterate**: Gather feedback from users on conflict detection quality
4. **Expand**: Add Alloy, TLA+, Event-B integrations based on adoption
5. **Optimize**: Profile and optimize solver performance for large specifications

## Resources

- **Z3 Documentation**: https://z3prover.github.io/
- **Alloy Documentation**: https://alloytools.org/
- **TLA+ Resources**: https://lamport.azurewebsites.net/tla/
- **Event-B**: https://www.event-b.org/
- **SPIN/LTL**: http://spinroot.com/

# Formal Methods & Verification Tools for Requirements Engineering

## Executive Summary

This research provides a comprehensive analysis of formal methods and verification tools applicable to requirements engineering, with focus on:

1. **Theorem Proving (Z3)** - Constraint solving and logical consistency verification
2. **Model Checking** - Alloy Analyzer and SPIN for specification validation
3. **Temporal Logic** - TLA+ for behavior specification and verification
4. **Refinement Methods** - Event-B for incremental formalization
5. **Design by Contract** - Preconditions, postconditions, invariants
6. **Constraint Languages** - OCL and SAT/SMT solvers
7. **Consistency Detection** - Algorithms for conflict identification

The research includes concrete API patterns, data structures, and integration strategies for TraceRTM's specification system.

---

## Part 1: Z3 Theorem Prover for Requirement Consistency

### 1.1 Overview

Z3 is Microsoft's SMT (Satisfiability Modulo Theories) solver that can:
- Verify logical consistency of requirement sets
- Detect conflicting constraints
- Find counterexamples to specification claims
- Generate minimal conflict explanations

### 1.2 Core Concepts

**Satisfiability (SAT)**: Can a formula be satisfied (true) for some assignment?
**SMT**: SAT extended with theories (linear arithmetic, arrays, uninterpreted functions)
**Proof Generation**: Z3 can generate proofs of unsatisfiability

### 1.3 API Patterns

```python
# Example 1: Basic Constraint Solving
from z3 import *

def verify_requirement_consistency(requirements: List[str]) -> VerificationResult:
    """
    Verify if a set of requirement constraints is satisfiable.

    Pattern: Convert requirements to Z3 formulas, check satisfiability.
    """
    solver = Solver()

    # Example: Resource allocation requirements
    # Req1: CPU usage must be < 80%
    # Req2: CPU usage must be > 90%
    # Result: UNSAT (contradiction)

    cpu_usage = Real('cpu_usage')

    # Convert natural language to constraints
    solver.add(cpu_usage < 80)  # Req1
    solver.add(cpu_usage > 90)  # Req2

    result = solver.check()

    return VerificationResult(
        status=str(result),  # 'sat', 'unsat', 'unknown'
        satisfiable=result == sat,
        model=solver.model() if result == sat else None,
        proof=solver.proof() if result == unsat else None
    )
```

### 1.4 Advanced Pattern: Multi-Theory Reasoning

```python
def verify_complex_requirements(spec: Specification) -> ConflictReport:
    """
    Advanced: Verify requirements across multiple theories.

    Pattern: Combine linear arithmetic, function definitions, and quantifiers.
    """
    solver = Solver()

    # Define constants for requirement types
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    COST = "cost"

    # Create variables for each requirement
    requirements = {
        "response_time_ms": Int('response_time_ms'),
        "availability_pct": Real('availability_pct'),
        "infrastructure_cost_usd": Int('infrastructure_cost_usd'),
        "server_count": Int('server_count'),
    }

    # Add requirement constraints
    solver.add(requirements['response_time_ms'] < 100)  # SLA requirement
    solver.add(requirements['availability_pct'] >= 99.9)  # SLA requirement
    solver.add(
        requirements['server_count'] * 50 == requirements['infrastructure_cost_usd']
    )  # Cost model

    # Detect conflicts
    conflicts = []
    for i, req in enumerate(spec.requirements):
        for j, other_req in enumerate(spec.requirements[i+1:], i+1):
            # Check pairwise consistency
            solver.push()  # Save solver state

            # Add potentially conflicting requirements
            add_requirement_constraint(solver, req)
            add_requirement_constraint(solver, other_req)

            if solver.check() == unsat:
                # Extract minimal unsat core
                core = solver.unsat_core()
                conflicts.append({
                    'requirement_1': req.id,
                    'requirement_2': other_req.id,
                    'reason': str(core),
                    'core_size': len(core)
                })

            solver.pop()  # Restore solver state

    return ConflictReport(
        is_consistent=solver.check() == sat,
        conflicts=conflicts,
        minimal_conflict_core=extract_unsat_core(solver)
    )


def add_requirement_constraint(solver: Solver, req: Requirement) -> None:
    """Convert requirement to Z3 constraint."""
    if req.type == RequirementType.CONSTRAINT:
        # Parse constraint expression and add to solver
        constraint = parse_z3_expression(req.constraint_expr)
        solver.add(constraint)
```

### 1.5 Data Structures for Z3 Integration

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Any

class VerificationStatus(str, Enum):
    """Z3 verification result status."""
    SAT = "sat"  # Satisfiable
    UNSAT = "unsat"  # Unsatisfiable
    UNKNOWN = "unknown"  # Timeout/incomplete

@dataclass
class VerificationResult:
    """Result of formal verification."""
    status: VerificationStatus
    satisfiable: bool
    model: Optional[dict[str, Any]] = None
    proof: Optional[str] = None
    execution_time_ms: float = 0.0
    solver_calls: int = 0

@dataclass
class ConflictReport:
    """Report of detected conflicts in requirements."""
    is_consistent: bool
    conflicts: List[dict] = None
    minimal_conflict_core: List[str] = None
    resolution_suggestions: List[str] = None

@dataclass
class ConstraintExpression:
    """Represents a constraint in Z3-compatible form."""
    original_text: str
    z3_formula: str  # Z3 syntax representation
    variables: List[str]
    theory: str  # 'linear_arithmetic', 'bit_vector', etc.
    confidence: float  # Parse confidence 0.0-1.0
```

### 1.6 Requirement Pattern Extraction

```python
class RequirementConstraintParser:
    """Parse natural language requirements into Z3 constraints."""

    PATTERNS = {
        'threshold': r'(\w+)\s+(must\s+)?be\s+(<|>|<=|>=|=)\s+(\d+)',
        'range': r'(\w+)\s+between\s+(\d+)\s+and\s+(\d+)',
        'quantifier': r'(all|some|no)\s+(\w+)\s+must\s+(\w+)',
    }

    @staticmethod
    def parse(requirement_text: str) -> ConstraintExpression:
        """
        Convert natural language to constraint expression.

        Examples:
        - "Response time must be < 100ms" -> response_time < 100
        - "Availability between 99 and 99.99%" -> availability >= 99 AND availability <= 99.99
        """
        # Implementation would use regex or NLP
        pass
```

### 1.7 Integration with TraceRTM

```python
# Add to Specification model
from sqlalchemy import Text, String
from sqlalchemy.orm import Mapped, mapped_column

class Specification(Base):
    # ... existing fields ...

    # Z3 verification fields
    z3_verification_status: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        comment="Status of Z3 consistency check: sat/unsat/unknown"
    )
    z3_constraints: Mapped[list[str]] = mapped_column(
        JSONType,
        nullable=True,
        comment="List of Z3-formatted constraints extracted from requirements"
    )
    z3_conflicts: Mapped[list[dict]] = mapped_column(
        JSONType,
        nullable=True,
        comment="Detected requirement conflicts with unsat cores"
    )
    z3_verification_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
```

---

## Part 2: Alloy Analyzer for Specification Modeling

### 2.1 Overview

Alloy is a lightweight formal specification language with:
- Relational model of state and behavior
- Constraint solver (uses SAT)
- Automatic generation of instances and counterexamples
- Visualization of constraints and models

### 2.2 Core Concepts

**Signature**: Class-like structure defining atoms and relations
**Relation**: Set-valued attributes representing connections
**Fact**: Global constraint (assertion)
**Pred**: Predicate (parameterized assertion)
**Check**: Assert that something is impossible

### 2.3 Requirement Modeling Patterns

```python
"""
Example: System Requirements in Alloy Syntax

Requirement: User authentication system
- Users must have unique IDs
- Sessions must be tied to users
- Sessions expire after 30 minutes
- Concurrent sessions are allowed
- Admin users have elevated privileges
"""

ALLOY_USER_AUTH_SPEC = """
// Signatures (domain model)
sig User {
    id: one Id,
    role: one Role,
    password: one String,
    sessions: set Session
}

sig Session {
    user: one User,
    created_at: one Timestamp,
    last_activity: one Timestamp
}

sig Id {}
sig Role {}
sig String {}
sig Timestamp {}

enum Role { User, Admin }

// Facts (global constraints)
fact unique_user_ids {
    // Requirement: Unique user IDs
    all disj u1, u2: User | u1.id != u2.id
}

fact session_user_consistency {
    // Requirement: Session references valid user
    all s: Session | s.user != none
}

fact concurrent_sessions_allowed {
    // Requirement: User can have multiple sessions
    // (Default behavior - no constraint needed)
}

fact admin_privilege_separation {
    // Requirement: Only admins can perform admin ops
    // (Implementation detail - checked in code)
}

// Predicates (parameterized constraints)
pred session_valid[s: Session, current_time: Timestamp] {
    // Session is valid if created within 30 minutes
    // This is pseudo-code representation
    sub[current_time, s.created_at] <= 30
}

pred can_access_resource[u: User, resource: Resource] {
    u.role = Admin or u in resource.allowed_users
}

// Assertions (things we claim are true)
assert no_orphaned_sessions {
    // All sessions must reference valid users
    all s: Session | s.user in User
}

// Checks (test assertions)
check no_orphaned_sessions for 10
"""

@dataclass
class AlloySpecification:
    """Specification in Alloy format."""
    signatures: List[str]  # Domain model
    facts: List[str]  # Global constraints
    predicates: List[str]  # Named constraints
    assertions: List[str]  # Properties to verify
    alloy_code: str  # Full Alloy specification
```

### 2.4 API Pattern: Alloy Analyzer Integration

```python
from typing import List, Dict, Any
from dataclasses import dataclass
import subprocess
import xml.etree.ElementTree as ET

@dataclass
class AlloyAnalysisResult:
    """Result of Alloy analysis."""
    satisfiable: bool
    instance: Optional[Dict[str, Any]]
    counterexample: Optional[Dict[str, Any]]
    theorem_satisfied: bool
    analysis_time_ms: float
    bounds_used: Dict[str, int]

class AlloyAnalyzer:
    """Wrapper for Alloy analyzer."""

    def __init__(self, alloy_path: str = "alloy"):
        self.alloy_path = alloy_path

    def verify_specification(self, spec_code: str) -> AlloyAnalysisResult:
        """
        Run Alloy analyzer on specification.

        Pattern: Generate Alloy code, invoke solver, parse XML results.
        """
        # Write specification to temp file
        spec_file = write_temp_alloy(spec_code)

        try:
            # Run Alloy analyzer
            result = subprocess.run(
                [self.alloy_path, spec_file],
                capture_output=True,
                timeout=30
            )

            # Parse XML output
            output_xml = ET.fromstring(result.stdout)

            # Extract results
            satisfiable = output_xml.find(".//satisfiable").text == "true"
            instance = parse_alloy_instance(output_xml) if satisfiable else None

            return AlloyAnalysisResult(
                satisfiable=satisfiable,
                instance=instance,
                counterexample=parse_counterexample(output_xml),
                theorem_satisfied=is_theorem_satisfied(output_xml),
                analysis_time_ms=float(output_xml.find(".//time").text),
                bounds_used=parse_bounds(output_xml)
            )
        finally:
            # Cleanup
            os.unlink(spec_file)

    def find_minimal_counterexample(self, spec_code: str) -> Optional[Dict[str, Any]]:
        """
        Find smallest counterexample to property.

        Pattern: Use Alloy's built-in scope reduction.
        """
        # Systematically increase scope until counterexample found
        for scope in [3, 5, 7, 10, 15]:
            scoped_spec = add_scope_bounds(spec_code, scope)
            result = self.verify_specification(scoped_spec)

            if result.counterexample:
                return result.counterexample

        return None

def convert_requirement_to_alloy(req: Requirement) -> str:
    """
    Convert requirement to Alloy constraint.

    Examples:
    Req: "Users must have unique IDs"
    -> "all disj u1, u2: User | u1.id != u2.id"

    Req: "Sessions are tied to users"
    -> "all s: Session | s.user != none"
    """

    templates = {
        'unique': 'all disj x1, x2: {entity} | x1.{attr} != x2.{attr}',
        'required': 'all x: {entity} | x.{attr} != none',
        'range': 'all x: {entity} | x.{attr} >= {min} and x.{attr} <= {max}',
        'cardinality': 'all x: {entity} | #{x.{attr}} {op} {count}',
    }

    # Parse requirement and match pattern
    # Then apply template
    pass
```

### 2.5 Instance Interpretation

```python
@dataclass
class AlloyInstance:
    """Parsed Alloy instance (counterexample or solution)."""
    atoms: Dict[str, List[str]]  # sig -> atoms
    relations: Dict[str, List[Tuple[str, str]]]  # relation -> tuples
    univ_size: int

    def explain(self) -> str:
        """Generate human-readable explanation of instance."""
        explanation = []

        for sig, atoms in self.atoms.items():
            explanation.append(f"{sig}: {', '.join(atoms)}")

        for rel, tuples in self.relations.items():
            for t in tuples:
                explanation.append(f"{rel}: {t[0]} -> {t[1]}")

        return '\n'.join(explanation)

def parse_alloy_instance(xml_root: ET.Element) -> AlloyInstance:
    """Parse Alloy's XML output into structured instance."""
    atoms = {}
    relations = {}

    for sig in xml_root.findall(".//sig"):
        sig_name = sig.get('label')
        atom_list = [atom.get('label') for atom in sig.findall(".//atom")]
        atoms[sig_name] = atom_list

    for field in xml_root.findall(".//field"):
        field_name = field.get('label')
        tuples = []
        for tuple_elem in field.findall(".//tuple"):
            from_atom = tuple_elem.find("atom[1]").get('label')
            to_atom = tuple_elem.find("atom[2]").get('label')
            tuples.append((from_atom, to_atom))
        relations[field_name] = tuples

    return AlloyInstance(
        atoms=atoms,
        relations=relations,
        univ_size=len(sum(atoms.values(), []))
    )
```

### 2.6 Requirement Pattern Library

```python
class AlloyRequirementPatterns:
    """Library of requirement-to-Alloy mappings."""

    @staticmethod
    def uniqueness(entity: str, attribute: str) -> str:
        """All instances must have unique attribute."""
        return f"all disj x1, x2: {entity} | x1.{attribute} != x2.{attribute}"

    @staticmethod
    def cardinality(entity: str, relation: str, count: int) -> str:
        """Each entity must have exactly N related items."""
        return f"all x: {entity} | #{x.{relation}} = {count}"

    @staticmethod
    def acyclicity(entity: str, relation: str) -> str:
        """Relation must be acyclic (no cycles)."""
        return f"no x: {entity} | x in x.^{relation}"

    @staticmethod
    def mutual_exclusion(entity: str, attr1: str, attr2: str) -> str:
        """Entity cannot have both attributes simultaneously."""
        return f"all x: {entity} | not (x.{attr1} != none and x.{attr2} != none)"

    @staticmethod
    def implies(condition: str, consequence: str) -> str:
        """Implication constraint."""
        return f"all x | ({condition}) implies ({consequence})"
```

---

## Part 3: TLA+ for Temporal Behavior Specification

### 3.1 Overview

TLA+ (Temporal Logic of Actions) enables:
- Specification of system behavior over time
- Verification of liveness and safety properties
- Model checking with TLC (TLA+ model checker)
- Formal description of distributed system protocols

### 3.2 Core Concepts

**Safety**: "Nothing bad happens" (invariants)
**Liveness**: "Something good eventually happens" (progress)
**Temporal Logic**: Operators like F (eventually), G (always), X (next)
**Actions**: State transitions describing how system evolves

### 3.3 Requirement Specification Pattern

```python
"""
Example: TLA+ specification for requirement workflow

System Requirements:
1. Requirement must progress through states: Draft -> Review -> Approved
2. Only one person can review at a time
3. Once approved, cannot return to draft
4. Reviews must complete within SLA time
"""

TLA_REQUIREMENT_WORKFLOW = """
-------------------------------- MODULE Requirements --------------------------------
EXTENDS Naturals, Sequences

CONSTANT MaxReqs, Reviewers, ReviewTimeLimit

VARIABLE reqs, reviews, clock

(* Requirement states *)
States == {"draft", "review", "approved", "rejected"}

(* Requirement structure *)
Requirement == [
    id: 1..MaxReqs,
    state: States,
    assignee: Reviewers ∪ {"none"}
]

(* Initial state *)
Init ==
    /\\ reqs = [i \\in 1..MaxReqs |-> [id |-> i, state |-> "draft", assignee |-> "none"]]
    /\\ reviews = <<>>
    /\\ clock = 0

(* Requirement submitted for review *)
SubmitForReview(req_id) ==
    /\\ reqs[req_id].state = "draft"
    /\\ reqs' = [reqs EXCEPT ![req_id].state = "review"]
    /\\ reviews' = Append(reviews, [req_id |-> req_id, started |-> clock])
    /\\ clock' = clock + 1

(* Requirement approved *)
Approve(req_id) ==
    /\\ reqs[req_id].state = "review"
    /\\ reqs' = [reqs EXCEPT ![req_id].state = "approved", ![req_id].assignee = "none"]
    /\\ reviews' = reviews  (* Keep review history *)
    /\\ clock' = clock + 1

(* Requirement rejected (returns to draft) *)
Reject(req_id) ==
    /\\ reqs[req_id].state = "review"
    /\\ reqs' = [reqs EXCEPT ![req_id].state = "draft", ![req_id].assignee = "none"]
    /\\ reviews' = reviews
    /\\ clock' = clock + 1

(* Next state *)
Next ==
    \\/ \\exists r \\in 1..MaxReqs: SubmitForReview(r)
    \\/ \\exists r \\in 1..MaxReqs: Approve(r)
    \\/ \\exists r \\in 1..MaxReqs: Reject(r)

(* Specification *)
Spec == Init /\\ [][Next]_<<reqs, reviews, clock>>

(* Invariants (Safety properties) *)

(* Invariant 1: No requirement can go from approved back to draft *)
NoBacktrackFromApproved ==
    \\forall i \\in 1..MaxReqs:
        (reqs[i].state = "approved") ~> (reqs[i].state = "approved")

(* Invariant 2: Once approved, state is permanent *)
ApprovedIsPermanent ==
    \\forall i \\in 1..MaxReqs:
        (reqs[i].state = "approved" => \\forall j \\in 1..MaxReqs: reqs'[i].state = "approved")

(* Invariant 3: Review time SLA *)
SLAViolation ==
    \\exists r \\in reviews:
        (clock - r.started > ReviewTimeLimit) /\\
        (reqs[r.req_id].state \\notin {"approved", "rejected"})

(* Liveness (Progress properties) *)

(* Every requirement eventually gets reviewed *)
EventuallyReviewed ==
    \\forall i \\in 1..MaxReqs: F (reqs[i].state \\in {"approved", "rejected"})

(* Eventually no requirements in review state *)
EventuallyComplete ==
    F (\\forall i \\in 1..MaxReqs: reqs[i].state \\in {"approved", "rejected"})

(* Property to check *)
THEOREM Spec => (NoBacktrackFromApproved /\\ ApprovedIsPermanent)

============================================================================================
"""

@dataclass
class TLASpecification:
    """TLA+ formal specification."""
    module_name: str
    imports: List[str]  # EXTENDS clauses
    constants: List[str]
    variables: List[str]
    init: str  # Initial state formula
    actions: List[str]  # State transition actions
    next: str  # Next state formula
    invariants: List[str]  # Safety properties
    liveness: List[str]  # Liveness properties
    tla_code: str  # Full TLA+ specification
```

### 3.4 Verification Pattern

```python
@dataclass
class TLAVerificationResult:
    """Result of TLA+ model checking."""
    property_satisfied: bool
    error_trace: Optional[List[Dict[str, Any]]]
    trace_length: int
    states_explored: int
    model_check_time_ms: float
    property_name: str

class TLAModelChecker:
    """Wrapper for TLC (TLA+ model checker)."""

    def __init__(self, tlc_path: str = "tlc"):
        self.tlc_path = tlc_path

    def verify_property(
        self,
        tla_spec: str,
        property_name: str,
        config: Dict[str, Any]
    ) -> TLAVerificationResult:
        """
        Verify TLA+ property using TLC.

        Pattern: Generate config, run model checker, parse error trace.
        """
        spec_file = write_temp_tla(tla_spec)
        config_file = write_tlc_config(config)

        try:
            # Run TLC
            result = subprocess.run(
                [self.tlc_path, "-config", config_file, spec_file],
                capture_output=True,
                timeout=300  # 5-minute timeout
            )

            # Parse output
            output = result.stdout.decode()

            if "Invariant" in output and "violated" in output:
                # Property violated - extract error trace
                trace = parse_error_trace(output)
                return TLAVerificationResult(
                    property_satisfied=False,
                    error_trace=trace,
                    trace_length=len(trace),
                    states_explored=extract_state_count(output),
                    model_check_time_ms=extract_time(output),
                    property_name=property_name
                )
            else:
                return TLAVerificationResult(
                    property_satisfied=True,
                    error_trace=None,
                    trace_length=0,
                    states_explored=extract_state_count(output),
                    model_check_time_ms=extract_time(output),
                    property_name=property_name
                )

        finally:
            os.unlink(spec_file)
            os.unlink(config_file)

    def diagnose_completeness(self, spec: TLASpecification) -> CompletenesDiagnosis:
        """
        Check if specification covers all requirements.

        Pattern: Generate liveness properties for each requirement,
                 verify that all are eventually satisfied.
        """
        diagnosis = CompletenesDiagnosis(
            complete=True,
            missing_behaviors=[],
            uncovered_requirements=[]
        )

        for req in spec.requirements:
            property = generate_liveness_property(req)
            result = self.verify_property(spec.tla_code, property.name, {})

            if not result.property_satisfied:
                diagnosis.complete = False
                diagnosis.uncovered_requirements.append(req.id)
                diagnosis.missing_behaviors.append(result.error_trace)

        return diagnosis

@dataclass
class CompletenesDiagnosis:
    """Diagnostic of specification completeness."""
    complete: bool
    missing_behaviors: List[List[Dict[str, Any]]]
    uncovered_requirements: List[str]
```

### 3.5 Requirement Mapping to TLA+

```python
class RequirementToTLA:
    """Convert requirements to TLA+ properties."""

    @staticmethod
    def eventual_progress(requirement_id: str, state_variable: str, target_state: str) -> str:
        """
        Requirement: X must eventually reach state Y.

        TLA+: F (state_variable = target_state)
        """
        return f"F ({state_variable} = \"{target_state}\")"

    @staticmethod
    def invariant_constraint(requirement_id: str, condition: str) -> str:
        """
        Requirement: X must always be true.

        TLA+: G (condition)
        """
        return f"G ({condition})"

    @staticmethod
    def ordering_constraint(req1_id: str, req2_id: str) -> str:
        """
        Requirement: Event 1 must occur before Event 2.

        TLA+: F event1 /\ (event1 ~> F event2)
        """
        return f"F event1 /\\ (event1 ~> F event2)"

    @staticmethod
    def mutual_exclusion(requirement_id: str, var1: str, var2: str) -> str:
        """
        Requirement: Var1 and Var2 cannot both be true.

        TLA+: G \\neg (var1 \\land var2)
        """
        return f"G \\neg ({var1} \\land {var2})"
```

---

## Part 4: Event-B for Refinement-Based Specification

### 4.1 Overview

Event-B provides:
- Mathematical refinement: Abstract model -> Concrete implementation
- Proof obligations: Automatically generated proof requirements
- Tool support: Rodin IDE with automated theorem proving
- Incremental formalization: Start abstract, add detail gradually

### 4.2 Core Concepts

**Machine**: State and events
**Context**: Constants and axioms
**Refinement**: Relationship between abstraction levels
**Proof Obligation**: Property that must be mathematically proved

### 4.3 Specification Pattern

```python
"""
Example: Event-B specification for access control system

Requirements:
1. Users can login/logout
2. Only authenticated users can access resources
3. Sessions are tied to users
4. Concurrent sessions allowed
5. Invalid credentials reject login

Events describe how state changes.
"""

EVENT_B_ACCESS_CONTROL = """
MACHINE AccessControl
SEES AccessContext

VARIABLES
    users,
    authenticated,
    sessions,
    active_sessions

INVARIANTS
    inv1: authenticated ⊆ users
    inv2: sessions ∈ user ↔ ℤ  (bijection to session IDs)
    inv3: active_sessions ⊆ sessions
    inv4: ∀ s ∈ active_sessions · session_expired(s) = FALSE

EVENTS
    INITIALISATION
        then
            users := ∅
            authenticated := ∅
            sessions := ∅
            active_sessions := ∅

    LOGIN
        any u, credentials
        where
            u ∈ users
            verify_credentials(u, credentials) = TRUE
            u ∉ authenticated
        then
            authenticated := authenticated ∪ {u}
            s := new_session(u)
            sessions := sessions ∪ {s}
            active_sessions := active_sessions ∪ {s}

    ACCESS_RESOURCE
        any u, resource
        where
            u ∈ authenticated
            user_authorized(u, resource)
        then
            skip  (unchanged state - read-only access)

    LOGOUT
        any u
        where
            u ∈ authenticated
        then
            authenticated := authenticated \\ {u}
            active_sessions := active_sessions \\ user_sessions(u)

END AccessControl
"""

@dataclass
class EventBMachine:
    """Event-B machine specification."""
    name: str
    variables: List[str]
    invariants: List[str]  # Proof obligations generated from these
    events: List['EventBEvent']
    event_b_code: str

@dataclass
class EventBEvent:
    """Event-B event (state transition)."""
    name: str
    parameters: List[str]
    guards: List[str]  # WHERE clause (preconditions)
    actions: List[str]  # THEN clause (postconditions)
```

### 4.4 Proof Obligation Generation

```python
@dataclass
class ProofObligation:
    """Generated proof obligation."""
    obligation_type: str  # 'invariant_preservation', 'guard_strengthening', etc.
    source: str  # Which machine/event generated this
    hypothesis: List[str]  # Assumptions
    goal: str  # What needs to be proved
    isabelle_syntax: str  # Theorem prover syntax
    automated_proof: Optional[str] = None
    proof_status: str = "open"  # open, proved, disproved

class ProofObligationGenerator:
    """Generate proof obligations from Event-B specifications."""

    def generate_for_invariant_preservation(
        self,
        invariant: str,
        event: EventBEvent,
        previous_state: dict
    ) -> ProofObligation:
        """
        Generate: Invariant I must hold after event E.

        Pattern: For each invariant I and each event E,
                 generate: guards(E) ∧ I_old => I_new
        """
        return ProofObligation(
            obligation_type="invariant_preservation",
            source=f"{event.name}",
            hypothesis=[
                f"∀ v ∈ vars · {invariant}(v_old)",
                *event.guards
            ],
            goal=f"∀ v' ∈ vars' · {invariant}(v')",
            isabelle_syntax=generate_isabelle_proof(invariant, event)
        )

    def generate_for_feasibility(self, event: EventBEvent) -> ProofObligation:
        """
        Generate: Event E can occur (guards are not contradictory).

        Pattern: Prove guards are satisfiable.
        """
        return ProofObligation(
            obligation_type="event_feasibility",
            source=event.name,
            hypothesis=[],
            goal=f"∃ vars · {' ∧ '.join(event.guards)}"
        )

def generate_proof_obligations(machine: EventBMachine) -> List[ProofObligation]:
    """
    Generate all proof obligations for a machine.

    Rules:
    1. Invariant preservation: For each invariant I and event E
    2. Event feasibility: For each event E with guards
    3. Witness strengthening: For refined events
    """
    obligations = []
    generator = ProofObligationGenerator()

    for event in machine.events:
        # Generate invariant preservation obligations
        for invariant in machine.invariants:
            obligations.append(
                generator.generate_for_invariant_preservation(invariant, event, {})
            )

        # Generate feasibility obligation
        obligations.append(generator.generate_for_feasibility(event))

    return obligations
```

### 4.5 Refinement Relationship

```python
@dataclass
class RefinementContext:
    """Links abstract machine to refined implementation."""
    abstract_machine: EventBMachine
    concrete_machine: EventBMachine
    gluing_invariant: str  # Links abstract and concrete variables
    event_correspondence: Dict[str, str]  # abstract_event -> concrete_event

def verify_refinement(context: RefinementContext) -> RefinementProof:
    """
    Verify that concrete machine properly refines abstract machine.

    Pattern: Generate gluing invariant preservation obligations.
    """
    obligations = []

    # For each event in abstract machine
    for abs_event in context.abstract_machine.events:
        concrete_event = context.event_correspondence.get(abs_event.name)

        if concrete_event is None:
            obligations.append(ProofObligation(
                obligation_type="event_correspondence",
                source=abs_event.name,
                hypothesis=[],
                goal=f"Event {abs_event.name} must have concrete counterpart"
            ))
            continue

        # Generate gluing invariant preservation proof
        obligation = ProofObligation(
            obligation_type="refinement_gluing",
            source=f"{abs_event.name} -> {concrete_event.name}",
            hypothesis=[context.gluing_invariant],
            goal=f"After {concrete_event.name}, gluing invariant holds"
        )
        obligations.append(obligation)

    return RefinementProof(
        valid_refinement=all(o.proof_status != "disproved" for o in obligations),
        proof_obligations=obligations
    )

@dataclass
class RefinementProof:
    """Result of refinement verification."""
    valid_refinement: bool
    proof_obligations: List[ProofObligation]
    gluing_invariant_satisfied: bool = True
```

---

## Part 5: SPIN Model Checker for Concurrent Systems

### 5.1 Overview

SPIN (Simple PROMELA Interpreter) verifies:
- Concurrent system behavior (asynchronous processes)
- LTL (Linear Temporal Logic) properties
- Deadlock freedom
- Message queue behavior
- Timing properties

### 5.2 PROMELA Specification Pattern

```python
"""
Example: System with timing requirements

Requirement: Timeout-based recovery
- If request not acknowledged within 5ms, retransmit
- Max 3 retransmissions
- After 3 retries, abort
"""

PROMELA_TIMEOUT_SPEC = """
/* Specification for request-response with timeout */

#define TIMEOUT 5
#define MAX_RETRIES 3

proctype Client(chan out, chan in) {
    int retries = 0;

    do
    :: (retries < MAX_RETRIES) ->
           /* Send request */
           out!request;

           /* Wait for response or timeout */
           if
           :: in?response ->
              printf("Response received\\n")
           :: (1) ->
              printf("Timeout - retrying\\n");
              retries++
           fi
    :: (retries >= MAX_RETRIES) ->
           printf("Max retries exceeded - abort\\n");
           break
    od
}

proctype Server(chan in, chan out) {
    do
    :: in?request ->
           printf("Request received\\n");
           out!response
    od
}

init {
    chan client_to_server = [0] of { bit };
    chan server_to_client = [0] of { bit };

    run Client(client_to_server, server_to_client);
    run Server(client_to_server, server_to_client)
}

/* Safety property: Request-response matching */
ltl always_response { [] (request -> <> response) }

/* Liveness property: Eventually complete */
ltl eventual_termination { <> terminated }
"""

@dataclass
class PROMLEAProcess:
    """PROMELA process definition."""
    name: str
    parameters: List[str]
    channels: List[str]
    states: List[str]
    transitions: List[str]
    variables: Dict[str, str]

@dataclass
class TimingRequirement:
    """Timing constraint for real-time systems."""
    name: str
    trigger: str  # Event that starts timer
    action: str  # Action when timeout occurs
    timeout_ms: int
    max_occurrences: Optional[int] = None
```

### 5.3 LTL Property Specification

```python
class LTLPropertyGenerator:
    """Generate LTL properties for timing requirements."""

    @staticmethod
    def response_time_requirement(
        trigger: str,
        response: str,
        max_time_steps: int
    ) -> str:
        """
        Requirement: Response must occur within N steps of trigger.

        LTL: [] (trigger -> <> response_within_N_steps)
        """
        # Build bounded response formula
        formula = trigger
        for i in range(max_time_steps):
            formula = f"X ({formula})"

        return f"[] ({trigger} -> {formula} {response})"

    @staticmethod
    def mutual_exclusion(var1: str, var2: str) -> str:
        """
        Requirement: var1 and var2 never both true.

        LTL: G !(var1 ∧ var2)
        """
        return f"[] !({var1} && {var2})"

    @staticmethod
    def eventual_termination(termination_flag: str) -> str:
        """
        Requirement: System eventually reaches termination state.

        LTL: F termination_flag
        """
        return f"<> {termination_flag}"

    @staticmethod
    def strict_ordering(event1: str, event2: str) -> str:
        """
        Requirement: Event 1 always precedes Event 2.

        LTL: [] (event2 -> event1_previously_happened)
        """
        return f"[] ({event2} -> <>[] {event1})"

    @staticmethod
    def bounded_occurrence(event: str, max_count: int) -> str:
        """
        Requirement: Event occurs at most N times.

        LTL: Built from conjunction of constraints
        """
        constraints = []
        for i in range(max_count + 1):
            constraints.append(f"event_occurred_{i}_times")
        return " && ".join(constraints)

def verify_timing_requirements(
    promela_spec: str,
    timing_reqs: List[TimingRequirement]
) -> Dict[str, bool]:
    """
    Verify timing requirements against PROMELA spec using SPIN.

    Pattern: Generate LTL properties, run model checker, report results.
    """
    results = {}
    ltl_generator = LTLPropertyGenerator()

    for req in timing_reqs:
        # Generate LTL property from requirement
        ltl_property = ltl_generator.response_time_requirement(
            req.trigger,
            req.action,
            req.timeout_ms
        )

        # Run SPIN model checker
        spec_with_ltl = f"{promela_spec}\nltl {req.name} {{ {ltl_property} }}"
        result = run_spin_model_checker(spec_with_ltl, req.name)

        results[req.name] = result.property_satisfied

    return results
```

### 5.4 Deadlock Detection

```python
@dataclass
class DeadlockAnalysis:
    """Analysis of potential deadlock states."""
    has_deadlock: bool
    deadlock_states: List[Dict[str, Any]]
    vulnerable_interactions: List[str]
    mitigation_strategies: List[str]

def analyze_deadlock_risk(promela_spec: str) -> DeadlockAnalysis:
    """
    Detect potential deadlock in concurrent specification.

    Pattern: Run SPIN with deadlock detection enabled,
             analyze state graph for cycles with no progress.
    """
    result = subprocess.run(
        ["spin", "-a", spec_file],
        capture_output=True
    )

    # Compile verifier
    subprocess.run(["gcc", "-o", "pan", "pan.c"])

    # Run with deadlock detection
    output = subprocess.run(
        ["./pan", "-a"],
        capture_output=True
    )

    if b"deadlock" in output.stdout:
        # Extract deadlock trace
        deadlock_states = parse_deadlock_trace(output.stdout)

        return DeadlockAnalysis(
            has_deadlock=True,
            deadlock_states=deadlock_states,
            vulnerable_interactions=extract_interactions(deadlock_states),
            mitigation_strategies=generate_mitigations(deadlock_states)
        )

    return DeadlockAnalysis(has_deadlock=False, deadlock_states=[])
```

---

## Part 6: Design by Contract (Eiffel-Style)

### 6.1 Overview

Design by Contract specifies:
- **Preconditions**: What must be true before operation
- **Postconditions**: What must be true after operation
- **Invariants**: What must always be true
- **Class invariants**: Properties that characterize valid object state

### 6.2 Core Data Structures

```python
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

class ContractViolation(str, Enum):
    """Types of contract violations."""
    PRECONDITION = "precondition_violated"
    POSTCONDITION = "postcondition_violated"
    INVARIANT = "invariant_violated"
    CLASS_INVARIANT = "class_invariant_violated"

@dataclass
class Contract:
    """Formal contract for operation."""
    operation_name: str
    preconditions: List[Callable]  # (self) -> bool
    postconditions: List[Callable]  # (self, result) -> bool
    class_invariants: List[Callable]  # (self) -> bool
    documentation: str
    retry_policy: Optional['RetryPolicy'] = None

@dataclass
class ContractViolationReport:
    """Report of contract violation."""
    violation_type: ContractViolation
    operation: str
    condition_text: str
    state: Dict[str, Any]
    timestamp: datetime
    remediation: Optional[str] = None
```

### 6.3 Implementation Pattern

```python
from functools import wraps
from typing import Any, TypeVar, Callable

T = TypeVar('T')

def contract(
    preconditions: List[Callable] = None,
    postconditions: List[Callable] = None,
    class_invariants: List[Callable] = None
):
    """
    Decorator to enforce contract on method.

    Pattern: Check preconditions before, postconditions after,
             class invariants always.
    """
    preconditions = preconditions or []
    postconditions = postconditions or []
    class_invariants = class_invariants or []

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> T:
            # Check class invariants (precondition for entire object)
            for invariant in class_invariants:
                if not invariant(self):
                    raise ContractViolationError(
                        f"Class invariant violated before {func.__name__}"
                    )

            # Check preconditions
            for precond in preconditions:
                if not precond(self, *args, **kwargs):
                    raise PreconditionViolationError(
                        f"Precondition failed for {func.__name__}"
                    )

            # Execute operation
            result = func(self, *args, **kwargs)

            # Check postconditions
            for postcond in postconditions:
                if not postcond(self, result, *args, **kwargs):
                    raise PostconditionViolationError(
                        f"Postcondition failed for {func.__name__}"
                    )

            # Verify class invariants still hold
            for invariant in class_invariants:
                if not invariant(self):
                    raise ContractViolationError(
                        f"Class invariant violated after {func.__name__}"
                    )

            return result

        return wrapper

    return decorator

class BankAccount:
    """Example: Bank account with contracts."""

    def __init__(self, initial_balance: float):
        self.balance = initial_balance

    # Class invariant: balance must be non-negative
    def invariant_non_negative_balance(self) -> bool:
        return self.balance >= 0

    # Class invariant: balance is numeric
    def invariant_numeric_balance(self) -> bool:
        return isinstance(self.balance, (int, float))

    def precond_sufficient_funds(self, amount: float) -> bool:
        return amount <= self.balance

    def precond_positive_amount(self, amount: float) -> bool:
        return amount > 0

    def postcond_balance_decreased(self, result: float, amount: float) -> bool:
        return self.balance == result - amount

    @contract(
        preconditions=[
            lambda self, amount: amount > 0,
            lambda self, amount: amount <= self.balance
        ],
        postconditions=[
            lambda self, result, amount: self.balance == result - amount
        ],
        class_invariants=[
            lambda self: self.balance >= 0
        ]
    )
    def withdraw(self, amount: float) -> float:
        """
        Withdraw money from account.

        Preconditions:
        - Amount must be positive
        - Sufficient funds available

        Postconditions:
        - Balance decreases by amount

        Invariants:
        - Balance never negative
        """
        old_balance = self.balance
        self.balance -= amount
        return old_balance
```

### 6.4 Requirement Expression as Contracts

```python
class RequirementToContract:
    """Convert requirements to contract specifications."""

    @staticmethod
    def functional_requirement_to_contract(req: FunctionalRequirement) -> Contract:
        """
        Convert functional requirement to method contract.

        Example:
        Req: "System must authenticate user with username/password"

        Becomes:
        - Precond: username and password provided
        - Postcond: returns User or None
        - Invariant: session never created for unauth user
        """

        # Parse requirement text to extract conditions
        preconditions = []
        postconditions = []

        if "must authenticate" in req.description.lower():
            preconditions.append(
                lambda self, user, password: user is not None and password is not None
            )
            postconditions.append(
                lambda self, result, user, password:
                    (result is not None) or (result is None)  # Type check
            )

        return Contract(
            operation_name=req.title,
            preconditions=preconditions,
            postconditions=postconditions,
            documentation=req.description
        )

    @staticmethod
    def nonfunctional_requirement_to_invariant(req: NonFunctionalRequirement) -> Callable:
        """
        Convert non-functional requirement to class invariant.

        Example:
        Req: "Response time must be < 100ms"

        Becomes:
        Invariant: last_response_time < 100
        """

        if "response time" in req.description.lower():
            return lambda self: self.last_response_time < 100

        elif "availability" in req.description.lower():
            return lambda self: self.uptime_percentage >= 99.9

        else:
            # Generic invariant - requires manual definition
            return lambda self: True
```

---

## Part 7: OCL (Object Constraint Language)

### 7.1 Overview

OCL enables:
- Constraint specification on UML models
- Invariants on class attributes
- Pre/postconditions on operations
- Derivation rules
- Collection queries

### 7.2 Constraint Pattern

```python
"""
Example: E-commerce system requirements in OCL

Context: Order
  inv order_amount_positive: self.totalAmount > 0
  inv minimum_quantity: self.items->size() > 0
  inv no_duplicate_items: self.items->isUnique(product_id)

Context: Order::submit(payment)
  pre: self.status = #draft
  pre: self.customer->notEmpty()
  pre: self.totalAmount > 0
  post: self.status = #submitted
  post: self.submittedAt = now()
  post: result = true
"""

@dataclass
class OCLConstraint:
    """OCL constraint specification."""
    name: str
    context: str  # Class or operation
    constraint_type: str  # inv, pre, post
    expression: str  # OCL expression
    severity: str  # error, warning, info

@dataclass
class OCLInvariant:
    """Class invariant in OCL."""
    constraint_name: str
    class_name: str
    expression: str
    description: str
    error_message: str

# Example OCL constraints
OCL_E_COMMERCE_CONSTRAINTS = [
    OCLInvariant(
        constraint_name="order_amount_positive",
        class_name="Order",
        expression="self.totalAmount > 0",
        description="Orders must have positive total amount",
        error_message="Order total amount must be greater than 0"
    ),
    OCLInvariant(
        constraint_name="minimum_items",
        class_name="Order",
        expression="self.items->size() > 0",
        description="Orders must contain at least one item",
        error_message="Order must contain at least one item"
    ),
    OCLInvariant(
        constraint_name="no_duplicate_items",
        class_name="Order",
        expression="self.items->isUnique(p | p.id)",
        description="Order cannot have duplicate items",
        error_message="Order contains duplicate products"
    ),
]
```

### 7.3 OCL to Python Translation

```python
class OCLToPythonTranslator:
    """Translate OCL constraints to Python/Z3 expressions."""

    OCL_TO_PYTHON_MAP = {
        'self': 'self',
        '->size()': 'len',
        '->notEmpty()': 'len(...) > 0',
        '->isEmpty()': 'len(...) == 0',
        '->includes()': 'in',
        '->isUnique()': 'len(...) == len(set(...))',
        '->forAll()': 'all',
        '->exists()': 'any',
        'and': 'and',
        'or': 'or',
        'not': 'not',
        'implies': '->',  # Material implication
    }

    @staticmethod
    def translate(ocl_constraint: str) -> str:
        """
        Convert OCL to Python constraint expression.

        Examples:
        OCL: "self.totalAmount > 0"
        Python: "self.totalAmount > 0"

        OCL: "self.items->size() > 0"
        Python: "len(self.items) > 0"

        OCL: "self.items->isUnique(id)"
        Python: "len(self.items) == len(set(i.id for i in self.items))"
        """
        expr = ocl_constraint

        # Replace OCL operations with Python equivalents
        expr = expr.replace('->size()', '.size()')
        expr = expr.replace('.size()', '_len')
        expr = expr.replace('_len', 'len')

        expr = expr.replace('->notEmpty()', '_not_empty')
        expr = expr.replace('_not_empty', '__len__() > 0')

        expr = expr.replace('->isEmpty()', '_is_empty')
        expr = expr.replace('_is_empty', '__len__() == 0')

        return expr

    @staticmethod
    def to_z3_expression(ocl_constraint: str, context: dict) -> str:
        """
        Convert OCL constraint to Z3 formula.

        Pattern: Parse constraint, build Z3 expression for solving.
        """
        # Extract variables from constraint
        variables = re.findall(r'\bself\.(\w+)', ocl_constraint)

        # Build Z3 variables
        z3_vars = {}
        for var in variables:
            if var in context['numeric_fields']:
                z3_vars[var] = Int(var) if context['numeric_fields'][var] == 'int' else Real(var)
            else:
                z3_vars[var] = String(var)

        # Translate constraint
        z3_expr = OCLToPythonTranslator.translate(ocl_constraint)

        return z3_expr
```

### 7.4 Validation Pattern

```python
def validate_ocl_constraints(obj: Any, constraints: List[OCLInvariant]) -> List[str]:
    """
    Validate object against OCL constraints.

    Pattern: Evaluate constraint expressions, collect violations.
    """
    violations = []

    for constraint in constraints:
        try:
            # Translate OCL to Python
            python_expr = OCLToPythonTranslator.translate(constraint.expression)

            # Evaluate in object's context
            result = eval(python_expr, {'self': obj})

            if not result:
                violations.append({
                    'constraint': constraint.constraint_name,
                    'message': constraint.error_message,
                    'expression': constraint.expression
                })
        except Exception as e:
            violations.append({
                'constraint': constraint.constraint_name,
                'error': str(e)
            })

    return violations
```

---

## Part 8: SAT/SMT Solvers for Requirement Conflicts

### 8.1 Overview

SAT (Boolean Satisfiability) and SMT (Satisfiability Modulo Theories) solvers find:
- Unsatisfiable cores (minimal conflict explanations)
- All solutions to constraints
- Optimal solutions (optimization extensions)

### 8.2 Conflict Detection Algorithm

```python
from z3 import *
from typing import List, Set, Tuple

@dataclass
class ConflictExplanation:
    """Minimal explanation of requirement conflict."""
    conflicting_requirements: List[str]
    core_size: int
    resolution_options: List[str]

class RequirementConflictDetector:
    """Use SAT/SMT to find requirement conflicts."""

    def find_conflicts(self, requirements: List[Requirement]) -> List[ConflictExplanation]:
        """
        Find all pairwise and higher-order conflicts.

        Algorithm:
        1. For each subset of requirements
        2. Check if satisfiable together
        3. If not, compute minimal unsat core
        4. Return conflicts sorted by core size
        """
        conflicts = []
        solver = Solver()

        # Add all requirement constraints
        for req in requirements:
            solver.add(self._requirement_to_z3(req))

        # Check overall satisfiability
        if solver.check() == unsat:
            # System is unsatisfiable - find core
            core = solver.unsat_core()
            core_reqs = [self._z3_to_requirement_id(c) for c in core]

            conflicts.append(ConflictExplanation(
                conflicting_requirements=core_reqs,
                core_size=len(core),
                resolution_options=self._suggest_resolutions(core)
            ))

        # Find pairwise conflicts
        for i, req1 in enumerate(requirements):
            for req2 in requirements[i+1:]:
                if self._has_conflict(req1, req2):
                    conflicts.append(ConflictExplanation(
                        conflicting_requirements=[req1.id, req2.id],
                        core_size=2,
                        resolution_options=self._suggest_pairwise_resolution(req1, req2)
                    ))

        return sorted(conflicts, key=lambda c: c.core_size)

    def _has_conflict(self, req1: Requirement, req2: Requirement) -> bool:
        """Check if two requirements conflict."""
        solver = Solver()
        solver.add(self._requirement_to_z3(req1))
        solver.add(self._requirement_to_z3(req2))
        return solver.check() == unsat

    def _requirement_to_z3(self, req: Requirement) -> ExprRef:
        """Convert requirement to Z3 expression."""
        # This would parse requirement constraint_expr
        pass

    def _suggest_resolutions(self, core: List[ExprRef]) -> List[str]:
        """Suggest ways to resolve conflict."""
        suggestions = []

        # Try relaxing each constraint in the core
        for constraint in core:
            suggestions.append(f"Relax: {constraint}")

        # Try removing constraints
        for constraint in core:
            suggestions.append(f"Remove: {constraint}")

        return suggestions[:3]  # Top 3 suggestions
```

### 8.3 Satisfiability Checking

```python
@dataclass
class SatisfiabilityAnalysis:
    """Analysis of requirement set satisfiability."""
    satisfiable: bool
    model: Optional[Dict[str, Any]] = None
    unsat_core: Optional[List[str]] = None
    num_models: int = 0  # May be infinite

def analyze_satisfiability(requirements: List[Requirement]) -> SatisfiabilityAnalysis:
    """
    Comprehensive satisfiability analysis of requirements.

    Pattern: Check SAT, enumerate solutions, find unsat cores.
    """
    solver = Solver()

    # Add all constraints
    for req in requirements:
        solver.add(parse_z3_expression(req.constraint_expr))

    # Check satisfiability
    result = solver.check()

    if result == sat:
        model = solver.model()

        # Count solutions (heuristic: try to find alternatives)
        num_solutions = count_alternate_models(solver, model, max_count=10)

        return SatisfiabilityAnalysis(
            satisfiable=True,
            model={d.name(): model[d] for d in model.decls()},
            num_models=num_solutions
        )

    elif result == unsat:
        core = solver.unsat_core()

        return SatisfiabilityAnalysis(
            satisfiable=False,
            unsat_core=[str(c) for c in core],
            num_models=0
        )

    else:  # unknown
        return SatisfiabilityAnalysis(
            satisfiable=None,  # Unknown
            num_models=-1  # Unknown
        )

def count_alternate_models(solver: Solver, model: ModelRef, max_count: int = 10) -> int:
    """Count how many solutions exist for satisfiable formula."""
    count = 1

    for i in range(max_count - 1):
        # Add constraint to exclude current model
        exclusion = Not(And([v() == model[v] for v in model.decls()]))

        solver.push()
        solver.add(exclusion)

        if solver.check() == sat:
            count += 1
            model = solver.model()
        else:
            break

        solver.pop()

    return count
```

---

## Part 9: Formal Requirements Languages

### 9.1 KAOS (Knowledge Acquisition in Automated Specification)

```python
"""
KAOS methodology for requirements capture:
- Goals: What the system should achieve
- Objects: What the system manipulates
- Agents: Who/what performs actions
- Operations: How goals are achieved
"""

@dataclass
class KAOSGoal:
    """KAOS goal specification."""
    name: str
    parent_goal: Optional[str] = None
    sub_goals: List[str] = None
    agents_responsible: List[str] = None

    # Refinement relationships
    AND_refinement: List[str] = None  # All sub-goals must be satisfied
    OR_refinement: List[str] = None   # At least one sub-goal must be satisfied

    definition: str = None
    concern: str = None  # Which stakeholder cares about this

class KAOSHierarchy:
    """Goal hierarchy in KAOS."""

    goals: Dict[str, KAOSGoal]

    def compute_goal_refinement_tree(self, goal_id: str) -> Dict:
        """Build AND/OR tree of goal refinements."""
        goal = self.goals[goal_id]

        return {
            'goal': goal.name,
            'and_refinement': [
                self.compute_goal_refinement_tree(g) for g in (goal.AND_refinement or [])
            ],
            'or_refinement': [
                self.compute_goal_refinement_tree(g) for g in (goal.OR_refinement or [])
            ]
        }
```

### 9.2 RSL (Requirements Specification Language)

```python
"""
RSL is a formal notation combining logic and set theory.

Example: Stack ADT specification
"""

RSL_STACK_SPEC = """
object STACK
    type
        Stack = Stack(top: Int, depth: Int)

    value
        empty: Stack = Stack(0, 0)

    axiom
        pop(push(s, x)) = s,
        top(push(s, x)) = x

    operation
        push(s: Stack, x: Int): Stack
            precondition s.depth < MAX_DEPTH
            postcondition
                result.depth = s.depth + 1 ∧
                result.top = x

        pop(s: Stack): Stack
            precondition s.depth > 0
            postcondition
                result.depth = s.depth - 1
end
"""

@dataclass
class RSLSpecification:
    """RSL formal specification."""
    module_name: str
    type_definitions: List[str]
    value_definitions: List[str]
    axioms: List[str]
    operations: List['RSLOperation']

@dataclass
class RSLOperation:
    """RSL operation specification."""
    name: str
    parameters: Dict[str, str]  # name -> type
    return_type: str
    precondition: str
    postcondition: str
```

### 9.3 SysML Constraint Patterns

```python
"""
SysML constraints for system specifications.

Pattern: Parametric diagrams with constraint blocks.
"""

@dataclass
class SysMLConstraintBlock:
    """SysML constraint block definition."""
    name: str
    parameters: Dict[str, str]  # Constraint parameters and types
    constraint_expression: str  # Mathematical expression

    # Examples:
    # Speed constraint: v = d/t (velocity = distance/time)
    # Power constraint: P = V * I (power = voltage * current)
    # Load constraint: stress = force / area

class SysMLConstraintLibrary:
    """Library of common system constraints."""

    # Performance constraints
    RESPONSE_TIME = SysMLConstraintBlock(
        name="ResponseTime",
        parameters={
            "processing_time_ms": "Real",
            "network_latency_ms": "Real",
            "total_response_time_ms": "Real"
        },
        constraint_expression="total_response_time_ms = processing_time_ms + network_latency_ms"
    )

    # Resource constraints
    MEMORY_USAGE = SysMLConstraintBlock(
        name="MemoryUsage",
        parameters={
            "instances": "Int",
            "memory_per_instance_mb": "Real",
            "total_memory_mb": "Real",
            "max_available_mb": "Real"
        },
        constraint_expression="""
        total_memory_mb = instances * memory_per_instance_mb,
        total_memory_mb <= max_available_mb
        """
    )

    # Reliability constraints
    AVAILABILITY = SysMLConstraintBlock(
        name="Availability",
        parameters={
            "uptime_hours": "Real",
            "downtime_hours": "Real",
            "total_hours": "Real",
            "availability_percent": "Real",
            "target_availability": "Real"
        },
        constraint_expression="""
        total_hours = uptime_hours + downtime_hours,
        availability_percent = (uptime_hours / total_hours) * 100,
        availability_percent >= target_availability
        """
    )
```

---

## Part 10: Consistency Checking Algorithms

### 10.1 Conflict Detection Algorithm

```python
from typing import List, Tuple, Set
from dataclasses import dataclass

@dataclass
class RequirementConflict:
    """Identified conflict between requirements."""
    requirement_ids: List[str]
    conflict_type: str  # 'contradiction', 'ordering', 'resource', 'timing'
    severity: str  # 'critical', 'high', 'medium', 'low'
    explanation: str
    resolution_steps: List[str]

class ConsistencyCheckingEngine:
    """Core consistency checking engine."""

    def check_all_conflicts(self, requirements: List[Requirement]) -> List[RequirementConflict]:
        """
        Run all consistency checks on requirement set.

        Algorithm:
        1. Check logical consistency (Z3)
        2. Check temporal consistency (ordering)
        3. Check resource consistency (allocation)
        4. Check performance consistency (timing)
        5. Check safety properties
        """
        conflicts = []

        # 1. Logical consistency
        conflicts.extend(self._check_logical_consistency(requirements))

        # 2. Temporal ordering
        conflicts.extend(self._check_temporal_consistency(requirements))

        # 3. Resource constraints
        conflicts.extend(self._check_resource_consistency(requirements))

        # 4. Performance/timing
        conflicts.extend(self._check_performance_consistency(requirements))

        # 5. Safety properties
        conflicts.extend(self._check_safety_consistency(requirements))

        return conflicts

    def _check_logical_consistency(self, requirements: List[Requirement]) -> List[RequirementConflict]:
        """
        Check for logical contradictions.

        Examples:
        - "Response time < 100ms" + "Response time > 500ms" = UNSAT
        - "System always available" + "Daily maintenance window" = UNSAT
        """
        conflicts = []
        solver = Solver()

        # Add all constraints
        constraint_map = {}
        for req in requirements:
            z3_expr = self._requirement_to_z3(req)
            solver.add(z3_expr)
            constraint_map[str(z3_expr)] = req.id

        # Check overall consistency
        if solver.check() == unsat:
            core = solver.unsat_core()
            core_req_ids = [constraint_map[str(c)] for c in core if str(c) in constraint_map]

            conflicts.append(RequirementConflict(
                requirement_ids=core_req_ids,
                conflict_type="logical_contradiction",
                severity="critical",
                explanation=f"Requirements {core_req_ids} are logically inconsistent",
                resolution_steps=[
                    f"Review requirement constraints",
                    f"Adjust bounds/thresholds",
                    f"Separate into alternatives"
                ]
            ))

        return conflicts

    def _check_temporal_consistency(self, requirements: List[Requirement]) -> List[RequirementConflict]:
        """
        Check for temporal ordering conflicts.

        Examples:
        - Event A must occur before Event B
        - Event B must occur before Event C
        - Event C must occur before Event A (cycle!)
        """
        conflicts = []

        # Extract ordering requirements
        orderings = {}  # event -> list of predecessors
        for req in requirements:
            if "before" in req.description.lower() or "then" in req.description.lower():
                # Parse temporal ordering
                pass

        # Detect cycles using topological sort
        cycles = self._detect_cycles(orderings)

        for cycle_events in cycles:
            conflicts.append(RequirementConflict(
                requirement_ids=cycle_events,
                conflict_type="temporal_cycle",
                severity="critical",
                explanation=f"Cyclic ordering: {' -> '.join(cycle_events)} -> {cycle_events[0]}",
                resolution_steps=[
                    f"Remove one ordering constraint",
                    f"Parallelize conflicting events",
                    f"Introduce intermediate state"
                ]
            ))

        return conflicts

    def _check_resource_consistency(self, requirements: List[Requirement]) -> List[RequirementConflict]:
        """
        Check for resource over-allocation.

        Example:
        - Req1: "Allocate 50% CPU"
        - Req2: "Allocate 60% CPU"
        - Req3: "Allocate 40% CPU"
        - Total: 150% (impossible!)
        """
        conflicts = []

        # Group requirements by resource type
        resource_allocations = {}
        for req in requirements:
            if "allocate" in req.description.lower() or "use" in req.description.lower():
                resource, amount = self._parse_resource_requirement(req)
                if resource not in resource_allocations:
                    resource_allocations[resource] = []
                resource_allocations[resource].append((req.id, amount))

        # Check for over-allocation
        for resource, allocations in resource_allocations.items():
            total = sum(amount for _, amount in allocations)
            if total > 100:  # Assuming percentages
                conflict_reqs = [req_id for req_id, _ in allocations]

                conflicts.append(RequirementConflict(
                    requirement_ids=conflict_reqs,
                    conflict_type="resource_overallocation",
                    severity="high",
                    explanation=f"Resource '{resource}' over-allocated: {total}% > 100%",
                    resolution_steps=[
                        f"Reduce allocation percentages",
                        f"Prioritize requirements",
                        f"Add resources",
                        f"Serialize conflicting allocations"
                    ]
                ))

        return conflicts

    def _check_performance_consistency(self, requirements: List[Requirement]) -> List[RequirementConflict]:
        """
        Check for performance impossibilities.

        Examples:
        - "Low latency required" + "Comprehensive analysis required" might be impossible
        - "Maximum 100 requests/sec" + "Process each request in 50ms" might be infeasible
        """
        conflicts = []

        # Use Z3 with timing theory
        solver = Solver()

        for req in requirements:
            if req.requirement_type == RequirementType.NON_FUNCTIONAL:
                # Add performance constraint
                solver.add(self._nonfunctional_to_z3(req))

        if solver.check() == unsat:
            core = solver.unsat_core()
            core_reqs = [str(c) for c in core]

            conflicts.append(RequirementConflict(
                requirement_ids=core_reqs,
                conflict_type="performance_impossibility",
                severity="high",
                explanation="Performance requirements are infeasible when combined",
                resolution_steps=[
                    f"Relax performance bounds",
                    f"Optimize algorithms",
                    f"Add parallelization",
                    f"Increase hardware resources"
                ]
            ))

        return conflicts

    def _check_safety_consistency(self, requirements: List[Requirement]) -> List[RequirementConflict]:
        """
        Check for safety violations.

        Examples:
        - "Allow user to delete any file" + "Never lose critical data" (conflicting)
        - "Maximize performance" + "Minimize power consumption" (may conflict)
        """
        conflicts = []

        # This would require domain-specific safety rule bases
        # For now, pattern-based detection

        safety_keywords = ["never", "always", "critical", "must not"]
        performance_keywords = ["maximize", "minimize", "fast", "efficient"]

        safety_reqs = [r for r in requirements if any(k in r.description.lower() for k in safety_keywords)]
        perf_reqs = [r for r in requirements if any(k in r.description.lower() for k in performance_keywords)]

        # Check for known conflicting patterns
        for safety_req in safety_reqs:
            for perf_req in perf_reqs:
                if self._are_likely_conflicting(safety_req, perf_req):
                    conflicts.append(RequirementConflict(
                        requirement_ids=[safety_req.id, perf_req.id],
                        conflict_type="safety_performance_tradeoff",
                        severity="medium",
                        explanation=f"Safety requirement may conflict with performance requirement",
                        resolution_steps=[
                            f"Clarify priority between safety and performance",
                            f"Establish acceptable tradeoffs",
                            f"Use monitoring/throttling to balance"
                        ]
                    ))

        return conflicts

    def _detect_cycles(self, graph: Dict) -> List[List[str]]:
        """Detect cycles in directed graph using DFS."""
        # Standard cycle detection algorithm
        pass

    def _are_likely_conflicting(self, req1: Requirement, req2: Requirement) -> bool:
        """Use heuristics to detect likely conflicts."""
        # Simple pattern matching - in practice would use ML model
        conflict_patterns = [
            ("delete", "never lose"),
            ("maximize", "minimize"),
            ("always available", "maintenance"),
        ]

        for pattern1, pattern2 in conflict_patterns:
            if (pattern1 in req1.description.lower() and pattern2 in req2.description.lower()) or \
               (pattern2 in req1.description.lower() and pattern1 in req2.description.lower()):
                return True

        return False
```

### 10.2 Integration with TraceRTM

```python
# Add to Specification service

class SpecificationVerificationService:
    """Service for formal verification of specifications."""

    def __init__(self, db_session):
        self.db = db_session
        self.consistency_engine = ConsistencyCheckingEngine()
        self.z3_analyzer = AlloyAnalyzer()
        self.tla_checker = TLAModelChecker()

    async def verify_specification_consistency(self, spec_id: str) -> VerificationReport:
        """
        Run comprehensive formal verification on specification.

        Returns: Summary of all verification results
        """
        spec = await self.db.get_specification(spec_id)
        requirements = await self.db.get_requirements(spec_id)

        # Run consistency checks
        conflicts = self.consistency_engine.check_all_conflicts(requirements)

        # Run Z3 constraint solving
        z3_results = self._verify_z3_constraints(requirements)

        # Run TLA+ temporal verification if applicable
        tla_results = None
        if spec.has_timing_requirements:
            tla_results = self._verify_temporal_properties(spec, requirements)

        # Generate report
        return VerificationReport(
            spec_id=spec_id,
            overall_consistent=len(conflicts) == 0 and z3_results.satisfiable,
            logical_conflicts=conflicts,
            z3_verification=z3_results,
            temporal_verification=tla_results,
            recommendations=self._generate_recommendations(conflicts, z3_results)
        )

    def _generate_recommendations(self, conflicts: List, results) -> List[str]:
        """Generate recommendations for resolving issues."""
        recommendations = []

        for conflict in conflicts:
            recommendations.extend(conflict.resolution_steps)

        return recommendations

# Add database fields to Specification model
class Specification(Base, TimestampMixin):
    # ... existing fields ...

    # Formal verification fields
    verification_status: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        comment="Status of formal verification: verified/has_conflicts/in_progress"
    )

    detected_conflicts: Mapped[list[dict]] = mapped_column(
        JSONType,
        nullable=True,
        comment="List of detected requirement conflicts"
    )

    z3_constraints: Mapped[list[str]] = mapped_column(
        JSONType,
        nullable=True,
        comment="Z3-formatted constraints for verification"
    )

    tla_specification: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="TLA+ specification for temporal verification"
    )

    last_verification_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
```

---

## Integration Roadmap

### Phase 1: Foundation (Week 1-2)
1. Implement Z3 constraint solver integration
2. Add basic OCL constraint validation
3. Create requirement-to-formula translation layer

### Phase 2: Advanced Verification (Week 3-4)
1. Implement Alloy analyzer integration
2. Add conflict detection algorithm
3. Build TLA+ temporal verification support

### Phase 3: Tool Integration (Week 5-6)
1. Integrate SPIN model checker for concurrent systems
2. Add Event-B refinement checking
3. Implement SAT/SMT solver wrapper

### Phase 4: UI & Reporting (Week 7-8)
1. Build verification result dashboard
2. Create conflict visualization
3. Generate formal verification reports

---

## Conclusion

This research provides:

1. **Theoretical Foundations**: Understanding formal methods applicable to requirements
2. **Practical APIs**: Code patterns for integrating verification tools
3. **Data Structures**: TraceRTM-compatible models for formal specifications
4. **Implementation Guidance**: Step-by-step integration roadmap
5. **Conflict Detection**: Algorithms for finding requirement inconsistencies

Key Insights:
- Z3 SMT solver best for consistency checking and conflict detection
- Alloy for relational specification and instance generation
- TLA+ for temporal properties and concurrent system verification
- Event-B for refinement-based development
- OCL for constraint specification on object models
- SPIN for model checking concurrent systems

The integration creates a comprehensive formal verification capability within TraceRTM's specification system, enabling teams to catch contradictions, verify completeness, and ensure temporal properties are satisfied.

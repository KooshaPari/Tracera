# Formal Verification Tools - Comparison Matrix

## Tool Comparison at a Glance

### Quick Comparison Matrix

| Aspect | Z3 | Alloy | TLA+ | Event-B | SPIN | PyEiffel | OCL |
|--------|----|----|------|---------|------|----------|-----|
| **Constraint Solving** | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ | ★★★☆☆ | ★★★★☆ |
| **Ease of Use** | ★★★★☆ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ | ★★★★★ | ★★★★☆ |
| **Performance** | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★★★☆ |
| **Scalability** | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★★★☆ |
| **Learning Curve** | ★★★★☆ | ★★★★☆ | ★★☆☆☆ | ★★☆☆☆ | ★★☆☆☆ | ★★★★★ | ★★★★☆ |
| **Cost** | ✓ Free | ✓ Free | ✓ Free | ✓ Free | ✓ Free | ✓ Free | ✓ Free |

---

## Detailed Comparison

### 1. Problem Types Each Tool Solves

#### Z3 (Theorem Prover)
**Best For**: Constraint satisfaction, logical consistency

```
Problems Solved:
✓ "Response time < 100ms AND Response time > 500ms" (contradiction)
✓ "CPU < 50% AND GPU < 50% AND Total < 80%" (feasibility)
✓ "If user.role = Admin then can_delete_file = True" (logic)
✓ Find satisfying assignment for constraints

NOT Good For:
✗ Temporal/ordering requirements
✗ Concurrent system behavior
✗ Distributed protocol verification
```

#### Alloy (Relational Analyzer)
**Best For**: Structural specification, model generation

```
Problems Solved:
✓ "Each user has exactly one active session" (structure)
✓ "No orphaned records in database" (integrity)
✓ Generate example instances of system
✓ Validate domain models

NOT Good For:
✗ Continuous/numeric constraints
✗ Temporal behavior
✗ Performance/timing requirements
```

#### TLA+ (Temporal Logic)
**Best For**: System behavior, temporal properties

```
Problems Solved:
✓ "Event A must occur before Event B" (ordering)
✓ "System eventually reaches ready state" (liveness)
✓ "Request always gets response within 100ms" (timing)
✓ "No deadlock can occur" (safety)

NOT Good For:
✗ Simple constraint checking
✗ Large constraint sets
✗ Continuous-time systems
```

#### Event-B (Refinement)
**Best For**: Incremental formalization, proof-based development

```
Problems Solved:
✓ "Refine abstract state machine to concrete" (refinement)
✓ "Prove invariant preservation" (correctness)
✓ "Model state transitions with proofs" (rigor)

NOT Good For:
✗ Quick verification
✗ Performance constraints
✗ Unstructured requirements
```

#### SPIN (Model Checker)
**Best For**: Concurrent systems, message passing

```
Problems Solved:
✓ "Two processes never access resource simultaneously" (mutual exclusion)
✓ "System never deadlocks" (deadlock freedom)
✓ "Message queue size never exceeds 100" (bounded resources)

NOT Good For:
✗ Single-threaded systems
✗ Continuous constraints
✗ Non-deterministic timing
```

#### Design by Contract
**Best For**: Operation-level specifications

```
Problems Solved:
✓ "Function precondition: balance > 0" (operation contract)
✓ "Function postcondition: balance decreases by amount" (contract)
✓ "Class invariant: balance >= 0 always" (invariant)

NOT Good For:
✗ System-level requirements
✗ Timing requirements
✗ Distributed systems
```

#### OCL (Object Constraints)
**Best For**: UML model constraints, object properties

```
Problems Solved:
✓ "Order.items->forAll(price > 0)" (collection constraint)
✓ "Customer.age >= 18" (property constraint)
✓ "Order.total = items->sum(price)" (derivation rule)

NOT Good For:
✗ Performance constraints
✗ Temporal requirements
✗ Non-OOP systems
```

---

## Scalability Analysis

### Maximum Problem Size by Tool

| Tool | Max Constraints | Max Variables | Max Entities | Max Processes |
|------|-----------------|---------------|--------------|---------------|
| Z3 | 10,000+ | 1,000+ | N/A | N/A |
| Alloy | ~1,000 | ~500 | ~200 signatures | N/A |
| TLA+ | ~100 | ~500 | N/A | ~20 |
| Event-B | ~500 | ~200 | ~100 states | N/A |
| SPIN | ~500 | ~200 | N/A | ~50 processes |
| PyEiffel | Unlimited | Unlimited | N/A | N/A |
| OCL | ~500 | ~200 | ~100 classes | N/A |

---

## Integration Complexity

### Integration Effort Score (1-10 scale)

```
Quick Integration (< 1 week):
  Design by Contract        1/10
  PyEiffel decorators       2/10
  OCL validators            3/10
  Z3 (basic)                4/10

Medium Integration (1-2 weeks):
  Z3 (full)                 5/10
  Alloy (basic)             6/10

Complex Integration (2+ weeks):
  Alloy (advanced)          7/10
  TLA+                      8/10
  Event-B                   8/10
  SPIN                      7/10
```

---

## Performance Profile

### Execution Time Benchmarks

```
Typical Specification Verification Time:

Problem Size: 50 constraints, 30 variables

Tool                  Time        Timeout Risk
Design by Contract    < 1ms       Never
Z3                    10-100ms    Low
OCL                   50-500ms    Low
Alloy                 1-10s       Medium
SPIN                  2-20s       Medium
TLA+                  5-60s       Medium-High
Event-B (proving)     1-60s       Medium-High
```

---

## Feature Capability Matrix

### What Each Tool Can Do

| Feature | Z3 | Alloy | TLA+ | Event-B | SPIN | Contract | OCL |
|---------|----|----|------|---------|------|----------|-----|
| **Satisfiability** | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ~ |
| **Counterexample** | ✓ | ✓ | ✓ | ~ | ✓ | ✗ | ~ |
| **Proof** | ~ | ~ | ✓ | ✓ | ~ | ✗ | ✗ |
| **Instance Gen** | ✓ | ✓ | ✓ | ~ | ~ | ✗ | ✗ |
| **Temporal Props** | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ |
| **Concurrency** | ✗ | ✗ | ✓ | ~ | ✓ | ✗ | ✗ |
| **Refinement** | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| **Automation** | High | High | Low | Low | Medium | High | High |

Legend: ✓ = Full support, ~ = Partial support, ✗ = Not supported

---

## Selection Decision Tree

```
START: "What do I need to verify?"

├─ "Simple constraint satisfaction?"
│  ├─ "With linear arithmetic only?"
│  │  └─> Z3 (BEST)
│  ├─ "With complex logic?"
│  │  └─> Z3 (BEST) + Alloy (validate structure)
│  └─ "Just operation contracts?"
│     └─> Design by Contract (BEST)
│
├─ "System structure/integrity?"
│  ├─ "Relational constraints?"
│  │  └─> Alloy (BEST)
│  ├─ "UML/object constraints?"
│  │  └─> OCL (BEST)
│  └─> Z3 (as fallback)
│
├─ "Temporal/ordering requirements?"
│  ├─ "Timing constraints (ms precision)?"
│  │  └─> TLA+ (BEST)
│  ├─ "Event ordering?"
│  │  └─> TLA+ (BEST)
│  ├─ "Concurrent processes?"
│  │  └─> SPIN (BEST) or TLA+
│  └─> Event-B (if need proofs)
│
├─ "Distributed systems?"
│  ├─ "Message passing?"
│  │  └─> SPIN (BEST)
│  ├─ "Protocol verification?"
│  │  └─> TLA+ (BEST)
│  └─> Event-B (if need formal proofs)
│
└─ "Need formal proofs?"
   ├─ "Invariant preservation?"
   │  └─> Event-B (BEST)
   ├─ "Correctness proofs?"
   │  └─> Event-B (BEST) + Coq/Isabelle
   └─> TLA+ (has proof assistant connection)
```

---

## Combination Strategies

### Multi-Tool Verification Stack

#### Stack 1: Quick Verification (Z3 + Design by Contract)
```
Use Case: Web application with REST API

1. Design by Contract: Operation-level contracts
   - API endpoint preconditions/postconditions
   - Data model invariants

2. Z3: System-level consistency
   - Requirement constraint checking
   - Resource allocation verification

Time: 1-2 weeks to deploy
Cost: Free
Benefit: Fast, immediate ROI
```

#### Stack 2: Complete Verification (Z3 + TLA+ + Event-B)
```
Use Case: Mission-critical system

1. Z3: Constraint satisfaction
   - Requirements consistency
   - Configuration validation

2. TLA+: Temporal properties
   - System behavior verification
   - Ordering/timing requirements

3. Event-B: Refinement proofs
   - Architecture → Implementation proofs
   - Invariant preservation

Time: 6-8 weeks to deploy
Cost: Free
Benefit: Maximum assurance
```

#### Stack 3: Distributed Systems (SPIN + TLA+)
```
Use Case: Microservices, message-based system

1. SPIN: Concurrent behavior
   - Deadlock-freedom
   - Message queue bounds

2. TLA+: Protocol specification
   - Message ordering
   - Consistency guarantees

Time: 4-6 weeks to deploy
Cost: Free
Benefit: High confidence in protocols
```

#### Stack 4: Data Integrity (Alloy + Z3)
```
Use Case: Database-heavy application

1. Alloy: Structural constraints
   - Database schema validation
   - Referential integrity

2. Z3: Numeric constraints
   - Balance/allocation constraints
   - Computed field validation

Time: 2-3 weeks to deploy
Cost: Free
Benefit: Data consistency guarantee
```

---

## Language Syntax Comparison

### Same Requirement, Different Tools

**Natural Language Requirement**:
> "Every order must have at least one item, and total amount must be positive"

#### Z3 (Python)
```python
from z3 import *

order_id = Int('order_id')
item_count = Int('item_count')
total_amount = Real('total_amount')

solver = Solver()
solver.add(item_count >= 1)  # At least one item
solver.add(total_amount > 0)  # Positive amount

assert solver.check() == sat
```

#### Alloy
```alloy
sig Order {
    items: set Item,
    total: Int
}

fact valid_orders {
    all o: Order | {
        #o.items > 0              // At least one item
        o.total > 0               // Positive amount
    }
}
```

#### TLA+
```tla
INIT == orders = {}

OrderValid(order) ==
    /\ Cardinality(order.items) > 0
    /\ order.total > 0

Invariant == ∀ order ∈ orders : OrderValid(order)
```

#### Event-B (Machine)
```event_b
INVARIANT
    inv1: ∀ o ∈ orders · #(o.items) > 0
    inv2: ∀ o ∈ orders · o.total > 0
```

#### OCL
```ocl
context Order
  inv at_least_one_item: self.items->size() > 0
  inv positive_total: self.total > 0
```

#### Design by Contract
```python
@contract(
    preconditions=[
        lambda self: len(self.items) > 0,
        lambda self: self.total > 0
    ]
)
def submit_order(self):
    pass
```

---

## Typical Problem Solving Times

### From Requirement to Verification

```
Problem Type                          Z3    Alloy  TLA+  Event-B  SPIN
─────────────────────────────────────────────────────────────────────
Constraint conflict detection        2h    4h     N/A   N/A      N/A
Database integrity constraints       3h    1h     N/A   N/A      N/A
API contract specification           1h    2h     N/A   N/A      N/A
System state machine                 3h    2h     4h    8h       N/A
Concurrent protocol                  N/A   N/A    6h    10h      4h
Timing requirements                  2h    N/A    3h    N/A      3h
Invariant proof                       N/A   N/A    5h    2h       N/A
```

---

## Tool Ecosystem & Community

| Tool | Community Size | Support | Learning Resources | IDE Support |
|------|---|---|---|---|
| Z3 | Large | Excellent | Extensive | VSCode, IDE plugins |
| Alloy | Medium | Good | Good | Built-in IDE |
| TLA+ | Medium | Good | Video courses | VSCode plugin |
| Event-B | Small | Good | Documentation | Rodin IDE |
| SPIN | Small | Fair | Research papers | Limited |
| PyEiffel | Small | Fair | Documentation | IDE plugins |
| OCL | Medium | Fair | UML books | UML tools |

---

## Installation & Deployment

### Installation Complexity

```
Easiest (just pip install):
  Z3:                pip install z3-solver
  Design by Contract: pip install pycontracts
  OCL:                pip install pyocl

Medium (needs setup):
  Alloy:    Download JAR, set JAVA_HOME
  SPIN:     Download, compile, add to PATH
  TLA+:     Download, set TLAHOME

Most Complex:
  Event-B:  Install Rodin IDE + plugins
```

---

## Cost Comparison

| Aspect | Z3 | Alloy | TLA+ | Event-B | SPIN | Contract | OCL |
|--------|----|----|------|---------|------|----------|-----|
| **Tool Cost** | Free | Free | Free | Free | Free | Free | Free |
| **Learning** | $0-500 | $0-500 | $500-1000 | $500-1000 | $200-500 | $0-200 | $0-300 |
| **Dev Time** | Low | Low | High | High | Medium | Very Low | Low |
| **Maintenance** | Low | Low | Medium | Medium | Medium | Very Low | Low |
| **Total Cost** | $2-5k | $3-6k | $8-15k | $10-20k | $5-10k | $1-3k | $2-5k |

---

## Recommendation Matrix

### Recommended Tool by Scenario

| Scenario | 1st Choice | 2nd Choice | Notes |
|----------|-----------|-----------|-------|
| REST API contracts | Design by Contract | Z3 | Fast, high value |
| Database integrity | Alloy | Z3 | Structure focus |
| Web application | Z3 + Contract | OCL | Practical combination |
| Microservices | SPIN + TLA+ | Event-B | Distributed focus |
| Real-time system | TLA+ | Event-B | Timing critical |
| Safety-critical | Event-B | TLA+ + SPIN | Maximum assurance |
| ML system | Z3 | Alloy | Constraint-heavy |
| Simple constraints | Z3 | Contract | Best effort |
| Complex proofs | Event-B | TLA+ | Formal rigor |

---

## Migration Path

### Starting Point: Quick Value with Z3

```
Week 1-2: Z3 Verification
├─ Constraint parsing
├─ Conflict detection
├─ API integration
└─ ROI: Catch 50% of conflicts early

Week 3-4: Add Design by Contract
├─ API contracts
├─ Operation validation
└─ ROI: Runtime assertion safety

Week 5-6: Add Alloy
├─ Data structure validation
├─ Instance generation
└─ ROI: Data integrity assurance

Week 7+: Add TLA+/Event-B
├─ Temporal properties
├─ Formal proofs
└─ ROI: Maximum assurance
```

This staged approach allows:
- Quick initial deployment (Z3 in 2 weeks)
- Early value demonstration
- Gradual capability expansion
- Learning curve management

---

## Conclusion

### Tool Selection Summary

**For immediate deployment** → **Z3**
- Fastest integration (1-2 weeks)
- Highest immediate ROI (catch 50% of conflicts)
- Lowest learning curve
- Excellent community support

**For complete solution** → **Z3 + TLA+ + Event-B**
- Comprehensive verification (8 weeks)
- Maximum confidence in specifications
- Formal proof capability
- Higher learning investment

**For specific needs**:
- **Distributed systems** → SPIN or TLA+
- **Data integrity** → Alloy
- **Quick wins** → Design by Contract
- **Object models** → OCL

Start with Z3, expand based on adoption and feedback.

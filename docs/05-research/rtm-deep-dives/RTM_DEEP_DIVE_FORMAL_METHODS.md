# Requirements Traceability - Deep Dive: Formal Methods

## Formal Specification Languages

### TLA+ (Temporal Logic of Actions)

TLA+ enables formal specification and verification of requirements:

```tla
---- MODULE RequirementTraceability ----
EXTENDS Integers, Sequences, FiniteSets

CONSTANTS Requirements, Links, LinkTypes

VARIABLES 
    requirements,  \* Set of active requirements
    links,         \* Set of traceability links
    status         \* Requirement status mapping

TypeInvariant ==
    /\ requirements \subseteq Requirements
    /\ links \subseteq Links
    /\ status \in [requirements -> {"draft", "active", "deprecated"}]

\* Requirement must exist before linking
LinkPrecondition ==
    \A link \in links:
        /\ link.source \in requirements
        /\ link.target \in requirements

\* No circular dependencies
NoCircularDependencies ==
    \A req \in requirements:
        LET deps == {link.target : link \in {l \in links : l.source = req}}
        IN req \notin TransitiveClosure(deps)

\* All active requirements must have at least one test
TestCoverage ==
    \A req \in requirements:
        status[req] = "active" =>
            \E link \in links:
                /\ link.source = req
                /\ link.type = "tests"

Init ==
    /\ requirements = {}
    /\ links = {}
    /\ status = [r \in {} |-> "draft"]

CreateRequirement(req) ==
    /\ req \in Requirements
    /\ req \notin requirements
    /\ requirements' = requirements \union {req}
    /\ status' = status @@ (req :> "draft")
    /\ UNCHANGED links

CreateLink(link) ==
    /\ link.source \in requirements
    /\ link.target \in requirements
    /\ link \notin links
    /\ links' = links \union {link}
    /\ UNCHANGED <<requirements, status>>

Next ==
    \/ \E req \in Requirements: CreateRequirement(req)
    \/ \E link \in Links: CreateLink(link)

Spec == Init /\ [][Next]_<<requirements, links, status>>

\* Properties to verify
THEOREM Spec => []TypeInvariant
THEOREM Spec => []LinkPrecondition
THEOREM Spec => []NoCircularDependencies
====
```

### Alloy (Relational Logic)

Alloy for modeling and analyzing requirements:

```alloy
module RequirementTraceability

abstract sig Requirement {
    decomposesTo: set Requirement,
    tests: set TestCase,
    implements: set Code
}

sig Epic extends Requirement {}
sig Feature extends Requirement {}
sig UserStory extends Requirement {}

sig TestCase {
    validates: one Requirement
}

sig Code {
    satisfies: one Requirement
}

// No circular decomposition
fact NoCircularDecomposition {
    no req: Requirement | req in req.^decomposesTo
}

// Every requirement must be tested
fact AllRequirementsTested {
    all req: Requirement | some tc: TestCase | tc.validates = req
}

// Every requirement must be implemented
fact AllRequirementsImplemented {
    all req: Requirement | some code: Code | code.satisfies = req
}

// Hierarchical decomposition
fact HierarchicalDecomposition {
    all epic: Epic | epic.decomposesTo in Feature
    all feature: Feature | feature.decomposesTo in UserStory
    no story: UserStory | some story.decomposesTo
}

// Check for orphaned requirements
pred NoOrphanedRequirements {
    all req: Requirement | 
        (some req.decomposesTo) or 
        (some req.~decomposesTo) or
        (req in Epic)
}

// Run analysis
run NoOrphanedRequirements for 10
check NoCircularDecomposition for 10
```

### Z Notation

Z notation for formal requirement specification:

```z
[REQUIREMENT, TESTCASE, CODE]

RequirementStatus ::= draft | active | deprecated | archived

RequirementSystem
    requirements: ℙ REQUIREMENT
    links: REQUIREMENT ↔ REQUIREMENT
    tests: REQUIREMENT ↔ TESTCASE
    implements: REQUIREMENT ↔ CODE
    status: REQUIREMENT → RequirementStatus

    dom status = requirements
    dom links ⊆ requirements
    ran links ⊆ requirements
    dom tests ⊆ requirements
    dom implements ⊆ requirements

InitRequirementSystem
    RequirementSystem'
    requirements' = ∅
    links' = ∅
    tests' = ∅
    implements' = ∅
    status' = ∅

CreateRequirement
    ΔRequirementSystem
    req?: REQUIREMENT
    
    req? ∉ requirements
    requirements' = requirements ∪ {req?}
    status' = status ∪ {req? ↦ draft}
    links' = links
    tests' = tests
    implements' = implements

CreateLink
    ΔRequirementSystem
    source?, target?: REQUIREMENT
    
    source? ∈ requirements
    target? ∈ requirements
    (source?, target?) ∉ links
    links' = links ∪ {(source?, target?)}
    requirements' = requirements
    status' = status
    tests' = tests
    implements' = implements

TestCoverage
    ΞRequirementSystem
    
    ∀ req: requirements | status(req) = active ⇒
        ∃ tc: TESTCASE | (req, tc) ∈ tests
```

## Property-Based Testing for Requirements

### Hypothesis (Python)

```python
from hypothesis import given, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant

class RequirementTraceabilityMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.requirements = {}
        self.links = []
    
    @rule(req_id=st.text(min_size=1), req_type=st.sampled_from(['epic', 'story', 'task']))
    def create_requirement(self, req_id, req_type):
        """Create a new requirement"""
        if req_id not in self.requirements:
            self.requirements[req_id] = {
                'id': req_id,
                'type': req_type,
                'status': 'draft'
            }
    
    @rule(source=st.text(), target=st.text(), link_type=st.sampled_from(['decomposes_to', 'tests']))
    def create_link(self, source, target, link_type):
        """Create a link between requirements"""
        if source in self.requirements and target in self.requirements:
            self.links.append({
                'source': source,
                'target': target,
                'type': link_type
            })
    
    @invariant()
    def no_circular_dependencies(self):
        """Verify no circular dependencies exist"""
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for link in self.links:
                if link['source'] == node:
                    neighbor = link['target']
                    if neighbor not in visited:
                        if has_cycle(neighbor, visited, rec_stack):
                            return True
                    elif neighbor in rec_stack:
                        return True
            
            rec_stack.remove(node)
            return False
        
        for req_id in self.requirements:
            assert not has_cycle(req_id, set(), set()), f"Circular dependency detected involving {req_id}"
    
    @invariant()
    def all_links_valid(self):
        """Verify all links reference existing requirements"""
        for link in self.links:
            assert link['source'] in self.requirements, f"Invalid source: {link['source']}"
            assert link['target'] in self.requirements, f"Invalid target: {link['target']}"

# Run property-based tests
TestRequirementTraceability = RequirementTraceabilityMachine.TestCase
```

### QuickCheck (Haskell)

```haskell
module RequirementTraceability where

import Test.QuickCheck

data Requirement = Requirement {
    reqId :: String,
    reqType :: RequirementType,
    reqStatus :: Status
} deriving (Show, Eq)

data RequirementType = Epic | Feature | Story | Task
    deriving (Show, Eq, Enum, Bounded)

data Status = Draft | Active | Deprecated
    deriving (Show, Eq, Enum, Bounded)

data Link = Link {
    source :: String,
    target :: String,
    linkType :: LinkType
} deriving (Show, Eq)

data LinkType = DecomposesTo | Tests | Implements
    deriving (Show, Eq, Enum, Bounded)

-- Generators
instance Arbitrary RequirementType where
    arbitrary = arbitraryBoundedEnum

instance Arbitrary Status where
    arbitrary = arbitraryBoundedEnum

instance Arbitrary Requirement where
    arbitrary = Requirement
        <$> arbitrary
        <*> arbitrary
        <*> arbitrary

instance Arbitrary Link where
    arbitrary = Link
        <$> arbitrary
        <*> arbitrary
        <*> arbitraryBoundedEnum

-- Properties
prop_NoSelfLinks :: Link -> Bool
prop_NoSelfLinks link = source link /= target link

prop_AllLinksValid :: [Requirement] -> [Link] -> Bool
prop_AllLinksValid reqs links =
    let reqIds = map reqId reqs
    in all (\link -> source link `elem` reqIds && target link `elem` reqIds) links

prop_NoCircularDependencies :: [Requirement] -> [Link] -> Bool
prop_NoCircularDependencies reqs links =
    let reqIds = map reqId reqs
    in all (\reqId -> not $ hasCycle reqId links []) reqIds
  where
    hasCycle :: String -> [Link] -> [String] -> Bool
    hasCycle node links visited
        | node `elem` visited = True
        | otherwise =
            let neighbors = [target l | l <- links, source l == node]
            in any (\n -> hasCycle n links (node:visited)) neighbors

-- Run tests
main :: IO ()
main = do
    quickCheck prop_NoSelfLinks
    quickCheck prop_AllLinksValid
    quickCheck prop_NoCircularDependencies
```

## Formal Verification Integration

### Linking Requirements to Proofs

```python
class FormalVerification:
    def __init__(self):
        self.requirements = {}
        self.proofs = {}
        self.verification_links = []
    
    def link_requirement_to_proof(self, req_id: str, proof_id: str):
        """Link requirement to formal proof"""
        link = {
            'requirement_id': req_id,
            'proof_id': proof_id,
            'verification_method': 'formal_proof',
            'verified_at': datetime.now()
        }
        self.verification_links.append(link)
    
    def verify_requirement(self, req_id: str) -> bool:
        """Verify requirement using formal methods"""
        req = self.requirements[req_id]
        
        # Convert requirement to formal specification
        formal_spec = self.convert_to_formal_spec(req)
        
        # Run model checker
        result = self.run_model_checker(formal_spec)
        
        if result.verified:
            # Create proof artifact
            proof_id = self.create_proof_artifact(req_id, result)
            self.link_requirement_to_proof(req_id, proof_id)
            return True
        else:
            # Log counterexample
            self.log_counterexample(req_id, result.counterexample)
            return False
```

### Contract-Based Design

```python
from typing import Protocol

class RequirementContract(Protocol):
    """Contract for requirement behavior"""
    
    def precondition(self) -> bool:
        """Precondition that must hold before operation"""
        ...
    
    def postcondition(self) -> bool:
        """Postcondition that must hold after operation"""
        ...
    
    def invariant(self) -> bool:
        """Invariant that must always hold"""
        ...

class CreateRequirementContract:
    def __init__(self, storage: RequirementStorage, req: Requirement):
        self.storage = storage
        self.req = req
    
    def precondition(self) -> bool:
        """Requirement must not already exist"""
        return self.storage.get_requirement(self.req.id) is None
    
    def postcondition(self) -> bool:
        """Requirement must exist after creation"""
        created = self.storage.get_requirement(self.req.id)
        return created is not None and created.id == self.req.id
    
    def invariant(self) -> bool:
        """Total number of requirements must increase by 1"""
        return True  # Checked by caller

def create_requirement_with_contract(storage: RequirementStorage, req: Requirement):
    """Create requirement with contract verification"""
    contract = CreateRequirementContract(storage, req)
    
    # Check precondition
    assert contract.precondition(), "Precondition violated"
    
    # Execute operation
    count_before = len(storage.list_requirements())
    storage.create_requirement(req)
    count_after = len(storage.list_requirements())
    
    # Check postcondition
    assert contract.postcondition(), "Postcondition violated"
    
    # Check invariant
    assert count_after == count_before + 1, "Invariant violated"
```


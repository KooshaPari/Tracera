# Test Oracle Selection & Implementation Decision Framework

## 1. Oracle Selection Decision Tree

```
START: Need to test a system
│
├─ Do you have clear expected outputs?
│  │
│  ├─ YES
│  │  │
│  │  └─ Use Traditional Unit Tests
│  │     (Assert expected == actual)
│  │
│  └─ NO
│     │
│     ├─ Is it an ML/AI system?
│     │  │
│     │  ├─ YES
│     │  │  │
│     │  │  └─ Use METAMORPHIC TESTING
│     │  │     + Property-Based Testing
│     │  │     (MR types: paraphrase invariance, inject robustness)
│     │  │
│     │  └─ NO
│     │     │
│     │     ├─ Can you implement reference version?
│     │     │  │
│     │     │  ├─ YES
│     │     │  │  │
│     │     │  │  └─ Use DIFFERENTIAL TESTING
│     │     │  │     (Compare against reference)
│     │     │  │
│     │     │  └─ NO
│     │     │     │
│     │     │     ├─ Does system have properties/invariants?
│     │     │     │  │
│     │     │     │  ├─ YES
│     │     │     │  │  │
│     │     │     │  │  ├─ Use PROPERTY-BASED TESTING
│     │     │     │  │  │  (Hypothesis/fast-check)
│     │     │     │  │  │
│     │     │     │  │  └─ Use METAMORPHIC RELATIONS
│     │     │     │  │     (Inverse operations, monotonicity)
│     │     │     │  │
│     │     │     │  └─ NO
│     │     │     │     │
│     │     │     │     ├─ Is it a service/API?
│     │     │     │     │  │
│     │     │     │     │  ├─ YES
│     │     │     │     │  │  │
│     │     │     │     │  │  └─ Use CONTRACT TESTING (Pact)
│     │     │     │     │  │
│     │     │     │     │  └─ NO
│     │     │     │     │     │
│     │     │     │     │     └─ Use STATISTICAL ORACLE
│     │     │     │     │        (If probabilistic)
│     │     │     │     │        OR Use CHAOS TESTING
│     │     │     │     │        (If resilience-focused)
│     │     │     │     │
│     │     │     │     └─ Consider FUZZING
│     │     │     │        (Input validation)
```

---

## 2. Oracle Selection Matrix

### By System Type

```
╔════════════════════════╦═════════════════════════════════════════════╗
║ System Type            ║ Recommended Oracles (Priority Order)         ║
╠════════════════════════╬═════════════════════════════════════════════╣
║ Neural Network         ║ 1. Metamorphic (injection robustness)        ║
║ LLM                    ║ 2. Property-based (consistency)              ║
║ Image Classification   ║ 3. Statistical (accuracy bounds)            ║
║                        ║ 4. Differential (if reference exists)        ║
╠════════════════════════╬═════════════════════════════════════════════╣
║ REST API               ║ 1. Contract Testing (Pact)                   ║
║ GraphQL Endpoint       ║ 2. Property-based (schema validation)        ║
║                        ║ 3. Differential (vs reference impl)          ║
║                        ║ 4. Metamorphic (idempotence)                 ║
╠════════════════════════╬═════════════════════════════════════════════╣
║ Data Pipeline          ║ 1. Metamorphic (commutativity, associativity)║
║ ETL Process            ║ 2. Property-based (invariants)               ║
║                        ║ 3. Differential (reference pipeline)         ║
║                        ║ 4. Mutation testing (pipeline integrity)     ║
╠════════════════════════╬═════════════════════════════════════════════╣
║ Distributed System     ║ 1. Chaos Engineering (fault tolerance)       ║
║ Microservices          ║ 2. Contract Testing (boundaries)             ║
║                        ║ 3. Property-based (eventual consistency)     ║
║                        ║ 4. Differential (multi-version)              ║
╠════════════════════════╬═════════════════════════════════════════════╣
║ Compiler/Interpreter   ║ 1. Differential Testing (N-version)          ║
║ Parser                 ║ 2. Metamorphic (syntactic transformations)   ║
║                        ║ 3. Fuzzing (grammar-based)                   ║
║                        ║ 4. Property-based (parse properties)         ║
╠════════════════════════╬═════════════════════════════════════════════╣
║ Mathematical Library   ║ 1. Property-based (mathematical props)       ║
║ DSP Functions          ║ 2. Metamorphic (commutative, distributive)   ║
║                        ║ 3. Differential (reference implementation)   ║
║                        ║ 4. Statistical (numerical precision)         ║
╠════════════════════════╬═════════════════════════════════════════════╣
║ UI Component           ║ 1. Visual Regression Testing                 ║
║ Design System          ║ 2. Property-based (accessibility)            ║
║                        ║ 3. Combinatorial (device × browser)          ║
║                        ║ 4. Contract testing (component API)          ║
╠════════════════════════╬═════════════════════════════════════════════╣
║ Configuration System   ║ 1. Combinatorial Testing (parameter coverage)║
║ Feature Flags          ║ 2. Property-based (invariants)               ║
║                        ║ 3. Metamorphic (configuration equivalence)   ║
║                        ║ 4. Chaos Testing (failure modes)             ║
╚════════════════════════╩═════════════════════════════════════════════╝
```

### By Testing Goal

```
╔════════════════════════════╦═══════════════════════════════════════════╗
║ Testing Goal               ║ Best Oracles                              ║
╠════════════════════════════╬═══════════════════════════════════════════╣
║ Correctness Verification   ║ • Metamorphic Relations                   ║
║ (Does it work?)            ║ • Differential Testing                    ║
║                            ║ • Contract Testing                        ║
╠════════════════════════════╬═══════════════════════════════════════════╣
║ Robustness Testing         ║ • Fuzzing (Grammar-based)                 ║
║ (Can it handle bad input?) ║ • Property-based (input validation)       ║
║                            ║ • Metamorphic (noise injection)           ║
╠════════════════════════════╬═══════════════════════════════════════════╣
║ Performance Validation     ║ • SLO-based Testing                       ║
║ (Is it fast enough?)       ║ • Percentile-based thresholds             ║
║                            ║ • Load profile specification               ║
╠════════════════════════════╬═══════════════════════════════════════════╣
║ Resilience Testing         ║ • Chaos Engineering                       ║
║ (Does it recover?)         ║ • Fault Injection                         ║
║                            ║ • Property-based (recovery properties)    ║
╠════════════════════════════╬═══════════════════════════════════════════╣
║ Regression Detection       ║ • Regression Oracle (intent-aligned)      ║
║ (Did we break something?)  ║ • Visual Regression Testing               ║
║                            ║ • Differential Testing                    ║
╠════════════════════════════╬═══════════════════════════════════════════╣
║ Test Quality Assurance     ║ • Mutation Testing                        ║
║ (Are our tests good?)      ║ • Mutation Score Computation              ║
║                            ║ • Equivalent Mutant Detection             ║
╠════════════════════════════╬═══════════════════════════════════════════╣
║ Integration Testing        ║ • Contract Testing (CDC)                  ║
║ (Do components work?)      ║ • Property-based (integration properties) ║
║                            ║ • Differential (multi-component)          ║
╠════════════════════════════╬═══════════════════════════════════════════╣
║ Coverage Maximization      ║ • Combinatorial Testing                   ║
║ (Are we testing enough?)   ║ • Fuzzing (edge cases)                    ║
║                            ║ • Property-based (boundary conditions)    ║
╚════════════════════════════╩═══════════════════════════════════════════╝
```

---

## 3. Implementation Checklist by Oracle Type

### Metamorphic Testing Checklist

```
PREPARATION:
  ☐ Identify system domain (ML, signal processing, math, etc.)
  ☐ Analyze function properties (commutativity, associativity, etc.)
  ☐ Review academic literature for domain-specific MRs
  ☐ Document known invariants and transformations

IMPLEMENTATION:
  ☐ Define MR 1: Basic property (e.g., commutativity)
  ☐ Define MR 2: Input transformation (e.g., scaling, permutation)
  ☐ Define MR 3: Output relationship (e.g., monotonicity)
  ☐ Implement MR library with base class
  ☐ Create test data generators for inputs
  ☐ Set tolerance levels for floating-point comparisons
  ☐ Implement relation verifier function

VALIDATION:
  ☐ Run MRs against reference implementation
  ☐ Verify MRs catch known bugs
  ☐ Measure MR coverage (% of code paths)
  ☐ Document cost of each MR (expensive vs cheap)
  ☐ Create MR documentation with examples

INTEGRATION:
  ☐ Add to CI/CD pipeline
  ☐ Set failure thresholds
  ☐ Monitor MR execution time
  ☐ Report MR violations in test output
  ☐ Track MR effectiveness over time
```

### Property-Based Testing Checklist

```
PREPARATION:
  ☐ Identify system properties (invariants, postconditions)
  ☐ Analyze valid input space
  ☐ Document business rules and constraints
  ☐ Identify boundary conditions and edge cases

STRATEGY DESIGN:
  ☐ Define base strategies for simple types
  ☐ Create composite strategies for complex objects
  ☐ Add assume() filters for preconditions
  ☐ Design strategies respecting constraint relationships
  ☐ Create model-based state machines (if stateful)

IMPLEMENTATION:
  ☐ Implement first property (basic invariant)
  ☐ Add assumption constraints
  ☐ Configure shrinking behavior
  ☐ Set example counts appropriate for domain
  ☐ Implement custom strategies with @composite
  ☐ Add multiple stateful rules (if applicable)

EXECUTION & TUNING:
  ☐ Run tests and capture shrunk counterexamples
  ☐ Adjust health check settings if needed
  ☐ Measure test execution time
  ☐ Balance thoroughness vs execution time
  ☐ Reproduce failures with captured examples

VALIDATION:
  ☐ Verify properties catch known bugs
  ☐ Check coverage vs traditional tests
  ☐ Document generated test cases
  ☐ Add property to regression test suite
```

### Mutation Testing Checklist

```
SETUP:
  ☐ Install mutation tool (mutmut, Stryker, etc.)
  ☐ Configure mutation operators to use
  ☐ Set equivalent mutant detection strategy
  ☐ Define mutation score thresholds

EXECUTION:
  ☐ Run full mutation suite
  ☐ Generate mutation score report
  ☐ Identify survived mutants
  ☐ Analyze equivalent mutants
  ☐ Review mutant-to-test mapping

ANALYSIS:
  ☐ For each survived non-equivalent mutant:
    ☐ Review mutated code
    ☐ Understand why test didn't catch it
    ☐ Decide if test gap or real mutant
  ☐ Identify patterns in survivors
  ☐ Compute true mutation score

IMPROVEMENT:
  ☐ Write test cases for survived mutants
  ☐ Add assertions for boundary conditions
  ☐ Increase test count if needed
  ☐ Use property-based testing for coverage
  ☐ Re-run mutations to verify improvement

CI/CD INTEGRATION:
  ☐ Add mutation testing to build pipeline
  ☐ Set failure threshold (e.g., 80%)
  ☐ Generate HTML reports for review
  ☐ Track mutation score over time
  ☐ Alert on score regression
```

### Fuzzing Checklist

```
TARGET PREPARATION:
  ☐ Identify input format (binary, text, structured)
  ☐ Define grammar or input schema if structured
  ☐ Create seed corpus with valid examples
  ☐ Write fuzzing harness
  ☐ Add assertions for properties/invariants

TOOL SETUP:
  ☐ Choose fuzzer (libFuzzer, AFL++, grammar-based)
  ☐ Configure timeout and memory limits
  ☐ Set up crash reporting
  ☐ Enable coverage instrumentation
  ☐ Configure mutation operators

EXECUTION:
  ☐ Run fuzzer on small corpus initially
  ☐ Monitor for crashes/hangs
  ☐ Gradually increase corpus size
  ☐ Run extended fuzzing (hours/days)
  ☐ Enable parallel fuzzing if available

CRASH ANALYSIS:
  ☐ Triage crashes (real bug vs edge case)
  ☐ Minimize crash test case
  ☐ Create regression test from crash
  ☐ Fix underlying issue
  ☐ Add test case to seed corpus

INTEGRATION:
  ☐ Add short fuzzing run to CI/CD
  ☐ Maintain crash corpus for regression
  ☐ Track coverage metrics
  ☐ Report bugs discovered by fuzzing
  ☐ Archive corpus periodically
```

### Contract Testing Checklist

```
CONSUMER SIDE:
  ☐ Define expected API contract
  ☐ Create consumer test with Pact
  ☐ Generate contract file (JSON)
  ☐ Verify contract matches actual requests
  ☐ Set up Pact Broker account

PROVIDER SIDE:
  ☐ Review contracts from consumers
  ☐ Implement provider verification tests
  ☐ Verify provider satisfies contract
  ☐ Fix contract violations if needed
  ☐ Publish verification results

INTEGRATION:
  ☐ Set up Pact Broker
  ☐ Configure CI/CD for contract publishing
  ☐ Add "Can I Deploy?" checks
  ☐ Set up contract monitoring
  ☐ Document breaking changes

MAINTENANCE:
  ☐ Review contract changes in PRs
  ☐ Update contracts when API evolves
  ☐ Maintain backward compatibility
  ☐ Document contract versions
  ☐ Monitor consumer/provider alignment
```

### Chaos Engineering Checklist

```
PLANNING:
  ☐ Define hypothesis (what should tolerate what?)
  ☐ Identify failure modes to test
  ☐ Define success criteria
  ☐ Plan monitoring strategy
  ☐ Set up blast radius limits

EXPERIMENT DESIGN:
  ☐ Choose single fault type first
  ☐ Define fault parameters (duration, intensity)
  ☐ Identify target components
  ☐ Plan health checks
  ☐ Document rollback procedure

EXECUTION:
  ☐ Run in staging first
  ☐ Monitor during experiment
  ☐ Collect metrics and logs
  ☐ Verify hypothesis
  ☐ Automatic rollback if needed

ANALYSIS:
  ☐ Review system behavior during chaos
  ☐ Identify gaps in resilience
  ☐ Document findings
  ☐ Prioritize improvements
  ☐ Update runbooks if needed

REMEDIATION:
  ☐ Fix identified gaps
  ☐ Implement circuit breakers/retries
  ☐ Add monitoring/alerting
  ☐ Repeat experiments after fixes
  ☐ Incorporate into regular testing
```

### Performance SLO Checklist

```
SLO DEFINITION:
  ☐ Define latency percentiles (P95, P99, P999)
  ☐ Set error rate thresholds
  ☐ Define availability targets
  ☐ Set throughput requirements
  ☐ Document measurement window

BASELINE ESTABLISHMENT:
  ☐ Measure current performance
  ☐ Calculate percentiles correctly
  ☐ Document hardware/config
  ☐ Establish historical baseline
  ☐ Set realistic targets

TEST IMPLEMENTATION:
  ☐ Create load profile (ramp-up, sustained, spike)
  ☐ Implement load generation (Locust, k6, etc.)
  ☐ Add performance assertions
  ☐ Implement SLO validation logic
  ☐ Create performance test suite

EXECUTION & TUNING:
  ☐ Run baseline performance test
  ☐ Measure against SLOs
  ☐ Identify bottlenecks
  ☐ Tune if needed
  ☐ Validate improvements

CI/CD INTEGRATION:
  ☐ Add performance tests to pipeline
  ☐ Set failure criteria (SLO violations)
  ☐ Generate performance reports
  ☐ Track trends over time
  ☐ Alert on regressions
```

---

## 4. Oracle Combination Patterns

### Pattern 1: ML System Testing Stack

```python
# Recommended for ML models
oracles = [
    MetamorphicOracle([
        ParaphraseInvarianceMR(),
        InjectionRobustnessMR(),
        ScaleInvarianceMR()
    ]),
    PropertyBasedOracle([
        "output_probability_bounds",
        "confidence_monotonicity"
    ]),
    DifferentialOracle(reference_model, test_model),
    StatisticalOracle(accuracy_threshold=0.92),
    MutationTesting(mutation_score_threshold=0.85)
]
```

### Pattern 2: API/Microservice Stack

```python
# Recommended for APIs and microservices
oracles = [
    ContractTestingOracle(pact_definitions),
    PropertyBasedOracle([
        "response_schema_valid",
        "status_code_appropriate",
        "error_handling_consistent"
    ]),
    DifferentialOracle(reference_impl, candidate_impl),
    MutationTesting(mutation_score_threshold=0.80),
    PerformanceSLOOracle(slo_definitions),
    ChaosEngineeringOracle([
        LatencyInjection(),
        ErrorInjection()
    ])
]
```

### Pattern 3: Data Pipeline Stack

```python
# Recommended for ETL/data pipelines
oracles = [
    MetamorphicOracle([
        CommutativityMR(),
        AssociativityMR(),
        InvariantPreservationMR()
    ]),
    PropertyBasedOracle([
        "data_integrity",
        "type_consistency",
        "completeness"
    ]),
    DifferentialOracle(legacy_pipeline, new_pipeline),
    MutationTesting(mutation_score_threshold=0.85),
    CombinatorialOracle(parameter_combinations)
]
```

### Pattern 4: UI Component Stack

```typescript
// Recommended for UI components
const oracles = [
    VisualRegressionOracle(percy_baselines),
    PropertyBasedOracle([
        "accessibility_wcag2a",
        "keyboard_navigable",
        "responsive"
    ]),
    CombinatorialOracle(device_browser_combinations),
    ContractOracle(component_api_spec),
    MutationOracle(mutation_threshold: 0.80)
]
```

---

## 5. Cost vs Effectiveness Matrix

```
╔──────────────────────┬────────────┬──────────┬──────────────┬───────────╗
║ Oracle Type          ║ Setup Cost ║ Run Time ║ Bug Detection║ Maturity  ║
╠──────────────────────┼────────────┼──────────┼──────────────┼───────────╣
║ Metamorphic          ║ Medium     ║ Fast     ║ Very High*   ║ ★★★★☆    ║
║ Property-Based       ║ Low        ║ Medium   ║ High         ║ ★★★★★    ║
║ Differential         ║ High       ║ Medium   ║ Very High    ║ ★★★★☆    ║
║ Contract Testing     ║ Medium     ║ Fast     ║ High         ║ ★★★★☆    ║
║ Mutation Testing     ║ Low        ║ Slow     ║ Indirect**   ║ ★★★★☆    ║
║ Fuzzing              ║ Medium     ║ Slow     ║ Very High    ║ ★★★★☆    ║
║ Chaos Engineering    ║ High       ║ Medium   ║ High         ║ ★★★★☆    ║
║ Visual Regression    ║ Medium     ║ Medium   ║ Medium       ║ ★★★★★    ║
║ Performance SLO      ║ Medium     ║ Slow     ║ Medium       ║ ★★★★☆    ║
║ Combinatorial        ║ Low        ║ Fast     ║ Medium       ║ ★★★☆☆    ║
╚──────────────────────┴────────────┴──────────┴──────────────┴───────────╝

* Especially for ML/AI systems without clear ground truth
** Measures test effectiveness, not directly bugs
```

---

## 6. Quick Decision Table

```
System Type    │ Hard to Test? │ Stateless? │ Oracle Recommendation
─────────────────────────────────────────────────────────────────────
ML Model       │ YES           │ YES        │ Metamorphic + Property
API            │ NO            │ YES        │ Contract + Property
Compiler       │ YES           │ YES        │ Differential + Fuzzing
Database       │ NO            │ YES        │ Property + Contract
Parser         │ NO            │ YES        │ Fuzzing + Property
Microservice   │ NO            │ NO         │ Contract + Chaos
Distributed    │ YES           │ NO         │ Chaos + Property
UI Component   │ NO            │ YES        │ Visual + Property
Data Pipeline  │ NO            │ YES        │ Metamorphic + Property
Config System  │ NO            │ YES        │ Combinatorial + Property
```

---

## 7. Implementation Timeline

### Week 1-2: Foundation
- [ ] Select primary oracle type based on system
- [ ] Set up testing framework
- [ ] Implement basic oracle verification
- [ ] Create 2-3 initial oracles
- [ ] Integrate with test runner

### Week 3-4: Expansion
- [ ] Add second oracle type
- [ ] Implement more comprehensive test data generation
- [ ] Create oracle documentation
- [ ] Set up reporting/metrics
- [ ] Add to CI/CD pipeline

### Week 5-6: Integration
- [ ] Combine multiple oracles
- [ ] Implement unified oracle system
- [ ] Create oracle effectiveness metrics
- [ ] Train team on usage
- [ ] Gather feedback and iterate

### Week 7-8: Hardening
- [ ] Optimize oracle performance
- [ ] Handle edge cases in oracle logic
- [ ] Create runbooks for false positives
- [ ] Monitor oracle effectiveness
- [ ] Plan expansions for new system areas

---

## 8. Success Metrics

```
Metamorphic Testing:
  ✓ MRs defined for major code paths
  ✓ MR coverage >= 70% of codebase
  ✓ MRs catch known bugs/regressions
  ✓ False positive rate < 5%

Property-Based Testing:
  ✓ >= 3 properties per module
  ✓ Shrunk examples reproduce consistently
  ✓ Properties find edge cases
  ✓ Execution time < 2x traditional tests

Mutation Testing:
  ✓ Mutation score >= 80%
  ✓ Equivalent mutants < 5% of total
  ✓ Killed mutants >> Survived mutants
  ✓ Score improving over time

Fuzzing:
  ✓ Crash corpus captured and reproduced
  ✓ Coverage increasing over time
  ✓ Bugs found before users report them
  ✓ Corpus represents diverse inputs

Contract Testing:
  ✓ Consumer and provider tests synchronized
  ✓ "Can I deploy?" checks passing
  ✓ API breaking changes detected early
  ✓ Consumer/provider expectations aligned

Chaos Engineering:
  ✓ Resilience improvements documented
  ✓ Recovery time meeting targets
  ✓ Circuit breakers activating correctly
  ✓ Team confidence in fault tolerance
```

---

## Appendix: Tool Maturity & Adoption (2024-2025)

### Python Ecosystem
```
Hypothesis         ★★★★★  (100K+ weekly downloads, 1000s of OSS projects)
pytest-hypothesis  ★★★★★  (Deep integration with pytest)
mutmut             ★★★★☆  (Most actively maintained mutation tool)
Pact Python        ★★★★☆  (Stable, good documentation)
pytest-benchmark   ★★★★☆  (Performance testing)
```

### JavaScript/TypeScript Ecosystem
```
fast-check         ★★★★★  (Mature, 400K+ weekly downloads)
Stryker            ★★★★★  (Industry standard mutation testing)
Jest               ★★★★★  (Dominant testing framework)
Pact JS            ★★★★☆  (Good contract support)
Playwright         ★★★★★  (Visual & E2E testing)
Chromatic          ★★★★☆  (Visual regression leader)
```

### Cross-Platform
```
libFuzzer          ★★★★★  (LLVM-backed, production-grade)
AFL++              ★★★★★  (Security auditing standard)
Chaos Toolkit      ★★★★☆  (Enterprise chaos engineering)
LitmusChaos        ★★★★☆  (Kubernetes-native chaos)
NIST ACTS          ★★★★☆  (Combinatorial testing gold standard)
```

---

## Conclusion

Use this framework to:
1. **Choose** the right oracle(s) for your system type
2. **Implement** following the provided checklists
3. **Combine** multiple oracles for comprehensive coverage
4. **Measure** effectiveness with provided metrics
5. **Iterate** and improve oracle suite over time

The key insight: **No single oracle suffices**. Effective testing combines multiple oracle strategies appropriate for your specific system characteristics.


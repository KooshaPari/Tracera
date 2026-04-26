# PolicyStack ↔ phenotype-policy-engine Consolidation

**Tracking**: W-51 PyO3 binding integration (2026-04-25)

## Phase-1 Status: IN-PROGRESS

### Components Completed

1. **Rust Policy Engine (phenotype-policy-engine)** ✅
   - ConditionGroup: Named group of evaluation conditions
   - RuleEvaluator: Core rule evaluation engine
   - MatcherKind: Exact, Regex, Contains variants
   - Rule: Single policy rule with conditions and actions
   - OnMismatchAction: Allow, Deny, Skip enum
   - RuleMetadata: Priority and tags tracking
   - Decision: Final policy decision with trace

2. **PyO3 Binding (phenotype-policy-engine-py)** ✅
   - Full FFI surface exposing all 7 core types
   - Type stubs (.pyi) for IDE support
   - maturin wheel builds (arm64-apple-darwin, Python 3.13)
   - crate-type: cdylib for shared library generation

3. **PolicyStack Integration Test Suite** ✅
   - tests/test_pyo3_integration.py: 12 tests, all passing
   - Tests: rule construction, metadata, context evaluation, multi-rule evaluation
   - Integration scenario: ACL rule evaluation against synthetic user context
   - FR-SHARED-001 through FR-SHARED-007 traced

### Test Results

```
tests/test_pyo3_integration.py::TestPyO3PolicyEngineIntegration

12 passed in 0.23s
- test_rule_evaluator_creation
- test_add_and_count_rules
- test_rule_metadata_assignment
- test_condition_group_construction
- test_matcher_kind_variants
- test_on_mismatch_action_variants
- test_evaluate_rules_with_context
- test_evaluate_multiple_rules
- test_clear_rules
- test_decision_creation_directly
- test_policystack_integration_scenario (PRIMARY INTEGRATION DEMO)
- test_repr_methods
```

### Integration Verified

PolicyStack can now:
1. Import phenotype-policy-engine-py bindings (with pytest.importorskip fallback)
2. Construct RuleEvaluator and add Rule objects
3. Evaluate rules against synthetic context dictionaries
4. Receive Decision objects with rule_id, allowed flag, and reason

Example usage (from test_policystack_integration_scenario):
```python
evaluator = pyo3.RuleEvaluator()
acl_rule = pyo3.Rule("acl-db-read", "EXACT", "DENY")
evaluator.add_rule(acl_rule)

request_context = {
    "user_role": "admin",
    "resource": "database:customers",
}

decisions = evaluator.evaluate(request_context)
# decisions[0] => Decision with rule_id, allowed, reason
```

## Residual Items

### Blockers
None. Integration is complete and tested.

### Future Enhancements (Phase-2)

1. **Constraint**: PyO3 bindings don't expose public field access (rule_id, allowed, reason)
   - Current: access via repr() parsing
   - Improvement: Add Pythonic getter methods or use #[pyo3(get)] on fields
   - Impact: Would make tests cleaner and enable better IDE support

2. **Config Loader Integration**
   - Load rules from TOML/YAML via phenotype-config-core
   - Populate RuleEvaluator from config files
   - Integrate into PolicyStack's existing policy-config structure

3. **Performance Benchmarking**
   - Measure PyO3 FFI overhead for large rule sets
   - Compare native Rust vs. Python evaluation latency
   - Target: <1ms for 100-rule evaluation

4. **Error Handling**
   - Add PyErr mapping for RuleEvaluationError
   - Propagate Rust error types to Python exceptions
   - Trace and reason should include error contexts

## Build Artifacts

- **Rust build**: phenoShared/target/release/libphenotype_policy_engine_py.*
- **Python wheel**: phenoShared/target/wheels/phenotype_policy_engine_py-0.1.0-cp313-cp313-macosx_11_0_arm64.whl
- **Type stubs**: phenoShared/crates/phenotype-policy-engine-py/phenotype_policy_engine_py.pyi
- **Tests**: PolicyStack/tests/test_pyo3_integration.py

## Build Environment

- Rust: edition 2021
- PyO3: 0.22 (extension-module feature)
- maturin: 1.12.6
- Python: 3.13
- Platform: aarch64-apple-darwin (arm64 macOS 11.0+)

## Next Steps

1. Ensure wheel is installed in CI/CD environments
2. Update PolicyStack's policy-evaluation path to consume RuleEvaluator
3. Migrate existing policy rules to Rust-backed Rule format
4. Add Phase-2 work: config loading, error propagation, performance tuning

# Test Oracle Implementation Guide: Practical Patterns

## Quick Reference: When to Use Each Oracle Type

```
┌─────────────────────────────────────────────────────────────────┐
│                    Oracle Selection Matrix                       │
├──────────────────────┬──────────────────────────────────────────┤
│ Oracle Type          │ Best For                                 │
├──────────────────────┼──────────────────────────────────────────┤
│ Metamorphic          │ • ML/AI systems • No clear expected output│
│                      │ • Image/signal processing • Parsers      │
│ Property-Based       │ • Complex logic • Invariant verification │
│                      │ • Boundary conditions • Edge cases       │
│ Differential Testing │ • Multiple implementations • Compilers   │
│                      │ • Concurrent algorithms                  │
│ Contract Testing     │ • Microservice boundaries • APIs         │
│                      │ • External integrations                  │
│ Regression Oracle    │ • Behavior change validation             │
│                      │ • Intent-aligned testing                │
│ Statistical Oracle   │ • Probabilistic systems • Randomized algs│
│                      │ • Neural networks                        │
│ Visual Regression    │ • UI components • Design consistency     │
│                      │ • Cross-browser compatibility            │
│ Mutation Testing     │ • Test quality assurance • Fault coverage │
│                      │ • Competency evaluation                  │
│ Chaos Engineering    │ • Fault tolerance • Recovery validation  │
│                      │ • Distributed systems                    │
│ Combinatorial        │ • Configuration-heavy systems            │
│                      │ • Feature interactions                   │
└──────────────────────┴──────────────────────────────────────────┘
```

---

## 1. Metamorphic Testing: Step-by-Step

### 1.1 Quick Start: Image Processing Example

```python
# tests/test_image_processing_metamorphic.py
import pytest
from hypothesis import given, strategies as st
import numpy as np
from PIL import Image

class TestImageProcessingMetamorphic:
    """
    Metamorphic testing for image processing library
    Problem: Hard to verify "correct" brightness adjustment
    Solution: Use metamorphic relations
    """

    def brightness_adjust(self, img: Image.Image, factor: float) -> Image.Image:
        """Function under test"""
        arr = np.array(img, dtype=np.float32)
        arr = np.clip(arr * factor, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)

    @staticmethod
    def mr_idempotence():
        """
        MR1: Idempotence
        f(f(x, 1.0), 1.0) should equal f(x, 1.0)
        """
        @given(st.data())
        def test_idempotence(draw, data):
            img = create_test_image(100, 100)
            factor = draw(st.floats(min_value=0.5, max_value=2.0))

            result1 = brightness_adjust(img, factor)
            result2 = brightness_adjust(result1, 1.0)

            assert images_close(result1, result2)

        return test_idempotence

    @staticmethod
    def mr_commutativity():
        """
        MR2: Commutativity
        f(f(x, a), b) should be similar to f(f(x, b), a)
        for multiplication
        """
        @given(st.data())
        def test_commutativity(draw):
            img = create_test_image(100, 100)
            factor_a = draw(st.floats(min_value=0.5, max_value=2.0))
            factor_b = draw(st.floats(min_value=0.5, max_value=2.0))

            result_ab = brightness_adjust(brightness_adjust(img, factor_a), factor_b)
            result_ba = brightness_adjust(brightness_adjust(img, factor_b), factor_a)

            assert images_close(result_ab, result_ba)

        return test_commutativity

    @staticmethod
    def mr_monotonicity():
        """
        MR3: Monotonicity
        f(x, a) <= f(x, b) when a <= b
        """
        @given(st.data())
        def test_monotonicity(draw):
            img = create_test_image(100, 100)
            factor_a = draw(st.floats(min_value=0.5, max_value=1.0))
            factor_b = draw(st.floats(min_value=1.0, max_value=2.0))

            result_a = brightness_adjust(img, factor_a)
            result_b = brightness_adjust(img, factor_b)

            avg_a = np.mean(np.array(result_a))
            avg_b = np.mean(np.array(result_b))

            assert avg_a <= avg_b

        return test_monotonicity
```

### 1.2 LLM Testing: Metamorphic Relations

```python
# tests/test_llm_metamorphic.py
from typing import Callable
import openai

class TestLLMMetamorphic:
    """
    Metamorphic testing for LLMs
    Challenge: No ground truth, unpredictable outputs
    Solution: Define metamorphic relations
    """

    def __init__(self, model_fn: Callable):
        self.model = model_fn

    def test_paraphrase_invariance(self):
        """
        MR: Paraphrased inputs should produce semantically similar outputs
        """
        @pytest.mark.property
        @given(st.text(min_size=20, max_size=100))
        def test_mr(prompt):
            output1 = self.model(prompt)

            # Generate paraphrase using another model or heuristic
            paraphrased = self._paraphrase(prompt)
            output2 = self.model(paraphrased)

            # Check semantic similarity (using embedding similarity)
            similarity = self._semantic_similarity(output1, output2)
            assert similarity > 0.85, f"Similarity too low: {similarity}"

        return test_mr

    def test_irrelevant_information_robustness(self):
        """
        MR: Adding irrelevant information shouldn't change core output
        """
        base_prompt = "Summarize this article: {article}"

        output1 = self.model(base_prompt)

        # Inject irrelevant information
        injected = base_prompt + "\n[IRRELEVANT: Random noise and unrelated text]"
        output2 = self.model(injected)

        similarity = self._semantic_similarity(output1, output2)
        assert similarity > 0.90

    def test_consistency_across_formats(self):
        """
        MR: Same semantic content in different formats should have similar outputs
        """
        # JSON format
        json_input = '{"question": "What is AI?", "context": "Technology"}'
        output1 = self.model(json_input)

        # Natural language format
        nl_input = "Question: What is AI? (Context: Technology)"
        output2 = self.model(nl_input)

        similarity = self._semantic_similarity(output1, output2)
        assert similarity > 0.80

    def _paraphrase(self, text: str) -> str:
        """Generate paraphrase of text"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Paraphrase the following text without changing meaning"},
                {"role": "user", "content": text}
            ]
        )
        return response['choices'][0]['message']['content']

    def _semantic_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity using embeddings"""
        # Using sentence-transformers or OpenAI embeddings
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')

        emb1 = model.encode(text1)
        emb2 = model.encode(text2)

        from scipy.spatial.distance import cosine
        return 1 - cosine(emb1, emb2)
```

---

## 2. Property-Based Testing: Real-World Examples

### 2.1 GraphQL API Property Testing

```python
# tests/test_graphql_properties.py
from hypothesis import given, strategies as st, assume
import json

@st.composite
def valid_graphql_query(draw):
    """Strategy for generating valid GraphQL queries"""
    operation_type = draw(st.sampled_from(['query', 'mutation']))
    operation_name = draw(st.text(
        min_size=1,
        max_size=20,
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ))

    fields = draw(st.lists(
        st.text(min_size=1, max_size=20),
        min_size=1,
        max_size=5
    ))

    query = f"""
    {operation_type} {operation_name} {{
        {' '.join(fields)}
    }}
    """

    return query

class TestGraphQLProperties:

    @given(valid_graphql_query())
    def test_query_is_valid(self, query):
        """Property: All generated queries parse correctly"""
        import gql

        # Should not raise
        gql.parse(query)

    @given(st.lists(
        st.fixed_dictionaries({
            'id': st.integers(min_value=1),
            'name': st.text(min_size=1),
            'email': st.emails()
        }),
        min_size=1,
        max_size=100
    ))
    def test_user_list_properties(self, users):
        """Property: User list queries maintain invariants"""
        # Test that paginated results maintain invariants

        # Property 1: IDs are unique
        ids = [u['id'] for u in users]
        assert len(ids) == len(set(ids)), "IDs must be unique"

        # Property 2: Email format is valid
        for user in users:
            assert '@' in user['email']

        # Property 3: Result count matches input
        result = query_users(users)
        assert len(result) == len(users)

    @given(st.data())
    def test_pagination_consistency(self, data):
        """Property: Pagination results consistent regardless of page size"""
        all_users = data.draw(st.lists(st.just({
            'id': st.integers(),
            'name': st.text()
        }), min_size=10, max_size=100))

        page_size = data.draw(st.integers(min_value=1, max_value=20))

        # Fetch all pages
        all_paginated = []
        page = 1
        while True:
            result = query_paginated_users(page, page_size)
            if not result:
                break
            all_paginated.extend(result)
            page += 1

        # Property: Total count matches
        assert len(all_paginated) == len(all_users)

        # Property: Order is consistent
        ids_direct = [u['id'] for u in all_users]
        ids_paginated = [u['id'] for u in all_paginated]
        assert ids_direct == ids_paginated
```

### 2.2 Data Structure Property Testing

```python
# tests/test_data_structures_properties.py
from hypothesis import given, strategies as st, assume
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize

class BinarySearchTreeStateMachine(RuleBasedStateMachine):
    """
    Stateful property test for binary search tree
    """

    def __init__(self):
        super().__init__()
        self.bst = BST()
        self.model = set()  # Reference model

    @initialize()
    def setup(self):
        """Reset state"""
        self.bst = BST()
        self.model = set()

    @rule(value=st.integers(min_value=-1000, max_value=1000))
    def insert(self, value):
        """Insert into both BST and model"""
        self.bst.insert(value)
        self.model.add(value)

    @rule(value=st.integers(min_value=-1000, max_value=1000))
    def find(self, value):
        """Find should agree with model"""
        bst_result = self.bst.find(value) is not None
        model_result = value in self.model
        assert bst_result == model_result

    @rule()
    def size_invariant(self):
        """Size should match model"""
        assert self.bst.size() == len(self.model)

    @rule()
    def inorder_invariant(self):
        """Inorder traversal should be sorted"""
        traversal = self.bst.inorder()
        assert traversal == sorted(traversal)

    @rule()
    def bst_property(self):
        """All left < root < all right"""
        def check_bst_property(node):
            if node is None:
                return True

            if node.left:
                if not all(v < node.value for v in
                          self.bst._get_all_values(node.left)):
                    return False

            if node.right:
                if not all(v > node.value for v in
                          self.bst._get_all_values(node.right)):
                    return False

            return (check_bst_property(node.left) and
                   check_bst_property(node.right))

        assert check_bst_property(self.bst.root)


TestBinarySearchTree = BinarySearchTreeStateMachine.TestCase
```

---

## 3. Mutation Testing: Practical Integration

### 3.1 Running mutmut (Python)

```bash
# Install
pip install mutmut

# Run mutation testing
mutmut run

# Run with specific test file
mutmut run --tests-dir tests/unit

# Show results
mutmut results

# Generate HTML report
mutmut html

# Use with pytest
mutmut run --pytest

# Equivalent mutant detection
mutmut run --no-progress --only-covered
```

### 3.2 Mutation Score CI Integration

```python
# scripts/check_mutation_score.py
"""
Check mutation score meets threshold in CI
"""
import subprocess
import json
import sys

def check_mutation_score(threshold: float = 0.85):
    """Run mutmut and verify score meets threshold"""

    # Run mutmut
    result = subprocess.run(
        ['mutmut', 'run', '--tests-dir', 'tests'],
        capture_output=True,
        text=True
    )

    # Parse results
    results = subprocess.run(
        ['mutmut', 'results', '--output', 'json'],
        capture_output=True,
        text=True
    )

    data = json.loads(results.stdout)

    total = len(data.get('results', []))
    killed = sum(1 for m in data.get('results', [])
                 if m.get('status') == 'killed')
    equivalent = sum(1 for m in data.get('results', [])
                    if m.get('status') == 'equivalent')

    score = killed / (total - equivalent) if (total - equivalent) > 0 else 0

    print(f"""
    Mutation Testing Results:
    ├─ Total Mutants: {total}
    ├─ Killed: {killed}
    ├─ Survived: {total - killed - equivalent}
    ├─ Equivalent: {equivalent}
    └─ Score: {score*100:.2f}%
    """)

    if score < threshold:
        print(f"FAILED: Score {score*100:.2f}% below threshold {threshold*100:.2f}%")
        return False

    print(f"PASSED: Score {score*100:.2f}% meets threshold {threshold*100:.2f}%")
    return True


if __name__ == "__main__":
    success = check_mutation_score(threshold=0.80)
    sys.exit(0 if success else 1)
```

### 3.3 Stryker Configuration (JavaScript)

```javascript
// stryker.config.mjs
export default {
  testRunner: 'jest',
  testFramework: 'jest',

  mutate: ['src/**/*.ts', '!src/**/*.spec.ts'],
  files: ['src/**/*.spec.ts'],

  mutator: {
    name: 'javascript',
    // Only include relevant mutators
    mutations: [
      'ArithmeticOperator',
      'EqualityOperator',
      'LogicalOperator',
      'BooleanLiteral',
      'ConditionalExpression'
    ]
  },

  // Skip these files/patterns
  ignoreStatic: true,

  // Report
  reporters: ['html', 'json', 'progress'],

  // Equivalent mutant detection
  equivalentMutantDetection: 'cheap',  // fast heuristics

  // Thresholds
  thresholds: {
    high: 90,
    medium: 80,
    low: 60
  }
};
```

---

## 4. Fuzzing: Practical Setup

### 4.1 Quick Start with libFuzzer (Python via atheris)

```python
# fuzz_targets/fuzz_json_parser.py
import atheris
import json
from json_parser import parse_json

@atheris.instrument_func
def fuzzing_harness(data: bytes) -> None:
    """Fuzzing harness for JSON parser"""

    try:
        # Decode input
        json_str = data.decode('utf-8', errors='ignore')

        # Parse with our implementation
        result = parse_json(json_str)

        # Verify result is JSON-serializable
        json.dumps(result)

        # Verify round-trip
        reparsed = json.loads(json.dumps(result))
        assert json.dumps(reparsed) == json.dumps(result)

    except (ValueError, json.JSONDecodeError):
        # Expected for invalid JSON
        pass
    except UnicodeDecodeError:
        pass

atheris.Setup(sys.argv, fuzzing_harness)
atheris.Fuzz()
```

Run with:
```bash
pip install atheris

# Generate seeds (optional)
mkdir seeds
echo '{"valid":"json"}' > seeds/valid.json
echo '[]' > seeds/empty.json

# Run with libFuzzer backend
python -m atheris -len=1024 -max_len=10000 fuzz_targets/fuzz_json_parser.py
```

### 4.2 Grammar-Based Fuzzing with Grammarinator

```python
# fuzz_targets/fuzz_url_parser.py
from grammarinator.tool import Grammarinator
import re

# URL grammar
url_grammar = """
url         : scheme "://" host path? query? fragment?
scheme      : /[a-z]+/
host        : domain ( ":" port )?
domain      : label ( "." label )*
label       : /[a-z0-9\-]+/
port        : /[0-9]+/
path        : ( "/" segment )*
segment     : /[a-z0-9\-._~]+/
query       : "?" parameter ( "&" parameter )*
parameter   : /[a-z0-9]+=/ /[a-z0-9]*/
fragment    : "#" /[a-z0-9]*/
"""

class URLGrammarFuzzer:
    def __init__(self):
        self.generator = Grammarinator(url_grammar)

    def fuzz(self, data: bytes) -> None:
        """Generate URLs respecting grammar"""
        # Use data to drive grammar traversal
        url = self.generator.generate(seed=data)

        # Test parser
        try:
            result = parse_url(url)
            assert result is not None
        except Exception as e:
            # Unexpected error
            raise

fuzzer = URLGrammarFuzzer()
```

---

## 5. Contract Testing: Practical Examples

### 5.1 Pact Consumer Test

```python
# tests/test_user_service_contract.py
import pytest
from pact import Consumer, Provider

# Setup consumer contract
pact = Consumer('WebClient').has_state(
    'user with id 123 exists'
).upon_receiving(
    'a request for user 123'
).with_request(
    'GET',
    '/api/users/123',
).will_respond_with(
    200,
    body={
        'id': 123,
        'name': 'Alice',
        'email': 'alice@example.com',
        'active': True
    }
)

@pytest.fixture
def user_api():
    """Fixture returns mock provider"""
    with pact:
        yield pact.service_mock

def test_get_user(user_api):
    """Test consumer code against contract"""
    # Arrange: pact sets up mock

    # Act: Call consumer code
    user = UserServiceClient(user_api.url).get_user(123)

    # Assert: Verify contract
    assert user['id'] == 123
    assert user['name'] == 'Alice'
    assert user['email'] == 'alice@example.com'

# Generate contract file
pact.write_interaction()
```

### 5.2 Pact Broker Integration

```python
# .github/workflows/contract-tests.yml
name: Contract Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run contract tests
        run: |
          pip install pact
          pytest tests/test_*_contract.py

      - name: Publish contracts to Pact Broker
        run: |
          pact-broker publish \
            --consumer-app-version ${{ github.sha }} \
            --pact-broker-base-url ${{ secrets.PACT_BROKER_URL }} \
            --pact-broker-username ${{ secrets.PACT_BROKER_USERNAME }} \
            --pact-broker-password ${{ secrets.PACT_BROKER_PASSWORD }}

      - name: Can I deploy?
        run: |
          pact-broker can-i-deploy \
            --consumer-version ${{ github.sha }} \
            --pact-broker-base-url ${{ secrets.PACT_BROKER_URL }}
```

---

## 6. Visual Regression Testing

### 6.1 Percy Configuration

```javascript
// percy.config.js
module.exports = {
  version: 2,

  static: {
    // Path to static files
    cleanUrls: true,
    include: 'dist/**/*',
    exclude: ['dist/**/*.map', '**/.DS_Store']
  },

  build: {
    // Build discovery
    staticHost: 'http://localhost:8000'
  },

  discovery: {
    // Static discovery for SPA
    allowed_hosts: ['localhost'],
    network_idle_timeout: 750
  },

  // Snapshots
  snapshot: {
    // Acceptable color difference (0-1, default 0)
    min_height: 1024,

    // Device widths for responsive testing
    widths: [375, 768, 1280, 1920]
  }
};
```

### 6.2 Playwright Percy Integration

```typescript
// tests/visual-regression.spec.ts
import { test, expect } from '@playwright/test';
import { percySnapshot } from '@percy/cli/dist/percy-snapshot';

test.describe('Visual Regression Tests', () => {

  test('dashboard should match baseline', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Take Percy snapshot
    await percySnapshot(page, 'Dashboard');
  });

  test('form should match across devices', async ({ page }) => {
    await page.goto('/contact-form');

    // Percy handles responsive testing
    await percySnapshot(page, 'Contact Form', {
      widths: [375, 768, 1280]
    });
  });

  test('comparison view should match baseline', async ({ page }) => {
    await page.goto('/comparison');

    // Wait for dynamic content
    await page.waitForSelector('[data-testid="comparison-loaded"]');

    await percySnapshot(page, 'Comparison View');
  });

  // Baseline comparison test
  test('should detect visual regressions', async ({ page }) => {
    await page.goto('/components/button');

    const screenshot = await page.screenshot();
    expect(screenshot).toMatchSnapshot('button-default.png');

    // Also Percy for diff visualization
    await percySnapshot(page, 'Button Component');
  });
});
```

---

## 7. Performance Testing SLO Validation

### 7.1 Load Test Script with SLO Validation

```python
# load_tests/test_api_performance.py
import pytest
import asyncio
from locust import HttpUser, task, between
from performance_framework import PerformanceSLO, PerformanceTestFramework

# Define SLOs
api_slo = PerformanceSLO(
    service_name="API Gateway",
    latency_thresholds={
        "P95": 300,  # 95% of requests < 300ms
        "P99": 1000  # 99% of requests < 1s
    },
    error_rate_threshold=0.1,  # < 0.1%
    availability_target=99.95,
    throughput_min_rps=100,
    throughput_max_rps=5000
)

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_users(self):
        """Most common operation"""
        self.client.get("/api/users")

    @task(1)
    def create_user(self):
        """Less common"""
        self.client.post("/api/users", json={
            "name": "Test User",
            "email": "test@example.com"
        })

    @task(2)
    def search(self):
        """Search operation"""
        self.client.get("/api/search?q=test")

@pytest.mark.performance
def test_api_slo_compliance(locust_runner):
    """Validate API meets SLO under load"""

    framework = PerformanceTestFramework(api_slo)

    # Run load test
    results = framework.run_load_test(
        target_rps=1000,
        duration_seconds=300,  # 5 minutes
        ramp_up_seconds=60
    )

    # Verify SLO compliance
    assert results["slo_compliance"]["latency_p95"]
    assert results["slo_compliance"]["latency_p99"]
    assert results["slo_compliance"]["error_rate"]
    assert results["slo_compliance"]["throughput"]

    # Report
    print(f"""
    Performance Test Results:
    P95 Latency: {results['percentiles']['P95']:.0f}ms
      (SLO: {api_slo.latency_thresholds['P95']}ms)
    P99 Latency: {results['percentiles']['P99']:.0f}ms
      (SLO: {api_slo.latency_thresholds['P99']}ms)
    Error Rate: {results['error_rate_percent']:.2f}%
      (SLO: {api_slo.error_rate_threshold}%)
    Throughput: {results['throughput_rps']:.0f} rps
    """)
```

---

## 8. Chaos Engineering: Practical Implementation

### 8.1 Python Chaos Test

```python
# chaos_tests/test_api_resilience.py
import pytest
import time
from chaos_framework import ChaosExperiment, FaultType

@pytest.mark.chaos
def test_api_resilience_to_latency():
    """Verify API recovers from induced latency"""

    experiment = ChaosExperiment(
        name="API Latency Injection",
        description="Inject 500ms latency and verify recovery",
        fault_injectors=[
            LatencyInjector(
                target_service="api-gateway",
                latency_ms=500,
                duration_seconds=60
            )
        ],
        hypothesis="API should remain operational and recover within 30s",
        duration_seconds=120,
        monitoring_metrics=[
            "request_latency_p99",
            "error_rate",
            "cpu_usage"
        ],
        success_criteria={
            "error_rate": 0.05,  # < 5%
            "recovery_time": 30  # < 30 seconds
        }
    )

    # Run chaos experiment
    results = experiment.run()

    # Verify results
    assert results["passed"], f"Chaos experiment failed: {results}"
    assert results["recovery_time"] < 30, \
        f"Recovery took {results['recovery_time']}s (max 30s)"

@pytest.mark.chaos
def test_circuit_breaker_activation():
    """Verify circuit breaker activates on cascading failures"""

    experiment = ChaosExperiment(
        name="Cascading Failure Test",
        fault_injectors=[
            CascadingFailureInjector(
                root_service="payment-service",
                propagation_depth=3
            )
        ],
        hypothesis="Circuit breakers should activate within 5s",
        duration_seconds=60,
        success_criteria={
            "circuit_breaker_activated": True,
            "activation_time": 5
        }
    )

    results = experiment.run()
    assert results["circuit_breaker_activated"]
    assert results["activation_time"] < 5
```

---

## 9. Combinatorial Testing: t-Way Coverage

### 9.1 Using ACTS Tool

```python
# tests/test_browser_compatibility.py
from combinatorial_framework import CombinatorialTestingFramework, Parameter

# Define parameters for browser compatibility testing
parameters = [
    Parameter("browser", ["Chrome", "Firefox", "Safari", "Edge"]),
    Parameter("os", ["Windows", "macOS", "Linux"]),
    Parameter("resolution", ["1920x1080", "1366x768", "768x1024"]),
    Parameter("javascript", ["enabled", "disabled"]),
    Parameter("cookies", ["enabled", "disabled"])
]

# Add constraints
def browser_os_constraint(case):
    """Safari only on macOS/iOS"""
    if case["browser"] == "Safari":
        return case["os"] in ["macOS"]
    return True

def js_requirement(case):
    """JavaScript must be enabled for modern features"""
    if case["resolution"] == "1366x768":
        return case["javascript"] == "enabled"
    return True

framework = CombinatorialTestingFramework(parameters)
framework.add_constraint(browser_os_constraint)
framework.add_constraint(js_requirement)

# Generate 2-way (pairwise) covering array
test_suite = framework.generate_covering_array(strength=2)

print(f"Generated {len(test_suite.test_cases)} test cases")
for i, test_case in enumerate(test_suite.test_cases):
    print(f"Test {i+1}: {test_case}")

# Use in parametrized tests
@pytest.mark.parametrize("test_case", test_suite.test_cases)
def test_compatibility(test_case):
    """Test application across combinations"""
    browser = test_case["browser"]
    os = test_case["os"]
    resolution = test_case["resolution"]
    js_enabled = test_case["javascript"] == "enabled"
    cookies_enabled = test_case["cookies"] == "enabled"

    # Run test with specific configuration
    driver = get_webdriver(browser, os, resolution, js_enabled, cookies_enabled)
    try:
        driver.get("https://app.example.com")
        assert driver.find_element("h1").text != ""
    finally:
        driver.quit()
```

---

## 10. Complete Integration: Multi-Oracle System

### 10.1 Unified Test Suite

```python
# tests/test_unified_oracle_system.py
import pytest
from unified_oracle import UnifiedTestOracleSystem

class TestDataTransformationWithUnifiedOracles:
    """
    Example: Testing data transformation service
    Uses multiple oracles for comprehensive verification
    """

    @pytest.fixture
    def oracle_system(self):
        """Setup unified oracle system"""
        system = UnifiedTestOracleSystem()

        # Add metamorphic oracle
        system.add_oracle(
            MetamorphicOracle([
                CommutativityMR(),
                IdempotenceMR(),
                MonotonicityMR()
            ]),
            "metamorphic",
            weight=1.5
        )

        # Add property-based oracle
        system.add_oracle(
            PropertyBasedOracle([
                "output_valid_json",
                "invariants_preserved",
                "round_trip_consistency"
            ]),
            "property_based",
            weight=1.0
        )

        # Add differential oracle
        system.add_oracle(
            DifferentialTestingOracle(
                reference_impl=reference_transform,
                test_impl=transform_under_test
            ),
            "differential",
            weight=1.2
        )

        return system

    @given(st.data())
    def test_transform_with_unified_oracles(self, data, oracle_system):
        """Test with unified oracle system"""

        # Generate test input
        input_data = data.draw(st.fixed_dictionaries({
            "id": st.integers(min_value=1),
            "name": st.text(min_size=1, max_size=50),
            "value": st.floats(min_value=0, allow_nan=False)
        }))

        # Run unified oracle verification
        verdict = oracle_system.verify(input_data, transform_function)

        # All verdicts must pass
        assert verdict.passed, f"Oracle failed: {verdict.evidence}"
        assert verdict.confidence > 0.8, f"Low confidence: {verdict.confidence}"

    def test_mutation_quality(self):
        """Run mutation testing to validate test suite"""
        import subprocess

        result = subprocess.run(
            ["mutmut", "run", "--tests-dir", "tests"],
            capture_output=True
        )

        # Check mutation score
        mutation_score = parse_mutation_score(result.stdout)
        assert mutation_score > 0.85, \
            f"Mutation score too low: {mutation_score*100:.0f}%"

    @pytest.mark.chaos
    def test_resilience_under_chaos(self):
        """Verify system resilience"""
        experiment = ChaosExperiment(
            faults=[LatencyInjector(delay_ms=500)],
            hypothesis="System recovers from latency",
            success_criteria={"recovery_time_s": 5}
        )

        results = experiment.run()
        assert results["passed"]

    @pytest.mark.performance
    def test_performance_slo(self):
        """Validate SLO compliance"""
        slo = PerformanceSLO(
            latency_thresholds={"P95": 300, "P99": 1000},
            error_rate_threshold=0.1
        )

        results = slo.validate(transform_function)
        assert all(results["slo_compliance"].values())
```

---

## 11. CI/CD Integration Checklist

```yaml
# .github/workflows/comprehensive-testing.yml
name: Comprehensive Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
          pip install hypothesis mutmut pytest-benchmark

      - name: Run unit tests
        run: pytest tests/unit -v

      - name: Run property-based tests
        run: pytest tests/ -m property -v

      - name: Run metamorphic tests
        run: pytest tests/ -m metamorphic -v

      - name: Run mutation testing
        run: |
          mutmut run
          python scripts/check_mutation_score.py --threshold 0.80

      - name: Run integration tests
        run: pytest tests/integration -v

      - name: Run fuzzing (short duration for CI)
        run: |
          timeout 60 python -m atheris \
            -max_len=1000 \
            fuzz_targets/fuzz_json_parser.py || true

      - name: Run contract tests
        run: pytest tests/ -m contract -v

      - name: Run visual regression tests
        run: pytest tests/visual -v

      - name: Validate SLO compliance
        run: pytest tests/ -m performance -v

      - name: Upload mutation report
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: mutation-report
          path: htmlcov/

      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const mutation_score = ...
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `Mutation Score: ${mutation_score*100}%`
            })
```

---

## 12. Troubleshooting Guide

### Issue: "All metamorphic tests pass but real bugs exist"

**Solution:** Add more diverse metamorphic relations
```python
# Add coverage for more scenarios
mr_suite = [
    CommutativityMR(),      # Order independence
    ScaleInvarianceMR(),    # Magnitude independence
    PermutationMR(),        # Input order
    NegationMR(),           # Sign flipping
    CompositionMR(),        # Function composition
    SimilarityMR()          # Input perturbation
]
```

### Issue: "Property-based tests are too slow"

**Solution:** Use `@settings` to control execution
```python
from hypothesis import settings, HealthCheck

@settings(
    max_examples=1000,  # Reduce from default 10000
    deadline=1000,      # 1s per test
    suppress_health_check=[HealthCheck.too_slow]
)
@given(complex_strategy())
def test_something(data):
    pass
```

### Issue: "Fuzzing not finding expected bugs"

**Solution:** Improve grammar and mutation strategies
```python
# Use more specific grammar
grammar = """
json: "{" pair ("," pair)* "}"
pair: string ":" value
value: string | number | bool | null | json | array
"""

# Increase mutation iterations
fuzz(max_iterations=1000000, timeout_per_input=5000)
```

---

## 13. Quick Reference Commands

```bash
# Python testing
pytest tests/ -v --hypothesis-show-statistics
pytest tests/ -m metamorphic -v
pytest tests/ --cov=src --cov-report=html

# Mutation testing
mutmut run
mutmut results
mutmut html

# Fuzzing
python -m atheris -max_len=10000 fuzz_target.py

# Contract testing
pytest tests/ -m contract
pact-broker publish ...

# Performance testing
locust -f load_tests/locustfile.py -u 1000 -r 100

# Visual regression
percy exec --dry-run -- npm run build
chromatic --project-token $CHROMATIC_TOKEN

# Chaos engineering
kubectl apply -f chaos-experiments/
chaosctl status
```

---

## Conclusion

This implementation guide provides practical patterns for all major test oracle techniques. Start with metamorphic testing for hard-to-verify systems, add property-based testing for invariant validation, and layer in mutation testing to ensure test effectiveness.


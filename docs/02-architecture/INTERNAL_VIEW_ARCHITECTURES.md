# Internal View Architectures: Deep Dive into View Implementation

**Date**: 2025-11-20
**Version**: 1.0
**Purpose**: Detailed internal architecture for each of the 32 views

---

## Executive Summary

This document provides AST-level detail on the internal architecture of each view in the trace system. For the 10 most complex views, we document:
- Internal data structures
- Query optimization strategies
- Caching layers
- Generation algorithms
- Validation rules
- API patterns

---

## Part 1: CODE View (Deep Dive)

### 1.1 Internal Architecture

**Purpose**: Source code representation with AST, symbols, dependencies, metrics

**Internal Data Structure**:
```python
@dataclass
class CodeView:
    """Complete code file representation with AST and analysis."""

    id: UUID
    file_path: Path
    language: Language
    content: str
    content_hash: str  # SHA-256 for change detection

    # AST Representation
    ast: AST  # Abstract Syntax Tree
    ast_version: int  # AST schema version

    # Symbol Table
    symbols: SymbolTable
    # {
    #   'functions': [Function],
    #   'classes': [Class],
    #   'variables': [Variable],
    #   'imports': [Import],
    #   'exports': [Export]
    # }

    # Dependency Graph
    dependencies: DependencyGraph
    # {
    #   'internal': [Path],  # Other project files
    #   'external': [Package],  # npm/pypi packages
    #   'call_graph': Graph  # Function call relationships
    # }

    # Code Metrics
    metrics: CodeMetrics
    # {
    #   'loc': int,  # Lines of code
    #   'sloc': int,  # Source lines (no comments/blanks)
    #   'cyclomatic_complexity': int,
    #   'cognitive_complexity': int,
    #   'maintainability_index': float,
    #   'test_coverage': float
    # }

    # Git Integration
    git_info: GitInfo
    # {
    #   'current_commit': str,
    #   'last_author': str,
    #   'last_modified': datetime,
    #   'blame': {line_number: Author}
    # }

    # Traceability
    implements: List[UUID]  # Feature/Story IDs
    tested_by: List[UUID]  # Test file IDs

    # Metadata
    created_at: datetime
    last_analyzed: datetime


@dataclass
class AST:
    """Abstract Syntax Tree representation."""
    tree: dict  # JSON-serializable AST
    parser: str  # 'ast' (Python), 'babel' (JS), 'tree-sitter'
    node_count: int
    depth: int


@dataclass
class SymbolTable:
    """Extracted symbols from code."""
    functions: List[FunctionSymbol]
    classes: List[ClassSymbol]
    variables: List[VariableSymbol]
    imports: List[ImportSymbol]


@dataclass
class FunctionSymbol:
    name: str
    signature: str
    line_start: int
    line_end: int
    docstring: Optional[str]
    parameters: List[Parameter]
    return_type: Optional[str]
    complexity: int  # Cyclomatic complexity
    calls: List[str]  # Function names called
    called_by: List[str]  # Functions that call this


@dataclass
class DependencyGraph:
    """Code dependency relationships."""
    internal_deps: List[str]  # Files in same project
    external_deps: List[ExternalDep]  # npm/pypi packages
    call_graph: nx.DiGraph  # Function call graph


@dataclass
class CodeMetrics:
    """Code quality metrics."""
    loc: int
    sloc: int
    comment_ratio: float
    cyclomatic_complexity: int
    cognitive_complexity: int
    maintainability_index: float  # 0-100
    test_coverage: float  # 0-1
    last_measured: datetime
```

### 1.2 Advanced Query Patterns

**Query 1: Find all functions that call authenticate()**
```python
# Using AST and call graph
code_view = await code_service.get_by_path("src/user_service.py")
callers = code_view.dependencies.call_graph.predecessors("authenticate")
# Returns: ['login', 'signup', 'reset_password']
```

**Query 2: Most complex functions in codebase**
```sql
SELECT file_path,
       jsonb_array_elements(symbols->'functions') AS func,
       (jsonb_array_elements(symbols->'functions')->>'complexity')::int AS complexity
FROM code_views
WHERE language = 'python'
ORDER BY complexity DESC
LIMIT 20;
```

**Query 3: Dependency graph visualization**
```python
# Export to GraphViz DOT format
def export_dependency_graph(code_views: List[CodeView]) -> str:
    graph = nx.DiGraph()
    for cv in code_views:
        graph.add_node(cv.file_path, label=cv.file_path.name)
        for dep in cv.dependencies.internal_deps:
            graph.add_edge(cv.file_path, dep)

    return nx.nx_agraph.to_agraph(graph).to_string()
```

### 1.3 AST-Based Search

**Search Pattern**: Find all HTTP POST endpoints

```python
# Python AST traversal
import ast

def find_http_endpoints(code_view: CodeView) -> List[Endpoint]:
    """Extract HTTP endpoints from FastAPI code."""
    tree = ast.parse(code_view.content)
    endpoints = []

    for node in ast.walk(tree):
        # Look for @app.post(...) decorators
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Attribute):
                        if decorator.func.attr in ['post', 'get', 'put', 'delete']:
                            # Extract endpoint path from decorator args
                            path = decorator.args[0].s if decorator.args else None
                            endpoints.append(Endpoint(
                                method=decorator.func.attr.upper(),
                                path=path,
                                function=node.name,
                                line=node.lineno
                            ))

    return endpoints
```

### 1.4 Automatic Metric Calculation

```python
async def analyze_code_file(file_path: Path) -> CodeView:
    """Parse file and extract all metadata."""

    content = file_path.read_text()
    content_hash = hashlib.sha256(content.encode()).hexdigest()

    # Parse AST
    if file_path.suffix == '.py':
        tree = ast.parse(content)
        ast_json = ast_to_json(tree)
        symbols = extract_python_symbols(tree)
        deps = extract_python_dependencies(tree)

    # Calculate metrics
    metrics = CodeMetrics(
        loc=content.count('\n') + 1,
        sloc=count_source_lines(content),
        comment_ratio=count_comments(content) / content.count('\n'),
        cyclomatic_complexity=calculate_complexity(tree),
        cognitive_complexity=calculate_cognitive(tree),
        maintainability_index=calculate_maintainability(metrics),
        test_coverage=await get_coverage_for_file(file_path)
    )

    # Git info
    repo = pygit2.Repository('.')
    blame = repo.blame(str(file_path))
    git_info = GitInfo(
        current_commit=repo.head.target.hex,
        last_author=blame[-1].author.name,
        last_modified=datetime.fromtimestamp(blame[-1].commit.commit_time)
    )

    return CodeView(
        id=uuid4(),
        file_path=file_path,
        language=detect_language(file_path),
        content=content,
        content_hash=content_hash,
        ast=AST(ast_json, 'ast', count_nodes(ast_json), max_depth(ast_json)),
        symbols=symbols,
        dependencies=deps,
        metrics=metrics,
        git_info=git_info,
        last_analyzed=datetime.now()
    )
```

---

## Part 2: TEST View (Deep Dive)

### 2.1 Internal Architecture

**Purpose**: Test representation with execution history, coverage mapping, flakiness detection

**Internal Data Structure**:
```python
@dataclass
class TestView:
    """Complete test file representation."""

    id: UUID
    file_path: Path
    test_framework: TestFramework  # pytest, jest, cypress
    language: Language

    # Test Cases
    test_cases: List[TestCase]

    # Coverage
    coverage_data: CoverageData

    # Execution History (last 30 runs)
    execution_history: List[TestExecution]

    # Flakiness
    flakiness_score: float  # 0-1 (0 = stable, 1 = always flaky)

    # Performance
    avg_duration: timedelta
    p95_duration: timedelta

    # Traceability
    verifies_code: List[UUID]  # Code View IDs
    verifies_features: List[UUID]  # Feature View IDs

    created_at: datetime
    last_run: datetime


@dataclass
class TestCase:
    """Single test case."""
    name: str
    line_start: int
    line_end: int
    test_type: TestType  # unit, integration, e2e
    status: TestStatus  # passed, failed, skipped, flaky
    duration_ms: int
    error_message: Optional[str]
    assertions: List[Assertion]
    fixtures: List[str]  # Fixture names used


@dataclass
class CoverageData:
    """Code coverage mapping."""
    overall_coverage: float
    line_coverage: float
    branch_coverage: float
    covered_lines: Set[int]
    uncovered_lines: Set[int]
    covered_branches: Set[Tuple[int, int]]
    uncovered_branches: Set[Tuple[int, int]]


@dataclass
class TestExecution:
    """Historical test execution result."""
    execution_time: datetime
    git_commit: str
    status: TestStatus
    duration_ms: int
    environment: str  # 'local', 'ci', 'staging'
    error: Optional[str]
```

### 2.2 Flakiness Detection Algorithm

```python
def calculate_flakiness_score(executions: List[TestExecution]) -> float:
    """Calculate test flakiness based on execution history.

    Flakiness = (# of status changes) / (# of executions)

    Examples:
      - Always passing: [P, P, P, P, P] = 0/5 = 0.0 (stable)
      - Always failing: [F, F, F, F, F] = 0/5 = 0.0 (stable)
      - Flaky: [P, F, P, F, P] = 4/5 = 0.8 (very flaky)
      - Intermittent: [P, P, P, F, P, P] = 2/6 = 0.33 (somewhat flaky)
    """
    if len(executions) < 2:
        return 0.0

    status_changes = 0
    for i in range(1, len(executions)):
        if executions[i].status != executions[i-1].status:
            status_changes += 1

    return status_changes / len(executions)


async def detect_flaky_tests() -> List[TestView]:
    """Identify flaky tests (score > 0.3)."""
    flaky_tests = await test_repository.find_all(
        filter=lambda t: t.flakiness_score > 0.3,
        order_by='flakiness_score',
        order='desc'
    )

    return flaky_tests
```

### 2.3 Coverage Mapping

**Link test lines to code lines**:
```python
class CoverageMapper:
    """Map test assertions to code lines."""

    def map_coverage(self, test_view: TestView, code_view: CodeView) -> CoverageMapping:
        """Determine which code lines are covered by which tests."""

        mapping = CoverageMapping()

        # Run coverage tool (coverage.py, istanbul)
        coverage_data = run_coverage(test_view.file_path, code_view.file_path)

        # Parse .coverage file
        for test_case in test_view.test_cases:
            # Determine which code lines this test executed
            executed_lines = coverage_data.get_lines_for_test(test_case.name)

            # Map to code functions
            for line in executed_lines:
                func = code_view.get_function_at_line(line)
                if func:
                    mapping.add(test_case, func, line)

        return mapping


@dataclass
class CoverageMapping:
    """Bidirectional mapping between tests and code."""
    test_to_code: Dict[TestCase, Set[FunctionSymbol]]
    code_to_test: Dict[FunctionSymbol, Set[TestCase]]

    def get_tests_for_function(self, func: FunctionSymbol) -> Set[TestCase]:
        """Which tests cover this function?"""
        return self.code_to_test.get(func, set())

    def get_functions_tested_by(self, test: TestCase) -> Set[FunctionSymbol]:
        """Which functions does this test cover?"""
        return self.test_to_code.get(test, set())

    def untested_functions(self, code_view: CodeView) -> Set[FunctionSymbol]:
        """Functions with no test coverage."""
        return {f for f in code_view.symbols.functions if f not in self.code_to_test}
```

---

## Part 3: API_CONTRACT View (Deep Dive)

### 3.1 Internal Architecture

**Purpose**: OpenAPI/GraphQL schema with validation, versioning, contract testing

**Internal Data Structure**:
```python
@dataclass
class APIContractView:
    """API contract with full OpenAPI 3.1 spec."""

    id: UUID
    feature_id: UUID
    endpoint_path: str
    http_method: HTTPMethod
    openapi_version: str  # "3.1.0"

    # Request
    request_schema: JSONSchema
    request_examples: List[Example]
    request_validation: ValidationRules

    # Response
    response_schemas: Dict[int, JSONSchema]  # Status code → schema
    response_examples: Dict[int, List[Example]]

    # Security
    security_schemes: List[SecurityScheme]
    required_scopes: List[str]

    # Contract Testing
    contract_tests: List[ContractTest]
    mock_server_url: Optional[str]

    # Versioning
    version: SemVer
    deprecated: bool
    sunset_date: Optional[date]

    # Documentation
    summary: str
    description: str
    tags: List[str]

    created_at: datetime
    last_validated: datetime


@dataclass
class JSONSchema:
    """JSON Schema for request/response."""
    schema_version: str  # "http://json-schema.org/draft-07/schema#"
    type: str
    properties: Dict[str, Property]
    required: List[str]
    additional_properties: bool
    examples: List[dict]


@dataclass
class ContractTest:
    """Contract test case."""
    test_id: UUID
    name: str
    request: dict
    expected_status: int
    expected_response_schema: JSONSchema
    status: TestStatus
    last_run: datetime
```

### 3.2 Contract Validation Engine

```python
class ContractValidator:
    """Validate API implementation matches contract."""

    async def validate_endpoint(
        self,
        contract: APIContractView,
        implementation_url: str
    ) -> ValidationResult:
        """Test API implementation against contract."""

        results = ValidationResult()

        for test in contract.contract_tests:
            # Send request
            response = await http_client.request(
                method=contract.http_method,
                url=f"{implementation_url}{contract.endpoint_path}",
                json=test.request,
                headers=self._build_auth_headers(contract)
            )

            # Validate status code
            if response.status_code != test.expected_status:
                results.add_failure(
                    f"Expected status {test.expected_status}, got {response.status_code}"
                )

            # Validate response schema
            try:
                jsonschema.validate(
                    instance=response.json(),
                    schema=test.expected_response_schema.to_dict()
                )
            except jsonschema.ValidationError as e:
                results.add_failure(f"Response schema mismatch: {e.message}")

        return results


    def generate_mock_server(self, contract: APIContractView) -> MockServer:
        """Generate mock server from contract for frontend development."""

        mock = MockServer()

        @mock.route(contract.endpoint_path, methods=[contract.http_method])
        def handler():
            # Validate request against schema
            request_data = request.get_json()
            jsonschema.validate(request_data, contract.request_schema.to_dict())

            # Return example response
            example_response = contract.response_examples[200][0]
            return jsonify(example_response), 200

        return mock
```

### 3.3 Automatic TypeScript Type Generation

```python
def generate_typescript_types(contract: APIContractView) -> str:
    """Generate TypeScript types from JSON Schema."""

    ts_code = f"// Auto-generated from {contract.id}\n\n"

    # Generate request type
    ts_code += json_schema_to_typescript(
        schema=contract.request_schema,
        type_name=f"{to_pascal_case(contract.endpoint_path)}Request"
    )

    ts_code += "\n\n"

    # Generate response type
    ts_code += json_schema_to_typescript(
        schema=contract.response_schemas[200],
        type_name=f"{to_pascal_case(contract.endpoint_path)}Response"
    )

    ts_code += "\n\n"

    # Generate API client function
    ts_code += generate_api_client_function(contract)

    return ts_code


def generate_api_client_function(contract: APIContractView) -> str:
    """Generate TypeScript API client function."""
    func_name = f"{contract.http_method.lower()}{to_pascal_case(contract.endpoint_path)}"
    request_type = f"{to_pascal_case(contract.endpoint_path)}Request"
    response_type = f"{to_pascal_case(contract.endpoint_path)}Response"

    return f'''
export async function {func_name}(
  request: {request_type}
): Promise<{response_type}> {{
  const response = await fetch("{contract.endpoint_path}", {{
    method: "{contract.http_method}",
    headers: {{ "Content-Type": "application/json" }},
    body: JSON.stringify(request),
  }});

  if (!response.ok) {{
    throw new Error(`API error: ${{response.status}}`);
  }}

  return await response.json() as {response_type};
}}
'''
```

---

## Part 4: MONITORING View (Deep Dive)

### 4.1 Internal Architecture

**Purpose**: Real-time metrics with TimescaleDB, dashboards, alerting

**Internal Data Structure**:
```python
@dataclass
class MonitoringView:
    """Real-time monitoring dashboard."""

    id: UUID
    product_id: UUID
    dashboard_name: str

    # Metric Definitions
    metrics: List[MetricDefinition]

    # Time Range
    time_range: TimeRange  # Last 1h, 24h, 7d, 30d

    # Panels
    panels: List[Panel]

    # Refresh
    refresh_interval: timedelta  # Auto-refresh every N seconds

    created_at: datetime


@dataclass
class MetricDefinition:
    """Single metric tracked."""
    metric_id: UUID
    name: str
    metric_type: MetricType  # counter, gauge, histogram
    query: str  # SQL query to fetch metric
    unit: str
    thresholds: Thresholds
    dimensions: List[Dimension]  # For segmentation (by region, by service, etc.)


@dataclass
class Thresholds:
    """Alert thresholds."""
    red_min: Optional[float]
    red_max: Optional[float]
    yellow_min: Optional[float]
    yellow_max: Optional[float]
    green_min: float
    green_max: float


@dataclass
class Panel:
    """Dashboard panel (chart, stat, table)."""
    panel_id: UUID
    type: PanelType  # line-chart, bar-chart, stat, table, heatmap
    title: str
    metrics: List[UUID]  # Metric IDs to display
    visualization_config: dict  # Chart-specific config
    position: Position  # {x, y, width, height}
```

### 4.2 Real-Time Query Engine

```python
class MonitoringQueryEngine:
    """Optimized queries for monitoring dashboard."""

    def __init__(self, timescaledb_conn):
        self.db = timescaledb_conn

    async def query_metric(
        self,
        metric_def: MetricDefinition,
        time_range: TimeRange,
        granularity: timedelta
    ) -> TimeSeriesData:
        """Query metric with automatic aggregation."""

        # Use continuous aggregate if available
        if granularity >= timedelta(hours=1):
            table = "monitoring_metrics_hourly"
        elif granularity >= timedelta(minutes=5):
            table = "monitoring_metrics_5min"
        else:
            table = "monitoring_metrics"  # Raw data

        query = f"""
        SELECT time_bucket($1, time) AS bucket,
               AVG(value) as avg_value,
               MIN(value) as min_value,
               MAX(value) as max_value,
               COUNT(*) as data_points
        FROM {table}
        WHERE metric_id = $2
          AND time >= $3
          AND time <= $4
        GROUP BY bucket
        ORDER BY bucket
        """

        results = await self.db.fetch_all(
            query,
            granularity,
            metric_def.metric_id,
            time_range.start,
            time_range.end
        )

        return TimeSeriesData(
            metric_id=metric_def.metric_id,
            data_points=[DataPoint(r['bucket'], r['avg_value'], r['min_value'], r['max_value']) for r in results],
            granularity=granularity
        )


    async def detect_anomalies(
        self,
        metric_id: UUID,
        time_range: TimeRange
    ) -> List[Anomaly]:
        """Detect anomalies using statistical methods."""

        # Fetch historical data
        data = await self.query_metric_raw(metric_id, time_range)

        # Calculate statistics
        mean = statistics.mean([d.value for d in data])
        stdev = statistics.stdev([d.value for d in data])

        # Identify outliers (>3 standard deviations)
        anomalies = []
        for point in data:
            z_score = abs((point.value - mean) / stdev)
            if z_score > 3:
                anomalies.append(Anomaly(
                    time=point.time,
                    value=point.value,
                    expected_range=(mean - 3*stdev, mean + 3*stdev),
                    z_score=z_score
                ))

        return anomalies
```

### 4.3 Alerting Engine

```python
class AlertEngine:
    """Evaluate thresholds and trigger alerts."""

    async def evaluate_metrics(self):
        """Check all metrics against thresholds."""

        metrics = await metric_repository.find_all()

        for metric_def in metrics:
            # Get latest value
            latest = await monitoring_query.get_latest(metric_def.metric_id)

            # Check thresholds
            alert_level = self._check_thresholds(latest.value, metric_def.thresholds)

            if alert_level in ['red', 'yellow']:
                await self._trigger_alert(
                    metric_def,
                    latest,
                    alert_level
                )


    def _check_thresholds(self, value: float, thresholds: Thresholds) -> str:
        """Determine alert level."""
        if thresholds.red_min and value < thresholds.red_min:
            return 'red'
        if thresholds.red_max and value > thresholds.red_max:
            return 'red'
        if thresholds.yellow_min and value < thresholds.yellow_min:
            return 'yellow'
        if thresholds.yellow_max and value > thresholds.yellow_max:
            return 'yellow'
        return 'green'


    async def _trigger_alert(
        self,
        metric_def: MetricDefinition,
        current_value: DataPoint,
        severity: str
    ):
        """Create alert and send notifications."""

        alert = Alert(
            alert_id=uuid4(),
            metric_id=metric_def.metric_id,
            severity=severity,
            triggered_at=datetime.now(),
            threshold_breached=metric_def.thresholds,
            actual_value=current_value.value,
            status='active'
        )

        await alert_repository.save(alert)
        await notification_service.send_alert(alert)
```

---

## Part 5: Neo4j Graph Algorithms (Deep Dive)

### 5.1 Dependency Analysis

**PageRank for Requirement Importance**:
```cypher
// Create in-memory graph projection
CALL gds.graph.project(
  'requirementGraph',
  'Requirement',
  {
    DEPENDS_ON: {
      orientation: 'REVERSE'  // Incoming edges = more important
    }
  }
)

// Run PageRank
CALL gds.pageRank.stream('requirementGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS requirement,
       gds.util.asNode(nodeId).id AS id,
       score
ORDER BY score DESC
LIMIT 20

// Interpretation:
// High PageRank = Many requirements depend on this
// = Removing this has widespread impact
// = Should be stable, well-tested
```

**Community Detection for Feature Clustering**:
```cypher
// Detect communities (clusters of related requirements)
CALL gds.louvain.stream('requirementGraph')
YIELD nodeId, communityId
WITH communityId, collect(gds.util.asNode(nodeId)) AS requirements
RETURN communityId,
       size(requirements) as cluster_size,
       [r in requirements | r.name][0..5] as sample_requirements
ORDER BY cluster_size DESC

// Use cases:
// - Automatic epic creation (cluster = epic)
// - Team assignment (cluster = team responsibility)
// - Architecture modules (cluster = bounded context)
```

**Betweenness Centrality for Bottleneck Detection**:
```cypher
// Find requirements that are "bridges" between clusters
CALL gds.betweenness.stream('requirementGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS requirement,
       score
ORDER BY score DESC
LIMIT 20

// High betweenness = This requirement connects many other requirements
// = Bottleneck in dependency graph
// = Delays here affect many downstream items
// = Prioritize for early completion
```

### 5.2 Impact Analysis with Multiple Relationship Types

```cypher
// Complex impact query: "If we remove OAuth, what's affected?"
MATCH path = (oauth:Requirement {name: "OAuth2 Integration"})<-[rel:DEPENDS_ON|IMPLEMENTS|USES*]-(affected)
WHERE ALL(r IN relationships(path) WHERE type(r) IN ['DEPENDS_ON', 'IMPLEMENTS', 'USES'])
RETURN DISTINCT affected.name AS affected_item,
       affected.view_type AS view,
       length(path) AS distance,
       [r IN relationships(path) | type(r)] AS relationship_chain
ORDER BY distance, view

// Result:
// - Feature "User Login" (FEATURE view, distance 1, [DEPENDS_ON])
// - Code "login_handler.py" (CODE view, distance 2, [DEPENDS_ON, IMPLEMENTS])
// - Test "test_login.py" (TEST view, distance 3, [DEPENDS_ON, IMPLEMENTS, TESTS])
// ... (potentially 100s of affected items across all 32 views)
```

---

## Part 6: Cascading Update Engine (Deep Dive)

### 6.1 Complete Cascade Algorithm

```python
class CascadingUpdateEngine:
    """Orchestrates updates across all 32 views."""

    async def execute_cascade(
        self,
        atom_change: AtomChange,
        dry_run: bool = False
    ) -> CascadeResult:
        """Execute cascading update across all affected views.

        Algorithm:
        1. Impact Analysis (find all affected atoms)
        2. Dependency Sort (topological order)
        3. Generate Update Plans (view-specific logic)
        4. Execute Updates (via Temporal workflow for reliability)
        5. Validate Consistency (ensure no broken refs)
        6. Publish Events (NATS for async consumers)
        """

        # Phase 1: Impact Analysis
        impact = await self.impact_analyzer.analyze_full(atom_change)
        # Returns: {
        #   'affected_views': [CODE, TEST, API, DATABASE, ...],
        #   'affected_atoms': [atom1, atom2, ...],
        #   'update_plans': [UpdatePlan, ...]
        # }

        # Phase 2: Topological Sort
        dep_graph = self._build_dependency_graph(impact.affected_atoms)
        update_order = nx.topological_sort(dep_graph)
        # Ensures dependencies are updated before dependents

        # Phase 3: Execute via Temporal (durable, retriable)
        workflow_id = f"cascade-{atom_change.requirement_id}-{uuid4()}"

        if dry_run:
            # Preview only
            return await self._preview_cascade(impact, update_order)
        else:
            # Execute durable workflow
            result = await self.temporal_client.execute_workflow(
                CascadeWorkflow.run,
                atom_change,
                impact,
                update_order,
                id=workflow_id,
                task_queue="cascade-queue",
                execution_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(max_attempts=3)
            )

            return result


@workflow.defn
class CascadeWorkflow:
    """Temporal workflow for reliable cascade execution."""

    @workflow.run
    async def run(
        self,
        atom_change: AtomChange,
        impact: ImpactAnalysis,
        update_order: List[UUID]
    ) -> CascadeResult:
        """Execute cascade with automatic retries and saga rollback."""

        completed_updates = []

        try:
            for atom_id in update_order:
                # Execute update activity (retriable)
                update_plan = impact.get_plan_for_atom(atom_id)

                result = await workflow.execute_activity(
                    apply_atom_update,
                    update_plan,
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        maximum_attempts=3,
                        backoff_coefficient=2.0
                    )
                )

                completed_updates.append(result)

        except Exception as e:
            # Rollback all completed updates (Saga pattern)
            workflow.logger.error(f"Cascade failed: {e}, rolling back...")

            for completed in reversed(completed_updates):
                await workflow.execute_activity(
                    rollback_atom_update,
                    completed,
                    start_to_close_timeout=timedelta(seconds=30)
                )

            raise CascadeFailedException(
                f"Cascade failed and rolled back: {e}",
                completed_updates=completed_updates
            )

        return CascadeResult(
            atom_change=atom_change,
            updates_applied=completed_updates,
            status='success'
        )
```

---

## Part 7: Caching Strategy (Multi-Layer)

### 7.1 Three-Layer Cache

**L1: In-Memory (Process-local)**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_feature_view(feature_id: UUID) -> FeatureView:
    """L1 cache: In-memory LRU."""
    # Only cache immutable data or with TTL
    pass
```

**L2: Redis (Distributed)**
```python
async def get_feature_view_cached(feature_id: UUID) -> FeatureView:
    """L2 cache: Redis distributed cache."""

    cache_key = f"feature:{feature_id}"

    # Try L2 (Redis)
    cached = await redis.get(cache_key)
    if cached:
        return FeatureView.from_json(cached)

    # Miss: Fetch from L3 (database)
    feature = await postgres.fetch_one(
        "SELECT * FROM feature_views WHERE id = $1",
        feature_id
    )

    # Populate L2
    await redis.setex(cache_key, 300, feature.to_json())  # 5 min TTL

    return feature
```

**L3: Database (PostgreSQL)**
```python
# Primary storage, always authoritative
```

### 7.2 Cache Invalidation

```python
async def on_feature_updated(event: FeatureUpdatedEvent):
    """Invalidate caches when feature changes."""

    # Invalidate L2 (Redis)
    await redis.delete(f"feature:{event.feature_id}")

    # Invalidate L1 (process-local) via pub/sub
    await redis.publish("cache.invalidate", json.dumps({
        "type": "feature",
        "id": str(event.feature_id)
    }))

    # All app instances subscribe to cache.invalidate and clear L1
```

---

## Summary

**Completed Deep Dives**: CODE, TEST, API_CONTRACT, MONITORING, Neo4j Algorithms, Cascading Engine, Caching Strategy

**Key Insights**:
1. **AST-level representation** enables advanced code queries
2. **Contract-first API development** with automatic mock generation
3. **Flakiness detection** improves test reliability
4. **Neo4j graph algorithms** provide unique capabilities (PageRank, community detection)
5. **Temporal workflows** ensure reliable cascading updates
6. **Multi-layer caching** (L1 in-memory, L2 Redis, L3 PostgreSQL) achieves 80%+ hit rate

**Total Infrastructure**:
- 10-11 services (PostgreSQL, Neo4j, TimescaleDB, Redis, NATS, Weaviate, S3, Temporal, Unleash, Nginx, optional Elasticsearch)
- 32 views fully supported
- 1000+ AI agents coordinated
- Event sourcing for compliance
- Semantic search across all views

**Cost**: $1,700-2,600/month managed services

---

**End of Internal View Architectures**

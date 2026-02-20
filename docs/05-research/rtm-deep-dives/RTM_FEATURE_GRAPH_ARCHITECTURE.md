# Feature Graph Architecture - Chaos-Resilient Design

## Core Philosophy

**Features, not requirements. Chaos, not compliance. Speed, not ceremony.**

## Graph Model

### Node Types

```python
# Primary node: Feature
class Feature(Node):
    # Identity
    id: str
    title: str
    description: str
    
    # Chaos metadata
    added_at: datetime
    added_by: str
    added_reason: str
    scope_wave: int
    
    # State
    status: FeatureStatus
    priority: int  # 1-100
    
    # Effort
    estimated_effort: int
    actual_effort: Optional[int]
    
    # Strong bindings (cascade on delete)
    code: List[CodeArtifact]
    tests: List[TestArtifact]
    docs: List[DocArtifact]
    apis: List[APIEndpoint]
    ui: List[UIComponent]

# Artifact nodes (owned by features)
class CodeArtifact(Node):
    path: str
    language: str
    lines_of_code: int
    owner_feature: str  # Feature ID

class TestArtifact(Node):
    path: str
    test_type: str  # unit, integration, e2e
    coverage: float
    owner_feature: str

class APIEndpoint(Node):
    method: str  # GET, POST, etc.
    path: str
    owner_feature: str

class UIComponent(Node):
    component_type: str  # page, modal, widget
    path: str
    owner_feature: str
```

### Edge Types

```python
class EdgeType(Enum):
    # Hierarchy
    DECOMPOSES_TO = "decomposes_to"  # Epic → Feature → Task
    PART_OF = "part_of"  # Task → Feature
    
    # Dependencies
    DEPENDS_ON = "depends_on"  # Feature A needs Feature B
    BLOCKS = "blocks"  # Feature A blocks Feature B
    ENABLES = "enables"  # Feature A enables Feature B
    
    # Conflicts
    CONFLICTS_WITH = "conflicts_with"  # Mutually exclusive
    DUPLICATES = "duplicates"  # Potential duplicate
    OVERLAPS = "overlaps"  # Partial overlap
    
    # Ownership
    OWNS = "owns"  # Feature owns artifact
    IMPLEMENTS = "implements"  # Code implements feature
    TESTS = "tests"  # Test validates feature
    DOCUMENTS = "documents"  # Doc describes feature
    
    # Temporal
    REPLACES = "replaces"  # New feature replaces old
    SUPERSEDES = "supersedes"  # Evolution
    DERIVED_FROM = "derived_from"  # Spawned from
```

## Storage Schema

### SQLite Schema for Chaos
```sql
-- Features table
CREATE TABLE features (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    priority INTEGER DEFAULT 50,
    
    -- Chaos tracking
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    added_by TEXT NOT NULL,
    added_reason TEXT,
    scope_wave INTEGER,
    
    -- Effort
    estimated_effort INTEGER,
    actual_effort INTEGER,
    
    -- Lifecycle
    cut_at TIMESTAMP,
    cut_reason TEXT,
    shipped_at TIMESTAMP,
    
    -- Metadata
    tags JSON,
    metadata JSON
);

-- Edges table (relationships)
CREATE TABLE edges (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    edge_type TEXT NOT NULL,
    
    -- Edge metadata
    strength REAL DEFAULT 1.0,  -- How strong is this link?
    confidence REAL DEFAULT 1.0,  -- How confident are we?
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    
    -- Cascade behavior
    cascade_delete BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (source_id) REFERENCES features(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES features(id) ON DELETE CASCADE
);

-- Artifacts table
CREATE TABLE artifacts (
    id TEXT PRIMARY KEY,
    artifact_type TEXT NOT NULL,  -- code, test, doc, api, ui
    path TEXT NOT NULL,
    owner_feature_id TEXT NOT NULL,
    
    -- Artifact metadata
    language TEXT,
    lines_of_code INTEGER,
    coverage REAL,
    
    -- Lifecycle
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    FOREIGN KEY (owner_feature_id) REFERENCES features(id) ON DELETE CASCADE
);

-- Scope waves table
CREATE TABLE scope_waves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    wave_type TEXT NOT NULL,  -- explosion, crash, pivot
    trigger TEXT NOT NULL,
    
    -- Metrics
    features_added INTEGER DEFAULT 0,
    features_cut INTEGER DEFAULT 0,
    features_changed INTEGER DEFAULT 0,
    effort_added INTEGER DEFAULT 0,
    effort_removed INTEGER DEFAULT 0,
    
    -- Metadata
    metadata JSON
);

-- Snapshots table (time travel)
CREATE TABLE snapshots (
    id TEXT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    label TEXT NOT NULL,
    
    -- Snapshot data
    features_snapshot JSON,
    edges_snapshot JSON,
    metrics_snapshot JSON
);

-- Indexes for performance
CREATE INDEX idx_features_status ON features(status);
CREATE INDEX idx_features_priority ON features(priority DESC);
CREATE INDEX idx_features_scope_wave ON features(scope_wave);
CREATE INDEX idx_edges_source ON edges(source_id);
CREATE INDEX idx_edges_target ON edges(target_id);
CREATE INDEX idx_edges_type ON edges(edge_type);
CREATE INDEX idx_artifacts_owner ON artifacts(owner_feature_id);
CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);
```

## Graph Algorithms for Chaos

### Transitive Dependency Closure
```python
def find_all_dependencies(feature_id: str) -> Set[str]:
    """Find all features this depends on (transitively)"""
    visited = set()
    queue = [feature_id]
    
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        
        # Find direct dependencies
        deps = db.execute("""
            SELECT target_id FROM edges
            WHERE source_id = ? AND edge_type = 'depends_on'
        """, (current,)).fetchall()
        
        queue.extend([d[0] for d in deps])
    
    visited.remove(feature_id)  # Don't include self
    return visited

def find_all_dependents(feature_id: str) -> Set[str]:
    """Find all features that depend on this (transitively)"""
    visited = set()
    queue = [feature_id]
    
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        
        # Find features that depend on current
        dependents = db.execute("""
            SELECT source_id FROM edges
            WHERE target_id = ? AND edge_type = 'depends_on'
        """, (current,)).fetchall()
        
        queue.extend([d[0] for d in dependents])
    
    visited.remove(feature_id)
    return visited
```

### Cycle Detection
```python
def detect_cycles() -> List[List[str]]:
    """Detect circular dependencies"""
    cycles = []
    
    def dfs(node, path, visited):
        if node in path:
            # Found cycle
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:])
            return
        
        if node in visited:
            return
        
        visited.add(node)
        path.append(node)
        
        # Get dependencies
        deps = db.execute("""
            SELECT target_id FROM edges
            WHERE source_id = ? AND edge_type = 'depends_on'
        """, (node,)).fetchall()
        
        for (dep,) in deps:
            dfs(dep, path.copy(), visited)
    
    # Check all features
    features = db.execute("SELECT id FROM features").fetchall()
    for (feature_id,) in features:
        dfs(feature_id, [], set())
    
    return cycles
```

### Critical Path Analysis
```python
def find_critical_path() -> List[str]:
    """Find longest dependency chain (critical path)"""
    
    def longest_path_from(node, memo):
        if node in memo:
            return memo[node]
        
        # Get dependencies
        deps = db.execute("""
            SELECT target_id FROM edges
            WHERE source_id = ? AND edge_type = 'depends_on'
        """, (node,)).fetchall()
        
        if not deps:
            memo[node] = ([node], 0)
            return memo[node]
        
        # Find longest path through dependencies
        max_path = []
        max_effort = 0
        
        for (dep,) in deps:
            path, effort = longest_path_from(dep, memo)
            if effort > max_effort:
                max_path = path
                max_effort = effort
        
        # Add current node
        feature = db.execute(
            "SELECT estimated_effort FROM features WHERE id = ?",
            (node,)
        ).fetchone()
        
        current_effort = feature[0] if feature else 0
        memo[node] = ([node] + max_path, max_effort + current_effort)
        return memo[node]
    
    # Find longest path from all root features
    roots = db.execute("""
        SELECT id FROM features
        WHERE id NOT IN (
            SELECT source_id FROM edges WHERE edge_type = 'depends_on'
        )
    """).fetchall()
    
    memo = {}
    critical_path = []
    max_effort = 0
    
    for (root,) in roots:
        path, effort = longest_path_from(root, memo)
        if effort > max_effort:
            critical_path = path
            max_effort = effort
    
    return critical_path
```

### Conflict Graph
```python
def build_conflict_graph() -> nx.Graph:
    """Build graph of conflicting features"""
    G = nx.Graph()
    
    # Add all active features as nodes
    features = db.execute("""
        SELECT id, title FROM features WHERE status = 'active'
    """).fetchall()
    
    for feature_id, title in features:
        G.add_node(feature_id, title=title)
    
    # Add conflict edges
    conflicts = db.execute("""
        SELECT source_id, target_id FROM edges
        WHERE edge_type IN ('conflicts_with', 'overlaps')
    """).fetchall()
    
    for source, target in conflicts:
        G.add_edge(source, target)
    
    return G

def find_conflict_clusters() -> List[Set[str]]:
    """Find clusters of conflicting features"""
    G = build_conflict_graph()
    return list(nx.connected_components(G))
```

## Mass Operations Engine

### Bulk Add with Auto-Linking
```python
class BulkAddEngine:
    def add_features_with_auto_link(self, features: List[Feature]):
        """Add features and automatically detect links"""
        
        # Add all features first
        for feature in features:
            db.execute("""
                INSERT INTO features (id, title, description, status, added_at, added_by, scope_wave)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (feature.id, feature.title, feature.description, feature.status,
                  feature.added_at, feature.added_by, feature.scope_wave))
        
        # Auto-detect links
        for i, feature1 in enumerate(features):
            for feature2 in features[i+1:]:
                # Check for duplicates (semantic similarity)
                similarity = self.compute_similarity(feature1.description, feature2.description)
                if similarity > 0.8:
                    self.create_edge(feature1.id, feature2.id, EdgeType.DUPLICATES, confidence=similarity)
                
                # Check for conflicts (keyword overlap)
                if self.has_keyword_conflict(feature1, feature2):
                    self.create_edge(feature1.id, feature2.id, EdgeType.CONFLICTS_WITH)
                
                # Check for dependencies (mentions in description)
                if feature2.id in feature1.description or feature2.title in feature1.description:
                    self.create_edge(feature1.id, feature2.id, EdgeType.DEPENDS_ON)
```

### Bulk Cut with Cascade
```python
class BulkCutEngine:
    def cut_features_cascade(self, feature_ids: List[str], reason: str) -> CutReport:
        """Cut features with full cascade"""
        
        # Find all affected features (dependents)
        all_affected = set(feature_ids)
        for fid in feature_ids:
            dependents = find_all_dependents(fid)
            all_affected.update(dependents)
        
        # Find all artifacts to delete
        artifacts_to_delete = []
        for fid in all_affected:
            artifacts = db.execute("""
                SELECT id, artifact_type, path FROM artifacts
                WHERE owner_feature_id = ?
            """, (fid,)).fetchall()
            artifacts_to_delete.extend(artifacts)
        
        # Calculate effort wasted
        effort_wasted = db.execute("""
            SELECT SUM(COALESCE(actual_effort, estimated_effort))
            FROM features
            WHERE id IN ({})
        """.format(','.join('?' * len(all_affected))), list(all_affected)).fetchone()[0]
        
        # Perform cascade delete
        for fid in all_affected:
            # Mark feature as cut
            db.execute("""
                UPDATE features
                SET status = 'cut', cut_at = ?, cut_reason = ?
                WHERE id = ?
            """, (datetime.now(), reason, fid))
            
            # Delete artifacts
            db.execute("""
                UPDATE artifacts
                SET deleted_at = ?
                WHERE owner_feature_id = ?
            """, (datetime.now(), fid))
        
        return CutReport(
            features_cut=list(all_affected),
            artifacts_deleted=artifacts_to_delete,
            effort_wasted=effort_wasted
        )
```


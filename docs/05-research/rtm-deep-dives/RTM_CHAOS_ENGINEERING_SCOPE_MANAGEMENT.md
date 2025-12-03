# Requirements Traceability - Chaos Engineering & Extreme Scope Management

## Problem Statement

**NOT compliance-driven. NOT regulatory-focused.**

**GOAL**: Manage **chaotic, explosive feature growth** in fast-moving product development where:
- Features are added **rapidly and continuously**
- Scope **expands and contracts violently**
- Requirements **change constantly**
- Teams need to **track everything** without drowning
- **Strong bindings** prevent orphaned work
- **Mass operations** are the norm, not the exception

## The Chaos Problem

### Typical Scenario
```
Day 1:   10 features planned
Day 7:   50 features added by stakeholders
Day 14:  30 features cut, 40 new ones added
Day 21:  Scope explosion - 200 features in flight
Day 30:  Scope crash - cut to 50 features for MVP
Day 45:  Another 100 features added for v2
```

### Pain Points
1. **Scope Explosion**: Features multiply faster than teams can track
2. **Orphaned Work**: Code/tests exist for deleted features
3. **Dependency Hell**: Cutting one feature breaks 10 others
4. **Context Loss**: Why was this feature added? Who requested it?
5. **Duplicate Work**: Same feature requested 3 different ways
6. **Impact Blindness**: Can't see what breaks when cutting features
7. **Merge Conflicts**: Feature branches diverge wildly

## Solution: Chaos-Resilient Feature Management

### Core Principles

1. **Everything is a Feature**: Not "requirements" - **features**
2. **Strong Bindings**: Delete a feature → cascade to all linked artifacts
3. **Mass Operations**: Bulk add/delete/move/merge features
4. **Impact Visualization**: See the blast radius instantly
5. **Temporal Snapshots**: Rewind to any point in time
6. **Conflict Detection**: Automatic detection of overlapping features
7. **Scope Metrics**: Real-time tracking of scope growth/crash

## Data Model for Chaos

### Feature Node
```python
class Feature:
    id: str
    title: str
    description: str
    status: FeatureStatus  # proposed, active, cut, shipped
    priority: int  # 1-100, changes constantly
    
    # Chaos tracking
    added_at: datetime
    added_by: str
    added_reason: str  # "Customer X demanded", "CEO wants", "Competitor has"
    cut_at: Optional[datetime]
    cut_reason: Optional[str]
    
    # Scope management
    estimated_effort: int  # story points
    actual_effort: Optional[int]
    scope_wave: int  # Which wave of scope explosion?
    
    # Strong bindings
    blocks: List[str]  # Feature IDs this blocks
    blocked_by: List[str]  # Feature IDs blocking this
    duplicates: List[str]  # Potential duplicates
    conflicts_with: List[str]  # Conflicting features
    
    # Artifacts (cascade delete)
    code_files: List[str]
    test_files: List[str]
    design_docs: List[str]
    api_endpoints: List[str]

class FeatureStatus(Enum):
    PROPOSED = "proposed"  # Just added
    ACTIVE = "active"  # Being worked on
    BLOCKED = "blocked"  # Blocked by dependencies
    CUT = "cut"  # Removed from scope
    SHIPPED = "shipped"  # Delivered
    ZOMBIE = "zombie"  # Cut but code still exists
```

### Scope Wave Tracking
```python
class ScopeWave:
    """Track waves of scope explosion/crash"""
    wave_id: int
    timestamp: datetime
    type: WaveType  # explosion, crash, pivot
    
    features_added: List[str]
    features_cut: List[str]
    features_changed: List[str]
    
    trigger: str  # "Stakeholder meeting", "Competitor launch", "Pivot"
    impact_score: float  # How much chaos did this cause?
    
    # Metrics
    total_effort_added: int
    total_effort_removed: int
    net_scope_change: int

class WaveType(Enum):
    EXPLOSION = "explosion"  # Massive feature add
    CRASH = "crash"  # Massive feature cut
    PIVOT = "pivot"  # Direction change
    MERGE = "merge"  # Feature consolidation
```

## Mass Operations

### Bulk Feature Add
```python
class BulkFeatureManager:
    def bulk_add_from_meeting(self, meeting_notes: str) -> List[Feature]:
        """Extract and add all features from meeting notes"""
        # Use NLP to extract features
        extracted = self.nlp.extract_features(meeting_notes)
        
        features = []
        for item in extracted:
            feature = Feature(
                id=self.generate_id(),
                title=item.title,
                description=item.description,
                status=FeatureStatus.PROPOSED,
                added_at=datetime.now(),
                added_by="stakeholder_meeting",
                added_reason=f"Extracted from meeting: {meeting_notes[:100]}",
                scope_wave=self.current_wave
            )
            
            # Auto-detect duplicates
            duplicates = self.find_duplicates(feature)
            if duplicates:
                feature.duplicates = [d.id for d in duplicates]
            
            # Auto-detect conflicts
            conflicts = self.find_conflicts(feature)
            if conflicts:
                feature.conflicts_with = [c.id for c in conflicts]
            
            features.append(feature)
            self.storage.create_feature(feature)
        
        # Create scope wave
        self.create_scope_wave(
            type=WaveType.EXPLOSION,
            features_added=[f.id for f in features],
            trigger="Stakeholder meeting"
        )
        
        return features
    
    def bulk_cut_features(self, feature_ids: List[str], reason: str):
        """Cut multiple features at once with cascade"""
        # Find all dependent features
        all_affected = set(feature_ids)
        for fid in feature_ids:
            dependents = self.find_dependents(fid)
            all_affected.update(dependents)
        
        # Warn about cascade
        if len(all_affected) > len(feature_ids):
            print(f"⚠️  Cutting {len(feature_ids)} features will affect {len(all_affected)} total")
            print(f"   Cascade will cut: {all_affected - set(feature_ids)}")
        
        # Cut all features
        for fid in all_affected:
            feature = self.storage.get_feature(fid)
            feature.status = FeatureStatus.CUT
            feature.cut_at = datetime.now()
            feature.cut_reason = reason
            self.storage.update_feature(feature)
            
            # Mark artifacts as orphaned
            self.mark_artifacts_orphaned(feature)
        
        # Create scope wave
        self.create_scope_wave(
            type=WaveType.CRASH,
            features_cut=list(all_affected),
            trigger=reason
        )
```

### Bulk Feature Merge
```python
def bulk_merge_duplicates(self) -> List[MergeResult]:
    """Find and merge duplicate features"""
    duplicates = self.find_all_duplicates()
    results = []
    
    for group in duplicates:
        # Pick primary (oldest or highest priority)
        primary = max(group, key=lambda f: (f.priority, -f.added_at.timestamp()))
        
        # Merge others into primary
        for feature in group:
            if feature.id != primary.id:
                # Transfer all links
                self.transfer_links(from_feature=feature, to_feature=primary)
                
                # Transfer artifacts
                primary.code_files.extend(feature.code_files)
                primary.test_files.extend(feature.test_files)
                
                # Mark as cut
                feature.status = FeatureStatus.CUT
                feature.cut_reason = f"Merged into {primary.id}"
                
                results.append(MergeResult(
                    merged_from=feature.id,
                    merged_into=primary.id
                ))
        
        self.storage.update_feature(primary)
    
    return results
```

## Impact Visualization

### Blast Radius Analysis
```python
class ImpactAnalyzer:
    def analyze_cut_impact(self, feature_id: str) -> ImpactReport:
        """Analyze impact of cutting a feature"""
        feature = self.storage.get_feature(feature_id)
        
        # Find all dependents (features that depend on this)
        dependents = self.find_all_dependents(feature_id)
        
        # Find all artifacts that will be orphaned
        orphaned_code = feature.code_files
        orphaned_tests = feature.test_files
        orphaned_docs = feature.design_docs
        
        # Calculate effort wasted
        effort_wasted = feature.actual_effort or feature.estimated_effort
        
        # Find features that will be unblocked
        unblocked = self.find_blocked_by(feature_id)
        
        return ImpactReport(
            feature_id=feature_id,
            dependents=dependents,
            orphaned_artifacts={
                'code': orphaned_code,
                'tests': orphaned_tests,
                'docs': orphaned_docs
            },
            effort_wasted=effort_wasted,
            unblocked_features=unblocked,
            blast_radius=len(dependents)
        )
    
    def visualize_dependency_graph(self, feature_id: str) -> str:
        """ASCII visualization of dependency graph"""
        graph = self.build_dependency_graph(feature_id)
        return self.render_ascii_graph(graph)
```

### Scope Metrics Dashboard
```python
class ScopeMetrics:
    def get_current_metrics(self) -> dict:
        """Real-time scope metrics"""
        features = self.storage.list_features()
        
        return {
            'total_features': len(features),
            'active_features': len([f for f in features if f.status == FeatureStatus.ACTIVE]),
            'proposed_features': len([f for f in features if f.status == FeatureStatus.PROPOSED]),
            'cut_features': len([f for f in features if f.status == FeatureStatus.CUT]),
            'zombie_features': len([f for f in features if f.status == FeatureStatus.ZOMBIE]),
            
            'total_estimated_effort': sum(f.estimated_effort for f in features if f.status == FeatureStatus.ACTIVE),
            'effort_wasted': sum(f.actual_effort or 0 for f in features if f.status == FeatureStatus.CUT),
            
            'scope_waves': len(self.storage.list_scope_waves()),
            'last_explosion': self.get_last_wave(WaveType.EXPLOSION),
            'last_crash': self.get_last_wave(WaveType.CRASH),
            
            'orphaned_artifacts': self.count_orphaned_artifacts(),
            'duplicate_features': len(self.find_all_duplicates()),
            'conflicting_features': len(self.find_all_conflicts()),
        }
    
    def plot_scope_over_time(self) -> str:
        """ASCII plot of scope changes"""
        waves = self.storage.list_scope_waves()
        
        # Build timeline
        timeline = []
        cumulative_scope = 0
        
        for wave in waves:
            cumulative_scope += wave.net_scope_change
            timeline.append((wave.timestamp, cumulative_scope, wave.type))
        
        return self.render_ascii_plot(timeline)
```

## CLI for Chaos Management

### Mass Operations CLI
```python
@app.command()
def explode(meeting_notes_file: str):
    """Add features from meeting notes (scope explosion)"""
    with open(meeting_notes_file) as f:
        notes = f.read()
    
    features = bulk_manager.bulk_add_from_meeting(notes)
    
    console.print(f"[red]💥 SCOPE EXPLOSION[/red]")
    console.print(f"   Added {len(features)} features")
    console.print(f"   Total scope: {metrics.get_current_metrics()['total_features']}")

@app.command()
def crash(reason: str, feature_ids: Optional[List[str]] = None):
    """Cut features (scope crash)"""
    if not feature_ids:
        # Interactive selection
        feature_ids = select_features_interactive()
    
    impact = impact_analyzer.analyze_cut_impact_bulk(feature_ids)
    
    console.print(f"[yellow]⚠️  IMPACT ANALYSIS[/yellow]")
    console.print(f"   Cutting {len(feature_ids)} features")
    console.print(f"   Will affect {impact.total_affected} features")
    console.print(f"   Will orphan {impact.orphaned_count} artifacts")
    console.print(f"   Effort wasted: {impact.effort_wasted} points")
    
    if Confirm.ask("Proceed with scope crash?"):
        bulk_manager.bulk_cut_features(feature_ids, reason)
        console.print(f"[red]💥 SCOPE CRASH COMPLETE[/red]")

@app.command()
def merge_duplicates():
    """Find and merge duplicate features"""
    duplicates = bulk_manager.find_all_duplicates()
    
    console.print(f"[cyan]Found {len(duplicates)} duplicate groups[/cyan]")
    
    for group in duplicates:
        console.print(f"\nDuplicate group:")
        for feature in group:
            console.print(f"  - {feature.id}: {feature.title}")
    
    if Confirm.ask("Merge all duplicates?"):
        results = bulk_manager.bulk_merge_duplicates()
        console.print(f"[green]✓ Merged {len(results)} features[/green]")

@app.command()
def impact(feature_id: str):
    """Show impact of cutting a feature"""
    report = impact_analyzer.analyze_cut_impact(feature_id)
    
    console.print(f"\n[bold]Impact Analysis: {feature_id}[/bold]")
    console.print(f"\nDependents: {len(report.dependents)}")
    for dep in report.dependents:
        console.print(f"  - {dep.id}: {dep.title}")
    
    console.print(f"\nOrphaned Artifacts:")
    console.print(f"  Code files: {len(report.orphaned_artifacts['code'])}")
    console.print(f"  Test files: {len(report.orphaned_artifacts['tests'])}")
    console.print(f"  Docs: {len(report.orphaned_artifacts['docs'])}")
    
    console.print(f"\nEffort Wasted: {report.effort_wasted} points")
    console.print(f"Blast Radius: {report.blast_radius} features")
    
    # Show dependency graph
    console.print(f"\n[bold]Dependency Graph:[/bold]")
    console.print(impact_analyzer.visualize_dependency_graph(feature_id))

@app.command()
def metrics():
    """Show scope metrics dashboard"""
    m = metrics.get_current_metrics()
    
    table = Table(title="Scope Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Total Features", str(m['total_features']))
    table.add_row("Active", str(m['active_features']))
    table.add_row("Proposed", str(m['proposed_features']))
    table.add_row("Cut", str(m['cut_features']))
    table.add_row("Zombie", str(m['zombie_features']))
    table.add_row("", "")
    table.add_row("Estimated Effort", f"{m['total_estimated_effort']} points")
    table.add_row("Effort Wasted", f"{m['effort_wasted']} points")
    table.add_row("", "")
    table.add_row("Scope Waves", str(m['scope_waves']))
    table.add_row("Orphaned Artifacts", str(m['orphaned_artifacts']))
    table.add_row("Duplicates", str(m['duplicate_features']))
    
    console.print(table)
    
    # Show scope over time
    console.print(f"\n[bold]Scope Over Time:[/bold]")
    console.print(metrics.plot_scope_over_time())
```

## Strong Bindings & Cascade Operations

### Cascade Delete
```python
class CascadeManager:
    def cascade_delete_feature(self, feature_id: str, dry_run: bool = False):
        """Delete feature and all linked artifacts"""
        feature = self.storage.get_feature(feature_id)
        
        # Find everything linked
        linked = {
            'code_files': feature.code_files,
            'test_files': feature.test_files,
            'design_docs': feature.design_docs,
            'api_endpoints': feature.api_endpoints,
            'dependent_features': self.find_dependents(feature_id)
        }
        
        if dry_run:
            return CascadeReport(feature_id=feature_id, would_delete=linked)
        
        # Delete code files
        for code_file in feature.code_files:
            self.delete_code_file(code_file)
        
        # Delete test files
        for test_file in feature.test_files:
            self.delete_test_file(test_file)
        
        # Delete design docs
        for doc in feature.design_docs:
            self.delete_doc(doc)
        
        # Mark dependent features as blocked
        for dep_id in linked['dependent_features']:
            dep = self.storage.get_feature(dep_id)
            dep.status = FeatureStatus.BLOCKED
            dep.blocked_by.append(f"Deleted: {feature_id}")
            self.storage.update_feature(dep)
        
        # Delete feature
        self.storage.delete_feature(feature_id)
        
        return CascadeReport(feature_id=feature_id, deleted=linked)

### Zombie Detection
```python
class ZombieDetector:
    """Detect orphaned code from cut features"""

    def find_zombies(self) -> List[ZombieArtifact]:
        """Find code/tests that exist but feature is cut"""
        zombies = []

        cut_features = self.storage.list_features(status=FeatureStatus.CUT)

        for feature in cut_features:
            # Check if code still exists
            for code_file in feature.code_files:
                if self.file_exists(code_file):
                    zombies.append(ZombieArtifact(
                        feature_id=feature.id,
                        artifact_type='code',
                        artifact_path=code_file,
                        cut_at=feature.cut_at,
                        cut_reason=feature.cut_reason
                    ))

            # Check if tests still exist
            for test_file in feature.test_files:
                if self.file_exists(test_file):
                    zombies.append(ZombieArtifact(
                        feature_id=feature.id,
                        artifact_type='test',
                        artifact_path=test_file,
                        cut_at=feature.cut_at,
                        cut_reason=feature.cut_reason
                    ))

        return zombies

    def cleanup_zombies(self, zombies: List[ZombieArtifact]):
        """Delete all zombie artifacts"""
        for zombie in zombies:
            console.print(f"Deleting zombie: {zombie.artifact_path}")
            self.delete_file(zombie.artifact_path)
```

## Conflict Detection

### Automatic Conflict Detection
```python
class ConflictDetector:
    def detect_conflicts(self, feature: Feature) -> List[Conflict]:
        """Detect features that conflict with this one"""
        conflicts = []
        all_features = self.storage.list_features(status=FeatureStatus.ACTIVE)

        for other in all_features:
            if other.id == feature.id:
                continue

            # Check for overlapping code files
            code_overlap = set(feature.code_files) & set(other.code_files)
            if code_overlap:
                conflicts.append(Conflict(
                    type=ConflictType.CODE_OVERLAP,
                    feature1=feature.id,
                    feature2=other.id,
                    details=f"Overlapping files: {code_overlap}"
                ))

            # Check for semantic similarity (potential duplicates)
            similarity = self.compute_similarity(feature.description, other.description)
            if similarity > 0.8:
                conflicts.append(Conflict(
                    type=ConflictType.SEMANTIC_DUPLICATE,
                    feature1=feature.id,
                    feature2=other.id,
                    details=f"Similarity: {similarity:.2f}"
                ))

            # Check for API endpoint conflicts
            endpoint_overlap = set(feature.api_endpoints) & set(other.api_endpoints)
            if endpoint_overlap:
                conflicts.append(Conflict(
                    type=ConflictType.API_CONFLICT,
                    feature1=feature.id,
                    feature2=other.id,
                    details=f"Conflicting endpoints: {endpoint_overlap}"
                ))

        return conflicts

class ConflictType(Enum):
    CODE_OVERLAP = "code_overlap"
    SEMANTIC_DUPLICATE = "semantic_duplicate"
    API_CONFLICT = "api_conflict"
    RESOURCE_CONFLICT = "resource_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"
```

## Temporal Snapshots

### Time Travel
```python
class TemporalManager:
    def create_snapshot(self, label: str) -> Snapshot:
        """Create a snapshot of current scope"""
        features = self.storage.list_features()

        snapshot = Snapshot(
            id=self.generate_id(),
            timestamp=datetime.now(),
            label=label,
            features=[f.to_dict() for f in features],
            metrics=self.metrics.get_current_metrics()
        )

        self.storage.save_snapshot(snapshot)
        return snapshot

    def restore_snapshot(self, snapshot_id: str):
        """Restore scope to a previous snapshot"""
        snapshot = self.storage.get_snapshot(snapshot_id)

        # Clear current features
        current = self.storage.list_features()
        for feature in current:
            self.storage.delete_feature(feature.id)

        # Restore features from snapshot
        for feature_data in snapshot.features:
            feature = Feature.from_dict(feature_data)
            self.storage.create_feature(feature)

        console.print(f"[green]✓ Restored to snapshot: {snapshot.label}[/green]")

    def compare_snapshots(self, snapshot1_id: str, snapshot2_id: str) -> SnapshotDiff:
        """Compare two snapshots"""
        s1 = self.storage.get_snapshot(snapshot1_id)
        s2 = self.storage.get_snapshot(snapshot2_id)

        s1_ids = {f['id'] for f in s1.features}
        s2_ids = {f['id'] for f in s2.features}

        return SnapshotDiff(
            added=s2_ids - s1_ids,
            removed=s1_ids - s2_ids,
            modified=self.find_modified(s1, s2)
        )

@app.command()
def snapshot(label: str):
    """Create a scope snapshot"""
    snapshot = temporal_manager.create_snapshot(label)
    console.print(f"[green]✓ Created snapshot: {label}[/green]")
    console.print(f"   ID: {snapshot.id}")
    console.print(f"   Features: {len(snapshot.features)}")

@app.command()
def restore(snapshot_id: str):
    """Restore to a previous snapshot"""
    if Confirm.ask(f"Restore to snapshot {snapshot_id}? This will delete current scope."):
        temporal_manager.restore_snapshot(snapshot_id)

@app.command()
def diff(snapshot1: str, snapshot2: str):
    """Compare two snapshots"""
    diff = temporal_manager.compare_snapshots(snapshot1, snapshot2)

    console.print(f"\n[bold]Snapshot Diff[/bold]")
    console.print(f"Added: {len(diff.added)} features")
    console.print(f"Removed: {len(diff.removed)} features")
    console.print(f"Modified: {len(diff.modified)} features")
```

## Real-World Chaos Scenarios

### Scenario 1: Post-Meeting Explosion
```bash
# Meeting ends, 50 new features requested
rtm explode meeting_notes.txt

# Output:
# 💥 SCOPE EXPLOSION
#    Added 50 features
#    Detected 5 duplicates
#    Detected 3 conflicts
#    Total scope: 150 features
```

### Scenario 2: Pre-Launch Crash
```bash
# Need to cut scope for MVP
rtm crash "MVP scope reduction" --interactive

# Interactive selection of features to cut
# Shows impact analysis for each
# Confirms cascade deletes
```

### Scenario 3: Zombie Cleanup
```bash
# Find orphaned code from cut features
rtm zombies

# Output:
# Found 23 zombie artifacts:
#   - src/feature_x.py (cut 2 weeks ago)
#   - tests/test_feature_y.py (cut 1 month ago)
#   ...

rtm zombies --cleanup
# Deletes all zombie artifacts
```

### Scenario 4: Merge Duplicates
```bash
# Find and merge duplicate features
rtm merge-duplicates

# Output:
# Found 3 duplicate groups:
#   Group 1: "User login", "Login feature", "Authentication"
#   Group 2: "Export CSV", "CSV export", "Download as CSV"
#   ...
```

## Key Differentiators from Compliance-Focused RTM

| Aspect | Compliance RTM | Chaos RTM |
|--------|---------------|-----------|
| **Goal** | Certification | Scope management |
| **Pace** | Slow, deliberate | Fast, chaotic |
| **Changes** | Controlled | Constant |
| **Operations** | Individual | Bulk/mass |
| **Focus** | Traceability | Impact & cleanup |
| **Metrics** | Coverage % | Scope growth/crash |
| **Artifacts** | Preserve all | Delete aggressively |
| **Duplicates** | Prevent | Detect & merge |
| **Conflicts** | Avoid | Detect & resolve |
| **Snapshots** | Audit trail | Time travel |
```


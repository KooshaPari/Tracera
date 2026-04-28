# Project State Visualization & Multi-View Decomposition

## Core Problem

**Goal**: Grasp entire project state instantly while drilling down into any view

### The Challenge
```
Project grows from:
  - 10 features → 500 features
  - 100 files → 10,000 files
  - 5 APIs → 200 APIs
  - 3 screens → 150 screens

Need to:
  ✓ See the whole picture instantly
  ✓ Drill down into any component
  ✓ Switch between views seamlessly
  ✓ Understand relationships at any level
  ✓ CRUD anything from any view
```

## Multi-View Architecture

### View Types

```python
class ViewType(Enum):
    # Product views
    FEATURE_VIEW = "feature"        # Features/epics/stories
    USER_VIEW = "user"              # User journeys/personas
    
    # Technical views
    CODE_VIEW = "code"              # Files/functions/classes
    API_VIEW = "api"                # Endpoints/services
    DATABASE_VIEW = "database"      # Tables/schemas/queries
    
    # UI views
    WIREFRAME_VIEW = "wireframe"    # Screens/components/buttons
    DESIGN_VIEW = "design"          # Design system/tokens
    
    # Testing views
    TEST_VIEW = "test"              # Test suites/cases
    COVERAGE_VIEW = "coverage"      # Coverage by feature
    
    # Architecture views
    SERVICE_VIEW = "service"        # Microservices/modules
    DEPENDENCY_VIEW = "dependency"  # Dependencies/imports
    
    # Temporal views
    TIMELINE_VIEW = "timeline"      # Changes over time
    ROADMAP_VIEW = "roadmap"        # Future plans

class View:
    """Base class for all views"""
    type: ViewType
    root_items: List[ViewItem]
    
    def render(self, depth: int = None) -> str:
        """Render view at specified depth"""
        pass
    
    def drill_down(self, item_id: str) -> View:
        """Drill down into specific item"""
        pass
    
    def switch_view(self, target_view: ViewType, item_id: str) -> View:
        """Switch to different view for same item"""
        pass
```

### Decomposable Items

Every item in every view can be decomposed:

```python
class ViewItem:
    """Base class for all view items"""
    id: str
    title: str
    type: str
    
    # Decomposition
    children: List[ViewItem]
    parent_id: Optional[str]
    
    # Cross-view links
    linked_items: Dict[ViewType, List[str]]
    
    # State
    status: str
    progress: float  # 0.0 to 1.0
    
    # Metadata
    owner: str
    created_at: datetime
    updated_at: datetime
    
    def decompose(self) -> List[ViewItem]:
        """Get all children"""
        return self.children
    
    def get_linked(self, view_type: ViewType) -> List[ViewItem]:
        """Get linked items in another view"""
        pass

# Example: Wireframe decomposition
class WireframeItem(ViewItem):
    """
    Screen
      ├─ Section
      │  ├─ Component
      │  │  ├─ Button
      │  │  ├─ Input
      │  │  └─ Label
      │  └─ Component
      └─ Section
    """
    wireframe_type: str  # screen, section, component, button, input, etc.
    
    # Links to other views
    implements_features: List[str]  # Feature IDs
    uses_apis: List[str]            # API endpoint IDs
    has_tests: List[str]            # Test IDs
    implemented_by: List[str]       # Code file IDs

# Example: Code decomposition
class CodeItem(ViewItem):
    """
    Module
      ├─ File
      │  ├─ Class
      │  │  ├─ Method
      │  │  │  ├─ Function call
      │  │  │  └─ Variable
      │  │  └─ Method
      │  └─ Function
      └─ File
    """
    code_type: str  # module, file, class, method, function
    path: str
    language: str
    
    # Links to other views
    implements_features: List[str]
    calls_apis: List[str]
    tested_by: List[str]
    uses_database: List[str]

# Example: Feature decomposition
class FeatureItem(ViewItem):
    """
    Epic
      ├─ Feature
      │  ├─ User Story
      │  │  ├─ Task
      │  │  └─ Task
      │  └─ User Story
      └─ Feature
    """
    feature_type: str  # epic, feature, story, task
    
    # Links to other views
    has_wireframes: List[str]
    implemented_in_code: List[str]
    uses_apis: List[str]
    has_tests: List[str]
```

## View Switching & Navigation

### Cross-View Navigation

```python
class ViewNavigator:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.current_view: View = None
        self.current_item: Optional[ViewItem] = None
        self.view_stack: List[Tuple[View, ViewItem]] = []
    
    def switch_view(self, target_view: ViewType, item_id: Optional[str] = None):
        """Switch to different view, optionally focusing on specific item"""
        
        if item_id:
            # Find corresponding item in target view
            target_item = self.find_linked_item(self.current_item, target_view)
        else:
            target_item = None
        
        # Save current state
        self.view_stack.append((self.current_view, self.current_item))
        
        # Switch view
        self.current_view = self.load_view(target_view)
        self.current_item = target_item
        
        return self.current_view
    
    def drill_down(self, item_id: str):
        """Drill down into item's children"""
        item = self.storage.get_item(item_id)
        
        # Save current state
        self.view_stack.append((self.current_view, self.current_item))
        
        # Focus on item
        self.current_item = item
        
        return item.children
    
    def drill_up(self):
        """Go back up one level"""
        if self.current_item and self.current_item.parent_id:
            parent = self.storage.get_item(self.current_item.parent_id)
            self.current_item = parent
            return parent
        return None
    
    def back(self):
        """Go back to previous view"""
        if self.view_stack:
            self.current_view, self.current_item = self.view_stack.pop()
        return self.current_view
    
    def find_linked_item(self, item: ViewItem, target_view: ViewType) -> Optional[ViewItem]:
        """Find corresponding item in target view"""
        if target_view in item.linked_items:
            linked_ids = item.linked_items[target_view]
            if linked_ids:
                return self.storage.get_item(linked_ids[0])
        return None
```

### Example Navigation Flow

```python
# Start in feature view
navigator.switch_view(ViewType.FEATURE_VIEW)
# Shows: All epics

# Drill down into epic
navigator.drill_down("EPIC-001")
# Shows: Features in EPIC-001

# Drill down into feature
navigator.drill_down("FEATURE-042")
# Shows: User stories in FEATURE-042

# Switch to wireframe view for this feature
navigator.switch_view(ViewType.WIREFRAME_VIEW, "FEATURE-042")
# Shows: Wireframes implementing FEATURE-042

# Drill down into screen
navigator.drill_down("SCREEN-LOGIN")
# Shows: Components in login screen

# Drill down into component
navigator.drill_down("COMPONENT-LOGIN-FORM")
# Shows: Buttons, inputs, labels in form

# Switch to code view for this component
navigator.switch_view(ViewType.CODE_VIEW, "COMPONENT-LOGIN-FORM")
# Shows: Code files implementing login form

# Back to previous view
navigator.back()
# Back to: Login form component in wireframe view
```

## TUI Interface for Multi-View

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Project: MyApp                    View: Feature    [F1: Help]   │
├─────────────────────────────────────────────────────────────────┤
│ Views: [Feature] Code  API  Wireframe  Test  Timeline          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ▼ EPIC-001: User Authentication (80% complete)                  │
│   ├─ ▼ FEATURE-042: Login System (100%)                         │
│   │   ├─ ✓ STORY-101: User can login with email                │
│   │   ├─ ✓ STORY-102: User can reset password                  │
│   │   └─ ⧗ STORY-103: User can enable 2FA                      │
│   └─ ▶ FEATURE-043: Session Management (60%)                    │
│                                                                  │
│ ▶ EPIC-002: Dashboard (40% complete)                            │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Selected: STORY-101: User can login with email                  │
│                                                                  │
│ Status: Complete  │  Owner: alice  │  Effort: 5 points          │
│                                                                  │
│ Linked Items:                                                    │
│   Wireframes: SCREEN-LOGIN (3 components)                       │
│   Code: auth/login.py, ui/LoginForm.tsx                         │
│   APIs: POST /api/auth/login                                    │
│   Tests: test_login.py (8 tests, 100% coverage)                 │
│                                                                  │
│ [Enter: Drill Down] [Tab: Switch View] [/: Search] [q: Quit]   │
└─────────────────────────────────────────────────────────────────┘
```

### Interactive Commands

```python
class TUIController:
    def __init__(self):
        self.navigator = ViewNavigator(storage)
        self.selected_item: Optional[ViewItem] = None
    
    def handle_key(self, key: str):
        if key == 'enter':
            # Drill down into selected item
            if self.selected_item:
                self.navigator.drill_down(self.selected_item.id)
        
        elif key == 'backspace':
            # Drill up
            self.navigator.drill_up()
        
        elif key == 'tab':
            # Cycle through views
            self.cycle_views()
        
        elif key == 'f':
            # Switch to feature view
            self.navigator.switch_view(ViewType.FEATURE_VIEW)
        
        elif key == 'c':
            # Switch to code view
            self.navigator.switch_view(ViewType.CODE_VIEW, self.selected_item.id)
        
        elif key == 'w':
            # Switch to wireframe view
            self.navigator.switch_view(ViewType.WIREFRAME_VIEW, self.selected_item.id)
        
        elif key == 'a':
            # Switch to API view
            self.navigator.switch_view(ViewType.API_VIEW, self.selected_item.id)
        
        elif key == 't':
            # Switch to test view
            self.navigator.switch_view(ViewType.TEST_VIEW, self.selected_item.id)
        
        elif key == 'e':
            # Edit selected item
            self.edit_item(self.selected_item)
        
        elif key == 'd':
            # Delete selected item (with cascade)
            self.delete_item(self.selected_item)
        
        elif key == 'n':
            # Create new item
            self.create_item()
        
        elif key == '/':
            # Search
            self.search()
```

## Project State Dashboard

### Overview Dashboard

```python
class ProjectStateDashboard:
    def render(self) -> str:
        """Render complete project state"""
        
        state = self.compute_state()
        
        return f"""
┌─────────────────────────────────────────────────────────────────┐
│                    PROJECT STATE DASHBOARD                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Features:  {state.features_total} total                          │
│   ✓ Complete: {state.features_complete} ({state.features_pct}%) │
│   ⧗ In Progress: {state.features_in_progress}                   │
│   ○ Not Started: {state.features_not_started}                   │
│                                                                  │
│ Code:  {state.code_files} files, {state.code_lines} lines       │
│   Coverage: {state.test_coverage}%                               │
│   Zombies: {state.zombie_files} orphaned files                  │
│                                                                  │
│ UI:  {state.wireframes} screens, {state.components} components  │
│   Implemented: {state.ui_implemented}%                           │
│   Tested: {state.ui_tested}%                                    │
│                                                                  │
│ APIs:  {state.api_endpoints} endpoints                          │
│   Documented: {state.api_documented}%                            │
│   Tested: {state.api_tested}%                                   │
│                                                                  │
│ Tests:  {state.test_count} tests                                │
│   Passing: {state.tests_passing} ({state.tests_passing_pct}%)  │
│   Failing: {state.tests_failing}                                │
│                                                                  │
│ Health Score: {state.health_score}/100                          │
│   ████████████████░░░░ {state.health_score}%                    │
│                                                                  │
│ [Press any view key to explore]                                 │
└─────────────────────────────────────────────────────────────────┘
        """
```

## CRUD Operations from Any View

### Universal CRUD Interface

```python
class UniversalCRUD:
    def create(self, view_type: ViewType, parent_id: Optional[str] = None):
        """Create new item in current view"""
        
        # Get item template for view type
        template = self.get_template(view_type)
        
        # Interactive form
        item_data = self.prompt_for_data(template)
        
        # Create item
        item = self.storage.create_item(view_type, item_data, parent_id)
        
        # Auto-link to related items
        self.auto_link(item)
        
        return item
    
    def read(self, item_id: str, view_type: ViewType) -> ViewItem:
        """Read item with all linked items"""
        item = self.storage.get_item(item_id)
        
        # Load linked items from other views
        for linked_view in ViewType:
            if linked_view != view_type:
                item.linked_items[linked_view] = self.storage.get_linked_items(
                    item_id, linked_view
                )
        
        return item
    
    def update(self, item_id: str, updates: dict):
        """Update item and propagate changes"""
        item = self.storage.get_item(item_id)
        
        # Update item
        for key, value in updates.items():
            setattr(item, key, value)
        
        item.updated_at = datetime.now()
        self.storage.update_item(item)
        
        # Propagate status changes to linked items
        if 'status' in updates:
            self.propagate_status_change(item)
        
        return item
    
    def delete(self, item_id: str, cascade: bool = True):
        """Delete item with optional cascade"""
        item = self.storage.get_item(item_id)
        
        if cascade:
            # Find all linked items
            linked = self.find_all_linked(item)
            
            # Show impact
            impact = self.analyze_delete_impact(item, linked)
            
            if self.confirm_delete(impact):
                # Cascade delete
                for linked_item in linked:
                    self.storage.delete_item(linked_item.id)
                
                self.storage.delete_item(item_id)
        else:
            # Just delete this item
            self.storage.delete_item(item_id)
```


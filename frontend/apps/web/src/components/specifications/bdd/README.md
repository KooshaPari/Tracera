# BDD/Gherkin Components

Comprehensive suite of React components for building Behavior-Driven Development (BDD) and Gherkin feature specifications UI.

## Components Overview

### 1. FeatureCard

**Purpose:** Display a feature summary with user story format, scenario statistics, and status.

**Features:**
- Feature number and name display
- User story format (As a... I want... So that...)
- Scenario count with pass/fail/pending breakdown
- Progress bar showing pass rate
- Status badge (draft, active, deprecated, archived)
- Tag display (max 2 tags with +N indicator)
- Click handler for navigation

**Props:**
```typescript
interface FeatureCardProps {
  feature: Feature;
  onClick?: () => void;
  className?: string;
}
```

**Example Usage:**
```tsx
import { FeatureCard } from "@/components/specifications/bdd";

<FeatureCard
  feature={{
    featureNumber: "F-001",
    name: "User Authentication",
    status: "active",
    asA: "new user",
    iWant: "to create an account",
    soThat: "I can access the application",
    scenarioCount: 5,
    passedScenarios: 4,
    failedScenarios: 1,
    pendingScenarios: 0,
    tags: ["auth", "security"],
  }}
  onClick={() => console.log("Feature clicked")}
/>
```

---

### 2. ScenarioCard

**Purpose:** Display individual scenarios with step breakdown and execution statistics.

**Features:**
- Scenario number and title
- Status badge with icon
- Given/When/Then step counts
- Execution statistics (count, last run date)
- Scenario Outline indicator
- Run button for test execution
- Link to related test cases
- Collapsible test case view

**Props:**
```typescript
interface ScenarioCardProps {
  scenario: Scenario;
  onRun?: () => void;
  onClick?: () => void;
  onViewTestCases?: () => void;
  className?: string;
  showExecutionStats?: boolean;
}
```

**Example Usage:**
```tsx
import { ScenarioCard } from "@/components/specifications/bdd";

<ScenarioCard
  scenario={{
    scenarioNumber: "S-001",
    title: "User successfully logs in",
    status: "passing",
    givenSteps: ["I am on the login page"],
    whenSteps: ["I enter valid credentials", "I click login"],
    thenSteps: ["I should be redirected to dashboard"],
    isOutline: false,
    executionCount: 42,
    lastExecutedAt: new Date().toISOString(),
  }}
  onRun={() => console.log("Running scenario")}
  onViewTestCases={() => console.log("View test cases")}
  showExecutionStats={true}
/>
```

---

### 3. StepBadge

**Purpose:** Color-coded badge for Gherkin step types.

**Features:**
- Type-specific colors (Given: blue, When: amber, Then: green, And/But: gray)
- Icons for visual recognition
- Compact and full display modes
- Description tooltips
- Accessibility-friendly

**Supported Types:**
- `Given` - Precondition (blue)
- `When` - Action (amber)
- `Then` - Outcome (green)
- `And` - Additional step (gray)
- `But` - Alternative step (gray)
- `Background` - Setup steps (purple)

**Props:**
```typescript
interface StepBadgeProps {
  type: StepType;
  className?: string;
  compact?: boolean;
}
```

**Example Usage:**
```tsx
import { StepBadge } from "@/components/specifications/bdd";

// Compact display
<StepBadge type="Given" compact />

// Full display with description
<StepBadge type="When" />

// Custom styling
<StepBadge type="Then" className="text-lg" />
```

---

### 4. GherkinEditor

**Purpose:** Monaco-based Gherkin editor with syntax highlighting, validation, and auto-completion.

**Features:**
- Syntax highlighting for Gherkin keywords
- Auto-completion for step definitions and keywords
- Real-time validation with error/warning indicators
- Line numbers and word wrap
- Read-only mode support
- Error list with line numbers
- Suggested steps panel
- Dark theme default

**Props:**
```typescript
interface GherkinEditorProps {
  content: string;
  onChange?: (content: string) => void;
  onValidation?: (isValid: boolean, errors: ValidationError[]) => void;
  className?: string;
  height?: string;
  showSuggestions?: boolean;
  readOnly?: boolean;
}

interface ValidationError {
  line: number;
  message: string;
  severity: "error" | "warning";
}
```

**Example Usage:**
```tsx
import { GherkinEditor } from "@/components/specifications/bdd";

const [content, setContent] = useState("");
const [errors, setErrors] = useState<ValidationError[]>([]);

<GherkinEditor
  content={content}
  onChange={setContent}
  onValidation={(isValid, validationErrors) => {
    setErrors(validationErrors);
  }}
  height="500px"
  showSuggestions={true}
  readOnly={false}
/>
```

**Validation:**
- Checks for unmatched quotes
- Validates step keywords
- Warns about invalid line starts
- Real-time error reporting

**Built-in Step Suggestions:**
```
Given I am on the login page
Given I have entered valid credentials
When I click the login button
When I enter the password
Then I should see the dashboard
And I should see a confirmation message
But I should not have access to admin features
```

---

### 5. GherkinViewer

**Purpose:** Formatted, read-only display of Gherkin with collapsible scenarios and parsed structure.

**Features:**
- Automatic Gherkin parsing (Feature, Background, Scenarios, Steps)
- Feature header with primary styling
- Background steps section
- Collapsible scenarios (expandable/collapsible mode)
- Color-coded step badges
- Examples section indicator
- Fallback to Monaco editor for complex content
- Interactive step cards with hover effects

**Props:**
```typescript
interface GherkinViewerProps {
  content: string;
  className?: string;
  height?: string;
  collapsible?: boolean;
  showLineNumbers?: boolean;
}
```

**Example Usage:**
```tsx
import { GherkinViewer } from "@/components/specifications/bdd";

const gherkinContent = `
Feature: User Authentication
  Background:
    Given the authentication service is running

  Scenario: User logs in successfully
    Given I am on the login page
    When I enter valid credentials
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see my profile information

  Scenario Outline: Invalid login attempts
    Given I am on the login page
    When I enter "<username>" and "<password>"
    Then I should see the error "<error_message>"

    Examples:
      | username | password | error_message |
      | user     | wrong    | Invalid password |
      | invalid  | pass123  | User not found |
`;

<GherkinViewer
  content={gherkinContent}
  collapsible={true}
  showLineNumbers={true}
  height="600px"
/>
```

**Parsing Behavior:**
- Extracts Feature header
- Identifies Background steps
- Groups scenarios with their steps
- Detects Scenario Outlines
- Associates Examples sections

---

### 6. ExamplesTable

**Purpose:** Editable data table for Scenario Outline examples.

**Features:**
- Dynamic row and column management
- Editable cells with inline editing
- Add/remove rows and columns
- Column renaming
- Visual row numbering
- Example count badge
- Keyboard navigation (Enter, Escape)
- Read-only mode support

**Props:**
```typescript
interface ExamplesTableProps {
  data: TableExample[];
  columns: string[];
  onDataChange?: (data: TableExample[]) => void;
  onColumnsChange?: (columns: string[]) => void;
  editable?: boolean;
  className?: string;
  title?: string;
}

type TableExample = Record<string, string>;
```

**Example Usage:**
```tsx
import { ExamplesTable } from "@/components/specifications/bdd";

const [examples, setExamples] = useState<TableExample[]>([
  { username: "alice", password: "pass123", status: "success" },
  { username: "bob", password: "wrong", status: "fail" },
]);

const [columns, setColumns] = useState(["username", "password", "status"]);

<ExamplesTable
  data={examples}
  columns={columns}
  onDataChange={setExamples}
  onColumnsChange={setColumns}
  editable={true}
  title="Login Examples"
/>
```

**Features in Detail:**
- **Inline Editing:** Click any cell to edit, Enter to confirm, Escape to cancel
- **Column Management:** Click X on column header to remove, + button to add
- **Row Management:** Click trash icon to remove row, "Add Example" button for new rows
- **Cell Reordering:** Drag columns (requires parent drag handler)

---

## Usage Examples

### Complete Feature Specification View

```tsx
import {
  FeatureCard,
  ScenarioCard,
  GherkinViewer,
  GherkinEditor,
} from "@/components/specifications/bdd";

export function FeatureSpecificationView() {
  const [showEditor, setShowEditor] = useState(false);
  const [gherkinContent, setGherkinContent] = useState("");

  return (
    <div className="space-y-6">
      {/* Feature Overview */}
      <FeatureCard
        feature={/* ... */}
        onClick={() => setShowEditor(true)}
      />

      {/* Editor Section */}
      {showEditor && (
        <GherkinEditor
          content={gherkinContent}
          onChange={setGherkinContent}
          showSuggestions={true}
        />
      )}

      {/* Viewer Section */}
      <GherkinViewer
        content={gherkinContent}
        collapsible={true}
      />

      {/* Scenarios */}
      <div className="grid gap-4">
        {scenarios.map((scenario) => (
          <ScenarioCard
            key={scenario.id}
            scenario={scenario}
            onRun={() => executeScenario(scenario)}
            showExecutionStats={true}
          />
        ))}
      </div>
    </div>
  );
}
```

### Scenario Outline with Examples

```tsx
import { GherkinEditor, ExamplesTable } from "@/components/specifications/bdd";

export function ScenarioOutlineEditor() {
  const [content, setContent] = useState(`
Scenario Outline: Login with various credentials
  Given I am on the login page
  When I enter "<username>" and "<password>"
  Then I should see "<result>"
  `);

  const [examples, setExamples] = useState([
    { username: "alice", password: "pass123", result: "success" },
    { username: "bob", password: "wrong", result: "error" },
  ]);

  return (
    <div className="space-y-4">
      <GherkinEditor content={content} onChange={setContent} />
      <ExamplesTable
        data={examples}
        columns={["username", "password", "result"]}
        onDataChange={setExamples}
      />
    </div>
  );
}
```

---

## Styling & Customization

All components use Tailwind CSS and respect the project's design system:

- **Colors:**
  - Given: Blue (`bg-blue-500/10`)
  - When: Amber (`bg-amber-500/10`)
  - Then: Green (`bg-green-500/10`)
  - And/But: Gray (`bg-gray-500/10`)

- **Spacing:** Consistent with Tailwind scale
- **Typography:** Uses font scales from design system
- **Animations:** Smooth transitions (200ms)
- **Dark Mode:** Fully supported via Monaco dark theme

---

## Accessibility

All components include:
- ARIA labels and roles
- Keyboard navigation support
- Focus management
- High contrast indicators
- Screen reader friendly
- Semantic HTML structure

---

## Dependencies

- `@monaco-editor/react` - Code editor
- `@tracertm/ui` - UI components library
- `lucide-react` - Icon library
- `framer-motion` - Ready for animation integration
- React hooks for state management

---

## File Structure

```
/components/specifications/bdd/
├── FeatureCard.tsx        # Feature summary display
├── ScenarioCard.tsx       # Individual scenario display
├── StepBadge.tsx         # Step type badge component
├── GherkinEditor.tsx     # Monaco-based editor
├── GherkinViewer.tsx     # Formatted viewer
├── ExamplesTable.tsx     # Data table for examples
├── index.ts              # Barrel exports
└── README.md             # This file
```

---

## Development Notes

### Type Safety
All components are fully typed with TypeScript. Import types from `@tracertm/types`:

```tsx
import type { Feature, Scenario, ScenarioStatus } from "@tracertm/types";
```

### Performance
- Components use proper memoization
- Editor uses Monaco's efficient rendering
- No unnecessary re-renders
- Lazy loading ready

### Testing
Components are designed for easy testing:
- Pure props-based behavior
- Callback handlers for user actions
- Mockable data structures
- Accessible selectors for E2E testing

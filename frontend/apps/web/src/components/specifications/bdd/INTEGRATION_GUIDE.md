# BDD Components Integration Guide

This guide demonstrates how to integrate the BDD/Gherkin components into your application.

## Quick Start

### Basic Import

```tsx
import {
  FeatureCard,
  ScenarioCard,
  GherkinEditor,
  GherkinViewer,
  StepBadge,
  ExamplesTable,
} from "@/components/specifications/bdd";
```

---

## 1. Displaying Features

### Simple Feature List

```tsx
import { FeatureCard } from "@/components/specifications/bdd";
import { useState } from "react";

export function FeaturesView() {
  const [features] = useState([
    {
      featureNumber: "F-001",
      name: "User Authentication",
      status: "active" as const,
      asA: "new user",
      iWant: "to create an account",
      soThat: "I can access the platform",
      scenarioCount: 5,
      passedScenarios: 4,
      failedScenarios: 1,
      pendingScenarios: 0,
      tags: ["auth", "security"],
    },
  ]);

  return (
    <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      {features.map((feature) => (
        <FeatureCard
          key={feature.featureNumber}
          feature={feature}
          onClick={() => console.log(`Clicked ${feature.name}`)}
        />
      ))}
    </div>
  );
}
```

---

## 2. Editing Gherkin Specifications

### Gherkin Editor with Validation

```tsx
import { GherkinEditor } from "@/components/specifications/bdd";
import { useState } from "react";
import { Button } from "@tracertm/ui";

export function SpecificationEditor() {
  const [content, setContent] = useState(`
Feature: User Login
  As a user
  I want to log in to the system
  So that I can access my account

  Background:
    Given the login page is loaded
    And the authentication service is available

  Scenario: Successful login
    Given I am on the login page
    When I enter valid credentials
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see my profile

  Scenario: Failed login with invalid password
    Given I am on the login page
    When I enter an invalid password
    And I click the login button
    Then I should see an error message
    And I should remain on the login page
  `.trim());

  const [errors, setErrors] = useState<any[]>([]);
  const [isSaved, setIsSaved] = useState(false);

  const handleValidation = (isValid: boolean, validationErrors: any[]) => {
    setErrors(validationErrors);
    console.log(`Validation: ${isValid ? "Valid" : "Invalid"}`);
  };

  const handleSave = async () => {
    if (errors.length === 0) {
      // Save specification
      console.log("Saving specification...");
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 2000);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Edit Specification</h2>
        <Button
          onClick={handleSave}
          disabled={errors.length > 0}
          variant={isSaved ? "default" : "outline"}
        >
          {isSaved ? "✓ Saved" : "Save Changes"}
        </Button>
      </div>

      <GherkinEditor
        content={content}
        onChange={setContent}
        onValidation={handleValidation}
        height="500px"
        showSuggestions={true}
      />
    </div>
  );
}
```

---

## 3. Viewing Formatted Specifications

### Interactive Gherkin Viewer

```tsx
import { GherkinViewer } from "@/components/specifications/bdd";

export function SpecificationViewer({ specContent }: { specContent: string }) {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Feature Specification</h2>
      <GherkinViewer
        content={specContent}
        collapsible={true}
        showLineNumbers={false}
        height="600px"
      />
    </div>
  );
}
```

---

## 4. Displaying Scenarios

### Scenario List with Execution

```tsx
import { ScenarioCard } from "@/components/specifications/bdd";
import { useState } from "react";

export function ScenariosView() {
  const [scenarios] = useState([
    {
      scenarioNumber: "S-001",
      title: "User successfully logs in",
      status: "passing" as const,
      givenSteps: [
        "I am on the login page",
        "the authentication service is running",
      ],
      whenSteps: [
        "I enter valid credentials",
        "I click the login button",
      ],
      thenSteps: [
        "I should be redirected to the dashboard",
        "I should see my profile",
      ],
      isOutline: false,
      executionCount: 42,
      lastExecutedAt: new Date().toISOString(),
    },
    {
      scenarioNumber: "S-002",
      title: "User fails to login with invalid password",
      status: "failing" as const,
      givenSteps: ["I am on the login page"],
      whenSteps: ["I enter an invalid password", "I click the login button"],
      thenSteps: [
        "I should see an error message",
        "I should remain on the login page",
      ],
      isOutline: false,
      executionCount: 15,
      lastExecutedAt: new Date(Date.now() - 3600000).toISOString(),
    },
  ]);

  const handleRunScenario = (scenario: any) => {
    console.log(`Running scenario: ${scenario.title}`);
    // Trigger test execution
  };

  const handleViewTestCases = (scenario: any) => {
    console.log(`Viewing test cases for: ${scenario.title}`);
    // Navigate to test cases
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Scenarios</h2>
      <div className="grid gap-3">
        {scenarios.map((scenario) => (
          <ScenarioCard
            key={scenario.scenarioNumber}
            scenario={scenario}
            onRun={() => handleRunScenario(scenario)}
            onViewTestCases={() => handleViewTestCases(scenario)}
            showExecutionStats={true}
          />
        ))}
      </div>
    </div>
  );
}
```

---

## 5. Managing Scenario Outline Examples

### Examples Table Editor

```tsx
import { ExamplesTable, GherkinEditor } from "@/components/specifications/bdd";
import { useState } from "react";

export function ScenarioOutlineEditor() {
  const [gherkinContent, setGherkinContent] = useState(`
Scenario Outline: User login with different credentials
  Given I am on the login page
  When I enter "<username>" as username
  And I enter "<password>" as password
  And I click the login button
  Then I should see "<result>"
  `.trim());

  const [examples, setExamples] = useState([
    { username: "alice@example.com", password: "SecurePass123!", result: "Success" },
    { username: "bob@example.com", password: "WrongPassword", result: "Error" },
    { username: "invalid@user", password: "pass123", result: "Error" },
  ]);

  const [columns, setColumns] = useState(["username", "password", "result"]);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Edit Scenario Outline</h2>
        <GherkinEditor
          content={gherkinContent}
          onChange={setGherkinContent}
          height="300px"
          readOnly={false}
        />
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4">Examples</h3>
        <ExamplesTable
          data={examples}
          columns={columns}
          onDataChange={setExamples}
          onColumnsChange={setColumns}
          editable={true}
          title="Test Data"
        />
      </div>
    </div>
  );
}
```

---

## 6. Step Badges

### Step Type Indicators

```tsx
import { StepBadge } from "@/components/specifications/bdd";

export function StepDisplay() {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <StepBadge type="Given" compact />
        <span>I am on the login page</span>
      </div>

      <div className="flex items-center gap-2">
        <StepBadge type="When" compact />
        <span>I enter valid credentials</span>
      </div>

      <div className="flex items-center gap-2">
        <StepBadge type="Then" compact />
        <span>I should see the dashboard</span>
      </div>

      <div className="flex items-center gap-2">
        <StepBadge type="And" compact />
        <span>I should see my profile</span>
      </div>

      <div className="space-y-2 mt-4">
        <h3 className="font-semibold">Full display:</h3>
        <StepBadge type="Given" />
        <StepBadge type="When" />
        <StepBadge type="Then" />
      </div>
    </div>
  );
}
```

---

## 7. Complete Dashboard Example

### Comprehensive Feature Management Dashboard

```tsx
import {
  FeatureCard,
  ScenarioCard,
  GherkinViewer,
  GherkinEditor,
  ExamplesTable,
} from "@/components/specifications/bdd";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@tracertm/ui";
import { useState } from "react";

export function BDDDashboard() {
  const [selectedFeature, setSelectedFeature] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [gherkinContent, setGherkinContent] = useState("");

  const features = [
    {
      featureNumber: "F-001",
      name: "Authentication",
      status: "active" as const,
      asA: "user",
      iWant: "to log in",
      soThat: "I can access my account",
      scenarioCount: 5,
      passedScenarios: 4,
      failedScenarios: 1,
      pendingScenarios: 0,
      tags: ["auth"],
    },
  ];

  const scenarios = [
    {
      scenarioNumber: "S-001",
      title: "Login success",
      status: "passing" as const,
      givenSteps: ["I am on login page"],
      whenSteps: ["I click login"],
      thenSteps: ["I see dashboard"],
      isOutline: false,
      executionCount: 10,
      lastExecutedAt: new Date().toISOString(),
    },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">BDD Dashboard</h1>

      <Tabs defaultValue="features" className="space-y-4">
        <TabsList>
          <TabsTrigger value="features">Features</TabsTrigger>
          <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
          <TabsTrigger value="editor">Editor</TabsTrigger>
        </TabsList>

        <TabsContent value="features">
          <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <FeatureCard
                key={feature.featureNumber}
                feature={feature}
                onClick={() => setSelectedFeature(feature.featureNumber)}
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="scenarios">
          <div className="space-y-3">
            {scenarios.map((scenario) => (
              <ScenarioCard
                key={scenario.scenarioNumber}
                scenario={scenario}
                onRun={() => console.log("Running scenario")}
                showExecutionStats={true}
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="editor" className="space-y-4">
          <div className="flex gap-2">
            <button
              onClick={() => setEditMode(!editMode)}
              className="px-4 py-2 bg-primary text-primary-foreground rounded"
            >
              {editMode ? "View" : "Edit"}
            </button>
          </div>

          {editMode ? (
            <GherkinEditor
              content={gherkinContent}
              onChange={setGherkinContent}
              height="600px"
            />
          ) : (
            <GherkinViewer content={gherkinContent} height="600px" />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

---

## 8. Type Safety

### Working with Types

```tsx
import type { Feature, Scenario, ScenarioStatus } from "@tracertm/types";
import {
  ValidationError,
  TableExample,
} from "@/components/specifications/bdd";

export function TypedExample() {
  const feature: Feature = {
    featureNumber: "F-001",
    name: "Login",
    status: "active" as const,
    // ... other required fields
  };

  const scenario: Scenario = {
    scenarioNumber: "S-001",
    title: "User logs in",
    status: "passing" as const,
    // ... other required fields
  };

  const validationErrors: ValidationError[] = [
    {
      line: 5,
      message: "Invalid step keyword",
      severity: "error",
    },
  ];

  const examples: TableExample[] = [
    { username: "alice", password: "pass123" },
    { username: "bob", password: "pass456" },
  ];

  return <div>{/* Use typed data */}</div>;
}
```

---

## 9. Custom Styling

### Tailwind Integration

```tsx
import { FeatureCard } from "@/components/specifications/bdd";

export function StyledFeature() {
  return (
    <FeatureCard
      feature={/* ... */}
      className="
        shadow-lg
        border-2
        border-primary
        rounded-xl
        hover:shadow-2xl
        dark:bg-slate-900
      "
    />
  );
}
```

---

## 10. Accessibility Considerations

All components follow accessibility best practices:

- **Keyboard Navigation:** Tab through all interactive elements
- **Screen Readers:** Proper ARIA labels and roles
- **Color Contrast:** WCAG AA compliant
- **Focus Management:** Visible focus indicators
- **Semantic HTML:** Proper heading hierarchy

```tsx
import { GherkinEditor } from "@/components/specifications/bdd";

export function AccessibleEditor() {
  return (
    <main>
      <h1>Feature Specification Editor</h1>
      <GherkinEditor
        content=""
        onChange={(content) => console.log(content)}
        height="500px"
        // All interactive elements are keyboard accessible
      />
    </main>
  );
}
```

---

## 11. Performance Tips

### Memoization

```tsx
import { useMemo } from "react";
import { FeatureCard } from "@/components/specifications/bdd";

export function OptimizedFeatureList({ features }: { features: Feature[] }) {
  const filteredFeatures = useMemo(
    () => features.filter((f) => f.status === "active"),
    [features]
  );

  return (
    <div className="grid gap-4">
      {filteredFeatures.map((feature) => (
        <FeatureCard key={feature.featureNumber} feature={feature} />
      ))}
    </div>
  );
}
```

### Lazy Loading

```tsx
import { lazy, Suspense } from "react";

const GherkinEditor = lazy(() =>
  import("@/components/specifications/bdd").then((m) => ({
    default: m.GherkinEditor,
  }))
);

export function LazyEditor() {
  return (
    <Suspense fallback={<div>Loading editor...</div>}>
      <GherkinEditor content="" onChange={() => {}} />
    </Suspense>
  );
}
```

---

## 12. Testing

### Component Testing with Playwright

```typescript
import { test, expect } from "@playwright/test";

test("ScenarioCard displays correctly", async ({ page }) => {
  await page.goto("/scenarios");

  // Check card is rendered
  const card = await page.locator("[role='article']").first();
  expect(card).toBeVisible();

  // Check scenario title
  const title = card.locator("h4");
  expect(title).toContainText("User successfully logs in");

  // Check step counts
  const steps = card.locator("text=/Given|When|Then/");
  expect(steps).toHaveCount(3);

  // Test run button
  const runButton = card.locator("button[title='Run scenario']");
  await runButton.click();
});
```

---

## Common Patterns

### Feature List with Filtering

```tsx
import { FeatureCard } from "@/components/specifications/bdd";
import { Input } from "@tracertm/ui";
import { useState, useMemo } from "react";

export function FilteredFeatures() {
  const [search, setSearch] = useState("");
  const [features] = useState(/* ... */);

  const filtered = useMemo(
    () =>
      features.filter(
        (f) =>
          f.name.toLowerCase().includes(search.toLowerCase()) ||
          f.tags.some((t) => t.toLowerCase().includes(search.toLowerCase()))
      ),
    [features, search]
  );

  return (
    <div className="space-y-4">
      <Input
        placeholder="Search features..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {filtered.map((f) => (
          <FeatureCard key={f.featureNumber} feature={f} />
        ))}
      </div>
    </div>
  );
}
```

---

## Troubleshooting

### Monaco Editor Not Loading

Ensure `@monaco-editor/react` is installed:

```bash
bun add @monaco-editor/react
```

### Type Errors with Feature/Scenario

Make sure to import types from `@tracertm/types`:

```tsx
import type { Feature, Scenario } from "@tracertm/types";
```

### Validation Errors Not Showing

Check that `onValidation` callback is properly wired and `ValidationError[]` is typed correctly.

---

## API Reference

See [README.md](./README.md) for complete API documentation.

---

## Support

For issues or feature requests, please refer to the project's issue tracker or documentation.

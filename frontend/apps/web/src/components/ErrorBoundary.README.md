# Error Boundary Implementation Guide

## Overview

Error boundaries are React components that catch JavaScript errors anywhere in their child component tree, log those errors, and display a fallback UI. This prevents the entire application from crashing when a single component fails.

## Features

Our ErrorBoundary component provides:

- **Automatic error catching**: Catches errors in component tree
- **Sentry integration**: Automatically reports errors to Sentry (if configured)
- **Custom fallback UI**: Flexible fallback rendering
- **Error context**: Named boundaries for easier debugging
- **Development details**: Shows stack traces in development mode
- **Reset functionality**: Allows users to retry after an error

## Basic Usage

### Wrap Critical Components

```tsx
import { ErrorBoundary } from "@/components/ErrorBoundary";

function App() {
  return (
    <ErrorBoundary name="AppRoot">
      <YourComponent />
    </ErrorBoundary>
  );
}
```

### With Custom Fallback

```tsx
import { ErrorBoundary } from "@/components/ErrorBoundary";

function CustomFallback(error: Error, reset: () => void) {
  return (
    <div>
      <h2>Oops! Something went wrong</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary name="GraphView" fallback={CustomFallback}>
      <GraphComponent />
    </ErrorBoundary>
  );
}
```

### Using Higher-Order Component

```tsx
import { withErrorBoundary } from "@/components/ErrorBoundary";

const GraphView = ({ data }) => {
  // Component implementation
};

// Wrap component with error boundary
export default withErrorBoundary(GraphView, {
  name: "GraphView",
  showDetails: true
});
```

## Safe Component Wrappers

We provide pre-wrapped versions of critical components:

### Graph Components

```tsx
import {
  SafeGraphViewContainer,
  SafeFlowGraphView,
  SafeEnhancedGraphView,
  SafeVirtualizedGraphView,
  SafeUnifiedGraphView,
} from "@/components/graph/SafeGraphComponents";

// Use safe version instead of direct import
function MyPage() {
  return <SafeGraphViewContainer projectId={id} />;
}
```

### Form Components

```tsx
import {
  SafeCreateItemForm,
  SafeCreateProblemForm,
  SafeCreateProcessForm,
  SafeCreateTestCaseForm,
  SafeCreateProjectForm,
  SafeCreateLinkForm,
} from "@/components/forms/SafeFormComponents";

// Use safe version instead of direct import
function MyDialog() {
  return <SafeCreateItemForm onSubmit={handleSubmit} />;
}
```

## Where to Use Error Boundaries

### ✅ Always Use For:

1. **Graph/Visualization Components**
   - Complex rendering logic
   - Heavy computations
   - External libraries (D3, Cytoscape, etc.)

2. **Form Components**
   - User input handling
   - Validation logic
   - API submissions

3. **Route Components**
   - Page-level components
   - Lazy-loaded routes
   - Dynamic content

4. **Third-party Integrations**
   - External widgets
   - Analytics components
   - Social media embeds

### ❌ Don't Use For:

1. **Event handlers** - Use try/catch instead
2. **Async code** - Use try/catch or .catch()
3. **Server-side rendering** - Not supported
4. **Errors in the error boundary itself**

## Props Reference

### ErrorBoundary Props

```typescript
interface ErrorBoundaryProps {
  children: ReactNode;

  // Optional custom fallback renderer
  fallback?: (error: Error, reset: () => void) => ReactNode;

  // Name for identification in logs/Sentry
  name?: string;

  // Show error details in production (default: false)
  showDetails?: boolean;

  // Callback when error is caught
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}
```

## Sentry Integration

Error boundaries automatically report to Sentry when configured:

### Setup Sentry

1. Install Sentry:
```bash
bun add @sentry/react
```

2. Set environment variable:
```bash
VITE_SENTRY_DSN=your-sentry-dsn
```

3. Sentry is automatically initialized in `src/lib/sentry.ts`

### What Gets Reported

- Error message and stack trace
- Component stack trace
- Error boundary name
- User context (if set)
- Breadcrumbs leading to error

## Examples

### Route-Level Error Boundary

```tsx
// In route file
import { ErrorBoundary } from "@/components/ErrorBoundary";

export const Route = createFileRoute("/dashboard")({
  component: DashboardComponent,
  errorComponent: ({ error }) => (
    <ErrorBoundary name="DashboardRoute">
      <div>Error in dashboard: {error.message}</div>
    </ErrorBoundary>
  ),
});
```

### Lazy-Loaded Component with Error Boundary

```tsx
import { lazy, Suspense } from "react";
import { ErrorBoundary } from "@/components/ErrorBoundary";

const HeavyComponent = lazy(() => import("./HeavyComponent"));

function App() {
  return (
    <ErrorBoundary name="HeavyComponent">
      <Suspense fallback={<Loading />}>
        <HeavyComponent />
      </Suspense>
    </ErrorBoundary>
  );
}
```

### Multiple Error Boundaries

```tsx
function App() {
  return (
    <ErrorBoundary name="AppRoot">
      <Header />

      <ErrorBoundary name="Sidebar">
        <Sidebar />
      </ErrorBoundary>

      <ErrorBoundary name="MainContent">
        <MainContent />
      </ErrorBoundary>

      <Footer />
    </ErrorBoundary>
  );
}
```

### Error Boundary with Callback

```tsx
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { toast } from "sonner";

function handleError(error: Error, errorInfo: React.ErrorInfo) {
  // Custom error handling
  console.error("Custom handler:", error);
  toast.error(`Error: ${error.message}`);

  // Send to analytics
  analytics.track("component_error", {
    error: error.message,
    component: errorInfo.componentStack,
  });
}

function App() {
  return (
    <ErrorBoundary name="Analytics" onError={handleError}>
      <AnalyticsWidget />
    </ErrorBoundary>
  );
}
```

## Testing Error Boundaries

### Test Component That Throws

```tsx
import { render, screen } from "@testing-library/react";
import { ErrorBoundary } from "@/components/ErrorBoundary";

function ThrowError() {
  throw new Error("Test error");
}

test("catches error and shows fallback", () => {
  render(
    <ErrorBoundary name="Test">
      <ThrowError />
    </ErrorBoundary>
  );

  expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
});
```

### Test Custom Fallback

```tsx
test("renders custom fallback", () => {
  const fallback = (error: Error) => <div>Custom: {error.message}</div>;

  render(
    <ErrorBoundary fallback={fallback}>
      <ThrowError />
    </ErrorBoundary>
  );

  expect(screen.getByText(/custom: test error/i)).toBeInTheDocument();
});
```

## Best Practices

1. **Name your boundaries**: Always provide a `name` prop for easier debugging
2. **Granular boundaries**: Use multiple boundaries to isolate failures
3. **User-friendly messages**: Provide clear error messages to users
4. **Recovery options**: Always provide a way to recover (reset, reload, etc.)
5. **Log errors**: Ensure errors are logged for debugging
6. **Test error states**: Write tests for error scenarios
7. **Don't overuse**: Only wrap components that might fail
8. **Combine with Suspense**: Use together for complete error handling

## Common Patterns

### Protected Route with Error Boundary

```tsx
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

export const Route = createFileRoute("/protected")({
  component: () => (
    <ErrorBoundary name="ProtectedPage">
      <ProtectedRoute>
        <ProtectedContent />
      </ProtectedRoute>
    </ErrorBoundary>
  ),
});
```

### Form Dialog with Error Boundary

```tsx
import { Dialog } from "@/components/ui/dialog";
import { SafeCreateItemForm } from "@/components/forms/SafeFormComponents";

function CreateItemDialog() {
  return (
    <Dialog>
      <DialogContent>
        <SafeCreateItemForm
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      </DialogContent>
    </Dialog>
  );
}
```

## Troubleshooting

### Error boundaries not catching errors?

Error boundaries do NOT catch:
- Errors in event handlers (use try/catch)
- Errors in async code (use .catch())
- Errors during SSR
- Errors in the error boundary itself

### Sentry not reporting?

Check:
1. `VITE_SENTRY_DSN` is set
2. Sentry is initialized in main.tsx
3. You're in production mode (or `VITE_SENTRY_ENABLED=true`)
4. Error is not filtered by `beforeSend` hook

### Error boundary keeps resetting?

Check:
1. Parent component is not re-rendering
2. Key prop is not changing
3. State is properly managed

## Resources

- [React Error Boundaries Docs](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [Sentry React Docs](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Error Boundary Best Practices](https://kentcdodds.com/blog/use-react-error-boundary-to-handle-errors-in-react)

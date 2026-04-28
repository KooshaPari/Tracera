# TraceRTM Frontend Testing Guide

## Running Tests

### All Tests

```bash
cd frontend/apps/web
npm run test
```

### With Coverage

```bash
npm run test:coverage
```

### Watch Mode

```bash
npm run test:watch
```

### UI Mode

```bash
npm run test:ui
```

## Test Structure

```
frontend/apps/web/src/__tests__/
├── setup.ts                      # Test setup
├── hooks/
│   ├── useItems.test.ts         # Items hook tests
│   ├── useProjects.test.ts      # Projects hook tests
│   └── useLinks.test.ts         # Links hook tests
├── components/
│   └── CreateItemForm.test.tsx  # Component tests
└── utils/
    └── api.test.ts              # API utility tests
```

## Coverage Goals

- Lines: 80%
- Functions: 80%
- Branches: 80%
- Statements: 80%

Reports generated in `coverage/`

## Writing Tests

### Hook Test Example

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useItems } from '../../hooks/useItems';

it('should fetch items', async () => {
  const { result } = renderHook(() => useItems(), {
    wrapper: createWrapper(),
  });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));

  expect(result.current.data).toEqual(mockItems);
});
```

### Component Test Example

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

it('should submit form', async () => {
  render(<CreateItemForm onSubmit={mockOnSubmit} />)

  await userEvent.type(screen.getByLabelText(/Title/), 'Test')
  await userEvent.click(screen.getByText('Submit'))

  expect(mockOnSubmit).toHaveBeenCalled()
})
```

## Testing Tools

- **Vitest**: Test runner
- **@testing-library/react**: Component testing
- **@testing-library/user-event**: User interactions
- **@testing-library/jest-dom**: Custom matchers

## Best Practices

1. **Mock fetch calls** to avoid real API requests
2. **Use user-event** for realistic interactions
3. **Test accessibility** with semantic queries
4. **Test error states** and loading states
5. **Keep tests focused** - one assertion per test when possible
6. **Use data-testid** sparingly - prefer semantic queries

## Mocking Patterns

### Mock fetch

```typescript
const mockFetch = vi.fn();
global.fetch = mockFetch;

mockFetch.mockResolvedValueOnce({
  ok: true,
  json: async () => mockData,
});
```

### Mock React Query

```typescript
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return ({ children }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};
```

## Package Scripts

Add these to `package.json`:

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage"
  }
}
```

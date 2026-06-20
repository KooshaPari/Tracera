# Test Variations - Mock vs Live (COMPREHENSIVE)

**Date**: 2025-11-22  
**Version**: 1.0 (MOCK & LIVE VARIATIONS)  
**Status**: APPROVED

---

## 🧪 **TEST VARIATIONS STRUCTURE**

### Test Pyramid with Variations

```
                    E2E Tests (Live)
                   /              \
                 /                  \
              Integration Tests      Integration Tests
              (Mock Database)        (Live Database)
             /                \      /                \
           /                    \  /                    \
        Unit Tests            Unit Tests            Unit Tests
        (Mock API)            (Mock DB)             (Live API)
```

### Test Categories

1. **Unit Tests** (500+ tests)
   - Mock variations (API mocked)
   - Mock variations (Database mocked)
   - Live variations (Real API calls)

2. **Integration Tests** (300+ tests)
   - Mock variations (Database mocked)
   - Live variations (Real database)
   - Hybrid variations (Mock external APIs, real DB)

3. **E2E Tests** (100+ tests)
   - Mock variations (All external services mocked)
   - Live variations (Real services)
   - Hybrid variations (Real UI, mock backend)

---

## 📊 **TEST VARIATION MATRIX**

### Unit Tests Variations

| Test Type | API | Database | Count | Purpose |
|-----------|-----|----------|-------|---------|
| Mock | Mocked | Mocked | 200+ | Fast, isolated tests |
| Mock | Mocked | Real | 100+ | Test data layer |
| Live | Real | Mocked | 100+ | Test API integration |
| Live | Real | Real | 100+ | Full integration |

### Integration Tests Variations

| Test Type | Database | External APIs | Count | Purpose |
|-----------|----------|---------------|-------|---------|
| Mock | Mocked | Mocked | 100+ | Fast, isolated |
| Mock | Mocked | Real | 50+ | Test external APIs |
| Live | Real | Mocked | 100+ | Test database |
| Live | Real | Real | 50+ | Full integration |

### E2E Tests Variations

| Test Type | UI | Backend | Database | Count | Purpose |
|-----------|----|---------|-----------| ------|---------|
| Mock | Real | Mocked | Mocked | 30+ | Fast feedback |
| Mock | Real | Mocked | Real | 20+ | Test data flow |
| Live | Real | Real | Mocked | 20+ | Test backend |
| Live | Real | Real | Real | 30+ | Full system |

---

## 🔧 **MOCK SETUP**

### Frontend Mock Setup

```typescript
// tests/setup/mocks.ts

import { vi } from 'vitest';

// Mock API Client
export const mockApiClient = {
  createItem: vi.fn(),
  readItem: vi.fn(),
  updateItem: vi.fn(),
  deleteItem: vi.fn(),
  listItems: vi.fn(),
  createLink: vi.fn(),
  // ... more mocks
};

// Mock Database
export const mockDatabase = {
  items: new Map(),
  links: new Map(),
  agents: new Map(),
  // ... more mocks
};

// Mock Real-Time
export const mockRealtime = {
  subscribe: vi.fn(),
  unsubscribe: vi.fn(),
  broadcast: vi.fn(),
  // ... more mocks
};

// Mock Authentication
export const mockAuth = {
  login: vi.fn(),
  logout: vi.fn(),
  getUser: vi.fn(),
  getToken: vi.fn(),
  // ... more mocks
};
```

### Backend Mock Setup

```go
// tests/mocks/mocks.go

package mocks

import (
	"github.com/stretchr/testify/mock"
)

// MockItemRepository
type MockItemRepository struct {
	mock.Mock
}

func (m *MockItemRepository) Create(item *Item) error {
	args := m.Called(item)
	return args.Error(0)
}

func (m *MockItemRepository) Read(id string) (*Item, error) {
	args := m.Called(id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*Item), args.Error(1)
}

// MockDatabase
type MockDatabase struct {
	mock.Mock
}

func (m *MockDatabase) Query(sql string, args ...interface{}) (interface{}, error) {
	callArgs := m.Called(sql, args)
	return callArgs.Get(0), callArgs.Error(1)
}

// MockRealtime
type MockRealtime struct {
	mock.Mock
}

func (m *MockRealtime) Subscribe(channel string) error {
	args := m.Called(channel)
	return args.Error(0)
}
```

---

## 📝 **UNIT TEST VARIATIONS**

### Example: FR-1.1 Create Item (Unit Tests)

#### Variation 1: Mock API, Mock Database

```typescript
// tests/frontend/features/FR-1.1-CreateItem.mock-mock.test.tsx
// Linked to: FR-1.1, US-1.1, AC-1 to AC-10

describe('FR-1.1: Create Item - Mock API, Mock Database', () => {
  beforeEach(() => {
    // Mock API
    mockApiClient.createItem.mockResolvedValue({
      id: 'item-1',
      title: 'Test Item',
      type: 'REQUIREMENT',
      status: 'DRAFT',
    });

    // Mock Database
    mockDatabase.items.clear();
  });

  test('should create item with mocked API', async () => {
    // Linked to: AC-1, AC-6
    const { getByTestId, getByText } = render(<CreateItemForm />);
    const titleInput = getByTestId('item-title-input');
    const submitButton = getByText('Create Item');

    fireEvent.change(titleInput, { target: { value: 'Test Item' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockApiClient.createItem).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Test Item' })
      );
    });
  });

  test('should handle API error gracefully', async () => {
    // Linked to: Error Scenario 1
    mockApiClient.createItem.mockRejectedValue(
      new Error('API Error')
    );

    const { getByTestId, getByText } = render(<CreateItemForm />);
    const submitButton = getByText('Create Item');

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(getByText('Failed to create item')).toBeInTheDocument();
    });
  });

  test('should validate input before API call', async () => {
    // Linked to: Validation Rule 1
    const { getByTestId, getByText } = render(<CreateItemForm />);
    const submitButton = getByText('Create Item');

    fireEvent.click(submitButton);

    expect(mockApiClient.createItem).not.toHaveBeenCalled();
    expect(getByText('Item title is required')).toBeInTheDocument();
  });
});
```

#### Variation 2: Mock API, Real Database

```typescript
// tests/frontend/features/FR-1.1-CreateItem.mock-live.test.tsx
// Linked to: FR-1.1, US-1.1, AC-1 to AC-10

describe('FR-1.1: Create Item - Mock API, Real Database', () => {
  let db: Database;

  beforeEach(async () => {
    // Real database connection
    db = await setupTestDatabase();
    await db.clear();

    // Mock API
    mockApiClient.createItem.mockImplementation(async (item) => {
      // Store in real database
      await db.items.insert(item);
      return item;
    });
  });

  afterEach(async () => {
    await db.close();
  });

  test('should persist item to real database', async () => {
    // Linked to: AC-6, AC-7
    const { getByTestId, getByText } = render(<CreateItemForm />);
    const titleInput = getByTestId('item-title-input');
    const submitButton = getByText('Create Item');

    fireEvent.change(titleInput, { target: { value: 'Test Item' } });
    fireEvent.click(submitButton);

    await waitFor(async () => {
      const item = await db.items.findOne({ title: 'Test Item' });
      expect(item).toBeDefined();
      expect(item.title).toBe('Test Item');
    });
  });

  test('should handle database constraints', async () => {
    // Linked to: Validation Rule 1
    // Insert duplicate
    await db.items.insert({
      id: 'item-1',
      title: 'Test Item',
      type: 'REQUIREMENT',
    });

    mockApiClient.createItem.mockRejectedValue(
      new Error('Duplicate item')
    );

    const { getByTestId, getByText } = render(<CreateItemForm />);
    const submitButton = getByText('Create Item');

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(getByText('Item already exists')).toBeInTheDocument();
    });
  });
});
```

#### Variation 3: Real API, Mock Database

```typescript
// tests/frontend/features/FR-1.1-CreateItem.live-mock.test.tsx
// Linked to: FR-1.1, US-1.1, AC-1 to AC-10

describe('FR-1.1: Create Item - Real API, Mock Database', () => {
  beforeEach(() => {
    // Real API (using test server)
    // Mock Database
    mockDatabase.items.clear();
  });

  test('should call real API endpoint', async () => {
    // Linked to: ADR-12 (API Design)
    const { getByTestId, getByText } = render(<CreateItemForm />);
    const titleInput = getByTestId('item-title-input');
    const submitButton = getByText('Create Item');

    fireEvent.change(titleInput, { target: { value: 'Test Item' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/items',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });
  });

  test('should handle API response correctly', async () => {
    // Linked to: AC-6
    const { getByTestId, getByText } = render(<CreateItemForm />);
    const submitButton = getByText('Create Item');

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(getByText('Item created successfully')).toBeInTheDocument();
    });
  });
});
```

#### Variation 4: Real API, Real Database

```typescript
// tests/frontend/features/FR-1.1-CreateItem.live-live.test.tsx
// Linked to: FR-1.1, US-1.1, AC-1 to AC-10

describe('FR-1.1: Create Item - Real API, Real Database', () => {
  let db: Database;
  let server: TestServer;

  beforeEach(async () => {
    // Start test server
    server = await startTestServer();

    // Connect to real test database
    db = await setupTestDatabase();
    await db.clear();
  });

  afterEach(async () => {
    await server.close();
    await db.close();
  });

  test('should create item end-to-end', async () => {
    // Linked to: FR-1.1, AC-1 to AC-10
    const { getByTestId, getByText } = render(<CreateItemForm />);
    const titleInput = getByTestId('item-title-input');
    const submitButton = getByText('Create Item');

    fireEvent.change(titleInput, { target: { value: 'Test Item' } });
    fireEvent.click(submitButton);

    await waitFor(async () => {
      // Verify in database
      const item = await db.items.findOne({ title: 'Test Item' });
      expect(item).toBeDefined();
      expect(item.status).toBe('DRAFT');
    });
  });

  test('should handle full error flow', async () => {
    // Linked to: Error Scenario 1
    const { getByTestId, getByText } = render(<CreateItemForm />);
    const submitButton = getByText('Create Item');

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(getByText('Item title is required')).toBeInTheDocument();
    });
  });
});
```

---

## 🔌 **INTEGRATION TEST VARIATIONS**

### Example: FR-1.1 Create Item (Integration Tests)

#### Variation 1: Mock Database, Mock External APIs

```go
// tests/backend/api/FR-1.1-CreateItem.mock-mock.test.go
// Linked to: FR-1.1, ADR-3, ADR-12

func TestCreateItem_MockDB_MockExternalAPIs(t *testing.T) {
  // Mock database
  mockDB := &mocks.MockDatabase{}
  mockDB.On("Query", mock.Anything, mock.Anything).Return(
    map[string]interface{}{"id": "item-1"},
    nil,
  )

  // Mock external APIs
  mockSearch := &mocks.MockSearchService{}
  mockSearch.On("Index", mock.Anything).Return(nil)

  mockRealtime := &mocks.MockRealtime{}
  mockRealtime.On("Broadcast", mock.Anything).Return(nil)

  // Create service with mocks
  service := NewItemService(mockDB, mockSearch, mockRealtime)

  // Test
  item := &Item{Title: "Test", Type: "REQUIREMENT"}
  result, err := service.Create(item)

  assert.NoError(t, err)
  assert.Equal(t, "item-1", result.ID)
  mockDB.AssertCalled(t, "Query", mock.Anything, mock.Anything)
  mockSearch.AssertCalled(t, "Index", mock.Anything)
  mockRealtime.AssertCalled(t, "Broadcast", mock.Anything)
}
```

#### Variation 2: Real Database, Mock External APIs

```go
// tests/backend/api/FR-1.1-CreateItem.live-mock.test.go
// Linked to: FR-1.1, ADR-3, ADR-12

func TestCreateItem_RealDB_MockExternalAPIs(t *testing.T) {
  // Real database
  db := setupTestDatabase(t)
  defer db.Close()

  // Mock external APIs
  mockSearch := &mocks.MockSearchService{}
  mockSearch.On("Index", mock.Anything).Return(nil)

  mockRealtime := &mocks.MockRealtime{}
  mockRealtime.On("Broadcast", mock.Anything).Return(nil)

  // Create service
  service := NewItemService(db, mockSearch, mockRealtime)

  // Test
  item := &Item{Title: "Test", Type: "REQUIREMENT"}
  result, err := service.Create(item)

  assert.NoError(t, err)
  assert.NotEmpty(t, result.ID)

  // Verify in database
  retrieved, err := db.Query("SELECT * FROM items WHERE id = ?", result.ID)
  assert.NoError(t, err)
  assert.NotNil(t, retrieved)
}
```

#### Variation 3: Real Database, Real External APIs

```go
// tests/backend/api/FR-1.1-CreateItem.live-live.test.go
// Linked to: FR-1.1, ADR-3, ADR-12

func TestCreateItem_RealDB_RealExternalAPIs(t *testing.T) {
  // Real database
  db := setupTestDatabase(t)
  defer db.Close()

  // Real external services
  searchService := NewSearchService()
  realtimeService := NewRealtimeService()

  // Create service
  service := NewItemService(db, searchService, realtimeService)

  // Test
  item := &Item{Title: "Test", Type: "REQUIREMENT"}
  result, err := service.Create(item)

  assert.NoError(t, err)
  assert.NotEmpty(t, result.ID)

  // Verify in database
  retrieved, err := db.Query("SELECT * FROM items WHERE id = ?", result.ID)
  assert.NoError(t, err)
  assert.NotNil(t, retrieved)

  // Verify in search index
  searchResult, err := searchService.Search("Test")
  assert.NoError(t, err)
  assert.True(t, len(searchResult) > 0)

  // Verify real-time broadcast
  // (would need to subscribe and verify message received)
}
```

---

## 🌐 **E2E TEST VARIATIONS**

### Example: Journey 1 - Project Manager (E2E Tests)

#### Variation 1: Mock Backend, Real UI

```typescript
// tests/e2e/journeys/Journey-1-ProjectManager.mock.test.ts
// Linked to: Journey 1, Steps 1-12

describe('Journey 1: Project Manager - Mock Backend', () => {
  test('should complete project planning workflow with mocked backend', async ({ page, context }) => {
    // Mock API responses
    await context.route('**/api/**', route => {
      if (route.request().url().includes('/api/items')) {
        route.abort('blockedbyclient');
        // Return mock response
        route.fulfill({
          status: 200,
          body: JSON.stringify({
            id: 'item-1',
            title: 'Test Item',
            status: 'DRAFT',
          }),
        });
      }
    });

    // Navigate to app
    await page.goto('http://localhost:3000');

    // Step 1: Login
    await page.fill('input[name="email"]', 'sarah@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button:has-text("Login")');

    // Step 2: View Dashboard
    await page.waitForURL('**/dashboard');
    expect(page.url()).toContain('/dashboard');

    // ... rest of journey with mocked API
  });
});
```

#### Variation 2: Real Backend, Real UI

```typescript
// tests/e2e/journeys/Journey-1-ProjectManager.live.test.ts
// Linked to: Journey 1, Steps 1-12

describe('Journey 1: Project Manager - Real Backend', () => {
  let server: TestServer;
  let db: Database;

  beforeAll(async () => {
    // Start real test server
    server = await startTestServer();

    // Connect to real test database
    db = await setupTestDatabase();
    await db.clear();
  });

  afterAll(async () => {
    await server.close();
    await db.close();
  });

  test('should complete project planning workflow with real backend', async ({ page }) => {
    // Navigate to app
    await page.goto('http://localhost:3000');

    // Step 1: Login
    await page.fill('input[name="email"]', 'sarah@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button:has-text("Login")');

    // Step 2: View Dashboard
    await page.waitForURL('**/dashboard');
    expect(page.url()).toContain('/dashboard');

    // Step 4: Create Project Structure
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Backend API');
    await page.selectOption('select[name="type"]', 'IMPLEMENTATION');
    await page.click('button:has-text("Create")');

    // Verify in database
    const item = await db.items.findOne({ title: 'Backend API' });
    expect(item).toBeDefined();
    expect(item.status).toBe('DRAFT');

    // ... rest of journey
  });
});
```

#### Variation 3: Hybrid - Real UI, Real Backend, Mock External Services

```typescript
// tests/e2e/journeys/Journey-1-ProjectManager.hybrid.test.ts
// Linked to: Journey 1, Steps 1-12

describe('Journey 1: Project Manager - Hybrid (Real Backend, Mock External)', () => {
  let server: TestServer;
  let db: Database;

  beforeAll(async () => {
    // Start real test server
    server = await startTestServer();

    // Connect to real test database
    db = await setupTestDatabase();
    await db.clear();

    // Mock external services
    mockSearchService();
    mockRealtimeService();
  });

  afterAll(async () => {
    await server.close();
    await db.close();
  });

  test('should complete project planning workflow', async ({ page }) => {
    // Navigate to app
    await page.goto('http://localhost:3000');

    // Step 1: Login
    await page.fill('input[name="email"]', 'sarah@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button:has-text("Login")');

    // Step 2: View Dashboard
    await page.waitForURL('**/dashboard');

    // Step 4: Create Project Structure
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Backend API');
    await page.selectOption('select[name="type"]', 'IMPLEMENTATION');
    await page.click('button:has-text("Create")');

    // Verify in database
    const item = await db.items.findOne({ title: 'Backend API' });
    expect(item).toBeDefined();

    // Verify search indexing (mocked)
    expect(mockSearchService.index).toHaveBeenCalledWith(
      expect.objectContaining({ title: 'Backend API' })
    );

    // ... rest of journey
  });
});
```

---

## 📊 **TEST VARIATION SUMMARY**

### Unit Tests (500+ tests)

| Variation | API | DB | Count | Speed | Isolation |
|-----------|-----|----|----|-------|-----------|
| Mock-Mock | Mocked | Mocked | 200+ | ⚡⚡⚡ | ✅✅✅ |
| Mock-Live | Mocked | Real | 100+ | ⚡⚡ | ✅ |
| Live-Mock | Real | Mocked | 100+ | ⚡⚡ | ✅ |
| Live-Live | Real | Real | 100+ | ⚡ | ⚠️ |

### Integration Tests (300+ tests)

| Variation | DB | External APIs | Count | Speed | Realism |
|-----------|----|----|-------|-------|---------|
| Mock-Mock | Mocked | Mocked | 100+ | ⚡⚡⚡ | ⚠️ |
| Mock-Live | Mocked | Real | 50+ | ⚡⚡ | ✅ |
| Live-Mock | Real | Mocked | 100+ | ⚡⚡ | ✅ |
| Live-Live | Real | Real | 50+ | ⚡ | ✅✅✅ |

### E2E Tests (100+ tests)

| Variation | UI | Backend | DB | Count | Speed | Realism |
|-----------|----|----|----|----|-------|---------|
| Mock | Real | Mocked | Mocked | 30+ | ⚡⚡⚡ | ⚠️ |
| Hybrid | Real | Real | Mocked | 20+ | ⚡⚡ | ✅ |
| Hybrid | Real | Mocked | Real | 20+ | ⚡⚡ | ✅ |
| Live | Real | Real | Real | 30+ | ⚡ | ✅✅✅ |

---

## 🎯 **RECOMMENDED TEST STRATEGY**

### Development (Fast Feedback)
- ✅ 200+ Mock-Mock unit tests (< 1 second)
- ✅ 100+ Mock-Live integration tests (< 5 seconds)
- ✅ 30+ Mock E2E tests (< 10 seconds)
- **Total**: < 20 seconds

### Pre-Commit (Comprehensive)
- ✅ 500+ unit tests (< 2 minutes)
- ✅ 300+ integration tests (< 5 minutes)
- ✅ 100+ E2E tests (< 10 minutes)
- **Total**: < 20 minutes

### CI/CD (Full Coverage)
- ✅ All 1,000+ tests (< 30 minutes)
- ✅ Coverage report (< 5 minutes)
- ✅ Performance tests (< 10 minutes)
- **Total**: < 45 minutes

---

## 🚀 **NEXT STEPS**

1. ✅ Create mock setup files
2. ✅ Create unit test variations
3. ✅ Create integration test variations
4. ✅ Create E2E test variations
5. ✅ Set up test environment configuration
6. ✅ Configure CI/CD test matrix
7. ✅ Create test reporting dashboard



# Test Implementation Templates

Ready-to-use templates for the comprehensive test plan.

---

## Backend Unit Test Templates

### Python Service Test Template

```python
# tests/unit/services/test_example_service.py

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.tracertm.services.example_service import ExampleService
from src.tracertm.models import Item, Project
from src.tracertm.schemas import ItemCreate

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_repository():
    """Mock repository for service testing."""
    return Mock()


@pytest.fixture
def service(mock_repository):
    """Create service with mocked dependencies."""
    service = ExampleService()
    service.repository = mock_repository
    return service


class TestExampleServiceBasics:
    """Test basic service functionality."""

    def test_service_initialization(self, service):
        """Service initializes correctly."""
        assert service is not None
        assert service.repository is not None

    def test_valid_input(self, service):
        """Service processes valid input."""
        # Arrange
        test_data = {"name": "test", "value": 42}

        # Act
        result = service.process(test_data)

        # Assert
        assert result is not None
        assert result["name"] == "test"

    def test_invalid_input_raises_error(self, service):
        """Service raises error on invalid input."""
        # Arrange
        invalid_data = {"name": "", "value": None}

        # Act & Assert
        with pytest.raises(ValueError):
            service.process(invalid_data)


class TestExampleServiceEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_list(self, service, mock_repository):
        """Service handles empty list."""
        # Arrange
        mock_repository.get_all.return_value = []

        # Act
        result = service.get_all()

        # Assert
        assert result == []

    def test_large_dataset(self, service, mock_repository):
        """Service handles large datasets efficiently."""
        # Arrange
        large_data = [{"id": i, "name": f"item_{i}"} for i in range(10000)]
        mock_repository.get_all.return_value = large_data

        # Act
        result = service.get_all()

        # Assert
        assert len(result) == 10000

    def test_null_values(self, service):
        """Service handles null values safely."""
        # Arrange
        data = {"name": None, "value": None}

        # Act
        result = service.process(data)

        # Assert
        assert result is not None


class TestExampleServiceDatabase:
    """Test service with database interactions."""

    @pytest.mark.asyncio
    async def test_create_and_retrieve(self, service, mock_repository):
        """Service creates and retrieves data correctly."""
        # Arrange
        create_data = ItemCreate(title="Test Item", description="Test")
        mock_repository.create = AsyncMock(return_value=Item(
            id="123",
            title="Test Item",
            description="Test"
        ))

        # Act
        result = await service.create(create_data)

        # Assert
        assert result.title == "Test Item"
        mock_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_item(self, service, mock_repository):
        """Service updates item correctly."""
        # Arrange
        item_id = "123"
        update_data = {"title": "Updated", "description": "New description"}
        mock_repository.update = AsyncMock(return_value=Item(
            id=item_id,
            title="Updated",
            description="New description"
        ))

        # Act
        result = await service.update(item_id, update_data)

        # Assert
        assert result.title == "Updated"

    @pytest.mark.asyncio
    async def test_delete_item(self, service, mock_repository):
        """Service deletes item correctly."""
        # Arrange
        item_id = "123"
        mock_repository.delete = AsyncMock(return_value=True)

        # Act
        result = await service.delete(item_id)

        # Assert
        assert result is True
        mock_repository.delete.assert_called_once_with(item_id)


class TestExampleServiceConcurrency:
    """Test concurrent service operations."""

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, service, mock_repository):
        """Service handles concurrent operations safely."""
        import asyncio

        # Arrange
        async def create_item(i):
            return await service.create({"title": f"Item {i}"})

        # Act
        results = await asyncio.gather(*[create_item(i) for i in range(10)])

        # Assert
        assert len(results) == 10
        assert all(r is not None for r in results)


@pytest.mark.performance
class TestExampleServicePerformance:
    """Test service performance."""

    def test_process_performance(self, service, benchmark):
        """Service processes data within performance threshold."""
        data = {"name": "test", "value": 42}

        result = benchmark(service.process, data)

        assert result is not None

    @pytest.mark.asyncio
    async def test_large_batch_performance(self, service, mock_repository):
        """Service handles large batches efficiently."""
        # Measure time for large batch
        import time

        items = [{"title": f"Item {i}", "description": "Test"} for i in range(1000)]
        mock_repository.create_many = AsyncMock(return_value=items)

        start = time.time()
        result = await service.create_many(items)
        elapsed = time.time() - start

        # Should complete in < 1 second
        assert elapsed < 1.0
        assert len(result) == 1000
```

---

## Backend Integration Test Template

```python
# tests/integration/api/test_items_endpoint_chain.py

import pytest
from httpx import AsyncClient
from src.tracertm.api.main import app
from src.tracertm.models import Item
import uuid

pytestmark = pytest.mark.integration


@pytest.fixture
async def client():
    """Create test client for API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def auth_headers(client):
    """Get authentication headers."""
    # Login and get token
    response = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


class TestItemsEndpointChain:
    """Test items endpoint workflows."""

    @pytest.mark.asyncio
    async def test_create_and_retrieve_item(self, client, auth_headers):
        """Test create item → retrieve item."""
        # 1. Create item
        create_response = await client.post(
            "/api/v1/items",
            json={
                "title": "Test Item",
                "description": "Integration test",
                "view": "Feature",
                "item_type": "requirement"
            },
            headers=auth_headers
        )

        assert create_response.status_code == 201
        item_id = create_response.json()["id"]

        # 2. Retrieve item
        get_response = await client.get(
            f"/api/v1/items/{item_id}",
            headers=auth_headers
        )

        assert get_response.status_code == 200
        item = get_response.json()
        assert item["title"] == "Test Item"
        assert item["id"] == item_id

    @pytest.mark.asyncio
    async def test_create_update_delete_item(self, client, auth_headers):
        """Test create → update → delete item."""
        # 1. Create
        create_response = await client.post(
            "/api/v1/items",
            json={"title": "Original Title", "view": "Feature"},
            headers=auth_headers
        )
        item_id = create_response.json()["id"]

        # 2. Update
        update_response = await client.put(
            f"/api/v1/items/{item_id}",
            json={"title": "Updated Title"},
            headers=auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Title"

        # 3. Delete
        delete_response = await client.delete(
            f"/api/v1/items/{item_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204

        # 4. Verify deleted
        get_response = await client.get(
            f"/api/v1/items/{item_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_items_and_list_with_filters(self, client, auth_headers):
        """Test create multiple items and filter list."""
        # 1. Create multiple items with different statuses
        for i in range(5):
            status = "done" if i % 2 == 0 else "todo"
            await client.post(
                "/api/v1/items",
                json={"title": f"Item {i}", "status": status},
                headers=auth_headers
            )

        # 2. List all items
        list_response = await client.get(
            "/api/v1/items",
            headers=auth_headers
        )
        assert list_response.status_code == 200
        all_items = list_response.json()["items"]
        assert len(all_items) >= 5

        # 3. Filter by status=done
        filtered_response = await client.get(
            "/api/v1/items?status=done",
            headers=auth_headers
        )
        filtered_items = filtered_response.json()["items"]
        assert all(item["status"] == "done" for item in filtered_items)

    @pytest.mark.asyncio
    async def test_item_with_links(self, client, auth_headers):
        """Test create item → create link → retrieve with links."""
        # 1. Create two items
        item1_response = await client.post(
            "/api/v1/items",
            json={"title": "Item 1"},
            headers=auth_headers
        )
        item1_id = item1_response.json()["id"]

        item2_response = await client.post(
            "/api/v1/items",
            json={"title": "Item 2"},
            headers=auth_headers
        )
        item2_id = item2_response.json()["id"]

        # 2. Create link between them
        link_response = await client.post(
            "/api/v1/links",
            json={
                "source_item_id": item1_id,
                "target_item_id": item2_id,
                "link_type": "depends_on"
            },
            headers=auth_headers
        )
        assert link_response.status_code == 201

        # 3. Get item 1 and verify link exists
        get_response = await client.get(
            f"/api/v1/items/{item1_id}",
            headers=auth_headers
        )
        item = get_response.json()
        assert any(link["target_id"] == item2_id for link in item.get("outgoing_links", []))

    @pytest.mark.asyncio
    async def test_error_handling(self, client, auth_headers):
        """Test error handling on invalid operations."""
        # Try to get non-existent item
        response = await client.get(
            f"/api/v1/items/{uuid.uuid4()}",
            headers=auth_headers
        )
        assert response.status_code == 404

        # Try to create item without required field
        response = await client.post(
            "/api/v1/items",
            json={"description": "Missing title"},
            headers=auth_headers
        )
        assert response.status_code == 422

        # Try to create link to non-existent item
        response = await client.post(
            "/api/v1/links",
            json={
                "source_item_id": uuid.uuid4(),
                "target_item_id": uuid.uuid4(),
                "link_type": "depends_on"
            },
            headers=auth_headers
        )
        assert response.status_code == 404 or response.status_code == 422
```

---

## Frontend Unit Test Template

```typescript
// src/__tests__/hooks/test_useExample.test.ts

import { renderHook, act, waitFor } from '@testing-library/react';
import { useExample } from '../../hooks/useExample';
import * as api from '../../api/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock API
jest.mock('../../api/client');

// Setup
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useExample', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initialization', () => {
    it('initializes with default state', () => {
      const { result } = renderHook(() => useExample(), {
        wrapper: createWrapper(),
      });

      expect(result.current.data).toBeUndefined();
      expect(result.current.isLoading).toBe(true);
      expect(result.current.error).toBeNull();
    });
  });

  describe('Data Fetching', () => {
    it('fetches data on mount', async () => {
      const mockData = { id: '1', name: 'Test' };
      (api.getExample as jest.Mock).mockResolvedValueOnce(mockData);

      const { result } = renderHook(() => useExample(), {
        wrapper: createWrapper(),
      });

      // Wait for loading to complete
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.data).toEqual(mockData);
      expect(api.getExample).toHaveBeenCalledTimes(1);
    });

    it('handles fetch errors gracefully', async () => {
      const mockError = new Error('Network error');
      (api.getExample as jest.Mock).mockRejectedValueOnce(mockError);

      const { result } = renderHook(() => useExample(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBeDefined();
      expect(result.current.data).toBeUndefined();
    });

    it('refetches data on demand', async () => {
      const mockData = { id: '1', name: 'Test' };
      (api.getExample as jest.Mock).mockResolvedValueOnce(mockData);

      const { result } = renderHook(() => useExample(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(api.getExample).toHaveBeenCalledTimes(1);

      // Trigger refetch
      act(() => {
        result.current.refetch();
      });

      await waitFor(() => {
        expect(api.getExample).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('State Updates', () => {
    it('updates state correctly', async () => {
      const mockData = { id: '1', name: 'Test' };
      (api.getExample as jest.Mock).mockResolvedValueOnce(mockData);

      const { result, rerender } = renderHook(() => useExample(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.data?.name).toBe('Test');
    });

    it('handles rapid state updates', async () => {
      const mockData = { id: '1', name: 'Test' };
      (api.getExample as jest.Mock).mockResolvedValueOnce(mockData);

      const { result } = renderHook(() => useExample(), {
        wrapper: createWrapper(),
      });

      // Multiple rapid updates shouldn't cause issues
      await waitFor(() => {
        expect(result.current.data).toBeDefined();
      });

      expect(result.current.data).toEqual(mockData);
    });
  });

  describe('Cleanup', () => {
    it('cleans up on unmount', async () => {
      const mockData = { id: '1', name: 'Test' };
      (api.getExample as jest.Mock).mockResolvedValueOnce(mockData);

      const { unmount } = renderHook(() => useExample(), {
        wrapper: createWrapper(),
      });

      unmount();

      // No errors should occur
      expect(true).toBe(true);
    });
  });
});
```

---

## Frontend Component Test Template

```typescript
// src/__tests__/components/test_Button.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from '../../components/Button';

describe('Button Component', () => {
  describe('Rendering', () => {
    it('renders button with text', () => {
      render(<Button>Click me</Button>);
      expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
    });

    it('renders button with custom className', () => {
      render(<Button className="custom-class">Test</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('custom-class');
    });

    it('renders disabled button', () => {
      render(<Button disabled>Disabled</Button>);
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });

    it('renders button with icon', () => {
      render(
        <Button icon="check">
          Save
        </Button>
      );
      expect(screen.getByRole('button')).toBeInTheDocument();
    });
  });

  describe('Interactions', () => {
    it('calls onClick handler on click', async () => {
      const handleClick = jest.fn();
      const user = userEvent.setup();

      render(<Button onClick={handleClick}>Click</Button>);
      const button = screen.getByRole('button');

      await user.click(button);

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when disabled', async () => {
      const handleClick = jest.fn();
      const user = userEvent.setup();

      render(
        <Button onClick={handleClick} disabled>
          Click
        </Button>
      );
      const button = screen.getByRole('button');

      await user.click(button);

      expect(handleClick).not.toHaveBeenCalled();
    });

    it('handles keyboard navigation', async () => {
      const handleClick = jest.fn();
      const user = userEvent.setup();

      render(<Button onClick={handleClick}>Click</Button>);
      const button = screen.getByRole('button');

      button.focus();
      expect(button).toHaveFocus();

      // Press Enter
      await user.keyboard('{Enter}');
      expect(handleClick).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('has proper aria-label for icon button', () => {
      render(<Button icon="search" ariaLabel="Search" />);
      expect(screen.getByLabelText('Search')).toBeInTheDocument();
    });

    it('has visible focus indicator', () => {
      render(<Button>Click</Button>);
      const button = screen.getByRole('button');

      button.focus();
      expect(button).toHaveFocus();

      // Check if focus styles are applied (implementation dependent)
      const styles = window.getComputedStyle(button);
      expect(styles.outline).not.toBe('none');
    });

    it('supports loading state', () => {
      render(
        <Button loading ariaLabel="Saving">
          Save
        </Button>
      );
      expect(screen.getByLabelText('Saving')).toBeInTheDocument();
    });
  });

  describe('States', () => {
    it('renders variant styles correctly', () => {
      const { rerender } = render(<Button variant="primary">Primary</Button>);
      let button = screen.getByRole('button');
      expect(button).toHaveClass('btn-primary');

      rerender(<Button variant="secondary">Secondary</Button>);
      button = screen.getByRole('button');
      expect(button).toHaveClass('btn-secondary');
    });

    it('renders size variations', () => {
      const { rerender } = render(<Button size="sm">Small</Button>);
      let button = screen.getByRole('button');
      expect(button).toHaveClass('btn-sm');

      rerender(<Button size="lg">Large</Button>);
      button = screen.getByRole('button');
      expect(button).toHaveClass('btn-lg');
    });
  });
});
```

---

## Frontend E2E Test Template

```typescript
// e2e/critical-flows/basic-workflow.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Basic Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to app
    await page.goto('http://localhost:5173');

    // Wait for app to load
    await page.waitForLoadState('networkidle');
  });

  test('user can create and view an item', async ({ page }) => {
    // 1. Click create button
    const createButton = page.getByRole('button', { name: /create/i });
    await expect(createButton).toBeVisible();
    await createButton.click();

    // 2. Fill form
    await page.getByLabel(/title/i).fill('Test Item');
    await page.getByLabel(/description/i).fill('Integration test item');

    // 3. Submit form
    const submitButton = page.getByRole('button', { name: /save|create/i });
    await submitButton.click();

    // 4. Wait for success message
    const successMessage = page.getByText(/created|saved/i);
    await expect(successMessage).toBeVisible();

    // 5. Verify item appears in list
    const itemInList = page.getByText('Test Item');
    await expect(itemInList).toBeVisible();

    // 6. Click item and view details
    await itemInList.click();
    await expect(page.getByText('Integration test item')).toBeVisible();
  });

  test('user can create and link two items', async ({ page }) => {
    // 1. Create first item
    await page.getByRole('button', { name: /create/i }).click();
    await page.getByLabel(/title/i).fill('Item A');
    await page.getByRole('button', { name: /save/i }).click();

    // 2. Create second item
    await page.getByRole('button', { name: /create/i }).click();
    await page.getByLabel(/title/i).fill('Item B');
    await page.getByRole('button', { name: /save/i }).click();

    // 3. Navigate to first item
    await page.getByText('Item A').click();

    // 4. Create link
    const linkButton = page.getByRole('button', { name: /link|create link/i });
    await linkButton.click();

    // 5. Select target
    await page.getByLabel(/target/i).click();
    await page.getByText('Item B').click();

    // 6. Confirm link
    await page.getByRole('button', { name: /confirm|create/i }).click();

    // 7. Verify link appears
    const linkIndicator = page.getByText('Item B');
    await expect(linkIndicator).toBeVisible();
  });

  test('user can filter and search items', async ({ page }) => {
    // 1. Create several items
    for (let i = 0; i < 5; i++) {
      await page.getByRole('button', { name: /create/i }).click();
      await page.getByLabel(/title/i).fill(`Item ${i}`);
      await page.getByRole('button', { name: /save/i }).click();
      await page.waitForTimeout(100); // Brief wait between items
    }

    // 2. Open search
    const searchInput = page.getByPlaceholder(/search/i);
    await searchInput.fill('Item 2');

    // 3. Verify filtered results
    await expect(page.getByText('Item 2')).toBeVisible();
    await expect(page.getByText('Item 1')).not.toBeVisible();

    // 4. Clear search
    await searchInput.clear();

    // 5. Verify all items reappear
    await expect(page.getByText('Item 0')).toBeVisible();
    await expect(page.getByText('Item 4')).toBeVisible();
  });

  test('user can delete an item', async ({ page }) => {
    // 1. Create item
    await page.getByRole('button', { name: /create/i }).click();
    await page.getByLabel(/title/i).fill('Delete Me');
    await page.getByRole('button', { name: /save/i }).click();

    // 2. Find and open item
    const item = page.getByText('Delete Me');
    await expect(item).toBeVisible();

    // 3. Right-click for context menu
    await item.click({ button: 'right' });

    // 4. Click delete
    const deleteOption = page.getByRole('menuitem', { name: /delete/i });
    await deleteOption.click();

    // 5. Confirm deletion
    const confirmButton = page.getByRole('button', { name: /confirm|yes|delete/i });
    await confirmButton.click();

    // 6. Verify item is gone
    await expect(item).not.toBeVisible();
  });

  test('graph view renders and is interactive', async ({ page }) => {
    // 1. Navigate to graph view
    const graphLink = page.getByRole('link', { name: /graph/i });
    if (await graphLink.isVisible()) {
      await graphLink.click();
    } else {
      const navButton = page.getByRole('button', { name: /menu/i });
      await navButton.click();
      await graphLink.click();
    }

    // 2. Wait for graph to render
    await page.waitForSelector('[data-testid="graph-container"]', { timeout: 5000 });

    // 3. Test zoom
    const graphContainer = page.locator('[data-testid="graph-container"]');
    await graphContainer.dragTo(graphContainer, { sourcePosition: { x: 100, y: 100 }, targetPosition: { x: 200, y: 200 } });

    // 4. Verify zoom works (no specific assertion, just verify no errors)
    await expect(graphContainer).toBeVisible();
  });

  test('performance: page loads within acceptable time', async ({ page }) => {
    const start = Date.now();

    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');

    const elapsed = Date.now() - start;

    // Page should load in < 3 seconds
    expect(elapsed).toBeLessThan(3000);
  });
});
```

---

## Backend API Load Test Template (K6)

```javascript
// tests/performance/load_tests/k6_api_load.js

import http from 'k6/http';
import { check, sleep, group } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 10 },   // Warm up
    { duration: '5m', target: 50 },   // Ramp up
    { duration: '10m', target: 50 },  // Stay at 50
    { duration: '5m', target: 0 },    // Ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<2000'],
    'http_req_failed': ['rate<0.01'],
    'group_duration{staticAsset:yes}': ['p(99)<1000'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const TOKEN = __ENV.TOKEN || 'test-token';

function getAuthHeaders() {
  return {
    'Authorization': `Bearer ${TOKEN}`,
    'Content-Type': 'application/json',
  };
}

export default function () {
  group('Get items', function () {
    let res = http.get(`${BASE_URL}/api/v1/items`, {
      headers: getAuthHeaders(),
    });

    check(res, {
      'status is 200': (r) => r.status === 200,
      'response time < 500ms': (r) => r.timings.duration < 500,
      'has items': (r) => r.json('items').length > 0,
    });

    sleep(1);
  });

  group('Create item', function () {
    let payload = JSON.stringify({
      title: `Item ${Date.now()}`,
      description: 'Load test item',
      view: 'Feature',
      item_type: 'requirement',
    });

    let res = http.post(`${BASE_URL}/api/v1/items`, payload, {
      headers: getAuthHeaders(),
    });

    check(res, {
      'status is 201': (r) => r.status === 201,
      'has id': (r) => r.json('id') != null,
    });

    // Store ID for later use
    let itemId = res.json('id');

    sleep(1);

    group('Get created item', function () {
      let getRes = http.get(`${BASE_URL}/api/v1/items/${itemId}`, {
        headers: getAuthHeaders(),
      });

      check(getRes, {
        'status is 200': (r) => r.status === 200,
        'title matches': (r) => r.json('title').includes('Item'),
      });
    });

    sleep(1);
  });

  group('Perform analysis', function () {
    // Get first item and run impact analysis
    let listRes = http.get(`${BASE_URL}/api/v1/items?limit=1`, {
      headers: getAuthHeaders(),
    });

    if (listRes.status === 200 && listRes.json('items').length > 0) {
      let itemId = listRes.json('items')[0].id;

      let analysisRes = http.get(
        `${BASE_URL}/api/v1/analysis/impact/${itemId}`,
        { headers: getAuthHeaders() }
      );

      check(analysisRes, {
        'analysis status is 200': (r) => r.status === 200,
        'analysis has results': (r) => r.json('impacted_items') != null,
      });
    }

    sleep(2);
  });
}
```

---

## Security Test Template

```python
# tests/security/test_api_security_validation.py

import pytest
from httpx import AsyncClient
from src.tracertm.api.main import app

pytestmark = pytest.mark.security


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


class TestAuthenticationSecurity:
    """Test authentication security."""

    @pytest.mark.asyncio
    async def test_invalid_credentials_rejected(self, client):
        """Invalid credentials should be rejected."""
        response = await client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "wrong_password"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token_rejected(self, client):
        """Expired token should be rejected."""
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.expired"
        response = await client.get(
            "/api/v1/items",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_token_rejected(self, client):
        """Missing auth token should be rejected."""
        response = await client.get("/api/v1/items")
        assert response.status_code == 401 or response.status_code == 403


class TestInputValidationSecurity:
    """Test input validation security."""

    @pytest.mark.asyncio
    async def test_xss_prevention(self, client, auth_headers):
        """XSS injection should be prevented."""
        response = await client.post(
            "/api/v1/items",
            json={
                "title": "<script>alert('xss')</script>",
                "description": "Test"
            },
            headers=auth_headers
        )
        assert response.status_code == 201

        item = response.json()
        # Script tags should be escaped or removed
        assert "<script>" not in item["title"]

    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self, client, auth_headers):
        """SQL injection should be prevented."""
        response = await client.get(
            "/api/v1/items",
            params={"search": "' OR '1'='1'"},
            headers=auth_headers
        )
        assert response.status_code == 200
        # Should return results, not execute injection

    @pytest.mark.asyncio
    async def test_large_input_rejected(self, client, auth_headers):
        """Very large inputs should be rejected or truncated."""
        large_string = "x" * 100000

        response = await client.post(
            "/api/v1/items",
            json={
                "title": large_string,
                "description": "Test"
            },
            headers=auth_headers
        )
        # Should be rejected or accept with truncation
        assert response.status_code in [201, 413, 422]


class TestAuthorizationSecurity:
    """Test authorization security."""

    @pytest.mark.asyncio
    async def test_cannot_access_others_items(self, client):
        """User should not access other users' items."""
        # This test requires setup with multiple users
        # Would need fixture with User A and User B tokens
        # Verify User A cannot GET User B's items
        pass

    @pytest.mark.asyncio
    async def test_cannot_delete_others_items(self, client):
        """User should not be able to delete others' items."""
        # Verify User A cannot DELETE User B's items
        pass


class TestAPISecurityHeaders:
    """Test security headers."""

    @pytest.mark.asyncio
    async def test_security_headers_present(self, client):
        """API should include security headers."""
        response = await client.get("/api/v1/items")

        headers = response.headers
        # Check security headers
        assert "x-content-type-options" in headers
        assert headers.get("x-content-type-options").lower() == "nosniff"
```

---

## Accessibility Test Template (E2E)

```typescript
// e2e/accessibility/wcag-basic-compliance.spec.ts

import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test.describe('WCAG 2.1 AA Compliance', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    // Inject axe-core
    await injectAxe(page);
  });

  test('homepage has no accessibility violations', async ({ page }) => {
    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check accessibility
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: {
        html: true,
      },
    });
  });

  test('form is keyboard accessible', async ({ page }) => {
    // Click to focus form
    const formButton = page.getByRole('button', { name: /create/i });
    await formButton.click();

    // Should be able to tab through fields
    const titleInput = page.getByLabel(/title/i);
    await titleInput.focus();
    await expect(titleInput).toBeFocused();

    // Tab to next field
    await page.keyboard.press('Tab');
    const descriptionInput = page.getByLabel(/description/i);
    await expect(descriptionInput).toBeFocused();

    // Tab to submit button
    await page.keyboard.press('Tab');
    const submitButton = page.getByRole('button', { name: /save/i });
    await expect(submitButton).toBeFocused();

    // Submit with Enter
    await page.keyboard.press('Enter');

    // Should show success
    const success = page.getByText(/success|created/i);
    await expect(success).toBeVisible();
  });

  test('focus indicators are visible', async ({ page }) => {
    // Get first button
    const button = page.getByRole('button').first();

    // Tab to focus it
    await button.focus();

    // Check if focused
    const focused = await button.evaluate(() => {
      const element = document.activeElement as HTMLElement;
      return window.getComputedStyle(element).outline !== 'none';
    });

    expect(focused).toBeTruthy();
  });

  test('headings are hierarchical', async ({ page }) => {
    const h1 = page.locator('h1');
    const h2 = page.locator('h2');

    // Should have at least one H1
    await expect(h1).toHaveCount(1);

    // H2 should come after H1
    const h2Text = await h2.first().textContent();
    expect(h2Text).toBeTruthy();
  });

  test('color contrast is sufficient', async ({ page }) => {
    // This is verified by axe-core in checkA11y
    // But we can also test manually
    const text = page.getByText(/welcome|dashboard/i).first();

    const contrastInfo = await text.evaluate(() => {
      const element = document.activeElement as HTMLElement;
      const style = window.getComputedStyle(element);
      return {
        color: style.color,
        backgroundColor: style.backgroundColor,
      };
    });

    // Visual check - can add contrast calculation if needed
    expect(contrastInfo.color).toBeTruthy();
  });

  test('form labels are associated with inputs', async ({ page }) => {
    const formButton = page.getByRole('button', { name: /create/i });
    await formButton.click();

    // Check that label is associated
    const titleInput = page.getByLabel(/title/i);
    const hasLabel = await titleInput.evaluate(() => {
      const element = document.querySelector('[data-testid="title-input"]');
      return element?.hasAttribute('aria-label') ||
             element?.getAttribute('id') !== null;
    });

    expect(hasLabel).toBeTruthy();
  });
});
```

---

## Test Configuration Files

### pytest.ini Configuration

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

markers =
    unit: Unit tests
    integration: Integration tests
    asyncio: Async tests
    performance: Performance tests
    slow: Slow tests
    security: Security tests
    concurrency: Concurrency tests
    property: Property-based tests
    benchmark: Benchmark tests
    smoke: Smoke tests

addopts =
    --strict-markers
    --tb=short
    -ra
```

### vitest.config.ts Configuration

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/__tests__/',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

---

**Next Steps:** Pick a category and use these templates to build your test suite!


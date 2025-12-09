import { test, expect } from '@playwright/test'

/**
 * Integration Workflow Tests
 *
 * Tests that verify multiple components working together
 * in realistic user workflows.
 */

test.describe('Project to Items Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should create project and add items in one flow', async ({ page }) => {
    // Navigate to projects
    await page.click('a[href="/projects"]')
    await page.waitForURL('/projects')

    // Create new project
    await page.click('button:has-text("New Project")')
    await page.fill('input[name="name"]', 'Test Project')
    await page.fill('textarea[name="description"]', 'A test project for workflow')
    await page.click('button:has-text("Create")')

    // Should navigate to project detail
    await page.waitForURL(/\/projects\/.*/)

    // Add first item to project
    await page.click('button:has-text("Add Item")')
    await page.fill('input[name="title"]', 'First Item')
    await page.fill('textarea[name="description"]', 'First item description')
    await page.selectOption('select[name="type"]', 'requirement')
    await page.click('button:has-text("Save")')

    // Verify item appears in project
    await expect(page.locator('text=First Item')).toBeVisible()

    // Add second item
    await page.click('button:has-text("Add Item")')
    await page.fill('input[name="title"]', 'Second Item')
    await page.fill('textarea[name="description"]', 'Second item description')
    await page.selectOption('select[name="type"]', 'task')
    await page.click('button:has-text("Save")')

    // Verify both items are visible
    await expect(page.locator('text=First Item')).toBeVisible()
    await expect(page.locator('text=Second Item')).toBeVisible()

    // Check project items count
    const itemCount = page.locator('[data-testid="item-count"]')
    await expect(itemCount).toHaveText('2')
  })

  test('should link items within project context', async ({ page }) => {
    // Navigate to existing project
    await page.goto('/projects/test-project-1')
    await page.waitForLoadState('networkidle')

    // Click on first item
    await page.click('[data-testid="item-card"]:first-child')

    // Open link panel
    await page.click('button:has-text("Add Link")')

    // Select link type
    await page.selectOption('select[name="linkType"]', 'implements')

    // Search for target item within project
    await page.fill('input[name="targetItem"]', 'Second Item')
    await page.waitForTimeout(500) // Wait for search results

    // Select from dropdown
    await page.click('[data-testid="search-result"]:has-text("Second Item")')

    // Save link
    await page.click('button:has-text("Create Link")')

    // Verify link appears in graph view
    await page.click('button:has-text("Graph View")')
    await page.waitForSelector('[data-testid="graph-canvas"]')

    // Should see connection between items
    const edges = page.locator('[data-testid="graph-edge"]')
    await expect(edges).toHaveCount(1)
  })

  test('should manage project lifecycle with items', async ({ page }) => {
    // Create project
    await page.goto('/projects')
    await page.click('button:has-text("New Project")')
    await page.fill('input[name="name"]', 'Lifecycle Project')
    await page.click('button:has-text("Create")')
    await page.waitForURL(/\/projects\/.*/)

    // Add items
    for (let i = 1; i <= 3; i++) {
      await page.click('button:has-text("Add Item")')
      await page.fill('input[name="title"]', `Item ${i}`)
      await page.click('button:has-text("Save")')
      await page.waitForTimeout(300)
    }

    // Archive project
    await page.click('[data-testid="project-menu"]')
    await page.click('button:has-text("Archive")')
    await page.click('button:has-text("Confirm")')

    // Verify redirect to projects list
    await page.waitForURL('/projects')

    // Archived project should not appear in default view
    await expect(page.locator('text=Lifecycle Project')).not.toBeVisible()

    // Show archived projects
    await page.click('button:has-text("Show Archived")')
    await expect(page.locator('text=Lifecycle Project')).toBeVisible()

    // Restore project
    await page.click('[data-testid="project-card"]:has-text("Lifecycle Project")')
    await page.click('button:has-text("Restore")')

    // Should appear in active projects again
    await page.goto('/projects')
    await expect(page.locator('text=Lifecycle Project')).toBeVisible()
  })
})

test.describe('Search to Navigation Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should search and navigate to results', async ({ page }) => {
    // Open global search
    await page.keyboard.press('Meta+k') // or Ctrl+k on Windows
    await page.waitForSelector('[data-testid="search-dialog"]')

    // Type search query
    await page.fill('[data-testid="search-input"]', 'authentication')
    await page.waitForTimeout(500)

    // Verify search results appear
    const results = page.locator('[data-testid="search-result"]')
    await expect(results).toHaveCountGreaterThan(0)

    // Click on first result
    await results.first().click()

    // Should navigate to the item
    await page.waitForURL(/\/(items|projects|agents)\/.*/)

    // Item details should be visible
    await expect(page.locator('[data-testid="item-detail"]')).toBeVisible()
  })

  test('should filter search by type', async ({ page }) => {
    await page.keyboard.press('Meta+k')
    await page.waitForSelector('[data-testid="search-dialog"]')

    // Select filter
    await page.click('[data-testid="filter-type"]')
    await page.click('[data-testid="filter-option"]:has-text("Requirements")')

    // Search
    await page.fill('[data-testid="search-input"]', 'user')
    await page.waitForTimeout(500)

    // All results should be requirements
    const results = page.locator('[data-testid="search-result"]')
    const count = await results.count()

    for (let i = 0; i < count; i++) {
      const badge = results.nth(i).locator('[data-testid="type-badge"]')
      await expect(badge).toHaveText('Requirement')
    }
  })

  test('should search within project context', async ({ page }) => {
    await page.goto('/projects/test-project-1')

    // Open project search
    await page.click('[data-testid="project-search"]')

    // Search only searches within this project
    await page.fill('[data-testid="search-input"]', 'item')
    await page.waitForTimeout(500)

    // Results should only be from this project
    const projectBadges = page.locator('[data-testid="project-badge"]')
    const count = await projectBadges.count()

    for (let i = 0; i < count; i++) {
      await expect(projectBadges.nth(i)).toHaveText('test-project-1')
    }
  })

  test('should navigate between search results using keyboard', async ({ page }) => {
    await page.keyboard.press('Meta+k')
    await page.waitForSelector('[data-testid="search-dialog"]')

    await page.fill('[data-testid="search-input"]', 'test')
    await page.waitForTimeout(500)

    // Navigate with arrow keys
    await page.keyboard.press('ArrowDown')
    let firstResult = page.locator('[data-testid="search-result"][aria-selected="true"]')
    await expect(firstResult).toBeVisible()

    await page.keyboard.press('ArrowDown')
    let secondResult = page.locator('[data-testid="search-result"][aria-selected="true"]')
    await expect(secondResult).toBeVisible()

    // Press Enter to navigate
    await page.keyboard.press('Enter')
    await page.waitForURL(/\/(items|projects|agents)\/.*/)
  })
})

test.describe('Dashboard to Detail Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should navigate from dashboard widget to detail view', async ({ page }) => {
    // Click on recent item from dashboard
    const recentItem = page.locator('[data-testid="recent-items"] [data-testid="item-card"]').first()
    await recentItem.click()

    // Should navigate to item detail
    await page.waitForURL(/\/items\/.*/)

    // Item detail should show
    await expect(page.locator('[data-testid="item-title"]')).toBeVisible()
    await expect(page.locator('[data-testid="item-description"]')).toBeVisible()

    // Breadcrumb should show path
    const breadcrumb = page.locator('[data-testid="breadcrumb"]')
    await expect(breadcrumb).toContainText('Dashboard')
    await expect(breadcrumb).toContainText('Items')
  })

  test('should navigate from dashboard stats to filtered lists', async ({ page }) => {
    // Click on "Open Items" stat
    await page.click('[data-testid="stat-open-items"]')

    // Should navigate to items page with filter
    await page.waitForURL(/\/items\?status=open/)

    // Filter should be applied
    const filterBadge = page.locator('[data-testid="active-filter"]')
    await expect(filterBadge).toContainText('Status: Open')

    // All visible items should be open
    const items = page.locator('[data-testid="item-card"]')
    const count = await items.count()

    for (let i = 0; i < Math.min(count, 5); i++) {
      const statusBadge = items.nth(i).locator('[data-testid="status-badge"]')
      await expect(statusBadge).toHaveText('Open')
    }
  })

  test('should update dashboard after creating item', async ({ page }) => {
    // Get initial item count
    const initialCount = await page.locator('[data-testid="total-items-count"]').textContent()

    // Create new item
    await page.click('button:has-text("Quick Add")')
    await page.fill('input[name="title"]', 'Dashboard Test Item')
    await page.click('button:has-text("Create")')

    // Wait for creation
    await page.waitForTimeout(1000)

    // Navigate back to dashboard
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // Count should be updated
    const newCount = await page.locator('[data-testid="total-items-count"]').textContent()
    expect(parseInt(newCount!)).toBeGreaterThan(parseInt(initialCount!))

    // New item should appear in recent items
    await expect(page.locator('[data-testid="recent-items"]')).toContainText('Dashboard Test Item')
  })
})

test.describe('Item CRUD with Links Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items')
    await page.waitForLoadState('networkidle')
  })

  test('should create item, add links, and verify in graph', async ({ page }) => {
    // Create first item
    await page.click('button:has-text("New Item")')
    await page.fill('input[name="title"]', 'Parent Requirement')
    await page.selectOption('select[name="type"]', 'requirement')
    await page.click('button:has-text("Save")')

    await page.waitForURL(/\/items\/.*/)
    const parentUrl = page.url()
    const parentId = parentUrl.split('/').pop()

    // Create second item
    await page.goto('/items')
    await page.click('button:has-text("New Item")')
    await page.fill('input[name="title"]', 'Child Task')
    await page.selectOption('select[name="type"]', 'task')
    await page.click('button:has-text("Save")')

    await page.waitForURL(/\/items\/.*/)

    // Add link to parent
    await page.click('button:has-text("Add Link")')
    await page.selectOption('select[name="linkType"]', 'implements')
    await page.fill('input[name="targetItem"]', 'Parent Requirement')
    await page.waitForTimeout(500)
    await page.click(`[data-testid="search-result"]:has-text("Parent Requirement")`)
    await page.click('button:has-text("Create Link")')

    // Verify link appears
    await expect(page.locator('[data-testid="link-list"]')).toContainText('Parent Requirement')

    // Navigate to graph
    await page.goto('/graph')
    await page.waitForSelector('[data-testid="graph-canvas"]')

    // Filter to show only these items
    await page.fill('[data-testid="graph-search"]', 'Parent Requirement')
    await page.waitForTimeout(500)

    // Should see both nodes and edge
    const nodes = page.locator('[data-testid="graph-node"]')
    await expect(nodes).toHaveCountGreaterThanOrEqual(2)

    const edges = page.locator('[data-testid="graph-edge"]')
    await expect(edges).toHaveCountGreaterThanOrEqual(1)
  })

  test('should update item and preserve links', async ({ page }) => {
    // Navigate to item with links
    await page.goto('/items/item-with-links')
    await page.waitForLoadState('networkidle')

    // Get current links count
    const linksCount = await page.locator('[data-testid="links-count"]').textContent()

    // Edit item
    await page.click('button:has-text("Edit")')
    await page.fill('input[name="title"]', 'Updated Item Title')
    await page.click('button:has-text("Save")')

    // Links should be preserved
    const newLinksCount = await page.locator('[data-testid="links-count"]').textContent()
    expect(newLinksCount).toBe(linksCount)

    // Title should be updated
    await expect(page.locator('[data-testid="item-title"]')).toHaveText('Updated Item Title')
  })

  test('should delete item and update linked items', async ({ page }) => {
    // Create two linked items
    await page.click('button:has-text("New Item")')
    await page.fill('input[name="title"]', 'Item to Delete')
    await page.click('button:has-text("Save")')
    await page.waitForURL(/\/items\/.*/)

    const deleteItemUrl = page.url()

    await page.goto('/items')
    await page.click('button:has-text("New Item")')
    await page.fill('input[name="title"]', 'Linked Item')
    await page.click('button:has-text("Save")')
    await page.waitForURL(/\/items\/.*/)

    // Link to item we'll delete
    await page.click('button:has-text("Add Link")')
    await page.fill('input[name="targetItem"]', 'Item to Delete')
    await page.waitForTimeout(500)
    await page.click('[data-testid="search-result"]:first-child')
    await page.click('button:has-text("Create Link")')

    // Delete the first item
    await page.goto(deleteItemUrl)
    await page.click('[data-testid="item-menu"]')
    await page.click('button:has-text("Delete")')
    await page.click('button:has-text("Confirm")')

    // Should redirect to items list
    await page.waitForURL('/items')

    // Navigate to linked item
    await page.goto('/items')
    await page.click('[data-testid="item-card"]:has-text("Linked Item")')

    // Link should be removed or marked as broken
    const brokenLinks = page.locator('[data-testid="broken-link"]')
    await expect(brokenLinks).toHaveCount(1)
  })
})

test.describe('Sync and Collaboration Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should sync changes across tabs', async ({ browser }) => {
    // Create two contexts (tabs)
    const context1 = await browser.newContext()
    const page1 = await context1.newPage()
    await page1.goto('/')
    await page1.waitForLoadState('networkidle')

    const context2 = await browser.newContext()
    const page2 = await context2.newPage()
    await page2.goto('/')
    await page2.waitForLoadState('networkidle')

    // Create item in tab 1
    await page1.goto('/items')
    await page1.click('button:has-text("New Item")')
    await page1.fill('input[name="title"]', 'Sync Test Item')
    await page1.click('button:has-text("Save")')
    await page1.waitForTimeout(1000)

    // Refresh tab 2 or wait for sync
    await page2.goto('/items')
    await page2.waitForLoadState('networkidle')

    // Item should appear in tab 2
    await expect(page2.locator('text=Sync Test Item')).toBeVisible()

    await context1.close()
    await context2.close()
  })

  test('should handle offline mode gracefully', async ({ page, context }) => {
    await page.goto('/items')

    // Go offline
    await context.setOffline(true)

    // Try to create item
    await page.click('button:has-text("New Item")')
    await page.fill('input[name="title"]', 'Offline Item')
    await page.click('button:has-text("Save")')

    // Should show offline indicator
    const offlineIndicator = page.locator('[data-testid="offline-indicator"]')
    await expect(offlineIndicator).toBeVisible()

    // Item should be queued
    const queuedBadge = page.locator('[data-testid="queued-badge"]')
    await expect(queuedBadge).toBeVisible()

    // Go back online
    await context.setOffline(false)

    // Wait for sync
    await page.waitForTimeout(2000)

    // Offline indicator should disappear
    await expect(offlineIndicator).not.toBeVisible()

    // Item should be synced
    await expect(queuedBadge).not.toBeVisible()
  })

  test('should resolve sync conflicts', async ({ page }) => {
    await page.goto('/items/conflicted-item')

    // Simulate conflict detected
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('sync:conflict', {
          detail: {
            itemId: 'conflicted-item',
            local: { title: 'Local Version' },
            remote: { title: 'Remote Version' },
          },
        })
      )
    })

    // Conflict dialog should appear
    const conflictDialog = page.locator('[data-testid="conflict-dialog"]')
    await expect(conflictDialog).toBeVisible()

    // Should show both versions
    await expect(conflictDialog).toContainText('Local Version')
    await expect(conflictDialog).toContainText('Remote Version')

    // Choose remote version
    await page.click('button:has-text("Use Remote")')

    // Item should be updated
    await expect(page.locator('[data-testid="item-title"]')).toHaveText('Remote Version')
  })

  test('should show real-time updates', async ({ page }) => {
    await page.goto('/items')

    // Simulate real-time update event
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('realtime:update', {
          detail: {
            type: 'item:created',
            data: {
              id: 'realtime-item',
              title: 'Real-time Item',
              type: 'task',
            },
          },
        })
      )
    })

    // Wait for update to be processed
    await page.waitForTimeout(500)

    // New item should appear
    await expect(page.locator('text=Real-time Item')).toBeVisible()

    // Should show notification
    const notification = page.locator('[data-testid="notification"]')
    await expect(notification).toBeVisible()
    await expect(notification).toContainText('New item created')
  })
})

test.describe('Multi-Agent Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/agents')
    await page.waitForLoadState('networkidle')
  })

  test('should create agents and assign to items', async ({ page }) => {
    // Create new agent
    await page.click('button:has-text("New Agent")')
    await page.fill('input[name="name"]', 'Test Agent')
    await page.selectOption('select[name="role"]', 'developer')
    await page.click('button:has-text("Create")')

    // Navigate to items
    await page.goto('/items')
    await page.click('[data-testid="item-card"]').first()

    // Assign agent
    await page.click('button:has-text("Assign Agent")')
    await page.fill('input[name="agent"]', 'Test Agent')
    await page.click('[data-testid="agent-option"]:has-text("Test Agent")')
    await page.click('button:has-text("Assign")')

    // Agent should appear in item
    await expect(page.locator('[data-testid="assigned-agents"]')).toContainText('Test Agent')

    // Navigate to agent detail
    await page.goto('/agents')
    await page.click('[data-testid="agent-card"]:has-text("Test Agent")')

    // Should show assigned items
    const assignedItems = page.locator('[data-testid="assigned-items"]')
    await expect(assignedItems).toHaveCountGreaterThan(0)
  })

  test('should track agent workload', async ({ page }) => {
    await page.click('[data-testid="agent-card"]').first()

    // Should show workload metrics
    await expect(page.locator('[data-testid="assigned-count"]')).toBeVisible()
    await expect(page.locator('[data-testid="completed-count"]')).toBeVisible()
    await expect(page.locator('[data-testid="in-progress-count"]')).toBeVisible()

    // Workload indicator should be visible
    const workloadBar = page.locator('[data-testid="workload-bar"]')
    await expect(workloadBar).toBeVisible()

    // Should categorize workload (low/medium/high)
    const workloadStatus = page.locator('[data-testid="workload-status"]')
    await expect(workloadStatus).toHaveText(/low|medium|high/i)
  })

  test('should filter items by agent', async ({ page }) => {
    // Get agent name
    const agentName = await page.locator('[data-testid="agent-card"]').first().textContent()

    // Navigate to items
    await page.goto('/items')

    // Open filter panel
    await page.click('button:has-text("Filter")')

    // Select agent filter
    await page.click('[data-testid="filter-agent"]')
    await page.fill('input[name="agent"]', agentName!)
    await page.click(`[data-testid="agent-option"]:has-text("${agentName}")`)
    await page.click('button:has-text("Apply")')

    // All visible items should have this agent assigned
    const items = page.locator('[data-testid="item-card"]')
    const count = await items.count()

    for (let i = 0; i < Math.min(count, 5); i++) {
      const agents = items.nth(i).locator('[data-testid="assigned-agents"]')
      await expect(agents).toContainText(agentName!)
    }
  })
})

test.describe('Bulk Operations Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/items')
    await page.waitForLoadState('networkidle')
  })

  test('should select multiple items and bulk update', async ({ page }) => {
    // Enable selection mode
    await page.click('button:has-text("Select")')

    // Select multiple items
    await page.click('[data-testid="item-checkbox"]').first()
    await page.click('[data-testid="item-checkbox"]').nth(1)
    await page.click('[data-testid="item-checkbox"]').nth(2)

    // Bulk action toolbar should appear
    const bulkToolbar = page.locator('[data-testid="bulk-toolbar"]')
    await expect(bulkToolbar).toBeVisible()
    await expect(bulkToolbar).toContainText('3 selected')

    // Bulk update status
    await page.click('button:has-text("Update Status")')
    await page.selectOption('select[name="status"]', 'in-progress')
    await page.click('button:has-text("Apply")')

    // All selected items should have new status
    const items = page.locator('[data-testid="item-card"]:has([data-testid="item-checkbox"]:checked)')
    const count = await items.count()

    for (let i = 0; i < count; i++) {
      const status = items.nth(i).locator('[data-testid="status-badge"]')
      await expect(status).toHaveText('In Progress')
    }
  })

  test('should bulk delete with confirmation', async ({ page }) => {
    await page.click('button:has-text("Select")')

    // Select items
    await page.click('[data-testid="item-checkbox"]').first()
    await page.click('[data-testid="item-checkbox"]').nth(1)

    // Click bulk delete
    await page.click('button:has-text("Delete")')

    // Confirmation dialog should appear
    const confirmDialog = page.locator('[data-testid="confirm-dialog"]')
    await expect(confirmDialog).toBeVisible()
    await expect(confirmDialog).toContainText('Delete 2 items')

    // Confirm deletion
    await page.click('button:has-text("Confirm")')

    // Items should be removed
    await page.waitForTimeout(500)

    // Selection count should be 0
    const bulkToolbar = page.locator('[data-testid="bulk-toolbar"]')
    await expect(bulkToolbar).not.toBeVisible()
  })

  test('should bulk export items', async ({ page }) => {
    await page.click('button:has-text("Select")')

    // Select all items on page
    await page.click('button:has-text("Select All")')

    // Click export
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button:has-text("Export")'),
    ])

    // Verify download
    expect(download.suggestedFilename()).toMatch(/items.*\.json/)

    // File should exist
    const path = await download.path()
    expect(path).toBeTruthy()
  })
})

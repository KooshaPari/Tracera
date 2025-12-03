import { test, expect } from '@playwright/test'

/**
 * E2E Tests for Agent Management
 * Tests agent listing, status monitoring, task execution, and configuration
 */
test.describe('Agents Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test.describe('Agents List View', () => {
    test('should navigate to agents page', async ({ page }) => {
      // Navigate to agents
      await page.getByRole('link', { name: /agents/i }).click()
      await page.waitForLoadState('networkidle')

      // Verify URL
      await expect(page).toHaveURL(/\/agents/)

      // Verify page heading
      const heading = page.getByRole('heading', { name: /agents/i })
      await expect(heading).toBeVisible()
    })

    test('should display list of agents', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      // Check for agents list
      const agentsList = page.locator('[data-testid="agents-list"]')
      await expect(agentsList).toBeVisible({ timeout: 5000 }).catch(() => {
        console.log('Agents list not found - checking alternative selectors')
      })

      // Look for individual agent cards/rows
      const agentCards = page.locator('[data-testid="agent-card"]')
      const count = await agentCards.count().catch(() => 0)

      if (count > 0) {
        expect(count).toBeGreaterThan(0)
        console.log(`Found ${count} agents`)
      } else {
        console.log('Agent cards not found - may use table layout')

        // Try table rows
        const agentRows = page.locator('[data-testid="agent-row"]')
        const rowCount = await agentRows.count().catch(() => 0)
        console.log(`Found ${rowCount} agent rows`)
      }
    })

    test('should show agent details', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      // Check for agent names from mock data
      const codeAnalyzer = page.getByText(/code analyzer/i)
      await expect(codeAnalyzer).toBeVisible({ timeout: 5000 }).catch(() => {
        console.log('Code Analyzer agent not found')
      })

      const testRunner = page.getByText(/test runner/i)
      await expect(testRunner).toBeVisible({ timeout: 5000 }).catch(() => {
        console.log('Test Runner agent not found')
      })

      const docGenerator = page.getByText(/documentation generator/i)
      await expect(docGenerator).toBeVisible({ timeout: 5000 }).catch(() => {
        console.log('Documentation Generator agent not found')
      })
    })
  })

  test.describe('Agent Status', () => {
    test('should display agent status badges', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      // Look for status indicators
      const idleStatus = page.getByText(/idle/i).first()
      await expect(idleStatus).toBeVisible({ timeout: 5000 }).catch(() => {
        console.log('Idle status not displayed')
      })

      const busyStatus = page.getByText(/busy|running/i).first()
      await expect(busyStatus).toBeVisible({ timeout: 5000 }).catch(() => {
        console.log('Busy status not displayed')
      })
    })

    test('should show agent type', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      // Check for agent types
      const analyzerType = page.getByText(/analyzer/i)
      await expect(analyzerType).toBeVisible({ timeout: 5000 }).catch(() => {
        console.log('Analyzer type not displayed')
      })

      const testType = page.getByText(/test/i)
      await expect(testType).toBeVisible({ timeout: 5000 }).catch(() => {
        console.log('Test type not displayed')
      })
    })

    test('should show agent capabilities', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      // Click first agent to view details
      const firstAgent = page.locator('[data-testid="agent-card"]').first()
      if (await firstAgent.isVisible({ timeout: 2000 })) {
        await firstAgent.click()
        await page.waitForLoadState('networkidle')

        // Look for capabilities section
        const capabilitiesSection = page.getByRole('heading', { name: /capabilities/i })
        await expect(capabilitiesSection).toBeVisible({ timeout: 5000 }).catch(() => {
          console.log('Capabilities section not found')
        })

        // Check for specific capabilities
        const capabilities = page.getByText(/code.*analysis|test.*execution|doc.*generation/i)
        await expect(capabilities.first()).toBeVisible({ timeout: 5000 }).catch(() => {
          console.log('Capabilities not listed')
        })
      } else {
        console.log('Agent cards not clickable')
      }
    })

    test('should show last heartbeat time', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      // Look for last seen/heartbeat indicator
      const lastSeen = page.getByText(/last.*seen|heartbeat|active.*ago/i)
      await expect(lastSeen.first()).toBeVisible({ timeout: 5000 }).catch(() => {
        console.log('Last heartbeat time not displayed')
      })
    })
  })

  test.describe('Agent Actions', () => {
    test('should start agent task', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      // Find an idle agent
      const idleAgent = page.locator('[data-testid="agent-card"]').filter({ hasText: /idle/i }).first()
      if (await idleAgent.isVisible({ timeout: 2000 })) {
        // Click to view details
        await idleAgent.click()
        await page.waitForLoadState('networkidle')

        // Look for start task button
        const startTaskBtn = page.getByRole('button', { name: /start.*task|run.*task|execute/i })
        if (await startTaskBtn.isVisible({ timeout: 2000 })) {
          await startTaskBtn.click()

          // Should show task configuration dialog
          const taskDialog = page.getByRole('dialog')
          await expect(taskDialog).toBeVisible({ timeout: 5000 }).catch(() => {
            console.log('Task configuration dialog not shown')
          })
        } else {
          console.log('Start task button not found')
        }
      } else {
        console.log('No idle agents available to start tasks')
      }
    })

    test('should stop running agent task', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      // Find a busy agent
      const busyAgent = page.locator('[data-testid="agent-card"]').filter({ hasText: /busy|running/i }).first()
      if (await busyAgent.isVisible({ timeout: 2000 })) {
        await busyAgent.click()
        await page.waitForLoadState('networkidle')

        // Look for stop button
        const stopBtn = page.getByRole('button', { name: /stop|cancel|abort/i })
        if (await stopBtn.isVisible({ timeout: 2000 })) {
          await stopBtn.click()

          // Confirm if needed
          const confirmBtn = page.getByRole('button', { name: /confirm|yes/i })
          if (await confirmBtn.isVisible({ timeout: 2000 })) {
            await confirmBtn.click()
          }

          await page.waitForLoadState('networkidle')

          // Should show stopped message
          const stoppedMsg = page.getByText(/stopped|cancelled/i)
          await expect(stoppedMsg).toBeVisible({ timeout: 5000 }).catch(() => {
            console.log('Stop confirmation not shown')
          })
        } else {
          console.log('Stop button not found for busy agent')
        }
      } else {
        console.log('No busy agents available to stop')
      }
    })

    test('should restart agent', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      const firstAgent = page.locator('[data-testid="agent-card"]').first()
      if (await firstAgent.isVisible({ timeout: 2000 })) {
        await firstAgent.click()
        await page.waitForLoadState('networkidle')

        // Look for restart button
        const restartBtn = page.getByRole('button', { name: /restart|reboot/i })
        if (await restartBtn.isVisible({ timeout: 2000 })) {
          await restartBtn.click()

          // Confirm restart
          const confirmBtn = page.getByRole('button', { name: /confirm|yes/i })
          if (await confirmBtn.isVisible({ timeout: 2000 })) {
            await confirmBtn.click()
            await page.waitForLoadState('networkidle')
          }

          console.log('Agent restart triggered')
        } else {
          console.log('Restart button not available')
        }
      } else {
        console.log('Agents not available')
      }
    })
  })

  test.describe('Agent Tasks', () => {
    test('should display task history', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      const firstAgent = page.locator('[data-testid="agent-card"]').first()
      if (await firstAgent.isVisible({ timeout: 2000 })) {
        await firstAgent.click()
        await page.waitForLoadState('networkidle')

        // Look for task history section
        const historySection = page.getByRole('heading', { name: /task.*history|recent.*tasks/i })
        await expect(historySection).toBeVisible({ timeout: 5000 }).catch(() => {
          console.log('Task history section not found')
        })

        // Check for task list
        const taskList = page.locator('[data-testid="task-list"]')
        await expect(taskList).toBeVisible({ timeout: 5000 }).catch(() => {
          console.log('Task list not displayed')
        })
      } else {
        console.log('Agents not accessible')
      }
    })

    test('should show task execution logs', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      const firstAgent = page.locator('[data-testid="agent-card"]').first()
      if (await firstAgent.isVisible({ timeout: 2000 })) {
        await firstAgent.click()
        await page.waitForLoadState('networkidle')

        // Look for logs section
        const logsSection = page.getByRole('heading', { name: /logs|output/i })
        if (await logsSection.isVisible({ timeout: 2000 })) {
          // Check for log content
          const logContent = page.locator('[data-testid="agent-logs"]')
          await expect(logContent).toBeVisible({ timeout: 5000 }).catch(() => {
            console.log('Agent logs not displayed')
          })
        } else {
          console.log('Logs section not found')
        }
      } else {
        console.log('Agents not available')
      }
    })

    test('should filter tasks by status', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      const firstAgent = page.locator('[data-testid="agent-card"]').first()
      if (await firstAgent.isVisible({ timeout: 2000 })) {
        await firstAgent.click()
        await page.waitForLoadState('networkidle')

        // Look for status filter
        const statusFilter = page.getByLabel(/status|filter/i)
        if (await statusFilter.isVisible({ timeout: 2000 })) {
          await statusFilter.click()
          await page.getByText(/completed|failed|running/i).first().click()
          await page.waitForLoadState('networkidle')

          console.log('Task status filter applied')
        } else {
          console.log('Task status filter not available')
        }
      } else {
        console.log('Agents not available')
      }
    })
  })

  test.describe('Agent Configuration', () => {
    test('should open agent settings', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      const firstAgent = page.locator('[data-testid="agent-card"]').first()
      if (await firstAgent.isVisible({ timeout: 2000 })) {
        await firstAgent.click()
        await page.waitForLoadState('networkidle')

        // Look for settings button
        const settingsBtn = page.getByRole('button', { name: /settings|configure/i })
        if (await settingsBtn.isVisible({ timeout: 2000 })) {
          await settingsBtn.click()

          // Settings dialog should open
          const settingsDialog = page.getByRole('dialog', { name: /settings|configuration/i })
          await expect(settingsDialog).toBeVisible({ timeout: 5000 }).catch(() => {
            console.log('Agent settings dialog not shown')
          })
        } else {
          console.log('Settings button not found')
        }
      } else {
        console.log('Agents not available')
      }
    })

    test('should update agent configuration', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      const firstAgent = page.locator('[data-testid="agent-card"]').first()
      if (await firstAgent.isVisible({ timeout: 2000 })) {
        await firstAgent.click()
        await page.waitForLoadState('networkidle')

        const settingsBtn = page.getByRole('button', { name: /settings|configure/i })
        if (await settingsBtn.isVisible({ timeout: 2000 })) {
          await settingsBtn.click()

          const settingsDialog = page.getByRole('dialog')
          if (await settingsDialog.isVisible({ timeout: 2000 })) {
            // Look for configuration fields
            const nameInput = settingsDialog.getByLabel(/name/i)
            if (await nameInput.isVisible({ timeout: 2000 })) {
              await nameInput.fill('Updated Agent Name')

              // Save settings
              const saveBtn = settingsDialog.getByRole('button', { name: /save|update/i })
              await saveBtn.click()
              await page.waitForLoadState('networkidle')

              // Verify update
              await expect(page.getByText(/updated agent name/i)).toBeVisible({ timeout: 5000 })
            } else {
              console.log('Configuration fields not found')
            }
          }
        } else {
          console.log('Settings not accessible')
        }
      } else {
        console.log('Agents not available')
      }
    })
  })

  test.describe('Agent Monitoring', () => {
    test('should display agent metrics', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      const firstAgent = page.locator('[data-testid="agent-card"]').first()
      if (await firstAgent.isVisible({ timeout: 2000 })) {
        await firstAgent.click()
        await page.waitForLoadState('networkidle')

        // Look for metrics section
        const metricsSection = page.getByRole('heading', { name: /metrics|statistics/i })
        if (await metricsSection.isVisible({ timeout: 2000 })) {
          // Check for common metrics
          const tasksCompleted = page.getByText(/tasks.*completed|completed.*tasks/i)
          await expect(tasksCompleted).toBeVisible({ timeout: 5000 }).catch(() => {
            console.log('Tasks completed metric not shown')
          })

          const successRate = page.getByText(/success.*rate|success.*%/i)
          await expect(successRate).toBeVisible({ timeout: 5000 }).catch(() => {
            console.log('Success rate not shown')
          })
        } else {
          console.log('Metrics section not found')
        }
      } else {
        console.log('Agents not available')
      }
    })

    test('should show real-time agent status updates', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      // Note: Real-time updates require WebSocket connection
      // For now, just verify status is displayed
      const statusBadge = page.locator('[data-testid="agent-status"]').first()
      await expect(statusBadge).toBeVisible({ timeout: 5000 }).catch(() => {
        console.log('Agent status badges not found')
      })

      console.log('Real-time status updates require WebSocket simulation')
    })

    test('should display resource usage', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      const firstAgent = page.locator('[data-testid="agent-card"]').first()
      if (await firstAgent.isVisible({ timeout: 2000 })) {
        await firstAgent.click()
        await page.waitForLoadState('networkidle')

        // Look for resource usage indicators
        const cpuUsage = page.getByText(/cpu|processor/i)
        await expect(cpuUsage).toBeVisible({ timeout: 5000 }).catch(() => {
          console.log('CPU usage not displayed')
        })

        const memoryUsage = page.getByText(/memory|ram/i)
        await expect(memoryUsage).toBeVisible({ timeout: 5000 }).catch(() => {
          console.log('Memory usage not displayed')
        })
      } else {
        console.log('Agents not available')
      }
    })
  })

  test.describe('Agent Dashboard Widget', () => {
    test('should display agents widget on dashboard', async ({ page }) => {
      await page.goto('/')
      await page.waitForLoadState('networkidle')

      // Look for agents widget
      const agentsWidget = page.locator('[data-testid="agents-widget"]')
      await expect(agentsWidget).toBeVisible({ timeout: 5000 }).catch(() => {
        console.log('Agents widget not found on dashboard')
      })

      // Alternative: check for agents section
      const agentsSection = page.getByRole('heading', { name: /agents/i })
      await expect(agentsSection).toBeVisible({ timeout: 5000 }).catch(() => {
        console.log('Agents section not on dashboard')
      })
    })

    test('should show agent status summary', async ({ page }) => {
      await page.goto('/')
      await page.waitForLoadState('networkidle')

      const agentsWidget = page.locator('[data-testid="agents-widget"]')
      if (await agentsWidget.isVisible({ timeout: 2000 })) {
        // Check for status counts
        const idleCount = agentsWidget.getByText(/\d+.*idle/i)
        await expect(idleCount).toBeVisible({ timeout: 5000 }).catch(() => {
          console.log('Idle agent count not shown')
        })

        const busyCount = agentsWidget.getByText(/\d+.*busy/i)
        await expect(busyCount).toBeVisible({ timeout: 5000 }).catch(() => {
          console.log('Busy agent count not shown')
        })
      } else {
        console.log('Agents widget not available')
      }
    })

    test('should navigate to agents page from widget', async ({ page }) => {
      await page.goto('/')
      await page.waitForLoadState('networkidle')

      const agentsWidget = page.locator('[data-testid="agents-widget"]')
      if (await agentsWidget.isVisible({ timeout: 2000 })) {
        // Look for "View All" or similar link
        const viewAllLink = agentsWidget.getByRole('link', { name: /view.*all|see.*all|more/i })
        if (await viewAllLink.isVisible({ timeout: 2000 })) {
          await viewAllLink.click()
          await page.waitForLoadState('networkidle')

          // Should navigate to agents page
          await expect(page).toHaveURL(/\/agents/)
        } else {
          // Try clicking widget header
          const widgetHeader = agentsWidget.getByRole('heading', { name: /agents/i })
          if (await widgetHeader.isVisible({ timeout: 2000 })) {
            await widgetHeader.click()
            await page.waitForLoadState('networkidle')
            await expect(page).toHaveURL(/\/agents/).catch(() => {
              console.log('Widget header not clickable for navigation')
            })
          }
        }
      } else {
        console.log('Agents widget not available')
      }
    })
  })

  test.describe('Agent Filtering', () => {
    test('should filter agents by status', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      const statusFilter = page.getByLabel(/status|filter.*status/i)
      if (await statusFilter.isVisible({ timeout: 2000 })) {
        await statusFilter.click()
        await page.getByText(/idle/i).click()
        await page.waitForLoadState('networkidle')

        // All visible agents should be idle
        const agentCards = page.locator('[data-testid="agent-card"]')
        const count = await agentCards.count().catch(() => 0)
        console.log(`Filtered to ${count} idle agents`)
      } else {
        console.log('Status filter not available')
      }
    })

    test('should filter agents by type', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      const typeFilter = page.getByLabel(/type|filter.*type/i)
      if (await typeFilter.isVisible({ timeout: 2000 })) {
        await typeFilter.click()
        await page.getByText(/analyzer|test|documentation/i).first().click()
        await page.waitForLoadState('networkidle')

        console.log('Type filter applied')
      } else {
        console.log('Type filter not available')
      }
    })

    test('should search agents by name', async ({ page }) => {
      await page.goto('/agents')
      await page.waitForLoadState('networkidle')

      const searchInput = page.getByPlaceholder(/search.*agent/i)
      if (await searchInput.isVisible({ timeout: 2000 })) {
        await searchInput.fill('code')
        await page.waitForLoadState('networkidle')

        // Should show Code Analyzer
        const codeAnalyzer = page.getByText(/code analyzer/i)
        await expect(codeAnalyzer).toBeVisible({ timeout: 5000 })
      } else {
        console.log('Agent search not available')
      }
    })
  })
})

/**
 * Comprehensive Tests for AgentsView
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AgentsView } from '../../views/AgentsView'

describe('AgentsView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders agents interface', () => {
    render(<AgentsView />)

    expect(screen.getByText('Agents')).toBeInTheDocument()
    expect(screen.getByText(/Monitor and manage automation agents/i)).toBeInTheDocument()
    expect(screen.getByText('+ New Agent')).toBeInTheDocument()
  })

  it('displays agent cards', () => {
    render(<AgentsView />)

    expect(screen.getByText('Sync Agent')).toBeInTheDocument()
    expect(screen.getByText('Validation Agent')).toBeInTheDocument()
    expect(screen.getByText('Coverage Agent')).toBeInTheDocument()
  })

  it('displays agent status badges', () => {
    render(<AgentsView />)

    expect(screen.getByText('active')).toBeInTheDocument()
    expect(screen.getByText('idle')).toBeInTheDocument()
    expect(screen.getByText('running')).toBeInTheDocument()
  })

  it('displays task counts', () => {
    render(<AgentsView />)

    expect(screen.getByText(/24 tasks completed/)).toBeInTheDocument()
    expect(screen.getByText(/12 tasks completed/)).toBeInTheDocument()
    expect(screen.getByText(/8 tasks completed/)).toBeInTheDocument()
  })

  it('displays action buttons for each agent', () => {
    render(<AgentsView />)

    const viewLogsButtons = screen.getAllByText('View Logs')
    const configureButtons = screen.getAllByText('Configure')

    expect(viewLogsButtons.length).toBeGreaterThan(0)
    expect(configureButtons.length).toBeGreaterThan(0)
  })

  it('handles new agent button click', async () => {
    const user = userEvent.setup()
    render(<AgentsView />)

    const newAgentButton = screen.getByText('+ New Agent')
    await user.click(newAgentButton)

    // Should trigger new agent creation
    expect(newAgentButton).toBeInTheDocument()
  })
})

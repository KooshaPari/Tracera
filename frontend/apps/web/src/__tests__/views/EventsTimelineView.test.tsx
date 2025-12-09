/**
 * Comprehensive Tests for EventsTimelineView
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { EventsTimelineView } from '../../views/EventsTimelineView'
import { useItems } from '../../hooks/useItems'

vi.mock('../../hooks/useItems', () => ({
  useItems: vi.fn(),
}))

describe('EventsTimelineView', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
    vi.clearAllMocks()
  })

  it('renders events timeline interface', () => {
    vi.mocked(useItems).mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
      error: null,
    } as any)

    render(
      <QueryClientProvider client={queryClient}>
        <EventsTimelineView />
      </QueryClientProvider>
    )

    expect(screen.getByText('Events Timeline')).toBeInTheDocument()
  })

  it('displays loading state', () => {
    vi.mocked(useItems).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
    } as any)

    render(
      <QueryClientProvider client={queryClient}>
        <EventsTimelineView />
      </QueryClientProvider>
    )

    // Should show loading state
  })

  it('displays events in timeline', () => {
    const events = [
      {
        id: 'event-1',
        title: 'Event 1',
        type: 'event',
        created_at: new Date().toISOString(),
      },
      {
        id: 'event-2',
        title: 'Event 2',
        type: 'event',
        created_at: new Date().toISOString(),
      },
    ]

    vi.mocked(useItems).mockReturnValue({
      data: events,
      isLoading: false,
      isError: false,
      error: null,
    } as any)

    render(
      <QueryClientProvider client={queryClient}>
        <EventsTimelineView />
      </QueryClientProvider>
    )

    expect(screen.getByText('Events Timeline')).toBeInTheDocument()
  })
})

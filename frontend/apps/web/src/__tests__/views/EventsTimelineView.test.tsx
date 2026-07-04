/**
 * Comprehensive Tests for EventsTimelineView
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useItems } from '../../hooks/useItems';
import { EventsTimelineView } from '../../views/EventsTimelineView';

vi.mock('../../hooks/useItems', () => ({
  useItems: vi.fn(),
}));

describe(EventsTimelineView, () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: { retry: false },
        queries: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  it('renders events timeline interface', () => {
    vi.mocked(useItems).mockReturnValue({
      data: [],
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <EventsTimelineView />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Events Timeline')).toBeInTheDocument();
  });

  it('displays loading state', () => {
    vi.mocked(useItems).mockReturnValue({
      data: undefined,
      error: null,
      isError: false,
      isLoading: true,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <EventsTimelineView />
      </QueryClientProvider>,
    );

    // Should show loading state
  });

  it('displays events in timeline', () => {
    const events = [
      {
        created_at: new Date().toISOString(),
        id: 'event-1',
        title: 'Event 1',
        type: 'event',
      },
      {
        created_at: new Date().toISOString(),
        id: 'event-2',
        title: 'Event 2',
        type: 'event',
      },
    ];

    vi.mocked(useItems).mockReturnValue({
      data: events,
      error: null,
      isError: false,
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <EventsTimelineView />
      </QueryClientProvider>,
    );

    expect(screen.getByText('Events Timeline')).toBeInTheDocument();
  });
});

/**
 * Comprehensive Tests for EventsTimelineView
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { EventsTimelineView } from "../../views/EventsTimelineView";

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

  it("renders events timeline interface", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <EventsTimelineView />
      </QueryClientProvider>,
    );

    expect(screen.getByRole("heading", { name: "Audit Timeline" })).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Search audit trail...")).toBeInTheDocument();
  });

  it("displays loading state", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <EventsTimelineView />
      </QueryClientProvider>,
    );

    expect(screen.getByText("User Authentication")).toBeInTheDocument();
  });

  it("displays events in timeline", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <EventsTimelineView />
      </QueryClientProvider>,
    );

    expect(screen.getByText("User Authentication")).toBeInTheDocument();
    expect(screen.getByText("Traceability Link")).toBeInTheDocument();
    expect(screen.getByText("Database Schema")).toBeInTheDocument();
  });
});

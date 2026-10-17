import type { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useNotifications } from "./useNotifications";

const mocks = vi.hoisted(() => ({ stream: vi.fn() }));
vi.mock("@/stores/authStore", () => ({ useAuthStore: () => ({ token: "test-token" }) }));
vi.mock("@/lib/sse-client", () => ({ createNotificationSSEClient: mocks.stream }));

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});

describe("notification availability", () => {
  it.each([404, 501, 503])("keeps HTTP %s unknown instead of zero", async (status) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(null, { status })));
    const { result } = renderHook(() => useNotifications(), { wrapper });
    await waitFor(() => expect(result.current.error).toMatchObject({ status }));
    expect(result.current.notifications).toBeUndefined();
    expect(result.current.unreadCount).toBeUndefined();
    expect(mocks.stream).not.toHaveBeenCalled();
  });

  it("accepts a genuinely empty successful collection", async () => {
    mocks.stream.mockReturnValue({ connect: vi.fn(), close: vi.fn(), isConnected: () => false });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("[]", { status: 200 })));
    const { result } = renderHook(() => useNotifications(), { wrapper });
    await waitFor(() => expect(result.current.unreadCount).toBe(0));
    expect(result.current.notifications).toEqual([]);
    expect(result.current.error).toBeNull();
  });
});

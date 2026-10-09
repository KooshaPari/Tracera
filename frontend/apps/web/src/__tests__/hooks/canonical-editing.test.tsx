import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useCreateItem, useUpdateItem, useDeleteItem, useItem } from "../../hooks/useItems";
import { useCreateLink, useDeleteLink } from "../../hooks/useLinks";
import { useAuthStore } from "../../stores/authStore";
import { setCSRFToken } from "../../lib/csrf";

const mockFetch = vi.fn();
const item = { id: "FR-01", project_id: "A", title: "Test", view: "feature", type: "task", status: "todo" };
function wrapper({ children }: { children: React.ReactNode }) {
  const [client] = React.useState(() => new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } }));
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
  mockFetch.mockReset();
  useAuthStore.setState({ token: "contract-token" });
  setCSRFToken("csrf-contract");
});
describe("canonical editing bindings", () => {
  it("creates a canonical item without unsupported fields and accepts absent item timestamps", async () => {
    mockFetch.mockResolvedValue(new Response(JSON.stringify(item), { status: 201 }));
    const { result } = renderHook(() => useCreateItem(), { wrapper });
    await act(async () => { await result.current.mutateAsync({ projectId: "A", title: "Test", view: "feature", type: "task", status: "todo" }); });
    const [, init] = mockFetch.mock.calls[0];
    expect(JSON.parse(init.body)).toEqual({ project_id: "A", title: "Test", view: "feature", type: "task", status: "todo" });
    expect(init.headers["X-CSRF-Token"]).toBe("csrf-contract");
    expect(init.credentials).toBe("include");
    await waitFor(() => expect(result.current.data?.createdAt).toBe(""));
  });
  it("updates the same imported ID in separate projects without leaking scope", async () => {
    mockFetch.mockImplementation(async (url: string) => new Response(JSON.stringify({ ...item, project_id: new URL(url, "https://example.test").searchParams.get("project_id") }), { status: 200 }));
    const { result } = renderHook(() => useUpdateItem(), { wrapper });
    for (const projectId of ["A", "B"]) await act(async () => { await result.current.mutateAsync({ id: "FR-01", projectId, data: { title: projectId } }); });
    expect(mockFetch.mock.calls.map(([url]) => new URL(url, "https://example.test").searchParams.get("project_id"))).toEqual(["A", "B"]);
    expect(mockFetch.mock.calls.map(([, init]) => JSON.parse(init.body))).toEqual([{ title: "A" }, { title: "B" }]);
    await waitFor(() => expect(result.current.data?.projectId).toBe("B"));
  });
  it("switches item detail cache scope when two projects reuse the same imported ID", async () => {
    mockFetch.mockImplementation(async (url: string) => {
      const project = new URL(url, "https://example.test").searchParams.get("project_id");
      return new Response(JSON.stringify({ ...item, project_id: project, title: `Item in ${project}` }), { status: 200 });
    });
    const { result, rerender } = renderHook(({ projectId }) => useItem("FR-01", projectId), { wrapper, initialProps: { projectId: "A" } });
    await waitFor(() => expect(result.current.data?.title).toBe("Item in A"));
    rerender({ projectId: "B" });
    await waitFor(() => expect(result.current.data?.title).toBe("Item in B"));
    await waitFor(() => expect(result.current.data?.projectId).toBe("B"));
    expect(mockFetch.mock.calls.map(([url]) => new URL(url, "https://example.test").searchParams.get("project_id"))).toEqual(["A", "B"]);
  });
  it("rejects unsupported edits before a request rather than discarding user input", async () => {
    const { result } = renderHook(() => useUpdateItem(), { wrapper });
    await expect(result.current.mutateAsync({ id: "FR-01", projectId: "A", data: { owner: "me" } })).rejects.toThrow(/not supported/);
    expect(mockFetch).not.toHaveBeenCalled();
  });
  it("deletes items with scope, cookies and CSRF protection", async () => {
    mockFetch.mockResolvedValue(new Response(null, { status: 204 }));
    const { result } = renderHook(() => useDeleteItem(), { wrapper });
    await act(async () => { await result.current.mutateAsync({ id: "FR/01", projectId: "A&B" }); });
    const [url, init] = mockFetch.mock.calls[0];
    expect(new URL(url, "https://example.test").searchParams.get("project_id")).toBe("A&B");
    expect(url).toContain("FR%2F01");
    expect(init.headers["X-CSRF-Token"]).toBe("csrf-contract");
    expect(init.credentials).toBe("include");
  });
  it("creates links with canonical payload and deletes the returned opaque identity", async () => {
    const canonicalLink = { id: "opaque-link", project_id: "A", source_id: "FR-01", target_id: "FR-02", type: "tests" };
    mockFetch.mockResolvedValueOnce(new Response(JSON.stringify(canonicalLink), { status: 201 })).mockResolvedValueOnce(new Response(null, { status: 204 }));
    const { result } = renderHook(() => ({ create: useCreateLink(), remove: useDeleteLink() }), { wrapper });
    await act(async () => { const link = await result.current.create.mutateAsync({ projectId: "A", sourceId: "FR-01", targetId: "FR-02", type: "tests" }); await result.current.remove.mutateAsync({ id: link.id, projectId: link.projectId }); });
    expect(JSON.parse(mockFetch.mock.calls[0][1].body)).toEqual({ project_id: "A", source_id: "FR-01", target_id: "FR-02", type: "tests" });
    expect(mockFetch.mock.calls[1][0]).toContain("/links/opaque-link?project_id=A");
  });
});

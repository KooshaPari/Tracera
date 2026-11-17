import { beforeEach, describe, expect, mock, test } from "bun:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { JSDOM } from "jsdom";

const get = mock();
mock.module("../src/api/client", () => ({
  client: { apiClient: { GET: get }, API_BASE_URL: "", getAuthHeaders: () => ({}) },
}));
mock.module("../src/api/mcp-config", () => ({ getMcpConfig: async () => ({}) }));
mock.module("../src/api/endpoints", () => ({ exportImportApi: {} }));
mock.module("../src/stores/authStore", () => ({ useAuthStore: mock() }));
const { ApiError } = await import("../src/api/client-errors");
const { Unavailable } = await import("../src/components/Availability");
const { ProjectSummary } = await import("../src/components/ProjectSummary");
const { fetchEvents, fetchEvent } = await import("../src/api/events");
const { fetchMatrix, exportMatrix } = await import("../src/api/matrix");
const { fetchSystemStatus } = await import("../src/api/system");
const { fetchReportTemplates, generateReport } = await import("../src/api/reports");
const { fetchProject } = await import("../src/hooks/useProjects");
const originalFetch = globalThis.fetch;
beforeEach(() => {
  get.mockReset();
  globalThis.fetch = originalFetch;
});
const reply = (status: number, data?: unknown) => ({
  response: new Response(null, { status }),
  data,
  error: status >= 400 ? { error: "not_implemented" } : undefined,
});
const dom = (element: React.ReactNode) => new JSDOM(renderToStaticMarkup(element)).window.document;

describe("frontend honest availability on desk Bun runner", () => {
  test.each([501, 503, 401])("wrappers preserve HTTP %s", async (status) => {
    get.mockResolvedValue(reply(status));
    for (const call of [
      fetchEvents,
      () => fetchEvent("id"),
      () => fetchMatrix("p"),
      () => exportMatrix("p", "csv"),
      fetchSystemStatus,
    ]) {
      await expect(call()).rejects.toMatchObject({ status });
    }
  });
  test("malformed data is not an empty success", async () => {
    get.mockResolvedValue(reply(200, {}));
    await expect(fetchEvents()).rejects.toMatchObject({ status: 502 });
    await expect(fetchMatrix("p")).rejects.toMatchObject({ status: 502 });
    await expect(fetchSystemStatus()).rejects.toMatchObject({ status: 502 });
  });
  test("real empty events remain valid; reports are honest 501", async () => {
    get.mockResolvedValue(reply(200, []));
    expect(await fetchEvents()).toEqual([]);
    await expect(fetchReportTemplates()).rejects.toMatchObject({ status: 501 });
    await expect(generateReport("p", "t", "pdf")).rejects.toMatchObject({ status: 501 });
  });
  test("genuine matrix export bytes are preserved", async () => {
    const blob = new Blob(["id,name\n1,real"], { type: "text/csv" });
    get.mockResolvedValue(reply(200, blob));
    expect(await exportMatrix("p", "csv")).toBe(blob);
  });
  test("501 renders Not implemented yet; transport renders unavailable", () => {
    expect(
      dom(<Unavailable error={new ApiError(501, "missing")} />).querySelector("h2")?.textContent,
    ).toBe("Not implemented yet");
    expect(
      dom(<Unavailable error={new Error("offline")} />).querySelector('[role="alert"]')
        ?.textContent,
    ).toContain("Service unavailable");
  });
  test.each([404, 501])(
    "listed project remains a real DOM summary on detail %s",
    async (status) => {
      const fetch = mock()
        .mockResolvedValueOnce(new Response("{}", { status }))
        .mockResolvedValueOnce(
          Response.json({
            items: [{ id: "valid/id", name: "Actual project", description: "Real description" }],
          }),
        );
      globalThis.fetch = fetch as typeof globalThis.fetch;
      const project = await fetchProject("valid/id", "token");
      expect(fetch.mock.calls[0][0]).toContain("valid%2Fid");
      const document = dom(<ProjectSummary project={{ ...project, detailUnavailable: status }} />);
      expect(document.querySelector("h1")?.textContent).toBe("Actual project");
      expect(document.body.textContent).toContain("Real description");
      expect(document.body.textContent).toContain("Showing project summary");
      expect(document.body.textContent).not.toContain("Project Not Found");
      expect(document.body.textContent).not.toContain("0%");
    },
  );
  test("absent project and forbidden project stay errors", async () => {
    globalThis.fetch = mock()
      .mockResolvedValueOnce(new Response("{}", { status: 404 }))
      .mockResolvedValueOnce(Response.json({ items: [] })) as typeof globalThis.fetch;
    await expect(fetchProject("absent", "token")).rejects.toMatchObject({ status: 404 });
    const fetch = mock().mockResolvedValue(new Response("{}", { status: 403 }));
    globalThis.fetch = fetch as typeof globalThis.fetch;
    await expect(fetchProject("valid", "token")).rejects.toMatchObject({ status: 403 });
    expect(fetch).toHaveBeenCalledTimes(1);
  });
});

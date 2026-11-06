import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { ApiError } from "./client-errors";
import { describeFailure, isNonApiContent, requireAvailable } from "./availability";
import { Unavailable } from "@/components/Availability";
import { ProjectSummary } from "@/components/ProjectSummary";
import { fetchProject } from "@/hooks/useProjects";
import { fetchEvents, fetchEvent } from "./events";
import { fetchMatrix, exportMatrix } from "./matrix";
import { fetchReportTemplates, generateReport } from "./reports";
import { fetchSystemStatus } from "./system";
const mocks = vi.hoisted(() => ({ get: vi.fn(), mcp: vi.fn() }));
vi.mock("./client", () => ({
  client: { apiClient: { GET: mocks.get }, API_BASE_URL: "", getAuthHeaders: () => ({}) },
}));
vi.mock("./mcp-config", () => ({ getMcpConfig: mocks.mcp }));
vi.mock("./endpoints", () => ({ exportImportApi: {} }));
vi.mock("@/stores/authStore", () => ({ useAuthStore: vi.fn() }));
beforeEach(() => {
  vi.clearAllMocks();
  mocks.mcp.mockResolvedValue({});
});
const reply = (status: number, data?: unknown) => ({
  response: new Response(null, { status }),
  data,
  error: status >= 400 ? { error: "not_implemented" } : undefined,
});
describe("honest capability errors", () => {
  it.each([501, 503, 401])("preserves HTTP %s", async (status) => {
    await expect(requireAvailable(Promise.resolve(reply(status)))).rejects.toMatchObject({
      status,
    });
  });
  it.each([
    fetchEvents,
    () => fetchEvent("id"),
    () => fetchMatrix("p"),
    () => exportMatrix("p", "csv"),
    fetchSystemStatus,
  ])("never converts failures to success", async (call) => {
    mocks.get.mockResolvedValue(reply(501));
    await expect(call()).rejects.toMatchObject({ status: 501 });
  });
  it("rejects malformed successful responses", async () => {
    mocks.get.mockResolvedValue(reply(200, {}));
    await expect(fetchEvents()).rejects.toMatchObject({ status: 502 });
    await expect(fetchMatrix("p")).rejects.toMatchObject({ status: 502 });
    await expect(fetchSystemStatus()).rejects.toMatchObject({ status: 502 });
  });
  it("retains genuine empty events and real backend health", async () => {
    mocks.get.mockResolvedValueOnce(reply(200, []));
    expect(await fetchEvents()).toEqual([]);
    mocks.get.mockResolvedValueOnce(reply(200, { status: "ok", uptime_seconds: 12 }));
    expect(await fetchSystemStatus()).toMatchObject({
      status: "healthy",
      uptime: 12,
      queuedJobs: undefined,
    });
  });
  it("reports unsupported generation and templates as typed 501", async () => {
    await expect(generateReport("p", "t", "pdf")).rejects.toMatchObject({
      status: 501,
      data: { error: "not_implemented" },
    });
    await expect(fetchReportTemplates()).rejects.toMatchObject({ status: 501 });
  });
  it("renders the shared 501 message", () => {
    render(<Unavailable error={new ApiError(501, "not implemented")} />);
    expect(screen.getByText("Not implemented yet")).toBeInTheDocument();
    expect(screen.queryByText("Service unavailable")).not.toBeInTheDocument();
  });
  it("renders unavailable for transport failures", () => {
    render(<Unavailable error={new Error("offline")} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Service unavailable");
  });
});
describe("valid listed project routing", () => {
  it.each([404, 501])("renders real listed summary when detail returns %s", async (status) => {
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(new Response("{}", { status }))
      .mockResolvedValueOnce(
        Response.json({
          items: [{ id: "valid/id", name: "Actual project", description: "Real description" }],
        }),
      );
    vi.stubGlobal("fetch", fetch);
    const project = await fetchProject("valid/id", "token");
    expect(fetch.mock.calls[0][0]).toContain("/projects/valid%2Fid");
    expect(project).toMatchObject({ id: "valid/id", detailUnavailable: status });
    render(<ProjectSummary project={{ ...project, detailUnavailable: status }} />);
    expect(screen.getByRole("heading", { name: "Actual project" })).toBeInTheDocument();
    expect(screen.getByText("Real description")).toBeInTheDocument();
    expect(screen.getByText(/Showing project summary/)).toBeInTheDocument();
    expect(screen.queryByText("Project Not Found")).not.toBeInTheDocument();
  });
  it("does not turn an absent id into a project", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(new Response("{}", { status: 404 }))
        .mockResolvedValueOnce(Response.json({ items: [] })),
    );
    await expect(fetchProject("absent", "token")).rejects.toMatchObject({ status: 404 });
  });
  it("does not hide authorization failures behind summaries", async () => {
    const fetch = vi.fn().mockResolvedValue(new Response("{}", { status: 403 }));
    vi.stubGlobal("fetch", fetch);
    await expect(fetchProject("valid", "token")).rejects.toMatchObject({ status: 403 });
    expect(fetch).toHaveBeenCalledTimes(1);
  });
});

describe("failure state model", () => {
  it.each([
    [new ApiError(401, "unauthorized"), "unauthorized"],
    [new ApiError(403, "forbidden"), "forbidden"],
    [new ApiError(404, "absent"), "absent_route"],
    [new ApiError(405, "method"), "absent_route"],
    [new ApiError(429, "limited"), "rate_limited"],
    [new ApiError(501, "not implemented"), "not_implemented"],
    [new ApiError(500, "server"), "unavailable"],
    [new ApiError(502, "invalid", { error: "invalid_response" }), "invalid_response"],
    [new ApiError(400, "bad request"), "failed"],
    [new Error("offline"), "unavailable"],
    [undefined, "unavailable"],
  ])("classifies %# as %s", (error, kind) => {
    expect(describeFailure(error).kind).toBe(kind);
  });

  it.each([
    [new ApiError(401, "unauthorized"), "Sign-in required"],
    [new ApiError(403, "forbidden"), "Access denied"],
    [new ApiError(404, "absent"), "Route not available"],
    [new ApiError(429, "limited"), "Too many requests"],
    [new ApiError(502, "invalid", { error: "invalid_response" }), "Invalid response"],
    [new ApiError(500, "server"), "Service unavailable"],
  ])("renders a distinct actionable state for %#", (error, heading) => {
    render(<Unavailable error={error} />);
    expect(screen.getByRole("alert")).toHaveTextContent(heading);
  });

  it("does not report a 2xx sign-in page as data", () => {
    expect(isNonApiContent("text/html; charset=utf-8")).toBe(true);
    expect(isNonApiContent("text/plain")).toBe(true);
    expect(isNonApiContent("application/json")).toBe(false);
    expect(isNonApiContent("text/csv")).toBe(false);
  });

  it("does not produce a downloadable artifact from an HTML 200", async () => {
    mocks.get.mockResolvedValue({
      response: new Response(null, { status: 200, headers: { "content-type": "text/html" } }),
      data: new Blob(["<html>sign in</html>"]),
    });
    await expect(exportMatrix("p", "csv")).rejects.toMatchObject({ status: 502 });
  });

  it("still returns a real CSV artifact", async () => {
    mocks.get.mockResolvedValue({
      response: new Response(null, { status: 200, headers: { "content-type": "text/csv" } }),
      data: new Blob(["id,traced\n1,true\n"]),
    });
    const artifact = await exportMatrix("p", "csv");
    expect(artifact).toBeInstanceOf(Blob);
  });
});

/**
 * Wire-format contract tests for /api/v1/projects endpoints.
 * Blast-radius rationale: projects CRUD is the primary resource in the app;
 * field-shape regressions in envelope normalization or ISO8601 timestamps silently
 * corrupt the project list and dashboard.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "@/api/endpoints";

// Hoisted mock so it is evaluated before module-level imports.
const openApiFetchMock = vi.hoisted(() => {
  const request = vi.fn();
  const use = vi.fn();
  return {
    default: vi.fn(() => ({ DELETE: vi.fn(), GET: request, POST: request, PUT: request, use })),
    request,
    use,
  };
});

vi.mock("openapi-fetch", () => ({ default: openApiFetchMock.default }));

// ISO 8601 regex — matches "2024-01-01T00:00:00.000Z" and variants
const ISO8601_REGEX = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/;

describe("projects contract tests", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("GET /api/v1/projects — envelope normalization", () => {
    it("normalizes {projects, total} envelope to array", async () => {
      openApiFetchMock.request.mockResolvedValueOnce({
        data: {
          projects: [
            { id: "p1", name: "Project 1", created_at: "2024-01-01T00:00:00Z" },
          ],
          total: 1,
        },
        error: undefined,
        response: new Response(null, { status: 200 }),
      });

      const result = await api.projects.list();

      expect(Array.isArray(result)).toBe(true);
      expect(result).toHaveLength(1);
      expect(result[0]).toHaveProperty("id", "p1");
    });

    it("normalizes {items, count} envelope to array", async () => {
      openApiFetchMock.request.mockResolvedValueOnce({
        data: {
          items: [
            { id: "p2", name: "Project 2", created_at: "2024-01-02T00:00:00Z" },
          ],
          count: 1,
        },
        error: undefined,
        response: new Response(null, { status: 200 }),
      });

      const result = await api.projects.list();

      expect(Array.isArray(result)).toBe(true);
      expect(result).toHaveLength(1);
      expect(result[0]).toHaveProperty("id", "p2");
    });
  });

  describe("POST /api/v1/projects — 201 created_at ISO8601", () => {
    it("returns created_at as ISO8601 string on 201", async () => {
      openApiFetchMock.request.mockResolvedValueOnce({
        data: {
          id: "new-proj",
          name: "New Project",
          description: "A test project",
          created_at: "2024-06-15T12:30:00Z",
        },
        error: undefined,
        response: new Response(null, { status: 201 }),
      });

      const result = await api.projects.create({ name: "New Project" });

      expect(result).toHaveProperty("created_at");
      expect(typeof result.created_at).toBe("string");
      expect(ISO8601_REGEX.test(result.created_at)).toBe(true);
    });
  });
});

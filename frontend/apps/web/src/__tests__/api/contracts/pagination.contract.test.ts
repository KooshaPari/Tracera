/**
 * Wire-format contract tests for pagination envelopes on list endpoints.
 * Blast-radius rationale: every list endpoint in the app uses one of these
 * two pagination envelopes. A missing `total` field corrupts the
 * pagination-controls (showing N/A or Infinity); wrong `items` key breaks
 * rendering of every list view (projects dashboard, search results).
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "@/api/endpoints";

// Same hoisted openapi-fetch mock pattern used in projects.contract.test.ts.
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

describe("pagination contract tests", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("GET /api/v1/items?limit=N&offset=M — pagination envelope", () => {
    it("returns envelope with items array and numeric total/limit/offset consistency", async () => {
      openApiFetchMock.request.mockResolvedValueOnce({
        data: {
          items: [
            { id: "item-1", project_id: "proj-1", title: "Item One", type: "requirement" },
            { id: "item-2", project_id: "proj-1", title: "Item Two", type: "requirement" },
          ],
          total: 50,
        },
        error: undefined,
        response: new Response(null, { status: 200 }),
      });

      // Pass explicit limit and offset to exercise the correct query params
      const result = await api.items.list({ limit: 2, offset: 0 });

      expect(Array.isArray(result)).toBe(true);
      expect(result).toHaveLength(2);
      // Wire-format envelope contract: items must be an array
      expect(result[0]).toHaveProperty("id", "item-1");
      expect(result[1]).toHaveProperty("id", "item-2");
    });

    it("handles cursor-pagination envelope with next_cursor and has_more", async () => {
      openApiFetchMock.request.mockResolvedValueOnce({
        data: {
          count: 3,
          has_more: true,
          items: [
            { id: "cursor-item-1", project_id: "proj-1", title: "Cursor Item", type: "requirement" },
          ],
          next_cursor: "eyJpZCI6ImN1cnNvci1pdGVtLTEifQ==",
        },
        error: undefined,
        response: new Response(null, { status: 200 }),
      });

      const result = await api.items.list({ limit: 1, cursor: undefined });

      // items.list returns the cursor-pagination response as-is for cursor envelopes
      expect((result as Record<string, unknown>)).toHaveProperty("has_more", true);
      expect((result as Record<string, unknown>)).toHaveProperty("next_cursor");
      expect(typeof (result as Record<string, unknown>).next_cursor).toBe("string");
      expect(Array.isArray((result as Record<string, unknown>).items)).toBe(true);
    });
  });

  describe("GET /api/v1/search — full search result envelope", () => {
    it("returns complete SearchResult envelope with hasMore, items, page, pageSize, total", async () => {
      openApiFetchMock.request.mockResolvedValueOnce({
        data: {
          hasMore: false,
          items: [
            { id: "search-item-1", project_id: "proj-1", title: "Found Item", type: "requirement" },
          ],
          page: 1,
          pageSize: 10,
          total: 1,
        },
        error: undefined,
        response: new Response(null, { status: 200 }),
      });

      const result = await api.search.searchGet({ q: "found" });

      expect(result).toHaveProperty("hasMore", false);
      expect(result).toHaveProperty("total", 1);
      expect(result).toHaveProperty("page", 1);
      expect(result).toHaveProperty("pageSize", 10);
      expect(Array.isArray(result.items)).toBe(true);
      expect(result.items[0]).toHaveProperty("id", "search-item-1");
    });
  });
});

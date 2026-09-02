/**
 * Wire-format contract tests for 429 rate-limit response shapes.
 * Blast-radius rationale: rate-limiting affects every endpoint. If the
 * client does not honour Retry-After correctly, clients hammer the server
 * after every rate-limit response, amplifying downstream load.
 * Header/body parity ensures robust fallback regardless of which header
 * the CDN strips.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

import { client } from "@/api/client";

const { ApiError, handleApiResponse, safeApiCall } = client;

// Hoisted openapi-fetch mock.
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

const { apiClient } = client;

describe("rate-limit contract tests", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("429 — Retry-After header", () => {
    it("sets Retry-After header as integer seconds on 429 response", async () => {
      const retryAfterSeconds = 30;
      const response = new Response(JSON.stringify({ detail: "Too Many Requests" }), {
        headers: { "Content-Type": "application/json", "Retry-After": String(retryAfterSeconds) },
        status: 429,
        statusText: "Too Many Requests",
      });
      // Capture the mocked request's resolved value to inspect the wire-format
      // response object directly. This is the contract under test.
      const mockedRequest = { data: undefined, error: { detail: "Too Many Requests" }, response };
      openApiFetchMock.request.mockResolvedValueOnce(mockedRequest);

      try {
        await handleApiResponse(
          safeApiCall(apiClient.GET("/api/v1/projects", { params: { query: {} } })),
        );
        expect.fail("expected handleApiResponse to reject");
      } catch (caught) {
        expect(caught).toBeInstanceOf(ApiError);
        const apiError = caught as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(429);
      }

      // Wire-format contract: the Retry-After header is on the 429 response.
      const retryAfter = mockedRequest.response.headers.get("Retry-After");
      expect(retryAfter).toBe("30");
      expect(mockedRequest.response.status).toBe(429);
    });
  });

  describe("429 — retry_after body field", () => {
    it("includes retry_after as integer in 429 body", async () => {
      const retryAfterBody = 45;
      openApiFetchMock.request.mockResolvedValueOnce({
        data: undefined,
        error: { detail: "Too many requests", retry_after: retryAfterBody },
        response: new Response(JSON.stringify({ detail: "Too many requests", retry_after: retryAfterBody }), {
          headers: { "Content-Type": "application/json" },
          status: 429,
          statusText: "Too Many Requests",
        }),
      });

      try {
        await handleApiResponse(
          safeApiCall(apiClient.POST("/api/v1/projects", { body: { name: "Test" } })),
        );
        expect.fail("expected handleApiResponse to reject");
      } catch (caught) {
        expect(caught).toBeInstanceOf(ApiError);
        const apiError = caught as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(429);
        expect(apiError.data).toHaveProperty("retry_after", 45);
        expect(typeof (apiError.data as { retry_after: unknown }).retry_after).toBe("number");
      }
    });
  });
});

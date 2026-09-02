/**
 * Wire-format contract tests for error envelope shapes.
 * Blast-radius rationale: every write endpoint can return 422 with
 * validation errors. If the frontend cannot parse the error envelope,
 * the user sees no actionable feedback and the operation appears
 * silently failed — a critical UX failure for write-heavy workflows.
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

describe("error-shapes contract tests", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("PUT /api/v1/projects/{id} — 422 validation error envelope", () => {
    it("returns ApiError with { code, message } on 422 with optional details", async () => {
      const errorBody = {
        code: "VALIDATION_ERROR",
        message: "Field 'name' is required",
      };
      openApiFetchMock.request.mockResolvedValueOnce({
        data: undefined,
        error: errorBody,
        response: new Response(JSON.stringify(errorBody), {
          headers: { "Content-Type": "application/json" },
          status: 422,
          statusText: "Unprocessable Entity",
        }),
      });

      try {
        await handleApiResponse(
          safeApiCall(
            apiClient.PUT("/api/v1/projects/proj-123", {
              params: { path: { id: "proj-123" } },
              body: { name: "" }, // invalid empty name
            }),
          ),
        );
        expect.fail("expected handleApiResponse to reject");
      } catch (caught) {
        expect(caught).toBeInstanceOf(ApiError);
        const apiError = caught as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(422);
        expect(apiError.data).toHaveProperty("code", "VALIDATION_ERROR");
        expect(apiError.data).toHaveProperty("message", "Field 'name' is required");
        expect(typeof (apiError.data as { code: unknown }).code).toBe("string");
        expect(typeof (apiError.data as { message: unknown }).message).toBe("string");
      }
    });

    it("accepts 422 envelope with optional details field", async () => {
      const errorBody = {
        code: "VALIDATION_ERROR",
        details: { field: "name", issue: "must not be empty" },
        message: "Validation failed",
      };
      openApiFetchMock.request.mockResolvedValueOnce({
        data: undefined,
        error: errorBody,
        response: new Response(JSON.stringify(errorBody), {
          headers: { "Content-Type": "application/json" },
          status: 422,
          statusText: "Unprocessable Entity",
        }),
      });

      try {
        await handleApiResponse(
          safeApiCall(
            apiClient.PUT("/api/v1/projects/proj-456", {
              params: { path: { id: "proj-456" } },
              body: { name: "" },
            }),
          ),
        );
        expect.fail("expected handleApiResponse to reject");
      } catch (caught) {
        expect(caught).toBeInstanceOf(ApiError);
        const apiError = caught as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(422);
        expect(apiError.data).toHaveProperty("code", "VALIDATION_ERROR");
        expect(apiError.data).toHaveProperty("message", "Validation failed");
        // Optional details field
        expect((apiError.data as { details?: unknown }).details).toEqual({
          field: "name",
          issue: "must not be empty",
        });
      }
    });
  });
});

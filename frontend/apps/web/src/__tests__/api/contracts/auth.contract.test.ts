/**
 * Wire-format contract tests for /api/v1/auth endpoints.
 *
 * Blast-radius rationale: auth is the entry point for all users. The
 * /api/v1/auth/login endpoint emits the ErrorResponse envelope
 * ({ error: string }) defined in the OpenAPI schema's
 * components.schemas["handlers.ErrorResponse"]. /api/v1/auth/me returns
 * a User object that the entire UI shell relies on. Field-shape
 * regressions here (e.g. access_token → token, missing required fields
 * on /me) silently break every session in production.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

import { client } from "@/api/client";

const { ApiError, handleApiResponse, safeApiCall } = client;

// Hoisted openapi-fetch mock. We follow the existing client.test.ts
// pattern: replace the default export with a factory that returns a
// client with .GET/.POST/.PUT/.DELETE/.use methods.
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

// We bind once at module-load (after the mock factory is registered).
// Using apiClient.GET/POST rather than the high-level authApi helpers so
// the wire-format contract under test is the HTTP envelope, not the
// higher-level AuthError conversion (which is exercised in
// auth.comprehensive.test.ts).
const { apiClient } = client;

describe("auth contract tests", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("POST /api/v1/auth/login — ErrorResponse envelope", () => {
    it("rejects with ApiError.data = { error: string } on 401 invalid credentials", async () => {
      const errorBody = { error: "Invalid credentials" };
      openApiFetchMock.request.mockResolvedValueOnce({
        data: undefined,
        error: errorBody,
        response: new Response(JSON.stringify(errorBody), {
          status: 401,
          statusText: "Unauthorized",
        }),
      });

      await expect(
        handleApiResponse(
          safeApiCall(
            apiClient.POST("/api/v1/auth/login", {
              body: { email: "alice@example.test", password: "wrong" },
            }),
          ),
        ),
      ).rejects.toMatchObject({
        name: "ApiError",
        status: 401,
        data: { error: "Invalid credentials" },
      });
    });

    it("rejects with ApiError.data = { error: string } on 400 validation error", async () => {
      const errorBody = { error: "Email is required" };
      openApiFetchMock.request.mockResolvedValueOnce({
        data: undefined,
        error: errorBody,
        response: new Response(JSON.stringify(errorBody), {
          status: 400,
          statusText: "Bad Request",
        }),
      });

      try {
        await handleApiResponse(
          safeApiCall(
            apiClient.POST("/api/v1/auth/login", {
              body: { email: "", password: "" },
            }),
          ),
        );
        expect.fail("expected handleApiResponse to reject");
      } catch (caught) {
        expect(caught).toBeInstanceOf(ApiError);
        const apiError = caught as InstanceType<typeof ApiError>;
        expect(apiError.status).toBe(400);
        expect(apiError.data).toEqual({ error: "Email is required" });
        expect(typeof (apiError.data as { error: unknown }).error).toBe("string");
      }
    });
  });

  describe("GET /api/v1/auth/me — required user fields", () => {
    it("returns user with required id, email, role on 200", async () => {
      const mockUser = {
        email: "alice@example.test",
        id: "user-abc",
        name: "Alice",
        role: "admin",
      };
      openApiFetchMock.request.mockResolvedValueOnce({
        data: mockUser,
        error: undefined,
        response: new Response(JSON.stringify(mockUser), {
          headers: { "Content-Type": "application/json" },
          status: 200,
          statusText: "OK",
        }),
      });

      const result = await handleApiResponse(
        safeApiCall(apiClient.GET("/api/v1/auth/me", { params: { query: {} } })),
      );

      expect(result).toBeDefined();
      expect(result).toHaveProperty("id", "user-abc");
      expect(result).toHaveProperty("email", "alice@example.test");
      expect(result).toHaveProperty("role", "admin");
      expect(typeof (result as { id: unknown }).id).toBe("string");
      expect(typeof (result as { email: unknown }).email).toBe("string");
      expect(typeof (result as { role: unknown }).role).toBe("string");
    });
  });
});
